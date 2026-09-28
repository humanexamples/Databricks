# `read_files` — Nutzung in Streaming Tables

`read_files` kann in Streaming Tables Dateien in Delta Lake laden. Dann läuft intern **Auto Loader**. Das Schlüsselwort `STREAM` ist Pflicht.

Im Streaming-Modus inferiert `read_files` das Schema aus einer **Stichprobe** der Daten. Es kann das Schema weiterentwickeln, wenn neue Daten kommen. Im Batch-Modus liest es dagegen alle Dateien (siehe [Schema-Inferenz](06%20Schema-Inferenz.md)).

```sql
-- Batch
SELECT * FROM read_files('gs://my-bucket/avroData');

-- Streaming: dieselbe Funktion mit STREAM, innerhalb einer Streaming Table
CREATE OR REFRESH STREAMING TABLE avro_data
AS SELECT * FROM STREAM read_files('gs://my-bucket/avroData', includeExistingFiles => false);
```

Die Streaming-Optionen (`includeExistingFiles`, `maxFilesPerTrigger`, `schemaEvolutionMode` usw.) gelten nur mit `STREAM` — siehe [Options](09%20Options.md).
