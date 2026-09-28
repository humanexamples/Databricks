# CSV-Dateien lesen und schreiben

CSV (comma-separated values) ist ein textbasiertes tabellarisches Format für Datenaustausch, ETL-Pipelines und Datenspeicherung. Databricks unterstützt CSV zum Lesen und Schreiben über Apache Spark – inklusive Schema-Inferenz, Kompression, Behandlung fehlerhafter Datensätze und Rescued Data.

> **Hinweis:** Databricks empfiehlt für SQL-Nutzer die tabellenwertige Funktion `read_files` zum Lesen von CSV-Dateien (ab Databricks Runtime 13.3 LTS). Wer CSV-Daten direkt per SQL ohne temporäre Views oder `read_files` liest, kann **keine** Datenquellen-Optionen angeben und **kein** Schema definieren.

## Voraussetzungen

Für die Nutzung von CSV-Dateien ist keine zusätzliche Konfiguration nötig. Das **Streaming** von CSV-Dateien erfordert allerdings [Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/).

## Optionen

CSV-Datenquellen werden über die Methoden `.option()` und `.options()` von `DataFrameReader` und `DataFrameWriter` konfiguriert. Vollständige Optionslisten: `DataFrameReader` CSV options und `DataFrameWriter` CSV options in der Spark-API-Dokumentation.

### Vollständige CSV-Leseoptionen (Spark API Reference)

Diese Optionsbasis gilt gemeinsam für `DataFrameReader.option()`, `read_files`, `COPY INTO` (`FORMAT_OPTIONS`) und Auto Loader.

| Option | Standard | Beschreibung |
|---|---|---|
| `badRecordsPath` | – | Pfad zum Speichern von Dateien mit Informationen über fehlerhafte CSV-Datensätze. |
| `charToEscapeQuoteEscaping` | `\0` | Zeichen zum Escapen des Quote-Escape-Zeichens, z. B. bei `[ " a\\", b ]`. |
| `columnNameOfCorruptRecord` | `_corrupt_record` | Spalte zum Speichern fehlerhafter, nicht parsebarer Datensätze. (Auto Loader unterstützt; nicht für `COPY INTO` legacy.) |
| `comment` | `\0` | Zeichen, das am Zeilenanfang einen Zeilenkommentar kennzeichnet. |
| `dateFormat` | `yyyy-MM-dd` | Format zum Parsen von Datums-Strings. |
| `emptyValue` | `""` (leerer String) | String-Repräsentation eines leeren Werts. |
| `enableDateTimeParsingFallback` | `false` | Ob bei Format-Nichtübereinstimmung auf das Legacy-Parsing zurückgefallen wird. |
| `encoding` / `charset` | `UTF-8` | Name der Zeichenkodierung der CSV-Dateien. (UTF-16/UTF-32 nicht mit Multiline-Modus kompatibel.) |
| `enforceSchema` | `true` | Ob das angegebene bzw. inferierte Schema zwangsweise auf die CSV-Dateien angewandt wird. |
| `escape` | `\` | Escape-Zeichen beim Parsen der Daten. |
| `extension` | `csv` | Erwartete Dateiendung beim Lesen. |
| `failOnUnknownFields` | `false` | Ob ein Fehler ausgelöst wird, wenn ein CSV-Datensatz Spalten enthält, die nicht im Schema stehen. |
| `failOnWidenedFields` | `false` | Ob ein Fehler ausgelöst wird, wenn Feldwerte nur durch Type Widening zum Schema-Typ passen. |
| `header` | `false` | Ob die CSV-Dateien eine Kopfzeile enthalten. |
| `ignoreLeadingWhiteSpace` | `false` | Ob führende Leerzeichen je geparstem Wert ignoriert werden. |
| `ignoreTrailingWhiteSpace` | `false` | Ob abschließende Leerzeichen je geparstem Wert ignoriert werden. |
| `inferSchema` | `false` | Ob die Datentypen der CSV-Datensätze inferiert werden oder alle Spalten als `StringType` gelten. |
| `inputBufferSize` | `1048576` (1 MB) | Puffergröße in Bytes für den CSV-Parser. |
| `lineSep` | – | String zwischen zwei aufeinanderfolgenden CSV-Datensätzen. |
| `locale` | `US` | Java-Locale, die das Standard-Parsing von Datum, Zeitstempel und Dezimalzahlen beeinflusst. |
| `maxCharsPerColumn` | `-1` | Maximale Zeichenanzahl, die für einen zu parsenden Wert erwartet wird. |
| `maxColumns` | `20480` | Harte Obergrenze für die Spaltenanzahl eines Datensatzes. |
| `mergeSchema` | `false` | Ob das Schema über mehrere Dateien hinweg inferiert und die Schemata der einzelnen Dateien zusammengeführt werden. |
| `mode` | `PERMISSIVE` | Parser-Modus für den Umgang mit fehlerhaften Datensätzen (`PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`). |
| `multiLine` | `false` | Ob CSV-Datensätze über mehrere Zeilen gehen. |
| `nanValue` | `NaN` | String-Repräsentation eines Not-a-Number-Werts. |
| `negativeInf` | `-Inf` | String-Repräsentation von negativer Unendlichkeit. |
| `nullValue` | `""` (leerer String) | String-Repräsentation eines `null`-Werts. |
| `parserCaseSensitive` (deprecated) | `false` | Ob im Header deklarierte Spalten case-sensitiv mit dem Schema abgeglichen werden. |
| `positiveInf` | `Inf` | String-Repräsentation von positiver Unendlichkeit. |
| `preferDate` | `true` | Versucht, Strings wenn möglich als `date` statt als `timestamp` zu inferieren. |
| `quote` | `"` | Zeichen zum Escapen von Werten, in denen der Feldtrenner Teil des Werts ist. |
| `readerCaseSensitive` | `true` | Case-Sensitivity-Verhalten, wenn `rescuedDataColumn` aktiviert ist. |
| `rescuedDataColumn` | – | Sammelt alle Daten, die wegen Typkonflikt oder Schema-Konflikt nicht geparst werden konnten. |
| `sep` / `delimiter` | `,` | Trennzeichen-String zwischen Spalten. |
| `singleVariantColumn` | – | Liest den gesamten CSV-Datensatz in eine einzelne `VariantType`-Spalte. (Erfordert `header=true`.) |
| `skipRows` | `0` | Anzahl der Zeilen ab Dateianfang, die ignoriert werden sollen. |
| `timeFormat` | `HH:mm:ss` | Format zum Parsen von `TimeType`-Spaltenwerten. |
| `timestampFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Format zum Parsen von Zeitstempel-Strings. |
| `timestampNTZFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS]` | Format zum Parsen von Zeitstempeln ohne Zeitzone. |
| `timeZone` | – | `java.time.ZoneId`, die beim Parsen von Zeitstempeln und Datumsangaben verwendet wird. |
| `unescapedQuoteHandling` | `STOP_AT_DELIMITER` | Strategie für nicht-escapte Quotes (siehe unten). |

**`unescapedQuoteHandling` — die fünf Werte:**

- **`STOP_AT_CLOSING_QUOTE`** — das Quote-Zeichen wird akkumuliert und der Wert weiter als quoted value geparst, bis ein schließendes Quote gefunden wird.
- **`BACK_TO_DELIMITER`** — der Wert gilt als unquoted; der Parser akkumuliert alle Zeichen des aktuellen Werts, bis der durch `sep` definierte Trenner gefunden wird.
- **`STOP_AT_DELIMITER`** — der Wert gilt als unquoted; der Parser akkumuliert alle Zeichen, bis der durch `sep` definierte Trenner **oder** ein Zeilenende gefunden wird.
- **`SKIP_VALUE`** — der geparste Inhalt für diesen Wert wird übersprungen (bis zum nächsten Trenner); stattdessen wird der in `nullValue` gesetzte Wert erzeugt.
- **`RAISE_ERROR`** — es wird eine `TextParsingException` geworfen.

> Auf derselben Spark-API-Reference-Seite stehen auch die Leseoptionen für Avro, Excel, JSON, Kafka, ORC, Parquet, State Store, Text und XML sowie die `DataStreamReader`-Optionen (Common Streaming, Auto Loader mit Directory-Listing/File-Notification, Kafka Streaming).

---

## Verwendung

### CSV-Dateien lesen

**Python**
```python
# Write wanderbricks reviews to CSV format
df = spark.read.table("samples.wanderbricks.reviews")
df.write.format("csv").option("header", "true").save("/Volumes/<catalog>/<schema>/<volume>/reviews_csv")

# Read the CSV file into a DataFrame
df = (spark.read
  .format("csv")
  .option("header", "true")
  .option("inferSchema", "true")
  .load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv"))
display(df)
df.printSchema()
```

**R**
```r
df <- read.df("/Volumes/<catalog>/<schema>/<volume>/reviews_csv", source = "csv", header = "true", inferSchema = "true")
display(df)
printSchema(df)
```

### CSV-Dateien mit SQL lesen

```sql
-- mode "FAILFAST" aborts file parsing with a RuntimeException if malformed lines are encountered
SELECT * FROM read_files(
  's3://<bucket>/<path>/<file>.csv',
  format => 'csv',
  header => true,
  mode => 'FAILFAST')
```

### CSV-Dateien über einen temporären View lesen

```sql
CREATE TEMPORARY VIEW diamonds
USING CSV
OPTIONS (path "/databricks-datasets/Rdatasets/data-001/csv/ggplot2/diamonds.csv", header "true", mode "FAILFAST");
SELECT * FROM diamonds;
```

### Schema angeben

Wenn das CSV-Schema bekannt ist, wird es über die `schema`-Option angegeben.

**Python**
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
  StructField("review_id", StringType(), True),
  StructField("rating", IntegerType(), True),
  StructField("comment", StringType(), True)])

df = spark.read.format("csv").schema(schema).option("header", "true").load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv")
df.printSchema()
```

**SQL**
```sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_csv',
  format => 'csv',
  header => true,
  schema => 'review_id string, rating int, comment string')
```

### Nur eine Teilmenge der Spalten lesen

CSV-Parser hängen davon ab, welche Spalten gelesen werden. Nicht passende Schemata können Werte in falsche Felder verschieben, da CSV keine Spaltennamen-Metadaten hat und Spark Schema-Felder **positionsbasiert** auf Spalten abbildet.

**Python**
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Read only a subset of columns by specifying a partial schema
schema = StructType([
  StructField("review_id", StringType(), True),
  StructField("rating", IntegerType(), True)])

df = spark.read.format("csv").schema(schema).option("header", "true").load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv")
display(df)
```

**SQL**
```sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_csv',
  format => 'csv',
  header => true,
  schema => 'review_id string, rating int')
```

---

## Fehlerhafte CSV-Datensätze behandeln

Beim Lesen mit angegebenem Schema können Daten nicht zum Schema passen. Die Parser-Modi:

- **PERMISSIVE** (Standard): Für nicht korrekt geparste Felder werden `NULL`-Werte eingefügt
- **DROPMALFORMED**: Zeilen mit nicht parsebaren Feldern werden verworfen
- **FAILFAST**: Lesen wird abgebrochen, sobald fehlerhafte Daten gefunden werden

Der Modus wird über die `mode`-Option gesetzt.

**Python**
```python
df = (spark.read
  .format("csv")
  .option("header", "true")
  .option("mode", "PERMISSIVE")
  .load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv"))
```

**SQL**
```sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_csv',
  format => 'csv',
  header => true,
  mode => 'PERMISSIVE')
```

Im `PERMISSIVE`-Modus lassen sich nicht parsebare Zeilen untersuchen durch:

1. Eine eigene `badRecordsPath`-Option, um korrupte Datensätze in eine Datei zu schreiben
2. Hinzufügen der Spalte `_corrupt_record` zum Schema, um korrupte Datensätze im DataFrame zu prüfen

> **Hinweis:** `badRecordsPath` hat Vorrang vor `_corrupt_record` – in den Pfad geschriebene fehlerhafte Zeilen erscheinen **nicht** im resultierenden DataFrame.

Fehlerhafte Zeilen über `_corrupt_record` untersuchen:

**Python**
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
  StructField("review_id", StringType(), True),
  StructField("rating", IntegerType(), True),
  StructField("comment", StringType(), True),
  StructField("_corrupt_record", StringType(), True)])

df = (spark.read
  .format("csv")
  .option("header", "true")
  .option("mode", "PERMISSIVE")
  .schema(schema)
  .load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv"))
display(df.filter(df["_corrupt_record"].isNotNull()))
```

**SQL**
```sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_csv',
  format => 'csv',
  header => true,
  mode => 'PERMISSIVE',
  schema => 'review_id string, rating int, comment string, _corrupt_record string')
WHERE _corrupt_record IS NOT NULL
```

---

## Rescued-Data-Spalte aktivieren

> **Hinweis:** Diese Funktion wird ab Databricks Runtime 8.3 unterstützt.

Im `PERMISSIVE`-Modus fängt die Rescued-Data-Spalte Daten auf, die nicht geparst wurden, weil ein oder mehrere Felder:

- im angegebenen Schema fehlen
- nicht zum Datentyp des angegebenen Schemas passen
- eine Groß-/Kleinschreibungs-Abweichung zu den Feldnamen im Schema haben

Die Rescued-Data-Spalte liefert ein JSON-Dokument mit den geretteten Spalten und dem Quelldateipfad zurück.

Die Option `rescuedDataColumn` beim Lesen auf einen Spaltennamen setzen:

**Python**
```python
df = spark.read.option("rescuedDataColumn", "_rescued_data").format("csv").load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv")
```

**SQL**
```sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_csv',
  format => 'csv',
  header => true,
  rescuedDataColumn => '_rescued_data')
```

Um den Quelldateipfad aus der Rescued-Data-Spalte zu entfernen:

**Python**
```python
spark.conf.set("spark.databricks.sql.rescuedDataColumn.filePath.enabled", "false")
```

In Verbindung mit `rescuedDataColumn` führen Datentyp-Abweichungen **nicht** dazu, dass Datensätze im `DROPMALFORMED`-Modus verworfen werden oder im `FAILFAST`-Modus Fehler auslösen. Nur korrupte Datensätze (unvollständiges oder fehlerhaftes CSV) werden verworfen bzw. lösen Fehler aus.

Im `PERMISSIVE`-Modus mit `rescuedDataColumn` gilt:

- Die erste Zeile (Header oder Daten) legt die erwartete Zeilenlänge fest
- Zeilen mit abweichender Spaltenanzahl gelten als unvollständig
- Datentyp-Abweichungen gelten nicht als korrupte Datensätze
- Nur unvollständige und fehlerhafte CSV-Datensätze werden in `_corrupt_record` bzw. `badRecordsPath` aufgezeichnet

---

## Verwandte Themen

- [Parquet lesen und schreiben](03%20Parquet%20lesen%20und%20schreiben.md) – für bessere Query-Performance oder effiziente Speicherung bietet das spaltenorientierte Parquet-Layout Vorteile gegenüber dem Textformat CSV.
- `read_files`-Referenz: `07 Data Management/.../05 Working with Files/_read_files.md`
