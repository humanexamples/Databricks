# Mit External Tables arbeiten

External Tables speichern ihre Daten im Cloud-Objektspeicher. Unity Catalog verwaltet nur die Metadaten, mit vollständiger Data Governance.

## Überblick

Unity Catalog verwaltet bei External Tables nicht den Lebenszyklus der Daten, die Optimierung, den Speicherort oder das Layout. Wird eine External Table gelöscht, entfernt Databricks nur die Metadaten. Die zugrunde liegenden Dateien bleiben erhalten.

## Wann External Tables sinnvoll sind

Databricks empfiehlt External Tables für:

- die Registrierung vorhandener Daten, die nicht mit Managed Tables kompatibel sind, etwa im Format JSON oder Avro
- den direkten Zugriff von Nicht-Databricks-Clients ohne Durchsetzung von Unity-Catalog-Berechtigungen

Hinweis: Unity Catalog Managed Tables sind grundsätzlich vorzuziehen, da sie automatische Optimierung und bessere Performance bieten. Werden Metadaten über einen Nicht-Databricks-Client geändert, muss `MSCK REPAIR TABLE <table-name> SYNC METADATA` ausgeführt werden, um Unity Catalog zu synchronisieren.

## Unterstützte Dateiformate

- DELTA
- CSV
- JSON
- AVRO
- PARQUET
- ORC
- TEXT

## External Table erstellen

### Voraussetzungen

- `CREATE EXTERNAL TABLE`-Berechtigung auf der External Location
- `USE CATALOG`-Berechtigung auf dem übergeordneten Katalog
- `USE SCHEMA`-Berechtigung auf dem übergeordneten Schema
- `CREATE TABLE`-Berechtigung auf dem übergeordneten Schema

SQL: Erstellen mit definiertem Schema

```sql
%sql
CREATE TABLE <catalog>.<schema>.<table-name>(
  <column-name> <data-type>)
LOCATION 's3://<bucket-path>/<table-directory>';
```

SQL: Erstellen aus Abfrageergebnissen

```sql
%sql
CREATE TABLE <catalog>.<schema>.<table-name>
LOCATION 's3://<bucket-path>/<table-directory>'
AS SELECT * FROM <source-table>;
```

Python: Erstellen mit definiertem Schema

```python
from pyspark.sql.types import StructType, StructField, StringType
schema = StructType([StructField("<column-name>", <data-type>())])
spark.createDataFrame([], schema).write \
  .option("path", "s3://<bucket-path>/<table-directory>") \
  .saveAsTable("<catalog>.<schema>.<table-name>")
```

Python: Erstellen aus einem DataFrame

```python
df.write \
  .option("path", "s3://<bucket-path>/<table-directory>") \
  .saveAsTable("<catalog>.<schema>.<table-name>")
```

## External Table löschen

SQL

```sql
%sql
DROP TABLE IF EXISTS catalog_name.schema_name.table_name;
```

Python

```python
spark.sql("DROP TABLE IF EXISTS catalog_name.schema_name.table_name")
```

Python (ab Runtime 18.2)

```python
spark.catalog.dropTable("catalog_name.schema_name.table_name", ifExists=True)
```

**Wichtig:** Beim Löschen wird nur die Metadaten-Registrierung entfernt. Die zugrunde liegenden Datendateien müssen manuell gelöscht werden.

## Weitere Ressourcen

Databricks stellt ein Beispiel-Notebook zum Erstellen und Verwalten einer External Table in Unity Catalog bereit. Weiterführende Links behandeln External Locations, Managed Tables und Anleitungen zur Konvertierung.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/external  
**Stand:** 2026-08-06
