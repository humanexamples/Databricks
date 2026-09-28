# `cloudFiles.*` — Auto-Loader-Optionen

Eine Datei pro `cloudFiles.*`-Option von `spark.readStream.format("cloudFiles")` — jede Datei enthält eine kurze Einordnung, das verbatim-zitierte (oder wo die Quelle beim Abruf abgeschnitten war, sinngemäß wiedergegebene) Original aus der Doku, eine einfache Erklärung und ein lauffähiges Codebeispiel.

Quelle: [Auto Loader options](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options).

## Common (formatunabhängig, direkt in diesem Ordner)

| Option | Wirkung | Default |
|---|---|---|
| [`cloudFiles.format`](cloudFiles.format.md) | Dateiformat im Quellpfad: `avro`, `binaryFile`, `csv`, `json`, `orc`, `parquet`, `text`, `xml`. | – (**Pflicht**) |
| [`cloudFiles.schemaLocation`](cloudFiles.schemaLocation.md) | Speicherort für das inferierte Schema und seine Änderungen. | – (**Pflicht** für Schema-Inferenz) |
| [`cloudFiles.schemaHints`](cloudFiles.schemaHints.md) | Typangaben für einzelne Spalten, die bei der Schema-Inferenz gelten. | – |
| [`cloudFiles.schemaEvolutionMode`](cloudFiles.schemaEvolutionMode.md) | Umgang mit neuen Spalten: `addNewColumns`, `none`, `rescue`, `failOnNewColumns`. | `addNewColumns` ohne Schema, sonst `none` |
| [`cloudFiles.inferColumnTypes`](cloudFiles.inferColumnTypes.md) | Exakte Spaltentypen inferieren. Bei `false` werden JSON- und CSV-Spalten als `STRING` gelesen. | `false` |
| [`cloudFiles.partitionColumns`](cloudFiles.partitionColumns.md) | Kommagetrennte Liste von Hive-Style-Partitionsspalten (`a=x/b=1/`) aus dem Pfad. `""` ignoriert alle. | – |
| [`cloudFiles.includeExistingFiles`](cloudFiles.includeExistingFiles.md) | Bereits vorhandene Dateien mitverarbeiten oder nur neue. Wird nur beim ersten Start ausgewertet. | `true` |
| [`cloudFiles.maxFilesPerTrigger`](cloudFiles.maxFilesPerTrigger.md) | Maximale Anzahl neuer Dateien pro Trigger. Ab DBR 18.0 dynamisch konfiguriert. | `1000` |
| [`cloudFiles.maxBytesPerTrigger`](cloudFiles.maxBytesPerTrigger.md) | Weiche Obergrenze neuer Bytes pro Trigger (z. B. `10g`). Eine Datei wird nie aufgeteilt. Ab DBR 18.0 dynamisch konfiguriert. | – |
| [`cloudFiles.maxFileAge`](cloudFiles.maxFileAge.md) | Wie lange ein Datei-Event zur Deduplizierung verfolgt wird. Nur bei Millionen Dateien pro Stunde anpassen, dann konservativ (z. B. 90 Tage). | – |
| [`cloudFiles.allowOverwrites`](cloudFiles.allowOverwrites.md) | Ob geänderte Dateien im Eingabeverzeichnis bestehende Daten überschreiben dürfen. | `false` |
| [`cloudFiles.backfillInterval`](cloudFiles.backfillInterval.md) | Intervall für asynchrone Backfills (z. B. `1 day`). Nicht zusammen mit `useManagedFileEvents = true`. | – |
| [`cloudFiles.cleanSource`](cloudFiles.cleanSource.md) | Verarbeitete Dateien löschen oder verschieben: `OFF`, `DELETE`, `MOVE`. Ab DBR 16.4. | `OFF` |
| [`cloudFiles.cleanSource.retentionDuration`](cloudFiles.cleanSource.retentionDuration.md) | Wartezeit, bevor verarbeitete Dateien bereinigt werden dürfen. Ab DBR 16.4. | `30 days` |
| [`cloudFiles.cleanSource.moveDestination`](cloudFiles.cleanSource.moveDestination.md) | Zielpfad (Cloud-Speicher oder UC-Volume) für `cleanSource = MOVE`. Ab DBR 16.4. | – |
| [`cloudFiles.useStrictGlobber`](cloudFiles.useStrictGlobber.md) | Strikter Globber wie bei anderen Spark-Dateiquellen. Ab DBR 12.2 LTS. | `false` |
| [`cloudFiles.validateOptions`](cloudFiles.validateOptions.md) | Optionen prüfen und bei unbekannten oder widersprüchlichen Optionen einen Fehler auslösen. | `true` |

Werden `maxFilesPerTrigger` und `maxBytesPerTrigger` zusammen gesetzt, gilt das Limit, das zuerst erreicht wird. Mit `Trigger.Once()` (deprecated) wirken beide nicht.

## [`Directory Listing/`](Directory%20Listing/)

`cloudFiles.useIncrementalListing` (veraltet).

## [`File Notification/`](File%20Notification/)

Allgemein (beide Modi bzw. klassischer Modus): `cloudFiles.useNotifications`, `cloudFiles.useManagedFileEvents`, `cloudFiles.listOnStart`, `cloudFiles.fetchParallelism`, `cloudFiles.pathRewrites`, `cloudFiles.resourceTag`.

Cloud-spezifische Auth-/Queue-Optionen (nur klassischer File-Notification-Modus) in eigenen Unterordnern:

- [`AWS S3/`](File%20Notification/AWS%20S3/) — `cloudFiles.region`, `cloudFiles.queueUrl`, `cloudFiles.awsAccessKey`, `cloudFiles.awsSecretKey`, `cloudFiles.roleArn`, `cloudFiles.roleExternalId`, `cloudFiles.roleSessionName`, `cloudFiles.stsEndpoint`
- [`Azure/`](File%20Notification/Azure/) — `cloudFiles.resourceGroup`, `cloudFiles.subscriptionId`, `cloudFiles.tenantId`, `cloudFiles.clientId`, `cloudFiles.clientSecret`, `cloudFiles.connectionString`, `cloudFiles.queueName`, `databricks.serviceCredential`
- [`GCS/`](File%20Notification/GCS/) — `cloudFiles.client`, `cloudFiles.clientEmail`, `cloudFiles.privateKey`, `cloudFiles.privateKeyId`, `cloudFiles.project`, `cloudFiles.subscription`

## Verwandt

- [../03 option.md](../03%20option.md) — `DataStreamReader.option()`, allgemeiner Einstiegspunkt
- Ausführlichere, tabellenbasierte Parallel-Referenz mit Themendateien (Schema-Inferenz, Type Widening, File Events, Clean Source, Best Practices, ...): [`../../../../07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/05 Working with Files/06 Auto Loader/`](../../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/06%20Auto%20Loader/00%20Überblick.md)

**Stand:** 2026-09-15
