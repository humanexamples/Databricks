# `DataFrameWriter.options()`

Fügt mehrere Ausgabeoptionen gleichzeitig für die zugrunde liegende Datenquelle hinzu.

## Signatur

```python
options(**options)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `**options` | `dict` | String-Schlüssel, die auf Werte primitiver Typen abgebildet werden. Verfügbare Optionen siehe `DataFrameWriter`-Optionen (`/aws/en/spark/api-options#batch-write-options`). |

## Rückgabewert

`DataFrameWriter`

## Verfügbare Optionen

Die [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) führt für `DataFrameWriter` keinen formatübergreifenden „Common"-Abschnitt — jedes Zielformat hat seine eigene Optionstabelle. Auf Databricks am wichtigsten ist **Delta Lake / Apache Iceberg** (Standardformat, siehe [13 DataFrameWriter — Delta Lake und Apache Iceberg.md](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/13%20DataFrameWriter%20%E2%80%94%20Delta%20Lake%20und%20Apache%20Iceberg.md)):

| Option | Standard | Typ | Beschreibung |
|---|---|---|---|
| `mergeSchema` | `None` | `true`/`false` | Aktiviert Schema Evolution für den Schreibvorgang — neue Spalten aus der Quelle werden dem Zielschema hinzugefügt. Gilt sowohl für Batch- als auch für Streaming-Appends. |
| `overwriteSchema` | `None` | `true`/`false` | Ersetzt Schema und Partitionierung beim Überschreiben. Erfordert `mode("overwrite")` ohne `replaceWhere`, nicht kombinierbar mit `partitionOverwriteMode`. |
| `replaceWhere` | `None` | Prädikat-Ausdruck | Überschreibt atomar nur die Datensätze, die dem Prädikat entsprechen (selektives Überschreiben). |
| `replaceOn` | `None` | Boolean-Ausdruck | Boolean-Ausdruck, der Zielzeilen zum Ersetzen durch Quellzeilen matcht (ab Runtime 17.1). |
| `replaceUsing` | `None` | kommagetrennte Spaltenliste | Spalten, über die Ziel- und Quellzeilen für den Ersatz gematcht werden (ab Runtime 16.3). |
| `targetAlias` | `None` | String | Alias für die Zieltabelle, zur Disambiguierung bei `replaceOn`/`replaceWhere`. |
| `partitionOverwriteMode` | `None` | `static`/`dynamic` | Bei `dynamic` werden nur Partitionen mit neuen Daten überschrieben (Legacy, nicht auf Serverless/DBSQL). |
| `clusterByAuto` | `false` | `true`/`false` | Aktiviert Automatic Liquid Clustering (Keys werden von Databricks gewählt); nur mit `mode("overwrite")`, ab Runtime 16.4. |
| `optimizeWrite` | `None` | `true`/`false` | Aktiviert Auto Optimize Write für diesen Schreibvorgang (überschreibt die Spark-Konfiguration). |
| `userMetadata` | `None` | String | Benutzerdefinierter String im Commit, sichtbar in `DESCRIBE HISTORY`. |
| `txnAppId` | `None` | String | Eindeutige Anwendungs-ID für idempotente Schreibvorgänge in `foreachBatch` — zusammen mit `txnVersion` für Exactly-once-Writes über mehrere Delta-Tabellen. |
| `txnVersion` | `None` | monoton steigende Ganzzahl | Transaktionsversion für idempotente `foreachBatch`-Writes, zusammen mit `txnAppId`. |

Für andere Zielformate (Avro, CSV, Excel, JSON, ORC, Parquet, Text, XML) gilt je eine eigene Optionstabelle, jeweils mit eigenem `compression`-Codec-Wertebereich sowie ggf. `dateFormat`/`timestampFormat`/`encoding`/`lineSep` — vollständige Tabellen in [07 Data Management/.../03 Spark API Options/12–20](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/).

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="options") as d:
    df = spark.createDataFrame([(100, None)], "age INT, name STRING")
    df.write.options(nullValue="Alice", header=True).mode(
        "overwrite").format("csv").save(d)
    spark.read.option("header", True).format('csv').load(d).show()
    # +---+------------+
    # |age|        name|
    # +---+------------+
    # |100|Alice|
    # +---+------------+
```

## Quellen

- DataFrameWriter.options: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/options

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
