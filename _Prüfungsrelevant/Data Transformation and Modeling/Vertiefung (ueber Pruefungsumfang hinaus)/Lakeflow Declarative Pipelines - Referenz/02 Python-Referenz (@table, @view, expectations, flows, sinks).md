# Python-Referenz für Lakeflow Declarative Pipelines (`pyspark.pipelines` / `dp`)

Alle Python-APIs von Lakeflow Declarative Pipelines werden über `from pyspark import pipelines as dp` importiert. Dieses Dokument fasst die Referenz für Dataset-Dekoratoren, Expectations, Flow-Dekoratoren, Sinks und die funktionalen (nicht-dekorator-basierten) Erzeugungsfunktionen zusammen.

## 1. `@dp.table`

Definiert eine **Streaming Table** in einer Pipeline — funktioniert mit Abfragen, die Streaming-Lesevorgänge ausführen.

```python
from pyspark import pipelines as dp

@dp.table(
  name="<name>",
  comment="<comment>",
  spark_conf={"<key>" : "<value>", "<key>" : "<value>"},
  table_properties={"<key>" : "<value>", "<key>" : "<value>"},
  path="<storage-location-path>",
  partition_cols=["<partition-column>", "<partition-column>"],
  cluster_by_auto = False,
  cluster_by = ["<clustering-column>", "<clustering-column>"],
  schema="schema-definition",
  row_filter = "row-filter-clause",
  private = False,
  replace_using = ["<key-column>", "<key-column>"],
  sequence_by = "<sequence-column>")
@dp.expect(...)
def <function-name>():
    return (<query>)
```

**Parameter:**

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| *(Funktion selbst)* | `function` | — | Erforderlich. Muss eine Apache-Spark-Streaming-DataFrame zurückgeben. |
| `name` | `str` | Funktionsname | Tabellenbezeichner. |
| `comment` | `str` | — | Dokumentationstext. |
| `spark_conf` | `dict` | — | Spark-Konfiguration für die Abfrage. |
| `table_properties` | `dict` | — | Delta-Lake-Tabelleneigenschaften. |
| `path` | `str` | Verwaltete Speicherposition | Speicherposition. |
| `partition_cols` | `list` | — | Spalten zur Partitionierung. |
| `cluster_by_auto` | `bool` | — | Automatisches Liquid Clustering. |
| `cluster_by` | `list` | — | Explizite Clustering-Spalten. |
| `schema` | `str` oder `StructType` | — | SQL-DDL oder Python-Objekt. |
| `row_filter` | `str` | — | Row-Level-Zugriffsfilter. |
| `private` | `bool` | — | Verbirgt die Tabelle vor dem Metastore; nur pipeline-intern zugänglich. |
| `replace_using` | `list` | — | Schlüsselspalten für REPLACE-USING-Flows (erfordert `sequence_by`). |
| `sequence_by` | `str` oder `Column` | — | Ordnungsspalte für Updates bei REPLACE-USING-Flows. |

**Hinweis:** `@dp.table` listet zusätzlich zu den Standard-Tabellenparametern auch `replace_using` und `sequence_by` — dieselben Parameter wie bei `@dp.replace_flow` (Abschnitt 7). REPLACE-USING-Semantik lässt sich also direkt über `@dp.table(replace_using=..., sequence_by=...)` aktivieren, ohne separaten `@dp.replace_flow`-Dekorator.

## 2. `@dp.temporary_view`

Definiert Sichten, die anschließend unter ihrem Namen in anderen Abfragen (auch Materialized Views und Streaming Tables) referenziert werden können. Ergebnisse werden bei Abfrage berechnet.

**Hinweis zur Benennung:** Das ältere `dlt`-Modul verwendete den Dekorator `@view` zur Definition einer temporären Sicht. Databricks empfiehlt das `pyspark.pipelines`-Modul (`dp`) mit dem Dekorator `@temporary_view`. Ein Dekorator namens `dp.view` ist in der aktuellen Referenz nicht als offizieller Name dokumentiert.

```python
from pyspark import pipelines as dp

@dp.temporary_view(
    name="<name>",
    comment="<comment>"
)
@dp.expect(...)
def <function-name>():
    return (<query>)
```

**Parameter:** `name` (Sichtname, Default: Funktionsname, muss innerhalb Katalog/Schema eindeutig sein), `comment` (Beschreibung). Rückgabetyp: je nach Abfrage eine Batch- oder Streaming-DataFrame.

## 3. `@dp.materialized_view`

Definiert eine Materialized View über eine Funktion, die eine **Batch**-DataFrame zurückgibt (typischerweise via `spark.read`, im Unterschied zu `@dp.table` mit `spark.readStream`).

```python
@dp.materialized_view(
    name="<name>",
    comment="<comment>",
    spark_conf = {"<key>" : "<value>", "<key>" : "<value>"},
    table_properties = {"<key>" : "<value>", "<key>" : "<value>"},
    path = "<storage-location-path>",
    partition_cols = ["<partition-column>", "<partition-column>"],
    cluster_by_auto = False,
    cluster_by = ["<clustering-column>", "<clustering-column>"],
    schema = "schema-definition",
    refresh_policy = None,
    row_filter = "row-filter-clause",
    private = False)
@dp.expect(...)
def <function-name>():
    return (<query>)
```

**Parameter:** wie bei `@dp.table`, zusätzlich `refresh_policy` (`str`, Default `"auto"`; Beta-Feature: `auto`, `incremental`, `incremental_strict`, `full`). Kein `replace_using`/`sequence_by` (nur bei Streaming Tables relevant).

```python
from pyspark import pipelines as dp

@dp.materialized_view(
    comment="Raw data on sales",
    schema="""
        customer_id STRING,
        customer_name STRING,
        order_number LONG
    """,
    cluster_by = ["customer_id"])
def sales():
    return ("...")
```

## 4. Expectations-Dekoratoren

Erzwingen Datenqualitäts-Constraints auf Materialized Views, Streaming Tables oder temporären Views. Das `dp`-Modul stellt sechs Dekoratoren bereit, unterschieden nach **Aktion bei Verstoß** (einbeziehen / verwerfen / Abbruch) und **Anzahl der Constraints** (einzeln / mehrere):

| Dekorator | Aktion bei Verstoß | Anzahl Constraints |
|---|---|---|
| `@dp.expect()` | Zeile einbeziehen | Einzeln |
| `@dp.expect_or_drop()` | Zeile verwerfen | Einzeln |
| `@dp.expect_or_fail()` | Abbruch | Einzeln |
| `@dp.expect_all()` | Zeile einbeziehen | Mehrere |
| `@dp.expect_all_or_drop()` | Zeile verwerfen | Mehrere |
| `@dp.expect_all_or_fail()` | Abbruch | Mehrere |

Expectation-Dekoratoren stehen nach `@dp.table()`/`@dp.materialized_view()`/`@dp.temporary_view()` und vor der Definitionsfunktion:

```python
from pyspark import pipelines as dp

@dp.table()
@dp.expect(description, constraint)
@dp.expect_or_drop(description, constraint)
@dp.expect_or_fail(description, constraint)
@dp.expect_all({description: constraint, ...})
@dp.expect_all_or_drop({description: constraint, ...})
@dp.expect_all_or_fail({description: constraint, ...})
def <function-name>():
    return (<query>)
```

```python
@dp.table()
@dp.expect_or_drop("valid_date", "order_datetime IS NOT NULL AND length(order_datetime) > 0")
def orders_valid():
    return (spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/databricks-datasets/retail-org/sales_orders")
    )
```

**Parameter:** `description` (`str`, erforderlich, pro Dataset eindeutig), `constraint` (`str`, erforderlich, SQL-Bedingung — löst bei `false` aus). Bei `expect_all`-Varianten werden `description`/`constraint`-Paare als `dict` übergeben.

**Verhalten von `@dp.expect`:** Die Zeile wird unabhängig vom Constraint-Ergebnis in das Ziel-Dataset einbezogen; die Anzahl gültiger und ungültiger Datensätze wird zusammen mit anderen Dataset-Metriken protokolliert. Mehrere Expectation-Dekoratoren lassen sich auf ein Dataset anwenden.

## 5. `create_table()` (funktional, ohne Dekorator)

Nicht-dekorator-basierte Variante zum Anlegen einer Tabelle — im Unterschied zu `@dp.table()` wird keine Funktion dekoriert; die Tabelle wird direkt erzeugt und typischerweise anschließend über `@dp.append_flow(target=...)` befüllt.

```python
from pyspark import pipelines as dp

dp.create_table(
  name="<table-name>",
  comment="<comment>",
  spark_conf={"<key>": "<value>"},
  table_properties={"<key>": "<value>"},
  partition_cols=["<partition-column>"],
  path="<storage-location-path>",
  schema="schema-definition",
  expect_all={"<key>": "<value>"},
  expect_all_or_drop={"<key>": "<value>"},
  expect_all_or_fail={"<key>": "<value>"},
  cluster_by=["<clustering-column>"],
  cluster_by_auto=False,
  row_filter="row-filter-clause",
  private=False
)
```

**Parameter:** `name` (erforderlich), `comment`, `spark_conf`, `table_properties`, `partition_cols`, `path`, `schema`, `expect_all`/`expect_all_or_drop`/`expect_all_or_fail` (Datenqualitäts-Constraints als Dict), `cluster_by`, `cluster_by_auto` (Default `False`), `row_filter` (Public Preview), `private` (Default `False`).

```python
from pyspark import pipelines as dp

dp.create_table("combined")

@dp.append_flow(target="combined")
def from_a():
    return spark.readStream.table("source_a")

@dp.append_flow(target="combined")
def from_b():
    return spark.readStream.table("source_b")
```

## 6. `create_streaming_table()`

Legt eine Zieltabelle für Streaming-Operationen an — typischerweise anschließend als `target` für `create_auto_cdc_flow()`, `create_auto_cdc_from_snapshot_flow()`, `append_flow` oder `replace_flow` verwendet.

```python
from pyspark import pipelines as dp

dp.create_streaming_table(
  name = "<table-name>",
  comment = "<comment>",
  spark_conf={"<key>" : "<value", "<key" : "<value>"},
  table_properties={"<key>" : "<value>", "<key>" : "<value>"},
  path="<storage-location-path>",
  partition_cols=["<partition-column>", "<partition-column>"],
  cluster_by_auto = False,
  cluster_by = ["<clustering-column>", "<clustering-column>"],
  schema="schema-definition",
  expect_all = {"<key>" : "<value", "<key" : "<value>"},
  expect_all_or_drop = {"<key>" : "<value", "<key" : "<value>"},
  expect_all_or_fail = {"<key>" : "<value", "<key" : "<value>"},
  row_filter = "row-filter-clause")
```

**Parameter:** `name` (erforderlich), `comment`, `spark_conf`, `table_properties`, `path` (Default: verwaltete Speicherposition des Schemas), `partition_cols`, `cluster_by_auto`, `cluster_by`, `schema`, `expect_all`/`expect_all_or_drop`/`expect_all_or_fail`, `row_filter` (Public Preview).

```python
from pyspark import pipelines as dp

dp.create_streaming_table("target")
dp.create_auto_cdc_from_snapshot_flow(
  target = "target",
  source = "source",
  keys = ["log_id"],
  stored_as_scd_type = 1)
```

## 7. `@dp.append_flow`

Erzeugt Append-Flows oder Backfills für Pipeline-Tabellen (oder Sinks). Die dekorierte Funktion muss eine Streaming-DataFrame zurückgeben (außer bei `once = True`).

```python
@dp.append_flow(
  target = "<target-table-name>",
  name = "<flow-name>",
  once = False,
  spark_conf = {"<key>" : "<value>", "<key>" : "<value>"},
  comment = "<comment>",
  import_checkpoint = "<checkpoint-path>"
)
def <function-name>():
  return (<streaming-query>)
```

**Parameter:** `target` (erforderlich), `name` (Default: Funktionsname), `once` (`bool`, Default `False` — bei `True`: Rückgabewert muss Batch-DataFrame sein, Flow läuft standardmäßig nur einmal, außer bei vollständigem Refresh), `comment`, `spark_conf`, `import_checkpoint` (`str`, Beta — Pfad eines bestehenden Structured-Streaming-Checkpoints; wird beim ersten Update einmalig in den Pipeline-verwalteten Speicher geklont, Flow setzt danach am letzten committeten Offset fort inkl. State; **nur bei `append_flow`** unterstützt, nicht bei bereits existierender Zieltabelle — nur bei per `create_table()` neu angelegter Tabelle oder Sink; Full Refresh importiert nicht erneut, sondern startet mit neuem leeren Checkpoint).

```python
from pyspark import pipelines as dp
dp.create_sink("my_sink", "delta", {"path": "/tmp/delta_sink"})

@dp.append_flow(name = "flow", target = "my_sink")
def flowFunc():
  return <streaming-query>

@dp.append_flow(name = "backfill", target = "my_sink", once = True)
def backfillFlowFunc():
    return (
      spark.read
      .format("json")
      .load("/path/to/backfill/")
    )
```

```python
dp.create_sink(
  "my_kafka_sink",
  "kafka",
  {
    "kafka.bootstrap.servers": "host:port",
    "topic": "my_topic"
  })

@dp.append_flow(name = "flow", target = "my_kafka_sink")
def myFlow():
  return read_stream("xxx").select(F.to_json(F.struct("*")).alias("value"))
```

## 8. `@dp.replace_flow`

Ersetzt gezielt Zeilen einer bestehenden Streaming Table anhand von Schlüsselspalten (REPLACE USING), statt reine Appends vorzunehmen. Die dekorierte Funktion muss eine Streaming-DataFrame zurückgeben.

```python
@dp.replace_flow(
  target = "<target-table-name>",
  replace_using = ["<key-column>", "<key-column>"],
  sequence_by = "<sequence-column>",
  name = "<flow-name>",
  comment = "<comment>",
  spark_conf = {"<key>" : "<value>", "<key>" : "<value>"}
)
def <function-name>():
  return (<streaming-query>)
```

**Parameter:** `target` (erforderlich), `replace_using` (erforderlich, mindestens eine Schlüsselspalte), `sequence_by` (erforderlich, pro Schlüssel gewinnt der höchste Sequenzwert), `name` (Default: Funktionsname), `comment`, `spark_conf`.

```python
from pyspark import pipelines as dp

dp.create_streaming_table("orders_current")
@dp.replace_flow(
  target = "orders_current",
  replace_using = ["order_id"],
  sequence_by = "updated_at")
def orders_flow():
  return spark.readStream.table("order_updates")
```

```python
dp.create_streaming_table("accounts_current")
@dp.replace_flow(
  target = "accounts_current",
  replace_using = ["region", "account_id"],
  sequence_by = "updated_at")
def accounts_flow():
  return spark.readStream.table("account_updates")
```

## 9. `@dp.update_flow`

Definiert einen Flow, der fortlaufend aktualisierte Ergebnisse (z. B. laufende Aggregationen ohne Watermark) in einen **Sink** schreibt — im Unterschied zu `@dp.append_flow`, das nur anhängt.

```python
@dp.update_flow(
    target = "<sink-name>",
    name = "<flow-name>",
    spark_conf = {"<key>" : "<value>", "<key>" : "<value>"},
    comment = "<comment>"
)
def <function-name>():
    return (<streaming-query>)
```

**Parameter:** `target` (erforderlich, Name des Sinks), `name` (Default: Funktionsname), `comment`, `spark_conf`. Rückgabetyp: Streaming-DataFrame, konfiguriert zum Schreiben in den Sink.

**Wichtige Einschränkung:** Delta-Tabellen-Sinks werden als Ziel von Update-Flows **nicht unterstützt** — im Unterschied zu Append-Flows, die sowohl Kafka- als auch Delta-Sinks akzeptieren.

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col

dp.create_sink("event_counts_sink", "kafka", {
    "kafka.bootstrap.servers": broker_address,
    "topic": output_topic,
})

@dp.update_flow(
    name="event_counts_flow",
    target="event_counts_sink",
)
def event_counts():
    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", broker_address)
            .option("subscribe", input_topic)
            .load()
            .selectExpr("CAST(key AS STRING) AS event_type")
            .groupBy(col("event_type"))
            .count()
    )
```

Real-Time-Modus über `spark_conf`:

```python
@dp.update_flow(
    name="my_rtm_flow",
    target="my_kafka_sink",
    spark_conf={
        "pipelines.trigger": "RealTime",
        "pipelines.trigger.interval": "5 minutes",
    }
)
def my_real_time_flow():
    return (
        spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", broker_address)
            .option("subscribe", input_topic)
            .load()
    )
```

## 10. `create_auto_cdc_flow()` (vormals `apply_changes()`)

Erzeugt einen Flow, der Quelldaten aus Change-Data-Feeds (CDF) mittels CDC-Funktionalität verarbeitet. `apply_changes()` ist die ältere Bezeichnung derselben Funktion mit identischer Signatur.

```python
from pyspark import pipelines as dp

dp.create_auto_cdc_flow(
  target = "<target-table>",
  source = "<data-source>",
  keys = ["key1", "key2", "keyN"],
  sequence_by = "<sequence-column>",
  system_sequence_by = None,
  ignore_null_updates = False,
  ignore_null_updates_column_list = None,
  ignore_null_updates_except_column_list = None,
  columns_to_update = None,
  apply_as_deletes = None,
  apply_as_truncates = None,
  column_list = None,
  except_column_list = None,
  stored_as_scd_type = "1",
  track_history_column_list = None,
  track_history_except_column_list = None,
  name = None,
  once = False
)
```

**Parameter:**

| Parameter | Typ | Default | Beschreibung |
|---|---|---|---|
| `target` | `str` | — | Erforderlich. Zieltabelle, üblicherweise vorab über `create_streaming_table()` angelegt. |
| `source` | `str` | — | Erforderlich. CDC-Datenquelle. |
| `keys` | `list` | — | Erforderlich. Spalte(n), die eine Zeile eindeutig identifizieren (Strings oder `col()`). |
| `sequence_by` | `str`, `col()` oder `struct()` | — | Erforderlich. Logische Reihenfolge der CDC-Ereignisse; sortierbarer Typ. |
| `system_sequence_by` | `str` oder `col()` | `None` | Systemzeitpunkt-Spalte; zusammen mit `stored_as_scd_type="bitemporal"`. |
| `ignore_null_updates` | `bool` | `False` | Steuert Behandlung von Nullwerten in CDC-Updates. |
| `ignore_null_updates_column_list` | `list` | `None` | Spalten, für die Nullwerte ignoriert werden. |
| `ignore_null_updates_except_column_list` | `list` | `None` | Spalten, die explizite Nullwerte anwenden — alle übrigen ignorieren Nullwerte. |
| `columns_to_update` | `str` oder `col()` | `None` | Quellspalte mit der je Change-Datensatz zu aktualisierenden Spaltenmenge (Array von Strings). |
| `apply_as_deletes` | `str` oder `expr()` | `None` | Wann ein CDC-Ereignis als DELETE behandelt wird. |
| `apply_as_truncates` | `str` oder `expr()` | `None` | Wann ein CDC-Ereignis als vollständiges TRUNCATE behandelt wird. |
| `column_list` | `list` | `None` | Teilmenge der zu übernehmenden Spalten (Einschlussliste). |
| `except_column_list` | `list` | `None` | Auszuschließende Spalten (Ausschlussliste). |
| `stored_as_scd_type` | `str` oder `int` | `"1"` | SCD Type 1, Type 2 oder bitemporal. |
| `track_history_column_list` | `list` | `None` | Spalten mit Historiennachverfolgung (Einschlussliste). |
| `track_history_except_column_list` | `list` | `None` | Von Historiennachverfolgung ausgeschlossene Spalten. |
| `name` | `str` | Wert von `target` | Flow-Name. |
| `once` | `bool` | `False` | Einmaliger Flow (Backfill). |

Jeweils nur einer der beiden Parameter eines Paares (`column_list`/`except_column_list`, `track_history_column_list`/`track_history_except_column_list`) wird gleichzeitig angegeben. Rückgabewert: Streaming-DataFrame (Batch-DataFrame bei `once=True`).

## 11. `create_auto_cdc_from_snapshot_flow()` (vormals `apply_changes_from_snapshot()`)

Python-exklusive Funktion. Erkennt Änderungen zwischen aufeinanderfolgenden Snapshots derselben Quelle automatisch (Inserts/Updates/Deletes) und wendet sie auf eine Zieltabelle an.

```python
from pyspark import pipelines as dp

dp.create_auto_cdc_from_snapshot_flow(
  target = "<target-table>",
  source = Any,
  keys = ["key1", "key2", "keyN"],
  stored_as_scd_type = "1",
  track_history_column_list = None,
  track_history_except_column_list = None)
```

**Parameter:** `target` (erforderlich, vorab per `create_streaming_table()` angelegt), `source` (erforderlich — Tabellen-/View-Name **oder** Python-Lambda-Funktion, die eine Snapshot-DataFrame und eine Version zurückgibt), `keys` (erforderlich), `stored_as_scd_type` (`"1"` Default oder `"2"`), `track_history_column_list`/`track_history_except_column_list`.

**Die Snapshot-Lambda-Funktion** hat die Signatur `lambda Any => Optional[(DataFrame, Any)]`. Die Pipeline-Laufzeit ruft sie wiederholt auf und lädt Snapshots samt Version, bis `None` zurückgegeben wird:

```python
def next_snapshot_and_version(latest_snapshot_version: Optional[int]) -> Tuple[DataFrame, Optional[int]]:
  if latest_snapshot_version is None:
    return (spark.read.load("filename.csv"), 1)
  else:
    return None

create_auto_cdc_from_snapshot_flow(
  # ...
  source = next_snapshot_and_version,
  # ...)
```

Codebeispiel (Tabellen-/View-Name als `source`):

```python
from pyspark import pipelines as dp

@dp.temporary_view(name="source")
def source():
  return spark.read.format("csv").option("header", True).load("/Volumes/main/landing/growing_log.csv")

dp.create_streaming_table("target")
dp.create_auto_cdc_from_snapshot_flow(
  target = "target",
  source = "source",
  keys = ["log_id"],
  stored_as_scd_type = 1)
```

## 12. `create_sink()`

Schreibt Daten aus einer deklarativen Pipeline in einen Event-Streaming-Dienst (Apache Kafka, Azure Event Hubs) oder in eine Delta-Tabelle. Python-exklusiv.

```python
from pyspark import pipelines as dp
dp.create_sink(name=<sink_name>, format=<format>, options=<options>)
```

**Parameter:** `name` (`str`, erforderlich, eindeutig innerhalb der Pipeline über alle Quelldateien), `format` (`str`, erforderlich, `"kafka"` oder `"delta"`), `options` (`dict`, optional — Schlüssel-Wert-Paare, unterstützt alle Databricks-Runtime-Optionen für Kafka-/Delta-Sinks).

**Einschränkungen:** Ein Sink funktioniert ausschließlich mit Append- und Update-Flows. Delta-Sinks akzeptieren voll qualifizierte Tabellennamen (`<catalog>.<schema>.<table>` für Unity Catalog, `<schema>.<table>` für den Hive-Metastore).

```python
# Kafka-Sink
dp.create_sink(
  "my_kafka_sink",
  "kafka",
  {
    "kafka.bootstrap.servers": "host:port",
    "topic": "my_topic"
  })

# Externe Delta-Tabelle als Sink (über Pfad)
dp.create_sink(
  "my_delta_sink",
  "delta",
  { "path": "/path/to/my/delta/table" })

# Delta-Tabelle als Sink (über Tabellennamen)
dp.create_sink(
  "my_delta_sink",
  "delta",
  { "tableName": "my_catalog.my_schema.my_table" })
```

## 13. `@dp.foreach_batch_sink`

Definiert einen ForEachBatch-Sink, der einen Stream als Serie von Micro-Batches verarbeitet, die in Python mit benutzerdefinierter Logik behandelt werden. Python-exklusiv. Als `target` eines Append-Flows referenziert.

```python
from pyspark import pipelines as dp

@dp.foreach_batch_sink(name="<name>")
def batch_handler(df, batch_id):
    # benutzerdefinierte Logik
```

**Parameter:** `name` (`str`, optional, Default: UDF-Name — eindeutiger Sink-Bezeichner innerhalb der Pipeline). Die dekorierte UDF-Funktion erhält `df` (Spark-DataFrame des aktuellen Micro-Batches) und `batch_id` (`int`, von Spark bei jedem Trigger-Intervall erhöht).

**Verhalten bei `batch_id == 0`:** zeigt Stream-Start oder Beginn eines Full Refresh an — der Code in `foreach_batch_sink` sollte einen Full Refresh für nachgelagerte Datenquellen korrekt behandeln.

**Stand:** 2026-09-14.
