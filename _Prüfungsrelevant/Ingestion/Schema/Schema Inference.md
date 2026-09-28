# Schema Inference

**Schema Inference** = Databricks **leitet Spalten und Datentypen automatisch aus dem Dateiinhalt ab**, wenn kein Schema angegeben wird. Ein **explizites** `schema` überspringt die Inferenz (schneller, deterministisch) — wie man es per DDL-String oder `StructType`/`StructField` definiert und mit `.schema()` übergibt: [Schema Definition.md](Schema%20Definition.md).

## 1. Databricks SQL-Tabellenwertfunktion `read_files()`

Wird genutzt, um Dateien direkt aus dem Cloud-Objektspeicher (z. B. S3, ADLS) via Databricks SQL abzufragen. [[1](https://docs.databricks.com/gcp/en/ingestion/google-drive)]

- **Standardverhalten (Default):** **AKTIV**. Wenn kein Schema angegeben wird, leitet die Funktion die Struktur automatisch ab.
- **Verhalten bei Textformaten (JSON/CSV):** Sie versucht sofort, **exakte Datentypen** (wie `INT`, `DOUBLE`, `TIMESTAMP`) zu inferieren. Dafür wird eine Stichprobe analysiert. [[1](https://docs.databricks.com/gcp/en/ingestion/cloud-object-storage/auto-loader/schema)]
- **Änderung des Verhaltens:**
  - *Schema fest vorgeben:* Übergeben Sie das Argument `schema => 'id INT, name STRING'`, um die Inferenz komplett zu überspringen.
  - *Sicherer String-Modus:* Setzen Sie `inferColumnTypes => false`, um Typkonflikte zu vermeiden (Spalten werden primär als `STRING` gelesen).
  - *Teilweise Korrektur:* Mit `schemaHints => 'user_id STRING'` überschreiben Sie die Inferenz nur für spezifische Spalten. [[1](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema)]

## 2. Databricks Auto Loader (`cloudFiles`)

Verarbeitet Dateien inkrementell und hocheffizient im Daten-Streaming über `spark.readStream` mit dem Format `cloudFiles`. [[1](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/patterns), [2](https://medium.com/@divyanshgoyal8989/databricks-autoloader-schema-evolution-vs-schema-inference-070190a4e23f)]

- **Standardverhalten (Default):** **AKTIV**. Bei der ersten Ausführung tastet er eine Stichprobe ab, um das Schema zu inferieren, und speichert dieses in einem Verzeichnis (`cloudFiles.schemaLocation`). [[1](https://medium.com/@divyanshgoyal8989/databricks-autoloader-schema-evolution-vs-schema-inference-070190a4e23f), [2](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/patterns)]
- **Verhalten bei Textformaten (JSON/CSV/XML):** Um Inferenz-Konflikte bei zukünftigen Schema-Änderungen zu vermeiden, liest der Auto Loader standardmäßig **alle Spalten als `STRING`** ein (Ausnahme: *Parquet* und *Avro*, da diese Typen nativ speichern). [[1](https://community.databricks.com/t5/get-started-discussions/best-practices-for-using-autoloader/td-p/155231), [2](https://docs.databricks.com/gcp/en/ingestion/cloud-object-storage/auto-loader/schema)]
- **Änderung des Verhaltens:**
  - *Präzise Typ-Inferenz erzwingen:* Aktivieren Sie `.option("cloudFiles.inferColumnTypes", "true")`, damit auch bei JSON/CSV echte Datentypen ermittelt werden.
  - *Schema Hints:* Mit `.option("cloudFiles.schemaHints", "id BIGINT")` erzwingen Sie Typen für ausgewählte Spalten. [[1](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema), [2](https://medium.com/@divyanshgoyal8989/databricks-autoloader-schema-evolution-vs-schema-inference-070190a4e23f)]

## 3. Standard Apache Spark Streaming (`spark.readStream()` ohne Auto Loader)

Der klassische, native Streaming-Reader von Apache Spark (z. B. `spark.readStream.format("json").load(...)`). [[1](https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/csv), [2](https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader)]

- **Standardverhalten (Default):** **deaktiviert**
- . Bei Standard-Streams ist die Schema-Inferenz absichtlich blockiert. Spark verlangt zwingend, dass Sie ein Schema manuell per `.schema(userSchema)` definieren. Andernfalls bricht der Stream sofort mit einer `AnalysisException` ab ("Streaming source ... requires a user-specified schema"). [[1](https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader), [2](https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/csv)]
- **Änderung des Verhaltens:**
  - *Inferenz erzwingen (Nicht empfohlen für Produktion):* Sie können die globale Spark-Konfiguration `spark.sql.streaming.forceDeleteTempCheckpointLocation` oder `spark.sql.streaming.schemaInference` auf `true` setzen, um die Inferenz zu erzwingen. Dies führt jedoch dazu, dass Spark die Quelldaten vorab scannen muss, was bei unendlichen Streams problematisch ist.

## 4. Standard Apache Spark Batch Reader (`spark.read`)

Der klassische Batch-Reader für DataFrames in PySpark oder Spark SQL. [[1](https://docs.databricks.com/gcp/en/ingestion/onedrive)]

- **Standardverhalten (Default):** **deaktiviert**. Ohne manuelle Aktivierung findet keine Inferenz statt.
- **Verhalten bei Textformaten (JSON/CSV):** Spark liest standardmäßig alle Spalten strikt als **`STRING`** ein, sofern kein explizites Schema definiert ist.
- **Änderung des Verhaltens:**
  - *Inferenz aktivieren:* Sie müssen die Inferenz explizit über `.option("inferSchema", "true")` einschalten. Spark führt dann einen zusätzlichen Vorab-Scan der Daten durch. [[1](https://docs.databricks.com/gcp/en/spark/api-options), [2](https://docs.databricks.com/gcp/en/ingestion/onedrive), [3](https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/csv)]

## 5. Die SQL-Funktion `from_json()`

Transformiert einen JSON-String (z. B. aus einer Kafka-Message) in eine strukturierte Spalte (`StructType`). [[1](https://docs.databricks.com/aws/en/data-engineering/schema-evolution), [2](https://docs.databricks.com/aws/fr/sql/language-manual/functions/from_json)]

- **Standardverhalten (Default):** **deaktiviert** (im normalen Spark/SQL-Kontext). Die Funktion verlangt standardmäßig zwingend ein manuell definiertes Zielschema als zweiten Parameter. [[1](https://docs.databricks.com/aws/fr/sql/language-manual/functions/from_json)]
- **Ausnahme in Databricks Pipelines:** Wenn `from_json()` innerhalb von automatisierten Pipelines wie *Lakeflow* oder *Delta Live Tables (DLT)* genutzt wird, ist die Schema-Inferenz **AKTIV**. [[1](https://docs.databricks.com/aws/en/data-engineering/schema-evolution), [2](https://docs.databricks.com/aws/fr/sql/language-manual/functions/from_json)]
- **Änderung des Verhaltens:** In unterstützten Pipelines aktivieren und steuern Sie die Inferenz durch Angabe eines `schemaLocationKey`, wodurch das JSON-Schema automatisch bei Änderungen angepasst wird. [[1](https://docs.databricks.com/aws/fr/sql/language-manual/functions/from_json)]

## 6. Die SQL-Funktion `from_csv()`

Analog zu `from_json()`, transformiert diese Funktion einen CSV-String in eine strukturierte Spalte. [[1](https://docs.databricks.com/aws/en/pyspark/reference/functions/from_csv)]

- **Standardverhalten (Default):** **deaktiviert**. Die Funktion benötigt als zweiten Parameter zwingend ein Schema (entweder als DDL-String oder ein struct). Ohne Angabe oder zusätzliche Optionen findet keine Inferenz statt. [[1](https://docs.databricks.com/aws/en/sql/language-manual/functions/from_csv), [2](https://docs.databricks.com/aws/en/pyspark/reference/functions/from_csv)]
- **Verhalten bei Textformaten:** Wenn Optionen übergeben werden, ohne `inferSchema` einzuschalten, werden alle Felder des übergebenen Schemas strikt angewendet oder als `STRING` interpretiert. Sie unterstützt im Gegensatz zu `from_json()` **keine** automatische Inferenz in DLT/Lakeflow Pipelines. [[1](https://docs.databricks.com/gcp/en/spark/api-options)]
- **Änderung des Verhaltens:**
  - *Inferenz für die Struktur aktivieren:* Sie können die Spark-Hilfsfunktion `schema_of_csv()` als zweiten Parameter übergeben (z. B. `from_csv(col, schema_of_csv("1,2,3"))`), um das Schema dynamisch aus einem Beispiel-String abzuleiten.
  - *Datentypen inferieren:* Sie können im optionalen Eigenschafts-Map das Argument `inferSchema -> "true"` übergeben, damit die CSV-Werte tiefergehend analysiert werden. [[1](https://docs.databricks.com/aws/en/pyspark/reference/functions/from_csv), [2](https://docs.databricks.com/aws/en/sql/language-manual/functions/from_csv), [3](https://docs.databricks.com/gcp/en/spark/api-options)]







