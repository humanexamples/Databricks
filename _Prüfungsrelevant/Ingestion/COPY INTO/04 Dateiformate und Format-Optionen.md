[← Übersicht](00%20Uebersicht.md)

# Dateiformate und Format-Optionen

## Unterstützte Formate

- In der SQL-Referenz: `CSV`, `JSON`, `AVRO`, `ORC`, `PARQUET`, `TEXT`, `BINARYFILE`
- Außerdem `XML` (ab Databricks Runtime 14.3) und `EXCEL`

**Delta-Tabellen als Quelle sind nicht erlaubt.** Der Grund: Nach einem `OPTIMIZE` könnten Daten doppelt geladen werden. Der Fehler heißt `COPY_INTO_SOURCE_FILE_FORMAT_NOT_SUPPORTED`.

---

## Ein Beispiel pro Format

**CSV mit Kopfzeile**

```sql
COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'delimiter' = ',', 'inferSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');
```

**JSON (mehrzeilig)**

```sql
COPY INTO main.bronze.bookings
FROM '/Volumes/main/raw/landing/bookings'
FILEFORMAT = JSON
FORMAT_OPTIONS ('multiLine' = 'true');
```

**Avro mit Umformung**

```sql
COPY INTO my_delta_table
FROM (SELECT to_date(dt) dt, event AS measurement, quantity::double
      FROM 's3://my-bucket/avroData')
FILEFORMAT = AVRO;
```

**Parquet**

```sql
COPY INTO landing_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data'
FILEFORMAT = PARQUET;
```

**XML** – `rowTag` gibt an, welches Element eine Zeile ist.

```sql
CREATE TABLE IF NOT EXISTS reviews;

COPY INTO reviews
FROM '/Volumes/<catalog>/<schema>/<volume>/reviews.xml'
FILEFORMAT = XML
FORMAT_OPTIONS ('mergeSchema' = 'true', 'rowTag' = 'review')
COPY_OPTIONS ('mergeSchema' = 'true');
```

**Excel**

```sql
CREATE TABLE IF NOT EXISTS excel_demo_table;

COPY INTO excel_demo_table
FROM '<path to excel directory or file>'
FILEFORMAT = EXCEL
FORMAT_OPTIONS ('mergeSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');
```

Excel-Optionen sind unter anderem `headerRows` (Standard `0`) und `dataAddress`, zum Beispiel `'Sheet1!A2:D10'`.

**Binärdateien (z. B. PDFs)**

```sql
COPY INTO main.bronze.pdf_docs
FROM '/Volumes/main/raw/landing/docs'
FILEFORMAT = BINARYFILE
PATTERN = '*.pdf';
```

---

## Alles in eine VARIANT-Spalte laden

Die ganze Zeile landet als eine `VARIANT`-Spalte. Das ist robust gegen Schemaänderungen. VARIANT-Ingestion gibt es für JSON ab Databricks Runtime 15.3 und für XML und CSV ab 16.4. Für diesen Fall empfiehlt Databricks Auto Loader statt `COPY INTO`, wo möglich.

```sql
CREATE TABLE table_name (variant_column VARIANT);

COPY INTO table_name
FROM '/Volumes/catalog_name/schema_name/volume_name/path'
FILEFORMAT = JSON
FILES = ('file-name')
FORMAT_OPTIONS ('singleVariantColumn' = 'variant_column');
```

---

## Allgemeine Optionen (alle Formate)

Diese Optionen gehen in `FORMAT_OPTIONS`.

**`ignoreCorruptFiles`** (Standard `false`): Beschädigte Dateien werden übersprungen. Ab Databricks Runtime 11.3 LTS.

```sql
FORMAT_OPTIONS ('ignoreCorruptFiles' = 'true')
```

**`ignoreMissingFiles`** (bei `COPY INTO` Standard `true`): Dateien, die während des Laufs verschwinden, werden ignoriert.

**`modifiedAfter` / `modifiedBefore`**: Nur Dateien, die nach bzw. vor diesem Zeitpunkt geändert wurden.

```sql
FORMAT_OPTIONS ('modifiedAfter' = '2026-09-01T00:00:00')
```

**`pathGlobFilter`**: ein Glob-Filter auf Dateinamen. In `COPY INTO` entspricht das `PATTERN`.

**`recursiveFileLookup`** (Standard `false`): Bei `true` werden auch Unterordner durchsucht, die nicht nach dem Muster `key=value` benannt sind.

```sql
FORMAT_OPTIONS ('recursiveFileLookup' = 'true')
```

**`ignoredPathSegmentRegex`** (Standard `^[._]`, ab Databricks Runtime 19): Datei- und Ordnernamen, die auf den regulären Ausdruck passen, werden ausgelassen. Standardmäßig sind das Namen, die mit `_` oder `.` beginnen.

---

## Wichtige CSV-Optionen

- `header` (Standard `false`): Die erste Zeile enthält die Spaltennamen.
- `sep` oder `delimiter` (Standard `,`): das Trennzeichen
- `inferSchema` (Standard `false`): Typen ableiten, statt alles als `STRING` zu lesen
- `mergeSchema` (Standard `false`): das Schema über mehrere Dateien zusammenführen
- `multiLine` (Standard `false`): Ein Datensatz darf über mehrere Zeilen gehen.
- `mode` (Standard `PERMISSIVE`): Umgang mit fehlerhaften Zeilen
- `badRecordsPath`: ein Pfad, unter dem Infos zu fehlerhaften Zeilen abgelegt werden
- `nullValue`, `dateFormat` (`yyyy-MM-dd`), `timestampFormat`, `encoding` (`UTF-8`), `quote` (`"`), `escape` (`\`), `skipRows` (`0`)

```sql
COPY INTO main.bronze.pipe_data
FROM '/Volumes/main/raw/landing/pipe'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header'     = 'true',
  'delimiter'  = '|',
  'nullValue'  = 'NA',
  'dateFormat' = 'dd.MM.yyyy',
  'skipRows'   = '1'
);
```

## Wichtige JSON-Optionen

- `multiLine` (Standard `false`): ein JSON-Objekt über mehrere Zeilen
- `mode` (Standard `PERMISSIVE`), `badRecordsPath`
- `allowComments`, `allowSingleQuotes` (Standard `true`), `primitivesAsString`, `inferTimestamp`

```sql
FORMAT_OPTIONS ('multiLine' = 'true', 'allowComments' = 'true')
```

## Wichtige XML-Optionen

- `rowTag`: das Element, das eine Zeile ist. Ohne diese Option geht es nicht.
- `rowValidationXSDPath`: jede Zeile gegen eine XSD prüfen
- `attributePrefix`, `valueTag` (Standard `_VALUE`)

```sql
FORMAT_OPTIONS ('rowTag' = 'review', 'rowValidationXSDPath' = '/Volumes/main/raw/xsd/review.xsd')
```

**Nicht unterstützt in `COPY INTO`:** `rescuedDataColumn` und `columnNameOfCorruptRecord`. Siehe [03 Zieltabelle und Schema](03%20Zieltabelle%20und%20Schema.md).
