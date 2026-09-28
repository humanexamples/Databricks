# DataFrameReader options — Text

Bereich: **DataFrameReader options › Text** (Batch-Lesen von Textdateien, festes Schema `value STRING`).

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `encoding` | `UTF-8` | Charset-Name | „The name of the encoding of the TEXT file line separator." |
| `lineSep` | None | String | „A string between two consecutive TEXT records." |
| `wholeText` | `false` | boolean | „Whether to read a file as a single record." |

## Beispiel

```python
df = spark.read.format("text").option("wholeText", "true").load("/Volumes/analytics/bronze/logs")
```

```sql
SELECT * FROM text.`/Volumes/analytics/bronze/logs`;
```

## Siehe auch

- [`../04 Dateitypen/03 Ingesting Text.md`](../04%20Dateitypen/03%20Ingesting%20Text.md)
