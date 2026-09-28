# Developer Reference — Übersicht

## Abschnittsübersicht

1. [Einordnung](#einordnung)
2. [Python-Entwicklung](#python)
3. [SQL-Entwicklung](#sql)
4. [Weitere Entwicklungsthemen](#weitere)
5. [Quellen](#quellen)

---

## <a id="einordnung">1. Einordnung</a>

Lakeflow-Pipelines dienen dazu, Datenladen und -transformationen über Abfragen umzusetzen, die Streaming-Tabellen und materialisierte Sichten (Materialized Views) definieren. Lakeflow-Pipelines unterstützen sowohl eine SQL- als auch eine Python-Schnittstelle — laut Doku bieten beide Schnittstellen "äquivalente Funktionalität für die meisten Datenverarbeitungs-Anwendungsfälle" ("equivalent functionality for most data processing use cases"). Diese Referenzseite verlinkt auf die Detailseiten zu Python-Entwicklung, SQL-Entwicklung sowie ergänzende Entwicklungsthemen.

---

## <a id="python">2. Python-Entwicklung</a>

| Thema | Beschreibung laut Doku |
|---|---|
| Develop pipeline code with Python | Überblick über die Pipeline-Entwicklung in Python. |
| Lakeflow pipelines Python language reference | Python-Referenzdokumentation für das `pipelines`-Modul. |
| Manage Python dependencies for pipelines | Anleitung zur Verwaltung von Python-Bibliotheken in Pipelines. |
| Import Python modules from Git folders or workspace files | Anleitung zur Verwendung von in Databricks gespeicherten Python-Modulen. |

---

## <a id="sql">3. SQL-Entwicklung</a>

| Thema | Beschreibung laut Doku |
|---|---|
| Develop Lakeflow pipelines code with SQL | Überblick über die Pipeline-Entwicklung in SQL. |
| Pipeline SQL language reference | Referenzdokumentation für die SQL-Syntax von Lakeflow-Pipelines. |
| Standalone pipelines | Verwendung von Databricks SQL im Zusammenspiel mit Pipelines. |

---

## <a id="weitere">4. Weitere Entwicklungsthemen</a>

| Thema | Beschreibung laut Doku |
|---|---|
| Convert a pipeline into a bundle project | Konvertierung einer Pipeline in ein Bundle — eine quellcodeverwaltete YAML-Datei zur einfacheren Pflege. |
| Create pipelines with dlt-meta | Verwendung der Open-Source-Bibliothek `dlt-meta`, um die Erstellung von Pipelines zu automatisieren. |
| Tutorial: Create multiple flows with different parameters | Erstellung mehrerer Flows in einer Schleife mit Python. |
| Develop pipeline code in your local development environment | Überblick über Optionen zur lokalen Pipeline-Entwicklung. |

---

## <a id="quellen">5. Quellen</a>

- Lakeflow pipelines developer reference (Übersichtsseite, Struktur und Linktexte): https://docs.databricks.com/aws/en/ldp/developer/

**Stand:** 2026-08-19.
