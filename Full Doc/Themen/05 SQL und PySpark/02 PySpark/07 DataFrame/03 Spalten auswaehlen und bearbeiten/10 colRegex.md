# `DataFrame.colRegex()`

Wählt Spalten anhand eines als regulärer Ausdruck angegebenen Spaltennamens aus und gibt sie als `Column` zurück.

## Signatur

```python
colRegex(colName: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `colName` | `str` | Spaltenname als regulärer Ausdruck. |

## Rückgabewert

`Column`

## Beispiel

```python
df = spark.createDataFrame([("a", 1), ("b", 2), ("c",  3)], ["Col1", "Col2"])
df.select(df.colRegex("`(Col1)?+.+`")).show()
# +----+
# |Col2|
# +----+
# |   1|
# |   2|
# |   3|
# +----+
```

## Quellen

- DataFrame.colRegex: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/colRegex

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
