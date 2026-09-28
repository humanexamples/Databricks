# Audit Logs, Billing und Lineage per System Tables abfragen

Drei praktisch besonders wichtige System-Tabellen-Schemas: Abrechnung (`system.billing`), Zugriffs-Audit (`system.access.audit`) und Data Lineage (`system.access.table_lineage`/`column_lineage`).

## Billing: `system.billing.usage`

Verfolgt abrechenbare Nutzung account-weit über alle Regionen hinweg — inklusive Korrekturen über `record_type` (`ORIGINAL`, `RETRACTION`, `RESTATEMENT`).

**Wichtige Spalten:** `record_id`, `account_id`, `workspace_id`, `sku_name` (z. B. `STANDARD_ALL_PURPOSE_COMPUTE`), `cloud`, `usage_start_time`, `usage_end_time`, `usage_date`, `custom_tags`, `usage_unit` (z. B. `DBU`), `usage_quantity`, `usage_metadata` (u. a. `job_id`), `identity_metadata` (u. a. `run_as`), `billing_origin_product`, `usage_type` (`COMPUTE_TIME`, `STORAGE_SPACE`, `NETWORK_BYTE`, …).

**DBU** (Databricks Unit) ist die Verarbeitungseinheit, in der Databricks abrechnet — jeder Job-, Query- oder Pipeline-Lauf verbraucht DBUs je nach genutztem Compute und Laufzeit. **SKU** identifiziert, welches Databricks-Produkt/-Tier die DBU-Nutzung erzeugt hat (Jobs Compute, All-Purpose Compute, DBSQL, Serverless, …) — da jede SKU unterschiedlich bepreist ist, lässt sich damit Spend nach Workload-Art aufschlüsseln.

**Beispiel — korrekte stündliche Aggregation inkl. Korrekturen:**

```sql
SELECT
  usage_metadata.job_id,
  usage_start_time,
  usage_end_time,
  SUM(usage_quantity) as usage_quantity
FROM system.billing.usage
GROUP BY ALL
HAVING usage_quantity != 0
```

## Audit-Logs: `system.access.audit`

Erfasst nahezu in Echtzeit, wer wann auf was zugegriffen hat.

**Wichtige Spalten:** `account_id`, `workspace_id`, `version`, `event_time`, `event_date`, `source_ip_address`, `user_agent`, `session_id`, `user_identity` (Struct), `service_name`, `action_name`, `request_id`, `request_params` (Map), `response` (Struct mit Statuscode/Fehlermeldung), `audit_level`, `event_id`, `identity_metadata` (`run_by`, `run_as`).

**Hinweise:** Die meisten Audit-Logs sind nur in der Region des jeweiligen Workspace verfügbar. Account-weite Audit-Logs tragen `workspace_id = 0`. Für bessere Performance auf `event_date` statt `event_time` filtern.

**Beispiele** (aus Kursmaterial übernommen und an das reale Schema angepasst):

```sql
-- Wer greift am häufigsten auf diese Tabelle zu?
SELECT user_identity.email, count(*)
FROM system.access.audit
WHERE request_params.table_full_name = "main.uc_deep_dive.login_data_silver"
  AND service_name = "unityCatalog"
  AND action_name = "generateTemporaryTableCredential"
GROUP BY 1 ORDER BY 2 DESC LIMIT 1;

-- Wer hat diese Tabelle gelöscht?
SELECT user_identity.email
FROM system.access.audit
WHERE request_params.full_name_arg = "main.uc_deep_dive.login_data_silver"
  AND service_name = "unityCatalog"
  AND action_name = "deleteTable";

-- Worauf hat dieser Nutzer in den letzten 24 Stunden zugegriffen?
SELECT request_params.table_full_name
FROM system.access.audit
WHERE user_identity.email = "user@example.com"
  AND service_name = "unityCatalog"
  AND action_name = "generateTemporaryTableCredential"
  AND datediff(now(), event_time) < 1;
```

## Lineage: `system.access.table_lineage` und `column_lineage`

Zwei Lineage-System-Tabellen erlauben programmatische Abfragen der Datenherkunft. Sie behalten ein **rollierendes 1-Jahres-Fenster** — ältere Events werden automatisch entfernt. Für Lineage über diesen Zeitraum hinaus: Catalog Explorer oder Lineage-API (unbegrenzte Aufbewahrung für Events ab dem 1. September 2024).

**`table_lineage`-Spalten (Auswahl):** `account_id`, `metastore_id`, `workspace_id`, `entity_type` (`NOTEBOOK`, `JOB`, `PIPELINE`, `DASHBOARD_V3`, `DBSQL_QUERY`, oder `NULL`), `entity_id`, `entity_run_id`, `source_table_full_name` (+ `_catalog`/`_schema`/`_name`), `source_path`, `source_type` (`TABLE`, `PATH`, `VIEW`, `MATERIALIZED_VIEW`, `METRIC_VIEW`, `STREAMING_TABLE`), analog `target_*`, `created_by`, `event_time`, `event_date`, `record_id`, `event_id`, `statement_id` (Fremdschlüssel zur Query-History, nur SQL-Warehouse), `entity_metadata`, `direct_access`.

`column_lineage` enthält zusätzlich `source_column_name` und `target_column_name`. **Hinweis:** Enthält keine Events ohne Quelle (z. B. Inserts mit expliziten Literalwerten).

**Event-Klassifizierung:** nur `source_type` gesetzt → Read; nur `target_type` gesetzt → Write; beide gesetzt → Read+Write.

**Beispiel:**

```sql
CREATE OR REPLACE TABLE car_features
AS SELECT *,
  in1+in2 as premium_feature_set
FROM car_features_exterior
JOIN car_features_interior
USING(id, model);
```

erzeugt u. a. folgenden `table_lineage`-Eintrag:

| entity_type | source_table_name | target_table_name | created_by |
|---|---|---|---|
| NOTEBOOK | car_features_exterior | car_features | user@example.com |

und folgenden `column_lineage`-Eintrag:

| source_table_name | target_table_name | source_column_name | target_column_name |
|---|---|---|---|
| car_features_interior | car_features | in1 | premium_feature_set |

**External Tables (per Pfad statt Name referenziert):**

```sql
SELECT *
FROM system.access.table_lineage
WHERE source_path = "s3://mybucket/table1" OR target_path = "s3://mybucket/table1";
```

**Hilfsfunktion, die Tabellenname und -pfad gleichzeitig abdeckt:**

```python
def getLineageForTable(table_name):
  table_path = spark.sql(f"describe detail {table_name}").select("location").head()[0]
  df = spark.read.table("system.access.table_lineage")
  return df.where(
    (df.source_table_full_name == table_name)
    | (df.target_table_full_name == table_name)
    | (df.source_path == table_path)
    | (df.target_path == table_path)
  )
```

**Einschränkung:** Records werden nur erzeugt, wenn sich Lineage tatsächlich ableiten lässt — die Lineage-System-Tabellen decken daher nur eine Teilmenge aller Lese-/Schreibzugriffe ab; die allgemeinen Data-Lineage-Einschränkungen von Unity Catalog gelten auch hier.

## Quellen

- https://docs.databricks.com/aws/en/admin/system-tables/audit-logs
- https://docs.databricks.com/aws/en/admin/system-tables/billing
- https://docs.databricks.com/aws/en/admin/system-tables/lineage
