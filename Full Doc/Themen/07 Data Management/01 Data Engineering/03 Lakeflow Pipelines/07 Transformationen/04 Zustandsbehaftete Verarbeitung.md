# Zustandsbehaftete Verarbeitung mit Watermarks optimieren — Referenz

Dieses Dokument beschreibt, wie Watermarks bei zustandsbehafteter Stream-Verarbeitung in Lakeflow-Declarative-Pipelines (LDP) eingesetzt werden — für Aggregationen, Joins und Deduplizierung. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/stateful-processing`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte.

## Abschnittsübersicht

1. [Was ist ein Watermark?](#was-ist-watermark)
2. [Wie ein Watermark definiert wird](#definition)
3. [Watermarks bei Stream-Stream-Joins](#stream-stream-joins)
4. [Windowed Aggregations mit Watermarks](#windowed-aggregations)
5. [Streaming-Datensätze deduplizieren](#deduplizierung)
6. [Pipeline-Konfiguration für zustandsbehaftete Verarbeitung optimieren](#konfiguration)
7. [Quellen](#quellen)

---

## <a id="was-ist-watermark">1. Was ist ein Watermark?</a>

**Hinweis:** Damit Queries mit Aggregationen inkrementell statt bei jedem Update vollständig neu berechnet werden, müssen Watermarks verwendet werden.

Ein *Watermark* ist ein Apache-Spark-Feature, das bei zustandsbehafteten Operationen wie Aggregationen einen zeitbasierten Schwellenwert für die Datenverarbeitung definiert. Eintreffende Daten werden verarbeitet, bis der Schwellenwert erreicht ist — an diesem Punkt wird das durch den Schwellenwert definierte Zeitfenster geschlossen. Watermarks helfen, Probleme bei der Query-Verarbeitung zu vermeiden, insbesondere bei großen Datasets oder lang laufenden Verarbeitungen — etwa hohe Latenz bei der Ergebniserzeugung oder sogar Out-of-Memory-(OOM)-Fehler aufgrund der Menge während der Verarbeitung im Zustand gehaltener Daten. Da Streaming-Daten inhärent ungeordnet eintreffen, unterstützen Watermarks zudem die korrekte Berechnung von Operationen wie Zeitfenster-Aggregationen.

## <a id="definition">2. Wie ein Watermark definiert wird</a>

Ein Watermark wird definiert, indem ein Zeitstempel-Feld und ein Wert angegeben werden, der den Zeitschwellenwert für *verspätete Daten* ("late data") repräsentiert. Daten gelten als verspätet, wenn sie nach dem definierten Zeitschwellenwert eintreffen. Ist der Schwellenwert z. B. auf 10 Minuten definiert, können Datensätze, die nach diesen 10 Minuten eintreffen, verworfen werden.

Da nach dem definierten Schwellenwert eintreffende Datensätze verworfen werden können, ist die Wahl eines Schwellenwerts, der Latenz- und Korrektheitsanforderungen ausbalanciert, wichtig. Ein kleinerer Schwellenwert führt dazu, dass Datensätze früher ausgegeben werden, erhöht aber auch die Wahrscheinlichkeit, dass verspätete Datensätze verworfen werden. Ein größerer Schwellenwert bedeutet eine längere Wartezeit, aber möglicherweise vollständigere Daten — und kann wegen der größeren Zustandsgröße zusätzliche Rechenressourcen erfordern. Da der optimale Schwellenwert von den Daten und Verarbeitungsanforderungen abhängt, sind Testen und Monitoring wichtig, um ihn zu bestimmen.

In Python wird die Funktion `withWatermark()` verwendet, in SQL die `WATERMARK`-Klausel:

```python
withWatermark("timestamp", "3 minutes")
```

```sql
WATERMARK timestamp DELAY OF INTERVAL 3 MINUTES
```

## <a id="stream-stream-joins">3. Watermarks bei Stream-Stream-Joins</a>

Für Stream-Stream-Joins muss auf **beiden** Seiten des Joins ein Watermark sowie eine Zeitintervall-Klausel definiert werden. Da jede Join-Quelle nur eine unvollständige Sicht auf die Daten hat, wird die Zeitintervall-Klausel benötigt, um der Streaming-Engine mitzuteilen, wann keine weiteren Matches mehr möglich sind. Die Zeitintervall-Klausel muss dieselben Felder verwenden wie die Watermarks.

Da beide Streams zu unterschiedlichen Zeiten unterschiedliche Schwellenwerte für Watermarks benötigen können, müssen die Streams keine identischen Schwellenwerte haben. Um Datenverlust zu vermeiden, pflegt die Streaming-Engine einen globalen Watermark basierend auf dem langsamsten Stream.

Das folgende Beispiel joint einen Stream von Ad-Impressions mit einem Stream von Nutzer-Klicks auf Anzeigen. Ein Klick muss innerhalb von 3 Minuten nach der Impression erfolgen. Nach Ablauf des 3-Minuten-Zeitintervalls werden Zeilen aus dem Zustand, die nicht mehr gematcht werden können, verworfen:

```python
from pyspark import pipelines as dp

dp.create_streaming_table("adImpressionClicks")
@dp.append_flow(target = "adImpressionClicks")
def joinClicksAndImpressions():
  clicksDf = (read_stream("rawClicks")
    .withWatermark("clickTimestamp", "3 minutes")
  )
  impressionsDf = (read_stream("rawAdImpressions")
    .withWatermark("impressionTimestamp", "3 minutes")
  )
  joinDf = impressionsDf.alias("imp").join(
  clicksDf.alias("click"),
  expr("""
    imp.userId = click.userId AND
    clickAdId = impressionAdId AND
    clickTimestamp >= impressionTimestamp AND
    clickTimestamp <= impressionTimestamp + interval 3 minutes
  """),
  "inner"
  ).select("imp.userId", "impressionAdId", "clickTimestamp", "impressionSeconds")

  return joinDf
```

```sql
CREATE OR REFRESH STREAMING TABLE
  silver.adImpressionClicks
AS SELECT
  imp.userId, impressionAdId, clickTimestamp, impressionSeconds
FROM STREAM
  (bronze.rawAdImpressions)
WATERMARK
  impressionTimestamp DELAY OF INTERVAL 3 MINUTES imp
INNER JOIN STREAM
  (bronze.rawClicks)
WATERMARK clickTimestamp DELAY OF INTERVAL 3 MINUTES click
ON
  imp.userId = click.userId
AND
  clickAdId = impressionAdId
AND
  clickTimestamp >= impressionTimestamp
AND
  clickTimestamp <= impressionTimestamp + interval 3 minutes
```

## <a id="windowed-aggregations">4. Windowed Aggregations mit Watermarks</a>

Eine verbreitete zustandsbehaftete Operation auf Streaming-Daten ist eine Windowed Aggregation. Sie ähnelt gruppierten Aggregationen, mit dem Unterschied, dass Aggregatwerte für die Menge der Zeilen zurückgegeben werden, die Teil des definierten Fensters sind.

Ein Fenster lässt sich mit einer bestimmten Länge definieren, und eine Aggregationsoperation kann auf allen Zeilen dieses Fensters ausgeführt werden. Spark Streaming unterstützt drei Fenstertypen:

- **Tumbling (feste) Fenster:** eine Serie fester, nicht überlappender, zusammenhängender Zeitintervalle. Ein Eingabedatensatz gehört nur zu einem einzigen Fenster.
- **Sliding Windows:** ähnlich zu Tumbling Windows, ebenfalls fester Größe, aber Fenster können sich überlappen — ein Datensatz kann in mehrere Fenster fallen.

Treffen Daten nach dem Ende des Fensters plus der Länge des Watermarks ein, werden für dieses Fenster keine neuen Daten mehr akzeptiert, das Aggregationsergebnis wird ausgegeben und der Zustand für das Fenster verworfen.

Das folgende Beispiel berechnet alle 5 Minuten eine Summe der Impressions über ein festes Fenster. Im `SELECT`-Teil wird der Alias `impressions_window` verwendet, das Fenster selbst wird Teil der `GROUP BY`-Klausel — es muss auf derselben Zeitstempel-Spalte basieren wie der Watermark, hier `clickTimestamp`:

```sql
CREATE OR REFRESH STREAMING TABLE
  gold.adImpressionSeconds
AS SELECT
  impressionAdId, window(clickTimestamp, "5 minutes") as impressions_window, sum(impressionSeconds) as totalImpressionSeconds
FROM STREAM
  (silver.adImpressionClicks)
WATERMARK
  clickTimestamp DELAY OF INTERVAL 3 MINUTES
GROUP BY
  impressionAdId, window(clickTimestamp, "5 minutes")
```

Ein ähnliches Python-Beispiel berechnet den Profit über stündliche feste Fenster:

```python
from pyspark import pipelines as dp

@dp.table()
def profit_by_hour():
  return (
    spark.readStream.table("sales")
      .withWatermark("timestamp", "1 hour")
      .groupBy(window("timestamp", "1 hour").alias("time"))
      .aggExpr("sum(profit) AS profit")
  )
```

## <a id="deduplizierung">5. Streaming-Datensätze deduplizieren</a>

Structured Streaming bietet Exactly-once-Verarbeitungsgarantien, dedupliziert Datensätze aus Datenquellen aber nicht automatisch. Da viele Message Queues At-least-once-Garantien haben, sollten Duplikate beim Lesen aus einer solchen Message Queue erwartet werden. Die Funktion `dropDuplicatesWithinWatermark()` dedupliziert Datensätze anhand beliebiger angegebener Felder und entfernt Duplikate aus einem Stream, selbst wenn sich manche Felder unterscheiden (z. B. Event Time oder Arrival Time). Zur Nutzung von `dropDuplicatesWithinWatermark()` muss ein Watermark angegeben werden — alle Duplikate, die innerhalb des vom Watermark angegebenen Zeitraums eintreffen, werden verworfen.

Geordnete Daten sind wichtig, da nicht-geordnete Daten dazu führen können, dass der Watermark-Wert fälschlich zu weit vorspringt — trifft dann älteren Daten ein, gelten diese als verspätet und werden verworfen. Die Option `withEventTimeOrder` verarbeitet den initialen Snapshot geordnet nach dem im Watermark angegebenen Zeitstempel. Sie lässt sich im Code, der das Dataset definiert, oder in den Pipeline-Einstellungen über `spark.databricks.delta.withEventTimeOrder.enabled` deklarieren:

```json
{
  "spark_conf": {
    "spark.databricks.delta.withEventTimeOrder.enabled": "true"
  }
}
```

**Hinweis:** Die `withEventTimeOrder`-Option wird nur mit Python unterstützt.

Im folgenden Beispiel werden Daten geordnet nach `clickTimestamp` verarbeitet, und Datensätze, die innerhalb von 5 Sekunden zueinander eintreffen und doppelte `userId`- und `clickAdId`-Spalten enthalten, werden verworfen:

```python
clicksDedupDf = (
  spark.readStream.table
    .option("withEventTimeOrder", "true")
    .table("rawClicks")
    .withWatermark("clickTimestamp", "5 seconds")
    .dropDuplicatesWithinWatermark(["userId", "clickAdId"]))
```

## <a id="konfiguration">6. Pipeline-Konfiguration für zustandsbehaftete Verarbeitung optimieren</a>

Um Produktionsproblemen und übermäßiger Latenz vorzubeugen, empfiehlt Databricks, RocksDB-basiertes State Management für zustandsbehaftete Stream-Verarbeitung zu aktivieren — besonders, wenn die Verarbeitung eine große Menge Zwischenzustand speichern muss.

**Serverless Pipelines verwalten State-Store-Konfigurationen automatisch.**

RocksDB-basiertes State Management lässt sich über folgende Konfiguration vor dem Deployment einer Pipeline aktivieren:

```json
{
  "configuration": {
    "spark.sql.streaming.stateStore.providerClass": "com.databricks.sql.streaming.state.RocksDBStateStoreProvider"
  }
}
```

Für zustandsbehaftete Operationen, die Millisekunden-Latenz erfordern, siehe die separate Doku-Seite "Use real-time mode in Lakeflow pipelines".

---

## <a id="quellen">7. Quellen</a>

- Optimize stateful processing with watermarks (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/ldp/stateful-processing
- Optimize stateful processing with watermarks (AWS): https://docs.databricks.com/aws/en/ldp/stateful-processing

**Stand:** 2026-08-19.
