# Vergleich: `read_files` vs. `spark.read` / `spark.read.load()`

Dieses Dokument vergleicht die beiden Databricks-Lesemechanismen `read_files` (SQL-Tabellenfunktion) und `spark.read`/`spark.read.load()` (`DataFrameReader`, PySpark) anhand der Aspekte, die zuvor in den jeweiligen Notebooks behandelt wurden: Schema-Inferenz, `schemaHints`, `_metadata`-Spalte, Batch/Streaming-Fähigkeit und Datei-Tracking. Basis sind ausschließlich die offiziellen Databricks-Dokumentationsseiten, die auch in den beiden Notebooks zitiert wurden.

## Kurzübersicht

| Aspekt | `read_files` | `spark.read` / `spark.read.load()` | Auto Loader (`cloudFiles`) |
|---|---|---|---|
| **Kategorie** | SQL-Tabellenfunktion (Databricks SQL) | PySpark-/Scala-API (`DataFrameReader`) | Structured-Streaming-Quelle (`spark.readStream.format("cloudFiles")`) |
| **Grundzweck** | Dateien direkt in SQL-Abfragen (`SELECT`, CTAS) einlesen | Dateien/Tabellen in ein `DataFrame` laden | Neue Dateien inkrementell und fortlaufend aus Cloud-Speicher verarbeiten |
| **Schema-Inferenz** | ✅ Ja, mit einheitlichem Schema über alle Dateien | ✅ Ja, formatabhängig (zusätzlicher Lesedurchlauf) | ✅ Ja, inkl. Erkennung von Schema-Drift zwischen Läufen |
| **`schemaHints`** | ✅ Ja, dokumentierte Option | ❌ Nicht vorhanden — nur vollständiges `.schema()` möglich | ✅ Ja — nativ, `schemaHints` ist ursprünglich eine Auto-Loader-Option |
| **`_metadata`-Spalte** | ✅ Ja, muss explizit ausgewählt werden | ✅ Ja, muss explizit ausgewählt werden | ✅ Ja, ebenfalls explizit auszuwählen |
| **Batch-fähig** | ✅ Ja (`SELECT * FROM read_files(...)`) | ✅ Ja (Standardmodus) | ❌ Nein — ausschließlich Streaming-Quelle |
| **Streaming-fähig** | ✅ Ja, mit `STREAM read_files(...)` — **gleiche Funktion, anderes Schlüsselwort** | ✅ Ja, aber nur über die **separate** Schnittstelle `spark.readStream` | ✅ Ja — das ist der einzige Modus |
| **Datei-Tracking (Batch)** | ❌ Nein | ❌ Nein | – (kein Batch-Modus vorhanden) |
| **Datei-Tracking (Streaming)** | ✅ Ja, via Auto Loader intern (Checkpoint) | ✅ Ja, via `spark.readStream` + `checkpointLocation` | ✅ Ja — RocksDB-Checkpoint, exactly-once, kein eigener Zustand nötig |
| **Tracking ein-/ausschaltbar?** | Nur im Streaming-Kontext (`allowOverwrites`, `includeExistingFiles`) | Nicht bei `spark.read`; nur durch Wechsel zu `spark.readStream` | Ja — direkt über `cloudFiles.allowOverwrites`, `cloudFiles.includeExistingFiles`, `cloudFiles.maxFileAge` |
| **Skalierung bei vielen Dateien** | Nicht spezifisch dokumentiert | Nicht spezifisch dokumentiert | ✅ Kosten skalieren mit Anzahl Dateien statt Verzeichnissen; verarbeitet laut Doku Milliarden Dateien |
| **Datei-Erkennungskosten** | Nicht spezifisch dokumentiert | Nicht spezifisch dokumentiert | ✅ Optional per File-Notification-Mode reduzierbar (kein Directory Listing nötig) |

---

## 1. Grundzweck und Kontext

`read_files` ist eine **SQL-Tabellenfunktion**, gedacht für den direkten Einsatz in `SELECT`-Abfragen, CTAS-Statements oder Streaming Tables innerhalb von Databricks SQL:

> *"Reads files under a provided location and returns the data in tabular form."*
> — [read_files table-valued function | Databricks on AWS](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files)

`spark.read` (`DataFrameReader`) ist die **programmatische PySpark-/Scala-Schnittstelle**, um Daten als `DataFrame` zu laden:

> *"Interface used to load a DataFrame from external storage systems (e.g. file systems, key-value stores, etc)."*
> — [DataFrameReader class | Databricks on AWS](https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader)

**Praktische Konsequenz:** Beide lösen dieselbe grundlegende Aufgabe (Dateien einlesen), aber für unterschiedliche Werkzeuge — `read_files` für SQL-Nutzer/SQL-Notebooks, `spark.read` für Python-/Scala-Notebooks. Die Spark-API-Optionsreferenz bestätigt, dass beide dieselben zugrunde liegenden Leseoptionen teilen:

> *"Use these options with DataFrameReader.option(), DataFrameReader.options(), read_files, COPY INTO, and Auto Loader to control how Databricks reads data files."*
> — [Spark API options reference | Databricks on AWS](https://docs.databricks.com/aws/en/spark/api-options)

```sql
-- read_files (SQL)
SELECT * FROM read_files('s3://bucket/path', format => 'json', multiLine => true);
```
```python
# spark.read (PySpark) — äquivalente Optionen
df = spark.read.format("json").option("multiLine", True).load("/path/to/data")
```

---

## 2. Schema-Inferenz

**Beide** Methoden leiten das Schema automatisch ab, wenn keines angegeben wird — mit leicht unterschiedlicher Dokumentation der Details.

### `read_files`

> *"If a schema is not provided, read_files attempts to infer a unified schema across the discovered files, which requires reading all the files unless a LIMIT statement is used."*
> — [read_files table-valued function | Databricks on AWS](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files)

```sql
-- Explizites Schema, um vollständige Schema-Inferenz zu vermeiden
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv',
    schema => 'id int, ts timestamp, event string');
```

### `spark.read`

> *"Specifies the input schema. Some data sources (such as JSON) can infer the input schema automatically from data. By specifying the schema here, the underlying data source can skip the schema inference step, which speeds up data loading."*
> — [schema (DataFrameReader) | Databricks on AWS](https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/schema)

Für JSON zusätzlich explizit dokumentiert:

> *"If schema is not specified, this function reads the input once to determine the input schema."*
> — [json (DataFrameReader) | Databricks on AWS](https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/json)

```python
# Explizites Schema, um den zusätzlichen Lesedurchlauf zu vermeiden
df = spark.read.schema("id int, ts timestamp, event string").json("s3://bucket/path")
```

**Unterschied:** Bei `read_files` ist die Notwendigkeit, für eine vollständige Inferenz **alle** Dateien zu lesen, explizit dokumentiert (inkl. Hinweis, dass auch bei `LIMIT` mehr Dateien gelesen werden können, um ein repräsentatives Schema zu erhalten). Bei `spark.read` wird dies nur formatspezifisch erwähnt (z. B. bei JSON: "reads the input once").

---

## 3. `schemaHints`

Dies ist der **deutlichste Unterschied** zwischen beiden Methoden.

### `read_files`: `schemaHints` ist eine dokumentierte, native Option

> Aus der `read_files`-Referenz: `schemaHints` — *"Schema information that read_files passes to Auto Loader schema inference."*
> — [read_files table-valued function | Databricks on AWS](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files)

```sql
-- Nur die Spalte `id` gezielt auf integer überschreiben, Rest wird weiter abgeleitet
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaHints => 'id int');
```

### `spark.read`: `schemaHints` existiert nicht

Für den regulären `DataFrameReader` dokumentiert Databricks **keine** `schemaHints`-Option. `schemaHints` ist laut Doku eine Eigenschaft von **Auto Loader**:

> *"When a column has different data types in two Parquet files, Auto Loader chooses the widest type. You can use schemaHints to override this choice."*
> — [Configure schema inference and evolution in Auto Loader | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema)

Da `read_files` intern auf Auto-Loader-Mechanismen aufbaut, "erbt" es diese Option — `spark.read` (der klassische Batch-`DataFrameReader`) hingegen nicht.

```python
# Kein Äquivalent zu schemaHints bei spark.read —
# stattdessen muss das GESAMTE Schema angegeben werden, um eine Spalte zu erzwingen
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("event", StringType(), True),
])
df = spark.read.schema(schema).json("s3://bucket/path")
```

**Konsequenz:** Mit `read_files` lässt sich **gezielt eine einzelne Spalte** überschreiben, ohne das restliche Schema von der automatischen Inferenz auszuschließen. Mit `spark.read` ist das nicht möglich — hier muss entweder das komplette Schema definiert oder vollständig auf Inferenz gesetzt werden.

---

## 4. Die `_metadata`-Spalte

Hier verhalten sich beide Methoden **identisch**.

### `read_files`

> *"read_files provides a _metadata column... To include _metadata in your results you must explicitly reference it in your query."*
> — [read_files table-valued function | Databricks on AWS](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files)

```sql
SELECT * EXCEPT (content), _metadata
FROM read_files('/Volumes/my_catalog/my_schema/my_volume', format => 'binaryFile');
```

### `spark.read`

> *"To include the _metadata column in the returned DataFrame, you must explicitly select it in the read query where you specify the source."*
> — [File metadata column | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/file-metadata-column)

```python
df = (spark.read
      .format("csv")
      .schema(schema)
      .load("/Volumes/catalog_name/schema_name/volume_name/data/*")
      .select("*", "_metadata"))
```

**Fazit:** Beide bieten dieselbe `_metadata`-Struktur (`file_path`, `file_name`, `file_size`, `file_modification_time`, `file_block_start`, `file_block_length`) mit identischer Regel: explizite Auswahl erforderlich, da die Spalte nicht automatisch in `SELECT *` bzw. `.select("*")` erscheint.

---

## 5. Batch- oder Streaming-Fähigkeit

### `read_files`: eine Funktion, zwei Modi über ein Schlüsselwort

`read_files` selbst deckt **beide** Modi ab — der Unterschied liegt allein im `STREAM`-Schlüsselwort:

```sql
-- Batch
SELECT * FROM read_files('gs://my-bucket/avroData');

-- Streaming (identische Funktion, nur mit STREAM-Präfix, innerhalb einer Streaming Table)
CREATE OR REFRESH STREAMING TABLE avro_data
AS SELECT * FROM STREAM read_files('gs://my-bucket/avroData', includeExistingFiles => false);
```

> *"read_files can be used in a streaming table to ingest files into Delta Lake. read_files uses Auto Loader in the backend for streaming ingestion... The STREAM keyword must be used with read_files."*
> — [read_files table-valued function | Databricks on AWS](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files)

### `spark.read`: strikte Trennung durch zwei separate Klassen

`spark.read` ist **ausschließlich** für Batch gedacht. Streaming erfolgt über eine **komplett andere Einstiegsmethode**, `spark.readStream` (`DataStreamReader`):

> *"Interface used to load a streaming DataFrame from external storage systems (for example, file systems and key-value stores). Use spark.readStream to access this."*
> — [DataStreamReader | Databricks on AWS](https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader)

```python
# Batch
batch_df = spark.read.format("delta").load("/Volumes/<catalog>/<schema>/<volume>/events")

# Streaming — eigene Klasse, kein Parameter an spark.read
streaming_df = spark.readStream.format("delta").load("/Volumes/<catalog>/<schema>/<volume>/events")
```

**Kernunterschied:** `read_files` ist **eine Funktion mit einem Schalter** (`STREAM`-Präfix); `spark.read` und `spark.readStream` sind **zwei separate Klassen** (`DataFrameReader` vs. `DataStreamReader`) mit jeweils eigenem Methodensatz. Es gibt bei `spark.read` keine Option, die den Streaming-Modus aktiviert — man muss die Einstiegsmethode wechseln.

---

## 6. Datei-Tracking

### Batch-Modus: bei beiden Methoden identisch — kein Tracking

Weder `read_files` im reinen `SELECT`/CTAS-Kontext noch `spark.read` dokumentieren einen Mechanismus, der sich merkt, welche Dateien bereits gelesen wurden. Beide sind zustandslose Leseoperationen, die bei jeder Ausführung alle aktuell vorhandenen Dateien neu verarbeiten.

### Streaming-Modus: beide nutzen Checkpoints, aber mit unterschiedlicher Einstellbarkeit

**`STREAM read_files(...)`** nutzt intern Auto Loader und erbt dessen Tracking-Optionen direkt als Parameter der Funktion:

```sql
CREATE OR REFRESH STREAMING TABLE events_overwrite_aware
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  allowOverwrites => true,       -- Tracking-Parameter erweitern (auch Änderungszeitpunkt berücksichtigen)
  includeExistingFiles => false  -- nur beim ersten Start relevant
);
```

**`spark.readStream`** (die Streaming-Gegenstelle zu `spark.read`) konfiguriert Tracking ebenfalls über Optionen, aber getrennt von der eigentlichen `spark.read`-API:

```python
tracked_df = (spark.readStream
              .format("cloudFiles")
              .option("cloudFiles.format", "json")
              .option("cloudFiles.allowOverwrites", "true")
              .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
              .load("/Volumes/analytics/bronze/events"))

(tracked_df.writeStream
   .option("checkpointLocation", "/Volumes/analytics/bronze/_checkpoint")
   .trigger(availableNow=True)
   .table("workspace.default.events_delta"))
```

> *"Checkpoints and write-ahead logs work together to provide processing guarantees for Structured Streaming workloads."*
> — [Structured Streaming checkpoints | Databricks on AWS](https://docs.databricks.com/aws/en/structured-streaming/checkpoints)

**Kernunterschied:** Bei `read_files` liegen die Tracking-Parameter (`allowOverwrites`, `includeExistingFiles`) **direkt als benannte Argumente der Funktion selbst** vor. Bei `spark.readStream` werden dieselben zugrunde liegenden Auto-Loader-Optionen über das `cloudFiles.`-Präfix in `.option()` gesetzt — funktional identisch, aber syntaktisch getrennt von der reinen Lesefunktion.

**Gemeinsamkeit:** Bei **beiden** gilt: Tracking lässt sich im **Batch-Modus nicht aktivieren** — der Wechsel in den Streaming-Modus (`STREAM`-Schlüsselwort bzw. `spark.readStream`) ist in beiden Fällen zwingende Voraussetzung für jegliches Datei-Tracking.

---

## 7. Syntaktischer Grundunterschied: benannte Parameter vs. Methodenketten

Ein struktureller Unterschied, der sich durch alle vorherigen Punkte zieht:

- **`read_files`** verwendet **benannte Parameter** in einem einzigen Funktionsaufruf:
  ```sql
  read_files(path, format => 'json', schema => '...', schemaHints => '...')
  ```
- **`spark.read`** verwendet **verkettete Methodenaufrufe**:
  ```python
  spark.read.format("json").schema("...").option("...", "...").load(path)
  ```

Beide konfigurieren im Kern dieselben zugrunde liegenden Leseoptionen (siehe *Spark API options reference*), unterscheiden sich aber in der Aufrufsyntax entsprechend ihrer jeweiligen Sprachumgebung (SQL vs. PySpark/Scala).

---

## 8. Was davon gehört eigentlich zu Auto Loader?

Die Doku definiert Auto Loader eindeutig als eine bestimmte Structured-Streaming-Quelle, nicht als allgemeinen Sammelbegriff:

> *"Auto Loader provides a Structured Streaming source called cloudFiles."*
> — [What is Auto Loader? | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)

**Auto Loader ist also konkret die `cloudFiles`-Quelle.** Von den in diesem Vergleich behandelten Methoden gehören dazu:

### ✅ Gehört zu Auto Loader

| Methode | Beleg laut Doku |
|---|---|
| `spark.readStream.format("cloudFiles")` | Ist per Definition Auto Loader (siehe Zitat oben). |
| `STREAM read_files(...)` | *"read_files uses Auto Loader in the backend for streaming ingestion."* — [read_files table-valued function](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files) |
| `CREATE OR REFRESH STREAMING TABLE ... AS SELECT * FROM STREAM read_files(...)` | Folgt direkt aus obigem Punkt. |
| `cloudFiles.*`-Optionen (`allowOverwrites`, `includeExistingFiles`, `maxFileAge`, `schemaHints` im Auto-Loader-Kontext, `cloudFiles.inferColumnTypes` …) | *"Options specific to the cloudFiles source are prefixed with cloudFiles to keep them in a separate namespace from other Structured Streaming source options."* — [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) |
| RocksDB-Checkpoint-Tracking | *"their metadata is persisted in a scalable key-value store (RocksDB) in the checkpoint location of your Auto Loader pipeline."* — [What is Auto Loader?](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/) |
| `cloud_files_state`-Tabellenfunktion | Fragt explizit den Auto-Loader-internen Tracking-Zustand ab. |

### ❌ Gehört NICHT zu Auto Loader

| Methode | Warum nicht |
|---|---|
| `read_files()` im Batch-Kontext (ohne `STREAM`) | Reine Tabellenfunktion für `SELECT`/CTAS — kein Streaming, keine `cloudFiles`-Anbindung. |
| `spark.read` / `spark.read.load()` | Batch-`DataFrameReader` — komplett getrennte Klasse ohne `cloudFiles`-Bezug. |
| `spark.readStream.format("json"/"csv"/"parquet"/...)` **ohne** `cloudFiles` | Klassische Spark Structured Streaming File Source — eigener Checkpoint-Mechanismus (Offsets/Commits), aber **nicht** RocksDB-basiert und nicht `cloudFiles`. Databricks empfiehlt hier ausdrücklich Auto Loader als Alternative: *"Databricks also recommends Auto Loader whenever you use Apache Spark Structured Streaming to ingest data from cloud object storage."* — [What is Auto Loader?](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/) |
| `COPY INTO` | Eigener Mechanismus mit Tracking über das Delta Transaction Log der Zieltabelle — kein `cloudFiles`, kein RocksDB. |
| CTAS | Reines Batch-SQL, keine Streaming-Quelle. |
| Streaming Tables allgemein | Nur dann Auto Loader, wenn intern `STREAM read_files(...)` bzw. `cloudFiles` verwendet wird — Streaming Tables können auch andere Quellen nutzen (z. B. Kafka, Delta-Tabellen als Stream), die nichts mit Auto Loader zu tun haben. |

**Fazit für diesen Vergleich:** Von `read_files` gehört nur der **Streaming-Modus** (`STREAM read_files(...)`) tatsächlich zu Auto Loader — der Batch-Modus nicht. Von `spark.read`/`spark.readStream` gehört **ausschließlich** `spark.readStream.format("cloudFiles")` zu Auto Loader; `spark.read` (Batch) hat damit gar keine Berührungspunkte, und selbst `spark.readStream` ohne `cloudFiles` zählt nicht dazu.

---

## 9. Was ist Auto Loader überhaupt?

> *"Auto Loader incrementally and efficiently processes new data files as they arrive in cloud storage without any additional setup."*
> — [What is Auto Loader? | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)

Technisch ist Auto Loader eine **Structured-Streaming-Quelle namens `cloudFiles`**:

> *"It provides a Structured Streaming source called cloudFiles. Given an input directory path on the cloud file storage, the cloudFiles source automatically processes new files as they arrive, with the option of also processing existing files in that directory."*
> — [What is Auto Loader? | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)

Zur Skalierung:

> *"You can use Auto Loader to process billions of files to migrate or backfill a table. Auto Loader scales to support near real-time ingestion of millions of files per hour."*
> — [What is Auto Loader? | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)

Zur Fortschrittsverfolgung (dem in Abschnitt 6 behandelten Tracking):

> *"As files are discovered, their metadata is persisted in a scalable key-value store (RocksDB) in the checkpoint location of your Auto Loader pipeline. This key-value store ensures that data is processed exactly once."*
> — [What is Auto Loader? | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)

Databricks empfiehlt Auto Loader explizit als Standardwerkzeug für Streaming-Ingestion aus Cloud-Speicher:

> *"Databricks also recommends Auto Loader whenever you use Apache Spark Structured Streaming to ingest data from cloud object storage."*
> — [What is Auto Loader? | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)

---

## 10. Vorteile von Auto Loader gegenüber `spark.readStream` ohne `cloudFiles`

Die Doku vergleicht Auto Loader explizit mit der klassischen, generischen Structured-Streaming-File-Source (`spark.readStream.format(fileFormat).load(directory)` **ohne** `cloudFiles`) — also genau der Methode, die in Abschnitt 5 als "nicht zu Auto Loader gehörend" eingeordnet wurde:

> *"In Apache Spark, you can read files incrementally using spark.readStream.format(fileFormat).load(directory). Auto Loader provides the following benefits over the file source:"*
> — [Benefits of Auto Loader over using Structured Streaming directly on files | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)

| Vorteil | Beschreibung laut Doku |
|---|---|
| **Skalierbarkeit** | *"Auto Loader can discover billions of files efficiently. Backfills can be performed asynchronously to avoid wasting any compute resources."* |
| **Performance** | *"The cost of discovering files with Auto Loader scales with the number of files that are being ingested instead of the number of directories that the files may land in."* |
| **Schema-Inferenz und -Evolution** | *"Auto Loader can detect schema drifts, notify you when schema changes happen, and rescue data that would have been otherwise ignored or lost."* |
| **Kosten** | *"Auto Loader uses native cloud APIs to get lists of files that exist in storage. In addition, Auto Loader's file notification mode can help reduce your cloud costs further by avoiding directory listing altogether. Auto Loader can automatically set up file notification services on storage to make file discovery much cheaper."* |

```python
# Klassische Structured Streaming File Source (OHNE Auto Loader) —
# Kosten skalieren mit der Anzahl der Verzeichnisse, keine RocksDB-Zustandsverwaltung
plain_df = spark.readStream.format("json").load("/Volumes/analytics/bronze/events")

# Auto Loader (cloudFiles) — Kosten skalieren mit der Anzahl der Dateien,
# RocksDB-Checkpoint, Schema-Drift-Erkennung, optionale Kostensenkung via File Notifications
autoloader_df = (spark.readStream
                  .format("cloudFiles")
                  .option("cloudFiles.format", "json")
                  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
                  .load("/Volumes/analytics/bronze/events"))
```

---

## 11. Vorteile von Auto Loader gegenüber `read_files` (Batch) und `spark.read`

Die in Abschnitt 9 genannten Vorteile gelten strukturell auch im Vergleich zu den **Batch-Methoden** `read_files` (ohne `STREAM`) und `spark.read`, da diese laut Doku ohnehin **keine** inkrementelle Verarbeitung, kein Tracking und keine automatische Schema-Evolution bieten (siehe Abschnitte 2, 5 und 6 dieses Vergleichs):

- **Inkrementelle Verarbeitung statt vollständigem Neu-Einlesen:** Während `read_files` (Batch) und `spark.read` bei jeder Ausführung alle aktuell vorhandenen Dateien neu verarbeiten (siehe Abschnitt 6), verarbeitet Auto Loader gemäß obigem Zitat nur **neue** Dateien, sobald sie eintreffen — ohne dass die Kosten mit der Gesamtdatenmenge im Verzeichnis wachsen.
- **Exactly-once-Garantie ohne eigenen Zustand:** *"You don't need to maintain or manage any state yourself to achieve fault tolerance or exactly-once semantics."* — [What is Auto Loader? | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/). Bei `read_files` (Batch) und `spark.read` gibt es dagegen laut Doku überhaupt keinen Zustand, den man verwalten könnte — jede erneute Ausführung ist unabhängig und vollständig.
- **Schema-Drift-Erkennung über die Zeit:** Auto Loader erkennt und meldet Schema-Änderungen zwischen aufeinanderfolgenden Ausführungen (*"detect schema drifts, notify you when schema changes happen"*). `read_files` (Batch) und `spark.read` leiten das Schema bei jeder Ausführung neu und unabhängig voneinander ab — ohne Bezug zu vorherigen Läufen (siehe Abschnitt 2).
- **Massives Datenvolumen:** Die Fähigkeit, *"billions of files"* effizient zu verarbeiten, ist für die genannten Batch-Methoden nicht dokumentiert — diese sind für einmalige/periodische Verarbeitung überschaubarer Datenmengen ausgelegt, nicht für kontinuierliche Ingestion in dieser Größenordnung.

**Zusammengefasst:** Die vier offiziell dokumentierten Vorteile (Skalierbarkeit, Performance, Schema-Inferenz/-Evolution, Kosten) sind zwar explizit im Vergleich zur generischen `spark.readStream`-File-Source formuliert, greifen aber aus denselben Gründen auch gegenüber den Batch-Methoden `read_files` und `spark.read` — mit dem zusätzlichen, grundlegenden Unterschied, dass Letztere gar nicht für inkrementelle/kontinuierliche Verarbeitung konzipiert sind (siehe Abschnitt 5).

---

## Zusammenfassung: Wann welche Methode?

| Situation | Empfehlung |
|---|---|
| SQL-Notebook / Databricks SQL, einzelne Spalten-Typen gezielt überschreiben | `read_files` mit `schemaHints` |
| Python-/Scala-Notebook, volle Kontrolle über Schema nötig | `spark.read` mit explizitem `.schema()` |
| Streaming Table direkt in SQL aufsetzen | `STREAM read_files(...)` |
| Streaming-Pipeline in PySpark mit `foreachBatch`/komplexer Logik | `spark.readStream` (ggf. mit `cloudFiles`) |
| Einmaliger Batch-Import/CTAS | Beide gleichwertig — Wahl abhängig von SQL- vs. Python-Kontext |
| Datei-Tracking benötigt | Bei beiden: zwingend Streaming-Modus (`STREAM` bzw. `spark.readStream`) |

## Quellen (ausschließlich offizielle Databricks-Dokumentation)

- read_files table-valued function: https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files
- DataFrameReader class: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader
- schema (DataFrameReader): https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/schema
- json (DataFrameReader): https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/json
- File metadata column: https://docs.databricks.com/aws/en/ingestion/file-metadata-column
- Configure schema inference and evolution in Auto Loader: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema
- DataStreamReader: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader
- Structured Streaming checkpoints: https://docs.databricks.com/aws/en/structured-streaming/checkpoints
- Spark API options reference: https://docs.databricks.com/aws/en/spark/api-options
- CREATE STREAMING TABLE: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table
- What is Auto Loader?: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/
- Using Auto Loader with Unity Catalog: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/unity-catalog
- Benefits of Auto Loader over using Structured Streaming directly on files (Abschnitt der "What is Auto Loader?"-Seite): https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/
