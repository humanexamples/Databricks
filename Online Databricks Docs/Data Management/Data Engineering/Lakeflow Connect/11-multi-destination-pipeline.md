# Multi-Destination-Pipelines erstellen

Managed-Ingestion-Connectors in Lakeflow Connect können Daten aus einer einzigen Pipeline heraus in mehrere Zielkataloge und -schemata schreiben. Wichtige Einschränkung: Managed Connectors unterstützen keine doppelten Tabellennamen im selben Zielschema – in diesem Fall muss für eine der Tabellen ein abweichender Name vergeben werden.

## Anwendungsfälle

**Zwei Objekte in unterschiedliche Schemata:** Zwei separate Objekte werden mit verschiedenen Connectors (z. B. Google Analytics, MySQL, Salesforce, SQL Server, Workday) in unterschiedliche Zielschemata geladen.

**Ein Objekt mehrfach:** Ein einzelnes Objekt wird dreimal in unterschiedliche Ziele geladen; für die dritte Instanz ist ein benutzerdefinierter `destination_table`-Name nötig, um Konflikte im selben Schema zu vermeiden.

## Beispiel: Zwei Objekte in unterschiedliche Schemata (Salesforce)

```python
# YAML
resources:
  pipelines:
    pipeline_sfdc:
      name: <pipeline-name>
      catalog: <target-catalog-1>
      schema: <target-schema-1>
      ingestion_definition:
        connection_name: <connection-name>
        objects:
          - table:
              source_schema: <source-schema-1>
              source_table: <source-table-1>
              destination_catalog: <target-catalog-1>
              destination_schema: <target-schema-1>
          - table:
              source_schema: <source-schema-2>
              source_table: <source-table-2>
              destination_catalog: <target-catalog-2>
              destination_schema: <target-schema-2>
```

```python
pipeline_spec = """{
  "name": "<pipeline-name>",
  "ingestion_definition": {
    "connection_name": "<connection-name>",
    "objects": [
      {
        "table": {
          "source_schema": "<source-schema-1>",
          "source_table": "<source-table-1>",
          "destination_catalog": "<target-catalog-1>",
          "destination_schema": "<target-schema-1>",
        },
        "table": {
          "source_schema": "<source-schema-2>",
          "source_table": "<source-table-2>",
          "destination_catalog": "<target-catalog-2>",
          "destination_schema": "<target-schema-2>",
        }
      }
    ]
  }}"""
```

```python
// JSON (Databricks CLI)
{
  "resources": {
    "pipelines": {
      "pipeline_sfdc": {
        "name": "<pipeline-name>",
        "catalog": "<target-catalog-1>",
        "schema": "<target-schema-1>",
        "ingestion_definition": {
          "connection_name": "<connection-name>",
          "objects": [
            {
              "table": {
                "source_schema": "<source-schema-1>",
                "source_table": "<source-table-1>",
                "destination_catalog": "<target-catalog-1>",
                "destination_schema": "<target-schema-1>"
              },
              "table": {
                "source_schema": "<source-schema-2>",
                "source_table": "<source-table-2>",
                "destination_catalog": "<target-catalog-2>",
                "destination_schema": "<target-schema-2>"
              }
            }
          ]
        }
      }
    }
  }
}
```

## Implementierungsoptionen

Beispiele stehen in drei Formaten zur Verfügung: Declarative Automation Bundles (YAML), Databricks-Notebooks (Python) und Databricks CLI (JSON). Jede Pipeline-Definition umfasst Verbindungsdetails (`connection_name` bzw. `connection_id`), Quellangaben (Schema, Tabelle oder Report-URL), Zielzuordnungen (`destination_catalog`, `destination_schema`, `destination_table`) sowie ein `objects`-Array mit mehreren Tabellen-/Report-Definitionen.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/multi-destination-pipeline  
**Stand:** 2026-08-07
