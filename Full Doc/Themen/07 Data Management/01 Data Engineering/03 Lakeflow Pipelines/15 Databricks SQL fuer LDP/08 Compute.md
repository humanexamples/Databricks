# Anforderungen und Compute für Standalone Pipelines

Dieses Dokument beschreibt die Voraussetzungen, Berechtigungen und Compute-Optionen für Standalone Materialized Views und Streaming Tables (Databricks SQL für LDP).

## Abschnittsübersicht

1. [Allgemeine Voraussetzungen](#allgemein)
2. [Berechtigungen zum Erstellen/Refreshen](#berechtigungen)
3. [Compute-Option: SQL-Warehouse](#sql-warehouse)
4. [Compute-Option: Notebook (Beta)](#notebook-beta)
5. [Zugriff und Abfrage](#zugriff)
6. [Quellen](#quellen)

---

## <a id="allgemein">1. Allgemeine Voraussetzungen</a>

Um Standalone Materialized Views und Streaming Tables zu erstellen und zu refreshen, benötigt man laut Doku "a serverless-enabled, Unity Catalog-enabled workspace, and either a SQL warehouse or a notebook on serverless general compute". Konkret bedeutet das:

- Ein Databricks-Account mit aktiviertem Serverless
- Einen Workspace mit aktiviertem Unity Catalog

## <a id="berechtigungen">2. Berechtigungen zum Erstellen/Refreshen</a>

Der Owner des Objekts benötigt:

- `SELECT`-Privileg auf den Basistabellen ("the base tables")
- `USE CATALOG`- und `USE SCHEMA`-Privilegien auf Katalog und Schema, die die Quelltabellen enthalten
- `USE CATALOG`- und `USE SCHEMA`-Privilegien auf Zielkatalog und -schema
- `CREATE MATERIALIZED VIEW`-Privileg auf dem Schema, das die Materialized View enthält (bei Materialized Views)
- `CREATE TABLE`-Privileg auf dem Schema, das die Streaming Table enthält (bei Streaming Tables)

Um eine bestehende Tabelle zu refreshen, ist das `REFRESH`-Privileg auf der Tabelle erforderlich.

### Voraussetzung für inkrementellen Refresh von Materialized Views

Für den inkrementellen Refresh von Materialized Views aus Delta-Tabellen müssen die Quelltabellen laut Doku Row Tracking aktiviert haben ("the source tables must have row tracking enabled").

## <a id="sql-warehouse">3. Compute-Option: SQL-Warehouse</a>

Erforderlich ist ein Unity-Catalog-fähiges Pro- oder Serverless-SQL-Warehouse in einer Region, die Serverless-Funktionalität unterstützt, sowie akzeptierte Nutzungsbedingungen ("terms of use").

## <a id="notebook-beta">4. Compute-Option: Notebook (Beta)</a>

Verfügbar auf Serverless General Compute mit **Databricks Runtime 18.1 oder höher**. Dieses Feature ist aktuell auf ausgewählte Regionen beschränkt (Beta-Status) und unterliegt folgenden Einschränkungen:

- Nur der Owner kann Tabellen refreshen
- Asynchrone Refreshes werden nicht unterstützt
- Der Preview-Channel steht nicht zur Verfügung
- Tabellen müssen auf demselben Compute-Typ refresht werden, mit dem sie erstellt wurden
- Keine Kostenzuordnung/-kontrolle möglich ("Cost attribution/control unavailable")
- Kein vertikales Autoscaling bei Fehlern ("Vertical autoscaling on errors unavailable")
- Keine Wiederholungsversuche bei Schema-Upgrades ("Schema upgrade retries unavailable")
- Keine Auswahl des Performance-Modus ("Performance mode selection unavailable")

## <a id="zugriff">5. Zugriff und Abfrage</a>

Nutzer können diese Tabellen über SQL-Warehouses, Lakeflow-Oberflächen oder Compute mit Standard- bzw. Dedicated-Access-Modus abfragen, sofern sie über die entsprechenden Berechtigungen verfügen (`SELECT` auf der Tabelle plus `USE CATALOG`/`USE SCHEMA` auf den übergeordneten Objekten).

---

## <a id="quellen">6. Quellen</a>

1. Requirements for standalone pipelines (AWS): https://docs.databricks.com/aws/en/ldp/dbsql/compute

**Hinweis:** Diese Seite enthält laut Abruf keine SQL-Code-Beispiele (reine Anforderungs-/Berechtigungsliste). Ein gezielter zweiter Abruf zur Code-Suche bestätigte dies ("No code examples provided in this section" für alle Unterabschnitte).
