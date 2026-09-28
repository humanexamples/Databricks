# Access Control — Überblick

Unity Catalog bietet vier ergänzende Mechanismen zur Zugriffskontrolle:

| Mechanismus | Gilt für | Definiert über | Anwendungsfall |
|---|---|---|---|
| **Privilegien & Eigentümerschaft** | Catalogs, Schemas, Tabellen | Grants (`GRANT`, `REVOKE`), Ownership | Basiszugriff und Delegation |
| **ABAC-Policies** | Getaggte Objekte (Tabellen, Schemas) | Policies mit Governed Tags und UDFs | Zentralisierte, tag-getriebene Policies mit dynamischer Durchsetzung |
| **Tabellenbezogene Row-/Column-Filter** | Einzelne Tabellen | UDFs direkt auf der Tabelle | Tabellenspezifische Filterung/Maskierung |
| **Workspace-Bindings** | Catalogs, External Locations, Storage Credentials | Workspace-Zuweisung | Zugriff auf Objekte auf bestimmte Workspaces beschränken |

## Empfehlung

Databricks empfiehlt **Attribute-Based Access Control (ABAC)**, um Zugriffskontrolle zentral und skalierbar auf Basis von Governed Tags zu steuern. Row Filter und Column Masks bleiben für tabellenspezifische Logik oder für Organisationen ohne ABAC-Nutzung sinnvoll.

## Struktur der weiterführenden Doku

- **Permissions-Modell** — Hierarchie, Vererbung, Privilegien-Konzepte (siehe `Berechtigungskonzepte.md`)
- **Zugriff verwalten** — Privilegien, Access Requests, Workspace-Catalog-Binding
- **Feingranularer Datenzugriff** — ABAC, Row-/Column-Filter

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/
