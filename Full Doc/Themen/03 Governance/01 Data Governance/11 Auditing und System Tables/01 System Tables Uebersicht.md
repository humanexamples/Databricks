# System Tables — Überblick

System Tables sind ein von Databricks gehosteter, analytischer Speicher der operativen Account-Daten im `system`-Catalog — sie ermöglichen Kostenmonitoring, Sicherheits-Audits, Compute-Performance-Analysen und Workload-Observability über den gesamten Account hinweg. Alle System Tables sind **read-only**.

## Voraussetzungen

- Der Workspace muss für Unity Catalog aktiviert sein.
- Der Metastore benötigt Unity Catalog Privilege Model Version 1.0.
- Zugriff ist nur über Unity-Catalog-aktivierte Workspaces möglich — die Tabellen erfassen aber Daten aller Workspaces der jeweiligen Region.

## Berechtigungen

Account- und Metastore-Admins haben standardmäßig Zugriff. Andere Nutzer benötigen:

- `USE CATALOG` auf dem `system`-Catalog,
- `USE SCHEMA` auf dem jeweiligen Schema,
- `SELECT` auf der jeweiligen System-Tabelle.

## Verfügbare Schemas (Auswahl)

| Schema | Inhalt |
|---|---|
| `system.billing` | Abrechenbare Nutzung, Preisdaten |
| `system.access` | Audit-Logs, Lineage, Netzwerk-Events |
| `system.compute` | Cluster, Warehouses, Nodes, Instance Pools |
| `system.lakeflow` | Jobs, Pipelines, Zerobus-Ingest-Operationen |
| `system.alert` | Alert-Konfigurationen und -Auswertungen |
| `system.serving` | Metadaten von Model-Serving-Endpunkten |
| `system.ai_gateway` | AI-Gateway-Nutzung und -Ausgaben |
| `system.information_schema` | Schema-Metadaten (funktioniert abweichend, siehe unten) |

## Aufbewahrung und Geltungsbereich

Die meisten Tabellen behalten Daten für **365 Tage** (kostenlose Aufbewahrungsfrist). Manche Tabellen (Node-Typen, Preise, Workspaces) werden unbegrenzt aufbewahrt. Workspace-Ereignisse sind regional, Account-Ereignisse global gespeichert.

## Streaming aus System Tables

Ab Databricks Runtime 16.4 lassen sich System Tables auch als Streaming-Quelle lesen — dabei muss die Option `skipChangeCommits` gesetzt werden, und die VACUUM-Aufbewahrung (Standard 7 Tage) sollte beim Lag-Monitoring berücksichtigt werden:

```python
spark.readStream.option("skipChangeCommits", "true").table("system.billing.usage")
```

## Einschränkung

Neue Spalten können jederzeit zu System Tables hinzugefügt werden. Stark selektive Query-Prädikate werden empfohlen, um Performance-Fehler zu vermeiden.

## `information_schema`: Metadaten-Abfragen

`INFORMATION_SCHEMA` ist ein SQL-Standard-Schema, das Metadaten über Objekte in allen Catalogs des Metastore liefert — sowohl account-weit (`system.information_schema`) als auch pro Catalog. Es gilt automatische Privilegien-Filterung: **es werden nur Objekte angezeigt, auf die bereits Zugriff besteht.**

**Wichtige Views:**

| View | Zweck | Wichtige Spalten |
|---|---|---|
| `TABLES` | Tabellen/Views im Catalog | `table_name`, `table_schema`, `table_catalog`, `table_owner`, `created_by`, `last_altered`, `last_altered_by` |
| `TABLE_PRIVILEGES` | Principals mit Privilegien auf Tabellen/Views | `grantee`, `privilege_type`, `table_name`, `table_schema`, `table_catalog` |
| `COLUMNS` | Spalten von Tabellen/Views | `column_name`, `data_type`, `table_name` |

Weitere Views: `SCHEMATA`, `CATALOGS`, `ROUTINES`, sowie privilegienbezogene Views (`SCHEMA_PRIVILEGES`, `CATALOG_PRIVILEGES`).

**Beispiele:**

```sql
-- In den letzten 24 Stunden geänderte Tabellen finden
SELECT table_name, table_owner, last_altered
FROM system.information_schema.tables
WHERE datediff(now(), last_altered) < 1;
```

```sql
-- Wer hat Zugriff auf diese Tabelle?
SELECT grantee, table_name, privilege_type
FROM system.information_schema.table_privileges
WHERE table_name = "login_data_silver";
```

**Hinweis:** Selektive Filter verwenden, um Timeouts zu vermeiden; Bezeichner klein schreiben für bessere Performance.

## Quellen

- https://docs.databricks.com/aws/en/admin/system-tables/
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-information-schema
