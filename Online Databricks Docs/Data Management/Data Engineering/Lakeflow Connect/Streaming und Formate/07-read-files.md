# Die Funktion read_files

`read_files` ist eine Table-Valued-Function in SQL, die Dateien unter einem angegebenen Pfad liest und die Daten in tabellarischer Form zurückgibt. Verfügbar in Databricks SQL und Databricks Runtime 13.3 LTS und höher.

Unterstützt werden die Formate JSON, CSV, XML, TEXT, BINARYFILE, PARQUET, AVRO und ORC. Das Format kann automatisch erkannt und ein einheitliches Schema über alle Dateien hinweg abgeleitet werden. Im Beta-Status kann mit `format => 'file'` statt des Dateiinhalts eine `FILE`-Referenz je Datei zurückgegeben werden.

## Syntax

```sql
%sql
read_files(path [, option_key => option_value ] [...])
```

## Argumente

Die Funktion erfordert Named Parameter Invocation für die Optionsschlüssel.

- **`path`**: Ein `STRING` mit dem URI des Datenspeicherorts. Unterstützt Azure Data Lake Storage (`abfss://`), S3 (`s3://`) und Google Cloud Storage (`gs://`). Kann Glob-Muster enthalten.
- **`option_key`**: Name der Konfigurationsoption. Für Optionen mit Punkten (`.`) im Namen sind Backticks nötig.
- **`option_value`**: Ein konstanter Ausdruck zur Festlegung des Wertes. Literale und skalare Funktionen sind erlaubt.

## Rückgabewert

Eine Tabelle mit den Daten aller unter `path` gelesenen Dateien. Das Schema hängt vom Dateiformat ab:

- **`BINARYFILE`**: Festes Schema mit den Spalten `path` (STRING), `modificationTime` (TIMESTAMP), `length` (LONG) und `content` (BINARY). Mit `* EXCEPT (content)` lässt sich der Binärinhalt bei reinen Metadaten-Abfragen ausschließen.
- **`TEXT`**: Festes Schema mit einer einzigen Spalte `value` (STRING).
- **Alle anderen Formate** (JSON, CSV, XML, PARQUET, AVRO, ORC): Das Schema wird aus dem Dateiinhalt abgeleitet oder über die Option `schema` explizit angegeben.

## Die _metadata-Spalte

`read_files` stellt eine `_metadata`-Spalte mit dateibezogenen Metadaten bereit. Diese Spalte ist nicht in `SELECT *` enthalten und muss explizit selektiert werden. Felder:

| Feld | Typ | Beschreibung |
| --- | --- | --- |
| `file_path` | STRING | Vollständiger Pfad zur Quelldatei |
| `file_name` | STRING | Name der Quelldatei |
| `file_size` | LONG | Größe der Quelldatei in Bytes |
| `file_modification_time` | TIMESTAMP | Letzte Änderungszeit der Quelldatei |
| `file_block_start` | LONG | Start des gelesenen Dateiblocks |
| `file_block_length` | LONG | Länge des gelesenen Dateiblocks |

```sql
%sql
SELECT * EXCEPT (content), _metadata
FROM read_files('/Volumes/my_catalog/my_schema/my_volume', format => 'binaryFile');
```

## Dateierkennung (File Discovery)

`read_files` kann eine einzelne Datei oder rekursiv alle Dateien unter einem Verzeichnis lesen, sofern kein Glob-Muster angegeben ist. Ein Glob-Muster schränkt die Rekursion auf ein bestimmtes Verzeichnismuster ein.

**Glob-Muster:**

| Muster | Beschreibung |
| --- | --- |
| `?` | Genau ein beliebiges Zeichen |
| `*` | Null oder mehr beliebige Zeichen |
| `[abc]` | Ein Zeichen aus der Menge {a,b,c} |
| `[a-z]` | Ein Zeichen aus dem Bereich {a…z} |
| `[^a]` | Ein Zeichen, das nicht aus der Menge/dem Bereich {a} stammt |
| `{ab,cd}` | Ein String aus der Menge {ab, cd} |
| `{ab,c{de,fh}}` | Ein String aus der Menge {ab, cde, cfh} |

`read_files` verwendet standardmäßig den strikten Globber von Auto Loader (Option `useStrictGlobber`). Bei deaktiviertem striktem Globber werden abschließende Schrägstriche (`/`) ignoriert, und ein Sternmuster wie `/*/` kann mehrere Verzeichnisse gleichzeitig erschließen.

## Schema-Inferenz

Ohne explizite `schema`-Angabe leitet `read_files` ein einheitliches Schema über alle gefundenen Dateien ab – dazu müssen grundsätzlich alle Dateien gelesen werden, sofern kein `LIMIT` verwendet wird. Mit `schemaHints` lassen sich Teile des abgeleiteten Schemas fixieren. Standardmäßig wird eine `rescuedDataColumn` bereitgestellt, die nicht zum Schema passende Daten rettet; sie lässt sich mit `schemaEvolutionMode => 'none'` deaktivieren.

**Partitions-Schema-Inferenz:** Bei Hive-artig partitionierten Verzeichnissen (`/spaltenname=wert/`) erkennt `read_files` Partitionsspalten automatisch. Ist eine Spalte sowohl als Partitions- als auch als Datenspalte vorhanden, gewinnt der Partitionswert – sofern nicht über die Option `partitionColumns` anders festgelegt.

## Authentifizierung

`read_files` liest Dateien aus Unity-Catalog-External-Locations oder -Volumes (Managed und External). Erforderlich ist die Berechtigung `READ FILES` auf der External Location bzw. `READ VOLUME` auf dem Volume.

## Verwendung in Streaming-Tabellen

In Streaming-Tabellen nutzt `read_files` intern Auto Loader; dabei muss das Schlüsselwort `STREAM` verwendet werden. In diesem Fall wird das Schema anhand einer Datenstichprobe abgeleitet und kann sich mit zunehmender Datenmenge weiterentwickeln (Schema Evolution).

## Wichtige Optionen

**Basis-Optionen:**

| Option | Typ | Beschreibung | Standard |
| --- | --- | --- | --- |
| `format` | String | Dateiformat der Quelle; wird automatisch erkannt, falls nicht angegeben | – |
| `schema` | String | Schema als DDL-String, z. B. `'id int, ts timestamp, event string'` | – |
| `inferColumnTypes` | Boolean | Ob bei Schema-Inferenz exakte Spaltentypen abgeleitet werden | `true` |
| `partitionColumns` | String | Kommaseparierte Liste der aus dem Verzeichnispfad abzuleitenden Hive-Partitionsspalten | – |
| `schemaHints` | String | Schema-Hinweise für die Inferenz | – |
| `useStrictGlobber` | Boolean | Ob ein strikter Globber verwendet wird (Standardverhalten anderer Spark-Dateiquellen) | `true` |

**Streaming-Optionen (nur in Streaming-Tabellen/-Queries):**

| Option | Typ | Beschreibung | Standard |
| --- | --- | --- | --- |
| `allowOverwrites` | Boolean | Ob nach der Erkennung geänderte Dateien erneut verarbeitet werden | `false` |
| `includeExistingFiles` | Boolean | Ob bereits vorhandene Dateien beim ersten Start mitverarbeitet werden | `true` |
| `maxBytesPerTrigger` | Byte String | Maximale neue Datenmenge je Trigger, z. B. `'10g'` (weiches Limit) | – |
| `maxFilesPerTrigger` | Integer | Maximale Anzahl neuer Dateien je Trigger | `1000` |
| `schemaEvolutionMode` | String | Modus für die Schema-Evolution bei neu entdeckten Spalten | `"addNewColumns"` ohne Schema, sonst `"none"` |
| `schemaLocation` | String | Speicherort für das abgeleitete Schema und dessen Änderungen | – |

## Beispiele

```sql
%sql
-- Liest die Dateien am angegebenen Pfad; erkennt Format und Schema automatisch.
SELECT * FROM read_files('abfss://container@storageAccount.dfs.core.windows.net/base/path');

-- Liest kopflose CSV-Dateien mit angegebenem Schema.
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv',
    schema => 'id int, ts timestamp, event string');

-- Leitet das Schema von CSV-Dateien mit Header ab.
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv')

-- Liest Dateien mit der Endung .csv.
SELECT * FROM read_files('s3://bucket/path/*.csv')

-- Liest eine einzelne JSON-Datei.
SELECT * FROM read_files(
    'abfss://container@storageAccount.dfs.core.windows.net/path/single.json')

-- Liest JSON-Dateien und überschreibt den Typ der Spalte `id` auf integer.
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaHints => 'id int')

-- Liest Dateien, die gestern hochgeladen oder geändert wurden.
SELECT * FROM read_files(
    'gs://my-bucket/avroData',
    modifiedAfter => date_sub(current_date(), 1),
    modifiedBefore => current_date())

-- Erstellt eine Delta-Tabelle und speichert den Quelldateipfad mit den Daten.
CREATE TABLE my_avro_data
  AS SELECT *, _metadata.file_path
  FROM read_files('gs://my-bucket/avroData')

-- Erstellt eine Streaming-Tabelle, die nur Dateien verarbeitet, die nach der Tabellenerstellung erscheinen.
CREATE OR REFRESH STREAMING TABLE avro_data
  AS SELECT * FROM STREAM read_files('gs://my-bucket/avroData', includeExistingFiles => false);
```

## Arbeiten mit unstrukturierten Dateien

Mit dem Format `BINARYFILE` lassen sich unstrukturierte Dateien in Unity-Catalog-Volumes lesen und filtern, auch in Kombination mit KI-Funktionen.

**Alle Dateien in einem Volume auflisten** (nur Metadaten, ohne Binärinhalt):

```sql
%sql
SELECT
  * EXCEPT (content),
  _metadata
FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>',
  format => 'binaryFile'
);
```

**Bilddateien nach Größe filtern:**

```sql
%sql
SELECT
  * EXCEPT (content),
  _metadata
FROM read_files(
  '/Volumes/my_catalog/my_schema/my_volume',
  format => 'binaryFile',
  fileNamePattern => '*.{jpg,jpeg,png,JPG,JPEG,PNG}'
)
WHERE _metadata.file_size BETWEEN 20000 AND 1000000;
```

**Kürzlich geänderte PDF-Dateien auflisten:**

```sql
%sql
SELECT
  * EXCEPT (content),
  _metadata
FROM read_files(
  '/Volumes/my_catalog/my_schema/my_volume',
  format => 'binaryFile',
  fileNamePattern => '*.{pdf,PDF}'
)
WHERE modificationTime >= current_timestamp() - INTERVAL 1 DAY;
```

**KI-Funktion auf Bilddateien anwenden:**

```sql
%sql
SELECT
  path AS file_path,
  ai_query(
    'databricks-llama-4-maverick',
    'Describe this image in ten words or less: ',
    files => content
  ) AS result
FROM read_files(
  's3://my-s3-bucket/path/to/images/',
  format => 'binaryFile',
  fileNamePattern => '*.{jpg,jpeg,png,JPG,JPEG,PNG}'
)
WHERE _metadata.file_size < 1000000
  AND _metadata.file_name LIKE '%robots%';
```

**Dokumente nach Dateinamensmuster parsen:**

```sql
%sql
SELECT
  path AS file_path,
  ai_parse_document(
    content,
    map('version', '2.0')
  ) AS result
FROM read_files(
  '/Volumes/main/public/my_files/',
  format => 'binaryFile',
  fileNamePattern => '*.{jpg,jpeg,pdf,png}'
)
WHERE _metadata.file_name ILIKE '%receipt%';
```

**Dateien mit einer strukturierten Tabelle verknüpfen:**

```sql
%sql
SELECT
  users.user_id,
  user_files.file_id,
  files._metadata.file_name AS file_name,
  files.* EXCEPT (content),
  ai_parse_document(files.content, map('version', '2.0')) AS parsed_document
FROM read_files(
  's3://my-bucket-name/files/',
  format => 'binaryFile',
  fileNamePattern => '*.{pdf,doc,docx,ppt,pptx,png,jpg,jpeg}'
) AS files
JOIN user_files
  ON user_files.file_id = element_at(split(files.path, '/'), -2)
JOIN users
  ON users.user_id = user_files.user_id
WHERE users.email LIKE '%@databricks.com'
  AND files._metadata.file_size < 10000000;
```

## Verwandte Funktionen

- `list_files`: Table-Valued-Function zum Auflisten von Dateien ohne deren Inhalt zu lesen.

---
**Quelle:** https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/functions/read_files  
**Stand:** 2026-08-07
