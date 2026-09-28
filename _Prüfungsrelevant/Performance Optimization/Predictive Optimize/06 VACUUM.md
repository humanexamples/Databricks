# VACUUM — nicht mehr referenzierte Dateien löschen

`VACUUM` entfernt **Datendateien**, die von **keiner Tabellenversion innerhalb der Retention** mehr referenziert werden. Das spart **Speicherkosten** und sorgt dafür, dass gelöschte oder geänderte Datensätze **endgültig** nicht mehr lesbar sind (Compliance, z. B. DSGVO).

> **Merksatz:** `OPTIMIZE` schreibt **neue** Dateien und markiert die alten als entfernt. `VACUUM` löscht die alten **physisch**, sobald sie älter als die Retention sind.

---

## 1. Warum gibt es überhaupt „verwaiste" Dateien?

Delta Lake (und Iceberg) ändern Dateien **nie in-place**. Jede Änderung schreibt neue Dateien und vermerkt im Transaktionslog (`_delta_log`), welche Dateien **hinzugefügt** (`AddFile`) und welche **entfernt** (`RemoveFile`) wurden. Die entfernten Dateien bleiben aber im Speicher liegen, damit **Time Travel** auf ältere Versionen funktioniert.

```
Version 0  INSERT     → AddFile(file-1), AddFile(file-2)
Version 1  UPDATE     → RemoveFile(file-1), AddFile(file-3)
Version 2  OPTIMIZE   → RemoveFile(file-2), RemoveFile(file-3), AddFile(file-4)

Aktuelle Version referenziert nur: file-4
Im Speicher liegen noch:           file-1, file-2, file-3, file-4
```

Ohne `VACUUM` wächst der Speicher bei jedem `UPDATE`, `DELETE`, `MERGE` und `OPTIMIZE` immer weiter.

---

## 2. Wie VACUUM funktioniert

1. **Retention bestimmen:** `delta.deletedFileRetentionDuration` (Standard **7 Tage**).
2. **Kandidaten finden:** Dateien, die aus dem Transaktionslog **logisch entfernt** wurden und **länger als die Retention** zurückliegen. Maßgeblich ist der Zeitpunkt der **Entfernung im Log plus Retention**, **nicht** der Änderungszeitstempel der Datei im Storage.
3. **Löschen:** Diese Dateien werden physisch aus dem Cloud-Speicher entfernt.

**Was VACUUM überspringt bzw. mitnimmt:**
- Verzeichnisse, die mit `_` oder `.` beginnen, werden übersprungen, z. B. `_delta_log`. Streaming-Checkpoints im Tabellenordner deshalb z. B. unter `_checkpoints` ablegen. (Ausnahme: Partitionsspalten, die mit `_` beginnen.)
- **Change-Data-Feed-Dateien** (`_change_data`) werden mit `VACUUM` entfernt.
- Dateien von **Bloom-Filter-Indizes** (`_delta_index`, veraltet) werden ebenfalls bereinigt.
- **Transaktionslog-Dateien** werden **nicht** von `VACUUM` gelöscht, sondern automatisch nach Checkpoints (Retention `delta.logRetentionDuration`, Standard **30 Tage**).
- Bei Tabellen mit **Iceberg-Reads** bereinigt `VACUUM` auch Iceberg-Metadaten älterer Versionen.
- Leere Verzeichnisse können zurückbleiben; der nächste `VACUUM`-Lauf entfernt sie.

**Zwei Phasen (wichtig für die Cluster-Größe):**

| Phase | Wer arbeitet? | Was passiert? |
|---|---|---|
| 1. Listing | **Worker** (parallel), Driver wartet | Dateien im Verzeichnis auflisten und mit dem Log abgleichen |
| 2. Löschen | **nur Driver**, Worker warten | Löschbefehl je Datei |

---

## 3. Syntax

```sql
VACUUM table_name;              -- Standard (= FULL), Retention aus Tabelleneigenschaft
VACUUM table_name DRY RUN;      -- nur anzeigen (bis zu 1000 Dateien), nichts löschen
VACUUM table_name FULL;         -- explizit Full-Modus
VACUUM table_name LITE;         -- Lite-Modus (siehe unten)
```

```python
from delta.tables import DeltaTable
DeltaTable.forName(spark, "table_name").vacuum()
```

> ℹ️ Die aktuelle SQL-Referenz beschreibt die Retention nur über die Tabelleneigenschaft `delta.deletedFileRetentionDuration`. Eine Klausel `RETAIN n HOURS` ist dort nicht (mehr) aufgeführt.

### FULL vs. LITE

| | `FULL` (Standard) | `LITE` |
|---|---|---|
| Vorgehen | Listet **alle** Dateien im Tabellenverzeichnis | Nutzt das **Transaktionslog**, kein Directory-Listing |
| Findet auch nicht referenzierte Dateien (z. B. aus abgebrochenen Transaktionen)? | ✅ | ❌ |
| Kosten/Dauer | hoch bei großen Tabellen | deutlich niedriger |
| Voraussetzung | — | mindestens ein erfolgreiches `VACUUM` innerhalb der Log-Retention (30 Tage); sonst Fehler `DELTA_CANNOT_VACUUM_LITE` → `VACUUM FULL` ausführen |
| Verfügbarkeit | immer | Public Preview (Doku-Seite: DBR 16.4 LTS; SQL-Referenz: `FULL`/`LITE`-Schlüsselwörter ab DBR 16.1) |

**Faustregel:** Für große Tabellen mit häufigem `VACUUM` regelmäßig `LITE`, gelegentlich `FULL`.

---

## 4. Retention und Time Travel

```sql
-- Time Travel über 30 Tage ermöglichen
ALTER TABLE t SET TBLPROPERTIES (
  'delta.deletedFileRetentionDuration' = 'interval 30 days',
  'delta.logRetentionDuration'         = 'interval 30 days'
);
```

| Eigenschaft | Standard | Steuert |
|---|---|---|
| `delta.deletedFileRetentionDuration` | **7 Tage** | Wie lange entfernte **Datendateien** erhalten bleiben (Schwelle für `VACUUM`) |
| `delta.logRetentionDuration` | **30 Tage** | Wie lange die **Tabellenhistorie** (Log) erhalten bleibt |

- Für Time Travel auf eine Version braucht man **beide**: Log **und** Datendateien.
- Nach `VACUUM` ist **kein Time Travel** und **kein `RESTORE`** mehr auf Versionen möglich, deren Dateien gelöscht wurden.
- Ab DBR 18.0 (bei UC-Managed-Tables ab DBR 12.2) werden Time-Travel-Abfragen **blockiert**, die älter als `deletedFileRetentionDuration` sind, und `logRetentionDuration` muss **≥** `deletedFileRetentionDuration` sein.
- Höhere Retention = mehr gespeicherte Dateien = **höhere Speicherkosten**.
- Tabellenhistorie ist **kein Backup-Ersatz**.

### Zu kurze Retention ist gefährlich

> „Databricks strongly recommends setting a retention interval of at least 7 days."

Lang laufende Jobs können Dateien geschrieben haben, die **noch nicht committet** sind. Ist die Retention kürzer als die Laufzeit des Jobs, löscht `VACUUM` diese Dateien und der Job schlägt fehl bzw. es gehen Daten verloren.

Ein **Safety Check** verhindert das. Abschalten nur, wenn man sicher ist:

```sql
SET spark.databricks.delta.retentionDurationCheck.enabled = false;
```

Predictive Optimization hält bei `VACUUM FULL` **immer mindestens 7 Tage** ein, auch wenn die Eigenschaft kleiner gesetzt ist.

---

## 5. Soft-Deletes: REORG TABLE … APPLY (PURGE)

Manche Features löschen nur **logisch über Metadaten**, ohne Dateien umzuschreiben:
- **Deletion Vectors** (jede Datenänderung),
- **Column Mapping** (`DROP COLUMN`).

Die „gelöschten" Werte stehen dann noch **physisch in den aktuellen Dateien**. `VACUUM` allein hilft nicht, weil diese Dateien noch referenziert sind.

```sql
REORG TABLE t APPLY (PURGE);   -- 1. Dateien ohne die gelöschten Daten neu schreiben
-- … Retention abwarten …
VACUUM t;                      -- 2. alte Dateien physisch löschen
```

Wichtig für **DSGVO-Löschungen**: Erst nach `REORG` **und** anschließendem `VACUUM` (nach Ablauf der Retention) sind die Daten wirklich weg.

> Achtung Disk Cache: Ein Cluster kann noch Daten gelöschter Dateien im Cache haben. Ein Neustart des Clusters leert ihn.

---

## 6. Wann ist VACUUM sinnvoll? Wie oft?

| Situation | Empfehlung |
|---|---|
| UC-Managed-Table | **Predictive Optimization** erledigt `VACUUM` automatisch; manuell meist unnötig |
| External Table oder ohne PO | `VACUUM` **regelmäßig** (z. B. täglich/wöchentlich) als geplanten Job |
| Viele `UPDATE`/`DELETE`/`MERGE`/`OPTIMIZE` | Häufiger, weil schnell viele verwaiste Dateien entstehen |
| Reine Append-Tabelle ohne `OPTIMIZE` | Wenig Nutzen: kaum entfernte Dateien |
| Datenschutz-Löschung muss physisch wirken | `REORG … APPLY (PURGE)` + `VACUUM` |
| Langes Time Travel nötig | Retention erhöhen **bevor** `VACUUM` läuft (bzw. bevor PO aktiviert wird) |

> „Databricks recommends regularly running `VACUUM` on all tables to reduce excess cloud data storage costs."

---

## 7. Compute-Empfehlung für manuelles VACUUM

- Cluster mit **Autoscaling 1–4 Worker**, je **8 Cores**.
- **Driver mit 8–32 Cores**; bei OOM-Fehlern den Driver vergrößern.
- Löscht `VACUUM` regelmäßig **> 10.000 Dateien** oder dauert **> 30 Minuten**: Engpass im Listing → **mehr Worker**; Engpass beim Löschen → **größerer Driver**.

---

## 8. Audit

`VACUUM` schreibt Audit-Informationen ins Transaktionslog (`DESCRIBE HISTORY`). Bei UC-Managed-Tables und External Tables ist das standardmäßig aktiv; steuerbar über:

```sql
SET spark.databricks.delta.vacuum.logging.enabled = true;
```

---

## 9. Prüfungsfallen

| Aussage | Richtig? |
|---|---|
| `VACUUM` löscht Dateien nach ihrem Änderungsdatum im Storage | ❌ Maßgeblich ist der Entfernungszeitpunkt im Log + Retention |
| `VACUUM` löscht auch alte `_delta_log`-Dateien | ❌ Log-Dateien werden nach Checkpoints automatisch entfernt |
| Nach `VACUUM` geht Time Travel auf alle Versionen weiter | ❌ Nur auf Versionen innerhalb der Retention |
| `VACUUM` macht Queries schneller | ❌ Es spart Speicher, ändert aber nichts am Layout der aktuellen Dateien |
| Standard-Retention ist 30 Tage | ❌ 7 Tage (30 Tage ist die **Log**-Retention) |
| `VACUUM` entfernt auch alte CDF-Daten | ✅ `_change_data` wird bereinigt |

## Quellen

- [Remove unused data files with vacuum](https://docs.databricks.com/aws/en/tables/operations/vacuum) · [Microsoft Learn](https://learn.microsoft.com/en-us/azure/databricks/tables/operations/vacuum)
- [VACUUM (SQL-Referenz)](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/delta-vacuum)
- [Work with table history](https://learn.microsoft.com/en-us/azure/databricks/tables/history)
- [Predictive optimization](https://docs.databricks.com/aws/en/optimizations/predictive-optimization)
