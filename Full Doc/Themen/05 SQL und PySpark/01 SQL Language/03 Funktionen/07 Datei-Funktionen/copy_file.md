# `copy_file` — Datei kopieren

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/copy_file>
> Gilt für: Databricks SQL, Databricks Runtime **18 LTS und höher**.
> **Beta** — Workspace-Admins steuern den Zugriff über die Previews-Seite.

Kopiert eine Datei an einen Zielpfad und gibt eine `FILE`-Referenz auf die kopierte Datei zurück.

## Syntax

```sql
copy_file(file => file
  [, destination => destination ]
  [, if_file_exists_mode => mode ])
```

Argumente können positionell oder benannt übergeben werden; nach dem ersten benannten Argument müssen alle folgenden ebenfalls benannt sein.

## Argumente

- **`file`**: ein zu kopierender `FILE`-Wert.
- **`destination`**: optionaler `STRING` mit vollständigem Zieldateipfad. Wird er weggelassen, wird die Datei in Unity-Catalog-verwalteten Speicher kopiert und `FILE EXTERNAL` → `FILE MANAGED` konvertiert.
- **`if_file_exists_mode`**: optionaler `STRING`, der das Verhalten steuert, wenn die Zieldatei existiert (nur mit `destination`-Argument). Case-insensitiv:
  - `'error'`: löst einen Fehler aus (Default)
  - `'overwrite'`: überschreibt die vorhandene Datei
  - `'skip'`: überspringt das Kopieren, gibt eine Referenz auf die vorhandene Datei zurück

## Rückgabe

Ein `FILE`-Wert, der auf die kopierte Datei verweist.

## Notes

- Ohne `destination` wird `FILE EXTERNAL` zu `FILE MANAGED` konvertiert.
- Standardmäßig Fehler, wenn die Zieldatei existiert, sofern `if_file_exists_mode` nicht anders gesetzt ist.
- Fehler, wenn die Quelldatei nicht existiert; `try_copy_file` gibt stattdessen `NULL` zurück.

**Häufige Fehlerklassen:** `COPY_FILE_ERROR.FILE_NOT_EXISTS`, `COPY_FILE_ERROR.FILE_ALREADY_EXISTS`, `COPY_FILE_AUTHORIZATION_ERROR.READ_UNAUTHORIZED`, `COPY_FILE_AUTHORIZATION_ERROR.WRITE_UNAUTHORIZED`.

## Beispiele

```sql
-- Zwischen Volumes kopieren
SELECT copy_file(
  to_file('/Volumes/source/data/input.csv'),
  destination => '/Volumes/target/data/output.csv');

-- Dynamische Dateinamen, vorhandene überspringen
SELECT copy_file(
  source_file,
  destination => '/Volumes/my_catalog/my_schema/my_volume/processed/' || file_name,
  if_file_exists_mode => 'skip')
FROM staging_files;

-- Vorhandenes Ziel überschreiben
SELECT copy_file(
  to_file('/Volumes/source/reports/report.pdf'),
  destination => '/Volumes/archive/reports/report.pdf',
  if_file_exists_mode => 'overwrite');

-- Fehler, wenn Quelle fehlt
SELECT copy_file(deleted_file, destination => '/Volumes/archive/reports/report.pdf');
-- Error: COPY_FILE_ERROR.FILE_NOT_EXISTS
```

## Verwandte Funktionen

- `to_file` / `try_to_file` function
- `create_file` function
- `try_copy_file` function
- `list_files` function
- `read_files` table-valued function
- `FILE` type
