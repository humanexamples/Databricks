# DataFrameReader options — ORC

Bereich: **DataFrameReader options › ORC** (Batch-Lesen von ORC-Dateien).

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `mergeSchema` | `false` | boolean | „Whether to infer the schema across multiple files and to merge the schema of each file." |

> ORC unterstützt keine Schema-Inferenz/-Evolution über Auto Loader ([`../06 Auto Loader/01 Schema-Inferenz und -Evolution.md`](../06%20Auto%20Loader/01%20Schema-Inferenz%20und%20-Evolution.md)).

## Beispiel

```python
df = spark.read.format("orc").option("mergeSchema", "true").load("/Volumes/analytics/bronze/orc_data")
```

## Siehe auch

- [`../04 Dateitypen/08 Ingesting ORC.md`](../04%20Dateitypen/08%20Ingesting%20ORC.md)
