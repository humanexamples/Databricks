# Datei-Tracking bei Databricks-Ingestion-Methoden

> **Version 3** – ergänzt um Optionen zum Ein-/Ausschalten des Trackings sowie die konkreten Parameter, nach denen getrackt wird. Ausschließlich basierend auf der offiziellen Databricks-Dokumentation (docs.databricks.com).

## Kurzübersicht

| Methode | Merkt sich gelesene Dateien? | Tracking-Parameter | Ein-/Ausschaltbar? |
|---|---|---|---|
| **Auto Loader** (`cloudFiles`) | ✅ Ja | Standardmäßig: **Dateipfad**. Optional zusätzlich: **letzter Änderungszeitpunkt** (`cloudFiles.allowOverwrites`) | ✅ Ja, über `cloudFiles.allowOverwrites` und `cloudFiles.maxFileAge` |
| **`COPY INTO`** | ✅ Ja | Dateiidentität (Metadaten im Delta Log der Zieltabelle) — laut Doku unabhängig vom Änderungszeitpunkt | ✅ Ja, über `COPY_OPTIONS ('force' = 'true')` |
| **`spark.readStream`** | ✅ Ja | Offsets/Commits im Checkpoint-Verzeichnis | ⚠️ Nicht dokumentiert als granulare Option — nur durch Löschen/Wechseln des Checkpoint-Verzeichnisses zurücksetzbar |
| **CTAS, `INSERT INTO`, `spark.read`, `read_files()` (Batch)** | ❌ Nein | – | – (kein Tracking-Mechanismus dokumentiert) |

---

## 1. Auto Loader — Optionen für das Tracking

### Standard-Tracking-Parameter: Dateipfad

Laut der offiziellen Auto Loader FAQ verfolgt Auto Loader Dateien primär anhand ihres **Pfads**:

> *"Auto Loader normally ingests each file only once based on its file path."*
> — [Auto Loader FAQ | Databricks on AWS](https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/faq.html)

### Option `cloudFiles.allowOverwrites`: zusätzlicher Tracking-Parameter "letzter Änderungszeitpunkt"

Standardmäßig (`cloudFiles.allowOverwrites = false`) gilt: Jede Datei wird exakt einmal verarbeitet, unabhängig von späteren Änderungen.

> *"With the default setting (cloudFiles.allowOverwrites = false), files are processed exactly once. When a file is appended to or overwritten, Auto Loader cannot guarantee which file version will be processed."*
> — [Auto Loader FAQ | Databricks on AWS](https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/faq.html)

Wird die Option auf `true` gesetzt, erweitert sich der Tracking-Parameter um den **Änderungszeitpunkt** der Datei:

> *"However, if you set the allowOverwrites option to true, Auto Loader also uses the file's last-modified timestamp to determine whether a file is new or has been updated and needs to be re-ingested."*
> — [Auto Loader FAQ | Databricks on AWS](https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/faq.html)

Wichtiger Hinweis der Doku zu dieser Option:

> *"With cloudFiles.allowOverwrites enabled, you must handle duplicate records yourself. Auto Loader will reprocess the entire file even when it is appended to or partially updated. In general, Databricks recommends using Auto Loader to ingest immutable files only and using the default setting cloudFiles.allowOverwrites = false."*
> — [Auto Loader FAQ | Databricks on AWS](https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/faq.html)

**Kein Tracking anhand des Dateiinhalts:** Die Doku beschreibt ausschließlich Pfad und Änderungszeitpunkt als Tracking-Parameter. Ein inhaltsbasiertes Tracking (z. B. Prüfsumme/Checksumme) wird an keiner Stelle erwähnt.

### Option `cloudFiles.maxFileAge`: Tracking-Zustand zeitlich begrenzen

Diese Option steuert, wie lange Auto Loader sich ein einzelnes Datei-Ereignis merkt, bevor es aus dem Tracking-Zustand entfernt ("verjährt") wird:

> *"If you want to prevent the file states from growing without limits, you can also consider using the cloudFiles.maxFileAge option to expire file events that are older than a certain age... cloudFiles.maxFileAge is provided as a cost control mechanism for high volume datasets."*
> — [Configure Auto Loader for production workloads | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production)

Die Doku warnt jedoch ausdrücklich vor unerwünschten Nebeneffekten bei zu aggressiver Einstellung:

> *"Tuning cloudFiles.maxFileAge too aggressively can cause data quality issues such as duplicate ingestion or missing files... already processed files expiring and then being re-processed causing duplicate data."*
> — [Configure Auto Loader for production workloads | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production)

Der Mindestwert liegt bei 14 Tagen, empfohlen wird ein konservativer Wert (z. B. 90 Tage):

> *"The minimum value that you can set for cloudFiles.maxFileAge is '14 days'."*
> — [Configure Auto Loader for production workloads | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production)

---

## 2. COPY INTO — Optionen für das Tracking

### Standardverhalten: Tracking unabhängig vom Änderungszeitpunkt

Anders als Auto Loader mit `allowOverwrites = true` berücksichtigt `COPY INTO` laut Doku den Änderungszeitpunkt einer Datei **nicht** — bereits geladene Dateien werden übersprungen, selbst wenn sie sich seither geändert haben:

> *"This is a retryable and idempotent operation. Files in the source location that have already been loaded are skipped. This is true even if the files have been modified since they were loaded."*
> — [COPY INTO | Databricks on AWS](https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into)

### Option `force`: Tracking gezielt deaktivieren

`COPY INTO` bietet eine explizite Option, um das Tracking (die Idempotenz) für einen einzelnen Lauf bewusst abzuschalten:

> *"force: boolean, default false. If set to true, idempotency is disabled and files are loaded regardless of whether they've been loaded before."*
> — [COPY INTO | Databricks on AWS](https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into)

---

## 3. Filter-Parameter, die **nicht** das Tracking selbst steuern, aber die Dateiauswahl beeinflussen

Laut der offiziellen Spark-API-Optionsreferenz gelten folgende Parameter **gemeinsam** für `DataFrameReader`, `read_files`, `COPY INTO` und Auto Loader:

> *"Use these options with DataFrameReader.option(), DataFrameReader.options(), read_files, COPY INTO, and Auto Loader to control how Databricks reads data files."*
> — [Spark API options reference | Databricks on AWS](https://docs.databricks.com/aws/en/spark/api-options)

| Option | Beschreibung laut Doku |
|---|---|
| `modifiedAfter` | *"An optional timestamp as a filter to only ingest files that have a modification timestamp after the specified timestamp."* |
| `modifiedBefore` | *"An optional timestamp as a filter to only ingest files that have a modification timestamp before the specified timestamp."* |
| `pathGlobFilter` / `fileNamePattern` | *"A potential glob pattern for choosing files. Equivalent to PATTERN in COPY INTO (legacy). fileNamePattern can be used in read_files."* |
| `recursiveFileLookup` | *"When true, this option searches through nested directories even if their names do not follow a partition naming scheme."* |

**Wichtige Unterscheidung:** Diese Optionen filtern, **welche Dateien überhaupt für die Verarbeitung in Frage kommen** (z. B. nur Dateien nach einem bestimmten Änderungsdatum). Sie sind kein Ersatz für die eigentliche Tracking-Logik (Checkpoint bei Auto Loader/Streaming, Delta-Log-Metadaten bei `COPY INTO`), die entscheidet, **welche dieser gefilterten Dateien bereits verarbeitet wurden**.

---

## 4. Weitere Auto-Loader-Optionen rund um das Tracking

### `cloudFiles.includeExistingFiles`: Anfangszustand des Trackings steuern

Diese Option legt fest, ob beim allerersten Start eines Streams bereits vorhandene Dateien in die Verarbeitung (und damit ins Tracking) aufgenommen werden, oder ob nur Dateien berücksichtigt werden, die **nach** dem Start neu hinzukommen:

> *"cloudFiles.includeExistingFiles ... this checks whether to include existing files in the Stream Processing Input Path or to only handle the new files arriving after initial setup."*
> — [Auto Loader options | Databricks on AWS](https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/options.html)

**Wichtige Einschränkung laut Doku:** Auch bei `includeExistingFiles = false` führt Auto Loader weiterhin eine Verzeichnisauflistung durch, um mit dem Dateiereignis-Cache auf demselben Stand zu sein:

> *"Even if includeExistingFiles is set to false, Auto Loader performs a directory listing to discover files created after the stream start and get current with the file events cache..."*
> — [Auto Loader FAQ | Databricks on AWS](https://learn.microsoft.com/en-us/azure/databricks/ingestion/cloud-object-storage/auto-loader/faq)

### `cloud_files_state`: den Tracking-Zustand direkt abfragen

Databricks stellt eine eigene Tabellenfunktion bereit, mit der sich der von Auto Loader intern geführte Tracking-Zustand pro Datei **direkt abfragen** lässt — inklusive Verarbeitungsstatus:

> *"Whether the file has been ingested, indicated by one of the following states: NULL: The file has not been processed yet, or the file state cannot be determined by Auto Loader. PROCESSING: The file is being processed. SKIPPED_CORRUPTED: The file was not ingested because it was corrupt."*
> — [cloud_files_state table-valued function | Databricks on AWS](https://docs.databricks.com/aws/en/sql/language-manual/functions/cloud_files_state)

Damit lässt sich konkret nachvollziehen, **wie** Auto Loader "feststellt", ob eine Datei bereits verarbeitet wurde — der Zustand ist über diese Funktion einsehbar, nicht nur implizit im Verhalten.

### `cloudFiles.cleanSource`: verarbeitete Dateien archivieren oder löschen

Diese Option (ab Databricks Runtime 16.4 LTS) verschiebt oder löscht Quelldateien, **nachdem** sie von Auto Loader verarbeitet wurden — das reduziert indirekt auch die Menge an Zustand, die für die Dateierkennung durchsucht werden muss:

> *"Auto Loader provides the cloudFiles.cleanSource option to automatically manage file retention by archiving or deleting files after they are processed... Setting cloudFiles.cleanSource deletes or moves files in the source directory."*
> — [Configure Auto Loader for production workloads | Databricks on AWS](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production)

### Tracking vollständig zurücksetzen: Checkpoint-Verzeichnis wechseln

Für `spark.readStream` (inkl. Auto Loader) gilt laut der allgemeinen Structured-Streaming-Dokumentation: Der Tracking-Zustand ist an das Checkpoint-Verzeichnis gebunden. Ein Wechsel oder Löschen dieses Verzeichnisses setzt das Tracking vollständig zurück:

> *"When you delete the files in a checkpoint directory or change to a new checkpoint location, the next run of the query begins fresh."*
> — [Structured Streaming checkpoints | Databricks on AWS](https://docs.databricks.com/aws/en/structured-streaming/checkpoints)

---

## 5. Methoden ohne dokumentierten Tracking-Mechanismus

Für CTAS, `INSERT INTO ... SELECT` aus Dateien, `spark.read` sowie `read_files()` im reinen Batch-Kontext (ohne `STREAM`-Präfix) beschreibt die Databricks-Dokumentation **keinen** Mechanismus, der sich merkt, welche Dateien bereits gelesen wurden — im Unterschied zu den expliziten "idempotent"/"exactly-once"-Aussagen bei Auto Loader und `COPY INTO`.

---

## Zusammenfassung

| Frage | Antwort laut Doku |
|---|---|
| Kann Tracking ein-/ausgeschaltet werden? | Ja, bei Auto Loader (`cloudFiles.allowOverwrites`, `cloudFiles.maxFileAge`) und bei `COPY INTO` (`force`). |
| Nach welchen Parametern wird getrackt? | **Dateipfad** (Standard bei Auto Loader), optional zusätzlich **letzter Änderungszeitpunkt** (Auto Loader mit `allowOverwrites=true`). Bei `COPY INTO`: Dateiidentität, explizit **unabhängig** vom Änderungszeitpunkt. |
| Wird nach Dateiinhalt getrackt? | Nicht dokumentiert — kein Hinweis auf inhaltsbasiertes Tracking (z. B. Prüfsumme) in der Databricks-Doku. |
| Gibt es reine Auswahlfilter (kein Tracking)? | Ja: `modifiedAfter`, `modifiedBefore`, `pathGlobFilter`/`fileNamePattern`, `recursiveFileLookup` — diese bestimmen die Dateiauswahl, nicht den "bereits verarbeitet"-Status. |

## Quellen (ausschließlich offizielle Databricks-Dokumentation)

- Auto Loader FAQ: https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/faq.html
- Configure Auto Loader for production workloads: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production
- COPY INTO Referenz: https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into
- Spark API options reference: https://docs.databricks.com/aws/en/spark/api-options
- What is Auto Loader?: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/
- Structured Streaming checkpoints: https://docs.databricks.com/aws/en/structured-streaming/checkpoints
- CREATE STREAMING TABLE: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table
- Delta Lake generated columns (CTAS): https://docs.databricks.com/aws/en/delta/generated-columns
- Auto Loader options: https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/options.html
- cloud_files_state table-valued function: https://docs.databricks.com/aws/en/sql/language-manual/functions/cloud_files_state
- Auto Loader FAQ (Microsoft Learn Spiegel der Databricks-Doku): https://learn.microsoft.com/en-us/azure/databricks/ingestion/cloud-object-storage/auto-loader/faq
