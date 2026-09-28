# SQL und Python UDFs in Unity Catalog

Referenz zu UDFs, die als governed Objekte in Unity Catalog registriert werden (`CREATE FUNCTION ... LANGUAGE SQL` bzw. `LANGUAGE PYTHON`), inklusive Custom Dependencies, Environment Isolation, Governance und Best Practices.

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [SQL- und Python-UDFs in Unity Catalog erstellen](#erstellen)
3. [UDFs mit Custom Dependencies erweitern](#dependencies)
4. [Unity-Catalog-UDFs in PySpark verwenden](#pyspark)
5. [Eine session-scoped UDF upgraden](#upgrade)
6. [UDFs in Unity Catalog teilen](#teilen)
7. [Environment Isolation](#isolation)
8. [UDFs für Agent-Tools](#agent-tools)
9. [UDFs für den Zugriff auf externe APIs](#external-apis)
10. [UDFs für Sicherheit und Compliance](#security)
11. [Best Practices](#best-practices)
12. [Zeitzonenverhalten bei Timestamp-Inputs](#timezone)
13. [Limitierungen](#limitierungen)
14. [Quellen](#quellen)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

- Um Python-Code in UDFs zu verwenden, die in Unity Catalog registriert sind, muss ein serverloses oder Pro-SQL-Warehouse oder ein Cluster mit Databricks Runtime 13.3 LTS oder höher verwendet werden.
- Enthält eine View eine Unity-Catalog-Python-UDF, schlägt sie auf klassischen SQL-Warehouses fehl.
- ARM-Instance-Support für Scala-UDFs auf Unity-Catalog-fähigen Clustern ist ab Databricks Runtime 15.2 verfügbar.

---

## <a id="erstellen">2. SQL- und Python-UDFs in Unity Catalog erstellen</a>

SQL-UDF:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.calculate_bmi(weight DOUBLE, height DOUBLE)
RETURNS DOUBLE
LANGUAGE SQL
RETURN
SELECT weight / (height * height);
```

Python-UDF:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.calculate_bmi(weight_kg DOUBLE, height_m DOUBLE)
RETURNS DOUBLE
LANGUAGE PYTHON
AS $$
return weight_kg / (height_m ** 2)
$$;
```

Aufruf:

```sql
SELECT person_id, my_catalog.my_schema.calculate_bmi(weight_kg, height_m) AS bmi
FROM person_data;
```

---

## <a id="dependencies">3. UDFs mit Custom Dependencies erweitern</a>

### Voraussetzungen

- Serverlose Notebooks und Jobs
- Klassisches All-Purpose-Compute mit Databricks Runtime Version 16.2 oder höher
- Pro- oder serverloses SQL-Warehouse

### Abhängigkeitsquellen

- PyPI-Pakete
- Dateien in Unity-Catalog-Volumes (der aufrufende Nutzer benötigt `READ VOLUME`-Berechtigungen auf dem Quell-Volume)
- Dateien unter öffentlichen URLs (die Netzwerksicherheitsregeln des Workspace müssen den Zugriff auf öffentliche URLs erlauben)

### Abhängigkeiten definieren

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.mixed_process(data STRING)
RETURNS STRING
LANGUAGE PYTHON
ENVIRONMENT (
  dependencies = '["simplejson==3.19.3", "/Volumes/my_catalog/my_schema/my_volume/packages/custom_package-1.0.0.whl", "https://my-bucket.s3.amazonaws.com/packages/special_package-2.0.0.whl?Expires=2043167927&Signature=abcd"]',
  environment_version = '3'
)
AS $$
import simplejson as json
import custom_package
return json.dumps(custom_package.process(data))
$$;
```

| Feld | Beschreibung | Typ | Beispielnutzung |
|---|---|---|---|
| `dependencies` | Liste kommagetrennter Abhängigkeiten. Jeder Eintrag ist ein String im [pip Requirements File Format](https://pip.pypa.io/en/stable/reference/requirements-file-format/). | STRING | `dependencies = '["simplejson==3.19.3", "/Volumes/catalog/schema/volume/packages/my_package-1.0.0.whl"]'` |
| `environment_version` | Legt die serverlose Environment-Version fest, in der die UDF läuft. Eine feste Environment-Version führt die UDF mit einer bestimmten Python-Version und vorinstallierten Paketen aus, unabhängig von Python-Version und Paketen der zugrunde liegenden Databricks Runtime. Unterstützte Werte sind `None` oder eine Environment-Version ab 3. Andere Werte als `None` werden nur auf serverlosem Compute und serverlosen SQL-Warehouses unterstützt. | STRING | `environment_version = '3'` |

---

## <a id="pyspark">4. Unity-Catalog-UDFs in PySpark verwenden</a>

```python
from pyspark.sql.functions import expr

result = df.withColumn("bmi", expr("my_catalog.my_schema.calculate_bmi(weight_kg, height_m)"))
display(result)
```

---

## <a id="upgrade">5. Eine session-scoped UDF upgraden</a>

Session-scoped PySpark-UDF:

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

@udf(StringType())
def greet(name):
    return f"Hello, {name}!"

result = df.withColumn("greeting", greet("name"))
result.show()
```

Äquivalente Unity-Catalog-UDF:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.greet(name STRING)
RETURNS STRING
LANGUAGE PYTHON
AS $$
return f"Hello, {name}!"
$$
```

---

## <a id="teilen">6. UDFs in Unity Catalog teilen</a>

Die Zugriffskontrollen des Katalogs bzw. Schemas, in dem die UDF registriert ist, regeln deren Berechtigungen. Empfohlen wird die Vergabe über die Databricks-SQL- oder Workspace-UI.

### Berechtigungen über die Workspace-UI

1. Katalog und Schema suchen, in dem die UDF gespeichert ist, und die UDF auswählen.
2. In den UDF-Einstellungen nach der Option "Permissions" suchen. Nutzer oder Gruppen hinzufügen und die Zugriffsart festlegen, z. B. `EXECUTE` oder `MANAGE`.

### Berechtigungen über Databricks SQL

```sql
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.calculate_bmi TO `user@example.com`;
```

```sql
REVOKE EXECUTE ON FUNCTION my_catalog.my_schema.calculate_bmi FROM `user@example.com`;
```

---

## <a id="isolation">7. Environment Isolation</a>

**Hinweis:** Shared Isolation Environments erfordern Databricks Runtime 18.0 oder höher. In früheren Versionen laufen alle Unity-Catalog-Python-UDFs im Strict-Isolation-Modus.

Unity-Catalog-Python-UDFs mit demselben Owner und derselben Session können standardmäßig eine Isolation Environment teilen. Das verbessert die Performance und reduziert den Speicherverbrauch, da weniger separate Umgebungen gestartet werden müssen.

### Strict Isolation

Um sicherzustellen, dass eine UDF stets in einer eigenen, vollständig isolierten Umgebung läuft, wird die `STRICT ISOLATION`-Characteristic-Klausel hinzugefügt. Diese sollte bei UDFs verwendet werden, die:

- Input als Code mit `eval()`, `exec()` oder ähnlichen Funktionen ausführen.
- Dateien ins lokale Dateisystem schreiben.
- globale Variablen oder den Systemzustand verändern.
- Umgebungsvariablen abfragen oder verändern.

```sql
CREATE OR REPLACE TEMPORARY FUNCTION run_python_snippet(python_code STRING)
RETURNS STRING
LANGUAGE PYTHON
STRICT ISOLATION
AS $$
import sys
from io import StringIO

# Capture standard output and error streams
captured_output = StringIO()
captured_errors = StringIO()
sys.stdout = captured_output
sys.stderr = captured_errors

try:
    # Execute the user-provided Python code in an empty namespace
    exec(python_code, {})
except SyntaxError:
    # Retry with escaped characters decoded (for cases like "\n")
    def decode_code(raw_code):
        return raw_code.encode('utf-8').decode('unicode_escape')
    python_code = decode_code(python_code)
    exec(python_code, {})

# Return everything printed to stdout and stderr
return captured_output.getvalue() + captured_errors.getvalue()
$$
```

### `DETERMINISTIC` setzen, wenn die Funktion konsistente Ergebnisse liefert

`DETERMINISTIC` sollte der Funktionsdefinition hinzugefügt werden, wenn sie für dieselben Eingaben stets dieselben Ausgaben liefert. Das erlaubt Query-Optimierungen, die Performance zu verbessern.

Standardmäßig behandelt Databricks Batch-Unity-Catalog-Python-UDFs als nicht-deterministisch, sofern nicht explizit anders deklariert. Beispiele für nicht-deterministische Funktionen: Erzeugen von Zufallswerten, Abfragen der aktuellen Uhrzeit/des aktuellen Datums oder externe API-Aufrufe.

---

## <a id="agent-tools">8. UDFs für Agent-Tools</a>

KI-Agenten können Unity-Catalog-UDFs als Tools nutzen, um Aufgaben auszuführen und benutzerdefinierte Logik anzuwenden. Siehe "Create agent tools using Unity Catalog functions" in der offiziellen Doku.

---

## <a id="external-apis">9. UDFs für den Zugriff auf externe APIs</a>

```sql
CREATE FUNCTION my_catalog.my_schema.get_food_calories(food_name STRING)
RETURNS DOUBLE
LANGUAGE PYTHON
AS $$
import requests

api_url = f"https://example-food-api.com/nutrition?food={food_name}"
response = requests.get(api_url)

if response.status_code == 200:
   data = response.json()
   # Assume the API returns a JSON object with a 'calories' field
   calories = data.get('calories', 0)
   return calories
else:
   return None  # API request failed

$$;
```

---

## <a id="security">10. UDFs für Sicherheit und Compliance</a>

```sql
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
$$
```

```sql
-- Zuerst die View anlegen
CREATE OR REPLACE VIEW my_catalog.my_schema.masked_customer_view AS
SELECT
  id,
  name,
  my_catalog.my_schema.mask_email(email) AS masked_email
FROM my_catalog.my_schema.customer_data;

-- Jetzt lässt sich die View abfragen
SELECT * FROM my_catalog.my_schema.masked_customer_view;
```

```text
+---+------------+------------------------+------------------------+
| id|        name|                   email|           masked_email |
+---+------------+------------------------+------------------------+
|  1|    John Doe|   john.doe@example.com |  j*******e@example.com |
|  2| Alice Smith|alice.smith@company.com |a**********h@company.com|
|  3|   Bob Jones|    bob.jones@email.org |   b********s@email.org |
+---+------------+------------------------+------------------------+
```

---

## <a id="best-practices">11. Best Practices</a>

Damit UDFs für alle Nutzer zugänglich sind, empfiehlt Databricks, einen dedizierten Katalog und ein dediziertes Schema mit passenden Zugriffskontrollen anzulegen. Für teamspezifische UDFs sollte ein dediziertes Schema innerhalb des Team-Katalogs für Speicherung und Verwaltung verwendet werden.

Databricks empfiehlt, im UDF-Docstring folgende Informationen anzugeben:

- die aktuelle Versionsnummer
- ein Changelog zur Nachverfolgung von Änderungen über Versionen hinweg
- Zweck, Parameter und Rückgabewert der UDF
- ein Beispiel für die Verwendung der UDF

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.calculate_bmi(weight_kg DOUBLE, height_m DOUBLE)
RETURNS DOUBLE
COMMENT "Calculates Body Mass Index (BMI) from weight and height."
LANGUAGE PYTHON
DETERMINISTIC
AS $$
 """
Parameters:
calculate_bmi (version 1.2):
- weight_kg (float): Weight of the individual in kilograms.
- height_m (float): Height of the individual in meters.

Returns:
- float: The calculated BMI.

Example Usage:

SELECT calculate_bmi(weight, height) AS bmi FROM person_data;

Change Log:
- 1.0: Initial version.
- 1.1: Improved error handling for zero or negative height values.
- 1.2: Optimized calculation for performance.

 Note: BMI is calculated as weight in kilograms divided by the square of height in meters.
 """
if height_m <= 0:
 return None  # Avoid division by zero and ensure height is positive
return weight_kg / (height_m ** 2)
$$;
```

---

## <a id="timezone">12. Zeitzonenverhalten bei Timestamp-Inputs</a>

**Wichtige Verhaltensänderung:** Ab **Databricks Runtime 18.0** bleiben `TIMESTAMP`-Werte, die an Python-UDFs übergeben werden, in UTC — das `datetime`-Objekt enthält jedoch keine Zeitzonen-Metadaten (`tzinfo`-Attribut) mehr. Diese Änderung bringt Unity-Catalog-Python-UDFs in Einklang mit Arrow-optimierten Python-UDFs in Apache Spark.

Beispiel:

```sql
CREATE FUNCTION timezone_udf(date TIMESTAMP)
RETURNS STRING
LANGUAGE PYTHON
AS $$
return f"{type(date)} {date} {date.tzinfo}"
$$;

SELECT timezone_udf(TIMESTAMP '2024-10-23 10:30:00');
```

Ausgabe in Databricks-Runtime-Versionen **vor 18.0**:

```text
<class 'datetime.datetime'> 2024-10-23 10:30:00+00:00 Etc/UTC
```

Ausgabe **ab Databricks Runtime 18.0**:

```text
<class 'datetime.datetime'> 2024-10-23 10:30:00+00:00 None
```

Ist eine UDF auf die Zeitzoneninformation angewiesen, muss sie explizit wiederhergestellt werden:

```python
from datetime import timezone

date = date.replace(tzinfo=timezone.utc)
```

---

## <a id="limitierungen">13. Limitierungen</a>

- Innerhalb einer Python-UDF können beliebig viele Python-Funktionen definiert werden, aber alle müssen einen skalaren Wert zurückgeben.
- Python-Funktionen müssen `NULL`-Werte selbstständig behandeln; alle Typ-Mappings müssen den Databricks-SQL-Sprach-Mappings folgen.
- Wird kein Katalog oder Schema angegeben, registriert Databricks Python-UDFs im aktuell aktiven Schema.
- Python-UDFs laufen in einer sicheren, isolierten Umgebung und haben keinen Zugriff auf Dateisysteme oder interne Dienste.
- Pro Query können nicht mehr als fünf UDFs aufgerufen werden.

---

## <a id="quellen">14. Quellen</a>

- SQL and Python user-defined functions (UDFs) in Unity Catalog: https://docs.databricks.com/aws/en/udf/unity-catalog
- Verwandte Datei in diesem Projekt: [UDF task context.md](../03%20UDF%20Task%20Context.md)

**Stand:** 2026-08-22.
