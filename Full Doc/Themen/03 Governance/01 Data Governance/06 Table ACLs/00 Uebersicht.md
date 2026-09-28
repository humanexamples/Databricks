# Table ACLs (Hive Metastore) — Legacy

**Hinweis:** Table Access Control für den (in jedem Workspace eingebauten) Hive Metastore ist ein **Legacy-Governance-Modell**. Databricks empfiehlt, stattdessen **Unity Catalog** zu nutzen — es bietet einen zentralen Ort, um Datenzugriff über mehrere Workspaces hinweg zu verwalten und zu auditieren (siehe die übrigen Kapitel dieses Ordners).

## Grundfunktion

Jeder Workspace enthält einen eingebauten Hive Metastore. Ist Table Access Control aktiviert, können Admins Berechtigungen für Datenobjekte programmatisch über Python und SQL verwalten. Standardmäßig gilt: Ein Cluster erlaubt allen Nutzern Zugriff auf alle vom eingebauten Hive Metastore verwalteten Daten, **sofern Table Access Control nicht aktiviert ist**.

## Voraussetzungen

- Mindestens ein **Premium**-Abonnement.
- Ein Data-Science-&-Engineering-Cluster mit passender Konfiguration **oder** ein SQL-Warehouse.

## Themen in diesem Kapitel

1. Aktivierung von Table Access Control auf Clustern (siehe `Table ACL.md`)
2. Verfügbare Privilegien und schützbare Objekte (siehe `Object Privileges.md`)
3. Das schützbare Objekt `ANY FILE` (siehe `ANY FILE.md`)

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/table-acls/
