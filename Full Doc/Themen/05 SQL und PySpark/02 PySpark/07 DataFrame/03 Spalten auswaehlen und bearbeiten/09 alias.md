# `DataFrame.alias()`

Gibt einen neuen DataFrame mit gesetztem Alias zurück. Nützlich z. B. bei Self-Joins, um Spalten beider Seiten eindeutig ansprechen zu können.

## Signatur

```python
alias(alias: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `alias` | `str` | Aliasname, der für den DataFrame gesetzt wird. |

## Rückgabewert

`DataFrame`: DataFrame mit Alias.

## Beispiel

```python
from pyspark.sql import functions as sf
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df_as1 = df.alias("df_as1")
df_as2 = df.alias("df_as2")
joined_df = df_as1.join(df_as2,
    sf.col("df_as1.name") == sf.col("df_as2.name"), 'inner')
joined_df.select(
    "df_as1.name", "df_as2.name", "df_as2.age"
).sort(sf.desc("df_as1.name")).show()
# +-----+-----+---+
# | name| name|age|
# +-----+-----+---+
# |  Tom|  Tom| 14|
# |  Bob|  Bob| 16|
# |Alice|Alice| 23|
# +-----+-----+---+
```

## Quellen

- DataFrame.alias: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/alias

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
