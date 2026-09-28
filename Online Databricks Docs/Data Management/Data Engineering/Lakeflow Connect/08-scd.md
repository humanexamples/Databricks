# History Tracking aktivieren (SCD Typ 2)

History Tracking bzw. Slowly Changing Dimensions (SCD) bestimmt, wie Datenänderungen über die Zeit verwaltet werden. "History Tracking ausschalten (SCD Typ 1), um veraltete Datensätze zu überschreiben, sobald sie in der Quelle aktualisiert oder gelöscht werden. History Tracking einschalten (SCD Typ 2), um eine Historie dieser Änderungen zu führen."

Hinweis: "Das Löschen einer Tabelle oder Spalte in der Quelle löscht diese Daten nicht im Ziel, selbst wenn SCD Typ 1 gewählt ist."

## Verhalten von History Tracking

Bei deaktiviertem SCD Typ 1 ersetzen Updates bestehende Zeilen vollständig. Bei aktiviertem SCD Typ 2 "behält das System die alte Zeile und fügt das Update als neue Zeile hinzu. Die alte Zeile wird als inaktiv markiert, damit erkennbar ist, welche Zeile aktuell ist."

## History Tracking in der UI aktivieren

Auf der "Source"-Seite des Data-Ingestion-Wizards im Dropdown-Menü "History tracking" den Wert "On" auswählen.

## History Tracking über die API aktivieren

Konfiguration über:

- `SCD_TYPE_1`: History Tracking aus
- `SCD_TYPE_2`: History Tracking an

### Google Analytics (YAML)

```python
resources:
  pipelines:
    pipeline_ga4:
      name: <pipeline-name>
      catalog: <destination-catalog>
      schema: <destination-schema>
      ingestion_definition:
        connection_name: <connection-name>
        objects:
          - table:
              source_url: <project-id>
              source_schema: <property-name>
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
              table_configuration:
                scd_type: SCD_TYPE_2
```

### Google Analytics (Python)

```python
pipeline_spec = """{
  "name": "<pipeline-name>",
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
            "scd_type": "SCD_TYPE_2",
          }
        }
      }
    ]
  }
}"""
```

### Google Analytics (JSON)

```python
{
  "resources": {
    "pipelines": {
      "pipeline_ga4": {
        "name": "<pipeline-name>",
        "catalog": "<destination-catalog>",
        "schema": "<destination-schema>",
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
                  "scd_type": "SCD_TYPE_2"
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

### Salesforce (YAML)

```python
resources:
  pipelines:
    pipeline_sfdc:
      name: <pipeline-name>
      catalog: <destination-catalog>
      schema: <destination-schema>
      ingestion_definition:
        connection_name: <connection-name>
        objects:
          - table:
              source_schema: <source-schema>
              source_table: <source-table>
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
              table_configuration:
                scd_type: SCD_TYPE_2
```

### Salesforce (Python)

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
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>",
          "table_configuration": {
            "scd_type": "SCD_TYPE_2",
          }
        }
      }
    ]
  }
}"""
```

### Salesforce (JSON)

```python
{
  "resources": {
    "pipelines": {
      "pipeline_sfdc": {
        "name": "<pipeline-name>",
        "catalog": "<destination-catalog>",
        "schema": "<destination-schema>",
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
                  "scd_type": "SCD_TYPE_2"
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

### SQL Server (YAML)

Unterstützte Sequenzspalten-Typen sind Timestamp, Date, Integer, Long und String.

```python
resources:
  pipelines:
    pipeline_sqlserver:
      name: <pipeline-name>
      catalog: <destination-catalog>
      schema: <destination-schema>
      ingestion_definition:
        connection_name: <connection-name>
        objects:
          - table:
              source_catalog: <source-catalog>
              source_schema: <source-schema>
              source_table: <source-table>
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
              table_configuration:
                scd_type: SCD_TYPE_2
                sequence_by: <sequence-column>
```

### SQL Server (Python)

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
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>",
          "table_configuration": {
            "scd_type": "SCD_TYPE_2",
            "sequence_by": "<version-number>"
          }
        }
      }
    ]
  }
}"""
```

### SQL Server (JSON)

```python
{
  "resources": {
    "pipelines": {
      "pipeline_sqlserver": {
        "name": "<pipeline-name>",
        "catalog": "<destination-catalog>",
        "schema": "<destination-schema>",
        "ingestion_definition": {
          "connection_name": "<connection-name>",
          "objects": [
            {
              "table": {
                "source_catalog": "<source-catalog>",
                "source_schema": "<source-schema>",
                "source_table": "<source-table>",
                "destination_catalog": "<destination-catalog>",
                "destination_schema": "<destination-schema>",
                "table_configuration": {
                  "scd_type": "SCD_TYPE_2",
                  "sequence_by": "<version-number>"
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

### Workday Reports (YAML)

```python
resources:
  pipelines:
    pipeline_workday:
      name: <pipeline-name>
      catalog: <destination-catalog>
      schema: <destination-schema>
      ingestion_definition:
        connection_name: <connection-name>
        objects:
          - report:
              source_url: <report-url>
              destination_catalog: <destination-catalog>
              destination_schema: <destination-schema>
              table_configuration:
                scd_type: SCD_TYPE_2
```

### Workday Reports (Python)

```python
pipeline_spec = """{
  "name": "<pipeline-name>",
  "ingestion_definition": {
    "connection_name": "<connection-name>",
    "objects": [
      {
        "report": {
          "source_url": "<report-url>",
          "destination_catalog": "<destination-catalog>",
          "destination_schema": "<destination-schema>",
          "table_configuration": {
            "scd_type": "SCD_TYPE_2",
          }
        }
      }
    ]
  }
}"""
```

### Workday Reports (JSON)

```python
{
  "resources": {
    "pipelines": {
      "pipeline_workday": {
        "name": "<pipeline-name>",
        "catalog": "<destination-catalog>",
        "schema": "<destination-schema>",
        "ingestion_definition": {
          "connection_name": "<connection-name>",
          "objects": [
            {
              "report": {
                "source_url": "<report-url>",
                "destination_catalog": "<destination-catalog>",
                "destination_schema": "<destination-schema>",
                "table_configuration": {
                  "scd_type": "SCD_TYPE_2"
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

## Einschränkungen

"Ein Full Refresh ersetzt die gesamte Tabelle. Dabei werden alle vorherigen Zeilenversionen entfernt. Die Historie wird ab dem Zeitpunkt des Refreshs neu aufgezeichnet."

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/scd  
**Stand:** 2026-08-07
