# CSV-Dateien lesen und schreiben

CSV (comma-separated values) ist ein weit verbreitetes textbasiertes Tabellenformat für Datenaustausch, ETL und allgemeine Datenspeicherung. Databricks unterstützt CSV über Apache Spark, inklusive Schema-Inferenz, Kompressionshandling, Behandlung fehlerhafter Datensätze und Rescued-Data-Funktionalität.

## Empfehlung

Für SQL-Nutzer empfiehlt Databricks die Table-Valued-Function `read_files` (verfügbar ab Databricks Runtime 13.3 LTS). Direktes SQL-Lesen von CSV ohne temporäre Views oder `read_files` ist bei Datenquellen-Optionen und Schema-Angabe eingeschränkt.

Für CSV-Streaming ist Auto Loader erforderlich; ansonsten ist keine zusätzliche Konfiguration nötig.

## CSV-Dateien lesen und schreiben (Python)

```python
df = spark.read.table("samples.wanderbricks.reviews")
df.write.format("csv").option("header", "true").save("/Volumes/<catalog>/<schema>/<volume>/reviews_csv")
df = (spark.read
  .format("csv")
  .option("header", "true")
  .option("inferSchema", "true")
  .load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv"))
display(df)
df.printSchema()
```

## Lesen mit read_files (SQL)

```sql
%sql
SELECT * FROM read_files(
  's3://<bucket>/<path>/<file>.csv',
  format => 'csv',
  header => true,
  mode => 'FAILFAST')
```

## Schema explizit angeben

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
schema = StructType([
  StructField("review_id", StringType(), True),
  StructField("rating", IntegerType(), True),
  StructField("comment", StringType(), True)])
df = spark.read.format("csv").schema(schema).option("header", "true").load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv")
```

## Umgang mit fehlerhaften Datensätzen

Es gibt drei Parsing-Modi:

- **PERMISSIVE** (Standard): Setzt NULL-Werte für nicht parsbare Felder.
- **DROPMALFORMED**: Entfernt Zeilen mit Parsing-Fehlern.
- **FAILFAST**: Bricht die Verarbeitung bei einem Fehler ab.

```python
df = (spark.read
  .format("csv")
  .option("header", "true")
  .option("mode", "PERMISSIVE")
  .load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv"))
```

## Rescued-Data-Spalte

Die Rescued-Data-Spalte erfasst nicht zuordenbare Felder, Typkonflikte oder Groß-/Kleinschreibungsabweichungen als JSON-Dokument (ab Databricks Runtime 8.3 unterstützt):

```python
df = spark.read.option("rescuedDataColumn", "_rescued_data").format("csv").load("/Volumes/<catalog>/<schema>/<volume>/reviews_csv")
```

## Hinweis

Für bessere Abfrageperformance und Speichereffizienz bietet das spaltenorientierte Parquet-Format Vorteile gegenüber reinem Text wie CSV.

---
**Quelle:** https://docs.databricks.com/aws/en/query/formats/csv  
**Stand:** 2026-08-07
