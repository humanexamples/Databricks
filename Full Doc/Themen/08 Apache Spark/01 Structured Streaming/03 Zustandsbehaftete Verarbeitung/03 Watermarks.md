# Watermarks — Referenz

Dieses Dokument beschreibt Watermark-Konzepte in Structured Streaming (allgemeiner Kontext, nicht Lakeflow-Pipelines) und gibt Empfehlungen zur Verwendung von Watermarks bei gängigen zustandsbehafteten Streaming-Operationen. Verifiziert per `WebFetch` gegen die GCP-Original-URL sowie ergänzend gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/watermarks`), die eine vollständige, wörtliche Wiedergabe des Roh-Inhalts lieferte.

## Abschnittsübersicht
1. [Überblick](#ueberblick)
2. [Was ist ein Watermark?](#was-ist-watermark)
3. [Wie beeinflussen Watermarks Verarbeitungszeit und Durchsatz?](#latenz-durchsatz)
4. [Watermarks und Output-Modus für Windowed Aggregations](#windowed-aggregations)
5. [Watermarks und Output-Modi für Stream-Stream-Joins](#stream-stream-joins)
6. [Verspätete-Daten-Schwellenwert mit Multiple-Watermarks-Policy steuern](#multiple-watermarks)
7. [Watermarks auf distinct-Operationen anwenden](#distinct)
8. [Duplikate innerhalb des Watermarks entfernen](#drop-duplicates)
9. [Anwendungsbeispiele](#use-cases)
10. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick</a>

Streaming-Queries akkumulieren im Laufe der Zeit Zustandsdaten ("state data"). Watermarks entfernen automatisch alte Zustandsdaten, um Speicherfehler und erhöhte Verarbeitungslatenz zu verhindern.

## <a id="was-ist-watermark">2. Was ist ein Watermark?</a>

Während der Verarbeitung hält Structured Streaming über Micro-Batches hinweg Zustand vor. Streaming-Queries nutzen diesen Zustand, um Ergebnisse inkrementell zu aktualisieren, statt nach jedem Micro-Batch alles neu zu berechnen. Watermarks steuern den Schwellenwert, ab dem eine Query aufhört, eine Zustandsentität zu verarbeiten.

Gängige Beispiele für Zustandsentitäten sind:

- Aggregationen über ein Zeitfenster.
- Eindeutige Keys in einem Join zwischen zwei Streams.

Um einen Watermark auf einem Streaming-DataFrame zu deklarieren, werden ein Zeitstempel-Feld und ein Schwellenwert für Verspätung ("lateness threshold") angegeben. Sobald neue Daten eintreffen, verfolgt der State-Manager den jüngsten Zeitstempel im angegebenen Feld und verarbeitet nur Datensätze innerhalb des Verspätungs-Schwellenwerts.

Queries verarbeiten immer Datensätze, die innerhalb des Schwellenwerts eintreffen. Queries können auch Datensätze verarbeiten, die außerhalb des Schwellenwerts eintreffen — dies ist jedoch nicht garantiert.

Das folgende Beispiel wendet einen 10-Minuten-Watermark-Schwellenwert auf eine gefensterte Zählung ("windowed count") an:

### Python

```python
from pyspark.sql.functions import window

(df
  .withWatermark("event_time", "10 minutes")
  .groupBy(
    window("event_time", "5 minutes"),
    "id")
  .count()
)
```

In diesem Beispiel:

- Die Spalte `event_time` wird verwendet, um einen 10-Minuten-Watermark und ein 5-Minuten-Tumbling-Window zu definieren.
- Für jede beobachtete `id` wird pro nicht überlappendem 5-Minuten-Fenster eine Zählung erstellt.
- Zustandsinformationen werden für jede Zählung so lange vorgehalten, bis das Ende des Fensters 10 Minuten älter ist als der zuletzt beobachtete `event_time`.

**Wichtig:** In einer `groupBy()`- und `window()`-Operation müssen Spalten über ihren Namen referenziert werden, `"<colName>"` oder `col("<colName>")`, damit der Event-Time-Marker erhalten bleibt. In Scala kann dafür auch `$colName` verwendet werden.

## <a id="latenz-durchsatz">3. Wie beeinflussen Watermarks Verarbeitungszeit und Durchsatz?</a>

Output-Modi steuern, wann eine Query mit Watermarks Daten in die Senke schreibt. Watermarks sind essenziell für die Durchsatzsteuerung bei zustandsbehafteter Verarbeitung, da sie die Gesamtmenge der im Speicher gehaltenen Zustandsinformationen reduzieren. Nicht alle Output-Modi werden für alle zustandsbehafteten Operationen unterstützt. Siehe [Watermarks und Output-Modus für Windowed Aggregations](#windowed-aggregations).

Die Wahl der Watermark-Dauer bringt Abwägungen mit sich:

- Kürzere Watermarks senken die Query-Latenz, da Queries weniger Zustandsinformationen speichern und Ergebnisse nach jeder abgeschlossenen Watermark-Dauer schreiben. Kurze Watermarks haben jedoch eine geringe Toleranz gegenüber verspäteten Daten.
- Längere Watermarks bieten eine hohe Toleranz gegenüber verspäteten Daten. Sie erhöhen jedoch die Query-Latenz, da Queries mehr Zustandsinformationen speichern und länger warten müssen, bevor Ergebnisse geschrieben werden.

## <a id="windowed-aggregations">4. Watermarks und Output-Modus für Windowed Aggregations</a>

Die folgende Tabelle zeigt das Verarbeitungsverhalten für Queries mit Aggregation über einen Zeitstempel und einen Watermark:

| Output-Modus | Verhalten |
| --- | --- |
| Append | Die Query schreibt Zeilen in die Zieltabelle, nachdem der Watermark-Schwellenwert überschritten wurde. Alle Schreibvorgänge werden gemäß dem Verspätungs-Schwellenwert verzögert. Alter Aggregationszustand wird nach Überschreiten des Schwellenwerts verworfen. |
| Update | Die Query schreibt Zeilen in die Zieltabelle, sobald Ergebnisse berechnet werden, und kann Zeilen aktualisieren bzw. überschreiben, sobald neue Daten eintreffen. Alter Aggregationszustand wird nach Überschreiten des Schwellenwerts verworfen. |
| Complete | Aggregationszustand wird nicht verworfen. Die Query schreibt bei jedem Trigger die Zieltabelle vollständig neu. |

## <a id="stream-stream-joins">5. Watermarks und Output-Modi für Stream-Stream-Joins</a>

Joins zwischen mehreren Streams unterstützen ausschließlich den Append-Modus. Queries schreiben pro Batch die gematchten Datensätze.

Für Inner Joins empfiehlt Databricks, auf jeder Streaming-Datenquelle einen Watermark-Schwellenwert zu setzen, damit die Query Zustandsinformationen für alte Datensätze verwerfen kann. Ohne Watermarks versucht Structured Streaming, bei jedem Trigger jeden Key von beiden Seiten des Joins zu joinen, was die Performance beeinträchtigen kann.

Für Outer Joins ist ein Watermark verpflichtend. Bleibt ein Datensatz ungematcht, schreibt die Query für diesen Key einen Null-Wert. Da Joins nur den Append-Modus unterstützen, werden ungematchte Datensätze erst geschrieben, nachdem der Verspätungs-Schwellenwert überschritten wurde.

## <a id="multiple-watermarks">6. Verspätete-Daten-Schwellenwert mit Multiple-Watermarks-Policy steuern</a>

Bei mehreren Structured-Streaming-Eingaben können mehrere Watermarks gesetzt werden, um die Toleranzschwellen für verspätete Daten zu steuern. Watermarks ermöglichen es, Zustandsinformationen und Latenz zu kontrollieren.

Eine Streaming-Query kann mehrere Eingabe-Streams haben, die per Union oder Join zusammengeführt werden. Für zustandsbehaftete Operationen kann jeder der Eingabe-Streams einen unterschiedlichen Schwellenwert für die Toleranz gegenüber verspäteten Daten benötigen. Diese Schwellenwerte werden mit `withWatermark("eventTime", delay)` auf jedem Eingabe-Stream einzeln angegeben. Das folgende Beispiel zeigt eine Query mit [Stream-Stream-Joins](https://databricks.com/blog/2018/03/13/introducing-stream-stream-joins-in-apache-spark-2-3.html).

### Python

```python
input_stream1 = ...      # delays up to 1 hour
input_stream2 = ...      # delays up to 2 hours

(input_stream1.withWatermark("eventTime1", "1 hour")
  .join(
    input_stream2.withWatermark("eventTime2", "2 hours"),
    joinCondition)
)
```

Während der Ausführung der Query mit zustandsbehafteten Operationen verfolgt Structured Streaming für jeden Eingabe-Stream individuell die maximale Event-Zeit, berechnet daraus anhand der jeweiligen Verzögerung Watermarks und bestimmt einen einzigen globalen Watermark. Standardmäßig verwendet Structured Streaming das Minimum als globalen Watermark. Fällt ein Stream hinter die anderen zurück, verhindert ein minimaler globaler Watermark, dass die Query Daten fälschlicherweise als verspätet markiert. Dies kann etwa auftreten, wenn einer der Streams aufgrund von Upstream-Fehlern keine Daten mehr empfängt. Der globale Watermark bewegt sich sicher im Tempo des langsamsten Streams und verzögert bei Bedarf die Query-Ausgabe.

Um die Latenz zu reduzieren, kann `spark.sql.streaming.multipleWatermarkPolicy` auf `max` gesetzt werden (Standard ist `min`), um den Watermark des schnellsten Streams als globalen Watermark zu verwenden. Diese Konfiguration verwirft jedoch Daten der langsameren Streams. Databricks empfiehlt, diese Konfiguration mit Vorsicht anzuwenden.

## <a id="distinct">7. Watermarks auf distinct-Operationen anwenden</a>

Die `distinct`-Operation verfolgt jeden eindeutigen Datensatz im Zustand. Ohne Watermark wächst der Zustand unbegrenzt und kann zu Speicherproblemen führen. Um den Zustand zu begrenzen und alte Datensätze nach Überschreiten des Schwellenwerts zu entfernen, wird ein Watermark auf ein Zeitstempel-Feld angewendet.

Das folgende Beispiel wendet einen Watermark auf eine `distinct`-Operation an:

### Python

```python
streamingDf = spark.readStream. ...  # columns: eventTime, id, value, ...

# Apply watermark before distinct operation
(streamingDf
  .withWatermark("eventTime", "1 hour")
  .distinct()
)
```

In diesem Beispiel entfernt die Streaming-Query doppelte Datensätze, die innerhalb einer Stunde nach dem zuletzt beobachteten `eventTime` eintreffen. Die Query verwirft Zustandsinformationen zur Deduplizierung, nachdem der Schwellenwert überschritten wurde.

**Wichtig:** Um bestimmte Spalten statt aller Spalten zu deduplizieren, sollten `dropDuplicates()` oder `dropDuplicatesWithinWatermark()` anstelle von `distinct` verwendet werden. Siehe [Duplikate innerhalb des Watermarks entfernen](#drop-duplicates).

## <a id="drop-duplicates">8. Duplikate innerhalb des Watermarks entfernen</a>

In Databricks Runtime 13.3 LTS oder höher kann ein eindeutiger Identifikator verwendet werden, um Datensätze innerhalb eines Watermark-Schwellenwerts zu deduplizieren.

Structured Streaming garantiert Exactly-once-Verarbeitung, dedupliziert Datensätze aus Datenquellen jedoch nicht automatisch. `dropDuplicatesWithinWatermark` entfernt Duplikate anhand eines beliebigen Feldes, selbst wenn sich Felder zwischen doppelten Datensätzen unterscheiden, etwa Event-Zeit oder Ankunftszeit.

Mit `dropDuplicatesWithinWatermark` deduplizieren Queries immer Datensätze, die innerhalb des Watermark-Schwellenwerts eintreffen. Queries können auch Datensätze deduplizieren, die außerhalb des Schwellenwerts eintreffen — dies ist jedoch nicht garantiert. Um sicherzustellen, dass Queries alle Duplikate entfernen, muss der Watermark-Schwellenwert größer als die maximale Zeitstempeldifferenz zwischen doppelten Events gesetzt werden.

Für die Verwendung der Methode `dropDuplicatesWithinWatermark` muss ein Watermark angegeben werden:

### Python

```python
streamingDf = spark.readStream. ...

# deduplicate using guid column with watermark based on eventTime column
(streamingDf
  .withWatermark("eventTime", "10 hours")
  .dropDuplicatesWithinWatermark(["guid"])
)
```

## <a id="use-cases">9. Anwendungsbeispiele</a>

Die folgenden Beispiele zeigen fortgeschrittene Windowing-Anwendungsfälle:

### Tumbling Windows zur Berechnung stündlicher Verkaufssummen

Tumbling Windows haben feste Größe und nicht überlappende Intervalle. Jede Eingabezeile gehört zu genau einem Fenster. Tumbling Windows eignen sich, um diskrete Zeitraum-Aggregationen zu berechnen, etwa stündliche Verkaufssummen:

#### Python

```python
from pyspark.sql.functions import window, sum

hourly_sales = (orders
  .withWatermark("timestamp", "1 hour")
  .groupBy(window("timestamp", "1 hour"))
  .agg(sum("amount").alias("total_sales"))
)
```

In diesem Beispiel:

- `window("timestamp", "1 hour")` gruppiert Bestellungen in nicht überlappende 1-Stunden-Intervalle, etwa 5–6 Uhr und 6–7 Uhr.
- `withWatermark("timestamp", "1 hour")` hält das Aggregat jedes Fensters so lange im Zustand, bis der Fensterend-Zeitstempel 1 Stunde älter ist als der maximale Bestellungs-Zeitstempel.

### Sliding Windows zur Berechnung rollierender Aggregate

Sliding Windows haben feste Größe, aber die Intervalle können sich überlappen. Eine einzelne Zeile kann zu mehreren Fenstern gehören. Sliding Windows eignen sich, um rollierende Aggregate zu berechnen, etwa Verkäufe über einen rollierenden 6-Stunden-Zeitraum:

#### Python

```python
from pyspark.sql.functions import window, sum

rolling_sales = (orders
  .withWatermark("timestamp", "1 hour")
  .groupBy(window("timestamp", "6 hours", slideDuration="1 hour"))
  .agg(sum("amount").alias("total_sales"))
)
```

In diesem Beispiel:

- `window("timestamp", "6 hours", slideDuration="1 hour")` gruppiert Bestellungen in 6-Stunden-Intervalle, die sich stündlich verschieben, z. B. 5–11 Uhr und 6–12 Uhr.
- `withWatermark("timestamp", "1 hour")` hält das Aggregat jedes Fensters so lange im Zustand, bis der Fensterend-Zeitstempel 1 Stunde älter ist als der maximale Bestellungs-Zeitstempel.
- `slideDuration` muss kleiner oder gleich `windowDuration` sein.

### Session Windows zur Prüfung der Nutzeraktivität

Session Windows haben keine feste Größe. Ein Fenster öffnet sich, sobald eine Zeile eintrifft, und schließt nach einer Lückendauer ("gap duration"), in der keine neuen Zeilen eintreffen. Session Windows eignen sich, um Aktivitätsausbrüche zwischen langen Leerlaufphasen zu aggregieren, etwa die Seitenaufrufe eines Nutzers innerhalb eines 30-Minuten-Zeitraums:

#### Python

```python
from pyspark.sql.functions import session_window, sum

sessionized_page_views = (activity
  .withWatermark("timestamp", "1 hour")
  .groupBy("user_id", session_window("timestamp", gapDuration="30 minutes"))
  .agg(sum("page_views").alias("total_page_views"))
)
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.functions.{session_window, sum}

val sessionizedPageViews = activity
  .withWatermark("timestamp", "1 hour")
  .groupBy($"user_id", session_window($"timestamp", "30 minutes"))
  .agg(sum($"page_views").alias("total_page_views"))
```

In diesem Beispiel:

- `session_window("timestamp", gapDuration="30 minutes")` öffnet ein Fenster, sobald der erste Seitenaufruf eintrifft. Jeder weitere Seitenaufruf, der innerhalb von 30 Minuten eintrifft, verlängert das Fenster. Trifft innerhalb von 30 Minuten kein Seitenaufruf ein, schließt das Fenster, und der nächste Seitenaufruf startet ein neues Fenster.
- `withWatermark("timestamp", "1 hour")` hält das Aggregat jeder Session so lange im Zustand, bis der Fensterend-Zeitstempel 1 Stunde älter ist als der maximale Seitenaufruf-Zeitstempel.
- Das `timeColumn`-Argument von `window()` und `session_window()` muss vom Typ `TimestampType` oder `TimestampNTZType` sein.
- Um Fenster auf Basis der Verarbeitungszeit statt der Event-Zeit zu definieren, kann `current_timestamp()` verwendet werden.
- Fensterdauern können von Mikrosekunden bis zu Tagen gesetzt werden. Monatsdauern und länger werden nicht unterstützt.
- Der `complete`-Output-Modus mit gefensterten Aggregationen hält den gesamten Fensterzustand unbegrenzt vor. Der `append`-Output-Modus mit einem geeigneten Watermark begrenzt das Zustandswachstum und verhindert Speicherprobleme bei großen Datasets. Weitere Details zum Verhalten der Output-Modi finden sich unter [Watermarks und Output-Modus für Windowed Aggregations](#windowed-aggregations).

---

## <a id="quellen">10. Quellen</a>
- Apply watermarks to control data processing thresholds (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/watermarks
- Apply watermarks to control data processing thresholds (Mirror, verifiziert/vollständig abgerufen, Azure): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/watermarks

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

Alle Watermark-Beispiele oben verwenden die DataFrame-API (`withWatermark` in Python/Scala). Das SQL Language Manual definiert für Lakeflow-Streaming-Tables eine eigene deklarative `WATERMARK`-Klausel direkt innerhalb der `FROM STREAM`-Quelle — funktional äquivalent zu `withWatermark(eventTime, delay)`, aber rein in SQL formuliert: `WATERMARK [named_expression] DELAY OF [interval]`.

**Watermark auf einer bestehenden Zeitstempelspalte:**

```sql
CREATE OR REFRESH STREAMING TABLE window_agg_1
AS SELECT window(ts, '10 seconds') as w, count(*) as CNT
FROM STREAM stream_source WATERMARK ts DELAY OF INTERVAL 10 SECONDS AS stream
GROUP BY window(ts, '10 seconds');
```

**Watermark auf einer erst abgeleiteten Zeitstempelspalte** — hier wird `ts_str` zunächst per `to_timestamp()` in einen Timestamp umgewandelt und der Watermark direkt auf dieser abgeleiteten Spalte `ts` definiert:

```sql
CREATE OR REFRESH STREAMING TABLE window_agg_2
AS SELECT window(ts, '10 seconds') as w, count(*) as CNT
FROM STREAM stream_source WATERMARK to_timestamp(ts_str) AS ts DELAY OF INTERVAL 10 SECONDS AS stream
GROUP BY window(ts, '10 seconds');
```

Beide Beispiele zeigen dasselbe Konzept wie die `withWatermark`-Beispiele in Abschnitt 2, angewendet auf eine mit `window()` gefensterte Zählung innerhalb einer per SQL definierten Streaming Table.

**Quelle:** https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-watermark
