# Session-scoped UDFs, Pandas UDFs und UDTFs

UDFs, die direkt über die PySpark-/Scala-API in einer Notebook-/Job-Session registriert werden (`spark.udf.register`, `@udf`, `@pandas_udf`, `@udtf`, `UserDefinedAggregateFunction`) — an die aktuelle `SparkSession` gebunden, **nicht** katalogweit governed (im Unterschied zu Unity-Catalog-UDFs, siehe vorheriges Kapitel).

---

## 1. Python Scalar UDFs (Session-scoped)

- DBR ≤12.2 LTS: Python-/Pandas-UDFs auf UC-Compute mit Standard Access Mode **nicht** unterstützt.
- Ab **DBR 13.3 LTS**: Scalar-Python-UDFs und Pandas-UDFs für **alle** Access Modes.
- Graviton-Instance-Support für Python-UDFs auf UC-fähigen Clustern: ab **DBR 15.2**.

```python
def squared(s):
  return s * s
spark.udf.register("squaredWithPython", squared)

# Mit explizitem Rückgabetyp
from pyspark.sql.types import LongType
def squared_typed(s):
  return s * s
spark.udf.register("squaredWithPython", squared_typed, LongType())
```
```sql
%sql select id, squaredWithPython(id) as id_squared from test
-- Ergebnis: id=4 -> id_squared=16
```

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import LongType
squared_udf = udf(squared, LongType())
df.select("id", squared_udf("id").alias("id_squared"))

# Als Dekorator
@udf("long")
def squared_udf(s):
  return s * s
```

**Variant-Typen mit UDFs:**
```python
from pyspark.sql.types import VariantType

# Rückgabe eines Variant
@udf(returnType=VariantType())
def toVariant(jsonString):
  return VariantVal.parseJson(jsonString)

# Rückgabe eines Struct<Variant>
@udf(returnType=StructType([StructField("v", VariantType(), True)]))
def toStructVariant(jsonString):
  return {"v": VariantVal.parseJson(jsonString)}

# Rückgabe eines Array<Variant>
@udf(returnType=ArrayType(VariantType()))
def toArrayVariant(jsonString):
  return [VariantVal.parseJson(jsonString)]

# Rückgabe eines Map<String, Variant>
@udf(returnType=MapType(StringType(), VariantType(), True))
def toMapVariant(jsonString):
  return {"v1": VariantVal.parseJson(jsonString), "v2": VariantVal.parseJson("[" + jsonString + "]")}
```

- **Dateien mit UDF (Beta):** Admin-steuerbar über Previews-Seite. PySpark-Typ `FileType` als Parameter-/Rückgabetyp (auch verschachtelt). Dateiinhalt lesen: `file.as_local_file()` (lokaler Pfad) oder `file.open()` (Byte-Stream).

**Auswertungsreihenfolge/Null-Prüfung:** Spark SQL garantiert **keine** Auswertungsreihenfolge für Subexpressions.
```python
spark.udf.register("strlen", lambda s: len(s), "int")
spark.sql("select s from test1 where s is not null and strlen(s) > 1")  # keine Garantie
```
Lösung — UDF selbst null-aware machen, oder `IF`/`CASE WHEN`:
```python
spark.udf.register("strlen_nullsafe", lambda s: len(s) if not s is None else -1, "int")
spark.sql("select s from test1 where s is not null and strlen_nullsafe(s) > 1")  # ok
spark.sql("select s from test1 where if(s is not null, strlen(s), null) > 1")     # ok
```

**Service Credentials:**
```python
@udf
def use_service_credential():
    from databricks.service_credentials import getServiceCredentialsProvider
    import boto3
    # Service Credential 'testcred' in Unity Catalog vorausgesetzt
    boto3_session = boto3.Session(botocore_session=getServiceCredentialsProvider('testcred'))

# Default Credential des Compute automatisch verwenden
@udf
def use_default_service_credential():
    import boto3
    boto3_session = boto3.Session()
```
Berechtigungen analog Batch-UC-Python-UDFs: **Ersteller** braucht `ACCESS` auf dem Service Credential.

Task-Ausführungskontext: siehe Abschnitt 6 ("UDF Task Context").

**Limitierung:** PySpark-UDFs auf Clustern mit Standard Access Mode und auf serverlosem Compute unterstützen **keine** Instance Profiles.

---

## 2. Pandas UDFs (vektorisiert)

Nutzen **Apache Arrow** für Datentransfer und **pandas** für Verarbeitung — vektorisiert statt zeilenweise.

**Series to Series UDF:**
```python
import pandas as pd
from pyspark.sql.functions import col, pandas_udf
from pyspark.sql.types import LongType

def multiply_func(a: pd.Series, b: pd.Series) -> pd.Series:
    return a * b

multiply = pandas_udf(multiply_func, returnType=LongType())
df.select(multiply(col("x"), col("x"))).show()
# Ergebnis: x=3 -> 9
```
- Die zugrunde liegende Funktion muss auch direkt mit lokalen pandas-Daten ausführbar sein (`multiply_func(x, x)`).

**Iterator of Series to Iterator of Series UDF:** Funktion nimmt einen **Iterator von Batches** entgegen, gibt Iterator von Ausgabe-Batches zurück. Gesamtlänge Output = Gesamtlänge Input. Die UDF selbst nimmt eine einzelne Spark-Spalte als Eingabe.
```python
from typing import Iterator
import pandas as pd
from pyspark.sql.functions import col, pandas_udf

@pandas_udf("long")
def plus_one(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
    for x in batch_iter:
        yield x + 1

df.select(plus_one(col("x"))).show()
# Ergebnis: x=3 -> 4
```
Zustand vor Batch-Verarbeitung initialisieren (`try`/`finally` zur Ressourcenfreigabe):
```python
y = 1  # von der UDF-Closure erfasster Wert
@pandas_udf("long")
def plus_y(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
    try:
        for x in batch_iter:
            yield x + y
    finally:
        pass  # Ressourcen hier freigeben
```

**Iterator of multiple Series to Iterator of Series UDF:** Funktion nimmt Iterator eines **Tupels** von Series entgegen; UDF nimmt mehrere Spark-Spalten als Eingabe.
```python
from typing import Iterator, Tuple
import pandas as pd
from pyspark.sql.functions import pandas_udf

@pandas_udf("long")
def multiply_two_cols(iterator: Iterator[Tuple[pd.Series, pd.Series]]) -> Iterator[pd.Series]:
    for a, b in iterator:
        yield a * b

df.select(multiply_two_cols("x", "x")).show()
# Ergebnis: x=3 -> 9
```

**Series to scalar UDF:** verhält sich wie Spark-Aggregatfunktion — einsetzbar mit `select`, `groupby().agg()`, Fenster-Operationen (`over(w)`).
```python
import pandas as pd
from pyspark.sql.functions import pandas_udf
from pyspark.sql import Window

@pandas_udf("double")
def mean_udf(v: pd.Series) -> float:
    return v.mean()

df.select(mean_udf(df['v'])).show()
df.groupby("id").agg(mean_udf(df['v'])).show()

w = Window.partitionBy('id').rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)
df.withColumn('mean_v', mean_udf(df['v']).over(w)).show()
```

**Arrow-Batch-Größe:** `spark.sql.execution.arrow.maxRecordsPerBatch` (Integer, max. Zeilen/Batch) — **Standard: 10.000**. Hat **keinen** Effekt auf serverloses Compute oder Standard-Access-Mode-Compute mit DBR 13.3 LTS–14.2 (Plattform verwaltet Batch-Sizing dort intern). Bei großer Spaltenanzahl anpassen — Konvertierung von Partitionen in Arrow-Record-Batches kann hohen JVM-Speicherverbrauch verursachen.

**Timestamp-mit-Zeitzone-Semantik:**
- Spark speichert Timestamps intern als **UTC**; Timestamps ohne Zeitzone werden beim Import als lokale Zeit nach UTC konvertiert (Mikrosekunden). Beim Export/Anzeigen: Lokalisierung über **Session-Zeitzone** (`spark.sql.session.timeZone`, Standard: lokale JVM-Systemzeitzone).
- pandas nutzt `datetime64[ns]` (Nanosekunden) mit optionaler Zeitzone pro Spalte.
- **Spark → pandas** (`toPandas()`, `pandas_udf` mit Timestamp-Spalten): Konvertierung in Nanosekunden → Session-Zeitzone → dort lokalisiert (Zeitzone entfernt, Werte erscheinen als lokale Zeit).
- **pandas → Spark** (`createDataFrame` mit pandas-DataFrame, oder Pandas-UDF gibt Timestamp zurück): Konvertierung in UTC-Mikrosekunden; Nanosekunden werden abgeschnitten. Automatisch.
- Eine **Standard-UDF** lädt Timestamps als Python-`datetime` (anders als pandas-Timestamp). Für Performance bei Timestamps in Pandas-UDFs: pandas-Time-Series-Funktionalität nutzen.

---

## 3. Python UDTFs (Session-scoped)

Python-Klassen mit verpflichtender `eval`-Methode, die Ausgabezeilen per `yield` liefert.

```python
from pyspark.sql.functions import lit, udtf

@udtf(returnType="sum: int, diff: int")
class GetSumDiff:
    def eval(self, x: int, y: int):
        yield x + y, x - y

GetSumDiff(lit(1), lit(2)).show()
# Ergebnis: sum=3, diff=-1
```
- Feldnamen/-typen explizit über `returnType` angeben (sofern keine `analyze`-Methode definiert ist).

**Registrieren/aufrufen:**
```python
spark.udtf.register("get_sum_diff", GetSumDiff)
spark.sql("SELECT * FROM get_sum_diff(1,2);").show()
```
```sql
%sql
SELECT * FROM get_sum_diff(1,2);
-- Ergebnis: sum=3, diff=-1
```

- **Dateien mit einer UDTF generieren:** UDTF kann `FILE` als Eingabe nehmen und eine/mehrere neue `FILE`-Werte per `yield` zurückgeben (z. B. Video in Frames aufteilen).

**Zu Unity Catalog upgraden** (erfordert **DBR 18+**):
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
```

**Apache Arrow nutzen** — bei wenig Eingabe, aber großer Ausgabetabelle empfohlen (`useArrow=True`):
```python
@udtf(returnType="c1: int, c2: int", useArrow=True)
```

**Variable Argumentlisten** — `*args`/`**kwargs`:
```python
@udtf(returnType="sum: int, diff: int")
class GetSumDiff:
    def eval(self, *args):
        x, y = args[0], args[1]
        yield x + y, x - y

@udtf(returnType="sum: int, diff: int")
class GetSumDiffKw:
    def eval(self, **kwargs):
        x, y = kwargs["x"], kwargs["y"]
        yield x + y, x - y

GetSumDiffKw(x=lit(1), y=lit(2)).show()
# Ergebnis: sum=3, diff=-1
```

**Statisches vs. dynamisches Ausgabeschema**
- Statisch: `StructType` (`StructType().add("c1", StringType())`) oder DDL-String (`"c1: string"`) nach `@udtf`.
- Dynamisch (zur Aufrufzeit berechnet): statische Methode `analyze` nimmt Argumente des UDTF-Aufrufs entgegen.

`AnalyzeArgument`-Felder:

| Feld | Beschreibung |
|---|---|
| `dataType` | Typ des Eingabearguments; bei Table-Argumenten `StructType` der Spalten. |
| `value` | Wert (`Optional[Any]`); `None` bei Table-Argumenten/nicht-konstanten Literalen. |
| `isTable` | Ob Tabelle (`BooleanType`). |
| `isConstantExpression` | Ob konstant-auswertbar (`BooleanType`). |

`AnalyzeResult`-Felder:

| Feld | Beschreibung |
|---|---|
| `schema` | Schema der Ergebnistabelle (`StructType`). |
| `withSinglePartition` | Ob alle Eingabezeilen an dieselbe Instanz gehen (`BooleanType`). |
| `partitionBy` | Zeilen mit gleicher Wertekombination → separate Instanz. |
| `orderBy` | Zeilenreihenfolge innerhalb jeder Partition. |
| `select` | Ausdrücke, die die UDTF aus dem `TABLE`-Argument erhält (in angegebener Reihenfolge). |

```python
from pyspark.sql.functions import lit, udtf
from pyspark.sql.types import StructType, IntegerType
from pyspark.sql.udtf import AnalyzeArgument, AnalyzeResult

@udtf
class MyUDTF:
  @staticmethod
  def analyze(text: AnalyzeArgument) -> AnalyzeResult:
    schema = StructType()
    for index, word in enumerate(sorted(set(text.value.split(" ")))):
      schema = schema.add(f"word_{index}", IntegerType())
    return AnalyzeResult(schema=schema)

  def eval(self, text: str):
    counts = {}
    for word in text.split(" "):
      counts[word] = counts.get(word, 0) + 1
    yield [counts[w] for w in sorted(set(text.split(" ")))]
```

**Zustand von `analyze` an `eval` weitergeben:** über Subklasse von `AnalyzeResult`, deren Instanz `analyze` zurückgibt; `__init__` nimmt zusätzliches Argument zum Konsumieren entgegen.
```python
from dataclasses import dataclass
from pyspark.sql.udtf import AnalyzeResult

@dataclass
class AnalyzeResultWithBuffer(AnalyzeResult):
    buffer: str = ""

@udtf
class TestUDTF:
  def __init__(self, analyze_result=None):
    self._total = 0
    self._buffer = analyze_result.buffer if analyze_result is not None else ""

  @staticmethod
  def analyze(argument, _) -> AnalyzeResult:
    return AnalyzeResultWithBuffer(
      schema=StructType().add("total", IntegerType()).add("buffer", StringType()),
      withSinglePartition=True,
      buffer=argument.value,
    )

  def eval(self, argument, row):
    self._total += 1

  def terminate(self):
    yield self._total, self._buffer

spark.udtf.register("test_udtf", TestUDTF)
```

**Ausgabezeilen per `yield`:** `eval` läuft einmal pro Zeile des Table-Arguments (oder genau einmal ohne Table-Argument), gefolgt von einem abschließenden `terminate`-Aufruf. Beide geben null oder mehr Zeilen zurück (Tupel, Listen, `pyspark.sql.Row`):
```python
def eval(self, x, y, z):
  yield (x, y, z)        # Tupel
  yield x, y, z          # Klammern optional
  yield x,                # eine Spalte (Komma am Ende!)
  yield Row(x, y, z)     # Row-Objekt

def terminate(self):
  yield [self.x, self.y, self.z]  # Zustand aus vorangegangenen eval-Aufrufen
```

**Skalare Argumente:** konstante Ausdrücke (Literale oder darauf basierende Funktionen), auch benannt:
```sql
SELECT * FROM get_sum_diff(1, y => 2)
```

**Table-Argumente:** zusätzlich zu skalaren Argumenten (auch kombiniert). Übergabe via `TABLE(...)`: Tabellen-Identifikator (`TABLE(t)`) oder Subquery (`TABLE(SELECT a, b, c FROM t)`). Wird als `pyspark.sql.Row` an `eval` übergeben, ein Aufruf pro Zeile.
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
```sql
SELECT * FROM filter_udtf(TABLE(SELECT * FROM range(10)));
-- Ergebnis: id = 6, 7, 8, 9
```

**Partitionierung der Eingabezeilen über Funktionsaufrufe:**
- **`PARTITION BY <spalte-oder-ausdruck>`** nach dem `TABLE`-Argument: alle Zeilen mit eindeutiger Wertekombination gehen an genau eine UDTF-Instanz. Akzeptiert beliebige Ausdrücke (`LENGTH(a)`, Monatsextraktion, Verkettung).
- **`WITH SINGLE PARTITION`** statt `PARTITION BY`: genau eine Partition (eine Instanz verarbeitet alle Zeilen).
- **`ORDER BY`** nach `PARTITION BY`/`WITH SINGLE PARTITION`: erzwingt Zeilenreihenfolge innerhalb jeder Partition.
```sql
SELECT * FROM filter_udtf(TABLE(values_table) PARTITION BY a ORDER BY b) ORDER BY 1;
SELECT * FROM filter_udtf(TABLE(values_table) PARTITION BY LENGTH(a) ORDER BY b) ORDER BY 1;
SELECT * FROM filter_udtf(TABLE(values_table) WITH SINGLE PARTITION ORDER BY b) ORDER BY 1;
```

**Aus `analyze` heraus festlegen** (äquivalent zur SQL-Syntax, Aufrufer muss nichts angeben):
- `PARTITION BY a` in SQL ↔ `analyze` setzt `partitionBy=[PartitioningColumn("a")]`.
- `WITH SINGLE PARTITION ORDER BY b` ↔ `withSinglePartition=True`, `orderBy=[OrderingColumn("b")]`.
- `TABLE(SELECT a FROM t)` ↔ `select=[SelectedColumn("a")]`.
```python
@staticmethod
def analyze(*args) -> AnalyzeResult:
  from pyspark.sql.functions import AnalyzeResult, OrderingColumn, PartitioningColumn
  return AnalyzeResult(
    schema=StructType().add("month", DateType()).add("longest_word", IntegerType()),
    partitionBy=[PartitioningColumn("extract(month from date)")],
    orderBy=[OrderingColumn("date")],
    select=[SelectedColumn("date"), SelectedColumn(name="length(word)", alias="length_word")])
```

---

## 4. Session-scoped Scala- und Java-UDFs

| Ansatz | Beschreibung |
|---|---|
| **Inline Scala-UDF** | Direkt im Notebook. Session-scoped. **Nicht** auf Serverless Compute unterstützt. |
| **Java-UDF aus JAR** | Vorkompiliert, via `spark.udf.registerJavaFunction`. Session-scoped. Auf Serverless Compute unterstützt. |
| **UC-governed Scala/Java-UDF** | In Unity Catalog registriert (Governance, Wiederverwendung, Auffindbarkeit). Auf Serverless Compute unterstützt (siehe vorheriges Kapitel). |

- Scala-UDFs auf UC-fähigem Compute mit Standard Access Mode: **DBR 14.2+**.
- ARM-Instance-Support für Scala-UDFs auf UC-fähigen Clustern: **DBR 15.2+**.
- `spark.udf.registerJavaFunction` (Java-UDF aus JAR): **DBR 18 LTS+**.
- Versions-Matching: klassisches Compute — Scala-/Spark-Version müssen zur DBR passen (z. B. DBR 18 LTS = Scala 2.13.16 + Spark 4.0); serverloses Compute — Scala-Version muss zur Environment Version passen.

```sql
%sql select id, square(id) as id_squared from test
-- Ergebnis: id=4 -> id_squared=16
```

- **Dateien mit UDF (Beta):** Scala-Typ `FileRef`. Lesen: `asLocalFile()` (`java.io.File`) oder `open()` (`java.io.InputStream`, muss geschlossen werden). Erzeugen: `FileRef.create(uri)`, `FileRef.fromBytes(bytes, destinationPath, contentType)`, `FileRef.fromLocalFile(localFile, destinationPath, contentType)`. Eine `FileRef` aus einer UDF in eine `FILE MANAGED`-Spalte zurückgeben wird **nicht** unterstützt.

**Java-UDF aus einer JAR registrieren:**
1. Projekt anlegen (sbt/Maven, analog UC-Scala/Java-UDFs — JDK 17, `spark-sql` als `provided`).
2. UDF-Klasse schreiben — implementiert `org.apache.spark.sql.api.java.UDF1<In, Out>` (oder `UDF2` usw.):
```java
package com.example;
import org.apache.spark.sql.api.java.UDF1;
public class MyIntegerUDF implements UDF1<Integer, Integer> {
  @Override
  public Integer call(Integer x) { return x + 1; }
}
```
3. Fat-JAR bauen (`sbt clean assembly` / `mvn clean package`).
4. JAR in ein UC-Volume hochladen.
5. Registrieren/aufrufen:
```python
spark.addArtifact("/Volumes/my_catalog/my_schema/udf_jars/my-udf-assembly-0.1.0-SNAPSHOT.jar")
from pyspark.sql.types import IntegerType
spark.udf.registerJavaFunction("my_udf", "com.example.MyIntegerUDF", IntegerType())
spark.sql("SELECT my_udf(21)").show()
# Ergebnis: 22
```

**Auswertungsreihenfolge/Null-Prüfung:** wie bei Python-UDFs — keine Garantie; Lösung: null-aware UDF oder `IF`/`CASE WHEN`.

**Typisierte Dataset-APIs** (Standard Access Mode auf UC-fähigen Clustern ab **DBR 15.4**) — `map`, `filter`, Aggregationen mit benutzerdefinierter Funktion.
Gleiches Muster für `filter()`, `mapPartitions()`, `foreach()`, `foreachPartition()`, `reduce()`, `flatMap()`.

**Scala-UDF-Feature-Kompatibilität nach DBR-Version:**

| Feature | Minimale DBR-Version |
|---|---|
| Scalar UDFs | 14.2 |
| `Dataset.map`, `mapPartitions`, `filter`, `reduce`, `flatMap` | 15.4 |
| `KeyValueGroupedDataset.flatMapGroups`, `mapGroups` | 15.4 |
| (Streaming) `foreachWriter` Sink | 15.4 |
| (Streaming) `foreachBatch` | 16.1 |
| (Streaming) `KeyValueGroupedDataset.flatMapGroupsWithState` | 16.2 |
| `spark.udf.registerJavaFunction` (Java-UDF aus JAR) | 18 LTS |

---

## 5. Scala User-Defined Aggregate Functions (UDAFs)

Session-scoped, über `UserDefinedAggregateFunction`-API. Voraussetzung: **DBR 13.3 LTS+**, klassisches Compute mit **Dedicated Access Mode**.

| Methode/Feld | Zweck |
|---|---|
| `inputSchema` | Eingabefelder der Aggregatfunktion. |
| `bufferSchema` | Interne Felder für die Berechnung. |
| `dataType` | Ausgabetyp der Funktion. |
| `initialize` | Startwert des Buffer-Schemas. |
| `update` | Aktualisierung des Buffer-Schemas anhand einer Eingabe. |
| `merge` | Zusammenführung zweier Buffer-Objekte. |
| `evaluate` | Liefert finalen Wert aus finalem Buffer-Zustand. |

```sql
select group_id, gm(id) from simple group by group_id
```

---

## 6. Task-Kontext in einer UDF abrufen (`TaskContext`)

Liefert Kontextinformationen während der Ausführung einer **Batch-Unity-Catalog-Python-UDF** oder **PySpark-Scalar-UDF** — z. B. zur Verifikation der Nutzeridentität bei externem Dienstzugriff. Voraussetzung: ab **DBR 16.3**, für Batch-UC-Python-UDFs und Scalar-Python-UDFs.

**PySpark UDF:**
```python
@udf
def log_context():
  import json
  from pyspark.taskcontext import TaskContext
  tc = TaskContext.get()

  session_user = tc.getLocalProperty("user")
  tags = dict(item.values() for item in json.loads(
      tc.getLocalProperty("spark.databricks.clusterUsageTags.clusterAllTags") or "[]"))
  current_version = {
    "dbr_version": tc.getLocalProperty("spark.databricks.clusterUsageTags.sparkVersion"),
    "dbsql_version": tc.getLocalProperty("spark.databricks.clusterUsageTags.dbsqlVersion")
  }
  return {"user": session_user, "tags": tags, "current_version": current_version}
```

**Batch Unity Catalog Python UDF:**
```sql
CREATE OR REPLACE FUNCTION main.test.call_lambda_func(data STRING, debug BOOLEAN) RETURNS STRING LANGUAGE PYTHON
PARAMETER STYLE PANDAS
HANDLER 'batchhandler'
CREDENTIALS (`batch-udf-service-creds-example-cred` DEFAULT)
AS $$
import boto3, json, pandas as pd, base64
from pyspark.taskcontext import TaskContext

def batchhandler(it):
  session = boto3.Session()  # Nutzt automatisch das DEFAULT-Credential
  client = session.client("lambda", region_name="us-west-2")
  user_ctx = {"custom": {"user": TaskContext.get().getLocalProperty("user")}}  # in Lambda-Kontext propagiert

  for vals, is_debug in it:
    payload = json.dumps({"values": vals.to_list(), "is_debug": bool(is_debug[0])})
    res = client.invoke(
      FunctionName="HashValuesFunction",
      InvocationType="RequestResponse",
      ClientContext=base64.b64encode(json.dumps(user_ctx).encode("utf-8")).decode("utf-8"),
      Payload=payload,
    )
    response_payload = json.loads(res["Payload"].read().decode("utf-8"))
    if "errorMessage" in response_payload:
      raise Exception(str(response_payload))
    yield pd.Series(response_payload["values"])
$$;
```

`TaskContext.getLocalProperty()` — verfügbare Property-Schlüssel:

| Property-Schlüssel | Beschreibung | Beispielwert |
|---|---|---|
| `user` | Nutzer, der die UDF aktuell ausführt. | `"alice"` |
| `spark.jobGroup.id` | Mit der UDF verknüpfte Spark-Job-Group-ID. | `"jobGroup-92318"` |
| `spark.databricks.clusterUsageTags.clusterAllTags` | Cluster-Metadaten-Tags (String-Repräsentation eines JSON-Dictionarys). | `[{"Department": "Finance"}]` |
| `spark.databricks.clusterUsageTags.region` | Region des Workspace. | `"us-west-2"` |
| `accountId` | Databricks-Account-ID. | `"1234567890123456"` |
| `orgId` | Workspace-ID (auf DBSQL nicht verfügbar). | `"987654321"` |
| `spark.databricks.clusterUsageTags.sparkVersion` | DBR-Version des Clusters (Nicht-DBSQL). | `"16.3"` |
| `spark.databricks.clusterUsageTags.dbsqlVersion` | DBSQL-Version (DBSQL-Umgebungen). | `"2024.35"` |

**Stand:** 2026-09-14.
