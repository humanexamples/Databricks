# `

# `spark.read` / `spark.read.load()` — Referenz

Dieses Dokument fasst die Funktionsweise des Databricks/PySpark `DataFrameReader` (`spark.read`) zusammen. Es ist das Gegenstück zur Schwesterdatei `_read_files.md` im selben Ordner.

## Abschnittsübersicht

1. [Grundzweck und Kontext](#grundzweck)
2. [Schema-Inferenz](#schema-inferenz)
3. [Vollständige Optionsreferenz (verifiziert)](#optionsreferenz)
4. [Fehlt bei `spark.read` ein `schemaHints`-Äquivalent?](#kein-schemahints)
5. [Die `_metadata`-Spalte](#metadata-spalte)
6. [Strikte Trennung von Batch (`spark.read`) und Streaming (`spark.readStream`)](#batch-streaming-trennung)
7. [Datei-Tracking](#datei-tracking)
8. [Syntax: verkettete Methodenaufrufe (Method Chaining)](#method-chaining)
9. [Rescuing Malformed Rows — die `_rescued_data`-Spalte](#rescued-data)
10. [Wann wird tatsächlich eine Exception geworfen?](#exceptions)
11. [Zusammenfassung: Wann `spark.read` verwenden?](#zusammenfassung)

---

## <a id="grundzweck">1. Grundzweck und Kontext</a>

`spark.read` (Klasse `DataFrameReader`) ist die programmatische Python-/Scala-Schnittstelle, um Daten als `DataFrame` in den Batch-Kontext zu laden.

Die Klasse stellt u. a. folgende Methoden bereit:

- `format(source)` — legt das Eingabeformat fest
- `schema(schema)` — legt das Schema fest (siehe Abschnitt 2)
- `option(key, value)` / `options(**options)` — setzt einzelne bzw. mehrere Leseoptionen
- `load(path, format, schema, **options)` — generischer Lade-Einstiegspunkt
- Format-spezifische Kurzformen: `json(...)`, `csv(...)`, `parquet(*paths, **options)`, `orc(...)`, `text(...)`, `xml(...)`, `excel(...)`
- `table(tableName)` — liest eine Tabelle als `DataFrame`
- `jdbc(url, table, ...)` — liest aus einer Datenbank über JDBC

`DataFrameReader` ist damit nicht nur auf Dateien beschränkt (siehe `table`/`jdbc`), wird in der Praxis aber meist für Dateien in Cloud-Speicher/Volumes verwendet.

```python
df = spark.read.format("json").option("multiLine", True).load("/path/to/data")
```

### Verhältnis zu `read_files` / `COPY INTO` / Auto Loader

Die Klassenreferenz-Seite von `DataFrameReader` selbst erwähnt `read_files`, `COPY INTO` oder Auto Loader an keiner Stelle. Dieser Zusammenhang wird stattdessen auf der separaten **Spark-API-Optionsreferenz** dokumentiert, die die verfügbaren Input-/Output-Optionen für lesende und schreibende Spark-APIs auflistet. Als abgedeckte APIs werden explizit genannt: `DataFrameReader.option()`/`.options()`, `read_files`, `COPY INTO` sowie Auto Loader. Die Optionen selbst steuern, wie Databricks Datendateien liest.

Die Basisoptionen (z. B. `ignoreCorruptFiles`, `modifiedAfter`, `recursiveFileLookup`, siehe Abschnitt 3) stehen dort ausdrücklich unter einer gemeinsamen Überschrift **"Common"** und gelten für alle Dateiformate. `spark.read` ist also eine von mehreren Schnittstellen (neben `read_files`, `COPY INTO`, Auto Loader) zu einer gemeinsamen, format-übergreifenden Optionsbasis, besitzt aber zusätzlich seine eigenen, Python-/Scala-spezifischen Methoden (`.option()`-Chaining statt benannter SQL-Parameter, siehe Abschnitt 8).

---

## <a id="schema-inferenz">2. Schema-Inferenz</a>

### `DataFrameReader.schema()`

`schema()` legt das Eingabeschema fest. Wird das Schema explizit angegeben, kann die zugrunde liegende Datenquelle den Schema-Inferenz-Schritt überspringen, was das Laden beschleunigt. Ohne Schema-Angabe leiten manche Datenquellen (namentlich JSON) das Schema automatisch aus den Daten ab.

```python
# Explizites Schema, um den zusätzlichen Lesedurchlauf zu vermeiden
df = spark.read.schema("id int, ts timestamp, event string").json("s3://bucket/path")
```

### Schema mit verschachtelten Feldern (`STRUCT`, `ARRAY`)

`schema()` akzeptiert entweder ein `StructType`-Objekt oder einen DDL-formatierten String (Beispiel: `'col0 INT, col1 DOUBLE'`). Beide Varianten unterstützen verschachtelte Typen — beim DDL-String über die `STRUCT<feldname: typ, ...>`/`ARRAY<typ>`-Syntax (siehe `_read_files.md` Abschnitt 2 für das Beispiel `STRUCT<Field1:INT NOT NULL COMMENT 'The first field.',Field2:ARRAY<INT>>`), bei `StructType` durch Verschachtelung von `StructType`-Objekten als Feldtyp.

Eigenes Beispiel, `StructType` in einer Variable vorbereitet, mit mehrstufiger Verschachtelung:

```python
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, DoubleType, ArrayType
)

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("user", StructType([
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), True),
    ]), True),
    StructField("tags", ArrayType(StringType()), True),
    StructField("address", StructType([
        StructField("street", StringType(), True),
        StructField("city", StringType(), True),
        StructField("geo", StructType([
            StructField("lat", DoubleType(), True),
            StructField("lon", DoubleType(), True),
        ]), True),
    ]), True),
])

df = spark.read.schema(schema).json("s3://bucket/path")
```

Gleichwertig als DDL-String in einer Variable (funktional identisch zur `StructType`-Variante oben):

```python
schema_ddl = """
  id INT,
  user STRUCT<name: STRING, age: INT>,
  tags ARRAY<STRING>,
  address STRUCT<street: STRING, city: STRING, geo: STRUCT<lat: DOUBLE, lon: DOUBLE>>
"""
df = spark.read.schema(schema_ddl).json("s3://bucket/path")
```

### JSON: automatische Inferenz mit explizitem einmaligen Lesedurchlauf

Ist bei `DataFrameReader.json()` kein Schema angegeben, liest die Funktion den Input einmal vollständig, um das Eingabeschema zu bestimmen — ein separater Lesedurchlauf allein zur Schema-Bestimmung.

### CSV: Inferenz nur über die explizite Option `inferSchema`

Anders als bei JSON ist Schema-Inferenz beim CSV-Reader **nicht** standardmäßig aktiv. Die Option `inferSchema` steuert, ob die Datentypen der geparsten CSV-Datensätze inferiert werden, und hat den Standardwert **`false`**.

```python
# inferSchema = false (Standard): alle Spalten werden als string gelesen
df = spark.read.option("inferSchema", False).csv("s3://bucket/path")

# inferSchema = true: Spark bestimmt die Spaltentypen aus den Daten
df = spark.read.option("inferSchema", True).csv("s3://bucket/path")
```

| Wert | Verhalten |
|---|---|
| `false` (Standard) | Keine Typ-Inferenz; alle Spalten werden als `string` eingelesen, sofern kein Schema angegeben ist. |
| `true` | Spark ermittelt die Datentypen je Spalte aus dem Dateiinhalt — analog zum für JSON dokumentierten zusätzlichen Lesedurchlauf. |

**Einschränkung:** Weder die `schema()`-Referenz noch die JSON- oder CSV-Optionsseite benennen eine feste Anzahl an Lesevorgängen (z. B. "genau zweimal"). Fest steht nur: Bei JSON ohne Schema wird der Input einmal vollständig zur Inferenz gelesen, und ein explizit angegebenes Schema erlaubt der Datenquelle, diesen Inferenzschritt zu überspringen — woraus sich ableiten lässt, dass ohne Schema ein zusätzlicher Lese-/Scan-Schritt stattfindet, bevor die eigentlichen Daten geladen werden.

---

## <a id="optionsreferenz">3. Vollständige Optionsreferenz (verifiziert)</a>

`spark.read` verwendet seine Optionen über `.option(key, value)` / `.options(**options)`, angewendet auf ein per `.format(...)` gewähltes Format.

```python
df = spark.read.format("json").option("multiLine", True).load("/path/to/data")
```

### Format-übergreifende Basisoptionen ("Common")

| Option | Standardwert | Beschreibung |
|---|---|---|
| `ignoreCorruptFiles` | `false` | *"Whether to ignore corrupt files. If true, the Spark jobs will continue to run when encountering corrupted files."* Ab Databricks Runtime 11.3 LTS. |
| `ignoreMissingFiles` | `false` | *"Whether to ignore missing files. If true, the Spark jobs continue to run when encountering missing files."* Ab Databricks Runtime 11.3 LTS. (Für `COPY INTO` (legacy) gilt abweichend `true` als Standard.) |
| `modifiedAfter` | keiner | *"An optional timestamp as a filter to only ingest files that have a modification timestamp after the specified timestamp."* |
| `modifiedBefore` | keiner | *"An optional timestamp as a filter to only ingest files that have a modification timestamp before the specified timestamp."* |
| `pathGlobFilter` | keiner | *"A potential glob pattern for choosing files."* (Bei `read_files` heißt dieselbe Option `fileNamePattern` — für `spark.read` gilt der Name `pathGlobFilter`.) |
| `recursiveFileLookup` | `false` | *"When `true`, this option searches through nested directories."* |
| `ignoredPathSegmentRegex` | `^[._]` | Regex, der Dateien/Verzeichnisse beim Auflisten überspringt; lässt sich alternativ auch über die Spark-Konfiguration `spark.sql.files.ignoredPathSegmentRegex` setzen (die Data-Source-Option hat bei gleichzeitiger Angabe Vorrang). Ab Databricks Runtime 19. |

```python
# Nur kürzlich geänderte Dateien einlesen, verschachtelte Verzeichnisse durchsuchen
df = (spark.read
      .option("modifiedAfter", "2026-08-01T00:00:00")
      .option("recursiveFileLookup", True)
      .format("json")
      .load("/Volumes/analytics/bronze/events"))
```

*(Die CSV-, JSON-, Parquet-, Avro-, ORC- und XML-spezifischen Optionen wurden in die jeweiligen Dateien unter `Dateitypen/` verschoben: `Ingesting CSV.md`, `Ingesting JSON.md`, `Ingesting Parquet.md`, `Ingesting Avro.md`, `Ingesting ORC.md`, `Ingesting XML.md`.)*

Die vollständigen Optionslisten (inkl. Excel, Text, State Store) finden sich in der Spark-API-Optionsreferenz.

---

## <a id="kein-schemahints">4. Fehlt bei `spark.read` ein `schemaHints`-Äquivalent?</a>

**`spark.read` besitzt kein `schemaHints`-Äquivalent.**

1. Die `DataFrameReader`-Klassenreferenz erwähnt an keiner Stelle eine `schemaHints`-Option.
2. Auf der Spark-API-Optionsreferenz erscheint `schemaHints` (dort als `cloudFiles.schemaHints`) ausschließlich im **Auto-Loader-Abschnitt** ("Common" unter den *Streaming*-Optionen) — als Schema-Information, die für die Schema-Inferenz von Auto Loader angegeben wird. Im Abschnitt für den generischen `DataFrameReader`/Batch-Optionen fehlt sie.

Um bei `spark.read` einzelne Spaltentypen dennoch gezielt zu erzwingen, muss folglich das **gesamte** Schema angegeben werden (per DDL-String oder `StructType`):

```python
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("event", StringType(), True),
])
df = spark.read.schema(schema).json("s3://bucket/path")
```

**Konsequenz:** Mit `spark.read` ist es nicht möglich, gezielt eine einzelne Spalte zu überschreiben, ohne das restliche Schema von der automatischen Inferenz auszuschließen — anders als bei `read_files`/Auto Loader (`schemaHints`, siehe `_read_files.md` Abschnitt 4) muss bei `spark.read` entweder das komplette Schema definiert oder vollständig auf Inferenz gesetzt werden.

### Einschränkung auf reines Batch-`spark.read` — im Streaming-Kontext existiert `cloudFiles.schemaHints`

Die obige Einschränkung gilt ausschließlich für das reine, Batch-orientierte `DataFrameReader`/`spark.read`. Wird stattdessen über `spark.readStream.format("cloudFiles")` auf Auto Loader zugegriffen (siehe Abschnitt 6), steht dort `cloudFiles.schemaHints` zur Verfügung (siehe Abschnitt 4 oben). Auch dieser Wert lässt sich, wie jeder normale Python-String, vorab in einer Variable zusammenbauen:

```python
hints = "loyalty_tier STRING, region_code STRING, signup_ts TIMESTAMP"

streaming_df = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaHints", hints)
    .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
    .load("/Volumes/analytics/bronze/events"))
```

---

## <a id="metadata-spalte">5. Die `_metadata`-Spalte</a>

Die `_metadata`-Spalte ist eine versteckte Spalte und für alle Eingabe-Dateiformate verfügbar. Sie enthält u. a. folgende Felder:

| Feld | Typ | Beschreibung |
|---|---|---|
| `file_path` | `STRING` | Dateipfad der Eingabedatei |
| `file_name` | `STRING` | Dateiname inkl. Erweiterung |
| `file_size` | `LONG` | Dateigröße in Bytes |
| `file_modification_time` | `TIMESTAMP` | Letzter Änderungszeitstempel |
| `file_block_start` | `LONG` | Startversatz des gelesenen Blocks, in Bytes |
| `file_block_length` | `LONG` | Länge des gelesenen Blocks, in Bytes |

**Muss explizit ausgewählt werden:** Um die `_metadata`-Spalte im zurückgegebenen DataFrame zu erhalten, muss sie in der Lese-Query explizit ausgewählt werden, z. B. über `.select("*", "_metadata")`. Die Spalte erscheint also **nicht** automatisch bei `.select("*")` allein.

```python
df = (spark.read
      .format("csv")
      .schema(schema)
      .load("/Volumes/catalog_name/schema_name/volume_name/data/*")
      .select("*", "_metadata"))
```

`_metadata` funktioniert sowohl beim klassischen `spark.read`-Anwendungsfall als auch bei Auto Loader und `COPY INTO` (legacy) — die Spalte ist damit kein auf Auto Loader beschränktes Feature.

---

## <a id="batch-streaming-trennung">6. Strikte Trennung von Batch (`spark.read`) und Streaming (`spark.readStream`)</a>

`spark.read` ist ausschließlich für Batch gedacht. Streaming erfolgt über eine eigene Klasse: `DataStreamReader` (`spark.readStream`) — die Schnittstelle, um einen streamenden DataFrame aus externen Storage-Systemen (z. B. Dateisysteme, Key-Value-Stores) zu laden.

Die `DataStreamReader`-Klassenreferenz listet ihre eigenen Methoden (`format`, `schema`, `option`, `options`, `load`, `json`, `csv`, `parquet`, `orc`, `text`, `xml`, `table`, `name`, `changes`) unabhängig von `DataFrameReader` — es handelt sich um zwei getrennte Klassen mit jeweils eigenem Methodensatz, nicht um einen Streaming-Parameter an `spark.read`.

```python
# Batch
batch_df = spark.read.format("delta").load("/Volumes/<catalog>/<schema>/<volume>/events")

# Streaming — eigene Klasse
streaming_df = spark.readStream.format("delta").load("/Volumes/<catalog>/<schema>/<volume>/events")
```

### `cloudFiles` als Auto-Loader-Format für `spark.readStream`

Auto Loader stellt eine Structured-Streaming-Quelle namens `cloudFiles` bereit. In Kombination mit der `DataStreamReader.format(source)`-Methode ergibt sich die bekannte Aufrufform:

```python
streaming_df = (spark.readStream
                .format("cloudFiles")
                .option("cloudFiles.format", "json")
                .load("/Volumes/analytics/bronze/events"))
```

Ohne `cloudFiles` handelt es sich um die generische Structured-Streaming-Dateiquelle mit eigenem, einfacherem Offset-/Commit-basiertem Checkpoint-Mechanismus (siehe Abschnitt 7) statt der für Auto Loader dokumentierten RocksDB-basierten Datei-Verfolgung.

---

## <a id="datei-tracking">7. Datei-Tracking</a>

### Batch-Modus (`spark.read`): kein Tracking

Weder die `DataFrameReader`-Klassenreferenz noch die Spark-API-Optionsreferenz dokumentieren für `spark.read` einen Mechanismus, der sich merkt, welche Dateien bereits gelesen wurden. Es handelt sich um eine zustandslose Leseoperation: Jede Ausführung liest erneut alle zum Zeitpunkt der Ausführung vorhandenen, zum Pfad/Filter passenden Dateien.

### Streaming-Modus (`spark.readStream`): Tracking über Checkpoints

Die Structured-Streaming-Checkpoints-Doku bestätigt: *"Checkpoints and write-ahead logs work together to provide processing guarantees for Structured Streaming workloads."* Ein Checkpoint enthält laut Doku u. a.:

- **Offsets:** *"The source offsets processed in each micro-batch. This allows the query to resume from exactly where it left off without reprocessing data."*
- Commit-Informationen (welche Micro-Batches erfolgreich verarbeitet wurden)
- Zustand (State) für zustandsbehaftete Operationen
- Metadaten (u. a. Query-ID, Konfiguration)

**Speziell für Auto Loader (`cloudFiles`)** ist zusätzlich dokumentiert: *"As files are discovered, their metadata is persisted in a scalable key-value store (RocksDB) in the checkpoint location"* — dieser Zustand ermöglicht laut Doku exactly-once-Verarbeitung. Die generische, nicht-`cloudFiles`-basierte Structured-Streaming-Dateiquelle nutzt dagegen den allgemeinen Offset-/Commit-Checkpoint-Mechanismus ohne die für Auto Loader dokumentierte RocksDB-Komponente.

```python
tracked_df = (spark.readStream
              .format("cloudFiles")
              .option("cloudFiles.format", "json")
              .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
              .load("/Volumes/analytics/bronze/events"))

(tracked_df.writeStream
   .option("checkpointLocation", "/Volumes/analytics/bronze/_checkpoint")
   .trigger(availableNow=True)
   .table("workspace.default.events_delta"))
```

**Wichtig:** Die Checkpoints-Doku selbst stellt keinen expliziten Vergleichssatz zwischen Batch- und Streaming-Tracking auf ("Batch hat kein Tracking, Streaming schon") — das ist eine Schlussfolgerung aus zwei getrennt bestätigten Fakten (kein dokumentierter Tracking-Mechanismus bei `spark.read`; dokumentierter Offset-/Zustands-Mechanismus bei `spark.readStream`-Checkpoints), nicht ein wörtliches Zitat. Bestätigt ist jedenfalls: Tracking lässt sich im Batch-Modus (`spark.read`) nicht aktivieren — der Wechsel zu `spark.readStream` ist Voraussetzung.

### `cloudFiles.schemaLocation` im Detail

Im obigen Beispiel legt `cloudFiles.schemaLocation` fest, wo Auto Loader das inferierte Schema ablegt. Bestätigt auf der Auto-Loader-Schema-Seite (zweifach abgerufen, identischer Wortlaut beide Male): *"Auto Loader stores the schema information in a directory `_schemas` at the configured `cloudFiles.schemaLocation` to track schema changes to the input data over time."* — an diesem Pfad entsteht also ein Unterverzeichnis `_schemas`, in dem das Schema und dessen Änderungen über die Zeit gespeichert werden. Für reines Batch-`spark.read` gibt es kein Äquivalent — dort wird bei jeder Ausführung neu inferiert (siehe Abschnitt 2), ohne dass etwas persistiert würde.

**Korrektur:** Eine vorherige Fassung dieses Abschnitts behauptete zusätzlich, bei einem Neustart werde das gespeicherte Schema wiederverwendet, statt erneut vollständig zu inferieren. Das ist **nicht belegt** — die Quelle äußert sich nicht explizit zum Neustart-Verhalten, sondern nur zum Nachverfolgen von Änderungen über die Zeit. Bestätigt ist eine Wiederverwendung nur für den spezifischen Fall der Schema-Evolution nach einer `UnknownFieldException` (siehe `06 Auto Loader/01 Schema-Inferenz und -Evolution.md`, Abschnitt Schema-Evolution-Modi), nicht als allgemeine Aussage für jeden Neustart.

**Ungeklärt:** Ob sich der Inhalt von `_schemas` gezielt selbst vorbefüllen lässt, um ein eigenes Startschema vorzugeben, ist auf der geprüften Seite nicht dokumentiert — sie beschreibt das Verzeichnis als internen Tracking-Mechanismus von Auto Loader, nicht als für Nutzer zum direkten Schreiben vorgesehene Schnittstelle.

---

## <a id="method-chaining">8. Syntax: verkettete Methodenaufrufe (Method Chaining)</a>

`spark.read` verwendet verkettete Methodenaufrufe (Method Chaining), bestätigt durch die Struktur der Klassenreferenz selbst (`format()`, `schema()`, `option()`/`options()`, `load()` geben jeweils den `DataFrameReader` zur Weiterverkettung zurück):

```python
df = (spark.read
      .format("json")
      .schema("id int, ts timestamp, event string")
      .option("multiLine", True)
      .load(path))
```

Dies unterscheidet sich strukturell von der in `_read_files.md` (Abschnitt 8) beschriebenen Syntax von `read_files`, das **ausschließlich benannte Parameter** in einem einzigen SQL-Funktionsaufruf verwendet:

```sql
-- read_files zum Vergleich (SQL, benannte Parameter statt Method Chaining)
SELECT * FROM read_files(
  path,
  format => 'json',
  schema => 'id int, ts timestamp, event string'
);
```

| Aspekt | `spark.read` | `read_files` |
|---|---|---|
| Sprache | Python/Scala (API) | SQL (Tabellenfunktion) |
| Optionsübergabe | `.option(key, value)`-Kette | benannte Parameter (`key => value`) im Funktionsaufruf |
| Rückgabewert je Aufruf | `DataFrameReader` (weiterverkettbar) bzw. am Ende `DataFrame` | direkt Tabellenergebnis |

---

## <a id="rescued-data">9. Rescuing Malformed Rows — die `_rescued_data`-Spalte</a>

### Was ist die "Rescued Data Column"?

Laut der CSV-Optionstabelle (Beschreibung von `rescuedDataColumn`) dient die Spalte dazu, Daten zu sammeln, die aufgrund eines Typkonflikts oder Schema-Mismatches (inkl. abweichender Groß-/Kleinschreibung) nicht geparst werden konnten, statt sie stillschweigend zu verwerfen.

### Verhalten bei `spark.read`: standardmäßig **aus**

**Zweifach bestätigt:**

1. In allen geprüften Optionstabellen der Spark-API-Optionsreferenz (CSV, JSON, Parquet, Avro, XML) ist der Standardwert von `rescuedDataColumn` durchgängig **keiner / `None`** — die Spalte wird also nicht automatisch erzeugt, sofern die Option nicht gesetzt wird.
2. Die CSV-Lese-Doku zeigt das Aktivieren explizit als notwendigen Schritt: *"To enable the rescued data column, set the `rescuedDataColumn` option to a column name when reading:"*, gefolgt vom Codebeispiel `spark.read.option("rescuedDataColumn", "_rescued_data").format("csv").load(...)`.

```python
# rescuedDataColumn muss bei spark.read explizit gesetzt werden
df = (spark.read
      .option("rescuedDataColumn", "_rescued_data")
      .format("json")
      .load("/Volumes/<catalog>/<schema>/<volume>/events_json"))
```

**Nuance gegenüber Auto Loader:** Die Auto-Loader-Schema-Doku formuliert für den Auto-Loader-Kontext abweichend: *"When Auto Loader infers the schema, Auto Loader automatically adds a rescued data column to your schema as `_rescued_data`."* Das bezieht sich jedoch ausdrücklich auf **Auto Loader** (also den Streaming-/`cloudFiles`-Kontext bzw. `STREAM read_files`), nicht auf `spark.read`. Für den reinen Batch-`DataFrameReader` (dieses Dokument) bleibt die zweifach bestätigte Aussage maßgeblich: **explizit zu setzen, kein automatisches Einschalten.**

### Die drei Parser-Modi (`PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`)

Für CSV/JSON gilt laut Optionstabelle (Abschnitt 3) `PERMISSIVE` als Standard-`mode`; verfügbare Werte sind `PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`. Für Avro gilt abweichend `FAILFAST` als Standard (siehe Abschnitt 3 und Abschnitt 10).

| Aspekt | `spark.read` |
|---|---|
| `rescuedDataColumn` standardmäßig aktiv? | Nein — muss per `.option("rescuedDataColumn", ...)` explizit gesetzt werden (zweifach bestätigt) |
| Parser-Modi (`PERMISSIVE`/`DROPMALFORMED`/`FAILFAST`) | Ja, format-abhängige Standardwerte (CSV/JSON: `PERMISSIVE`; Avro: `FAILFAST`) |
| Korrupte (nicht nur typfalsche) Datensätze | `columnNameOfCorruptRecord` (Standard `_corrupt_record`) |

---

## <a id="exceptions">10. Wann wird tatsächlich eine Exception geworfen?</a>

**Grundunterscheidung (analog zu `_read_files.md` Abschnitt 14):** `spark.read` ist eine reine Lese-Schnittstelle — sie schreibt selbst nichts. Exceptions auf der **Lese-Ebene** (während `spark.read` selbst parst) sind dokumentiert die Ausnahme; Exceptions auf der **Schreib-Ebene** (wenn das Ergebnis anschließend z. B. per `DataFrame.write` in eine Delta-Tabelle geschrieben wird) sind der dokumentierte Normalfall bei Schema-Abweichung. Dieselbe Unterscheidung, die in `_read_files.md` Abschnitt 14.4 für `read_files` herausgearbeitet wurde, gilt strukturell identisch für `spark.read`: Schreib-Ebene-Fehler entstehen nicht durch `spark.read` selbst, sondern durch die nachgelagerte `DataFrameWriter`-Operation — dasselbe Delta-Schema-Enforcement-Verhalten träte unabhängig davon auf, ob die Daten aus `spark.read`, `read_files` oder einer anderen Quelle stammen.

### 10.1 Lese-Ebene

| Auslöser | Exception / Verhalten | Bedingung laut Doku |
|---|---|---|
| `.option("mode", "FAILFAST")` + fehlerhafter/unvollständiger Datensatz | Abbruch | Standard-`mode` bei CSV/JSON ist `PERMISSIVE` — `FAILFAST` muss explizit gesetzt werden |
| Avro: nicht parsbarer Datensatz **ohne** explizit gesetzten `mode` | Abbruch, da der Avro-**Standardwert** für `mode` bei `spark.read.format("avro")` **`FAILFAST`** ist — abweichend vom `PERMISSIVE`-Standard bei CSV/JSON | Zweifach bestätigt (siehe Abschnitt 3) |
| Avro: `.option("avroSchemaEvolutionMode", "restart")` + Schema-Änderung erkannt | *"raises an `UnknownFieldException` when schema changes are detected and requires a job restart"* | Laut Optionstabelle Teil der **Batch**-Avro-Optionen, nicht auf Streaming beschränkt |
| CSV: `.option("failOnUnknownFields", True)` gesetzt | Abbruch, sobald ein Datensatz Spalten enthält, die nicht im Schema stehen | Standardmäßig `false` |
| CSV: `.option("failOnWidenedFields", True)` gesetzt | Abbruch, sobald ein Feldwert nur durch Typ-Erweiterung zum deklarierten Schema-Typ passt | Standardmäßig `false`; `failOnUnknownFields => true` kann diesen Effekt überdecken |
| `format("binaryFile")` mit explizitem `schema`, das nicht zum erwarteten festen Binary-File-Schema passt | Fehlerklasse `BINARY_FILE_DATA_SOURCE_SCHEMA_MISMATCH`: *"The schema provided to the binary file data source does not match the expected schema."* (laut Fehlerklassen-Referenz mit Platzhaltern für erwartetes/angegebenes Schema fortgesetzt) | Bestätigt über die Fehlerklassen-Referenzseite; die Seite war beim Abruf an anderer Stelle abgeschnitten (siehe unten) |
| CSV: `enforceSchema` zusammen mit `rescuedDataColumn` **oder** `failOnUnknownFields` gesetzt | **Ungeklärt:** Auf der CSV-Lese-Doku selbst findet sich dazu kein Hinweis/keine Fehlermeldung (gezielt geprüft: kein Warnhinweis vorhanden). Die Fehlerklassen-Referenzseite ist zu lang für einen vollständigen Abruf und bricht vor dem relevanten Abschnitt ab. Strukturell sehr ähnlich und **bestätigt** existiert die Fehlerklasse `AVRO_POSITIONAL_FIELD_MATCHING_UNSUPPORTED` für Avro: *"The use of positional field matching is not supported when either `rescuedDataColumn` or `failOnUnknownFields` is enabled."* Ob es eine wortgleiche CSV-spezifische Fehlerklasse gibt, bleibt unbestätigt. |

**Wichtige Einschränkung:** Reine **Typkonflikte** einzelner Felder gelten in Kombination mit aktiver `rescuedDataColumn` explizit nicht als korrupt und landen (auch bei `FAILFAST`) in der Rescued-Data-Spalte statt in einer Exception. Da `rescuedDataColumn` bei `spark.read` standardmäßig **aus** ist (Abschnitt 9), greift dieser Schutz hier nur, wenn er bewusst aktiviert wurde.

**Kein Fehler, aber fehleranfällig:** Wird ein explizites Schema angegeben, das nicht zur tatsächlichen Spaltenreihenfolge einer CSV-Datei passt, erfolgt keine Exception — CSV besitzt keine Spaltennamen-Metadaten, Spark ordnet die Schema-Felder positionsbasiert zu.

### 10.2 Schreib-Ebene: Delta-Tabellen (Schema Enforcement)

Diese Ebene betrifft nicht `spark.read` selbst, sondern das anschließende Schreiben (`DataFrame.write...`) in eine Ziel-Delta-Tabelle.

**Zentrales Ergebnis dieser Recherche:** Weder die kanonische Schema-Enforcement-Seite (`/aws/en/tables/schema-enforcement`) noch die Schema-Update-Seite (`/aws/en/delta/update-schema`) zeigen an irgendeiner Stelle einen wörtlich zitierbaren Exception-Text in einem Code-Block. Beide Seiten wurden gezielt danach befragt; beide Antworten bestätigen übereinstimmend: kein Code-Block mit realem Fehlertext vorhanden, das Verhalten wird nur in Prosa/mit Kommentarzeilen wie `-- Fails: unknown_column does not exist in target_table` beschrieben.

| Auslöser | Verhalten laut Doku | Einschränkung |
|---|---|---|
| Schreibvorgang enthält neue Spalten gegenüber der Ziel-Delta-Tabelle, `mergeSchema` nicht gesetzt | Schlägt fehl (dokumentiertes Schema-Enforcement-Standardverhalten); Fehlschlag selbst ist normal-dokumentiert | **Ungeklärt:** Der exakte Exception-Wortlaut ist nicht belegt. Die KB-Seite "AnalysisException error due to a schema mismatch" zeigt den Text `AnalysisException: A schema mismatch detected when writing to the Delta table (...)` nur als **explizit als illustrativ eingeordnetes Beispiel** im Problem-Abschnitt, nicht als bestätigten realen Systemoutput (per gezieltem Abruf verifiziert). Lösung laut KB: `.option("mergeSchema", "true")` beim Schreiben setzen. |
| Verschachtelte (nested) Felder werden bei **`MERGE INTO`**-Statements mit aktivierter automatischer Schema-Evolution hinzugefügt/entfernt | Schlägt fehl, da automatische Schema-Evolution laut KB "Delta Merge cannot resolve nested field" *"only supports top level columns. Nested fields are not supported."* | Diese Quelle bezieht sich laut eigenem Wortlaut *("You are attempting a Delta Merge with automatic schema evolution...")* explizit auf `MERGE INTO`, nicht auf einfache Schreib-/Append-Operationen. Der dort gezeigte Fehlertext ist zudem ein **Platzhalter-Format** (`"Delta Merge cannot resolve 'field' due to data type mismatch"`), kein vollständiges wörtliches Zitat. Ob dieselbe Einschränkung für reine Append-Schreibvorgänge (der bei `spark.read` übliche Fall) gilt, ist **nicht bestätigt**. |
| Spaltentyp der eingehenden Daten weicht ab und ist nicht kompatibel erweiterbar (außerhalb von `MERGE INTO`) | **Ungeklärt:** Für dieses Szenario wurde in keiner geprüften Databricks-Quelle ein bestätigter wörtlicher Fehlertext gefunden. Eine zuvor in einer früheren, nicht-verifizierten Fassung dieses Dokuments zitierte Meldung ("Failed to merge fields ... Failed to merge incompatible data types ...") entspricht einem bekannten generischen Spark-SQL-Fehlerformat, ließ sich aber in keiner offiziellen Databricks-Quelle wörtlich bestätigen und wird hier nicht mehr reproduziert. |
| Reine Parquet-Tabellen (nicht Delta) mit abweichendem Schema beim Anhängen | **Ungeklärt:** Auch hierfür wurde keine Databricks-Quelle mit bestätigtem Fehlertext gefunden. Eine früher zitierte generische Analyzer-Meldung (`cannot resolve '<column>' given input columns: [...]`) ist nicht Databricks-doku-bestätigt und wird hier nicht mehr reproduziert. |

**Korrektur gegenüber der vorherigen, nicht verifizierten Fassung dieses Dokuments:** Die zuvor in Abschnitt 10.2 als wörtliches Zitat dargestellten Texte — insbesondere die vollständige `AnalysisException`-Meldung zu `mergeSchema` und die "Failed to merge fields... Failed to merge incompatible data types..."-Meldung — ließen sich bei dieser Recherche nicht bestätigen und wurden durch die obigen "Ungeklärt"-Markierungen ersetzt. Dies deckt sich mit dem identischen Befund in `_read_files.md` Abschnitt 14.3, wo dieselben zwei Zitate ebenfalls als nicht verifizierbar identifiziert wurden.

### 10.3 Zusammenfassende Einordnung

- **Auf der Lese-Ebene** (`spark.read` selbst) ist eine Exception die **Ausnahme**: v. a. `FAILFAST` bei korrupten Datensätzen, der abweichende Avro-Standard-`mode`, `avroSchemaEvolutionMode => 'restart'`, oder explizit gesetzte `failOn*`-Optionen.
- **Auf der Schreib-Ebene** in Delta-Tabellen ist eine Exception bei Schema-Abweichung der dokumentierte Normalfall (Schema Enforcement) — betrifft aber nicht `spark.read` selbst, sondern die nachgelagerte Schreiboperation. Die exakten Fehlertexte dafür sind, wie oben dargelegt, überwiegend nicht wörtlich belegbar und daher als "Ungeklärt" markiert.
- **Praktische Konsequenz:** Da `rescuedDataColumn` bei `spark.read` standardmäßig deaktiviert ist (Abschnitt 9), ist das Risiko stiller Typ-Fehlparsierungen bzw. unerwarteter `FAILFAST`-Abbrüche bei Typkonflikten höher als bei `read_files`/Auto Loader im Streaming-Kontext, sofern die Option nicht bewusst gesetzt wird.

---

## <a id="zusammenfassung">11. Zusammenfassung: Wann `spark.read` verwenden?</a>

| Situation | Empfehlung |
|---|---|
| Python-/Scala-Notebook, volle programmatische Kontrolle über Schema/Optionen nötig | `spark.read` mit explizitem `.schema()` |
| Einmaliger Batch-Import | `spark.read` |
| Gezielt einzelne Spaltentypen überschreiben, Rest inferieren lassen | Nicht direkt möglich (kein `schemaHints`, siehe Abschnitt 4) — dafür eher `read_files`/Auto Loader |
| Streaming-Pipeline in PySpark, ggf. mit `foreachBatch`/komplexer Logik | `spark.readStream`, optional mit `.format("cloudFiles")` für Auto-Loader-Funktionalität |
| Datei-Tracking benötigt | Zwingend `spark.readStream` statt `spark.read` |
| Robustheit gegen Typkonflikte beim Lesen gewünscht | `.option("rescuedDataColumn", "_rescued_data")` explizit setzen, da bei `spark.read` nicht standardmäßig aktiv |
| Ziel-Tabelle: Delta, Schema kann sich ändern | Beim **Schreiben** zusätzlich `.option("mergeSchema", "true")` erwägen (betrifft die Schreib-, nicht die Lese-Operation) |

---

