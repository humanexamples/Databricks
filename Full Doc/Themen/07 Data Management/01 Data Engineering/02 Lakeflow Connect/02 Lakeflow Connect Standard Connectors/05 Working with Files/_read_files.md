# `read_files` — Referenz

Dieses Dokument fasst die Funktionsweise der Databricks-SQL-Tabellenfunktion `read_files` zusammen:

- Batch-Modus
- Streaming-Modus, inkl. der zugrunde liegenden Auto-Loader-Mechanismen im Streaming-Fall). 

## Abschnittsübersicht

1. [Grundzweck und Kontext](#grundzweck)
2. [Schema-Inferenz](#schema-inferenz)
3. [Vollständige Optionsreferenz](#optionsreferenz)
4. [`schemaHints`](#schemahints)
5. [Die `_metadata`-Spalte](#metadata-spalte)
6. [Batch- und Streaming-Modus über das `STREAM`-Schlüsselwort](#batch-streaming-modus)
7. [Datei-Tracking im Streaming-Modus](#datei-tracking)
8. [Syntax: benannte Parameter](#benannte-parameter)
9. [Zwei Datei-Erkennungsmodi im Streaming-Modus](#erkennungsmodi)
10. [Schema-Evolution-Modi und automatische Typ-Erweiterung](#schema-evolution-modi)
11. [Beobachtbarkeit und Zustandsabfrage (`cloud_files_state`)](#cloud-files-state)
12. [Vorteile des Streaming-Modus gegenüber dem Batch-Modus](#vorteile-streaming)
13. [Rescuing Malformed Rows — die `_rescued_data`-Spalte](#rescued-data)
14. [Wann wird tatsächlich eine Exception geworfen?](#exceptions)
15. [Zusammenfassung: Wann Batch, wann Streaming?](#zusammenfassung-batch-streaming)
16. [Beispielsammlung](#beispiele)

---

## <a id="grundzweck">1. Grundzweck und Kontext</a>

`read_files` ist eine SQL-Tabellenfunktion, gedacht für den direkten Einsatz in 

- `SELECT`-Abfragen
- CTAS-Statements oder 
- Streaming Tables innerhalb von Databricks SQL. 

Unterstützt: JSON, CSV, XML, TEXT, BINARYFILE, PARQUET, AVRO und ORC.

`read_files` kann das Dateiformat dabei auch automatisch erkennen und ein einheitliches Schema über alle Dateien hinweg ableiten.

```sql
SELECT * FROM read_files('s3://bucket/path', format => 'json', multiLine => true);
```

`read_files` benötigt zwingend benannte Parameter für alle Optionen außer dem Pfad. 

Der Pfad unterstützt Globs und das Lesen von 

- Azure Data Lake Storage (`abfss://`)
- S3 (`s3://`) 
- Google Cloud Storage (`gs://`).

### Rückgabeschema je nach Format

- **`BINARYFILE`**: feste Spalten 
  - `path` (`STRING`)
  - `modificationTime` (`TIMESTAMP`)
  - `length` (`LONG`)
  - `content` (`BINARY`).
- **`TEXT`**: feste Schema mit einer einzelnen Spalte:
  - `value` (`STRING`).
- **Alle anderen Formate** (JSON, CSV, XML, PARQUET, AVRO, ORC): Schema wird aus dem Dateiinhalt inferiert oder über die `schema`-Option explizit angegeben.

### `FILE`-Typ (Beta)

Mit `format => 'file'` gibt `read_files` statt des Dateiinhalts eine `FILE`-Referenz pro Datei zurück (Beta-Feature).

### File Discovery und Glob-Patterns

`read_files` liest entweder eine einzelne Datei oder rekursiv alle Dateien unter einem angegebenen Verzeichnis. Wird im Pfad ein Glob-Pattern angegeben, rekursiert `read_files` gezielt in das passende Verzeichnismuster.

| Pattern | Bedeutung |
|---|---|
| `?` | Genau ein beliebiges Zeichen |
| `*` | Null oder mehr Zeichen |
| `[abc]` | Ein Zeichen aus der Menge {a,b,c} |
| `[a-z]` | Ein Zeichen aus dem Bereich {a…z} |
| `[^a]` | Ein Zeichen, das **nicht** aus der Menge/dem Bereich {a} stammt |
| `{ab,cd}` | Ein String aus der Menge {ab, cd} |
| `{ab,c{de,fh}}` | Ein String aus der Menge {ab, cde, cfh} |

```sql
-- Nur Dateien mit .csv-Endung lesen
SELECT * FROM read_files('s3://bucket/path/*.csv');
```

`read_files` verwendet für Globs standardmäßig den **strikten** Auto-Loader-Globber (`useStrictGlobber => true`) — das ist der **umgekehrte** Standardwert gegenüber Auto Loader selbst (dort ist der strikte Globber standardmäßig deaktiviert). Beim strikten Globber werden abschließende Schrägstriche (`/`) nicht automatisch entfernt, wodurch Muster wie `/*/` nicht ungewollt mehrere zusätzliche Verzeichnisebenen erfassen. Verfügbar ab Databricks Runtime 12.2 LTS.

### Authentifizierung für Cloud-Speicher

`read_files` liest Dateien aus Unity-Catalog-External-Locations oder Unity-Catalog-Volumes (managed und external). Erforderlich ist das Privileg `READ FILES` auf der External Location bzw. `READ VOLUME` auf dem Volume, das die Dateien enthält.

Beispiele:

```sql
-- WRITE FILES, READ FILES auf External Location
GRANT READ FILES, WRITE FILES ON EXTERNAL LOCATION <location-name> TO <principal>;

SELECT * FROM read_files('s3://<bucket>/<path>', format => 'csv');
```

```sql
-- READ VOLUME-Privileg auf einem Unity-Catalog-Volume
GRANT READ VOLUME ON VOLUME <catalog>.<schema>.<volume-name> TO <principal>;

SELECT * FROM read_files('/Volumes/<catalog>/<schema>/<volume-name>', format => 'json');
```

---

## <a id="schema-inferenz">2. Schema-Inferenz</a>

Wird kein Schema angegeben, versucht `read_files`, ein einheitliches Schema über alle entdeckten Dateien abzuleiten. Dafür müssen — sofern kein `LIMIT` verwendet wird — grundsätzlich alle Dateien gelesen werden. Selbst bei Verwendung von `LIMIT` kann ein größeres Set an Dateien als nötig gelesen werden, um ein repräsentativeres Schema der Daten zurückzugeben; Databricks fügt SQL-Abfragen in Notebooks/SQL-Editor automatisch ein `LIMIT` hinzu, falls keines angegeben wurde.

**Wichtig:** Auch mit `LIMIT` liest `read_files` unter Umständen mehr Dateien, als für das Limit selbst nötig wären. Der Grund: Es soll ein repräsentativeres Schema der Daten zurückgegeben werden. Es ist also nicht garantiert, dass genau so viele Dateien gelesen werden, wie für `LIMIT n` Zeilen minimal nötig wären.

**Automatisches LIMIT in Notebooks/SQL-Editor:** Für interaktive `SELECT`-Abfragen in Notebooks und im SQL-Editor fügt Databricks automatisch ein `LIMIT` hinzu, falls keines angegeben wurde. Ob dieses automatische `LIMIT` auch bei CTAS-Statements oder Streaming-Table-Definitionen gilt, ist unklar.

```sql
-- Ohne LIMIT: read_files liest zur Schema-Inferenz grundsätzlich ALLE entdeckten Dateien
SELECT * FROM read_files('s3://bucket/path', format => 'json');

-- Mit LIMIT: read_files kann die Schema-Inferenz auf einen Teil der Dateien beschränken
-- (kann aber dennoch mehr als 10 Dateien lesen, um ein repräsentatives Schema zu liefern)
SELECT * FROM read_files('s3://bucket/path', format => 'json') LIMIT 10;
```

### Werden die Daten dabei zweimal gelesen?

Ja, faktisch entsteht ein zusätzlicher, separater Lesevorgang, wenn kein Schema angegeben wird:

1. **Erster Durchlauf (Inferenz):** Ohne `LIMIT` werden alle entdeckten Dateien gelesen, nur um Spalten und Datentypen zu bestimmen.
2. **Zweiter Durchlauf (eigentliches Laden):** Erst danach werden die Daten tatsächlich geparst und in das Ergebnis geladen.

**Einschränkung:** Es gibt keine feste Anzahl an Lesevorgängen (z. B. "genau zweimal"). Ohne `LIMIT` kann der Effekt sogar größer sein als "einmal mehr". Der Grund: Alle Dateien müssen für die Inferenz gelesen werden. Bei vielen oder großen Dateien ist das aufwändiger als ein einzelner zusätzlicher Scan.

**Praktische Konsequenz:** Ein explizit angegebenes Schema (`schema => '...'`) überspringt den Inferenz-Durchlauf vollständig und beschleunigt dadurch das Laden — besonders relevant bei großen oder häufig wiederholt gelesenen Datenmengen.

### `inferColumnTypes`

`read_files` besitzt die Option, die der `inferSchema`-Option von `spark.read.csv()` entspricht — sie heißt bei `read_files`  **`inferColumnTypes`**.

| Option | Standardwert bei `read_files` | Bedeutung |
|---|---|---|
| `inferColumnTypes` | `true` | Ob beim Ableiten des Schemas die exakten Spaltentypen bestimmt werden. Bei JSON und CSV werden die Spaltentypen standardmäßig inferiert. |

Der Standardwert von `inferColumnTypes` bei `read_files` ist `true`. Das ist das **Gegenteil** des Standardverhaltens von Auto Loader bei CSV- und JSON-Datentypen.

Der Standardwert `true` gilt gleichermaßen für **Batch-`read_files`** und für **`STREAM read_files`** — es gibt keinen separaten Default für den Streaming-Fall.

```sql
-- Spaltentypen exakt inferieren (Standard im Batch-Modus)
SELECT * FROM read_files('s3://bucket/path', format => 'csv', inferColumnTypes => true);

-- Alle Spalten als string belassen, keine Typ-Inferenz
SELECT * FROM read_files('s3://bucket/path', format => 'csv', inferColumnTypes => false);
```

Die Typ-Inferenz insgesamt wird implizit ausgelöst, sobald kein `schema`-Parameter angegeben wird.

### Schema mit verschachtelten Feldern (`STRUCT`, `ARRAY`)

Das DDL-Format, das `read_files` für den `schema`-Parameter erwartet, unterstützt auch verschachtelte Typen. Laut der offiziellen `STRUCT`-Typreferenz lautet die Syntax `STRUCT<feldname: typ, ...>`, mit optionalem `NOT NULL` und `COMMENT` je Feld; Arrays werden mit `ARRAY<typ>` deklariert. Bestätigtes Beispiel aus der Doku (dort zur Illustration der `STRUCT`-Syntax, nicht `read_files`-spezifisch): `STRUCT<Field1:INT NOT NULL COMMENT 'The first field.',Field2:ARRAY<INT>>`.

Eigenes Beispiel, das diese bestätigte Syntax auf `read_files` anwendet (mehrstufige Verschachtelung: `STRUCT` in `STRUCT`, `ARRAY` von `STRUCT`):

```sql
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schema => '
      id INT,
      user STRUCT<name: STRING, age: INT>,
      tags ARRAY<STRING>,
      address STRUCT<street: STRING, city: STRING, geo: STRUCT<lat: DOUBLE, lon: DOUBLE>>,
      orders ARRAY<STRUCT<order_id: STRING, amount: DOUBLE>>
    ');
```

---

## <a id="optionsreferenz">3. Vollständige Optionsreferenz (verifiziert)</a>

`read_files` teilt sich seine Leseoptionen laut der offiziellen **Spark-API-Optionsreferenz** mit `DataFrameReader.option()`, `COPY INTO` und Auto Loader — es gibt also eine gemeinsame Optionsbasis, die zusätzlich zu den `read_files`-eigenen Basis-/Streaming-Optionen (Abschnitte 2–10) zur Verfügung steht.

> Die **format-spezifischen** Leseoptionen (Ziel des Doku-Links `read_files#csv-options` u. a.) stehen auf der Spark-API-Optionsseite. Die **vollständige CSV-Leseoptionstabelle** (alle ~40 Optionen mit Defaults, inkl. `unescapedQuoteHandling`-Werte) ist übersetzt in `12 Query Data/01 Dateiformate/01 CSV lesen und schreiben.md`, Abschnitt „Vollständige CSV-Leseoptionen (Spark API Reference)".

### `read_files`-eigene Basisoptionen

| Option | Typ | Standardwert | Beschreibung |
|---|---|---|---|
| `format` | String | keiner (auto-erkannt) | Dateiformat: `avro`, `binaryFile`, `csv`, `file` (Beta), `json`, `orc`, `parquet`, `text`, `xml`. |
| `schema` | String | keiner | Schema im DDL-Format, z. B. `'id int, ts timestamp, event string'`. |
| `inferColumnTypes` | Boolean | `true` | Ob exakte Spaltentypen inferiert werden (siehe Abschnitt 2). |
| `partitionColumns` | String | keiner | Kommagetrennte Liste der aus Hive-Style-Verzeichnissen (`a=x/b=1/`) zu inferierenden Partitionsspalten. Leerer String ignoriert alle Partitionsspalten. Siehe unten. |
| `schemaHints` | String | keiner | Siehe Abschnitt 4. |
| `useStrictGlobber` | Boolean | `true` | Siehe Abschnitt 1 (Globbing). Ab Databricks Runtime 12.2 LTS. |

### Partitionsspalten (`partitionColumns`)

**Was sind Partitionsspalten?** Bei Hive-Style-partitionierten Verzeichnissen kodiert die Verzeichnisstruktur selbst Spaltenwerte als Schlüssel-Wert-Paare, verbunden durch ein Gleichheitszeichen — z. B. `<base-path>/a=x/b=1/c=y/file.format`. In diesem Beispiel sind `a`, `b` und `c` Partitionsspalten: Ihre Werte stehen nicht im Dateiinhalt, sondern im Pfad selbst.

**Automatische Erkennung:** Nutzt man Schema-Inferenz und übergibt den `<base-path>`, werden diese Partitionsspalten automatisch zum abgeleiteten Schema hinzugefügt. Wird stattdessen ein explizites `schema` angegeben, müssen die Partitionsspalten darin enthalten sein — andernfalls werden sie ignoriert.

**Rangfolge bei Namenskonflikt:** Existiert eine Spalte sowohl als Partitionsspalte im Pfad als auch als Datenspalte innerhalb der Datei, wird der aus dem Pfad gelesene Partitionswert verwendet.

**Die Option `partitionColumns` im Detail:**
- Kommagetrennte Liste der Partitionsspalten, die `read_files` aus der Verzeichnisstruktur übernehmen soll.
- Ein leerer String (`""`) ignoriert alle Partitionsspalten vollständig — sie bleiben reine Pfadinformation und erscheinen nicht im Ergebnis.
- Nützlich bei inkonsistenter Verzeichnistiefe: Wird z. B. `year,month,day` angegeben, aber manche Dateien liegen nur unter `year=2022/week=1/...` (ohne `month`/`day`), dann erhalten diese Dateien `year=2022`, während `month` und `day` `NULL` bleiben. Dateien unter `year=2022/month=2/day=3/...` werden dagegen vollständig geparst.

**Beispiel-Code:**

```sql
-- Automatische Partitionserkennung: year, month, day werden aus dem Pfad abgeleitet,
-- z. B. aus /Volumes/main/sales/raw/year=2024/month=03/day=15/data.csv
SELECT * FROM read_files(
    '/Volumes/main/sales/raw',
    format => 'csv');
```

```sql
-- partitionColumns explizit einschränken: nur year und month als Spalten übernehmen
SELECT * FROM read_files(
    '/Volumes/main/sales/raw',
    format => 'csv',
    partitionColumns => 'year,month');
```

```sql
-- Alle Partitionsspalten ignorieren: year/month/day bleiben reine Pfadinformation
-- und erscheinen nicht als Spalten im Ergebnis
SELECT * FROM read_files(
    '/Volumes/main/sales/raw',
    format => 'csv',
    partitionColumns => '');
```

```sql
-- Inkonsistente Verzeichnistiefe: manche Dateien haben nur "year" im Pfad, andere
-- zusätzlich "month" und "day" -- partitionColumns erzwingt trotzdem ein einheitliches Schema.
-- /base-path/year=2022/week=1/file1.csv           -> year=2022, month=NULL, day=NULL
-- /base-path/year=2022/month=2/day=3/file2.csv    -> year=2022, month=2,    day=3
SELECT * FROM read_files(
    '/base-path',
    format => 'csv',
    partitionColumns => 'year,month,day');
```

### `read_files`-eigene Streaming-Optionen (nur mit `STREAM`)

| Option | Typ | Standardwert | Beschreibung |
|---|---|---|---|
| `allowOverwrites` | Boolean | `false` | Ob nach der Entdeckung geänderte Dateien erneut verarbeitet werden — bei einem Refresh wird eine Datei erneut verarbeitet, wenn sie nach dem letzten erfolgreichen Refresh geändert wurde. |
| `includeExistingFiles` | Boolean | `true` | Ob bereits vorhandene Dateien beim ersten Start mitverarbeitet werden. Wird nur beim allerersten Start ausgewertet; spätere Änderungen der Option nach einem Neustart haben keine Wirkung. |
| `maxBytesPerTrigger` | Byte-String | keiner | Weiche Obergrenze für neue Bytes pro Trigger, z. B. `'10g'`. In Kombination mit `maxFilesPerTrigger` gilt jeweils das zuerst erreichte Limit. |
| `maxFilesPerTrigger` | Integer | `1000` | Maximale Anzahl neuer Dateien pro Trigger. |
| `schemaEvolutionMode` | String | `'addNewColumns'` ohne Schema, `'none'` mit Schema | Siehe Abschnitt 10. |
| `schemaLocation` | String | keiner | Speicherort für das inferierte Schema und dessen Änderungen. In einer Streaming Table nicht zwingend erforderlich. |

### `schemaLocation` im Detail

`schemaLocation` ist ausschließlich im Streaming-Modus (`STREAM read_files`) relevant, da `read_files` dort intern Auto Loader nutzt (siehe Abschnitt 6). Auto Loader legt an diesem Pfad ein Unterverzeichnis `_schemas` an, in dem das inferierte Schema und dessen Änderungen über die Zeit gespeichert werden — bestätigt auf der Auto-Loader-Schema-Seite (zweifach abgerufen, identischer Wortlaut beide Male): *"Auto Loader stores the schema information in a directory `_schemas` at the configured `cloudFiles.schemaLocation` to track schema changes to the input data over time."*

**Korrektur:** Eine vorherige Fassung dieses Abschnitts behauptete zusätzlich, bei einem Neustart werde das dort gespeicherte Schema wiederverwendet, statt erneut vollständig zu inferieren. Das ist **nicht belegt** — die Quelle sagt nur, dass Schemaänderungen über die Zeit nachverfolgt werden, äußert sich aber nicht explizit zum Neustart-Verhalten. Bestätigt ist das Wiederverwenden nur für den spezifischen Fall der Schema-Evolution nach einer `UnknownFieldException` (siehe Abschnitt 10: "beim Neustart wird das erweiterte Schema verwendet") — das ist ein anderer, enger gefasster Sachverhalt als eine allgemeine Schema-Wiederverwendung bei jedem Neustart.

```sql
CREATE OR REFRESH STREAMING TABLE events_bronze
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaLocation => '/Volumes/analytics/bronze/_schema'
);
```

**Ungeklärt:** Ob sich der Inhalt von `_schemas` gezielt selbst vorbefüllen lässt (um z. B. ein eigenes Startschema vorzugeben, ohne den `schema`-Parameter zu nutzen), ist auf der geprüften Seite nicht dokumentiert — das Verzeichnis wird dort als interner Tracking-Mechanismus von Auto Loader beschrieben, nicht als für Nutzer zum direkten Schreiben vorgesehene Schnittstelle.

### Format-übergreifende Basisoptionen (gemeinsam mit `spark.read`)

| Option | Standardwert | Beschreibung |
|---|---|---|
| `ignoreCorruptFiles` | `false` | Bei `true` laufen Spark-Jobs auch bei beschädigten Dateien weiter; bereits gelesene Inhalte werden zurückgegeben. Ab Databricks Runtime 11.3 LTS. |
| `ignoreMissingFiles` | `false` (Auto Loader) | Bei `true` laufen Spark-Jobs auch bei fehlenden Dateien weiter. Ab Databricks Runtime 11.3 LTS. |
| `modifiedAfter` | keiner | Nur Dateien mit Änderungszeitstempel **nach** dem angegebenen Zeitstempel. |
| `modifiedBefore` | keiner | Nur Dateien mit Änderungszeitstempel **vor** dem angegebenen Zeitstempel. |
| `pathGlobFilter` / `fileNamePattern` | keiner | Glob-Muster zur Dateiauswahl; bei `read_files` heißt die Option `fileNamePattern`. |
| `recursiveFileLookup` | `false` | Bei `true` werden auch verschachtelte Verzeichnisse durchsucht, die keinem Partitions-Namensschema folgen. |
| `ignoredPathSegmentRegex` | `^[._]` | Regex, der Dateien/Verzeichnisse beim Auflisten überspringt (Standard: Namen, die mit `_` oder `.` beginnen). Ab Databricks Runtime 19. |

```sql
-- Dateien, die gestern hochgeladen/geändert wurden
SELECT * FROM read_files(
    'gs://my-bucket/avroData',
    modifiedAfter => date_sub(current_date(), 1),
    modifiedBefore => current_date());

-- Nur Bilddateien nach Namensmuster filtern und nach Dateigröße einschränken
SELECT * EXCEPT (content), _metadata
FROM read_files(
    '/Volumes/my_catalog/my_schema/my_volume',
    format => 'binaryFile',
    fileNamePattern => '*.{jpg,jpeg,png,JPG,JPEG,PNG}')
```

---

## <a id="schemahints">4. `schemaHints`</a>

`schemaHints` ist Schemainformation, die an die Auto-Loader-Schema-Inferenz übergeben wird, um gezielt einzelne Spaltentypen zu überschreiben, ohne das restliche Schema von der automatischen Inferenz auszuschließen.

```sql
-- Nur die Spalte `id` gezielt auf integer überschreiben, Rest wird weiter abgeleitet
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaHints => 'id int');
```

`schemaHints` dient dazu, eine von Auto Loader/`read_files` getroffene Typentscheidung bei der Schema-Inferenz gezielt zu überschreiben. `schemaHints` lässt sich laut Doku auch für Partitionsspalten verwenden, um das inferierte Schema einer Partitionsspalte zu überschreiben. Array- und Map-Unterstützung für `schemaHints` ist ab Databricks Runtime 9.1 LTS verfügbar.

(Das zuvor hier stehende Beispiel "unterschiedliche Datentypen derselben Spalte über mehrere Parquet-Dateien hinweg" war eine nicht belegte, selbst ausgedachte Illustration und wurde entfernt — die Doku nennt kein konkretes Beispiel für den Anwendungsfall.)

**Bestätigt:** `schemaHints` greift laut Doku nur, wenn kein explizites `schema` angegeben ist (*"Auto Loader uses schema hints only if you do not provide a schema"*).

**Ungeklärt (Korrektur):** Eine frühere Fassung dieses Abschnitts behauptete zusätzlich, `schemaHints` wirke sich "nur auf die anfängliche Schema-Inferenz aus, nicht auf die spätere Evolution eines bereits gespeicherten Schemas" (siehe Abschnitt 10). Das ließ sich trotz gezielter Recherche (Auto-Loader-Schema-Seite, `read_files`-Seite, explizite Suche im Kontext der `schemaEvolutionMode`-Abschnitte) an keiner Stelle bestätigen — `schemaHints` wird in den Evolution-Abschnitten der Doku nicht erwähnt, weder zustimmend noch ablehnend. Da sowohl `schemaHints` als auch der Standard-Evolution-Modus `addNewColumns` nur ohne explizites Schema greifen, ist sogar denkbar, dass beide gleichzeitig aktiv sind.

Konkret, gezielt nachgeprüft und ebenfalls **ungeklärt**: Löst eine per `schemaHints` vorab deklarierte, noch nicht existierende Spalte (siehe `06 Auto Loader/01 Schema-Inferenz und -Evolution.md`, "Praxisbeispiel: Vorab-Deklaration künftiger Spalten"), sobald sie tatsächlich in den Daten auftaucht, unter `addNewColumns` noch eine `UnknownFieldException` aus — oder verhindert die Vorab-Deklaration diesen Fehlschlag für genau diese Spalte? Eine gezielte Nachfrage an die Auto-Loader-Schema-Seite ergab dazu keine Aussage; die Doku stellt nur die Vorab-Deklaration selbst fest, klärt aber nicht, ob sie die spätere Exception verhindert.

### `schemaHints` aus einer Variable befüllen

`schemaHints` ist laut Doku ein normaler String-Parameter — er lässt sich daher wie jeder andere String vorab in einer Variable zusammenbauen, statt ihn inline in die Abfrage zu schreiben. In einem Databricks-Notebook geschieht das typischerweise in Python, wobei der fertige String per f-String in die SQL-Anweisung eingesetzt wird:

```python
hints = "loyalty_tier STRING, region_code STRING, signup_ts TIMESTAMP"

spark.sql(f"""
  SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaHints => '{hints}')
""")
```

**Ungeklärt:** Ob sich `schemaHints` auch direkt als reine SQL-Session-Variable übergeben lässt (z. B. `DECLARE VARIABLE hints STRING DEFAULT '...'; ... schemaHints => hints`), konnte nicht verifiziert werden. Die `read_files`-eigene Funktionsreferenz beschränkt `option_value` explizit auf "literals and scalar functions" (Zitat aus der Argumente-Beschreibung), ohne Session-Variablen ausdrücklich zu erwähnen; die allgemeinere Referenzseite zur benannten Parameterübergabe erlaubt zwar "jeden Ausdruck, der implizit in den Parametertyp umgewandelt werden kann", nennt aber ebenfalls kein Variablenbeispiel. Die dedizierte Referenzseite zu `DECLARE VARIABLE` war bei der Recherche nicht erreichbar (HTTP 404 bei zwei verschiedenen URL-Varianten). Der oben gezeigte Python-Weg ist dagegen ein Standard-Notebook-Muster ohne Databricks-spezifische Einschränkung und funktioniert zuverlässig.

---

## <a id="metadata-spalte">5. Die `_metadata`-Spalte</a>

`read_files` stellt eine `_metadata`-Spalte mit dateibezogenen Metadaten bereit (`file_path`, `file_name`, `file_size`, `file_modification_time`, `file_block_start`, `file_block_length`). Diese muss in der Abfrage explizit referenziert werden, um in den Ergebnissen zu erscheinen — sie erscheint nicht automatisch bei `SELECT *`.

`_metadata` wird standardmäßig nicht in `SELECT *`-Ergebnissen eingeschlossen und muss explizit ausgewählt werden.

```sql
SELECT * EXCEPT (content), _metadata
FROM read_files('/Volumes/my_catalog/my_schema/my_volume', format => 'binaryFile');

-- Nur Bilddateien nach Namensmuster filtern und nach Dateigröße einschränken
SELECT * EXCEPT (content), _metadata
FROM read_files(
    '/Volumes/my_catalog/my_schema/my_volume',
    format => 'binaryFile',
WHERE _metadata.file_size BETWEEN 20000 AND 1000000; -- Die Zahlen sind in Bytes anggegeben.
```

---

## <a id="batch-streaming-modus">6. Batch- und Streaming-Modus über das `STREAM`-Schlüsselwort</a>

`read_files` selbst deckt beide Modi ab — der Unterschied liegt allein im `STREAM`-Schlüsselwort:

```sql
-- Batch
SELECT * FROM read_files('gs://my-bucket/avroData');

-- Streaming (identische Funktion, nur mit STREAM-Präfix, innerhalb einer Streaming Table)
CREATE OR REFRESH STREAMING TABLE avro_data
AS SELECT * FROM STREAM read_files('gs://my-bucket/avroData', includeExistingFiles => false);
```

`read_files` kann in einer Streaming Table verwendet werden, um Dateien in Delta Lake einzulesen, wobei intern **Auto Loader** zum Einsatz kommt. Für diesen Modus ist das Schlüsselwort `STREAM` zwingend erforderlich. Das bedeutet: Alle unten beschriebenen Auto-Loader-Fähigkeiten (Datei-Tracking, Erkennungsmodi, Schema-Evolution, `cloud_files_state`) stehen `read_files` nur im Streaming-Modus zur Verfügung — im reinen Batch-`SELECT`/CTAS-Kontext nicht.

---

## <a id="datei-tracking">7. Datei-Tracking im Streaming-Modus</a>

Im reinen `SELECT`/CTAS-Batch-Kontext dokumentiert `read_files` keinen Mechanismus, der sich merkt, welche Dateien bereits gelesen wurden — es ist eine zustandslose Leseoperation, die bei jeder Ausführung alle aktuell vorhandenen Dateien neu verarbeitet.

Im Streaming-Modus (`STREAM read_files(...)`) nutzt die Funktion intern Auto Loader und erbt dessen Tracking-Optionen direkt als benannte Argumente:

```sql
CREATE OR REFRESH STREAMING TABLE events_overwrite_aware
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  allowOverwrites => true,       -- Tracking-Parameter erweitern (auch Änderungszeitpunkt berücksichtigen)
  includeExistingFiles => false  -- nur beim ersten Start relevant
);
```

Entdeckte Dateimetadaten werden dabei in einem skalierbaren Key-Value-Store (RocksDB) im Checkpoint-Verzeichnis gespeichert — dieser Zustand ermöglicht exactly-once-Garantien, ohne dass ein eigener Tracking-Mechanismus verwaltet werden muss.

**Wichtig:** Tracking lässt sich im Batch-Modus nicht aktivieren — der Wechsel in den Streaming-Modus (`STREAM`-Schlüsselwort) ist zwingende Voraussetzung für jegliches Datei-Tracking.

---

## <a id="benannte-parameter">8. Syntax: benannte Parameter</a>

`read_files` verwendet durchgängig benannte Parameter in einem einzigen Funktionsaufruf:

```sql
SELECT * FROM read_files(
  path,
  format => 'json',
  schema => 'id int, ts timestamp, event string',
  schemaHints => 'id int'
);
```

Optionsnamen mit Punkten (z. B. aus dem `cloudFiles.`-Namensraum) müssen dabei in Backticks (`` ` ``) gesetzt werden.

---

## <a id="erkennungsmodi">9. Zwei Datei-Erkennungsmodi im Streaming-Modus</a>

Im Streaming-Modus (`STREAM read_files`, intern Auto Loader) stehen zwei Mechanismen zur Verfügung, um neue Dateien zu erkennen:

- **Directory Listing (Standard):** Neue Dateien werden durch Auflisten des Eingabeverzeichnisses erkannt. Dieser Modus lässt sich ohne zusätzliche Berechtigungskonfiguration starten, abgesehen vom Zugriff auf die Daten im Cloud-Speicher selbst.
- **File Notification (empfohlen für die meisten Workloads):** Es werden Benachrichtigungs- und Warteschlangendienste der Cloud-Infrastruktur genutzt, die auf Datei-Ereignisse im Eingabeverzeichnis abonniert sind. Dieser Modus ist laut Doku performanter und skalierbarer als Directory Listing. (Die Doku selbst begründet dies nicht näher — eine frühere Fassung dieses Dokuments hatte hier eine nicht belegte Begründung ergänzt; diese wurde entfernt.)

Beide Modi lassen sich über Stream-Neustarts hinweg wechseln, wobei weiterhin exactly-once-Garantien gelten. In keinem der beiden Modi wird eine bestimmte Reihenfolge garantiert, in der Dateien entdeckt oder verarbeitet werden.

```sql
-- File-Notification-Modus über das cloudFiles-Präfix (Backticks wegen des Punkts)
SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  `cloudFiles.useNotifications` => 'true'
);
```

Im reinen Batch-Modus (ohne `STREAM`) existiert kein Äquivalent zu diesen Erkennungsmodi, da hier keinerlei fortlaufende Dateierkennung stattfindet (siehe Abschnitt 7).

---

## <a id="schema-evolution-modi">10. Schema-Evolution-Modi und automatische Typ-Erweiterung</a>

Über die reine Schema-Inferenz (Abschnitt 2) hinaus bietet der Streaming-Modus von `read_files` mehrere konfigurierbare **Schema-Evolution-Modi**, die steuern, wie mit neu auftauchenden Spalten, umbenannten/gelöschten Spalten und Typänderungen umgegangen wird.

### Welche Arten von Schema-Änderungen abgedeckt werden

| Änderungstyp | Verhalten laut Doku |
|---|---|
| **Neue Spalten** | Unterstützt, abhängig vom gewählten `schemaEvolutionMode` |
| **Spalten umbenennen** | Unterstützt — wird als neue Spalte behandelt; die alte Spalte erhält für neue Zeilen `NULL` |
| **Gelöschte Spalten** | Unterstützt als "Soft Delete" — neue Zeilen erhalten für die gelöschte Spalte `NULL` |
| **Typ-Erweiterung (Type Widening)** | Unterstützt ab Databricks Runtime 16.4 mit `schemaEvolutionMode => 'addNewColumnsWithTypeWidening'` |

### Die fünf `schemaEvolutionMode`-Werte im Detail

- **`addNewColumns`** (Standard, wenn kein Schema angegeben ist): Neue Spalten führen dazu, dass der Stream mit einer `UnknownFieldException` stoppt. Vor diesem Fehler wird das Schema aus dem letzten Micro-Batch abgeleitet und der Schema-Speicherort aktualisiert — beim Neustart wird das erweiterte Schema verwendet. Bereits bestehende Spalten behalten ihren Datentyp.
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

Unterstützte, verlustfreie Typ-Erweiterungen laut Doku:

| Quelltyp | Mögliche Zieltypen |
|---|---|
| `byte` | `short`, `int`, `long`, `decimal`, `double` |
| `short` | `int`, `long`, `decimal`, `double` |
| `int` | `long`, `decimal`, `double` |
| `long` | `decimal` |
| `float` | `double` |
| `decimal` | `decimal` mit höherer Präzision/Skala |
| `date` | `timestampNTZ` (nur Parquet) |

Type Widening funktioniert für alle Formate mit Schema-Evolution-Unterstützung — sowohl Textformate (JSON, CSV, XML) als auch Binärformate (Avro, Parquet).

### Verwandte, aber eigenständige Bausteine

- **`rescuedDataColumn`** fungiert als Sicherheitsnetz über alle Evolution-Modi hinweg — selbst bei `addNewColumns` oder `failOnNewColumns` lässt sie sich zusätzlich aktivieren, um nicht passende Werte abzufangen (siehe Abschnitt 13).
- **`schemaHints`** überschreibt gezielt einzelne Spaltentypen während der anfänglichen Schema-Inferenz, wirkt sich aber nicht auf die spätere Evolution eines bereits gespeicherten Schemas aus (siehe Abschnitt 4).
- **Delta-Table-Ebene (`mergeSchema`/`overwriteSchema`)**: Beim Schreiben in Delta-Tabellen existieren zusätzlich eigene Schema-Evolution-Mechanismen (additiv bei `mergeSchema`, überschreibend bei `overwriteSchema`) — eine separate Ebene, unabhängig vom `schemaEvolutionMode` des Streaming-Modus.
- **Einschränkung:** Der `from_json`-Parser unterstützt keine Schema-Evolution.

**Einordnung:** Diese Fähigkeit betrifft ausschließlich den Streaming-Modus (`STREAM read_files`); im Batch-Modus existiert kein vergleichbares, über mehrere Läufe hinweg wirksames Evolutions-Konzept.

---

## <a id="cloud-files-state">11. Beobachtbarkeit und Zustandsabfrage (`cloud_files_state`)</a>

Der Streaming-Modus von `read_files` erlaubt es, den internen Ingestion-Zustand direkt abzufragen:

```sql
-- Datei-Level-Zustand eines read_files-Streams abfragen
SELECT * FROM cloud_files_state(TABLE(workspace.default.events_delta));
```

Damit lässt sich pro Datei nachvollziehen, ob sie bereits verarbeitet wurde, sich noch in Verarbeitung befindet oder aufgrund von Beschädigung übersprungen wurde. Diese Beobachtbarkeits-Fähigkeit hängt eng mit dem in Abschnitt 7 behandelten Tracking zusammen, ist aber eine eigene, abfragbare Schnittstelle. Im Batch-Modus existiert keine Entsprechung, da hier kein Zustand vorliegt, den man abfragen könnte.

---

## <a id="vorteile-streaming">12. Vorteile des Streaming-Modus gegenüber dem Batch-Modus</a>

Da der Streaming-Modus (`STREAM read_files`) intern Auto Loader nutzt, gelten die dafür dokumentierten Vorteile gegenüber dem reinen Batch-Modus (`read_files` ohne `STREAM`):

- **Inkrementelle Verarbeitung statt vollständigem Neu-Einlesen:** Während der Batch-Modus bei jeder Ausführung alle aktuell vorhandenen Dateien neu verarbeitet (siehe Abschnitt 7), verarbeitet der Streaming-Modus nur neue Dateien, sobald sie eintreffen — ohne dass die Kosten mit der Gesamtdatenmenge im Verzeichnis wachsen.
- **Exactly-once-Garantie ohne eigenen Zustand:** Im Streaming-Modus muss kein eigener Zustand verwaltet werden, um Fehlertoleranz oder exactly-once-Semantik zu erreichen. Im Batch-Modus gibt es dagegen überhaupt keinen Zustand, den man verwalten könnte — jede erneute Ausführung ist unabhängig und vollständig.
- **Schema-Drift-Erkennung über die Zeit:** Der Streaming-Modus erkennt und meldet Schema-Änderungen zwischen aufeinanderfolgenden Ausführungen. Der Batch-Modus leitet das Schema bei jeder Ausführung neu und unabhängig voneinander ab — ohne Bezug zu vorherigen Läufen (siehe Abschnitt 2).
- **Massives Datenvolumen:** Der Streaming-Modus kann laut Doku Milliarden Dateien effizient verarbeiten und skaliert auf eine nahezu Echtzeit-Ingestion von Millionen Dateien pro Stunde — eine Fähigkeit, die für den Batch-Modus nicht dokumentiert ist. Der Batch-Modus ist für einmalige/periodische Verarbeitung überschaubarer Datenmengen ausgelegt.
- **Kosten der Dateierkennung:** Im Streaming-Modus skalieren die Kosten der Dateierkennung mit der Anzahl der eingelesenen Dateien statt mit der Anzahl der Verzeichnisse; native Cloud-APIs werden zum Abrufen von Dateilisten genutzt, und der File-Notification-Modus kann diese Kosten weiter senken.

---

## <a id="rescued-data">13. Rescuing Malformed Rows — die `_rescued_data`-Spalte</a>

### Was ist die "Rescued Data Column"?

Die Rescued-Data-Spalte stellt sicher, dass beim ETL-Prozess keine Daten verloren gehen. Sie enthält alle Daten, die nicht geparst werden konnten — etwa weil ein Feld im angegebenen Schema fehlte, ein Typkonflikt vorlag, oder die Groß-/Kleinschreibung der Spalte nicht mit dem Schema übereinstimmte. Zurückgegeben wird die Spalte als JSON-Blob mit den geretteten Spalten sowie dem Quelldateipfad des Datensatzes.

### Verhalten bei `read_files`

Die `rescuedDataColumn` ist standardmäßig aktiv, sofern kein explizites Schema angegeben wird bzw. Schema-Evolution zugelassen ist:

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

### Die drei Parser-Modi (`PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`)

`read_files` unterstützt über die zugrunde liegenden JSON-/CSV-Parser die drei Modi `PERMISSIVE`, `DROPMALFORMED` und `FAILFAST`. In Kombination mit der `rescuedDataColumn` führen Typkonflikte in `DROPMALFORMED` nicht dazu, dass Datensätze verworfen werden, und lösen in `FAILFAST` keinen Fehler aus — nur wirklich korrupte Datensätze (unvollständiges oder fehlerhaftes JSON/CSV) führen zum Verwerfen bzw. zu einem Fehler.

Konkret bei CSV: Nur unvollständige und fehlerhafte CSV-Datensätze gelten als korrupt und werden in der Spalte `_corrupt_record` bzw. unter `badRecordsPath` erfasst.

**Wichtige Unterscheidung laut Doku:**
- **Typ-Mismatches** (z. B. Text statt Zahl) → landen in `_rescued_data`, werden nicht verworfen (auch nicht in `DROPMALFORMED`/`FAILFAST`, solange `rescuedDataColumn` aktiv ist).
- **Wirklich korrupte/unvollständige Datensätze** (z. B. defektes JSON/CSV) → landen stattdessen in `_corrupt_record` bzw. `badRecordsPath`, oder lösen im `FAILFAST`-Modus einen Fehler aus.

| Aspekt | `read_files` |
|---|---|
| `rescuedDataColumn` standardmäßig aktiv? | ✅ Ja, bei Schema-Inferenz |
| Deaktivierbar? | ✅ Ja, über `schemaEvolutionMode => 'none'` |
| Parser-Modi (`PERMISSIVE`/`DROPMALFORMED`/`FAILFAST`) | ✅ Ja |
| Korrupte (nicht nur typfalsche) Datensätze | `_corrupt_record` / `badRecordsPath` (Batch) bzw. `badRecordsPath` (Streaming, intern Auto Loader) |

`read_files` teilt sich dieses Verhalten (`_rescued_data` standardmäßig aktiv bei Inferenz) mit Auto Loader, da `read_files` intern auf dessen Mechanismen aufbaut.

---

## <a id="exceptions">14. Wann wird tatsächlich eine Exception geworfen?</a>

**Ausgangsfrage:** In welchen konkreten Situationen wirft `read_files` eine Exception, weil Daten nicht zum (inferierten oder angegebenen) Schema passen? Die Auslöser sind über mehrere Doku-Seiten verteilt (CSV/JSON-Lese-Doku, Auto-Loader-Schema-Doku, Delta-Lake-Schema-Enforcement-Doku, Error-Class-Referenz) und werden hier gebündelt. **Wichtiger Befund einer erneuten, gezielten Recherche:** Die `read_files`-Referenzseite selbst enthält keine einzige Erwähnung von "exception", "error", "fail" oder "FAILFAST" — sämtliche Aussagen in diesem Abschnitt stammen aus anderen Quellen, nicht von der `read_files`-Seite. Das erhöht das Risiko unbelegter Zusammenfassungen zusätzlich; entsprechend wurde 14.3 bei dieser Recherche grundlegend überarbeitet (siehe dort).

**Grundunterscheidung:**

- **Lese-Ebene** (Batch `read_files` bzw. Parsen einzelner Datensätze im Streaming-Modus): Ein Typ- oder Struktur-Konflikt in einem *einzelnen Datensatz* führt in der Regel **nicht** automatisch zu einer Exception — er wird geparst, verworfen oder gerettet, abhängig vom `mode`.
- **Schreib-Ebene** (Ergebnis wird in eine Delta-Tabelle geschrieben, oder ein Stream wird mit neuem Schema fortgesetzt): Hier ist eine Exception der **dokumentierte Standardfall**, sobald sich das Schema unterscheidet — bewusstes Schema-Enforcement, keine Fehlbehandlung.

### 14.1 Batch-Lese-Ebene

| Auslöser | Exception / Verhalten | Bedingung laut Doku |
|---|---|---|
| `mode => 'FAILFAST'` + fehlerhafter/unvollständiger Datensatz | Abbruch mit `RuntimeException` | Nur bei **korrupten** Datensätzen (unvollständiges/fehlerhaftes CSV oder JSON) — **nicht** bei reinen Typkonflikten, sofern `rescuedDataColumn` aktiv ist |
| `mode => 'FAILFAST'` **ohne** `rescuedDataColumn` | Abbruch bereits bei Typkonflikten | Nur relevant, wenn die Rescued-Data-Spalte explizit deaktiviert wurde (z. B. via `schemaEvolutionMode => 'none'` ohne zusätzliche `rescuedDataColumn`-Angabe) |
| CSV: Zeile mit **abweichender Spaltenanzahl** gegenüber der ersten Zeile (Header oder erste Datenzeile) | Datensatz gilt als *unvollständig* → landet in `_corrupt_record`/`badRecordsPath`, oder bricht bei `FAILFAST` ab | Die erste Zeile der Datei legt die erwartete Zeilenlänge fest |
| CSV: `failOnUnknownFields => true` gesetzt | Abbruch, sobald ein Datensatz Spalten enthält, die nicht im Schema stehen — statt sie stillschweigend zu verwerfen/retten | Standardmäßig `false`; explizit zu aktivieren |
| CSV: `failOnWidenedFields => true` gesetzt | Abbruch, sobald ein Feldwert nur durch Typ-Erweiterung zum deklarierten Schema-Typ passt, statt ihn stillschweigend zu retten | Standardmäßig `false`; `failOnUnknownFields => true` kann diesen Effekt überdecken |
| CSV: `enforceSchema` zusammen mit `rescuedDataColumn` **oder** `failOnUnknownFields` gesetzt | Fehler zur Konfigurationszeit — der genaue Wortlaut *"The CSV option enforceSchema cannot be set when using rescuedDataColumn or failOnUnknownFields, as columns are read by name rather than ordinal."* konnte wegen der Länge der Fehlerklassen-Referenzseite (mehrere hundert Einträge, bei Abruf abgeschnitten) nicht direkt verifiziert werden. Strukturell sehr ähnlich und **bestätigt** existiert die Fehlerklasse `AVRO_POSITIONAL_FIELD_MATCHING_UNSUPPORTED` für Avro: *"The use of positional field matching is not supported when either rescuedDataColumn or failOnUnknownFields is enabled."* | **Ungeklärt:** Ob die CSV-spezifische Meldung exakt so lautet, bleibt unbestätigt; dass die Optionskombination generell nicht zulässig ist, ist durch das Avro-Analogon und die `enforceSchema`-Beschreibung (Abschnitt 3) plausibel, aber nicht wörtlich belegt. |
| Avro: nicht parsbarer Datensatz **ohne** explizit gesetzten `mode` | Abbruch, da der Avro-**Standard**-`mode` `FAILFAST` ist — abweichend vom `PERMISSIVE`-Standard bei CSV/JSON | Betrifft ausschließlich das Avro-Format (siehe Abschnitt 3) |
| CTAS: deklarierte Spaltenanzahl passt nicht zur Anzahl der Spalten im Abfrageergebnis | **Korrektur:** Der hier ursprünglich zitierte Wortlaut ("The number of columns (...) declared in (...) does not match the number of columns (...) in the query output.") ließ sich bei gezielter Nachprüfung nicht verifizieren und weicht vom tatsächlich bestätigten Format der einschlägigen Databricks-Fehlerklassen-Familie ab. **Bestätigt** sind stattdessen die real existierenden Fehlerklassen `INSERT_COLUMN_ARITY_MISMATCH` und `CREATE_VIEW_COLUMN_ARITY_MISMATCH` mit dem Format *"Cannot write to `<tableName>`"* / *"Cannot create view `<viewName>`, the reason is: not enough/too many data columns: ... columns: `<X>`. Data columns: `<Y>`."* | **Ungeklärt:** Ob es eine analoge `..._COLUMN_ARITY_MISMATCH`-Klasse speziell für CTAS gibt, ließ sich wegen der Länge der Fehlerklassen-Referenzseite nicht bestätigen. |
| `read_files` mit `format => 'binaryFile'` und explizitem `schema`-Parameter, der nicht zum erwarteten Schema passt | **Korrektur:** Die bestätigte Fehlerklasse heißt `BINARY_FILE_DATA_SOURCE_SCHEMA_MISMATCH` mit dem Text *"The schema provided to the binary file data source does not match the expected schema. Expected schema: `<expectedSchema>` Provided schema: `<providedSchema>`."* — nicht "file reference data source", wie in einer früheren Fassung dieses Dokuments unzutreffend zitiert wurde. | Betrifft laut Fehlerklassen-Referenz namentlich das `BINARYFILE`-Format (festes Schema, siehe Abschnitt 1). **Ungeklärt:** Ob ein analoger Fehler auch bei Parquet/Avro mit inkompatiblem explizitem Schema exakt so protokolliert wird, wurde nicht verifiziert. |

**Wichtige Einschränkung:** Reine **Typkonflikte** einzelner Felder gelten in Kombination mit aktiver `rescuedDataColumn` explizit **nicht** als korrupt — sie landen unabhängig vom `mode` (auch bei `FAILFAST`) in der Rescued-Data-Spalte, nicht in einer Exception.

**Kein Fehler, aber fehleranfällig:** Wird ein explizites Schema angegeben, das nicht zur tatsächlichen Spaltenreihenfolge einer CSV-Datei passt, erfolgt **keine** Exception — CSV besitzt keine Spaltennamen-Metadaten, Spark ordnet die Schema-Felder rein positionsbasiert zu. Beim Einlesen mehrerer Dateien mit unterschiedlicher Spaltenreihenfolge wird das Schema aus einer Stichprobe abgeleitet, wodurch Dateien mit abweichender Spaltenreihenfolge fehlerhaft, aber ohne Exception, zugeordnet werden können.

### 14.2 Streaming-Ebene (`STREAM read_files`)

| Auslöser | Exception | Bedingung laut Doku |
|---|---|---|
| Neue, bisher unbekannte Spalte in den Daten, `schemaEvolutionMode => 'addNewColumns'` (Standard ohne angegebenes Schema) | `UnknownFieldException` (`org.apache.spark.sql.catalyst.util.UnknownFieldException: Encountered unknown field(s) during parsing: <column name>`) | Der Stream stoppt **bewusst** — vor dem Abbruch wird der Schema-Speicherort bereits mit dem erweiterten Schema aktualisiert; ein Neustart übernimmt dieses automatisch |
| Neue Spalte **oder** durch Type-Widening abgedeckte Typänderung, `schemaEvolutionMode => 'addNewColumnsWithTypeWidening'` | Ebenfalls `UnknownFieldException`, nach demselben Muster | Ab Databricks Runtime 16.4; Type Widening muss zusätzlich auf Ziel-Tabellenebene aktiviert sein |
| Neue Spalte, `schemaEvolutionMode => 'failOnNewColumns'` | Stream schlägt fehl und startet **nicht** automatisch mit erweitertem Schema neu | Strikter als `addNewColumns`: keine automatische Hintergrundaktualisierung vor dem Fehler |
| Schema wurde explizit angegeben, gleichzeitig `schemaEvolutionMode => 'addNewColumns'` gewählt | Konfigurationsfehler: `addNewColumns` ist bei explizit angegebenem Schema nicht zulässig (funktioniert dort nur als `schemaHints`) | Betrifft die Kombination aus explizitem Schema + Evolution-Modus |
| Nested-Struktur bei `schemaEvolutionMode => 'rescue'` | Für `rescue` allgemein dokumentiert: neue/nicht passende Spalten landen ausschließlich in `_rescued_data`, ohne den Stream zu unterbrechen | **Ungeklärt:** Bei gezielter Nachfrage auf der Auto-Loader-Schema-Seite wird nur das allgemeine `rescue`-Verhalten für neue Spalten beschrieben — ob dies explizit auch für neue Felder *innerhalb bestehender verschachtelter Structs* (nicht nur neue Top-Level-Spalten) so dokumentiert ist, wurde nicht bestätigt. |

### 14.3 Schreib-Ebene: Delta-Tabellen (Schema Enforcement)

Diese Ebene betrifft das Schreiben der von `read_files` gelesenen Daten in eine Ziel-Delta-Tabelle.

**Korrektur nach erneuter, gezielter Recherche:** Keine der zuvor hier als wörtliches Zitat ausgewiesenen Fehlermeldungen ließ sich bestätigen. Weder die kanonischen Delta-Schema-Seiten (`/aws/en/delta/update-schema`, `/aws/en/tables/schema-enforcement`) noch die verlinkten Knowledge-Base-Artikel zeigen den realen Exception-Text in einem Code-Block — sie beschreiben das Verhalten nur in Prosa bzw. mit ausdrücklich als "illustrativ" gekennzeichneten Beispielen (bestätigt durch zwei unabhängige Abrufe derselben KB-Seite mit widersprüchlichem Ergebnis beim exakten Wortlaut).

| Auslöser | Verhalten laut Doku | Einschränkung |
|---|---|---|
| Schreibvorgang enthält neue Spalten gegenüber der Ziel-Delta-Tabelle | Schlägt mit `AnalysisException` fehl, sofern `mergeSchema` nicht aktiviert ist — Standardverhalten von Delta Lake (Schema Enforcement), Fehlschlag selbst ist dokumentiert-normal | **Ungeklärt:** Der exakte Exception-Wortlaut ist nicht belegt — die KB "AnalysisException error due to a schema mismatch" nennt ihn nur als illustratives Beispiel, kein realer Systemoutput. Lösung laut KB: beim Schreiben `.option("mergeSchema", "true")` setzen. |
| Verschachtelte (nested) Felder werden bei **`MERGE INTO`**-Statements mit aktivierter automatischer Schema-Evolution hinzugefügt/entfernt | Schlägt fehl, da automatische Schema-Evolution laut KB "Delta Merge cannot resolve nested field" **nur Top-Level-Spalten** unterstützt, keine verschachtelten Felder | **Wichtig:** Diese Quelle bezieht sich explizit auf `MERGE INTO`, nicht auf einfache Schreib-/Append-Operationen wie bei `read_files` → CTAS/Streaming Table üblich. Ob dieselbe Einschränkung auch für reine Append-Schreibvorgänge gilt, wurde **nicht bestätigt**. |
| Spaltentyp der eingehenden Daten weicht ab und ist nicht kompatibel erweiterbar | **Ungeklärt:** Für dieses Szenario (außerhalb von `MERGE INTO`) wurde in keiner geprüften Databricks-Quelle ein bestätigter Fehlertext gefunden. | Die zuvor hier zitierte Meldung *"Failed to merge fields ... Failed to merge incompatible data types ..."* entspricht einem bekannten generischen Spark-SQL-Fehlerformat, ließ sich aber in keiner offiziellen Databricks-Quelle wörtlich bestätigen und wurde entfernt. |
| Reine Parquet-Tabellen (nicht Delta) mit abweichendem Schema beim Anhängen | **Ungeklärt:** Auch hierfür wurde keine Databricks-Quelle mit bestätigtem Fehlertext gefunden. | Die zuvor zitierte Meldung `cannot resolve '<column>' given input columns: [...]` ist ein bekanntes generisches Spark-Analyzer-Fehlerformat, aber nicht Databricks-doku-bestätigt und wurde entfernt. |

### 14.4 Was davon betrifft `read_files` selbst — und was nicht?

Auf Nachfrage erneut geprüft: Nicht alle Auslöser in 14.1–14.3 sind tatsächlich Verhalten von `read_files` selbst.

- **14.1 (Batch-Lese-Ebene) und 14.2 (Streaming-Ebene) betreffen `read_files` direkt.** Diese Exceptions entstehen, während `read_files` selbst die Dateien liest bzw. parst — im Batch-Fall über den zugrunde liegenden CSV/JSON/Avro-Parser, im Streaming-Fall über den intern genutzten Auto Loader. Beides ist Teil der Ausführung von `read_files`/`STREAM read_files` selbst.

- **14.3 (Schreib-Ebene) betrifft NICHT `read_files` selbst, sondern die umschließende SQL-Anweisung.** `read_files` ist eine reine Lese-Tabellenfunktion; sie schreibt selbst nichts. Die dort beschriebenen Exceptions entstehen erst, wenn das Ergebnis in eine Zieltabelle geschrieben wird — im `CREATE TABLE AS`/`CREATE STREAMING TABLE`/`INSERT`-Statement, das `read_files` umschließt. Dasselbe Delta-Schema-Enforcement-Verhalten träte identisch auf, wenn die Daten statt aus `read_files` aus `spark.read`, einer anderen Tabelle oder sonst einer Quelle stammten — es ist allgemeines Delta-Lake-Verhalten, kein `read_files`-spezifisches.

- **Der `MERGE INTO`-Fall in 14.3 liegt zusätzlich außerhalb des in diesem Dokument gezeigten `read_files`-Anwendungsfalls.** Alle Code-Beispiele hier nutzen `read_files` für `CREATE TABLE AS`/`CREATE OR REFRESH STREAMING TABLE` (Append-Schreiben), nicht für `MERGE INTO`. Der Nested-Field-Fehler träte nur auf, wenn das Ergebnis von `read_files` zusätzlich manuell in eine separate `MERGE INTO`-Anweisung eingespeist wird — ein Muster, das sonst nirgends in diesem Dokument vorkommt.

**Fazit:** Nur 14.1 und 14.2 beschreiben tatsächliches `read_files`-Verhalten. 14.3 ist allgemeines Delta-Lake-Schreibverhalten — hier belassen, weil es in der Praxis unmittelbar auf `read_files`-Ergebnisse angewendet wird (CTAS/Streaming Table), aber nicht spezifisch für `read_files` selbst.

### 14.5 Zusammenfassende Einordnung

- **Auf der Batch-Lese-Ebene** ist eine Exception die **Ausnahme**: v. a. `FAILFAST` mit strukturell korrupten Datensätzen, oder Konfigurationsfehler.
- **Auf der Streaming-Ebene** ist `UnknownFieldException` bei neuen Spalten der **dokumentierte Normalfall**, sofern nicht `rescue` gewählt wurde.
- **Auf der Schreib-Ebene** in Delta-Tabellen ist eine Exception bei Schema-Abweichungen der **dokumentierte Normalfall** (Schema Enforcement) — betrifft aber, wie in 14.4 dargelegt, nicht `read_files` selbst, sondern den umschließenden Schreibvorgang.

---

## <a id="zusammenfassung-batch-streaming">15. Zusammenfassung: Wann Batch, wann Streaming?</a>

| Situation | Empfehlung |
|---|---|
| SQL-Notebook / Databricks SQL, einzelne Spalten-Typen gezielt überschreiben | `read_files` mit `schemaHints` |
| Streaming Table direkt in SQL aufsetzen | `STREAM read_files(...)` |
| Einmaliger Batch-Import/CTAS | `read_files` ohne `STREAM` |
| Datei-Tracking benötigt | Zwingend Streaming-Modus (`STREAM`-Schlüsselwort) |
| Große, laufend wachsende Datenmenge, kontinuierliche Ingestion | `STREAM read_files(...)` (nutzt Auto Loader) |
| Sehr große Verzeichnisse mit häufigen neuen Dateien | `STREAM read_files` im File-Notification-Modus |
| Ingestion-Zustand pro Datei einsehen/debuggen | `cloud_files_state`-Tabellenfunktion |

---

## <a id="beispiele">16. Offizielle Beispielsammlung aus der Funktionsreferenz</a>

Die folgenden Beispiele stammen wörtlich aus der `read_files`-Funktionsreferenz (Abschnitte *Syntax*, *Arguments*, *Returns*, *Examples*). Sie ergänzen die themenbezogenen Snippets der vorherigen Abschnitte um die vollständige, unveränderte Beispielgalerie der Doku — inklusive der neueren Anwendungsfälle mit AI-Funktionen (`ai_query`, `ai_parse_document`) und dem Join von Dateien mit strukturierten Tabellen.

### Syntax

```
read_files(path [, option_key => option_value ] [...])
```

### Arguments

Die Funktion erfordert benannte Parameter für die Options-Keys.

- **`path`**: Ein `STRING` mit der URI des Speicherorts der Daten. Unterstützt das Lesen aus Azure Data Lake Storage (`'abfss://'`), S3 (`s3://`) und Google Cloud Storage (`'gs://'`). Kann Globs enthalten.
- **`option_key`**: Der Name der zu konfigurierenden Option. Optionen mit Punkten in Backticks (`` ` ``) setzen.
- **`option_value`**: Ein konstanter Ausdruck, auf den die Option gesetzt wird. Akzeptiert Literale und skalare Funktionen.

### Returns

Eine Tabelle mit den Daten der Dateien unter dem angegebenen `path`. Das Schema hängt vom Dateiformat ab:

- **`BINARYFILE`**: festes Schema mit den Spalten `path` (STRING), `modificationTime` (TIMESTAMP), `length` (LONG), `content` (BINARY).
- **`TEXT`**: festes Schema mit einer einzelnen Spalte `value` (STRING).
- **Alle anderen Formate** (JSON, CSV, XML, PARQUET, AVRO, ORC): Schema aus dem Dateiinhalt inferiert oder über die `schema`-Option angegeben.

### Examples

**Beispiel 1 – Format und Schema automatisch erkennen**
```sql
SELECT * FROM read_files('abfss://container@storageAccount.dfs.core.windows.net/base/path');
```

**Beispiel 2 – CSV mit angegebenem Schema**
```sql
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv',
    schema => 'id int, ts timestamp, event string');
```

**Beispiel 3 – CSV mit Headern (Schema inferiert)**
```sql
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv')
```

**Beispiel 4 – CSV-Dateien nach Endung lesen**
```sql
SELECT * FROM read_files('s3://bucket/path/*.csv')
```

**Beispiel 5 – einzelne JSON-Datei**
```sql
SELECT * FROM read_files(
    'abfss://container@storageAccount.dfs.core.windows.net/path/single.json')
```

**Beispiel 6 – JSON mit `schemaHints`**
```sql
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaHints => 'id int')
```

**Beispiel 7 – nach Änderungsdatum filtern**
```sql
SELECT * FROM read_files(
    'gs://my-bucket/avroData',
    modifiedAfter => date_sub(current_date(), 1),
    modifiedBefore => current_date())
```

**Beispiel 8 – Delta-Tabelle mit Quellpfad erstellen**
```sql
CREATE TABLE my_avro_data
  AS SELECT *, _metadata.file_path
  FROM read_files('gs://my-bucket/avroData')
```

**Beispiel 9 – Streaming Table nur mit neuen Dateien**
```sql
CREATE OR REFRESH STREAMING TABLE avro_data
  AS SELECT * FROM STREAM read_files('gs://my-bucket/avroData', includeExistingFiles => false);
```

**Beispiel 10 – Dateien in einem Volume auflisten (ohne `content`)**
```sql
SELECT
  * EXCEPT (content),
  _metadata
FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>',
  format => 'binaryFile');
```

**Beispiel 11 – Bilddateien nach Größe filtern**
```sql
SELECT
  * EXCEPT (content),
  _metadata
FROM read_files(
  '/Volumes/my_catalog/my_schema/my_volume',
  format => 'binaryFile',
  fileNamePattern => '*.{jpg,jpeg,png,JPG,JPEG,PNG}')
WHERE _metadata.file_size BETWEEN 20000 AND 1000000;
```

**Beispiel 12 – PDFs auflisten, die innerhalb des letzten Tages geändert wurden**
```sql
SELECT
  * EXCEPT (content),
  _metadata
FROM read_files(
  '/Volumes/my_catalog/my_schema/my_volume',
  format => 'binaryFile',
  fileNamePattern => '*.{pdf,PDF}')
WHERE modificationTime >= current_timestamp() - INTERVAL 1 DAY;
```

**Beispiel 13 – Bilder mit einer AI-Funktion verarbeiten**
```sql
SELECT
  path AS file_path,
  ai_query(
    'system.ai.llama-4-maverick',
    'Describe this image in ten words or less: ',
    files => content
  ) AS result
FROM read_files(
  's3://my-s3-bucket/path/to/images/',
  format => 'binaryFile',
  fileNamePattern => '*.{jpg,jpeg,png,JPG,JPEG,PNG}')
WHERE _metadata.file_size < 1000000
  AND _metadata.file_name LIKE '%robots%';
```

**Beispiel 14 – Dokumente parsen**
```sql
SELECT
  path AS file_path,
  ai_parse_document(
    content,
    map('version', '2.0')
  ) AS result
FROM read_files(
  '/Volumes/main/public/my_files/',
  format => 'binaryFile',
  fileNamePattern => '*.{jpg,jpeg,pdf,png}')
WHERE _metadata.file_name ILIKE '%receipt%';
```

**Beispiel 15 – Dateien mit strukturierten Tabellen joinen**
```sql
SELECT
  users.user_id,
  user_files.file_id,
  files._metadata.file_name AS file_name,
  files.* EXCEPT (content),
  ai_parse_document(files.content, map('version', '2.0')) AS parsed_document
FROM read_files(
  's3://my-bucket-name/files/',
  format => 'binaryFile',
  fileNamePattern => '*.{pdf,doc,docx,ppt,pptx,png,jpg,jpeg}') AS files
JOIN user_files
  ON user_files.file_id = element_at(split(files.path, '/'), -2)
JOIN users
  ON users.user_id = user_files.user_id
WHERE users.email LIKE '%@databricks.com'
  AND files._metadata.file_size < 10000000;
```

---

## <a id="quellen">17. Quellen</a>

- read_files table-valued function: https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files
- Spark API options reference (vollständige Optionslisten für CSV/JSON/Avro/Parquet/ORC/XML/Excel/Text, gemeinsame Basis von read_files, spark.read, COPY INTO und Auto Loader): https://docs.databricks.com/aws/en/spark/api-options
- Configure schema inference and evolution in Auto Loader: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema
- Schema evolution in Databricks: https://docs.databricks.com/aws/en/data-engineering/schema-evolution
- Automatic type widening with Auto Loader: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/type-widening
- CREATE STREAMING TABLE: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table
- What is Auto Loader?: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/
- Using Auto Loader with Unity Catalog: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/unity-catalog
- Read and write CSV files: https://docs.databricks.com/aws/en/query/formats/csv
- Compare Auto Loader file detection modes: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-detection-modes
- cloud_files_state table-valued function: https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/functions/cloud_files_state
- Auto Loader streaming query failure with unknownFieldException error (Knowledge Base): https://kb.databricks.com/auto-loader-streaming-query-failure-with-unknownfieldexception-error
- Error conditions in Databricks: https://docs.databricks.com/aws/en/error-messages/error-classes
- AnalysisException error due to a schema mismatch (Knowledge Base): https://kb.databricks.com/delta/analysisexception-error-due-to-a-schema-mismatch
- Delta Merge cannot resolve nested field (Knowledge Base): https://kb.databricks.com/delta/delta-merge-cannot-resolve-field
- Column drift when reading multiple delimited files (Knowledge Base): https://kb.databricks.com/data-sources/column-drift-when-reading-multiple-delimited-files-
