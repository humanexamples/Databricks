# Lakeflow Connect Managed Connectors

Managed Connectors ergänzen die Standard-Connectors (Cloud-Objektspeicher, Kafka — siehe `Lakeflow Connect Standard Connectors/`) um Ingestion aus **Unternehmensdatenbanken und SaaS-Anwendungen**. Sie sind Unity-Catalog-governt und laufen auf Serverless Compute über Lakeflow Pipelines — inklusive effizienter inkrementeller Lese-/Schreiboperationen.

## Connector-Kategorien

| Kategorie | Beispiele |
|---|---|
| Community Connectors | quelloffen, community-gepflegt |
| Datenbank-Connectors mit CDC | MySQL, PostgreSQL, SQL Server |
| Dateiquellen-Connectors | Google Drive, SharePoint |
| Query-basierte Connectors | direkte Datenbank-Queries ohne CDC |
| SaaS-Connectors | Salesforce, HubSpot, Jira, Workday, … |
| Streaming-Connectors | RabbitMQ und andere Message Busse |

## Inkrementelle Ingestion

Änderungen an den Quelldaten werden nachverfolgt: Der erste Lauf lädt den vollständigen Datenbestand, jeder Folgelauf nutzt das Change-Tracking, um nach Möglichkeit nur die seit dem letzten Lauf geänderten Daten zu laden.

## SaaS-Connector-Architektur

Drei Kernkomponenten:

1. **Connection** — ein Unity-Catalog-Objekt, das die Authentifizierungsdaten sicher speichert.
2. **Ingestion Pipeline** — fragt die Quelle ab und schreibt die Ergebnisse auf Serverless Compute in Streaming Tables.
3. **Ziel-Streaming-Tables** — nehmen die eingelesenen Daten auf.

**Ablauf:** Credentials liegen sicher im Unity-Catalog-Connection-Objekt → die Pipeline authentifiziert sich damit → Daten werden über die SaaS-API abgerufen → Ergebnisse werden in Streaming Tables im Catalog geschrieben.

## Datenbank-Connector-Architektur

Datenbank-Connectors benötigen zusätzlich eine **Ingestion Gateway** und **Staging Storage**, um kontinuierliche Change-Capture zu unterstützen:

1. **Connection** — Unity-Catalog-Objekt mit den Datenbank-Zugangsdaten.
2. **Ingestion Gateway** — eine eigene, kontinuierlich als Task laufende Komponente, die Metadaten, Snapshots und Change-Logs von der Quelldatenbank abgreift und in einem Unity-Catalog-Volume zwischenspeichert (Staging).
3. **Staging Storage** — das Unity-Catalog-Volume als Zwischenschicht; standardmäßig nur für den ausführenden Nutzer zugänglich, abgesichert über reguläre Unity-Catalog-Mechanismen.
4. **Ingestion Pipeline** — verarbeitet die zwischengespeicherten Daten weiter und schreibt sie in Streaming Tables (läuft auf Serverless Compute).
5. **Ziel-Streaming-Tables** — enthalten den finalen, inkrementell aktualisierten Datenbestand.

**Zentraler Unterschied zu SaaS-Connectors:** Die Ingestion Gateway läuft als eigener, dauerhaft aktiver Task parallel zu den zeitgesteuerten Pipeline-Läufen — SaaS-Connectors benötigen diese zusätzliche Komponente nicht.

## Partner Connect

Partner Connect erlaubt es, Testkonten bei ausgewählten Databricks-Technologiepartnern anzulegen und Partnerlösungen direkt aus der Databricks-UI heraus anzubinden, ohne die Plattform zu verlassen. Databricks provisioniert dafür automatisch benötigte Ressourcen (SQL-Warehouses, Service Principals, Access Tokens). Partner aus der Kategorie Data Ingestion können dabei Datenbanken/Tabellen im Workspace anlegen — diese gehören zunächst dem Service Principal der Partnerlösung; Zugriff für weitere Nutzer muss explizit per `GRANT` vergeben werden.

**Einschränkung:** Partner Connect erfordert mindestens den Premium-Plan und ist in AWS-GovCloud-Regionen nicht verfügbar.

## Quellen

- https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/
- https://docs.databricks.com/aws/en/partner-connect/
