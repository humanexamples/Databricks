# `cloudFiles.schemaEvolutionMode`

Steuert, wie Auto Loader auf neu auftauchende Spalten reagiert.

## Beschreibung

> *"The mode for evolving the schema as new columns are discovered in the data."*

Es gibt fünf Modi. Bei `addNewColumns` (Default, wenn kein Schema angegeben ist) stoppt der Stream bei einer neuen Spalte mit einer `UnknownFieldException`, nachdem die neue Spalte bereits ins gespeicherte Schema aufgenommen wurde — ein Neustart läuft dann mit dem erweiterten Schema weiter. `addNewColumnsWithTypeWidening` verhält sich wie `addNewColumns`, erweitert zusätzlich kompatible Typen automatisch (z. B. `int` → `long`; ab Databricks Runtime 16.4). Bei `rescue` entwickelt sich das Schema nie weiter, der Stream läuft ungestört durch, neue Spalten landen in der Spalte `_rescued_data`. Bei `failOnNewColumns` schlägt der Stream fehl und startet nicht automatisch neu, bis das Schema manuell aktualisiert oder die betroffene Datei entfernt wurde. Bei `none` (Default, wenn ein Schema explizit angegeben ist) findet keine Evolution statt, neue Spalten werden schlicht ignoriert und auch nicht gerettet, außer `rescuedDataColumn` ist gesetzt. `addNewColumns` selbst ist bei explizit angegebenem `schema` nicht erlaubt, funktioniert aber in Kombination mit `schemaHints`.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.schemaEvolutionMode", "rescue")
      .load("/Volumes/analytics/bronze/events"))
```

```sql
CREATE OR REFRESH STREAMING TABLE events
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaLocation => '/Volumes/analytics/bronze/_schema',
  schemaEvolutionMode => 'rescue'
);
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
