# `DataFrame.join()`

Joint mit einem anderen DataFrame über den angegebenen Join-Ausdruck.

## Signatur

```python
join(other: "DataFrame", on: Optional[Union[str, List[str], Column, List[Column]]] = None, how: Optional[str] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `other` | `DataFrame` | Rechte Seite des Joins. |
| `on` | `str`, `list` oder `Column`, optional | Ein String mit dem Namen der Join-Spalte, eine Liste von Spaltennamen, ein Join-Ausdruck (`Column`) oder eine Liste von `Column`s. Ist `on` ein String oder eine Liste von Strings (Name der Join-Spalte(n)), müssen die Spalte(n) auf beiden Seiten existieren; es wird ein Equi-Join ausgeführt. |
| `how` | `str`, optional | Standard `inner`. Muss einer der folgenden Werte sein: `inner`, `cross`, `outer`, `full`, `fullouter`, `full_outer`, `left`, `leftouter`, `left_outer`, `right`, `rightouter`, `right_outer`, `semi`, `leftsemi`, `left_semi`, `anti`, `leftanti` und `left_anti`. |

## Rückgabewert

`DataFrame`: Gejointer DataFrame.

## Beispiel

```python
import pyspark.sql.functions as sf
from pyspark.sql import Row
df = spark.createDataFrame([Row(name="Alice", age=2), Row(name="Bob", age=5)])
df2 = spark.createDataFrame([Row(name="Tom", height=80), Row(name="Bob", height=85)])

df.join(df2, "name").show()
# +----+---+------+
# |name|age|height|
# +----+---+------+
# | Bob|  5|    85|
# +----+---+------+

joined = df.join(df2, df.name == df2.name, "outer").sort(sf.desc(df.name))
joined.show()
# +-----+----+----+------+
# | name| age|name|height|
# +-----+----+----+------+
# |  Bob|   5| Bob|    85|
# |Alice|   2|NULL|  NULL|
# | NULL|NULL| Tom|    80|
# +-----+----+----+------+

df.alias("a").join(
    df.alias("b"), sf.col("a.name") == sf.col("b.name"), "outer"
).sort(sf.desc("a.name")).select("a.name", "b.age").show()
# +-----+---+
# | name|age|
# +-----+---+
# |  Bob|  5|
# |Alice|  2|
# +-----+---+
```

Siehe auch [`crossJoin`](02%20crossJoin.md), [`lateralJoin`](03%20lateralJoin.md), [`alias`](../03%20Spalten%20auswaehlen%20und%20bearbeiten/09%20alias.md), [`hint`](../11%20Partitionierung%20und%20Query-Plan/05%20hint.md).

## Quellen

- DataFrame.join: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/join

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
