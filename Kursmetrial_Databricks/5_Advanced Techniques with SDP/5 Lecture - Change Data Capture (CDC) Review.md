


 

Konzepte und Umsetzungsmuster für Change Data Capture (CDC) im Lakehouse. 

```sql
-- CDC mit `AUTO CDC INTO` in Spark Declarative Pipelines umsetzen

CREATE OR REFRESH STREAMING TABLE customers;

CREATE FLOW scd_type_1_flow AS
AUTO CDC INTO customers 
 FROM STREAM updates
 KEYS (CustomerID)                              
 APPLY AS DELETE WHEN operation = "DELETE"     
 SEQUENCE BY ProcessDate                 
 COLUMNS * EXCEPT (operation)  
 STORED AS SCD TYPE 1;
```

- **`AUTO CDC INTO customers`** – Gibt die Zieltabelle für die CDC-Operationen an
- **`FROM STREAM updates`** – Definiert den Quell-Stream mit den CDC-Events
- **`KEYS (CustomerID)`** – Legt eindeutige Schlüssel für den Abgleich von Quell- und Zieldatensätzen fest
- **`APPLY AS DELETE WHEN operation = "DELETE"`** – Definiert die Löschlogik anhand der Spalte operation
- **`SEQUENCE BY ProcessDate`** – Stellt sicher, dass Events in chronologischer Reihenfolge verarbeitet werden
- **`COLUMNS * EXCEPT (operation)`** – Schließt alle Spalten außer operativen Metadaten ein
- **`STORED AS SCD TYPE 1`** – Legt das Muster SCD Type 1 fest (Standard ist SCD Type 1)

### Entscheidungsrahmen:

**Wählen Sie SCD Type 1, wenn:**
- nur der aktuelle Datenzustand benötigt wird
- Speichereffizienz Vorrang hat
- keine historische Nachverfolgung erforderlich ist

**Wählen Sie SCD Type 2, wenn:**
- historische Analysen unverzichtbar sind
- Audit Trails für die Compliance erforderlich sind
- Reporting zu einem bestimmten Zeitpunkt benötigt wird

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
