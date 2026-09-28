# `read_files` — Options

## Basisoptionen

| Option | Typ | Standard | Beschreibung |
|---|---|---|---|
| `format` | String | auto-erkannt | `avro`, `binaryFile`, `csv`, `file` (Beta), `json`, `orc`, `parquet`, `text`, `xml` |
| `schema` | String | – | Schema im DDL-Format, z. B. `'id int, ts timestamp, event string'`. Ohne Angabe wird ein einheitliches Schema inferiert. |
| `inferColumnTypes` | Boolean | `true` | Ob exakte Spaltentypen inferiert werden (bei JSON/CSV standardmäßig). Bei Auto Loader ist der Default umgekehrt. |
| `partitionColumns` | String | – | Kommagetrennte Liste der Hive-Style-Partitionsspalten (`<base-path>/a=x/b=1/c=y/…`). Mit `schema` müssen diese Spalten im Schema stehen. Leerer String ignoriert alle. |
| `schemaHints` | String | – | Typangaben, die einzelne Spalten der Inferenz überschreiben |
| `useStrictGlobber` | Boolean | `true` | Strikter Globber wie bei anderen Spark-Dateiquellen (ab DBR 12.2 LTS). Bei Auto Loader ist der Default umgekehrt. |

## Streaming-Optionen (nur mit `STREAM`)

| Option | Typ | Standard | Beschreibung |
|---|---|---|---|
| `allowOverwrites` | Boolean | `false` | Ob nach der Entdeckung geänderte Dateien erneut verarbeitet werden. Bei einem Refresh wird eine Datei neu gelesen, wenn sie seit dem letzten erfolgreichen Refresh geändert wurde. |
| `includeExistingFiles` | Boolean | `true` | Ob bereits vorhandene Dateien mitverarbeitet werden. Wird nur beim allerersten Start ausgewertet. Spätere Änderungen wirken nicht. |
| `maxBytesPerTrigger` | Byte-String | – | Weiche Obergrenze neuer Bytes pro Trigger, z. B. `'10g'`. Beispiel: Limit `10g`, Dateien je 3 GB → 12 GB pro Microbatch. |
| `maxFilesPerTrigger` | Integer | `1000` | Maximale Anzahl neuer Dateien pro Trigger |
| `schemaEvolutionMode` | String | `'addNewColumns'` ohne Schema / `'none'` mit Schema | Umgang mit neuen Spalten. Gilt nicht für `text` und `binaryFile`. |
| `schemaLocation` | String | – | Speicherort für das inferierte Schema und seine Änderungen. In einer Streaming Table nicht nötig. |

Werden `maxBytesPerTrigger` und `maxFilesPerTrigger` zusammen gesetzt, gilt das Limit, das zuerst erreicht wird.

Bei Streaming Tables auf **serverless SQL Warehouses** beide Optionen **nicht** setzen. Dann greift die dynamische Admission Control.

## Allgemeine Dateioptionen (gemeinsam mit `spark.read`)

`ignoreCorruptFiles` (`false`), `ignoreMissingFiles` (`false`), `modifiedAfter`, `modifiedBefore`, `pathGlobFilter` / `fileNamePattern`, `recursiveFileLookup` (`false`), `ignoredPathSegmentRegex` (`^[._]`, ab DBR 19).

## Format-spezifische Optionen

Die Optionen für JSON, CSV, XML, Parquet, Avro, Text, ORC und Binary sind die Leseoptionen des `DataFrameReader`.
