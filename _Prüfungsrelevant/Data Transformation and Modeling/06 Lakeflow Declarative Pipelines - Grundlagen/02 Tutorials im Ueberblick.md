# Tutorials im Überblick

Grundmuster aller Tutorials: **New → ETL Pipeline** → Katalog/Schema mit Schreibrechten wählen → Sprache (SQL/Python) wählen → schrittweise Streaming Tables/Materialized Views über Auto Loader, Flows und Transformationen aufbauen.

## 1. Gemeinsame Voraussetzungen

- Workspace mit aktiviertem **Unity Catalog**.
- Recht, Compute zu erstellen oder bestehende zu nutzen (Serverless meist Default in UC-Workspaces).
- Recht, neues Schema (ggf. Volume) im Katalog zu erstellen.
- Volle Rechte zum Erstellen/Ausführen/Aktualisieren/Einsehen von Pipelines + Output.

## 2. Tutorial "Erste Pipeline": Grundmuster mit Expectations

1. Pipeline über **New → ETL Pipeline** erstellen (Name, Katalog/Schema, Sprache).
2. Code-Symbol → **Use sample code** → **Run pipeline**.
   — Ergebnis: aus Quelle `wanderbricks` (Tabelle `users`) entstehen `sample_users_<date_time>` und `sample_aggregation_<date_time>`.
3. Datenqualität via Expectation absichern:

```sql
CREATE MATERIALIZED VIEW users_cleaned(
  CONSTRAINT non_null_email EXPECT (email IS NOT NULL) ON VIOLATION DROP ROW)
AS SELECT * FROM sample_users_<date_time>;
-- Ergebnis: Zeilen mit email IS NULL werden verworfen (DROP ROW)
```

```python
from pyspark import pipelines as dp

@dp.materialized_view
@dp.expect_or_drop("no null emails", "email IS NOT NULL")
def users_cleaned():
    return spark.read.table("sample_users_<date_time>")
```

4. Join zu Top-100-Nutzern nach Buchungszahl:

```sql
CREATE OR REFRESH MATERIALIZED VIEW users_and_bookings AS
SELECT u.name AS name, COUNT(b.booking_id) AS booking_count
FROM users_cleaned u
JOIN samples.wanderbricks.bookings b ON u.user_id = b.user_id
GROUP BY u.name ORDER BY booking_count DESC LIMIT 100;
-- Ergebnis: Tabelle mit 100 Zeilen (name, booking_count), absteigend sortiert
```

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, count, desc

@dp.materialized_view
def users_and_bookings():
    return (spark.read.table("users_cleaned")
        .join(spark.read.table("samples.wanderbricks.bookings"), "user_id")
        .groupBy(col("name"))
        .agg(count("booking_id").alias("booking_count"))
        .orderBy(desc("booking_count")).limit(100))
```

Ergebnis-Graph: 4 Tabellen insgesamt. Weitere Editor-Features: Selective Execution, Data Previews, interaktiver Graph, Declarative-Automation-Bundles-Integration für Versionskontrolle/CI-CD.

## 3. Tutorial "ETL mit CDC": Bronze/Silver/Gold über mehrere Stufen

Künstliche CDC-Events (`APPEND`, `DELETE`, `UPDATE`) → konsolidierte Kundentabelle + vollständige Änderungshistorie.

**Bronze — Auto Loader, rohe CDC-Nachrichten (JSON) aus UC-Volume:**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import *

path = "/Volumes/<catalog>/<schema>/raw_data/customers"
dp.create_streaming_table("customers_cdc_bronze",
  comment="New customer data incrementally ingested from cloud object storage landing zone")

@dp.append_flow(target = "customers_cdc_bronze", name = "customers_bronze_ingest_flow")
def customers_bronze_ingest_flow():
  return (
      spark.readStream
          .format("cloudFiles")
          .option("cloudFiles.format", "json")
          .option("cloudFiles.inferColumnTypes", "true")
          .load(f"{path}")
  )
```

```sql
CREATE OR REFRESH STREAMING TABLE customers_cdc_bronze
COMMENT "New customer data incrementally ingested from cloud object storage landing zone";

CREATE FLOW customers_bronze_ingest_flow AS
INSERT INTO customers_cdc_bronze BY NAME
  SELECT *
  FROM STREAM read_files(
    "/Volumes/<catalog>/<schema>/raw_data/customers",
    format => "json",
    inferColumnTypes => "true"
  )
```

**Silver — Bereinigung mit Expectations** (verwirft `_rescued_data`-, fehlende `id`-, ungültige `operation`-Zeilen):

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import *

dp.create_streaming_table(
  name = "customers_cdc_clean",
  expect_all_or_drop = {"no_rescued_data": "_rescued_data IS NULL",
"valid_id": "id IS NOT NULL",
"valid_operation": "operation IN ('APPEND', 'DELETE', 'UPDATE')"}
  )

@dp.append_flow(target = "customers_cdc_clean",
  name = "customers_cdc_clean_flow")
def customers_cdc_clean_flow():
  return (
      spark.readStream.table("customers_cdc_bronze")
          .select("address", "email", "id", "firstname", "lastname",
          "operation", "operation_date", "_rescued_data")
  )
```

```sql
CREATE OR REFRESH STREAMING TABLE customers_cdc_clean (
  CONSTRAINT no_rescued_data EXPECT (_rescued_data IS NULL) ON VIOLATION DROP ROW,
  CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW,
  CONSTRAINT valid_operation EXPECT (operation IN ('APPEND', 'DELETE', 'UPDATE'))
    ON VIOLATION DROP ROW)
COMMENT "New customer data incrementally ingested from cloud object storage landing zone";

CREATE FLOW customers_cdc_clean_flow AS
INSERT INTO customers_cdc_clean BY NAME
SELECT * FROM STREAM customers_cdc_bronze;
```

**Gold — Auto CDC, SCD Type 1** (nur aktueller Stand):

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import *

dp.create_streaming_table(name="customers",
  comment="Clean, materialized customers")

dp.create_auto_cdc_flow(
  target="customers",
  source="customers_cdc_clean",
  keys=["id"],
  sequence_by=col("operation_date"),
  ignore_null_updates=False,
  apply_as_deletes=expr("operation = 'DELETE'"),
  except_column_list=["operation", "operation_date", "_rescued_data"],
)
```

```sql
CREATE OR REFRESH STREAMING TABLE customers;

CREATE FLOW customers_cdc_flow
AS AUTO CDC INTO customers
FROM stream(customers_cdc_clean)
KEYS (id)
APPLY AS DELETE WHEN
operation = "DELETE"
SEQUENCE BY operation_date
COLUMNS * EXCEPT (operation, operation_date, _rescued_data)
STORED AS SCD TYPE 1;
-- Ergebnis: customers enthält je id genau 1 Zeile (aktueller Stand), DELETE-Events entfernen die Zeile
```

**Historie — SCD Type 2** (analog zu Gold, parallel auf `customers_history`; einziger Unterschied: `stored_as_scd_type="2"` / `STORED AS SCD TYPE 2` → volle Änderungshistorie statt nur aktueller Zeile).

**Aggregation** über die SCD-2-Historie:

```sql
CREATE OR REPLACE MATERIALIZED VIEW customers_history_agg AS
SELECT
  id,
  count(distinct address) as address_count,
  count(distinct email) AS email_count,
  count(distinct firstname) AS firstname_count,
  count(distinct lastname) AS lastname_count
FROM customers_history
GROUP BY id
-- Ergebnis: je Kunde Anzahl unterschiedlicher Adressen/E-Mails/Namen über die Zeit
```

**Zeitplanung:** Editor → **Schedule** → **Schedules → Add schedule → New schedule** (erzeugt Job).

## 4. Tutorial "Datei-Pipelines": unstrukturierte Dokumente mit KI-Funktionen

Medaillon-Pipeline für PDF-Verträge: Bronze (rohe `FILE`-Referenzen) → Silver (geparst/klassifiziert) → Gold (extrahierte Felder je Vertragstyp).

- **Voraussetzung:** `FILE`-Datentyp + `ai_parse_document`/`ai_classify`/`ai_extract` im Preview-Status — von Workspace-Admin über **Previews → Manage Databricks previews** aktivieren (Preview-Channel nötig).

**Bronze — `FILE`-Referenzen per Auto Loader** (`cloudFiles.format = 'file'`; Tabelleneigenschaft `databricks.filespace-preview` referenziert einen Volume-Pfad als FileSpace):

```sql
CREATE OR REFRESH STREAMING TABLE raw_contracts (
  path STRING,
  size BIGINT,
  modification_time TIMESTAMP,
  file FILE MANAGED)
TBLPROPERTIES ('databricks.filespace-preview' = '/Volumes/my_catalog/my_schema/filespace/')
AS SELECT *
  FROM STREAM read_files(
    '/Volumes/samples/sec/contracts/',
    format => 'file');
```

```python
from pyspark import pipelines as dp

@dp.table(
  name="raw_contracts",
  schema="path STRING, size BIGINT, modification_time TIMESTAMP, file FILE MANAGED",
  table_properties={"databricks.filespace-preview": "/Volumes/my_catalog/my_schema/filespace/"})
def raw_contracts():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "file")
      .load("/Volumes/samples/sec/contracts/")
  )
```

**Silver — Parsen + Klassifizieren:**

```sql
CREATE OR REFRESH MATERIALIZED VIEW parsed_contracts AS
  SELECT path, ai_parse_document(file) AS parsed
  FROM raw_contracts;

CREATE OR REFRESH MATERIALIZED VIEW classified_contracts AS
  SELECT
    path, parsed,
    ai_classify(
      parsed,
      '["affiliate_agreement", "marketing_agreement", "consulting_agreement", "hosting_agreement", "escrow_agreement"]',
      map('version', '2.1')
    ):response[0].value::STRING AS contract_type
  FROM parsed_contracts
  WHERE is_variant_null(parsed:error_status);
-- Ergebnis: pro Dokument ein contract_type aus den 5 vorgegebenen Kategorien; ungeparste Dokumente (error_status gesetzt) werden gefiltert
```

**Gold — strukturierte Felder mit `ai_extract`** (Beispiel: `consulting_agreement`):

```sql
CREATE OR REFRESH MATERIALIZED VIEW consulting_agreements AS
  WITH extracted AS (
    SELECT
      path,
      ai_extract(
        parsed,
        '["company_name", "consultant_name", "compensation_amount", "effective_date"]',
        map('version', '2.1')
      ) AS fields
    FROM classified_contracts
    WHERE contract_type = 'consulting_agreement'
  )
  SELECT
    path,
    fields:response.company_name.value::STRING AS company_name,
    fields:response.consultant_name.value::STRING AS consultant_name,
    fields:response.compensation_amount.value::STRING AS compensation_amount,
    fields:response.effective_date.value::STRING AS effective_date
  FROM extracted;
-- Ergebnis: flache Tabelle mit je einer Zeile pro consulting_agreement-Vertrag und den 4 extrahierten Feldern
```

Muster (Filter auf `contract_type` + `ai_extract`) analog für weitere Vertragstypen fortsetzbar (z. B. `party_1_name`/`party_2_name`/`commission_rate` für `affiliate_agreement`).

## 5. Tutorial "Geodaten-Pipelines": räumliche Joins

GPS-Daten → native räumliche Typen (`GEOMETRY`) → Abgleich mit Lager-Geofences → Arrivals. Voraussetzung: DBR mit nativen räumlichen Typen/Funktionen (`ST_Point`, `ST_GeomFromWKT`, `ST_Contains`).

**Bronze — GPS-Pings via Auto Loader:**

```sql
CREATE OR REFRESH STREAMING TABLE gps_bronze
COMMENT "Raw GPS pings ingested from volume using Auto Loader";

CREATE FLOW gps_bronze_ingest_flow AS
INSERT INTO gps_bronze BY NAME
SELECT *
FROM STREAM read_files(
  "/Volumes/<catalog>/<schema>/raw_data/gps",
  format => "json",
  inferColumnTypes => "true")
```

**Silver — Koordinaten → Geometrie:**

```sql
CREATE OR REFRESH STREAMING TABLE raw_gps_silver
COMMENT "GPS pings with native geometry point for spatial joins";

CREATE FLOW raw_gps_silver_flow AS
INSERT INTO raw_gps_silver BY NAME
SELECT
  device_id, timestamp, longitude, latitude,
  ST_Point(longitude, latitude) AS point_geom
FROM STREAM(gps_bronze)
```

**Gold — Geofences (Materialized View) + räumlicher Join:**

```sql
CREATE OR REPLACE MATERIALIZED VIEW warehouse_geofences_gold AS
SELECT
  warehouse_name,
  ST_GeomFromWKT(boundary_wkt) AS boundary_geom
FROM read_files(
  "/Volumes/<catalog>/<schema>/raw_data/geofences",
  format => "json")

CREATE OR REPLACE MATERIALIZED VIEW warehouse_arrivals AS
SELECT
  g.device_id, g.timestamp, w.warehouse_name
FROM raw_gps_silver g
JOIN warehouse_geofences_gold w
  ON ST_Contains(w.boundary_geom, g.point_geom)
-- Ergebnis: eine Zeile je GPS-Punkt, der innerhalb eines Geofence-Polygons liegt
```

Verifikation z. B. via `GROUP BY warehouse_name` (Ankünfte je Lager) oder `ORDER BY timestamp DESC LIMIT 10`. Zeitplanung wie in Abschnitt 3 über **Schedule → Add schedule** (Standard: täglich).

## 6. Weitere Tutorials (nur benannt)

- **SQL-ETL:** inkrementelle ETL-Pipeline in Databricks SQL mit ST, `AUTO CDC`, MV.
- **Quellcode-verwaltete Pipeline:** Aufbau via Declarative-Automation-Bundles + Git-Ordner.
- **Bundle-Konvertierung:** bestehende Pipeline → Declarative-Automation-Bundles-Projekt.

## 7. Wiederkehrende Muster über alle Tutorials

- **Bronze/Silver/Gold:** Auto Loader (`cloudFiles`/`read_files()`) → Bronze-ST → bereinigt/transformiert (oft mit Expectations) in Silver → verdichtet (oft MV) in Gold.
- **`CREATE STREAMING TABLE` + `CREATE FLOW`** (SQL) bzw. `dp.create_streaming_table()` + `@dp.append_flow` (Python) = Standardmuster für inkrementellen Ingest.
- **Expectations** (`CONSTRAINT ... EXPECT ... ON VIOLATION DROP ROW` bzw. `expect_all_or_drop`/`expect_or_drop`) sichern Datenqualität ab.
- **`AUTO CDC INTO`** (SQL) / `create_auto_cdc_flow()` (Python): CDC deklarativ, SCD Type 1 (aktueller Stand) oder Type 2 (volle Historie) via `STORED AS SCD TYPE 1/2` bzw. `stored_as_scd_type`.
- **Zeitplanung** einheitlich über **Schedule**-Button (Dialog **Schedules → Add schedule**) — erzeugt im Hintergrund einen Job.

---

**Stand:** 2026-09-14.
