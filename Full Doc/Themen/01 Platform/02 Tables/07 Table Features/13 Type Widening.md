# Type Widening

Type Widening ist ein Feature für Delta-Lake-Tabellen ab Databricks Runtime 15.4 LTS. Es erlaubt, Spaltendatentypen in einen breiteren Typ zu ändern, **ohne** zugrunde liegende Datendateien neu zu schreiben. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Unterstützte Typänderungen

| Ausgangstyp | Unterstützte breitere Typen |
|---|---|
| BYTE | SHORT, INT, BIGINT, DECIMAL, DOUBLE |
| SHORT | INT, BIGINT, DECIMAL, DOUBLE |
| INT | BIGINT, DECIMAL, DOUBLE |
| BIGINT | DECIMAL |
| FLOAT | DOUBLE |
| DECIMAL | DECIMAL mit größerer Präzision und Skala |
| DATE | TIMESTAMP_NTZ |
| VOID | jeder Typ |

Typänderungen funktionieren für Top-Level-Spalten und verschachtelte Felder in Structs, Maps und Arrays. VOID-Konvertierungen erfordern nicht, dass Type Widening aktiviert ist (ab Runtime 18.2+).

**Decimal-Spezialverhalten:** Spark kürzt standardmäßig Nachkommastellen, wenn Integer-Typen zu Decimal/Double hochgestuft werden. Die Gesamtpräzision muss mindestens der Ausgangspräzision entsprechen; bei einer Erhöhung der Skala muss die Gesamtpräzision entsprechend mitwachsen. Mindest-Zielwerte: `decimal(10,0)` für byte/short/int, `decimal(20,0)` für long. Beispiel: Um bei `decimal(10,1)` zwei zusätzliche Nachkommastellen zu erhalten, ist mindestens `decimal(12,3)` nötig.

## 2. Aktivierung

```sql
-- Bestehende Tabelle
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');

-- Bei Tabellenerstellung
CREATE TABLE T(c1 INT) TBLPROPERTIES('delta.enableTypeWidening' = 'true');
```

## 3. Manuelle Typänderungen

```sql
ALTER TABLE <table_name> ALTER COLUMN <col_name> TYPE <new_type>;
```

Aktualisiert das Schema, ohne Datendateien neu zu schreiben.

## 4. Automatische Schema Evolution

Bei aktiviertem Type Widening kann Schema Evolution Spaltentypen während der Ingestion automatisch anpassen. Voraussetzungen: automatische Schema Evolution beim Schreibbefehl aktiviert, Zieltabelle hat Type Widening aktiviert, Quellspaltentyp ist breiter als der Zielspaltentyp, Type Widening unterstützt die Konvertierung.

```sql
CREATE TABLE target_table (id INT, data STRING) TBLPROPERTIES ('delta.enableTypeWidening' = 'true');
CREATE TABLE source_table (id BIGINT, data STRING);
INSERT WITH SCHEMA EVOLUTION INTO target_table SELECT * FROM source_table;
```

**Äquivalent per `saveAsTable` (Python):**

```python
spark.table("source_table").write.mode("append").option("mergeSchema", "true").saveAsTable("target_table")
```

**Äquivalent per `MERGE INTO`:**

```python
from delta.tables import DeltaTable
source_df = spark.table("source_table")
target_table = DeltaTable.forName(spark, "target_table")
(target_table.alias("target")
  .merge(source_df.alias("source"), "target.id = source.id")
  .withSchemaEvolution()
  .whenMatchedUpdateAll()
  .whenNotMatchedInsertAll()
  .execute())
```

```sql
MERGE WITH SCHEMA EVOLUTION INTO target_table
USING source_table
ON target_table.id = source_table.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

## 5. Streaming und Auto Loader

**Auto Loader** (Public Preview) unterstützt Type Widening mit automatischer Schema Evolution:

```python
(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "<path-to-schema-location>")
  .load("<path-to-source-data>")
  .writeStream
  .option("mergeSchema", "true")
  .option("checkpointLocation", "<path-to-checkpoint>")
  .trigger(availableNow=True)
  .toTable("table_name"))
```

**Streaming von Delta-Lake-Tabellen** (ab Runtime 16.4 LTS+) unterstützt es mit der `mergeSchema`-Option:

```python
(spark.readStream
  .table("delta_source_table")
  .writeStream
  .option("checkpointLocation", "/path/to/checkpointLocation")
  .option("mergeSchema", "true")
  .toTable("output_table"))
```

Ist `mergeSchema` aktiviert, werden Typänderungen automatisch übernommen und neue Spalten automatisch dem nachgelagerten Schema hinzugefügt. Ohne `mergeSchema` gilt `spark.sql.storeAssignmentPolicy` (Standard: Downcast).

`schemaTrackingLocation` ist in Runtime 18.0 und darunter zwingend erforderlich, ab 18.1+ optional:

```python
checkpoint_path = "/path/to/checkpointLocation"
(spark.readStream
  .option("schemaTrackingLocation", checkpoint_path)
  .table("delta_source_table")
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .toTable("output_table"))
```

Bei Typänderungen im Stream (Runtime 18.0 und darunter) stoppt der Stream — Fortsetzung über `allowSourceColumnTypeChange`:

```python
checkpoint_path = "/path/to/checkpointLocation"
(spark.readStream
  .option("schemaTrackingLocation", checkpoint_path)
  .option("allowSourceColumnTypeChange", "<delta_source_table_version>")
  # alternativ: .option("allowSourceColumnTypeChange", "always")
  .table("delta_source_table")
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .toTable("output_table"))
```

**Alternative über SQL-Konfiguration** (je nach gewünschtem Geltungsbereich):

```sql
-- Nur für diesen Stream und diese Schema-Änderungsserie
SET spark.databricks.delta.streaming.allowSourceColumnTypeChange.ckpt_<checkpoint_id> = "<delta_source_table_version>";

-- Für diesen Stream generell
SET spark.databricks.delta.streaming.allowSourceColumnTypeChange = "<delta_source_table_version>";

-- Für alle Streams
SET spark.databricks.delta.streaming.allowSourceColumnTypeChange = "always";
```

## 6. Lakeflow Pipelines

**Auf Pipeline-Ebene aktivieren (JSON):**

```json
{
  "configuration": {
    "pipelines.enableTypeWidening": "true"
  }
}
```

**Auf Pipeline-Ebene aktivieren (YAML):**

```yaml
configuration:
  pipelines.enableTypeWidening: 'true'
```

**Für einzelne Tabellen aktivieren (Python):**

```python
import dlt
@dlt.table(
  table_properties={"delta.enableTypeWidening": "true"})
def my_table():
  return spark.readStream.table("source_table")
```

**Für einzelne Tabellen aktivieren (SQL):**

```sql
CREATE OR REFRESH STREAMING TABLE my_table
TBLPROPERTIES ('delta.enableTypeWidening' = 'true')
AS SELECT * FROM source_table;
```

**Pipeline-Kompatibilitätshinweise:** Typänderungen in Materialized Views lösen immer ein vollständiges Recompute aus; Typänderungen an Quelltabellen erfordern ebenfalls ein vollständiges Recompute der Materialized View. Tabellen sind nur ab Runtime 15.4 LTS+ lesbar — für nachgelagerte Reader-Kompatibilität entweder die Type-Widening-Eigenschaft deaktivieren und einen Full Refresh auslösen, oder den Compatibility Mode auf der Tabelle aktivieren.

## 7. Deaktivierung und Entfernung

```sql
-- Zukünftiges Widening verhindern
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.enableTypeWidening' = 'false');

-- Feature vollständig entfernen
ALTER TABLE <table-name> DROP FEATURE 'typeWidening' [TRUNCATE HISTORY];
```

**Namenshinweis:** Für Tabellen, die noch auf Databricks Runtime 15.4 LTS laufen, muss stattdessen `'typeWidening-preview'` als Feature-Name verwendet werden. Details zum Entfernungs-Prozess: siehe [07 Drop Feature.md](07%20Drop%20Feature.md).

## 8. OpenSharing-Unterstützung

Ab Databricks Runtime 16.1+, ausschließlich für Databricks-zu-Databricks-Sharing — sowohl Provider als auch Empfänger müssen auf Runtime 16.1+ laufen. Tabellen mit aktiviertem Type Widening lassen sich **nicht** an Nicht-Databricks-Konsumenten freigeben.

**Einschränkung beim Change-Data-Feed-Lesen:** Kann nicht über Typänderungen hinweg gelesen werden — Lesevorgänge müssen bei einer Typänderung in zwei separate Reads aufgeteilt werden.

## 9. Einschränkungen

**Apache-Iceberg-Kompatibilität:** Iceberg unterstützt folgende Typänderungen nicht: byte/short/int/long zu decimal oder double, Erhöhung der Decimal-Skala, date zu timestampNTZ. Aktiviert man Iceberg Reads auf einer Delta-Tabelle mit solchen Änderungen, entsteht ein Fehler. **Lösungsmöglichkeiten:** entweder die Iceberg-Metadaten über `ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.universalFormat.config.icebergCompatVersion' = '<version>')` neu generieren, oder das Type-Widening-Feature entfernen.

**Typabhängige Funktionen:** `hash()`, `xxhash64()`, `bit_get()`, `bit_reverse()` und `typeof()` liefern je nach Eingabetyp unterschiedliche Ergebnisse (z. B. liefert `hash(1::INT)` ein anderes Ergebnis als `hash(1::BIGINT)`) — explizites Casting für stabile Ergebnisse nutzen:

```python
spark.read.table("table_name") \
  .selectExpr("hash(CAST(column_name AS BIGINT))")
```

```sql
SELECT hash(CAST(column_name AS BIGINT)) FROM table_name;
```

## 10. Verwandte Themen

- Iceberg-Kompatibilität im Detail: siehe [14 Iceberg Reads (UniForm).md](14%20Iceberg%20Reads%20%28UniForm%29.md).
- Runtime-Anforderungen und Protokollversion im Gesamtüberblick: siehe [08 Feature Compatibility.md](08%20Feature%20Compatibility.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/type-widening
