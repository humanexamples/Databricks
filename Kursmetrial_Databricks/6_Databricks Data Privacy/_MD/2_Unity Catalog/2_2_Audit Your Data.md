## 2_2_Ihre Daten auditieren

- Unity Catalog verfügt inzwischen über umfangreiche System-Tabellen, die dir helfen, viele wichtige Fragen zu deinem Lakehouse zu beantworten. Das macht es transparenter und leichter zu verwalten und zu überwachen.
- Diese finden sich im „system“-Katalog. Beginnend mit Objekt-Metadaten kannst du das Schema „information_schema“ nutzen, um Analysen auf deinen operativen Daten durchzuführen und so Fragen rund um Ownership, Inventar, Datenzugriff, Tags usw. zu beantworten.

Zum Beispiel:

- Welche Tabellen befinden sich in einem bestimmten Katalog?
- Wer hat Zugriff auf eine bestimmte Tabelle?
- Wer hat die letzte Aktualisierung an einer Gold-Tabelle vorgenommen und wann?
- Wer ist Owner einer bestimmten Tabelle und mehr

System Tables - https://docs.databricks.com/en/admin/system-tables/index.html
Information Schema - https://docs.databricks.com/en/sgl/lanquage-manual/sgl-ref-information-schema.html

```sql
# System Tables: Object Metadata
# Fragen zum Zustand von Objekten im Katalog beantworten

# Welche Tabellen befinden sich im Katalog sales?
SELECT table_name 
FROM system.information_schema.tables 
WHERE table_catalog="sales";

# Wer hat die Gold-Tabellen zuletzt aktualisiert und wann?
SELECT table_name, last_altered_by, last_altered 
FROM system.information_schema.tables 
WHERE table_catalog="churn_gold" ORDER BY 1, 3 DESC;

# Wer hat Zugriff auf diese Tabelle?
SELECT grantee, table_name, privilege_type
FROM system.information_schema.table_privileges
WHERE table_name = "login_data_silver";

# Who owns this gold table?
SELECT table_owner
FROM system.information_schema.tables
WHERE table_catalog = "retail_prod" AND table_schema = "churn_gold" AND table_name = "churn_features";
```

------

Innerhalb des System-Katalogs kannst du außerdem die Billing-Logs über das Schema „billing“ und die Tabelle „usage“ nutzen, um Fragen zu beantworten wie:

- Wie ist der tägliche Trend beim DBU-Verbrauch?
- Wie viele DBUs jeder SKU wurden in diesem Monat verbraucht?
- Welche 10 Nutzer haben die meisten DBUs verbraucht?
- Welche Jobs haben die meisten DBUs verbraucht?

System Billing Schema - https://docs.databricks.com/en/admin/system-tables/billing.html

```sql
# System Tables: Billing Logs
# Understand const allocation across your data estate

# Wie ist der tägliche Trend beim DBU-Verbrauch?
SELECT usage_date as 'Date', sum(usage_quantity) as 'DBUs Consumed'
FROM system.billing.usage
GROUP BY usage_date
ORDER BY usage_date ASC;

# Welche 10 Benutzer haben die meisten DBUs verbraucht?
SELECT identity_metadata.run_as as 'User', sum(usage_quantity) as' DBUS'
FROM system.billing.usage
GROUP BY identity_metadata.run_as
ORDER BY DBUS DESC
LIMIT 10;

# Wie viele DBUs wurden in diesem Monat bisher pro SKU verbraucht?
SELECT sku_name as 'SKU', sum(usage_quantity) as 'DBUS'
FROM system.billing.usage
WHERE month(usage_date) = month(CURRENT_DATE)
GROUP BY sku
ORDER BY 'DBUS' DESC;

# Welche Jobs haben die meisten DBUs verbraucht?
SELECT usage_metadata. job_id as 'Job ID',
sum(usage_quantity) as 'DBUs'
FROM system.billing. usage
GROUP BY Job ID;
```

------

Du kannst außerdem die „Audit Logs“ im Schema „access“ und der Tabelle „audit“ nutzen, um Fragen zu beantworten wie:

- Auf welche Tabelle wird am häufigsten zugegriffen?
- Wer hat eine bestimmte Tabelle gelöscht?
- Worauf hat ein bestimmter Nutzer in den letzten 24 Stunden zugegriffen?
- Auf welche Tabellen greift ein bestimmter Nutzer am häufigsten zu?

Hier sind einige Beispiele. Beachte, dass sich dieses Feature noch in der Public Preview befindet – kläre also mit deinem Workspace-Administrator, ob es aktiviert ist.

Audit Logs - https://docs.databricks.com/en/admin/system-tables/audit-logs.html

```sql
# System Tables: Audit Logs
# Nahezu in Echtzeit sehen, wer wann worauf zugegriffen hat

# Wer greift am häufigsten auf diese Tabelle zu?
SELECT user_identity.email, count(*)
FROM system. access.audit
WHERE request_params.table_full_name = "main. uc_deep_dive. login_data_silver"
	AND service_name = "unityCatalog"
	AND action_name = "generateTemporaryTableCredential"
GROUP BY 1 ORDER BY 2 DESC LIMIT 1;

# Who deleted this table?
SELECT user_identity. email
FROM system. access.audit
WHERE request_params. full_name_arg = "main. uc_deep_dive. login_data_silver"
	AND service_name = "unityCatalog"
	AND action_name = "deleteTable";
	
# Worauf hat dieser Benutzer in den letzten 24 Stunden zugegriffen?
SELECT request_params. table_full_name
FROM system. access.audit
WHERE user_identity.email = "ifi.derekli@databricks.com"
	AND service_name = "unityCatalog"
	AND action_name = "generateTemporaryTableCredential"
	AND datediff(now(), event_time) < 1;

# Auf welche Tabellen greift dieser Benutzer am häufigsten zu?
SELECT request_params. table_full_name, count(*)
FROM system. access. audit
WHERE user_identity.email = "ifi.derekli@databricks.com"
	AND service_name = "unityCatalog"
	AND action_name = "generateTemporaryTableCredential"
GROUP BY 1 ORDER BY 2 DESC LIMIT 1;
```

------

Was ist mit Lineage-Daten? Hier gibt es zwei Optionen: erstens auf Tabellenebene und zweitens auf Spaltenebene. Dafür kannst du das Schema „access“ und die Tabelle „table_lineage“ nutzen, um Fragen zu beantworten wie:

- Welche Tabellen speisen sich aus einer bestimmten Tabelle?
- Welche Nutzer-Queries lesen aus einer bestimmten Tabelle?

Dieses Feature befindet sich im Preview-Modus – kläre es also mit deinem Administrator.

Table Lineage - https://docs.databricks.com/en/admin/system-tables/lineage.html
Column Lineage - https://docs.databricks.com/en/admin/system-tables/lineage.html#column-lineage-table

```sql
# System Tables: Lineage Data
# Vor- und nachgelagerte Quellen an einem Ort abfragen

# Welche Tabellen speisen sich aus dieser Tabelle?
SELECT DISTINCT target_table_full_name
FROM system.access.table lineage
WHERE source_table_name = "login_data_bronze";

# Welche Benutzerabfragen lesen aus dieser Tabelle?
SELECT DISTINCT entity_type, entity_id, source_table_full_name
FROM system. access.table lineage
WHERE source_table_name = "login_data_silver";
```
