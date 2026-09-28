# Insights-Tab (Catalog Explorer)

Der Insights-Tab im Catalog Explorer zeigt Nutzungstrends und häufige Aktivität zu einer in Unity Catalog registrierten Tabelle — nützlich sowohl zur Vertrauensbewertung von Daten als auch zur Identifikation ungenutzter Tabellen für Cleanup-Maßnahmen. Basierend auf einer privaten Kursnotiz sowie der offiziellen Databricks-Dokumentation.

## Was der Insights-Tab anzeigt

- Ein Diagramm zur **Tabellennutzung der letzten 30 Tage**.
- **Häufige Queries und Notebooks**, die auf die Tabelle zugreifen.
- **Häufig genutzte Dashboards.**
- **Häufige Nutzer**, die auf die Tabelle zugreifen.
- **Andere Tabellen**, die häufig zusammen mit dieser Tabelle gejoint werden.

Popularität wird dabei unterschiedlich gemessen: Tabellen-Popularität bemisst sich an interaktiven Lesezugriffen, Spalten-Popularität am Anteil der Queries, die die jeweilige Spalte referenzieren.

## Geltungsbereich (Scope)

Die einzelnen Abschnitte unterscheiden sich im Geltungsbereich:

| Abschnitt | Scope |
|---|---|
| Tabellennutzungs-Diagramm (30 Tage) | **metastore-weit** — über alle am Metastore angehängten Workspaces hinweg |
| Häufig gejointe Tabellen | **metastore-weit** |
| Häufige Nutzer | **workspace-begrenzt** |
| Häufige Queries | **workspace-begrenzt** — nur gespeicherte Queries im SQL-Editor |
| Häufige Dashboards / Notebooks | **workspace-begrenzt** |

## Benötigte Berechtigungen

Um häufige Queries und Nutzerdaten im Insights-Tab einzusehen, werden folgende Privilegien benötigt:

- `SELECT`-Privileg auf der Tabelle
- `USE SCHEMA`-Privileg auf dem übergeordneten Schema der Tabelle
- `USE CATALOG`-Privileg auf dem übergeordneten Catalog der Tabelle
- Für Query-Ergebnisse zusätzlich `CAN VIEW`-Berechtigung in Databricks SQL

Metastore-Admins verfügen standardmäßig über diese Berechtigungen.

## Nutzen: ungenutzte Tabellen identifizieren

Der Insights-Tab hilft bei Fragen wie „Kann ich diesen Daten vertrauen?" oder „Welche Nutzer können dazu Auskunft geben?" — und lässt sich damit auch nutzen, um Tabellen zu identifizieren, die von Anwendungen nicht mehr verwendet werden. Solche Tabellen können anschließend zur späteren Bereinigung (Cleanup) getaggt werden (siehe [Uebersicht.md](../10%20Governed%20Tags/Uebersicht.md) sowie [Discoverability und Tag-Suche.md](../10%20Governed%20Tags/Discoverability%20und%20Tag-Suche.md)).

## Quellen

- https://docs.databricks.com/aws/en/discover/table-insights
- Private Kursnotiz (Berechtigungsanforderungen, Cleanup-Anwendungsfall)
