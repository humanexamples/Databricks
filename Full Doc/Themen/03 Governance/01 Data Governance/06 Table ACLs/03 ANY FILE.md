# Das schützbare Objekt `ANY FILE` — Legacy

**Hinweis:** Legacy-Governance-Modell für den Hive Metastore. Databricks empfiehlt stattdessen Unity Catalog.

## Grundfunktion

`ANY FILE` gewährt direkten Zugriff auf Dateisystem und Cloud-Speicher — unabhängig von Hive-Table-ACLs auf Datenbankobjekten.

## Privilegien

Nutzer können `MODIFY`- oder `SELECT`-Privilegien auf `ANY FILE` erhalten. Workspace-Administratoren besitzen standardmäßig `MODIFY`; wer `MODIFY` besitzt, kann Zugriff an andere vergeben oder entziehen.

## Zusammenspiel mit Unity Catalog

Ist Unity Catalog aktiviert, dienen `ANY FILE`-Privilegien als **Fallback-Mechanismus** für Speicherpfade und Datenquellen, die **nicht** unter Unity-Catalog-Governance stehen. Wichtig: Diese Privilegien können Unity-Catalog-Privilegien **nicht überschreiben** und erweitern keine Rechte auf von Unity Catalog verwalteten Datenobjekten.

`SELECT` auf `ANY FILE` ist u. a. erforderlich für:

- Cloud-Speicherzugriff über URIs
- Nutzung von DBFS-Root oder -Mounts
- Datenquellen aus benutzerdefinierten Bibliotheken
- Externe Quellen außerhalb von Unity Catalog
- Bestimmte Streaming-Muster

## Einschränkungen

`ANY FILE`-Privilegien umgehen Legacy-Hive-Table-ACLs, umgehen aber **niemals** Unity-Catalog-Schutzmechanismen. Das Objekt erscheint nicht im Information Schema, entsprechend seinem Legacy-Status. Databricks rät zu besonderer Vorsicht bei der Vergabe dieser Privilegien in gemischten Governance-Umgebungen.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/table-acls/any-file
