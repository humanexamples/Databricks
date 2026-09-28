[← Übersicht](00%20Uebersicht.md)

# CDC prozedural mit `foreachBatch` und `MERGE`

**Kombination:** Structured Streaming · `foreachBatch` · Window-Funktion (`row_number`) · Delta `MERGE` · Lakeflow Jobs (`availableNow`)

Derselbe Zweck wie `AUTO CDC`, aber **ohne Pipeline**: ein normaler Stream in einem Notebook oder Job, der jeden Micro-Batch per `MERGE` auf die Zieltabelle anwendet. Sinnvoll, wenn freie Merge-Logik nötig ist oder die Verarbeitung auf Classic Compute ohne Pipeline laufen soll.

Die einfache Upsert-Variante **ohne Deletes** steht in [Dedup- und Upsert-Muster, Abschnitt B](../Ingestion/Datei%20Ingestion%20Varianten/99%20Dedup%20und%20Upsert%20Muster.md). Hier kommt hinzu: **Deletes** und **Schutz vor veralteten Events**.

---

## Zieltabelle

```sql
CREATE TABLE IF NOT EXISTS catalog.schema.silver_customers (
  customer_id BIGINT,
  name        STRING,
  city        STRING,
  email       STRING,
  change_ts   TIMESTAMP        -- Sequenz des zuletzt angewendeten Events
)
CLUSTER BY (customer_id);      -- Liquid Clustering auf dem Merge-Key beschleunigt das MERGE
```

## Batch-Funktion

```python
from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql.window import Window

TARGET = "catalog.schema.silver_customers"
COLS   = ["customer_id", "name", "city", "email", "change_ts"]

def apply_cdc_batch(batch_df, batch_id):
    # 1. Pro Key nur das jüngste Event dieses Micro-Batches behalten.
    #    MERGE bricht ab, wenn mehrere Quellzeilen dieselbe Zielzeile treffen.
    w = Window.partitionBy("customer_id").orderBy(F.col("change_ts").desc())
    latest = (batch_df.withColumn("_rn", F.row_number().over(w))
                      .filter("_rn = 1")
                      .drop("_rn"))

    # 2. Events anwenden — aber nur, wenn sie neuer sind als der Stand im Ziel.
    (DeltaTable.forName(batch_df.sparkSession, TARGET).alias("t")
        .merge(latest.alias("s"), "t.customer_id = s.customer_id")
        .whenMatchedDelete(
            condition = "s.op = 'd' AND s.change_ts >= t.change_ts")
        .whenMatchedUpdate(
            condition = "s.op <> 'd' AND s.change_ts > t.change_ts",
            set       = {c: f"s.{c}" for c in COLS})
        .whenNotMatchedInsert(
            condition = "s.op <> 'd'",
            values    = {c: f"s.{c}" for c in COLS})
        .execute())
```

## Stream starten

```python
(spark.readStream.table("catalog.schema.bronze_customers_cdc")   # Bronze aus 01
    .select(F.coalesce("after.customer_id", "before.customer_id").alias("customer_id"),
            F.col("after.name").alias("name"),
            F.col("after.city").alias("city"),
            F.col("after.email").alias("email"),
            F.col("op"),
            F.expr("timestamp_millis(ts_ms)").alias("change_ts"))
    .writeStream
    .foreachBatch(apply_cdc_batch)
    .option("checkpointLocation", "/Volumes/catalog/schema/_checkpoints/silver_customers")
    .trigger(availableNow=True)          # verarbeitet alles Neue und stoppt → ideal als Job-Task
    .start())
```

Mit `trigger(availableNow=True)` läuft der Stream wie ein Batch: Ein Lakeflow Job startet ihn z. B. stündlich oder per **Table-Update-Trigger**, sobald Bronze neue Daten hat.

---

## Die Bausteine im Zusammenspiel

| Baustein | Warum nötig |
|---|---|
| `row_number()` pro Key | Ein Micro-Batch kann mehrere Events desselben Keys enthalten |
| `s.change_ts > t.change_ts` | Ein verspätetes, älteres Event darf einen neueren Stand nicht überschreiben |
| `whenMatchedDelete` | Deletes der Quelle werden im Ziel ausgeführt |
| `whenNotMatchedInsert` mit `op <> 'd'` | Ein Delete für einen unbekannten Key erzeugt keine Zeile |
| Checkpoint | Exactly-once: Nach einem Absturz wird ab dem letzten bestätigten Batch weitergemacht |
| Idempotentes `MERGE` | Wird ein Batch wiederholt, ändert sich das Ergebnis nicht (Sequenzvergleich) |

## Grenzen gegenüber `AUTO CDC`

| Aspekt | `foreachBatch` + `MERGE` | `AUTO CDC` |
|---|---|---|
| Delete, danach verspätetes älteres Update | Zeile wird **wieder eingefügt** (kein Gedächtnis für gelöschte Keys) | gelöschte Keys werden eine Zeit lang als Tombstones gemerkt → korrekt |
| SCD 2 | viel eigener Code → [../SCD/03](../SCD/03%20SCD%20Type%202%20manuell%20mit%20MERGE.md) | `STORED AS SCD TYPE 2` |
| Metriken | selbst bauen | `num_upserted_rows`, `num_deleted_rows` im Event Log |
| Freiheit | beliebige Bedingungen, mehrere Ziele pro Batch | festes Schema (Keys, Sequenz, Delete-Bedingung) |
| Laufzeit | jedes Compute, kein Pipeline-Kontext | Lakeflow Pipeline (Serverless / Pro / Advanced) |

---
[← Vorherige Datei](02%20CDC%20aus%20Kafka.md) · [Übersicht](00%20Uebersicht.md) · [Nächste Datei →](04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md)

## Quellen

- [Use foreachBatch to write to arbitrary data sinks](https://docs.databricks.com/aws/en/structured-streaming/foreach)
- [Upsert into a Delta Lake table using merge](https://docs.databricks.com/aws/en/delta/merge)
