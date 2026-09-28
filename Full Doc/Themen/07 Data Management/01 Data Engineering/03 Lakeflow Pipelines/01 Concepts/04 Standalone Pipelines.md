# Standalone Pipelines

Referenz zum Konzept "Standalone Pipeline" im Vergleich zu Lakeflow-Pipelines, basierend auf `https://docs.databricks.com/aws/en/ldp/concepts/standalone-pipelines` (Text zusätzlich per Azure/Microsoft-Learn-Spiegelseite `learn.microsoft.com/en-us/azure/databricks/ldp/concepts/standalone-pipelines` wörtlich gegengeprüft).

## Abschnittsübersicht

1. [Zwei Wege, Materialized Views und Streaming Tables zu bauen](#zwei-wege)
2. [Standalone-Pipeline im Detail](#standalone-detail)
3. [Lakeflow-Pipeline im Detail](#lakeflow-detail)
4. [Pipeline-Typ-Label in der UI](#typ-label)
5. [Wann Standalone, wann Lakeflow?](#wann-was)
6. [Vergleichstabelle](#vergleichstabelle)
7. [Quellen](#quellen)

---

## <a id="zwei-wege">1. Zwei Wege, Materialized Views und Streaming Tables zu bauen</a>

Databricks bietet zwei Wege, um Materialized Views und Streaming Tables zu erstellen: Standalone-Pipelines oder Lakeflow-Pipelines. Beide laufen auf derselben deklarativen Engine und erzeugen von Unity Catalog verwaltete Tabellen. Der Unterschied liegt darin, wie viel von der Pipeline selbst autoriert und betrieben wird.

## <a id="standalone-detail">2. Standalone-Pipeline im Detail</a>

Eine **Standalone**-Materialized-View oder -Streaming-Table ist ein einzelnes Dataset, das mit SQL-Syntax definiert wird. Databricks erstellt und verwaltet im Hintergrund automatisch eine Pipeline, um es zu aktualisieren. Standalone-Datasets werden erstellt und aktualisiert aus:

- einem Databricks-SQL-Warehouse, oder
- einem Notebook auf Serverless General Compute mittels `spark.sql()`.

## <a id="lakeflow-detail">3. Lakeflow-Pipeline im Detail</a>

Eine **Lakeflow-Pipeline** ist eine Pipeline, die als Einheit autoriert und betrieben wird. Sie kann viele Datasets enthalten, in SQL und Python, mit Abhängigkeitsorchestrierung, Lineage und pipeline-weiten operativen Funktionen.

## <a id="typ-label">4. Pipeline-Typ-Label in der UI</a>

Wird eine standalone Materialized View oder Streaming Table erstellt, erscheint die dahinterliegende, verwaltete Pipeline auf der Seite **Jobs & Pipelines** mit dem Pipeline-Typ `MV/ST`. Datasets, die in einer Lakeflow-Pipeline definiert sind, tragen den Pipeline-Typ `ETL`.

## <a id="wann-was">5. Wann Standalone, wann Lakeflow?</a>

### Standalone-Pipelines verwenden, wenn:

- Abfragen mit einer einzigen Materialized View oder Streaming Table beschleunigt oder Daten transformiert werden.
- Aus einem Databricks-SQL-Warehouse, dem SQL-Editor oder einem Notebook auf Serverless General Compute gearbeitet wird und Refreshes über `SCHEDULE`, `TRIGGER ON UPDATE` oder einen SQL-Task in einem Job geplant werden.
- Keine Sinks, keine Multi-Stage-Orchestrierung und keine anderen reinen Pipeline-Funktionen benötigt werden.

### Lakeflow-Pipelines verwenden, wenn:

- Eine mehrstufige Pipeline mit Zwischen-Datasets aufgebaut wird, bei der Databricks Abhängigkeiten und Lineage über die Datasets hinweg verwaltet. Zwischen-Datasets können dabei entweder im Katalog veröffentlicht oder privat innerhalb der Pipeline gehalten werden.
- Tabellen und Flows in Python autoriert werden.
- In externe Delta-Tabellen oder Event-Streaming-Ziele über Sinks (`create_sink()` oder `foreach_batch_sink()`) geschrieben wird.
- Change Data Capture aus einem Datenbank-Snapshot mittels `create_auto_cdc_from_snapshot_flow()` angewendet wird.
- Triggered- oder Continuous-Ausführung über die gesamte Pipeline hinweg gewünscht ist.

## <a id="vergleichstabelle">6. Vergleichstabelle</a>

| Eigenschaft | Standalone Streaming Table / Materialized View | Pipeline Streaming Table / Materialized View |
|---|---|---|
| Authoring-Schnittstelle | SQL-Syntax, über ein Databricks-SQL-Warehouse oder mit `spark.sql()` in einem Notebook auf Serverless General Compute | SQL und Python |
| Umfang | Ein Dataset, in einer von Databricks verwalteten Pipeline | Viele Datasets in einer Pipeline, mit Abhängigkeitsorchestrierung und Lineage |
| Ausführung | Triggered, mit `SCHEDULE`, `TRIGGER ON UPDATE` oder einem SQL-Task | Triggered oder Continuous |
| Nur-Pipeline-Funktionen | — | Sinks, `create_auto_cdc_from_snapshot_flow()`, private Datasets |
| Pipeline-Typ-Label | `MV/ST` | `ETL` |
| Verschieben zwischen Pipelines | Nicht unterstützt; die Tabelle muss in der Ziel-Pipeline neu erstellt werden | Unterstützt |

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/concepts/standalone-pipelines
- https://learn.microsoft.com/en-us/azure/databricks/ldp/concepts/standalone-pipelines (Gegenprüfung)
