# JSON-Dateien lesen und schreiben

> Quelle: <https://docs.databricks.com/aws/en/query/formats/json>

JSON (JavaScript Object Notation) ist ein weit verbreitetes semi-strukturiertes Format für Datenaustausch und -speicherung. Databricks liest und schreibt JSON über Apache Spark und unterstützt sowohl **Single-Line**- als auch **Multi-Line**-Format mit automatischer Schema-Inferenz und Data-Rescue.

## Voraussetzungen

Für die Arbeit mit JSON-Dateien ist keine zusätzliche Konfiguration nötig.

## Optionen

JSON-Datenquellen werden über `.option()` und `.options()` von `DataFrameReader` und `DataFrameWriter` konfiguriert. Vollständige Optionslisten stehen in der API-Referenz.

---

## Verwendung

### JSON-Dateien schreiben und lesen

**Single-Line-Modus** (Standard) speichert ein vollständiges JSON-Objekt pro Zeile.

**Python:**
```python
# Write wanderbricks reviews to JSON format
df = spark.read.table("samples.wanderbricks.reviews")
df.write.format("json").save("/Volumes/<catalog>/<schema>/<volume>/reviews_json")

# Read the JSON files into a DataFrame
df = spark.read.format("json").load("/Volumes/<catalog>/<schema>/<volume>/reviews_json")
df.printSchema()
display(df)
```

### Multi-Line-JSON-Dateien lesen

Den Multi-Line-Modus aktivieren, wenn JSON-Objekte über mehrere Zeilen gehen.

**Python:**
```python
mdf = spark.read.option("multiline", "true").format("json").load("/Volumes/<catalog>/<schema>/<volume>/multi-line.json")
mdf.show(truncate=False)
```

**SQL:**
```sql
CREATE TEMPORARY VIEW multiLineJsonTable
USING json
OPTIONS (path="/Volumes/<catalog>/<schema>/<volume>/multi-line.json",
multiline=true)
```

### JSON-Dateien mit SQL lesen

Die tabellenwertige Funktion `read_files` ermöglicht SQL-basiertes JSON-Lesen:

```sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_json',
  format => 'json',
  multiLine => true)
```

Alternative Syntax mit `USING JSON`:

```sql
DROP TABLE IF EXISTS reviews_json_table;
CREATE TABLE reviews_json_table
USING JSON
OPTIONS (path "/Volumes/<catalog>/<schema>/<volume>/reviews_json", multiline true);
SELECT * FROM reviews_json_table;
```

### Zeichenkodierung angeben

Standardmäßig wird der Zeichensatz automatisch erkannt. Explizit über die `charset`-Option:

**Python:**
```python
spark.read.option("charset", "UTF-16BE").format("json").load("/Volumes/<catalog>/<schema>/<volume>/fileInUTF16.json")
```

**SQL:**
```sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/fileInUTF16.json',
  format => 'json',
  charset => 'UTF-16BE')
```

Unterstützte Zeichensätze: `UTF-8`, `UTF-16BE`, `UTF-16LE`, `UTF-16`, `UTF-32BE`, `UTF-32LE`, `UTF-32`.

### Rescued-Data-Spalte aktivieren

Die Rescued-Data-Spalte verhindert Datenverlust, indem sie nicht geparste Informationen auffängt – wegen fehlender Felder, Typ-Abweichungen oder Groß-/Kleinschreibungs-Abweichungen.

**Python:**
```python
df = spark.read.option("rescuedDataColumn", "_rescued_data").format("json").load("/Volumes/<catalog>/<schema>/<volume>/reviews_json")
```

**SQL:**
```sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_json',
  format => 'json',
  rescuedDataColumn => '_rescued_data')
```

Um Dateipfad-Informationen aus den Rescued Data zu entfernen:

```python
spark.conf.set("spark.databricks.sql.rescuedDataColumn.filePath.enabled", "false")
```

Der JSON-Parser unterstützt drei Modi: `PERMISSIVE`, `DROPMALFORMED` und `FAILFAST`. In Kombination mit `rescuedDataColumn` führen Typ-Abweichungen **nicht** zum Verwerfen von Datensätzen oder zu Fehlern – nur wirklich korruptes/fehlerhaftes JSON ist betroffen.

---

## Verwandte Themen

- **Parquet** bietet bessere Query-Performance für analytische, leselastige Workloads.
- **Avro** bietet kompakte Binärkodierung mit Schema-Evolution für Streaming-Systeme wie Apache Kafka.
- [JSON-Strings abfragen (semi-strukturiert)](../02%20Semi-strukturierte%20Daten/01%20JSON-Strings%20abfragen.md) – JSON, das als String-Spalte gespeichert ist, mit dem `:`-Operator abfragen.
