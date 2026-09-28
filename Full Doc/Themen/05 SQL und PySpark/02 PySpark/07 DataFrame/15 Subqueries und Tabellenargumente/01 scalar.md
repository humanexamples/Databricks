# `DataFrame.scalar()`

Gibt ein `Column`-Objekt für eine SCALAR-Subquery zurück, die genau eine Zeile und eine Spalte enthält.

## Signatur

```python
scalar()
```

## Rückgabewert

`Column`: Ein `Column`-Objekt, das eine SCALAR-Subquery repräsentiert.

## Hinweise

`scalar()` ist nützlich, um aus einem DataFrame ein `Column`-Objekt zu gewinnen, das einen skalaren Wert repräsentiert – insbesondere, wenn der DataFrame aus einer Aggregation oder Einzelwertberechnung stammt. Die zurückgegebene `Column` kann direkt in `select`-Klauseln oder als Prädikat in Filtern des äußeren DataFrames verwendet werden und ermöglicht so dynamisches Filtern und Berechnungen auf Basis skalarer Werte.

## Beispiel

```python
data = [
    (1, "Alice", 45000, 101), (2, "Bob", 54000, 101), (3, "Charlie", 29000, 102),
    (4, "David", 61000, 102), (5, "Eve", 48000, 101),
]
employees = spark.createDataFrame(data, ["id", "name", "salary", "department_id"])

from pyspark.sql import functions as sf
employees.where(
    sf.col("salary") > employees.select(sf.avg("salary")).scalar()
).select("name", "salary", "department_id").orderBy("name").show()
# +-----+------+-------------+
# | name|salary|department_id|
# +-----+------+-------------+
# |  Bob| 54000|          101|
# |David| 61000|          102|
# |  Eve| 48000|          101|
# +-----+------+-------------+

employees.alias("e1").where(
    sf.col("salary")
    > employees.alias("e2").where(
        sf.col("e2.department_id") == sf.col("e1.department_id").outer()
    ).select(sf.avg("salary")).scalar()
).select("name", "salary", "department_id").orderBy("name").show()
# +-----+------+-------------+
# | name|salary|department_id|
# +-----+------+-------------+
# |  Bob| 54000|          101|
# |David| 61000|          102|
# +-----+------+-------------+
```

Siehe auch [`exists`](02%20exists.md).

## Quellen

- DataFrame.scalar: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/scalar

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
