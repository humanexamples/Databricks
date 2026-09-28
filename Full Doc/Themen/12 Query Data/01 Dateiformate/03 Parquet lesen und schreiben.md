# Parquet-Dateien lesen und schreiben

> Quelle: <https://docs.databricks.com/aws/en/query/formats/parquet>

Apache Parquet ist ein **spaltenorientiertes** Dateiformat, das für analytische Workloads optimiert ist. Query-Engines können nur die benötigten Spalten lesen und irrelevante Row Groups überspringen.

Parquet ist das zugrunde liegende Speicherformat von **Delta Lake** und damit das häufigste Format für Daten in Databricks. Die Plattform unterstützt Parquet zum Lesen und Schreiben über Apache Spark – inklusive Schema-Angabe, Partitionierung und Write-Kompression.

## Voraussetzungen

Für die Nutzung von Parquet-Dateien ist keine zusätzliche Konfiguration nötig. Das **Streaming** von Parquet-Dateien erfordert [Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/).

## Optionen

Parquet-Datenquellen werden über die Methoden `.option()` und `.options()` von `DataFrameReader` und `DataFrameWriter` konfiguriert.

---

## Verwendung

### Parquet-Dateien mit SQL lesen

Mit `read_files` lassen sich Parquet-Dateien direkt aus dem Cloud-Speicher per SQL abfragen, ohne eine Tabelle zu erstellen.

```sql
SELECT * FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>/reviews_parquet',
  format => 'parquet')
```

### Parquet-Dateien lesen und schreiben

**Python**
```python
# Write wanderbricks reviews to Parquet format
df = spark.read.table("samples.wanderbricks.reviews")
df.write.format("parquet").save("/Volumes/<catalog>/<schema>/<volume>/reviews_parquet")

# Read a Parquet file into a DataFrame
df = spark.read.format("parquet").load("/Volumes/<catalog>/<schema>/<volume>/reviews_parquet")
display(df)

# Write with overwrite mode
df.write.format("parquet").mode("overwrite").save("/Volumes/<catalog>/<schema>/<volume>/reviews_parquet")
```

**SQL**
```sql
-- Write wanderbricks reviews to Parquet format
CREATE TABLE reviews_parquet
USING PARQUET
AS SELECT * FROM samples.wanderbricks.reviews;
SELECT * FROM reviews_parquet;
```

### Schema angeben

Ein Schema beim Lesen von Parquet-Dateien angeben, um den Overhead der Schema-Inferenz zu vermeiden.

**Python**
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
    StructField("review_id", StringType(), True),
    StructField("rating", IntegerType(), True),
    StructField("comment", StringType(), True)])

df = spark.read.format("parquet").schema(schema).load("/Volumes/<catalog>/<schema>/<volume>/reviews_parquet")
df.printSchema()
df.show()
```

**SQL**
```sql
-- Create a table with an explicit schema from Parquet files
CREATE TABLE reviews_parquet (
  review_id STRING,
  rating INT,
  comment STRING)
USING PARQUET
OPTIONS (path "/Volumes/<catalog>/<schema>/<volume>/reviews_parquet");
SELECT * FROM reviews_parquet;
```

### Partitionierte Parquet-Dateien schreiben

Partitionierte Parquet-Dateien schreiben, um die Query-Performance bei großen Datasets zu optimieren.

**Python**
```python
from pyspark.sql.functions import year, month

df = spark.read.table("samples.wanderbricks.bookings")
df_with_parts = df.withColumn("year", year("check_in")).withColumn("month", month("check_in"))
df_with_parts.write.format("parquet").partitionBy("year", "month").save("/Volumes/<catalog>/<schema>/<volume>/bookings_parquet_partitioned")
```

**SQL**
```sql
-- Write partitioned Parquet files by year and month
CREATE TABLE bookings_parquet_partitioned
USING PARQUET
PARTITIONED BY (year, month)
AS SELECT *, year(check_in) AS year, month(check_in) AS month
FROM samples.wanderbricks.bookings;
```

---

## Verwandte Themen

- Wenn ACID-Transaktionen, Schema-Enforcement oder Time Travel zusätzlich zur spaltenorientierten Performance von Parquet benötigt werden, ist **Delta Lake** das empfohlene Format für Daten in Databricks.
- [CSV lesen und schreiben](01%20CSV%20lesen%20und%20schreiben.md)
