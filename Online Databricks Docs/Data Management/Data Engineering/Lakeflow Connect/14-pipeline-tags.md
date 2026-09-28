# Tags für Managed-Ingestion-Pipelines

Pipeline-Tagging (Public Preview) ist für SaaS-, Datenbank- und Query-basierte Connectors verfügbar. Tags sind benutzerdefinierte Schlüssel-Wert-Metadaten für Pipelines.

## Funktionsweise von Pipeline-Tags

Mit Tags lassen sich:

- Pipelines nach Umgebung, Projekt oder Team gruppieren
- Verantwortliche für eine Pipeline identifizieren
- Pipeline-Nutzung mit bestimmten Kostenstellen oder Budgets verknüpfen
- Operationen anhand von Tag-Werten filtern

**Wichtige Abgrenzung:** Tags sind Metadaten auf der Pipeline-Ressource selbst, während Serverless-Nutzungsrichtlinien (Usage Policies) Tags auf Abrechnungsdatensätze für Serverless Compute anwenden.

## Tags hinzufügen oder aktualisieren

Tags werden über ein `tags`-Objekt in der Pipeline-Spezifikation definiert. Beispiel für eine Produktions-Sales-Pipeline mit Tags für Umgebung, Owner, Kostenstelle und Projekt:

```python
// JSON (Pipeline-Spezifikation)
{
  "name": "sales-data-pipeline",
  "catalog": "prod",
  "target": "sales",
  "serverless": true,
  "tags": {
    "environment": "production",
    "owner": "data-engineering-team",
    "costcenter": "engineering-analytics",
    "project": "sales-analytics"
  },
  "ingestion_definition": {
    "connection_name": "salesforce-prod",
    "objects": [
      {
        "table": {
          "source_schema": "salesforce",
          "source_table": "Account",
          "destination_catalog": "prod",
          "destination_schema": "sales",
          "table_configuration": {
            "scd_type": "SCD_TYPE_1"
          }
        }
      }
    ]
  }
}
```

## Pipeline-Tags einsehen

Um die Tags einer Pipeline abzufragen, wird die Systemtabelle `pipelines` abgefragt.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/pipeline-tags  
**Stand:** 2026-08-07
