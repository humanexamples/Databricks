# Kosten von Managed-Ingestion-Pipelines überwachen

Diese Seite erklärt, wie sich die Kosten von Lakeflow-Connect-Managed-Ingestion-Pipelines über Databricks-Systemtabellen und Abrechnungsdaten nachverfolgen und analysieren lassen.

## Wichtige Abrechnungsparameter

- **`billing_origin_product`**: bei allen Managed-Connector-Nutzungen auf `LAKEFLOW_CONNECT` gesetzt.
- **`usage_type`**: bei Pipeline-Verarbeitung auf `COMPUTE_TIME` gesetzt.
- **`usage_unit`**: erfasst in `MILLISECOND` (reine Rechenzeit) und `DBU`.

## Metadatenfelder zur Nutzung

Informationen zu den Pipeline-Ressourcen werden über folgende Felder erfasst:

- `dlt_pipeline_id`: Pipeline-Kennung
- `uc_table_catalog`, `uc_table_schema`, `uc_table_name`: Details zur Zieltabelle

## Kernkonzepte

**Wartungskosten der Pipeline:** Auch in inaktiven Zeiten fallen Infrastruktur- und Metadatenverwaltungskosten an – getrennt von den eigentlichen Datenverarbeitungskosten.

**Kostenüberwachung:** Databricks empfiehlt, AI/BI-Dashboards zu erstellen und Alerts auf Basis der Abrechnungsdaten der Systemtabellen einzurichten, um die Kosten laufend im Blick zu behalten.

## Beispielabfragen

Die Dokumentation stellt neun Abfrage-Vorlagen bereit, u. a. für:

- Monatliche DBU-Gesamtverbräuche
- Ermittlung der teuersten Pipelines
- Kostenentwicklung einzelner Pipelines
- Kostenzuordnung über Budget-Tags
- Trennung von Wartungs- und Verarbeitungskosten
- Monat-über-Monat-Wachstumsanalyse
- Umrechnung in Dollar-Kosten
- Kostenaggregation nach Zieltabelle

Jede Abfrage greift auf die Systemtabelle `system.billing.usage` zu, gefiltert nach Lakeflow-Connect-spezifischen `WHERE`-Bedingungen.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/monitor-costs  
**Stand:** 2026-08-07
