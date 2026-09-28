# Pandas UDFs

Referenz zu Pandas-UDFs (vektorisierte UDFs), die Apache Arrow für den Datentransfer und pandas für die Verarbeitung nutzen. Ergänzt die generelle [UDF-Performance-Hierarchie in Serialization.md](../../Performance%20Optimization/Code%20Optimization/Serialization.md).

## Abschnittsübersicht

1. [Series to Series UDF](#series-to-series)
2. [Iterator of Series to Iterator of Series UDF](#iterator-series)
3. [Iterator of multiple Series to Iterator of Series UDF](#iterator-multi-series)
4. [Series to scalar UDF](#series-to-scalar)
5. [Nutzung: Arrow-Batch-Größe konfigurieren](#arrow-batch-size)
6. [Nutzung: Timestamp-mit-Zeitzone-Semantik](#timestamp-semantics)
7. [Quellen](#quellen)

---

## <a id="series-to-series">1. Series to Series UDF</a>

```python
import pandas as pd
from pyspark.sql.functions import col, pandas_udf
from pyspark.sql.types import LongType

# Declare the function and create the UDF
def multiply_func(a: pd.Series, b: pd.Series) -> pd.Series:
    return a * b

multiply = pandas_udf(multiply_func, returnType=LongType())

# The function for a pandas_udf should be able to execute with local pandas data
x = pd.Series([1, 2, 3])
print(multiply_func(x, x))
# 0    1
# 1    4
# 2    9
# dtype: int64

# Create a Spark DataFrame, 'spark' is an existing SparkSession
df = spark.createDataFrame(pd.DataFrame(x, columns=["x"]))

# Execute function as a Spark vectorized UDF
df.select(multiply(col("x"), col("x"))).show()
# +-------------------+
# |multiply_func(x, x)|
# +-------------------+
# |                  1|
# |                  4|
# |                  9|
# +-------------------+
```

---

## <a id="iterator-series">2. Iterator of Series to Iterator of Series UDF</a>

- Die Python-Funktion nimmt einen Iterator von Batches statt eines einzelnen Eingabe-Batches entgegen und gibt einen Iterator von Ausgabe-Batches statt eines einzelnen Ausgabe-Batches zurück.
- Die Gesamtlänge der Ausgabe im Iterator muss der Gesamtlänge der Eingabe entsprechen.
- Die gewrappte Pandas-UDF nimmt eine einzelne Spark-Spalte als Eingabe.

```python
import pandas as pd
from typing import Iterator
from pyspark.sql.functions import col, pandas_udf, struct

pdf = pd.DataFrame([1, 2, 3], columns=["x"])
df = spark.createDataFrame(pdf)

# When the UDF is called with the column,
# the input to the underlying function is an iterator of pd.Series.
@pandas_udf("long")
def plus_one(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
    for x in batch_iter:
        yield x + 1

df.select(plus_one(col("x"))).show()
# +-----------+
# |plus_one(x)|
# +-----------+
# |          2|
# |          3|
# |          4|
# +-----------+

# In the UDF, you can initialize some state before processing batches.
# Wrap your code with try/finally or use context managers to ensure
# the release of resources at the end.
y = 1  # value captured by the UDF closure

@pandas_udf("long")
def plus_y(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
    try:
        for x in batch_iter:
            yield x + y
    finally:
        pass  # release resources here, if any

df.select(plus_y(col("x"))).show()
# +---------+
# |plus_y(x)|
# +---------+
# |        2|
# |        3|
# |        4|
# +---------+
```

---

## <a id="iterator-multi-series">3. Iterator of multiple Series to Iterator of Series UDF</a>

- Die zugrunde liegende Python-Funktion nimmt einen Iterator eines Tupels von pandas-Series entgegen.
- Die gewrappte Pandas-UDF nimmt mehrere Spark-Spalten als Eingabe.

```python
from typing import Iterator, Tuple
import pandas as pd

from pyspark.sql.functions import col, pandas_udf, struct

pdf = pd.DataFrame([1, 2, 3], columns=["x"])
df = spark.createDataFrame(pdf)

@pandas_udf("long")
def multiply_two_cols(
        iterator: Iterator[Tuple[pd.Series, pd.Series]]) -> Iterator[pd.Series]:
    for a, b in iterator:
        yield a * b

df.select(multiply_two_cols("x", "x")).show()
# +-----------------------+
# |multiply_two_cols(x, x)|
# +-----------------------+
# |                      1|
# |                      4|
# |                      9|
# +-----------------------+
```

---

## <a id="series-to-scalar">4. Series to scalar UDF</a>

```python
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql import Window

df = spark.createDataFrame(
    [(1, 1.0), (1, 2.0), (2, 3.0), (2, 5.0), (2, 10.0)],
    ("id", "v"))

# Declare the function and create the UDF
@pandas_udf("double")
def mean_udf(v: pd.Series) -> float:
    return v.mean()

df.select(mean_udf(df['v'])).show()
# +-----------+
# |mean_udf(v)|
# +-----------+
# |        4.2|
# +-----------+

df.groupby("id").agg(mean_udf(df['v'])).show()
# +---+-----------+
# | id|mean_udf(v)|
# +---+-----------+
# |  1|        1.5|
# |  2|        6.0|
# +---+-----------+

w = Window \
    .partitionBy('id') \
    .rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)
df.withColumn('mean_v', mean_udf(df['v']).over(w)).show()
# +---+----+------+
# | id|   v|mean_v|
# +---+----+------+
# |  1| 1.0|   1.5|
# |  1| 2.0|   1.5|
# |  2| 3.0|   6.0|
# |  2| 5.0|   6.0|
# |  2|10.0|   6.0|
# +---+----+------+
```

---

## <a id="arrow-batch-size">5. Nutzung: Arrow-Batch-Größe konfigurieren</a>

**Hinweis:** Diese Konfiguration hat keinen Einfluss auf serverloses Compute oder auf Compute mit Standard Access Mode und Databricks Runtime 13.3 LTS bis 14.2. Auf serverlosem Compute verwaltet die Plattform das Arrow-Batch-Sizing intern.

Datenpartitionen in Spark werden in Arrow-Record-Batches konvertiert, was vorübergehend zu hohem Speicherverbrauch in der JVM führen kann. Um mögliche Out-of-Memory-Fehler zu vermeiden, lässt sich die Größe der Arrow-Record-Batches über die Konfiguration `spark.sql.execution.arrow.maxRecordsPerBatch` anpassen — ein Integer, der die maximale Zeilenanzahl pro Batch festlegt. Der Standardwert ist **10.000 Datensätze pro Batch**. Bei einer großen Spaltenanzahl sollte der Wert entsprechend angepasst werden. Mit diesem Limit wird jede Datenpartition in eine oder mehrere Record-Batches zur Verarbeitung aufgeteilt.

---

## <a id="timestamp-semantics">6. Nutzung: Timestamp-mit-Zeitzone-Semantik</a>

Spark speichert Timestamps intern als UTC-Werte; Timestamp-Daten ohne angegebene Zeitzone werden beim Import als lokale Zeit nach UTC konvertiert, mit Mikrosekunden-Auflösung.

Werden Timestamp-Daten in Spark exportiert oder angezeigt, wird die Session-Zeitzone zur Lokalisierung der Timestamp-Werte verwendet. Die Session-Zeitzone wird über die Konfiguration `spark.sql.session.timeZone` festgelegt und ist standardmäßig die lokale JVM-Systemzeitzone. pandas verwendet einen `datetime64`-Typ mit Nanosekunden-Auflösung (`datetime64[ns]`), mit optionaler Zeitzone pro Spalte.

Werden Timestamp-Daten von Spark nach pandas übertragen, werden sie in Nanosekunden konvertiert, jede Spalte wird in die Spark-Session-Zeitzone konvertiert und anschließend in diese Zeitzone lokalisiert — dabei wird die Zeitzone entfernt und die Werte werden als lokale Zeit angezeigt. Dies geschieht beim Aufruf von `toPandas()` oder von `pandas_udf` mit Timestamp-Spalten.

Werden Timestamp-Daten von pandas nach Spark übertragen, werden sie in UTC-Mikrosekunden konvertiert. Dies geschieht beim Aufruf von `createDataFrame` mit einem pandas-DataFrame oder wenn eine Pandas-UDF einen Timestamp zurückgibt. Diese Konvertierungen erfolgen automatisch, damit Spark die Daten im erwarteten Format erhält — eigene Konvertierungen sind daher nicht nötig. Etwaige Nanosekundenwerte werden abgeschnitten.

Eine Standard-UDF lädt Timestamp-Daten als Python-`datetime`-Objekte, was sich von einem pandas-Timestamp unterscheidet. Für beste Performance wird empfohlen, bei der Arbeit mit Timestamps in einer Pandas-UDF die pandas-Time-Series-Funktionalität zu nutzen.

---

## <a id="quellen">7. Quellen</a>

- pandas user-defined functions: https://docs.databricks.com/aws/en/udf/pandas

**Stand:** 2026-08-22.
