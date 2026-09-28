# OPTIMIZE — Datenlayout verbessern

`OPTIMIZE` **schreibt Datendateien neu**, um das Layout einer Delta- oder Iceberg-Tabelle zu verbessern:
- **Compaction (Bin-Packing):** viele kleine Dateien zu wenigen großen zusammenfassen,
- **Liquid Clustering:** Daten nach den Clustering-Keys gruppieren (bei geclusterten Tabellen),
- **Z-Ordering:** Daten nach `ZORDER BY`-Spalten gemeinsam ablegen (nur Delta ohne Liquid Clustering, Legacy).

Ziel: **weniger Dateien öffnen** und **mehr Dateien per Data Skipping überspringen** → schnellere Queries.

> **Merksatz:** `OPTIMIZE` macht Queries **schneller**, `VACUUM` macht Speicher **billiger**. `OPTIMIZE` erzeugt verwaiste Dateien, die erst `VACUUM` löscht.

---

## 1. Das Problem: kleine Dateien (Small-File-Problem)

Streaming, häufige kleine Batches, `MERGE`/`UPDATE` und stark partitionierte Tabellen erzeugen viele kleine Dateien. Jede Datei bedeutet:
- einen eigenen Cloud-Storage-Request (Latenz),
- Metadaten im Transaktionslog,
- eigene Min/Max-Statistiken.

Tausende kleine Dateien verlangsamen Leseoperationen deutlich. `OPTIMIZE` fasst sie zusammen.

---

## 2. Wie OPTIMIZE funktioniert

1. Liest die betroffenen (kleinen bzw. nicht geclusterten) Dateien.
2. Schreibt die Daten in **neue, größere** (bzw. geclusterte) Dateien.
3. Committet im Log: `AddFile` für neue Dateien mit **`dataChange = false`**, `RemoveFile` für alte.
4. Die alten Dateien bleiben im Speicher, bis `VACUUM` sie nach Ablauf der Retention löscht.

**Eigenschaften:**
- **Keine Datenänderung:** Eine Abfrage vor und nach `OPTIMIZE` liefert dasselbe Ergebnis.
- **Snapshot Isolation:** Laufende Leser werden nicht unterbrochen.
- **Streaming-sicher:** Streams mit dieser Tabelle als Quelle sind nicht betroffen (wegen `dataChange = false`).
- **Bin-Packing ist idempotent:** Ein zweiter Lauf auf denselben Daten bewirkt nichts.
- **Z-Ordering ist nicht idempotent**, arbeitet aber inkrementell.
- **Liquid Clustering ist inkrementell:** Nur Daten, die geclustert werden müssen, werden neu geschrieben.
- Innerhalb von **Partitionen**: Compaction erfolgt pro Partition.
- **Ausgabe:** Datei-Statistiken (min, max, total …) zu entfernten und hinzugefügten Dateien, bei Z-Order auch Z-Order-Statistiken.

---

## 3. Syntax

```
OPTIMIZE table_name [FULL] [WHERE predicate]
  [ZORDER BY (col_name1 [, ...])]
```

```sql
OPTIMIZE events;                                        -- Compaction bzw. inkrementelles Clustering
OPTIMIZE events WHERE date >= '2017-01-01';             -- nur Partitionen, die zum Prädikat passen
OPTIMIZE events FULL;                                   -- alles neu schreiben (DBR 16.0+)
OPTIMIZE events FULL WHERE date >= '2025-01-01';        -- Teil-Reclustering bei Liquid Clustering (DBR 18.1+)
OPTIMIZE events
  WHERE date >= current_timestamp() - INTERVAL 1 day
  ZORDER BY (eventType);                                -- Z-Order (Legacy, nicht mit Liquid Clustering)
```

```python
from delta.tables import DeltaTable
dt = DeltaTable.forName(spark, "events")
dt.optimize().executeCompaction()                        # Compaction
dt.optimize().where("date='2021-11-18'").executeCompaction()
dt.optimize().executeZOrderBy("eventType")               # Z-Order
```

### Parameter

| Parameter | Bedeutung | Einschränkungen |
|---|---|---|
| `WHERE` | Nur Zeilen, die das Prädikat erfüllen | Nur Filter auf **Partitions-/Clustering-Spalten**. Bei Liquid Clustering stattdessen `FULL WHERE` (DBR 18.1+, nur einfache Bereichsprädikate auf **einer** Clustering-Spalte) |
| `FULL` | Schreibt **alle** Datendateien neu | DBR 16.0+. Nutzen: vollständiges Reclustering nach Key-Änderung; Neukomprimierung nach Codec-Wechsel |
| `ZORDER BY` | Legt Spaltenwerte gemeinsam ab | **Nicht** mit Liquid Clustering kombinierbar; Wirkung sinkt mit jeder weiteren Spalte; nur auf Spalten **mit Statistiken** sinnvoll |

**Beispiel `FULL` nach Codec-Wechsel:**

```sql
ALTER TABLE t SET TBLPROPERTIES ('delta.parquet.compression.codec' = 'ZSTD');
OPTIMIZE t FULL;
```

---

## 4. OPTIMIZE und Liquid Clustering

- Bei geclusterten Tabellen gruppiert `OPTIMIZE` die Daten nach den Clustering-Keys, **inkrementell**.
- Nach **Änderung der Keys** (`ALTER TABLE … CLUSTER BY (…)`) werden bestehende Daten **nicht** automatisch umgeschrieben → `OPTIMIZE t FULL`.
- Beim Schreiben wird nur ab bestimmten Größen sofort geclustert (Clustering on Write). Deshalb regelmäßig `OPTIMIZE`.
- **Empfehlung ohne PO:** regelmäßige `OPTIMIZE`-Jobs, bei vielen Updates/Inserts **alle 1–2 Stunden**. Weil das Clustering inkrementell ist, laufen sie meist schnell.
- **Mit PO:** geplante `OPTIMIZE`-Jobs **abschalten**.
- Voraussetzung zum Triggern von Clustering: DBR 13.3 LTS+; für große Tabellen empfiehlt Databricks DBR 17.3 LTS+.

### Liquid Clustering vs. Z-Order vs. Partitionierung

| | Liquid Clustering | Z-Order | Partitionierung |
|---|---|---|---|
| Empfehlung | ✅ für alle neuen Tabellen | Legacy | Legacy (nur sehr große Tabellen) |
| Keys ändern ohne Rewrite | ✅ | Z-Order-Spalten bei jedem Lauf angeben | ❌ |
| Inkrementell | ✅ | teilweise | — |
| Von PO ausgeführt | ✅ | ❌ | — |
| Kombinierbar | nicht mit Partitionen oder Z-Order | nicht mit Liquid | nicht mit Liquid |

---

## 5. Dateigrößen

| Einstellung | Wirkung |
|---|---|
| **Autotuning** (Standard, UC-Managed) | Zielgröße nach Tabellengröße: < 2,56 TB → **256 MB**; 2,56–10 TB → linear 256 MB bis 1 GB; > 10 TB → **1 GB** |
| `delta.targetFileSize` | Feste Zielgröße (z. B. `100mb`). Bei UC-Managed-Tables mit DBR 11.3+ respektiert **nur `OPTIMIZE`** diesen Wert |
| `spark.databricks.delta.optimize.maxFileSize` | Maximale Ausgabedateigröße von `OPTIMIZE`, Standard **1 GB** |

Wächst die Zielgröße einer Tabelle, werden bestehende kleinere Dateien von `OPTIMIZE` **nicht** erneut zusammengefasst. Wer das will, setzt eine feste `targetFileSize`.

---

## 6. Abgrenzung: Auto Compaction und Optimized Writes

Beide reduzieren das Small-File-Problem **beim Schreiben**, sind aber **kein vollständiger Ersatz** für `OPTIMIZE`.

| | Optimized Writes | Auto Compaction | `OPTIMIZE` |
|---|---|---|---|
| Wann? | **Während** des Writes (Shuffle vor dem Schreiben) | **Direkt nach** einem erfolgreichen Write, synchron auf demselben Cluster | Manuell, per Job oder durch PO (Serverless) |
| Tabelleneigenschaft | `delta.autoOptimize.optimizeWrite` | `delta.autoOptimize.autoCompact` (`auto` empfohlen) | — |
| Wirkt auf | Die gerade geschriebenen Daten | Noch nicht kompaktierte kleine Dateien | Ganze Tabelle bzw. `WHERE`-Bereich |
| Clustering/Z-Order | ❌ | ❌ | ✅ |
| Kosten | höhere Schreib-Latenz | Zeit auf dem Schreib-Cluster | eigener Compute |

- Bei **`MERGE`, `UPDATE`, `DELETE`** sind Auto Compaction und Optimized Writes **immer aktiv** und nicht abschaltbar.
- Für **UC-Managed-Tables** stimmt Databricks Dateigrößen automatisch ab; manuelles Tuning ist dort nicht nötig.
- Für Tabellen **> 1 TB** empfiehlt Databricks zusätzlich geplantes `OPTIMIZE`, sofern PO es nicht ohnehin übernimmt.
- In `DESCRIBE HISTORY` erscheinen Auto Compaction, Liquid Clustering und Z-Order alle als `OPTIMIZE`. Unterscheidung über `operationParameters`: `auto = true` → Auto Compaction; `clusterBy` gefüllt → Liquid Clustering; `zOrderBy` gefüllt → Z-Order.

---

## 7. Wann ist OPTIMIZE sinnvoll? Wie oft?

| Situation | Empfehlung |
|---|---|
| UC-Managed-Table | **Predictive Optimization** führt `OPTIMIZE` aus, wenn es sich lohnt |
| External Table oder ohne PO | Mit **täglichem** `OPTIMIZE` starten, dann Frequenz nach Kosten/Nutzen anpassen |
| Liquid-Clustering-Tabelle mit vielen Updates/Inserts, ohne PO | Alle **1–2 Stunden** |
| Streaming-Ingest mit vielen kleinen Dateien | Auto Compaction + regelmäßiges `OPTIMIZE` |
| Clustering-Keys geändert | Einmalig `OPTIMIZE … FULL` |
| Nur neue Daten betroffen (partitioniert) | `OPTIMIZE … WHERE <partition>` |
| Kleine, selten geänderte Tabelle | Kaum Nutzen |

**Trade-off:** Häufiger → bessere Query-Performance, aber höhere Compute-Kosten. Seltener → günstiger, aber mehr kleine Dateien.

**Compute:** `OPTIMIZE` ist **CPU-intensiv** (Parquet-Decoding/-Encoding) → **Compute-optimierte** Instanztypen, profitiert von lokalen SSDs.

---

## 8. Prüfungsfallen

| Aussage | Richtig? |
|---|---|
| `OPTIMIZE` löscht die alten Dateien | ❌ Das macht erst `VACUUM` |
| `OPTIMIZE` ändert Daten, Streams lesen die Dateien neu | ❌ `dataChange = false`, Streams sind nicht betroffen |
| `ZORDER BY` funktioniert mit Liquid Clustering | ❌ Nicht kombinierbar |
| Predictive Optimization führt `ZORDER` aus | ❌ Nur Compaction und Liquid Clustering |
| `OPTIMIZE … WHERE` erlaubt beliebige Spalten | ❌ Nur Partitions-/Clustering-Spalten |
| Nach `ALTER TABLE … CLUSTER BY` sind alte Daten sofort neu geclustert | ❌ Erst nach `OPTIMIZE … FULL` |
| Auto Compaction ersetzt `OPTIMIZE` vollständig | ❌ Kein Clustering, keine volle Konsolidierung großer Tabellen |
| Bin-Packing ist idempotent | ✅ |

## Quellen

- [Optimize data file layout](https://learn.microsoft.com/en-us/azure/databricks/tables/operations/optimize)
- [OPTIMIZE (SQL-Referenz)](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/delta-optimize)
- [Use liquid clustering for tables](https://learn.microsoft.com/en-us/azure/databricks/tables/clustering)
- [Control data file size](https://learn.microsoft.com/en-us/azure/databricks/tables/tune-file-size)
- [Work with table history](https://learn.microsoft.com/en-us/azure/databricks/tables/history)
- [Data skipping](https://learn.microsoft.com/en-us/azure/databricks/tables/data-skipping)
