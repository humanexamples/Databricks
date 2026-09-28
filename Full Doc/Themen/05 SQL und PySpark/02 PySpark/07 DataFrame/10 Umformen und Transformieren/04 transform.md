# `DataFrame.transform()`

Gibt einen neuen DataFrame zurück. Kompakte Syntax zum Verketten benutzerdefinierter Transformationen.

## Signatur

```python
transform(func: Callable[..., "DataFrame"], *args: Any, **kwargs: Any)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `func` | Funktion | Funktion, die einen DataFrame entgegennimmt und einen DataFrame zurückgibt. |
| `*args` | beliebig | Positionsargumente, die an `func` übergeben werden. |
| `**kwargs` | beliebig | Keyword-Argumente, die an `func` übergeben werden. |

## Rückgabewert

`DataFrame`: Transformierter DataFrame.

## Beispiel

```python
from pyspark.sql import functions as sf
df = spark.createDataFrame([(1, 1.0), (2, 2.0)], ["int", "float"])
def cast_all_to_int(input_df):
    return input_df.select([sf.col(c).cast("int") for c in input_df.columns])

def sort_columns_asc(input_df):
    return input_df.select(*sorted(input_df.columns))

df.transform(cast_all_to_int).transform(sort_columns_asc).show()
# +-----+---+
# |float|int|
# +-----+---+
# |    1|  1|
# |    2|  2|
# +-----+---+

def add_n(input_df, n):
    cols = [(sf.col(c) + n).alias(c) for c in input_df.columns]
    return input_df.select(cols)

df.transform(add_n, 1).transform(add_n, n=10).show()
# +---+-----+
# |int|float|
# +---+-----+
# | 12| 12.0|
# | 13| 13.0|
# +---+-----+
```

## Quellen

- DataFrame.transform: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/transform

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
