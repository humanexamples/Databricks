# Lakeflow Connect – Überblick über Managed Connectors

Lakeflow Connect bietet verwaltete Konnektoren zur Aufnahme von Daten aus SaaS-Anwendungen und Datenbanken. Diese Konnektoren werden von Unity Catalog verwaltet und laufen auf serverlosem Compute.

## Konnektor-Typen

Die Plattform bietet sechs Hauptkategorien:

1. **Community-Konnektoren** – Open-Source, community-entwickelt
2. **Datenbank-Konnektoren (CDC)** – Change Data Capture für MySQL, PostgreSQL, SQL Server
3. **Datei-Quellen-Konnektoren** – unstrukturierte und strukturierte Dateien aus Google Drive, SharePoint
4. **Query-basierte Konnektoren** – direkte Datenbankabfragen ohne CDC-Setup
5. **SaaS-Konnektoren** – Enterprise-Anwendungen wie Salesforce, HubSpot, Jira, Workday
6. **Streaming-Konnektoren** – kontinuierliche Aufnahme aus RabbitMQ und weiteren Event-Quellen

## Kernkomponenten

**Query-basierte Konnektoren** bestehen aus:

- einer Unity-Catalog-Verbindung, die Zugangsdaten speichert
- einer Ingestion-Pipeline, die die Quelle direkt abfragt
- Ziel-Streaming-Tabellen

**Streaming-Konnektoren** bestehen aus:

- einer Unity-Catalog-Verbindung mit Endpunkt-Zugangsdaten
- einer Pipeline, die kontinuierlich Nachrichten liest
- Streaming-Tabellen zur Speicherung

## Kernfunktionen

**Inkrementelle Aufnahme**: Änderungen werden nachverfolgt, sodass nachfolgende Läufe nur geänderte Daten aufnehmen. Der Ansatz hängt von den Fähigkeiten der Quelle ab.

**Orchestrierung**: Für jeden zur Pipeline hinzugefügten Zeitplan wird automatisch ein Job erstellt, wobei die Ingestion-Pipeline als Task läuft.

**Fehlerbehandlung**: automatische Wiederholungsversuche mit exponentiellem Backoff sowie Cursor-Tracking, um an der letzten erfolgreichen Position fortzusetzen.

## Programmatische Erstellung von Verbindungen

Verbindungen lassen sich erstellen über:

- Notebooks mit der Connections-API
- die Databricks CLI mit JSON-Schema entsprechend der REST-API
- Declarative Automation Bundles mit Pre-Deploy-Skripten

Hinweis: OAuth-basierte Konnektoren (Confluence, Jira, Slack, Zendesk) erfordern eine interaktive Anmeldung.

## Monitoring und Deployment

Die Plattform bietet Event-Logs, Cluster-Logs, Health-Metriken und Datenqualitäts-Monitoring. Das Deployment erfolgt über Declarative Automation Bundles mit Unterstützung für Versionskontrolle, Code-Review und CI/CD-Praktiken.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/  
**Stand:** 2026-08-07
