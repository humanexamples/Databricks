# Privilegien und schützbare Objekte — Legacy

**Hinweis:** Legacy-Governance-Modell für den Hive Metastore. Databricks empfiehlt stattdessen Unity Catalog.

## Voraussetzungen

- Ein Admin muss Table Access Control für den Workspace aktivieren und erzwingen.
- Der Cluster muss für Table Access Control aktiviert sein.
- In Databricks SQL ist Datenzugriffskontrolle unabhängig von den Workspace-Einstellungen **immer** aktiviert.

## Privilegien verwalten

```sql
GRANT privilege_type ON securable_object TO principal;
```

Weitere Befehle: `REVOKE`, `DENY`, `MSCK`, `SHOW GRANTS`.

Die Eigentümerschaft eines Objekts geht bei aktiviertem Table Access Control auf den Ersteller über. Eigentümer oder Workspace-Admin können sie neu zuweisen:

```sql
ALTER <object> OWNER TO <principal>;
```

## Hierarchie der schützbaren Objekte

`CATALOG` → `SCHEMA` → `TABLE`/`VIEW`/`FUNCTION`, zusätzlich `ANONYMOUS FUNCTION` und `ANY FILE` (umgeht Catalog-Beschränkungen, wenn vergeben — siehe `ANY FILE.md`).

## Vergebbare Privilegien

Acht Privilegientypen: `SELECT`, `CREATE`, `MODIFY`, `USAGE`, `READ_METADATA`, `CREATE_NAMED_FUNCTION`, `MODIFY_CLASSPATH`, `ALL PRIVILEGES`.

`USAGE` ist erforderlich, um eine Aktion auf einem Schema-Objekt auszuführen — erfüllt entweder durch Admin-Status, direkten Grant, Grant auf Catalog-Ebene oder Eigentümerschaft.

## Dynamische Views

Databricks stellt dynamische View-Funktionen wie `current_user()` und `is_member()` bereit, um Column-Level-, Row-Level- und Daten-Maskierungsberechtigungen direkt in View-Definitionen umzusetzen.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/table-acls/object-privileges
