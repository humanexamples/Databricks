[← Übersicht](../00%20Uebersicht.md)

# Geteilten CDF lesen (Empfänger / Recipient)

> Quellen: [Read data shared using Databricks-to-Databricks sharing](https://docs.databricks.com/aws/en/opensharing/read-data-databricks) · [Read data shared using open sharing](https://docs.databricks.com/aws/en/opensharing/read-data-open) · [Query data: OpenSharing](https://docs.databricks.com/aws/en/query/formats/opensharing) · [Type widening](https://docs.databricks.com/aws/en/tables/features/type-widening) · [System tables](https://docs.databricks.com/aws/en/admin/system-tables/) · [Error classes](https://docs.databricks.com/aws/en/error-messages/error-classes) · [Serverless Release Notes](https://docs.databricks.com/aws/en/release-notes/serverless/)

**Voraussetzung auf Anbieterseite:** CDF auf der Quelltabelle aktiviert und Tabelle `WITH HISTORY` geteilt → [01 Provider](01%20CDF%20teilen%20%28Provider%29.md). History Sharing erfordert **DBR 12.2 LTS** oder höher.

---

## A – Databricks-to-Databricks: Empfänger arbeitet in Databricks

Die geteilte Tabelle erscheint im Katalog des Empfängers und wird **wie eine eigene Tabelle** angesprochen.

### Batch mit SQL

Time Travel auf der geteilten Historie:

```sql
SELECT * FROM vaccine.vaccine_us.vaccine_us_distribution VERSION AS OF 3;
SELECT * FROM vaccine.vaccine_us.vaccine_us_distribution TIMESTAMP AS OF "2023-01-01 00:00:00";
```

Ist CDF aktiviert, geht auch `table_changes()`, mit Version oder Zeitstempel:

```sql
SELECT * FROM table_changes('vaccine.vaccine_us.vaccine_us_distribution', 0, 3);
SELECT * FROM table_changes('vaccine.vaccine_us.vaccine_us_distribution', "2023-01-01 00:00:00", "2022-02-01 00:00:00");
```

### Streaming

Mit geteilter Historie kann die Tabelle Quelle für Structured Streaming sein. Unterstützte Optionen: `ignoreDeletes`, `ignoreChanges`, `startingVersion`, `startingTimestamp`, `maxFilesPerTrigger`, `maxBytesPerTrigger` und **`readChangeFeed`**.

Normaler Stream (Beispiele aus der Doku):

```scala
spark.readStream.format("deltaSharing")
.option("startingVersion", 0)
.option("ignoreChanges", true)
.option("maxFilesPerTrigger", 10)
.table("vaccine.vaccine_us.vaccine_us_distribution")
```

```python
spark.readStream.format("deltaSharing")\
.option("startingVersion", 0)\
.option("ignoreDeletes", true)\
.option("maxBytesPerTrigger", 10000)\
.table("vaccine.vaccine_us.vaccine_us_distribution")
```

CDF streamen:

```scala
spark.readStream.format("deltaSharing")
.option("readChangeFeed", "true")
.table("vaccine.vaccine_us.vaccine_us_distribution")
```

**Trigger:** `Trigger.ProcessingTime` (Default), `Trigger.AvailableNow` (für `responseFormat=delta` ab **DBR 18.0**; bis DBR 17.3 wird es automatisch zu `Trigger.Once`), `Trigger.Once` (deprecated).

### Tabellen mit Deletion Vectors oder Column Mapping

- Batch-Reads: SQL Warehouse oder DBR **14.1+**.
- **CDF- und Streaming-Queries: DBR 14.2+**, und zusätzlich die Option **`responseFormat=delta`**.
- `responseFormat=delta` ist **optional** ab DBR **16.4** für CDF- oder normale Streaming-Queries bzw. ab DBR **17.3** für CDF-**Streaming**-Queries.

```scala
import org.apache.spark.sql.SparkSession

// Batch query
spark.read.format("deltaSharing").table(<tableName>)

// CDF query
spark.read.format("deltaSharing")
  .option("readChangeFeed", "true")
  .option("responseFormat", "delta")
  .option("startingVersion", 1)
  .table(<tableName>)

// Streaming query
spark.readStream.format("deltaSharing").option("responseFormat", "delta").table(<tableName>)
```

---

## B – Open Sharing: Empfänger ohne Databricks-Katalog (Profil-Datei)

Gelesen wird über eine **Credential-Datei** (`<profile-path>`) und den Pfad `#<share-name>.<schema-name>.<table-name>`.

### Spark (Batch)

Erfordert `delta-sharing-spark` **0.5.0** oder höher. Mindestens **ein Startparameter** ist Pflicht.

| Parameter | Bedeutung |
|---|---|
| `<starting-version>` | optional; Startversion, inklusive (Long) |
| `<ending-version>` | optional; Endversion, inklusive. Ohne Angabe: neueste Version |
| `<starting-timestamp>` | optional; wird in die erste Version **≥** diesem Zeitpunkt umgerechnet. Format `yyyy-mm-dd hh:mm:ss[.fffffffff]` |
| `<ending-timestamp>` | optional; wird in die letzte Version **≤** diesem Zeitpunkt umgerechnet |

```python
delta_sharing.load_table_changes_as_spark(f"<profile-path>#<share-name>.<schema-name>.<table-name>",
  starting_version=<starting-version>,
  ending_version=<ending-version>)

delta_sharing.load_table_changes_as_spark(f"<profile-path>#<share-name>.<schema-name>.<table-name>",
  starting_timestamp=<starting-timestamp>,
  ending_timestamp=<ending-timestamp>)

spark.read.format("deltaSharing").option("readChangeFeed", "true")\
.option("startingVersion", <starting-version>)\
.option("endingVersion", <ending-version>)\
.load("<profile-path>#<share-name>.<schema-name>.<table-name>")

spark.read.format("deltaSharing").option("readChangeFeed", "true")\
.option("startingTimestamp", <starting-timestamp>)\
.option("endingTimestamp", <ending-timestamp>)\
.load("<profile-path>#<share-name>.<schema-name>.<table-name>")
```

```scala
spark.read.format("deltaSharing").option("readChangeFeed", "true")
.option("startingVersion", <starting-version>)
.option("endingVersion", <ending-version>)
.load("<profile-path>#<share-name>.<schema-name>.<table-name>")

spark.read.format("deltaSharing").option("readChangeFeed", "true")
.option("startingTimestamp", <starting-timestamp>)
.option("endingTimestamp", <ending-timestamp>)
.load("<profile-path>#<share-name>.<schema-name>.<table-name>")
```

Variante aus der Seite „Query data: OpenSharing“:

```python
df = (spark.read
  .format("deltasharing")
  .option("readChangeFeed", "true")
  .option("startingTimestamp", "2021-04-21 05:45:46")
  .option("endingTimestamp", "2021-05-21 12:00:00")
  .load("<profile-path>#<share-name>.<schema-name>.<table-name>")
)
```

### Spark Structured Streaming

Erfordert `delta-sharing-spark` **0.6.0** oder höher. Gleiche Optionen wie oben, inklusive `readChangeFeed`. `Trigger.AvailableNow` mit Beachtung von `maxVersionsPerRpc` ab `delta-sharing-spark` **1.4.0**.

```python
streaming_df = (spark.readStream
  .format("deltasharing")
  .load("<profile-path>#<share-name>.<schema-name>.<table-name>")
)

# If CDF is enabled on the source table
streaming_cdf_df = (spark.readStream
  .format("deltasharing")
  .option("readChangeFeed", "true")
  .option("startingTimestamp", "2021-04-21 05:45:46")
  .load("<profile-path>#<share-name>.<schema-name>.<table-name>")
)
```

Deletion Vectors / Column Mapping bei Open Sharing: `delta-sharing-spark` **3.1+**, für CDF und Streaming `responseFormat=delta`:

```scala
import org.apache.spark.sql.SparkSession

val spark = SparkSession
        .builder()
        .appName("...")
        .master("...")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()

val tablePath = "<profile-file-path>#<share-name>.<schema-name>.<table-name>"

// Batch query
spark.read.format("deltaSharing").load(tablePath)

// CDF query
spark.read.format("deltaSharing")
  .option("readChangeFeed", "true")
  .option("responseFormat", "delta")
  .option("startingVersion", 1)
  .load(tablePath)

// Streaming query
spark.readStream.format("deltaSharing").option("responseFormat", "delta").load(tablePath)
```

### pandas

Ob ein CDF verfügbar ist, hängt davon ab, ob der Anbieter ihn geteilt hat.

```python
import delta_sharing
delta_sharing.load_table_changes_as_pandas(
  f"<profile-path>#<share-name>.<schema-name>.<table-name>",
  starting_version=<starting-version>,
  ending_version=<ending-version>)

delta_sharing.load_table_changes_as_pandas(
  f"<profile-path>#<share-name>.<schema-name>.<table-name>",
  starting_timestamp=<starting-timestamp>,
  ending_timestamp=<ending-timestamp>)
```

Leeres oder unerwartetes Ergebnis → Datenanbieter kontaktieren.

---

## Sonderfälle

### Type Widening

Unterstützt in Databricks-to-Databricks-Sharing ab **DBR 16.1** auf beiden Seiten. Für CDF muss `responseFormat` auf `delta` stehen:

```scala
spark.read
  .format("deltaSharing")
  .option("responseFormat", "delta")
  .option("readChangeFeed", "true")
  .option("startingVersion", "<start version>")
  .option("endingVersion", "<end version>")
  .load("<table>")
```

Über eine **Typänderung hinweg** kann der CDF nicht gelesen werden. Stattdessen **zwei Reads**: einer endet bei der Version mit der Typänderung, der andere beginnt dort.

### System Tables

Databricks teilt System Tables per OpenSharing. Den CDF einer System Table per `readChangeFeed` zu streamen erfordert **DBR 17.3+**.

### Transaktionen

Delta-Sharing-Tabellen unterstützen Multi-Statement-Transaktionen; **Time Travel, CDF und Streaming** sind darin aber **nicht** unterstützt.

---

## Einschränkungen (Python-Connector und Open Sharing)

- Der OpenSharing-**Python-Connector** (1.1.0+) unterstützt Snapshot-Queries auf Tabellen mit Column Mapping, **aber keine CDF-Queries** auf solchen Tabellen.
- Der Python-Connector bricht CDF-Queries mit `use_delta_format=True` ab, wenn sich das Schema im abgefragten Versionsbereich geändert hat.
- **Geteilte Streaming Tables** (Databricks-to-Open): nur aktueller Snapshot, **kein** CDF, keine Historie, keine Streaming-Quelle.

## Fehlermeldungen beim Lesen geteilter CDFs

| Fehler | Bedeutung |
|---|---|
| `DS_CDF_NOT_ENABLED` | CDF ist auf der Originaltabelle für diese Version nicht aktiviert → Anbieter kontaktieren |
| `DS_CDF_NOT_SHARED` | CDF ist für die Tabelle nicht geteilt → Anbieter kontaktieren |
| `DS_CDF_NOT_ENABLED_AUTO_CDF_AVAILABLE` | Tabelle unterstützt **Auto CDF**, aber nicht über CDC-Dateien. Lösung: **DBR 17.3+** und Option `("responseFormat", "delta")`; der Client muss Auto CDF aktiviert haben |
| `DS_CDF_MODE_INCONSISTENT` | CDF-Modus hat sich ab einer Version geändert und passt nicht zum Modus beim Start der Query |
| `DS_CDF_RPC_INVALID_PARAMETER` | ungültiger Parameter |

---
[← Vorherige Datei](01%20CDF%20teilen%20%28Provider%29.md) · [Übersicht](../00%20Uebersicht.md) · [Weiter: Lakebase CDF →](../05%20Lakebase%20CDF/01%20Lakebase%20Change%20Data%20Feed.md)
