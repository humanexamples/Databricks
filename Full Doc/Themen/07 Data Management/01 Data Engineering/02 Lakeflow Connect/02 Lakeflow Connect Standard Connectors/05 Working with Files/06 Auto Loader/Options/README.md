# Auto Loader — `cloudFiles.*`-Options-Referenz

Eine Datei pro Auto-Loader-Option. Quelle: [Auto Loader options](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options) (leitet auf die [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) weiter), Gegenprüfung über die [Azure-Spiegelseite](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options). Verbatim-Beschreibungen sind als Zitat gekennzeichnet; wo die Referenzseite beim Abruf abgeschnitten war (AWS-/GCS-Auth-Optionen), ist die Beschreibung sinngemäß und mit Hinweis versehen.

## readStream vs. writeStream

**Alle `cloudFiles.*`-Optionen sind Lese-Optionen** — sie werden auf der `DataStreamReader`-Seite gesetzt:

```python
spark.readStream.format("cloudFiles").option("cloudFiles.<name>", <wert>).load(<pfad>)
```

bzw. in SQL als benannter Parameter von `read_files` / `STREAM read_files` **ohne** `cloudFiles.`-Präfix:

```sql
... FROM STREAM read_files('<pfad>', format => 'json', schemaLocation => '<pfad>')
```

Auf der `writeStream`-Seite (`DataStreamWriter`) gibt es **keine** `cloudFiles.*`-Optionen. Dort relevant sind die generischen Structured-Streaming-Optionen:

| writeStream-Option | Zweck |
|---|---|
| `checkpointLocation` | Pfad für Checkpoint/RocksDB-Datei-Tracking (Pflicht außerhalb von Lakeflow-Pipelines) |
| `mergeSchema` | `true` erlaubt Schema-Evolution in die Delta-Zieltabelle (Gegenstück zu `cloudFiles.schemaEvolutionMode` auf der Leseseite) |
| `path` | Zielpfad bei `.start("<pfad>")` statt `.toTable(...)` |
| `.trigger(...)` | Structured-Streaming-Trigger (`availableNow`, `processingTime`, `once`, `continuous`) — nicht zu verwechseln mit Lakeflow-Pipeline-Triggern |

---

## Optionen nach Kategorie

### Common Auto Loader options (formatunabhängig)

| Option | Standard | Kurz |
|---|---|---|
| [cloudFiles.format](cloudFiles.format.md) | — (Pflicht) | Dateiformat der Quelle |
| [cloudFiles.schemaLocation](cloudFiles.schemaLocation.md) | — (Pflicht für Inferenz) | Speicherort für inferiertes Schema |
| [cloudFiles.schemaHints](cloudFiles.schemaHints.md) | None | Typ-Hints für die Schema-Inferenz |
| [cloudFiles.schemaEvolutionMode](cloudFiles.schemaEvolutionMode.md) | `addNewColumns` / `none` | Verhalten bei neuen Spalten |
| [cloudFiles.inferColumnTypes](cloudFiles.inferColumnTypes.md) | `false` | Exakte Spaltentypen inferieren |
| [cloudFiles.partitionColumns](cloudFiles.partitionColumns.md) | None | Hive-Style-Partitionsspalten |
| [cloudFiles.includeExistingFiles](cloudFiles.includeExistingFiles.md) | `true` | Bestehende Dateien einbeziehen |
| [cloudFiles.maxFilesPerTrigger](cloudFiles.maxFilesPerTrigger.md) | `1000` | Harte Datei-Obergrenze pro Micro-Batch |
| [cloudFiles.maxBytesPerTrigger](cloudFiles.maxBytesPerTrigger.md) | None | Weiche Byte-Obergrenze pro Micro-Batch |
| [cloudFiles.maxFileAge](cloudFiles.maxFileAge.md) | None | Deduplizierungs-Tracking-Dauer |
| [cloudFiles.allowOverwrites](cloudFiles.allowOverwrites.md) | `false` | Überschriebene/angehängte Dateien neu verarbeiten |
| [cloudFiles.backfillInterval](cloudFiles.backfillInterval.md) | None | Asynchrone Backfills im Intervall |
| [cloudFiles.cleanSource](cloudFiles.cleanSource.md) | `OFF` | Verarbeitete Dateien löschen/verschieben |
| [cloudFiles.cleanSource.retentionDuration](cloudFiles.cleanSource.retentionDuration.md) | `30 days` | Wartezeit vor Cleanup |
| [cloudFiles.cleanSource.moveDestination](cloudFiles.cleanSource.moveDestination.md) | None | Zielpfad bei `MOVE` |
| [cloudFiles.useStrictGlobber](cloudFiles.useStrictGlobber.md) | `false` | Striktes Glob-Verhalten |
| [cloudFiles.validateOptions](cloudFiles.validateOptions.md) | `true` | Options-Validierung |

### Directory Listing Mode

| Option | Standard | Kurz |
|---|---|---|
| [cloudFiles.useIncrementalListing](cloudFiles.useIncrementalListing.md) | `auto` / `false` | (Veraltet) Inkrementelle Verzeichnisauflistung |

### File Notification Mode (allgemein)

| Option | Standard | Kurz |
|---|---|---|
| [cloudFiles.useNotifications](cloudFiles.useNotifications.md) | `false` | File-Notification-Modus statt Directory Listing |
| [cloudFiles.useManagedFileEvents](cloudFiles.useManagedFileEvents.md) | `false` | File Events verwenden |
| [cloudFiles.listOnStart](cloudFiles.listOnStart.md) | `false` | Vollständige Auflistung beim Stream-Start |
| [cloudFiles.fetchParallelism](cloudFiles.fetchParallelism.md) | `1` | Threads beim Abrufen aus der Queue |
| [cloudFiles.pathRewrites](cloudFiles.pathRewrites.md) | None | Pfad-Präfix-Rewrites bei Multi-Bucket-Queue |
| [cloudFiles.resourceTag](cloudFiles.resourceTag.md) | None | Key-Value-Tags für Cloud-Ressourcen |

### File Notification — AWS S3

| Option | Kurz |
|---|---|
| [cloudFiles.region](cloudFiles.region.md) | AWS-Region von Bucket/SNS/SQS |
| [cloudFiles.queueUrl](cloudFiles.queueUrl.md) | URL einer bestehenden SQS-Queue |
| [cloudFiles.awsAccessKey](cloudFiles.awsAccessKey.md) | AWS Access Key ID |
| [cloudFiles.awsSecretKey](cloudFiles.awsSecretKey.md) | AWS Secret Access Key |
| [cloudFiles.roleArn](cloudFiles.roleArn.md) | ARN der zu übernehmenden IAM-Rolle |
| [cloudFiles.roleExternalId](cloudFiles.roleExternalId.md) | External ID bei `AssumeRole` |
| [cloudFiles.roleSessionName](cloudFiles.roleSessionName.md) | Session-Name bei `AssumeRole` |
| [cloudFiles.stsEndpoint](cloudFiles.stsEndpoint.md) | Benutzerdefinierter STS-Endpunkt |

### File Notification — Azure (ADLS / Blob Storage)

| Option | Kurz |
|---|---|
| [cloudFiles.resourceGroup](cloudFiles.resourceGroup.md) | Azure Resource Group des Storage Accounts |
| [cloudFiles.subscriptionId](cloudFiles.subscriptionId.md) | Azure Subscription ID |
| [cloudFiles.tenantId](cloudFiles.tenantId.md) | Azure Tenant ID des Service Principals |
| [cloudFiles.clientId](cloudFiles.clientId.md) | Client/Application ID des Service Principals |
| [cloudFiles.clientSecret](cloudFiles.clientSecret.md) | Client Secret des Service Principals |
| [cloudFiles.connectionString](cloudFiles.connectionString.md) | Connection String (Account Key oder SAS) |
| [cloudFiles.queueName](cloudFiles.queueName.md) | Name einer bestehenden Azure-Queue |
| [databricks.serviceCredential](databricks.serviceCredential.md) | Databricks-Service-Credential (nicht `cloudFiles.*`, aber hier relevant) |

### File Notification — GCS (Google Cloud Storage)

| Option | Kurz |
|---|---|
| [cloudFiles.client](cloudFiles.client.md) | Client ID des Google-Service-Accounts |
| [cloudFiles.clientEmail](cloudFiles.clientEmail.md) | E-Mail des Google-Service-Accounts |
| [cloudFiles.privateKey](cloudFiles.privateKey.md) | Private Key des Google-Service-Accounts |
| [cloudFiles.privateKeyId](cloudFiles.privateKeyId.md) | Private Key ID des Google-Service-Accounts |
| [cloudFiles.project](cloudFiles.project.md) | GCP-Projekt-ID des GCS-Buckets |
| [cloudFiles.subscription](cloudFiles.subscription.md) | Name einer bestehenden Pub/Sub-Subscription |

---

## Nicht in diesem Ordner

- **Formatspezifische Parser-Optionen** (`multiLine`, `header`, `sep`, `rowTag`, `mode`, `columnNameOfCorruptRecord`, `rescuedDataColumn`, `singleVariantColumn`, `prefersDecimal`, `readerCaseSensitive`, …) sind keine `cloudFiles.*`-Optionen; sie werden ohne Präfix gesetzt und in der Spark-API-Optionsreferenz je Format gelistet. Siehe [`../../04 Dateitypen/`](../../04%20Dateitypen/) und [`../01 Schema-Inferenz und -Evolution.md`](../01%20Schema-Inferenz%20und%20-Evolution.md).
- **Generische Datei-Optionen** (`pathGlobFilter`, `modifiedAfter`, `modifiedBefore`, `recursiveFileLookup`, `ignoreCorruptFiles`, `ignoreMissingFiles`) — ebenfalls ohne `cloudFiles.`-Präfix.
