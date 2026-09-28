# Liquid Clustering für Managed-Ingestion-Pipelines

Liquid Clustering optimiert das Datenlayout von Tabellen anhand von Clustering-Spalten und verbessert so die Abfrageperformance. Diese Funktion gilt für Streaming-Tabellen, die von Managed-Ingestion-Pipelines erzeugt werden.

## Konfigurationsmöglichkeiten

| Property | Ebene | Beschreibung |
| --- | --- | --- |
| `enable_auto_clustering` | Pipeline | Bei `true` wird automatisches Liquid Clustering für alle Tabellen der Pipeline aktiviert. Databricks wählt und pflegt die Clustering-Keys automatisch. |
| `clustering_columns` | Tabelle | Legt eine explizite Liste von Spalten fest, nach denen eine bestimmte Zieltabelle geclustert wird. Wird innerhalb der Tabelleneinstellungen konfiguriert. |

## Voraussetzungen

- Automatisches Clustering benötigt Databricks Runtime 15.4 LTS oder höher, da die intelligente Key-Auswahl auf Metadaten aufbaut, die erst in dieser Version eingeführt wurden.
- Tabellen mit Clustering können ab Databricks Runtime 13.3 LTS und neueren Versionen gelesen werden, die dieses Feature unterstützen.

## Konfigurationsbeispiel

Das folgende Beispiel aktiviert automatisches Clustering pipeline-weit und legt gleichzeitig explizite `clustering_columns` für die Tabelle `users_1` fest:

```python
# YAML (Databricks Asset / Declarative Automation Bundle)
resources:
  pipelines:
    pipeline_cdc:
      name: <pipeline-name>
      catalog: <destination-catalog>
      schema: <destination-schema>
      ingestion_definition:
        ingestion_gateway_id: <gateway-pipeline-id>
        table_configuration:
          enable_auto_clustering: true
        objects:
          - table:
              source_schema: <source-schema>
              source_table: users_1
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
              table_configuration:
                clustering_columns:
                  - user_id
                  - country
          - table:
              source_schema: <source-schema>
              source_table: calendar_test
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
```

```python
pipeline_spec = """{
  "ingestion_definition": {
    "ingestion_gateway_id": "<gateway-pipeline-id>",
    "table_configuration": {
      "enable_auto_clustering": true
    },
    "objects": [
      {
        "table": {
          "source_schema": "<source-schema>",
          "source_table": "users_1",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>",
          "table_configuration": {
            "clustering_columns": ["user_id", "country"]
          }
        }
      },
      {
        "table": {
          "source_schema": "<source-schema>",
          "source_table": "calendar_test",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>"
        }
      }
    ]
  }
}"""
```

```python
// JSON (Databricks CLI)
{
  "ingestion_definition": {
    "ingestion_gateway_id": "<gateway-pipeline-id>",
    "table_configuration": {
      "enable_auto_clustering": true
    },
    "objects": [
      {
        "table": {
          "source_schema": "<source-schema>",
          "source_table": "users_1",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>",
          "table_configuration": {
            "clustering_columns": ["user_id", "country"]
          }
        }
      },
      {
        "table": {
          "source_schema": "<source-schema>",
          "source_table": "calendar_test",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>"
        }
      }
    ]
  }
}
```

## Einschränkungen

- Liquid Clustering für Managed-Ingestion-Pipelines wird nur bei Datenbank-Connectors unterstützt, die Change Data Capture (CDC) verwenden.
- Direkte `ALTER TABLE`-Befehle funktionieren nicht auf Zieltabellen – die Konfiguration erfolgt stattdessen über die Pipeline-Einstellungen.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/clustering  
**Stand:** 2026-08-07
