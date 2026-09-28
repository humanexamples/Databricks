# `read_files` — Die `_metadata`-Spalte

`read_files` stellt eine `_metadata`-Spalte mit Metadaten pro Datei bereit. Sie ist **nicht** Teil von `SELECT *` und muss explizit ausgewählt werden.

Felder:

- `file_path` (`STRING`): vollständiger Pfad der Quelldatei.
- `file_name` (`STRING`): Name der Quelldatei.
- `file_size` (`LONG`): Größe der Quelldatei in Bytes.
- `file_modification_time` (`TIMESTAMP`): letzte Änderung der Quelldatei.
- `file_block_start` (`LONG`): Beginn des gelesenen Blocks.
- `file_block_length` (`LONG`): Länge des gelesenen Blocks.

```sql
SELECT * EXCEPT (content), _metadata
FROM read_files('/Volumes/my_catalog/my_schema/my_volume', format => 'binaryFile');
```
