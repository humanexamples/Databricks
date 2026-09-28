```sql
CREATE OR REPLACE TABLE kafka_events_bronze_decoded AS
SELECT
  cast(unbase64(key) AS STRING) AS decoded_key,
  offset,
  partition,
  timestamp,
  topic,
  cast(unbase64(value) AS STRING) AS decoded_value
FROM kafka_events_bronze_raw;
```

```sql
CREATE OR REPLACE TABLE kafka_events_bronze_string_flattened AS
SELECT
  decoded_key,
  offset,
  partition,
  timestamp,
  topic,
  decoded_value:device,
  decoded_value:traffic_source,
  decoded_value:geo,       -- Enthält einen weiteren JSON-formatierten String
  decoded_value:items      -- Enthält ein verschachteltes Array JSON-formatierter Strings
FROM kafka_events_bronze_decoded;


-- Die Tabelle anzeigen
SELECT *
FROM kafka_events_bronze_string_flattened;
```

------

```sql
SELECT schema_of_json('{"device":"Linux","ecommerce":{"purchase_revenue_in_usd":1075.5,"total_item_quantity":1,"unique_items":1},"event_name":"finalize","event_previous_timestamp":1593879231210816,"event_timestamp":1593879335779563,"geo":{"city":"Houston","state":"TX"},"items":[{"coupon":"NEWBED10","item_id":"M_STAN_K","item_name":"Standard King Mattress","item_revenue_in_usd":1075.5,"price_in_usd":1195.0,"quantity":1}],"traffic_source":"email","user_first_touch_timestamp":1593454417513109,"user_id":"UA000000106116176"}')
AS schema
```

Kopieren Sie die Ausgabe von `schema_of_json` und fügen Sie sie in die Funktion [**`from_json()`**](https://docs.databricks.com/en/sql/language-manual/functions/from_json.html) ein. 

```sql
CREATE OR REPLACE TABLE kafka_events_bronze_struct AS
SELECT 
  * EXCEPT (decoded_value),
  from_json(
      decoded_value,    -- JSON-formatierte String-Spalte
      'STRUCT<device: STRING, ecommerce: STRUCT<purchase_revenue_in_usd: DOUBLE, total_item_quantity: BIGINT, unique_items: BIGINT>, event_name: STRING, event_previous_timestamp: BIGINT, event_timestamp: BIGINT, geo: STRUCT<city: STRING, state: STRING>, items: ARRAY<STRUCT<coupon: STRING, item_id: STRING, item_name: STRING, item_revenue_in_usd: DOUBLE, price_in_usd: DOUBLE, quantity: BIGINT>>, traffic_source: STRING, user_first_touch_timestamp: BIGINT, user_id: STRING>') AS value
FROM kafka_events_bronze_decoded;


-- Die neue Tabelle anzeigen.
SELECT *
FROM kafka_events_bronze_struct
LIMIT 5;
```

```sql
SELECT 
  decoded_key,
  value.device as device,
  value.geo.city as city,
  value.items as items,
  array_size(items) AS number_elements_in_array
FROM kafka_events_bronze_struct
ORDER BY number_elements_in_array DESC;
```

#### C2.3 Arrays auflösen (Explode)

```sql
CREATE OR REPLACE TABLE bronze_explode_array AS
SELECT
  decoded_key,
  array_size(value.items) AS number_elements_in_array,
  explode(value.items) AS item_in_array,
  value.items
FROM kafka_events_bronze_struct
ORDER BY number_elements_in_array DESC;
```

## D. Arbeiten mit einer VARIANT-Spalte (Public Preview)

```sql
CREATE OR REPLACE TABLE kafka_events_bronze_variant AS
SELECT
  decoded_key,
  offset,
  partition,
  timestamp,
  topic,
  parse_json(decoded_value) AS json_variant_value   -- decoded_value in VARIANT konvertieren
FROM kafka_events_bronze_decoded;
```

```sql
SELECT
  json_variant_value,
  json_variant_value:device :: STRING,  -- Den Wert von device abrufen und in einen String casten
  json_variant_value:items
FROM kafka_events_bronze_variant
LIMIT 10;
```
