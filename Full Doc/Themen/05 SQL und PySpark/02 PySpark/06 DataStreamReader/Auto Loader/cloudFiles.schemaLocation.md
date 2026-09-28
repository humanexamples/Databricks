# `cloudFiles.schemaLocation`

Speicherort für das von Auto Loader inferierte Schema.

## Beschreibung

> *"The location to store the inferred schema and subsequent changes."*

Verzeichnis, in dem Auto Loader das inferierte Schema und dessen spätere Änderungen ablegt (in einem Unterverzeichnis `_schemas`). Erst das Setzen dieses Pfads aktiviert Schema-Inferenz und -Evolution überhaupt. Es darf identisch mit `checkpointLocation` sein. Für die eigentlich schon fest typisierten Formate `binaryFile` und `text` empfiehlt Databricks, den Pfad trotzdem zu setzen, um wiederholte Partitionsspalten-Inferenz bei jedem Stream-Start zu vermeiden. Unity Catalog erlaubt nicht, diesen Pfad innerhalb des Tabellenverzeichnisses selbst zu verschachteln.

## Beispiel

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .load("/Volumes/analytics/bronze/events"))
```

```sql
CREATE OR REFRESH STREAMING TABLE events
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaLocation => '/Volumes/analytics/bronze/_schema'
);
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
