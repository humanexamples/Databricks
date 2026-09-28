# Python UDTFs (User-Defined Table Functions) in Unity Catalog

Referenz zu governed Python-UDTFs in Unity Catalog: geben statt eines Skalarwerts eine ganze Ergebnistabelle zurück. Typische Einsatzgebiete:

- Arrays oder komplexe Datenstrukturen in mehrere Zeilen transformieren
- externe APIs oder Dienste in SQL-Workflows integrieren
- benutzerdefinierte Datengenerierung oder -anreicherung implementieren
- Daten verarbeiten, die zustandsbehaftete Operationen über mehrere Zeilen hinweg erfordern

Zwei Registrierungsarten stehen zur Verfügung:

- **Unity Catalog:** die UDTF wird als governed Objekt in Unity Catalog registriert (dieses Dokument).
- **Session-scoped:** Registrierung auf die lokale `SparkSession`, isoliert auf das aktuelle Notebook oder den aktuellen Job — siehe [Python UDTFs (Session-scoped)](../02%20Session-scoped%20UDFs/03%20Python%20UDTFs.md).

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [Eine UDTF in Unity Catalog erstellen](#erstellen)
3. [Table-Argumente](#table-argumente)
4. [Ein dynamisches Ausgabeschema berechnen (polymorphe UDTFs)](#polymorph)
5. [Environment Isolation](#isolation)
6. [`DETERMINISTIC` setzen](#deterministic)
7. [Praxisbeispiele](#praxisbeispiele)
8. [Limitierungen](#limitierungen)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

- Serverlose Notebooks und Jobs
- Klassisches Compute mit Standard Access Mode (Databricks Runtime 17.1 oder höher)
- SQL-Warehouse (serverlos oder Pro)

---

## <a id="erstellen">2. Eine UDTF in Unity Catalog erstellen</a>

```sql
CREATE OR REPLACE FUNCTION square_numbers(start INT, end INT)
RETURNS TABLE (num INT, squared INT)
LANGUAGE PYTHON
HANDLER 'SquareNumbers'
DETERMINISTIC
AS $$
class SquareNumbers:
    """
    Basic UDTF that computes a sequence of integers
    and includes the square of each number in the range.
    """
    def eval(self, start: int, end: int):
        for num in range(start, end + 1):
            yield (num, num * num)
$$;

SELECT * FROM square_numbers(1, 5);
```

```text
+-----+---------+
| num | squared |
+-----+---------+
| 1   | 1       |
| 2   | 4       |
| 3   | 9       |
| 4   | 16      |
| 5   | 25      |
+-----+---------+
```

---

## <a id="table-argumente">3. Table-Argumente</a>

**Hinweis:** `TABLE`-Argumente werden ab Databricks Runtime 17.2 unterstützt.

UDTFs können ganze Tabellen als Eingabeargumente akzeptieren, was komplexe zustandsbehaftete Transformationen und Aggregationen ermöglicht.

### `eval()`- und `terminate()`-Lifecycle-Methoden

Table-Argumente in UDTFs nutzen zur Verarbeitung jeder Zeile folgende Funktionen:

- **`eval()`:** wird einmal für jede Zeile der Eingabetabelle aufgerufen. Dies ist die zentrale Verarbeitungsmethode und ist Pflicht.
- **`terminate()`:** wird einmal am Ende jeder Partition aufgerufen, nachdem alle Zeilen von `eval()` verarbeitet wurden. Dient dazu, finale aggregierte Ergebnisse zurückzugeben oder Aufräumarbeiten durchzuführen. Diese Methode ist optional, aber essenziell für zustandsbehaftete Operationen wie Aggregationen, Zählungen oder Batch-Verarbeitung.

### Zeilen-Zugriffsmuster

`eval()` erhält Zeilen aus `TABLE`-Argumenten als `pyspark.sql.Row`-Objekte. Auf Werte kann per Spaltenname (`row['id']`, `row['name']`) oder per Index (`row[0]`, `row[1]`) zugegriffen werden.

- **Schema-Flexibilität:** `TABLE`-Argumente können ohne Schemadefinition deklariert werden (z. B. `data TABLE`, `t TABLE`). Die Funktion akzeptiert dann jede Tabellenstruktur — der Code sollte daher prüfen, dass benötigte Spalten vorhanden sind.

Siehe auch die Praxisbeispiele [IP-Adressen gegen CIDR-Netzblöcke matchen](#beispiel-cidr) und [Batch-Bildbeschriftung über Databricks-Vision-Endpoints](#beispiel-vision).

---

## <a id="polymorph">4. Ein dynamisches Ausgabeschema berechnen (polymorphe UDTFs)</a>

```sql
CREATE OR REPLACE FUNCTION extract_fields(json_str STRING, fields STRING)
RETURNS TABLE
LANGUAGE PYTHON
HANDLER 'ExtractFields'
AS $$
class ExtractFields:
    @staticmethod
    def analyze(json_str, fields):

        # Build the output schema from the requested field names
        from pyspark.sql.types import StructType, StructField, StringType
        from pyspark.sql.udtf import AnalyzeResult
        col_names = [f.strip() for f in fields.value.split(",")]
        return AnalyzeResult(
            StructType([StructField(name, StringType()) for name in col_names])
        )

    def eval(self, json_str: str, fields: str):
        # Parse the JSON and yield only the requested fields
        import json
        data = json.loads(json_str)
        col_names = [f.strip() for f in fields.split(",")]
        yield tuple(data.get(name) for name in col_names)
$$;

-- Extract the name and city
SELECT * FROM extract_fields(
  '{"name": "Alice", "age": 30, "city": "Seattle"}',
  'name, city'
);
```

```text
+-------+---------+
| name  | city    |
+-------+---------+
| Alice | Seattle |
+-------+---------+
```

**Warnung:** Bei Unity-Catalog-polymorphen UDTFs müssen sämtliche Imports innerhalb des Methodenkörpers von `analyze()` platziert werden — Top-Level-Imports stehen in der Unity-Catalog-Sandbox-Umgebung nicht zur Verfügung.

### Die `analyze`-Methode definieren

Die Handler-Klasse muss eine `@staticmethod` namens `analyze` enthalten, die dieselben Argumente wie die UDTF akzeptiert und ein `AnalyzeResult` zurückgibt, das das Ausgabeschema beschreibt. Databricks ruft `analyze()` zur Query-Planungszeit auf, um das Schema vor der Ausführung der Funktion aufzulösen.

Jeder Parameter von `analyze` ist eine Instanz der Klasse `AnalyzeArgument`:

| Feld | Beschreibung |
|---|---|
| `dataType` | Der Typ des Eingabearguments als `DataType`. Für Table-Argumente ist dies ein `StructType`, das die Spalten der Tabelle repräsentiert. |
| `value` | Der Wert des Eingabearguments als `Optional[Any]`. Ist `None` für Table-Argumente oder nicht-konstante Ausdrücke. |
| `isTable` | Ob das Eingabeargument ein Table-Argument ist, als `BooleanType`. |
| `isConstantExpression` | Ob das Eingabeargument ein konstant-auswertbarer Ausdruck ist, als `BooleanType`. |

Die `analyze`-Methode gibt eine Instanz der Klasse `AnalyzeResult` zurück:

| Feld | Beschreibung |
|---|---|
| `schema` | Das Schema der Ergebnistabelle als `StructType`. |
| `withSinglePartition` | Wenn `True`, werden alle Eingabezeilen an dieselbe UDTF-Klasseninstanz gesendet. |
| `partitionBy` | Falls nicht leer, werden Eingabezeilen anhand der angegebenen Ausdrücke partitioniert, sodass jede eindeutige Kombination von einer separaten UDTF-Instanz verarbeitet wird. |
| `orderBy` | Falls nicht leer, legt eine Reihenfolge der Zeilen innerhalb jeder Partition fest. |
| `select` | Falls nicht leer, legt fest, welche Spalten des Eingabe-`TABLE`-Arguments die UDTF erhält. |

### Zustand von `analyze` an `eval` weitergeben

```sql
CREATE OR REPLACE FUNCTION tag_language(t TABLE, lang_code STRING)
RETURNS TABLE
LANGUAGE PYTHON
HANDLER 'TagLanguage'
AS $$
class TagLanguage:
    @staticmethod
    def analyze(t, lang_code):
        from dataclasses import dataclass
        from pyspark.sql.types import StructType, StructField, StringType
        from pyspark.sql.udtf import AnalyzeResult

        @dataclass
        class LangResult(AnalyzeResult):
            language: str = ""

        # Resolve the language code to a full name once during planning
        languages = {"en": "English", "es": "Spanish", "fr": "French", "de": "German"}
        return LangResult(
            schema=StructType([
                StructField("text", StringType()),
                StructField("language", StringType())
            ]),
            language=languages.get(lang_code.value, "Unknown")
        )

    def __init__(self, result):
        self._language = result.language

    def eval(self, row, lang_code: str):
        # Tag each row with the pre-resolved language name
        yield (row['text'], self._language)
$$;

SELECT * FROM tag_language(
  TABLE(VALUES ('Hola mundo'), ('Buenos días') t(text)),
  'es'
);
```

```text
+-------------+----------+
| text        | language |
+-------------+----------+
| Hola mundo  | Spanish  |
| Buenos días | Spanish  |
+-------------+----------+
```

### Partitionierung aus der `analyze`-Methode heraus festlegen

Akzeptiert eine polymorphe UDTF ein Table-Argument, kann die `analyze`-Methode steuern, wie Eingabezeilen auf UDTF-Instanzen verteilt werden, indem sie `partitionBy`, `orderBy`, `withSinglePartition` und `select` auf dem `AnalyzeResult` setzt. Das erübrigt für Aufrufer, `PARTITION BY` oder `ORDER BY` in SQL anzugeben.

---

## <a id="isolation">5. Environment Isolation</a>

### Strict Isolation

Um sicherzustellen, dass eine UDTF stets in einer eigenen, vollständig isolierten Umgebung läuft, wird die `STRICT ISOLATION`-Characteristic-Klausel hinzugefügt. Diese sollte bei UDTFs verwendet werden, die:

- Input als Code mit `eval()`, `exec()` oder ähnlichen Funktionen ausführen.
- Dateien ins lokale Dateisystem schreiben.
- globale Variablen oder den Systemzustand verändern.
- Umgebungsvariablen abfragen oder verändern.

```sql
CREATE OR REPLACE TEMPORARY FUNCTION multiply_numbers(factor STRING)
RETURNS TABLE (original INT, scaled INT)
LANGUAGE PYTHON
STRICT ISOLATION
HANDLER 'Multiplier'
AS $$
import os

class Multiplier:
    def eval(self, factor: str):
        # Save the factor as an environment variable
        os.environ["FACTOR"] = factor

        # Read it back and convert it to a number
        scale = int(os.getenv("FACTOR", "1"))

        # Multiply 0 through 4 by the factor
        for i in range(5):
            yield (i, i * scale)
$$;

SELECT * FROM multiply_numbers("3");
```

---

## <a id="deterministic">6. `DETERMINISTIC` setzen, wenn die Funktion konsistente Ergebnisse liefert</a>

`DETERMINISTIC` sollte der Funktionsdefinition hinzugefügt werden, wenn sie für dieselben Eingaben stets dieselben Ausgaben liefert. Das erlaubt Query-Optimierungen, die Performance zu verbessern.

Standardmäßig werden Batch-Unity-Catalog-Python-UDTFs als nicht-deterministisch angenommen, sofern nicht explizit anders deklariert. Beispiele für nicht-deterministische Funktionen: Erzeugen von Zufallswerten, Abfragen der aktuellen Uhrzeit/des aktuellen Datums oder externe API-Aufrufe.

---

## <a id="praxisbeispiele">7. Praxisbeispiele</a>

### Beispiel: `explode` neu implementieren

```sql
CREATE OR REPLACE FUNCTION my_explode(arr ARRAY<STRING>)
RETURNS TABLE (element STRING)
LANGUAGE PYTHON
HANDLER 'MyExplode'
DETERMINISTIC
AS $$
class MyExplode:
    def eval(self, arr):
        if arr is None:
            return
        for element in arr:
            yield (element,)
$$;
```

```sql
SELECT element FROM my_explode(array('apple', 'banana', 'cherry'));
```

```text
+---------+
| element |
+---------+
| apple   |
| banana  |
| cherry  |
+---------+
```

```sql
SELECT s.*, e.element
FROM my_items AS s,
LATERAL my_explode(s.items) AS e;
```

### Beispiel: IP-Adress-Geolokalisierung über eine REST-API

```sql
CREATE OR REPLACE FUNCTION ip_to_location(ip_address STRING)
RETURNS TABLE (city STRING, country STRING)
LANGUAGE PYTHON
HANDLER 'IPToLocationAPI'
AS $$
class IPToLocationAPI:
    def eval(self, ip_address):
        import requests
        api_url = f"https://api.ip-lookup.example.com/{ip_address}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            yield (data.get('city'), data.get('country'))
        except requests.exceptions.RequestException as e:
            # Return nothing if the API request fails
            return
$$;
```

```sql
SELECT
  l.timestamp,
  l.request_path,
  geo.city,
  geo.country
FROM web_logs AS l,
LATERAL ip_to_location(l.ip_address) AS geo;
```

### <a id="beispiel-cidr">Beispiel: IP-Adressen gegen CIDR-Netzblöcke matchen</a>

```sql
-- An example IP logs with both IPv4 and IPv6 addresses
CREATE OR REPLACE TEMPORARY VIEW ip_logs AS
VALUES
  ('log1', '192.168.1.100'),
  ('log2', '10.0.0.5'),
  ('log3', '172.16.0.10'),
  ('log4', '8.8.8.8'),
  ('log5', '2001:db8::1'),
  ('log6', '2001:db8:85a3::8a2e:370:7334'),
  ('log7', 'fe80::1'),
  ('log8', '::1'),
  ('log9', '2001:db8:1234:5678::1')
t(log_id, ip_address);
```

```sql
CREATE OR REPLACE TEMPORARY FUNCTION ip_cidr_matcher(t TABLE)
RETURNS TABLE(log_id STRING, ip_address STRING, network STRING, ip_version INT)
LANGUAGE PYTHON
HANDLER 'IpMatcher'
COMMENT 'Match IP addresses against a list of network CIDR blocks'
AS $$
class IpMatcher:
    def __init__(self):
        import ipaddress
        # Heavy initialization - load networks once per partition
        self.nets = []
        cidrs = ['192.168.0.0/16', '10.0.0.0/8', '172.16.0.0/12',
                 '2001:db8::/32', 'fe80::/10', '::1/128']
        for cidr in cidrs:
            self.nets.append(ipaddress.ip_network(cidr))

    def eval(self, row):
        import ipaddress
	    # Validate that required fields exist
        required_fields = ['log_id', 'ip_address']
        for field in required_fields:
            if field not in row:
                raise ValueError(f"Missing required field: {field}")
        try:
            ip = ipaddress.ip_address(row['ip_address'])
            for net in self.nets:
                if ip in net:
                    yield (row['log_id'], row['ip_address'], str(net), ip.version)
                    return
            yield (row['log_id'], row['ip_address'], None, ip.version)
        except ValueError:
            yield (row['log_id'], row['ip_address'], 'Invalid', None)
$$;
```

```sql
-- Process all IP addresses
SELECT
  *
FROM
  ip_cidr_matcher(t => TABLE(ip_logs))
ORDER BY
  log_id;
```

```text
+--------+-------------------------------+-----------------+-------------+
| log_id | ip_address                    | network         | ip_version  |
+--------+-------------------------------+-----------------+-------------+
| log1   | 192.168.1.100                 | 192.168.0.0/16  | 4           |
| log2   | 10.0.0.5                      | 10.0.0.0/8      | 4           |
| log3   | 172.16.0.10                   | 172.16.0.0/12   | 4           |
| log4   | 8.8.8.8                       | null            | 4           |
| log5   | 2001:db8::1                   | 2001:db8::/32   | 6           |
| log6   | 2001:db8:85a3::8a2e:370:7334  | 2001:db8::/32   | 6           |
| log7   | fe80::1                       | fe80::/10       | 6           |
| log8   | ::1                           | ::1/128         | 6           |
| log9   | 2001:db8:1234:5678::1         | 2001:db8::/32   | 6           |
+--------+-------------------------------+-----------------+-------------+
```

### <a id="beispiel-vision">Beispiel: Batch-Bildbeschriftung über Databricks-Vision-Endpoints</a>

```sql
CREATE OR REPLACE TEMPORARY VIEW sample_images AS
VALUES
    ('https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg', 'scenery'),
    ('https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/1024px-Camponotus_flavomarginatus_ant.jpg', 'animals'),
    ('https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Cat_August_2010-4.jpg/1200px-Cat_August_2010-4.jpg', 'animals'),
    ('https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/M101_hires_STScI-PRC2006-10a.jpg/1024px-M101_hires_STScI-PRC2006-10a.jpg', 'scenery')
images(image_url, category);
```

```sql
CREATE OR REPLACE TEMPORARY FUNCTION batch_inference_image_caption(data TABLE, api_token STRING)
RETURNS TABLE (caption STRING)
LANGUAGE PYTHON
HANDLER 'BatchInferenceImageCaption'
COMMENT 'batch image captioning by sending groups of image URLs to a Databricks vision endpoint and returning concise captions for each image.'
AS $$
class BatchInferenceImageCaption:
    def __init__(self):
        self.batch_size = 3
        self.vision_endpoint = "databricks-claude-sonnet-4-5"
        self.workspace_url = "<workspace-url>"
        self.image_buffer = []
        self.results = []

    def eval(self, row, api_token):
        self.image_buffer.append((str(row[0]), api_token))
        if len(self.image_buffer) >= self.batch_size:
            self._process_batch()

    def terminate(self):
        if self.image_buffer:
            self._process_batch()
        for caption in self.results:
            yield (caption,)

    def _process_batch(self):
        batch_data = self.image_buffer.copy()
        self.image_buffer.clear()

        import base64
        import httpx
        import requests

        # API request timeout in seconds
        api_timeout = 60
        # Maximum tokens for vision model response
        max_response_tokens = 300
        # Temperature controls randomness (lower = more deterministic)
        model_temperature = 0.3

        # create a batch for the images
        batch_images = []
        api_token = batch_data[0][1] if batch_data else None

        for image_url, _ in batch_data:
            image_response = httpx.get(image_url, timeout=15)
            image_data = base64.standard_b64encode(image_response.content).decode("utf-8")
            batch_images.append(image_data)

        content_items = [{
            "type": "text",
            "text": "Provide brief captions for these images, one per line."
        }]
        for img_data in batch_images:
            content_items.append({
                "type": "image_url",
                "image_url": {
                    "url": "data:image/jpeg;base64," + img_data
                }
            })

        payload = {
            "messages": [{
                "role": "user",
                "content": content_items
            }],
            "max_tokens": max_response_tokens,
            "temperature": model_temperature
        }

        response = requests.post(
            self.workspace_url + "/serving-endpoints/" +
            self.vision_endpoint + "/invocations",
            headers={
                'Authorization': 'Bearer ' + api_token,
                'Content-Type': 'application/json'
            },
            json=payload,
            timeout=api_timeout
        )

        result = response.json()
        batch_response = result['choices'][0]['message']['content'].strip()

        lines = batch_response.split('\n')
        captions = [line.strip() for line in lines if line.strip()]

        while len(captions) < len(batch_data):
            captions.append(batch_response)

        self.results.extend(captions[:len(batch_data)])
$$;
```

```sql
SELECT
  caption
FROM
  batch_inference_image_caption(
    data => TABLE(sample_images),
    api_token => secret('your_secret_scope', 'api_token')
  )
```

```text
+---------------------------------------------------------------------------------------------------------------+
| caption                                                                                                       |
+---------------------------------------------------------------------------------------------------------------+
| Wooden boardwalk cutting through vibrant wetland grasses under blue skies                                     |
| Black ant in detailed macro photography standing on a textured surface                                        |
| Tabby cat lounging comfortably on a white ledge against a white wall                                          |
| Stunning spiral galaxy with bright central core and sweeping blue-white arms against the black void of space. |
+---------------------------------------------------------------------------------------------------------------+
```

Mit expliziter Partitionierung nach `category`:

```sql
SELECT
  *
FROM
  batch_inference_image_caption(
    TABLE(sample_images)
    PARTITION BY category ORDER BY (category),
    secret('your_secret_scope', 'api_token')
  )
```

```text
+------------------------------------------------------------------------------------------------------+
| caption                                                                                                |
+------------------------------------------------------------------------------------------------------+
| Black ant in detailed macro photography standing on a textured surface                               |
| Stunning spiral galaxy with bright center and sweeping blue-tinged arms against the black of space.  |
| Tabby cat lounging comfortably on white ledge against white wall                                     |
| Wooden boardwalk cutting through lush wetland grasses under blue skies                               |
+------------------------------------------------------------------------------------------------------+
```

### Beispiel: ROC-Kurve und AUC-Berechnung zur ML-Modellevaluierung

Merkmale dieses Beispiels:

- **Nutzung externer Bibliotheken:** integriert scikit-learn für die ROC-Kurven-Berechnung
- **Zustandsbehaftete Aggregation:** akkumuliert Vorhersagen über alle Zeilen, bevor Metriken berechnet werden
- **Nutzung von `terminate()`:** verarbeitet den vollständigen Datensatz und gibt Ergebnisse erst zurück, nachdem alle Zeilen ausgewertet wurden
- **Fehlerbehandlung:** validiert, dass benötigte Spalten in der Eingabetabelle vorhanden sind

```sql
CREATE OR REPLACE TEMPORARY FUNCTION compute_roc_curve(t TABLE)
RETURNS TABLE (threshold DOUBLE, true_positive_rate DOUBLE, false_positive_rate DOUBLE, auc DOUBLE)
LANGUAGE PYTHON
HANDLER 'ROCCalculator'
COMMENT 'Compute ROC curve and AUC using scikit-learn'
AS $$
class ROCCalculator:
    def __init__(self):
        from sklearn import metrics
        self._roc_curve = metrics.roc_curve
        self._roc_auc_score = metrics.roc_auc_score

        self._true_labels = []
        self._predicted_scores = []

    def eval(self, row):
        if 'y_true' not in row or 'y_score' not in row:
            raise KeyError("Required columns 'y_true' and 'y_score' not found")

        true_label = row['y_true']
        predicted_score = row['y_score']

        label = float(true_label)
        self._true_labels.append(label)
        self._predicted_scores.append(float(predicted_score))

    def terminate(self):
        false_pos_rate, true_pos_rate, thresholds = self._roc_curve(
            self._true_labels,
            self._predicted_scores,
            drop_intermediate=False
        )

        auc_score = float(self._roc_auc_score(self._true_labels, self._predicted_scores))

        for threshold, tpr, fpr in zip(thresholds, true_pos_rate, false_pos_rate):
            yield float(threshold), float(tpr), float(fpr), auc_score
$$;
```

```sql
CREATE OR REPLACE TEMPORARY VIEW binary_classification_data AS
SELECT *
FROM VALUES
  ( 1, 1.0, 0.95, 'high_confidence_positive'),
  ( 2, 1.0, 0.87, 'high_confidence_positive'),
  ( 3, 1.0, 0.82, 'medium_confidence_positive'),
  ( 4, 0.0, 0.78, 'false_positive'),
  ( 5, 1.0, 0.71, 'medium_confidence_positive'),
  ( 6, 0.0, 0.65, 'false_positive'),
  ( 7, 0.0, 0.58, 'true_negative'),
  ( 8, 1.0, 0.52, 'low_confidence_positive'),
  ( 9, 0.0, 0.45, 'true_negative'),
  (10, 0.0, 0.38, 'true_negative'),
  (11, 1.0, 0.31, 'low_confidence_positive'),
  (12, 0.0, 0.15, 'true_negative'),
  (13, 0.0, 0.08, 'high_confidence_negative'),
  (14, 0.0, 0.03, 'high_confidence_negative')
AS data(sample_id, y_true, y_score, prediction_type);
```

```sql
SELECT
    threshold,
    true_positive_rate,
    false_positive_rate,
    auc
FROM compute_roc_curve(
  TABLE(
    SELECT y_true, y_score
    FROM binary_classification_data
    WHERE y_true IS NOT NULL AND y_score IS NOT NULL
    ORDER BY sample_id
  )
)
ORDER BY threshold DESC;
```

```text
+-----------+---------------------+----------------------+-------+
| threshold | true_positive_rate  | false_positive_rate  | auc   |
+-----------+---------------------+----------------------+-------+
| 1.95      | 0.0                 | 0.0                  | 0.786 |
| 0.95      | 0.167               | 0.0                  | 0.786 |
| 0.87      | 0.333               | 0.0                  | 0.786 |
| 0.82      | 0.5                 | 0.0                  | 0.786 |
| 0.78      | 0.5                 | 0.125                | 0.786 |
| 0.71      | 0.667               | 0.125                | 0.786 |
| 0.65      | 0.667               | 0.25                 | 0.786 |
| 0.58      | 0.667               | 0.375                | 0.786 |
| 0.52      | 0.833               | 0.375                | 0.786 |
| 0.45      | 0.833               | 0.5                  | 0.786 |
| 0.38      | 0.833               | 0.625                | 0.786 |
| 0.31      | 1.0                 | 0.625                | 0.786 |
| 0.15      | 1.0                 | 0.75                 | 0.786 |
| 0.08      | 1.0                 | 0.875                | 0.786 |
| 0.03      | 1.0                 | 1.0                  | 0.786 |
+-----------+---------------------+----------------------+-------+
```

### Beispiel: Dynamische Spaltenprojektion aus einem Table-Argument

```sql
CREATE OR REPLACE FUNCTION project_columns(t TABLE, columns STRING)
RETURNS TABLE
LANGUAGE PYTHON
HANDLER 'ProjectColumns'
AS $$
class ProjectColumns:
    @staticmethod
    def analyze(t, columns):
        from pyspark.sql.types import StructType
        from pyspark.sql.udtf import AnalyzeResult

        requested = [c.strip() for c in columns.value.split(",")]
        input_schema = t.dataType
        output_fields = []
        for field in input_schema.fields:
            if field.name in requested:
                output_fields.append(field)
        if not output_fields:
            raise ValueError(
                f"None of the requested columns {requested} "
                f"exist in the input table"
            )
        return AnalyzeResult(schema=StructType(output_fields))

    def eval(self, row, columns: str):
        requested = [c.strip() for c in columns.split(",")]
        yield tuple(row[col] for col in requested if col in row)
$$;
```

```sql
SELECT * FROM project_columns(
  TABLE(SELECT * FROM samples.nyctaxi.trips LIMIT 5),
  'pickup_zip, dropoff_zip, fare_amount'
);
```

---

## <a id="limitierungen">8. Limitierungen</a>

- Unity-Catalog-Service-Credentials werden nicht unterstützt.
- Custom Dependencies werden nicht unterstützt.
