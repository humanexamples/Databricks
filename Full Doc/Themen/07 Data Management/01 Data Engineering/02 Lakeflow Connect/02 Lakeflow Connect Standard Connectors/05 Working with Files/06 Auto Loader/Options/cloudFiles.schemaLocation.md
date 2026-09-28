# cloudFiles.schemaLocation

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None (erforderlich, um das Schema zu inferieren) |
| **Datentyp** | Pfad-String |
| **`read_files`-Parameter** | `schemaLocation` (in Lakeflow-Pipelines automatisch verwaltet) |
| **Seit** | alle Versionen |

## Beschreibung

> „The location to store the inferred schema and subsequent changes."

Verzeichnis, in dem Auto Loader das inferierte Schema und dessen spätere Änderungen ablegt (Unterverzeichnis `_schemas`). Das Angeben dieses Pfads **aktiviert Schema-Inferenz und -Evolution**. Es darf dasselbe Verzeichnis wie `checkpointLocation` sein. Für Binär- und `text`-Formate empfiehlt Databricks, den Pfad ebenfalls zu setzen, um wiederholte Partitionsspalten-Inferenz zu vermeiden.

Unity Catalog erlaubt **nicht**, diesen Pfad innerhalb des Tabellenverzeichnisses zu verschachteln.

## Beispiel

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .load("/Volumes/analytics/bronze/events"))
```

## Siehe auch

- [../01 Schema-Inferenz und -Evolution.md](../01%20Schema-Inferenz%20und%20-Evolution.md)
- [../03 Unity-Catalog-Integration.md](../03%20Unity-Catalog-Integration.md)
- [../09 Datei-Tracking und Checkpoints.md](../09%20Datei-Tracking%20und%20Checkpoints.md)
