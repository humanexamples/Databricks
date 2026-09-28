# `DataFrame.unpivot()`

Wandelt einen DataFrame vom Wide- ins Long-Format um (Unpivot), wobei optional Identifier-Spalten erhalten bleiben. Das ist die Umkehrung von `groupBy(...).pivot(...).agg(...)` – mit Ausnahme der Aggregation, die sich nicht umkehren lässt.

*Hinzugefügt in Databricks Runtime 11.1*

## Signatur

```python
unpivot(ids: Union["ColumnOrName", List["ColumnOrName"], Tuple["ColumnOrName", ...]], values: Optional[Union["ColumnOrName", List["ColumnOrName"], Tuple["ColumnOrName", ...]]], variableColumnName: str, valueColumnName: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `ids` | `str`, `Column`, `tuple`, `list` | Spalte(n), die als Identifier verwendet werden. Eine einzelne Spalte bzw. ein Spaltenname oder eine Liste/ein Tupel für mehrere Spalten. |
| `values` | `str`, `Column`, `tuple`, `list`, optional | Spalte(n), die „entpivotiert“ werden. Eine einzelne Spalte bzw. ein Spaltenname oder eine Liste/ein Tupel für mehrere Spalten. Falls angegeben, darf die Angabe nicht leer sein. Ohne Angabe werden alle Spalten verwendet, die nicht in `ids` stehen. |
| `variableColumnName` | `str` | Name der Variablenspalte. |
| `valueColumnName` | `str` | Name der Wertespalte. |

## Rückgabewert

`DataFrame`: Entpivotierter DataFrame.

## Hinweise

Unterstützt Spark Connect.

## Beispiel

```python
df = spark.createDataFrame(
    [(1, 11, 1.1), (2, 12, 1.2)],
    ["id", "int", "double"],
)
df.show()
# +---+---+------+
# | id|int|double|
# +---+---+------+
# |  1| 11|   1.1|
# |  2| 12|   1.2|
# +---+---+------+

from pyspark.sql import functions as sf
df.unpivot(
    "id", ["int", "double"], "var", "val"
).sort("id", sf.desc("var")).show()
# +---+------+----+
# | id|   var| val|
# +---+------+----+
# |  1|   int|11.0|
# |  1|double| 1.1|
# |  2|   int|12.0|
# |  2|double| 1.2|
# +---+------+----+
```

Siehe auch [`melt`](02%20melt.md) (Alias), [`transpose`](03%20transpose.md).

## Quellen

- DataFrame.unpivot: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/unpivot

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
