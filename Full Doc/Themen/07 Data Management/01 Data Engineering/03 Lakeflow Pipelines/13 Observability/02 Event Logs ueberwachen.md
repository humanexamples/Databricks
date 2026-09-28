# Pipeline-Event-Log überwachen

Das Pipeline-Event-Log enthält alle Informationen zu einer Pipeline — Audit-Logs, Datenqualitätsprüfungen, Pipeline-Fortschritt und Data Lineage. Dieses Dokument zeigt, wie das Event Log direkt abgefragt wird, mit zahlreichen praktischen Beispiel-Queries. Jede Aussage und jede SQL-Query wurde per `WebFetch` gegen die Azure-Spiegelseite `learn.microsoft.com/en-us/azure/databricks/ldp/monitor-event-logs` verifiziert (dort wortwörtlich reproduzierbar; inhaltlich deckungsgleich mit `docs.databricks.com/aws/en/ldp/monitor-event-logs`). Für die vollständige Feldreferenz siehe `Event-Log-Schema.md`.

## Abschnittsübersicht

1. [Grundlagen: Zugriffswege](#grundlagen)
2. [Das Event Log abfragen](#abfragen)
3. [Basis-Abfragebeispiele](#basis-beispiele)
4. [Erweiterte Abfragebeispiele](#erweiterte-beispiele)
5. [Pipelines auditieren](#audit)
6. [Nutzeraktionen im Event Log abfragen](#nutzeraktionen)
7. [Laufzeitinformationen](#laufzeitinfo)
8. [Quellen](#quellen)

---

## <a id="grundlagen">1. Grundlagen: Zugriffswege</a>

Event-Log-Einträge lassen sich auf drei Wegen einsehen: über die Pipeline-Monitoring-UI, über die Pipelines-REST-API, oder durch direktes Abfragen des Event Logs. Dieses Dokument konzentriert sich auf das direkte Abfragen.

Zusätzlich lassen sich benutzerdefinierte Aktionen definieren, die beim Protokollieren von Ereignissen ausgeführt werden, z. B. das Versenden von Alerts, über Event Hooks (siehe `Event Hooks.md`).

**Wichtig:** Das Event Log oder der übergeordnete Katalog/Schema, in dem es veröffentlicht ist, sollte **nicht gelöscht** werden — das kann dazu führen, dass die Pipeline bei zukünftigen Läufen nicht mehr aktualisiert werden kann.

---

## <a id="abfragen">2. Das Event Log abfragen</a>

Dieser Abschnitt beschreibt das Standardverhalten für Pipelines, die mit Unity Catalog und dem Default Publishing Mode konfiguriert sind.

- Für Unity-Catalog-Pipelines im Legacy Publishing Mode siehe `Live Schema.md`.
- Für Hive-Metastore-Pipelines siehe `Hive Metastore.md`.

Standardmäßig schreibt eine Pipeline das Event Log in eine versteckte Delta-Tabelle im Standardkatalog und -schema der Pipeline. Obwohl versteckt, bleibt die Tabelle für hinreichend berechtigte Nutzer abfragbar. Standardmäßig kann nur der **Run-As-User** der Pipeline das Event-Log-Tabelle abfragen.

Abfrage als Run-As-User über die Pipeline-ID:

```sql
SELECT * FROM event_log(<pipelineId>);
```

Der Name des versteckten Event Logs folgt standardmäßig dem Muster `event_log_{pipeline_id}`, wobei Bindestriche der System-UUID durch Unterstriche ersetzt werden. Die Event-Log-Tabelle erscheint in `system.information_schema.tables`, ist aber im Catalog Explorer oder anderen Workspace-UI-Seiten nicht sichtbar — der Zugriff erfolgt ausschließlich über die Funktion `event_log()`.

Das Event Log lässt sich über die **Advanced settings** der Pipeline veröffentlichen. Dabei werden Name sowie optional Katalog und Schema angegeben:

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

Der Event-Log-Speicherort dient zugleich als Schema-Speicherort für alle Auto-Loader-Abfragen der Pipeline. Databricks empfiehlt, vor einer Änderung der Berechtigungen zunächst eine View über die Event-Log-Tabelle zu erstellen, da manche Compute-Einstellungen bei direkter Freigabe der Tabelle Zugriff auf Schema-Metadaten ermöglichen könnten:

```sql
CREATE VIEW event_log_raw
AS SELECT * FROM <catalog_name>.<schema_name>.<event_log_table_name>;
```

`<catalog_name>.<schema_name>.<event_log_table_name>` ist durch den vollständig qualifizierten Namen der eigenen Event-Log-Tabelle zu ersetzen; wurde das Event Log nicht veröffentlicht, wird stattdessen `event_log(<pipelineId>)` verwendet.

In Unity Catalog unterstützen Views auch Streaming-Abfragen:

```python
df = spark.readStream.table("event_log_raw")
```

Alle folgenden Beispiele setzen voraus, dass die View `event_log_raw` wie oben beschrieben erstellt wurde.

---

## <a id="basis-beispiele">3. Basis-Abfragebeispiele</a>

### Pipeline-Updates überwachen (vorherige Updates abfragen)

Zeigt Update-ID, Status, Startzeit, Abschlusszeit und Dauer:

```sql
with last_status_per_update AS (
    SELECT
        origin.pipeline_id AS pipeline_id,
        origin.pipeline_name AS pipeline_name,
        origin.update_id AS pipeline_update_id,
        FROM_JSON(details, 'struct<update_progress: struct<state: string>>').update_progress.state AS last_update_state,
        timestamp,
        ROW_NUMBER() OVER (
            PARTITION BY origin.update_id
            ORDER BY timestamp DESC
        ) AS rn
    FROM event_log_raw
    WHERE event_type = 'update_progress'
    QUALIFY rn = 1
),
update_durations AS (
    SELECT
        origin.pipeline_id AS pipeline_id,
        origin.pipeline_name AS pipeline_name,
        origin.update_id AS pipeline_update_id,
        -- Capture the start of the update
        MIN(CASE WHEN event_type = 'create_update' THEN timestamp END) AS start_time,

        -- Capture the end of the update based on terminal states or current timestamp (relevant for continuous mode pipelines)
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
    s.pipeline_id,
    s.pipeline_name,
    s.pipeline_update_id,
    d.start_time,
    d.end_time,
    CASE
        WHEN d.start_time IS NOT NULL AND d.end_time IS NOT NULL THEN
            ROUND(TIMESTAMPDIFF(MILLISECOND, d.start_time, d.end_time) / 1000)
        ELSE NULL
    END AS duration_seconds,
    s.last_update_state AS pipeline_update_status
FROM last_status_per_update s
JOIN update_durations d
  ON s.pipeline_id = d.pipeline_id
 AND s.pipeline_update_id = d.pipeline_update_id
ORDER BY d.start_time DESC;
```

### Probleme beim inkrementellen Refresh von Materialized Views debuggen

Zeigt für alle Flows des jüngsten Updates, ob sie inkrementell aktualisiert wurden, sowie weitere Planungsinformationen:

```sql
WITH latest_update AS (
  SELECT
    origin.pipeline_id,
    origin.update_id AS latest_update_id
  FROM event_log_raw AS origin
  WHERE origin.event_type = 'create_update'
  ORDER BY timestamp DESC
  -- LIMIT 1 -- remove if you want to get all of the update_ids
),
parsed_planning AS (
  SELECT
    origin.pipeline_name,
    origin.pipeline_id,
    origin.flow_name,
    lu.latest_update_id,
    from_json(
      details:planning_information,
      'struct<
        technique_information: array<struct<
          maintenance_type: string,
          is_chosen: boolean,
          is_applicable: boolean,
          cost: double,
          incrementalization_issues: array<struct<
            issue_type: string,
            prevent_incrementalization: boolean,
            operator_name: string,
            plan_not_incrementalizable_sub_type: string,
            expression_name: string,
            plan_not_deterministic_sub_type: string
          >>
        >>
      >'
    ) AS parsed
  FROM event_log_raw AS origin
  JOIN latest_update lu
    ON origin.update_id = lu.latest_update_id
  WHERE details:planning_information IS NOT NULL
),
chosen_technique AS (
  SELECT
    pipeline_name,
    pipeline_id,
    flow_name,
    latest_update_id,
    FILTER(parsed.technique_information, t -> t.is_chosen = true)[0] AS chosen_technique,
    parsed.technique_information AS planning_information
  FROM parsed_planning
)
SELECT
  pipeline_name,
  pipeline_id,
  flow_name,
  latest_update_id,
  chosen_technique.maintenance_type,
  chosen_technique,
  planning_information
FROM chosen_technique
ORDER BY latest_update_id DESC;
```

### Kosten eines Pipeline-Updates abfragen

Zeigt DBU-Verbrauch sowie den Run-As-Nutzer:

```sql
SELECT
  sku_name,
  billing_origin_product,
  usage_date,
  collect_set(identity_metadata.run_as) as users,
  SUM(usage_quantity) AS `DBUs`
FROM
  system.billing.usage
WHERE
  usage_metadata.dlt_pipeline_id = :pipeline_id
GROUP BY
  ALL;
```

---

## <a id="erweiterte-beispiele">4. Erweiterte Abfragebeispiele</a>

### Metriken für alle Flows einer Pipeline abfragen

Zeigt Flow-Name, Update-Dauer, Datenqualitätsmetriken sowie Informationen zu verarbeiteten Zeilen (Output, gelöscht, upserted, verworfen):

```sql
WITH flow_progress_raw AS (
  SELECT
    origin.pipeline_name         AS pipeline_name,
    origin.pipeline_id           AS pipeline_id,
    origin.flow_name             AS table_name,
    origin.update_id             AS update_id,
    timestamp,
    details:flow_progress.status AS status,
    TRY_CAST(details:flow_progress.metrics.num_output_rows AS BIGINT)      AS num_output_rows,
    TRY_CAST(details:flow_progress.metrics.num_upserted_rows AS BIGINT)    AS num_upserted_rows,
    TRY_CAST(details:flow_progress.metrics.num_deleted_rows AS BIGINT)     AS num_deleted_rows,
    TRY_CAST(details:flow_progress.data_quality.dropped_records AS BIGINT) AS num_expectation_dropped_rows,
    FROM_JSON(
      details:flow_progress.data_quality.expectations,
      SCHEMA_OF_JSON("[{'name':'str', 'dataset':'str', 'passed_records':42, 'failed_records':42}]")
    ) AS expectations_array

  FROM event_log_raw
  WHERE event_type = 'flow_progress'
    AND origin.flow_name IS NOT NULL
    AND origin.flow_name != 'pipelines.flowTimeMetrics.missingFlowName'
),

aggregated_flows AS (
  SELECT
    pipeline_name,
    pipeline_id,
    update_id,
    table_name,
    MIN(CASE WHEN status IN ('STARTING', 'RUNNING', 'COMPLETED') THEN timestamp END) AS start_timestamp,
    MAX(CASE WHEN status IN ('STARTING', 'RUNNING', 'COMPLETED') THEN timestamp END) AS end_timestamp,
    MAX_BY(status, timestamp) FILTER (
      WHERE status IN ('COMPLETED', 'FAILED', 'CANCELLED', 'EXCLUDED', 'SKIPPED', 'STOPPED', 'IDLE')
    ) AS final_status,
    SUM(COALESCE(num_output_rows, 0))              AS total_output_records,
    SUM(COALESCE(num_upserted_rows, 0))            AS total_upserted_records,
    SUM(COALESCE(num_deleted_rows, 0))             AS total_deleted_records,
    MAX(COALESCE(num_expectation_dropped_rows, 0)) AS total_expectation_dropped_records,
    MAX(expectations_array)                        AS total_expectations

  FROM flow_progress_raw
  GROUP BY pipeline_name, pipeline_id, update_id, table_name
)
SELECT
  af.pipeline_name,
  af.pipeline_id,
  af.update_id,
  af.table_name,
  af.start_timestamp,
  af.end_timestamp,
  af.final_status,
  CASE
    WHEN af.start_timestamp IS NOT NULL AND af.end_timestamp IS NOT NULL THEN
      ROUND(TIMESTAMPDIFF(MILLISECOND, af.start_timestamp, af.end_timestamp) / 1000)
    ELSE NULL
  END AS duration_seconds,

  af.total_output_records,
  af.total_upserted_records,
  af.total_deleted_records,
  af.total_expectation_dropped_records,
  af.total_expectations
FROM aggregated_flows af
-- Optional: filter to latest update only
WHERE af.update_id = (
  SELECT update_id
  FROM aggregated_flows
  ORDER BY end_timestamp DESC
  LIMIT 1
)
ORDER BY af.end_timestamp DESC, af.pipeline_name, af.pipeline_id, af.update_id, af.table_name;
```

### Datenqualitäts- bzw. Expectations-Metriken abfragen

Sind auf Datasets Expectations definiert, werden die Metriken für bestandene/fehlgeschlagene Datensätze im Objekt `details:flow_progress.data_quality.expectations` gespeichert; die Anzahl verworfener Datensätze im Objekt `details:flow_progress.data_quality`. Ereignisse mit Datenqualitätsinformationen haben den Event-Typ `flow_progress`. Datenqualitätsmetriken sind für manche Datasets ggf. nicht verfügbar (siehe Expectation-Limitationen).

Verfügbare Metriken:

| Metrik | Beschreibung |
|---|---|
| `dropped_records` | Anzahl der Datensätze, die verworfen wurden, weil sie eine oder mehrere Expectations nicht erfüllten. |
| `passed_records` | Anzahl der Datensätze, die die Expectation-Kriterien erfüllten. |
| `failed_records` | Anzahl der Datensätze, die die Expectation-Kriterien nicht erfüllten. |

```sql
WITH latest_update AS (
  SELECT
    origin.pipeline_id,
    origin.update_id AS latest_update_id
  FROM event_log_raw AS origin
  WHERE origin.event_type = 'create_update'
  ORDER BY timestamp DESC
  LIMIT 1 -- remove if you want to get all of the update_ids
),
SELECT
  row_expectations.dataset as dataset,
  row_expectations.name as expectation,
  SUM(row_expectations.passed_records) as passing_records,
  SUM(row_expectations.failed_records) as failing_records
FROM
  (
    SELECT
      explode(
        from_json(
          details:flow_progress:data_quality:expectations,
          "array<struct<name: string, dataset: string, passed_records: int, failed_records: int>>"
        )
      ) row_expectations
    FROM
      event_log_raw,
      latest_update
    WHERE
      event_type = 'flow_progress'
      AND origin.update_id = latest_update.id
  )
GROUP BY
  row_expectations.dataset,
  row_expectations.name;
```

### Lineage-Informationen abfragen

Ereignisse mit Lineage-Informationen haben den Event-Typ `flow_definition`. Das Objekt `details:flow_definition` enthält `output_dataset` und `input_datasets` für jede Beziehung im Graphen.

```sql
with latest_update as (
  SELECT origin.update_id as id
    FROM event_log_raw
    WHERE event_type = 'create_update'
    ORDER BY timestamp DESC
    limit 1 -- remove if you want all of the update_ids
)
SELECT
  details:flow_definition.output_dataset as flow_name,
  details:flow_definition.input_datasets as input_flow_names,
  details:flow_definition.flow_type as flow_type,
  details:flow_definition.schema, -- the schema of the flow
  details:flow_definition -- overall flow_definition object
FROM event_log_raw inner join latest_update on origin.update_id = latest_update.id
WHERE details:flow_definition IS NOT NULL
ORDER BY timestamp;
```

### Cloud-Datei-Ingestion mit Auto Loader überwachen

Pipelines erzeugen Ereignisse, wenn Auto Loader Dateien verarbeitet. Für Auto-Loader-Ereignisse ist der `event_type` gleich `operation_progress`, und `details:operation_progress:type` ist entweder `AUTO_LOADER_LISTING` oder `AUTO_LOADER_BACKFILL`. Das Objekt `details:operation_progress` enthält zusätzlich `status`, `duration_ms`, `auto_loader_details:source_path` und `auto_loader_details:num_files_listed`.

```sql
with latest_update as (
  SELECT origin.update_id as id
    FROM event_log_raw
    WHERE event_type = 'create_update'
    ORDER BY timestamp DESC
    limit 1 -- remove if you want all of the update_ids
)
SELECT
  timestamp,
  details:operation_progress.status,
  details:operation_progress.type,
  details:operation_progress:auto_loader_details
FROM
  event_log_raw,latest_update
WHERE
  event_type like 'operation_progress'
  AND
  origin.update_id = latest_update.id
  AND
  details:operation_progress.type in ('AUTO_LOADER_LISTING', 'AUTO_LOADER_BACKFILL');
```

### Daten-Backlog zur Optimierung der Streaming-Dauer überwachen

Jede Pipeline verfolgt die Menge der im Backlog vorhandenen Daten im Objekt `details:flow_progress.metrics.backlog_bytes`. Ereignisse mit Backlog-Metriken haben den Event-Typ `flow_progress`.

```sql
with latest_update as (
  SELECT origin.update_id as id
    FROM event_log_raw
    WHERE event_type = 'create_update'
    ORDER BY timestamp DESC
    limit 1 -- remove if you want all of the update_ids
)
SELECT
  timestamp,
  Double(details :flow_progress.metrics.backlog_bytes) as backlog
FROM
  event_log_raw,
  latest_update
WHERE
  event_type ='flow_progress'
  AND
  origin.update_id = latest_update.id;
```

**Hinweis:** Backlog-Metriken sind je nach Datenquellentyp und Databricks-Runtime-Version der Pipeline ggf. nicht verfügbar.

### Autoscaling-Ereignisse für klassisches Compute überwachen

Für Pipelines mit klassischem Compute (also nicht Serverless) erfasst das Event Log Cluster-Resizes, wenn Enhanced Autoscaling aktiviert ist. Ereignisse mit Enhanced-Autoscaling-Informationen haben den Event-Typ `autoscale`; die Resize-Anfrage-Informationen liegen im Objekt `details:autoscale`.

```sql
with latest_update as (
  SELECT origin.update_id as id
    FROM event_log_raw
    WHERE event_type = 'create_update'
    ORDER BY timestamp DESC
    limit 1 -- remove if you want all of the update_ids
)
SELECT
  timestamp,
  Double(
    case
      when details :autoscale.status = 'RESIZING' then details :autoscale.requested_num_executors
      else null
    end
  ) as starting_num_executors,
  Double(
    case
      when details :autoscale.status = 'SUCCEEDED' then details :autoscale.requested_num_executors
      else null
    end
  ) as succeeded_num_executors,
  Double(
    case
      when details :autoscale.status = 'PARTIALLY_SUCCEEDED' then details :autoscale.requested_num_executors
      else null
    end
  ) as partially_succeeded_num_executors,
  Double(
    case
      when details :autoscale.status = 'FAILED' then details :autoscale.requested_num_executors
      else null
    end
  ) as failed_num_executors
FROM
  event_log_raw,
  latest_update
WHERE
  event_type = 'autoscale'
  AND
  origin.update_id = latest_update.id
```

### Compute-Ressourcennutzung für klassisches Compute überwachen

`cluster_resources`-Ereignisse liefern Metriken zur Anzahl der Task-Slots im Cluster, deren Auslastung und der Anzahl wartender Tasks. Bei aktiviertem Enhanced Autoscaling enthalten `cluster_resources`-Ereignisse zusätzlich Metriken des Autoscaling-Algorithmus, u. a. `latest_requested_num_executors` und `optimal_num_executors`, sowie Statuswerte wie `CLUSTER_AT_DESIRED_SIZE`, `SCALE_UP_IN_PROGRESS_WAITING_FOR_EXECUTORS` und `BLOCKED_FROM_SCALING_DOWN_BY_CONFIGURATION`.

```sql
with latest_update as (
  SELECT origin.update_id as id
    FROM event_log_raw
    WHERE event_type = 'create_update'
    ORDER BY timestamp DESC
    limit 1 -- remove if you want all of the update_ids
)
SELECT
  timestamp,
  Double(details:cluster_resources.avg_num_queued_tasks) as queue_size,
  Double(details:cluster_resources.avg_task_slot_utilization) as utilization,
  Double(details:cluster_resources.num_executors) as current_executors,
  Double(details:cluster_resources.latest_requested_num_executors) as latest_requested_num_executors,
  Double(details:cluster_resources.optimal_num_executors) as optimal_num_executors,
  details :cluster_resources.state as autoscaling_state
FROM
  event_log_raw,
  latest_update
WHERE
  event_type = 'cluster_resources'
  AND
  origin.update_id = latest_update.id;
```

### Pipeline-Streaming-Metriken überwachen

`stream_progress`-Ereignisse (siehe `Event-Log-Schema.md`) ähneln stark den `StreamingQueryListener`-Metriken von Structured Streaming, mit folgenden Unterschieden:

- Die Metriken `numInputRows`, `inputRowsPerSecond` und `processedRowsPerSecond` existieren in `StreamingQueryListener`, jedoch **nicht** in `stream_progress`.
- Für Kafka- und Kinesis-Streams können die Felder `startOffset`, `endOffset` und `latestOffset` zu groß werden und daher abgeschnitten (truncated) werden. Für jedes dieser Felder gibt es dann ein zusätzliches boolesches `...Truncated`-Feld (`startOffsetTruncated`, `endOffsetTruncated`, `latestOffsetTruncated`).

```sql
SELECT
  parse_json(get_json_object(details, '$.stream_progress.progress_json')) AS stream_progress_json
FROM event_log_raw
WHERE event_type = 'stream_progress';
```

Beispiel eines solchen Ereignisses als JSON:

```json
{
  "id": "abcd1234-ef56-7890-abcd-ef1234abcd56",
  "sequence": {
    "control_plane_seq_no": 1234567890123456
  },
  "origin": {
    "cloud": "<cloud>",
    "region": "<region>",
    "org_id": 0123456789012345,
    "pipeline_id": "abcdef12-abcd-3456-7890-abcd1234ef56",
    "pipeline_type": "WORKSPACE",
    "pipeline_name": "<pipeline name>",
    "update_id": "1234abcd-ef56-7890-abcd-ef1234abcd56",
    "request_id": "1234abcd-ef56-7890-abcd-ef1234abcd56"
  },
  "timestamp": "2025-06-17T03:18:14.018Z",
  "message": "Completed a streaming update of 'flow_name'.",
  "level": "INFO",
  "details": {
    "stream_progress": {
      "progress": {
        "id": "abcdef12-abcd-3456-7890-abcd1234ef56",
        "runId": "1234abcd-ef56-7890-abcd-ef1234abcd56",
        "name": "silverTransformFromBronze",
        "timestamp": "2022-11-01T18:21:29.500Z",
        "batchId": 4,
        "durationMs": {
          "latestOffset": 62,
          "triggerExecution": 62
        },
        "stateOperators": [],
        "sources": [
          {
            "description": "DeltaSource[dbfs:/path/to/table]",
            "startOffset": {
              "sourceVersion": 1,
              "reservoirId": "abcdef12-abcd-3456-7890-abcd1234ef56",
              "reservoirVersion": 3216,
              "index": 3214,
              "isStartingVersion": true
            },
            "endOffset": {
              "sourceVersion": 1,
              "reservoirId": "abcdef12-abcd-3456-7890-abcd1234ef56",
              "reservoirVersion": 3216,
              "index": 3214,
              "isStartingVersion": true
            },
            "latestOffset": null,
            "metrics": {
              "numBytesOutstanding": "0",
              "numFilesOutstanding": "0"
            }
          }
        ],
        "sink": {
          "description": "DeltaSink[dbfs:/path/to/sink]",
          "numOutputRows": -1
        }
      }
    }
  },
  "event_type": "stream_progress",
  "maturity_level": "EVOLVING"
}
```

Beispiel unabgeschnittener Datensätze in einer Kafka-Quelle (die `...Truncated`-Felder stehen auf `false`):

```json
{
  "description": "KafkaV2[Subscribe[KAFKA_TOPIC_NAME_INPUT_A]]",
  "startOffsetTruncated": false,
  "startOffset": {
    "KAFKA_TOPIC_NAME_INPUT_A": {
      "0": 349706380
    }
  },
  "endOffsetTruncated": false,
  "endOffset": {
    "KAFKA_TOPIC_NAME_INPUT_A": {
      "0": 349706672
    }
  },
  "latestOffsetTruncated": false,
  "latestOffset": {
    "KAFKA_TOPIC_NAME_INPUT_A": {
      "0": 349706672
    }
  },
  "numInputRows": 292,
  "inputRowsPerSecond": 13.65826278123392,
  "processedRowsPerSecond": 14.479817514628582,
  "metrics": {
    "avgOffsetsBehindLatest": "0.0",
    "estimatedTotalBytesBehindLatest": "0.0",
    "maxOffsetsBehindLatest": "0",
    "minOffsetsBehindLatest": "0"
  }
}
```

---

## <a id="audit">5. Pipelines auditieren</a>

Event-Log-Einträge und weitere Databricks-Audit-Logs zusammen ergeben ein vollständiges Bild davon, wie Daten in einer Pipeline aktualisiert werden.

Lakeflow-Pipelines nutzen die Credentials des Pipeline-Owners, um Updates auszuführen. Die genutzten Credentials lassen sich durch Ändern des Pipeline-Owners anpassen. Das Audit-Log erfasst den Nutzer für Aktionen an der Pipeline, einschließlich Pipeline-Erstellung, Konfigurationsänderungen und ausgelöste Updates.

---

## <a id="nutzeraktionen">6. Nutzeraktionen im Event Log abfragen</a>

Ereignisse mit Informationen zu Nutzeraktionen haben den Event-Typ `user_action`; Details liegen im Objekt `user_action` im Feld `details`.

```sql
SELECT timestamp, details:user_action:action, details:user_action:user_name FROM event_log_raw WHERE event_type = 'user_action'
```

Beispielergebnis:

| `timestamp` | `action` | `user_name` |
|---|---|---|
| 2021-05-20T19:36:03.517+0000 | `START` | `user@company.com` |
| 2021-05-20T19:35:59.913+0000 | `CREATE` | `user@company.com` |
| 2021-05-27T00:35:51.971+0000 | `START` | `user@company.com` |

---

## <a id="laufzeitinfo">7. Laufzeitinformationen</a>

Laufzeitinformationen zu einem Pipeline-Update, z. B. die Databricks-Runtime-Version:

```sql
SELECT origin.update_id, details:runtime_details:runtime_version:dbr_version FROM event_log_raw WHERE event_type = 'runtime_details'
```

Beispielergebnis:

| `update_id` | `dbr_version` |
|---|---|
| `1234abcd-ef56-7890-abcd-ef1234abcd56` | 18.0 |

---

## <a id="quellen">8. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/monitor-event-logs
- https://learn.microsoft.com/en-us/azure/databricks/ldp/monitor-event-logs (primäre Quelle für die wörtliche SQL-Reproduktion)

**Stand:** 2026-08-19
