# `DataFrame.toJSON()`

Konvertiert einen DataFrame in ein RDD von Strings bzw. einen DataFrame (jede Zeile als JSON-String).

## Signatur

```python
toJSON(use_unicode: bool = True)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `use_unicode` | `bool`, optional, Standard `True` | Ob nach Unicode konvertiert werden soll. Im Spark-Connect-Modus ist dieses Argument nicht erlaubt. |

## Rückgabewert

`RDD` (im Classic-Modus) oder `DataFrame` (im Connect-Modus)

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.toJSON().first()
# '{"age":2,"name":"Alice"}'
```

## Quellen

- DataFrame.toJSON: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/toJSON

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
