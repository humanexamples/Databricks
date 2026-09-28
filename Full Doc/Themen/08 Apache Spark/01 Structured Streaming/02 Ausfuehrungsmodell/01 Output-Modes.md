# Output Mode für Structured Streaming — Referenz

Dieses Dokument beschreibt, wie ein Output Mode für zustandsbehaftetes Streaming ausgewählt wird: was Output Mode bedeutet, welche drei Modi verfügbar sind, welche Produktionsüberlegungen (Anwendungssemantik, Operator-/Senken-Kompatibilität, Latenz und Kosten) relevant sind, sowie ein durchgerechnetes Beispiel, das zeigt, wie Output Mode mit Watermarks bei zustandsbehaftetem Streaming zusammenwirkt. Verifiziert per `WebFetch` sowohl gegen die GCP-Originalseite (`docs.databricks.com/gcp/en/structured-streaming/output-mode`) als auch gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/output-mode`); beide lieferten inhaltsgleiche, vollständige Fassungen, wobei die Azure-Version einen zusätzlichen Hinweis zu Materialized Views enthält.

## Abschnittsübersicht

1. [Was ist Output Mode?](#was-ist-output-mode)
2. [Verfügbare Output-Modi](#verfuegbare-modi)
3. [Produktionsüberlegungen](#produktionsueberlegungen)
4. [Konfigurationsbeispiele](#konfigurationsbeispiele)
5. [Beispiel: Zustandsbehaftetes Streaming und Output-Modi](#beispiel)
6. [Quellen](#quellen)

---

## <a id="was-ist-output-mode">1. Was ist Output Mode?</a>

Dieser Artikel behandelt die Auswahl eines Output Mode für zustandsbehaftetes Streaming. Nur zustandsbehaftete Streams mit Aggregationen erfordern eine Output-Mode-Konfiguration.

Joins unterstützen nur den Append-Output-Mode, und der Output Mode hat keinen Einfluss auf Deduplizierung. Die beliebigen zustandsbehafteten Operatoren `mapGroupsWithState` und `flatMapGroupsWithState` geben Datensätze nach ihrer eigenen benutzerdefinierten Logik aus, sodass der Output Mode des Streams ihr Verhalten nicht beeinflusst.

Bei zustandslosem Streaming verhalten sich alle Output-Modi gleich.

Um den Output Mode korrekt zu konfigurieren, müssen zustandsbehaftetes Streaming, Watermarks und Trigger verstanden werden. Siehe dazu folgende Artikel:

- "What is stateful streaming?"
- "Apply watermarks to control data processing thresholds"
- "Configure Structured Streaming trigger intervals" (siehe `Trigger.md` in diesem Verzeichnis)

Der Output Mode einer Structured-Streaming-Query bestimmt, welche Datensätze die Operatoren der Query bei jedem Trigger ausgeben. Es gibt drei Arten von Datensätzen, die ausgegeben werden können:

- Datensätze, die durch zukünftige Verarbeitung nicht mehr verändert werden.
- Die Datensätze, die sich seit dem letzten Trigger verändert haben.
- Alle Datensätze in der State-Tabelle.

Zu wissen, welche Art von Datensätzen ausgegeben werden soll, ist für zustandsbehaftete Operatoren wichtig, da sich eine bestimmte, von einem zustandsbehafteten Operator erzeugte Zeile von Trigger zu Trigger ändern kann. Wenn beispielsweise ein Streaming-Aggregations-Operator mehr Zeilen für ein bestimmtes Fenster empfängt, können sich dessen Aggregationswerte über mehrere Trigger hinweg ändern.

Bei zustandslosen Operatoren wirkt sich die Unterscheidung zwischen Datensatztypen nicht auf das Verhalten des Operators aus. Die Datensätze, die ein zustandsloser Operator während eines Triggers ausgibt, sind stets die während dieses Triggers verarbeiteten Quelldatensätze.

## <a id="verfuegbare-modi">2. Verfügbare Output-Modi</a>

Es gibt drei Output-Modi, die einem Operator mitteilen, welche Datensätze er während eines bestimmten Triggers ausgeben soll:

| Output Mode | Beschreibung |
|---|---|
| **Append Mode (Standard)** | Standardmäßig laufen Streaming-Queries im Append Mode. In diesem Modus geben Operatoren nur Zeilen aus, die sich in zukünftigen Triggern nicht mehr ändern. Zustandsbehaftete Operatoren nutzen den Watermark, um zu bestimmen, wann dies der Fall ist. |
| **Update Mode** | Im Update Mode geben Operatoren alle Zeilen aus, die sich während des Triggers geändert haben, selbst wenn sich der ausgegebene Datensatz in einem nachfolgenden Trigger noch ändern könnte. |
| **Complete Mode** | Complete Mode funktioniert nur mit Streaming-Aggregationen. Im Complete Mode werden alle jemals vom Operator erzeugten Ergebniszeilen stromabwärts ausgegeben. |

## <a id="produktionsueberlegungen">3. Produktionsüberlegungen</a>

Bei vielen zustandsbehafteten Streaming-Operationen muss zwischen Append und Update Mode gewählt werden. Die folgenden Abschnitte skizzieren Überlegungen, die diese Entscheidung beeinflussen können.

**Hinweis:** Complete Mode hat gewisse Anwendungsfälle, kann aber mit zunehmender Datenmenge schlecht performen. Databricks empfiehlt die Verwendung von Materialized Views, um die mit Complete Mode verbundenen semantischen Garantien bei gleichzeitig inkrementeller Verarbeitung für viele zustandsbehaftete Operationen zu erhalten. Siehe die Dokumentation zu Materialized Views.

### Anwendungssemantik

Anwendungssemantik beschreibt, wie nachgelagerte Anwendungen die Streaming-Daten nutzen.

Wenn nachgelagerte Dienste für jeden nachgelagerten Schreibvorgang eine einzelne Aktion ausführen müssen, sollte in den meisten Fällen der Append Mode verwendet werden. Gibt es beispielsweise einen nachgelagerten Benachrichtigungsdienst, der für jeden neu in die Senke geschriebenen Datensatz eine Benachrichtigung sendet, stellt der Append Mode sicher, dass jeder Datensatz nur einmal geschrieben wird. Der Update Mode schreibt den Datensatz jedes Mal, wenn sich die Zustandsinformation ändert, was zu zahlreichen Aktualisierungen führen würde.

Wenn nachgelagerte Dienste aktuelle Ergebnisse benötigen, sorgt der Update Mode dafür, dass die Senke so aktuell wie möglich bleibt. Beispiele sind ein Machine-Learning-Modell, das Features in Echtzeit liest, oder ein Analytics-Dashboard, das Echtzeit-Aggregate verfolgt.

### Operator- und Senken-Kompatibilität

Structured Streaming unterstützt nicht alle in Apache Spark verfügbaren Operationen, und manche Streaming-Operationen werden nicht in allen Output-Modi unterstützt. Weitere Informationen zu Operator-Einschränkungen finden sich in der OSS-Streaming-Dokumentation (Abschnitt "Unsupported Operations").

Nicht alle Senken unterstützen alle Output-Modi. Kafka unterstützt alle Output-Modi. Delta Lake, das allen von Unity Catalog verwalteten Tabellen zugrunde liegt, unterstützt Append und Complete Mode, aber nicht Update Mode. Für ein Verhalten ähnlich dem Update Mode mit Delta-Lake-Senken siehe "Merge in streaming".

Weitere Informationen zur Senken-Kompatibilität finden sich in der OSS-Streaming-Dokumentation (Abschnitt "Output Sinks").

### Latenz und Kosten

Der Output Mode beeinflusst, wie viel Zeit vergehen muss, bevor ein Datensatz geschrieben wird, und die Häufigkeit sowie die Menge der geschriebenen Daten können sich auf die mit Streaming-Pipelines verbundenen Kosten auswirken.

Der Append Mode zwingt zustandsbehaftete Operatoren dazu, Ergebnisse erst auszugeben, nachdem die zustandsbehafteten Ergebnisse finalisiert wurden — das dauert mindestens so lange wie die Watermark-Verzögerung. Eine Watermark-Verzögerung von `1 hour` im Append Output Mode bedeutet, dass Datensätze mindestens eine Stunde Verzögerung haben, bevor sie stromabwärts ausgegeben werden.

Der Update Mode führt zu einem Schreibvorgang pro Trigger pro Aggregatwert. Wenn die Senke pro Schreibvorgang pro Datensatz abrechnet, kann dies teuer werden, wenn sich Datensätze mehrfach aktualisieren, bevor die Watermark-Verzögerung verstreicht.

## <a id="konfigurationsbeispiele">4. Konfigurationsbeispiele</a>

Die folgenden Codebeispiele zeigen die Konfiguration des Output Mode für Streaming-Updates an Unity-Catalog-Tabellen:

**Python**

```python
# Append output mode (default)
(df.writeStream
  .toTable("target_table")
)

# Append output mode (same as default behavior)
(df.writeStream
  .outputMode("append")
  .toTable("target_table")
)

# Update output mode
(df.writeStream
  .outputMode("update")
  .toTable("target_table")
)

# Complete output mode
(df.writeStream
  .outputMode("complete")
  .toTable("target_table")
)
```

Siehe die OSS-Dokumentation für `PySpark DataStreamWriter.outputMode` bzw. `Scala DataStreamWriter.outputMode`.

## <a id="beispiel">5. Beispiel: Zustandsbehaftetes Streaming und Output-Modi</a>

Das folgende Beispiel soll dabei helfen nachzuvollziehen, wie Output Mode mit Watermarks bei zustandsbehaftetem Streaming zusammenwirkt.

Betrachtet wird eine Streaming-Aggregation, die den in einem Geschäft stündlich erzielten Gesamtumsatz berechnet, mit einer Watermark-Verzögerung von 15 Minuten. Der erste Microbatch verarbeitet folgende Datensätze:

- $15 um 14:40 Uhr
- $10 um 14:30 Uhr
- $30 um 15:10 Uhr

An diesem Punkt liegt der Watermark der Engine bei 14:55 Uhr, da 15 Minuten (die Verzögerung) von der maximal gesehenen Zeit (15:10 Uhr) abgezogen werden. Der Streaming-Aggregations-Operator hat folgendes in seinem Zustand:

- `[2pm, 3pm]`: $25
- `[3pm, 4pm]`: $30

Die folgende Tabelle skizziert, was in jedem Output Mode passieren würde:

| Output Mode | Ergebnis und Begründung |
|---|---|
| Append | Der Streaming-Aggregations-Operator gibt nichts stromabwärts aus. Das liegt daran, dass sich beide Fenster noch ändern könnten, wenn mit einem nachfolgenden Trigger neue Werte auftauchen: Der Watermark von 14:55 Uhr zeigt an, dass noch Datensätze nach 14:55 Uhr eintreffen könnten, und diese Datensätze könnten entweder in das Fenster `[2pm, 3pm]` oder das Fenster `[3pm, 4pm]` fallen. |
| Update | Der Operator gibt beide Datensätze aus, da beide Datensätze Aktualisierungen erhalten haben. |
| Complete | Der Operator gibt alle Datensätze aus. |

Nun empfange der Stream einen weiteren Datensatz:

- $20 um 15:20 Uhr

Der Watermark aktualisiert sich auf 15:05 Uhr, da die Engine 15 Minuten von 15:20 Uhr abzieht. An diesem Punkt hat der Streaming-Aggregations-Operator folgendes in seinem Zustand:

- `[2pm, 3pm]`: $25
- `[3pm, 4pm]`: $50

Die folgende Tabelle skizziert, was in jedem Output Mode passieren würde:

| Output Mode | Ergebnis und Begründung |
|---|---|
| Append | Der Streaming-Aggregations-Operator stellt fest, dass der Watermark von 15:05 Uhr größer ist als das Ende des Fensters `[2pm, 3pm]`. Per Definition des Watermarks kann sich dieses Fenster nicht mehr ändern, daher wird das Fenster `[2pm, 3pm]` ausgegeben. |
| Update | Der Streaming-Aggregations-Operator gibt das Fenster `[3pm, 4pm]` aus, da sich der Zustandswert von $30 auf $50 geändert hat. |
| Complete | Der Operator gibt alle Datensätze aus. |

Zusammengefasst verhalten sich zustandsbehaftete Operatoren in den Output-Modi wie folgt:

- Im Append Mode werden Datensätze einmalig nach der Watermark-Verzögerung geschrieben.
- Im Update Mode werden Datensätze geschrieben, die sich seit dem vorherigen Trigger geändert haben.
- Im Complete Mode werden alle jemals vom zustandsbehafteten Operator erzeugten Datensätze geschrieben.

---

## <a id="quellen">6. Quellen</a>

- Select an output mode for Structured Streaming (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/output-mode
- Select an output mode for Structured Streaming (Azure-Spiegelseite, vollständig als Rohtext abgerufen, inhaltsgleich, mit zusätzlichem Hinweis zu Materialized Views): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/output-mode

**Stand:** 2026-08-22.
