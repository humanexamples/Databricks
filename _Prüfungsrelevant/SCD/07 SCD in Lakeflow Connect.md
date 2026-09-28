[← Übersicht](00%20Uebersicht.md)

# SCD in Lakeflow Connect (Managed Connectors)

**Kombination:** Lakeflow Connect · log-basiertes CDC der Quelldatenbank · SCD 1 / SCD 2 per Konfiguration · Databricks Asset Bundle · Weiterverarbeitung in Gold

Bei Managed Connectors (SQL Server, Salesforce, Google Analytics, …) schreibst du **weder CDC- noch SCD-Code**. Der Connector liest die Änderungen der Quelle selbst (bei Datenbanken über deren Change Tracking bzw. CDC) und wendet sie auf die Zieltabellen an. Du wählst nur pro Tabelle, ob die Historie behalten wird:

| Einstellung | Bedeutung | UI |
|---|---|---|
| `SCD_TYPE_1` | History Tracking **aus**: Updates und Deletes überschreiben bzw. entfernen Zeilen | „History tracking: Off“ |
| `SCD_TYPE_2` | History Tracking **an**: alte Zeile bleibt als inaktive Version erhalten | „History tracking: On“ |

---

## Beispiel: SQL Server, zwei Tabellen mit unterschiedlichem SCD-Typ

```yaml
# resources/erp_ingestion.pipeline.yml
resources:
  pipelines:
    erp_sqlserver_ingestion:
      name: erp_sqlserver_ingestion
      catalog: main
      schema: erp_bronze
      ingestion_definition:
        connection_name: erp_sqlserver_connection
        objects:
          # Kunden: Historie behalten → SCD 2
          - table:
              source_catalog: erp
              source_schema: dbo
              source_table: customers
              destination_catalog: main
              destination_schema: erp_bronze
              table_configuration:
                scd_type: SCD_TYPE_2
                sequence_by: modified_at

          # Bestellungen: Fakten, nur aktueller Stand → SCD 1
          - table:
              source_catalog: erp
              source_schema: dbo
              source_table: orders
              destination_catalog: main
              destination_schema: erp_bronze
              table_configuration:
                scd_type: SCD_TYPE_1
```

- `sequence_by` legt bei SCD 2 fest, welche Spalte die Reihenfolge der Versionen bestimmt. Laut Doku werden Timestamp, Date, Integer, Long und String unterstützt.
- Datenbank-Connectoren benötigen zusätzlich ein **Ingestion Gateway**, das die Änderungen aus der Quelle liest → [Lakeflow Connect Übersicht](../../Online%20Databricks%20Docs/Data%20Management/Data%20Engineering/Lakeflow%20Connect/02-lakeflow-connect-uebersicht.md).
- Deployment wie jedes Bundle: `databricks bundle deploy -t prod`.

**Achtung:** Wird in der Quelle eine ganze **Tabelle oder Spalte** gelöscht, bleiben diese Daten im Ziel erhalten, auch bei SCD 1. Nur **Zeilen**-Deletes werden übernommen.

---

## Weiterverarbeitung: die Connector-Tabellen als Quelle

Die Zieltabellen des Connectors sind normale Delta-Tabellen in Unity Catalog. Alles aus den anderen Dateien lässt sich darauf aufbauen:

```sql
-- Gold: Point-in-Time-Umsatz auf Basis der SCD-2-Kundentabelle des Connectors
CREATE OR REFRESH MATERIALIZED VIEW main.erp_gold.revenue_by_city_historical AS
SELECT d.city, sum(o.amount) AS revenue
FROM main.erp_bronze.orders o
JOIN main.erp_bronze.customers d
  ON  o.customer_id = d.customer_id
  AND o.order_date >= d.__START_AT
  AND o.order_date <  coalesce(d.__END_AT, TIMESTAMP'9999-12-31')
GROUP BY d.city;
```

Die Spaltennamen `__START_AT` / `__END_AT` im Beispiel folgen der AUTO-CDC-Konvention. Vor dem Einsatz mit `DESCRIBE TABLE main.erp_bronze.customers` prüfen, wie die Versionsspalten in deiner Zieltabelle heißen.

| Weiterverarbeitung | Datei |
|---|---|
| Point-in-Time-Join, Surrogate Keys, SCD-6-View | [04](04%20SCD%20im%20Star-Schema.md) |
| Zugriffsschutz, Konsistenzprüfung | [05](05%20SCD%20mit%20Governance%2C%20Data%20Quality%20und%20Performance.md) |
| Änderungen per CDF weiterreichen | [../CDC/04](../CDC/04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md) |

---

## Wann Lakeflow Connect, wann AUTO CDC selbst bauen?

| | Lakeflow Connect Managed Connector | AUTO CDC in eigener Pipeline |
|---|---|---|
| Quelle | unterstützte Datenbank oder SaaS-Anwendung | alles, was Change-Events liefert (Dateien, Kafka, CDF) |
| CDC-Erfassung | übernimmt der Connector | selbst organisiert (Debezium, Export, …) |
| Aufwand | Konfiguration | Code |
| Flexibilität | SCD-Typ und Sequenzspalte wählbar | alle AUTO-CDC-Optionen (`TRACK HISTORY`, Expectations vorab, eigene Transformation) |

---
[← Vorherige Datei](06%20SCD%20Type%202%20vs.%20Delta%20Time%20Travel.md) · [Übersicht](00%20Uebersicht.md)

## Quellen

- Lakeflow-Connect-Doku in diesem Repo: [08-scd.md](../../Online%20Databricks%20Docs/Data%20Management/Data%20Engineering/Lakeflow%20Connect/08-scd.md)
- [Lakeflow Connect](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/)
