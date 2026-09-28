[← Übersicht](../00%20Uebersicht.md)

# Change Feeds bei Datei-Ingestion (`read_files` / Auto Loader)

> Quellen: [Ingest files (Lakeflow Connect)](https://docs.databricks.com/aws/en/ingestion/file) · [Error classes](https://docs.databricks.com/aws/en/error-messages/error-classes) · [CF_INVALID_CHANGE_FEED_RESPONSE](https://docs.databricks.com/aws/en/error-messages/cf-invalid-change-feed-response-error-class)

> **Abgrenzung:** Hier geht es **nicht** um den Delta-CDF einer Tabelle, sondern um den **Change Feed eines Datei-Quellsystems** (z. B. SharePoint), den `read_files` bzw. Auto Loader mit derselben Option `readChangeFeed` lesen. Das Muster ist aber dasselbe: Änderungen erfassen und mit AUTO CDC anwenden.

## Das Problem

Ein Streaming-Ingest fügt **neue Dateien** hinzu, erfasst aber **keine Änderungen oder Löschungen** in der Quelle. Um diese anzuwenden, liest man den **Change Feed der Quelle** und wendet ihn mit `AUTO CDC` an.

> **Warnung aus der Doku:** Databricks empfiehlt, die Change Data **zuerst in einer Managed Table zu landen** und dann `AUTO CDC` auf diese Tabelle anzuwenden. Wendet man `AUTO CDC` direkt auf `STREAM read_files(..., readChangeFeed => true)` an, wird der Change Feed der Quelle **für jeden nachgelagerten Flow erneut gelesen**, was die Kosten erhöhen kann.

## Schritt 1: Change Feed in eine Streaming Table landen

Mit `readChangeFeed => true` liefert `read_files` den Change Feed inklusive der Metadatenspalten **`_file_id`**, **`_sequence`** und **`_is_deleted`**. Beispiel mit SharePoint:

```sql
CREATE OR REFRESH STREAMING TABLE documents_changes (
  _file_id STRING,
  _sequence BIGINT,
  _is_deleted BOOLEAN,
  path STRING,
  size BIGINT,
  modification_time TIMESTAMP,
  file FILE MANAGED
)
TBLPROPERTIES ('databricks.filespace-preview' = '/Volumes/my_catalog/my_schema/filespace/')
AS SELECT *
  FROM STREAM read_files(
    'https://example.sharepoint.com/sites/my-site/',
    connection => 'my_sharepoint_connection',
    format => 'file',
    readChangeFeed => true);
```

```python
from pyspark import pipelines as dp

@dp.table(
  name="documents_changes",
  table_properties={"databricks.filespace-preview": "/Volumes/my_catalog/my_schema/filespace/"}
)
def documents_changes():
  return (
    spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "file")
      .option("databricks.connection", "my_sharepoint_connection")
      .option("cloudFiles.readChangeFeed", "true")
      .load("https://example.sharepoint.com/sites/my-site/")
  )
```

## Schritt 2: Mit AUTO CDC anwenden (SCD Typ 1)

`_file_id` ist der Key, `_sequence` die Sequenz, `_is_deleted` kennzeichnet Löschungen:

```sql
CREATE OR REFRESH STREAMING TABLE documents
  TBLPROPERTIES ('databricks.filespace-preview' = '/Volumes/my_catalog/my_schema/filespace/');

CREATE FLOW documents_cdc AS AUTO CDC INTO
  documents
FROM STREAM documents_changes
  KEYS (_file_id)
  APPLY AS DELETE WHEN _is_deleted = true
  SEQUENCE BY _sequence
  COLUMNS * EXCEPT (_is_deleted, _sequence)
  STORED AS SCD TYPE 1;
```

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, expr

dp.create_streaming_table(
  name="documents",
  table_properties={"databricks.filespace-preview": "/Volumes/my_catalog/my_schema/filespace/"}
)

dp.create_auto_cdc_flow(
  target = "documents",
  source = "documents_changes",
  keys = ["_file_id"],
  sequence_by = col("_sequence"),
  apply_as_deletes = expr("_is_deleted = true"),
  except_column_list = ["_is_deleted", "_sequence"],
  stored_as_scd_type = 1
)
```

## Vergleich mit dem Delta-CDF

| | Delta-CDF | Datei-Change-Feed |
|---|---|---|
| Quelle | Delta-/Iceberg-Tabelle | Datei-Quellsystem (z. B. SharePoint) |
| Option | `readChangeFeed` auf `spark.read(Stream).table(...)` | `readChangeFeed => true` in `read_files` bzw. `cloudFiles.readChangeFeed` |
| Metadaten | `_change_type`, `_commit_version`, `_commit_timestamp` | `_file_id`, `_sequence`, `_is_deleted` |
| Delete-Bedingung in AUTO CDC | `_change_type = 'delete'` | `_is_deleted = true` |

## Zugehörige Fehlermeldungen

| Fehler | Bedeutung |
|---|---|
| `CF_READ_CHANGE_FEED_UNSUPPORTED` | `cloudFiles.readChangeFeed` wird in dieser Konfiguration nicht unterstützt |
| `CF_CHANGE_FEED_NOT_FOUND` | die Change-Feed-Ressource (Laufwerk oder Ordner) wurde nicht gefunden oder ist für den Connector nicht erreichbar |
| `CF_CHANGE_FEED_PERMISSION_DENIED` | Zugriff auf den Change Feed verweigert; Connector-Berechtigungen prüfen |
| `CF_CHANGE_FEED_RATE_LIMIT_EXCEEDED` | API-Rate-Limit des Change Feeds überschritten; später erneut versuchen oder weniger parallele Streams |
| `CF_INVALID_CHANGE_FEED_RESPONSE` | ungültige Antwort des Change-Feed-Dienstes; Databricks Support kontaktieren |
| `CF_DELTA_JOURNAL_CDF_NOT_ENABLED` | „Delta change-feed source requires CDF to be enabled on `<tableDescription>`“ |

---
[← Vorherige Datei](03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md) · [Übersicht](../00%20Uebersicht.md) · [Weiter: Delta Sharing →](../04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md)
