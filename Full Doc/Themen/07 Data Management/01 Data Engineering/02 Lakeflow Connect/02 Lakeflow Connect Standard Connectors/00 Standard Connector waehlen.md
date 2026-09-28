# Standard Connector wählen (Ingestion-Übersicht)

> Quelle: <https://docs.databricks.com/aws/en/ingestion/> — die Seite `/aws/en/ingestion/` rendert aktuell als *„Choose a standard connector"*.

Diese Seite hilft bei der Auswahl eines Standard-Ingestion-Connectors nach **Datenquelle** und gewünschtem **Grad an Anpassbarkeit vs. Automatisierung**.

---

## Ebenen des ETL-Stacks

Databricks bietet drei Ingestion-Produktebenen, geordnet von **am anpassbarsten** zu **am stärksten automatisiert**. Jede Ebene baut auf der vorherigen auf und erhöht den Automatisierungsgrad.

| Ebene | Beschreibung |
|---|---|
| **Structured Streaming** | Die Streaming-Engine von Apache Spark — bietet *"end-to-end fault tolerance with exactly-once processing guarantees"*. |
| **Lakeflow Pipelines** | Erweitert Structured Streaming um ein *"declarative framework for creating data pipelines"* und übernimmt Orchestrierung, Monitoring, Datenqualität und Fehlerbehandlung. |
| **Managed Connectors** | Voll verwaltete Connectors mit quellenspezifischer Authentifizierung, CDC, Edge-Case-Handling, langfristiger API-Pflege, automatischen Retries und automatischer Schema-Evolution. |

**Empfehlung laut Doku:** Mit der **am stärksten verwalteten Ebene beginnen** und nur dann eine Ebene tiefer gehen, wenn die Anforderungen dort nicht erfüllt werden.

> **Hinweis:** SQL-Beispiele für inkrementelle Ingestion aus Cloud-Objektspeicher verwenden die `CREATE STREAMING TABLE`-Syntax — die **empfohlene Alternative zu `COPY INTO`**.

---

## Connector-Auswahl nach Quelle

Die Doku-Tabelle listet Standard-Ingestion-Connectors nach Datenquelle und Grad der Pipeline-Anpassung. Spalten: **Quelle** · **More customization** (Structured Streaming) · **Some customization** (Lakeflow Pipelines) · **More automation** (Managed Connectors). Die Zellen führen jeweils die unterstützten Sprachen auf.

| Quelle | More customization | Some / More automation |
|---|---|---|
| **Cloud-Objektspeicher** | Auto Loader + Structured Streaming (Python, Scala) | Auto Loader + Lakeflow Pipelines (Python, Scala, SQL); Auto Loader + Databricks SQL (SQL) |
| **SFTP-Server** | Ingest files from SFTP servers (Python, SQL) | — |
| **Apache Kafka** | Structured Streaming (Python, Scala) | Lakeflow Pipelines (Python, Scala, SQL); Databricks SQL (SQL) |
| **Amazon Kinesis** | Structured Streaming (Python, Scala) | Lakeflow Pipelines (Python, Scala, SQL); Databricks SQL (SQL) |
| **Google Pub/Sub** | Structured Streaming (Python, Scala) | — |

### Auswahlkriterien

- Verfügbarkeit für die konkrete Datenquelle
- Benötigter Grad an Anpassbarkeit
- Automatisierungswunsch
- Benötigter Sprach-Support (Python / Scala / SQL)

---

## Einordnung im Projekt

- Detaillierter Methodenvergleich (Auto Loader / `COPY INTO` / CTAS+`spark.read` / CDF / `MERGE INTO`): siehe `03 Incremental Batch Ingestion/00 Overview.md` und `04 Streaming Ingestion/01 Data Ingestion.md`.
- `read_files` als SQL-Schnittstelle zu Auto Loader: siehe `05 Working with Files/_read_files.md`.
- `COPY INTO`-Sprachreferenz: siehe `06 DML Statements/_copy_into.md`.
- Weitere (nicht-Standard-)Ingestion-Features (Lakehouse Federation, Zerobus, Delta Sharing, Marketplace): siehe `03 Other Ingestion Features.md`.
