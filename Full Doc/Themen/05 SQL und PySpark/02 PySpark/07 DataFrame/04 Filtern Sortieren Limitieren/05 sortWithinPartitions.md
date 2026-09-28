# `DataFrame.sortWithinPartitions()`

Gibt einen neuen DataFrame zurück, in dem jede Partition nach der bzw. den angegebenen Spalte(n) sortiert ist (keine globale Sortierung, kein Shuffle).

## Signatur

```python
sortWithinPartitions(*cols: Union[int, str, Column, List[Union[int, str, Column]]], **kwargs: Any)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `cols` | `int`, `str`, `list` oder `Column`, optional | Liste von `Column`s, Spaltennamen oder Spaltenordinalzahlen, nach denen sortiert wird. |
| `ascending` | `bool` oder `list`, optional, Standard `True` | Boolean oder Liste von Booleans: aufsteigend vs. absteigend. Für mehrere Sortierreihenfolgen eine Liste angeben; deren Länge muss der Länge von `cols` entsprechen. |

## Rückgabewert

`DataFrame`: Innerhalb der Partitionen sortierter DataFrame.

## Hinweise

Spaltenordinalzahlen beginnen bei 1 – anders als das 0-basierte `__getitem__`. Eine negative Ordinalzahl bedeutet absteigende Sortierung.

## Beispiel

Das folgende Beispiel kombiniert `sortWithinPartitions` mit [`coalesce`](../11%20Partitionierung%20und%20Query-Plan/04%20coalesce.md), um die Zeilen innerhalb einer Partition zu sortieren.

```python
from pyspark.sql import functions as sf
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df.sortWithinPartitions("age", ascending=False)
# DataFrame[age: bigint, name: string]

df.coalesce(1).sortWithinPartitions(1).show()
# +---+-----+
# |age| name|
# +---+-----+
# |  2|Alice|
# |  5|  Bob|
# +---+-----+

df.coalesce(1).sortWithinPartitions(-1).show()
# +---+-----+
# |age| name|
# +---+-----+
# |  5|  Bob|
# |  2|Alice|
# +---+-----+
```

Siehe auch [`sort`](03%20sort.md).

## Quellen

- DataFrame.sortWithinPartitions: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/sortWithinPartitions

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
