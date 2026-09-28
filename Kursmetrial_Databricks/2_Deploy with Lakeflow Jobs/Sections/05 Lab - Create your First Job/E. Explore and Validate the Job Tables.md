## E. Die Job-Tabellen erkunden und validieren
1. Wählen Sie im linken Bereich **Catalog**.

2. Klappen Sie den Katalog **dbacademy** auf.

3. Klappen Sie Ihren eindeutigen Schemanamen auf.

4. Bestätigen Sie, dass der Job die folgenden Tabellen erstellt hat:
  - **bank_master_data_bronze**
  - **borrower_details_silver**
  - **loan_details_silver**

Sie können auch die Anweisung `SHOW TABLES` verwenden, um die verfügbaren Tabellen in Ihrem Schema anzuzeigen.

```sql
%sql
SHOW TABLES;
```

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
