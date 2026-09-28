# Zieltabelle benennen

Standardmäßig erhalten Zieltabellen denselben Namen wie ihre Quelltabellen. Bei Namenskonflikten im selben Zielschema lässt sich ein benutzerdefinierter Name vergeben – Managed-Ingestion-Connectors unterstützen keine doppelten Zieltabellennamen im selben Schema.

## Möglichkeiten zur Benennung

**Über die UI:** Auf der Seite **Source** im Daten-Ingestion-Assistenten einen benutzerdefinierten Namen im Feld **Destination table** eingeben.

**Über die API:** Der Parameter `destination_table` ermöglicht die Benennung über drei Wege: Declarative Automation Bundles (YAML), Databricks-Notebooks (Python) und Databricks CLI (JSON).

## Beispiel (Google Analytics)

```python
# YAML
resources:
  pipelines:
    pipeline_ga4:
      name: <pipeline-name>
      catalog: <target-catalog>
      schema: <target-schema>
      ingestion_definition:
        connection_name: <connection-name>
        objects:
        - table:
              source_url: <project-id>
              source_schema: <property-name>
              destination_catalog: <target-catalog>
              destination_schema: <target-schema>
              destination_table: <custom-target-table-name>
```

```python
pipeline_spec = """{
  "name": "<pipeline-name>",
  "ingestion_definition": {
    "connection_name": "<connection-name>",
    "objects": [
      {
        "table": {
          "source_catalog": "<project-id>",
          "source_schema": "<property-name>",
          "source_table": "<source-table>",
          "destination_catalog": "<target-catalog>",
          "destination_schema": "<target-schema>",
          "destination_table": "<custom-target-table-name>",
        }
      }
    ]
  }
}"""
```

```python
// JSON (Databricks CLI)
{
  "resources": {
    "pipelines": {
      "pipeline_ga4": {
        "name": "<pipeline-name>",
        "catalog": "<target-catalog>",
        "schema": "<target-schema>",
        "ingestion_definition": {
          "connection_name": "<connection-name>",
          "objects": [
            {
              "table": {
                "source_url": "<project-id>",
                "source_schema": "<property-name>",
                "destination_catalog": "<destination-catalog>",
                "destination_schema": "<destination-schema>",
                "destination_table": "<custom-destination-table-name>"
              }
            }
          ]
        }
      }
    }
  }
}
```

Weitere Beispiele in der Originaldokumentation zeigen dasselbe Muster für Salesforce (tabellenbasierte Ingestion) und Workday (reportbasierte Ingestion) – jeweils mit `destination_table` neben Katalog- und Schema-Parametern.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/table-rename  
**Stand:** 2026-08-07
