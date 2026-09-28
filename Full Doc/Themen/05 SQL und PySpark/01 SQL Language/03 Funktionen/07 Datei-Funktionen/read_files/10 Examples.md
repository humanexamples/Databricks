# `read_files` — Examples

**Beispiel 1 – Format und Schema automatisch erkennen**
```sql
SELECT * FROM read_files('abfss://container@storageAccount.dfs.core.windows.net/base/path');
```

**Beispiel 2 – CSV ohne Header mit angegebenem Schema**
```sql
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv',
    schema => 'id int, ts timestamp, event string');
```

**Beispiel 3 – CSV mit Headern (Schema inferiert)**
```sql
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'csv')
```

**Beispiel 4 – CSV-Dateien nach Endung lesen**
```sql
SELECT * FROM read_files('s3://bucket/path/*.csv')
```

**Beispiel 5 – einzelne JSON-Datei**
```sql
SELECT * FROM read_files(
    'abfss://container@storageAccount.dfs.core.windows.net/path/single.json')
```

**Beispiel 6 – JSON mit `schemaHints`**
```sql
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaHints => 'id int')
```

**Beispiel 7 – nach Änderungsdatum filtern**
```sql
SELECT * FROM read_files(
    'gs://my-bucket/avroData',
    modifiedAfter => date_sub(current_date(), 1),
    modifiedBefore => current_date())
```

**Beispiel 8 – Delta-Tabelle mit Quellpfad erstellen**
```sql
CREATE TABLE my_avro_data
  AS SELECT *, _metadata.file_path
  FROM read_files('gs://my-bucket/avroData')
```

**Beispiel 9 – Streaming Table nur mit neuen Dateien**
```sql
CREATE OR REFRESH STREAMING TABLE avro_data
  AS SELECT * FROM STREAM read_files('gs://my-bucket/avroData', includeExistingFiles => false);
```

**Beispiel 10 – Dateien in einem Volume auflisten (ohne `content`)**
```sql
SELECT
  * EXCEPT (content),
  _metadata
FROM read_files(
  '/Volumes/<catalog>/<schema>/<volume>',
  format => 'binaryFile');
```

**Beispiel 11 – Bilddateien nach Größe filtern**
```sql
SELECT
  * EXCEPT (content),
  _metadata
FROM read_files(
  '/Volumes/my_catalog/my_schema/my_volume',
  format => 'binaryFile',
  fileNamePattern => '*.{jpg,jpeg,png,JPG,JPEG,PNG}')
WHERE _metadata.file_size BETWEEN 20000 AND 1000000;
```

**Beispiel 12 – PDFs auflisten, die innerhalb des letzten Tages geändert wurden**
```sql
SELECT
  * EXCEPT (content),
  _metadata
FROM read_files(
  '/Volumes/my_catalog/my_schema/my_volume',
  format => 'binaryFile',
  fileNamePattern => '*.{pdf,PDF}')
WHERE modificationTime >= current_timestamp() - INTERVAL 1 DAY;
```

**Beispiel 13 – Bilder mit einer AI-Funktion verarbeiten**
```sql
SELECT
  path AS file_path,
  ai_query(
    'system.ai.llama-4-maverick',
    'Describe this image in ten words or less: ',
    files => content
  ) AS result
FROM read_files(
  's3://my-s3-bucket/path/to/images/',
  format => 'binaryFile',
  fileNamePattern => '*.{jpg,jpeg,png,JPG,JPEG,PNG}')
WHERE _metadata.file_size < 1000000
  AND _metadata.file_name LIKE '%robots%';
```

**Beispiel 14 – Dokumente parsen**
```sql
SELECT
  path AS file_path,
  ai_parse_document(
    content,
    map('version', '2.0')
  ) AS result
FROM read_files(
  '/Volumes/main/public/my_files/',
  format => 'binaryFile',
  fileNamePattern => '*.{jpg,jpeg,pdf,png}')
WHERE _metadata.file_name ILIKE '%receipt%';
```

**Beispiel 15 – Dateien mit strukturierten Tabellen joinen**
```sql
SELECT
  users.user_id,
  user_files.file_id,
  files._metadata.file_name AS file_name,
  files.* EXCEPT (content),
  ai_parse_document(files.content, map('version', '2.0')) AS parsed_document
FROM read_files(
  's3://my-bucket-name/files/',
  format => 'binaryFile',
  fileNamePattern => '*.{pdf,doc,docx,ppt,pptx,png,jpg,jpeg}') AS files
JOIN user_files
  ON user_files.file_id = element_at(split(files.path, '/'), -2)
JOIN users
  ON users.user_id = user_files.user_id
WHERE users.email LIKE '%@databricks.com'
  AND files._metadata.file_size < 10000000;
```
