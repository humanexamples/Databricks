# `DataFrame.sort()`

Gibt einen neuen DataFrame zurück, der nach der bzw. den angegebenen Spalte(n) sortiert ist.

## Signatur

```python
sort(*cols: Union[int, str, Column, List[Union[int, str, Column]]], **kwargs: Any)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `cols` | `int`, `str`, `list` oder `Column`, optional | Liste von `Column`s, Spaltennamen oder Spaltenordinalzahlen, nach denen sortiert wird. |
| `ascending` | `bool` oder `list`, optional, Standard `True` | Boolean oder Liste von Booleans: aufsteigend vs. absteigend. Für mehrere Sortierreihenfolgen eine Liste angeben; deren Länge muss der Länge von `cols` entsprechen. |

## Rückgabewert

`DataFrame`: Sortierter DataFrame.

## Hinweise

Spaltenordinalzahlen beginnen bei 1 – anders als das 0-basierte `__getitem__`. Eine negative Ordinalzahl bedeutet absteigende Sortierung.

## Beispiel

```python
from pyspark.sql import functions as sf
df = spark.createDataFrame([
    (2, "Alice"), (5, "Bob")], schema=["age", "name"])

df.sort(sf.asc("age")).show()
# +---+-----+
# |age| name|
# +---+-----+
# |  2|Alice|
# |  5|  Bob|
# +---+-----+

df.sort(df.age.desc()).show()
# +---+-----+
# |age| name|
# +---+-----+
# |  5|  Bob|
# |  2|Alice|
# +---+-----+

df.sort("age", ascending=False).show()
# +---+-----+
# |age| name|
# +---+-----+
# |  5|  Bob|
# |  2|Alice|
# +---+-----+

df = spark.createDataFrame([
    (2, "Alice"), (2, "Bob"), (5, "Bob")], schema=["age", "name"])
df.orderBy(sf.desc("age"), "name").show()
# +---+-----+
# |age| name|
# +---+-----+
# |  5|  Bob|
# |  2|Alice|
# |  2|  Bob|
# +---+-----+
```

Siehe auch [`orderBy`](04%20orderBy.md) (Alias), [`sortWithinPartitions`](05%20sortWithinPartitions.md).

## Quellen

- DataFrame.sort: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/sort

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
