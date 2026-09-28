# Zieltabellen vollständig neu laden (Full Refresh)

Ein Full Refresh einer Ingestion-Pipeline löscht Daten und Zustand der Zieltabellen und verarbeitet anschließend alle Datensätze der Quelle erneut. Der Vorgang kann für alle oder nur ausgewählte Tabellen ausgeführt werden.

## Zugriffsmöglichkeiten

| Interface | Methode |
| --- | --- |
| Lakehouse UI | Pipeline-Update manuell auslösen |
| Pipelines API | `POST /api/2.0/pipelines/{pipeline_id}/updates` |
| Databricks CLI | `databricks pipelines start-update` |

**Wichtiger Hinweis:** Pipeline-Updates können während der Initialisierungs- oder Tabellen-Reset-Phase fehlschlagen. Lakeflow Connect führt automatische Wiederholungsversuche durch, manuelles Eingreifen kann jedoch nötig sein. "Falls auch manuelle Wiederholungen fehlschlagen, ein Support-Ticket erstellen."

## Full-Refresh-Verhalten bei CDC-Datenbank-Konnektoren

Bei Datenbank-Konnektoren folgt der Refresh-Prozess einem optimierten Ablauf:

1. **Snapshot-Erstellung**: Das Ingestion-Gateway beginnt sofort mit der Erstellung eines neuen Quelltabellen-Snapshots.
2. **Fortlaufende Verfügbarkeit**: Die Zieltabelle behält während der Snapshot-Verarbeitung ihre vorhandenen Daten.
3. **Atomarer Refresh**: Nach Abschluss des Snapshots werden alle Snapshot-Daten und die zwischenzeitlich angesammelten CDC-Datensätze in einer einzigen Operation angewendet.

Dies reduziert Ausfallzeiten und verhindert `PENDING_RESET`-Fehler sowie Timeouts.

**Achtung:** Gateway-Snapshots können nicht fortgesetzt werden. Ein Pipeline-Update während der Snapshot-Erstellung bricht den aktuellen Snapshot ab und startet einen neuen.

## Full-Refresh-Fenster (Datenbank-Konnektoren)

Ein Full-Refresh-Fenster legt fest, wann Snapshot-Operationen stattfinden dürfen.

| Parameter | Typ | Pflicht | Details |
| --- | --- | --- | --- |
| `start_hour` | Integer | Ja | Startstunde des Fensters (0–23, 24-Stunden-Format) |
| `days_of_week` | Array | Nein | Aktive Tage (MONDAY–SUNDAY); Standard ist jeder Tag |
| `time_zone_id` | String | Nein | Zeitzonen-ID; Standard ist UTC |

### Full-Refresh-Fenster konfigurieren (YAML)

```python
resources:
  pipelines:
    gateway:
      name: <gateway-name>
      gateway_definition:
        connection_id: <connection-id>
        gateway_storage_catalog: <destination-catalog>
        gateway_storage_schema: <destination-schema>
        gateway_storage_name: <destination-schema>
      target: <destination-schema>
      catalog: <destination-catalog>
    pipeline_sqlserver:
      name: <pipeline-name>
      catalog: <destination-catalog>
      schema: <destination-schema>
      ingestion_definition:
        ingestion_gateway_id: <gateway-id>
        objects:
          - table:
              source_schema: <source-schema>
              source_table: <source-table>
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
        full_refresh_window:
          start_hour: 20
          days_of_week:
            - MONDAY
            - TUESDAY
          time_zone_id: 'America/Los_Angeles'
```

### Full-Refresh-Fenster konfigurieren (Python)

```python
gateway_pipeline_spec = {
  "pipeline_type": "INGESTION_GATEWAY",
  "name": "<gateway-name>",
  "catalog": "<destination-catalog>",
  "target": "<destination-schema>",
  "gateway_definition": {
    "connection_id": "<connection-id>",
    "gateway_storage_catalog": "<destination-catalog>",
    "gateway_storage_schema": "<destination-schema>",
    "gateway_storage_name": "<destination-schema>"
  }
}

ingestion_pipeline_spec = {
  "pipeline_type": "MANAGED_INGESTION",
  "name": "<pipeline-name>",
  "catalog": "<destination-catalog>",
  "schema": "<destination-schema>",
  "ingestion_definition": {
    "ingestion_gateway_id": "<gateway-pipeline-id>",
    "source_type": "SQLSERVER",
    "objects": [
      {
        "table": {
          "source_schema": "<source-schema>",
          "source_table": "<source-table>",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>"
        }
      }
    ],
    "full_refresh_window": {
      "start_hour": 20,
      "days_of_week": ["MONDAY", "TUESDAY"],
      "time_zone_id": "America/Los_Angeles"
    }
  }
}
```

## Auto Full Refresh Policy

Auto Full Refresh löst automatisch aus, wenn die Pipeline auf nicht unterstützte DDL-Operationen trifft:

- Tabellen-Truncate
- inkompatible Schema-Änderungen
- Umbenennung von Spalten
- Hinzufügen von Spalten mit Default-Werten

**Konfigurationsparameter:**

| Parameter | Typ | Standard | Beschreibung |
| --- | --- | --- | --- |
| `enabled` | Boolean | false | aktiviert Auto Full Refresh |
| `min_interval_hours` | Integer | 24 | minimaler Wartezeitraum zwischen Full Refreshes |

Die Konfiguration kann erfolgen auf:

- Pipeline-Ebene: `ingestion_definition.table_configuration.auto_full_refresh_policy`
- Tabellen-Ebene: `ingestion_definition.objects[].table.table_configuration.auto_full_refresh_policy`

Tabellen-Ebene-Einstellungen überschreiben die Pipeline-Konfiguration.

### Auto Full Refresh Policy auf Pipeline-Ebene (YAML)

```python
resources:
  pipelines:
    gateway:
      name: <gateway-name>
      gateway_definition:
        connection_id: <connection-id>
        gateway_storage_catalog: <destination-catalog>
        gateway_storage_schema: <destination-schema>
        gateway_storage_name: <destination-schema>
      target: <destination-schema>
      catalog: <destination-catalog>
    pipeline_sqlserver:
      name: <pipeline-name>
      catalog: <destination-catalog>
      schema: <destination-schema>
      ingestion_definition:
        ingestion_gateway_id: <gateway-id>
        objects:
          - table:
              source_schema: <source-schema>
              source_table: <source-table>
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
        table_configuration:
          auto_full_refresh_policy:
            enabled: true
            min_interval_hours: 24
```

### Auto Full Refresh Policy auf Pipeline-Ebene (Python)

```python
gateway_pipeline_spec = {
  "pipeline_type": "INGESTION_GATEWAY",
  "name": "<gateway-name>",
  "catalog": "<destination-catalog>",
  "target": "<destination-schema>",
  "gateway_definition": {
    "connection_id": "<connection-id>",
    "gateway_storage_catalog": "<destination-catalog>",
    "gateway_storage_schema": "<destination-schema>",
    "gateway_storage_name": "<destination-schema>"
  }
}

ingestion_pipeline_spec = {
  "pipeline_type": "MANAGED_INGESTION",
  "name": "<pipeline-name>",
  "catalog": "<destination-catalog>",
  "schema": "<destination-schema>",
  "ingestion_definition": {
    "ingestion_gateway_id": "<gateway-pipeline-id>",
    "source_type": "SQLSERVER",
    "objects": [
      {
        "table": {
          "source_schema": "<source-schema>",
          "source_table": "<source-table>",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>"
        }
      }
    ],
    "table_configuration": {
      "auto_full_refresh_policy": {
        "enabled": True,
        "min_interval_hours": 24
      }
    }
  }
}
```

### Auto Full Refresh Policy pro Tabelle, mit Überschreiben (YAML)

In diesem Beispiel nutzt `table_1` die Pipeline-weite Policy (aktiviert), während `table_2` sie auf Tabellen-Ebene überschreibt (deaktiviert).

```python
resources:
  pipelines:
    gateway:
      name: <gateway-name>
      gateway_definition:
        connection_id: <connection-id>
        gateway_storage_catalog: <destination-catalog>
        gateway_storage_schema: <destination-schema>
        gateway_storage_name: <destination-schema>
      target: <destination-schema>
      catalog: <destination-catalog>
    pipeline_sqlserver:
      name: <pipeline-name>
      catalog: <destination-catalog>
      schema: <destination-schema>
      ingestion_definition:
        ingestion_gateway_id: <gateway-id>
        objects:
          - table:
              source_schema: <source-schema>
              source_table: table_1
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
          - table:
              source_schema: <source-schema>
              source_table: table_2
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
              table_configuration:
                auto_full_refresh_policy:
                  enabled: false
                  min_interval_hours: 24
        table_configuration:
          auto_full_refresh_policy:
            enabled: true
            min_interval_hours: 24
```

### Auto Full Refresh Policy pro Tabelle, mit Überschreiben (Python)

```python
gateway_pipeline_spec = {
  "pipeline_type": "INGESTION_GATEWAY",
  "name": "<gateway-name>",
  "catalog": "<destination-catalog>",
  "target": "<destination-schema>",
  "gateway_definition": {
    "connection_id": "<connection-id>",
    "gateway_storage_catalog": "<destination-catalog>",
    "gateway_storage_schema": "<destination-schema>",
    "gateway_storage_name": "<destination-schema>"
  }
}

ingestion_pipeline_spec = {
  "pipeline_type": "MANAGED_INGESTION",
  "name": "<pipeline-name>",
  "catalog": "<destination-catalog>",
  "schema": "<destination-schema>",
  "ingestion_definition": {
    "ingestion_gateway_id": "<gateway-pipeline-id>",
    "source_type": "SQLSERVER",
    "objects": [
      {
        "table": {
          "source_schema": "<source-schema>",
          "source_table": "table_1",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>"
        }
      },
      {
        "table": {
          "source_schema": "<source-schema>",
          "source_table": "table_2",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>",
          "table_configuration": {
            "auto_full_refresh_policy": {
              "enabled": False,
              "min_interval_hours": 24
            }
          }
        }
      }
    ],
    "table_configuration": {
      "auto_full_refresh_policy": {
        "enabled": True,
        "min_interval_hours": 24
      }
    }
  }
}
```

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/full-refresh  
**Stand:** 2026-08-07
