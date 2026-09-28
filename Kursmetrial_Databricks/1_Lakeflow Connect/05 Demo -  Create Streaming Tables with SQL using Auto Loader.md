## Streaming Tables für die inkrementelle Verarbeitung erstellen

Führen Sie die folgenden Schritte aus, um das Volume `/Volumes/dbacademy/your-lab-user-schema/csv_files_autoloader_source` zu erkunden und zu bestätigen, dass es eine einzelne CSV-Datei enthält.

```sql
SELECT *
FROM read_files(
  '/Volumes/' || my_catalog || '/data_ingestion/csv_files_autoloader_source',
  format => 'CSV',
  sep => '|',
  header => true
);
```

#### Eine STREAMING TABLE mit Databricks SQL erstellen
Die inkrementelle Batch-Ingestion erkennt automatisch neue Datensätze in der Datenquelle und ignoriert bereits ingestierte Datensätze. Dadurch verringert sich die verarbeitete Datenmenge, sodass Ingestion-Jobs schneller laufen und Compute-Ressourcen effizienter nutzen.

```sql
CREATE OR REFRESH STREAMING TABLE sql_csv_autoloader
SCHEDULE EVERY 1 WEEK     -- Das Planen der Aktualisierung ist optional
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/ADD_YOUR_CATALOG_NAME/data_ingestion/csv_files_autoloader_source',
  format => 'CSV',
  sep => '|',
  header => true
);
```

```sql
DESCRIBE TABLE EXTENDED sql_csv_autoloader;
```

```sql
DESCRIBE HISTORY sql_csv_autoloader;
```

```sql
REFRESH STREAMING TABLE sql_csv_autoloader;
```

```sql
DESCRIBE HISTORY sql_csv_autoloader;
```

