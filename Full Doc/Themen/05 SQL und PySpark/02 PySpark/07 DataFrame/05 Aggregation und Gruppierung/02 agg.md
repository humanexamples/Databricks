# `DataFrame.agg()`

Aggregiert über den gesamten DataFrame ohne Gruppierung (Kurzform für `df.groupBy().agg()`).

## Signatur

```python
agg(*exprs: Union[Column, Dict[str, str]])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `exprs` | `Column` oder `dict` aus Schlüssel-/Wert-Strings | Spalten oder Ausdrücke, nach denen der DataFrame aggregiert wird. |

## Rückgabewert

`DataFrame`: Aggregierter DataFrame.

## Beispiel

```python
from pyspark.sql import functions as sf
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.agg({"age": "max"}).show()
# +--------+
# |max(age)|
# +--------+
# |       5|
# +--------+
df.agg(sf.min(df.age)).show()
# +--------+
# |min(age)|
# +--------+
# |       2|
# +--------+
```

Siehe auch [`groupBy`](01%20groupBy.md).

## Quellen

- DataFrame.agg: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/agg

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
