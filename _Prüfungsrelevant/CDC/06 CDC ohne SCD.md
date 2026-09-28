[← Übersicht](00%20Uebersicht.md)

# CDC ohne SCD

**Kombination:** Change Data Feed · Append-Flow · Sinks (Kafka) · Streaming-Aggregation mit Watermark

CDC wird oft mit SCD 1 oder 2 kombiniert, aber nicht immer. Sobald die Change-Events **nicht** auf eine Tabelle mit dem aktuellen Stand einer Dimension angewendet werden, spricht man nicht von SCD. Die folgenden Muster nutzen CDC-Events direkt.

| Muster | Was mit den Events passiert |
|---|---|
| A – Change-Log / Audit | unverändert anhängen |
| B – Event-Weitergabe | an ein externes System senden |
| C – Inkrementelle Aggregation | zu Kennzahlen verdichten |
| D – Löschungen propagieren | siehe [04, Abschnitt C](04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md) |

---

## A – Change-Log / Audit-Tabelle (append-only)

Jede Änderung an `silver_customers` wird dauerhaft als eigene Zeile festgehalten: wer, was, wann. Das ist **keine** SCD-2-Tabelle: Es gibt keine Gültigkeitszeiträume, sondern nur eine Liste von Ereignissen, inklusive `update_preimage` für Vorher-Nachher-Vergleiche.

```python
from pyspark import pipelines as dp

@dp.table(comment="Vollständiges Änderungsprotokoll von silver_customers")
def audit_customers_changes():
    return (spark.readStream.option("readChangeFeed", "true")
            .table("catalog.schema.silver_customers")
            .selectExpr("customer_id", "name", "city",
                        "_change_type AS change_type",
                        "_commit_version AS version",
                        "_commit_timestamp AS changed_at"))
```

```sql
-- Wie sah Kunde 42 vor und nach jedem Update aus?
SELECT version, change_type, city, changed_at
FROM audit_customers_changes
WHERE customer_id = 42
ORDER BY version, change_type;
```

**Unterschied zu CDF und Time Travel:** Der CDF und alte Versionen verschwinden mit `VACUUM`. Die Audit-Tabelle bleibt, solange man sie behält.

---

## B – Event-Weitergabe an Kafka (Sink)

Andere Systeme (Microservices, Suchindex, Cache) sollen auf Kundenänderungen reagieren. Die Pipeline liest den CDF und schreibt jedes Event in ein Kafka-Topic. Ziel ist also keine Tabelle.

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, to_json, struct

dp.create_sink(
    "customer_events_sink",
    "kafka",
    {
        "kafka.bootstrap.servers": "broker1:9092",
        "topic": "lakehouse.customers.changes",
    })

@dp.append_flow(name="publish_customer_changes", target="customer_events_sink")
def publish_customer_changes():
    return (spark.readStream.option("readChangeFeed", "true")
            .table("catalog.schema.silver_customers")
            .filter("_change_type != 'update_preimage'")
            .select(col("customer_id").cast("string").alias("key"),
                    to_json(struct("customer_id", "name", "city",
                                   "_change_type", "_commit_timestamp")).alias("value")))
```

Kafka erwartet die Spalten `key` und `value`. Der Key sorgt dafür, dass alle Events eines Kunden in derselben Partition landen und damit in der richtigen Reihenfolge ankommen.

---

## C – Inkrementelle Aggregation mit Watermark

Kennzahl: Wie viele Inserts, Updates und Deletes kommen pro Stunde aus dem ERP? Die Events werden direkt aus Bronze gezählt, ohne sie vorher in eine SCD-Tabelle zu mergen.

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import window, expr

@dp.table(comment="Änderungsvolumen je Stunde und Operation")
def gold_cdc_volume_per_hour():
    return (spark.readStream.table("bronze_customers_cdc")          # aus 01
            .withColumn("change_ts", expr("timestamp_millis(ts_ms)"))
            .withWatermark("change_ts", "2 hours")                   # verspätete Events bis 2 h
            .groupBy(window("change_ts", "1 hour"), "op")
            .count())
```

Die **Watermark** legt fest, wie lange auf verspätete Events gewartet wird. Danach gilt ein Stundenfenster als abgeschlossen, wird einmal geschrieben, und der Zustand wird freigegeben. Ohne Watermark würde der Zustand unbegrenzt wachsen.

Nützlich z. B. als Monitoring: Ein plötzlicher Anstieg von `op = 'd'` deutet auf eine Massenlöschung in der Quelle hin, und ein SQL-Alert kann darauf reagieren.

---

## Zusammenfassung

| | mit SCD | ohne SCD |
|---|---|---|
| Ziel | Dimensionstabelle mit aktuellem Stand (1) oder Versionen (2) | Log, externes System, Kennzahl |
| Frage, die beantwortet wird | „Wie ist / war der Zustand?“ | „Was ist passiert?“ / „Wer muss reagieren?“ |
| Typische Technik | AUTO CDC, `MERGE` | Append-Flow, Sink, Streaming-Aggregation |

---
[← Vorherige Datei](05%20Timestamp-basiertes%20CDC%20mit%20Lakeflow%20Jobs.md) · [Übersicht](00%20Uebersicht.md) · [Weiter zu SCD →](../SCD/00%20Uebersicht.md)

## Quellen

- [Use Delta Lake change data feed on Databricks](https://docs.databricks.com/aws/en/delta/delta-change-data-feed)
- [Stream processing with Apache Kafka and Databricks](https://docs.databricks.com/aws/en/connect/streaming/kafka)
