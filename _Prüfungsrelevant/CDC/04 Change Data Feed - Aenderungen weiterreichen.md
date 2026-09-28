[← Übersicht](00%20Uebersicht.md)

# Change Data Feed (CDF) – Änderungen weiterreichen

**Kombination:** Delta Change Data Feed · Structured Streaming · `foreachBatch` + `MERGE` · AUTO CDC · DSGVO-Löschungen · Medallion

CDF ist CDC **für Delta-Tabellen selbst**: Die Tabelle protokolliert jede Zeilenänderung, und nachgelagerte Schritte lesen nur diese Änderungen statt der ganzen Tabelle.

> Vollständige CDF-Dokumentation (Automatic vs. Legacy CDF, alle Lese-Optionen, Delta Sharing, Lakebase CDF, Fehlermeldungen): [../CDF/00 Uebersicht.md](../CDF/00%20Uebersicht.md)

---

## CDF aktivieren und lesen

```sql
-- Für eine bestehende Tabelle
ALTER TABLE catalog.schema.silver_customers
SET TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- Direkt beim Anlegen
CREATE TABLE catalog.schema.silver_orders (order_id BIGINT, status STRING)
TBLPROPERTIES (delta.enableChangeDataFeed = true);

-- Änderungen ab Version 5 (Batch)
SELECT * FROM table_changes('catalog.schema.silver_customers', 5);

-- Änderungen in einem Zeitraum
SELECT * FROM table_changes('catalog.schema.silver_customers',
                            '2026-09-01 00:00:00', '2026-09-02 00:00:00');
```

```python
# Batch
spark.read.option("readChangeFeed", "true") \
          .option("startingVersion", 5) \
          .table("catalog.schema.silver_customers")

# Streaming (merkt sich die Position im Checkpoint)
spark.readStream.option("readChangeFeed", "true") \
                .table("catalog.schema.silver_customers")
```

**Zusätzliche Spalten im Ergebnis:**

| Spalte | Werte |
|---|---|
| `_change_type` | `insert`, `update_preimage` (alter Wert), `update_postimage` (neuer Wert), `delete` |
| `_commit_version` | Delta-Version der Änderung |
| `_commit_timestamp` | Zeitpunkt des Commits |

> CDF erfasst nur Änderungen **ab der Aktivierung**. Ältere Versionen haben keinen Feed.

---

## A – Silver → Gold per CDF und `MERGE` (inkl. Deletes)

Gold enthält eine Kopie der Kunden mit denselben Spalten wie Silver. Statt Silver jedes Mal komplett zu lesen, werden nur Änderungen übernommen, **auch Löschungen**.

```python
from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql.window import Window

TARGET = "catalog.schema.gold_customers"

def propagate_changes(batch_df, batch_id):
    # update_preimage (alter Wert) wird nicht gebraucht
    changes = batch_df.filter("_change_type != 'update_preimage'")

    # pro Key nur die jüngste Änderung dieses Batches
    w = Window.partitionBy("customer_id").orderBy(F.col("_commit_version").desc())
    latest = (changes.withColumn("_rn", F.row_number().over(w))
                     .filter("_rn = 1").drop("_rn"))

    data_cols = [c for c in latest.columns if not c.startswith("_")]

    (DeltaTable.forName(batch_df.sparkSession, TARGET).alias("t")
        .merge(latest.alias("s"), "t.customer_id = s.customer_id")
        .whenMatchedDelete(condition="s._change_type = 'delete'")
        .whenMatchedUpdate(condition="s._change_type != 'delete'",
                           set={c: f"s.{c}" for c in data_cols})
        .whenNotMatchedInsert(condition="s._change_type != 'delete'",
                              values={c: f"s.{c}" for c in data_cols})
        .execute())

(spark.readStream.option("readChangeFeed", "true")
      .table("catalog.schema.silver_customers")
      .writeStream
      .foreachBatch(propagate_changes)
      .option("checkpointLocation", "/Volumes/catalog/schema/_checkpoints/gold_customers")
      .trigger(availableNow=True)
      .start())
```

---

## B – CDF als Quelle für AUTO CDC (deklarativ)

Dieselbe Weitergabe ohne eigenen Merge-Code: Der CDF einer Delta-Tabelle **ist** bereits ein Change-Event-Strom, den AUTO CDC direkt verarbeiten kann. Das Ziel kann dabei eine andere SCD-Form haben als die Quelle, z. B. **Quelle SCD 1 → Ziel SCD 2**.

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, expr

@dp.temporary_view
def customers_changes():
    return (spark.readStream.option("readChangeFeed", "true")
            .table("catalog.schema.silver_customers")
            .filter("_change_type != 'update_preimage'"))

dp.create_streaming_table("gold_customers_history")

dp.create_auto_cdc_flow(
    target             = "gold_customers_history",
    source             = "customers_changes",
    keys               = ["customer_id"],
    sequence_by        = col("_commit_version"),
    apply_as_deletes   = expr("_change_type = 'delete'"),
    except_column_list = ["_change_type", "_commit_version", "_commit_timestamp"],
    stored_as_scd_type = 2)
```

**Hinweis zu AUTO-CDC-Zielen als Quelle:** Ab DBR 15.2 lässt sich der CDF einer Streaming Table lesen, die selbst Ziel eines AUTO-CDC-Flows ist. Bei SCD-2-Zielen ist der Primärschlüssel dort `keys` **plus** `coalesce(__START_AT, __END_AT)`.

---

## C – DSGVO: Löschung durch alle Schichten propagieren

Eine Kundin verlangt die Löschung ihrer Daten. Gelöscht wird **einmal** in Silver. CDF trägt das `delete`-Event automatisch weiter, und Muster A oder B löscht die Zeile in Gold.

```sql
-- 1. Löschung an der Quelle der Propagation
DELETE FROM catalog.schema.silver_customers WHERE customer_id = 42;

-- 2. Kontrolle: Das Delete-Event steht im Feed
SELECT customer_id, _change_type, _commit_version
FROM table_changes('catalog.schema.silver_customers', 0)
WHERE customer_id = 42;

-- 3. Nach dem nächsten Lauf von Muster A ist die Zeile in Gold weg.
--    Physisch verschwinden die alten Datendateien erst nach VACUUM:
VACUUM catalog.schema.gold_customers;
```

> **Wichtig für DSGVO:** Nach `DELETE` stehen die Daten über Time Travel noch in alten Versionen. Erst `VACUUM` (nach Ablauf der Retention, Default 7 Tage) entfernt die Dateien endgültig. Auch der CDF selbst enthält die gelöschten Werte, bis `VACUUM` gelaufen ist.

---

## CDF vs. AUTO CDC — Rollen im Lakehouse

```
Quelle ──AUTO CDC──► Bronze/Silver ──CDF──► Silver ──CDF──► Gold
        (herein)                   (weiter)        (weiter)
```

| | AUTO CDC | CDF |
|---|---|---|
| Richtung | von außen nach innen | innerhalb des Lakehouse |
| Liefert | wendet Events auf **eine** Zieltabelle an | stellt Änderungen **einer** Tabelle zum Lesen bereit |
| Ursache der Änderung | externe Change-Events | egal: `MERGE`, `DELETE`, `UPDATE`, AUTO-CDC-Flow |

---
[← Vorherige Datei](03%20CDC%20prozedural%20mit%20foreachBatch%20und%20MERGE.md) · [Übersicht](00%20Uebersicht.md) · [Nächste Datei →](05%20Timestamp-basiertes%20CDC%20mit%20Lakeflow%20Jobs.md)

## Quellen

- [Use Delta Lake change data feed on Databricks](https://docs.databricks.com/aws/en/delta/delta-change-data-feed)
- [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)
- [Remove unused data files with vacuum](https://docs.databricks.com/aws/en/delta/vacuum)
