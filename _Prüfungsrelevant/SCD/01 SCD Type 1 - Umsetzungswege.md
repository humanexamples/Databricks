[← Übersicht](00%20Uebersicht.md)

# SCD Type 1 – Umsetzungswege

**SCD 1:** nur der aktuelle Stand, alte Werte werden überschrieben. Welcher Weg passt, hängt davon ab, **was die Quelle liefert**:

| Quelle liefert | Weg |
|---|---|
| Change-Events (insert/update/delete + Sequenz) | A – AUTO CDC |
| geänderte Zeilen (Upserts, ohne Deletes) | B – `MERGE` aus Updates |
| jedes Mal den kompletten Bestand | C – `MERGE` aus Snapshot · D – AUTO CDC FROM SNAPSHOT · E – Full Overwrite |

---

## A – AUTO CDC (Change-Events)

```sql
CREATE OR REFRESH STREAMING TABLE dim_customer;

CREATE FLOW dim_customer_scd1 AS AUTO CDC INTO dim_customer
FROM STREAM customers_cdc_clean
KEYS (customer_id)
APPLY AS DELETE WHEN op = 'd'
SEQUENCE BY change_ts
COLUMNS * EXCEPT (op)
STORED AS SCD TYPE 1;          -- Default, könnte auch weggelassen werden
```

Vollständiges Beispiel mit Bronze und Expectations: [../CDC/01](../CDC/01%20Debezium-Dateien%20mit%20Auto%20Loader%20und%20AUTO%20CDC.md).

---

## B – `MERGE` aus Updates, kombiniert mit SCD 0 und SCD 3

Ein `MERGE` kann pro Spalte unterschiedlich mit Änderungen umgehen:

- `name`, `email` → **SCD 1** (überschreiben)
- `created_at` → **SCD 0** (nie ändern, nur beim Insert setzen)
- `city` → **SCD 3** (vorherigen Wert in `previous_city` merken)

```sql
MERGE INTO catalog.schema.dim_customer t
USING (
  SELECT * FROM customer_updates
  QUALIFY row_number() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) = 1
) s
ON t.customer_id = s.customer_id
WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE SET
  t.name          = s.name,                                   -- SCD 1
  t.email         = s.email,                                  -- SCD 1
  t.previous_city = CASE WHEN t.city <=> s.city THEN t.previous_city
                         ELSE t.city END,                     -- SCD 3
  t.city          = s.city,
  t.updated_at    = s.updated_at
  -- created_at wird bewusst nicht gesetzt                    -- SCD 0
WHEN NOT MATCHED THEN INSERT
  (customer_id, name, email, city, previous_city, created_at, updated_at)
  VALUES (s.customer_id, s.name, s.email, s.city, NULL, s.updated_at, s.updated_at);
```

- `QUALIFY` entfernt Duplikate **innerhalb** der neuen Daten. Das `MERGE` selbst dedupliziert nur gegen das Ziel.
- `<=>` ist der NULL-sichere Vergleich: `NULL <=> NULL` ist `true`.
- `s.updated_at > t.updated_at` schützt vor verspäteten, älteren Daten.

---

## C – `MERGE` aus einem Voll-Snapshot (inkl. Deletes)

Die Quelle liefert jeden Tag den kompletten Bestand. Was im Snapshot fehlt, wurde in der Quelle gelöscht.

```sql
MERGE INTO catalog.schema.dim_product t
USING catalog.schema.product_snapshot_today s
ON t.product_id = s.product_id
-- nur tatsächlich geänderte Zeilen anfassen → weniger neu geschriebene Dateien, schlankerer CDF
WHEN MATCHED AND (NOT (t.name <=> s.name) OR NOT (t.price <=> s.price)) THEN
  UPDATE SET *
WHEN NOT MATCHED THEN
  INSERT *
WHEN NOT MATCHED BY SOURCE THEN
  DELETE;
```

Ohne die Änderungsbedingung würde jede Zeile bei jedem Lauf neu geschrieben, auch wenn sich nichts geändert hat. Nachgelagerte CDF-Leser würden dann lauter Scheinänderungen sehen.

---

## D – AUTO CDC FROM SNAPSHOT (deklarativ, nur Python)

Derselbe Fall wie C, aber die Pipeline ermittelt Inserts, Updates und Deletes selbst durch Vergleich mit dem vorherigen Snapshot.

```python
from pyspark import pipelines as dp

@dp.temporary_view
def product_snapshot():
    return spark.read.table("catalog.schema.product_snapshot_today")

dp.create_streaming_table("dim_product")

dp.create_auto_cdc_from_snapshot_flow(
    target             = "dim_product",
    source             = "product_snapshot",
    keys               = ["product_id"],
    stored_as_scd_type = 1)
```

Varianten mit Versionsfunktion für mehrere Snapshot-Dateien: [Referenz Abschnitt 5.2](../Data%20Transformation%20and%20Modeling/Vertiefung%20%28ueber%20Pruefungsumfang%20hinaus%29/Lakeflow%20Declarative%20Pipelines%20-%20Transformation%20und%20CDC/03%20Change%20Data%20Capture%20%28CDC%29.md) · Datei-Fall: [Periodische Voll-Snapshots](../Ingestion/Datei%20Ingestion%20Varianten/05%20Periodische%20Voll-Snapshots.md).

---

## E – Full Overwrite

```sql
CREATE OR REPLACE TABLE catalog.schema.dim_product AS
SELECT * FROM catalog.schema.product_snapshot_today;
```

Technisch ebenfalls „nur aktueller Stand“, aber mit Nachteilen: Jede Zeile wird neu geschrieben, der CDF zeigt keine echten Einzeländerungen, und nachgelagerte Materialized Views müssen komplett neu rechnen. Nur für kleine Tabellen sinnvoll.

---

## Kombination: SCD 1 + Materialized View in Gold

SCD 1 hat einen Vorteil für nachgelagerte Materialized Views: Weil sich pro Lauf nur wenige Zeilen ändern, kann die MV **inkrementell** aktualisiert werden statt vollständig neu.

```sql
CREATE OR REFRESH MATERIALIZED VIEW gold_revenue_per_segment AS
SELECT c.segment, sum(o.amount) AS revenue
FROM silver_orders o
JOIN dim_customer c ON o.customer_id = c.customer_id
GROUP BY c.segment;
```

Bei SCD 2 müsste die MV zusätzlich nach `__END_AT IS NULL` filtern oder einen Point-in-Time-Join machen → [04](04%20SCD%20im%20Star-Schema.md).

---
[← Übersicht](00%20Uebersicht.md) · [Nächste Datei →](02%20SCD%20Type%202%20mit%20AUTO%20CDC.md)

## Quellen

- [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)
- [MERGE INTO (SQL language manual)](https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into)
