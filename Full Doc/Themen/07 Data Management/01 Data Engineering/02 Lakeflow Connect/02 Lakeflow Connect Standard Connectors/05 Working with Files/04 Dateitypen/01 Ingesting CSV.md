```python
SELECT * 
FROM csv.`/Volumes/dbacademy_ecommerce/v01/raw/sales-csv`
LIMIT 5;
```

```python
spark.sql(f'''
SELECT *
FROM text.`{DA.paths.working_dir}/csv_demo_files/lab_malformed_data.csv`
'''
).display()
```

```python
SELECT * 
FROM read_files(
        "/Volumes/dbacademy_ecommerce/v01/raw/sales-csv",
        format => "csv",
        sep => "|",
        header => true
      )
LIMIT 5;


SELECT *
FROM read_files(
        DA.paths_working_dir || '/csv_demo_files/malformed_example_1_data.csv',
        format => "csv",
        sep => "|",
        header => true,
        schema => '''
            order_id INT, 
            email STRING, 
            transactions_timestamp BIGINT''', 
        rescueddatacolumn => '_rescued_data'    -- Create the _rescued_data column
      );
```

```python
df = (spark
      .read 
      .option("header", True) 
      .option("sep","|") 
      .option("rescuedDataColumn", "_rescued_data")       # <--------- Add the rescued data column
      .csv("/Volumes/dbacademy_ecommerce/v01/raw/sales-csv")
    )
```

```python
CREATE TABLE sales_bronze AS
SELECT 
  *,
  _metadata.file_modification_time AS file_modification_time,
  _metadata.file_name AS source_file, 
  current_timestamp() as ingestion_time 
FROM read_files(
        "/Volumes/dbacademy_ecommerce/v01/raw/sales-csv",
        format => "csv",
        sep => "|",
        header => true
      );
```

```python
def get_health_csv_schema():
    return StructType([
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

def read_health_data(csv_path, schema):
    return (
        spark
        .read
        .format("csv")
        .option("header", "true")  # Use the header row for column names
        .schema(schema)            # Apply the defined schema
        .load(csv_path)            # Load the CSV data
        .select(
            "*",
            "_metadata.file_name",                        # Include file name from metadata
            "_metadata.file_modification_time",           # Include file modification timestamp
            current_timestamp().alias("processing_time")  # Add a processing time column
        )
    )
```

---

*Verschoben aus `_read_files.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

### CSV-spezifische Optionen (Auswahl, gemeinsam mit `spark.read`)

| Option | Standardwert | Beschreibung |
|---|---|---|
| `sep` / `delimiter` | `,` | Trennzeichen zwischen Spalten. |
| `header` | `false` | Ob die CSV-Dateien eine Kopfzeile besitzen. Bei Schema-Inferenz nimmt `read_files`/Auto Loader an, dass Dateien Header besitzen. |
| `inferSchema` | `false` | Für `spark.read.csv()`; bei `read_files`/Auto Loader stattdessen `inferColumnTypes` verwenden. |
| `mode` | `PERMISSIVE` | `PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`. |
| `columnNameOfCorruptRecord` | `_corrupt_record` | Spalte für nicht parsbare Datensätze; bleibt bei `DROPMALFORMED` leer. |
| `enforceSchema` | `true` | Erzwingt das angegebene/inferierte Schema und ignoriert Header. Wird bei Auto Loader mit aktivem Rescue/Schema-Evolution standardmäßig ignoriert. |
| `failOnUnknownFields` | `false` | Bricht ab, wenn ein CSV-Datensatz Spalten enthält, die nicht im Schema stehen (statt sie stillschweigend zu verwerfen/retten). |
| `failOnWidenedFields` | `false` | Bricht ab, wenn ein Feldwert nur durch Typ-Erweiterung zum Schema passt, statt ihn stillschweigend zu retten. `failOnUnknownFields => true` kann den Effekt dieser Option überdecken. |
| `rescuedDataColumn` | keiner | Standardmäßig aktiv bei Auto Loader/`read_files`. |
| `multiLine` | `false` | Ob CSV-Datensätze mehrere Zeilen umfassen. |
| `quote` | `"` | Zeichen zum Maskieren von Werten, die das Trennzeichen enthalten. |
| `escape` | `\` | Escape-Zeichen. |
| `nullValue` | leerer String | String-Repräsentation eines Null-Werts. |
| `dateFormat` | `yyyy-MM-dd` | Format für Datumsangaben. |
| `timestampFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Format für Zeitstempel. |
| `skipRows` | `0` | Anzahl zu überspringender Zeilen am Dateianfang (inkl. Kommentar-/Leerzeilen). |
| `maxColumns` | `20480` | Harte Obergrenze für die Spaltenanzahl pro Datensatz. |
| `unescapedQuoteHandling` | `STOP_AT_DELIMITER` | Strategie für nicht maskierte Anführungszeichen (`STOP_AT_CLOSING_QUOTE`, `BACK_TO_DELIMITER`, `STOP_AT_DELIMITER`, `SKIP_VALUE`, `RAISE_ERROR`). |
| `singleVariantColumn` | keiner | Liest den gesamten CSV-Datensatz in eine einzelne `VARIANT`-Spalte statt Feld für Feld zu parsen. Erfordert `header=true`. |

```sql
-- Robustes CSV-Lesen mit expliziter Fehlerbehandlung
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv',
    header => true,
    sep => ';',
    mode => 'PERMISSIVE',
    columnNameOfCorruptRecord => '_corrupt_record',
    dateFormat => 'dd.MM.yyyy');
```

---

*Verschoben aus `_spark_read.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

### CSV-spezifische Optionen (Auswahl, aus der CSV-Optionstabelle)

| Option | Standardwert | Beschreibung |
|---|---|---|
| `sep` / `delimiter` | `,` | *"The separator string between columns."* |
| `header` | `false` | Ob die CSV-Dateien eine Kopfzeile besitzen. |
| `inferSchema` | `false` | Siehe `_spark_read.md`, Abschnitt 2. |
| `mode` | `PERMISSIVE` | Parser-Modus: `PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`. |
| `columnNameOfCorruptRecord` | `_corrupt_record` | Spalte für nicht parsbare Datensätze. |
| `enforceSchema` | `true` | *"Whether to forcibly apply the specified or inferred schema to the CSV files."* (Wert per zwei unabhängigen Abrufen bestätigt.) |
| `failOnUnknownFields` | `false` | *"Whether to fail when the CSV record contains columns not present in schema."* |
| `failOnWidenedFields` | `false` | *"Whether to fail when a field value cannot be parsed without widening."* `failOnUnknownFields => true` kann diesen Effekt überdecken. |
| `rescuedDataColumn` | keiner (`None`) | Bei `spark.read` **nicht** standardmäßig aktiv — muss explizit gesetzt werden. |
| `multiLine` | `false` | Ob CSV-Datensätze mehrere Zeilen umfassen. |
| `quote` | `"` | Zeichen zum Maskieren von Werten, die das Trennzeichen enthalten. |
| `escape` | `\` | Escape-Zeichen. |
| `nullValue` | leerer String | String-Repräsentation eines Null-Werts. |
| `dateFormat` | `yyyy-MM-dd` | Format für Datumsangaben. |
| `timestampFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Format für Zeitstempel. |
| `skipRows` | `0` | Anzahl zu überspringender Zeilen am Dateianfang. |
| `maxColumns` | `20480` | Harte Obergrenze für die Spaltenanzahl pro Datensatz. |
| `unescapedQuoteHandling` | `STOP_AT_DELIMITER` | Strategie für nicht maskierte Anführungszeichen; mögliche Werte laut Doku: `STOP_AT_CLOSING_QUOTE`, `BACK_TO_DELIMITER`, `STOP_AT_DELIMITER`, `SKIP_VALUE`, `RAISE_ERROR`. |
| `singleVariantColumn` | keiner | *"When set to a column name, reads the entire CSV record into a single `VariantType` column with that name instead of parsing each field into its own column. Requires `header=true`."* |

```python
# Robustes CSV-Lesen mit expliziter Fehlerbehandlung
df = (spark.read
      .option("header", True)
      .option("sep", ";")
      .option("mode", "PERMISSIVE")
      .option("columnNameOfCorruptRecord", "_corrupt_record")
      .option("dateFormat", "dd.MM.yyyy")
      .csv("s3://bucket/path"))
```

---

*Ursprünglich aus der früheren Sammeldatei `_autoloader.md` (Nutzer-Notizen `GenertingSchema.md`, verifiziert/korrigiert); die Auto-Loader-Referenz liegt jetzt im Ordner `../06 Auto Loader/`:*

Die Notizen enthielten ein CTAS-Beispiel mit `read_files` und dem Parameter `inferSchema => 'false'`. **Korrektur:** `inferSchema` ist laut der Spark-API-Optionsreferenz eine CSV-spezifische Option des `DataFrameReader` (Standardwert ebenfalls `false`, Beschreibung: Ob die Datentypen der geparsten CSV-Datensätze inferiert werden sollen, oder ob angenommen werden soll, dass alle Spalten vom Typ `StringType` sind. Erfordert bei `true` einen zusätzlichen Durchlauf über die Daten. Für Auto Loader stattdessen `cloudFiles.inferColumnTypes` verwenden.) — die Doku verweist also für den `cloudFiles`/Auto-Loader-Kontext ausdrücklich auf `cloudFiles.inferColumnTypes`, und `read_files` selbst dokumentiert (siehe `_read_files.md` Abschnitt 2) ausschließlich `inferColumnTypes`, nicht `inferSchema`, als eigenen Options-Namen. Nachfolgend die sinngemäß korrigierte Fassung des Beispiels (im gezeigten Fall ist die Option ohnehin folgenlos, da ein explizites `schema` angegeben ist und dieses die Inferenz überspringt):

```sql
-- Angepasst aus GenertingSchema.md: inferSchema -> inferColumnTypes korrigiert
CREATE OR REPLACE TABLE sdp_lab_1_bronze.employees_bronze_lab08
AS
SELECT
  *,
  current_timestamp() AS ingestion_time,
  _metadata.file_name AS raw_file_name
FROM read_files(
  '/Volumes/' || my_catalog || '/sdp_lab_1_bronze/lab_files',
  format => 'CSV',
  -- Explizites Schema überspringt die Inferenz ohnehin vollständig
  schema => '
    EmployeeID STRING,
    FirstName STRING,
    Country STRING,
    Department STRING,
    Salary DOUBLE,
    HireDate DATE,
    Operation STRING,
    ProcessDate DATE
  ',
  header => 'true',
  inferColumnTypes => 'false'
);
```

Die zwei weiteren Notiz-Beispiele nutzen `spark.read.option("inferSchema", "true").csv(...)` bzw. ein explizites `StructType`-Schema — das ist reiner Batch-`DataFrameReader`-Kontext (`spark.read`, nicht `spark.readStream`/`cloudFiles`), für den `inferSchema` tatsächlich der korrekte, dokumentierte Options-Name ist:

```python
# Batch-Vergleich (spark.read, NICHT Auto Loader): inferSchema ist hier der korrekte Name
sdf = (spark.read
       .format("csv")
       .option("header", "true")
       .option("inferSchema", "true")
       .load(csv_file_path))
```

Die private Notiz behauptet zusätzlich, `inferSchema => true` weise Spark an, die gesamte Datei zunächst vollständig zu durchsuchen, um Datentypen zu bestimmen. **Sinngemäß bestätigt:** Die offizielle Beschreibung der CSV-Option `inferSchema` formuliert es so, dass bei `true` ein zusätzlicher Durchlauf über die Daten erforderlich ist — inhaltlich gleichbedeutend, aber nicht wortgleich mit der Notiz. Die exakte englische Formulierung "scans through the entire file" wurde in keiner offiziellen Databricks-Quelle wörtlich gefunden.
