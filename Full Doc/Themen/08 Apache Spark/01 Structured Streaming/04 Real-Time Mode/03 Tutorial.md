# Tutorial: Einen Real-Time-Streaming-Workload ausführen — Referenz

Dieses Dokument ist eine Schritt-für-Schritt-Anleitung, um die erste Real-Time-Mode-Streaming-Query in einem Notebook auszuführen. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/tutorial`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte.

## Abschnittsübersicht

1. [Einleitung](#einleitung)
2. [Voraussetzungen](#voraussetzungen)
3. [Schritt 1: Ein Notebook erstellen](#schritt-1)
4. [Schritt 2: Eine Real-Time-Mode-Query ausführen](#schritt-2)
5. [Den Code verstehen](#code-verstehen)
6. [Schritt 3: Ergebnisse validieren](#schritt-3)
7. [Quellen](#quellen)

---

## <a id="einleitung">1. Einleitung</a>

Real-Time Mode ermöglicht Streaming mit ultra-niedriger Latenz — mit einer End-to-End-Latenz von bis zu fünf Millisekunden — und eignet sich damit ideal für operative Workloads wie Betrugserkennung und Echtzeit-Personalisierung. Dieses Tutorial führt durch das Einrichten der ersten Real-Time-Streaming-Query anhand eines einfachen Beispiels.

Für konzeptionelle Informationen zu Real-Time Mode, wann er eingesetzt werden sollte und welche Features unterstützt werden, siehe die Datei `Konzepte.md`. Für Konfigurationsanforderungen siehe die Datei `Setup.md`.

## <a id="voraussetzungen">2. Voraussetzungen</a>

Vor Beginn muss sichergestellt sein, dass Berechtigungen zum Erstellen eines klassischen Compute-Clusters mit der in `Setup.md` beschriebenen Konfiguration vorhanden sind. Alternativ kann der Workspace-Administrator gebeten werden, einen Real-Time-Mode-Cluster einzurichten.

## <a id="schritt-1">3. Schritt 1: Ein Notebook erstellen</a>

Notebooks bieten eine interaktive Umgebung zum Entwickeln und Testen von Streaming-Queries. Das Notebook wird verwendet, um die Real-Time-Query zu schreiben und die Ergebnisse laufend aktualisiert zu sehen.

Zum Erstellen eines Notebooks:

1. In der Seitenleiste auf **New** klicken, dann auf **Notebook**.
2. Im Compute-Dropdown-Menü den Real-Time-Mode-Cluster auswählen.
3. **Python** oder **Scala** als Standardsprache auswählen.

## <a id="schritt-2">4. Schritt 2: Eine Real-Time-Mode-Query ausführen</a>

Den folgenden Code in eine Notebook-Zelle kopieren und ausführen. Dieses Beispiel verwendet eine Rate-Quelle, die Zeilen mit einer festgelegten Rate erzeugt, und zeigt die Ergebnisse in Echtzeit an.

**Hinweis:** Die `display`-Funktion mit `realTime`-Trigger ist ab Databricks Runtime 17.1 verfügbar.

### Python

```python
inputDF = (
  spark
  .readStream
  .format("rate")
  .option("numPartitions", 2)
  .option("rowsPerSecond", 1)
  .load()
)
display(inputDF, realTime="5 minutes", outputMode="update")
```

**Scala** (aus der AWS-Doku ergänzt):

```scala
import org.apache.spark.sql.streaming.Trigger
import org.apache.spark.sql.streaming.OutputMode

val inputDF = spark
  .readStream
  .format("rate")
  .option("numPartitions", 2)
  .option("rowsPerSecond", 1)
  .load()
display(inputDF, trigger=Trigger.RealTime(), outputMode=OutputMode.Update())
```

Nach dem Ausführen des Codes erscheint eine Tabelle, die sich in Echtzeit aktualisiert, sobald neue Zeilen erzeugt werden. Die Tabelle zeigt eine Spalte `timestamp` und eine Spalte `value`, die sich mit jeder Zeile erhöht.

## <a id="code-verstehen">5. Den Code verstehen</a>

Der obige Code demonstriert die wesentlichen Bestandteile einer Real-Time-Streaming-Query. Die folgenden Tabellen erklären die wichtigsten Parameter und was sie steuern:

### Python

| Parameter | Beschreibung |
| --- | --- |
| `format("rate")` | Verwendet die Rate-Quelle, eine eingebaute Quelle, die Zeilen mit konfigurierbarer Rate erzeugt. Nützlich zum Testen ohne externe Abhängigkeiten. |
| `numPartitions` | Legt die Anzahl der Partitionen für die generierten Daten fest. |
| `rowsPerSecond` | Steuert, wie viele Zeilen pro Sekunde erzeugt werden. |
| `realTime="5 minutes"` | Aktiviert Real-Time Mode. Das Intervall gibt an, wie oft die Query den Fortschritt checkpointet. Längere Intervalle bedeuten selteneres Checkpointing, aber potenziell längere Recovery-Zeiten nach Fehlern. |
| `outputMode="update"` | Real-Time Mode erfordert den Update-Output-Modus. |

### Scala

| Parameter | Beschreibung |
| --- | --- |
| `format("rate")` | Verwendet die Rate-Quelle, eine eingebaute Quelle, die Zeilen mit konfigurierbarer Rate erzeugt. Nützlich zum Testen ohne externe Abhängigkeiten. |
| `numPartitions` | Legt die Anzahl der Partitionen für die generierten Daten fest. |
| `rowsPerSecond` | Steuert, wie viele Zeilen pro Sekunde erzeugt werden. |
| `Trigger.RealTime()` | Aktiviert Real-Time Mode mit dem Standard-Checkpoint-Intervall. Es kann auch ein Intervall angegeben werden, z. B. `Trigger.RealTime("5 minutes")`. |
| `OutputMode.Update()` | Real-Time Mode erfordert den Update-Output-Modus. |

## <a id="schritt-3">6. Schritt 3: Ergebnisse validieren</a>

Beim Ausführen der Query erzeugt die `display`-Funktion eine Tabelle, die sich in Echtzeit aktualisiert, sobald die Rate-Quelle neue Zeilen erzeugt. Jede Zeile enthält:

- Einen Zeitstempel dafür, wann die Zeile von der Rate-Quelle erzeugt wurde.
- Einen monoton steigenden Zähler, der sich mit jeder neuen Zeile erhöht.

Die Tabelle aktualisiert sich fortlaufend mit minimaler Latenz und demonstriert, wie Real-Time Mode Daten verarbeitet, sobald sie verfügbar werden. Das ist der Kernvorteil von Real-Time Mode — die Fähigkeit, Daten sofort zu sehen und darauf zu reagieren, statt auf die Batch-Verarbeitung zu warten.

---

## <a id="quellen">7. Quellen</a>

- Tutorial: Run a real-time streaming workload (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/real-time/tutorial
- Tutorial: Run a real-time streaming workload (Mirror, Azure, verifiziert/vollständig abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/tutorial
- Tutorial: Run a real-time streaming workload (AWS): https://docs.databricks.com/aws/en/structured-streaming/real-time/tutorial

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
