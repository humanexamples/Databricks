# `assertDataFrameEqual` und `assertSchemaEqual` — vollständige API-Referenz

Vollständige Parameter- und Beispiel-Referenz der beiden zentralen `pyspark.testing`-Funktionen, die in diesem Kapitel durchgängig verwendet werden (siehe [07 PySpark-Testing-Utilities und Praxisbeispiel.md](07%20PySpark-Testing-Utilities%20und%20Praxisbeispiel.md), Abschnitt 1). Diese Datei ergänzt die dortigen Kurzbeschreibungen um alle offiziell dokumentierten Parameter, Hinweise und Beispiele — direkt aus dem Docstring der Referenzimplementierung (`pyspark/testing/utils.py`) übernommen. Teil der [Testing](../Uebersicht.md)-Reihe, Kapitel [01 Unit Test](../01%20Unit%20Test/).

## Abschnittsübersicht

1. [`assertDataFrameEqual`: Signatur und Parameter](#dfe-signatur)
2. [`assertDataFrameEqual`: Hinweise (Notes)](#dfe-notes)
3. [`assertDataFrameEqual`: Beispiele](#dfe-beispiele)
4. [`assertSchemaEqual`: Signatur und Parameter](#se-signatur)
5. [`assertSchemaEqual`: Hinweise (Notes)](#se-notes)
6. [`assertSchemaEqual`: Beispiele](#se-beispiele)
7. [Quelle](#quelle)

---

## <a id="dfe-signatur">1. `assertDataFrameEqual`: Signatur und Parameter</a>

*Verfügbar seit Spark 3.5.0.*

```python
def assertDataFrameEqual(
    actual: Union[DataFrame, "pandas.DataFrame", "pyspark.pandas.DataFrame", List[Row]],
    expected: Union[DataFrame, "pandas.DataFrame", "pyspark.pandas.DataFrame", List[Row]],
    checkRowOrder: bool = False,
    rtol: float = 1e-5,
    atol: float = 1e-8,
    ignoreNullable: bool = True,
    ignoreColumnOrder: bool = False,
    ignoreColumnName: bool = False,
    ignoreColumnType: bool = False,
    maxErrors: Optional[int] = None,
    showOnlyDiff: bool = False,
    includeDiffRows: bool = False,
)
```

Util-Funktion zur Gleichheitsprüfung zwischen `actual` und `expected` (DataFrames oder Listen von `Row`-Objekten). Unterstützt Spark-, Spark-Connect-, pandas- und pandas-on-Spark-DataFrames (für Details zu Letzterem siehe `assertPandasOnSparkEqual`).

| Parameter | Typ / Standard | Bedeutung |
|---|---|---|
| `actual` | DataFrame (Spark/Spark-Connect/pandas/pandas-on-Spark) oder `List[Row]` | das zu vergleichende/testende DataFrame |
| `expected` | wie `actual` | das erwartete Ergebnis, mit dem `actual` verglichen wird |
| `checkRowOrder` | `bool`, Standard `False` | ob die Zeilenreihenfolge beim Vergleich berücksichtigt wird. `False` (Standard): Reihenfolge wird ignoriert. `True`: Reihenfolge muss übereinstimmen (siehe Abschnitt 2) |
| `rtol` | `float`, Standard `1e-5` | relative Toleranz für die Näherungsgleichheit von Float-Werten (siehe Abschnitt 2) |
| `atol` | `float`, Standard `1e-8` | absolute Toleranz für die Näherungsgleichheit von Float-Werten (siehe Abschnitt 2) |
| `ignoreNullable` | `bool`, Standard `True` *(seit 4.0.0)* | ob die `nullable`-Eigenschaft einer Spalte beim Schema-Gleichheitscheck berücksichtigt wird. `True` (Standard): wird ignoriert. `False`: Spalten gelten nur bei identischer `nullable`-Einstellung als gleich |
| `ignoreColumnOrder` | `bool`, Standard `False` *(seit 4.0.0)* | ob Spalten nach Position (Standard) oder nach Name verglichen werden. `True`: eine Spalte im erwarteten DataFrame wird mit der gleichnamigen Spalte im tatsächlichen DataFrame verglichen |
| `ignoreColumnName` | `bool`, Standard `False` *(seit 4.0.0)* | ob der initiale Schema-Gleichheitscheck bei unterschiedlichen Spaltennamen fehlschlägt. `True`: Funktion besteht auch bei unterschiedlichen Namen — Datentypen werden dann anhand der Spaltenreihenfolge verglichen |
| `ignoreColumnType` | `bool`, Standard `False` *(seit 4.0.0)* | ob der Datentyp einer Spalte beim Vergleich ignoriert wird. `True`: Schema-Gleichheitscheck besteht auch bei unterschiedlichen Datentypen, Zeilen werden trotzdem verglichen |
| `maxErrors` | `Optional[int]`, Standard `None` *(seit 4.0.0)* | maximale Anzahl an Zeilen-Vergleichsfehlschlägen, bevor die Funktion abbricht — `None` (Standard) vergleicht alle Zeilen unabhängig von der Fehleranzahl |
| `showOnlyDiff` | `bool`, Standard `False` *(seit 4.0.0)* | `True`: Fehlermeldung enthält nur die abweichenden Zeilen. `False` (Standard): Fehlermeldung enthält alle Zeilen (sofern mindestens eine Zeile abweicht) |
| `includeDiffRows` | `bool`, Standard `False` *(seit 4.0.0)* | `True`: die abweichenden Zeilen werden im `PySparkAssertionError` mitgeliefert (nützlich zum Debuggen). `False` (Standard): abweichende Zeilen werden nicht als Datensatz zurückgegeben |

## <a id="dfe-notes">2. `assertDataFrameEqual`: Hinweise (Notes)</a>

- Schlägt `assertDataFrameEqual` fehl, nutzt die Fehlermeldung Pythons `difflib`-Bibliothek, um pro abweichender Zeile in `actual`/`expected` ein Diff-Log anzuzeigen.
- Bei `checkRowOrder` gilt: Die Zeilenreihenfolge eines PySpark-DataFrames ist **nicht-deterministisch**, sofern nicht explizit sortiert.
- Schema-Gleichheit wird **nur** geprüft, wenn `expected` ein DataFrame ist (nicht bei einer Liste von `Row`-Objekten).
- Bei Float-/Decimal-Werten prüft `assertDataFrameEqual` **Näherungsgleichheit**: Zwei Werte `a` und `b` gelten als näherungsweise gleich, wenn gilt:

  ```
  absolute(a - b) <= (atol + rtol * absolute(b))
  ```

- `ignoreColumnOrder` und `ignoreColumnName` dürfen **nicht gleichzeitig** auf `True` gesetzt werden.

## <a id="dfe-beispiele">3. `assertDataFrameEqual`: Beispiele</a>

**Grundlegende Gleichheit:**

```python
>>> df1 = spark.createDataFrame(data=[("1", 1000), ("2", 3000)], schema=["id", "amount"])
>>> df2 = spark.createDataFrame(data=[("1", 1000), ("2", 3000)], schema=["id", "amount"])
>>> assertDataFrameEqual(df1, df2)  # pass, DataFrames are identical
```

**Näherungsgleichheit mit `rtol`:**

```python
>>> df1 = spark.createDataFrame(data=[("1", 0.1), ("2", 3.23)], schema=["id", "amount"])
>>> df2 = spark.createDataFrame(data=[("1", 0.109), ("2", 3.23)], schema=["id", "amount"])
>>> assertDataFrameEqual(df1, df2, rtol=1e-1)  # pass, DataFrames are approx equal by rtol
```

**Vergleich gegen eine Liste von `Row`-Objekten:**

```python
>>> df1 = spark.createDataFrame(data=[(1, 1000), (2, 3000)], schema=["id", "amount"])
>>> list_of_rows = [Row(1, 1000), Row(2, 3000)]
>>> assertDataFrameEqual(df1, list_of_rows)  # pass, actual and expected data are equal
```

**pandas-on-Spark-DataFrames:**

```python
>>> import pyspark.pandas as ps
>>> df1 = ps.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})
>>> df2 = ps.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6], 'c': [7, 8, 9]})
>>> # pass, pandas-on-Spark DataFrames are equal
>>> assertDataFrameEqual(df1, df2)
```

**Fehlschlag mit Diff-Ausgabe (abweichende Werte):**

```python
>>> df1 = spark.createDataFrame(
...     data=[("1", 1000.00), ("2", 3000.00), ("3", 2000.00)], schema=["id", "amount"])
>>> df2 = spark.createDataFrame(
...     data=[("1", 1001.00), ("2", 3000.00), ("3", 2003.00)], schema=["id", "amount"])
>>> assertDataFrameEqual(df1, df2)
Traceback (most recent call last):
...
PySparkAssertionError: [DIFFERENT_ROWS] Results do not match: ( 66.66667 % )
*** actual ***
! Row(id='1', amount=1000.0)
  Row(id='2', amount=3000.0)
! Row(id='3', amount=2000.0)
*** expected ***
! Row(id='1', amount=1001.0)
  Row(id='2', amount=3000.0)
! Row(id='3', amount=2003.0)
```

**Beispiel für `ignoreNullable`:**

```python
>>> from pyspark.sql.types import StructType, StructField, StringType, LongType
>>> df1_nullable = spark.createDataFrame(
...     data=[(1000, "1"), (5000, "2")],
...     schema=StructType(
...         [StructField("amount", LongType(), True), StructField("id", StringType(), True)]
...     )
... )
>>> df2_nullable = spark.createDataFrame(
...     data=[(1000, "1"), (5000, "2")],
...     schema=StructType(
...         [StructField("amount", LongType(), True), StructField("id", StringType(), False)]
...     )
... )
>>> assertDataFrameEqual(df1_nullable, df2_nullable, ignoreNullable=True)  # pass
>>> assertDataFrameEqual(df1_nullable, df2_nullable, ignoreNullable=False)
Traceback (most recent call last):
...
PySparkAssertionError: [DIFFERENT_SCHEMA] Schemas do not match.
--- actual
+++ expected
- StructType([StructField('amount', LongType(), True), StructField('id', StringType(), True)])
?                                                                                      ^^^
+ StructType([StructField('amount', LongType(), True), StructField('id', StringType(), False)])
?                                                                                      ^^^^
```

**Beispiel für `ignoreColumnOrder`:**

```python
>>> df1_col_order = spark.createDataFrame(
...     data=[(1000, "1"), (5000, "2")], schema=["amount", "id"]
... )
>>> df2_col_order = spark.createDataFrame(
...     data=[("1", 1000), ("2", 5000)], schema=["id", "amount"]
... )
>>> assertDataFrameEqual(df1_col_order, df2_col_order, ignoreColumnOrder=True)
```

**Beispiel für `ignoreColumnName`:**

```python
>>> df1_col_names = spark.createDataFrame(
...     data=[(1000, "1"), (5000, "2")], schema=["amount", "identity"]
... )
>>> df2_col_names = spark.createDataFrame(
...     data=[(1000, "1"), (5000, "2")], schema=["amount", "id"]
... )
>>> assertDataFrameEqual(df1_col_names, df2_col_names, ignoreColumnName=True)
```

**Beispiel für `ignoreColumnType`:**

```python
>>> df1_col_types = spark.createDataFrame(
...     data=[(1000, "1"), (5000, "2")], schema=["amount", "id"]
... )
>>> df2_col_types = spark.createDataFrame(
...     data=[(1000.0, "1"), (5000.0, "2")], schema=["amount", "id"]
... )
>>> assertDataFrameEqual(df1_col_types, df2_col_types, ignoreColumnType=True)
```

**Beispiel für `maxErrors`** (meldet nur die erste abweichende Zeile):

```python
>>> df1 = spark.createDataFrame([(1, "A"), (2, "B"), (3, "C")])
>>> df2 = spark.createDataFrame([(1, "A"), (2, "X"), (3, "Y")])
>>> assertDataFrameEqual(df1, df2, maxErrors=1)
Traceback (most recent call last):
...
PySparkAssertionError: [DIFFERENT_ROWS] Results do not match: ( 33.33333 % )
*** actual ***
  Row(_1=1, _2='A')
! Row(_1=2, _2='B')
*** expected ***
  Row(_1=1, _2='A')
! Row(_1=2, _2='X')
```

**Beispiel für `showOnlyDiff`** (meldet nur die abweichenden Zeilen):

```python
>>> df1 = spark.createDataFrame([(1, "A"), (2, "B"), (3, "C")])
>>> df2 = spark.createDataFrame([(1, "A"), (2, "X"), (3, "Y")])
>>> assertDataFrameEqual(df1, df2, showOnlyDiff=True)
Traceback (most recent call last):
...
PySparkAssertionError: [DIFFERENT_ROWS] Results do not match: ( 66.66667 % )
*** actual ***
! Row(_1=2, _2='B')
! Row(_1=3, _2='C')
*** expected ***
! Row(_1=2, _2='X')
! Row(_1=3, _2='Y')
```

**Beispiel für `includeDiffRows`** — die abweichenden Zeilen zur weiteren Analyse in den Fehler einbetten:

```python
>>> df1 = spark.createDataFrame(
...     data=[("1", 1000.00), ("2", 3000.00), ("3", 2000.00)], schema=["id", "amount"])
>>> df2 = spark.createDataFrame(
...     data=[("1", 1001.00), ("2", 3000.00), ("3", 2003.00)], schema=["id", "amount"])
>>> try:
...     assertDataFrameEqual(df1, df2, includeDiffRows=True)
... except PySparkAssertionError as e:
...     spark.createDataFrame(e.data).show()
+-----------+-----------+
|         _1|         _2|
+-----------+-----------+
|{1, 1000.0}|{1, 1001.0}|
|{3, 2000.0}|{3, 2003.0}|
+-----------+-----------+
```

---

## <a id="se-signatur">4. `assertSchemaEqual`: Signatur und Parameter</a>

*Verfügbar seit Spark 3.5.0.*

```python
def assertSchemaEqual(
    actual: StructType,
    expected: StructType,
    ignoreNullable: bool = True,
    ignoreColumnOrder: bool = False,
    ignoreColumnName: bool = False,
)
```

Util-Funktion zur Gleichheitsprüfung zwischen den DataFrame-Schemas `actual` und `expected`.

| Parameter | Typ / Standard | Bedeutung |
|---|---|---|
| `actual` | `StructType` | das zu vergleichende/testende Schema |
| `expected` | `StructType` | das erwartete Schema, mit dem `actual` verglichen wird |
| `ignoreNullable` | `bool`, Standard `True` *(seit 4.0.0)* | wie bei `assertDataFrameEqual` (siehe Abschnitt 1) |
| `ignoreColumnOrder` | `bool`, Standard `False` *(seit 4.0.0)* | wie bei `assertDataFrameEqual` |
| `ignoreColumnName` | `bool`, Standard `False` *(seit 4.0.0)* | wie bei `assertDataFrameEqual` |

## <a id="se-notes">5. `assertSchemaEqual`: Hinweise (Notes)</a>

Schlägt `assertSchemaEqual` fehl, nutzt die Fehlermeldung ebenfalls Pythons `difflib`-Bibliothek, um ein Diff-Log von `actual`- und `expected`-Schema anzuzeigen (identischer Mechanismus wie bei `assertDataFrameEqual`, siehe Abschnitt 2).

## <a id="se-beispiele">6. `assertSchemaEqual`: Beispiele</a>

**Grundlegende Gleichheit:**

```python
>>> from pyspark.sql.types import StructType, StructField, ArrayType, IntegerType, DoubleType
>>> s1 = StructType([StructField("names", ArrayType(DoubleType(), True), True)])
>>> s2 = StructType([StructField("names", ArrayType(DoubleType(), True), True)])
>>> assertSchemaEqual(s1, s2)  # pass, schemas are identical
```

**Unterschiedliche Schemas mit `ignoreNullable=False` schlagen fehl:**

```python
>>> s3 = StructType([StructField("names", ArrayType(DoubleType(), True), False)])
>>> assertSchemaEqual(s1, s3, ignoreNullable=False)
Traceback (most recent call last):
...
PySparkAssertionError: [DIFFERENT_SCHEMA] Schemas do not match.
--- actual
+++ expected
- StructType([StructField('names', ArrayType(DoubleType(), True), True)])
?                                                                 ^^^
+ StructType([StructField('names', ArrayType(DoubleType(), True), False)])
?                                                                 ^^^^
```

**Fehlschlag bei unterschiedlichen Spaltennamen und -typen:**

```python
>>> df1 = spark.createDataFrame(data=[(1, 1000), (2, 3000)], schema=["id", "number"])
>>> df2 = spark.createDataFrame(data=[("1", 1000), ("2", 5000)], schema=["id", "amount"])
>>> assertSchemaEqual(df1.schema, df2.schema)
Traceback (most recent call last):
...
PySparkAssertionError: [DIFFERENT_SCHEMA] Schemas do not match.
--- actual
+++ expected
- StructType([StructField('id', LongType(), True), StructField('number', LongType(), True)])
?                               ^^                               ^^^^^
+ StructType([StructField('id', StringType(), True), StructField('amount', LongType(), True)])
?                               ^^^^                              ++++ ^
```

**Vergleich ohne Berücksichtigung der Spaltenreihenfolge:**

```python
>>> s1 = StructType(
...     [StructField("a", IntegerType(), True), StructField("b", DoubleType(), True)]
... )
>>> s2 = StructType(
...     [StructField("b", DoubleType(), True), StructField("a", IntegerType(), True)]
... )
>>> assertSchemaEqual(s1, s2, ignoreColumnOrder=True)
```

**Vergleich ohne Berücksichtigung der Spaltennamen:**

```python
>>> s1 = StructType(
...     [StructField("a", IntegerType(), True), StructField("c", DoubleType(), True)]
... )
>>> s2 = StructType(
...     [StructField("b", IntegerType(), True), StructField("d", DoubleType(), True)]
... )
>>> assertSchemaEqual(s1, s2, ignoreColumnName=True)
```

### Quelle

- https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.testing.assertDataFrameEqual.html
- https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.testing.assertSchemaEqual.html
- https://github.com/apache/spark/blob/master/python/pyspark/testing/utils.py (Referenzimplementierung/Docstring-Quelle)

**Stand:** 2026-09-01.
