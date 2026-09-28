# PySpark: DataStreamReader und DataStreamWriter

Structured-Streaming-Pendants zu `DataFrameReader`/`DataFrameWriter`: `DataStreamReader` (`spark.readStream`) lädt einen Streaming-DataFrame; `DataStreamWriter` (`df.writeStream`) schreibt ihn kontinuierlich in eine Senke. Start via `start()` bzw. `toTable()`/`table()` — liefert ein `StreamingQuery`-Objekt.

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_chk/bronze")
      .load("/Volumes/catalog/schema/landing/"))

q = (df.writeStream
       .option("checkpointLocation", "/Volumes/catalog/schema/_chk/bronze")
       .trigger(availableNow=True)
       .toTable("catalog.schema.bronze"))
```

---

## 1. `DataStreamWriter` (`df.writeStream`)

| Methode | Beschreibung |
|---|---|
| `format(source)` | Legt die Ausgabe-Datenquelle (Senke) fest. |
| `option(key, value)` / `options(**options)` | Fügt Ausgabeoption(en) hinzu (u. a. `checkpointLocation`). |
| `outputMode(outputMode)` | Legt fest, wie Daten in die Senke geschrieben werden (`append`, `complete`, `update`). |
| `partitionBy(*cols)` | Partitioniert die Ausgabe im Dateisystem nach Spalten. |
| `clusterBy(*cols)` | Clustert die Ausgabe nach Spalten (auch für hohe Kardinalität geeignet). |
| `trigger(...)` | Legt das Auslöse-Intervall fest. |
| `queryName(queryName)` | Vergibt einen eindeutigen Namen für die `StreamingQuery`. |
| `foreach(f)` | Verarbeitet die Ausgabe zeilenweise über Funktion/Writer-Objekt. |
| `foreachBatch(func)` | Verarbeitet jeden Micro-Batch als DataFrame + Batch-ID. |
| `start(path, format, outputMode, partitionBy, queryName, **options)` | Startet die Query gegen eine Quelle/Senke. |
| `toTable(tableName, format, outputMode, partitionBy, queryName, **options)` | Startet die Query mit kontinuierlicher Ausgabe in eine Tabelle. |
| `table(tableName)` | Alias für `toTable()`. |

### `outputMode(outputMode)`

| Wert | Verhalten |
|---|---|
| `append` (Standard) | Nur **neue** Zeilen werden geschrieben. |
| `complete` | Bei jedem Update wird das **gesamte** Ergebnis geschrieben (nur für Queries mit Aggregationen). |
| `update` | Nur bei diesem Update **geänderte** Zeilen werden geschrieben; ohne Aggregation entspricht das `append`. |

```python
df.writeStream.outputMode('append')

df = df.groupby().count()
q = df.writeStream.outputMode("complete").format("console").start()
# Ergebnis: bei jedem Micro-Batch wird die volle aktuelle count()-Summe neu ausgegeben
```

### `format(source)`

```python
q = df.writeStream.format("csv").option("checkpointLocation", cp).start(d)
```

### `option(key, value)` / `options(**options)`

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `checkpointLocation` | *(erforderlich)* | Pfad (z. B. Unity-Catalog-Volume) | Verzeichnis für Offsets (Fortschritt), Commits (Exactly-once), State (zustandsbehaftete Queries), Metadata (Query-ID). Muss vor Query-Start gesetzt werden. |
| `mergeSchema` | `None` | `true`/`false` | Schema Evolution beim Schreiben in eine Delta-Tabelle — gilt auch für Streaming-Appends. |
| `txnAppId` | `None` | String | Eindeutige Anwendungs-ID für idempotente Writes **in `foreachBatch`**, mit `txnVersion` (Exactly-once über mehrere Delta-Tabellen). |
| `txnVersion` | `None` | monoton steigende Ganzzahl | Transaktionsversion für idempotente `foreachBatch`-Writes. |

- Gotcha: **jede Query benötigt ein eigenes** `checkpointLocation`-Verzeichnis — niemals zwischen Queries teilen.
- Sink-spezifische Optionen (z. B. Kafka: `kafka.bootstrap.servers`, `topic`) richten sich nach dem jeweiligen Format/Connector.

```python
(df.writeStream
  .option("checkpointLocation", "/Volumes/catalog/schema/volume/path")
  .toTable("catalog.schema.table"))

df.writeStream.options(checkpointLocation="/Volumes/catalog/schema/volume/path", mergeSchema="true")
```

### `partitionBy(*cols)` / `clusterBy(*cols)`

```python
# partitionBy — Hive-Partitionierungsschema
q = df.writeStream.partitionBy("timestamp").format("parquet").option("checkpointLocation", cp).start(d)

# clusterBy — ähnliche Werte landen in derselben Datei (Data Skipping); anders als partitionBy
# auch für Spalten mit HOHER Kardinalität geeignet
q = df.writeStream.clusterBy("timestamp").format("parquet").option("checkpointLocation", cp).start(d)
```

### `trigger(*, processingTime=None, once=None, continuous=None, availableNow=None, realTime=None)`

- Ohne `trigger()`: Query läuft so schnell wie möglich (≙ `processingTime='0 seconds'`).
- Gotcha: es darf immer nur **ein** Parameter gesetzt werden.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `processingTime` | `str` | Intervall-String (z. B. `'5 seconds'`) — periodische Micro-Batch-Query. |
| `once` | `bool` | `True` verarbeitet genau eine Batch, dann Terminierung. **Veraltet** — stattdessen `availableNow=True`. |
| `continuous` | `str` | Intervall-String — Continuous-Query mit diesem Checkpoint-Intervall. **Nicht auf Databricks Serverless Compute unterstützt.** |
| `availableNow` | `bool` | `True` verarbeitet alle aktuell verfügbaren Daten in mehreren Batches, dann Terminierung. |
| `realTime` | `str` | Batch-Dauer-String — Query im Real-Time-Modus mit Batches dieser Dauer. |

```python
df.writeStream.trigger(processingTime='5 seconds')
df.writeStream.trigger(continuous='5 seconds')       # nicht auf Serverless
df.writeStream.trigger(availableNow=True)
df.writeStream.trigger(realTime='5 seconds')
```

### `queryName(queryName)`

- Muss unter allen aktiven Queries derselben `SparkSession` eindeutig sein.

```python
q = df.writeStream.queryName("streaming_query").format("console").start()
q.name  # Ergebnis: 'streaming_query'
```

### `foreach(f)`

- Funktion, die eine `Row` entgegennimmt, **oder** Objekt mit `process(row)` und optional `open(partition_id, epoch_id)` / `close(error)`.
- Gotcha: Objekt muss serialisierbar sein; Initialisierung (z. B. Verbindung öffnen) gehört in `open()`, **nicht** in den Konstruktor.

```python
def print_row(row):
    print(row)
q = df.writeStream.foreach(print_row).start()

class RowPrinter:
    def open(self, partition_id, epoch_id):
        print("Opened %d, %d" % (partition_id, epoch_id))
        return True
    def process(self, row):
        print(row)
    def close(self, error):
        print("Closed with error: %s" % str(error))
q = df.writeStream.foreach(RowPrinter()).start()
```

### `foreachBatch(func)`

- Funktion wird pro Micro-Batch mit Ausgabezeilen als DataFrame + Batch-ID (`int`) aufgerufen.
- Nur im **Micro-Batch-Modus** unterstützt (Trigger ≠ `continuous`). Über Batch-ID: transaktionale/deduplizierte Writes in externe Systeme (z. B. `MERGE`/Upsert).
- Gotcha: im Spark-Connect-Modus hat die Funktion **keinen** Zugriff auf außerhalb definierte Variablen.
- Gotcha: der `MERGE` in `foreachBatch` muss **idempotent** sein, da eine Batch bei Neustart wiederholt werden kann.

```python
def func(batch_df, batch_id):
    batch_df.collect()
q = df.writeStream.foreachBatch(func).start()
```

```python
# Anwendungsfall: Upsert per MERGE
from delta.tables import DeltaTable

def upsert_to_delta(micro_batch_df, batch_id):
    (DeltaTable.forName(spark, "catalog.schema.target").alias("t")
        .merge(micro_batch_df.alias("s"), "t.id = s.id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute())

(spark.readStream.format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "/Volumes/catalog/schema/_chk/target")
    .load("/Volumes/catalog/schema/landing/")
    .writeStream
    .foreachBatch(upsert_to_delta)
    .option("checkpointLocation", "/Volumes/catalog/schema/_chk/target")
    .trigger(availableNow=True)
    .start())
```

### `start(path=None, format=None, outputMode=None, partitionBy=None, queryName=None, **options)`

Rückgabe: `StreamingQuery`.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `path` | `str`, optional | Pfad in einem Hadoop-kompatiblen Dateisystem. |
| `format` | `str`, optional | Zielformat. |
| `outputMode` | `str`, optional | `append`, `complete` oder `update`. |
| `partitionBy` | `str`/`list`, optional | Partitionierungsspalten. |
| `queryName` | `str`, optional | Eindeutiger Query-Name. |
| `**options` | — | Weitere Optionen; `checkpointLocation` für die meisten Streams empfohlen. |

```python
q = df.writeStream.format('memory').queryName('this_query').start()
q.isActive  # Ergebnis: True
q.stop()
```

### `toTable(tableName, format=None, outputMode=None, partitionBy=None, queryName=None, **options)` / `table(tableName)`

- `toTable`: Parameter analog zu `start()`, plus `tableName: str`. Bei **v1-Tabellen** wird `partitionBy` immer berücksichtigt; bei **v2-Tabellen** nur, wenn die Tabelle noch nicht existiert.
- `table(tableName)`: Alias für `toTable()`, nimmt nur `tableName: str` entgegen.
- Beide: Rückgabe `StreamingQuery`.

```python
q = (spark.readStream.format("rate").option("rowsPerSecond", 10).load()
    .writeStream.toTable(
        "my_table2", queryName='that_query', outputMode="append",
        format='parquet', checkpointLocation=d))

q = (df.writeStream
       .option("checkpointLocation", "/Volumes/catalog/schema/_chk/rate")
       .table("catalog.schema.rate_events"))
```

---

## 2. `DataStreamReader` (`spark.readStream`)

Lädt einen Streaming-DataFrame aus externen Speichersystemen (Dateisysteme, Key-Value-Stores).

| Methode | Beschreibung |
|---|---|
| `format(source)` | Legt das Format der Eingabe-Datenquelle fest. |
| `schema(schema)` | Legt das Schema fest (überspringt Schema-Inferenz). |
| `option(key, value)` / `options(**options)` | Fügt Eingabeoption(en) hinzu. |
| `load(path, format, schema, **options)` | Lädt einen Datenstrom und gibt ihn als DataFrame zurück. |
| `csv(path, schema, **options)` | Lädt einen CSV-Datei-Stream. |
| `json(path, schema, **options)` | Lädt einen JSON-Datei-Stream. |
| `parquet(path, **options)` | Lädt einen Parquet-Datei-Stream. |
| `orc(path, **options)` | Lädt einen ORC-Datei-Stream. |
| `text(path, **options)` | Lädt einen Text-Datei-Stream (`value`-Spalte). |
| `xml(path, schema, **options)` | Lädt einen XML-Datei-Stream. |
| `excel(path, **options)` | Lädt einen Excel-Datei-Stream. |
| `table(tableName)` | Definiert einen Streaming-DataFrame auf einer Tabelle. |
| `name(source_name)` | Vergibt einen Namen für die Streaming-Quelle (Checkpoint-Evolution). |
| `changes(tableName)` | Gibt Zeilen-Änderungen (CDC) einer Tabelle als Streaming-DataFrame zurück. |

### `format(source)`

```python
q = spark.readStream.format("text").load(d).writeStream.format("console").start()
```

### `schema(schema)`

- Für dateibasierte Streaming-Quellen **in der Regel erforderlich** (Ausnahme: Auto Loader mit `cloudFiles.schemaLocation` inferiert selbst).

| Parameter | Typ | Beschreibung |
|---|---|---|
| `schema` | `StructType` oder `str` | `StructType`-Objekt oder DDL-String, z. B. `col0 INT, col1 DOUBLE`. |

```python
spark.readStream.schema("col0 INT, col1 DOUBLE")
```

### `option(key, value)` / `options(**options)`

**Common-Optionen** für dateibasierte Streaming-Quellen (`spark.readStream.format("<file-format>")`), unabhängig von Auto Loader:

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `cleanSource` | `off` | enum (`off`, `archive`, `delete`) | Wie Quelldateien nach Verarbeitung behandelt werden. |
| `fileNameOnly` | `false` | boolean | Bereits verarbeitete Dateien nur am Dateinamen (statt vollständigem Pfad) erkennen. |
| `latestFirst` | `false` | boolean | Zuletzt geänderte Dateien zuerst in jedem Micro-Batch verarbeiten. |
| `maxBytesPerTrigger` | `None` | Ganzzahl | Soft-Maximum für die pro Micro-Batch verarbeitete Datenmenge. |
| `maxCachedFiles` | `10000` | Ganzzahl | Max. Anzahl unverarbeiteter Dateien, für folgende Micro-Batches gecacht. |
| `maxFileAge` | `7d` | Dauer | Maximales Alter von Dateien, die berücksichtigt werden. |
| `maxFilesPerTrigger` | `1000` (Delta/Auto Loader); kein Maximum (andere Quellen) | Ganzzahl | Obergrenze für neue Dateien je Micro-Batch. |
| `sourceArchiveDir` | `None` | Pfad | Archivverzeichnis, wenn `cleanSource=archive`. |

- Gotcha: für **Auto-Loader** (`format("cloudFiles")`) gelten stattdessen die `cloudFiles.*`-Optionen (z. B. `cloudFiles.format`, `cloudFiles.schemaLocation`, `cloudFiles.schemaEvolutionMode`) — das dateibasierte `cleanSource`/`sourceArchiveDir` ist **nicht** dasselbe wie `cloudFiles.cleanSource`. Für Kafka gelten eigene sink-spezifische Optionen.

```python
spark.readStream.option("x", 1)
spark.readStream.options(rowsPerSecond=10, numPartitions=10)
```

### `load(path=None, format=None, schema=None, **options)`

Rückgabe: `DataFrame`.

| Parameter | Typ | Beschreibung |
|---|---|---|
| `path` | `str`, optional | Pfad für dateisystembasierte Quellen. |
| `format` | `str`, optional | Quellformat. Standard: `'parquet'`. |
| `schema` | `StructType`/`str`, optional | Eingabeschema. |
| `**options` | | Weitere String-Optionen. |

```python
q = spark.readStream.schema("age INT, name STRING").format("json").load(d) \
    .writeStream.format("console").start()
```

### Format-Shortcuts

```python
# csv(path, schema=None, **options)
# wichtige **options: header, inferSchema, sep, encoding, multiLine, mode, rescuedDataColumn
# Gotcha: inferSchema=True liest die Eingabe einmal komplett durch -> deaktivieren oder schema explizit angeben
q = spark.readStream.schema("age INT, name STRING").csv(d).writeStream.format("console").start()

# json(path, schema=None, **options)
# JSON Lines (newline-delimited) ist Standard; für 1 Datensatz/Datei: multiLine=true
q = spark.readStream.schema("age INT, name STRING").json(d).writeStream.format("console").start()

# parquet(path, **options) — z. B. mergeSchema, datetimeRebaseMode
q = spark.readStream.schema("id LONG").parquet(d).writeStream.format("console").start()

# orc(path, **options) — z. B. mergeSchema
q = spark.readStream.schema("id LONG").orc(d).writeStream.format("console").start()

# text(path, **options) — Ergebnisschema: String-Spalte "value" + evtl. Partitionierungsspalten
# UTF-8 erforderlich; Standard: 1 Zeile = 1 DataFrame-Zeile. Weitere Optionen: wholeText, lineSep
q = spark.readStream.text(d).writeStream.format("console").start()

# xml(path, schema=None, **options) — wichtige Option: rowTag (Pflicht)
q = spark.readStream.schema("age INT, name STRING").xml(d, rowTag="person") \
    .writeStream.format("console").start()

# excel(path, **options) — z. B. dataAddress, header
q = spark.readStream.schema("id LONG").excel(d).writeStream.format("console").start()
```

### `table(tableName)`

- Zugrunde liegende Datenquelle (z. B. Delta) muss Streaming-Modus unterstützen. Rückgabe: `DataFrame`.

```python
q1 = spark.readStream.format("rate").load().writeStream.toTable("my_table", checkpointLocation=d)
q2 = spark.readStream.table("my_table").writeStream.format("console").start()
```

### `name(source_name)`

- Namen für **Checkpoint-Evolution**: benannte Quellen können umgeordnet/ergänzt werden, ohne Checkpoint-Kompatibilität zu brechen. Ist Quellen-Evolution aktiviert, **müssen alle Quellen benannt werden**.
- Voraussetzung: `spark.sql.streaming.queryEvolution.enableSourceEvolution` muss aktiviert sein (ab DBR 18.2).

| Parameter | Typ | Beschreibung |
|---|---|---|
| `source_name` | `str` | Nur ASCII-Buchstaben (a–z, A–Z), Ziffern (0–9), Unterstriche (`_`). |

```python
df1 = spark.readStream.format("rate").name("source1").load()
df2 = spark.readStream.format("rate").name("source2").load()
query = df1.union(df2).writeStream.format("console").start()

# Gültig: "mySource", "my_source_123"
# Ungültig (löst AnalysisException aus): "my-source"
```

### `changes(tableName)`

- CDC (Change Data Capture) als Streaming-DataFrame. Funktioniert mit Data-Source-V2-Tabellen, deren Katalog `TableCatalog.loadChangelog()` implementiert.
- Über `option()`: Startversion/-zeitstempel und Verarbeitungsoptionen (`startingVersion`, `startingTimestamp`).

| Parameter | Typ | Beschreibung |
|---|---|---|
| `tableName` | `str` | Name der Quelltabelle. |

```python
spark.readStream.option("startingVersion", "10").changes("my_table")
# Ergebnis: Streaming-DataFrame mit Zeilen-Änderungen ab Tabellenversion 10
```

**Stand:** 2026-09-14.
