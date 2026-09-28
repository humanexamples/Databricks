

### Fehlerhafte Daten ingestieren und retten

Definieren Sie das Schema für die Ingestion explizit. Das Schema ist wie folgt definiert:
- `item_id` (STRING)
- `name` (STRING)
- `price` (DOUBLE)

Verwenden Sie die richtige Option, um die Rescued-Data-Spalte einzuschließen, und benennen Sie sie **_rescued_data**, um fehlerhafte Zeilen zu erfassen.

```sql
SELECT * 
FROM read_files(
        '/Volumes/'|| my_catalog || '/data_ingestion/landing_folder/csv_demo_files/lab_malformed_data.csv',
        format => "csv",
        sep => ",",
        header => true,
        schema => '''
              item_id STRING, 
              name STRING, 
              price DOUBLE
        ''',
        rescueddatacolumn => "_rescued_data"
      )
```

### B3. Zusätzliche Metadatenspalten während der Ingestion hinzufügen
```sql
---- Tabelle zu Demonstrationszwecken löschen, falls sie existiert
DROP TABLE IF EXISTS 10_lab_bronze;

---- Die UC-Tabelle erstellen
CREATE TABLE 10_lab_bronze 
AS
SELECT
  *,
  _metadata.file_modification_time AS file_modification_time,
  _metadata.file_name AS source_file, 
  current_timestamp() as ingestion_time
FROM read_files(
        '/Volumes/'|| my_catalog || '/data_ingestion/landing_folder/csv_demo_files/lab_malformed_data.csv',
        format => "csv",
        sep => ",",
        header => true,
        schema => 'item_id STRING, name STRING, price DOUBLE', 
        rescueddatacolumn => "_rescued_data"
      );
```

## C. (Optional) Challenge: Daten retten
Sie berichten Ihrem Datenteam, und alle sind sich einig, dass beim Ingestieren als Bronze-Tabelle alle Werte in der Rescued-Data-Spalte bereinigt werden sollen, die ein `$` enthalten. Um dieses Problem zu beheben, vereinbaren Sie, diese Sonderfälle während der Ingestion mithilfe der Spalte `_rescued_data` zu behandeln.

Ihr Team hat beschlossen, das `$` aus dem Preis zu entfernen und während der Ingestion einfach den numerischen Wert zu speichern.

```sql
CREATE OR REPLACE TABLE 10_lab_challenge
SELECT
  item_id,
  name,
  price,
  coalesce(price, replace(_rescued_data:price,'$','')) AS price_fixed,
  _rescued_data,
  _metadata.file_modification_time AS file_modification_time,
  _metadata.file_name AS source_file, 
  current_timestamp() as ingestion_timestamp
FROM read_files(
        '/Volumes/'|| my_catalog || '/data_ingestion/landing_folder/csv_demo_files/lab_malformed_data.csv',
        format => "csv",
        sep => ",",
        header => true,
        schema => 'item_id STRING, name STRING, price DOUBLE', 
        rescueddatacolumn => "_rescued_data"
      );

---- Die Tabelle anzeigen
SELECT *
FROM 10_lab_challenge
```
