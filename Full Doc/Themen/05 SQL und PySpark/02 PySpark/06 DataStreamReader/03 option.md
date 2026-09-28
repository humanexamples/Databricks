# `DataStreamReader.option()`

Fügt der zugrunde liegenden Datenquelle eine einzelne Eingabeoption hinzu.

## Signatur

```python
option(key, value)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `key` | `str` | Der Options-Schlüssel. |
| `value` | `str`, `int`, `float` oder `bool` | Der Options-Wert. |

## Rückgabewert

`DataStreamReader`

## Beispiele

```python
spark.readStream.option("x", 1)
# <...streaming.readwriter.DataStreamReader object ...>
```

```python
import time
q = spark.readStream.format("rate").option("rowsPerSecond", 10).load().writeStream.format("console").start()
time.sleep(3)
q.stop()
```

---

# Verfügbare Optionen (ohne `cloudFiles.*`)

Welche Optionen gelten, hängt von der Quelle in `format(...)` ab:

- [Dateiquellen und Delta Lake — gemeinsame Optionen](#dateiquellen-und-delta-lake--gemeinsame-optionen)
- [Delta Lake](#delta-lake)
- [Kafka](#kafka)
- [Kinesis](#kinesis)
- [Pub/Sub](#pubsub)
- [Pulsar](#pulsar)

Nicht hier aufgeführt:

- **Auto Loader** (`format("cloudFiles")`): eigene `cloudFiles.*`-Optionen, siehe [CloudFiles/00 Übersicht.md](CloudFiles/00%20%C3%9Cbersicht.md).
- **Formatoptionen** (CSV, JSON, Parquet usw.): gleich wie bei `spark.read`, siehe [06 csv.md](06%20csv.md), [07 json.md](07%20json.md) usw.

Parallele Referenz im Projekt: [03 Spark API Options/](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/21%20DataStreamReader%20%E2%80%94%20Common.md) (Common, Auto Loader, Kafka).

## Übersicht als Tabellen

Details und Codebeispiele je Option folgen weiter unten.

### Dateiquellen und Delta Lake — gemeinsam

| Option | Default | Beschreibung |
|---|---|---|
| `cleanSource` | `off` | Quelldatei nach Verarbeitung: `off`, `delete` oder `archive` (nach `sourceArchiveDir`). Nicht für Delta-Tabellen. |
| `sourceArchiveDir` | – | Archivverzeichnis für `cleanSource = archive`. Nicht für Delta-Tabellen. |
| `fileNameOnly` | `false` | Verarbeitete Dateien nur am Dateinamen erkennen statt am vollen Pfad. Nicht für Delta-Tabellen. |
| `latestFirst` | `false` | Neueste Dateien zuerst verarbeiten. Nicht für Delta-Tabellen. |
| `maxFileAge` | `7d` | Maximales Dateialter, gemessen an der jüngsten Datei. Nicht für Delta-Tabellen. |
| `maxCachedFiles` | `10000` | Max. zwischengespeicherte unverarbeitete Dateien; `0` = kein Cache. Nicht für Delta-Tabellen. |
| `maxFilesPerTrigger` | `1000` (Delta); kein Limit (andere Dateiquellen) | Max. neue Dateien pro Microbatch. |
| `maxBytesPerTrigger` | – | Weiche Obergrenze der Datenmenge pro Microbatch. |

### Delta Lake

| Option | Default | Beschreibung |
|---|---|---|
| `startingVersion` | neueste Version | Start ab dieser Delta-Version (oder `latest`). Nicht mit `startingTimestamp`. |
| `startingTimestamp` | neueste Version | Start ab diesem Zeitpunkt. Nicht mit `startingVersion`. |
| `skipChangeCommits` | `false` | Nur Appends verarbeiten, Änderungen/Löschungen ignorieren. Ab DBR 12.2 LTS. |
| `ignoreChanges` (deprecated) | `false` | Neu geschriebene Dateien nach UPDATE/MERGE/DELETE erneut ausgeben. Bis DBR 11.3 LTS. |
| `ignoreDeletes` (deprecated) | `false` | Löschen ganzer Partitionen ignorieren. |
| `readChangeFeed` / `readChangeData` | `false` | Change Data Feed lesen (Änderungen auf Zeilenebene). |
| `failOnDataLoss` | `true` | Fehler, wenn Daten durch Log-Retention fehlen. |
| `excludeRegex` | – | Dateien mit passendem Pfad (Java-Regex) ausschließen. |
| `schemaTrackingLocation` | – | Verzeichnis für Schema-Tracking; innerhalb der `checkpointLocation`. |
| `allowSourceColumnDrop` | – | Nach gelöschten Spalten weiterlaufen (Version oder `always`). Braucht `schemaTrackingLocation`. |
| `allowSourceColumnRename` | – | Nach umbenannten Spalten weiterlaufen. Braucht `schemaTrackingLocation`. |
| `allowSourceColumnTypeChange` | – | Nach geänderten Spaltentypen weiterlaufen. Braucht `schemaTrackingLocation`. |
| `withEventTimeOrder` | `false` | Ersten Snapshot nach Event Time aufteilen, damit mit Watermark nichts verworfen wird. Ab DBR 11.3 LTS. |

### Kafka

Genau eine von `subscribe`, `subscribePattern`, `assign` ist Pflicht.

| Option | Default | Beschreibung |
|---|---|---|
| `kafka.bootstrap.servers` | – | Broker-Adressen (`host:port`, kommagetrennt). |
| `subscribe` | – | Topics (kommagetrennt). |
| `subscribePattern` | – | Topic-Muster (Java-Regex). |
| `assign` | – | Konkrete Partitionen als JSON. |
| `startingOffsets` | `latest` (Streaming), `earliest` (Batch) | Startpunkt: `earliest`, `latest` oder JSON. Nur beim ersten Start. |
| `startingOffsetsByTimestamp` | – | Start-Offsets pro Partition als Zeitstempel (ms). |
| `startingTimestamp` | – | Globaler Start-Zeitstempel (ms). |
| `startingOffsetsByTimestampStrategy` | `error` | Wenn kein Offset zum Zeitstempel existiert: `error` oder `latest`. |
| `failOnDataLoss` | `true` | Fehler bei möglichem Datenverlust. |
| `includeHeaders` | `false` | Kafka-Header als Spalte ausgeben. |
| `groupIdPrefix` | `spark-kafka-source` (Streaming), `spark-kafka-relation` (Batch) | Präfix der automatisch erzeugten Group-ID. |
| `kafka.group.id` | – | Feste Consumer-Group-ID (Vorsicht bei parallelen Abfragen). |
| `minPartitions` | – | Mindestanzahl Spark-Partitionen. |
| `maxRecordsPerPartition` | – | Max. Datensätze pro Spark-Partition. |
| `fetchoffset.numretries` | `3` | Wiederholungen beim Offset-Abruf. |
| `fetchoffset.retryintervalms` | `1000` | Pause zwischen Wiederholungen (ms). |
| `kafkaconsumer.polltimeoutms` | – | Timeout für `poll()` (ms). |
| `maxOffsetsPerTrigger` | – | Max. Offsets pro Trigger. Nur Streaming. |
| `minOffsetsPerTrigger` | – | Min. Offsets, bevor ein Microbatch startet. Nur Streaming. |
| `maxTriggerDelay` | `15m` | Max. Wartezeit auf `minOffsetsPerTrigger`. Nur Streaming. |
| `bytesEstimateWindowLength` | `300s` | Fenster für die Metrik `estimatedTotalBytesBehindLatest`. Nur Streaming. |
| `databricks.serviceCredential` | – | UC Service Credential für Cloud-Kafka. Ab DBR 16.1. |
| `databricks.serviceCredential.scope` | – | OAuth-Scope der Service Credential. |
| `kafka.security.protocol` | – | z. B. `SASL_SSL`, `SSL`, `PLAINTEXT`. |
| `kafka.sasl.mechanism` | – | z. B. `PLAIN`, `SCRAM-SHA-512`, `AWS_MSK_IAM`. |
| `kafka.sasl.jaas.config` | – | JAAS-Login-Konfiguration. |
| `kafka.sasl.login.callback.handler.class` | – | Login-Callback-Handler-Klasse. |
| `kafka.sasl.client.callback.handler.class` | – | Client-Callback-Handler-Klasse. |
| `kafka.ssl.truststore.location` / `.password` | – | Truststore-Datei und Passwort. |
| `kafka.ssl.keystore.location` / `.password` | – | Keystore-Datei und Passwort. |

### Kinesis

Genau eine von `streamName`, `streamARN` ist Pflicht.

| Option | Default | Beschreibung |
|---|---|---|
| `streamName` | – | Stream-Namen (kommagetrennt). |
| `streamARN` | – | Stream-ARNs (kommagetrennt). Ab DBR 16.1. |
| `region` | lokal ermittelte Region | Region der Streams. |
| `endpoint` | lokal ermittelte Region | Regionaler Kinesis-Endpoint. |
| `initialPosition` | `latest` | Start: `latest`, `trim_horizon`/`earliest`, `at_timestamp`. |
| `consumerMode` | `polling` | `polling` oder `efo` (Enhanced Fan-Out). Ab DBR 11.3 LTS. |
| `consumerName` | ID der Streaming-Abfrage | EFO-Consumer-Name. Ab DBR 11.3 LTS. |
| `consumerNamePrefix` | `databricks_` | Präfix vor `consumerName`. Ab DBR 16.0. |
| `consumerRefreshInterval` | `300s` (max. `3600s`) | Prüfintervall der EFO-Registrierung. |
| `registeredConsumerId` | – | Bestehende EFO-Consumer (Namen oder ARNs). Ab DBR 16.1. |
| `registeredConsumerIdType` | – | `name` oder `ARN`. Ab DBR 16.1. |
| `requireConsumerDeregistration` | `false` | EFO-Consumer beim Beenden abmelden. |
| `fetchBufferSize` | `20gb` | Puffer für den nächsten Trigger (keine harte Grenze). |
| `maxFetchDuration` | `10s` | Pufferdauer vorab geholter Daten. |
| `maxFetchRate` | `1.0` (max. `2.0`) | Max. Prefetch-Rate pro Shard in MB/s. |
| `minFetchPeriod` | `400ms` (min. `200ms`) | Mindestabstand zwischen Prefetch-Versuchen. |
| `maxRecordsPerFetch` | `10000` | Datensätze pro API-Aufruf. |
| `shardsPerTask` | `5` | Shards pro Spark-Task. Nicht mit `maxPartitions`. |
| `maxPartitions` | – | Anzahl Spark-Tasks. Nicht mit `shardsPerTask`. Ab DBR 19. |
| `shardFetchInterval` | `1s` | Prüfintervall für Resharding. |
| `maxShardsPerDescribe` | `100` | Max. Shards pro Auflist-Aufruf (bis `10000`). |
| `coalesceThresholdBlockSize` | `10000000` | Schwelle für automatisches Zusammenfassen kleiner Blöcke. |
| `coalesceBinSize` | `128000000` | Zielgröße nach dem Zusammenfassen (Bytes). |
| `serviceCredential` | – | Databricks Service Credential. Ab DBR 16.1. |
| `roleArn` | – | IAM-Rolle, die angenommen wird. |
| `roleExternalId` | – | External ID für `roleArn`. |
| `roleSessionName` | – | Name der Rollen-Session. |
| `stsEndpoint` | – | Eigener STS-Endpoint. |
| `awsAccessKey` / `awsSecretKey` | – | Access Key und Secret (nur gemeinsam). |

### Pub/Sub

`subscriptionId`, `topicId` und `projectId` sind Pflicht.

| Option | Default | Beschreibung |
|---|---|---|
| `subscriptionId` | – | Subscription-ID; wird angelegt, falls nicht vorhanden. |
| `topicId` | – | Topic-ID. |
| `projectId` | – | Google-Cloud-Projekt-ID. |
| `numFetchPartitions` | Hälfte der Executors beim Start | Parallele Fetch-Tasks. |
| `maxBytesPerTrigger` | – | Weiche Obergrenze der Bytes pro Microbatch. |
| `maxRecordsPerFetch` | `1000` | Zeilen pro Task vor der Verarbeitung. |
| `maxFetchPeriod` | `10s` | Fetch-Dauer pro Task. Default empfohlen. |
| `deleteSubscriptionOnStreamStop` | `false` | Subscription beim Stoppen löschen. |
| `serviceCredential` | – | Databricks Service Credential. Ab DBR 16.1. |
| `clientEmail` / `clientId` / `privateKey` / `privateKeyId` | – | Google-Service-Account-Daten; Pflicht ohne Service Credential. |

### Pulsar (ab DBR 14.1)

`service.url` und genau eine von `topic`, `topics`, `topicsPattern` sind Pflicht.

| Option | Default | Beschreibung |
|---|---|---|
| `service.url` | – | Pulsar-Service-URL. |
| `topic` | – | Ein Topic. |
| `topics` | – | Mehrere Topics (kommagetrennt). |
| `topicsPattern` | – | Topic-Muster (Java-Regex). |
| `startingOffsets` | `latest` | Startpunkt: `latest`, `earliest` oder JSON. |
| `failOnDataLoss` | `true` | Fehler bei Datenverlust. |
| `maxBytesPerTrigger` | – | Weiche Obergrenze pro Microbatch. Braucht `admin.url`. |
| `admin.url` | – | HTTP-URL des Admin-Dienstes. |
| `pollTimeoutMs` | `120000` | Lese-Timeout (ms). |
| `allowDifferentTopicSchemas` | `false` | Bei unterschiedlichen Schemas nur Rohwerte liefern. |
| `waitingForNonExistedTopic` | `false` | Warten, bis Topics existieren. |
| `predefinedSubscription` | – | Fester Subscription-Name zur Fortschrittsverfolgung. |
| `subscriptionPrefix` | – | Präfix für die zufällig erzeugte Subscription. |
| `pulsar.client.useKeyStoreTls` | `false` | KeyStore-TLS statt PEM-Dateien. |
| `pulsar.client.*` / `pulsar.admin.*` / `pulsar.reader.*` | – | Weitere Client-, Admin- und Reader-Konfiguration inkl. Authentifizierung. |

---

## Dateiquellen und Delta Lake — gemeinsame Optionen

Gelten für Delta-Lake-Tabellen und dateibasierte Streaming-Quellen (`format("json")`, `format("csv")`, `format("parquet")` …). Viele davon gelten **nicht** beim Streamen aus einer Delta-Tabelle — das ist jeweils vermerkt.

### `cleanSource`

**Default:** `off` · **Werte:** `off`, `delete`, `archive` · **Nicht für Delta-Tabellen.**

Was mit Quelldateien nach der Verarbeitung passiert. `off` tut nichts, `delete` löscht die Datei endgültig, `archive` verschiebt sie nach `sourceArchiveDir`. Bei `archive` muss `sourceArchiveDir` gesetzt sein. Nicht dasselbe wie `cloudFiles.cleanSource`.

```python
df = (spark.readStream.format("json").schema(schema)
      .option("cleanSource", "archive")
      .option("sourceArchiveDir", "/Volumes/main/raw/archive")
      .load("/Volumes/main/raw/landing"))
```

### `sourceArchiveDir`

**Default:** – · **Werte:** Pfad · **Nicht für Delta-Tabellen.**

Archivverzeichnis für `cleanSource = archive`. Die Dateien werden dorthin verschoben, die relative Verzeichnisstruktur bleibt erhalten.

```python
.option("cleanSource", "archive").option("sourceArchiveDir", "/Volumes/main/raw/archive")
```

### `fileNameOnly`

**Default:** `false` · **Werte:** `true`, `false` · **Nicht für Delta-Tabellen.**

Bereits verarbeitete Dateien nur am Dateinamen erkennen statt am vollständigen Pfad. Bei `true` gelten gleichnamige Dateien in verschiedenen Verzeichnissen als dieselbe Datei und werden nicht erneut verarbeitet.

```python
df = spark.readStream.format("csv").schema(schema).option("fileNameOnly", "true").load("/Volumes/main/raw/landing")
```

### `latestFirst`

**Default:** `false` · **Werte:** `true`, `false` · **Nicht für Delta-Tabellen.**

Die zuletzt geänderten Dateien zuerst verarbeiten. Nützlich, wenn aktuelle Daten schnell ankommen sollen. Ist `latestFirst = true` und `maxFilesPerTrigger` oder `maxBytesPerTrigger` gesetzt, wird `maxFileAge` ignoriert.

```python
df = (spark.readStream.format("json").schema(schema)
      .option("latestFirst", "true")
      .option("maxFilesPerTrigger", 100)
      .load("/Volumes/main/raw/landing"))
```

### `maxFileAge`

**Default:** `7d` · **Werte:** Dauer, z. B. `7d`, `4h` · **Nicht für Delta-Tabellen.**

Maximales Alter einer Datei, damit sie noch verarbeitet wird. Bezugspunkt ist die **jüngste Datei**, nicht die aktuelle Systemzeit. Ältere Dateien werden ignoriert.

```python
df = spark.readStream.format("json").schema(schema).option("maxFileAge", "2d").load("/Volumes/main/raw/landing")
```

### `maxCachedFiles`

**Default:** `10000` · **Werte:** positive Ganzzahl oder `0` · **Nicht für Delta-Tabellen.**

Maximale Anzahl unverarbeiteter Dateien, die für die nächsten Microbatches zwischengespeichert werden. `0` schaltet den Cache ab. Erhöhen, wenn pro Trigger sehr viele neue Dateien ankommen.

```python
df = spark.readStream.format("parquet").schema(schema).option("maxCachedFiles", 50000).load("/Volumes/main/raw/landing")
```

### `maxFilesPerTrigger`

**Default:** `1000` bei Delta Lake (und Auto Loader), **kein Limit** bei anderen Dateiquellen · **Werte:** positive Ganzzahl

Obergrenze neuer Dateien pro Microbatch. Zusammen mit `maxBytesPerTrigger` gilt das Limit, das zuerst erreicht wird. Für Auto Loader stattdessen `cloudFiles.maxFilesPerTrigger`.

```python
df = spark.readStream.format("delta").option("maxFilesPerTrigger", 10).load("/path/to/delta-table")
```

### `maxBytesPerTrigger`

**Default:** – · **Werte:** positive Ganzzahl

Weiche Obergrenze für die Datenmenge pro Microbatch. Ist die kleinste Eingabeeinheit größer, wird das Limit überschritten. Zusammen mit `maxFilesPerTrigger` gilt das Limit, das zuerst erreicht wird. Für Auto Loader stattdessen `cloudFiles.maxBytesPerTrigger`.

```python
df = spark.readStream.format("delta").option("maxBytesPerTrigger", 1073741824).table("main.bronze.events")  # ~1 GB
```

---

## Delta Lake

Gelten beim Lesen einer Delta-Tabelle mit `spark.readStream` (`format("delta")` bzw. `.table(...)`).

### `startingVersion`

**Default:** neueste verfügbare Version · **Werte:** positive Ganzzahl, `0` oder `latest`

Delta-Version, ab der gelesen wird (inklusive). `latest` liest nur die neuesten Änderungen. Nicht zusammen mit `startingTimestamp`. Wird ignoriert, wenn schon ein Checkpoint existiert.

```python
df = spark.readStream.option("startingVersion", 5).table("main.silver.orders")
```

### `startingTimestamp`

**Default:** neueste verfügbare Version · **Werte:** Zeitstempel (`2019-01-01T00:00:00.000Z`) oder Datum (`2019-01-01`)

Liest alle Änderungen, die zu oder nach diesem Zeitpunkt committet wurden. Liegt der Zeitpunkt vor allen Commits, startet der Stream beim ältesten verfügbaren Commit. Nicht zusammen mit `startingVersion`. Wird ignoriert, wenn schon ein Checkpoint existiert.

```python
df = spark.readStream.option("startingTimestamp", "2026-01-01").table("main.silver.orders")
```

### `skipChangeCommits`

**Default:** `false` · **Werte:** `true`, `false` · **Ab DBR 12.2 LTS.**

Ignoriert Transaktionen, die bestehende Zeilen löschen oder ändern, und verarbeitet nur Appends. Databricks empfiehlt die Option für die meisten Workloads ohne Change Data Feed.

```python
df = spark.readStream.option("skipChangeCommits", "true").table("main.silver.orders")
```

### `ignoreChanges` (deprecated)

**Default:** `false` · **Werte:** `true`, `false` · **Nur bis DBR 11.3 LTS.**

Gibt neu geschriebene Datendateien nach `UPDATE`, `MERGE INTO`, `DELETE` oder `OVERWRITE` erneut aus. Unveränderte Zeilen können mit ausgegeben werden, also Duplikate downstream behandeln. Deletes werden nicht weitergegeben. Ab DBR 12.2 LTS ersetzt durch `skipChangeCommits`.

```python
df = spark.readStream.option("ignoreChanges", "true").table("main.silver.orders")  # veraltet
```

### `ignoreDeletes` (deprecated)

**Default:** `false` · **Werte:** `true`, `false`

Ignoriert Transaktionen, die Daten an Partitionsgrenzen löschen (nur komplette Partitionen). Andere Deletes und Updates deckt es nicht ab. Stattdessen `skipChangeCommits` verwenden.

```python
df = spark.readStream.option("ignoreDeletes", "true").table("main.silver.orders")  # veraltet
```

### `readChangeFeed` (Alias `readChangeData`)

**Default:** `false` · **Werte:** `true`, `false`

Liest den Change Data Feed. Der Stream liefert dann Änderungen auf Zeilenebene (Inserts, Updates, Deletes) mit zusätzlichen Metadatenspalten.

```python
df = (spark.readStream
      .option("readChangeFeed", "true")
      .option("startingVersion", 0)
      .table("main.silver.orders"))
```

### `failOnDataLoss`

**Default:** `true` · **Werte:** `true`, `false`

Ob die Abfrage fehlschlägt, wenn Quelldaten wegen Log-Retention (`logRetentionDuration`) gelöscht wurden. `false` überspringt fehlende Daten und läuft weiter.

```python
df = spark.readStream.option("failOnDataLoss", "false").table("main.silver.orders")
```

### `excludeRegex`

**Default:** – · **Werte:** Java-Regex

Dateien, deren Pfad auf das Muster passt, werden beim Streaming-Read ausgeschlossen. Nützlich für Dateien, die nicht der erwarteten Namenskonvention folgen.

```python
df = spark.readStream.format("delta").option("excludeRegex", ".*_tmp.*").load("/path/to/delta-table")
```

### `schemaTrackingLocation`

**Default:** – · **Werte:** Pfad

Verzeichnis, in dem Delta Lake Schemaänderungen für den Streaming-Read verfolgt. Pflicht bei Tabellen mit Column Mapping in Kombination mit den `allowSourceColumn*`-Optionen. Muss innerhalb der `checkpointLocation` der Abfrage liegen.

```python
df = (spark.readStream
      .option("schemaTrackingLocation", "/Volumes/main/chk/orders/_schema")
      .table("main.silver.orders"))
```

### `allowSourceColumnDrop`

**Default:** – · **Werte:** Delta-Versionsnummer oder `always` · **Erfordert `schemaTrackingLocation`.**

Stream läuft weiter, nachdem Spalten aus der Quelltabelle gelöscht wurden. Mit einer Versionsnummer werden alle Schemaänderungen bis zu dieser Version akzeptiert.

```python
df = (spark.readStream
      .option("schemaTrackingLocation", "/Volumes/main/chk/orders/_schema")
      .option("allowSourceColumnDrop", "always")
      .table("main.silver.orders"))
```

### `allowSourceColumnRename`

**Default:** – · **Werte:** Delta-Versionsnummer oder `always` · **Erfordert `schemaTrackingLocation`.**

Stream läuft weiter, nachdem Spalten in der Quelltabelle umbenannt wurden. Mit einer Versionsnummer werden alle Schemaänderungen bis zu dieser Version akzeptiert.

```python
.option("schemaTrackingLocation", "/Volumes/main/chk/orders/_schema").option("allowSourceColumnRename", 12)
```

### `allowSourceColumnTypeChange`

**Default:** – · **Werte:** Delta-Versionsnummer oder `always` · **Erfordert `schemaTrackingLocation`.**

Stream läuft weiter, nachdem Spaltentypen in der Quelltabelle geändert wurden (Type Widening). Mit einer Versionsnummer werden alle Schemaänderungen bis zu dieser Version akzeptiert.

```python
.option("schemaTrackingLocation", "/Volumes/main/chk/orders/_schema").option("allowSourceColumnTypeChange", "always")
```

### `withEventTimeOrder`

**Default:** `false` · **Werte:** `true`, `false` · **Ab DBR 11.3 LTS.**

Teilt den ersten Tabellen-Snapshot in Event-Time-Buckets auf. So werden in zustandsbehafteten Abfragen mit Watermark keine Zeilen fälschlich als verspätet verworfen. Nach Beginn der Snapshot-Verarbeitung nur änderbar, wenn der Checkpoint gelöscht wird.

```python
df = (spark.readStream.option("withEventTimeOrder", "true").table("main.silver.events")
      .withWatermark("event_time", "10 minutes"))
```

---

## Kafka

Gelten für `spark.readStream.format("kafka")` und `spark.read.format("kafka")`. Genau **eine** der Optionen `subscribe`, `subscribePattern` oder `assign` ist Pflicht.

### `kafka.bootstrap.servers`

**Default:** – · **Werte:** kommagetrennte `host:port`-Liste

Adressen der Kafka-Broker. Kommen keine Daten an, zuerst diese Liste prüfen. Bei falschen Adressen gibt es oft **keinen Fehler**, weil der Client endlos neu versucht.

```python
df = (spark.readStream.format("kafka")
      .option("kafka.bootstrap.servers", "broker1:9092,broker2:9092")
      .option("subscribe", "orders")
      .load())
```

### `subscribe`

**Default:** – · **Werte:** kommagetrennte Topic-Namen

Topics, die abonniert werden.

```python
.option("subscribe", "orders,payments")
```

### `subscribePattern`

**Default:** – · **Werte:** Java-Regex

Muster für die Topic-Namen, z. B. `topic.*`.

```python
.option("subscribePattern", "sales_.*")
```

### `assign`

**Default:** – · **Werte:** JSON, z. B. `{"topicA":[0,1],"topicB":[2,4]}`

Konkrete Partitionen, die gelesen werden.

```python
.option("assign", '{"orders":[0,1],"payments":[2]}')
```

### `startingOffsets`

**Default:** `latest` (Streaming), `earliest` (Batch) · **Werte:** `earliest`, `latest` oder JSON

Startpunkt beim Lesen. Im JSON steht `-1` für den neuesten und `-2` für den ältesten Offset. Gilt nur beim Start einer neuen Abfrage, eine fortgesetzte Abfrage nutzt den Checkpoint. Neue Partitionen während der Laufzeit starten bei `earliest`. Im Batch-Modus ist `latest` nicht erlaubt.

```python
.option("startingOffsets", '{"orders":{"0":23,"1":-2}}')
```

### `startingOffsetsByTimestamp`

**Default:** – · **Werte:** JSON mit Zeitstempeln in ms, z. B. `{"topicA":{"0":1000,"1":2000}}`

Start-Offsets pro Partition als Zeitstempel. Gibt es zu einem Zeitstempel keinen Offset, entscheidet `startingOffsetsByTimestampStrategy`. Gilt nur beim Start einer neuen Abfrage.

```python
.option("startingOffsetsByTimestamp", '{"orders":{"0":1735689600000,"1":1735689600000}}')
```

### `startingTimestamp`

**Default:** – · **Werte:** Zeitstempel in ms (positive Ganzzahl oder `0`)

Globaler Start-Zeitstempel für alle Partitionen. Gibt es keinen passenden Offset, entscheidet `startingOffsetsByTimestampStrategy`.

```python
.option("startingTimestamp", 1735689600000)
```

### `startingOffsetsByTimestampStrategy`

**Default:** `error` · **Werte:** `error`, `latest`

Verhalten, wenn für einen Zeitstempel aus `startingOffsetsByTimestamp` oder `startingTimestamp` kein Offset existiert. `error` wirft eine Exception, `latest` nimmt den neuesten Offset.

```python
.option("startingTimestamp", 1735689600000).option("startingOffsetsByTimestampStrategy", "latest")
```

### `failOnDataLoss`

**Default:** `true` · **Werte:** `true`, `false`

Ob die Abfrage fehlschlägt, wenn Daten verloren sein könnten, z. B. durch gelöschte Topics oder abgeschnittene Offsets. Databricks schätzt das konservativ, es kann Fehlalarme geben.

```python
.option("failOnDataLoss", "false")
```

### `includeHeaders`

**Default:** `false` · **Werte:** `true`, `false`

Kafka-Header als Spalte in die Ausgabe aufnehmen.

```python
.option("includeHeaders", "true")
```

### `groupIdPrefix`

**Default:** `spark-kafka-source` (Streaming), `spark-kafka-relation` (Batch) · **Werte:** String

Präfix der automatisch erzeugten Consumer-Group-ID. Wird ignoriert, wenn `kafka.group.id` gesetzt ist.

```python
.option("groupIdPrefix", "orders-pipeline")
```

### `kafka.group.id`

**Default:** – · **Werte:** String

Feste Consumer-Group-ID. Vorsicht: Abfragen mit derselben Group-ID stören sich gegenseitig und lesen evtl. nur Teile der Daten, z. B. bei parallelen Batch- und Streaming-Jobs oder schnellem Neustart. Dann `session.timeout.ms` klein setzen.

```python
.option("kafka.group.id", "orders-consumer")
```

### `minPartitions`

**Default:** – · **Werte:** positive Ganzzahl

Mindestanzahl Spark-Partitionen. Große Kafka-Partitionen werden aufgeteilt, um mehr Parallelität zu bekommen (gegen Skew oder Lastspitzen). Ohne die Option gibt es eine Spark-Partition pro Kafka-Partition. Initialisiert die Consumer bei jedem Trigger neu, was mit SSL die Performance beeinträchtigen kann.

```python
.option("minPartitions", 64)
```

### `maxRecordsPerPartition`

**Default:** – · **Werte:** positive Ganzzahl

Maximale Anzahl Datensätze pro Spark-Partition. Mit `minPartitions` kombinierbar, dann gilt die Variante mit mehr Partitionen.

```python
.option("maxRecordsPerPartition", 100000)
```

### `fetchoffset.numretries`

**Default:** `3` · **Werte:** positive Ganzzahl oder `0`

Anzahl Wiederholungen, wenn das Abrufen der Offsets fehlschlägt.

```python
.option("fetchoffset.numretries", 5)
```

### `fetchoffset.retryintervalms`

**Default:** `1000` · **Werte:** positive Ganzzahl oder `0`

Wartezeit in ms zwischen diesen Wiederholungen.

```python
.option("fetchoffset.retryintervalms", 2000)
```

### `kafkaconsumer.polltimeoutms`

**Default:** – · **Werte:** positive Ganzzahl

Timeout in ms für den `poll()`-Aufruf des Kafka-Consumers.

```python
.option("kafkaconsumer.polltimeoutms", 5000)
```

### Nur für Streaming (`readStream`)

#### `maxOffsetsPerTrigger`

**Default:** – · **Werte:** positive Ganzzahl

Maximale Anzahl Offsets pro Trigger, proportional auf die Partitionen verteilt.

```python
.option("maxOffsetsPerTrigger", 100000)
```

#### `minOffsetsPerTrigger`

**Default:** – · **Werte:** positive Ganzzahl

Mindestanzahl Offsets, bevor ein Microbatch startet. Ist `maxTriggerDelay` erreicht, startet er trotzdem.

```python
.option("minOffsetsPerTrigger", 10000).option("maxTriggerDelay", "5m")
```

#### `maxTriggerDelay`

**Default:** `15m` · **Werte:** Dauer, z. B. `10m`, `600s`

Maximale Wartezeit auf `minOffsetsPerTrigger`, bevor getriggert wird.

```python
.option("maxTriggerDelay", "2m")
```

#### `bytesEstimateWindowLength`

**Default:** `300s` · **Werte:** Dauer, z. B. `10m`, `600s`

Zeitfenster zur Schätzung der Metrik `estimatedTotalBytesBehindLatest`.

```python
.option("bytesEstimateWindowLength", "10m")
```

### Authentifizierung

Databricks empfiehlt für Cloud-Kafka-Dienste (AWS MSK, Azure Event Hubs, Google Cloud Managed Kafka) eine **Unity Catalog Service Credential**. Dann sind `kafka.sasl.mechanism`, `kafka.sasl.jaas.config` und `kafka.security.protocol` nicht nötig.

- `databricks.serviceCredential` — Name der Service Credential (ab DBR 16.1). Default: –
- `databricks.serviceCredential.scope` — OAuth-Scope, nur wenn Databricks ihn nicht selbst ableiten kann. Default: –

```python
df = (spark.readStream.format("kafka")
      .option("kafka.bootstrap.servers", "b-1.msk.example:9098")
      .option("subscribe", "orders")
      .option("databricks.serviceCredential", "msk-credential")
      .load())
```

Ohne Service Credential: SASL/SSL-Optionen als `kafka.*`-Eigenschaften, alle ohne Default:

- `kafka.security.protocol` — z. B. `SASL_SSL`, `SSL`, `PLAINTEXT`
- `kafka.sasl.mechanism` — z. B. `PLAIN`, `SCRAM-SHA-256`, `SCRAM-SHA-512`, `OAUTHBEARER`, `AWS_MSK_IAM`
- `kafka.sasl.jaas.config` — JAAS-Login-Konfiguration
- `kafka.sasl.login.callback.handler.class`, `kafka.sasl.client.callback.handler.class` — Callback-Handler-Klassen
- `kafka.ssl.truststore.location`, `kafka.ssl.truststore.password` — Truststore
- `kafka.ssl.keystore.location`, `kafka.ssl.keystore.password` — Keystore

```python
jaas = 'org.apache.kafka.common.security.plain.PlainLoginModule required username="{}" password="{}";'.format(
    dbutils.secrets.get("kafka", "user"), dbutils.secrets.get("kafka", "pw"))
df = (spark.readStream.format("kafka")
      .option("kafka.bootstrap.servers", "broker1:9093")
      .option("subscribe", "orders")
      .option("kafka.security.protocol", "SASL_SSL")
      .option("kafka.sasl.mechanism", "PLAIN")
      .option("kafka.sasl.jaas.config", jaas)
      .load())
```

---

## Kinesis

Gelten für `spark.readStream.format("kinesis")`. Genau **eine** der Optionen `streamName` oder `streamARN` ist Pflicht.

### `streamName`

**Default:** – · **Werte:** kommagetrennte Stream-Namen

Kinesis-Streams, die gelesen werden.

```python
df = (spark.readStream.format("kinesis")
      .option("streamName", "clickstream")
      .option("region", "eu-central-1")
      .option("serviceCredential", "kinesis-credential")
      .load())
```

### `streamARN`

**Default:** – · **Werte:** kommagetrennte Stream-ARNs · **Ab DBR 16.1.**

Streams per ARN statt per Name.

```python
.option("streamARN", "arn:aws:kinesis:eu-central-1:123456789012:stream/clickstream")
```

### `region`

**Default:** lokal ermittelte Region · **Werte:** String

Region, in der die Streams liegen.

```python
.option("region", "eu-central-1")
```

### `endpoint`

**Default:** lokal ermittelte Region · **Werte:** String

Regionaler Endpoint für Kinesis Data Streams.

```python
.option("endpoint", "https://kinesis.eu-central-1.amazonaws.com")
```

### `initialPosition`

**Default:** `latest` · **Werte:** `latest`, `trim_horizon`, `earliest`, `at_timestamp`

Startpunkt im Stream. `trim_horizon` ist ein Alias für `earliest`. `at_timestamp` erwartet JSON im Java-Zeitformat, optional mit eigenem `format`.

```python
.option("initialPosition", '{"at_timestamp": "06/25/2020 10:23:45 PDT", "format": "MM/dd/yyyy HH:mm:ss ZZZ"}')
```

### `consumerMode`

**Default:** `polling` · **Werte:** `polling`, `efo` · **Ab DBR 11.3 LTS.**

Consumer-Typ. `efo` (Enhanced Fan-Out) gibt jedem Shard einen eigenen Durchsatz von 2 MB/s.

```python
.option("consumerMode", "efo")
```

### `consumerName`

**Default:** ID der Streaming-Abfrage · **Werte:** ein Name oder kommagetrennte Liste (eine pro Stream) · **Ab DBR 11.3 LTS.**

Name, unter dem die Abfrage im EFO-Modus bei Kinesis registriert wird.

```python
.option("consumerMode", "efo").option("consumerName", "clickstream-bronze")
```

### `consumerNamePrefix`

**Default:** `databricks_` · **Werte:** String · **Ab DBR 16.0.**

Präfix vor `consumerName` bei der EFO-Registrierung.

```python
.option("consumerNamePrefix", "prod_")
```

### `consumerRefreshInterval`

**Default:** `300s` (max. `3600s`) · **Werte:** Dauer, z. B. `1s` · **Ab DBR 11.3 LTS.**

Intervall, in dem die EFO-Registrierung geprüft und erneuert wird.

```python
.option("consumerRefreshInterval", "600s")
```

### `registeredConsumerId`

**Default:** – · **Werte:** kommagetrennte Consumer-Namen oder -ARNs · **Ab DBR 16.1.**

Bereits registrierte EFO-Consumer verwenden.

```python
.option("registeredConsumerId", "clickstream-consumer").option("registeredConsumerIdType", "name")
```

### `registeredConsumerIdType`

**Default:** – · **Werte:** `name`, `ARN` · **Ab DBR 16.1.**

Ob `registeredConsumerId` Namen oder ARNs enthält.

```python
.option("registeredConsumerIdType", "ARN")
```

### `requireConsumerDeregistration`

**Default:** `false` · **Werte:** `true`, `false` · **Ab DBR 11.3 LTS.** Erfordert `consumerMode = efo`.

EFO-Consumer beim Beenden der Abfrage abmelden.

```python
.option("consumerMode", "efo").option("requireConsumerDeregistration", "true")
```

### `fetchBufferSize`

**Default:** `20gb` · **Werte:** Byte-String, z. B. `2gb`, `10mb`

Datenmenge, die für den nächsten Trigger gepuffert wird. Abbruchbedingung, keine harte Obergrenze.

```python
.option("fetchBufferSize", "2gb")
```

### `maxFetchDuration`

**Default:** `10s` · **Werte:** Dauer, z. B. `1m`

Wie lange vorab geholte Daten gepuffert werden, bevor sie zur Verarbeitung freigegeben werden.

```python
.option("maxFetchDuration", "200ms")
```

### `maxFetchRate`

**Default:** `1.0` (max. `2.0`) · **Werte:** positive Dezimalzahl

Maximale Prefetch-Rate pro Shard in MB/s. Begrenzt die Abrufe, um Throttling zu vermeiden. Kinesis erlaubt höchstens 2,0 MB/s.

```python
.option("maxFetchRate", 1.5)
```

### `minFetchPeriod`

**Default:** `400ms` (min. `200ms`) · **Werte:** Dauer, z. B. `1s`

Mindestabstand zwischen zwei Prefetch-Versuchen. Kinesis erlaubt höchstens 5 Abrufe pro Sekunde, daher mindestens 200 ms.

```python
.option("minFetchPeriod", "1s")
```

### `maxRecordsPerFetch`

**Default:** `10000` · **Werte:** positive Ganzzahl

Datensätze pro Kinesis-API-Aufruf. Mit der Kinesis Producer Library aggregierte Datensätze können mehr ergeben.

```python
.option("maxRecordsPerFetch", 5000)
```

### `shardsPerTask`

**Default:** `5` · **Werte:** positive Ganzzahl

Shards, die ein Spark-Task parallel vorab holt. Für minimale Latenz: Anzahl Cores ≥ Anzahl Shards / `shardsPerTask`. Nicht zusammen mit `maxPartitions`.

```python
.option("shardsPerTask", 2)
```

### `maxPartitions`

**Default:** – · **Werte:** positive Ganzzahl · **Ab DBR 19.**

Anzahl Spark-Tasks für Kinesis. Spark nutzt `min(aktive Shards, maxPartitions)` Tasks. Nicht zusammen mit `shardsPerTask`.

```python
.option("maxPartitions", 16)
```

### `shardFetchInterval`

**Default:** `1s` · **Werte:** Dauer, z. B. `2m`

Intervall, in dem Kinesis auf Resharding geprüft wird.

```python
.option("shardFetchInterval", "30s")
```

### `maxShardsPerDescribe`

**Default:** `100` · **Werte:** positive Ganzzahl bis `10000`

Maximale Anzahl Shards pro API-Aufruf beim Auflisten.

```python
.option("maxShardsPerDescribe", 500)
```

### `coalesceThresholdBlockSize`

**Default:** `10000000` · **Werte:** positive Ganzzahl

Schwelle für das automatische Zusammenfassen: Ist die durchschnittliche Blockgröße kleiner, werden die vorab geholten Blöcke auf `coalesceBinSize` zusammengefasst.

```python
.option("coalesceThresholdBlockSize", 5000000)
```

### `coalesceBinSize`

**Default:** `128000000` · **Werte:** positive Ganzzahl

Ungefähre Zielgröße eines Blocks in Bytes nach dem Zusammenfassen.

```python
.option("coalesceBinSize", 64000000)
```

### Authentifizierung

Empfohlen ist eine **Service Credential**. Alternativ IAM-Rolle oder Access Keys. Alle ohne Default:

- `serviceCredential` — Name der Databricks Service Credential (ab DBR 16.1)
- `roleArn` — ARN der IAM-Rolle, die angenommen wird
- `roleExternalId` — optionale External ID für `roleArn`
- `roleSessionName` — Bezeichner der Rollen-Session
- `stsEndpoint` — eigener STS-Endpoint für `roleArn`
- `awsAccessKey`, `awsSecretKey` — Access Key und Secret, nur gemeinsam

```python
df = (spark.readStream.format("kinesis")
      .option("streamName", "clickstream")
      .option("region", "eu-central-1")
      .option("roleArn", "arn:aws:iam::123456789012:role/kinesis-reader")
      .option("roleSessionName", "databricks-bronze")
      .load())
```

---

## Pub/Sub

Gelten für `spark.readStream.format("pubsub")`. `subscriptionId`, `topicId` und `projectId` sind Pflicht.

### `subscriptionId`

**Default:** – · **Pflicht.**

ID der Subscription. Existiert sie nicht, legt der Connector sie an.

```python
df = (spark.readStream.format("pubsub")
      .option("subscriptionId", "orders-sub")
      .option("topicId", "orders")
      .option("projectId", "my-gcp-project")
      .option("serviceCredential", "pubsub-credential")
      .load())
```

### `topicId`

**Default:** – · **Pflicht.**

ID des Topics.

```python
.option("topicId", "orders")
```

### `projectId`

**Default:** – · **Pflicht.**

ID des Google-Cloud-Projekts.

```python
.option("projectId", "my-gcp-project")
```

### `numFetchPartitions`

**Default:** die Hälfte der beim Start verfügbaren Executors · **Werte:** positive Ganzzahl

Anzahl paralleler Spark-Tasks, die Zeilen aus der Subscription holen.

```python
.option("numFetchPartitions", 8)
```

### `maxBytesPerTrigger`

**Default:** – · **Werte:** positive Ganzzahl

Weiche Obergrenze der Bytes pro Microbatch.

```python
.option("maxBytesPerTrigger", 104857600)
```

### `maxRecordsPerFetch`

**Default:** `1000` · **Werte:** positive Ganzzahl

Zeilen, die jeder Task vor der Verarbeitung holt.

```python
.option("maxRecordsPerFetch", 5000)
```

### `maxFetchPeriod`

**Default:** `10s` · **Werte:** Dauer, z. B. `1s`, `1m`

Wie lange jeder Task vor der Verarbeitung holt. Databricks empfiehlt den Default.

```python
.option("maxFetchPeriod", "10s")
```

### `deleteSubscriptionOnStreamStop`

**Default:** `false` · **Werte:** `true`, `false`

Bei `true` wird die Subscription aus `subscriptionId` gelöscht, wenn die Abfrage endet.

```python
.option("deleteSubscriptionOnStreamStop", "true")
```

### Authentifizierung

Empfohlen: `serviceCredential` (Name der Databricks Service Credential, ab DBR 16.1). Ohne Service Credential sind diese vier Optionen Pflicht, alle ohne Default: `clientEmail`, `clientId`, `privateKey`, `privateKeyId` (Daten des Google Service Accounts).

```python
df = (spark.readStream.format("pubsub")
      .option("subscriptionId", "orders-sub").option("topicId", "orders").option("projectId", "my-gcp-project")
      .option("clientEmail", dbutils.secrets.get("gcp", "client_email"))
      .option("clientId", dbutils.secrets.get("gcp", "client_id"))
      .option("privateKey", dbutils.secrets.get("gcp", "private_key"))
      .option("privateKeyId", dbutils.secrets.get("gcp", "private_key_id"))
      .load())
```

---

## Pulsar

Gelten für `spark.readStream.format("pulsar")`, **ab DBR 14.1**. `service.url` ist Pflicht, dazu genau **eine** der Optionen `topic`, `topics` oder `topicsPattern`.

### `service.url`

**Default:** – · **Pflicht.**

Service-URL von Pulsar, z. B. `pulsar://broker.example.com:6650`.

```python
df = (spark.readStream.format("pulsar")
      .option("service.url", "pulsar://broker.example.com:6650")
      .option("topic", "orders")
      .load())
```

### `topic`

**Default:** – · **Werte:** ein Topic-Name

Ein einzelnes Topic.

```python
.option("topic", "orders")
```

### `topics`

**Default:** – · **Werte:** kommagetrennte Topic-Namen

Mehrere Topics.

```python
.option("topics", "orders,payments")
```

### `topicsPattern`

**Default:** – · **Werte:** Java-Regex

Muster für die Topic-Namen.

```python
.option("topicsPattern", "persistent://public/default/sales-.*")
```

### `startingOffsets`

**Default:** `latest` · **Werte:** `latest`, `earliest` oder JSON

Startpunkt beim Lesen.

```python
.option("startingOffsets", "earliest")
```

### `failOnDataLoss`

**Default:** `true` · **Werte:** `true`, `false`

Ob die Abfrage bei Datenverlust fehlschlägt, z. B. wenn Topics gelöscht werden oder Nachrichten durch die Retention verfallen.

```python
.option("failOnDataLoss", "false")
```

### `maxBytesPerTrigger`

**Default:** – · **Werte:** positive Ganzzahl · **Erfordert `admin.url`.**

Weiche Obergrenze der Bytes pro Microbatch.

```python
.option("admin.url", "http://broker.example.com:8080").option("maxBytesPerTrigger", 104857600)
```

### `admin.url`

**Default:** – · **Werte:** URL

HTTP-URL des Pulsar-Admin-Dienstes. Pflicht, wenn `maxBytesPerTrigger` gesetzt ist.

```python
.option("admin.url", "http://broker.example.com:8080")
```

### `pollTimeoutMs`

**Default:** `120000` · **Werte:** positive Ganzzahl

Timeout in ms beim Lesen von Nachrichten.

```python
.option("pollTimeoutMs", 60000)
```

### `allowDifferentTopicSchemas`

**Default:** `false` · **Werte:** `true`, `false`

Bei mehreren Topics mit unterschiedlichen Schemas die automatische Deserialisierung abschalten. Bei `true` kommen nur die Rohwerte zurück.

```python
.option("topics", "orders,payments").option("allowDifferentTopicSchemas", "true")
```

### `waitingForNonExistedTopic`

**Default:** `false` · **Werte:** `true`, `false`

Ob der Connector wartet, bis die Topics angelegt sind.

```python
.option("waitingForNonExistedTopic", "true")
```

### `predefinedSubscription`

**Default:** – · **Werte:** String

Fester Subscription-Name, über den der Connector den Fortschritt der Spark-Anwendung verfolgt.

```python
.option("predefinedSubscription", "spark-orders")
```

### `subscriptionPrefix`

**Default:** – · **Werte:** String

Präfix für die zufällig erzeugte Subscription, über die der Connector den Fortschritt verfolgt.

```python
.option("subscriptionPrefix", "spark-")
```

### Weitere Pulsar-Konfiguration und Authentifizierung

Zusätzliche Einstellungen über Präfixe: `pulsar.admin.*` (Admin), `pulsar.client.*` (Client inkl. Auth), `pulsar.reader.*` (Reader). Zugangsdaten am besten in Secrets ablegen.

Client-Authentifizierung, alle ohne Default außer `useKeyStoreTls`:

- `pulsar.client.authPluginClassName` — Auth-Plugin-Klasse, z. B. `org.apache.pulsar.client.impl.auth.AuthenticationTls`
- `pulsar.client.authParams` — Zugangsdaten für das Plugin, z. B. `tlsCertFile:…,tlsKeyFile:…`
- `pulsar.client.useKeyStoreTls` — KeyStore-TLS statt PEM-Dateien. Default: `false`
- `pulsar.client.tlsTrustStoreType` — Format des Truststores, z. B. `JKS`
- `pulsar.client.tlsTrustStorePath` — Pfad zum Truststore. Pflicht bei `useKeyStoreTls = true`
- `pulsar.client.tlsTrustStorePassword` — Passwort des Truststores

Für einen PulsarAdmin gibt es dieselben Einstellungen als `pulsar.admin.*` (`authPluginClassName`, `authParams`, `useTls`, `tlsAllowInsecureConnection`, `tlsTrustCertsFilePath`, `useKeyStoreTls`, `tlsTrustStoreType`, `tlsTrustStorePath`, `tlsTrustStorePassword`), alle ohne Default.

```python
df = (spark.readStream.format("pulsar")
      .option("service.url", "pulsar+ssl://broker.example.com:6651")
      .option("topic", "orders")
      .option("pulsar.client.authPluginClassName", "org.apache.pulsar.client.impl.auth.AuthenticationTls")
      .option("pulsar.client.authParams",
              "tlsCertFile:/Volumes/main/certs/role.cert.pem,tlsKeyFile:/Volumes/main/certs/role.key-pk8.pem")
      .load())
```
