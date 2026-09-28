# PySpark-Testing-Utilities und Praxisbeispiel

Die offiziellen `pyspark.testing.utils`-Hilfsfunktionen (`assertDataFrameEqual`, `assertSchemaEqual`), eine pytest-Kurzeinführung sowie ein vollständiges, durchgängiges Praxisbeispiel (Health-Datensatz: Schema-Validierung, Spaltenumbenennung, Wert-Mapping) aus privatem Kursmaterial. Teil der [Testing](../Uebersicht.md)-Reihe, Kapitel [01 Unit Test](../01%20Unit%20Test/). Ergänzt [01 Notebook-Testing Grundlagen.md](01%20Notebook-Testing%20Grundlagen.md) um konkrete, ausführbare Beispiele.

## Abschnittsübersicht

1. [`pyspark.testing.utils`](#pyspark-testing-utils)
2. [Weitere Unit-Testing-Ressourcen](#ressourcen)
3. [pytest-Grundlagen](#pytest-grundlagen)
4. [Beispiel: `assertDataFrameEqual()`](#beispiel-dataframe-equal)
   - 4.1 [Näherungsweise Gleichheit mit `rtol`](#rtol)
5. [Beispiel: `assertSchemaEqual()`](#beispiel-schema-equal)
6. [Beispiel: einfache Assertion ohne PySpark-Testing-Utility](#beispiel-simple-assert)
   - 6.1 [`unittest` als Alternative zu pytest](#unittest-alternative)
7. [pytest ausführen](#pytest-ausfuehren)
8. [Vollständiges Praxisbeispiel: Health-Datensatz](#praxisbeispiel)
9. [Quelle](#quelle)

---

## <a id="pyspark-testing-utils">1. `pyspark.testing.utils`</a>

`pyspark.testing.utils` stellt Hilfsfunktionen bereit, die Unit Testing in PySpark vereinfachen:

- **`assertDataFrameEqual(actual, expected[, ...])`** — Utility-Funktion zur Gleichheitsprüfung zwischen einem tatsächlichen und einem erwarteten DataFrame, mit optionalen Parametern.
- **`assertSchemaEqual(actual, expected)`** — Utility-Funktion zur Gleichheitsprüfung zwischen den Schemas von `actual` und `expected`.

**Vollständige Parameter- und Beispiel-Referenz beider Funktionen** (alle Parameter seit Spark 4.0.0, alle offiziellen Docstring-Beispiele inkl. Fehler-Diffs): siehe [12 assertDataFrameEqual und assertSchemaEqual (API-Referenz).md](12%20assertDataFrameEqual%20und%20assertSchemaEqual%20%28API-Referenz%29.md).

**Drei Testing-Optionen laut offiziellem PySpark-Guide „Testing PySpark"** (ab Spark 3.5+, alle drei nutzen dieselben `pyspark.testing`-Utility-Funktionen und sind untereinander sowie mit jedem beliebigen Test-Framework/jeder CI-Pipeline kombinierbar):

1. **Nur die PySpark-Built-in-Testing-Utilities** (`assertDataFrameEqual`, `assertSchemaEqual`) — für einfache Ad-hoc-Validierung, z. B. direkt in einer Notebook-Session, ohne Test-Framework-Overhead (siehe Abschnitte 4–5 unten).
2. **`unittest`** — Pythons eingebautes Test-Framework, über eine Basisklasse mit `setUpClass`/`tearDownClass` für die SparkSession (siehe Abschnitt 6.1).
3. **`pytest`** — mit einer Fixture für die SparkSession (siehe Abschnitte 3, 7 und das Praxisbeispiel in Abschnitt 8).

## <a id="ressourcen">2. Weitere Unit-Testing-Ressourcen</a>

- **pytest** — Test-Framework, in diesem Kapitel durchgängig genutzt. Vollständige Referenz: [08 pytest — Grundlagen und Referenz.md](08%20pytest%20%E2%80%94%20Grundlagen%20und%20Referenz.md).
- **chispa** — Community-Assertion-Bibliothek für PySpark-DataFrames mit besonders lesbaren Fehlerausgaben, Alternative/Ergänzung zu `assertDataFrameEqual`. Vollständige Referenz: [09 chispa — PySpark-Testbibliothek.md](09%20chispa%20%E2%80%94%20PySpark-Testbibliothek.md).
- **nutter** — Microsofts Framework zum Testen ganzer Databricks-Notebooks (statt einzelner Python-Funktionen). Vollständige Referenz: [10 nutter — Databricks-Notebook-Testing.md](10%20nutter%20%E2%80%94%20Databricks-Notebook-Testing.md).
- **unittest** — Pythons eingebautes Test-Framework, bereits als Alternative in Abschnitt 6.1 demonstriert. Vollständige Referenz: [11 unittest — Python-Standardbibliothek-Referenz.md](11%20unittest%20%E2%80%94%20Python-Standardbibliothek-Referenz.md).

**Video: „Best Practices for Unit Testing PySpark"** (Databricks, Data + AI Summit) — https://www.youtube.com/watch?v=TbWcCyP2MgE. Eine automatisierte Transkript-Auswertung war über die verfügbaren Werkzeuge nicht möglich; die folgenden Kernthemen stammen aus einem inhaltlich eng verwandten, offiziellen Databricks-Begleitartikel zum selben Thema (siehe Quelle unten) und decken sich mit den bereits in diesem Dokument demonstrierten Mustern:

- **Herausforderungen:** Databricks-spezifische Laufzeitbibliotheken wie `dbutils` existieren außerhalb von Databricks nicht; die automatisch initialisierte SparkSession ist andernorts nicht verfügbar; Notebook-basierte Workflows erschweren modulares Testen.
- **Code-Refactoring für Testbarkeit:** Transformationslogik in eigenständige Python-Funktionen/-Module auslösen, `dbutils`-Aufrufe per Dependency Injection ersetzbar machen, Hauptausführungslogik in `if __name__ == "__main__":` kapseln, um Ausführung beim Import zu vermeiden.
- **pytest mit Fixtures:** session-scoped Fixture für die SparkSession, um Initialisierungs-Overhead zu reduzieren (vgl. Abschnitt 8 unten):
  ```python
  @pytest.fixture(scope="session")
  def spark_session():
      return SparkSession.builder.master("local[*]").appName("PyTest").getOrCreate()
  ```
- **Code-Organisation:** Databricks Repos mit separaten Testdateien (z. B. `test_functions.py`); Databricks Asset Bundles für CI/CD (siehe [10 Developers/03 Databricks Asset Bundles](../../10%20Developers/03%20Databricks%20Asset%20Bundles/)); Tests direkt im Notebook über `pytest.main([".", "-v", "-p", "no:cacheprovider"])` (vgl. Abschnitt 7).
- **DataFrame-Validierung:** `assertDataFrameEqual`/`assertSchemaEqual` ab Spark 3.5+/Databricks Runtime 14.2+ (siehe Abschnitte 4–5).
- **Mocking:** `unittest.mock` zum Simulieren von `dbutils`-Verhalten, ohne die echte Databricks-Laufzeitumgebung zu benötigen.
- **Sechs Best Practices laut Begleitartikel:** Transformationslogik von Laufzeit-spezifischen Operationen trennen; kleine, synthetische Beispieldaten statt Produktionsdaten in Tests nutzen; eine einzige SparkSession über Tests hinweg teilen; Tests in CI/CD-Pipelines integrieren (GitHub Actions, Azure DevOps); Code lokal validieren, bevor er nach Databricks deployt wird; Business-Logik von I/O- und Utility-Aufrufen isolieren.

## <a id="pytest-grundlagen">3. pytest-Grundlagen</a>

Pytest nutzt Pythons eingebaute `assert`-Statements (alternativ auch andere Assert-Varianten wie in PySpark). Einfach zu verwenden, liefert aber bei Testfehlschlägen detaillierte Fehlermeldungen, was das Debuggen erheblich beschleunigt.

Pytest entdeckt und führt automatisch alle Tests aus — keine manuelle Konfiguration nötig. Testdateien und -funktionen müssen lediglich mit dem Präfix `test_` benannt werden.

## <a id="beispiel-dataframe-equal">4. Beispiel: `assertDataFrameEqual()`</a>

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

### <a id="rtol">4.1 Näherungsweise Gleichheit mit `rtol`</a>

Für Floating-Point-Spalten, bei denen exakte Gleichheit wegen Rundungsfehlern unrealistisch ist, akzeptiert `assertDataFrameEqual` einen relativen Toleranz-Parameter `rtol` (offizielles Beispiel):

```python
df1 = spark.createDataFrame(data=[("1", 0.1), ("2", 3.23)], schema=["id", "amount"])
df2 = spark.createDataFrame(data=[("1", 0.109), ("2", 3.23)], schema=["id", "amount"])
assertDataFrameEqual(df1, df2, rtol=1e-1)  # besteht, DataFrames sind bis auf rtol gleich
```

## <a id="beispiel-schema-equal">5. Beispiel: `assertSchemaEqual()`</a>

```python
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType, LongType
from pyspark.sql.functions import when, col
from pyspark.testing.utils import assertSchemaEqual

def test_get_health_csv_schema_match():

    # Schema aus der eigenen Funktion abrufen
    actual_schema = project_functions.get_health_csv_schema()
    
    # Erwartetes Schema definieren. Ändert sich die Funktion während der Entwicklung, erkennt der Unit Test den Fehler und der Test schlägt fehl.
    expected_schema = StructType([
        StructField("ID", IntegerType(), True),
        StructField("PII", StringType(), True),
        StructField("Age", DoubleType(), True)
    ])

    # Prüfen, ob das tatsächliche Schema dem erwarteten Schema entspricht
    assertSchemaEqual(actual_schema, expected_schema)
    print('Test passed!')

test_get_health_csv_schema_match()
```

## <a id="beispiel-simple-assert">6. Beispiel: einfache Assertion ohne PySpark-Testing-Utility</a>

Nicht jeder Test benötigt `assertDataFrameEqual`/`assertSchemaEqual` — für einfache Vergleiche (hier: Spaltennamen nach einer Transformation) genügt ein normales Python-`assert`:

```python
def test_uppercase_columns_function():

    ## Fake-DataFrame mit zufälligen Spaltennamen
    data = [(1, 5.0, 1, 1, 1, 1)]
    columns = ["id", "trip_distance", "My_Column", "WithNumbers123", "WithSymbolX@#", "With Space"]
    df = spark.createDataFrame(data, columns)

    ## transforms.uppercase_columns_names-Funktion anwenden, um die tatsächlichen Spaltennamen zu erhalten
    actual_df = transforms.uppercase_columns_names(df)
    actual_columns = actual_df.columns

    ## Liste der erwarteten Spaltennamen erstellen
    expected_columns = ['ID', 'TRIP_DISTANCE', 'MY_COLUMN', 'WITHNUMBERS123', 'WITHSYMBOLX@#', "WITH SPACE"]

    ## Test der tatsächlichen gegen die erwarteten Spaltennamen mit einfachem Python-assert
    assert actual_columns == expected_columns
    print('Test Passed!')

test_uppercase_columns_function()
```

### <a id="unittest-alternative">6.1 `unittest` als Alternative zu pytest</a>

Neben pytest dokumentiert der offizielle PySpark-Guide auch Pythons eingebautes `unittest`-Modul als vollwertige Option (Option 2 der Übersicht in Abschnitt 1) — nützlich, wenn kein zusätzliches Test-Framework installiert werden soll oder kann.

**Verwendetes Beispiel (aus dem offiziellen Guide, unabhängig vom Health-Datensatz-Beispiel in Abschnitt 8):** eine Transformationsfunktion, die überzählige Leerzeichen in einer Namensspalte entfernt:

```python
from pyspark.sql.functions import col, regexp_replace

def remove_extra_spaces(df, column_name):
    df_transformed = df.withColumn(column_name, regexp_replace(col(column_name), "\\s+", " "))
    return df_transformed
```

**Basisklasse mit `@classmethod`** für Setup/Teardown der SparkSession — läuft einmal je Testklasse, nicht je Testfunktion:

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

**Tests als Methoden der abgeleiteten Klasse:**

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

`unittest` erkennt automatisch alle Funktionen, deren Name mit `test` beginnt — analog zu pytest (siehe Abschnitt 3).

**Ausführung in einem Notebook** (statt über die Kommandozeile):

```python
unittest.main(argv=[''], verbosity=0, exit=False)
```

```
Ran 1 test in 1.734s

OK
```

`argv=['']` verhindert, dass `unittest.main()` die Notebook-eigenen Kommandozeilenargumente als Test-Selektoren interpretiert; `exit=False` verhindert, dass der Aufruf die Notebook-Kernel-Session beendet (was `unittest.main()` standardmäßig via `sys.exit()` täte).

## <a id="pytest-ausfuehren">7. pytest ausführen</a>

```python
# pytest installieren
!pip install pytest==8.3.4

# autoreload aktivieren
%load_ext autoreload
%autoreload 2
```

```python
# pytest auf der Datei ./tests_lab/lab_unit_test_solution.py ausführen. Zelle ausführen und bestätigen, dass die Unit Tests bestehen.

import pytest
import sys

sys.dont_write_bytecode = True

retcode = pytest.main(["./tests_lab/lab_unit_test_solution.py", "-v", "-p", "no:cacheprovider"])

assert retcode == 0, "The pytest invocation failed. See the log for details."
```

Die `autoreload`-Extension sorgt dafür, dass Änderungen an importierten Python-Modulen automatisch übernommen werden, ohne die Notebook-Session neu starten zu müssen — vollständige Referenz inkl. Runtime-16.0+-Verhalten (gezieltes Neuladen, automatische Aktivierungs-Vorschläge) und Grenzen (nur Driver-Prozess, nicht für UDFs/Executor-Code) siehe [Workspace Files als Code-Module.md](../../04%20Data%20guides/02%20Work%20with%20files/02%20Workspace%20Files%20als%20Code-Module.md), Abschnitt 2.

## <a id="praxisbeispiel">8. Vollständiges Praxisbeispiel: Health-Datensatz</a>

Ein vollständiges, eigenständiges Testmodul (`test_spark_helper_functions.py`) für ein Beispielprojekt, das eine Health-CSV-Datei verarbeitet. Demonstriert eine session-scoped pytest-Fixture für die SparkSession sowie drei reale Tests gegen Hilfsfunktionen aus `src.helpers.project_functions`.

```python
import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, DateType, DoubleType, LongType
from pyspark.sql.functions import when, col
from pyspark.testing.utils import assertDataFrameEqual, assertSchemaEqual

# Diese Datei muss über pytest ausgeführt werden. Wird die .py-Datei direkt ausgeführt, entsteht ein Fehler.
# Ggf. den Pfad zu den src.helpers-Modulen über sys.path.append('/path/to/file') ergänzen.
from src.helpers import project_functions


# pytest-Fixture, die eine SparkSession für die Tests bereitstellt.
# Die Fixture heißt 'spark' und wird einmal je Test-Session aufgebaut.
@pytest.fixture(scope="session")
def spark():
    # SparkSession erstellen. Existiert bereits eine, wird sie wiederverwendet.
    spark = SparkSession.builder.getOrCreate()
    
    # Die SparkSession an die Testfunktion übergeben.
    yield spark
    # Nach dem Test kann bei Bedarf Cleanup-Code ergänzt werden.


def test_get_health_csv_schema_match():
    # Erwartetes Schema definieren, gegen das getestet wird.
    # Ändert sich das Verhalten der Funktion, schlägt der Test fehl, sofern das Schema nicht mehr passt.
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

    # Die Funktion aufrufen, die das Schema aus der Health-CSV ermittelt.
    actual_schema = project_functions.get_health_csv_schema()

    # Prüfen, ob das tatsächliche Schema dem erwarteten Schema entspricht.
    assertSchemaEqual(actual_schema, expected_schema)


def test_high_cholest_column_valid_map(spark):
    # Beispieldaten definieren und DataFrame erstellen
    data = [
        (0,),
        (1,), 
        (2,), 
        (3,), 
        (4,), 
        (None,)
    ]
    sample_df = spark.createDataFrame(data, ["value"])

    # Transformation auf die Beispieldaten anwenden
    actual_df = sample_df.withColumn("actual", project_functions.high_cholest_map("value"))

    # Statisches DataFrame mit den erwarteten Ergebnissen der high_cholest_map-Funktion.
    # Ändert sich die Funktion und reproduziert diese Ergebnisse nicht mehr, wird ein Fehler zurückgegeben.
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

    ## Prüfen, ob die Spalte im Beispiel- und im erwarteten DataFrame übereinstimmt.
    assertDataFrameEqual(actual_df.select(col('actual')), expected_df.select(col('actual')))


def test_age_group_column_valid_map(spark):
    # Beispieldaten definieren und DataFrame erstellen
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

    # Transformation auf die Beispieldaten anwenden
    actual_df = sample_df.withColumn("actual", project_functions.group_ages_map("value"))

    # Statisches DataFrame mit den erwarteten Ergebnissen
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

    ## Prüfen, ob die Spalte im Beispiel- und im erwarteten DataFrame übereinstimmt.
    assertDataFrameEqual(actual_df.select(col('actual')), expected_df.select(col('actual')))
```

**Wichtige Muster in diesem Beispiel:**

- Die `spark`-Fixture ist `scope="session"` — wird also nur einmal je Testlauf erstellt und über alle Tests hinweg wiederverwendet (Performance).
- `test_get_health_csv_schema_match()` benötigt keine `spark`-Fixture als Parameter, da sie nur das *Schema* prüft, keine tatsächlichen Daten verarbeitet.
- `test_high_cholest_column_valid_map(spark)` und `test_age_group_column_valid_map(spark)` benötigen die Fixture, da sie DataFrames erzeugen und transformieren.
- Statische, hartkodierte Erwartungs-DataFrames sind der Kern jedes Tests — Mapping-Funktionen (`high_cholest_map`, `group_ages_map`) werden gegen bekannte Eingabe-/Ausgabe-Paare geprüft, inklusive Edge Cases wie `None`/negative Werte.

## <a id="quelle">9. Quelle</a>

- Private Kursnotiz (vollständiges Beispielprojekt).
- https://spark.apache.org/docs/latest/api/python/reference/pyspark.testing.html (offizielle `pyspark.testing`-API-Referenz, zur Einordnung von `assertDataFrameEqual`/`assertSchemaEqual`)
- https://spark.apache.org/docs/latest/api/python/getting_started/testing_pyspark.html (offizieller Guide „Testing PySpark": Drei-Optionen-Struktur, `rtol`-Beispiel, `unittest`-Pattern)
- https://docs.databricks.com/aws/en/files/workspace-modules#autoreload-for-python-modules (autoreload für Python-Module)
- https://www.youtube.com/watch?v=TbWcCyP2MgE („Best Practices for Unit Testing PySpark", Databricks, Data + AI Summit — Titel/Autor per oEmbed verifiziert, Inhalt nicht per Transkript zugänglich)
- https://community.databricks.com/t5/technical-blog/writing-unit-tests-for-pyspark-in-databricks-approaches-and-best/ba-p/122398 (thematisch eng verwandter, offizieller Databricks-Begleitartikel, siehe Abschnitt 2)

**Stand:** 2026-09-01.
