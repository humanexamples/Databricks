# Spalten für die Ingestion auswählen

Lakeflow Connect erlaubt die gezielte Steuerung, welche Spalten aus Quelltabellen aufgenommen werden. Standardmäßig werden alle aktuellen und zukünftigen Spalten der angegebenen Tabellen aufgenommen; dieses Verhalten lässt sich über Table-Configuration-Eigenschaften anpassen.

## Konfigurationseigenschaften

| Property | Beschreibung |
| --- | --- |
| `include_columns` | Legt fest, welche Spalten aufgenommen werden. Zukünftig hinzugefügte Spalten der Quelle werden automatisch ausgeschlossen, außer sie werden der Liste hinzugefügt. |
| `exclude_columns` | Legt fest, welche Spalten ausgeschlossen werden. Zukünftig hinzugefügte Spalten der Quelle werden automatisch eingeschlossen. |

Das Feature gilt für SaaS-Konnektoren, Datenbank-Konnektoren und Query-basierte Konnektoren.

## Beispiel: Google Analytics (YAML – Declarative Automation Bundles)

```python
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
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
              table_configuration:
                include_columns:
                  - <column_a>
                  - <column_b>
                  - <column_c>
```

## Beispiel: Google Analytics (Python – Notebook)

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
          "table_configuration": {
            "include_columns": ["<column_a>", "<column_b>", "<column_c>"]
          }
        }
      }
    ]
  }
}"""
```

## Beispiel: Google Analytics (JSON – Databricks CLI)

```python
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
                "table_configuration": {
                  "include_columns": ["<column_a>", "<column_b>", "<column_c>"]
                }
              }
            }
          ]
        }
      }
    }
  }
}
```

## Beispiel: Salesforce (YAML)

```python
resources:
  pipelines:
    pipeline_sfdc:
      name: <pipeline-name>
      catalog: <target-catalog>
      schema: <target-schema>
      ingestion_definition:
        connection_name: <connection-name>
        objects:
          - table:
              source_schema: <source-schema>
              source_table: <source-table>
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
              table_configuration:
                include_columns:
                  - <column_a>
                  - <column_b>
                  - <column_c>
```

## Beispiel: Salesforce (Python)

```python
pipeline_spec = """{
  "name": "<pipeline-name>",
  "ingestion_definition": {
    "connection_name": "<connection-name>",
    "objects": [
      {
        "table": {
          "source_catalog": "<source-catalog>",
          "source_schema": "<source-schema>",
          "source_table": "<source-table>",
          "destination_catalog": "<target-catalog>",
          "destination_schema": "<target-schema>",
          "table_configuration": {
            "include_columns": ["<column_a>", "<column_b>", "<column_c>"]
          }
        }
      }
    ]
  }
}"""
```

## Beispiel: Salesforce (JSON)

```python
{
  "resources": {
    "pipelines": {
      "pipeline_sfdc": {
        "name": "<pipeline-name>",
        "catalog": "<target-catalog>",
        "schema": "<target-schema>",
        "ingestion_definition": {
          "connection_name": "<connection-name>",
          "objects": [
            {
              "table": {
                "source_schema": "<source-schema>",
                "source_table": "<source-table>",
                "destination_catalog": "<destination-catalog>",
                "destination_schema": "<destination-schema>",
                "table_configuration": {
                  "include_columns": ["<column_a>", "<column_b>", "<column_c>"]
                }
              }
            }
          ]
        }
      }
    }
  }
}
```

## Beispiel: Workday (YAML) – Spaltenauswahl auf Report-Ebene

```python
resources:
  pipelines:
    pipeline_workday:
      name: <pipeline-name>
      catalog: <target-catalog>
      schema: <target-schema>
      ingestion_definition:
        connection_name: <connection-name>
        objects:
          - report:
              source_url: <report-url>
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
              table_configuration:
                include_columns:
                  - <column_a>
                  - <column_b>
                  - <column_c>
```

## Beispiel: Workday (Python)

```python
pipeline_spec = """{
  "name": "<pipeline-name>",
  "ingestion_definition": {
    "connection_name": "<connection-name>",
    "objects": [
      {
        "report": {
          "source_url": "<report-url>",
          "destination_catalog": "<target-catalog>",
          "destination_schema": "<target-schema>",
          "table_configuration": {
            "include_columns": ["<column_a>", "<column_b>", "<column_c>"]
          }
        }
      }
    ]
  }
}"""
```

## Beispiel: Workday (JSON)

```python
{
  "resources": {
    "pipelines": {
      "pipeline_workday": {
        "name": "<pipeline-name>",
        "catalog": "<target-catalog>",
        "schema": "<target-schema>",
        "ingestion_definition": {
          "connection_name": "<connection-name>",
          "objects": [
            {
              "report": {
                "source_url": "<report-url>",
                "destination_catalog": "<destination-catalog>",
                "destination_schema": "<destination-schema>",
                "table_configuration": {
                  "include_columns": ["<column_a>", "<column_b>", "<column_c>"]
                }
              }
            }
          ]
        }
      }
    }
  }
}
```

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/column-selection  
**Stand:** 2026-08-07
