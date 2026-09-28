# Serverless Compute — Best Practices

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/best-practices>

Empfehlungen, um Produktivität zu maximieren, Kosten zu senken und Zuverlässigkeit zu verbessern — für Notebooks, Jobs und Pipelines auf Serverless Compute.

## Migration zu Serverless

Details siehe [06 Migration von Classic zu Serverless.md](06%20Migration%20von%20Classic%20zu%20Serverless.md).

### Python-Paket-Versionierung

Abhängigkeiten in `requirements.txt` auf konkrete Versionen pinnen:

```
numpy==2.2.2
pandas==2.2.3
```

> *"If you don't specify a version, the package may resolve to a different version based on the serverless environment version, which can increase latency as new packages need to be installed."*

### Benennung temporärer Views

Serverless nutzt **Spark Connect** (Client-Server, wertet Temp-Views **lazy** aus). Für jeden Temp-View **eindeutige Namen** verwenden, um Fehler zu vermeiden — besonders in iterativem Code.

## Networking & Konnektivität

- **Kein VPC-Peering.** Alternativen: Private Endpoints zu VPC-internen Ressourcen; Private Endpoints zu AWS-managed Services; Firewall-Konfigurationen für Databricks-Serverless-Traffic.
- > *"Object storage services like Amazon S3 are regional services that do not use VPCs and are not affected by this limitation."*
- Für Enterprise-Apps und Managed Databases: **Lakeflow Connect**. Ausgehenden Traffic über **Egress Controls** überwachen/beschränken.

## Serverless Environment-Versionen

- Serverless verwendet **Environment-Versionen** statt klassischer Databricks-Runtime-Versionen.
- Stabile APIs bei unabhängigen Server-Upgrades; Rückwärtskompatibilität; **3-Jahre-Support-Lebenszyklus** ab Release; Performance-Verbesserungen und Security-Patches ohne Code-Änderungen.

## Dependency-Management

- *"Serverless compute does not support init scripts. Instead, use serverless environments to install and manage libraries."*
- Environments cachen installierte Pakete → geringere Startlatenz bei Folge-Runs.
- Für private Repositories: **pre-signed URLs** in den Environment-Einstellungen.

## Performance-Modi

| Modus | Am besten für | Startzeit | Kosten |
|---|---|---|---|
| **Performance-optimized** (Default) | Interaktive Workloads, Notebooks | schnell | höher |
| **Standard** | Batch-Jobs, Pipelines | 4–6 Minuten | *"can reduce costs by up to 70% compared to performance-optimized mode"* |

**Standard-Modus ist für Notebooks nicht verfügbar.**

## Streaming-Workloads

- Serverless unterstützt **nur `Trigger.AvailableNow`**; zeitbasierte Trigger werden nicht unterstützt (siehe [07 Streaming.md](07%20Streaming.md)).
- Speicherfehler vermeiden, indem Daten pro Micro-Batch begrenzt werden: `maxFilesPerTrigger`, `maxBytesPerTrigger`.
- > *"Each trigger processes all available data in the source, which can result in larger micro-batches than a time-based trigger would."*

## Debugging

Die **Spark UI ist nicht verfügbar.** Stattdessen das **Query Profile** (aus der Query History in der Databricks-UI) zur Performance-Analyse nutzen.

## Daten-Ingestion

- **SQL-basiert:** `COPY INTO`, Streaming Tables, Auto Loader (inkrementell aus Cloud-Speicher).
- **Alternativen:** Partner-Connect-Integrationen, File-Upload-UI, OpenSharing (Abfrage ohne Duplizierung), Lakehouse Federation (externe Datenbank-Abfragen).

## Nicht unterstützte Write-Targets

Wenn direktes Schreiben nicht unterstützt wird: **Unity Catalog Iceberg REST Catalog** nutzen, damit das Zielsystem direkt aus Databricks-Tabellen liest. Beispiel: Snowflake ist kein unterstützter Serverless-Sink, kann aber als Iceberg-Client Unity-Catalog-Tabellen lesen.

## Spark-Konfiguration

> *"Databricks has removed support for manually setting most Spark configurations."* Nicht unterstützte Konfigurationen führen zu Job-Fehlern. Liste der unterstützten Parameter in der Doku *Configure Spark properties for serverless notebooks and jobs*.

## Kosten-Monitoring

- Serverless Usage Policies zur Attribution
- Systemtabellen für Dashboards und Alerts
- Account-Level-Budget-Alerts
- Vorkonfigurierte Usage-Dashboards

## Verwandte Themen

- [06 Migration von Classic zu Serverless.md](06%20Migration%20von%20Classic%20zu%20Serverless.md) · [07 Streaming.md](07%20Streaming.md) · [09 Einschraenkungen.md](09%20Einschraenkungen.md)
