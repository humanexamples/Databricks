# `DataFrame.dropna()`

Gibt einen neuen DataFrame zurück, der Zeilen mit NULL- oder NaN-Werten auslässt. `DataFrame.dropna` und `DataFrameNaFunctions.drop` sind Aliase voneinander.

## Signatur

```python
dropna(how: str = "any", thresh: Optional[int] = None, subset: Optional[Union[str, Tuple[str, ...], List[str]]] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `how` | `str`, optional, Standard `'any'` | `'any'` oder `'all'`. Bei `'any'` wird eine Zeile entfernt, wenn sie irgendeinen NULL-Wert enthält. Bei `'all'` nur, wenn alle ihre Werte NULL sind. |
| `thresh` | `int`, optional, Standard `None` | Falls angegeben, werden Zeilen entfernt, die weniger als `thresh` Nicht-NULL-Werte haben. Überschreibt den Parameter `how`. |
| `subset` | `str`, `tuple` oder `list`, optional | Optionale Liste der zu berücksichtigenden Spaltennamen. |

## Rückgabewert

`DataFrame`: DataFrame ohne die betroffenen Zeilen.

## Beispiel

```python
from pyspark.sql import Row
df = spark.createDataFrame([
    Row(age=10, height=80.0, name="Alice"),
    Row(age=5, height=float("nan"), name="Bob"),
    Row(age=None, height=None, name="Tom"),
    Row(age=None, height=float("nan"), name=None),
])

df.na.drop().show()
# +---+------+-----+
# |age|height| name|
# +---+------+-----+
# | 10|  80.0|Alice|
# +---+------+-----+

df.na.drop(how='all').show()
# +----+------+-----+
# | age|height| name|
# +----+------+-----+
# |  10|  80.0|Alice|
# |   5|   NaN|  Bob|
# |NULL|  NULL|  Tom|
# +----+------+-----+

df.na.drop(thresh=2).show()
# +---+------+-----+
# |age|height| name|
# +---+------+-----+
# | 10|  80.0|Alice|
# |  5|   NaN|  Bob|
# +---+------+-----+
```

Siehe auch [`fillna`](03%20fillna.md), [`na`](01%20na.md).

## Quellen

- DataFrame.dropna: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/dropna

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
