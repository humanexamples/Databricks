[← Übersicht](00%20Uebersicht.md)

# Deduplizierungs- und Upsert-Muster

Wird aus mehreren Fällen referenziert (u. a. [Fall 3](03%20Gleiche%20Datei%20wird%20ueberschrieben.md), [Fall 4](04%20Datei%20waechst.md), [Fall 6](06%20Change-Events%20in%20Dateien.md)).

## A – `MERGE INTO` in SQL (Batch oder in einer Streaming Table über einen Flow)

```sql
MERGE INTO catalog.schema.target t
USING (
  SELECT * FROM (
    SELECT *, row_number() OVER (PARTITION BY id ORDER BY updated_at DESC) AS rn
    FROM source_updates
  ) WHERE rn = 1                         -- Duplikate INNERHALB der neuen Daten entfernen
) s
ON t.id = s.id
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

> `MERGE` dedupliziert neue Daten gegen bestehende, **nicht** innerhalb der neuen Daten – daher der `row_number()`-Filter bzw. `dropDuplicates()` vorab.

## B – `foreachBatch` + `MERGE` (Auto-Loader-Stream mit Upsert)

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window

def upsert_to_delta(micro_batch_df, batch_id):
    w = Window.partitionBy("id").orderBy(col("updated_at").desc())
    deduped = (micro_batch_df
               .withColumn("_rn", row_number().over(w))
               .filter("_rn = 1").drop("_rn"))
    (DeltaTable.forName(spark, "catalog.schema.target").alias("t")
        .merge(deduped.alias("s"), "t.id = s.id")
        .whenMatchedUpdateAll(condition="s.updated_at > t.updated_at")
        .whenNotMatchedInsertAll()
        .execute())

(spark.readStream.format("cloudFiles")
   .option("cloudFiles.format", "json")
   .option("cloudFiles.schemaLocation", checkpoint)
   .option("cloudFiles.allowOverwrites", "true")
   .load("/Volumes/catalog/schema/landing/")
   .writeStream
   .foreachBatch(upsert_to_delta)
   .option("checkpointLocation", checkpoint)
   .trigger(availableNow=True)
   .start())
```

Hinweise: `MERGE` im `foreachBatch` muss **idempotent** sein (Batch-Wiederholung möglich). Bei Metrik-Verzerrung Batch-DataFrame vor dem `MERGE` `cache()`n und danach `unpersist()`en.

## C – Deklarativ ohne eigenen Merge-Code

`AUTO CDC INTO` / `create_auto_cdc_flow` ([Fall 6](06%20Change-Events%20in%20Dateien.md)) bzw. `create_auto_cdc_from_snapshot_flow` ([Fall 5](05%20Periodische%20Voll-Snapshots.md)) übernehmen Dedup + SCD automatisch (`SEQUENCE BY` bestimmt den „neuesten" Satz).

---
[← Übersicht](00%20Uebersicht.md)
