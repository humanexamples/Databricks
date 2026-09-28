# Tutorial: COPY INTO mit einem Instance Profile (Databricks SQL)

Dieses Tutorial zeigt, wie mit `COPY INTO` Daten aus einem Amazon-S3-Bucket in eine Databricks-SQL-Tabelle geladen werden, wenn ein SQL-Warehouse über ein AWS Instance Profile für den S3-Zugriff konfiguriert ist.

## Voraussetzungen

- Konfigurierter S3-Datenzugriff (durch einen Administrator, siehe Anleitung zur Konfiguration des Datenzugriffs)
- Ein SQL-Warehouse, das mit dem Instance Profile konfiguriert ist
- "Can manage"-Berechtigung auf dem SQL-Warehouse
- Die vollständige S3-URI der Quelldaten
- Grundkenntnisse der Databricks-SQL-Oberfläche

## Schritt 1: Zugriff auf den Cloud-Speicher prüfen

In der Seitenleiste **Create > Query** wählen, ein SQL-Warehouse auswählen und folgende Abfrage ausführen (`<path>` durch die eigene S3-URI ersetzen, z. B. `s3://<bucket>/<folder>/`), dann auf **Run** klicken, um den Zugriff zu prüfen:

```sql
%sql
select * from csv.<path>
```

## Schritt 2: Tabelle erstellen

Eine Zieltabelle für die eingehenden Daten anlegen:

```sql
%sql
CREATE TABLE <catalog_name>.<schema_name>.<table_name> (
  tpep_pickup_datetime  TIMESTAMP,
  tpep_dropoff_datetime TIMESTAMP,
  trip_distance DOUBLE,
  fare_amount DOUBLE,
  pickup_zip INT,
  dropoff_zip INT
);
```

## Schritt 3: Daten aus dem Cloud-Speicher laden

`header` behandelt die erste CSV-Zeile als Spaltennamen, `inferSchema` erkennt die Datentypen automatisch. Bei erneuter Ausführung werden bereits geladene Daten nicht erneut geladen, da `COPY INTO` nur neue Dateien verarbeitet.

```sql
%sql
COPY INTO <catalog-name>.<schema-name>.<table-name>
FROM 's3://<s3-bucket>/<folder>/'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',
  'inferSchema' = 'true')
COPY_OPTIONS (
  'mergeSchema' = 'true');

SELECT * FROM <catalog_name>.<schema_name>.<table_name>;
```

## Aufräumen

Tabelle löschen:

```sql
%sql
DROP TABLE <catalog-name>.<schema-name>.<table-name>;
```

Abfrage-Tabs lassen sich durch Klick auf das X-Symbol beim Überfahren mit der Maus schließen.

## Wichtiger Hinweis

Databricks empfiehlt, für das Laden von Millionen von Dateien Auto Loader zu verwenden. Auto Loader wird in Databricks SQL nicht unterstützt.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/tutorial-dbsql  
**Stand:** 2026-08-07
