# Standalone Materialized Views überwachen

Dieses Dokument beschreibt Monitoring- und Troubleshooting-Möglichkeiten für Standalone Materialized Views: Detailansichten, Event-Log-Abfragen, Refresh-Verlauf und Kostenzuordnung.

## Abschnittsübersicht

1. [Details einer einzelnen Materialized View einsehen](#details)
2. [Läufe überwachen](#laeufe)
3. [Fehlgeschlagene Refreshes untersuchen](#troubleshooting)
4. [Kostenzuordnung](#kosten)
5. [Quellen](#quellen)

---

## <a id="details">1. Details einer einzelnen Materialized View einsehen</a>

Drei Wege stehen zur Verfügung:

### Catalog Explorer

Zeigt aktuellen Refresh-Status, Zeitpunkt des letzten Laufs, Refresh-Zeitpläne und benutzerdefinierte Tags. Detaillierte Fehlerinformationen sind über "See refresh details" abrufbar.

### `DESCRIBE EXTENDED`

```sql
-- Als Tabelle:
DESCRIBE TABLE EXTENDED sales;

-- Als einzelnes JSON-Objekt:
DESCRIBE TABLE EXTENDED sales AS JSON;
```

Liefert unter anderem: Status des letzten abgeschlossenen Refreshs, Refresh-Zeitplan, Spalten, Refresh-Typ, Datengröße in Bytes gesamt, Speicherort der Materialized View, Clustering-Spalten, Status von Deletion Vectors, Status von Row Tracking.

### Event-Log-Abfragen

Owner können eine View auf dem Event-Log anlegen oder direkt per `TABLE`-Wertfunktion abfragen:

```sql
CREATE VIEW my_event_log_view AS
SELECT *
FROM event_log(TABLE(<catalog_name>.<schema_name>.<mv_name>));
```

```sql
SELECT *
FROM my_event_log_view
WHERE event_type = "update_progress"
ORDER BY timestamp desc;
```

Direkte Abfrage (nur für den Owner möglich):

```sql
SELECT *
FROM event_log(TABLE(<catalog_name>.<schema_name>.<mv_name>))
WHERE event_type = "update_progress"
ORDER BY timestamp desc;
```

## <a id="laeufe">2. Läufe überwachen</a>

Drei Monitoring-Wege:

- **Jobs & Pipelines-Seite:** Filterung nach Pipeline-Typ "MV/ST", um alle zugänglichen Materialized Views/Streaming Tables anzuzeigen.
- **Query-History-Tab:** Zugriff auf `REFRESH`-Statements, die typischerweise detaillierte Query-Pläne enthalten ("REFRESH statements typically include detailed query plans").
- **Benachrichtigungen für Scheduled Refreshes:** konfigurierbar über Catalog Explorer oder job-basierte Zeitplanung.

### Refresh-Verlauf abfragen

```sql
SELECT *
FROM event_log(TABLE(<fully-qualified-table-name>))
WHERE event_type = "update_progress"
ORDER BY timestamp desc;
```

### Refresh-Typ abfragen (inkrementell vs. vollständig)

```sql
SELECT timestamp, message
FROM event_log(TABLE(my_catalog.my_schema.sales))
WHERE event_type = 'planning_information'
ORDER BY timestamp desc;
```

Beispielausgabe aus der Doku: `"Flow 'sales' has been planned to be executed as ROW_BASED."`

## <a id="troubleshooting">3. Fehlgeschlagene Refreshes untersuchen</a>

Die Pipeline-Monitoring-Seite liefert den Status des letzten Laufs sowie die Laufhistorie zusammen mit Event-Logs zur Fehlersuche.

## <a id="kosten">4. Kostenzuordnung</a>

Zwei Tagging-Ansätze:

### Warehouse-Tags (automatisch vererbt)

```sql
SELECT
  usage_metadata.dlt_pipeline_id,
  custom_tags,
  SUM(usage_quantity) AS dbus
FROM system.billing.usage
WHERE billing_origin_product = 'SQL'
  AND usage_metadata.dlt_pipeline_id IS NOT NULL
  AND usage_date >= DATEADD(day, -30, current_date)
GROUP BY ALL
ORDER BY dbus DESC;
```

### Objekt-Level-Tags (manueller Join gegen Billing-Daten)

```sql
SELECT
  u.*,
  tag_info.tags
FROM
  system.billing.usage u
LEFT JOIN (
  SELECT
    t.catalog_name,
    t.schema_name,
    t.table_name,
    collect_list(named_struct('tag_name', t.tag_name, 'tag_value', t.tag_value)) AS tags
  FROM
    main.information_schema.table_tags t
  GROUP BY
    t.catalog_name,
    t.schema_name,
    t.table_name) tag_info
  ON tag_info.catalog_name = u.usage_metadata.uc_table_catalog
  AND tag_info.schema_name = u.usage_metadata.uc_table_schema
  AND tag_info.table_name = u.usage_metadata.uc_table_name
WHERE usage_metadata.uc_table_name is not null;
```

---

## <a id="quellen">5. Quellen</a>

1. Monitor standalone materialized views (AWS): https://docs.databricks.com/aws/en/ldp/dbsql/materialized-monitor
