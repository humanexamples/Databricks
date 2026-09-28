# COPY INTO mit Unity-Catalog-Volumes oder External Locations

Diese Seite beschreibt, wie `COPY INTO` Daten aus Amazon S3 in Databricks-SQL-Tabellen lädt – entweder über Unity-Catalog-Volumes oder über External Locations.

## Voraussetzungen

- Die Berechtigung `READ VOLUME` auf einem Volume bzw. `READ FILES` auf einer External Location.
- Der Pfad zu den Quelldaten als Cloud-Object-Storage-URL oder Volume-Pfad, z. B. `s3://landing-bucket/raw-data/json` oder `/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data/json`.
- Die Berechtigung `USE SCHEMA` auf dem Schema, das die Zieltabelle enthält.
- Die Berechtigung `USE CATALOG` auf dem übergeordneten Katalog.

## Daten aus einem Volume laden

Bei Zugriff auf ein Volume mit dem Pfad `/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/` sind z. B. folgende Befehle gültig:

```sql
%sql
COPY INTO landing_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data'
FILEFORMAT = PARQUET;
```

```sql
%sql
COPY INTO json_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data/json'
FILEFORMAT = JSON;
```

## Daten über eine External Location laden

Folgendes Beispiel lädt Daten aus S3 in eine Tabelle unter Verwendung einer Unity-Catalog External Location für den Zugriff auf die Quelldaten:

```sql
%sql
COPY INTO my_json_data
FROM 's3://landing-bucket/json-data'
FILEFORMAT = JSON;
```

## Rechtevererbung bei External Locations

Berechtigungen auf einer External Location gelten für alle untergeordneten Verzeichnisse. Bei Zugriff auf eine External Location mit der URL `s3://landing-bucket/raw-data` sind z. B. folgende Befehle gültig:

```sql
%sql
COPY INTO landing_table
FROM 's3://landing-bucket/raw-data'
FILEFORMAT = PARQUET;
```

```sql
%sql
COPY INTO json_table
FROM 's3://landing-bucket/raw-data/json'
FILEFORMAT = JSON;
```

Berechtigungen auf dieser External Location gewähren jedoch keine Rechte auf übergeordnete oder parallele Verzeichnisse. Folgende Befehle sind z. B. **nicht** gültig:

```sql
%sql
COPY INTO parent_table
FROM 's3://landing-bucket'
FILEFORMAT = PARQUET;
```

```sql
%sql
COPY INTO sibling_table
FROM 's3://landing-bucket/json-data'
FILEFORMAT = JSON;
```

## Drei-Ebenen-Namespace für Zieltabellen

Zieltabellen können mit dem Drei-Ebenen-Namespace (`katalog.schema.tabelle`) referenziert werden:

```sql
%sql
COPY INTO quickstart_catalog.quickstart_schema.landing_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data'
FILEFORMAT = PARQUET;
```

Alternativ lassen sich Katalog und Schema vorab als Standard festlegen:

```sql
%sql
USE CATALOG quickstart_catalog;
USE SCHEMA quickstart_schema;

COPY INTO landing_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data'
FILEFORMAT = PARQUET;
```

Databricks empfiehlt grundsätzlich, Volumes gegenüber External Locations für den Dateizugriff zu bevorzugen.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/unity-catalog  
**Stand:** 2026-08-07
