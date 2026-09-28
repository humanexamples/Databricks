# Ingestion-Gateway-Fortschritt mit Event-Logs überwachen

Databricks stellt Event-Logs bereit, um den Fortschritt eines Ingestion-Gateways in Echtzeit zu überwachen. Diese Logs liefern Metriken pro Tabelle sowohl für die Snapshot- als auch für die Change-Data-Capture-Phase (CDC) und helfen, Pipeline-Health zu verfolgen und Probleme zu identifizieren.

## Wichtige Fähigkeiten

Progress Events ermöglichen es:

- "nachzuverfolgen, wie viele Zeilen und Bytes pro Tabelle aufgenommen wurden, ohne auf den Abschluss der Pipeline zu warten"
- den Fortschritt in Prozent für initiale Ladevorgänge (Snapshots) zu überwachen
- die verbleibende Zeit bis zum Abschluss pro Tabelle zu schätzen
- die End-to-End-CDC-Discovery-Latenz pro Tabelle zu messen
- Liveness-Signale zu erhalten, auch wenn keine Datenänderungen auftreten
- Alerts auf Basis strukturierter Event-Daten zu erstellen

## Event-Typen

Das Gateway sendet standardmäßig alle 5 Minuten zwei primäre Event-Typen:

- **`flow_progress`-Events** melden Zeilen- und Byte-Zähler als Deltas (die nach jeder Emission zurückgesetzt werden) für Snapshot- und CDC-Flows. CDC-Flows enthalten zusätzlich Latenzmetriken.
- **`operation_progress`-Events** melden kumulative Snapshot-Fortschrittswerte in Prozent sowie die geschätzte Abschlusszeit.

## Zugriff auf Progress Events

1. Zum Gateway im Databricks-Workspace navigieren
2. Den Tab "Event log" öffnen
3. Die Event-Log-Tabelle direkt per SQL abfragen

### Beispielabfrage für `flow_progress`-Events

```sql
%sql
SELECT
  timestamp,
  CONCAT(origin.catalog_name, '.', origin.schema_name, '.', origin.dataset_name) AS table_name,
  details:flow_progress:metrics:num_upserted_rows::bigint AS rows_upserted,
  COALESCE(details:flow_progress:metrics:num_deleted_rows::bigint, 0) AS rows_deleted,
  details:flow_progress:metrics:num_output_bytes::bigint AS output_bytes,
  CASE
    WHEN origin.flow_name LIKE '%_snapshot_flow' THEN 'snapshot'
    WHEN origin.flow_name LIKE '%_cdc_flow' THEN 'cdc'
    ELSE 'unknown'
  END AS ingestion_phase
FROM event_log('<pipeline-id>')
WHERE event_type = 'flow_progress'
  AND level = 'METRICS'
  AND origin.pipeline_type = 'INGESTION_GATEWAY'
ORDER BY timestamp DESC
```

### Beispielabfrage für `operation_progress`-Events

```sql
%sql
SELECT
  timestamp,
  origin.flow_name AS flow_name,
  details:operation_progress:status::string AS status,
  details:operation_progress:progress_percent::double AS progress_pct
FROM event_log('<pipeline-id>')
WHERE event_type = 'operation_progress'
  AND level = 'METRICS'
  AND origin.pipeline_type = 'INGESTION_GATEWAY'
ORDER BY timestamp DESC
```

## Struktur der Events

### Beispiel: Snapshot Flow Progress

```python
{
  "id": "01234567-89ab-cdef-0123-456789abcdef",
  "timestamp": "2025-10-14T13:33:14.175Z",
  "level": "METRICS",
  "event_type": "flow_progress",
  "origin": {
    "pipeline_type": "INGESTION_GATEWAY",
    "pipeline_name": "MyPipeline",
    "dataset_name": "customers",
    "catalog_name": "main",
    "schema_name": "sales",
    "flow_name": "main.sales.customers_snapshot_flow",
    "ingestion_source_type": "SQLSERVER"
  },
  "message": "Completed a streaming update of 'main.sales.customers_snapshot_flow'.",
  "details": {
    "flow_progress": {
      "status": "RUNNING",
      "metrics": {
        "num_upserted_rows": 7512704,
        "num_deleted_rows": null,
        "num_output_bytes": 458752000
      }
    }
  },
  "maturity_level": "STABLE"
}
```

### Beispiel: CDC Flow Progress

```python
{
  "id": "01234567-89ab-cdef-0123-456789abcdef",
  "timestamp": "2025-10-14T13:33:57.426Z",
  "level": "METRICS",
  "event_type": "flow_progress",
  "origin": {
    "pipeline_type": "INGESTION_GATEWAY",
    "pipeline_name": "MyPipeline",
    "dataset_name": "customers",
    "catalog_name": "main",
    "schema_name": "sales",
    "flow_name": "main.sales.customers_cdc_flow",
    "ingestion_source_type": "SQLSERVER"
  },
  "message": "Completed a streaming update of 'main.sales.customers_cdc_flow'.",
  "details": {
    "flow_progress": {
      "status": "RUNNING",
      "metrics": {
        "num_upserted_rows": 25,
        "num_deleted_rows": 3,
        "num_output_bytes": 18432
      },
      "streaming_metrics": {
        "discovery_latency_ms": 12450,
        "batch_processing_time_ms": 8100,
        "event_time": {
          "max": "2025-10-14T13:33:45.000Z"
        }
      }
    }
  },
  "maturity_level": "STABLE"
}
```

### Beispiel: Operation Progress

```python
{
  "id": "01234567-89ab-cdef-0123-456789abcdef",
  "timestamp": "2025-10-14T13:33:14.175Z",
  "level": "METRICS",
  "event_type": "operation_progress",
  "origin": {
    "pipeline_type": "INGESTION_GATEWAY",
    "pipeline_name": "MyPipeline",
    "dataset_name": "customers",
    "catalog_name": "main",
    "schema_name": "sales",
    "flow_name": "main.sales.customers_snapshot_flow",
    "ingestion_source_type": "SQLSERVER"
  },
  "message": "Snapshot in progress for 'main.sales.customers'.",
  "details": {
    "operation_progress": {
      "type": "CDC_SNAPSHOT",
      "status": "IN_PROGRESS",
      "duration_ms": 3600000,
      "progress_percent": 65.5,
      "estimated_completion_ms": 1885000,
      "cdc_snapshot": {
        "target_table_name": "main.sales.customers",
        "snapshot_timestamp": 1737542400000,
        "snapshot_reason": "NEW_TABLE"
      }
    }
  },
  "maturity_level": "STABLE"
}
```

## Konfiguration

Progress Events sind für neue Gateways standardmäßig aktiviert.

**Events aktivieren/deaktivieren:**
```json
"configuration": {
    "pipelines.gateway.progressEventsEnabled": "true"
}
```

**Emissionsfrequenz anpassen** (Standard 300 Sekunden / 5 Minuten, gültiger Bereich 30–3600 Sekunden):
```json
"configuration": {
    "pipelines.gateway.progressEventEmitFrequencySeconds": "300"
}
```

### Beispiel: Gateway-Konfiguration (Python)

```python
gateway_pipeline_spec = {
   "pipeline_type": "INGESTION_GATEWAY",
   "name": "my_gateway_pipeline",
   "catalog": "main",
   "target": "my_schema",
   "continuous": True,
   "configuration": {
      "pipelines.gateway.progressEventsEnabled": "true",
      "pipelines.gateway.progressEventEmitFrequencySeconds": "300"
   },
   # ... rest of pipeline spec
}
```

## Metrik-Typen

- **Delta-Metriken** (`num_upserted_rows`, `num_deleted_rows`, `num_output_bytes`) stellen Änderungen seit dem letzten Event dar und werden nach jeder Emission auf null zurückgesetzt.
- **Kumulative Metriken** (`progress_percent`) akkumulieren über die Lebensdauer eines Snapshots von 0,0 bis 100,0.
- **Zeitpunktbezogene Metriken** (`discovery_latency_ms`, `batch_processing_time_ms`, `event_time.max`, `estimated_completion_ms`) spiegeln den Zustand zum Zeitpunkt der Emission wider.

## Interpretation der CDC-Latenz

| Muster | Bedeutung |
| --- | --- |
| Beide Werte klein | CDC läuft und ist aktuell |
| Hohe Discovery-Latenz, niedrige Batch-Zeit | Verzögerung auf Quellseite |
| Beide Werte hoch | Verzögerung auf Gateway-Seite |

## Troubleshooting

- **Keine Progress-Events sichtbar:** prüfen, ob `progressEventsEnabled` auf true steht, ein volles Intervall abwarten, sicherstellen, dass die Pipeline läuft, und den Filter `level = 'METRICS'` einschließen.
- **Falsche Emissionsfrequenz:** die Einstellung `progressEventEmitFrequencySeconds` prüfen und anpassen.
- **Metriken werden nach Neustart zurückgesetzt:** dies ist beabsichtigt; Metriken existieren nur im Arbeitsspeicher und beginnen nach einem Neustart neu.
- **Fehlende Metriken für einzelne Tabellen:** sicherstellen, dass Tabellen nicht gefiltert werden, CDC in der Quelle aktiviert ist und die Tabellen in der Gateway-Konfiguration enthalten sind.
- **Fehlende `estimated_completion_ms` oder `streaming_metrics`:** erfordert ein Gateway-Image ab Mai 2026; die im Original bereitgestellte Diagnoseabfrage ausführen.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/gateway-event-logs  
**Stand:** 2026-08-07
