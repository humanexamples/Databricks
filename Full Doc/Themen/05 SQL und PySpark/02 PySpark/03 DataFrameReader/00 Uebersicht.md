# `DataFrameReader` — Klassenreferenz

Referenz für `pyspark.sql.DataFrameReader`, erreichbar über `spark.read`.

## Beschreibung

*"Interface used to load a DataFrame from external storage systems (e.g. file systems, key-value stores, etc)."*

Auf Deutsch: Schnittstelle zum Laden eines DataFrames aus externen Speichersystemen (Dateisysteme, Key-Value-Stores usw.), erreichbar über `spark.read`.

## Methodenübersicht

| Methode | Beschreibung | Details |
| --- | --- | --- |
| `format(source)` | Legt das Format der Eingabedatenquelle fest. | [01 format.md](01%20format.md) |
| `schema(schema)` | Legt das Eingabeschema fest. | [02 schema.md](02%20schema.md) |
| `option(key, value)` | Fügt eine einzelne Option für die zugrunde liegende Datenquelle hinzu. | [03 option.md](03%20option.md) |
| `options(**options)` | Fügt mehrere Optionen für die zugrunde liegende Datenquelle hinzu. | [04 options.md](04%20options.md) |
| `load(path, format, schema, **options)` | Lädt Daten aus einer Datenquelle und gibt sie als DataFrame zurück. | [05 load.md](05%20load.md) |
| `csv(path, schema, sep, encoding, ...)` | Lädt eine CSV-Datei und gibt das Ergebnis als DataFrame zurück. | [06 csv.md](06%20csv.md) |
| `json(path, schema, ...)` | Lädt JSON-Dateien und gibt das Ergebnis als DataFrame zurück. | [07 json.md](07%20json.md) |
| `text(paths, wholetext, lineSep, ...)` | Lädt Textdateien und gibt ein DataFrame mit einer String-Spalte `"value"` zurück. | [08 text.md](08%20text.md) |
| `table(tableName)` | Gibt die angegebene Tabelle als DataFrame zurück. | — |
| `parquet(*paths, **options)` | Lädt Parquet-Dateien. | — |
| `xml(path, rowTag, schema, ...)` | Lädt eine XML-Datei. | — |
| `excel(path, dataAddress, headerRows, ...)` | Lädt Excel-Dateien. | — |
| `orc(path, mergeSchema, pathGlobFilter, ...)` | Lädt ORC-Dateien. | — |
| `jdbc(url, table, column, lowerBound, upperBound, numPartitions, predicates, properties)` | Liest eine Datenbanktabelle über eine JDBC-URL und Verbindungseigenschaften. | — |

## Typische Verwendungsmuster

**Direkte Formatmethoden:**

```python
df = spark.read.json("path/to/file.json")
df = spark.read.option("header", "true").csv("path/to/file.csv")
df = spark.read.parquet("path/to/file.parquet")
df = spark.read.table("table_name")
```

**Über `format` + `load`:**

```python
df = spark.read.format("json").load("path/to/file.json")
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("path/to/file.csv")
```

**Mit explizitem Schema:**

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
schema = StructType([
    StructField("name", StringType(), True),
    StructField("age", IntegerType(), True)])
df = spark.read.schema(schema).csv("path/to/file.csv")
df = spark.read.schema("name STRING, age INT").csv("path/to/file.csv")
```

**Über JDBC:**

```python
df = spark.read.jdbc(
    url="jdbc:postgresql://localhost:5432/mydb",
    table="users",
    properties={"user": "myuser", "password": "mypassword"})
df = spark.read.jdbc(
    url="jdbc:postgresql://localhost:5432/mydb",
    table="users",
    column="id",
    lowerBound=1,
    upperBound=1000,
    numPartitions=10,
    properties={"user": "myuser", "password": "mypassword"})
```

**Method Chaining:**

```python
df = spark.read \
    .format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .option("delimiter", ",") \
    .schema("name STRING, age INT") \
    .load("path/to/file.csv")
```

## Quellen

- DataFrameReader (Klassenreferenz): https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
