# Structured Streaming Batch-Größe konfigurieren — Referenz

Dieses Dokument beschreibt, wie mittels Admission Controls eine konsistente Batch-Größe für Streaming-Queries erreicht wird: die Optionen `maxFilesPerTrigger` und `maxBytesPerTrigger`, deren Zusammenspiel, sowie Hinweise zu Kafka und anderen Quellen mit eigenen Rate-Limit-Optionen. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/batch-size`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte (die GCP-Originalseite lieferte über WebFetch nur eine gekürzte Fassung).

## Abschnittsübersicht

1. [Übersicht](#uebersicht)
2. [Eingaberate mit maxFilesPerTrigger begrenzen](#max-files-per-trigger)
3. [Eingaberate mit maxBytesPerTrigger begrenzen](#max-bytes-per-trigger)
4. [Mehrere Eingaberaten gemeinsam festlegen](#kombination)
5. [Eingaberaten für andere Structured-Streaming-Quellen begrenzen](#andere-quellen)
6. [Quellen](#quellen)

---

## <a id="uebersicht">1. Übersicht</a>

Diese Seite erklärt, wie Admission Controls verwendet werden, um eine konsistente Batch-Größe für Streaming-Queries zu erreichen.

Admission Controls begrenzen die Eingaberate für Structured-Streaming-Queries, was helfen kann, eine konsistente Batch-Größe beizubehalten und zu verhindern, dass große Batches zu Spill und kaskadierenden Verzögerungen bei der Micro-Batch-Verarbeitung führen.

Databricks bietet für Delta Lake und Auto Loader dieselben Optionen zur Kontrolle der Structured-Streaming-Batch-Größe.

**Hinweis:** Admission-Control-Einstellungen können geändert werden, ohne den Checkpoint einer Streaming-Query zurückzusetzen. Siehe dazu "Wiederherstellung nach Änderungen an einer Structured-Streaming-Query" (siehe `Checkpoints.md` in diesem Verzeichnis, Abschnitt 3).

Das Ändern von Admission-Control-Einstellungen zur Vergrößerung oder Verkleinerung der Batch-Größe hat Auswirkungen auf die Performance. Um den Workload zu optimieren, kann es nötig sein, die Compute-Konfiguration anzupassen.

**Warnung:** Ist ein Micro-Batch geplant, wenn ein Stream stoppt, wirkt sich eine Änderung an den Admission Controls erst aus, nachdem der geplante Micro-Batch abgeschlossen ist. Stoppt ein Stream beispielsweise nach einer fehlgeschlagenen Transaktion, kann es nötig sein, den Checkpoint zu löschen, um den Stream zu zwingen, die Transaktion mit den neuen Admission Controls erneut zu verarbeiten. Dieses Verhalten tritt auf, weil Structured Streaming idempotent ist und Micro-Batches bei wiederholten Ausführungen dieselben Daten enthalten müssen. Siehe dazu "Structured Streaming semantics" (Basic Semantics) in der Spark-Dokumentation.

## <a id="max-files-per-trigger">2. Eingaberate mit maxFilesPerTrigger begrenzen</a>

Das Setzen von `maxFilesPerTrigger` (bzw. `cloudFiles.maxFilesPerTrigger` für Auto Loader) gibt eine Obergrenze für die Anzahl der in jedem Micro-Batch verarbeiteten Dateien an. Sowohl für Delta Lake als auch für Auto Loader liegt der Standardwert bei 1000. (Zu beachten ist, dass diese Option auch in Apache Spark für andere File-Quellen existiert, wo standardmäßig kein Maximum gilt.)

## <a id="max-bytes-per-trigger">3. Eingaberate mit maxBytesPerTrigger begrenzen</a>

Das Setzen von `maxBytesPerTrigger` (bzw. `cloudFiles.maxBytesPerTrigger` für Auto Loader) legt ein "Soft Max" für die in jedem Micro-Batch verarbeitete Datenmenge fest. Das bedeutet, dass ein Batch ungefähr diese Datenmenge verarbeitet und unter Umständen mehr als das Limit verarbeitet, um die Streaming-Query voranzubringen, wenn die kleinste Eingabeeinheit größer als dieses Limit ist. Für diese Einstellung gibt es keinen Standardwert.

Wird beispielsweise ein Byte-String wie `10g` angegeben, um jeden Microbatch auf 10 GB Daten zu begrenzen, und es liegen Dateien von je 3 GB vor, verarbeitet Databricks 12 GB in einem Microbatch.

## <a id="kombination">4. Mehrere Eingaberaten gemeinsam festlegen</a>

Wird `maxBytesPerTrigger` zusammen mit `maxFilesPerTrigger` verwendet, verarbeitet der Micro-Batch Daten, bis die niedrigere der beiden Grenzen — `maxFilesPerTrigger` oder `maxBytesPerTrigger` — erreicht ist.

## <a id="andere-quellen">5. Eingaberaten für andere Structured-Streaming-Quellen begrenzen</a>

Streaming-Quellen wie Apache Kafka haben jeweils eigene, benutzerdefinierte Eingabe-Limits, etwa `maxOffsetsPerTrigger`. Weitere Details finden sich unter "Standard connectors in Lakeflow Connect".

---

## <a id="quellen">6. Quellen</a>

- Configure Structured Streaming batch size on Databricks (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/batch-size
- Configure Structured Streaming batch size on Azure Databricks (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/batch-size

**Stand:** 2026-08-22.
