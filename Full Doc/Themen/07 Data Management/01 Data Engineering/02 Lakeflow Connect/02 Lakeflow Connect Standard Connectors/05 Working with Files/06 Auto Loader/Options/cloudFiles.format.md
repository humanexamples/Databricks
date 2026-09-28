# cloudFiles.format

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | — (Pflichtoption) |
| **Gültige Werte** | `avro`, `binaryFile`, `csv`, `json`, `orc`, `parquet`, `text`, `xml` |
| **`read_files`-Parameter** | `format` |
| **Seit** | alle Versionen |

## Beschreibung

> „The data file format in the source path. Valid values include: `avro`, `binaryFile`, `csv`, `json`, `orc`, `parquet`, `text`, `xml`."

Legt fest, welches Dateiformat Auto Loader im Quellpfad einliest. Es gibt keinen Standardwert — die Option muss immer angegeben werden (Ausnahme: in `read_files` kann das Format teils aus der Dateiendung abgeleitet werden). Vorkomprimierte Varianten der Formate werden mitgelesen.

## Beispiel

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .load("/Volumes/analytics/bronze/events"))
```

```sql
CREATE OR REFRESH STREAMING TABLE events
AS SELECT * FROM STREAM read_files('/Volumes/analytics/bronze/events', format => 'json');
```

## Siehe auch

- [../00 Überblick.md](../00%20Überblick.md) — unterstützte Formate
- [../01 Schema-Inferenz und -Evolution.md](../01%20Schema-Inferenz%20und%20-Evolution.md) — Formate mit/ohne Schema-Inferenz
