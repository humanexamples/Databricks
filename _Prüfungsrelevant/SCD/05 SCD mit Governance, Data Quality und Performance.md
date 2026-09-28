[← Übersicht](00%20Uebersicht.md)

# SCD mit Governance, Data Quality und Performance

**Kombination:** Expectations · Konsistenzprüfung der Historie · Unity Catalog (Dynamic View, Column Mask, Row Filter) · DSGVO-Löschung über alle Versionen · Liquid Clustering

---

## A – Data Quality **vor** dem SCD-Ziel

Fehlerhafte Events müssen raus, **bevor** sie eine Version erzeugen. Eine falsche Version in SCD 2 lässt sich später nur mühsam korrigieren.

```python
from pyspark import pipelines as dp

@dp.temporary_view
@dp.expect_or_drop("valid_key", "customer_id IS NOT NULL")
@dp.expect_or_drop("valid_sequence", "change_ts IS NOT NULL")   # NULL-Sequenz wird von AUTO CDC nicht unterstützt
@dp.expect_or_drop("valid_op", "op IN ('c', 'u', 'd', 'r')")
@dp.expect("plausible_city", "city IS NULL OR length(city) > 1")  # nur protokollieren
def customers_cdc_clean():
    # flache Change-Events; Aufbereitung des Debezium-Formats wie in ../CDC/01
    return spark.readStream.table("bronze_customers_cdc_flat")
```

Vollständiger Ablauf mit Bronze und beiden SCD-Zielen: [../CDC/01](../CDC/01%20Debezium-Dateien%20mit%20Auto%20Loader%20und%20AUTO%20CDC.md). Soll nichts verloren gehen, statt `expect_or_drop` das **Quarantine Pattern** verwenden: [Data Quality Checks und Validierung](../Data%20Transformation%20and%20Modeling/07%20Data%20Quality%20Checks%20und%20Validierung.md).

---

## B – Data Quality **nach** dem SCD-Ziel: Ist die Historie konsistent?

Zwei Regeln, die für jede SCD-2-Tabelle gelten müssen:

1. Pro Key höchstens **eine** aktuelle Version.
2. Die Versionen eines Keys **überlappen sich nicht**.

```sql
-- Prüf-View in der Pipeline: bricht das Update ab, wenn die Historie kaputt ist
CREATE OR REFRESH MATERIALIZED VIEW dq_customer_history (
  CONSTRAINT one_current_version EXPECT (current_versions <= 1)  ON VIOLATION FAIL UPDATE,
  CONSTRAINT no_overlap          EXPECT (overlaps = 0)           ON VIOLATION FAIL UPDATE
) AS
SELECT customer_id,
       count_if(__END_AT IS NULL) AS current_versions,
       count_if(next_start < __END_AT) AS overlaps
FROM (
  SELECT customer_id, __START_AT, __END_AT,
         lead(__START_AT) OVER (PARTITION BY customer_id ORDER BY __START_AT) AS next_start
  FROM dim_customer_history
)
GROUP BY customer_id;
```

> **Lücken** zwischen Versionen sind dagegen erlaubt: Wird ein Kunde gelöscht und später neu angelegt, liegt zwischen `__END_AT` der alten und `__START_AT` der neuen Version ein Zeitraum ohne Zeile.

---

## C – Zugriff steuern (Unity Catalog)

### C1 – Dynamic View: nur aktuelle Zeilen, E-Mail maskiert

Der einfachste Weg für AUTO-CDC-Ziele, weil die Tabelle selbst unverändert bleibt:

```sql
CREATE VIEW catalog.gold.v_customer_current AS
SELECT customer_id,
       name,
       city,
       CASE WHEN is_account_group_member('pii_readers') THEN email
            ELSE '***' END AS email
FROM catalog.silver.dim_customer_history
WHERE __END_AT IS NULL;

GRANT SELECT ON VIEW catalog.gold.v_customer_current TO `analysts`;
-- analysts bekommen KEIN SELECT auf die Tabelle selbst → Historie und Klartext-E-Mail bleiben verborgen
```

### C2 – Column Mask und Row Filter direkt auf der Tabelle

Für manuell gepflegte SCD-Tabellen ([03](03%20SCD%20Type%202%20manuell%20mit%20MERGE.md)). Die Regeln gelten dann für **jeden** Zugriff, auch ohne View. Annahme im Beispiel: Die Tabelle hat zusätzlich die Spalten `email` und `region`.

```sql
CREATE FUNCTION catalog.schema.mask_email(email STRING)
RETURN CASE WHEN is_account_group_member('pii_readers') THEN email ELSE '***' END;

CREATE FUNCTION catalog.schema.region_filter(region STRING)
RETURN is_account_group_member('admins')
    OR (region = 'DE' AND is_account_group_member('team_de'));

ALTER TABLE catalog.schema.dim_customer_history
  ALTER COLUMN email SET MASK catalog.schema.mask_email;

ALTER TABLE catalog.schema.dim_customer_history
  SET ROW FILTER catalog.schema.region_filter ON (region);
```

Mask und Filter wirken auf **alle Versionen** der Historie gleichermaßen.

---

## D – DSGVO: Recht auf Löschung bei SCD 2

Bei SCD 2 stecken personenbezogene Daten nicht nur in der aktuellen Zeile, sondern in **jeder alten Version**. Das Schließen der Version (Delete-Event) reicht deshalb nicht: Die Daten stehen weiterhin in der Historie.

```sql
-- 1. Alle Versionen der Person entfernen (auf AUTO-CDC-Zielen ist DML erlaubt,
--    sobald die Tabelle in Unity Catalog veröffentlicht ist)
DELETE FROM catalog.silver.dim_customer_history WHERE customer_id = 42;

-- 2. Auch Bronze/Change-Log enthält die Rohevents
DELETE FROM catalog.bronze.bronze_customers_cdc
WHERE coalesce(after.customer_id, before.customer_id) = 42;

-- 3. Alte Datendateien physisch entfernen (nach Ablauf der Retention)
VACUUM catalog.silver.dim_customer_history;
VACUUM catalog.bronze.bronze_customers_cdc;
```

**Alternative:** Personenbezogene Spalten pseudonymisieren, bevor sie in die SCD-Tabelle gelangen (Token statt Klarname). Dann genügt es, den Eintrag in der Token-Tabelle zu löschen, und die Historie bleibt analytisch nutzbar.

Löschungen in nachgelagerte Tabellen weitergeben: [../CDC/04, Abschnitt C](../CDC/04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md).

---

## E – Performance

| Maßnahme | Wirkung | Umsetzung |
|---|---|---|
| **Liquid Clustering** auf dem Key | `MERGE` und AUTO CDC finden die betroffenen Zeilen schneller | `CREATE OR REFRESH STREAMING TABLE dim_customer_history CLUSTER BY (customer_id);` · Python: `dp.create_streaming_table("…", cluster_by=["customer_id"])` · manuell: `CLUSTER BY (customer_id, is_current)` |
| **`TRACK HISTORY`** | weniger unnötige Versionen → kleinere Tabelle | [02, Abschnitt B](02%20SCD%20Type%202%20mit%20AUTO%20CDC.md) |
| **Nur echte Änderungen schreiben** | weniger neu geschriebene Dateien, schlankerer CDF | Änderungsbedingung im `MERGE` ([01, Abschnitt C](01%20SCD%20Type%201%20-%20Umsetzungswege.md)) |
| **Predictive Optimization** | `OPTIMIZE` und `VACUUM` laufen automatisch | für Unity-Catalog-Managed-Tables aktivieren |
| **Range Join** für Point-in-Time-Abfragen | schnellere Fakt-Dimension-Joins | [04, Abschnitt A](04%20SCD%20im%20Star-Schema.md) |

---
[← Vorherige Datei](04%20SCD%20im%20Star-Schema.md) · [Übersicht](00%20Uebersicht.md) · [Nächste Datei →](06%20SCD%20Type%202%20vs.%20Delta%20Time%20Travel.md)

## Quellen

- [Manage data quality with pipeline expectations](https://docs.databricks.com/aws/en/ldp/expectations)
- [Filter sensitive table data using row filters and column masks](https://docs.databricks.com/aws/en/tables/row-and-column-filters)
- [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)
