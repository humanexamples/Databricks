# Unity Catalog UDFs

UDFs erweitern die eingebauten Spark-Fähigkeiten um wiederverwendbaren Code für komplexe Berechnungen/Transformationen.

- **UDF statt Spark-Funktion:** nur wenn sich die Logik mit eingebauten (verteilt optimierten) Spark-Funktionen schwer ausdrücken lässt — empfohlen für Ad-hoc-Queries, manuelle Datenbereinigung, explorative Analyse, kleine/mittlere Datensätze (Verschlüsselung, Hashing, JSON-Parsing, Validierung). Für große Datensätze / regelmäßige ETL-/Streaming-Workloads: eingebaute Spark-Methoden verwenden.

| UDF-Typ | Beschreibung |
|---|---|
| **Scalar UDFs** | Eine Zeile → ein Wert. Unity-Catalog-governed oder session-scoped. |
| **Batch Scalar UDFs** | Batches via Pandas-Iteratoren, 1:1-Zeilenparität — weniger Overhead, Zustand zwischen Batches möglich. |
| **Non-Scalar UDFs** | Flexibles Input/Output-Verhältnis (1:N, many:many), z. B. session-scoped Pandas-UDFs. |
| **UDAF** | Aggregiert mehrere Zeilen zu einem Ergebnis (`GROUP BY`). |
| **UDTFs** | Geben eine ganze Ergebnistabelle statt eines Skalarwerts zurück. |

```sql
CREATE OR REPLACE FUNCTION main.test.get_name_length(name STRING)
RETURNS INT
RETURN LENGTH(name);

SELECT name, main.test.get_name_length(name) AS name_length FROM your_table;
-- Ergebnis: name='Alice' -> name_length=5
```
```python
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

@udf(returnType=IntegerType())
def get_name_length(name):
  return len(name)

df = df.withColumn("name_length", get_name_length(df.name))
```

Dieses Kapitel: UDFs/UDTFs als **governed Objekte in Unity Catalog** (SQL/Python, Scala/Java, Batch-Python, Python-UDTFs) — katalogweit auffindbar/teilbar/über Privilegien steuerbar. Session-scoped UDFs (an `SparkSession` gebunden, nicht katalogweit governed) → nächstes Kapitel.

---

## 1. SQL- und Python-UDFs

- Python-Code in UC-UDFs: serverloses/Pro-SQL-Warehouse oder Cluster mit **DBR 13.3 LTS+**.
- View mit UC-Python-UDF schlägt auf **klassischen** SQL-Warehouses fehl.
- ARM-Instance-Support für Scala-UDFs auf UC-fähigen Clustern: ab **DBR 15.2**.

```sql
-- SQL-UDF
CREATE OR REPLACE FUNCTION my_catalog.my_schema.calculate_bmi(weight DOUBLE, height DOUBLE)
RETURNS DOUBLE
LANGUAGE SQL
RETURN SELECT weight / (height * height);

-- Python-UDF (äquivalent)
CREATE OR REPLACE FUNCTION my_catalog.my_schema.calculate_bmi(weight_kg DOUBLE, height_m DOUBLE)
RETURNS DOUBLE
LANGUAGE PYTHON
AS $$
return weight_kg / (height_m ** 2)
$$;

SELECT person_id, my_catalog.my_schema.calculate_bmi(weight_kg, height_m) AS bmi
FROM person_data;
-- Ergebnis: weight_kg=70, height_m=1.75 -> bmi=22.857...
```
```python
from pyspark.sql.functions import expr
result = df.withColumn("bmi", expr("my_catalog.my_schema.calculate_bmi(weight_kg, height_m)"))
```

**Custom Dependencies** — Voraussetzung: serverlose Notebooks/Jobs, klassisches Compute mit **DBR 16.2+**, oder Pro-/serverloses SQL-Warehouse. Quellen: PyPI-Pakete, Dateien in UC-Volumes (`READ VOLUME` nötig), Dateien unter öffentlichen URLs (Netzwerkregeln müssen Zugriff erlauben).

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.mixed_process(data STRING)
RETURNS STRING
LANGUAGE PYTHON
ENVIRONMENT (
  dependencies = '["simplejson==3.19.3", "/Volumes/my_catalog/my_schema/my_volume/packages/custom_package-1.0.0.whl", "https://my-bucket.s3.amazonaws.com/packages/special_package-2.0.0.whl?Expires=..."]',
  environment_version = '3'
)
AS $$
import simplejson as json
import custom_package
return json.dumps(custom_package.process(data))
$$;
```
- `dependencies`: kommagetrennt, pip-Requirements-Format je Eintrag.
- `environment_version`: feste Python-Version + vorinstallierte Pakete, unabhängig von DBR — Werte `None` oder ≥`3`; ≠`None` nur auf serverlosem Compute/SQL-Warehouses.

**Session-scoped → Unity-Catalog-UDF Upgrade:**
```python
# Session-scoped
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

@udf(StringType())
def greet(name):
    return f"Hello, {name}!"
```
```sql
-- Äquivalente Unity-Catalog-UDF
CREATE OR REPLACE FUNCTION my_catalog.my_schema.greet(name STRING)
RETURNS STRING
LANGUAGE PYTHON
AS $$
return f"Hello, {name}!"
$$
```

**Governance:** Zugriffskontrollen des Katalogs/Schemas regeln Berechtigungen; Vergabe bevorzugt über Databricks-SQL-/Workspace-UI (UDF → "Permissions" → `EXECUTE`/`MANAGE`).
```sql
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.calculate_bmi TO `user@example.com`;
REVOKE EXECUTE ON FUNCTION my_catalog.my_schema.calculate_bmi FROM `user@example.com`;
```

**Environment Isolation**
- Shared Isolation Environments erfordern **DBR 18.0+**; davor laufen alle UC-Python-UDFs im Strict-Isolation-Modus.
- Standard: UDFs mit gleichem Owner/gleicher Session **teilen** eine Isolation Environment (bessere Performance, weniger Speicher).
- `STRICT ISOLATION` erzwingt eigene, vollständig isolierte Umgebung — nötig bei `eval()`/`exec()`, Dateisystem-Schreibzugriff, globaler/Systemzustand-Änderung, Umgebungsvariablen-Zugriff.

```sql
CREATE OR REPLACE TEMPORARY FUNCTION run_python_snippet(python_code STRING)
RETURNS STRING
LANGUAGE PYTHON
STRICT ISOLATION
AS $$
import sys
from io import StringIO
captured_output = StringIO()
sys.stdout = captured_output
exec(python_code, {})
return captured_output.getvalue()
$$
```

**`DETERMINISTIC`** — setzen, wenn gleiche Eingabe stets gleiche Ausgabe liefert (erlaubt Ergebnis-Caching). Standard: Batch-UC-Python-UDFs gelten als **nicht-deterministisch**, sofern nicht anders deklariert (nicht-deterministisch z. B. bei Zufallswerten, aktueller Uhrzeit, externen API-Aufrufen).

```sql
-- Externe API
CREATE FUNCTION my_catalog.my_schema.get_food_calories(food_name STRING)
RETURNS DOUBLE
LANGUAGE PYTHON
AS $$
import requests
response = requests.get(f"https://example-food-api.com/nutrition?food={food_name}")
if response.status_code == 200:
   return response.json().get('calories', 0)
return None
$$;
```
```sql
-- Datenmaskierung (E-Mail) + View für kontrollierten Zugriff
CREATE OR REPLACE FUNCTION my_catalog.my_schema.mask_email(email STRING)
RETURNS STRING
LANGUAGE PYTHON
DETERMINISTIC
AS $$
parts = email.split('@', 1)
if len(parts) == 2:
  username, domain = parts
else:
  return None
masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
return f"{masked_username}@{domain}"
$$;
-- Ergebnis: mask_email('john.doe@example.com') -> 'j****************e@example.com'

CREATE OR REPLACE VIEW my_catalog.my_schema.masked_customer_view AS
SELECT id, name, my_catalog.my_schema.mask_email(email) AS masked_email
FROM my_catalog.my_schema.customer_data;
```

- KI-Agenten können UC-UDFs als **Tools** nutzen.
- **Best Practice:** dedizierter Katalog/Schema mit passenden Zugriffskontrollen (bzw. dediziertes Schema im Team-Katalog für teamspezifische UDFs); im Docstring: Versionsnummer, Changelog, Zweck/Parameter/Rückgabewert, Beispielnutzung dokumentieren.

**Zeitzonenverhalten bei Timestamp-Inputs** — ab **DBR 18.0**: `TIMESTAMP`-Werte an Python-UDFs bleiben UTC, aber das `datetime`-Objekt hat **keine `tzinfo` mehr** (Angleichung an Arrow-optimierte Python-UDFs in Apache Spark).

```sql
CREATE FUNCTION timezone_udf(date TIMESTAMP)
RETURNS STRING
LANGUAGE PYTHON
AS $$
return f"{type(date)} {date} {date.tzinfo}"
$$;
-- Vor DBR 18.0: ... 2024-10-23 10:30:00+00:00 Etc/UTC
-- Ab DBR 18.0:  ... 2024-10-23 10:30:00+00:00 None
```
- Zeitzone explizit wiederherstellen: `date = date.replace(tzinfo=timezone.utc)`.

**Limitierungen:**
- Beliebig viele interne Python-Funktionen, aber alle müssen **skalar** zurückgeben.
- Python-Funktionen müssen `NULL` selbst behandeln; Typ-Mappings folgen den Databricks-SQL-Sprach-Mappings.
- Ohne Katalog-/Schema-Angabe: Registrierung im aktuell aktiven Schema.
- Laufen in sicherer isolierter Umgebung — kein Zugriff auf Dateisysteme/interne Dienste.
- **Maximal 5 UDF-Aufrufe pro Query.**

---

## 2. Scala- und Java-UDFs

Governed, reusable (team-/notebook-/job-/SQL-Warehouse-übergreifend), discoverable (Catalog Explorer, System Tables), isolated (Sandbox mit einmaligem Cold-Start pro Session).

- **Scala 2.13.16** (2.12 nicht unterstützt); **JDK 17**.
- Packaging: **Fat-JAR** mit allen Drittanbieter-Abhängigkeiten.
- Berechtigungen: erstellen → `USAGE`+`CREATE FUNCTION` auf Schema, `USAGE` auf Katalog; ausführen → `EXECUTE` auf Funktion, `USAGE` auf Schema/Katalog; JAR-Zugriff → `READ VOLUME`.
- Handler: Scala als Methode auf einem `object` (nicht `class`); Java als `public static`-Methode. Parametertypen/-reihenfolge/Rückgabetyp müssen `CREATE FUNCTION` entsprechen.
- **Nur skalar** — genau ein Rückgabewert, keine Tabellen-Rückgabe.
- **Self-contained** — nur Eingabeargumente, **keine** Spark-APIs/Spark-Core-Abhängigkeit.

```java
package com.example;
public class MyUDF {
    public static int addOne(int x) { return x + 1; }
}
```

Build: Scala `sbt clean assembly` (`sbt-assembly`); Java `mvn clean package` (`maven-shade-plugin`) → JAR hochladen in UC-Volume (Catalog Explorer → Volume → "Upload to this volume" → "Copy path"). Alternativ: einfache Java-Handler direkt im Python-Notebook kompilieren/packen (`javac`/`jar` als Subprozesse, dann Kopie ins Volume).

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.add_one(x INT)
RETURNS INT
LANGUAGE SCALA
DETERMINISTIC
ENVIRONMENT (
  java_dependencies = '["/Volumes/my_catalog/my_schema/udf_jars/my-udf-assembly-0.1.0-SNAPSHOT.jar"]',
  environment_version = '4'
)
HANDLER 'com.example.MyUDF.addOne';
-- analog LANGUAGE JAVA, gleiches HANDLER-Format paket.Klasse.methode

SELECT my_catalog.my_schema.add_one(5) AS result;
-- Ergebnis: result = 6

SELECT id, price, currency, my_catalog.my_schema.convert_to_usd(price, currency) AS price_usd
FROM my_catalog.my_schema.transactions;
```
```sql
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.add_one TO `data-engineers`;
REVOKE EXECUTE ON FUNCTION my_catalog.my_schema.add_one FROM `data-engineers`;
```
- UDFs auffinden über `system.information_schema.routines`.
- **Aktualisieren:** Code ändern → JAR mit neuer Version bauen → ins Volume hochladen → `CREATE OR REPLACE FUNCTION` mit aktualisiertem `java_dependencies`-Pfad.

**Performance:**
- Cold-Start-Latenz nur beim ersten Aufruf pro Session (Sandbox-Init) — bei Benchmarks berücksichtigen.
- Teure Berechnungen außerhalb des Handlers (auf `object`-/Klassenebene) einmalig cachen.
- `DETERMINISTIC` setzen, wenn zutreffend.

**Limitierungen:**
- Nur **skalar** — **keine** UDAFs, **keine** UDTFs.
- Läuft in isolierter Sandbox **ohne aktive Spark-Session** — keine `SparkSession`/`SparkContext`/`spark.sql(...)`/DataFrame-Ops.
- Keine Spark-Core-Abhängigkeit.
- Kein Laufzeitzugriff auf Workspace-Dateien/UC-Volumes.

Best Practices: JAR-Versionierung (`my-udf-0.1.0.jar` …); SQL-Typ-Mappings vor Deployment validieren; `READ VOLUME`/`EXECUTE` nur an tatsächliche Nutzer, Gruppen-Ownership teamübergreifend. Lokal testen: Scala mit ScalaTest (`sbt test`), Java mit JUnit 5 (`mvn test`) direkt gegen Handler-Methoden.

---

## 3. Batch Python UDFs

Verarbeiten Zeilen-**Batches** statt Einzelzeilen, garantierte **1:1-Input/Output-Zeilenparität**. Erfordern **DBR 16.3+**.

`PARAMETER STYLE PANDAS`: Verarbeitung in Batches über Pandas-Iteratoren; `HANDLER 'name'` benennt die Verarbeitungsfunktion.

```sql
CREATE OR REPLACE TEMPORARY FUNCTION calculate_bmi_pandas(weight_kg DOUBLE, height_m DOUBLE)
RETURNS DOUBLE
LANGUAGE PYTHON
DETERMINISTIC
PARAMETER STYLE PANDAS
HANDLER 'handler_function'
AS $$
import pandas as pd
from typing import Iterator, Tuple

def handler_function(batch_iter: Iterator[Tuple[pd.Series, pd.Series]]) -> Iterator[pd.Series]:
  for weight_series, height_series in batch_iter:
    yield weight_series / (height_series ** 2)
$$;
```

Handler-Funktion:
1. Akzeptiert Iterator über eine/mehrere `pandas.Series` (je eine pro UDF-Parameter, pro Batch).
2. Iteriert/verarbeitet die Daten.
3. `yield`et pro Batch eine `pandas.Series` **gleicher Länge** wie Input (1:1-Parität).

```sql
-- Ein Parameter
CREATE OR REPLACE TEMPORARY FUNCTION one_parameter_udf(value INT)
RETURNS STRING
LANGUAGE PYTHON DETERMINISTIC PARAMETER STYLE PANDAS HANDLER 'handler_func'
AS $$
import pandas as pd
from typing import Iterator
def handler_func(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
  for value_batch in batch_iter:
    d = {"min": value_batch.min(), "max": value_batch.max()}
    yield pd.Series([str(d)] * len(value_batch))
$$;
-- Zwei Parameter: Iterator liefert Tupel von Series in Argumentreihenfolge
-- for p1, p2 in batch_iter: yield p1 + p2
```

Custom Dependencies: wie in Abschnitt 1 (`ENVIRONMENT(dependencies=..., environment_version=...)`).

**Performance:** Code **außerhalb** der Handler-Funktion (Modulebene) läuft nur **einmal pro Isolation Environment**, nicht pro Batch:
```sql
CREATE OR REPLACE TEMPORARY FUNCTION expensive_computation_udf(value INT)
RETURNS INT
LANGUAGE PYTHON DETERMINISTIC PARAMETER STYLE PANDAS HANDLER 'handler_func'
AS $$
def compute_value():
  return 1  # expensive computation...
expensive_value = compute_value()
def handler_func(batch_iter):
  for batch in batch_iter:
    yield batch * expensive_value
$$;
```

**Environment Isolation:** Shared Isolation Environments erfordern **DBR 17.1+** (sonst Strict-Isolation-Modus für alle Batch-UC-Python-UDFs); Standard-Verarbeitungs-UDFs profitieren von geteilter Isolation. `STRICT ISOLATION` bei denselben Mustern wie Abschnitt 1.

**Service Credentials:**
```sql
CREATE OR REPLACE TEMPORARY FUNCTION example_udf(data STRING)
RETURNS STRING
LANGUAGE PYTHON PARAMETER STYLE PANDAS HANDLER 'handler_function'
CREDENTIALS (
  `credential-name` DEFAULT,
  `complicated-credential-name` AS short_name,
  `simple-cred`,
  cred_no_quotes
)
AS $$
# Python code here
$$;
```
- **Ersteller** braucht `ACCESS` auf dem UC-Service-Credential; **Aufrufer** genügt `EXECUTE` auf der UDF (läuft mit Creator-Credential-Berechtigungen). Bei temporären Funktionen ist Ersteller = Aufrufer; auf No-PE-Scope-("dedicated")-Clustern gelten Aufrufer-Berechtigungen.
```python
from databricks.service_credentials import getServiceCredentialsProvider
import boto3
# Bei CREDENTIALS(`aws-cred` AS testcred):
boto3_session = boto3.Session(botocore_session=getServiceCredentialsProvider('testcred'))
```
- Praxisbeispiel: Batch-UDF ruft via `DEFAULT`-Credential eine AWS-Lambda-Funktion auf, propagiert `TaskContext`-Infos (z. B. Nutzeridentität) in den Lambda-Kontext.
- Task-Kontext: siehe Kapitel "Session-scoped UDFs, Pandas UDFs und UDTFs" → Abschnitt "UDF Task Context".

`DETERMINISTIC`: wie Abschnitt 1 — Batch-UDFs/UDTFs standardmäßig nicht-deterministisch.

**Limitierung:** Batch-UDF-Aufrufe auf serverlosem Notebook-/Job-Compute erfordern konfigurierte **Serverless Egress Control**.

---

## 4. Python UDTFs

Geben eine **ganze Ergebnistabelle** statt eines Skalarwerts zurück. Einsatz: Arrays/komplexe Strukturen in mehrere Zeilen transformieren; externe APIs/Dienste in SQL-Workflows; benutzerdefinierte Datengenerierung/-anreicherung; zustandsbehaftete Verarbeitung über mehrere Zeilen.

Zwei Registrierungsarten: **Unity Catalog** (governed, dieser Abschnitt) und **Session-scoped** (siehe nächstes Kapitel).

Voraussetzung: serverlose Notebooks/Jobs; klassisches Compute mit Standard Access Mode (**DBR 17.1+**); SQL-Warehouse (serverlos/Pro).

```sql
CREATE OR REPLACE FUNCTION square_numbers(start INT, end INT)
RETURNS TABLE (num INT, squared INT)
LANGUAGE PYTHON
HANDLER 'SquareNumbers'
DETERMINISTIC
AS $$
class SquareNumbers:
    def eval(self, start: int, end: int):
        for num in range(start, end + 1):
            yield (num, num * num)
$$;

SELECT * FROM square_numbers(1, 5);
-- Ergebnis:
-- num | squared
-- 1   | 1
-- 2   | 4
-- 3   | 9
-- 4   | 16
-- 5   | 25
```

**Table-Argumente** (ab **DBR 17.2**): komplexe zustandsbehaftete Transformationen/Aggregationen über ganze Tabellen als Eingabe.

Lifecycle-Methoden:
- **`eval()`** (Pflicht): einmal pro **Zeile** der Eingabetabelle — zentrale Verarbeitung.
- **`terminate()`** (optional): einmal am **Ende jeder Partition** nach allen `eval()`-Aufrufen — finale aggregierte Ergebnisse/Aufräumarbeiten; essenziell für Aggregationen/Zählungen/Batch-Verarbeitung.

`eval()` erhält `TABLE`-Zeilen als `pyspark.sql.Row` — Zugriff per Name (`row['id']`) oder Index (`row[0]`). `TABLE`-Argumente ohne Schema deklarierbar (`data TABLE`) — Funktion akzeptiert dann jede Struktur (Code sollte Spalten prüfen).

**Polymorphe UDTFs (dynamisches Ausgabeschema):** Handler-Klasse implementiert `@staticmethod analyze()` (gleiche Argumente wie UDTF) → gibt `AnalyzeResult` (Ausgabeschema) zurück; Databricks ruft sie zur **Query-Planungszeit** auf.

```sql
CREATE OR REPLACE FUNCTION extract_fields(json_str STRING, fields STRING)
RETURNS TABLE
LANGUAGE PYTHON
HANDLER 'ExtractFields'
AS $$
class ExtractFields:
    @staticmethod
    def analyze(json_str, fields):
        from pyspark.sql.types import StructType, StructField, StringType
        from pyspark.sql.udtf import AnalyzeResult
        col_names = [f.strip() for f in fields.value.split(",")]
        return AnalyzeResult(
            StructType([StructField(name, StringType()) for name in col_names])
        )

    def eval(self, json_str: str, fields: str):
        import json
        data = json.loads(json_str)
        col_names = [f.strip() for f in fields.split(",")]
        yield tuple(data.get(name) for name in col_names)
$$;
```
- **Warnung:** bei UC-polymorphen UDTFs müssen alle Imports **innerhalb des Methodenkörpers** von `analyze()` stehen — Top-Level-Imports funktionieren in der Sandbox nicht.

`AnalyzeArgument` (Parameter von `analyze`):

| Feld | Beschreibung |
|---|---|
| `dataType` | Typ des Eingabearguments; bei Table-Argumenten ein `StructType` der Spalten. |
| `value` | Wert des Arguments (`Optional[Any]`); `None` bei Table-Argumenten/nicht-konstanten Ausdrücken. |
| `isTable` | Ob Table-Argument (`BooleanType`). |
| `isConstantExpression` | Ob konstant-auswertbar (`BooleanType`). |

`AnalyzeResult` (Rückgabe von `analyze`):

| Feld | Beschreibung |
|---|---|
| `schema` | Schema der Ergebnistabelle (`StructType`). |
| `withSinglePartition` | `True`: alle Eingabezeilen an dieselbe UDTF-Instanz. |
| `partitionBy` | Zeilen nach Ausdrücken partitioniert, je eindeutiger Kombination eigene Instanz. |
| `orderBy` | Zeilenreihenfolge innerhalb jeder Partition. |
| `select` | Welche Spalten des Eingabe-`TABLE`-Arguments die UDTF erhält. |

- Zustand von `analyze` an `eval` weiterreichen: über Konstruktor `__init__(self, result)`.
- Bei Table-Argument steuert `analyze()` via `partitionBy`/`orderBy`/`withSinglePartition`/`select` die Zeilenverteilung — Aufrufer brauchen dann kein `PARTITION BY`/`ORDER BY` in SQL.

**Environment Isolation:** `STRICT ISOLATION` wie in Abschnitt 1, bei `eval`/`exec`, Dateisystem-Schreibzugriff, globaler/Umgebungsvariablen-Manipulation.

`DETERMINISTIC`: wie andere UDF-Typen — Standard nicht-deterministisch.

**Praxismuster:**
- **`explode` neu implementieren:** `eval()` iteriert Array-Argument, gibt jedes Element als eigene Zeile aus — einsetzbar mit `LATERAL`.
- **IP-Geolokalisierung über REST-API:** `eval()` ruft pro Zeile externe API auf, gibt Ergebnisfelder zurück (`LATERAL`-Join gegen Log-Tabelle).
- **IP-Adressen gegen CIDR-Netzblöcke matchen:** `__init__` lädt einmalig pro Partition eine Liste von `ipaddress.ip_network`-Objekten; `eval()` matcht pro Zeile — Aufruf: `FROM ip_cidr_matcher(t => TABLE(ip_logs))`.
- **Batch-Bildbeschriftung über Vision-Endpoint:** `eval()` puffert Zeilen bis Batch-Größe erreicht; `terminate()` verarbeitet letzten unvollständigen Batch und gibt gesammelte Ergebnisse aus — inkl. optionaler expliziter `PARTITION BY ... ORDER BY (...)`.
- **ROC-Kurve/AUC (ML-Evaluierung):** nutzt scikit-learn, akkumuliert alle Zeilen in `eval()` (zustandsbehaftete Aggregation über gesamten Datensatz), berechnet Metriken erst in `terminate()`; validiert Spalten, wirft `KeyError` bei fehlenden Feldern.
- **Dynamische Spaltenprojektion:** `analyze()` liest Eingabeschema aus `t.dataType`, gibt nur angeforderte Spalten als Ausgabeschema zurück; `eval()` projiziert entsprechend.

**Limitierungen:** Unity-Catalog-**Service-Credentials nicht unterstützt**; **Custom Dependencies nicht unterstützt**.

**Stand:** 2026-09-14.
