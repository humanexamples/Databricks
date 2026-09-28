# Vergleich: `read_files` vs. `spark.read` / `spark.read.load()`

Dieses Dokument vergleicht die beiden Databricks-Lesemechanismen `read_files` (SQL-Tabellenfunktion) und `spark.read`/`spark.read.load()` (`DataFrameReader`, PySpark) sowie Auto Loader.

## Abschnittsübersicht

1. Grundzweck und Kontext
2. Schema-Inferenz
3. `schemaHints`
4. Die `_metadata`-Spalte
5. Batch- oder Streaming-Fähigkeit
6. Datei-Tracking
7. Syntaktischer Grundunterschied: benannte Parameter vs. Methodenketten
8. Was davon gehört eigentlich zu Auto Loader?
9. Was ist Auto Loader überhaupt?
10. Auto Loader in SQL — nicht nur PySpark/Scala
11. Zwei Datei-Erkennungsmodi: Directory Listing vs. File Notification
12. Schema-Evolution-Modi und automatische Typ-Erweiterung
13. Beobachtbarkeit und Zustandsabfrage (`cloud_files_state`)
14. Vorteile von Auto Loader gegenüber `spark.readStream` ohne `cloudFiles`
15. Vorteile von Auto Loader gegenüber `read_files` (Batch) und `spark.read`
16. Rescuing Malformed Rows — die `_rescued_data`-Spalte
17. Wann wird tatsächlich eine Exception geworfen? — Systematische Übersicht
18. Was gehört alles zu Declarative Pipelines?
19. Zusammenfassung: Wann welche Methode?

## Kurzübersicht

**Legende:** ✅ = standardmäßig/automatisch vorhanden · ⚙️ = vorhanden, aber erfordert explizite Aktivierung/Konfiguration · ❌ = nicht vorhanden/nicht möglich

| Aspekt | `read_files` | `spark.read` / `spark.read.load()` | Auto Loader (`cloudFiles`) | SDP / Lakeflow Declarative Pipelines |
|---|---|---|---|---|
| **Kategorie** | SQL-Tabellenfunktion (Databricks SQL) | PySpark-/Scala-API (`DataFrameReader`) | Structured-Streaming-Quelle (`spark.readStream.format("cloudFiles")`) | Deklaratives Pipeline-Rahmenwerk (SQL & Python) für Batch- und Streaming-Datenpipelines |
| **Grundzweck** | Dateien direkt in SQL-Abfragen (`SELECT`, CTAS) einlesen | Dateien/Tabellen in ein `DataFrame` laden | Neue Dateien inkrementell und fortlaufend aus Cloud-Speicher verarbeiten | Streaming Tables, Materialized Views und Flows deklarativ orchestrieren |
| **Schema-Inferenz** | ✅ Ja, mit einheitlichem Schema über alle Dateien | ✅ Ja, formatabhängig (zusätzlicher Lesedurchlauf) | ✅ Ja, inkl. Erkennung von Schema-Drift zwischen Läufen | ✅ Übernimmt die Schema-Inferenz der zugrunde liegenden Quelle (`read_files`/Auto Loader) |
| **`schemaHints`** | ✅ Ja, dokumentierte Option | ❌ Nicht vorhanden — nur vollständiges `.schema()` möglich | ✅ Ja — nativ, `schemaHints` ist ursprünglich eine Auto-Loader-Option | ✅ Ja, über `STREAM read_files(..., schemaHints => ...)` innerhalb einer Streaming Table |
| **`_metadata`-Spalte** | ⚙️ Ja, muss explizit ausgewählt werden | ⚙️ Ja, muss explizit ausgewählt werden | ⚙️ Ja, ebenfalls explizit auszuwählen | ⚙️ Ja, ebenfalls explizit auszuwählen (geerbt von `read_files`) |
| **Batch-fähig** | ✅ Ja (`SELECT * FROM read_files(...)`) | ✅ Ja (Standardmodus) | ❌ Nein — ausschließlich Streaming-Quelle | ✅ Ja, über Materialized Views (batch-artige, inkrementell aktualisierte Transformationen) |
| **Streaming-fähig** | ✅ Ja, mit `STREAM read_files(...)` — gleiche Funktion, anderes Schlüsselwort | ✅ Ja, aber nur über die separate Schnittstelle `spark.readStream` | ✅ Ja — das ist der einzige Modus | ✅ Ja, über Streaming Tables als primäres Ingestion-Objekt |
| **Datei-Tracking (Batch)** | ❌ Nein | ❌ Nein | – (kein Batch-Modus vorhanden) | – (Materialized Views nutzen inkrementelles Refresh statt Datei-Tracking) |
| **Datei-Tracking (Streaming)** | ✅ Ja, via Auto Loader intern (Checkpoint) | ✅ Ja, via `spark.readStream` + `checkpointLocation` | ✅ Ja — RocksDB-Checkpoint, exactly-once, kein eigener Zustand nötig | ✅ Ja, geerbt von Auto Loader innerhalb der Streaming Table |
| **Tracking ein-/ausschaltbar?** | Nur im Streaming-Kontext (`allowOverwrites`, `includeExistingFiles`) | Nicht bei `spark.read`; nur durch Wechsel zu `spark.readStream` | Ja — direkt über `cloudFiles.allowOverwrites`, `cloudFiles.includeExistingFiles`, `cloudFiles.maxFileAge` | Ja, über dieselben Parameter innerhalb von `STREAM read_files(...)` |
| **Skalierung bei vielen Dateien** | Nicht spezifisch dokumentiert | Nicht spezifisch dokumentiert | ✅ Kosten skalieren mit Anzahl Dateien statt Verzeichnissen; verarbeitet Milliarden Dateien | ✅ Geerbt von Auto Loader, zusätzlich automatische Orchestrierung/Parallelisierung der Flows |
| **Datei-Erkennungskosten** | Nicht spezifisch dokumentiert | Nicht spezifisch dokumentiert | ⚙️ Grundkosten über native Cloud-APIs; per File-Notification-Modus (Konfiguration nötig) weiter reduzierbar | ⚙️ Geerbt von Auto Loader (identische Konfigurationsoptionen) |
| **Rescued Data Column (`_rescued_data`)** | ✅ Standardmäßig aktiv bei Schema-Inferenz | ⚙️ Muss explizit per `.option("rescuedDataColumn", ...)` aktiviert werden | ✅ Standardmäßig aktiv bei Schema-Inferenz | ✅ Geerbt von Auto Loader/`read_files` innerhalb der Streaming Table |

### Zu "Skalierung bei vielen Dateien" und "Datei-Erkennungskosten"

Diese beiden Zeilen beschreiben zwei unterschiedliche, aber verwandte Aspekte, die in der Doku nur für Auto Loader explizit behandelt werden:

- **Skalierung bei vielen Dateien** beantwortet die Frage: *Wie viele Dateien insgesamt kann das System effizient verarbeiten/verwalten?* Auto Loader kann Milliarden von Dateien effizient verarbeiten (z. B. für Migration oder Backfill einer Tabelle) und skaliert auf eine Ingestion von Millionen Dateien pro Stunde nahezu in Echtzeit. Für `read_files` (Batch) und `spark.read` gibt es dazu keine vergleichbare Aussage — das bedeutet nicht zwingend, dass diese es nicht könnten, nur dass keine offizielle Skalierungsangabe wie bei Auto Loader existiert.

- **Datei-Erkennungskosten** beantwortet eine andere Frage: *Wie aufwändig ist es, überhaupt herauszufinden, welche Dateien neu bzw. zu verarbeiten sind* — also der Erkennungsschritt selbst, nicht die anschließende Verarbeitung. Die Kosten der Dateierkennung skalieren bei Auto Loader mit der Anzahl der eingelesenen Dateien, nicht mit der Anzahl der Verzeichnisse, in denen sie liegen — im Gegensatz zur klassischen `spark.readStream`-File-Source, die bei jedem Micro-Batch das komplette Verzeichnis neu auflisten muss. Zusätzlich nutzt Auto Loader native Cloud-APIs zum Abrufen von Dateilisten; der optionale (⚙️) File-Notification-Modus kann diese Kosten weiter senken, indem das wiederholte Directory Listing komplett vermieden wird — Auto Loader richtet die dafür nötigen Cloud-Benachrichtigungsdienste automatisch ein, sobald der Modus konfiguriert ist (siehe Abschnitt 11).

Beide Punkte hängen zusammen: Weil die Erkennungskosten bei Auto Loader mit der Dateianzahl statt der Verzeichnisanzahl skalieren, bleibt Auto Loader auch bei sehr vielen Dateien effizient — während die klassische File-Source bei großen, tief verschachtelten Verzeichnisstrukturen zunehmend langsamer und teurer wird.

---

## 1. Grundzweck und Kontext

`read_files` ist eine SQL-Tabellenfunktion, gedacht für den direkten Einsatz in `SELECT`-Abfragen, CTAS-Statements oder Streaming Tables innerhalb von Databricks SQL. Sie liest Dateien an einem angegebenen Speicherort ein und gibt die Daten tabellarisch zurück.

`spark.read` (`DataFrameReader`) ist die programmatische PySpark-/Scala-Schnittstelle, um Daten aus externen Speichersystemen (Dateisysteme, Key-Value-Stores etc.) als `DataFrame` zu laden.

**Praktische Konsequenz:** Beide lösen dieselbe grundlegende Aufgabe (Dateien einlesen), aber für unterschiedliche Werkzeuge — `read_files` für SQL-Nutzer/SQL-Notebooks, `spark.read` für Python-/Scala-Notebooks. `DataFrameReader`-Methoden, `read_files`, `COPY INTO` und Auto Loader teilen sich dieselben zugrunde liegenden Leseoptionen zur Steuerung des Dateilesens.

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

**Was ist Schema-Inferenz?** Statt das Schema (Spaltennamen und Datentypen) manuell vorzugeben, liest das System die Daten selbst an und leitet das Schema automatisch daraus ab.

**Beide** Methoden leiten das Schema automatisch ab, wenn keines angegeben wird — mit leicht unterschiedlicher Dokumentation der Details.

### `read_files`

Wird kein Schema angegeben, versucht `read_files`, ein einheitliches Schema über alle entdeckten Dateien abzuleiten. Dafür müssen — sofern kein `LIMIT` verwendet wird — grundsätzlich alle Dateien gelesen werden.

```sql
-- Explizites Schema, um vollständige Schema-Inferenz zu vermeiden
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv',
    schema => 'id int, ts timestamp, event string');
```

### `spark.read`

Manche Datenquellen (z. B. JSON) können ihr Schema automatisch aus den Daten ableiten. Wird das Schema explizit über `.schema()` angegeben, kann die zugrunde liegende Datenquelle diesen Inferenzschritt überspringen, was das Laden beschleunigt. Für JSON ist zusätzlich dokumentiert, dass ohne Schema-Angabe die Eingabedaten einmal komplett gelesen werden, um das Schema zu bestimmen.

```python
# Explizites Schema, um den zusätzlichen Lesedurchlauf zu vermeiden
df = spark.read.schema("id int, ts timestamp, event string").json("s3://bucket/path")
```

**Unterschied:** Bei `read_files` ist die Notwendigkeit, für eine vollständige Inferenz alle Dateien zu lesen, explizit dokumentiert (inkl. Hinweis, dass auch bei `LIMIT` mehr Dateien gelesen werden können, um ein repräsentatives Schema zu erhalten). Bei `spark.read` wird dies nur formatspezifisch erwähnt (z. B. bei JSON: ein einmaliges Durchlesen der Eingabe).

### Werden die Daten dabei zweimal gelesen?

Bei beiden Methoden entsteht ein zusätzlicher, separater Lesevorgang, wenn kein Schema angegeben wird:

1. **Erster Durchlauf (Inferenz):** Die Daten (bei `read_files` ohne `LIMIT` alle entdeckten Dateien, bei JSON in `spark.read` der komplette Input) werden gelesen, nur um Spalten und Datentypen zu bestimmen.
2. **Zweiter Durchlauf (eigentliches Laden):** Erst danach werden die Daten tatsächlich geparst und in das `DataFrame`/die Zieltabelle geladen.

Es handelt sich um einen zusätzlichen, vermeidbaren Schritt: Die Datenquelle kann diesen Inferenzschritt bei explizitem Schema "überspringen" — ein Schritt, der übersprungen werden kann, muss vorher separat stattgefunden haben.

**Einschränkung:** Es gibt keine feste Anzahl an Lesevorgängen (z. B. nicht "genau zweimal"). Bei `read_files` ohne `LIMIT` kann der Effekt sogar größer sein als "einmal mehr", weil alle Dateien für die Inferenz gelesen werden müssen — bei vielen/großen Dateien entsprechend aufwändiger als ein einzelner zusätzlicher Scan.

**Praktische Konsequenz für beide Methoden:** Ein explizit angegebenes Schema (`schema => '...'` bzw. `.schema(...)`) überspringt den Inferenz-Durchlauf vollständig und beschleunigt dadurch das Laden — besonders relevant bei großen oder häufig wiederholt gelesenen Datenmengen.

### Exkurs: `inferSchema` bei `spark.read` (CSV)

Anders als bei JSON ist Schema-Inferenz beim CSV-Reader **nicht** standardmäßig aktiv, sondern über die explizite Option `inferSchema` steuerbar:

```python
# inferSchema = false (Standard)
df = spark.read.option("inferSchema", False).csv("s3://bucket/path")

# inferSchema = true
df = spark.read.option("inferSchema", True).csv("s3://bucket/path")
```

| Wert | Verhalten |
|---|---|
| `false` (Standard) | Es findet **keine** Typ-Inferenz statt. Alle Spalten werden unabhängig vom tatsächlichen Inhalt als `string` eingelesen. Dadurch entfällt der zusätzliche Lesedurchlauf zur Typbestimmung — das Laden ist schneller, die Daten müssen aber ggf. nachträglich manuell in die gewünschten Typen (`int`, `double`, `timestamp` etc.) konvertiert werden. |
| `true` | Spark liest die Daten einmal vollständig (bzw. eine Stichprobe, abhängig von weiteren Optionen) durch, um für jede Spalte den plausibelsten Datentyp zu bestimmen (z. B. `integer`, `double`, `boolean`, `timestamp`, sonst `string` als Fallback). Es entsteht derselbe zusätzliche Inferenz-Durchlauf wie bereits oben für JSON beschrieben — mit entsprechend höherem Aufwand bei großen Dateien. |

**Einordnung zum Rest von Abschnitt 2:** `inferSchema` ist damit für CSV das funktionale Gegenstück zu dem, was bei JSON automatisch geschieht (dort gibt es keine eigene An/Aus-Option, da Inferenz dort Standardverhalten ist). Bei `read_files` existiert keine separate `inferSchema`-Option — dort wird die Typ-Inferenz implizit ausgelöst, sobald kein `schema`-Parameter angegeben wird, und lässt sich nicht formatspezifisch abschalten wie bei `spark.read.csv()`.

---

## 3. `schemaHints`

Dies ist der deutlichste Unterschied zwischen beiden Methoden.

### `read_files`: `schemaHints` ist eine dokumentierte, native Option

`schemaHints` ist Schemainformation, die an die Auto-Loader-Schema-Inferenz übergeben wird.

```sql
-- Nur die Spalte `id` gezielt auf integer überschreiben, Rest wird weiter abgeleitet
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaHints => 'id int');
```

### `spark.read`: `schemaHints` existiert nicht

Für den regulären `DataFrameReader` gibt es keine `schemaHints`-Option. `schemaHints` dient dazu, die von Auto Loader gewählte Typentscheidung (z. B. bei unterschiedlichen Datentypen derselben Spalte über mehrere Parquet-Dateien hinweg) gezielt zu überschreiben.

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

**Konsequenz:** Mit `read_files` lässt sich gezielt eine einzelne Spalte überschreiben, ohne das restliche Schema von der automatischen Inferenz auszuschließen. Mit `spark.read` ist das nicht möglich — hier muss entweder das komplette Schema definiert oder vollständig auf Inferenz gesetzt werden.

---

## 4. Die `_metadata`-Spalte

Hier verhalten sich beide Methoden identisch.

### `read_files`

`read_files` stellt eine `_metadata`-Spalte mit dateibezogenen Metadaten bereit. Diese muss in der Abfrage explizit referenziert werden, um in den Ergebnissen zu erscheinen.

```sql
SELECT * EXCEPT (content), _metadata
FROM read_files('/Volumes/my_catalog/my_schema/my_volume', format => 'binaryFile');
```

### `spark.read`

Auch bei `spark.read` muss die `_metadata`-Spalte in der Leseabfrage, in der die Quelle angegeben wird, explizit ausgewählt werden, um im zurückgegebenen `DataFrame` enthalten zu sein.

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

`read_files` selbst deckt beide Modi ab — der Unterschied liegt allein im `STREAM`-Schlüsselwort:

```sql
-- Batch
SELECT * FROM read_files('gs://my-bucket/avroData');

-- Streaming (identische Funktion, nur mit STREAM-Präfix, innerhalb einer Streaming Table)
CREATE OR REFRESH STREAMING TABLE avro_data
AS SELECT * FROM STREAM read_files('gs://my-bucket/avroData', includeExistingFiles => false);
```

`read_files` kann in einer Streaming Table verwendet werden, um Dateien in Delta Lake einzulesen, wobei intern Auto Loader zum Einsatz kommt. Für diesen Modus ist das Schlüsselwort `STREAM` zwingend erforderlich.

### `spark.read`: strikte Trennung durch zwei separate Klassen

`spark.read` ist ausschließlich für Batch gedacht. Streaming erfolgt über eine komplett andere Einstiegsmethode: `spark.readStream` (`DataStreamReader`), die Schnittstelle, um ein streamendes `DataFrame` aus externen Speichersystemen zu laden.

```python
# Batch
batch_df = spark.read.format("delta").load("/Volumes/<catalog>/<schema>/<volume>/events")

# Streaming — eigene Klasse, kein Parameter an spark.read
streaming_df = spark.readStream.format("delta").load("/Volumes/<catalog>/<schema>/<volume>/events")
```

**Kernunterschied:** `read_files` ist eine Funktion mit einem Schalter (`STREAM`-Präfix); `spark.read` und `spark.readStream` sind zwei separate Klassen (`DataFrameReader` vs. `DataStreamReader`) mit jeweils eigenem Methodensatz. Es gibt bei `spark.read` keine Option, die den Streaming-Modus aktiviert — man muss die Einstiegsmethode wechseln.

---

## 6. Datei-Tracking

### Batch-Modus: bei beiden Methoden identisch — kein Tracking

Weder `read_files` im reinen `SELECT`/CTAS-Kontext noch `spark.read` dokumentieren einen Mechanismus, der sich merkt, welche Dateien bereits gelesen wurden. Beide sind zustandslose Leseoperationen, die bei jeder Ausführung alle aktuell vorhandenen Dateien neu verarbeiten.

### Streaming-Modus: beide nutzen Checkpoints, aber mit unterschiedlicher Einstellbarkeit

`STREAM read_files(...)` nutzt intern Auto Loader und erbt dessen Tracking-Optionen direkt als Parameter der Funktion:

```sql
CREATE OR REFRESH STREAMING TABLE events_overwrite_aware
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  allowOverwrites => true,       -- Tracking-Parameter erweitern (auch Änderungszeitpunkt berücksichtigen)
  includeExistingFiles => false  -- nur beim ersten Start relevant
);
```

`spark.readStream` (die Streaming-Gegenstelle zu `spark.read`) konfiguriert Tracking ebenfalls über Optionen, aber getrennt von der eigentlichen `spark.read`-API:

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

Checkpoints und Write-Ahead-Logs arbeiten zusammen, um Verarbeitungsgarantien für Structured-Streaming-Workloads bereitzustellen.

**Kernunterschied:** Bei `read_files` liegen die Tracking-Parameter (`allowOverwrites`, `includeExistingFiles`) direkt als benannte Argumente der Funktion selbst vor. Bei `spark.readStream` werden dieselben zugrunde liegenden Auto-Loader-Optionen über das `cloudFiles.`-Präfix in `.option()` gesetzt — funktional identisch, aber syntaktisch getrennt von der reinen Lesefunktion.

**Gemeinsamkeit:** Bei beiden gilt: Tracking lässt sich im Batch-Modus nicht aktivieren — der Wechsel in den Streaming-Modus (`STREAM`-Schlüsselwort bzw. `spark.readStream`) ist in beiden Fällen zwingende Voraussetzung für jegliches Datei-Tracking.

---

## 7. Syntaktischer Grundunterschied: benannte Parameter vs. Methodenketten

Ein struktureller Unterschied, der sich durch alle vorherigen Punkte zieht:

- **`read_files`** verwendet benannte Parameter in einem einzigen Funktionsaufruf:
  ```sql
  read_files(path, format => 'json', schema => '...', schemaHints => '...')
  ```
- **`spark.read`** verwendet verkettete Methodenaufrufe:
  ```python
  spark.read.format("json").schema("...").option("...", "...").load(path)
  ```

Beide konfigurieren im Kern dieselben zugrunde liegenden Leseoptionen, unterscheiden sich aber in der Aufrufsyntax entsprechend ihrer jeweiligen Sprachumgebung (SQL vs. PySpark/Scala).

---

## 8. Was davon gehört eigentlich zu Auto Loader?

Auto Loader ist eindeutig eine bestimmte Structured-Streaming-Quelle, kein allgemeiner Sammelbegriff: Auto Loader stellt eine Structured-Streaming-Quelle namens `cloudFiles` bereit.

**Auto Loader ist also konkret die `cloudFiles`-Quelle.** Von den in diesem Vergleich behandelten Methoden gehören dazu:

### ✅ Gehört zu Auto Loader

| Methode | Warum |
|---|---|
| `spark.readStream.format("cloudFiles")` | Ist per Definition Auto Loader. |
| `STREAM read_files(...)` | Nutzt Auto Loader im Hintergrund für die Streaming-Ingestion. |
| `CREATE OR REFRESH STREAMING TABLE ... AS SELECT * FROM STREAM read_files(...)` | Folgt direkt aus obigem Punkt. |
| `cloudFiles.*`-Optionen (`allowOverwrites`, `includeExistingFiles`, `maxFileAge`, `schemaHints` im Auto-Loader-Kontext, `cloudFiles.inferColumnTypes` …) | Optionen mit dem `cloudFiles`-Präfix sind bewusst in einem eigenen Namensraum von anderen Structured-Streaming-Quellenoptionen getrennt. |
| RocksDB-Checkpoint-Tracking | Entdeckte Dateimetadaten werden in einem skalierbaren Key-Value-Store (RocksDB) im Checkpoint-Verzeichnis der Auto-Loader-Pipeline gespeichert. |
| `cloud_files_state`-Tabellenfunktion | Fragt explizit den Auto-Loader-internen Tracking-Zustand ab. |

### ❌ Gehört NICHT zu Auto Loader

| Methode | Warum nicht |
|---|---|
| `read_files()` im Batch-Kontext (ohne `STREAM`) | Reine Tabellenfunktion für `SELECT`/CTAS — kein Streaming, keine `cloudFiles`-Anbindung. |
| `spark.read` / `spark.read.load()` | Batch-`DataFrameReader` — komplett getrennte Klasse ohne `cloudFiles`-Bezug. |
| `spark.readStream.format("json"/"csv"/"parquet"/...)` ohne `cloudFiles` | Klassische Spark Structured Streaming File Source — eigener Checkpoint-Mechanismus (Offsets/Commits), aber nicht RocksDB-basiert und nicht `cloudFiles`. Databricks empfiehlt hier ausdrücklich Auto Loader als Alternative, sobald Structured Streaming zur Ingestion aus Cloud-Objektspeicher eingesetzt wird. |
| `COPY INTO` | Eigener Mechanismus mit Tracking über das Delta Transaction Log der Zieltabelle — kein `cloudFiles`, kein RocksDB. |
| CTAS | Reines Batch-SQL, keine Streaming-Quelle. |
| Streaming Tables allgemein | Nur dann Auto Loader, wenn intern `STREAM read_files(...)` bzw. `cloudFiles` verwendet wird — Streaming Tables können auch andere Quellen nutzen (z. B. Kafka, Delta-Tabellen als Stream), die nichts mit Auto Loader zu tun haben. |

**Fazit für diesen Vergleich:** Von `read_files` gehört nur der Streaming-Modus (`STREAM read_files(...)`) tatsächlich zu Auto Loader — der Batch-Modus nicht. Von `spark.read`/`spark.readStream` gehört ausschließlich `spark.readStream.format("cloudFiles")` zu Auto Loader; `spark.read` (Batch) hat damit gar keine Berührungspunkte, und selbst `spark.readStream` ohne `cloudFiles` zählt nicht dazu.

---

## 9. Was ist Auto Loader überhaupt?

Auto Loader verarbeitet neue Datendateien inkrementell und effizient, sobald sie in Cloud-Speicher eintreffen — ohne zusätzliche Einrichtung. Technisch ist Auto Loader die bereits erwähnte Structured-Streaming-Quelle `cloudFiles`: Bei einem angegebenen Eingabeverzeichnispfad im Cloud-Dateispeicher verarbeitet die `cloudFiles`-Quelle automatisch neue Dateien, sobald sie eintreffen, optional auch bereits vorhandene Dateien im Verzeichnis.

**Zur Skalierung:** Auto Loader kann eingesetzt werden, um Milliarden von Dateien zu migrieren oder eine Tabelle nachzubefüllen (Backfill), und skaliert auf eine nahezu Echtzeit-Ingestion von Millionen Dateien pro Stunde.

Databricks empfiehlt Auto Loader explizit als Standardwerkzeug, sobald Apache Spark Structured Streaming zur Ingestion von Daten aus Cloud-Objektspeicher eingesetzt wird.

---

## 10. Auto Loader in SQL — nicht nur PySpark/Scala

**Wichtige Korrektur/Ergänzung:** Auto Loader ist nicht auf PySpark/Scala beschränkt, sondern lässt sich auch direkt in **SQL** einsetzen. Auto Loader unterstützt sowohl Python als auch SQL in Lakeflow-Pipelines.

In SQL wird Auto Loader über die bereits in Abschnitt 5 behandelte `STREAM read_files(...)`-Syntax angesprochen — das ist der offizielle, dokumentierte Weg, Auto-Loader-Funktionalität aus SQL heraus aufzurufen:

```sql
CREATE OR REFRESH STREAMING TABLE ingestion_st
AS SELECT * FROM STREAM read_files(
  "/databricks-datasets/retail-org/sales_orders",
  format => "json"
);
```

Dieselbe Streaming Table lässt sich äquivalent auch in Python über `spark.readStream.format("cloudFiles")` in einer Lakeflow-Pipeline definieren — SQL und Python sind hier zwei gleichwertige Schnittstellen zu derselben zugrunde liegenden `cloudFiles`-Quelle:

```python
@dp.table
def customers():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("gs://mybucket/analysis/*/*/*.json")
    )
```
```sql
CREATE OR REFRESH STREAMING TABLE sales
AS SELECT *
FROM STREAM read_files(
  'gs://mybucket/analysis/*/*/*.json',
  format => "json"
);
```

**Einordnung:** `spark.read` (Batch-`DataFrameReader`) hat kein SQL-Äquivalent in diesem Sinne — `read_files` im Batch-Modus ist ohnehin bereits die SQL-Entsprechung zu `spark.read`. Bei Auto Loader hingegen ist die SQL-Fähigkeit (`STREAM read_files`) eine dokumentierte, eigenständige Fähigkeit, die weder `read_files` (Batch) noch `spark.read` in dieser Form besitzen, da Letztere gar nicht mit Auto Loader verbunden sind (siehe Abschnitt 8).

---

## 11. Zwei Datei-Erkennungsmodi: Directory Listing vs. File Notification

Eine weitere Fähigkeit, die ausschließlich Auto Loader betrifft: die Wahl zwischen zwei unterschiedlichen Mechanismen, um neue Dateien überhaupt zu erkennen.

- **Directory Listing (Standard):** Auto Loader erkennt neue Dateien durch Auflisten des Eingabeverzeichnisses. Dieser Modus lässt sich ohne zusätzliche Berechtigungskonfiguration starten, abgesehen vom Zugriff auf die Daten im Cloud-Speicher selbst.
- **File Notification (empfohlen für die meisten Workloads):** Auto Loader nutzt Benachrichtigungs- und Warteschlangendienste der Cloud-Infrastruktur, die auf Datei-Ereignisse im Eingabeverzeichnis abonniert sind. Dieser Modus ist performanter und skalierbarer als Directory Listing, da kein wiederholtes Auflisten des Verzeichnisses nötig ist.

Beide Modi lassen sich über Stream-Neustarts hinweg wechseln, wobei weiterhin exactly-once-Garantien gelten. Auch garantiert Auto Loader in keinem der beiden Modi eine bestimmte Reihenfolge, in der Dateien entdeckt oder verarbeitet werden.

```python
# Directory Listing (Standard) — keine zusätzliche Konfiguration nötig
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .load("/Volumes/analytics/bronze/events"))
```

```python
# File Notification Mode — performanter/skalierbarer, benötigt Cloud-Berechtigungen
# für automatisch eingerichtete Benachrichtigungs-/Warteschlangendienste
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.useNotifications", "true")
      .load("/Volumes/analytics/bronze/events"))
```

**Einordnung:** Weder `read_files` (Batch) noch `spark.read` besitzen ein Äquivalent zu diesen zwei Erkennungsmodi, da beide keinerlei fortlaufende Dateierkennung durchführen (siehe Abschnitt 6) — dieser Aspekt ist eine reine Auto-Loader-/Streaming-Fähigkeit.

---

## 12. Schema-Evolution-Modi und automatische Typ-Erweiterung

Über die reine Schema-Inferenz (Abschnitt 2) hinaus bietet Auto Loader mehrere konfigurierbare **Schema-Evolution-Modi**, die steuern, wie mit neu auftauchenden Spalten, umbenannten/gelöschten Spalten und Typänderungen umgegangen wird.

Diese Modi sind spezifisch für Auto Loader/`read_files` im Streaming-Kontext dokumentiert und gehen über das hinaus, was `spark.read` an Schema-Handling bietet — `spark.read` leitet das Schema bei jeder Ausführung unabhängig neu ab, ohne eine "Evolution" über mehrere Läufe hinweg zu verfolgen (siehe Abschnitt 2).

### Welche Arten von Schema-Änderungen abgedeckt werden

| Änderungstyp | Verhalten |
|---|---|
| **Neue Spalten** | Unterstützt, abhängig vom gewählten `schemaEvolutionMode` |
| **Spalten umbenennen** | Unterstützt — wird als neue Spalte behandelt; die alte Spalte erhält für neue Zeilen `NULL` |
| **Gelöschte Spalten** | Unterstützt als "Soft Delete" — neue Zeilen erhalten für die gelöschte Spalte `NULL` |
| **Typ-Erweiterung (Type Widening)** | Unterstützt ab Databricks Runtime 16.4 mit `schemaEvolutionMode => 'addNewColumnsWithTypeWidening'` |

### Die fünf `schemaEvolutionMode`-Werte im Detail

- **`addNewColumns`** (Standard, wenn kein Schema angegeben ist): Neue Spalten führen dazu, dass der Stream mit einer `UnknownFieldException` stoppt. Vor diesem Fehler leitet Auto Loader das Schema aus dem letzten Micro-Batch ab und aktualisiert den Schema-Speicherort — beim Neustart wird das erweiterte Schema verwendet. Bereits bestehende Spalten behalten ihren Datentyp.
- **`rescue`**: Schema bleibt eingefroren, der Stream läuft ohne Unterbrechung weiter. Neue oder nicht passende Spalten landen ausschließlich in der `rescuedDataColumn`.
- **`failOnNewColumns`**: Der Stream schlägt bei neuen Spalten fehl und startet erst nach manueller Schema-Aktualisierung neu — strikter als `addNewColumns`, da hier keine automatische Schema-Aktualisierung im Hintergrund erfolgt.
- **`none`** (Standard, wenn ein Schema angegeben ist): Schema entwickelt sich nicht weiter, neue Spalten werden ignoriert. Der Stream schlägt wegen Schema-Änderungen nicht fehl. Daten werden dabei **nicht** gerettet, außer die `rescuedDataColumn`-Option ist zusätzlich explizit gesetzt.
- **`addNewColumnsWithTypeWidening`**: Verhält sich wie `addNewColumns`, erweitert zusätzlich automatisch kompatible Datentypen (z. B. `int` → `long`, `float` → `double`), ohne dass Daten neu geschrieben werden müssen.

```sql
-- Neue Spalten werden automatisch zum Schema hinzugefügt (Standardverhalten ohne Schema-Angabe)
CREATE OR REFRESH STREAMING TABLE events_evolving
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'addNewColumns'
);
```

```sql
-- Neue Spalten werden ignoriert und landen stattdessen in der rescuedDataColumn
CREATE OR REFRESH STREAMING TABLE events_rescue_only
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'rescue'
);
```

```sql
-- Stream schlägt bei neuen Spalten fehl, bis das Schema manuell aktualisiert wird
CREATE OR REFRESH STREAMING TABLE events_strict
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'failOnNewColumns'
);
```

```sql
-- Automatische, verlustfreie Typ-Erweiterung zusätzlich zu neuen Spalten
CREATE OR REFRESH STREAMING TABLE events_type_widening
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'addNewColumnsWithTypeWidening'
);
```

### Type Widening im Detail

Unterstützte, verlustfreie Typ-Erweiterungen:

| Quelltyp | Mögliche Zieltypen |
|---|---|
| `byte` | `short`, `int`, `long`, `decimal`, `double` |
| `short` | `int`, `long`, `decimal`, `double` |
| `int` | `long`, `decimal`, `double` |
| `long` | `decimal` |
| `float` | `double` |
| `decimal` | `decimal` mit höherer Präzision/Skala |

Type Widening funktioniert für alle Formate mit Schema-Evolution-Unterstützung — sowohl Textformate (JSON, CSV, XML) als auch Binärformate (Avro, Parquet).

### Verwandte, aber eigenständige Bausteine

- **`rescuedDataColumn`** fungiert als Sicherheitsnetz über alle Evolution-Modi hinweg — selbst bei `addNewColumns` oder `failOnNewColumns` lässt sie sich zusätzlich aktivieren, um nicht passende Werte abzufangen (siehe Abschnitt 16).
- **`schemaHints`** überschreibt gezielt einzelne Spaltentypen während der anfänglichen Schema-Inferenz, wirkt sich aber nicht auf die spätere Evolution eines bereits gespeicherten Schemas aus (siehe Abschnitt 3).
- **Delta-Table-Ebene (`mergeSchema`/`overwriteSchema`)**: Beim Schreiben in Delta-Tabellen existieren zusätzlich eigene Schema-Evolution-Mechanismen (additiv bei `mergeSchema`, überschreibend bei `overwriteSchema`) — eine separate Ebene, unabhängig vom `cloudFiles.schemaEvolutionMode` von Auto Loader.
- **Einschränkung:** Der `from_json`-Parser unterstützt keine Schema-Evolution.

**Einordnung:** Diese Fähigkeit betrifft ausschließlich den Auto-Loader-/Streaming-Zweig von `read_files`; im Batch-`read_files` und bei `spark.read` existiert kein vergleichbares, über mehrere Läufe hinweg wirksames Evolutions-Konzept.

---

## 13. Beobachtbarkeit und Zustandsabfrage (`cloud_files_state`)

`cloud_files_state` wurde in Abschnitt 8 bereits als Zuordnungskriterium zu Auto Loader genannt; hier als eigenständige **Fähigkeit** im Detail: Auto Loader erlaubt es, den internen Ingestion-Zustand direkt abzufragen — eine Möglichkeit, die weder `read_files` (Batch) noch `spark.read` bieten, da diese keinen Zustand besitzen, den man abfragen könnte.


```sql
-- Datei-Level-Zustand eines Auto-Loader-/read_files-Streams abfragen
SELECT * FROM cloud_files_state(TABLE(workspace.default.events_delta));
```

Damit lässt sich pro Datei nachvollziehen, ob sie bereits verarbeitet wurde, sich noch in Verarbeitung befindet oder aufgrund von Beschädigung übersprungen wurde — eine Beobachtbarkeits-Fähigkeit, die eng mit dem in Abschnitt 6 behandelten Tracking zusammenhängt, hier aber als eigene, abfragbare Schnittstelle betrachtet wird.

---

## 14. Vorteile von Auto Loader gegenüber `spark.readStream` ohne `cloudFiles`

Auto Loader wird hier explizit mit der klassischen, generischen Structured-Streaming-File-Source (`spark.readStream.format(fileFormat).load(directory)` ohne `cloudFiles`) verglichen — also genau der Methode, die in Abschnitt 8 als "nicht zu Auto Loader gehörend" eingeordnet wurde. Dabei ergeben sich folgende Vorteile:

| Vorteil | Beschreibung |
|---|---|
| **Skalierbarkeit** | Auto Loader kann Milliarden Dateien effizient entdecken. Backfills können asynchron durchgeführt werden, ohne Rechenressourcen zu verschwenden. |
| **Performance** | Die Kosten der Dateierkennung skalieren mit der Anzahl der eingelesenen Dateien, nicht mit der Anzahl der Verzeichnisse, in denen die Dateien liegen. |
| **Schema-Inferenz und -Evolution** | Auto Loader kann Schema-Drifts erkennen, über Schema-Änderungen benachrichtigen und Daten "retten", die andernfalls ignoriert oder verloren gegangen wären. |
| **Kosten** | Auto Loader nutzt native Cloud-APIs, um Dateilisten abzurufen. Zusätzlich kann der File-Notification-Modus Cloud-Kosten weiter senken, indem das Directory Listing vollständig vermieden wird — Auto Loader kann die dafür nötigen Benachrichtigungsdienste im Speicher automatisch einrichten. |

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

## 15. Vorteile von Auto Loader gegenüber `read_files` (Batch) und `spark.read`

Die in Abschnitt 14 genannten Vorteile gelten strukturell auch im Vergleich zu den Batch-Methoden `read_files` (ohne `STREAM`) und `spark.read`, da diese ohnehin keine inkrementelle Verarbeitung, kein Tracking und keine automatische Schema-Evolution bieten (siehe Abschnitte 2, 5 und 6 dieses Vergleichs):

- **Inkrementelle Verarbeitung statt vollständigem Neu-Einlesen:** Während `read_files` (Batch) und `spark.read` bei jeder Ausführung alle aktuell vorhandenen Dateien neu verarbeiten (siehe Abschnitt 6), verarbeitet Auto Loader nur neue Dateien, sobald sie eintreffen — ohne dass die Kosten mit der Gesamtdatenmenge im Verzeichnis wachsen.
- **Exactly-once-Garantie ohne eigenen Zustand:** Bei Auto Loader muss kein eigener Zustand verwaltet werden, um Fehlertoleranz oder exactly-once-Semantik zu erreichen. Bei `read_files` (Batch) und `spark.read` gibt es dagegen überhaupt keinen Zustand, den man verwalten könnte — jede erneute Ausführung ist unabhängig und vollständig.
- **Schema-Drift-Erkennung über die Zeit:** Auto Loader erkennt und meldet Schema-Änderungen zwischen aufeinanderfolgenden Ausführungen. `read_files` (Batch) und `spark.read` leiten das Schema bei jeder Ausführung neu und unabhängig voneinander ab — ohne Bezug zu vorherigen Läufen (siehe Abschnitt 2).
- **Massives Datenvolumen:** Die dokumentierte Fähigkeit, Milliarden Dateien effizient zu verarbeiten, ist für die genannten Batch-Methoden nicht dokumentiert — diese sind für einmalige/periodische Verarbeitung überschaubarer Datenmengen ausgelegt, nicht für kontinuierliche Ingestion in dieser Größenordnung.

**Zusammengefasst:** Die vier offiziell dokumentierten Vorteile (Skalierbarkeit, Performance, Schema-Inferenz/-Evolution, Kosten) sind zwar explizit im Vergleich zur generischen `spark.readStream`-File-Source formuliert, greifen aber aus denselben Gründen auch gegenüber den Batch-Methoden `read_files` und `spark.read` — mit dem zusätzlichen, grundlegenden Unterschied, dass Letztere gar nicht für inkrementelle/kontinuierliche Verarbeitung konzipiert sind (siehe Abschnitt 5).

---

## 16. Rescuing Malformed Rows — die `_rescued_data`-Spalte

Ein weiterer wichtiger Vergleichspunkt: Wie gehen `read_files`, `spark.read` und Auto Loader mit fehlerhaften/nicht zum Schema passenden Datensätzen um?

### Was ist die "Rescued Data Column"?

Die Rescued-Data-Spalte stellt sicher, dass beim ETL-Prozess keine Daten verloren gehen. Sie enthält alle Daten, die nicht geparst werden konnten — etwa weil ein Feld im angegebenen Schema fehlte, ein Typkonflikt vorlag, oder die Groß-/Kleinschreibung der Spalte nicht mit dem Schema übereinstimmte. Zurückgegeben wird die Spalte als JSON-Blob mit den geretteten Spalten sowie dem Quelldateipfad des Datensatzes.

Statt einen nicht passenden Datensatz zu verwerfen, wird er also nicht verloren, sondern in einer eigenen Spalte (standardmäßig `_rescued_data`) als JSON aufbewahrt — inklusive Pfad zur Quelldatei.

### `read_files`

Bei `read_files` ist die `rescuedDataColumn` standardmäßig aktiv, sofern kein explizites Schema angegeben wird bzw. Schema-Evolution zugelassen ist:

```sql
-- Standardmäßig wird eine rescuedDataColumn bereitgestellt, um nicht passende Daten zu "retten"
SELECT * FROM read_files('s3://bucket/path', format => 'json');
```

```sql
-- Die rescuedDataColumn lässt sich gezielt deaktivieren
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaEvolutionMode => 'none');
```

Zusätzlich unterstützt `read_files` (über die zugrunde liegenden CSV-/JSON-Parser-Optionen) den `mode`-Parameter:

```sql
-- mode "FAILFAST" bricht das Parsen der Datei mit einer RuntimeException ab,
-- sobald fehlerhafte Zeilen auftreten
SELECT * FROM read_files(
    's3://bucket/path/file.csv',
    format => 'csv',
    mode => 'FAILFAST');
```

### `spark.read`

Bei `spark.read` muss die `rescuedDataColumn`-Option explizit aktiviert werden — sie ist hier nicht standardmäßig eingeschaltet. Dazu wird die Option `rescuedDataColumn` mit einem Spaltennamen (üblicherweise `_rescued_data`) gesetzt.

```python
# rescuedDataColumn muss bei spark.read explizit gesetzt werden
df = (spark.read
      .option("rescuedDataColumn", "_rescued_data")
      .format("json")
      .load("/Volumes/<catalog>/<schema>/<volume>/events_json"))
```

### Auto Loader

Bei Auto Loader ist die `_rescued_data`-Spalte standardmäßig Teil des zurückgegebenen Schemas, sobald das Schema per Inferenz ermittelt wird.

```python
# Auto Loader: _rescued_data erscheint automatisch bei Schema-Inferenz
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .load("/Volumes/analytics/bronze/events"))
```

### Die drei Parser-Modi (`PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`) — gelten für alle drei

Für alle drei Methoden gilt dasselbe Grundverhalten der JSON-/CSV-Parser: Sie unterstützen die drei Modi `PERMISSIVE`, `DROPMALFORMED` und `FAILFAST`. In Kombination mit der `rescuedDataColumn` führen Typkonflikte in `DROPMALFORMED` nicht dazu, dass Datensätze verworfen werden, und lösen in `FAILFAST` keinen Fehler aus — nur wirklich korrupte Datensätze (unvollständiges oder fehlerhaftes JSON/CSV) führen zum Verwerfen bzw. zu einem Fehler.

Konkret bei CSV: Nur unvollständige und fehlerhafte CSV-Datensätze gelten als korrupt und werden in der Spalte `_corrupt_record` bzw. unter `badRecordsPath` erfasst.

**Wichtige Unterscheidung:**
- **Typ-Mismatches** (z. B. Text statt Zahl) → landen in `_rescued_data`, werden nicht verworfen (auch nicht in `DROPMALFORMED`/`FAILFAST`, solange `rescuedDataColumn` aktiv ist).
- **Wirklich korrupte/unvollständige Datensätze** (z. B. defektes JSON/CSV) → landen stattdessen in `_corrupt_record` bzw. `badRecordsPath`, oder lösen im `FAILFAST`-Modus einen Fehler aus.

### Vergleich im Überblick

| Aspekt | `read_files` | `spark.read` | Auto Loader |
|---|---|---|---|
| `rescuedDataColumn` standardmäßig aktiv? | ✅ Ja, bei Schema-Inferenz | ⚙️ Nein, muss per `.option("rescuedDataColumn", ...)` gesetzt werden | ✅ Ja, bei Schema-Inferenz |
| Deaktivierbar? | ✅ Ja, über `schemaEvolutionMode => 'none'` | Einfach die Option weglassen (ist ohnehin standardmäßig aus) | Über Schema-Evolution-Einstellungen konfigurierbar |
| Parser-Modi (`PERMISSIVE`/`DROPMALFORMED`/`FAILFAST`) | ✅ Ja | ✅ Ja | ✅ Ja |
| Korrupte (nicht nur typfalsche) Datensätze | `_corrupt_record` / `badRecordsPath` | `_corrupt_record` / `badRecordsPath` | `badRecordsPath` |

**Kernunterschied:** `read_files` und Auto Loader teilen sich das Verhalten (`_rescued_data` standardmäßig aktiv bei Inferenz), da `read_files` intern auf Auto-Loader-Mechanismen aufbaut. `spark.read` als klassischer, reiner `DataFrameReader` verhält sich hier bewusst konservativer — die Rescued-Data-Funktion muss explizit angefordert werden, sonst gilt das Standard-Spark-Verhalten (`PERMISSIVE`-Modus ohne automatisches Retten von Typ-Mismatches in einer eigenen Spalte).

---

## 17. Wann wird tatsächlich eine Exception geworfen? — Systematische Übersicht

**Ausgangsfrage:** In welchen konkreten Situationen wirft Databricks eine Exception, weil Daten nicht zum (inferierten oder angegebenen) Schema passen? Diese Frage wird in der Doku **nicht an einer einzigen Stelle zusammenhängend** beantwortet — die einzelnen Auslöser sind über mehrere Doku-Seiten verteilt (CSV/JSON-Lese-Doku, Auto-Loader-Schema-Doku, Delta-Lake-Schema-Enforcement-Doku, Error-Class-Referenz). Dieser Abschnitt bündelt sie erstmals im Kontext dieses Vergleichs.

**Wichtige Grundunterscheidung, die die gesamte Doku durchzieht:**

- **Lese-Ebene** (`read_files`, `spark.read`, Auto Loader beim Parsen einzelner Datensätze): Ein Typ- oder Struktur-Konflikt in einem *einzelnen Datensatz* führt in der Regel **nicht** automatisch zu einer Exception — er wird geparst, verworfen oder gerettet, abhängig vom `mode`. Nur bestimmte, unten aufgeführte Situationen lösen tatsächlich einen Abbruch aus.
- **Schreib-/Evolutions-Ebene** (Schreiben in eine Delta-Tabelle, Fortsetzen eines Streams mit neuem Schema): Hier ist eine Exception der **dokumentierte Standardfall**, sobald sich das Schema der eingehenden Daten von dem der Zieltabelle bzw. des zuletzt bekannten Stream-Schemas unterscheidet — das ist bewusstes Schema-Enforcement, keine Fehlbehandlung.

### 17.1 Lese-Ebene: `read_files` / `spark.read` (Batch, CSV & JSON)

| Auslöser | Exception / Verhalten | Bedingung |
|---|---|---|
| `mode => 'FAILFAST'` + fehlerhafter/unvollständiger Datensatz | Abbruch mit `RuntimeException` (SQL-Beispiel: *"mode 'FAILFAST' aborts file parsing with a RuntimeException if malformed lines are encountered"*) | Nur bei **korrupten** Datensätzen (unvollständiges/fehlerhaftes CSV oder JSON) — **nicht** bei reinen Typkonflikten, sofern `rescuedDataColumn` aktiv ist |
| `mode => 'FAILFAST'` **ohne** `rescuedDataColumn` | Abbruch bereits bei Typkonflikten (z. B. Text in einer als Zahl inferierten Spalte) | Nur relevant, wenn die Rescued-Data-Spalte explizit deaktiviert wurde (bei `read_files` z. B. via `schemaEvolutionMode => 'none'` ohne zusätzliche `rescuedDataColumn`-Angabe) |
| CSV: Zeile mit **abweichender Spaltenanzahl** gegenüber der ersten Zeile (Header oder erste Datenzeile) | Datensatz gilt als *unvollständig* → landet in `_corrupt_record`/`badRecordsPath`, oder bricht bei `FAILFAST` ab | Die erste Zeile der Datei legt die erwartete Zeilenlänge fest; abweichende Zeilen gelten unabhängig vom Modus als korrupt |
| CSV: `enforceSchema` zusammen mit `rescuedDataColumn` **oder** `failOnUnknownFields` gesetzt | Fehler zur Konfigurationszeit (kein Lesefehler, sondern ein Validierungsfehler): *"The CSV option enforceSchema cannot be set when using rescuedDataColumn or failOnUnknownFields, as columns are read by name rather than ordinal."* | Tritt unabhängig vom Dateiinhalt auf, reine Optionskombination |
| CTAS/`CREATE TABLE ... AS SELECT`: deklarierte Spaltenanzahl passt nicht zur Anzahl der Spalten im Abfrageergebnis | Fehler laut Error-Class-Referenz: *"The number of columns (`<declaredCount>`) declared in `<statementType>` does not match the number of columns (`<queryCount>`) in the query output."* | Tritt beim Anlegen der Zieltabelle auf, nicht beim eigentlichen Dateilesen |
| `read_files` mit explizitem `schema`-Parameter, der nicht zum tatsächlichen Datei-Schema passt | Fehler laut Error-Class-Referenz: *"The schema provided to the file reference data source does not match the expected schema."* mit dem Hinweis, das Schema zu entfernen oder anzupassen | Betrifft insbesondere Formate mit eingebettetem Schema (Parquet/Avro), bei denen ein explizit angegebenes Schema dem im Dateiformat gespeicherten widerspricht |

**Wichtige Einschränkung (bereits in Abschnitt 16 angerissen, hier präzisiert):** Reine **Typkonflikte** einzelner Felder (z. B. `"abc"` in einer als `int` inferierten Spalte) gelten in Kombination mit aktiver `rescuedDataColumn` explizit **nicht** als korrupt — sie landen unabhängig vom `mode` (auch bei `FAILFAST`) in der Rescued-Data-Spalte, nicht in einer Exception. Nur **strukturell korrupte** Datensätze (unvollständiges/fehlerhaftes CSV oder JSON) lösen in `FAILFAST` einen Abbruch aus.

**Ebenfalls dokumentiert, aber kein Fehler im engeren Sinn:** Wird ein explizites Schema angegeben, das nicht zur tatsächlichen Spaltenreihenfolge einer CSV-Datei passt, erfolgt **keine** Exception — da CSV keine Spaltennamen-Metadaten besitzt, ordnet Spark die Schema-Felder rein positionsbasiert zu, wodurch Werte stillschweigend in falsche Felder rutschen können. Dasselbe gilt beim Einlesen mehrerer Dateien mit unterschiedlicher Spaltenreihenfolge in einem `spark.read`-Aufruf: Das Schema wird aus einer Stichprobe abgeleitet, wodurch Dateien mit abweichender Spaltenreihenfolge fehlerhaft, aber **ohne Exception**, zugeordnet werden können.

### 17.2 Streaming-Ebene: Auto Loader / `STREAM read_files`

| Auslöser | Exception | Bedingung |
|---|---|---|
| Neue, bisher unbekannte Spalte in den Daten, `schemaEvolutionMode => 'addNewColumns'` (Standard ohne angegebenes Schema) | `UnknownFieldException` (`org.apache.spark.sql.catalyst.util.UnknownFieldException: Encountered unknown field(s) during parsing: <column name>`) | Der Stream stoppt **bewusst** — vor dem Abbruch aktualisiert Auto Loader den Schema-Speicherort bereits mit dem erweiterten Schema; ein Neustart des Streams übernimmt dieses automatisch |
| Neue Spalte **oder** durch Type-Widening abgedeckte Typänderung, `schemaEvolutionMode => 'addNewColumnsWithTypeWidening'` | Ebenfalls `UnknownFieldException`, nach demselben Muster (Schema wird vor dem Abbruch aktualisiert) | Ab Databricks Runtime 16.4; Type Widening muss zusätzlich auf Ziel-Tabellenebene aktiviert sein |
| Neue Spalte, `schemaEvolutionMode => 'failOnNewColumns'` | Stream schlägt fehl und startet **nicht** automatisch mit erweitertem Schema neu — manuelles Eingreifen nötig | Strikter als `addNewColumns`: keine automatische Hintergrundaktualisierung des Schema-Speicherorts vor dem Fehler |
| Schema wurde explizit angegeben, gleichzeitig `schemaEvolutionMode => 'addNewColumns'` gewählt | Konfigurationsfehler: `addNewColumns` ist bei explizit angegebenem Schema nicht zulässig (funktioniert dort nur als `schemaHints`) | Betrifft die Kombination aus explizitem Schema + Evolution-Modus, unabhängig vom tatsächlichen Dateiinhalt |
| `cloudFiles.schemaHints`/`rescuedDataColumn` gemeinsam mit inkompatibler Nested-Struktur | Keine Exception, sondern stille Nicht-Erfassung: neue verschachtelte Felder erscheinen bei `rescue`-Modus nicht automatisch in der Zieltabelle, sondern nur als JSON in `_rescued_data` | Explizit als Design-Entscheidung dokumentiert ("rescue mode intentionally freezes the schema") |

### 17.3 Schreib-Ebene: Delta-Tabellen (Schema Enforcement)

Diese Ebene ist die **strengste** und liegt strukturell "hinter" dem reinen Lesen — sie betrifft das Schreiben der gelesenen Daten in eine Ziel-Delta-Tabelle und ist damit indirekt für alle drei Lesemethoden relevant, sobald deren Ergebnis in eine bestehende Delta-Tabelle geschrieben wird.

| Auslöser | Exception | Bedingung |
|---|---|---|
| Batch- oder Streaming-Schreibvorgang enthält neue Spalten gegenüber der Ziel-Delta-Tabelle | `AnalysisException`: *"A schema mismatch detected when writing to the Delta table (Table ID: ...). To enable schema migration using DataFrameWriter or DataStreamWriter, please set: '.option("mergeSchema", "true")'."* | Standardverhalten von Delta Lake (Schema Enforcement); tritt unabhängig davon auf, ob die Daten zuvor per `read_files`, `spark.read` oder Auto Loader gelesen wurden |
| Spaltentyp der eingehenden Daten weicht vom Typ in der Ziel-Delta-Tabelle ab und ist **nicht** kompatibel erweiterbar | `AnalysisException`/`DeltaAnalysisException`: *"Failed to merge fields '<column>' and '<column>'. Failed to merge incompatible data types <TypeA> and <TypeB>"* | Tritt auch **mit** aktiviertem `mergeSchema` auf, wenn keine verlustfreie Typ-Erweiterung möglich ist (z. B. `String` → `Int`) |
| Verschachtelte (nested) Felder werden hinzugefügt oder entfernt, selbst bei `mergeSchema => true` | Fehler beim Zusammenführen des Schemas — automatische Schema-Evolution unterstützt laut Doku nur Top-Level-Spalten | Explizit als Einschränkung dokumentiert: Nested-Feld-Änderungen werden von der automatischen Schema-Evolution nicht abgedeckt |
| Bereits geöffnetes `DataFrame`/`DeltaTable`-Objekt, dessen zugrunde liegendes Tabellenschema sich zwischenzeitlich inkompatibel geändert hat | `AnalysisException`: *"The schema of your Delta table has changed in an incompatible way since your DataFrame or DeltaTable object was created. Please redefine your DataFrame or DeltaTable object."* | Tritt insbesondere bei `MERGE`-Operationen auf parallel geänderten Tabellen auf |
| Reine Parquet-Tabellen (nicht Delta) mit abweichendem Schema beim Anhängen | `AnalysisException: cannot resolve '<column>' given input columns: [...]` | Parquet-Tabellen besitzen laut Doku kein eigenes Schema-Enforcement wie Delta; `mergeSchema` wird beim Schreiben in Parquet-Tabellen ignoriert |

### 17.4 Zusammenfassende Einordnung

- **Auf der reinen Lese-Ebene** von `read_files`/`spark.read` ist eine Exception die **Ausnahme**, nicht die Regel: Sie tritt praktisch nur bei `FAILFAST` in Kombination mit strukturell korrupten (nicht nur typfalschen) Datensätzen auf, oder bei bestimmten Konfigurationsfehlern (inkompatible Optionskombinationen, nicht passendes explizites Schema bei Formaten mit eingebettetem Schema).
- **Auf der Streaming-Ebene** von Auto Loader ist eine Exception (`UnknownFieldException`) bei neuen Spalten der **dokumentierte Normalfall**, sofern nicht explizit ein toleranterer Evolution-Modus (`rescue`) gewählt wurde — sie dient dort als kontrollierter Mechanismus, um den Stream mit aktualisiertem Schema neu zu starten, nicht als reiner Fehlerfall.
- **Auf der Schreib-Ebene** in Delta-Tabellen ist eine Exception bei Schema-Abweichungen ebenfalls der **dokumentierte Normalfall** (Schema Enforcement) — unabhängig davon, welche der drei Lesemethoden die Daten zuvor bereitgestellt hat.

**Praktische Konsequenz für dieses Vergleichsdokument:** Die in Abschnitt 16 beschriebene Rescued-Data-Spalte verhindert Exceptions auf der *Lese*-Ebene für Typkonflikte; sie verhindert **nicht** die hier neu beschriebenen Exceptions auf der *Schreib*-Ebene, sobald die geretteten bzw. geparsten Daten anschließend in eine Delta-Tabelle mit abweichendem Schema geschrieben werden.

---

## 18. Was gehört alles zu Declarative Pipelines?

`STREAM read_files(...)` wurde bisher immer im Kontext von `CREATE OR REFRESH STREAMING TABLE` gezeigt (Abschnitte 5, 10, 12). Diese Syntax ist Teil eines größeren Rahmenwerks: **Lakeflow Spark Declarative Pipelines** (frühere Bezeichnung: Delta Live Tables/DLT). Hier die Bausteine, die dazugehören.

### Die drei Dataset-Typen

Lakeflow Declarative Pipelines bieten drei Arten von Datasets:

- **Streaming Tables**: Verarbeiten jede Eingabezeile nur einmal — geeignet für Dateningestion und latenzarme Streaming-Transformationen, Append-only-Workloads, hohes Datenvolumen und ereignisgesteuerte Verarbeitung aus Cloud-Speicher oder Message-Bussen. Werden immer gegen Streaming-Quellen definiert (z. B. `STREAM read_files(...)`, wie in den vorherigen Abschnitten gezeigt).
- **Materialized Views**: Cachen Abfrageergebnisse und aktualisieren sie inkrementell — geeignet für komplexe Transformationen und analytische Abfragen, die von mehreren Datasets wiederverwendet werden. Verfolgen Änderungen in vorgelagerten Daten und verarbeiten bei Trigger nur die geänderten Daten inkrementell. Der Dateninhalt lässt sich nicht direkt verändern — nur über die Query-Definition.
- **Temporary Views**: Pipeline-interne Views, die Transformationslogik organisieren, ohne Daten zu materialisieren.

```sql
-- Streaming Table (Ingestion-Layer) — bereits aus vorherigen Abschnitten bekannt
CREATE OR REFRESH STREAMING TABLE orders_bronze
AS SELECT * FROM STREAM read_files('/Volumes/raw/orders', format => 'json');
```

```sql
-- Materialized View (Transformations-Layer) — inkrementell aktualisiert, keine STREAM-Quelle nötig
CREATE OR REFRESH MATERIALIZED VIEW customer_orders
AS SELECT c.customer_id, c.name, o.order_id, o.total
FROM customers c
JOIN orders_bronze o ON c.customer_id = o.customer_id;
```

### Flows

Ein **Flow** ist der grundlegende Datenverarbeitungsbaustein innerhalb von Pipelines: Er liest Daten aus einer Quelle, wendet benutzerdefinierte Verarbeitungslogik an und schreibt das Ergebnis in ein Ziel (Streaming Table oder Materialized View). Pipelines teilen sich dieselben Streaming-Flow-Typen (Append, Update, Complete) wie Spark Structured Streaming — aktuell sind davon nur Append und Update verfügbar.

### AUTO CDC

Eine spezielle Flow-Art für Change-Data-Capture (CDC): **AUTO CDC** (SQL: `APPLY CHANGES INTO`, Python: `apply_changes()`) verarbeitet CDC-Events unter Berücksichtigung von Reihenfolge, Deduplizierung und Schema-Evolution deklarativ, inklusive Unterstützung für SCD Typ 1 und Typ 2 — ohne dass dafür manueller Code für außer-der-Reihe eintreffende Events oder Streaming-Konzepte wie Watermarks geschrieben werden muss.

```sql
-- AUTO CDC: deklarative Verarbeitung von Change-Data-Capture-Events
CREATE OR REFRESH STREAMING TABLE customers_silver;

APPLY CHANGES INTO customers_silver
FROM STREAM customers_cdc_bronze
KEYS (customer_id)
SEQUENCE BY updated_at
STORED AS SCD TYPE 2;
```

### Sinks

Ein **Sink** ist ein Streaming-Ziel für eine Pipeline und unterstützt Delta-Tabellen, Apache-Kafka-Topics, Azure-EventHubs-Topics sowie benutzerdefinierte Python-Datenquellen. Ein Sink kann einen oder mehrere Streaming-Flows (Append, Update) empfangen.

### SQL- und Python-Entwicklung

Wie bereits in Abschnitt 10 gezeigt, lassen sich Pipelines sowohl in **SQL** als auch in **Python** entwickeln. SQL-Code zur Definition von Pipeline-Datasets nutzt durchgehend die `CREATE OR REFRESH`-Syntax für Materialized Views und Streaming Tables. Python wird von Databricks für umfangreichere Tests und Operationen empfohlen, die in SQL schwer umsetzbar sind (z. B. Metaprogrammierung).

### Automatische Orchestrierung als zentraler Vorteil

Gegenüber der manuellen Entwicklung mit Apache Spark und Structured-Streaming-APIs samt manueller Orchestrierung bieten Pipelines automatische Orchestrierung: Verarbeitungsschritte ("Flows") werden in korrekter Reihenfolge mit maximaler Parallelität ausgeführt, und vorübergehende Fehler werden gestuft wiederholt — vom einzelnen Spark-Task über den Flow bis zur gesamten Pipeline.

### Pipelines auch außerhalb von Lakeflow nutzbar

Streaming Tables und Materialized Views lassen sich auch **außerhalb** einer vollständigen Lakeflow-Declarative-Pipeline direkt in Databricks SQL erstellen, aktualisieren und abfragen — genau die Syntax, die in diesem Vergleichsdokument bereits mehrfach verwendet wurde (`CREATE OR REFRESH STREAMING TABLE ...`).

### Einordnung zu `read_files`, `spark.read` und Auto Loader

| Baustein | Bezug zu den bisher verglichenen Methoden |
|---|---|
| Streaming Table | Zielobjekt für `STREAM read_files(...)` bzw. `spark.readStream.format("cloudFiles")` (siehe Abschnitte 5, 8, 10) |
| Materialized View | Kein direktes Äquivalent bei `read_files`/`spark.read` — eigenständiges, inkrementell aktualisiertes Konstrukt für nachgelagerte Transformationen |
| AUTO CDC | Eigenständige Fähigkeit ohne Entsprechung bei `read_files` (Batch) oder `spark.read` — deckt einen anderen Anwendungsfall (CDC-Verarbeitung) als reines Dateilesen ab |
| Sinks | Betrifft das Schreiben, nicht das Lesen — daher kein direkter Vergleichspunkt zu den in diesem Dokument behandelten Lesemethoden |
| SQL/Python-Wahlfreiheit | Deckt sich mit der in Abschnitt 10 gezeigten SQL-Fähigkeit von Auto Loader |

**Fazit:** Nur der Streaming-Table-Baustein steht in direktem Bezug zu `read_files` und Auto Loader aus diesem Vergleich. Materialized Views, AUTO CDC und Sinks sind eigenständige Konzepte des größeren Lakeflow-Declarative-Pipelines-Rahmenwerks, die über das reine Dateilesen hinausgehen und keine unmittelbare Entsprechung bei `spark.read` oder `read_files` (Batch) besitzen.

---

## 19. Zusammenfassung: Wann welche Methode?

| Situation | Empfehlung |
|---|---|
| SQL-Notebook / Databricks SQL, einzelne Spalten-Typen gezielt überschreiben | `read_files` mit `schemaHints` |
| Python-/Scala-Notebook, volle Kontrolle über Schema nötig | `spark.read` mit explizitem `.schema()` |
| Streaming Table direkt in SQL aufsetzen | `STREAM read_files(...)` |
| Streaming-Pipeline in PySpark mit `foreachBatch`/komplexer Logik | `spark.readStream` (ggf. mit `cloudFiles`) |
| Einmaliger Batch-Import/CTAS | Beide gleichwertig — Wahl abhängig von SQL- vs. Python-Kontext |
| Datei-Tracking benötigt | Bei beiden: zwingend Streaming-Modus (`STREAM` bzw. `spark.readStream`) |
| Große, laufend wachsende Datenmenge, kontinuierliche Ingestion | Auto Loader (`cloudFiles`) |
| Auto Loader ohne PySpark/Scala einsetzen | Auto Loader in SQL über `STREAM read_files(...)` |
| Sehr große Verzeichnisse mit häufigen neuen Dateien | Auto Loader im File-Notification-Modus statt Directory Listing |
| Ingestion-Zustand pro Datei einsehen/debuggen | `cloud_files_state`-Tabellenfunktion |
