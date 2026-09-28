# foreachBatch in Structured Streaming

Mit `foreachBatch` lassen sich die Ergebnisse einer Streaming-Query in Senken schreiben, die keine native Streaming-Unterstützung bieten. Das Muster `streamingDF.writeStream.foreachBatch(...)` wendet eine Batch-Funktion auf die Ausgabedaten jedes Micro-Batches an.

## Funktionsweise

Die übergebene Funktion erhält zwei Parameter: einen DataFrame mit den Daten des Micro-Batches und eine eindeutige Batch-ID.

**Garantien und Einschränkungen:**

- `foreachBatch` bietet **At-least-once**-Schreibgarantien; Exactly-once-Semantik lässt sich mit der `batchId` zur Deduplizierung erreichen.
- Nicht kompatibel mit Continuous-Processing-Modus – dort `foreach()` verwenden.
- Bei zustandsbehafteten Operatoren muss jeder Batch vollständig konsumiert werden.

**Leere DataFrames:** Der Code muss den Fall leerer Micro-Batches explizit behandeln, sonst kann die Query fehlschlagen (z. B. durch Delta-Lake-`OPTIMIZE`-Vorgänge, die leere Micro-Batches erzeugen).

## Einfaches Python-Beispiel

```python
def process_batch(output_df, batch_id):
    if not output_df.isEmpty():
        # Geschäftslogik
        pass
streamingDF.writeStream.foreachBatch(process_batch).start()
```

## Wichtige Anwendungsfälle

- **Delta-Lake-Merge-Operationen:** `foreachBatch` wird für MERGE-Operationen in Structured Streaming benötigt.
- **Schreiben in mehrere Ziele:** Das Schreiben in mehrere Senken über `foreachBatch` serialisiert die Ausführung der Streaming-Writes, was die Latenz pro Micro-Batch erhöhen kann.

## Fehlerbehandlung

Databricks empfiehlt, die Streaming-Query bei Fehlern schnell fehlschlagen zu lassen (Fail Fast) und die Retry-Logik der Orchestrierungsschicht zu überlassen, z. B. Lakeflow Jobs oder Apache Airflow. Für Delta-Lake-Ziele sorgen die Schreiboptionen `txnAppId` und `txnVersion` in Kombination mit der `batchId` für Idempotenz.

## Beispiel: Dead-Letter-Queue

```python
from pyspark.sql.functions import current_timestamp, lit

main_table = "catalog.schema.orders"
dlq_table = "catalog.schema.orders_dlq"
app_id = "orders-streaming-job"

def process_orders(batch_df, batch_id):
    if batch_df.isEmpty():
        return
    valid_condition = "order_amount > 0 AND customer_id IS NOT NULL"

    batch_df.filter(valid_condition).write \
        .format("delta") \
        .mode("append") \
        .option("txnVersion", batch_id) \
        .option("txnAppId", app_id) \
        .saveAsTable(main_table)

    invalid_df = batch_df.filter(f"NOT ({valid_condition})")
    if not invalid_df.isEmpty():
        invalid_df \
            .withColumn("dlq_batch_id", lit(batch_id)) \
            .withColumn("dlq_ingest_time", current_timestamp()) \
            .write \
            .format("delta") \
            .mode("append") \
            .option("txnVersion", batch_id) \
            .option("txnAppId", app_id) \
            .saveAsTable(dlq_table)
```

## Teilweisen Batch-Konsum ermöglichen

Bei zustandsbehafteten Operatoren muss der gesamte Batch konsumiert werden. Nicht benötigte Zeilen können dazu „still“ durchlaufen werden:

```python
def do_nothing(row):
    pass

def partial_func(batch_df, batch_id):
    batch_df.show(2)
    batch_df.foreach(do_nothing)  # Rest still konsumieren
```

## Hinweise ab Databricks Runtime 14.0

Im Standard-Access-Modus gelten innerhalb der `foreachBatch`-Funktion folgende Einschränkungen:

- `print()` schreibt nur in die Treiber-Logs.
- Auf `dbutils.widgets` kann innerhalb der Funktion nicht zugegriffen werden.
- Alle referenzierten Objekte müssen serialisierbar sein.

---
**Quelle:** https://docs.databricks.com/aws/en/structured-streaming/foreach  
**Stand:** 2026-08-07
