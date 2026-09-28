[← Übersicht](00%20Uebersicht.md)

# Debezium-Dateien mit Auto Loader und AUTO CDC (End-to-End)

**Kombination:** Log-basiertes CDC (Debezium) · Auto Loader · Datei-Metadaten · Medallion · Expectations · AUTO CDC mit **SCD 1 und SCD 2 aus derselben Quelle** · Materialized View in Gold

```
Quell-DB ──Debezium──► JSON-Dateien im Volume
                          │  Auto Loader
                          ▼
              bronze_customers_cdc        (Rohevents, append-only, + Herkunft)
                          │  Temporary View + Expectations
                          ▼
              customers_cdc_clean         (flach, validiert)
                 │                  │
     AUTO CDC SCD 1        AUTO CDC SCD 2
                 ▼                  ▼
      silver_customers    silver_customers_history
                 │
                 ▼  Materialized View
      gold_customers_per_city
```

---

## Das Debezium-Eventformat

Debezium schreibt pro Zeilenänderung ein Event. Annahme hier: JSON **ohne** Schema-Envelope (`value.converter.schemas.enable=false`).

```json
{"before": null,
 "after":  {"customer_id": 42, "name": "Anna", "city": "Hamburg", "email": "anna@example.com"},
 "op": "c", "ts_ms": 1756700000000}

{"before": {"customer_id": 42, "name": "Anna", "city": "Hamburg", "email": "anna@example.com"},
 "after":  {"customer_id": 42, "name": "Anna", "city": "Berlin",  "email": "anna@example.com"},
 "op": "u", "ts_ms": 1756786400000}

{"before": {"customer_id": 42, "name": "Anna", "city": "Berlin", "email": "anna@example.com"},
 "after":  null,
 "op": "d", "ts_ms": 1756872800000}
```

| `op` | Bedeutung | Wo steht der Key? |
|---|---|---|
| `c` | Insert (create) | `after` |
| `u` | Update | `after` |
| `d` | Delete | **nur** in `before` |
| `r` | Read (Initial-Snapshot) | `after` |

---

## Python-Pipeline

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, coalesce, current_timestamp, expr

# ---------- Bronze: Rohevents unverändert + Herkunft (Auto Loader) ----------
@dp.table(comment="Debezium-Rohevents, append-only")
def bronze_customers_cdc():
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "json")
            .option("cloudFiles.inferColumnTypes", "true")
            .load("/Volumes/catalog/schema/landing/debezium/customers/")
            .select("*",
                    col("_metadata.file_path").alias("source_file"),
                    current_timestamp().alias("ingested_at")))

# ---------- Aufbereitung: Envelope flach machen + Data Quality ----------
@dp.temporary_view
@dp.expect_or_drop("valid_key", "customer_id IS NOT NULL")
@dp.expect_or_drop("valid_op", "op IN ('c', 'u', 'd', 'r')")
@dp.expect("valid_email", "email IS NULL OR email LIKE '%@%'")   # nur protokollieren
def customers_cdc_clean():
    return (spark.readStream.table("bronze_customers_cdc")
            .select(
                # bei Deletes ist 'after' NULL → Key aus 'before'
                coalesce(col("after.customer_id"), col("before.customer_id")).alias("customer_id"),
                col("after.name").alias("name"),
                col("after.city").alias("city"),
                col("after.email").alias("email"),
                col("op"),
                expr("timestamp_millis(ts_ms)").alias("change_ts")))

# ---------- Silver A: nur aktueller Stand (SCD 1) ----------
dp.create_streaming_table("silver_customers")

dp.create_auto_cdc_flow(
    target             = "silver_customers",
    source             = "customers_cdc_clean",
    keys               = ["customer_id"],
    sequence_by        = col("change_ts"),
    apply_as_deletes   = expr("op = 'd'"),
    except_column_list = ["op"],
    stored_as_scd_type = 1)

# ---------- Silver B: vollständige Historie (SCD 2) ----------
dp.create_streaming_table("silver_customers_history")

dp.create_auto_cdc_flow(
    target             = "silver_customers_history",
    source             = "customers_cdc_clean",
    keys               = ["customer_id"],
    sequence_by        = col("change_ts"),
    apply_as_deletes   = expr("op = 'd'"),
    except_column_list = ["op"],
    stored_as_scd_type = 2,
    track_history_except_column_list = ["email"])   # E-Mail-Änderung → keine neue Version

# ---------- Gold: Kennzahl auf dem aktuellen Stand ----------
@dp.materialized_view
def gold_customers_per_city():
    return (spark.read.table("silver_customers")
            .groupBy("city").count())
```

## Dasselbe in SQL

```sql
-- Bronze
CREATE OR REFRESH STREAMING TABLE bronze_customers_cdc AS
SELECT *, _metadata.file_path AS source_file, current_timestamp() AS ingested_at
FROM STREAM read_files('/Volumes/catalog/schema/landing/debezium/customers/',
                       format => 'json', inferColumnTypes => true);

-- Aufbereitung
CREATE TEMPORARY VIEW customers_cdc_clean AS
SELECT coalesce(after.customer_id, before.customer_id) AS customer_id,
       after.name, after.city, after.email,
       op,
       timestamp_millis(ts_ms) AS change_ts
FROM STREAM bronze_customers_cdc
WHERE op IN ('c', 'u', 'd', 'r');

-- Silver SCD 1
CREATE OR REFRESH STREAMING TABLE silver_customers;

CREATE FLOW customers_scd1 AS AUTO CDC INTO silver_customers
FROM STREAM customers_cdc_clean
KEYS (customer_id)
APPLY AS DELETE WHEN op = 'd'
SEQUENCE BY change_ts
COLUMNS * EXCEPT (op)
STORED AS SCD TYPE 1;

-- Silver SCD 2
CREATE OR REFRESH STREAMING TABLE silver_customers_history;

CREATE FLOW customers_scd2 AS AUTO CDC INTO silver_customers_history
FROM STREAM customers_cdc_clean
KEYS (customer_id)
APPLY AS DELETE WHEN op = 'd'
SEQUENCE BY change_ts
COLUMNS * EXCEPT (op)
STORED AS SCD TYPE 2
TRACK HISTORY ON * EXCEPT (email);

-- Gold
CREATE OR REFRESH MATERIALIZED VIEW gold_customers_per_city AS
SELECT city, count(*) AS customers
FROM silver_customers
GROUP BY city;
```

> In SQL sind Expectations auf Streaming Tables und Materialized Views über `CONSTRAINT … EXPECT … ON VIOLATION …` möglich. Für Expectations **auf der Quelle eines AUTO-CDC-Flows** ist die Python-Variante mit `@dp.temporary_view` + `@dp.expect_or_drop` der direkte Weg.

---

## Was die Kombination leistet

| Baustein | Aufgabe |
|---|---|
| Auto Loader | erkennt neue Debezium-Dateien, exactly-once, Schema-Inferenz |
| `_metadata.file_path` | Herkunft jedes Events → Nachverfolgbarkeit bei Fehlern |
| Bronze append-only | Roh-Change-Log bleibt vollständig erhalten → Replay jederzeit möglich |
| Expectations | ungültige Events (kein Key, unbekannte `op`) fliegen **vor** dem Merge raus |
| AUTO CDC | ordnet Events per `SEQUENCE BY`, dedupliziert, behandelt Out-of-Order-Events |
| SCD 1 + SCD 2 parallel | Analysten bekommen den aktuellen Stand, Audit bekommt die Historie — aus **einer** Quelle |
| `track_history_except_column_list` | irrelevante Änderungen (E-Mail) erzeugen keine neue Version |
| Materialized View | Gold rechnet bei SCD 1 inkrementell nach |

## Stolperfallen

- **Gleicher `ts_ms` für denselben Key:** Die Reihenfolge ist dann nicht eindeutig. Lösung: nach mehreren Spalten sequenzieren, z. B. `sequence_by = struct("change_ts", "lsn")` — siehe Referenz Abschnitt 3.2.
- **`NULL` in der Sequenzspalte** wird nicht unterstützt → Expectation `change_ts IS NOT NULL` ergänzen.
- **Initial-Snapshot (`op = 'r'`)** wird hier wie ein Insert behandelt. Liegt der Snapshot getrennt vor, besser per `once = True`-Flow laden (Referenz Abschnitt 9.2).
- Aus einem AUTO-CDC-Ziel **streamt** man weiter über dessen Change Data Feed → [04](04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md).

---
[← Übersicht](00%20Uebersicht.md) · [Nächste Datei →](02%20CDC%20aus%20Kafka.md)
