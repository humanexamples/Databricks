# Standardrechte ohne expliziten Grant

Nicht jede Berechtigung muss manuell vergeben werden — Unity Catalog stattet Nutzer standardmäßig mit einigen Grundrechten aus.

## Catalog `main`

Alle Nutzer besitzen standardmäßig `USE CATALOG` auf dem Catalog `main`.

## Workspace-Catalog

Alle Workspace-Nutzer erhalten das `USE CATALOG`-Privileg auf dem Workspace-Catalog. Zusätzlich erhalten Workspace-Nutzer auf dem Schema `default` in diesem Catalog folgende Privilegien:

- `USE SCHEMA`
- `CREATE TABLE`
- `CREATE VOLUME`
- `CREATE MODEL`
- `CREATE FUNCTION`
- `CREATE MATERIALIZED VIEW`

**Ungeklärt:** Ob und wie sich dieses automatische Default-Verhalten des Workspace-Catalogs abschalten oder pro Workspace konfigurieren lässt, wurde in den geprüften Quellen nicht behandelt.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-privileges
