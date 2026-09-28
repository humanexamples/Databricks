# Structured Streaming: Grundlagen und Ausführungsmodell

## 1. Was ist Structured Streaming?

- Near-Realtime-Engine mit Exactly-once-Garantien, gleiche APIs wie Spark-Batch — Query wird formuliert wie auf statischen Daten, Engine führt sie inkrementell aus.
- Datenquellen gelten als unbeschränkt (unendlich) → Sortier-Transformationen über die gesamte Quelle nicht unterstützt. Aggregationen/Joins brauchen i. d. R. Zustand (Watermarks, Fenster, Output-Modus).
- **Empfehlung:** Für neue ETL-/Ingestion-/Streaming-Workloads bevorzugt Databricks Lakeflow-Pipelines (Spark Declarative Pipelines) — ähnliche Syntax, aber Checkpoints/Trigger/Zustand/Metadaten werden automatisch verwaltet.

| Baustein | Zweck |
|---|---|
| Auto Loader | Neue Dateien inkrementell/effizient aus Cloud-Speicher verarbeiten |
| Delta-Lake-Streaming-Reads/-Writes | Delta-Tabellen als Quelle/Senke, Exactly-once |
| Standard-Connectors | Message Busse, Queues, Unternehmensanwendungen |
| Micro-Batch-Größe | Eingaberate begrenzen → konsistente Batches, weniger Delay |
| Checkpoints | Fehlertoleranz, Exactly-once |
| Output-Modus | Append / Update / Complete für zustandsbehaftete Queries |
| Trigger-Intervalle | Latenz vs. Kosten |
| Real-Time-Modus | Sub-Sekunden End-to-End-Latenz |
| Zustandslos/zustandsbehaftet | Aggregationen, Joins, Dedup über zustandsbehaftete Operatoren |
| Watermarks | Wartezeit auf verspätete Daten |
| StreamingQueryListener | Fortschritt/Performance-Metriken |
| Unity Catalog | Governance/Zugriffskontrolle |

## 2. Ersten Structured-Streaming-Workload ausführen

### 2.1 Auto Loader aus Objektspeicher lesen

- `readStream` konfigurieren lädt noch keine Daten — erst eine Aktion (Write in Senke) startet den Job. `display()` startet ebenfalls einen Job, aber nicht für Produktion verwenden.

```python
file_path = "/databricks-datasets/structured-streaming/events"
checkpoint_path = "/tmp/ss-tutorial/_checkpoint"

raw_df = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", checkpoint_path)
    .load(file_path)
)
```

### 2.2 Streaming-Transformation

- Die meisten Databricks/Spark-SQL-Transformationen funktionieren auf Streams; auch MLflow-Modelle als UDF für Streaming-Vorhersagen ladbar.

```python
from pyspark.sql.functions import col, current_timestamp

transformed_df = (raw_df.select(
    "*",
    col("_metadata.file_path").alias("source_file"),
    current_timestamp().alias("processing_time")
    )
)
```

### 2.3 Inkrementelles Batch-Schreiben nach Delta Lake

```python
target_path = "/tmp/ss-tutorial/"
checkpoint_path = "/tmp/ss-tutorial/_checkpoint"

transformed_df.writeStream \
    .trigger(availableNow=True) \
    .option("checkpointLocation", checkpoint_path) \
    .option("path", target_path) \
    .start()
# Ergebnis: verarbeitet alle bislang unverarbeiteten Datensätze, beendet sich danach selbst → Code gefahrlos wiederholt ausführbar
```

- Jeder Streaming-Writer braucht einen eigenen, eindeutigen Checkpoint-Speicherort (liefert Stream-Identität, trackt Datensätze + Zustand).
- **Warnung:** Laufende Queries können Auto Termination der Compute verhindern → unerwartete Kosten. Streams aktiv beenden.

### 2.4 Delta Lake → Delta Lake

```python
(spark.readStream
    .table("<table-name1>")
    .join(spark.read.table("<table-name2>"), on="<id>", how="left")
    .writeStream
    .trigger(availableNow=True)
    .option("checkpointLocation", "<checkpoint-path>")
    .toTable("<table-name3>")
)
```

### 2.5 Kafka → Kafka

- Schreiben in Cloud-Objektspeicher fügt Latenz hinzu. Für niedrigste Latenz + Persistierung: zwei getrennte Jobs (einer für Lakehouse-Ingestion, einer für Near-Realtime-Transformationen zu Messaging-Bus-Senken).

```python
(spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "<server:ip>")
    .option("subscribe", "<topic>")
    .option("startingOffsets", "latest")
    .load()
    .join(spark.read.table("<table-name>"), on="<id>", how="left")
    .writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "<server:ip>")
    .option("topic", "<topic>")
    .option("checkpointLocation", "<checkpoint-path>")
    .start()
)
```

## 3. Praxismuster

### 3.1 Schreiben nach Cassandra

- Über Spark-Cassandra-Connector (passende `spark-cassandra-connector-assembly`-Version nötig).

```python
spark.conf.set("spark.cassandra.connection.host", "host1,host2")

df.writeStream \
  .format("org.apache.spark.sql.cassandra") \
  .outputMode("append") \
  .option("checkpointLocation", "/path/to/checkpoint") \
  .option("keyspace", "keyspace_name") \
  .option("table", "table_name") \
  .start()
```

### 3.2 `foreachBatch()` — Batch-Writer wiederverwenden (z. B. Azure Synapse)

- Erlaubt, bestehende Batch-Datenschreiber für Streaming-Ergebnisse wiederzuverwenden.

```python
from pyspark.sql.functions import *
from pyspark.sql import *

def writeToSQLWarehouse(df, epochId):
  df.write \
    .format("com.databricks.spark.sqldw") \
    .mode('overwrite') \
    .option("url", "jdbc:sqlserver://<connection-string>") \
    .option("forward_spark_azure_storage_credentials", "true") \
    .option("dbtable", "my_table_in_dw_copy") \
    .option("tempdir", "wasbs://<container>@<account>.blob.core.windows.net/<dir>") \
    .save()

spark.conf.set("spark.sql.shuffle.partitions", "1")

query = (
  spark.readStream.format("rate").load()
    .selectExpr("value % 10 as key")
    .groupBy("key")
    .count()
    .toDF("key", "count")
    .writeStream
    .foreachBatch(writeToSQLWarehouse)
    .outputMode("update")
    .start()
    )
# Ergebnis: jeder Micro-Batch wird per Batch-API nach Synapse geschrieben (overwrite je epochId)
```

### 3.3 `MERGE` in Delta Lake über `foreachBatch` (Upserts aus einem Stream)

- Reguläres `MERGE` wird von Structured Streaming nicht direkt unterstützt (Streaming-Writer können keine beliebige Upsert-Logik). `foreachBatch()` wendet `MERGE` pro Micro-Batch an — nützlich für: effizientere Writes (Update- statt Complete-Mode-Neuschreibung), fortlaufendes Anwenden eines Change-Streams, automatische Dedup über insert-only Merges.

**Variante 1 — SQL-`MERGE` via Temp View:**

```python
def upsertToDelta(microBatchOutputDF, batchId):
  microBatchOutputDF.createOrReplaceTempView("updates")
  microBatchOutputDF.sparkSession.sql("""
    MERGE INTO aggregates t
    USING updates s
    ON s.key = t.key
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
  """)

(streamingAggregatesDF.writeStream
  .foreachBatch(upsertToDelta)
  .outputMode("update")
  .start())
```

**Variante 2 — Delta-API (`DeltaTable.merge`):**

```python
from delta.tables import *
deltaTable = DeltaTable.forName(spark, "table_name")

def upsertToDelta(microBatchOutputDF, batchId):
  (deltaTable.alias("t").merge(
      microBatchOutputDF.alias("s"), "s.key = t.key")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll()
    .execute())

(streamingAggregatesDF.writeStream
  .foreachBatch(upsertToDelta)
  .outputMode("update")
  .start())
```

**Idempotente Schreibvorgänge (`txnAppId` / `txnVersion`):** Bei mehreren Senken in `foreachBatch` muss jeder Write idempotent sein (Wiederholung nach Abbruch darf keine Duplikate erzeugen).

- `txnAppId`: eindeutige Kennung (z. B. StreamingQuery-ID oder eigener String).
- `txnVersion`: monoton steigender Zähler (typischerweise `batchId`).
- Delta nutzt beide, um doppelte Writes zu erkennen/unterdrücken.

```python
app_id = ...  # eindeutige Anwendungskennung

def writeToDeltaLakeTableIdempotent(batch_df, batch_id):
  batch_df.write.format(...).option("txnVersion", batch_id).option("txnAppId", app_id).save(...)  # Ziel 1
  batch_df.write.format(...).option("txnVersion", batch_id).option("txnAppId", app_id).save(...)  # Ziel 2

streamingDF.writeStream.foreachBatch(writeToDeltaLakeTableIdempotent).start()
```

**Gotchas `foreachBatch`/`MERGE`:**

- `MERGE`-Statement muss idempotent sein (Neustarts können denselben Batch erneut anwenden).
- Checkpoint gelöscht + Query mit neuem Checkpoint neu gestartet → andere `txnAppId` vergeben (neuer Checkpoint startet wieder bei Batch-ID 0; Delta nutzt Batch-ID + `txnAppId` als eindeutigen Key).
- `merge` liest Daten wiederholt → Input-Data-Rate-Metriken können ein Vielfaches der echten Rate zeigen. Abhilfe: Batch-DataFrame vor Merge cachen, danach uncachen.
- Bei mehreren Senken: lieber separater Streaming-Write pro Senke statt mehrerer Writes in einem `foreachBatch` (sonst serialisiert, weniger Parallelität/mehr Latenz).

## 4. Output-Modus

- Nur zustandsbehaftete Streams mit Aggregationen brauchen eine Output-Mode-Konfiguration. Joins: nur Append. Dedup: vom Output-Modus unbeeinflusst. `mapGroupsWithState`/`flatMapGroupsWithState`: eigene Ausgabelogik, Output-Modus wirkungslos. Zustandslos: alle Modi verhalten sich gleich.

| Output-Modus | Beschreibung |
|---|---|
| **Append (Standard)** | Nur Zeilen, die sich künftig nicht mehr ändern (zustandsbehaftete Operatoren nutzen dafür den Watermark). |
| **Update** | Alle Zeilen, die sich seit letztem Trigger geändert haben — auch wenn sie sich später nochmal ändern könnten. |
| **Complete** | Nur für Streaming-Aggregationen. Jeder Trigger gibt alle jemals erzeugten Ergebniszeilen aus. |

- **Hinweis:** Complete Mode skaliert schlecht mit wachsender Datenmenge → Databricks empfiehlt für viele zustandsbehaftete Fälle Materialized Views (gleiche Semantik, inkrementell).

### Produktionsüberlegungen

- **Semantik:** genau eine Aktion pro Datensatz (z. B. Benachrichtigung) → Append (schreibt jeden Datensatz einmal). Möglichst aktuelle Ergebnisse (Echtzeit-Feature-Reads, Dashboards) → Update.
- **Kompatibilität:** Kafka unterstützt alle 3 Modi. Delta Lake (Basis aller UC-verwalteten Tabellen): Append + Complete, **nicht** Update (für Update-ähnliches Verhalten → `MERGE` via `foreachBatch`, Abschnitt 3.3).
- **Latenz/Kosten:** Append gibt erst nach Watermark-Ablauf aus (z. B. 1 h Watermark = mind. 1 h Latenz). Update schreibt pro Trigger pro geändertem Aggregat → teuer bei pro-Datensatz abgerechneten Senken.

### Konfiguration

```python
# Append (Standard)
df.writeStream.toTable("target_table")
df.writeStream.outputMode("append").toTable("target_table")

# Update
df.writeStream.outputMode("update").toTable("target_table")

# Complete
df.writeStream.outputMode("complete").toTable("target_table")
```

### Durchgerechnetes Beispiel

Stündlicher Umsatz, Watermark-Verzögerung 15 min. Erster Micro-Batch: $15 @14:40, $10 @14:30, $30 @15:10 → Watermark = 15:10 − 15min = 14:55. Zustand: `[2pm,3pm]: $25`, `[3pm,4pm]: $30`.

| Modus | Ergebnis (1. Batch) |
|---|---|
| Append | Nichts — Watermark 14:55 liegt vor beiden Fensterenden, beide könnten noch neue Daten erhalten. |
| Update | Beide Fenster (beide haben sich geändert). |
| Complete | Alle Datensätze. |

Neuer Datensatz $20 @15:20 → Watermark → 15:05. Zustand: `[2pm,3pm]: $25`, `[3pm,4pm]: $50`.

| Modus | Ergebnis (2. Batch) |
|---|---|
| Append | `[2pm,3pm]` (Watermark 15:05 > Fensterende, kann sich nicht mehr ändern). |
| Update | `[3pm,4pm]` ($30 → $50). |
| Complete | Alle Datensätze. |

- **Merksatz:** Append = einmalig nach Watermark-Ablauf; Update = alle seit letztem Trigger geänderten; Complete = jeder Trigger alle jemals erzeugten Zeilen.

## 5. Trigger-Intervalle

- **Wichtig:** Ohne explizite Trigger-Konfiguration → `processingTime` mit Intervall `0` (prüft alle paar ms auf neue Daten) → kann hohes Volumen an Cloud-Storage-API-Calls/Kosten erzeugen.

| Trigger-Modus | Syntax (Python) | Am besten für |
|---|---|---|
| Unspecified (Standard) | — | Allgemeines Streaming, 3–5 s Latenz. Entspricht `processingTime`=0ms, läuft solange neue Daten eintreffen. |
| Processing Time | `.trigger(processingTime='10 seconds')` | Balance Kosten/Performance, weniger Overhead durch häufiges Prüfen. |
| Available Now | `.trigger(availableNow=True)` | Geplante inkrementelle Batch-Verarbeitung — verarbeitet alles zum Start Verfügbare. |
| Real-time Mode | `.trigger(realTime='5 minutes')` | Ultra-niedrige Latenz (Betrugserkennung, Echtzeit-Personalisierung). Wert = Micro-Batch-Länge; 5 min minimieren Overhead/Batch (z. B. Query-Kompilierung). |
| Continuous | `.trigger(continuous='1 second')` | **Nicht unterstützt** (experimentelles Spark-OSS-Feature) — stattdessen Real-time Mode. |

- **Serverless Compute:** nur `Trigger.AvailableNow()` und `Trigger.Once()` unterstützt; empfohlen: `Trigger.AvailableNow()`.
- `processingTime`: feste Micro-Batch-Intervalle, balanciert Latenzanforderung vs. Eintreffrate.
- `AvailableNow`: **Wichtig:** ab DBR 11.3 LTS ist `Trigger.Once` veraltet → stattdessen `Trigger.AvailableNow` für inkrementelle Batches. Batch-Größe konfigurierbar (z. B. `maxBytesPerTrigger`, quellenabhängig).

Minimale DBR-Version je Quelle für `AvailableNow`:

| Quelle | Minimale DBR-Version |
|---|---|
| File-Quellen (JSON, Parquet usw.) | 9.1 LTS |
| Delta Lake | 10.4 LTS |
| Auto Loader | 10.4 LTS |
| Apache Kafka | 10.4 LTS |
| Kinesis | 13.1 |
| OpenSharing (`responseFormat=delta`; `parquet` benötigt `delta-sharing-client` ≥ 1.4.0) | 18.0 |

- **Real-time Mode:** End-to-End-Latenz < 1 s (Tail), typischerweise ~300 ms. Nicht zu verwechseln mit Spark OSS "Continuous Processing" (seit 2.3 experimentell, von Databricks nicht unterstützt/empfohlen) — auch nicht mit Continuous Processing in Spark/Lakeflow Declarative Pipelines.

### Trigger-Intervalle zwischen Läufen ändern

- Änderbar mit demselben Checkpoint. Stoppt Query mitten im Micro-Batch → dieser wird noch mit alter Konfig fertig verarbeitet, dann greift die neue.
- **Zeitbasiert → `AvailableNow`:** ein Micro-Batch kann noch als inkrementeller Batch laufen, bevor alle verfügbaren Datensätze abgearbeitet sind.
- **`AvailableNow` → zeitbasiert:** Verarbeitung setzt fort für alles, was zum letzten `AvailableNow`-Lauf verfügbar war.
- **Query-Fehler:** Trigger-Wechsel behebt keinen Fehler — der fehlgeschlagene Batch muss idempotent abgeschlossen werden. Abhilfe: Compute hochskalieren; selten: Neustart mit neuem Checkpoint.

## 6. Batch-Größe (Admission Controls)

- Begrenzen Eingaberate → konsistente Batch-Größe, verhindern Spill/kaskadierende Verzögerungen durch zu große Batches. Delta Lake und Auto Loader bieten dieselben Optionen.
- Änderbar ohne Checkpoint-Reset (Abschnitt 7) — wirkt sich aber auf Performance aus, ggf. Compute-Konfig anpassen.
- **Warnung:** Ist bereits ein Micro-Batch geplant, greift eine Admission-Control-Änderung erst nach dessen Abschluss. Stoppt der Stream z. B. nach fehlgeschlagener Transaktion, kann Checkpoint-Löschung nötig sein, damit die Transaktion mit den neuen Controls erneut verarbeitet wird (Structured Streaming ist idempotent — Micro-Batches müssen bei Wiederholung dieselben Daten enthalten).

| Option | Beschreibung | Standardwert |
|---|---|---|
| `maxFilesPerTrigger` (`cloudFiles.maxFilesPerTrigger` für Auto Loader) | Obergrenze der pro Micro-Batch verarbeiteten Dateien. | 1000 (Delta Lake, Auto Loader); andere Spark-File-Quellen: kein Maximum. |
| `maxBytesPerTrigger` (`cloudFiles.maxBytesPerTrigger` für Auto Loader) | "Soft Max" für Datenmenge pro Micro-Batch — kann überschritten werden, wenn kleinste Eingabeeinheit größer als Limit ist. | kein Standardwert |

```text
Beispiel: maxBytesPerTrigger = "10g", Dateien à 3 GB
# Ergebnis: ein Micro-Batch verarbeitet 12 GB (Soft-Limit überschritten, um nächste vollständige Datei einzuschließen)
```

- Beide Optionen kombiniert → Micro-Batch verarbeitet bis zur **niedrigeren** der beiden Grenzen.
- Andere Quellen (z. B. Kafka) haben eigene Rate-Limits, z. B. `maxOffsetsPerTrigger`.

## 7. Checkpoints

- Checkpoints + Write-Ahead-Logs zusammen liefern die Verarbeitungsgarantien. Checkpoint trackt Zustand + verarbeitete Datensätze. Checkpoint gelöscht/Speicherort gewechselt → Query startet von vorn.

Checkpoint-Verzeichnis enthält:

- **Offsets:** pro Micro-Batch verarbeitete Quell-Offsets → Fortsetzung ohne Re-Processing.
- **Commits:** Protokoll der committeten Micro-Batches → Exactly-once.
- **State:** bei zustandsbehafteten Queries (Aggregationen, Stream-Stream-Joins, Dedup, `transformWithState`) — Operator-Metadaten, State-Schema, gecheckpointeter State-Store-Inhalt.
- **Metadata:** eindeutige Query-ID (Konfig liegt im Offset-Log).

- Jede Query braucht einen eigenen, niemals geteilten Checkpoint.
- **Hinweis:** Zu unterscheiden von `DataFrame.checkpoint()` (nicht-streamend, Ausführungsplan-Abschneiden mit UC-Volumes).

### Aktivieren

```python
(df.writeStream
  .option("checkpointLocation", "/Volumes/catalog/schema/volume/path")
  .toTable("catalog.schema.table")
)
```

- Manche Senken (`display()` in Notebooks, `memory`-Senke) generieren ohne diese Option automatisch einen temporären Checkpoint — ohne Fehlertoleranz/Konsistenzgarantie, ggf. nicht bereinigt. Immer expliziten Speicherort angeben.

### Erlaubte vs. nicht erlaubte Änderungen zwischen Neustarts

- **Neuer Checkpoint nötig bei:** Anzahl/Typ der Eingabequellen, abonnierte Kafka-Topics/Auto-Loader-Pfade, Typ zustandsbehafteter Operationen, State-Schema, Typ der Ausgabesenke.
- **Sicher (kein neuer Checkpoint):** Filter hinzufügen/entfernen, Rate Limits ändern, Trigger-Intervalle ändern, UDF-Logik in `mapGroupsWithState` aktualisieren (Semantik kann sich ändern).

| Änderungsart | Erlaubt? |
|---|---|
| Eingabequellen Anzahl/Typ | Standardmäßig nein (Quellen werden per Position im Query-Plan identifiziert). Mit Source Evolution (unten) ja. |
| Parameter Eingabequellen: Rate Limits (z. B. `maxOffsetsPerTrigger`) | Ja |
| Parameter Eingabequellen: abonnierte Kafka-Topics/Dateien | I. A. nein (unvorhersehbare Ergebnisse) |
| Trigger-Intervall | Ja (Wechsel Batch ↔ Zeitintervall möglich) |
| Ausgabesenke Typ: File → Kafka | Ja (Kafka sieht nur neue Daten) |
| Ausgabesenke Typ: Kafka → File | Nein |
| Ausgabesenke Typ: Kafka ↔ Foreach | Ja |
| Ausgabesenke Parameter: Ausgabeverzeichnis (File) | Nein |
| Ausgabesenke Parameter: Ausgabe-Topic | Ja |
| Ausgabesenke Parameter: `ForeachWriter`-Code | Ja (Semantik hängt vom Code ab) |
| Filter hinzufügen/löschen | Ja |
| Projektion, gleiches Ausgabeschema | Ja |
| Projektion, anderes Ausgabeschema | Nur wenn Senke Schemaänderung zulässt |
| Zustandsbehaftete Operationen (hinzufügen/löschen/Schema ändern) | **Nein** — State-Schema muss über Neustarts konstant bleiben |

Details zustandsbehaftete Operationen:

- Streaming-Aggregation (`groupBy(...).agg(...)`): Gruppierungsschlüssel/Aggregate ändern → nein.
- Streaming-Dedup (`dropDuplicates(...)`): dito, nein.
- Stream-Stream-Join: Schema-/Equi-Join-Spalten-Änderung nein; Join-Typ (Inner/Outer) nicht änderbar; andere Bedingungsänderungen unscharf definiert.
- `mapGroupsWithState`/`flatMapGroupsWithState`: State-Schema/Timeout-Typ ändern → nein. Logik innerhalb der Mapping-Funktion ändern → ja (Semantik hängt von Logik ab). Für explizite State-Schema-Migration: State z. B. als Avro-kodierte Bytes speichern → Avro-Schema zwischen Neustarts änderbar.

- **Wichtig:** `dropDuplicates()`/`dropDuplicatesWithinWatermark()` können beim Neustart wegen State-Schema-Kompatibilitätsprüfung fehlschlagen, wenn der Compute-Access-Mode wechselt. Erlaubt: "dedicated" ↔ "no isolation", "standard" ↔ "serverless"; andere Kombinationen vermeiden.

### Source Evolution (Quellen umbenennen, hinzufügen, entfernen)

- Standardmäßig werden Quellen per Position im Query-Plan (0, 1, 2, …) identifiziert → jede Änderung an Anzahl/Reihenfolge bricht Checkpoint-Kompatibilität. Source Evolution erlaubt stabile, benutzerdefinierte Namen je Quelle → Umordnen/Hinzufügen/Entfernen ohne Checkpoint-Verlust. Erfordert DBR 18.2+.

```python
spark.conf.set("spark.sql.streaming.queryEvolution.enableSourceEvolution", "true")
# vor Definition der Query setzen
```

- Aktiv → **jede** Streaming-Quelle braucht `.name()` (sonst Fehler `UNNAMED_STREAMING_SOURCES_WITH_ENFORCEMENT`). Namen: nur `[a-zA-Z0-9_]+`, je Query eindeutig.

| Aktion | Verhalten über Neustart (gleicher Checkpoint) |
|---|---|
| Umordnen | Jede Quelle setzt anhand ihres Namens beim letzten committeten Offset fort. |
| Hinzufügen | Neue Quelle startet von Beginn, bestehende setzen fort. |
| Entfernen | Quelle wird dauerhaft aus dem Checkpoint entfernt; Wiederhinzufügen mit gleichem Namen nicht möglich. |

```python
orders_us = (spark.readStream
  .name("orders_us")
  .table("catalog.schema.orders_us")
)

orders_eu = (spark.readStream
  .name("orders_eu")
  .table("catalog.schema.orders_eu")
)

all_orders = orders_us.union(orders_eu)
```

- **Einschränkungen:** braucht frischen Checkpoint (nicht nachträglich auf bestehendem Checkpoint aktivierbar). Einmal aktiv → nicht mehr deaktivierbar für denselben Checkpoint. Quellennamen sind dauerhaft — Umbenennen = Quelle entfernen + unter neuem Namen von Beginn an neu hinzufügen.

**Stand:** 2026-09-14.
