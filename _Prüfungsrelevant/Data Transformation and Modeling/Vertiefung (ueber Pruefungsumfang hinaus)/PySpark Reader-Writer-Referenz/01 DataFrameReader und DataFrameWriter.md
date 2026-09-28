# PySpark: DataFrameReader und DataFrameWriter

## 1. PySpark-Grundlagen

- PySpark = Python-Schnittstelle zu Apache Spark. In Databricks-Notebooks steht `SparkSession` als `spark` bereits vorkonfiguriert bereit.
- **DataFrame** = in benannten Spalten organisiertes Dataset: **Schema** (Spaltennamen/-typen), **Rows** (Datensätze), **Columns** (einfache Typen wie String/Integer oder komplexe wie Array/Map).
- **Lazy Evaluation:** *Transformations* (`.select()`, `.filter()`, …) beschreiben nur Logik; erst eine *Action* (`.show()`, `.collect()`, `.count()`) löst die Berechnung aus.
- **Immutability:** jede Transformation liefert ein **neues** DataFrame.

| API/Bibliothek | Zweck |
|---|---|
| Spark SQL und DataFrames | Verarbeitung strukturierter Daten. |
| Structured Streaming | Kontinuierliche Datenverarbeitung. |
| Pandas API on Spark | Verteilte Pandas-Workloads. |
| MLlib | Machine Learning. |
| GraphX | Graph-Berechnungen. |

### DataFrames erzeugen

```python
# Mit angegebenen Werten
df_children = spark.createDataFrame(
  data = [("Mikhail", 15), ("Zaky", 13), ("Zoya", 8)],
  schema = ['name', 'age'])

# Mit explizitem Schema
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
df_children_with_schema = spark.createDataFrame(
  data = [("Mikhail", 15), ("Zaky", 13), ("Zoya", 8)],
  schema = StructType([
    StructField('name', StringType(), True),
    StructField('age', IntegerType(), True)
  ]))

# Aus einer Unity-Catalog-Tabelle
df_customer = spark.table('samples.tpch.customer')

# Aus einer Datei (z. B. CSV in einem Volume)
df_csv = (spark.read
  .format("csv")
  .option("header", True)
  .option("inferSchema", True)
  .load(volume_file_path))

# Aus einer JSON-API-Antwort
import requests
response = requests.get("https://api.fda.gov/drug/drugsfda.json?limit=100")
df_drugs = spark.createDataFrame(response.json()["results"])
# Verschachteltes Feld auswählen: df_drugs.select(df_drugs["products"][0]["brand_name"])
```

### Spalten und Zeilen — gängige Operationen

```python
from pyspark.sql.functions import col, expr, avg, count

# Spalten auswählen — gleichwertige Schreibweisen
df_customer.select(col("c_custkey"), col("c_acctbal"))
df_customer.select(expr("c_custkey"), expr("c_acctbal"))
df_customer.selectExpr("c_custkey as key", "round(c_acctbal) as account_rounded")
df_customer.select("c_custkey", "c_acctbal")
df_customer.select(df_customer["c_custkey"], df_customer["c_acctbal"])
df_customer.select(df_customer.c_custkey, df_customer.c_acctbal)

# Spalten erzeugen/umbenennen/casten/entfernen
df_customer_flag = df_customer.withColumn("balance_flag", col("c_acctbal") > 1000)
df_renamed = df_customer_flag.withColumnRenamed("balance_flag", "balance_flag_renamed")
df_casted = df_customer.withColumn("c_custkey", col("c_custkey").cast(StringType()))
df_customer_flag_renamed.drop("c_phone", "balance_flag_renamed")

# Zeilen filtern — kombinierbar mit & (UND) und | (ODER)
df_customer.filter(col("c_custkey") == 412449)
df_customer.filter((col("c_nationkey") == 20) & (col("c_acctbal") > 1000))
df_customer.filter((col("c_custkey") == 412446) | (col("c_custkey") == 412447))

# Duplikate, Nullwerte, Union, Sortierung
df_customer.distinct()
df_customer.na.drop()                                    # äquivalent zu na.drop("any")
df_customer.na.drop("all", subset=["c_acctbal", "c_custkey"])
df_customer.na.fill("0", subset=["c_acctbal"])
df_customer.na.replace([""], ["UNKNOWN"], subset=["c_phone"])
df_that_one_customer.union(df_filtered_customer)
df_customer.orderBy(col("c_acctbal").desc(), col("c_custkey").asc())
df_sorted.limit(10)
```

- Gotcha: Sortieren ist bei großen Datenmengen teuer, und die Reihenfolge sortierter Daten ist nach Speichern + erneutem Einlesen **nicht garantiert**.

```python
# Join
df_joined = df_order.join(
  df_customer,
  on = df_order["o_custkey"] == df_customer["c_custkey"],
  how = "inner")   # "inner", "left", "outer" u.a.

# Aggregation (analog GROUP BY)
df_segment_balance = df_customer.groupBy("c_mktsegment").agg(avg(df_customer["c_acctbal"]))
df_customer.count()

# Method Chaining (dank Lazy Evaluation)
df_chained = (
    df_order.filter(col("o_orderstatus") == "F")
    .groupBy(col("o_orderpriority"))
    .agg(count(col("o_orderkey")).alias("n_orders"))
    .sort(col("n_orders").desc()))

# Visualisierung im Notebook
display(df_order)
```

### Benutzerdefinierte Datenquellen (Python DataSource API)

- Ab **DBR 15.4 LTS** (Serverless ab Version 2): Connectors zu Systemen ohne native Spark-Unterstützung (REST-APIs, Google Sheets, proprietäre Dienste) **in reinem Python**, ohne JVM-Connector-Entwicklung.
- Gotcha: alle Klassen/Methoden müssen **serialisierbar** sein (nur Dictionaries/primitive Typen).

| Baustein | Beschreibung |
|---|---|
| `DataSource` (Basisklasse) | Muss `name` (Bezeichner) und `schema` bereitstellen. |
| `reader()` / `writer()` | Liefern Reader-/Writer-Objekte für Batch-Operationen. |
| `streamReader()` / `simpleStreamReader()` | Für Streaming-Lesevorgänge. |
| `streamWriter()` | Für Streaming-Schreibvorgänge. |
| `spark.dataSource.register(...)` | Registriert die Datenquelle vor Nutzung über `spark.read.format("name")`. |

```python
from pyspark.sql.datasource import DataSource, DataSourceReader
from pyspark.sql.types import StructType

class FakeDataSourceReader(DataSourceReader):
    def __init__(self, schema, options):
        self.schema: StructType = schema
        self.options = options
    def read(self, partition):
        from faker import Faker
        fake = Faker()
        num_rows = int(self.options.get("numRows", 3))
        for _ in range(num_rows):
            row = []
            for field in self.schema.fields:
                value = getattr(fake, field.name)()
                row.append(value)
            yield tuple(row)          # read() ist ein Generator, pro Partition

class FakeDataSource(DataSource):
    @classmethod
    def name(cls):
        return "fake"                 # legt den .format(...)-String fest
    def schema(self):
        return "name string, date string, zipcode string, state string"   # Schema als DDL-String
    def reader(self, schema: StructType):
        return FakeDataSourceReader(schema, self.options)   # self.options: per .option(...) gereichte Optionen

spark.dataSource.register(FakeDataSource)
spark.read.format("fake").load().show()
# Ergebnis: 3 Zeilen Fake-Daten (name, date, zipcode, state) via faker generiert
```

- Weitere dokumentierte Beispielmuster: Batch-Writer (persistiert Partitionen als Dateien), GitHub-Integration (`variant`-Typ), Streaming-Reader/-Writer (`streamReader`/`streamWriter`), BigQuery-Connector (inkrementelles Checkpointing, Parallelisierung), API-Authentifizierung (Credential-Verwaltung über Unity-Catalog-HTTP-Connections).

---

## 2. `DataFrameReader` (`spark.read`)

Lädt ein DataFrame aus externen Speichersystemen (Dateisysteme, Key-Value-Stores usw.).

| Methode | Beschreibung |
|---|---|
| `format(source)` | Legt das Format der Eingabedatenquelle fest. |
| `schema(schema)` | Legt das Eingabeschema fest. |
| `option(key, value)` | Fügt eine einzelne Option hinzu. |
| `options(**options)` | Fügt mehrere Optionen hinzu. |
| `load(path, format, schema, **options)` | Lädt Daten und gibt sie als DataFrame zurück. |
| `csv(path, schema, sep, encoding, ...)` | Lädt CSV-Datei(en). |
| `json(path, schema, ...)` | Lädt JSON-Datei(en). |
| `text(paths, wholetext, lineSep, ...)` | Lädt Textdateien in eine String-Spalte `"value"`. |
| `table(tableName)` | Gibt eine Tabelle als DataFrame zurück. |
| `parquet(*paths, **options)` | Lädt Parquet-Dateien. |
| `xml(path, rowTag, schema, ...)` | Lädt eine XML-Datei. |
| `excel(path, dataAddress, headerRows, ...)` | Lädt Excel-Dateien. |
| `orc(path, mergeSchema, pathGlobFilter, ...)` | Lädt ORC-Dateien. |
| `jdbc(url, table, column, lowerBound, upperBound, numPartitions, predicates, properties)` | Liest eine Datenbanktabelle via JDBC. |

Alle Methoden geben `DataFrameReader` zurück (verkettbar), außer `load()`/`csv()`/`json()`/`text()`/`table()`/`parquet()`/etc., die ein `DataFrame` liefern.

```python
# format()
spark.read.format('json').load(d).show()

# schema() — vermeidet automatische Schema-Inferenz
spark.read.schema("col0 INT, col1 DOUBLE").format("csv").load(d).printSchema()
# root
#  |-- col0: integer (nullable = true)
#  |-- col1: double (nullable = true)
```

### `option(key, value)` / `options(**options)`

**Formatübergreifende ("Common") Optionen** für die meisten Batch-Lesevorgänge (`spark.read`, `read_files`, `COPY INTO`):

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `ignoreCorruptFiles` | `false` | boolean | Ignoriert defekte Dateien — Job läuft trotz beschädigter Dateien weiter (ab DBR 11.3 LTS). |
| `ignoredPathSegmentRegex` | `^[._]` | Regex | Steuert, welche Dateien/Verzeichnisse beim File Listing als versteckt übersprungen werden (ab DBR 19). |
| `ignoreMissingFiles` | `false` (Auto Loader); `true` (COPY INTO, Legacy) | boolean | Ignoriert fehlende Dateien — Job läuft weiter (ab DBR 11.3 LTS). |
| `modifiedAfter` / `modifiedBefore` | `None` | Timestamp | Filtert Dateien nach Änderungszeitpunkt (nach/vor). |
| `pathGlobFilter` / `fileNamePattern` | `None` | Glob-Muster | Glob-Muster zur Dateiauswahl. |
| `recursiveFileLookup` | `false` | boolean | Durchsucht verschachtelte Verzeichnisse auch ohne Partitionsnamensschema. |

- Zusätzlich akzeptieren `option()`/`options()` **formatspezifische** Schlüssel (z. B. `header`/`inferSchema`/`sep` für CSV, `multiLine` für JSON, `mergeSchema` für Parquet).

```python
spark.read.schema(df.schema).option("nullValue", "Alice").format('csv').load(d).show()
spark.read.options(nullValue="Alice", header=True).format('csv').load(d).show()
```

### `load(path=None, format=None, schema=None, **options)`

Allgemeinste Lademethode.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `path` | `str`/`list`, optional | Ein oder mehrere Pfade in einer dateisystembasierten Quelle. |
| `format` | `str`, optional | Format der Quelle; Standard `'parquet'`. |
| `schema` | `StructType`/`str`, optional | Eingabeschema. |
| `**options` | `dict` | Zusätzliche Optionen. |

```python
df = spark.read.load(d, schema=df.schema, format="csv", nullValue="Alice", header=True)
```

### Format-Shortcuts

```python
# csv(path, schema=None, **options)
spark.read.csv(d, schema=df.schema, nullValue="Alice").show()

# json(path, schema=None, **options)
spark.read.json(d).show()
spark.read.json([d1, d2]).show()             # mehrere Verzeichnisse
spark.read.json(d, schema="name STRING, age INT").show()   # mit explizitem Schema

# text(paths, wholetext=False, lineSep=None, **options)
# Ergebnis: DataFrame mit genau einer String-Spalte "value" (1 Zeile Datei = 1 Zeile DataFrame)
spark.read.schema(df.schema).text(d).sort("alphabets").show()
```

| `text()`-Parameter | Typ | Beschreibung |
|---|---|---|
| `paths` | `str`/`list` | Ein oder mehrere Eingabepfade. |
| `wholetext` | `bool`, optional | `True` liest jede Datei als eine einzige Zeile. Standard `False`. |
| `lineSep` | `str`, optional | Zeilentrennzeichen; Standard `'\n'`, `'\r'` oder `'\r\n'`. |

---

## 3. `DataFrameWriter` (`df.write`)

Schreibt ein DataFrame in externe Speichersysteme. Streaming-Pendant: `df.writeStream` (`DataStreamWriter`, siehe eigenes Kapitel).

| Methode | Beschreibung |
|---|---|
| `mode(saveMode)` | Verhalten, wenn Daten/Tabelle bereits existieren. |
| `format(source)` | Legt das Ausgabeformat fest. |
| `option(key, value)` / `options(**options)` | Fügt Ausgabeoption(en) hinzu. |
| `partitionBy(*cols)` | Partitioniert die Ausgabe im Dateisystem nach Spalten. |
| `bucketBy(numBuckets, col, *cols)` | Bucketet die Ausgabe nach Spalten. |
| `sortBy(col, *cols)` | Sortiert die Ausgabe innerhalb jedes Buckets. |
| `clusterBy(*cols)` | Clustert Daten nach Spalten (Liquid Clustering). |
| `save(path, format, mode, partitionBy, **options)` | Speichert den DataFrame-Inhalt in einer Datenquelle. |
| `insertInto(tableName, overwrite)` | Fügt Inhalt in eine bestehende Tabelle ein (positionsbasiert). |
| `saveAsTable(name, format, mode, partitionBy, **options)` | Speichert als benannte Tabelle (namensbasiert). |
| `json(path, mode, compression, ...)` | Speichert im JSON-Format. |
| `parquet(path, mode, partitionBy, compression)` | Speichert im Parquet-Format. |
| `text(path, compression, lineSep)` | Speichert als Textdatei. |
| `csv(path, mode, compression, sep, ...)` | Speichert im CSV-Format. |
| `xml(path, rowTag, mode, ...)` | Speichert im XML-Format. |
| `orc(path, mode, partitionBy, compression)` | Speichert im ORC-Format. |
| `excel(path, mode, dataAddress, headerRows)` | Speichert im Excel-Format. |
| `jdbc(url, table, mode, properties)` | Speichert in einer externen Datenbanktabelle via JDBC. |

### `mode(saveMode)`

| Wert | Verhalten |
|---|---|
| `'append'` | Neue Daten werden an bestehende angehängt. |
| `'overwrite'` | Bestehende Daten werden durch neue ersetzt. |
| `'error'` / `'errorifexists'` (**Standard**) | Exception, falls Zieldaten bereits existieren. |
| `'ignore'` | Schreibvorgang wird stillschweigend übersprungen, falls Zieldaten bereits existieren (kein Fehler, kein Schreiben). |

```python
spark.createDataFrame([{"age": 100, "name": "Alice"}]).write.mode("overwrite").format("parquet").save(d)
spark.createDataFrame([{"age": 120, "name": "Sue"}]).write.mode("append").format("parquet").save(d)
# Ergebnis: erster Write ersetzt d vollständig, zweiter hängt an -> d enthält Alice(100) + Sue(120)
```

### `option(key, value)` / `options(**options)`

- Gotcha: Anders als beim Lesen gibt es für `DataFrameWriter` **keinen** formatübergreifenden "Common"-Optionsabschnitt — jedes Zielformat hat eine eigene Optionstabelle.

**Delta Lake / Apache Iceberg (Standardformat auf Databricks):**

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `mergeSchema` | `None` | `true`/`false` | Schema Evolution — neue Quellspalten werden dem Zielschema hinzugefügt (Batch- und Streaming-Appends). |
| `overwriteSchema` | `None` | `true`/`false` | Ersetzt Schema und Partitionierung beim Überschreiben. Erfordert `mode("overwrite")` ohne `replaceWhere`, nicht kombinierbar mit `partitionOverwriteMode`. |
| `replaceWhere` | `None` | Prädikat-Ausdruck | Überschreibt atomar nur Datensätze, die dem Prädikat entsprechen. |
| `replaceOn` | `None` | Boolean-Ausdruck | Matcht Zielzeilen zum Ersetzen durch Quellzeilen (Python/Scala ab DBR 18.2; SQL bereits ab DBR 17.1). |
| `replaceUsing` | `None` | Spaltenliste (kommagetrennt) | Spalten zum Matchen von Ziel-/Quellzeilen beim Ersatz (Python/Scala ab DBR 18.2; SQL bereits ab DBR 16.3). |
| `targetAlias` | `None` | String | Alias für die Zieltabelle zur Disambiguierung bei `replaceOn`/`replaceWhere`. |
| `partitionOverwriteMode` | `None` | `static`/`dynamic` | `dynamic` überschreibt nur Partitionen mit neuen Daten (Legacy, nicht auf Serverless/DBSQL). |
| `clusterByAuto` | `false` | `true`/`false` | Automatic Liquid Clustering (Databricks wählt Keys); nur mit `mode("overwrite")`, ab DBR 16.4. |
| `optimizeWrite` | `None` | `true`/`false` | Auto Optimize Write für diesen Schreibvorgang (überschreibt Spark-Konfiguration). |
| `userMetadata` | `None` | String | Benutzerdefinierter String im Commit, sichtbar in `DESCRIBE HISTORY`. |
| `txnAppId` | `None` | String | Eindeutige Anwendungs-ID für idempotente `foreachBatch`-Writes (mit `txnVersion`, Exactly-once über mehrere Delta-Tabellen). |
| `txnVersion` | `None` | monoton steigende Ganzzahl | Transaktionsversion für idempotente `foreachBatch`-Writes. |

**Gemeinsame Schlüssel, die in mehreren anderen Formaten wiederkehren** (Avro, CSV, Excel, JSON, ORC, Parquet, Text, XML — jeweils mit eigener vollständiger Optionstabelle):

| Option | Beispielwerte (formatabhängig) | Beschreibung |
|---|---|---|
| `compression` | CSV/JSON/Text/XML: `none`,`bzip2`,`gzip`,`lz4`,`snappy`,`deflate`,`zstd`; Parquet zusätzlich `lzo`,`brotli`,`lz4_raw`; ORC: `uncompressed`,`zlib`,`lzo`,`zstd`,`lz4`,`brotli`; Avro: `uncompressed`,`deflate`,`snappy`,`bzip2`,`xz`,`zstandard` | Komprimierungscodec beim Schreiben. |
| `dateFormat` | z. B. `yyyy-MM-dd` | Formatstring für Datumsspalten (CSV, JSON, XML). |
| `timestampFormat` | z. B. `yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]` | Formatstring für Timestamp-Spalten (CSV, JSON, XML). |
| `encoding` | `UTF-8` | Zeichenkodierung der Ausgabedateien (CSV, JSON, Text, XML). |
| `lineSep` | `\n` | Zeilentrenner zwischen Datensätzen (CSV, JSON, Text). |

```python
df.write.option("nullValue", "Alice").mode("overwrite").format("csv").save(d)
df.write.options(nullValue="Alice", header=True).mode("overwrite").format("csv").save(d)
```

### `save(path=None, format=None, mode=None, partitionBy=None, **options)`

Allgemeinste Schreibmethode. Rückgabe: `None`.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `path` | `str`, optional | Pfad in einem Hadoop-kompatiblen Dateisystem. |
| `format` | `str`, optional | Zielformat. |
| `mode` | `str`, optional | `'append'`, `'overwrite'`, `'ignore'`, `'error'`/`'errorifexists'` (Standard). |
| `partitionBy` | `list`, optional | Partitionierungsspalten. |
| `**options` | `dict` | Zusätzliche Optionen. |

### Format-Shortcuts

```python
# csv(path, mode=None, compression=None, sep=None, quote=None, escape=None, header=None,
#     nullValue=None, escapeQuotes=None, quoteAll=None, dateFormat=None, timestampFormat=None,
#     ignoreLeadingWhiteSpace=None, ignoreTrailingWhiteSpace=None, charToEscapeQuoteEscaping=None,
#     encoding=None, emptyValue=None, lineSep=None)
# alle Parameter außer path/mode = gleichnamige Optionen, alternativ per .option()/.options()
df.write.csv(d, mode="overwrite")

# json(path, mode=None, compression=None, dateFormat=None, timestampFormat=None, lineSep=None,
#      encoding=None, ignoreNullFields=None)   -> JSON Lines
df.write.json(d, mode="overwrite")

# text(path, compression=None, lineSep=None)
# Gotcha: DataFrame darf nur EINE Spalte vom Typ String besitzen
df.write.mode("overwrite").text(d)
```

### `saveAsTable(name, format=None, mode=None, partitionBy=None, **options)` vs. `insertInto(tableName, overwrite=None)`

| | `saveAsTable` | `insertInto` |
|---|---|---|
| Ziel | Neue/bestehende Tabelle | Nur **bereits existierende** Tabelle |
| Spaltenauflösung | **namensbasiert** | **positionsbasiert** (ignoriert Spaltennamen!) |

```python
df.write.saveAsTable("tblA")

df = spark.createDataFrame([(100, "Alice"), (120, "Alice"), (140, "Bob")], schema=["age", "name"])
df.write.saveAsTable("tblA")
df.selectExpr("age AS col1", "name AS col2").write.insertInto("tblA")
# Ergebnis: col1/col2 landen trotz abweichender Namen positionsbasiert in age/name — tblA verdoppelt sich
```

| `insertInto`-Parameter | Typ | Beschreibung |
|---|---|---|
| `tableName` | `str` | Zieltabelle. |
| `overwrite` | `bool`, optional | `True` überschreibt bestehende Daten; standardmäßig deaktiviert. |

### `partitionBy(*cols)` / `sortBy(col, *cols)` / `clusterBy(*cols)`

```python
# partitionBy — Hive-Partitionierungsschema (spalte=wert-Unterverzeichnisse)
df.write.partitionBy("name").mode("overwrite").format("parquet").save(d)
spark.read.parquet(f"{d}/name=Alice").show()    # Ergebnis: gezielt nur diese Partition lesen

# sortBy — nur zusammen mit bucketBy() und saveAsTable()
df.write.bucketBy(1, "name").sortBy("age").mode("overwrite").saveAsTable("sorted_bucketed_table")

# clusterBy — Liquid Clustering, optimiert spätere Query-Performance
df.write.clusterBy("name").mode("overwrite").format("parquet").save(d)
```

**Stand:** 2026-09-14.
