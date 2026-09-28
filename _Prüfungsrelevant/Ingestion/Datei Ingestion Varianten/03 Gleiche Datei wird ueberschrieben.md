[← Übersicht](00%20Uebersicht.md)

# Fall 3 – Gleiche Datei, gleicher Ort, wird periodisch überschrieben (neuer Inhalt, gleicher Name)

Standardmäßig wird der neue Inhalt **nicht** geladen (`COPY INTO` überspringt die Datei, Auto Loader trackt sie über den Pfad als „erledigt"). Man muss das Tracking bewusst aufweichen (`force = true` / `cloudFiles.allowOverwrites = true`) oder ohne Tracking arbeiten (Batch `read_files()` / `spark.read`).

**Die entscheidende Frage ist, was im Ziel passieren soll.** Danach sind die Umsetzungen gegliedert:

| Abschnitt | Verhalten im Ziel | Historie? |
|---|---|---|
| [1](#s1) | Ziel wird bei jedem Lauf **komplett ersetzt** | nein |
| [2](#s2) | Zeilen werden **angehängt** (jede Datei-Version bleibt als Rohdaten erhalten) | ja (roh, alle Versionen) |
| [3](#s3) | **Insert / Update / Delete** je Key, nur der **aktuelle** Stand (SCD Type 1) | nein |
| [4](#s4) | **Insert / Update / Delete** je Key **mit Versionshistorie** (SCD Type 2) | ja (fachlich, mit Gültigkeitszeitraum) |

## <a id="trigger">Die zwei Auslöse-Varianten</a>

**Jede** Umsetzung unten wird als **zwei getrennte, vollständige Code-Beispiele** gezeigt (jeweils mit Option Python und Option SQL, wo beide existieren):

| | **⏱ Feste Periode** | **⚡ Bei Überschreiben in der Source-Location** |
|---|---|---|
| Structured Streaming | `.trigger(processingTime="15 minutes")` | `.option("cloudFiles.useNotifications", "true")` + **kein** `.trigger(...)` (läuft, sobald das Cloud-Event eintrifft) |
| Streaming Table (SQL) | `SCHEDULE REFRESH EVERY 15 MINUTES` | `TRIGGER ON UPDATE AT MOST EVERY INTERVAL 1 MINUTE` (setzt aktivierte *File Events* auf der External Location voraus) |
| Batch (SQL / Python / `COPY INTO`) | Databricks-Job mit `quartz_cron_expression` | dasselbe Statement in `foreachBatch` eines kontinuierlichen Auto-Loader-Notification-Streams |

> **Nicht** geeignet für „bei Überschreiben": ein Job-`file_arrival`-Trigger – der feuert **nur bei neuen Dateinamen**, nicht wenn eine bestehende Datei am selben Pfad ersetzt wird.

---

## <a id="s1">1. Ziel komplett überschreiben (Full Overwrite / Replace)</a>

**Wann:** Die Datei enthält immer den kompletten aktuellen Stand, keine Historie, kein Key-Abgleich. Idempotent per Full Refresh, kein File Tracking nötig.

### a) Ganze Tabelle ersetzen

**⏱ Feste Periode** – Notebook mit dieser Zelle, per Job-Cron stündlich:

```python
# Option 1 – Python
df = (spark.read
        .format("csv")
        .option("header", "true")
        .load("/Volumes/catalog/schema/landing/current.csv"))

(df.write
   .format("delta")
   .mode("overwrite")
   .option("overwriteSchema", "true")
   .saveAsTable("catalog.schema.target"))
```

```sql
-- Option 2 – SQL
INSERT OVERWRITE catalog.schema.target
SELECT * FROM read_files('/Volumes/catalog/schema/landing/current.csv', format => 'csv', header => true);
```

```json
{ "schedule": { "quartz_cron_expression": "0 0 * * * ?", "timezone_id": "Europe/Berlin" } }
```

**⚡ Bei Überschreiben** – Notification-Stream, der pro Event einmal überschreibt:

```python
# eine der beiden foreachBatch-Funktionen wählen:

# Option 1 – Python
def overwrite_target(batch_df, _):
    (batch_df.write
       .format("delta").mode("overwrite")
       .option("overwriteSchema", "true")
       .saveAsTable("catalog.schema.target"))

# Option 2 – SQL
def overwrite_target(batch_df, _):
    batch_df.createOrReplaceTempView("incoming")
    batch_df.sparkSession.sql("INSERT OVERWRITE catalog.schema.target SELECT * FROM incoming")

(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_checkpoints/target")
  .option("cloudFiles.useNotifications", "true")
  .option("cloudFiles.allowOverwrites", "true")
  .option("header", "true")
  .load("/Volumes/catalog/schema/landing/")
  .writeStream
  .foreachBatch(overwrite_target)
  .option("checkpointLocation", "/Volumes/catalog/schema/_checkpoints/target")
  .start())
```

### b) Tabelle bei jedem Lauf neu aufbauen (`CREATE OR REPLACE TABLE`)

**⏱ Feste Periode** – identisch zur `SQL`-Option in a), nur mit Schema-Neuaufbau; per Job-Cron:

```sql
CREATE OR REPLACE TABLE catalog.schema.target AS
SELECT * FROM read_files('/Volumes/catalog/schema/landing/current.csv', format => 'csv', header => true);
```

```json
{ "schedule": { "quartz_cron_expression": "0 0 * * * ?", "timezone_id": "Europe/Berlin" } }
```

> Eine normale Tabelle hat **keine** `SCHEDULE REFRESH`-Klausel (`CREATE OR REFRESH TABLE` existiert nicht) – der Zeitplan kommt immer über den Job. Ein eingebautes `SCHEDULE REFRESH` haben nur `STREAMING TABLE` (hängt an) und `MATERIALIZED VIEW` (voll re-materialisiert, aber read-only und nur sinnvoll bei transformierenden Queries).

**⚡ Bei Überschreiben** – kein deklaratives Full-Overwrite mit Event-Trigger → den Notification-Stream aus **[a) ⚡](#s1)** verwenden.

---

## <a id="s2">2. Append: Zeilen ans Ziel anhängen</a>

**Wann:** Jede Datei-Version soll als Rohschicht (Bronze) erhalten bleiben. Ohne nachgelagerte Dedup entstehen bei jeder Dateiänderung **Duplikate**.

### a) Anhängen (Batch)

**⏱ Feste Periode** – per Job-Cron stündlich:

```python
# Option 1 – Python
df = spark.read.format("csv")
				.option("header", "true")
    			.load("/Volumes/catalog/schema/landing/")
df.write.format("delta")
		.mode("append")
    	.saveAsTable("catalog.schema.bronze_raw")
```

```sql
-- Option 2 – SQL
INSERT INTO catalog.schema.bronze_raw
SELECT *, _metadata.file_modification_time AS _src_mtime, current_timestamp() AS _ingest_ts
FROM read_files('/Volumes/catalog/schema/landing/', format => 'csv', header => true);
```

```json
{ "schedule": { "quartz_cron_expression": "0 0 * * * ?", "timezone_id": "Europe/Berlin" } }
```

**⚡ Bei Überschreiben** – Notification-Stream:

```python
# Option 1 – Python: reiner Append über .toTable()
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_checkpoints/bronze_raw")
  .option("cloudFiles.useNotifications", "true")
  .option("cloudFiles.allowOverwrites", "true")
  .option("header", "true")
  .load("/Volumes/catalog/schema/landing/")
  .writeStream
  .option("checkpointLocation", "/Volumes/catalog/schema/_checkpoints/bronze_raw")
  .toTable("catalog.schema.bronze_raw"))
```

```python
# Option 2 – SQL-INSERT im foreachBatch (wenn zusätzliche Spalten / SQL-Logik nötig)
def append_target(batch_df, _):
    batch_df.createOrReplaceTempView("incoming")
    batch_df.sparkSession.sql("INSERT INTO catalog.schema.bronze_raw SELECT * FROM incoming")

(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_checkpoints/bronze_raw")
  .option("cloudFiles.useNotifications", "true")
  .option("cloudFiles.allowOverwrites", "true")
  .option("header", "true")
  .load("/Volumes/catalog/schema/landing/")
  .writeStream
  .foreachBatch(append_target)
  .option("checkpointLocation", "/Volumes/catalog/schema/_checkpoints/bronze_raw")
  .start())
```

### b) `COPY INTO` mit `force`

**⏱ Feste Periode** – per Job-Cron:

```sql
COPY INTO catalog.schema.bronze_raw
FROM '/Volumes/catalog/schema/landing/'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true') -- If set to true, idempotency is disabled 
                                   -- and files are loaded regardless of whether 
                                   -- they've been loaded before.
COPY_OPTIONS  ('force' = 'true');
```

```json
{ "schedule": { "quartz_cron_expression": "0 0 * * * ?", "timezone_id": "Europe/Berlin" } }
```

**⚡ Bei Überschreiben** – `COPY INTO` hat keine Event-Auslösung → stattdessen den Notification-Stream aus **[a) ⚡](#s2)** verwenden.

### c) Auto Loader – Streaming

**⏱ Feste Periode**

```python
# Option 1 – Python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_checkpoints/bronze_raw")
  .option("cloudFiles.allowOverwrites", "true") # To allow Auto Loader to process the file 
                                                # again when it is appended to or 
                                                # overwritten, you can set 
                                                # cloudFiles.allowOverwrites to true.
  .option("header", "true")
  .load("/Volumes/catalog/schema/landing/")
  .writeStream
  .option("checkpointLocation", "/Volumes/catalog/schema/_checkpoints/bronze_raw")
  .trigger(processingTime="15 minutes")
  .toTable("catalog.schema.bronze_raw"))
```

```sql
-- Option 2 – SQL (Streaming Table)
CREATE OR REFRESH STREAMING TABLE catalog.schema.bronze_raw
  SCHEDULE REFRESH EVERY 15 MINUTES
AS SELECT *, _metadata.file_modification_time AS _src_mtime
   FROM STREAM read_files(
       '/Volumes/catalog/schema/landing/',
       format => 'csv', 
       header => true, 
       allowOverwrites => true);
```

**⚡ Bei Überschreiben**

```python
# Option 1 – Python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_checkpoints/bronze_raw")
  .option("cloudFiles.allowOverwrites", "true")
  .option("cloudFiles.useNotifications", "true")
  .option("header", "true")
  .load("/Volumes/catalog/schema/landing/")
  .writeStream
  .option("checkpointLocation", "/Volumes/catalog/schema/_checkpoints/bronze_raw")
  .toTable("catalog.schema.bronze_raw"))
```

```sql
-- Option 2 – SQL (Streaming Table, File Events aktiviert)
CREATE OR REFRESH STREAMING TABLE catalog.schema.bronze_raw
  TRIGGER ON UPDATE AT MOST EVERY INTERVAL 1 MINUTE
AS SELECT *, _metadata.file_modification_time AS _src_mtime
   FROM STREAM read_files(
       '/Volumes/catalog/schema/landing/',
       format => 'csv', 
       header => true, 
       allowOverwrites => true);
```

### d) Auto Loader – Lakeflow-Pipeline (`@dp.table`)

Pipeline-Code identisch; die Periode ist eine Pipeline-Einstellung.

```python
from pyspark import pipelines as dp

@dp.table(name="bronze_raw")
def bronze_raw():
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "csv")
            .option("cloudFiles.allowOverwrites", "true")
            .option("header", "true")
            .load("/Volumes/catalog/schema/landing/"))
```

**⏱ Feste Periode** – Pipeline im *Triggered*-Modus (`{ "continuous": false }`) + Job-Cron.
**⚡ Bei Überschreiben** – Pipeline im *Continuous*-Modus (`{ "continuous": true }`); in der `@dp.table` zusätzlich `.option("cloudFiles.useNotifications", "true")`.

---

## <a id="s3">3. Insert / Update / Delete ohne Historie (Upsert / SCD Type 1)</a>

**Wann:** Pro Business-Key (`id`) nur der **aktuelle** Stand. Geänderte Zeilen aktualisiert, neue eingefügt, im Snapshot fehlende gelöscht.

### a) Upsert per `MERGE`

**⏱ Feste Periode** – Batch-Skript / SQL-Zelle, per Job-Cron alle 30 Min.:

```python
# Option 1 – Python (DeltaTable-API)
from delta.tables import DeltaTable
from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window

incoming = spark.read
				.format("csv")
    			.option("header", "true")
        		.load("/Volumes/catalog/schema/landing/")
w = Window.partitionBy("id").orderBy(col("updated_at").desc())
deduped = incoming.withColumn("_rn", row_number().over(w)).filter("_rn = 1").drop("_rn")

(DeltaTable.forName(spark, "catalog.schema.target").alias("t")
  .merge(deduped.alias("s"), "t.id = s.id")
  .whenMatchedUpdateAll().whenNotMatchedInsertAll().whenNotMatchedBySourceDelete()
  .execute())
```

```sql
-- Option 2 – SQL
CREATE OR REPLACE TEMP VIEW incoming AS
SELECT * FROM read_files('/Volumes/catalog/schema/landing/', format => 'csv', header => true);

MERGE INTO catalog.schema.target t
USING (
    SELECT * FROM (SELECT *, row_number() 
                   OVER (PARTITION BY id ORDER BY updated_at DESC) AS rn
                   FROM incoming) 
    WHERE rn = 1) s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE;
```

```json
{ "schedule": { "quartz_cron_expression": "0 0/30 * * * ?", "timezone_id": "Europe/Berlin" } }
```

**⚡ Bei Überschreiben** – dieselbe Merge-Logik in `foreachBatch` eines Notification-Streams:

```python
# eine der beiden foreachBatch-Funktionen wählen:

# Option 1 – Python (DeltaTable-API)
from delta.tables import DeltaTable
from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window

def upsert(batch_df, _):
    w = Window.partitionBy("id").orderBy(col("updated_at").desc())
    deduped = batch_df.withColumn("_rn", row_number().over(w)).filter("_rn = 1").drop("_rn")
    (DeltaTable.forName(spark, "catalog.schema.target").alias("t")
      .merge(deduped.alias("s"), "t.id = s.id")
      .whenMatchedUpdateAll().whenNotMatchedInsertAll().whenNotMatchedBySourceDelete()
      .execute())

# Option 2 – SQL
def upsert(batch_df, _):
    batch_df.createOrReplaceTempView("incoming")
    batch_df.sparkSession.sql("""
        MERGE INTO catalog.schema.target t
        USING (SELECT * FROM (SELECT *, row_number() OVER (PARTITION BY id ORDER BY updated_at DESC) AS rn
                              FROM incoming) WHERE rn = 1) s
        ON t.id = s.id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
        WHEN NOT MATCHED BY SOURCE THEN DELETE
    """)

(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_checkpoints/target")
  .option("cloudFiles.useNotifications", "true")
  .option("cloudFiles.allowOverwrites", "true")
  .option("header", "true")
  .load("/Volumes/catalog/schema/landing/")
  .writeStream
  .foreachBatch(upsert)
  .option("checkpointLocation", "/Volumes/catalog/schema/_checkpoints/target")
  .start())
```

> Merge-Feinheiten (Dedup, `updated_at`-Vergleich, Batch-Wiederholung) siehe [99 Dedup und Upsert Muster.md](99%20Dedup%20und%20Upsert%20Muster.md).

### b) Deklarativ – `create_auto_cdc_from_snapshot_flow(..., stored_as_scd_type = 1)`

Lakeflow Declarative Pipelines, **nur Python** (kein SQL für „AUTO CDC FROM SNAPSHOT"). Erkennt Insert/Update/Delete durch Snapshot-Vergleich.

```python
from pyspark import pipelines as dp

@dp.view(name="snapshot")
def snapshot():
    return spark.read.format("csv").option("header", True).load("/Volumes/catalog/schema/landing/")

dp.create_streaming_table("catalog.schema.target")
dp.create_auto_cdc_from_snapshot_flow(
    target="catalog.schema.target", source="snapshot", keys=["id"], stored_as_scd_type=1)
```

**⏱ Feste Periode** – Pipeline im *Triggered*-Modus (`{ "continuous": false }`) + Job-Cron.
**⚡ Bei Überschreiben** – Snapshot-Flows haben **keinen** file-overwrite-Trigger → die `foreachBatch`-`MERGE`-Variante aus **[a) ⚡](#s3)** verwenden.

### c) Ohne Merge-Code – Tabelle bei jedem Lauf neu aufbauen (mit `QUALIFY`)

Die Zieltabelle wird bei jedem Lauf komplett aus dem deduplizierten Dateiinhalt neu geschrieben – Update/Delete ergeben sich automatisch, kein `MERGE` nötig.

**⏱ Feste Periode** – per Job-Cron alle 30 Min.:

```sql
CREATE OR REPLACE TABLE catalog.schema.target AS
SELECT * EXCEPT (rn) FROM (
  SELECT *, row_number() OVER (PARTITION BY id ORDER BY updated_at DESC) AS rn
  FROM read_files('/Volumes/catalog/schema/landing/', format => 'csv', header => true)
) WHERE rn = 1;
```

```json
{ "schedule": { "quartz_cron_expression": "0 0/30 * * * ?", "timezone_id": "Europe/Berlin" } }
```

> Deklarative Alternative ohne Job: dieselbe Query als **Materialized View** mit `SCHEDULE REFRESH EVERY 30 MINUTES` – lohnt sich hier aber nur, wenn die Query weitere Transformationen enthält (read-only, serverloses Compute).

**⚡ Bei Überschreiben** – Full-Rebuild hat keinen Event-Trigger → die `foreachBatch`-`MERGE`-Variante aus **[a) ⚡](#s3)** verwenden.

> Enthält die Datei **explizite** Lösch-Marker (`operation = 'DELETE'`) statt eines Voll-Snapshots → Fall 6: [Change-Events](06%20Change-Events%20in%20Dateien.md).

---

## <a id="s4">4. Insert / Update / Delete mit Historie (SCD Type 2)</a>

**Wann:** Jede Version einer Zeile wird historisiert (`__START_AT`/`__END_AT` bzw. `valid_from`/`valid_to`/`is_current`).

### a) Deklarativ (empfohlen) – `create_auto_cdc_from_snapshot_flow(..., stored_as_scd_type = 2)`

Lakeflow Declarative Pipelines, **nur Python**.

```python
from pyspark import pipelines as dp

@dp.view(name="snapshot")
def snapshot():
    return spark.read.format("csv").option("header", True).load("/Volumes/catalog/schema/landing/")

dp.create_streaming_table("catalog.schema.target_history")
dp.create_auto_cdc_from_snapshot_flow(
    target="catalog.schema.target_history", source="snapshot", keys=["id"], stored_as_scd_type=2)
```

**⏱ Feste Periode** – Pipeline im *Triggered*-Modus (`{ "continuous": false }`) + Job-Cron.
**⚡ Bei Überschreiben** – Snapshot-Flows haben **keinen** file-overwrite-Trigger → die manuelle SCD-2-`MERGE`-Variante **[b) ⚡](#s4)** verwenden.

### b) Manuell per `MERGE` (Zwei-Schritt-Muster)

`hash` = Hash aller fachlichen Spalten zum Änderungsvergleich. Kern-Logik (in beiden Varianten identisch, hier auf einer Quell-View `incoming`):

```sql
CREATE OR REPLACE TEMP VIEW staged_updates AS
SELECT i.id AS mergeKey, i.* FROM incoming i
UNION ALL
SELECT NULL AS mergeKey, i.* FROM incoming i
JOIN catalog.schema.target_history t ON i.id = t.id AND t.is_current = true AND i.hash <> t.hash;

MERGE INTO catalog.schema.target_history t
USING staged_updates s
ON t.id = s.mergeKey AND t.is_current = true
WHEN MATCHED AND t.hash <> s.hash THEN
  UPDATE SET is_current = false, valid_to = current_timestamp()
WHEN NOT MATCHED THEN
  INSERT (id, name, region, status, hash, is_current, valid_from, valid_to)
  VALUES (s.id, s.name, s.region, s.status, s.hash, true, current_timestamp(), NULL);

-- Deletes bei Snapshot: im Snapshot fehlende offene Zeilen schließen
MERGE INTO catalog.schema.target_history t
USING incoming s ON t.id = s.id
WHEN NOT MATCHED BY SOURCE AND t.is_current = true THEN
  UPDATE SET is_current = false, valid_to = current_timestamp();
```

**⏱ Feste Periode** – `incoming` aus `read_files()`, alles als SQL-Zellen per Job-Cron alle 30 Min.:

```sql
CREATE OR REPLACE TEMP VIEW incoming AS
SELECT *, sha2(concat_ws('|', name, region, status), 256) AS hash
FROM read_files('/Volumes/catalog/schema/landing/', format => 'csv', header => true);
-- ... danach die Kern-Logik oben
```

```json
{ "schedule": { "quartz_cron_expression": "0 0/30 * * * ?", "timezone_id": "Europe/Berlin" } }
```

**⚡ Bei Überschreiben** – `incoming` ist der Micro-Batch-DataFrame; die Kern-Logik per `spark.sql(...)` im `foreachBatch` eines Notification-Streams:

```python
from pyspark.sql.functions import sha2, concat_ws

def scd2(batch_df, _):
    (batch_df
      .withColumn("hash", sha2(concat_ws("|", "name", "region", "status"), 256))
      .createOrReplaceTempView("incoming"))
    sql = batch_df.sparkSession.sql
    sql("""CREATE OR REPLACE TEMP VIEW staged_updates AS
           SELECT i.id AS mergeKey, i.* FROM incoming i
           UNION ALL
           SELECT NULL AS mergeKey, i.* FROM incoming i
           JOIN catalog.schema.target_history t
             ON i.id = t.id AND t.is_current = true AND i.hash <> t.hash""")
    sql("""MERGE INTO catalog.schema.target_history t USING staged_updates s
           ON t.id = s.mergeKey AND t.is_current = true
           WHEN MATCHED AND t.hash <> s.hash THEN
             UPDATE SET is_current = false, valid_to = current_timestamp()
           WHEN NOT MATCHED THEN
             INSERT (id, name, region, status, hash, is_current, valid_from, valid_to)
             VALUES (s.id, s.name, s.region, s.status, s.hash, true, current_timestamp(), NULL)""")
    sql("""MERGE INTO catalog.schema.target_history t USING incoming s ON t.id = s.id
           WHEN NOT MATCHED BY SOURCE AND t.is_current = true THEN
             UPDATE SET is_current = false, valid_to = current_timestamp()""")

(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_checkpoints/target_history")
  .option("cloudFiles.useNotifications", "true")
  .option("cloudFiles.allowOverwrites", "true")
  .option("header", "true")
  .load("/Volumes/catalog/schema/landing/")
  .writeStream
  .foreachBatch(scd2)
  .option("checkpointLocation", "/Volumes/catalog/schema/_checkpoints/target_history")
  .start())
```

### c) CDF-basiert

Wenn bereits eine Append-Bronze-Tabelle ([Abschnitt 2](#s2)) mit aktiviertem Change Data Feed existiert:

```sql
ALTER TABLE catalog.schema.bronze_raw SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
-- danach: SELECT * FROM table_changes('catalog.schema.bronze_raw', <startVersion>) ... in ein foreachBatch-MERGE
```

**⏱ / ⚡** ergeben sich aus dem Trigger des `table_changes`-Streams (`processingTime` vs. `useNotifications` auf der Bronze-Quelle, kein Trigger).

> Datenbasierte CDC-Feeds (Dateien mit `operation`-Spalte statt Snapshots) → [Fall 6](06%20Change-Events%20in%20Dateien.md): SQL-`AUTO CDC INTO … STORED AS SCD TYPE 2`.

---
[← Vorheriger Fall](02%20Append-only.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](04%20Datei%20waechst.md)
