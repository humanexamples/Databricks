# `DataFrame.unpersist()`

Markiert den DataFrame als nicht persistent und entfernt alle zugehörigen Blöcke aus Speicher und Festplatte.

## Signatur

```python
unpersist(blocking: bool = False)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `blocking` | `bool` | Ob blockiert werden soll, bis alle Blöcke gelöscht sind. |

## Rückgabewert

`DataFrame`: Nicht mehr persistierter DataFrame.

## Hinweise

- Der Standardwert von `blocking` wurde in Spark 2.0 auf `False` geändert, um mit Scala übereinzustimmen.
- Gecachte Daten werden von allen Spark-Sessions auf dem Cluster gemeinsam genutzt; `unpersist` wirkt sich daher auf alle Sessions aus.

## Beispiel

```python
df = spark.range(1)
df.persist()
# DataFrame[id: bigint]
df.unpersist()
# DataFrame[id: bigint]
df = spark.range(1)
df.unpersist(True)
# DataFrame[id: bigint]
```

Siehe auch [`cache`](01%20cache.md), [`persist`](02%20persist.md).

## Quellen

- DataFrame.unpersist: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/unpersist

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
