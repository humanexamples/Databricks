[← Übersicht](../00%20Uebersicht.md)

# Was ist Change Data Feed? Automatic vs. Legacy CDF

> Quellen: [Use change data feed on Databricks](https://docs.databricks.com/aws/en/tables/features/change-data-feed) (Stand 16.09.2026) · [Release Notes September 2026](https://docs.databricks.com/aws/en/release-notes/product/2026/september) · [What's coming](https://docs.databricks.com/aws/en/release-notes/whats-coming) · [Databricks Runtime 19](https://docs.databricks.com/aws/en/release-notes/runtime/19) · [Automatic upgrades](https://docs.databricks.com/aws/en/tables/automatic-upgrades) · [Delta Lake Übersicht](https://docs.databricks.com/aws/en/delta/)

## Definition

**Change Data Feed (CDF)** verfolgt **Änderungen auf Zeilenebene** zwischen den Versionen einer **Delta-Lake-Tabelle** oder einer **Apache-Iceberg-v3-Tabelle**. Jeder Änderungsdatensatz enthält die Zeilendaten und Metadaten, die angeben, ob die Zeile eingefügt, geändert oder gelöscht wurde.

**Typische Einsatzfälle:**

- **Inkrementelle ETL-Pipelines**, die nur die seit dem letzten Lauf geänderten Zeilen verarbeiten.
- **Audit Trails**, die Datenänderungen für Compliance und Governance nachverfolgen.
- **Replikation**, die Änderungen an nachgelagerte Tabellen, Caches oder externe Systeme weitergibt.

> **Abgrenzung zu CDC:** Change Data Capture ist das allgemeine Muster, Änderungen eines Quellsystems zu erfassen. CDF ist der CDC-Feed, den **Delta-Tabellen selbst** erzeugen („Delta tables also generate their own CDC feed, known as a Change Data Feed (CDF)“). Siehe [../../CDC/00 Uebersicht.md](../../CDC/00%20Uebersicht.md).

---

## Die zwei Varianten

Databricks unterstützt zwei Ansätze:

| | **Automatic CDF** (Auto CDF) | **Legacy CDF** |
|---|---|---|
| Wann werden Änderungen berechnet? | beim **Lesen** (Query-Zeit) | beim **Schreiben** (materialisiert) |
| Technische Grundlage | **Row Tracking** (Delta) bzw. **Row Lineage** (Iceberg v3) | eigene Change-Data-Dateien und Transaktionslog |
| Konfiguration pro Tabelle | **keine**: jede Tabelle, die die Anforderungen erfüllt, unterstützt es automatisch | **explizit**: `delta.enableChangeDataFeed = true` |
| Tabellenformate | Delta Lake **und** Iceberg v3 | nur Delta Lake |
| Schreib-Performance | besser: `MERGE` und `UPDATE` laut Release Notes **etwa 15 % schneller** | Overhead durch Änderungsdateien |
| Speicherkosten | geringer | leicht höher (Änderungen evtl. in separaten Dateien) |
| Lese-APIs | `table_changes()` und `readChangeFeed` | **dieselben** APIs |
| Status | **GA** seit Databricks Runtime 19 (September 2026) | wird weiter unterstützt; Databricks empfiehlt Migration |

> **Merksatz:** Beide Varianten werden **gleich gelesen**. Der Unterschied liegt nur darin, **wann** die Änderungen berechnet werden und **ob** man CDF pro Tabelle einschalten muss.

---

## Automatic Change Data Feed

Automatic CDF berechnet Zeilenänderungen **zur Abfragezeit** statt beim Schreiben. Dafür nutzt es **Row Tracking** bei Delta-Tabellen und **Row Lineage** bei Iceberg-v3-Tabellen. Weil bei `MERGE INTO` und `UPDATE` nicht bei jedem Schreibvorgang Änderungen berechnet werden, verbessert Auto CDF die Schreib-Performance und senkt die Speicherkosten.

Auto CDF funktioniert mit **Batch-Queries**, **Structured Streaming** und **Databricks-to-Databricks OpenSharing** (Delta Sharing).

### Anforderungen

- **Databricks Runtime 19** oder höher
- Ein unterstütztes, in **Unity Catalog** registriertes Tabellenformat:
  - Managed Table im Delta-Format **mit aktiviertem Row Tracking** oder im **Iceberg-v3**-Format
  - External Table im Delta-Format **mit aktiviertem Row Tracking**

> **Hinweis:** CDF ist nicht Teil der Apache-Iceberg-Spezifikation. Databricks-Reader können den automatischen CDF von Iceberg-v3-Tabellen abfragen, **externe Iceberg-Reader nicht**. Auch bei Delta Lake können **nur Databricks-Reader** den automatischen CDF abfragen.

### Verwenden

Batch-Read (Python / Scala / SQL):

```python
spark.read \
  .option("readChangeFeed", "true") \
  .option("startingVersion", 0) \
  .table("<table_name>")
```

```scala
spark.read
  .option("readChangeFeed", "true")
  .option("startingVersion", 0)
  .table("<table_name>")
```

```sql
SELECT * FROM table_changes('<table_name>', 0)
```

Streaming-Read (Python / Scala):

```python
(spark.readStream
  .option("readChangeFeed", "true")
  .table("<table_name>"))
```

```scala
spark.readStream
  .option("readChangeFeed", "true")
  .table("<table_name>")
```

Details: [Batch](../02%20Lesen/01%20Batch%20-%20table_changes%20und%20readChangeFeed.md) · [Streaming](../02%20Lesen/02%20Streaming%20-%20readStream%20und%20Optionen.md)

### Von Legacy auf Automatic migrieren

1. Prüfen, ob die Tabelle die Anforderungen erfüllt.
2. Legacy CDF ausschalten:

```sql
ALTER TABLE <table_name> UNSET TBLPROPERTIES ('delta.enableChangeDataFeed');
```

> **Legacy und Automatic CDF können nicht gleichzeitig verwendet werden.**

### Verbreitung und Automatic Upgrades

- **Release Notes September 2026 / DBR 19:** Auto CDF ist **allgemein verfügbar (GA)**. Voraussetzung: DBR 19+ mit aktiviertem Row Tracking.
- **What's coming:** Auto CDF wird schrittweise ausgerollt und soll **bis Ende Oktober 2026** in allen unterstützten Regionen verfügbar sein.
- **Automatic Upgrades:** Databricks aktiviert **Row Tracking** automatisch auf neuen und bestehenden Tabellen (ab DBR 14.0 kompatibel; Rollout ab Juli 2026). Laut Doku gilt: *„When row tracking is enabled, automatic change data feed is available without additional configuration.“*

> **Konsequenz:** Auf aktuellen Unity-Catalog-Tabellen ist CDF in vielen Fällen bereits verfügbar, **ohne** dass jemand `delta.enableChangeDataFeed` gesetzt hat.

---

## Legacy Change Data Feed (nur Delta Lake)

Legacy CDF muss **pro Tabelle** manuell eingeschaltet werden. Iceberg-Tabellen werden nicht unterstützt. Databricks empfiehlt die Migration auf Automatic CDF.

Wenn Legacy CDF aktiv ist, zeichnet die Runtime für **alle** in die Tabelle geschriebenen Daten Änderungsereignisse auf.

### Einschalten: neue Tabelle

```sql
CREATE TABLE student (id INT, name STRING, age INT)
  TBLPROPERTIES (delta.enableChangeDataFeed = true)
```

> **Achtung:** Schaltet man Legacy CDF für einen Zeitraum aus und später wieder ein, ist **dieser Zeitraum nicht abfragbar**. Für solche Lücken Automatic CDF verwenden.

### Einschalten: bestehende Tabelle

```sql
ALTER TABLE myDeltaTable
  SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
```

### Speicherverhalten

- Leicht **höhere Speicherkosten** möglich, weil Änderungen in separaten Dateien landen können.
- Manche Operationen (**insert-only**, **Löschen ganzer Partitionen**) erzeugen **keine** Change-Data-Dateien; der CDF wird dann direkt aus dem Transaktionslog berechnet.
- Change-Data-Dateien folgen der **Retention Policy** der Tabelle: `VACUUM` löscht sie; Änderungen aus dem Transaktionslog folgen der Checkpoint-Retention.
- Databricks rät davon ab, den CDF durch direktes Lesen der Change-Data-Dateien zu rekonstruieren. **Immer die Delta-/Iceberg-APIs verwenden.**

Mehr zu Speicher und Retention: [03 Tabelleneigenschaften, Protokoll und Speicher](03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md)

---

## Prüfungsrelevante Kernaussagen

- CDF = **zeilenbasierte Änderungen** zwischen Tabellenversionen, mit `_change_type`, `_commit_version`, `_commit_timestamp`.
- **Legacy:** `delta.enableChangeDataFeed = true`; erfasst nur Änderungen **ab Aktivierung**.
- **Automatic:** kein Tabellen-Flag, braucht **Row Tracking** + **DBR 19** + Unity Catalog.
- Gelesen wird **immer** über `table_changes()` (SQL) oder `readChangeFeed` (Python/Scala).
- CDF ist **kein dauerhaftes Archiv** → siehe [Streaming, Abschnitt „Dauerhafte Historie“](../02%20Lesen/02%20Streaming%20-%20readStream%20und%20Optionen.md).

---
[← Übersicht](../00%20Uebersicht.md) · [Nächste Datei →](02%20Schema%20und%20Metadatenspalten.md)
