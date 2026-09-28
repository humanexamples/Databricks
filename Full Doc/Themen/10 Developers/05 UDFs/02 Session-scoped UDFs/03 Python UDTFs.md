# Python UDTFs (Session-scoped)

Referenz zu session-scoped Python User-Defined Table Functions (UDTFs). Apache Spark implementiert Python-UDTFs als Python-Klassen mit einer verpflichtenden `eval`-Methode, die Ausgabezeilen per `yield` zurückgibt.

Zwei Registrierungsarten stehen zur Verfügung:

- **Unity Catalog:** die UDTF wird als governed Objekt in Unity Catalog registriert — siehe [Python UDTFs (Unity Catalog)](../01%20Unity%20Catalog%20UDFs/04%20Python%20UDTFs%20%28Unity%20Catalog%29.md).
- **Session-scoped:** Registrierung auf die lokale `SparkSession`, isoliert auf das aktuelle Notebook oder den aktuellen Job (dieses Dokument).

## Abschnittsübersicht

1. [Grundlegende UDTF-Syntax](#syntax)
2. [Eine UDTF registrieren](#registrieren)
3. [Eine registrierte UDTF aufrufen](#aufrufen)
4. [Dateien mit einer UDTF generieren](#dateien)
5. [Eine session-scoped UDTF zu Unity Catalog upgraden](#upgrade)
6. [Apache Arrow nutzen](#arrow)
7. [Variable Argumentlisten — `*args` und `**kwargs`](#varargs)
8. [Ein statisches Schema bei der Registrierung festlegen](#statisches-schema)
9. [Ein dynamisches Schema zur Aufrufzeit berechnen](#dynamisches-schema)
10. [Ausgabezeilen per `yield` zurückgeben](#yield)
11. [Skalare Argumente an eine UDTF übergeben](#skalare-argumente)
12. [Table-Argumente an eine UDTF übergeben](#table-argumente)

---

## <a id="syntax">1. Grundlegende UDTF-Syntax</a>

Um eine Klasse als UDTF zu verwenden, muss die PySpark-Funktion `udtf` importiert werden. Databricks empfiehlt, diese Funktion als Dekorator zu verwenden und Feldnamen und -typen explizit über die `returnType`-Option anzugeben (sofern die Klasse nicht wie später beschrieben eine `analyze`-Methode definiert).

Die folgende UDTF erstellt eine Tabelle aus einer festen Liste von zwei Integer-Argumenten:

```python
from pyspark.sql.functions import lit, udtf

@udtf(returnType="sum: int, diff: int")
class GetSumDiff:
    def eval(self, x: int, y: int):
        yield x + y, x - y

GetSumDiff(lit(1), lit(2)).show()
```

```text
+----+-----+
| sum| diff|
+----+-----+
|   3|   -1|
+----+-----+
```

---

## <a id="registrieren">2. Eine UDTF registrieren</a>

Um eine session-scoped UDTF für die Verwendung in SQL-Queries zu registrieren, wird `spark.udtf.register()` verwendet. Dabei werden ein Name für die SQL-Funktion und die Python-UDTF-Klasse angegeben.

```python
spark.udtf.register("get_sum_diff", GetSumDiff)
```

---

## <a id="aufrufen">3. Eine registrierte UDTF aufrufen</a>

Nach der Registrierung lässt sich die UDTF in SQL entweder über das `%sql`-Magic-Command oder die Funktion `spark.sql()` verwenden:

```python
spark.udtf.register("get_sum_diff", GetSumDiff)
spark.sql("SELECT * FROM get_sum_diff(1,2);").show()
```

```python
%sql
SELECT * FROM get_sum_diff(1,2);
```

---

## <a id="dateien">4. Dateien mit einer UDTF generieren</a>

Eine UDTF kann eine `FILE` als Eingabe entgegennehmen und eine oder mehrere neue `FILE`-Werte per `yield` zurückgeben — etwa beim Aufteilen eines Videos in einzelne Frames.

---

## <a id="upgrade">5. Eine session-scoped UDTF zu Unity Catalog upgraden</a>

Eine session-scoped UDTF lässt sich zu Unity Catalog upgraden, um zentralisierte Governance zu nutzen und das sichere Teilen und Wiederverwenden von Funktionen über Nutzer und Teams hinweg zu erleichtern.

**Hinweis:** Unity-Catalog-UDTFs erfordern Databricks Runtime 18 oder höher.

Zum Upgrade wird SQL DDL mit der `CREATE OR REPLACE FUNCTION`-Anweisung verwendet. Das folgende Beispiel zeigt, wie die UDTF `GetSumDiff` von einer session-scoped Funktion in eine Unity-Catalog-Funktion umgewandelt wird:

```sql
CREATE OR REPLACE FUNCTION get_sum_diff(x INT, y INT)
RETURNS TABLE (sum INT, diff INT)
LANGUAGE PYTHON
HANDLER 'GetSumDiff'
AS $$
class GetSumDiff:
    def eval(self, x: int, y: int):
        yield x + y, x - y
$$;

SELECT * FROM get_sum_diff(10, 3);
```

```text
+-----+------+
| sum | diff |
+-----+------+
| 13  | 7    |
+-----+------+
```

---

## <a id="arrow">6. Apache Arrow nutzen</a>

Erhält die UDTF nur eine kleine Datenmenge als Eingabe, gibt aber eine große Tabelle aus, empfiehlt Databricks die Nutzung von Apache Arrow. Aktivierbar über den Parameter `useArrow` bei der Deklaration der UDTF:

```python
@udtf(returnType="c1: int, c2: int", useArrow=True)
```

---

## <a id="varargs">7. Variable Argumentlisten — `*args` und `**kwargs`</a>

```python
@udtf(returnType="sum: int, diff: int")
class GetSumDiff:
    def eval(self, *args):
        assert(len(args) == 2)
        assert(isinstance(arg, int) for arg in args)
        x = args[0]
        y = args[1]
        yield x + y, x - y

GetSumDiff(lit(1), lit(2)).show()
```

```python
@udtf(returnType="sum: int, diff: int")
class GetSumDiff:
    def eval(self, **kwargs):
        x = kwargs["x"]
        y = kwargs["y"]
        yield x + y, x - y

GetSumDiff(x=lit(1), y=lit(2)).show()
```

---

## <a id="statisches-schema">8. Ein statisches Schema bei der Registrierung festlegen</a>

Die UDTF gibt Zeilen mit einem Ausgabeschema aus geordneten Spaltennamen und -typen zurück. Soll das UDTF-Schema für alle Queries stets gleich bleiben, lässt sich nach dem `@udtf`-Dekorator ein statisches, festes Schema angeben — entweder als `StructType`:

```python
StructType().add("c1", StringType())
```

oder als DDL-String, der einen Struct-Typ repräsentiert:

```text
c1: string
```

---

## <a id="dynamisches-schema">9. Ein dynamisches Schema zur Aufrufzeit berechnen</a>

UDTFs können das Ausgabeschema auch programmatisch für jeden Aufruf abhängig von den Werten der Eingabeargumente berechnen. Dazu wird eine statische Methode namens `analyze` definiert, die null oder mehr Parameter entgegennimmt, die den Argumenten des jeweiligen UDTF-Aufrufs entsprechen.

Jedes Argument der `analyze`-Methode ist eine Instanz der Klasse `AnalyzeArgument`:

| `AnalyzeArgument`-Feld | Beschreibung |
|---|---|
| `dataType` | Der Typ des Eingabearguments als `DataType`. Für Table-Argumente ist dies ein `StructType`, das die Spalten der Tabelle repräsentiert. |
| `value` | Der Wert des Eingabearguments als `Optional[Any]`. Ist `None` für Table-Argumente oder literale Skalarargumente, die nicht konstant sind. |
| `isTable` | Ob das Eingabeargument eine Tabelle ist, als `BooleanType`. |
| `isConstantExpression` | Ob das Eingabeargument ein konstant-auswertbarer Ausdruck ist, als `BooleanType`. |

Die `analyze`-Methode gibt eine Instanz der Klasse `AnalyzeResult` zurück, die das Schema der Ergebnistabelle als `StructType` sowie einige optionale Felder enthält. Akzeptiert die UDTF ein Eingabe-Table-Argument, kann `AnalyzeResult` außerdem eine gewünschte Art der Partitionierung und Ordnung der Zeilen der Eingabetabelle über mehrere UDTF-Aufrufe hinweg enthalten (siehe [Partitionierung aus der analyze-Methode heraus](#partitionierung-analyze)):

| `AnalyzeResult`-Feld | Beschreibung |
|---|---|
| `schema` | Das Schema der Ergebnistabelle als `StructType`. |
| `withSinglePartition` | Ob alle Eingabezeilen an dieselbe UDTF-Klasseninstanz gesendet werden, als `BooleanType`. |
| `partitionBy` | Falls nicht leer, werden alle Zeilen mit jeder eindeutigen Kombination von Werten der Partitionierungsausdrücke von einer separaten UDTF-Instanz verarbeitet. |
| `orderBy` | Falls nicht leer, legt dies eine Reihenfolge der Zeilen innerhalb jeder Partition fest. |
| `select` | Falls nicht leer, eine Sequenz von Ausdrücken, die die UDTF für Catalyst zur Auswertung gegen die Spalten des Eingabe-`TABLE`-Arguments angibt. Die UDTF erhält für jeden Namen in der Liste ein Eingabeattribut, in der aufgeführten Reihenfolge. |

Dieses `analyze`-Beispiel liefert eine Ausgabespalte pro Wort im Eingabe-String-Argument:

```python
from pyspark.sql.functions import lit, udtf
from pyspark.sql.types import StructType, IntegerType
from pyspark.sql.udtf import AnalyzeArgument, AnalyzeResult


@udtf
class MyUDTF:
  @staticmethod
  def analyze(text: AnalyzeArgument) -> AnalyzeResult:
    schema = StructType()
    for index, word in enumerate(sorted(list(set(text.value.split(" "))))):
      schema = schema.add(f"word_{index}", IntegerType())
    return AnalyzeResult(schema=schema)

  def eval(self, text: str):
    counts = {}
    for word in text.split(" "):
      if word not in counts:
            counts[word] = 0
      counts[word] += 1
    result = []
    for word in sorted(list(set(text.split(" ")))):
      result.append(counts[word])
    yield result

MyUDTF(lit("hello world")).columns
```

```text
['word_0', 'word_1']
```

### Zustand für zukünftige `eval`-Aufrufe weitergeben

Die `analyze`-Methode eignet sich als praktischer Ort für Initialisierung, deren Ergebnisse dann an zukünftige `eval`-Aufrufe desselben UDTF-Aufrufs weitergegeben werden.

Dazu wird eine Subklasse von `AnalyzeResult` erstellt und eine Instanz dieser Subklasse aus der `analyze`-Methode zurückgegeben. Anschließend wird der `__init__`-Methode ein zusätzliches Argument hinzugefügt, um diese Instanz entgegenzunehmen.

Dieses `analyze`-Beispiel gibt ein konstantes Ausgabeschema zurück, fügt aber benutzerdefinierte Informationen in die Ergebnis-Metadaten ein, die von zukünftigen `__init__`-Aufrufen konsumiert werden:

```python
from pyspark.sql.functions import lit, udtf
from pyspark.sql.types import StructType, IntegerType
from pyspark.sql.udtf import AnalyzeArgument, AnalyzeResult

@dataclass
class AnalyzeResultWithBuffer(AnalyzeResult):
    buffer: str = ""

@udtf
class TestUDTF:
  def __init__(self, analyze_result=None):
    self._total = 0
    if analyze_result is not None:
      self._buffer = analyze_result.buffer
    else:
      self._buffer = ""

  @staticmethod
  def analyze(argument, _) -> AnalyzeResult:
    if (
      argument.value is None
      or argument.isTable
      or not isinstance(argument.value, str)
      or len(argument.value) == 0
    ):
      raise Exception("The first argument must be a non-empty string")
    assert argument.dataType == StringType()
    assert not argument.isTable
    return AnalyzeResultWithBuffer(
      schema=StructType()
        .add("total", IntegerType())
        .add("buffer", StringType()),
      withSinglePartition=True,
      buffer=argument.value,
    )

  def eval(self, argument, row: Row):
    self._total += 1

  def terminate(self):
    yield self._total, self._buffer

spark.udtf.register("test_udtf", TestUDTF)

spark.sql(
  """
  WITH t AS (
    SELECT id FROM range(1, 21)
  )
  SELECT total, buffer
  FROM test_udtf("abc", TABLE(t))
  """
).show()
```

```text
+-------+-------+
| count | buffer|
+-------+-------+
|    20 |  "abc"|
+-------+-------+
```

---

## <a id="yield">10. Ausgabezeilen per `yield` zurückgeben</a>

Die `eval`-Methode läuft einmal pro Zeile des Table-Arguments (oder genau einmal, falls kein Table-Argument übergeben wird), gefolgt von einem abschließenden Aufruf der `terminate`-Methode. Beide Methoden geben null oder mehr Zeilen zurück, die dem Ergebnisschema entsprechen, indem sie Tupel, Listen oder `pyspark.sql.Row`-Objekte per `yield` zurückgeben.

Rückgabe einer Zeile als Tupel aus drei Elementen:

```python
def eval(self, x, y, z):
  yield (x, y, z)
```

Die Klammern können auch weggelassen werden:

```python
def eval(self, x, y, z):
  yield x, y, z
```

Ein Komma am Ende gibt eine Zeile mit nur einer Spalte zurück:

```python
def eval(self, x, y, z):
  yield x,
```

Auch ein `pyspark.sql.Row`-Objekt kann per `yield` zurückgegeben werden:

```python
def eval(self, x, y, z):
  from pyspark.sql.types import Row
  yield Row(x, y, z)
```

Dieses Beispiel gibt Ausgabezeilen aus der `terminate`-Methode über eine Python-Liste zurück — Zustand aus vorangegangenen Schritten der UDTF-Auswertung lässt sich dazu in der Klasse speichern:

```python
def terminate(self):
  yield [self.x, self.y, self.z]
```

---

## <a id="skalare-argumente">11. Skalare Argumente an eine UDTF übergeben</a>

Skalare Argumente können als konstante Ausdrücke aus Literalwerten oder darauf basierenden Funktionen übergeben werden:

```sql
SELECT * FROM get_sum_diff(1, y => 2)
```

---

## <a id="table-argumente">12. Table-Argumente an eine UDTF übergeben</a>

Python-UDTFs können zusätzlich zu skalaren Eingabeargumenten eine Eingabetabelle als Argument entgegennehmen. Eine einzelne UDTF kann auch ein Table-Argument und mehrere skalare Argumente gleichzeitig akzeptieren.

Jede SQL-Query kann eine Eingabetabelle über das Schlüsselwort `TABLE` gefolgt von Klammern um einen passenden Tabellen-Identifikator übergeben, z. B. `TABLE(t)`. Alternativ lässt sich auch eine Table-Subquery übergeben, z. B. `TABLE(SELECT a, b, c FROM t)` oder `TABLE(SELECT t1.a, t2.b FROM t1 INNER JOIN t2 USING (key))`.

Das Table-Argument wird dann als `pyspark.sql.Row`-Argument an die `eval`-Methode übergeben, mit einem Aufruf von `eval` pro Zeile der Eingabetabelle. Standard-PySpark-Spaltenfeld-Annotationen lassen sich verwenden, um mit Spalten in jeder Zeile zu interagieren. Das folgende Beispiel importiert explizit den PySpark-`Row`-Typ und filtert die übergebene Tabelle auf das `id`-Feld:

```python
from pyspark.sql.functions import udtf
from pyspark.sql.types import Row

@udtf(returnType="id: int")
class FilterUDTF:
    def eval(self, row: Row):
        if row["id"] > 5:
            yield row["id"],

spark.udtf.register("filter_udtf", FilterUDTF)
```

Zum Abfragen der Funktion wird das SQL-Schlüsselwort `TABLE` verwendet:

```sql
SELECT * FROM filter_udtf(TABLE(SELECT * FROM range(10)));
```

```text
+---+
| id|
+---+
|  6|
|  7|
|  8|
|  9|
+---+
```

### Partitionierung der Eingabezeilen über Funktionsaufrufe festlegen

Beim Aufruf einer UDTF mit einem Table-Argument kann jede SQL-Query die Eingabetabelle anhand der Werte einer oder mehrerer Spalten der Eingabetabelle auf mehrere UDTF-Aufrufe partitionieren.

Um eine Partitionierung festzulegen, wird die `PARTITION BY`-Klausel im Funktionsaufruf nach dem `TABLE`-Argument verwendet. Das garantiert, dass alle Eingabezeilen mit jeder eindeutigen Kombination von Werten der Partitionierungsspalten von genau einer Instanz der UDTF-Klasse verarbeitet werden.

Neben einfachen Spaltenverweisen akzeptiert die `PARTITION BY`-Klausel auch beliebige Ausdrücke, die auf Eingabetabellenspalten basieren — z. B. die `LENGTH` eines Strings, das Extrahieren eines Monats aus einem Datum oder die Verkettung zweier Werte.

Statt `PARTITION BY` lässt sich auch `WITH SINGLE PARTITION` angeben, um nur eine Partition anzufordern, in der alle Eingabezeilen von genau einer Instanz der UDTF-Klasse verarbeitet werden müssen.

Innerhalb jeder Partition kann optional eine geforderte Reihenfolge der Eingabezeilen festgelegt werden, in der die `eval`-Methode der UDTF sie konsumiert — dazu wird nach der oben beschriebenen `PARTITION BY`- oder `WITH SINGLE PARTITION`-Klausel eine `ORDER BY`-Klausel angegeben.

Beispiel-UDTF:

```python
from pyspark.sql.functions import udtf
from pyspark.sql.types import Row

@udtf(returnType="a: string, b: int")
class FilterUDTF:
  def __init__(self):
    self.key = ""
    self.max = 0

  def eval(self, row: Row):
    self.key = row["a"]
    self.max = max(self.max, row["b"])

  def terminate(self):
    yield self.key, self.max

spark.udtf.register("filter_udtf", FilterUDTF)
```

Partitionierungsoptionen können auf mehrere Arten beim Aufruf über die Eingabetabelle angegeben werden:

```sql
-- Create an input table with some example values.
DROP TABLE IF EXISTS values_table;
CREATE TABLE values_table (a STRING, b INT);
INSERT INTO values_table VALUES ('abc', 2), ('abc', 4), ('def', 6), ('def', 8);
SELECT * FROM values_table;
```

```text
+-------+----+
|     a |  b |
+-------+----+
| "abc" | 2  |
| "abc" | 4  |
| "def" | 6  |
| "def" | 8  |
+-------+----+
```

```sql
-- Query the UDTF with the input table as an argument and a directive to partition the input
-- rows such that all rows with each unique value in the `a` column are processed by the same
-- instance of the UDTF class. Within each partition, the rows are ordered by the `b` column.
SELECT * FROM filter_udtf(TABLE(values_table) PARTITION BY a ORDER BY b) ORDER BY 1;
```

```text
+-------+----+
|     a |  b |
+-------+----+
| "abc" | 4  |
| "def" | 8  |
+-------+----+
```

```sql
-- Query the UDTF with the input table as an argument and a directive to partition the input
-- rows such that all rows with each unique result of evaluating the "LENGTH(a)" expression are
-- processed by the same instance of the UDTF class. Within each partition, the rows are ordered
-- by the `b` column.
SELECT * FROM filter_udtf(TABLE(values_table) PARTITION BY LENGTH(a) ORDER BY b) ORDER BY 1;
```

```text
+-------+---+
|     a | b |
+-------+---+
| "def" | 8 |
+-------+---+
```

```sql
-- Query the UDTF with the input table as an argument and a directive to consider all the input
-- rows in one single partition such that exactly one instance of the UDTF class consumes all of
-- the input rows. Within each partition, the rows are ordered by the `b` column.
SELECT * FROM filter_udtf(TABLE(values_table) WITH SINGLE PARTITION ORDER BY b) ORDER BY 1;
```

```text
+-------+----+
|     a |  b |
+-------+----+
| "def" | 8 |
+-------+----+
```

### <a id="partitionierung-analyze">Partitionierung der Eingabezeilen aus der `analyze`-Methode heraus festlegen</a>

Für jede der oben genannten Partitionierungs-Arten beim UDTF-Aufruf in SQL-Queries gibt es eine entsprechende Möglichkeit, dieselbe Partitionierungsmethode automatisch über die `analyze`-Methode der UDTF festzulegen:

- Statt eine UDTF als `SELECT * FROM udtf(TABLE(t) PARTITION BY a)` aufzurufen, kann die `analyze`-Methode das Feld `partitionBy=[PartitioningColumn("a")]` setzen und die Funktion einfach über `SELECT * FROM udtf(TABLE(t))` aufgerufen werden.
- Statt `TABLE(t) WITH SINGLE PARTITION ORDER BY b` in der SQL-Query anzugeben, kann `analyze` die Felder `withSinglePartition=true` und `orderBy=[OrderingColumn("b")]` setzen und dann einfach `TABLE(t)` übergeben werden.
- Statt `TABLE(SELECT a FROM t)` zu übergeben, kann `select=[SelectedColumn("a")]` gesetzt werden.

Im folgenden Beispiel gibt `analyze` ein konstantes Ausgabeschema zurück, wählt eine Teilmenge der Spalten der Eingabetabelle aus und legt fest, dass die Eingabetabelle anhand der Werte der Spalte `date` auf mehrere UDTF-Aufrufe partitioniert wird:

```python
@staticmethod
def analyze(*args) -> AnalyzeResult:
  """
  The input table will be partitioned across several UDTF calls based on the monthly
  values of each `date` column. The rows within each partition will arrive ordered by the `date`
  column. The UDTF will only receive the `date` and `word` columns from the input table.
  """
  from pyspark.sql.functions import (
    AnalyzeResult,
    OrderingColumn,
    PartitioningColumn,
  )

  assert len(args) == 1, "This function accepts one argument only"
  assert args[0].isTable, "Only table arguments are supported"
  return AnalyzeResult(
    schema=StructType()
      .add("month", DateType())
      .add("longest_word", IntegerType()),
    partitionBy=[
      PartitioningColumn("extract(month from date)")],
    orderBy=[
      OrderingColumn("date")],
    select=[
      SelectedColumn("date"),
      SelectedColumn(
        name="length(word)",
        alias="length_word")])
```

