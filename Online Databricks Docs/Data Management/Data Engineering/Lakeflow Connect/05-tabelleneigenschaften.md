# Delta-Tabelleneigenschaften setzen

Diese Seite erklärt, wie sich Delta-Lake-Tabelleneigenschaften für Ziel-Streaming-Tabellen konfigurieren lassen, die von Managed-Ingestion-Pipelines erzeugt werden. Statt `ALTER TABLE ... SET TBLPROPERTIES` direkt zu verwenden, werden die Eigenschaften über die `ingestion_definition` der Pipeline gesetzt.

## Konfigurationsebenen

| Ebene | Verhalten |
| --- | --- |
| Pipeline | `table_properties` in der pipeline-weiten `table_configuration` setzen, um die Eigenschaften auf alle Tabellen und Schemas anzuwenden |
| Tabelle oder Schema | `table_properties` in der `table_configuration` einer einzelnen Tabelle oder eines Schemas setzen, um die Pipeline-Einstellungen zu überschreiben |

## Beispiel: Type Widening pipeline-weit aktivieren, für eine Tabelle überschreiben (YAML)

```python
resources:
  pipelines:
    pipeline_cdc:
      name: <pipeline-name>
      catalog: <destination-catalog>
      schema: <destination-schema>
      ingestion_definition:
        ingestion_gateway_id: <gateway-pipeline-id>
        table_configuration:
          table_properties:
            delta.enableTypeWidening: 'true'
            delta.enableDeletionVectors: 'true'
        objects:
          - table:
              source_schema: <source-schema>
              source_table: users_1
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
              table_configuration:
                table_properties:
                  delta.enableTypeWidening: 'false'
          - table:
              source_schema: <source-schema>
              source_table: calendar_test
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
```

## Dasselbe Beispiel (Python)

```python
pipeline_spec = """{
  "ingestion_definition": {
    "ingestion_gateway_id": "<gateway-pipeline-id>",
    "table_configuration": {
      "table_properties": {
        "delta.enableTypeWidening": "true",
        "delta.enableDeletionVectors": "true"
      }
    },
    "objects": [
      {
        "table": {
          "source_schema": "<source-schema>",
          "source_table": "users_1",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>",
          "table_configuration": {
            "table_properties": {
              "delta.enableTypeWidening": "false"
            }
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

## Dasselbe Beispiel (JSON – Databricks CLI)

```python
{
  "ingestion_definition": {
    "ingestion_gateway_id": "<gateway-pipeline-id>",
    "table_configuration": {
      "table_properties": {
        "delta.enableTypeWidening": "true",
        "delta.enableDeletionVectors": "true"
      }
    },
    "objects": [
      {
        "table": {
          "source_schema": "<source-schema>",
          "source_table": "users_1",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>",
          "table_configuration": {
            "table_properties": {
              "delta.enableTypeWidening": "false"
            }
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

## Vererbung und Überschreiben

"Auf Pipeline-Ebene gesetzte Tabelleneigenschaften werden von allen Tabellen und Schemas der Pipeline geerbt." Beim Überschreiben auf Tabellen- oder Schema-Ebene müssen die Pipeline-weiten Einstellungen explizit wiederholt werden, damit sie erhalten bleiben – nicht wiederholte Eigenschaften werden nicht automatisch übernommen.

## Einschränkungen

- Das Setzen von Tabelleneigenschaften wird nur für Datenbank-Konnektoren mit Change Data Capture (CDC) unterstützt; SaaS- und Query-basierte Konnektoren werden nicht unterstützt.
- Das Entfernen einer Eigenschaft aus der Pipeline-Spezifikation macht das zugrunde liegende Tabellenfeature nicht automatisch rückgängig.
- Beim Zurücksetzen bestimmter Eigenschaften kann ein vollständiger Refresh der betroffenen Tabellen erforderlich sein.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/table-properties  
**Stand:** 2026-08-07
