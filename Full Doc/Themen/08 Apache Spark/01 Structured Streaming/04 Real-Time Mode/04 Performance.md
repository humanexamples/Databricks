# Performance von Real-Time-Mode-Queries optimieren und überwachen — Referenz

Dieses Dokument beschreibt Compute-Tuning, Techniken zur Reduzierung der End-to-End-Latenz sowie Ansätze zur Messung der Query-Performance in Real-Time Mode. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/performance`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte.

## Abschnittsübersicht

1. [Compute-Tuning](#compute-tuning)
2. [Latenzoptimierung](#latenzoptimierung)
3. [Monitoring und Observability](#monitoring)
4. [Quellen](#quellen)

---

## <a id="compute-tuning">1. Compute-Tuning</a>

Bei der Konfiguration des Compute sollte Folgendes berücksichtigt werden:

- Anders als im Micro-Batch-Modus können Real-Time-Tasks im Leerlauf bleiben, während sie auf Daten warten — richtiges Sizing ist daher essenziell, um Ressourcenverschwendung zu vermeiden.
- Ein Ziel für die Cluster-Auslastung anstreben, z. B. 50 %, durch Abstimmung von:
    - `maxPartitions` (für Kafka)
    - `spark.sql.shuffle.partitions` (für Shuffle-Stages)
- Databricks empfiehlt, `maxPartitions` so zu setzen, dass jeder Task mehrere Kafka-Partitionen verarbeitet, um Overhead zu reduzieren.
- Task-Slots pro Worker an den Workload anpassen, für einfache einstufige Jobs.
- Bei Shuffle-intensiven Jobs experimentell die minimale Anzahl an Shuffle-Partitionen ermitteln, die Backlogs vermeidet, und davon ausgehend anpassen. Das Compute plant den Job nicht ein, wenn nicht genügend Slots vorhanden sind.

**Hinweis:** Ab Databricks Runtime 16.4 LTS verwenden alle Real-Time-Pipelines Checkpoint v2, um nahtlose Wechsel zwischen Real-Time- und Micro-Batch-Modus zu ermöglichen.

## <a id="latenzoptimierung">2. Latenzoptimierung</a>

Structured Streaming Real-Time Mode bietet optionale Techniken zur Reduzierung der End-to-End-Latenz. Keine davon ist standardmäßig aktiviert — sie müssen separat aktiviert werden.

- **Asynchronous progress tracking:** Verschiebt Schreibvorgänge in Offset- und Commit-Logs in einen asynchronen Thread und reduziert dadurch die Zeit zwischen Batches bei zustandslosen Queries.
- **Asynchronous state checkpointing:** Beginnt mit der Verarbeitung des nächsten Micro-Batches, sobald die Berechnung abgeschlossen ist, ohne auf das Abschließen des State-Checkpointing zu warten, wodurch die Latenz bei zustandsbehafteten Queries reduziert wird.

## <a id="monitoring">3. Monitoring und Observability</a>

In Real-Time Mode spiegeln traditionelle Batch-Dauer-Metriken die tatsächliche End-to-End-Latenz nicht wider. Die folgenden Ansätze dienen dazu, Latenz präzise zu messen und Engpässe in Queries zu identifizieren.

Die End-to-End-Latenz ist workload-spezifisch und lässt sich mitunter nur mit Business-Logik präzise messen. Wird z. B. der Quell-Zeitstempel in Kafka mit ausgegeben, lässt sich die Latenz als Differenz zwischen dem Ausgabe-Zeitstempel von Kafka und dem Quell-Zeitstempel berechnen.

### Eingebaute Metriken mit `StreamingQueryProgress`

Das Ereignis `StreamingQueryProgress` wird automatisch in den Driver-Logs protokolliert und ist über die `onQueryProgress()`-Callback-Funktion des `StreamingQueryListener` zugänglich. Dies ermöglicht es, programmatisch auf Fortschrittsereignisse zu reagieren, etwa um Metriken an ein externes Monitoring-System zu veröffentlichen. `QueryProgressEvent.json()` bzw. `toString()` enthalten folgende Real-Time-Mode-Metriken:

1. **Processing Latency** (`processingLatencyMs`). Die verstrichene Zeit zwischen dem Lesen eines Datensatzes durch die Real-Time-Mode-Query und dem Schreiben in die nächste Stage bzw. Downstream. Bei einstufigen Queries misst dies dieselbe Dauer wie die End-to-End-Latenz. Das System meldet diese Metrik pro Task.
2. **Source Queuing Latency** (`sourceQueuingLatencyMs`). Die verstrichene Zeit zwischen dem Schreiben eines Datensatzes auf einen Message Bus — z. B. der Log-Append-Zeitpunkt bei Kafka — und dem ersten Lesen des Datensatzes durch die Real-Time-Mode-Query. Das System meldet diese Metrik pro Task.
3. **End-to-End Latency** (`e2eLatencyMs`). Die Zeit zwischen dem Schreiben des Datensatzes auf einen Message Bus und dem Schreiben des Datensatzes Downstream durch die Real-Time-Mode-Query. Das System aggregiert diese Metrik pro Batch über alle von allen Tasks verarbeiteten Datensätze.

Beispiel:

```json
"rtmMetrics" : {
    "processingLatencyMs" : {
      "P0" : 0,
      "P50" : 0,
      "P90" : 0,
      "P95" : 0,
      "P99" : 0
    },
    "sourceQueuingLatencyMs" : {
      "P0" : 0,
      "P50" : 1,
      "P90" : 1,
      "P95" : 2,
      "P99" : 3
    },
    "e2eLatencyMs" : {
      "P0" : 0,
      "P50" : 1,
      "P90" : 1,
      "P95" : 2,
      "P99" : 4
    }
}
```

### Task-Auslastung überwachen (aus der AWS-Doku ergänzt)

Mit **`busyTimeFraction`** lässt sich prüfen, ob die Auslastung der Spark-Tasks den Durchsatz begrenzt:

- Werte **nahe 1**: Tasks sind voll ausgelastet; die Query braucht eventuell **mehr Compute**.
- **Niedrigere** Werte: Tasks verbringen mehr Zeit im Leerlauf oder blockiert.
- Wertebereich 0 bis 1, gemeldet **pro Stage und Task**.

Debug-Metriken **vor** dem Start der Streaming-Query aktivieren:

```python
spark.conf.set("spark.databricks.streaming.execution.enableDebugMetrics", "true")
```

Zugriff auf die Task-Metriken, zwei Wege:

**Raw Data:** Query starten oder neu starten. Nach einem Trigger unter der Query-Zelle **Raw Data** öffnen und `_taskMetrics` unter `latencies` suchen. Beispiel:

```json
{
  "latencies": {
    "_taskMetrics": {
      "stage_0_task_0": {
        "busyTimeFraction": 0.03
      }
    }
  }
}
```

**Python:** Nach einem Trigger über `lastProgress` auf `_taskMetrics` zugreifen:

```python
import json

task_metrics = json.loads(query.lastProgress.json)["latencies"]["_taskMetrics"]
print(task_metrics)
```

### Benutzerdefinierte Latenzmessung mit der Observe API

Die Observe API ermöglicht es, Latenz inline zu messen, ohne einen separaten Job zu starten. Ist ein Quell-Zeitstempel vorhanden, der die Ankunftszeit der Quelldaten annähert, lässt sich die Latenz pro Batch schätzen, indem vor der Senke ein Zeitstempel aufgezeichnet und die Differenz berechnet wird. Die Ergebnisse erscheinen in Fortschrittsberichten und stehen Listenern zur Verfügung.

### Python

```python
from datetime import datetime

from pyspark.sql.functions import avg, col, lit, max, percentile_approx, udf, unix_millis
from pyspark.sql.types import TimestampType

@udf(returnType=TimestampType())
def current_timestamp():
  return datetime.now()

# Query before outputting
.withColumn("temp-timestamp", current_timestamp())
.withColumn(
  "latency",
  unix_millis(col("temp-timestamp")).cast("long") - unix_millis(col("timestamp")).cast("long"))
.observe(
  "observedLatency",
  avg(col("latency")).alias("avg"),
  max(col("latency")).alias("max"),
  percentile_approx(col("latency"), lit(0.99), lit(150)).alias("p99"),
  percentile_approx(col("latency"), lit(0.5), lit(150)).alias("p50"))
.drop(col("latency"))
.drop(col("temp-timestamp"))
# Output part of the query. For example, .WriteStream, etc.
```

Beispiel-Ausgabe:

```json
"observedMetrics" : {
  "observedLatency" : {
    "avg" : 63.8369765176552,
    "max" : 219,
    "p99" : 154,
    "p50" : 49
  }
}
```

---

## <a id="quellen">4. Quellen</a>

- Optimize and monitor real-time mode query performance (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/real-time/performance
- Optimize and monitor real-time mode query performance (Mirror, Azure, verifiziert/vollständig abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/real-time/performance
- Optimize and monitor real-time mode query performance (AWS): https://docs.databricks.com/aws/en/structured-streaming/real-time/performance

**Stand:** 2026-08-22; Codebeispiele am 2026-09-28 gegen die AWS-Doku abgeglichen und ergänzt.
