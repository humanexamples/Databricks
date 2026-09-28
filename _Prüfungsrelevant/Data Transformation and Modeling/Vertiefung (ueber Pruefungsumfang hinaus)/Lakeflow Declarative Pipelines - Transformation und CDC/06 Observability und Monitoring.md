# Observability und Monitoring in Lakeflow Declarative Pipelines

## 1. Die drei Monitoring-Ebenen

- **Jobs-&-Pipelines-Liste:** schnellste Prüfmöglichkeit — Status der letzten fünf Läufe je Pipeline.
- **Pipeline-Monitoring-UI:** nach Status eingefärbter Graph, Zeilenanzahlen/Datenqualitätsmetriken je Tabelle, Update-Historie, Streaming-Backlog-Metriken.
- **Event Log:** zugrunde liegende Wahrheitsquelle — strukturierte Delta-Tabelle, programmatisch abfragbar.
- **Benachrichtigungen:** an der Pipeline (eigener Zeitplan) oder als Job-Benachrichtigungen.
- Themen: UI-Monitoring, Event Log (Lineage, Datenqualität, Ressourcennutzung), Query History, Custom Monitoring (Event Hooks).
- Troubleshooting: Streaming-Checkpoint-Fehlschlag-Recovery (Abschnitt 6), hohe Initialisierungszeiten (Abschnitt 7).

## 2. Pipelines in der UI überwachen

### 2.1 E-Mail-Benachrichtigungen

Konfigurierbar für: Update erfolgreich; Update fehlgeschlagen (wiederholbar/nicht — jeder Fehlschlag); Update mit fatalem Fehler (nur diese Fälle); einzelner Flow fehlgeschlagen. Konfiguration in Pipeline-Einstellungen. Für Custom-Reaktionen: Python-Event-Hooks (Abschnitt 5).

### 2.2 Jobs-&-Pipelines-Liste

Workspace-Seitenleiste → **Jobs & Pipelines**: Ersteller, Trigger, Ergebnis der letzten fünf Läufe. Filter: Textsuche, **Type** (Jobs/Pipelines/All, bei Pipelines zusätzlich ETL/Ingestion), **Owner**, **Favorites**, **Tags** (bis 5), **Run as** (bis 2). Play/Stop-Icons zum Starten/Stoppen; Kebab-Menü für weitere Aktionen.

### 2.3 Pipeline-Details auf der Monitoring-Seite

- Pipeline-Graph (DAG) erscheint nach Update-Start; Pfeile = Abhängigkeiten. Rechter Bereich: ID, Compute-Kosten, Edition, Channel, Update-Details.
- **Edit pipeline** → Quellcode; **Navigate to code** beim Tabellen-Hover.
- **List**-Ansicht: alle Datasets tabellarisch, filterbar nach Name/Typ/Status.
- **Run as**-Nutzer = Pipeline-Owner (Updates laufen mit dessen Rechten, änderbar über **Permissions**).
- **Update-Ausführungsverhalten:** Zeitplan/API/kontinuierlich → automatisches Retry/Restart. UI/Editor → Fast-Start, debugging-fokussiert. **Run now with different settings** überschreibt für einzelnen Lauf.
- Fehler im Event Log: **View logs**-Button; auch über **View event log** rechts. Im Editor: **Issues**-Panel.

### 2.4 Unified-Runs-List-Preview

- **Public Preview**, standardmäßig an (Admin kann deaktivieren). Zugriff: **Runs** in Seitenleiste oder **Jobs & Pipelines** → Tab **Runs**.
- Zeigt Läufe der letzten **60 Tage**; bei Filter auf Jobs/Pipelines, Admin, oder `Run as: Me` zusätzlich Graph mit Erfolg/Fehlschlag der letzten **48 Stunden** (bis zu 1 h Verzögerung).
- Filter: Name, All/Jobs/Pipelines, Pipeline type, Run as, Start time, Run status, Error code. Spalten: End time, Run ID, Launched, Duration, Run parameters.

### 2.5 Dataset-Details

Klick auf Dataset zeigt: **Schema**, **Datenqualitätsmetriken**, **Quellcode** (Navigate to code), **Query History** (Performance-Tab). Tabellenkommentare nur im Catalog Explorer (View in catalog).

### 2.6 Update-Historie

Dropdown zeigt vergangene Updates (Graph/Details/Ereignisse); **Show the latest update** kehrt zurück. **60 Tage** in dieser Ansicht sichtbar; ältere nur im Event Log.

### 2.7 Fehlgeschlagenes Update debuggen

1. **Fehlerursache identifizieren:** fehlgeschlagene Tabellen/Flows im DAG hervorgehoben, zeigt ob isoliert oder auf Nachgelagerte übergriffen.
2. **Event Log für vollständige Meldung abfragen:** UI kann kürzen — `error`/`details`-Spalten enthalten vollständigen Stack Trace.
3. **Nur Fehlgeschlagenes erneut ausführen:** **Refresh failed tables** wiederholt nur fehlgeschlagene Tabellen + Nachgelagerte.
4. **Vor vollständigem Update validieren:** **Validate** prüft Graph/Code erneut, ohne zu materialisieren.
5. **Retry-Verhalten:** manuell aus Editor ausgelöst → keine automatischen Retries. Zeitplan/API → automatische Retries für behebbare Fehler.

- **Gotcha:** ungültiger/inkompatibler Streaming-Checkpoint (nach Änderung an `dropDuplicates()`/Aggregation, oder Quelländerung) — einfacher Retry behebt das nicht, Neuverarbeitung nötig (Full Refresh oder Checkpoint-Reset, Abschnitt 6).

### 2.8 Streaming-Metriken anzeigen

**Public Preview.** Je Streaming-Flow (Kafka, Kinesis, Auto Loader, Delta): Backlog-Sekunden/Bytes/Datensätze/Dateien als Diagramme — je Minute aggregierter Max, letzte **48 Stunden**. Chart-Icon im Graph bei verfügbaren Metriken (öffnet **Flows**-Tab); Filter **Has streaming metrics**.

| Quelle | Backlog Bytes | Backlog Records | Backlog Seconds | Backlog Files |
|---|---|---|---|---|
| Kafka | ✓ | ✓ | | |
| Kinesis | ✓ | | ✓ | |
| Delta | ✓ | | | ✓ |
| Auto Loader | ✓ | | | ✓ |
| Google Pub/Sub | ✓ | ✓ | | |

## 3. Pipeline-Event-Log direkt abfragen

- Enthält: Audit-Logs, Datenqualitätsprüfungen, Pipeline-Fortschritt, Lineage. Zugriff: UI, REST-API, direkte Abfrage.
- **Gotcha:** Event Log / dessen Katalog/Schema nicht löschen — Pipeline könnte künftig nicht mehr aktualisieren.

### 3.1 Zugriffswege

Standard (UC, Default Publishing): versteckte Delta-Tabelle im Default-Katalog/-Schema. Standardmäßig nur **Run-As-User** berechtigt:

```sql
SELECT * FROM event_log(<pipelineId>);
```

- Tabellenname: `event_log_{pipeline_id}` (Bindestriche→Unterstriche); sichtbar in `system.information_schema.tables`, nicht im Catalog Explorer — Zugriff nur via `event_log()`.
- Veröffentlichung über **Advanced settings** (Name, optional Katalog/Schema):

```json
{
  "id": "ec2a0ff4-d2a5-4c8c-bf1d-d9f12f10e749",
  "name": "billing_pipeline",
  "event_log": {
    "catalog": "catalog_name",
    "schema": "schema_name",
    "name": "event_log_table_name"
  }
}
```

- Event-Log-Speicherort dient auch als Schema-Speicherort für alle Auto-Loader-Abfragen. Empfehlung vor Berechtigungsänderung: erst View erstellen (manche Compute-Einstellungen könnten sonst Schema-Metadaten-Zugriff ermöglichen):

```sql
CREATE VIEW event_log_raw
AS SELECT * FROM <catalog_name>.<schema_name>.<event_log_table_name>;
```

- In UC unterstützen Views auch Streaming-Abfragen: `spark.readStream.table("event_log_raw")`. Folgende Beispiele setzen `event_log_raw` voraus.

### 3.2 Basis-Abfragebeispiele

Pipeline-Updates überwachen (ID, Status, Zeiten, Dauer):

```sql
with last_status_per_update AS (
    SELECT
        origin.pipeline_id AS pipeline_id,
        origin.pipeline_name AS pipeline_name,
        origin.update_id AS pipeline_update_id,
        FROM_JSON(details, 'struct<update_progress: struct<state: string>>').update_progress.state AS last_update_state,
        timestamp,
        ROW_NUMBER() OVER (PARTITION BY origin.update_id ORDER BY timestamp DESC) AS rn
    FROM event_log_raw
    WHERE event_type = 'update_progress'
    QUALIFY rn = 1
),
update_durations AS (
    SELECT
        origin.pipeline_id AS pipeline_id,
        origin.pipeline_name AS pipeline_name,
        origin.update_id AS pipeline_update_id,
        MIN(CASE WHEN event_type = 'create_update' THEN timestamp END) AS start_time,
        COALESCE(
            MAX(CASE
                WHEN event_type = 'update_progress'
                 AND FROM_JSON(details, 'struct<update_progress: struct<state: string>>').update_progress.state IN ('COMPLETED', 'FAILED', 'CANCELED')
                THEN timestamp
            END),
            current_timestamp()
        ) AS end_time
    FROM event_log_raw
    WHERE event_type IN ('create_update', 'update_progress')
      AND origin.update_id IS NOT NULL
    GROUP BY pipeline_id, pipeline_name, pipeline_update_id
    HAVING start_time IS NOT NULL
)
SELECT
    s.pipeline_id, s.pipeline_name, s.pipeline_update_id,
    d.start_time, d.end_time,
    CASE WHEN d.start_time IS NOT NULL AND d.end_time IS NOT NULL THEN
        ROUND(TIMESTAMPDIFF(MILLISECOND, d.start_time, d.end_time) / 1000)
    ELSE NULL END AS duration_seconds,
    s.last_update_state AS pipeline_update_status
FROM last_status_per_update s
JOIN update_durations d
  ON s.pipeline_id = d.pipeline_id AND s.pipeline_update_id = d.pipeline_update_id
ORDER BY d.start_time DESC;
```

Kosten eines Pipeline-Updates (DBU-Verbrauch, Run-As-Nutzer):

```sql
SELECT
  sku_name, billing_origin_product, usage_date,
  collect_set(identity_metadata.run_as) as users,
  SUM(usage_quantity) AS `DBUs`
FROM system.billing.usage
WHERE usage_metadata.dlt_pipeline_id = :pipeline_id
GROUP BY ALL;
```

### 3.3 Erweiterte Abfragebeispiele

Metriken für alle Flows (Datenqualität, verarbeitete Zeilen — Output/gelöscht/upserted/verworfen), aggregiert über `flow_progress`:

```sql
WITH flow_progress_raw AS (
  SELECT
    origin.pipeline_name AS pipeline_name, origin.pipeline_id AS pipeline_id,
    origin.flow_name AS table_name, origin.update_id AS update_id, timestamp,
    details:flow_progress.status AS status,
    TRY_CAST(details:flow_progress.metrics.num_output_rows AS BIGINT) AS num_output_rows,
    TRY_CAST(details:flow_progress.metrics.num_upserted_rows AS BIGINT) AS num_upserted_rows,
    TRY_CAST(details:flow_progress.metrics.num_deleted_rows AS BIGINT) AS num_deleted_rows,
    TRY_CAST(details:flow_progress.data_quality.dropped_records AS BIGINT) AS num_expectation_dropped_rows,
    FROM_JSON(details:flow_progress.data_quality.expectations,
      SCHEMA_OF_JSON("[{'name':'str', 'dataset':'str', 'passed_records':42, 'failed_records':42}]")) AS expectations_array
  FROM event_log_raw
  WHERE event_type = 'flow_progress'
    AND origin.flow_name IS NOT NULL
    AND origin.flow_name != 'pipelines.flowTimeMetrics.missingFlowName'
),
aggregated_flows AS (
  SELECT
    pipeline_name, pipeline_id, update_id, table_name,
    MIN(CASE WHEN status IN ('STARTING', 'RUNNING', 'COMPLETED') THEN timestamp END) AS start_timestamp,
    MAX(CASE WHEN status IN ('STARTING', 'RUNNING', 'COMPLETED') THEN timestamp END) AS end_timestamp,
    MAX_BY(status, timestamp) FILTER (WHERE status IN ('COMPLETED', 'FAILED', 'CANCELLED', 'EXCLUDED', 'SKIPPED', 'STOPPED', 'IDLE')) AS final_status,
    SUM(COALESCE(num_output_rows, 0)) AS total_output_records,
    SUM(COALESCE(num_upserted_rows, 0)) AS total_upserted_records,
    SUM(COALESCE(num_deleted_rows, 0)) AS total_deleted_records,
    MAX(COALESCE(num_expectation_dropped_rows, 0)) AS total_expectation_dropped_records,
    MAX(expectations_array) AS total_expectations
  FROM flow_progress_raw
  GROUP BY pipeline_name, pipeline_id, update_id, table_name
)
SELECT af.*, CASE WHEN af.start_timestamp IS NOT NULL AND af.end_timestamp IS NOT NULL THEN
    ROUND(TIMESTAMPDIFF(MILLISECOND, af.start_timestamp, af.end_timestamp) / 1000) ELSE NULL END AS duration_seconds
FROM aggregated_flows af
ORDER BY af.end_timestamp DESC;
```

Datenqualitäts-/Expectations-Metriken (`details:flow_progress.data_quality`, Event-Typ `flow_progress`; Metriken: `dropped_records`, `passed_records`, `failed_records`):

```sql
SELECT
  row_expectations.dataset as dataset, row_expectations.name as expectation,
  SUM(row_expectations.passed_records) as passing_records,
  SUM(row_expectations.failed_records) as failing_records
FROM (
    SELECT explode(from_json(details:flow_progress:data_quality:expectations,
      "array<struct<name: string, dataset: string, passed_records: int, failed_records: int>>")) row_expectations
    FROM event_log_raw
    WHERE event_type = 'flow_progress'
)
GROUP BY row_expectations.dataset, row_expectations.name;
```

Lineage-Informationen (Event-Typ `flow_definition`, `output_dataset`/`input_datasets` je Graph-Beziehung):

```sql
SELECT
  details:flow_definition.output_dataset as flow_name,
  details:flow_definition.input_datasets as input_flow_names,
  details:flow_definition.flow_type as flow_type,
  details:flow_definition.schema
FROM event_log_raw
WHERE details:flow_definition IS NOT NULL
ORDER BY timestamp;
```

Auto-Loader-Ingestion überwachen (Event-Typ `operation_progress`, `type` gleich `AUTO_LOADER_LISTING`/`AUTO_LOADER_BACKFILL`; zusätzlich `status`, `duration_ms`, `auto_loader_details:source_path`, `auto_loader_details:num_files_listed`):

```sql
SELECT timestamp, details:operation_progress.status, details:operation_progress.type,
  details:operation_progress:auto_loader_details
FROM event_log_raw
WHERE event_type like 'operation_progress'
  AND details:operation_progress.type in ('AUTO_LOADER_LISTING', 'AUTO_LOADER_BACKFILL');
```

Daten-Backlog überwachen (`details:flow_progress.metrics.backlog_bytes`, Event-Typ `flow_progress`; je nach Quelltyp/Runtime ggf. nicht verfügbar):

```sql
SELECT timestamp, Double(details:flow_progress.metrics.backlog_bytes) as backlog
FROM event_log_raw
WHERE event_type ='flow_progress';
```

- **Autoscaling (klassisches Compute):** Event-Typ `autoscale`, nur bei Enhanced Autoscaling erfasst — `details:autoscale.status`/`requested_num_executors` mit Werten `RESIZING`, `SUCCEEDED`, `PARTIALLY_SUCCEEDED`, `FAILED`.
- **Cluster-Ressourcennutzung (klassisches Compute):** Event-Typ `cluster_resources` — `avg_num_queued_tasks`, `avg_task_slot_utilization`, `num_executors`; bei Enhanced Autoscaling zusätzlich `latest_requested_num_executors`, `optimal_num_executors`, Status wie `CLUSTER_AT_DESIRED_SIZE`, `SCALE_UP_IN_PROGRESS_WAITING_FOR_EXECUTORS`, `BLOCKED_FROM_SCALING_DOWN_BY_CONFIGURATION`.
- **Pipeline-Streaming-Metriken:** `stream_progress`-Ereignisse ähneln `StreamingQueryListener`-Metriken; Unterschiede: `numInputRows`/`inputRowsPerSecond`/`processedRowsPerSecond` fehlen; Kafka/Kinesis-Offsets ggf. abgeschnitten (zusätzliches `...Truncated`-Feld):

```sql
SELECT parse_json(get_json_object(details, '$.stream_progress.progress_json')) AS stream_progress_json
FROM event_log_raw
WHERE event_type = 'stream_progress';
```

### 3.4 Pipelines auditieren

- Event-Log + weitere Databricks-Audit-Logs = vollständiges Bild der Datenaktualisierung. Pipelines nutzen Credentials des Owners (änderbar per Owner-Wechsel). Audit-Log erfasst Nutzer für Pipeline-Aktionen.

Nutzeraktionen (Event-Typ `user_action`):

```sql
SELECT timestamp, details:user_action:action, details:user_action:user_name FROM event_log_raw WHERE event_type = 'user_action'
```

Laufzeitinformationen (z. B. Runtime-Version):

```sql
SELECT origin.update_id, details:runtime_details:runtime_version:dbr_version FROM event_log_raw WHERE event_type = 'runtime_details'
```

## 4. Event-Log-Schema (Feldreferenz)

### 4.1 PipelineEvent-Objekt

| Feld | Beschreibung |
|---|---|
| `id` | eindeutiger Bezeichner |
| `sequence` | Metadaten zur Ordnung von Ereignissen |
| `origin` | Cloud/Region/Nutzer/Pipeline-Info (siehe 4.6) |
| `timestamp` | Aufzeichnungszeitpunkt (UTC) |
| `message` | menschenlesbare Beschreibung |
| `level` | `INFO`, `WARN`, `ERROR`, `METRICS` (Hochvolumen, nur Delta-Tabelle, nicht UI) |
| `maturity_level` | `STABLE`, `NULL`, `EVOLVING`, `DEPRECATED` — Monitoring/Alerts nicht auf `EVOLVING`/`DEPRECATED` bauen |
| `error` | Fehlerdetails |
| `details` | strukturiert, Format je `event_type` |
| `event_type` | Ereignistyp |

### 4.2 Event-Typen im Überblick

| `event_type` | Beschreibung |
|---|---|
| `create_update` | vollständige Config des gestarteten Updates |
| `user_action` | Nutzeraktionen |
| `runtime_details` | genutzte Runtime |
| `flow_progress` | Flow-Lebenszyklus |
| `update_progress` | Update-Lebenszyklus |
| `flow_definition` | Schema/Query-Plan (DAG-Kanten, Lineage) |
| `dataset_definition` | ein Dataset |
| `sink_definition` | ein Sink |
| `deprecation` | bald/bereits veraltete Features |
| `cluster_resources` | Cluster-Ressourcen (nur klassisches Compute) |
| `autoscale` | Autoscaling (nur klassisches Compute) |
| `planning_information` | inkrementell vs. voll (MV) |
| `hook_progress` | Event-Hook-Status |
| `operation_progress` | Fortschritt (z. B. Auto Loader) |
| `stream_progress` | Streaming-Flow-Fortschritt |
| `behavior_change_in_spark_connect` | erkanntes Verhaltensänderungs-Muster |

### 4.3 Wichtige Details-Typen

- **`flow_progress`:** `status` (`QUEUED`/`STARTING`/`RUNNING`/`COMPLETED`/`FAILED`/`SKIPPED`/`STOPPED`/`IDLE`/`EXCLUDED`), `metrics` (FlowMetrics), `data_quality`.
- **`update_progress`:** `state` (`QUEUED`/`CREATED`/`WAITING_FOR_RESOURCES`/`INITIALIZING`/`RESETTING`/`SETTING_UP_TABLES`/`RUNNING`/`STOPPING`/`COMPLETED`/`FAILED`/`CANCELED`), `cancellation_cause` (`USER_ACTION`/`WORKFLOW_CANCELLATION`).
- **`flow_definition`:** `input_datasets`, `output_dataset`, `output_sink`, `explain_text`, `schema_json`, `schema`, `flow_type` (`COMPLETE`/`CHANGE`/`SNAPSHOT_CHANGE`/`APPEND`/`MATERIALIZED_VIEW`/`VIEW`), `comment`, `spark_conf`, `language`, `once`.
- **`dataset_definition`:** `dataset_type`, `num_flows`, `expectations`.
- **`sink_definition`:** `format`, `options`.
- **`planning_information`:** `technique_information` (Array), `source_table_information`, `target_table_information`.
- **`operation_progress`:** `type` (`AUTO_LOADER_LISTING`/`AUTO_LOADER_BACKFILL`/`CONNECTOR_FETCH`/`CDC_SNAPSHOT`), `status` (`STARTED`/`COMPLETED`/`CANCELED`/`FAILED`/`IN_PROGRESS`), `duration_ms`.

### 4.4 FlowMetrics-Objekt (wichtige Felder)

| Feld | Beschreibung |
|---|---|
| `num_output_rows` | geschriebene Output-Zeilen |
| `num_upserted_rows` / `num_deleted_rows` | upgeserte/gelöschte Output-Zeilen |
| `backlog_bytes` / `backlog_records` / `backlog_files` / `backlog_seconds` | Backlog über alle Quellen |
| `executor_time_ms` / `executor_cpu_time_ms` | Task-Ausführungszeiten |
| `source_metrics` | je Eingabequelle (`source_name`, Backlog-Felder) |

### 4.5 Wichtige Enums für `planning_information`

- **IssueType** (Gründe für Full statt inkrementell — Auswahl): `CDF_UNAVAILABLE` (Aktivierung: `ALTER TABLE ... SET TBLPROPERTIES ('delta.enableChangeDataFeed' = true)`), `DATA_SCHEMA_CHANGED`, `PARTITION_SCHEMA_CHANGED`, `INPUT_NOT_IN_DELTA`, `DATA_FILE_MISSING`, `PLAN_NOT_DETERMINISTIC`, `PLAN_NOT_INCREMENTALIZABLE`, `QUERY_FINGERPRINT_CHANGED`, `CONFIGURATION_CHANGED`, `CHANGE_SET_MISSING`, `EXPECTATIONS_NOT_SUPPORTED`, `TOO_MANY_FILE_ACTIONS`, `INCREMENTAL_PLAN_REJECTED_BY_COST_MODEL`, `ROW_TRACKING_NOT_ENABLED` (Aktivierung: `ALTER TABLE ... SET TBLPROPERTIES ('delta.enableRowTracking' = true)`), `TOO_MANY_PARTITIONS_CHANGED`, `MAP_TYPE_NOT_SUPPORTED`, `TIME_ZONE_CHANGED`, `DATA_HAS_CHANGED`, `PRIOR_TIMESTAMP_MISSING`.
- **MaintenanceType:** `MAINTENANCE_TYPE_COMPLETE_RECOMPUTE`, `MAINTENANCE_TYPE_NO_OP`; inkrementell: `MAINTENANCE_TYPE_PARTITION_OVERWRITE`, `MAINTENANCE_TYPE_ROW_BASED`, `MAINTENANCE_TYPE_APPEND_ONLY`, `MAINTENANCE_TYPE_GROUP_AGGREGATE`, `MAINTENANCE_TYPE_GENERIC_AGGREGATE`, `MAINTENANCE_TYPE_WINDOW_FUNCTION`.

### 4.6 Origin-Objekt (wichtige Felder)

`cloud`, `region`, `org_id`, `pipeline_id`, `pipeline_type` (`WORKSPACE`/`DBSQL`/`MANAGED_INGESTION`/`DATABASE_TABLE_SYNC`/`BRICKSTORE`/`BRICKINDEX`), `pipeline_name`, `cluster_id`, `update_id`, `table_name`, `dataset_name`, `sink_name`, `flow_id` (bleibt gleich bei inkrementellem Update, ändert sich bei Full Refresh/Checkpoint-Reset/Full Recompute), `flow_name`, `batch_id`, `request_id`.

## 5. Query History für Pipeline-Läufe

- Je MV-/Streaming-Table-Refresh erscheint eine `REFRESH`-Anweisung in der Query History (eine je Flow-Ausführung). **Compute**-Filter → nur Pipeline-Compute-Abfragen.
- **Query-History-Seite:** **Compute** → **Pipeline compute** (+ Nutzer/Zeit/Status) → Query anklicken (Dauer, Metriken) → **See query profile** → **Query Source** zur Pipeline-Monitoring-Seite.
- **Pipeline-Monitoring-Seite:** **Performance**-Tab unten.
- **Pipelines Editor:** ebenfalls **Performance**-Tab, ggf. auf gewählte Tabelle beschränkt. Ein Eintrag je Flow-Ausführung (außer mehrere Flows schreiben in dieselbe Tabelle). Bis zu **1.000 Anweisungen** (**View all in query history** für vollständige Liste). Standard sichtbar: Dauer, Lese-/Schreibmetriken; Klick auf `REFRESH` zeigt mehr + Query Profile. Während und nach Lauf verfügbar.
- **Einschränkung:** Provisionierungs-/Warteschlangenzeit nicht verfügbar.

## 6. Event Hooks — Custom Monitoring

**Public Preview.** Benutzerdefinierte Python-Callbacks, ausgeführt bei Event-Log-Persistierung — eigenes Monitoring/Alerting.

### 6.1 Grundprinzip

- Python-Funktion mit genau einem Argument (Event-Dictionary), im Pipeline-Quellcode. Alle Hooks verarbeiten **sämtliche** Ereignisse jedes Updates; bei mehreren Quelldateien gelten sie für die ganze Pipeline. Nicht im Graph sichtbar; funktionieren bei Hive-Metastore- und UC-Pipelines.
- Python einzige unterstützte Sprache — SQL-Pipelines brauchen separate Python-Quelldatei.
- Nur für `maturity_level = STABLE`-Ereignisse ausgelöst.
- **Gotcha:** laufen asynchron zu Updates, aber **synchron zueinander** — nur ein Hook gleichzeitig; unbegrenzt laufender Hook blockiert alle anderen.
- Vor Compute-Beendigung: feste (nicht konfigurierbare) Wartezeit für nachhinkende Hooks — **nicht garantiert**, dass alle Hooks für alle Ereignisse ausgelöst werden.

### 6.2 Event-Hook-Verarbeitung überwachen

Event-Typ `hook_progress` fürs Hook-Monitoring — für `hook_progress`-Ereignisse selbst werden keine Hooks ausgelöst (Vermeidung zirkulärer Abhängigkeiten).

### 6.3 Einen Event Hook definieren

```python
@dp.on_event_hook(max_allowable_consecutive_failures=None)
def user_event_hook(event):
  # Python code defining the event hook
```

- `max_allowable_consecutive_failures`: max. aufeinanderfolgende Fehlschläge vor Deaktivierung (dann keine neuen Events bis Pipeline-Neustart). `>= 0` oder `None` (Standard, unbegrenzt). Fehlschläge/Deaktivierungen als `hook_progress`-Events überwachbar. Funktion: genau ein Parameter (Event-Dict), Rückgabewert ignoriert.

### 6.4 Beispiele

Bestimmte Ereignisse gezielt verarbeiten:

```python
@dp.on_event_hook
def my_event_hook(event):
  if (
    event['event_type'] == 'update_progress' and
    event['details']['update_progress']['state'] == 'STOPPING'
  ):
    print('Received notification that update is stopping: ', event)
```

Alle Ereignisse an Slack senden:

```python
from pyspark import pipelines as dp
import requests

API_TOKEN = dbutils.secrets.get(scope="<secret-scope>", key="<token-key>")

@dp.on_event_hook
def write_events_to_slack(event):
  res = requests.post(
    url='https://slack.com/api/chat.postMessage',
    headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_TOKEN},
    json={'channel': '<channel-id>', 'text': 'Received event:\n' + event}
  )
```

Event Hook nach vier Fehlschlägen deaktivieren:

```python
from pyspark import pipelines as dp

def run_failing_operation():
   raise Exception('Operation has failed')

@dp.on_event_hook(max_allowable_consecutive_failures=3)
def non_reliable_event_hook(event):
  run_failing_operation()
```

Vollständiges Beispiel — Pipeline mit Slack-Event-Hook:

```python
from pyspark import pipelines as dp
import requests

API_TOKEN = dbutils.secrets.get(scope="<secret-scope>", key="<token-key>")
SLACK_POST_MESSAGE_URL = 'https://slack.com/api/chat.postMessage'
DEV_CHANNEL = 'CHANNEL'
SLACK_HTTPS_HEADER_COMMON = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_TOKEN}

@dp.table
def test_dataset():
 return spark.range(5)

@dp.on_event_hook
def write_events_to_slack(event):
  res = requests.post(url=SLACK_POST_MESSAGE_URL, headers=SLACK_HTTPS_HEADER_COMMON, json = {
    'channel': DEV_CHANNEL,
    'text': 'Event hook triggered by event: ' + event['event_type'] + ' event.'
  })
```

## 7. Nach Streaming-Checkpoint-Fehlschlag wiederherstellen

### 7.1 Was ist ein Streaming-Checkpoint?

Persistiert: **Fortschritt** (verarbeitete Quell-Offsets), **Zwischenzustand** (zustandsbehaftete Operationen über Micro-Batches), **Metadaten**. Wichtig für Fehlertoleranz, Exactly-once (mit idempotenten Senken), Zustandsverwaltung.

### 7.2 Pipeline-Checkpoints

- Pipelines abstrahieren Checkpoint-Verwaltung: je in Streaming Table schreibendem Flow ein eigener interner Checkpoint (nicht direkt zugänglich). Relevant bei:
  - **Rewind/Replay:** Daten ab Zeitpunkt neu verarbeiten, Tabellenzustand erhalten — Checkpoint zurücksetzen.
  - **Wiederherstellung nach Fehlschlag/Beschädigung:** drei Ansätze — Full Table Refresh; Full Table Refresh mit Backup+Backfill; Checkpoint zurücksetzen + inkrementell fortsetzen.

### 7.3 Beispiel: Pipeline-Fehlschlag durch Code-Änderung

Szenario: zwei Streaming Flows in SCD-1-Table `customers` — `customers_incremental_flow` (CDC-Feed, dedupliziert, upsertet), `customers_snapshot_flow` (initialer Snapshot, einmalig).

```python
@dp.temporary_view(name="customers_incremental_view")
def query():
    return (
    spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.includeExistingFiles", "true")
        .load(customers_incremental_path)
        .dropDuplicates(["customer_id"])
    )

@dp.temporary_view(name="customers_snapshot_view")
def full_orders_snapshot():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.includeExistingFiles", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(customers_snapshot_path)
        .select("*")
    )

dp.create_streaming_table("customers")

dp.create_auto_cdc_flow(
    flow_name = "customers_incremental_flow",
    target = "customers",
    source = "customers_incremental_view",
    keys = ["customer_id"],
    sequence_by = col("sequenceNum"),
    apply_as_deletes = expr("operation = 'DELETE'"),
    apply_as_truncates = expr("operation = 'TRUNCATE'"),
    except_column_list = ["operation", "sequenceNum"],
    stored_as_scd_type = 1
)
dp.create_auto_cdc_flow(
    flow_name = "customers_snapshot_flow",
    target = "customers",
    source = "customers_snapshot_view",
    keys = ["customer_id"],
    sequence_by = lit(0),
    stored_as_scd_type = 1,
    once = True
)
```

Entfernt man später `dropDuplicates()` (Performance-Optimierung) und deployt erneut, schlägt das Update fehl:

```
Streaming stateful operator name does not match with the operator in state metadata.
This is likely to happen when a user adds/removes/changes stateful operators of existing streaming query.
Stateful operators in the metadata: [(OperatorId: 0 -> OperatorName: dedupe)];
Stateful operators in current batch: []. SQLSTATE: 42K03 SQLSTATE: XXKST
```

- Häufige Auslöser: Hinzufügen/Entfernen zustandsbehafteter Operatoren (`dropDuplicates()`, Aggregationen); Hinzufügen/Entfernen/Kombinieren von Streaming-Quellen bei bestehendem Checkpoint; State-Schema-Änderung zustandsbehafteter Operationen.

### 7.4 Wiederherstellungsoptionen

| Methode | Komplexität | Kosten | Datenverlust | Duplizierung | Initialer Snapshot | Vollständiges Reset |
|---|---|---|---|---|---|---|
| Full Table Refresh | niedrig | mittel | ja (ohne Snapshot/bei gelöschten Rohdateien) | nein (bei Apply-Changes-Ziel) | ja | ja |
| Full Table Refresh + Backup/Backfill | mittel | hoch | nein | nein (bei idempotenten Senken, z. B. Auto CDC) | nein | nein |
| Table-Checkpoint zurücksetzen | mittel-hoch (mittel bei Append-only) | niedrig | nein (sorgfältige Abwägung) | nein (bei idempotenten Writern) | nein | nein |

**Empfehlungen:** Full Table Refresh bei vermeidbarer Reset-Komplexität + möglicher Neuberechnung (erlaubt auch Code-Änderungen). Mit Backup/Backfill, wenn Kosten akzeptabel. Checkpoint zurücksetzen, wenn bestehende Daten unbedingt erhalten + inkrementelle Fortsetzung gewünscht.

### 7.5 Checkpoint zurücksetzen und inkrementell fortsetzen

1. **Pipeline anhalten** (keine aktiven Updates).
2. **Startposition bestimmen** — letzter verarbeiteter Offset/Zeitstempel: Auto Loader `modifiedAfter`, Kafka `startingOffsets`, Delta `startingVersion`.
3. **Code-Änderungen vornehmen** (z. B. `dropDuplicates()` entfernen, `modifiedAfter` setzen):

```python
@dp.temporary_view(name="customers_incremental_view")
def query():
    return (
    spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.includeExistingFiles", "true")
        .option("modifiedAfter", "2025-04-09T06:15:00")
        .load(customers_incremental_path)
        # .dropDuplicates(["customer_id"])
    )
```

- **Gotcha:** falsch gesetzter `modifiedAfter` → Datenverlust oder -duplizierung. Bei Stream-Stream-Join/-Union: Strategie für alle beteiligten Quellen anwenden.

4. **Flow-Namen identifizieren** — vollqualifiziert `catalog.schema.flow_name`. Ohne expliziten `flow_name`: Standard = vollqualifizierter Zieltabellenname.
5. **Checkpoint zurücksetzen** via Pipelines-Updates-API:

```python
import requests
import json

databricks_instance = "<DATABRICKS_URL>"
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
pipeline_id = "<YOUR_PIPELINE_ID>"
flows_to_reset = ["<YOUR_FLOW_NAME>"]
endpoint = f"{databricks_instance}/api/2.0/pipelines/{pipeline_id}/updates"
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
payload = {"reset_checkpoint_selection": flows_to_reset}

response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
if response.status_code == 200:
    print("Pipeline update started successfully.")
else:
    print(f"Error: {response.status_code}, {response.text}")
```

6. **Pipeline ausführen** — verarbeitet neue Daten ab Startposition mit frischem Checkpoint; bestehende Tabellendaten bleiben erhalten.

### 7.6 Best Practices

- Private-Preview-Features nicht produktiv einsetzen.
- Änderungen testen: Test-Pipeline in niedrigerer Umgebung → Fehler reproduzieren → Änderung anwenden → validieren, Go/No-Go → auf Produktion ausrollen.

## 8. Hohe Initialisierungszeiten beheben

### 8.1 Einordnung

- Viele Datasets/Flows → Verwaltungs-Overhead → höhere Initialisierung. Bei getriggerten Pipelines mit Initialisierungsverzögerung > 5 Min: Aufteilung auf mehrere Pipelines empfohlen (selbst bei gemeinsamer Quelle).
- **Gotcha:** getriggerte Pipelines wiederholen Initialisierungsschritte bei **jedem** Trigger; kontinuierliche nur beim Stoppen/Neustarten — dieser Abschnitt betrifft primär getriggerte Pipelines.

### 8.2 Wann eine Aufteilung sinnvoll ist

- `INITIALIZING`/`SETTING_UP_TABLES` dauern > 5 Min und beeinträchtigen Gesamtzeit.
- Driver wird Engpass bei mehr als **30–40 Streaming Tables** in einer Pipeline.
- Getriggerte Pipeline mit vielen Streaming-Table-Flows kann evtl. nicht alle parallelisierbaren Stream-Updates parallel ausführen.

### 8.3 Details zu Performance-Problemen

- **`INITIALIZING`:** Aufbau logischer Pläne (Abhängigkeitsgraph, Update-Reihenfolge).
- **`SETTING_UP_TABLES`:** Schema-Validierung/-Auflösung aller Tabellen; Abhängigkeitsgraph + Ausführungsreihenfolge; Prüfung ob Dataset aktiv/neu; Erstellung Streaming Tables (erstes Update) bzw. temporärer Views/Backup-Tabellen für MVs (jedes Update).
- Verzögerungsgründe: viele Flows mit komplexen Abhängigkeiten; komplexe Transformationen (auch `Auto CDC`); selbst nicht am Update beteiligte Flows verursachen Overhead (z. B. > 700 Flows, davon < 50 je Trigger aktualisiert, müssen dennoch bestimmte Schritte durchlaufen).
- **Driver-Engpässe:** Driver entscheidet je Tabelle, welche Cluster-Instanz welchen Flow bearbeitet — > 30–40 Streaming Tables → CPU-Engpass. Speicherprobleme häufiger bei 30+ parallelen Flows (keine feste Schwelle). Getriggerte Pipelines verarbeiten ggf. nur Teilmenge parallel.

### 8.4 Trade-offs beim Aufteilen

- Innerhalb einer Pipeline: automatische Abhängigkeitsverwaltung. Bei mehreren Pipelines: selbst verwalten (z. B. Job mit Task-Abhängigkeiten — `pipeline_C` erst nach `pipeline_A` **und** `pipeline_B`).
- **Concurrency:** Flow-Laufzeiten stark unterschiedlich — vor Aufteilung Abfragezeiten betrachten, kurze Abfragen gruppieren.

### 8.5 Aufteilung planen

Beispiel: Quell-Pipeline mit 25 Tabellen (1 Root + 8 Segmente à 2 Views) → zwei Pipelines: eine mit Root + 4 Segmenten, andere mit übrigen 4 Segmenten (abhängig von erster).

### 8.6 Pipeline ohne Full Refresh aufteilen

Neue Pipelines erstellen, Tabellen zur Lastbalance verschieben, ohne Full Refresh auszulösen.

**Einschränkungen:** Pipelines müssen in UC sein; Quell-/Ziel-Pipeline im selben Workspace (keine Workspace-Grenzen-Verschiebung); Ziel-Pipeline muss vor Verschiebung erstellt und mindestens einmal gelaufen sein (auch bei Fehlschlag); keine Verschiebung von Default- zu Legacy-Publishing-Mode.

**Stand:** 2026-09-14.
