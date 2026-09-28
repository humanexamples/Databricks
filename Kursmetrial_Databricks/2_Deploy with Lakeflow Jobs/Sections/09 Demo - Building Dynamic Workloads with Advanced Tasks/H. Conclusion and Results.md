## H. Fazit und Ergebnisse

Wenn Ihr Job-Run erfolgreich war, klicken Sie auf das Katalog-Symbol und navigieren Sie zu Ihrem Schema im Katalog dbacademy. Suchen Sie nach den neuen Tabellen **customers_sales_gold**, **customers_orders_ca_silver**, **customers_orders_ny_silver** und **customers_orders_va_silver**.

Die Tabelle `customers_sales_gold` erfordert keine Transformation. Sie ist unsere Gold-Tabelle mit Verkaufskennzahlen wie **units_purchased, avg_price_per_unit, total_price**, Kundendetails wie **customer_id, customer_name, loyalty_segment** sowie unterstützenden Bestelldetails.

```sql
%sql
SELECT * 
FROM customers_sales_gold
```

Die Tabellen **customers_orders_ca_silver**, **customers_orders_ny_silver** und **customers_orders_va_silver** sind staatenspezifisch und enthalten die relevanten Daten für jeden Bundesstaat. Diese Tabellen werden weiter transformiert, um Geschäftsspalten hinzuzufügen; das erledigen wir in einer späteren Demo, um Gold-Tabellen zu erstellen. Fragen Sie sie jetzt ab, um zu sehen, welche Art von Daten sie enthalten.

```sql
%sql
SELECT * 
FROM customers_orders_ca_silver
```

```sql
%sql
SELECT * 
FROM customers_orders_ny_silver
```

```sql
%sql
SELECT * 
FROM customers_orders_va_silver
```

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
