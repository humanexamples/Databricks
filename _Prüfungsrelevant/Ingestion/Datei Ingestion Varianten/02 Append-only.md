[← Übersicht](00%20Uebersicht.md)

# Fall 2 – Neue, unveränderliche Dateien kommen laufend dazu (Append-only)

Der empfohlene Standardfall. Jede Datei wird genau einmal geladen.

Dazu zählt auch der **periodische Drop mit eindeutigem Dateinamen** (z. B. täglich `orders_2026-09-04.csv`): Weil jeder Name neu ist, ist das technisch **derselbe** Fall – `COPY INTO` und Auto Loader tracken ohnehin pro Pfad. Wer bei eindeutigen Namen gezielt nur die neueste Datei laden will (statt sich auf das Tracking zu verlassen), findet dafür unten Option F.

---

**A) Auto Loader – kontinuierliches Streaming (Python)**

```python
checkpoint = "/Volumes/catalog/schema/_checkpoints/bronze"

(spark.readStream
 		.format("cloudFiles")
  		.option("cloudFiles.format", "json")
  		.option("cloudFiles.schemaLocation", checkpoint)
  		.option("cloudFiles.schemaEvolutionMode", "addNewColumns")
      	.load("/Volumes/catalog/schema/landing/")
      .writeStream
  		.option("checkpointLocation", checkpoint)
  		.trigger(processingTime="1 minute")
  		.toTable("catalog.schema.bronze"))
```

**B) Auto Loader – getriggerter Batch (`availableNow`) in einem Job**

```python
(spark.readStream
 		.format("cloudFiles")
  		.option("cloudFiles.format", "json")
  		.option("cloudFiles.schemaLocation", checkpoint)
  		.load("/Volumes/catalog/schema/landing/")
     .writeStream
  		.option("checkpointLocation", checkpoint)
  		.trigger(availableNow=True)  # alle bis Startzeit vorhandenen Dateien, dann Stop
  		.toTable("catalog.schema.bronze"))
```

Periode über den Job-Zeitplan, der dieses Notebook/Skript neu startet – z. B. täglich um 05:30:

```json
{
  "schedule": {
    "quartz_cron_expression": "0 30 5 * * ?",
    "timezone_id": "Europe/Berlin"
  }
}
```

**C) Auto Loader deklarativ in SQL (Streaming Table / Lakeflow Declarative Pipelines)**

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.bronze
  SCHEDULE REFRESH EVERY 1 HOUR
AS SELECT
     *,
     _metadata.file_path AS file_path
   FROM STREAM read_files(
     '/Volumes/catalog/schema/landing/',
     format => 'json'
   );
```

**D) `COPY INTO` in einem geplanten Job** (idempotent – bereits geladene Dateien werden übersprungen; bei eindeutigen Namen lädt jeder Lauf automatisch nur die neuen Dateien):

```sql
COPY INTO catalog.schema.bronze
FROM '/Volumes/catalog/schema/landing/'
FILEFORMAT = JSON
COPY_OPTIONS ('mergeSchema' = 'true');
```

**E) Python-Pipeline (Lakeflow Declarative Pipelines)**

```python
from pyspark import pipelines as dp   # ältere Syntax: import dlt  ->  @dlt.table

@dp.table(name="bronze")
def bronze():
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "json")
            .load("/Volumes/catalog/schema/landing/"))
```

**F) Nur gezielt die neueste Datei laden** (optional bei eindeutigem Namen, ohne sich auf Tracking zu verlassen)

`COPY INTO` mit `PATTERN` oder `FILES`:

```sql
COPY INTO catalog.schema.orders_bronze
FROM '/Volumes/catalog/schema/landing/orders/'
FILEFORMAT = CSV
PATTERN = 'orders_????-??-??.csv'
FORMAT_OPTIONS ('header' = 'true');
```

Batch `read_files()` mit Zeitfenster-Filter (nur die zuletzt geänderten Dateien):

```sql
CREATE OR REPLACE TABLE catalog.schema.orders_today AS
SELECT * FROM read_files(
  '/Volumes/catalog/schema/landing/orders/',
  format        => 'csv',
  header        => true,
  modifiedAfter => date_sub(current_timestamp(), 1)
);
```

---
[← Vorheriger Fall](01%20Einmaliger%2C%20statischer%20Bestand.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](03%20Gleiche%20Datei%20wird%20ueberschrieben.md)
