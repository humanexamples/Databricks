# Tutorial: COPY INTO mit Spark SQL (Notebook)

Databricks empfiehlt `COPY INTO` für inkrementelles und massenhaftes Laden von Datenquellen mit tausenden Dateien. Dieses Tutorial lädt JSON-Daten aus einem Unity-Catalog-Volume mit dem Wanderbricks-Beispieldatensatz in eine Delta-Tabelle.

## Voraussetzungen

- Zugriff auf eine Compute-Ressource
- Ein Unity-Catalog-fähiger Workspace mit Berechtigungen zum Erstellen von Schemas und Volumes in einem Katalog

## Schritt 1: Umgebung konfigurieren

Ein Notebook erstellen und an eine Compute-Ressource anhängen. Den folgenden Setup-Code ausführen, `<catalog>` durch einen zugänglichen Katalog ersetzen.

Python-Variante:

```python
# Set parameters and reset demo environment
catalog = "<catalog>"
username = spark.sql("SELECT regexp_replace(session_user(), '[^a-zA-Z0-9]', '_')").first()[0]
schema = f"copyinto_{username}_db"
volume = "copy_into_source"
source = f"/Volumes/{catalog}/{schema}/{volume}"
spark.sql(f"SET c.catalog={catalog}")
spark.sql(f"SET c.schema={schema}")
spark.sql(f"SET c.volume={volume}")
spark.sql(f"DROP SCHEMA IF EXISTS {catalog}.{schema} CASCADE")
spark.sql(f"CREATE SCHEMA {catalog}.{schema}")
spark.sql(f"CREATE VOLUME {catalog}.{schema}.{volume}")
```

SQL-Variante:

```sql
%sql
-- Reset demo environment
DROP SCHEMA IF EXISTS <catalog>.copy_into_tutorial CASCADE;
CREATE SCHEMA <catalog>.copy_into_tutorial;
CREATE VOLUME <catalog>.copy_into_tutorial.copy_into_source;
```

## Schritt 2: Beispieldaten als JSON in das Volume schreiben

Daten aus der Wanderbricks-Beispieltabelle `bookings` werden gelesen und als JSON-Dateien in das Volume geschrieben, um das Eintreffen externer Daten zu simulieren. Das Schreiben von Dateien in ein Volume erfordert Python – in einem produktiven Workflow würden diese Daten von externen Systemen stammen.

Python-Variante:

```python
# Write a batch of Wanderbricks bookings data as JSON to the volume
bookings = spark.read.table("samples.wanderbricks.bookings")
batch_1 = bookings.orderBy("booking_id").limit(20)
batch_1.write.mode("append").json(f"{source}/bookings")
```

SQL-Variante (auch im SQL-Notebook ist für diesen Schritt eine Python-Zelle mit `%python` nötig, da das Schreiben in ein Volume Python erfordert):

```python
%python
# Write a batch of Wanderbricks bookings data as JSON to the volume
bookings = spark.read.table("samples.wanderbricks.bookings")
batch_1 = bookings.orderBy("booking_id").limit(20)
batch_1.write.mode("append").json("/Volumes/<catalog>/copy_into_tutorial/copy_into_source/bookings")
```

## Schritt 3: Mit COPY INTO JSON-Daten idempotent laden

Vor der Nutzung von `COPY INTO` wird eine Ziel-Delta-Tabelle angelegt. Da die Operation idempotent ist, werden Daten auch bei mehrfacher Ausführung nur einmal geladen.

Python-Variante:

```python
# Create target table and load data
spark.sql(f"CREATE TABLE IF NOT EXISTS {catalog}.{schema}.bookings_target")
spark.sql(f"""
  COPY INTO {catalog}.{schema}.bookings_target
  FROM '/Volumes/{catalog}/{schema}/{volume}/bookings'
  FILEFORMAT = JSON
  FORMAT_OPTIONS ('mergeSchema' = 'true')
  COPY_OPTIONS ('mergeSchema' = 'true')
""")
```

SQL-Variante:

```sql
%sql
-- Create target table and load data
CREATE TABLE IF NOT EXISTS <catalog>.copy_into_tutorial.bookings_target;
COPY INTO <catalog>.copy_into_tutorial.bookings_target
FROM '/Volumes/<catalog>/copy_into_tutorial/copy_into_source/bookings'
FILEFORMAT = JSON
FORMAT_OPTIONS ('mergeSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true')
```

## Schritt 4: Tabelleninhalt prüfen

Prüfen, dass die Tabelle 20 Zeilen aus dem ersten Batch enthält und das Schema korrekt aus den JSON-Quelldateien inferiert wurde.

Python-Variante:

```python
# Review loaded data
display(spark.sql(f"SELECT * FROM {catalog}.{schema}.bookings_target"))
```

SQL-Variante:

```sql
%sql
-- Review loaded data
SELECT * FROM <catalog>.copy_into_tutorial.bookings_target
```

## Schritt 5: Weitere Daten laden und Ergebnis prüfen

Ein weiterer Batch wird geschrieben, um das Eintreffen zusätzlicher Daten zu simulieren, danach wird `COPY INTO` erneut ausgeführt. Nur neue Dateien werden geladen.

Python-Variante:

```python
# Write another batch of Wanderbricks bookings data as JSON
bookings = spark.read.table("samples.wanderbricks.bookings")
batch_2 = bookings.orderBy(bookings.booking_id.desc()).limit(20)
batch_2.write.mode("append").json(f"{source}/bookings")
```

SQL-Variante:

```python
%python
# Write another batch of Wanderbricks bookings data as JSON
bookings = spark.read.table("samples.wanderbricks.bookings")
batch_2 = bookings.orderBy(bookings.booking_id.desc()).limit(20)
batch_2.write.mode("append").json("/Volumes/<catalog>/copy_into_tutorial/copy_into_source/bookings")
```

Anschließend den `COPY INTO`-Befehl aus Schritt 3 erneut ausführen und die Tabelle danach erneut prüfen.

Python-Variante:

```python
# Confirm new data was loaded
display(spark.sql(f"SELECT COUNT(*) AS total_rows FROM {catalog}.{schema}.bookings_target"))
```

SQL-Variante:

```sql
%sql
-- Confirm new data was loaded
SELECT COUNT(*) AS total_rows FROM <catalog>.copy_into_tutorial.bookings_target
```

## Schritt 6: Tutorial aufräumen

Schema, Tabellen und Volume am Ende entfernen.

Python-Variante:

```python
# Drop schema and all associated objects
spark.sql(f"DROP SCHEMA IF EXISTS {catalog}.{schema} CASCADE")
```

SQL-Variante:

```sql
%sql
-- Drop schema and all associated objects
DROP SCHEMA IF EXISTS <catalog>.copy_into_tutorial CASCADE;
```

## Weiterführende Ressourcen

- SQL-Befehlsreferenz zu `COPY INTO`
- Dokumentation zum Wanderbricks-Beispieldatensatz

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/tutorial-notebook  
**Stand:** 2026-08-07
