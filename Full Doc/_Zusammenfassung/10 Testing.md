# 11 Testing — Gesamtübersicht

Konsolidierte Übersicht aller 28 Original-Markdown-Dateien im Ordner `11 Testing\` (Unit Test, Integrationstest, CI-CD, Git Workflow, Andere Themen) mit **allen** enthaltenen Code-Beispielen und einer kurzen, einfachen Einführung pro Thema. Jede Originaldatei bleibt die primäre, ausführliche Quelle — dieses Dokument dient als kompakter Überblick plus vollständige Code-Referenz an einem Ort.

Das Kapitel folgt der klassischen Testpyramide (Unit Test → Integrationstest) plus zwei Delivery-Themen (CI/CD, Git Workflow) und einer Restkategorie für angrenzende Themen (ML-Lifecycle, MLOps, Python-Entwicklung, allgemeine Best Practices). Ein Teil der Inhalte besteht aus kuratierten Zusammenfassungen von Databricks-Blogartikeln statt aus offizieller Referenzdokumentation.

## Inhaltsverzeichnis

**Unit Test** (1–13): 1. Überblick — 2. Notebook-Testing Grundlagen — 3. Python-Unit-Tests im Workspace (UI) — 4. Testing mit Databricks Connect — 5. pytest in der VS-Code-Extension — 6. Notebook Workflows als Testing-Orchestrierung (Legacy) — 7. Notebook Best Practices — 8. PySpark-Testing-Utilities und Praxisbeispiel — 9. pytest — Grundlagen und Referenz — 10. chispa — PySpark-Testbibliothek — 11. nutter — Databricks-Notebook-Testing — 12. unittest — Python-Standardbibliothek-Referenz — 13. assertDataFrameEqual/assertSchemaEqual (API-Referenz)

**Integrationstest** (14–16): 14. Lakeflow Pipelines Unit Testing — 15. Integrationstest-Konzepte auf Databricks — 16. SDP-Integrationstest-Patterns (Praxisbeispiel)

**CI-CD** (17–18): 17. CI/CD Best Practices — 18. Blog: CI/CD-Praxisbeispiele und Software-Engineering-Kultur

**Git Workflow** (19–22): 19. Jobs mit Git-Quellcode — 20. Blog: Repos-Historie und Features — 21. Blog: Asset Bundles und Git-Workflows (Ankündigungen) — 22. Blog: Lakebase Database Branching

**Andere Themen** (23–28): 23. ML-Lifecycle — 24. MLOps-Workflow — 25. Python-Entwicklung auf Databricks — 26. Allgemeine Developer Best Practices — 27. Blog: MLOps, DataOps und KI-gestützte Entwicklung — 28. dbx (Legacy, archiviert)

**Ergänzungen** (29–30): 29. Blog: Python-Abhängigkeitsverwaltung in Spark Connect — 30. Pandas API on Spark: DataFrame-/Series-/Index-Gleichheitsfunktionen

---

## 1. Überblick über das Testing-Kapitel

**Einfach erklärt:** Dieses Kapitel sammelt alles rund um das Testen von Notebooks, Lakeflow-Pipelines und ML-Workflows auf Databricks, plus die dazugehörige CI/CD- und Git-Workflow-Kultur. Die Gliederung folgt der Testpyramide (Unit → Integration) plus den zwei explizit angefragten Delivery-Themen (CI/CD, Git Workflow) und einer Restkategorie für Inhalte, die im Kontext relevant sind, aber keiner Hauptkategorie eindeutig zuzuordnen sind (ML-Lifecycle, allgemeine Developer-Best-Practices, Python-Entwicklung).

Ein Teil der ursprünglich angefragten Themen deckt sich mit bereits ausführlich dokumentierten Inhalten im Developers-Kapitel und wurde dort nicht dupliziert:

- Git Folders / Repos-Setup, Git-Operationen, CI/CD über Repos → Developers/Git Folders (Repos)
- CI/CD-Grundlagen, -Workflows, GitHub Actions, Azure DevOps, Jenkins → Developers/CI-CD
- Bundles im Workspace (Web-UI) → Developers/Databricks Asset Bundles

---

## 2. Notebook-Testing Grundlagen

**Einfach erklärt:** Unit Testing bedeutet, kleine, in sich geschlossene Code-Einheiten (Funktionen) früh und häufig zu testen. Für Databricks-Notebooks empfiehlt sich, Funktionen und Tests bei Python/R **außerhalb** von Notebooks zu halten (bessere Wiederverwendbarkeit, externe Test-Frameworks), während bei Scala Funktionen und Tests in getrennten Notebooks bleiben (kein externer Speicherort unterstützt) und SQL-Funktionen als UDFs in Schemas gespeichert werden. Wichtige Best Practice: **nicht** gegen Produktionsdaten testen, sondern synthetische Testdaten oder Views nutzen.

**Testing-Frameworks je Sprache:**

| Sprache | Framework | Konvention |
|---|---|---|
| Python | pytest | Dateien mit Präfix `test_` |
| R | testthat | Dateien mit Präfix `test` |
| Scala | ScalaTest (FunSuite-Stil) | — |
| SQL | `SELECT`-Statements mit bedingter Logik | — |

**Praktisches Testmuster 1 — `unittest` direkt im Notebook:**

```python
def reverse(s):
    return s[::-1]

import unittest

class TestHelpers(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('abc'), 'cba')

r = unittest.main(argv=[''], verbosity=2, exit=False)
assert r.result.wasSuccessful(), 'Test failed; see logs above'
```

**Praktisches Testmuster 2 — Widgets für Test-/Normal-Modus:**

```python
dbutils.widgets.dropdown("Mode", "Test", ["Test", "Normal"])

def reverse(s):
    return s[::-1]

if dbutils.widgets.get('Mode') == 'Test':
    assert reverse('abc') == 'cba'
    print('Tests passed')
else:
    print(reverse('desrever'))
```

**Testcode über `%run` auslagern** (dediziertes Test-Notebook getrennt vom Code-Notebook):

`shared-code-notebook`:
```python
def reverse(s):
    return s[::-1]
```

`shared-code-notebook-test` (Zelle 1):
```python
%run ./shared-code-notebook
```

`shared-code-notebook-test` (Zelle 2):
```python
import unittest

class TestHelpers(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('abc'), 'cba')

r = unittest.main(argv=[''], verbosity=2, exit=False)
assert r.result.wasSuccessful(), 'Test failed; see logs above'
```

Weitere wichtige Punkte: Fehler bleiben sichtbar, selbst wenn Zell-Ergebnisse per „Hide Result" ausgeblendet sind. Geplante Notebooks können Tests periodisch automatisiert ausführen und bei Fehlschlag benachrichtigen. Für Code in Git-Repositories lassen sich Tests direkt aus Notebooks oder dem Web Terminal ausführen — kombinierbar mit GitHub-Actions-Trigger bei jedem Commit.

---

## 3. Python-Unit-Tests im Workspace (UI)

**Einfach erklärt:** Databricks bietet direkt im Workspace integrierte Tools, um Python-Unit-Tests zu entdecken, auszuführen und nachzuverfolgen — ganz ohne externe Test-Runner aufzurufen: eine Testing-Sidebar, Inline-Run-Icons neben jedem Testfall und ein dediziertes Ergebnis-Panel. Erkannt werden Dateien nach pytest-Konvention (`test_*.py`, `*_test.py`) sowie Funktionen/Methoden, die mit „test" beginnen.

**Beispielstruktur, die erkannt wird:**

```python
class TestClass():    
    def test_1(self):        
        assert True    
    def test_3(self):        
        assert 4 == 3

def test_foo():    
    assert "foo" == "bar"
```

In der Sidebar lassen sich alle Tests, alle fehlgeschlagenen Tests oder einzelne Tests per Klick ausführen, nach Name/Status filtern; bei Fehlschlägen erscheint ein Inline-Fehlerindikator mit vollständiger Fehlermeldung im Modal. Der „Testing"-Tab im unteren Panel zeigt eine vollständige Zusammenfassung des letzten Laufs. Hinweis: Das Tests-Icon erscheint nur, wenn die Datei aktiv im Editor-Tab und nicht im Read-only-Modus ist; in Pipelines/Bundles/Git-Folder-Bereichen mit angehängtem Cluster umfasst die Erkennung alle Dateien im Ordner.

---

## 4. Testing mit Databricks Connect

**Einfach erklärt:** Mit Databricks Connect (Databricks Runtime 13.3 LTS+) lässt sich PySpark-Code **lokal** mit pytest testen — der Code läuft auf der eigenen Maschine, aber die `SparkSession` verbindet sich mit einem Remote-Cluster. Wichtig: Databricks Connect und PySpark dürfen sich in der Entwicklungsumgebung nicht gegenseitig blockieren („schließen sich gegenseitig aus"); beim Ausführen über das Terminal funktioniert pytest nur mit dem `DEFAULT`-Konfigurationsprofil, das eine Compute-Ressource (Cluster oder Serverless) angeben muss.

**`nyctaxi_functions.py`:**
```python
from databricks.connect import DatabricksSession
from pyspark.sql import DataFrame, SparkSession

def get_spark() -> SparkSession:
  spark = DatabricksSession.builder.getOrCreate()
  return spark

def get_nyctaxi_trips() -> DataFrame:
  spark = get_spark()
  df = spark.read.table("samples.nyctaxi.trips")
  return df
```

**`main.py`:**
```python
from nyctaxi_functions import *

df = get_nyctaxi_trips()
df.show(5)
```

**`test_nyctaxi_functions.py`:**
```python
import pyspark.sql.connect.session
from nyctaxi_functions import *

def test_get_spark():
  spark = get_spark()
  assert isinstance(spark, pyspark.sql.connect.session.SparkSession)

def test_get_nyctaxi_trips():
  df = get_nyctaxi_trips()
  assert df.count() > 0
```

**Ausführung vom Projekt-Root:**
```
$ pytest
=================== test session starts ====================
platform darwin -- Python 3.11.7, pytest-8.1.1, pluggy-1.4.0
rootdir: <project-rootdir>
collected 2 items
test_nyctaxi_functions.py .. [100%]
======================== 2 passed ==========================
```

---

## 5. pytest in der VS-Code-Extension

**Einfach erklärt:** Die Databricks-IDE-Extension bietet zwei Wege, Python-Code zu testen: **pytest** direkt gegen einen Remote-Cluster (gut für Funktionen, die PySpark-DataFrames im lokalen Speicher entgegennehmen/zurückgeben) oder **Databricks Connect** für lokales Testen mit vollen Spark-APIs.

**Methode 1 — pytest:** Testdatei mit pytest-Fixture (SparkSession auf dem Remote-Cluster) anlegen, einen separaten Runner (`pytest_databricks.py`) erstellen, der Dateien nach `_test.py`-Muster durchsucht, eine eigene VS-Code-Run-Konfiguration einrichten (`launch.json` mit angepasstem `program`/`args`), dann über „Start Debugging" ausführen.

Beispiel-`launch.json`-Werte: `"program": "${workspaceFolder}/pytest_databricks.py"`, `"args": ["."]`.

**Methode 2 — Databricks Connect:** Setup wie in Abschnitt 4, Testdatei mit Standard-pytest-Syntax:

```python
def test_find_all_taxis():
    taxis = main.find_all_taxis()
    assert taxis.count() > 5
```

Eine debugpy-basierte Launch-Konfiguration benötigt das Feld `"databricks": true`. Wichtig: „Das bloße Ausführen des Tests löst die angepasste Debug-Konfiguration nicht aus" — nur über den Debug-Ansatz funktioniert die Databricks-Connect-Anbindung.

---

## 6. Notebook Workflows als Testing-Orchestrierung (Legacy-Beispiel)

**Einfach erklärt:** Eine alte, nicht mehr erreichbare Beispielseite demonstrierte, wie man mit `dbutils.notebook.run()` ein „Driver-Notebook" baut, das mehrere Test-Notebooks ausführt und deren Erfolg/Fehlschlag aggregiert. Die Seite leitet heute auf die aktuelle Doku zu „Notebook workflows" um — dieses Muster ist die technische Grundlage für notebook-basierte Test-Orchestrierung.

**Kernkonzept:** `run(path: String, timeout_seconds: int, arguments: Map): String` startet einen neuen, ephemeren Job. Argumente und Rückgabewerte müssen Strings sein; der `arguments`-Parameter setzt Widget-Werte im Ziel-Notebook und akzeptiert nur ASCII-Zeichen. Rückgabewerte über `dbutils.notebook.exit()` — davon lässt sich nur **ein einzelner String** zurückgeben; für strukturierte Daten gibt es drei Ansätze: Global-Temporary-View, DBFS-Storage-Pfad oder JSON-Serialisierung. Fehler werfen eine `WorkflowException`, die sich mit Standard-Try-Catch für Retry-Logik abfangen lässt. Mehrere Notebooks lassen sich über Threads/Futures nebenläufig orchestrieren — die technische Basis für paralleles Driver-Notebook-Testing.

---

## 7. Notebook Best Practices (Software Engineering)

**Einfach erklärt:** Professionelle Entwicklungspraktiken für Notebooks anhand eines COVID-Analyse-Beispiels: Notebooks mit Git Folders verbinden und über Branches getrennt vom `main`-Branch arbeiten; wiederverwendbare Funktionen in gemeinsame Module extrahieren statt monolithischer Notebooks; Abhängigkeiten explizit über `requirements.txt` deklarieren; gemeinsam genutzten Code **separat vom Notebook** testen (Fehler im Shared Code sollten zuerst erkannt werden, bevor das Haupt-Notebook fehlschlägt); Ausführung über Jobs statt manueller Läufe automatisieren; GitHub-Actions-Workflows für automatisiertes Testen bei Merges nutzen.

**Beispielmodul `covid_analysis/transforms.py`** mit vier Funktionen: `filter_country()`, `pivot_and_clean()`, `clean_spark_cols()`, `index_to_col()`.

**Empfohlene Repository-Struktur:**

```
├── covid_analysis/
│   └── transforms.py
├── notebooks/
│   ├── covid_eda_modular
│   ├── covid_eda_raw (optional)
│   └── run_unit_tests
├── requirements.txt
└── tests/
    ├── testdata.csv
    └── transforms_test.py
```

Wichtige Sicherheitsempfehlung: „Aus Sicherheitsgründen rät Databricks davon ab, den persönlichen Access Token des Workspace-Nutzers an GitHub weiterzugeben. Stattdessen einen einem Service-Principal zugeordneten Databricks-Access-Token nutzen."

---

## 8. PySpark-Testing-Utilities und Praxisbeispiel

**Einfach erklärt:** `pyspark.testing.utils` liefert die offiziellen Hilfsfunktionen `assertDataFrameEqual` und `assertSchemaEqual` zur Gleichheitsprüfung von DataFrames bzw. Schemas. Es gibt drei kombinierbare Testing-Optionen. Alle nutzen dieselben `pyspark.testing`-Funktionen: nur die Built-in-Utilities für Ad-hoc-Validierung, `unittest` für ein vollwertiges Framework, oder `pytest` mit Fixtures.

**Beispiel `assertDataFrameEqual`:**
```python
from pyspark.sql.functions import col, when

def add_new_col(df, new, s_col):
 return (df
         .withColumn(new,                        
            when(col(s_col) == 0, 'Normal')                            
            .otherwise('Unknown')))

def test_add_new_col():
   data = [(0,), (1,), (-1,),(None,)]
   columns = ["value"]
   df = spark.createDataFrame(data, columns)

   actual_df = add_new_col(df, "new_value", "value")

   expected_data = [(0, 'Normal'), (1, 'Unknown'),
                    (-1, 'Unknown'), (None, 'Unknown')]
   expected_df = spark.createDataFrame(expected_data,
                                       ["value", "new_value"])

   assertDataFrameEqual(actual_df, expected_df)
```

**Näherungsweise Gleichheit mit `rtol`:**
```python
df1 = spark.createDataFrame(data=[("1", 0.1), ("2", 3.23)], schema=["id", "amount"])
df2 = spark.createDataFrame(data=[("1", 0.109), ("2", 3.23)], schema=["id", "amount"])
assertDataFrameEqual(df1, df2, rtol=1e-1)  # besteht, DataFrames sind bis auf rtol gleich
```

**Beispiel `assertSchemaEqual`:**
```python
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType, LongType
from pyspark.sql.functions import when, col
from pyspark.testing.utils import assertSchemaEqual

def test_get_health_csv_schema_match():
    actual_schema = project_functions.get_health_csv_schema()
    expected_schema = StructType([
        StructField("ID", IntegerType(), True),
        StructField("PII", StringType(), True),
        StructField("Age", DoubleType(), True)
    ])
    assertSchemaEqual(actual_schema, expected_schema)
    print('Test passed!')

test_get_health_csv_schema_match()
```

**Einfache Assertion ohne PySpark-Testing-Utility:**
```python
def test_uppercase_columns_function():
    data = [(1, 5.0, 1, 1, 1, 1)]
    columns = ["id", "trip_distance", "My_Column", "WithNumbers123", "WithSymbolX@#", "With Space"]
    df = spark.createDataFrame(data, columns)

    actual_df = transforms.uppercase_columns_names(df)
    actual_columns = actual_df.columns

    expected_columns = ['ID', 'TRIP_DISTANCE', 'MY_COLUMN', 'WITHNUMBERS123', 'WITHSYMBOLX@#', "WITH SPACE"]

    assert actual_columns == expected_columns
    print('Test Passed!')

test_uppercase_columns_function()
```

**`unittest` als Alternative zu pytest** — Transformationsfunktion:
```python
from pyspark.sql.functions import col, regexp_replace

def remove_extra_spaces(df, column_name):
    df_transformed = df.withColumn(column_name, regexp_replace(col(column_name), "\\s+", " "))
    return df_transformed
```

Basisklasse mit klassenweitem Setup/Teardown:
```python
import unittest

class PySparkTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder.appName("Testing PySpark Example").getOrCreate()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()
```

Tests als Methoden der abgeleiteten Klasse:
```python
from pyspark.testing.utils import assertDataFrameEqual

class TestTranformation(PySparkTestCase):
    def test_single_space(self):
        sample_data = [{"name": "John    D.", "age": 30},
                       {"name": "Alice   G.", "age": 25},
                       {"name": "Bob  T.", "age": 35},
                       {"name": "Eve   A.", "age": 28}]

        original_df = spark.createDataFrame(sample_data)
        transformed_df = remove_extra_spaces(original_df, "name")

        expected_data = [{"name": "John D.", "age": 30},
        {"name": "Alice G.", "age": 25},
        {"name": "Bob T.", "age": 35},
        {"name": "Eve A.", "age": 28}]
        expected_df = spark.createDataFrame(expected_data)

        assertDataFrameEqual(transformed_df, expected_df)
```

Ausführung im Notebook statt Kommandozeile:
```python
unittest.main(argv=[''], verbosity=0, exit=False)
```
```
Ran 1 test in 1.734s

OK
```

**pytest ausführen:**
```python
!pip install pytest==8.3.4
%load_ext autoreload
%autoreload 2
```
```python
import pytest
import sys

sys.dont_write_bytecode = True

retcode = pytest.main(["./tests_lab/lab_unit_test_solution.py", "-v", "-p", "no:cacheprovider"])

assert retcode == 0, "The pytest invocation failed. See the log for details."
```

**Vollständiges Praxisbeispiel: Health-Datensatz** (`test_spark_helper_functions.py`, session-scoped Fixture + drei Tests):

```python
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType, LongType
from pyspark.sql.functions import when, col
from pyspark.testing.utils import assertDataFrameEqual, assertSchemaEqual

from src.helpers import project_functions


@pytest.fixture(scope="session")
def spark():
    spark = SparkSession.builder.getOrCreate()
    yield spark


def test_get_health_csv_schema_match():
    expected_schema = StructType([
        StructField("ID", IntegerType(), True),
        StructField("PII", StringType(), True),
        StructField("date", DateType(), True),
        StructField("HighCholest", IntegerType(), True),
        StructField("HighBP", DoubleType(), True),
        StructField("BMI", DoubleType(), True),
        StructField("Age", DoubleType(), True),
        StructField("Education", DoubleType(), True),
        StructField("income", IntegerType(), True)
    ])
    actual_schema = project_functions.get_health_csv_schema()
    assertSchemaEqual(actual_schema, expected_schema)


def test_high_cholest_column_valid_map(spark):
    data = [
        (0,),
        (1,), 
        (2,), 
        (3,), 
        (4,), 
        (None,)
    ]
    sample_df = spark.createDataFrame(data, ["value"])

    actual_df = sample_df.withColumn("actual", project_functions.high_cholest_map("value"))

    expected_df = spark.createDataFrame(
        [
            (0, "Normal"),
            (1, "Above Average"),
            (2, "High"),
            (3, "Unknown"),
            (4, "Unknown"),
            (None, "Unknown")
        ],
        schema=StructType([
            StructField("value", LongType(), True),
            StructField("actual", StringType(), True)
        ])
    )

    assertDataFrameEqual(actual_df.select(col('actual')), expected_df.select(col('actual')))


def test_age_group_column_valid_map(spark):
    data = [
        (0,),
        (9,), 
        (10,), 
        (20,), 
        (30,), 
        (40,),
        (50,), 
        (60,),
        (-1,), 
        (None,)
    ]
    sample_df = spark.createDataFrame(data, ["value"])

    actual_df = sample_df.withColumn("actual", project_functions.group_ages_map("value"))

    data = [
        (0, "0-9"),
        (9, "0-9"),
        (10, "10-19"),
        (20, "20-29"),
        (30, "30-39"),
        (40, "40-49"),
        (50, "50+"),
        (60, "50+"),
        (-1, "Unknown"),
        (None, "Unknown")  # Nullwert
    ]

    schema = StructType([
        StructField("value", LongType(), True),
        StructField("actual", StringType(), True)
    ])

    expected_df = spark.createDataFrame(data, schema)

    assertDataFrameEqual(actual_df.select(col('actual')), expected_df.select(col('actual')))
```

---

## 9. pytest — Grundlagen und Referenz

**Einfach erklärt:** `pytest` ist das im Projekt bevorzugte Test-Framework für PySpark-Code. Kernfunktionen: detaillierte Fehlerinfos bei fehlgeschlagenen `assert`-Statements (ohne `self.assert*`-Namen wie bei `unittest`), Auto-Discovery von Test-Modulen/-Funktionen ohne manuelle Registrierung, modulare Fixtures zur Ressourcenverwaltung (z. B. SparkSession), Unterstützung für bestehende `unittest`-Suiten, Kompatibilität mit Python 3.10+/PyPy 3, über 1.300 externe Plugins.

**Minimalbeispiel:**
```python
def inc(x):
    return x + 1

def test_answer():
    assert inc(3) == 5
```

Bei Ausführung schlägt dieser Test mit einer detaillierten Ausgabe fehl (`assert 4 == 5`).

---

## 10. chispa — PySpark-Testbibliothek

**Einfach erklärt:** „Chispa" (Community-Bibliothek, nicht offiziell von Databricks/Apache Spark) liefert Assertion-Funktionen für PySpark-DataFrames mit besonders lesbaren, farblich hervorgehobenen Diffs im Fehlerfall — eine Alternative/Ergänzung zu `pyspark.testing.utils`.

**Installation:**
```bash
pip install chispa
```
```bash
poetry add chispa --group dev
```

**Spalten-Gleichheit:**
```python
from chispa import assert_column_equality

def test_remove_non_word_characters_short():
    data = [
        ("jo&&se", "jose"),
        ("**li**", "li"),
        ("#::luisa", "luisa"),
        (None, None)
    ]
    df = (spark.createDataFrame(data, ["name", "expected_name"])
        .withColumn("clean_name", remove_non_word_characters(F.col("name"))))
    assert_column_equality(df, "clean_name", "expected_name")
```

**DataFrame-Gleichheit:**
```python
from chispa import assert_df_equality

def test_remove_non_word_characters_long():
    source_data = [
        ("jo&&se",),
        ("**li**",),
        ("#::luisa",),
        (None,)
    ]
    source_df = spark.createDataFrame(source_data, ["name"])

    actual_df = source_df.withColumn(
        "clean_name",
        remove_non_word_characters(F.col("name"))
    )

    expected_data = [
        ("jo&&se", "jose"),
        ("**li**", "li"),
        ("#::luisa", "luisa"),
        (None, None)
    ]
    expected_df = spark.createDataFrame(expected_data, ["name", "clean_name"])

    assert_df_equality(actual_df, expected_df)
```

**Vergleichsoptionen für `assert_df_equality`:**

| Option | Wirkung |
|---|---|
| `ignore_row_order=True` | Zeilenreihenfolge wird beim Vergleich ignoriert |
| `ignore_column_order=True` | Spaltenreihenfolge wird ignoriert |
| `ignore_columns=[...]` | angegebene Spalten werden vom Vergleich ausgeschlossen |
| `ignore_nullable=True` | Nullability-Unterschiede im Schema werden ignoriert |
| `ignore_metadata=True` | Schema-Metadaten-Unterschiede werden übergangen |
| `transforms=[...]` | wendet Vorverarbeitungsschritte auf beide DataFrames an |
| `underline_cells=True` | hebt abweichende Zellen zusätzlich hervor |
| `allow_nan_equality=True` | behandelt `NaN == NaN` als gleich |

```python
assert_df_equality(df1, df2, ignore_row_order=True)
assert_df_equality(df1, df2, ignore_column_order=True)
assert_df_equality(df1, df2, ignore_columns=["clean_name"])
assert_df_equality(df1, df2, ignore_nullable=True)
```

**Näherungsweise Gleichheit (Floats):**
```python
def test_approx_col_equality_same():
    data = [
        (1.1, 1.1),
        (2.2, 2.15),
        (3.3, 3.37),
        (None, None)
    ]
    df = spark.createDataFrame(data, ["num1", "num2"])
    assert_approx_column_equality(df, "num1", "num2", 0.1)
```
```python
def test_approx_df_equality_same():
    data1 = [(1.1, "a"), (2.2, "b"), (3.3, "c"), (None, None)]
    df1 = spark.createDataFrame(data1, ["num", "letter"])

    data2 = [(1.05, "a"), (2.13, "b"), (3.3, "c"), (None, None)]
    df2 = spark.createDataFrame(data2, ["num", "letter"])

    assert_approx_df_equality(df1, df2, 0.1)
```

**Eigenes Ausgabeformat:**
```python
from chispa import FormattingConfig

formats = FormattingConfig(
    mismatched_rows={"color": "light_yellow"},
    matched_rows={"color": "cyan", "style": "bold"},
    mismatched_cells={"color": "purple"},
    matched_cells={"color": "blue"},
)

assert_basic_rows_equality(df1.collect(), df2.collect(), formats=formats)
```
```python
from chispa import FormattingConfig, Color, Style

formats = FormattingConfig(
    mismatched_rows={"color": Color.LIGHT_YELLOW},
    matched_rows={"color": Color.CYAN, "style": Style.BOLD},
    mismatched_cells={"color": Color.PURPLE},
    matched_cells={"color": Color.BLUE},
)
```

**Voraussetzungen:** Python `>=3.10,<4.0`; getestet gegen PySpark 3.5.x, 4.0.x, 4.1.x.
```bash
poetry install
poetry run pytest tests
```

---

## 11. nutter — Databricks-Notebook-Testing

**Einfach erklärt:** Microsofts Open-Source-Framework testet ganze Databricks-**Notebooks** (statt einzelner Python-Funktionen wie pytest/unittest) — nutzt intern `dbutils.notebook.run()`, führt das zu testende Notebook aus und prüft anschließend Assertions gegen dessen Ergebnisse. Besteht aus zwei Komponenten: **Nutter Runner** (serverseitig, auf dem Cluster) und **Nutter CLI** (clientseitig, für Laptops/Build-Agents).

**`NutterFixture`-Klasse:**
```python
from runtime.nutterfixture import NutterFixture, tag
class MyTestFixture(NutterFixture):
    def run_test_name(self):
        dbutils.notebook.run('notebook_under_test', 600, args)

    def assertion_test_name(self):
        some_tbl = sqlContext.sql('SELECT COUNT(*) AS total FROM sometable')
        first_row = some_tbl.first()
        assert (first_row[0] == 1)
```

**Lifecycle-Präfixe:** `before_`, `run_`, `assertion_` (erforderlich), `after_`; zusätzlich `before_all()`/`after_all()` auf Fixture-Ebene.

**Tests im Notebook ausführen:**
```python
result = MyTestFixture().execute_tests()
print(result.to_string())
result.exit(dbutils)
```

**Installation:** Cluster-seitig als PyPI-Bibliothek; CLI:
```bash
pip install nutter
```

**Umgebungsvariablen (Linux):**
```bash
export DATABRICKS_HOST=<HOST>
export DATABRICKS_TOKEN=<TOKEN>
```
**Windows PowerShell:**
```powershell
$env:DATABRICKS_HOST="HOST"
$env:DATABRICKS_TOKEN="TOKEN"
```

**CLI-Befehle:**
```bash
nutter list /dataload
nutter list /dataload --recursive
```
```bash
nutter run dataload/test_sourceLoad --cluster_id 0123-12334-tonedabc \
  --notebook_params "{\"example_key_1\": \"example_value_1\"}"
```
```bash
nutter run dataload/src* --cluster_id 0123-12334-tonedabc \
  --notebook_params "{\"example_key_1\": \"example_value_1\"}"
```
```bash
nutter run dataload/ --cluster_id 0123-12334-tonedabc --recursive
```
```bash
nutter run dataload/ --cluster_id 0123-12334-tonedabc \
  --recursive --max_parallel_tests 2
```

**Fortgeschrittene Muster — mehrere Assertions ohne `run_`:**
```python
class MultiTestFixture(NutterFixture):
    def before_all(self):
        dbutils.notebook.run('notebook_under_test', 600, args)

    def assertion_test_case_1(self):
        ...

    def assertion_test_case_2(self):
        ...
```

**Paralleler Fixture-Runner:**
```python
from runtime.runner import NutterFixtureParallelRunner

parallel_runner = NutterFixtureParallelRunner(num_of_workers=2)
parallel_runner.add_test_fixture(CustomerTestFixture())
parallel_runner.add_test_fixture(CountryTestFixture())

result = parallel_runner.execute()
print(result.to_string())
```

**Geteilter State zwischen Tests:**
```python
class TestFixture(NutterFixture):
    def __init__(self):
        self.file = '/data/myfile'
        NutterFixture.__init__(self)
```

Ausführungsreihenfolge: Tests laufen alphabetisch sortiert (sortiertes Dictionary).

**CLI-Flags (`run`):**

| Flag | Bedeutung |
|---|---|
| `--timeout` | Ausführungs-Timeout in Sekunden (Standard: 120) |
| `--junit_report` | erzeugt einen JUnit-XML-Report |
| `--tags_report` | erzeugt einen CSV-Report mit Test-Tags |
| `--max_parallel_tests` | maximale Anzahl gleichzeitiger Testausführungen |
| `--recursive` | führt Tests in der gesamten Ordnerhierarchie aus |
| `--poll_wait_time` | Polling-Intervall in Sekunden (Standard: 5) |
| `--notebook_params` | übergibt Parameter, abrufbar via `dbutils.widgets.get('key')` |

**Azure-DevOps-Integration:**
```yaml
- script: |
    pip install nutter
  displayName: 'Install Nutter'

- script: |
    nutter run /Shared/ $CLUSTER --recursive --junit_report
  displayName: 'Execute Nutter'
  env:
      CLUSTER: $(clusterID)
      DATABRICKS_HOST: $(databricks_host)
      DATABRICKS_TOKEN: $(databricks_token)

- task: PublishTestResults@2
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: '**/test-*.xml'
```

Die CLI beendet sich bei Testfehlschlägen mit Exit-Code ≠ 0 — die Pipeline erkennt Fehlschläge automatisch.

---

## 12. unittest — Python-Standardbibliothek-Referenz

**Einfach erklärt:** `unittest` ist Pythons eingebautes, von JUnit inspiriertes Test-Framework. Kernbegriffe: **Test Fixture** (Setup/Cleanup für einen oder mehrere Tests), **Test Case** (eine einzelne Testeinheit über `TestCase`), **Test Suite** (Sammlung von Testfällen), **Test Runner** (orchestriert Ausführung und Ergebnisdarstellung).

**Minimalbeispiel:**
```python
import unittest

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
```

**Setup/Teardown pro Testmethode:**
```python
import unittest

class WidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.widget = Widget('The widget')

    def tearDown(self):
        self.widget.dispose()

    def test_default_widget_size(self):
        self.assertEqual(self.widget.size(), (50, 50),
                         'incorrect default size')

    def test_widget_resize(self):
        self.widget.resize(100, 150)
        self.assertEqual(self.widget.size(), (100, 150),
                         'wrong size after resize')
```

**Setup/Teardown pro Klasse:**
```python
class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass
```

**Wichtige Assert-Methoden (Auswahl):** `assertEqual`, `assertNotEqual`, `assertTrue`, `assertFalse`, `assertIs`, `assertIsNone`, `assertIn`, `assertIsInstance`, `assertRaises`, `assertWarns`, `assertLogs`, `assertAlmostEqual`, `assertGreater`, `assertRegex`, `assertCountEqual`, `assertListEqual`, `assertDictEqual` u. v. m.

```python
self.assertRaises(ValueError, int, 'xyz')

with self.assertRaises(ValueError):
    int('xyz')

with self.assertRaises(ValueError) as cm:
    int('xyz')
the_exception = cm.exception
self.assertEqual(the_exception.args[0], "...")
```

**Tests überspringen:**
```python
class MyTestCase(unittest.TestCase):

    @unittest.skip("demonstrating skipping")
    def test_nothing(self):
        self.fail("shouldn't happen")

    @unittest.skipIf(mylib.__version__ < (1, 3),
                     "not supported in this library version")
    def test_format(self):
        pass

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_windows_support(self):
        pass
```

**Erwarteter Fehlschlag:**
```python
class ExpectedFailureTestCase(unittest.TestCase):
    @unittest.expectedFailure
    def test_fail(self):
        self.assertEqual(1, 0, "broken")
```

**Test-Discovery:**
```bash
cd project_directory
python -m unittest discover
python -m unittest discover -s project_directory
python -m unittest discover -p "*_test.py"
```

**Kommandozeile:**
```bash
python -m unittest test_module1 test_module2
python -m unittest test_module.TestClass.test_method
python -m unittest -v test_module
python -m unittest -k foo
```

**Async-Tests (`IsolatedAsyncioTestCase`):**
```python
from unittest import IsolatedAsyncioTestCase

class Test(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._async_connection = await AsyncConnection()

    async def test_response(self):
        response = await self._async_connection.get("https://example.com")
        self.assertEqual(response.status_code, 200)

    async def asyncTearDown(self):
        await self._async_connection.close()
```

**Zusammenfassungstabelle:**

| Feature | Nutzung |
|---|---|
| Basis-Test | `TestCase` erweitern, `test_*`-Methoden definieren |
| Setup/Teardown | `setUp()`, `tearDown()` (je Test) |
| Klassen-Setup | `setUpClass()`, `tearDownClass()` (je Klasse) |
| Assertions | 60+ `assert*()`-Methoden |
| Test überspringen | `@skip()`, `@skipIf()`, `@skipUnless()`, `skipTest()` |
| Erwarteter Fehlschlag | `@expectedFailure` |
| Subtests | `with self.subTest(...)` |
| Test-Discovery | `python -m unittest discover` |

---

## 13. assertDataFrameEqual und assertSchemaEqual (API-Referenz)

**Einfach erklärt:** Vollständige Parameter- und Beispiel-Referenz der beiden zentralen `pyspark.testing`-Funktionen, direkt aus dem Docstring der Referenzimplementierung (`pyspark/testing/utils.py`).

**`assertDataFrameEqual`-Signatur (seit Spark 3.5.0):**
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

Wichtigste Parameter: `checkRowOrder` (Standard `False` = Reihenfolge wird ignoriert), `rtol`/`atol` (relative/absolute Toleranz für Float-Näherungsgleichheit: `absolute(a - b) <= (atol + rtol * absolute(b))`), `ignoreNullable`/`ignoreColumnOrder`/`ignoreColumnName`/`ignoreColumnType` (seit 4.0.0), `maxErrors`, `showOnlyDiff`, `includeDiffRows`. Hinweis: `ignoreColumnOrder` und `ignoreColumnName` dürfen **nicht gleichzeitig** `True` sein.

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
>>> assertDataFrameEqual(df1, df2)
```

**Fehlschlag mit Diff-Ausgabe:**
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

**`ignoreNullable`:**
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
```

**`ignoreColumnOrder`:**
```python
>>> df1_col_order = spark.createDataFrame(
...     data=[(1000, "1"), (5000, "2")], schema=["amount", "id"]
... )
>>> df2_col_order = spark.createDataFrame(
...     data=[("1", 1000), ("2", 5000)], schema=["id", "amount"]
... )
>>> assertDataFrameEqual(df1_col_order, df2_col_order, ignoreColumnOrder=True)
```

**`ignoreColumnName`:**
```python
>>> df1_col_names = spark.createDataFrame(
...     data=[(1000, "1"), (5000, "2")], schema=["amount", "identity"]
... )
>>> df2_col_names = spark.createDataFrame(
...     data=[(1000, "1"), (5000, "2")], schema=["amount", "id"]
... )
>>> assertDataFrameEqual(df1_col_names, df2_col_names, ignoreColumnName=True)
```

**`ignoreColumnType`:**
```python
>>> df1_col_types = spark.createDataFrame(
...     data=[(1000, "1"), (5000, "2")], schema=["amount", "id"]
... )
>>> df2_col_types = spark.createDataFrame(
...     data=[(1000.0, "1"), (5000.0, "2")], schema=["amount", "id"]
... )
>>> assertDataFrameEqual(df1_col_types, df2_col_types, ignoreColumnType=True)
```

**`maxErrors`** (meldet nur die erste abweichende Zeile):
```python
>>> df1 = spark.createDataFrame([(1, "A"), (2, "B"), (3, "C")])
>>> df2 = spark.createDataFrame([(1, "A"), (2, "X"), (3, "Y")])
>>> assertDataFrameEqual(df1, df2, maxErrors=1)
```

**`showOnlyDiff`:**
```python
>>> assertDataFrameEqual(df1, df2, showOnlyDiff=True)
```

**`includeDiffRows`:**
```python
>>> try:
...     assertDataFrameEqual(df1, df2, includeDiffRows=True)
... except PySparkAssertionError as e:
...     spark.createDataFrame(e.data).show()
```

**`assertSchemaEqual`-Signatur (seit Spark 3.5.0):**
```python
def assertSchemaEqual(
    actual: StructType,
    expected: StructType,
    ignoreNullable: bool = True,
    ignoreColumnOrder: bool = False,
    ignoreColumnName: bool = False,
)
```

**Grundlegende Gleichheit:**
```python
>>> from pyspark.sql.types import StructType, StructField, ArrayType, IntegerType, DoubleType
>>> s1 = StructType([StructField("names", ArrayType(DoubleType(), True), True)])
>>> s2 = StructType([StructField("names", ArrayType(DoubleType(), True), True)])
>>> assertSchemaEqual(s1, s2)  # pass, schemas are identical
```

**Vergleich ohne Spaltenreihenfolge/-namen:**
```python
>>> s1 = StructType(
...     [StructField("a", IntegerType(), True), StructField("b", DoubleType(), True)]
... )
>>> s2 = StructType(
...     [StructField("b", DoubleType(), True), StructField("a", IntegerType(), True)]
... )
>>> assertSchemaEqual(s1, s2, ignoreColumnOrder=True)
```
```python
>>> s1 = StructType(
...     [StructField("a", IntegerType(), True), StructField("c", DoubleType(), True)]
... )
>>> s2 = StructType(
...     [StructField("b", IntegerType(), True), StructField("d", DoubleType(), True)]
... )
>>> assertSchemaEqual(s1, s2, ignoreColumnName=True)
```

---

## 14. Lakeflow Pipelines Unit Testing

**Einfach erklärt:** Das offizielle **Beta**-Testing-Framework für Lakeflow Declarative Pipelines validiert Transformationslogik mit Mock-Daten — isoliert über eine Test-`SparkSession`, die Tabellenoperationen in ein temporäres Test-Schema umleitet. Verfügbar ausschließlich über den webbasierten Lakeflow Pipelines Editor.

**Voraussetzungen:** Pipeline-Owner-Berechtigung, `USE CATALOG`/`CREATE SCHEMA`-Rechte, **Triggered**-Pipeline-Modus (nicht kontinuierlich), Pipeline auf **PREVIEW**-Channel, kein Spark Connect.

```sql
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG <catalog_name> TO `<principal>`;
```

**Kritische Isolationsgrenzen:** nur Tabellennamen-Umleitung — Pfad-basierte Reads/Writes (`/Volumes/...`, `dbfs:/`, `s3://`) und Connector-Operationen (Kafka, Auto Loader) umgehen die Isolation. `event_log()` liefert Produktionsdaten, nicht Test-Logs — stattdessen `event_log_table_name` aus dem Run-Status über `test_spark` abfragen.

**Nicht unterstützte Governance-Operationen:** `GRANT`, `REVOKE`, `ALTER ... OWNER TO`, `SET`/`UNSET TAGS`, `CREATE`/`DROP POLICY`, `CREATE`/`DROP CATALOG`/`SCHEMA`.

**Pipeline-Einstellungen (JSON):**
```json
"continuous": false,
"channel": "PREVIEW"
```

**Erforderliche Imports:**
```python
import pytest
from pyspark.pipelines.testing import TestPipeline, test_spark

test_pipeline = TestPipeline.active()
```

**Testing-APIs:**

| API | Beschreibung |
|---|---|
| `TestPipeline.active()` | gibt das `TestPipeline`-Objekt der aktuellen Pipeline zurück |
| `test_pipeline.run(test_spark, set([table_names]))` | selektiver Refresh der angegebenen Tabellen |
| `test_spark`-Fixture | SparkSession mit namensbasierter Tabellen-Umleitung |

**Mock-Daten — SQL-basiert:**
```python
test_spark.sql("""
    CREATE TABLE catalog.schema.table_name AS
    SELECT * FROM VALUES
        (1, 'value1'),
        (2, 'value2')
    AS t(id, name)
""")
```

**Mock-Daten — DataFrame-basiert:**
```python
df = test_spark.createDataFrame(
    [(1, 'value1'), (2, 'value2')],
    schema=["id", "name"])
df.write.saveAsTable("catalog.schema.table_name")
```

**Synthetische Daten mit Faker:**
```python
from pyspark.sql import functions as F
from faker import Faker

fake = Faker()
fake_firstname = F.udf(fake.first_name)
fake_lastname = F.udf(fake.last_name)
fake_email = F.udf(fake.ascii_company_email)

df = (
    test_spark.range(0, 100)
    .withColumn("firstname", fake_firstname())
    .withColumn("lastname", fake_lastname())
    .withColumn("email", fake_email()))
df.write.saveAsTable("catalog.schema.table_name")
```

**Ausführliches Beispiel: Aggregations-Testing:**
```python
import pytest
from pyspark.pipelines.testing import TestPipeline, test_spark
from pyspark.testing import assertDataFrameEqual

test_pipeline = TestPipeline.active()

def mock_users(session):
    session.sql("""
        CREATE TABLE catalog.schema.wanderbricks_users AS
        SELECT * FROM VALUES
            (1, 'alice@example.com', 'Alice', 'admin'),
            (2, NULL, 'Bob', 'user'),
            (3, 'charlie@example.com', 'Charlie', 'user'),
            (4, NULL, 'Dana', 'admin')
        AS t(user_id, email, name, user_type)
    """)

def test_users_row_count(test_spark):
    mock_users(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.users"]))
    result = test_spark.table("catalog.schema.users")
    assert result.count() == 4

def test_users_schema(test_spark):
    mock_users(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.users"]))
    result = test_spark.table("catalog.schema.users")
    expected_fields = {"user_id", "email", "name", "user_type"}
    actual_fields = set(f.name for f in result.schema.fields)
    assert expected_fields == actual_fields

def test_users_null_handling(test_spark):
    mock_users(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.users"]))
    result = test_spark.table("catalog.schema.users")
    null_emails = result.filter("email IS NULL").count()
    assert null_emails == 2

def test_counts(test_spark):
    mock_users(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.users", "catalog.schema.counts"]))
    result = test_spark.table("catalog.schema.counts")
    admin_row = result.filter("user_type = 'admin'").collect()[0]
    user_row = result.filter("user_type = 'user'").collect()[0]
    assert admin_row["total_count"] == 2
    assert admin_row["count_valid_emails"] == 1
    assert user_row["total_count"] == 2
    assert user_row["count_valid_emails"] == 1

def test_counts_full_dataframe(test_spark):
    mock_users(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.users", "catalog.schema.counts"]))
    result = test_spark.table("catalog.schema.counts")
    expected = test_spark.createDataFrame(
        [("admin", 2, 1), ("user", 2, 1)],
        schema=["user_type", "total_count", "count_valid_emails"]
    )
    assertDataFrameEqual(result, expected)
```

**Auto-CDC-Testing — Standard-Flow:**
```python
def test_auto_cdc_flow(test_spark):
    test_spark.sql("""
        CREATE TABLE catalog.schema.change_feed AS
        SELECT * FROM VALUES
            (1, 'Alice', 1000),
            (2, 'Bob', 1001),
            (1, 'Alice Updated', 1002)
        AS t(userId, name, ts)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.target_autocdc"]))
    result = test_spark.table("catalog.schema.target_autocdc")
    user_ids = set(row["userId"] for row in result.collect())
    assert user_ids == {1, 2}
    latest_user1 = result.filter("userId = 1").collect()[0]
    assert latest_user1["ts"] == 1002
    assert latest_user1["name"] == "Alice Updated"
    user2 = result.filter("userId = 2").collect()[0]
    assert user2["ts"] == 1001
```

**Verspätet eintreffende Events:**
```python
def test_auto_cdc_late_arriving(test_spark):
    test_spark.sql("""
        CREATE TABLE catalog.schema.change_feed AS
        SELECT * FROM VALUES
            (1, 'Alice', 1000),
            (2, 'Bob', 1001)
        AS t(userId, name, ts)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.target_autocdc"]))
    test_spark.sql("""
        INSERT INTO catalog.schema.change_feed VALUES
            (1, 'Alice Updated', 1003),
            (2, 'Bob (stale)', 999)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.target_autocdc"]))
    result = test_spark.table("catalog.schema.target_autocdc")
    alice = result.filter("userId = 1").collect()[0]
    assert alice["ts"] == 1003
    assert alice["name"] == "Alice Updated"
    bob = result.filter("userId = 2").collect()[0]
    assert bob["ts"] == 1001
    assert bob["name"] == "Bob"
```

**CDC-aus-Snapshot:**
```python
def test_auto_cdc_from_snapshot_flow(test_spark):
    test_spark.sql("""
        CREATE TABLE catalog.schema.snapshot AS
        SELECT * FROM VALUES
            (1, 'Alice', '2024-01-01'),
            (2, 'Bob', '2024-01-02')
        AS t(userId, name, created_at)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.target"]))
    test_spark.sql("TRUNCATE TABLE catalog.schema.snapshot")
    test_spark.sql("INSERT INTO catalog.schema.snapshot VALUES (2, 'Bob', '2024-01-03')")
    test_pipeline.run(test_spark, set(["catalog.schema.target"]))
    result = test_spark.table("catalog.schema.target")
    assert result.count() == 3
    user_ids = [row["userId"] for row in result.collect()]
    assert set(user_ids) == {1, 2}
```

**Joins- und Expectations-Testing:**
```python
def mock_properties(session):
    session.sql("""
        CREATE TABLE catalog.schema.property_images AS
        SELECT * FROM VALUES
            (101, 'img1.jpg', '2024-02-01'),
            (102, 'img2.jpg', '2024-01-15'),
            (103, 'img3.jpg', '2024-12-20')
        AS t(property_id, image_url, uploaded_at)
    """)
    session.sql("""
        CREATE TABLE catalog.schema.property_amenities AS
        SELECT * FROM VALUES
            (101, 'wifi'),
            (102, 'pool'),
            (103, 'parking')
        AS t(property_id, amenity)
    """)

def test_property_join(test_spark):
    mock_properties(test_spark)
    test_pipeline.run(test_spark, set(["catalog.schema.property_images_amenities_join"]))
    result = test_spark.table("catalog.schema.property_images_amenities_join")
    assert result.count() == 3
    property_ids = set(row["property_id"] for row in result.collect())
    assert property_ids == {101, 102, 103}

def test_property_expectation(test_spark):
    mock_properties(test_spark)
    test_spark.sql("""
        INSERT INTO catalog.schema.property_images VALUES (104, 'img4.jpg', '2023-12-31')
    """)
    test_spark.sql("""
        INSERT INTO catalog.schema.property_amenities VALUES (104, 'gym')
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.property_images_amenities_join"]))
    result = test_spark.table("catalog.schema.property_images_amenities_join")
    valid_ids = set(row["property_id"] for row in result.collect())
    assert 104 not in valid_ids
    assert valid_ids == {101, 102, 103}
```

---

## 15. Integrationstest-Konzepte auf Databricks

**Einfach erklärt:** Databricks hat keine einzelne, dedizierte „Integrationstest"-Dokumentationsseite — die Konzepte sind über mehrere Doku-Seiten und Blogartikel verteilt. Unit Testing prüft isolierte Funktionen; Integrationstests prüfen das **Zusammenspiel mehrerer Komponenten** (mehrere Transformationsschritte, eine ganze Pipeline, oder Pipeline+Anwendung zusammen). Terminologie ist uneinheitlich: offizielle Doku nennt Pipeline-Kettentests „Unit Testing" (siehe Abschnitt 14), Blogartikel und die Developer-Best-Practices-Seite nutzen „Integration Testing" für dieselbe Ebene.

**Drei-Ebenen-Testmodell (Developer Best Practices, siehe Abschnitt 26):**
1. **Unit Tests** — Geschäftslogik mit pytest, blockierend bei PR-Fehlschlägen.
2. **Bundle-Validierung** — `bundle validate` lokal, `bundle deploy` in Nicht-Produktions-Workspaces in CI.
3. **Integrationstests** — in Staging, mit Abschlussprüfungen und Datenqualitäts-Assertions.

**Workflow-basierte Integrationstests (DLT-DevOps-Blog):** ein Databricks Workflow mit sequenziellen Tasks — (1) Testdaten aufsetzen, (2) DLT-Pipeline gegen Testdaten ausführen, (3) Ergebnisse validieren. **Nachteil:** Zusatzcode + zusätzliche Compute-Ressourcen nötig.

**DLT-Expectations als leichtgewichtige Alternative (empfohlen):**
```python
@dlt.table
@dlt.expect("valid_types", "type IN ('A', 'B', 'C')")
def silver_validation():
    return dlt.read("silver_layer")
```
Keine zusätzlichen Compute-Ressourcen, integriert sich in die bestehende Pipeline-Ausführung, Ergebnisse landen im DLT-Event-Log.

**Integrationstests in MLOps-Pipelines (Staging):** eigener CI-Schritt, der alle Pipelines (Feature Engineering, Training, Inferenz, Monitoring) durchläuft, um korrektes Zusammenspiel zu verifizieren (siehe Abschnitt 24).

**Data Contract Tests und Regression Tests (DataOps):** Data Contract Tests erzwingen Schema/Nullability/Wertebereich **zwischen** Pipeline-Stufen; Regression Tests führen die vollständige Pipeline gegen repräsentative Stichproben aus und vergleichen mit Baselines (siehe Abschnitt 27).

**Bundle-Validierung als Vorstufe:** `databricks bundle validate` prüft nur YAML-Syntax/-Struktur, keinen tatsächlichen Datenfluss — liegt explizit zwischen Unit Tests und Integrationstests.

**Werkzeugkasten je Integrationstest-Typ:**

| Anwendungsfall | Werkzeug/Ansatz |
|---|---|
| Kette abhängiger Lakeflow-Pipeline-Tabellen | `TestPipeline.run()` mit mehreren Tabellennamen |
| Datenqualität kontinuierlich während des Pipeline-Laufs | DLT/LDP-Expectations (`@dlt.expect`) |
| Vollständige Pipeline in eigenem Testlauf | Workflow mit Setup-/Run-/Validate-Tasks |
| ML-Pipeline-Zusammenspiel | Staging-CI-Schritt im MLOps-Workflow |
| Schema-/Wertebereich-Verträge zwischen Pipeline-Stufen | Data Contract Tests (Great Expectations, Soda Core, dbt-Tests) |
| Konfigurations-Korrektheit vor dem eigentlichen Test | `databricks bundle validate` |
| Umgebungsparametrisierte SDP-Expectations + Job-Tasks | `@dp.expect_all_or_fail`, `TEST_`-Materialized-Views (siehe Abschnitt 16) |

---

## 16. SDP-Integrationstest-Patterns (Praxisbeispiel)

**Einfach erklärt:** Zwei praktische Muster für Integrationstests mit Spark Declarative Pipelines (SDP, aktueller Name für Lakeflow Declarative Pipelines/DLT): (1) Expectations-basierte Tests direkt in der Pipeline, umgebungsparametrisiert für dev/stage/prod, und (2) Job-Tasks-basierte Integrationstests als separate Schritte nach der Pipeline-Ausführung.

**Methode 1 — SDK-Beispiel zum Erstellen/Starten der Pipeline:**
```python
pipeline = DeclarativePipelineCreator(
                            pipeline_name=f"sdk_health_etl_{DA.catalog_dev}", 
                            catalog_name = DA.catalog_name,
                            schema_name = 'default',
                            root_path_folder_name='src',
                            source_folder_names=[
                                'src/sdp/**', 
                                'tests/integration_test/**'],
                            configuration = {
                                'target': 'development',
                                'raw_data_path':f'/Volumes/{DA.catalog_name}/default/health'
                            })

pipeline.create_pipeline()

pipeline.start_pipeline()
```

**Vollständiges Codebeispiel `integration_tests_sdp.py`:**
```python
from pyspark import pipelines as dp

## Zielumgebungs-Konfigurationsvariable in der Variable target speichern
target = spark.conf.get("target")

## Basierend auf dem deployten Target die spezifischen Validierungsmetriken für die Tabellen ermitteln.
target_integration_tests_validation = {
    'development': {
        'health_bronze': {
            'total_rows': 7500
        },
        'health_silver': {
            'total_rows': 7500
        }
    },
    'stage': {
        'health_bronze': {
            'total_rows': 35000
        },
        'health_silver': {
            'total_rows': 35000
        }
    }
}

## Erwartete Werte für die Gesamtzeilenanzahl der Tabellen je nach Target (development oder stage) speichern
if target in ('development', 'stage'):
    total_expected_bronze = target_integration_tests_validation[target]['health_bronze']['total_rows']
    total_expected_silver = target_integration_tests_validation[target]['health_silver']['total_rows']


def test_count_table_total_rows(table_name, total_count, target):
    '''
    Zählt die Zeilen der angegebenen Tabelle und vergleicht sie mit den erwarteten Werten für
    development/stage-Daten. Schlägt das Update fehl, wenn die Anzahl nicht übereinstimmt.
    '''
    @dp.table(
        name=f"TEST_{target}_{table_name}_total_rows_verification",
        comment=f"Confirms all rows were ingested from the {target} raw data to {table_name}"
    )
    @dp.expect_all_or_fail({"valid count": f"total_rows = {total_count}"}) 
    def count_table_total_rows():
        return spark.sql(f"""
            SELECT COUNT(*) AS total_rows FROM {table_name}
        """)


def test_gold_table_columns():
    '''
    Prüft die eindeutigen Werte in den Spalten Age_Group und HighCholest_Group der Gold-Tabelle
    chol_age_agg — bestätigt, dass die distinkten Werte dieser Spalten korrekt sind.
    ''' 
    check_silver_calc_columns = {
        "valid age group": "Age_Group in ('0-9', '10-19', '20-29', '30-39', '40-49', '50+', 'Unknown')",
        "valid cholest group": "HighCholest_Group in ('Normal', 'Above Average', 'High', 'Unknown')"
    }

    @dp.table(comment="Check age group and high cholest group in the gold table")
    @dp.expect_all_or_fail(check_silver_calc_columns)
    def test_calculated_columns_age_cholesterol():
        return (dp
                .read("chol_age_agg")
                .select("Age_Group", "HighCholest_Group")
            )


## Die angegebenen Tests je nach Zielumgebung ausführen (development, stage oder production)
if target in ('development','stage'):  ## Dynamischer Integrationstest für dev-/stage-Tabellen
    test_count_table_total_rows('health_bronze',  total_expected_bronze, target)
    test_count_table_total_rows('health_silver',  total_expected_silver, target)
    test_gold_table_columns()
elif target == 'production':  ## In Production nur die Gold-Tabelle testen
    test_gold_table_columns()
```

**Wichtige Muster:** Umgebungsparametrisierung über `target` (in Production nur Wertebereichsprüfungen, keine Zeilenanzahl-Prüfungen); `@dp.expect_all_or_fail(...)` löst bei Verstoß einen harten Pipeline-Fehlschlag aus (im Gegensatz zu `@dp.expect`, das nur protokolliert); `TEST_`-Namenskonvention für Test-Materialized-Views.

**Methode 2 — Lakeflow Jobs mit Tasks:** (1) Unit Tests ausführen (Fail-Fast bei Fehlschlag), (2) SDP **ohne** Expectations ausführen, (3) Integrationstests als eigene Notebook-Tasks (Zeilenanzahl, Tabellenexistenz, Spalten/Werte, Duplikate), (4) Visualisierung erstellen. Vorteil gegenüber Methode 1: Trennung von Datenverarbeitung und Testlogik, jeder Task zeigt individuell Erfolg/Fehlschlag. Vorteil von Methode 1: keine zusätzliche Orchestrierung nötig, Ergebnisse landen automatisch im Pipeline-Event-Log.

---

## 17. CI/CD Best Practices

**Einfach erklärt:** Die sechs offiziellen Kernprinzipien für CI/CD auf Databricks:

1. **Alles versionieren:** Notebooks, Skripte, IaC, Job-Konfigurationen in Git; Branching-Strategien wie Gitflow für Dev/Staging/Production.
2. **Testen automatisieren:** Unit Tests mit pytest/ScalaTest; Workflows mit `databricks bundle validate`; Integrationstests für Data Pipelines mit Tools wie chispa.
3. **Infrastructure as Code:** Cluster/Jobs über Databricks Asset Bundles YAML oder Terraform, umgebungsspezifisch parametrisiert.
4. **Umgebungen isolieren:** getrennte Workspaces für Dev/Staging/Production, MLflow Model Registry für Modellversionierung.
5. **Tools passend zum Cloud-Ökosystem:** Azure → Azure DevOps; AWS → GitHub Actions; GCP → Cloud Build.
6. **Überwachen und Rollbacks automatisieren:** Deployment-Erfolgsraten verfolgen, automatisierte Rollback-Mechanismen.

**Zusätzliche Sicherheitsempfehlung:** Workload Identity Federation für die CI/CD-Authentifizierung — eliminiert die Notwendigkeit, Secrets zu speichern.

---

## 18. Blog: CI/CD-Praxisbeispiele und Software-Engineering-Kultur

**Einfach erklärt:** Kuratierte Zusammenfassung von acht Databricks-Blogartikeln zu CI/CD-Praxis, historischen Fallstudien und Tooling (Blog-Narrativ, keine normative Spezifikation).

**1. DevOps für Delta Live Tables (2023):** Standard-DevOps-Praktiken lassen sich auf Data-Pipeline-Entwicklung anwenden. Entwicklungs-Workflow: Feature-Branch → PR → CI/CD aktualisiert Staging + Unit Tests → Review → Merge → Release-Pipeline deployt Production. Code-Struktur für Testbarkeit — Transformationslogik von DLT-Pipeline-Definitionen trennen:

```python
from transformations.data_processing import clean_bronze_data

@dlt.table
def silver_layer():
    bronze_data = dlt.read("bronze_table")
    return clean_bronze_data(bronze_data)
```

Unit Testing: lokal (pytest-basiert, kein Databricks-Ressourcenverbrauch) oder notebook-basiert (Nutter). Integrationstests: Databricks-Workflows-Ansatz (Zusatzcode + Compute nötig) vs. DLT-Expectations-Ansatz (empfohlen):

```python
@dlt.table
@dlt.expect("valid_types", "type IN ('A', 'B', 'C')")
def silver_validation():
    return dlt.read("silver_layer")
```

Azure-DevOps-Beispiel: `onPush`-Stage (Checkout, Poetry, Staging-Update, Unit Tests via Nutter) und `onRelease`-Stage (zusätzlich Integrationstests + Production-Repo-Update).

**2. Software-Engineering-Best-Practices für Notebooks:** inhaltsgleich mit Abschnitt 7.

**3. CI/CD für Data Pipelines (2017):** fünf Phasen (Exploration, iterative Entwicklung mit Unit Tests, CI/Build, Staging-Testing, Production-Deployment). Blue/Green-Production-Deployment für einfachen Rollback.

**4. Metacogs CI/CD-Pipeline für Apache Spark (2016):** Fallstudie mit Jenkins. Ergebnisse: Feature-Deployment-Zeit von ~1 Monat auf 1–2 Wochen; mind. 28 % AWS-EC2-Kosteneinsparung; neue Data Scientists in 1 statt 4 Wochen produktiv.

**5. Produktionsreif und automatisiert (2020):** dreistufige CI/CD-Architektur (Development, Staging/Integration, Production); fünf Schritte automatisierte Umgebungs-Provisionierung.

**6. Databricks Labs CI/CD Templates:** Open-Source-Cookiecutter-Tool.
```bash
pip install cookiecutter
cookiecutter https://github.com/databrickslabs/cicd-templates.git
```

**7. CI/CD mit Notebooks und Azure DevOps (Teil 1):** Kreditscoring-Beispiel, Drei-Umgebungen-Architektur (Development/Staging/Production, Shared-Nothing-Prinzip für Daten/MLflow).

**8. GitHub Actions für Databricks:** erste First-Party-GitHub-Actions — Notebooks ausführen, mehrere Workspaces sequenziell ansteuern (Staging → Production). *Ersetzt/vertieft durch [Developers/CI-CD/04 GitHub Actions Integration.md].*

---

## 19. Jobs mit Git-Quellcode

**Einfach erklärt:** Tasks in Lakeflow Jobs können Quellcode direkt aus Remote-Git-Repositories abrufen (Notebooks, Python-Skripte, SQL-Dateien, dbt-Projekte). Wichtig: „Alle Tasks eines Jobs müssen denselben Commit referenzieren." Solche Tasks können nicht in Workspace-Dateien schreiben — temporäre Daten müssen in ephemeren Storage, dauerhafte Daten in Volumes/Tabellen.

**Sparse Checkout** für große Repositories (>2.500 Dateien, selten aktualisierter Ziel-Branch): Databricks cacht Checkouts nach Workspace, Repository-URL, Commit-Hash und Sparse-Pattern-Fingerabdruck (bis zu einer Woche gültig).

**Import-Rate-Berechnung:** Dateien/Stunde = Job-Läufe/Stunde × Cache-Miss-Rate × importierte Dateien je Miss. Schwellenwerte: <150.000/h Normalbetrieb; 150.000–300.000/h verschlechterte Performance; >300.000/h Jobs schließen nicht zuverlässig ab.

**Best Practices:** drei oder weniger gemeinsame Checkout-Patterns organisationsweit; Jobs auf stabile Release-Branches statt `main` ausrichten; Merges in geplante Release-Fenster bündeln.

**GitHub-Actions-Beispiel für stündliche Release-Branch-Schnitte:**
```yaml
name: Cut Hourly Release Candidate
on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:
jobs:
  update-branch:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout main branch
        uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 0
      - name: Update release-candidate branch
        run: |
          git push origin HEAD:release-candidate --force
```

**API-Implementierung (Jobs API, `sparse_checkout`-Block):**
```json
{
  "git_source": {
    "git_url": "https://github.com/example/my-repo",
    "git_provider": "gitHub",
    "git_branch": "release-candidate",
    "sparse_checkout": {
      "patterns": ["src/models", "src/utils"]
    }
  }
}
```

---

## 20. Blog: Repos-Historie und Features

**Einfach erklärt:** Kuratierte Zusammenfassung von vier historischen Blogartikeln zur Entwicklung von Databricks Repos (heute „Git Folders"): Produktionsreife (2021) — Repository-Ebenen-Integration mit Git-Providern (GitHub, Bitbucket, GitLab, Azure DevOps), Allow Lists und Secret Detection. GA-Ankündigung (7. Okt. 2021) mit „Files in Repos" (Public Preview) für Nicht-Notebook-Dateien. Neue Konfliktauflösung: Merge (bewahrt volle Historie) vs. Rebase (sauberere, aber umgeschriebene Historie) direkt in der UI. OAuth-2.0-Git-Credential-Support für Service Principals (GA) — löst PAT-Sicherheitsprobleme durch kurzlebige, automatisch erneuerte Tokens (8 Stunden bei GitHub).

---

## 21. Blog: Asset Bundles und Git-Workflows (Ankündigungen)

**Einfach erklärt:** Kuratierte Zusammenfassung von drei Ankündigungs-/Tutorial-Blogartikeln. **AI/BI-Dashboards sicher mit Asset Bundles ausliefern:** Workflow über Git Folder + Bundle-Editor, Branch/PR/Review-Zyklus, `${variable}`-Syntax für umgebungsspezifische Werte, Revert-Funktion für schnellen Rollback. **Asset Bundles jetzt im Workspace (Public Preview):** Bundles direkt in der Workspace-UI ohne CLI/VS Code, `source_linked_deployment` für schnellere Iteration. **Git-Support für Databricks Workflows (heute Lakeflow Jobs):** mehrere Git-Provider, jeder Job-Lauf an einen Commit-Hash gebunden (Reproduzierbarkeit, Audit-Trail); Einschränkung: Workspace-Repos-Tasks und Remote-Git-Tasks nicht in einem Multi-Task-Job mischbar.

---

## 22. Blog: Lakebase Database Branching

**Einfach erklärt:** Kuratierte Zusammenfassung von drei Blogartikeln zu Copy-on-Write-Database-Branching mit Lakebase (Databricks' verwaltetem Postgres) — thematisch nur lose mit Notebook-/Pipeline-Testing verwandt, aber explizit angefragt. **Glaspoort-Fallstudie:** flache Branch-Topologie ab Production (statt hierarchischem Stacking) eliminiert die „Reset Tax"; Per-PR-CI/CD-Flow mit temporären `pr-xxxx`-Branches (TTL 1 Stunde); Ergebnis: Iterationszyklen zehnfach beschleunigt. **Technische Grundlage:** Copy-on-Write statt vollständiger Duplizierung — Branch-Erstellung in Sekunden statt Minuten/Stunden, Storage-Kosten proportional zu Änderungen statt Gesamtdatenmenge. **Evolutionäre Datenbankentwicklung (Teil 3):** Tier-Topologie (Production/Staging als Eltern-Branches, Features als ephemere Kind-Branches); Governance wird einmal auf dem Trunk entworfen und automatisch vererbt; SCM-State-Machine mit fünf Zuständen (`scaffold-complete, feature-claimed, pr-ready, ci-green, merged`) für agentengenerierten Code.

---

## 23. ML-Lifecycle

**Einfach erklärt:** Der End-to-End-ML-Weg auf Databricks über drei Stufen (Development, Staging, Production) und acht Phasen: (1) Anwendungsfall abgrenzen und Erfolg definieren, (2) Daten explorieren (EDA, Genie Chat/Code), (3) Daten/Features vorbereiten (Unity Catalog, Feature Store), (4) Modelle trainieren und Experimente nachverfolgen (MLflow Tracking), (5) Evaluieren (Accuracy, AUC, Bias/Fairness), (6) Modelle registrieren und staged testen (MLflow Model Registry, Alias „Staging"/„Production"), (7) In Produktion deployen (Real-Time Serving vs. Batch Inference — „Train once"), (8) Überwachen und Neu-Trainieren (Inference-Tabellen, Data-Drift-Monitoring).

---

## 24. MLOps-Workflow

**Einfach erklärt:** MLOps ist „eine Menge von Prozessen und automatisierten Schritten zur Verwaltung von Code, Daten und Modellen" — integriert DevOps, DataOps und ModelOps. Kernprinzipien: Umgebungen nach Entwicklungsstufe trennen (Dev/Staging/Prod); vier Kernpraktiken für Zugriffskontrolle/Versionierung (Git-Integration, Delta-Lake-Storage, MLflow-Management, Unity-Catalog-Modelle); **Code deployen, nicht Modelle**.

**Development-Stufe (6 Schritte):** Datenquellen (Dev-Catalog) → EDA (AutoML-Unterstützung) → Code-Repository-Management → Modell trainieren (Training/Tuning + Evaluation in MLflow) → Modell validieren/deployen (Alias „Challenger" → „Champion") → Code committen.

**Staging-Stufe (5 Schritte):** eigener Staging-Catalog → Code mergen + Unit Testing (CI baut, Testfehlschlag → PR-Ablehnung) → Integrationstests (alle Pipelines: Feature Engineering, Training, Inferenz, Monitoring) → Merge in Main → Release-Branch erstellen.

**Production-Stufe (7 Schritte):** Modell trainieren (Production-Catalog) → Modell validieren (Alias „Challenger") → Modell deployen (Offline-Vergleich Challenger vs. Champion, ggf. A/B-Tests) → Model Serving (Endpoints mit Traffic-Splits) → Inferenz (Batch/Streaming) → Data Profiling (Drift-Monitoring) → Retraining (geplant oder getriggert durch Performance-Alerts).

---

## 25. Python-Entwicklung auf Databricks

**Einfach erklärt:** Übersichtsseite für Python-Entwickler: Einstieg (Code importieren, auf Cluster ausführen, fortgeschrittene Fähigkeiten inkl. Python-Unit-Tests im Workspace), Tutorials (Data Engineering, Data Science/ML, AutoML). **Debugging:** `pdb` in Notebooks (Runtime 11.3 LTS+), Variable Explorer (ab 12.2 LTS); `breakpoint()` funktioniert nicht in IPython/Databricks-Notebooks — stattdessen `import pdb; pdb.set_trace()`.

**Python-APIs:** **PySpark** (offizielle, flexiblere API mit Spark SQL/Structured Streaming/MLlib/GraphX) vs. **Pandas API on Spark** (Nachfolger von Koalas, ab Runtime 10.0) — „pandas skaliert nicht auf Big Data", die Pandas API on Spark füllt diese Lücke.

**Code-Management:** Notebooks mit Jupyter-ähnlicher Funktionalität plus Big-Data-Visualisierungen und MLflow-Integration; Notebook-State-Reset über „New session"; Git Folders für Versionierung.

**Cluster/Libraries:** Default Libraries, Notebook-scoped Libraries (`%pip install`), Compute-scoped Libraries (Nicht-Python).

**Jobs:** Notebooks, Python-Skripte, Wheel-Dateien; Erstellung über UI/REST-API/Python-SDK/CLI; `spark_python_task`-Feld für Skript-Jobs.

**ML:** scikit-learn, TensorFlow, Keras, PyTorch, MLlib, XGBoost (Databricks Runtime for ML); MLflow Tracking, Model Registry, Jobs/Model Serving.

**IDEs:** PyCharm, Jupyter, VS Code — Synchronisation via Git Folders, Libraries/Jobs, oder Databricks Connect (Remote Execution).

---

## 26. Allgemeine Developer Best Practices

**Einfach erklärt:** Die vollständige offizielle Best-Practices-Sammlung für Databricks-Entwickler.

**Source Control:** alle Dateien versionieren (Notebooks, `.py`/`.sql`, `databricks.yml`); Build-Artefakte/Credentials über `.gitignore` ausschließen; **ein einzelnes Repository** bevorzugt (Ausnahme: regulierte Branchen); **Trunk-based Branching** minimiert Merge-Konflikte.

**Workspace-Konfiguration:** Workspace-Umgebungen nach Teamgröße isolieren (≤5 Engineers: Dev+Prod; 5+: zusätzlich Staging); ein Unity-Catalog-Metastore mit getrennten Catalogs je Umgebung; Produktions-Catalogs im `ISOLATED`-Modus; persönliche Schemas nach Muster `dev_${user_name}`; Serverless Compute bevorzugt.

**CI/CD-Empfehlungen:** Databricks Asset Bundles für CI/CD empfohlen; Terraform nur für externe/Cloud-Ebenen-Ressourcen (Workspace-Provisionierung, Networking).

**Bundle-Management:** kleine, team-eigene Bundles statt eines großen; `sync.paths` für gemeinsame Ordner; Inter-Bundle-Abhängigkeiten in der CI/CD-Ebene modellieren, nicht Bundles zusammenlegen; eigene Bundle-Templates für Konventionen; kleine Bundles ermöglichen gezielte Rollbacks/Hotfixes.

**Allgemeine Entwicklung:** Service Principals/OIDC für Nicht-Development-Automatisierung; Workload Identity Federation für regulierte Branchen; Geschäftslogik in `.py`/`.sql`-Modulen statt in Notebooks; dynamische Wertreferenzen (`{{tasks.<task_key>.values.<value_key>}}`) statt statischer Variablen.

**Testing und Observability:** dasselbe Drei-Ebenen-Testmodell wie in Abschnitt 15 (Unit Tests → Bundle-Validierung → Integrationstests); Lakeflow Pipelines sollten eingebaute Development-/Validierungs-Features nutzen (siehe Abschnitt 14) statt Ad-hoc-Notebook-Ausführung; Logging als Teil des Deployment-Vertrags behandeln (strukturierte Logs, Standard-Betriebsmetriken).

---

## 27. Blog: MLOps, DataOps und KI-gestützte Entwicklung

**Einfach erklärt:** Kuratierte Zusammenfassung von vier Blogartikeln.

**1. Deployment und Testing mit Notebooks und MLflow (2020):** GitHub-Flow-basierter Ansatz ohne separaten Build-Server. Token-Management über Databricks Secrets:
```
databricks secrets create-scope --scope cicd-test
databricks secrets put --scope cicd-test --key token
```
Abruf: `dbutils.secrets.get(scope="cicd-test", key="token")`. Triggering über eine Delta-Tabelle als Source of Truth:
```
dbutils.notebook.run(PATH_PREFIX + s"${git_hash}/notebook", ...)
```

**2. MLOps vs. DevOps:** „88 % der KI-Initiativen scheitern, ohne Produktionsreife zu erreichen" ohne dedizierte MLOps-Praktiken. Kernunterschiede:

| Aspekt | DevOps | MLOps |
|---|---|---|
| Primärer Fokus | Quellcode und Konfiguration | Code, Datensätze, Feature-Tabellen, Modell-Artefakte, Inferenz-Outputs |
| Versionierung | Git-basierte Code-Repositories | Git (Code) + DVC/Delta Lake (Daten) + Model Registries (Modelle) |
| Quality Gates | Unit-/Integrationstests | Datenvalidierung, Modell-Performance-Schwellenwerte, Vorhersage-Genauigkeit |

**Model Drift** ist der schärfste Kontrast — Modell-Performance erodiert, selbst wenn Code unverändert bleibt. **Continuous Training (CT):** automatisches Retraining bei Verteilungsverschiebung, ohne DevOps-Entsprechung.

**3. Was ist DataOps?** „DataOps ist eine kollaborative Datenmanagement-Praxis, die DevOps-Prinzipien … auf den End-to-End-Datenlebenszyklus anwendet." Marktwachstum von 3,9 Mrd. USD (2023) auf projizierte 10,9 Mrd. USD (2028). Drei Testtypen: Unit Tests (Transformationslogik), Data Contract Tests (Schema/Nullability/Wertebereich zwischen Pipeline-Stufen), Regression Tests (volle Pipelines gegen Stichproben). **Statistical Process Control (SPC):** Kontrollgrenzen bei 2/3 Standardabweichungen statt statischer Schwellenwerte. Metriken: Pipeline Success Rate (Ziel >95 %), MTTD (<1h bei reifer Praxis), MTTR (<4h).

**4. Benchmarking von Coding Agents auf Databricks' Multi-Millionen-Zeilen-Codebase:** interner Benchmark mit echten Engineering-Aufgaben. Kernerkenntnisse: nur eine Tool-Mischung liefert Frontier-Performance; offene Modelle (GLM 5.2) produktionsreif und günstiger als Opus 4.8 bei gleicher Qualität; Token-Preise täuschen bei Kostenanalyse (Sonnet 5 günstiger je Token, aber teurer je Task, da mehr Tokens genutzt werden); Harness-Wahl beeinflusst Effizienz drastisch (2x Kostenunterschied bei gleicher Qualität). „Git History Sealing" verhindert, dass Agenten über die Historie die Lösung finden; tatsächliche Testausführung statt LLM-Richter bestimmt Erfolg.

**5. AgentOps als Erweiterung von MLOps:** Im September 2026 wurde das „Big Book of AgentOps" veröffentlicht. Es überträgt das etablierte MLOps-„Deploy-Code"-Muster (siehe Abschnitt 24) auf GenAI-Agenten, inklusive evaluation-driven CI/CD, einem nativen Observability-Loop und OpenTelemetry-Integration.

---

## 28. dbx (Legacy, archiviert)

**Einfach erklärt:** Die angefragte Archiv-Seite zu `dbx` liefert einen HTTP-404-Fehler — nicht mehr online verfügbar. `dbx` (Databricks Labs) war ein CLI-Tool zur Verpackung und Bereitstellung von Databricks-Jobs, das als Vorläufer-Werkzeug für CI/CD-Workflows diente (siehe Abschnitt 18, „Databricks Labs CI/CD Templates"). Es wurde archiviert und durch **Databricks Asset Bundles** (heute „Declarative Automation Bundles") als offiziell empfohlenen, first-party Nachfolger ersetzt.

---

## 29. Blog: Python-Abhängigkeitsverwaltung in Spark Connect

**Einfach erklärt:** Klassisches Spark erlaubt es nur, Python-Abhängigkeiten **statisch** vor dem Start des Treibers zu konfigurieren — Änderungen zur Laufzeit sind nicht möglich. Ab Apache Spark 3.5.0 löst Spark Connect (und damit auch Databricks Connect, siehe Abschnitt 4) dieses Problem über **sitzungsbasierte Artefakte**: Jede Session bekommt ein eigenes, dediziertes Verzeichnis für Python-Dateien und -Archive; startet ein Python-Worker, wird dessen Arbeitsverzeichnis auf dieses Session-Verzeichnis gesetzt. Dadurch können mehrere gleichzeitige Sessions auf demselben Spark-Connect-Server unterschiedliche Abhängigkeitskonfigurationen nutzen, statt sich eine einzige, treiberweite Umgebung zu teilen — relevant z. B. beim lokalen Testen mit Databricks Connect (Abschnitt 4/5), wenn verschiedene Projekte/Sessions unterschiedliche Paketversionen benötigen.

**Drei unterstützte Wege, eine Python-Umgebung als Archiv an die Session auszuliefern:**

| Werkzeug | Funktionsweise |
|---|---|
| **conda-pack** | erzeugt relokierbare Conda-Umgebungen (Interpreter + Abhängigkeiten) als Archiv für Treiber und Executor |
| **PEX** (Python EXecutable) | bündelt Python-Pakete zu einer einzigen, in sich geschlossenen ausführbaren Datei |
| **venv-pack** | verpackt eine isolierte `virtualenv`-Umgebung analog zu conda-pack als Archiv |

Alle drei Ansätze erzeugen ein Archiv, das der Spark-Connect-Session als Artefakt mitgegeben („geshippt") wird, sodass Treiber und Executor dieselbe isolierte Python-Umgebung verwenden — Databricks bietet für Notebook-Nutzer zusätzlich vereinfachte Oberflächen für denselben Mechanismus. Verfügbar seit Apache Spark 3.5.0 (GA).

---

## 30. Pandas API on Spark: DataFrame-/Series-/Index-Gleichheitsfunktionen

**Einfach erklärt:** Ergänzend zu `assertDataFrameEqual`/`assertSchemaEqual` (Abschnitt 13, für reguläre PySpark-DataFrames) bietet `pyspark.pandas.testing` eigene Gleichheitsfunktionen speziell für die **Pandas API on Spark** (siehe Abschnitt 25): `assert_frame_equal`, `assert_series_equal` und `assert_index_equal`. Sie nutzen „exakt dieselbe API wie die pandas-Test-Utility-Funktionen". Bestehender pandas-Testcode lässt sich damit unverändert auf Pandas-API-on-Spark-Objekte anwenden, inklusive Vergleichen zwischen Pandas-API-on-Spark- und nativen pandas-Objekten. Der Parameter `check_dtype=False` erlaubt es, zwei Objekte trotz unterschiedlicher Spaltentypen als gleich zu behandeln (analog zu `ignoreColumnType` bei `assertDataFrameEqual`, siehe Abschnitt 13).

Diese drei Funktionen sind seit Apache Spark 3.5 / Databricks Runtime 14.2 verfügbar. Die ältere, generische Funktion `assertPandasOnSparkEqual` (einheitliche Funktion für alle Pandas-on-Spark-Objekttypen) ist seit Spark 3.5.1 **deprecated** und wird mit Spark 4.0 entfernt — sie wird durch die drei spezifischeren Funktionen ersetzt.

Import und Grundmuster:

```python
from pyspark.pandas.testing import assert_frame_equal

assert_frame_equal(actual_ps_df, expected_ps_df, check_dtype=False)
```
