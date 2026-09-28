# Datenaufnahme in Databricks – Überblick

Databricks bietet unterschiedliche Ebenen für die Datenaufnahme (Ingestion) – von manuellem Streaming-Code bis zu vollständig verwalteten Konnektoren. Diese Seite gibt einen Überblick über die verfügbaren Ansätze und Werkzeuge.

## Die drei Ebenen des ETL-Stacks

Databricks organisiert Ingestion-Lösungen hierarchisch in drei Ebenen:

1. **Structured Streaming** – die Streaming-Engine von Apache Spark mit Exactly-once-Verarbeitungsgarantien über Spark-APIs.
2. **Lakeflow Pipelines** – ein deklaratives Framework, das Structured Streaming um Orchestrierung, Monitoring und Datenqualitätsmanagement erweitert.
3. **Managed Connectors** – vollständig verwaltete Lösungen für populäre Quellen; übernehmen Authentifizierung, CDC, Schema-Evolution und automatische Wiederholungsversuche.

Databricks empfiehlt, mit der am stärksten verwalteten Ebene zu beginnen und nur dann eine Ebene tiefer zu gehen, wenn die Anforderungen dies erfordern.

## Standard-Konnektoren nach Quelle

| Quelle | Verfügbar über | Sprachen |
| --- | --- | --- |
| Cloud Object Storage | Auto Loader (Structured Streaming, Lakeflow Pipelines, Databricks SQL) | Python, Scala, SQL |
| SFTP-Server | Datei-Ingestion | Python, SQL |
| Apache Kafka | Structured Streaming, Lakeflow Pipelines | – |
| Amazon Kinesis | Structured Streaming, Lakeflow Pipelines | – |
| Google Pub/Sub | Structured Streaming | – |

Jeder Konnektor bietet einen unterschiedlichen Grad an Anpassbarkeit – von "mehr Anpassung" bis "mehr Automatisierung".

## Empfehlung für SQL-Nutzer

Für eine skalierbare, inkrementelle Aufnahme aus Cloud-Speicher empfiehlt Databricks die Syntax `CREATE STREAMING TABLE` als Alternative zu `COPY INTO`.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/  
**Stand:** 2026-08-07
