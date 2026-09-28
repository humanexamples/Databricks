

```sql
CREATE OR REPLACE TABLE lab13_lab_kafka_events_raw
AS
SELECT 
  *,
  cast(unbase64(value) as STRING) as decoded_value
FROM read_files(
        '/Volumes/' || my_catalog || '/data_ingestion/landing_folder/json_demo_files/lab_kafka_events.json',
        format => "json", 
        schema => '''
          key STRING, 
          timestamp DOUBLE, 
          value STRING
        ''',
        rescueddatacolumn => '_rescued_data'
      );
```

```sql
-- Parse the JSON formatted STRING
CREATE OR REPLACE TABLE lab13_lab_kafka_events_flattened_str
AS
SELECT 
  key,
  timestamp,
  decoded_value:user_id,
  decoded_value:event_type,
  cast(decoded_value:event_timestamp AS TIMESTAMP),
  from_json(decoded_value:items,'ARRAY<STRUCT<item_id: STRING, price_usd: DOUBLE, quantity: BIGINT>>') AS items
FROM lab13_lab_kafka_events_raw;
```

```sql
-- Den JSON-formatierten String in einen VARIANT umwandeln
-- HINWEIS: Die VARIANT-Spalte decoded_value_variant ist in dieser Lösung enthalten, um die Spalte anzuzeigen
-- HINWEIS: Der Datentyp VARIANT funktioniert nicht mit Serverless Version 1.
CREATE OR REPLACE TABLE lab13_lab_kafka_events_flattened_variant
AS
SELECT
  key,
  timestamp,
  parse_json(decoded_value) AS decoded_value_variant,
  cast(decoded_value_variant:user_id AS STRING),
  decoded_value_variant:event_type :: STRING,
  decoded_value_variant:event_timestamp :: TIMESTAMP,
  decoded_value_variant:items
FROM lab13_lab_kafka_events_raw;
```

```sql
-- Die obige JSON-Struktur innerhalb der Funktion from_json verwenden, 
-- um den JSON-formatierten String in einen STRUCT umzuwandeln
-- HINWEIS: Die STRUCT-Spalte decoded_value_struct ist 
-- in dieser Lösung enthalten, um die Spalte anzuzeigen
CREATE OR REPLACE TABLE lab13_lab_kafka_events_flattened_struct
AS
SELECT
  key,
  timestamp,
  from_json(decoded_value, 'STRUCT<event_timestamp: STRING, event_type: STRING, items: ARRAY<STRUCT<item_id: STRING, price_usd: DOUBLE, quantity: BIGINT>>, user_id: STRING>') AS decoded_value_struct,
  decoded_value_struct.user_id,
  decoded_value_struct.event_type,
  cast(decoded_value_struct.event_timestamp AS TIMESTAMP),
  decoded_value_struct.items
FROM lab13_lab_kafka_events_raw;
```
