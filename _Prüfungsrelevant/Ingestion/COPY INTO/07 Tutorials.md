[← Übersicht](00%20Uebersicht.md)

# Tutorials

## Tutorial 1: COPY INTO mit Spark SQL im Notebook

**Ziel:** JSON-Dateien aus einem Volume inkrementell in eine Delta-Tabelle laden. Die Daten kommen aus dem Beispiel-Datensatz Wanderbricks.

**Voraussetzungen:** ein Compute und ein Workspace mit Unity Catalog. In einem Katalog brauchst du `CREATE SCHEMA` und `CREATE VOLUME`.

### Schritt 1: Umgebung anlegen

```sql
DROP SCHEMA IF EXISTS <catalog>.copy_into_tutorial CASCADE;
CREATE SCHEMA <catalog>.copy_into_tutorial;
CREATE VOLUME <catalog>.copy_into_tutorial.copy_into_source;
```

### Schritt 2: Erste Beispieldaten als JSON ins Volume schreiben

Dateien in ein Volume schreiben geht nur mit Python. Im echten Betrieb liefert sie ein anderes System.

```python
bookings = spark.read.table("samples.wanderbricks.bookings")
batch_1 = bookings.orderBy("booking_id").limit(20)
batch_1.write.mode("append").json("/Volumes/<catalog>/copy_into_tutorial/copy_into_source/bookings")
```

### Schritt 3: Tabelle ohne Schema anlegen und laden

`CREATE TABLE` braucht hier nur den Namen. Das Schema entsteht beim Laden.

```sql
CREATE TABLE IF NOT EXISTS <catalog>.copy_into_tutorial.bookings_target;

COPY INTO <catalog>.copy_into_tutorial.bookings_target
FROM '/Volumes/<catalog>/copy_into_tutorial/copy_into_source/bookings'
FILEFORMAT = JSON
FORMAT_OPTIONS ('mergeSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');
```

Führst du den Befehl mehrmals aus, werden die Daten trotzdem nur einmal geladen.

### Schritt 4: Ergebnis prüfen

```sql
SELECT * FROM <catalog>.copy_into_tutorial.bookings_target;   -- 20 Zeilen
```

### Schritt 5: Weitere Daten liefern und erneut laden

```python
bookings = spark.read.table("samples.wanderbricks.bookings")
batch_2 = bookings.orderBy(bookings.booking_id.desc()).limit(20)
batch_2.write.mode("append").json("/Volumes/<catalog>/copy_into_tutorial/copy_into_source/bookings")
```

Jetzt führst du das `COPY INTO` aus Schritt 3 noch einmal aus. **Nur die neuen Dateien** werden geladen.

```sql
SELECT COUNT(*) AS total_rows FROM <catalog>.copy_into_tutorial.bookings_target;   -- 40
```

### Schritt 6: Aufräumen

```sql
DROP SCHEMA IF EXISTS <catalog>.copy_into_tutorial CASCADE;
```

**Dasselbe in Python:** Die SQL-Befehle stehen dann in `spark.sql(...)`, Katalog und Schema kommen aus Variablen.

```python
catalog = "<catalog>"
username = spark.sql("SELECT regexp_replace(session_user(), '[^a-zA-Z0-9]', '_')").first()[0]
schema = f"copyinto_{username}_db"
volume = "copy_into_source"

spark.sql(f"CREATE TABLE IF NOT EXISTS {catalog}.{schema}.bookings_target")
spark.sql(f"""
  COPY INTO {catalog}.{schema}.bookings_target
  FROM '/Volumes/{catalog}/{schema}/{volume}/bookings'
  FILEFORMAT = JSON
  FORMAT_OPTIONS ('mergeSchema' = 'true')
  COPY_OPTIONS ('mergeSchema' = 'true')
""")
```

---

## Tutorial 2: COPY INTO im SQL-Editor mit Instance Profile

**Ziel:** CSV-Dateien aus S3 über ein SQL Warehouse laden. Das Warehouse hat ein Instance Profile.

`COPY INTO` eignet sich für Quellen mit **Tausenden** Dateien. Für **Millionen** Dateien empfiehlt Databricks Auto Loader. Die Tutorial-Seite sagt noch, Auto Loader werde in Databricks SQL nicht unterstützt. Das ist veraltet: In Databricks SQL nutzt man Auto Loader heute über Streaming Tables mit `read_files`.

### Schritt 1: Zugriff prüfen

```sql
select * from csv.`s3://<bucket>/<folder>/`
```

### Schritt 2: Tabelle mit Schema anlegen

```sql
CREATE TABLE <catalog_name>.<schema_name>.<table_name> (
  tpep_pickup_datetime  TIMESTAMP,
  tpep_dropoff_datetime TIMESTAMP,
  trip_distance DOUBLE,
  fare_amount DOUBLE,
  pickup_zip INT,
  dropoff_zip INT
);
```

### Schritt 3: Laden

```sql
COPY INTO <catalog-name>.<schema-name>.<table-name>
FROM 's3://<s3-bucket>/<folder>/'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',        -- erste Zeile = Spaltennamen
  'inferSchema' = 'true'    -- Datentypen automatisch bestimmen
)
COPY_OPTIONS (
  'mergeSchema' = 'true'
);

SELECT * FROM <catalog_name>.<schema_name>.<table_name>;
```

Klickst du noch einmal auf **Run**, wird nichts Neues geladen. `COPY INTO` verarbeitet nur Daten, die es für neu hält.

### Aufräumen

```sql
DROP TABLE <catalog-name>.<schema-name>.<table-name>;
```

---

## Mini-Beispiel: COPY INTO in vier Sprachen

Der Befehl bleibt derselbe. Nur der Aufruf ändert sich.

**SQL**

```sql
COPY INTO main.bronze.bookings
FROM '/Volumes/main/raw/landing/booking_updates'
FILEFORMAT = JSON
FORMAT_OPTIONS ('multiLine' = 'true');
```

**Python**

```python
spark.sql("COPY INTO main.bronze.bookings "
          "FROM '/Volumes/main/raw/landing/booking_updates' "
          "FILEFORMAT = JSON FORMAT_OPTIONS ('multiLine' = 'true')")
```

**R**

```r
library(SparkR)
sparkR.session()
sql(paste("COPY INTO main.bronze.bookings",
          " FROM '/Volumes/main/raw/landing/booking_updates'",
          " FILEFORMAT = JSON FORMAT_OPTIONS ('multiLine' = 'true')", sep = ""))
```

**Scala**

```scala
spark.sql("COPY INTO main.bronze.bookings " +
  "FROM '/Volumes/main/raw/landing/booking_updates' " +
  "FILEFORMAT = JSON FORMAT_OPTIONS ('multiLine' = 'true')")
```
