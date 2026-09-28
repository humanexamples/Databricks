[← Übersicht](00%20Uebersicht.md)

# Fall 1 – Einmaliger, statischer Bestand

Alle Dateien liegen bereits vor, es kommen keine neuen dazu.

**A) CTAS mit `read_files()` (SQL)**

```sql
CREATE OR REPLACE TABLE catalog.schema.bronze AS
SELECT
  *,
  _metadata.file_path              AS file_path,
  _metadata.file_modification_time AS file_modification_time
FROM read_files('/Volumes/catalog/schema/landing/', format => 'json');
```

**B) `spark.read` (Python)**

```python
df = (spark.read
      .format("json")
      .load("/Volumes/catalog/schema/landing/"))
df.write.mode("overwrite").saveAsTable("catalog.schema.bronze")
```

**C) `COPY INTO` einmalig**

```sql
CREATE TABLE IF NOT EXISTS catalog.schema.bronze;

COPY INTO catalog.schema.bronze
FROM '/Volumes/catalog/schema/landing/'
FILEFORMAT = JSON
FORMAT_OPTIONS ('mergeSchema' = 'true')
COPY_OPTIONS  ('mergeSchema' = 'true');
```

**D) Auto Loader im Einmal-Modus** (`availableNow`) – sinnvoll, wenn der Bestand später doch wächst:

```python
checkpoint = "/Volumes/catalog/schema/_checkpoints/bronze"

(spark.readStream.format("cloudFiles")
  		.option("cloudFiles.format", "json")
  		.option("cloudFiles.schemaLocation", checkpoint)
  		.load("/Volumes/catalog/schema/landing/")
  	  .writeStream
  		.option("checkpointLocation", checkpoint)
  		.trigger(availableNow=True)
  		.toTable("catalog.schema.bronze"))
```

**E) `INSERT INTO … SELECT … FROM read_files(…)`** – einfachste Variante, wenn die Zieltabelle bereits existiert (Schema also schon feststeht); auch mit direkter Cloud-URI statt Volume-Pfad möglich (erfordert `READ FILES` auf einer passenden Unity-Catalog-External-Location):

```sql
INSERT INTO catalog.schema.bronze
SELECT * FROM read_files(
  'abfss://container@storageaccount.dfs.core.windows.net/pfad/zu/dateien/',
  format => 'json'
);
```

> **Kein File Tracking, nicht idempotent:** Im Unterschied zu A–D merkt sich `INSERT INTO` nichts – ein erneuter Lauf liest **alle** Dateien am Pfad erneut und hängt sie **nochmal** an (Duplikate). Nur für einen echten Einmal-Lauf geeignet, nicht für wiederholte/geplante Ausführung. Für Full-Refresh-Wiederholbarkeit stattdessen `INSERT OVERWRITE` statt `INSERT INTO` verwenden (siehe [Fall 9](09%20Korrektur%2C%20Teilmenge%20neu%20laden.md)).

---
[← Übersicht](00%20Uebersicht.md) · [Nächster Fall →](02%20Append-only.md)
