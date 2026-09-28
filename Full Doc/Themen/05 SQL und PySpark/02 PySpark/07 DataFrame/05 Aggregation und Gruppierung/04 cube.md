# `DataFrame.cube()`

Erstellt einen mehrdimensionalen Cube für den aktuellen DataFrame über die angegebenen Spalten, auf dem Aggregationen ausgeführt werden können (Aggregate für alle Kombinationen der Spalten inkl. Gesamtsumme).

## Signatur

```python
cube(*cols: "ColumnOrName")
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `cols` | `list`, `str`, `int` oder `Column` | Die Spalten für den Cube. Jedes Element ist ein Spaltenname (String), ein Ausdruck (`Column`), eine Spaltenordinalzahl (`int`, 1-basiert) oder eine Liste davon. |

## Rückgabewert

`GroupedData`: Cube der Daten auf Basis der angegebenen Spalten.

## Hinweise

Spaltenordinalzahlen beginnen bei 1 – anders als das 0-basierte `__getitem__`.

## Beispiel

```python
df = spark.createDataFrame([("Alice", 2), ("Bob", 5)], schema=["name", "age"])

df.cube("name").count().orderBy("name").show()
# +-----+-----+
# | name|count|
# +-----+-----+
# | NULL|    2|
# |Alice|    1|
# |  Bob|    1|
# +-----+-----+

df.cube("name", df.age).count().orderBy("name", "age").show()
# +-----+----+-----+
# | name| age|count|
# +-----+----+-----+
# | NULL|NULL|    2|
# | NULL|   2|    1|
# | NULL|   5|    1|
# |Alice|NULL|    1|
# |Alice|   2|    1|
# |  Bob|NULL|    1|
# |  Bob|   5|    1|
# +-----+----+-----+
```

Siehe auch [`rollup`](03%20rollup.md), [`groupingSets`](05%20groupingSets.md), [`groupBy`](01%20groupBy.md).

## Quellen

- DataFrame.cube: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/cube

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
