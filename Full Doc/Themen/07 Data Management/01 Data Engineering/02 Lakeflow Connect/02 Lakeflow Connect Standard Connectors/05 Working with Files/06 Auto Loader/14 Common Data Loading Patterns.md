# Auto Loader — Common Data Loading Patterns

---

## 1. Daten als Variant aufnehmen

Auto Loader kann alle Daten aus den unterstützten Dateiquellen als einzelne `VARIANT`-Spalte laden — flexibel bei Schema-Änderungen, unter Beibehaltung von Case-Sensitivity und Null-Werten.

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("singleVariantColumn", "data")
  .load("/Volumes/analytics/bronze/events"))
```

---

## 2. Verzeichnisse/Dateien mit Glob-Mustern filtern

| Muster | Trifft auf |
|---|---|
| `?` | Ein einzelnes Zeichen |
| `*` | Null oder mehr Zeichen |
| `[abc]` | Ein Zeichen aus der Menge `{a, b, c}` |
| `[a-z]` | Ein Zeichen aus dem Bereich `a`–`z` |
| `[^a]` | Ein Zeichen, das **nicht** aus der Menge `{a}` ist |
| `{ab,cd}` | Ein String aus der Menge `{ab, cd}` |
| `{ab,c{de,fh}}` | Ein String aus der Menge `{ab, cde, cfh}` |

Der `path`-Parameter erlaubt nur Präfix-Filterung; für Suffix-Muster `pathGlobFilter` verwenden.

```python
df = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "<format>") \
  .schema(schema) \
  .load("/Volumes/catalog_name/schema_name/volume_name/*/files")
```

```python
df = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "binaryFile") \
  .option("pathGlobfilter", "*.png") \
  .load("/Volumes/catalog_name/schema_name/volume_name/path")
```

---

## 3. Einfaches ETL ermöglichen

```python
spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "json") \
  .option("cloudFiles.schemaLocation", "<path-to-schema-location>") \
  .load("/Volumes/catalog_name/schema_name/volume_name/source_data") \
  .writeStream \
  .option("mergeSchema", "true") \
  .option("checkpointLocation", "<path-to-checkpoint>") \
  .start("<path_to_target>")
```

---

## 4. Datenverlust bei wohlstrukturierten Daten verhindern

```python
spark.readStream.format("cloudFiles") \
  .schema(expected_schema) \
  .option("cloudFiles.format", "json") \
  .option("cloudFiles.schemaEvolutionMode", "rescue") \
  .load("/Volumes/catalog_name/schema_name/volume_name/source_data") \
  .writeStream \
  .option("checkpointLocation", "<path-to-checkpoint>") \
  .start("<path_to_target>")
```

Um stattdessen bei neuen Spalten zu stoppen, statt zu retten:

```python
.option("cloudFiles.schemaEvolutionMode", "failOnNewColumns")
```

---

## 5. Flexible, semi-strukturierte Datenpipelines ermöglichen

```python
spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "json") \
  .option("cloudFiles.schemaHints",
          "headers map<string,string>, statusCode SHORT") \
  .load("/Volumes/catalog_name/schema_name/volume_name/api/requests") \
  .writeStream \
  .option("mergeSchema", "true") \
  .option("checkpointLocation", "<path-to-checkpoint>") \
  .start("<path_to_target>")
```

---

## 6. Verschachtelte JSON-Daten transformieren

```python
spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "json") \
  .option("cloudFiles.schemaLocation", "<path-to-checkpoint>") \
  .load("/Volumes/catalog_name/schema_name/volume_name/nested_json") \
  .selectExpr(
    "*",
    "tags:page.name",
    "tags:page.id::int",
    "tags:eventType"
  )
```

---

## 7. Verschachtelte JSON-Daten inferieren

```python
spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "json") \
  .option("cloudFiles.schemaLocation", "<path-to-checkpoint>") \
  .option("cloudFiles.inferColumnTypes", "true") \
  .load("/Volumes/catalog_name/schema_name/volume_name/nested_json")
```

---

## 8. CSV-Dateien ohne Header laden

```python
df = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "csv") \
  .option("rescuedDataColumn", "_rescued_data") \
  .schema(<schema>) \
  .load(<path>)
```

---

## 9. Schema auf CSV-Dateien mit Header erzwingen

```python
df = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "csv") \
  .option("header", "true") \
  .option("rescuedDataColumn", "_rescued_data") \
  .schema(<schema>) \
  .load(<path>)
```

---

## 10. Bild- oder Binärdaten für ML nach Delta Lake aufnehmen

```python
spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "binaryFile") \
  .load("/Volumes/catalog_name/schema_name/volume_name/images") \
  .writeStream \
  .option("checkpointLocation", "<path-to-checkpoint>") \
  .start("<path_to_target>")
```

---

## 11. Auto-Loader-Syntax für Lakeflow-Pipelines

Vollständiges Beispiel mit `multiLine`-JSON (Python-Dekorator-Syntax `@dp.tabledef` sowie SQL):

```python
@dp.tabledef
def booking_updates():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("multiLine", "true")
      .load("/Volumes/my_catalog/my_schema/my_volume/wanderbricks/booking_updates")
  )

@dp.tabledef
def reviews():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("multiLine", "true")
      .load("/Volumes/my_catalog/my_schema/my_volume/wanderbricks/reviews")
  )
```

```sql
CREATE OR REFRESH STREAMING TABLE booking_updates
AS SELECT * FROM STREAM read_files(
  "/Volumes/my_catalog/my_schema/my_volume/wanderbricks/booking_updates",
  format => "json",
  multiLine => true);

CREATE OR REFRESH STREAMING TABLE reviews
AS SELECT * FROM STREAM read_files(
  "/Volumes/my_catalog/my_schema/my_volume/wanderbricks/reviews",
  format => "json",
  multiLine => true);
```

Variante mit Spalten-Typ-Inferenz (SQL):

```sql
CREATE OR REFRESH STREAMING TABLE booking_updates
AS SELECT * FROM STREAM read_files(
  "/Volumes/my_catalog/my_schema/my_volume/wanderbricks/booking_updates",
  format => "json",
  multiLine => true,
  inferColumnTypes => true);
```

Variante mit explizitem Schema (Python und SQL):

```python
@dp.tabledef
def booking_updates_raw():
  return (
    spark.readStream.format("cloudFiles")
      .schema("booking_id LONG, booking_update_id LONG, user_id LONG, property_id LONG, status STRING, guests_count INT, total_amount DOUBLE, check_in DATE, check_out DATE, created_at TIMESTAMP, updated_at TIMESTAMP")
      .option("cloudFiles.format", "json")
      .option("multiLine", "true")
      .load("/Volumes/my_catalog/my_schema/my_volume/wanderbricks/booking_updates")
  )
```

```sql
CREATE OR REFRESH STREAMING TABLE booking_updates_raw
AS SELECT *
FROM STREAM read_files(
  "/Volumes/my_catalog/my_schema/my_volume/wanderbricks/booking_updates",
  format => "json",
  multiLine => true,
  schema => "booking_id LONG, booking_update_id LONG, user_id LONG, property_id LONG, status STRING, guests_count INT, total_amount DOUBLE, check_in DATE, check_out DATE, created_at TIMESTAMP, updated_at TIMESTAMP");
```

> **Hinweis:** Lakeflow-Pipelines verwalten Schema- und Checkpoint-Verzeichnisse automatisch; manuelle Konfiguration kann verhindern, dass ein Full Refresh diese Verzeichnisse betrifft.

---

# Praxis-Patterns: Multi-Flow-Ingestion und resilientes Bronze-Layer-Design

## Mehrere Quellen in eine Ziel-Streaming-Table: Multi-Flow-Pattern

Anstatt mehrere Quellen über `UNION` in einer Abfrage zusammenzuführen, empfiehlt Databricks, für jede Quelle einen eigenen, expliziten `CREATE FLOW` zu definieren, der unabhängig in dieselbe Ziel-Streaming-Table schreibt:

```sql
CREATE OR REFRESH STREAMING TABLE raw_orders;

CREATE FLOW raw_orders_us
AS INSERT INTO raw_orders BY NAME
SELECT * FROM STREAM read_files("/path/to/orders/us", format => "csv");

CREATE FLOW raw_orders_eu
AS INSERT INTO raw_orders BY NAME
SELECT * FROM STREAM read_files("/path/to/orders/eu", format => "csv");

CREATE FLOW raw_orders_apac
AS INSERT INTO raw_orders BY NAME
SELECT * FROM STREAM read_files("/path/to/orders/apac", format => "csv");
```

Jeder Flow betreibt seinen **eigenen** Auto-Loader-Zustand (eigener Checkpoint-Anteil, eigenes Datei-Tracking je Quellverzeichnis) innerhalb derselben Ziel-Streaming-Table. Nützlich, wenn Streaming-Quellen an eine bestehende Streaming Table anhängen sollen, ohne einen vollständigen Refresh zu erfordern — ein neuer Flow lässt sich nachträglich ergänzen, ohne bestehende Flows oder die Zieltabelle neu aufzubauen.

## Resilientes Bronze-Layer-Design: `schemaEvolutionMode => 'rescue'` + durchgängige `STRING`-Ingestion

Da Textformate (JSON, CSV, XML) ohne `cloudFiles.inferColumnTypes` standardmäßig als `string` inferiert werden und der Modus `rescue` bewirkt, dass Auto Loader das Schema nie weiterentwickelt und der Stream nicht wegen Schema-Änderungen fehlschlägt, lässt sich die Bronze-Schicht so konfigurieren, dass kein Datensatz wegen eines Typ- oder Schema-Konflikts verworfen wird oder den Stream zum Stoppen bringt. Die Typ-Durchsetzung wird bewusst auf die Silber-Schicht per `TRY_CAST` verschoben.

```sql
-- Bronze: Schema eingefroren, rescue-Modus verhindert Stream-Abbruch bei Schema-Drift
CREATE OR REFRESH STREAMING TABLE bronze_events
COMMENT 'Bronze: rescue-Modus verhindert Stream-Abbruch bei Schema-Drift'
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'rescue'
);
```

```sql
-- Silver: Typ-Durchsetzung mit TRY_CAST statt hartem CAST
CREATE OR REFRESH STREAMING TABLE silver_events (
  CONSTRAINT valid_amount EXPECT (
    CASE WHEN amount IS NOT NULL THEN amount >= 0 ELSE TRUE END
  ) ON VIOLATION DROP ROW
)
AS SELECT *,
  TRY_CAST(amount_str AS DOUBLE) AS amount
FROM STREAM bronze_events;
```

**Zusatzregel bei Constraints auf nachträglich hinzugekommenen Spalten:** Wird eine Spalte per Schema-Evolution oder `schemaHints` neu hinzugefügt, tragen alle davor eingelesenen Datensätze für diese Spalte `NULL`. Ein `EXPECT`-Constraint auf einer solchen Spalte sollte daher NULL-tolerant formuliert werden (`CASE WHEN ... IS NOT NULL THEN ... ELSE TRUE END`), da sonst historische Datensätze fälschlich als Constraint-Verletzung markiert würden.

## Ende-zu-Ende-Beispiel: `.trigger(processingTime=...)` statt `availableNow`

Ein Auto-Loader-Stream mit explizitem Schema und festem Intervall-Trigger. Dies ist der Structured-Streaming-eigene `.trigger()`-Parameter — nicht zu verwechseln mit den Lakeflow-Pipeline-Trigger-Konfigurationen (Continuous/File-Arrival/Scheduled) aus [11 Best Practices.md](11%20Best%20Practices.md).

```python
schema = "id BIGINT, event_type STRING, event_ts TIMESTAMP"

events_stream = (
  spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .schema(schema)
    .load("/Volumes/analytics/bronze/events")
  .writeStream
    .format("delta")
    .outputMode("append")
    .trigger(processingTime="3 seconds")
    .option("checkpointLocation", "/Volumes/analytics/bronze/_checkpoint")
    .table("workspace.default.events_bronze"))
```
