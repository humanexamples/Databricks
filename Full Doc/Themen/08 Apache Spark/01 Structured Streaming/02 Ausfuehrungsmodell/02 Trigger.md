# Structured Streaming Trigger-Intervalle konfigurieren — Referenz

Dieses Dokument beschreibt, wie Trigger-Intervalle bei Structured Streaming konfiguriert werden: die verfügbaren Trigger-Modi (Unspecified, Processing Time, Available Now, Real-time Mode, Continuous), Details zu `processingTime` und `AvailableNow` inklusive unterstützter Datenquellen, den Real-time Mode, wie Cloud-Storage-Kosten kontrolliert werden, sowie wie sich Trigger-Intervalle zwischen Läufen mit demselben Checkpoint ändern lassen. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/triggers`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte (die GCP-Originalseite lieferte über WebFetch nur eine gekürzte Fassung).

## Abschnittsübersicht

1. [Übersicht der Trigger-Modi](#uebersicht)
2. [processingTime: Zeitbasierte Trigger-Intervalle](#processing-time)
3. [AvailableNow: Inkrementelle Batch-Verarbeitung](#available-now)
4. [realTime: Operative Workloads mit ultra-niedriger Latenz](#real-time)
5. [Cloud-Storage-Kosten kontrollieren](#kosten)
6. [Trigger-Intervalle zwischen Läufen ändern](#intervall-aendern)
7. [Quellen](#quellen)

---

## <a id="uebersicht">1. Übersicht der Trigger-Modi</a>

Apache Spark Structured Streaming verarbeitet Daten inkrementell. Trigger-Intervalle steuern, wie häufig Structured Streaming auf neue Daten prüft. Trigger-Intervalle lassen sich für Near-Realtime-Verarbeitung, geplante Datenbank-Refreshes oder Batch-Verarbeitung aller neuen Daten eines Tages oder einer Woche konfigurieren.

Da Auto Loader Structured Streaming zum Laden von Daten verwendet, verschafft das Verständnis der Funktionsweise von Triggern die größtmögliche Flexibilität, um Kosten bei der Datenaufnahme mit der gewünschten Häufigkeit zu kontrollieren.

**Wichtig:** Databricks empfiehlt, einen Trigger-Modus zu wählen, der Latenz und Kosten für den jeweiligen Anwendungsfall ausbalanciert. Andernfalls können beim Cloud-Provider unerwartete Storage-Kosten entstehen. Details siehe Abschnitt [Cloud-Storage-Kosten kontrollieren](#kosten).

Die folgende Tabelle fasst die bei Structured Streaming verfügbaren Trigger-Modi zusammen:

| Trigger-Modus | Syntax-Beispiel (Python) | Am besten geeignet für |
|---|---|---|
| Unspecified (Standard) | N/A | Allgemeines Streaming mit 3–5 Sekunden Latenz. Entspricht einem `processingTime`-Trigger mit 0-ms-Intervallen. Die Stream-Verarbeitung läuft kontinuierlich, solange neue Daten eintreffen. |
| Processing Time | `.trigger(processingTime='10 seconds')` | Ausbalancieren von Kosten und Performance. Reduziert Overhead, indem verhindert wird, dass das System zu häufig auf Daten prüft. |
| Available Now | `.trigger(availableNow=True)` | Geplante, inkrementelle Batch-Verarbeitung. Verarbeitet so viele Daten wie zum Zeitpunkt des Auslösens des Streaming-Jobs verfügbar sind. |
| Real-time Mode | `.trigger(realTime='5 minutes')` | Operative Workloads mit ultra-niedriger Latenz, die Sub-Sekunden-Verarbeitung erfordern, etwa Betrugserkennung oder Echtzeit-Personalisierung. `'5 minutes'` gibt die Länge eines Micro-Batches an. 5 Minuten werden verwendet, um den Overhead pro Batch (z. B. Query-Kompilierung) zu minimieren. |
| Continuous | `.trigger(continuous='1 second')` | Nicht unterstützt. Dies ist ein experimentelles Feature aus Spark OSS. Stattdessen sollte der Real-time Mode verwendet werden. |

**Hinweis (Serverless Compute):** Auf Serverless Compute werden nur `Trigger.AvailableNow()` und `Trigger.Once()` unterstützt. Databricks empfiehlt `Trigger.AvailableNow()`.

Für kontinuierliches Streaming auf Serverless Compute sollte "Triggered vs. continuous pipeline mode" im Continuous Mode verwendet werden.

Siehe dazu auch die Dokumentation zu Streaming-Einschränkungen ("Streaming limitations") unter Serverless Compute.

## <a id="processing-time">2. processingTime: Zeitbasierte Trigger-Intervalle</a>

Structured Streaming bezeichnet zeitbasierte Trigger-Intervalle als "fixed interval micro-batches" (feste Micro-Batch-Intervalle). Mit dem Schlüsselwort `processingTime` wird eine Zeitdauer als String angegeben, etwa `.trigger(processingTime='10 seconds')`.

Die Konfiguration dieses Intervalls bestimmt, wie häufig das System prüft, ob neue Daten eingetroffen sind. Die Processing Time sollte so konfiguriert werden, dass Latenzanforderungen und die Rate, mit der Daten in der Quelle eintreffen, ausbalanciert werden.

## <a id="available-now">3. AvailableNow: Inkrementelle Batch-Verarbeitung</a>

**Wichtig:** In Databricks Runtime 11.3 LTS und höher ist `Trigger.Once` veraltet (deprecated). Für alle inkrementellen Batch-Verarbeitungs-Workloads sollte `Trigger.AvailableNow` verwendet werden.

Die Trigger-Option `AvailableNow` konsumiert alle verfügbaren Datensätze als inkrementellen Batch, wobei sich die Batch-Größe mit Optionen wie `maxBytesPerTrigger` konfigurieren lässt. Die Größenoptionen variieren je nach Datenquelle.

### Unterstützte Datenquellen

`Trigger.AvailableNow` wird für inkrementelle Batch-Verarbeitung aus vielen Structured-Streaming-Quellen unterstützt. Die folgende Tabelle enthält die minimal unterstützte Databricks-Runtime-Version, die für jede Datenquelle erforderlich ist:

| Quelle | Minimal unterstützte Databricks-Runtime-Version |
|---|---|
| File-Quellen (JSON, Parquet usw.) | 9.1 LTS |
| Delta Lake | 10.4 LTS |
| Auto Loader | 10.4 LTS |
| Apache Kafka | 10.4 LTS |
| Kinesis | 13.1 |
| OpenSharing (`responseFormat=delta`; `responseFormat=parquet` erfordert `delta-sharing-client` 1.4.0 oder höher) | 18.0 |

## <a id="real-time">4. realTime: Operative Workloads mit ultra-niedriger Latenz</a>

Der Real-time Mode für Structured Streaming erreicht eine End-to-End-Latenz von unter 1 Sekunde im Tail-Bereich, im häufigen Fall liegt sie bei rund 300 ms. Weitere Details zur effektiven Konfiguration und Nutzung des Real-time Mode finden sich in der separaten Doku-Seite "Real-time mode in Structured Streaming".

Apache Spark hat ein zusätzliches Trigger-Intervall, bekannt als "Continuous Processing". Dieser Modus ist seit Spark 2.3 als experimentell eingestuft. Databricks unterstützt oder empfiehlt diesen Modus nicht. Für Use Cases mit niedriger Latenz sollte stattdessen der Real-time Mode verwendet werden.

**Hinweis:** Der Continuous-Processing-Modus dieser Seite ist nicht mit Continuous Processing in Spark Declarative Pipelines (bzw. Lakeflow Declarative Pipelines) zu verwechseln.

## <a id="kosten">5. Cloud-Storage-Kosten kontrollieren</a>

Wird standardmäßig kein Trigger-Modus gesetzt, setzt Structured Streaming den Trigger-Modus auf `processingTime` mit einem Intervall von `0`, was alle paar Millisekunden auf neue Daten prüft. Dies kann pro Tag ein hohes Volumen an Cloud-Storage-API-Aufrufen erzeugen und zu unerwarteten Kosten beim Cloud-Provider führen.

Databricks empfiehlt, einen für die jeweiligen Latenz- und Kostenanforderungen passenden Trigger-Modus zu konfigurieren. Siehe [processingTime](#processing-time) für Informationen zur Konfiguration eines zeitbasierten Trigger-Intervalls.

## <a id="intervall-aendern">6. Trigger-Intervalle zwischen Läufen ändern</a>

Das Trigger-Intervall lässt sich zwischen Läufen ändern, während derselbe Checkpoint weiterverwendet wird.

### Verhalten beim Ändern von Intervallen

Stoppt eine Structured-Streaming-Query, während gerade ein Micro-Batch verarbeitet wird, muss dieser Micro-Batch abgeschlossen werden, bevor das neue Trigger-Intervall greift. Nach dem Ändern des Trigger-Intervalls kann es vorkommen, dass ein Micro-Batch noch mit der zuvor angegebenen Konfiguration verarbeitet wird. Im Folgenden das erwartete Verhalten nach einem Übergang:

- **Vom zeitbasierten Intervall zu `AvailableNow`:** Ein Micro-Batch kann als inkrementeller Batch verarbeitet werden, bevor alle verfügbaren Datensätze verarbeitet sind.
- **Von `AvailableNow` zum zeitbasierten Intervall:** Die Verarbeitung kann für alle Datensätze fortgesetzt werden, die verfügbar waren, als der letzte `AvailableNow`-Job ausgelöst wurde.

### Wiederherstellung nach Query-Fehlern

Wird versucht, nach einem Query-Fehler mit einem inkrementellen Batch wiederherzustellen, löst eine Änderung des Trigger-Intervalls das Problem nicht. Der vorherige, nicht erfolgreiche Batch muss abgeschlossen werden, da Structured Streaming idempotente Micro-Batches voraussetzt. Siehe dazu die Fehlertoleranz-Semantik von Apache Spark ("fault tolerance semantics for Apache Spark").

Zur Behebung des Fehlers sollte die Compute-Kapazität hochskaliert werden, etwa durch Vergrößern der Worker-Knoten. In seltenen Fällen kann es nötig sein, den Stream mit einem neuen Checkpoint neu zu starten.

---

## <a id="quellen">7. Quellen</a>

- Configure Structured Streaming trigger intervals (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/triggers
- Configure Structured Streaming trigger intervals (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/triggers

**Stand:** 2026-08-22.
