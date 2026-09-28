## G. Ihre neuen Tabellen ansehen
1. Wählen Sie im linken Bereich **Catalog**. Navigieren Sie dann in den Katalog **dbacademy**.

2. Klappen Sie Ihren eindeutigen Schemanamen auf.

3. Beachten Sie, dass sich in Ihrem Schema die Tabellen **sales_bronze** und **orders_bronze** befinden.

## H. Ihre neuen Tabellen abfragen

```sql
%sql
-- Tabelle sales_bronze abfragen
SELECT * 
FROM sales_bronze
LIMIT 5;
```

```sql
%sql
-- Tabelle orders_bronze abfragen
SELECT * 
FROM orders_bronze
LIMIT 50;
```

## Zusätzliche Ressourcen

- [Lakeflow Jobs Documentation](https://docs.databricks.com/aws/en/jobs/)

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
