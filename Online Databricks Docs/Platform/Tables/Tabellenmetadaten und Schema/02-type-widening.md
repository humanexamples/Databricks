# Type Widening

Type Widening ändert den Datentyp einer Spalte in einen breiteren Typ. Dabei werden keine Datendateien neu geschrieben. Die Funktion steht ab Databricks Runtime 15.4 LTS zur Verfügung.

## Was Type Widening bedeutet

Ohne Type Widening muss Databricks beim Ändern eines Spaltentyps alle Datendateien neu schreiben. Mit aktiviertem Type Widening reicht eine Metadaten-Änderung. Das spart Zeit und Rechenkosten.

Type-Änderungen funktionieren für Top-Level-Spalten. Sie funktionieren auch für Felder in Structs, Maps und Arrays.

## Unterstützte Typ-Änderungen

Die folgende Tabelle zeigt, welche Zieltypen für welchen Quelltyp erlaubt sind.

| Quelltyp | Erlaubte breitere Typen |
|---|---|
| BYTE | SHORT, INT, BIGINT, DECIMAL, DOUBLE |
| SHORT | INT, BIGINT, DECIMAL, DOUBLE |
| INT | BIGINT, DECIMAL, DOUBLE |
| BIGINT | DECIMAL |
| FLOAT | DOUBLE |
| DECIMAL | DECIMAL mit höherer Präzision und Skala |
| DATE | TIMESTAMP_NTZ |
| VOID | Jeder Typ |

### Sonderfall VOID

Für eine Änderung von VOID zu einem anderen Typ muss Type Widening nicht aktiviert sein. Diese Änderung funktioniert immer, ohne zusätzliche Konfiguration. VOID-Type-Widening gibt es ab Databricks Runtime 18.2.

### Decimal-Verhalten

Spark kappt standardmäßig den Nachkommateil eines Werts, wenn eine Operation einen Integer-Typ zu Decimal oder Double erweitert und ein nachgelagerter Schreibvorgang den Wert zurück in eine Integer-Spalte schreibt.

Bei einer Änderung eines Zahlentyps zu Decimal muss die Gesamtpräzision gleich oder größer als die Ausgangspräzision sein. Erhöht sich zusätzlich die Skala, muss auch die Gesamtpräzision entsprechend steigen.

- BYTE, SHORT und INT benötigen mindestens `decimal(10,0)`.
- LONG benötigt mindestens `decimal(20,0)`.
- Für zwei zusätzliche Nachkommastellen bei `decimal(10,1)` ist das Minimalziel `decimal(12,3)`.

## Type Widening aktivieren

Für eine bestehende Tabelle wird die Tabelleneigenschaft gesetzt.

```sql
%sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true')
```

Bei der Tabellenerstellung lässt sich die Eigenschaft direkt mitgeben.

```sql
%sql
CREATE TABLE T(c1 INT) TBLPROPERTIES('delta.enableTypeWidening' = 'true')
```

Das Aktivieren von Type Widening hebt das Reader- und Writer-Protokoll der Tabelle an. Das kann die Kompatibilität mit externen Delta-Lake-Clients beeinträchtigen. Tabellen mit aktiviertem Type Widening lassen sich nur mit Databricks Runtime 15.4 LTS oder höher lesen.

## Typ-Änderung manuell anwenden

```sql
%sql
ALTER TABLE <table_name> ALTER COLUMN <col_name> TYPE <new_type>
```

## Type Widening mit automatischer Schema-Evolution

Ohne aktiviertes Type Widening versucht die Schema-Evolution immer, Daten auf den Zieltyp der Tabelle herunterzurechnen. Type Widening ändert das: Es erweitert stattdessen den Zieltyp.

Damit die Schema-Evolution einen Typ erweitert, müssen vier Bedingungen erfüllt sein: Der Schreibbefehl nutzt automatische Schema-Evolution, die Zieltabelle hat Type Widening aktiviert, der Quellspaltentyp ist breiter als der Zieltyp, und Type Widening unterstützt genau diese Typ-Änderung.

Beispiel: Tabellen anlegen

```python
spark.sql("CREATE TABLE target_table (id INT, data STRING) TBLPROPERTIES ('delta.enableTypeWidening' = 'true')")
spark.sql("CREATE TABLE source_table (id BIGINT, data STRING)")
```

Schema-Evolution mit saveAsTable (Python):

```python
spark.table("source_table").write.mode("append").option("mergeSchema", "true").saveAsTable("target_table")
```

Schema-Evolution mit MERGE (Python):

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

INSERT mit Schema-Evolution (SQL):

```sql
%sql
INSERT WITH SCHEMA EVOLUTION INTO target_table SELECT * FROM source_table;
```

MERGE mit Schema-Evolution (SQL):

```sql
%sql
MERGE WITH SCHEMA EVOLUTION INTO target_table
USING source_table
ON target_table.id = source_table.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

## Auto Loader

Type Widening mit Auto Loader befindet sich in der Public Preview. Auto Loader unterstützt Type Widening zusammen mit automatischer Schema-Evolution. Die Zieltabelle muss Type Widening aktiviert haben.

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

## Type Widening deaktivieren

```sql
%sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.enableTypeWidening' = 'false')
```

## Das Table Feature entfernen

Beim Entfernen des Features werden Datendateien neu geschrieben, damit sie zum aktuellen Schema passen. Der Befehl unterscheidet sich je nachdem, ob die Tabelle mit der Preview-Version erstellt wurde.

```sql
%sql
ALTER TABLE <table-name> DROP FEATURE 'typeWidening' [TRUNCATE HISTORY]
```

```sql
%sql
ALTER TABLE <table-name> DROP FEATURE 'typeWidening-preview' [TRUNCATE HISTORY]
```

## Streaming von einer Delta-Lake-Tabelle

Streaming-Unterstützung für Type Widening gibt es ab Databricks Runtime 16.4 LTS.

Ist `mergeSchema` aktiviert und die Zieltabelle hat Type Widening aktiviert, werden Typ-Änderungen automatisch in die nachgelagerte Tabelle übernommen. Neue Spalten werden ebenfalls automatisch hinzugefügt.

Ohne `mergeSchema` folgen Werte der Konfiguration `spark.sql.storeAssignmentPolicy`, die standardmäßig herunterrechnet.

```python
(spark.readStream
 .table("delta_source_table")
 .writeStream
 .option("checkpointLocation", "/path/to/checkpointLocation")
 .option("mergeSchema", "true")
 .toTable("output_table"))
```

## Typ-Änderungen in einem Stream behandeln

Eine Schema-Tracking-Location ist in Databricks Runtime 18.0 und darunter erforderlich. Ab Runtime 18.1 ist sie optional. Sie muss im gleichen Pfad wie der Streaming-Checkpoint liegen. Nach einer erkannten Typ-Änderung entwickelt der Stream sein verfolgtes Schema weiter und stoppt. Danach muss die Typ-Änderung manuell behandelt werden.

```python
checkpoint_path = "/path/to/checkpointLocation"
(spark.readStream
 .option("schemaTrackingLocation", checkpoint_path)
 .table("delta_source_table")
 .writeStream
 .option("checkpointLocation", checkpoint_path)
 .toTable("output_table"))
```

Um eine erkannte Quellspalten-Typ-Änderung explizit zuzulassen, gibt es die Option `allowSourceColumnTypeChange`.

```python
checkpoint_path = "/path/to/checkpointLocation"
(spark.readStream
 .option("schemaTrackingLocation", checkpoint_path)
 .option("allowSourceColumnTypeChange", "<delta_source_table_version>")
 # alternatively to allow all future type changes for this stream:
 # .option("allowSourceColumnTypeChange", "always")
 .table("delta_source_table")
 .writeStream
 .option("checkpointLocation", checkpoint_path)
 .toTable("output_table"))
```

```sql
%sql
-- To unblock for this particular stream just for this series of schema change(s):
SET spark.databricks.delta.streaming.allowSourceColumnTypeChange.ckpt_<checkpoint_id> = "<delta_source_table_version>"

-- To unblock for this particular stream:
SET spark.databricks.delta.streaming.allowSourceColumnTypeChange = "<delta_source_table_version>"

-- To unblock for all streams:
SET spark.databricks.delta.streaming.allowSourceColumnTypeChange = "always"
```

## Lakeflow Pipelines

Type Widening lässt sich für eine ganze Pipeline oder für einzelne Tabellen aktivieren. Typ-Änderungen bei materialisierten Sichten lösen immer eine vollständige Neuberechnung aus. Wird eine Typ-Änderung an einer Quelltabelle angewendet, benötigen abhängige materialisierte Sichten ebenfalls eine vollständige Neuberechnung.

### Type Widening für eine ganze Pipeline aktivieren

```json
{
  "configuration": {
    "pipelines.enableTypeWidening": "true"
  }
}
```

```yaml
configuration:
  pipelines.enableTypeWidening: 'true'
```

### Type Widening für einzelne Tabellen aktivieren

```python
import dlt

@dlt.table(
    table_properties={"delta.enableTypeWidening": "true"})
def my_table():
    return spark.readStream.table("source_table")
```

```sql
%sql
CREATE OR REFRESH STREAMING TABLE my_table
TBLPROPERTIES ('delta.enableTypeWidening' = 'true')
AS SELECT * FROM source_table
```

## Kompatibilität mit nachgelagerten Lesern

Tabellen mit aktiviertem Type Widening lassen sich nur mit Databricks Runtime 15.4 LTS oder höher lesen. Um die Lesbarkeit für Runtime 14.3 und darunter zu erhalten, muss Type Widening deaktiviert werden oder der Compatibility Mode aktiviert sein.

```sql
%sql
ALTER TABLE <table-name> SET TBLPROPERTIES
('delta.universalFormat.config.icebergCompatVersion' = '<version>')
```

## OpenSharing

Unterstützung für Type Widening in OpenSharing gibt es ab Databricks Runtime 16.1. Anbieter und Empfänger müssen beide auf Databricks Runtime 16.1 oder höher laufen.

Das Lesen von Change Data Feed über eine Typ-Änderung hinweg wird nicht unterstützt. Stattdessen muss die Operation in zwei separate Lesevorgänge aufgeteilt werden: einer endet bei der Tabellenversion mit der Typ-Änderung, der andere beginnt bei dieser Version.

Tabellen mit aktiviertem Type Widening lassen sich über OpenSharing nicht mit Nicht-Databricks-Konsumenten teilen.

```python
spark.read
 .format("deltaSharing")
 .option("responseFormat", "delta")
 .option("readChangeFeed", "true")
 .option("startingVersion", "<start version>")
 .option("endingVersion", "<end version>")
 .load("<table>")
```

## Einschränkungen

### Kompatibilität mit Apache Iceberg

Apache Iceberg unterstützt nicht alle Typ-Änderungen, die Type Widening abdeckt. Nicht unterstützt sind zum Beispiel: BYTE, SHORT, INT, LONG zu Decimal oder Double, eine Erhöhung der Decimal-Skala sowie DATE zu TIMESTAMP_NTZ. Ist bei einer Delta-Tabelle das Lesen als Iceberg aktiviert, führen solche nicht unterstützten Typ-Änderungen zu einem Fehler.

### Typabhängige Funktionen

Funktionen wie `hash`, `xxhash64`, `bit_get`, `bit_reverse` und `typeof` liefern je nach Eingabetyp unterschiedliche Ergebnisse. Für stabile Ergebnisse müssen Werte explizit auf den gewünschten Typ gecastet werden.

```python
spark.read.table("table_name") \
    .selectExpr("hash(CAST(column_name AS BIGINT))")
```

```python
spark.read.table("main.johan_lasperas.dlt_type_widening_bronze2") \
    .selectExpr("hash(CAST(a AS BIGINT))")
```

```sql
%sql
-- Use explicit casting for stable hash values
SELECT hash(CAST(column_name AS BIGINT)) FROM table_name
```

### Nicht unterstützte Funktionen

- Die Schema-Tracking-Location kann bei Streaming mit Typ-Änderungen nicht per SQL gesetzt werden.
- Tabellen mit aktiviertem Type Widening lassen sich nicht über OpenSharing an Nicht-Databricks-Konsumenten teilen.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/features/type-widening  
**Stand:** 2026-08-06
