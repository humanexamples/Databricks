# DataStreamReader options — Auto Loader

Bereich: **DataStreamReader options › Auto Loader** — die `cloudFiles.*`-Optionen (`spark.readStream.format("cloudFiles")`), mit den H4-Unterbereichen **Common**, **Directory listing** und **File notification** (inkl. cloud-spezifischer S3-/ADLS-/GCS-Optionen).

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

> **Detailseiten:** Für jede einzelne Option gibt es eine eigene Datei unter [`../06 Auto Loader/Options/`](../06%20Auto%20Loader/Options/README.md). Hier die kompakte Bereichsübersicht.

---

## Common

| Option | Standard | Beschreibung (Kurz) |
|---|---|---|
| `cloudFiles.allowOverwrites` | `false` | Überschriebene/angehängte Dateien neu verarbeiten |
| `cloudFiles.backfillInterval` | None | Asynchrone Backfills im Intervall (nicht bei File Events) |
| `cloudFiles.cleanSource` | `OFF` | Verarbeitete Dateien `DELETE`/`MOVE` (DBR 16.4+) |
| `cloudFiles.cleanSource.retentionDuration` | `30 days` | Wartezeit vor Cleanup |
| `cloudFiles.cleanSource.moveDestination` | None | Zielpfad bei `MOVE` |
| `cloudFiles.format` | — (Pflicht) | Dateiformat der Quelle |
| `cloudFiles.includeExistingFiles` | `true` | Bestehende Dateien einbeziehen (nur Erststart) |
| `cloudFiles.inferColumnTypes` | `false` | Exakte Spaltentypen inferieren |
| `cloudFiles.maxBytesPerTrigger` | None | Weiche Byte-Obergrenze/Micro-Batch |
| `cloudFiles.maxFileAge` | None | Deduplizierungs-Tracking-Dauer (min. `14 days`) |
| `cloudFiles.maxFilesPerTrigger` | `1000` | Harte Datei-Obergrenze/Micro-Batch |
| `cloudFiles.partitionColumns` | None | Hive-Style-Partitionsspalten |
| `cloudFiles.schemaEvolutionMode` | `addNewColumns` / `none` | Verhalten bei neuen Spalten |
| `cloudFiles.schemaHints` | None | Typ-Hints für die Inferenz |
| `cloudFiles.schemaLocation` | — (für Inferenz Pflicht) | Speicherort des inferierten Schemas |
| `cloudFiles.useStrictGlobber` | `false` | Striktes Glob-Verhalten (DBR 12.2 LTS+) |
| `cloudFiles.validateOptions` | `true` | Options-Validierung |

## Directory listing

| Option | Standard | Beschreibung (Kurz) |
|---|---|---|
| `cloudFiles.useIncrementalListing` *(veraltet)* | `auto` (≤ DBR 17.2) / `false` (≥ DBR 17.3) | Inkrementelle statt vollständige Verzeichnisauflistung |

## File notification

### Allgemein

| Option | Standard | Beschreibung (Kurz) |
|---|---|---|
| `cloudFiles.useNotifications` | `false` | Klassischer File-Notification-Modus |
| `cloudFiles.useManagedFileEvents` | `false` | File Events (DBR 14.3 LTS+) |
| `cloudFiles.listOnStart` | `false` | Vollständige Auflistung beim Stream-Start |
| `cloudFiles.fetchParallelism` | `1` | Threads beim Abrufen aus der Queue |
| `cloudFiles.pathRewrites` | None | Pfad-Präfix-Rewrites bei Multi-Bucket-Queue |
| `cloudFiles.resourceTag` | None | Key-Value-Tags für Cloud-Ressourcen |

### S3

`cloudFiles.region`, `cloudFiles.queueUrl`, `cloudFiles.awsAccessKey`, `cloudFiles.awsSecretKey`, `cloudFiles.roleArn`, `cloudFiles.roleExternalId`, `cloudFiles.roleSessionName`, `cloudFiles.stsEndpoint`

### Azure Data Lake Storage / Blob Storage

`cloudFiles.resourceGroup`, `cloudFiles.subscriptionId`, `cloudFiles.tenantId`, `cloudFiles.clientId`, `cloudFiles.clientSecret`, `cloudFiles.connectionString`, `cloudFiles.queueName`, `databricks.serviceCredential`

### Google Cloud Storage

`cloudFiles.client`, `cloudFiles.clientEmail`, `cloudFiles.privateKey`, `cloudFiles.privateKeyId`, `cloudFiles.project`, `cloudFiles.subscription`

---

## Siehe auch

- [`../06 Auto Loader/`](../06%20Auto%20Loader/00%20Überblick.md) — Themendateien
- [`../06 Auto Loader/Options/`](../06%20Auto%20Loader/Options/README.md) — eine Datei pro Option, mit Verbatim-Beschreibungen und Beispielen
