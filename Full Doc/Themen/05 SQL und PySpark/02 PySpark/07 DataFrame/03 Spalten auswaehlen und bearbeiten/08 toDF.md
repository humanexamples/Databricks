# `DataFrame.toDF()`

Gibt einen neuen DataFrame mit den angegebenen neuen Spaltennamen zurück.

## Signatur

```python
toDF(*cols: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `*cols` | `tuple` | Tupel von Strings mit den neuen Spaltennamen. Die Anzahl muss der Spaltenanzahl des ursprünglichen DataFrames entsprechen. |

## Rückgabewert

`DataFrame`: DataFrame mit neuen Spaltennamen.

## Beispiel

```python
df = spark.createDataFrame([(14, "Tom"), (23, "Alice"),
    (16, "Bob")], ["age", "name"])
df.toDF('f1', 'f2').show()
# +---+-----+
# | f1|   f2|
# +---+-----+
# | 14|  Tom|
# | 23|Alice|
# | 16|  Bob|
# +---+-----+
```

Siehe auch [`withColumnsRenamed`](07%20withColumnsRenamed.md).

## Quellen

- DataFrame.toDF: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/toDF

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
