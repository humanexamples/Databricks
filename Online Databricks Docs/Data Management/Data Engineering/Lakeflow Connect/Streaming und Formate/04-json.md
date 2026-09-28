# JSON-Dateien lesen und schreiben

JSON (JavaScript Object Notation) ist ein weit verbreitetes semi-strukturiertes Format für Datenaustausch und -speicherung. Databricks liest und schreibt JSON über Apache Spark, mit Unterstützung für Single-Line- und Multi-Line-Modus, automatischer Schema-Inferenz und Rescued-Data-Funktionalität. Es ist keine zusätzliche Konfiguration nötig.

## Schreiben und Lesen im Single-Line-Modus (Standard)

Im Standardmodus enthält jede Zeile der Ausgabedatei genau ein vollständiges JSON-Objekt.

```python
df = spark.read.table("samples.wanderbricks.reviews")
df.write.format("json").save("/Volumes/<catalog>/<schema>/<volume>/reviews_json")
df = spark.read.format("json").load("/Volumes/<catalog>/<schema>/<volume>/reviews_json")
df.printSchema()
display(df)
```

## Multi-Line-JSON lesen

Aktivieren Sie den Multi-Line-Modus, wenn sich JSON-Objekte über mehrere Zeilen erstrecken:

```python
mdf = spark.read.option("multiline", "true").format("json").load("/Volumes/<catalog>/<schema>/<volume>/multi-line.json")
mdf.show(truncate=False)
```

```sql
%sql
CREATE TEMPORARY VIEW multiLineJsonTable
USING json
OPTIONS (path="/Volumes/<catalog>/<schema>/<volume>/multi-line.json", multiline=true)
```

## Lesen mit read_files (SQL)

```sql
%sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_json',
  format => 'json',
  multiLine => true)
```

Alternative über `USING JSON`:

```sql
%sql
DROP TABLE IF EXISTS reviews_json_table;
CREATE TABLE reviews_json_table
USING JSON
OPTIONS (path "/Volumes/<catalog>/<schema>/<volume>/reviews_json", multiline true);
SELECT * FROM reviews_json_table;
```

## Zeichenkodierung angeben

Unterstützte Zeichensätze sind u. a. UTF-8, UTF-16BE, UTF-16LE, UTF-16, UTF-32BE, UTF-32LE und UTF-32:

```python
spark.read.option("charset", "UTF-16BE").format("json").load("/Volumes/<catalog>/<schema>/<volume>/fileInUTF16.json")
```

```sql
%sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/fileInUTF16.json',
  format => 'json',
  charset => 'UTF-16BE')
```

## Rescued-Data-Spalte

Die Rescued-Data-Spalte sorgt dafür, dass beim ETL nie Daten verloren gehen. Sie erfasst nicht geparste Daten aufgrund fehlenden Schemas, Typkonflikten oder Groß-/Kleinschreibungsabweichungen als JSON mit den betroffenen Spalten und dem Quelldateipfad. Aktivierung über die Option `rescuedDataColumn`:

```python
df = spark.read.option("rescuedDataColumn", "_rescued_data").format("json").load("/Volumes/<catalog>/<schema>/<volume>/reviews_json")
```

Den Dateipfad aus den Rescued Data entfernen:

```python
spark.conf.set("spark.databricks.sql.rescuedDataColumn.filePath.enabled", "false")
```

## Hinweis

Parquet bietet bessere Performance für analytische, leselastige Workloads; Avro bietet kompakte Binärkodierung mit Schema Evolution für Event-Streaming-Systeme.

---
**Quelle:** https://docs.databricks.com/aws/en/query/formats/json  
**Stand:** 2026-08-07
