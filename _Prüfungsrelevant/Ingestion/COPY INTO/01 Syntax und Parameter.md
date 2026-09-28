[← Übersicht](00%20Uebersicht.md)

# COPY INTO – Syntax und Parameter

```sql
COPY INTO target_table [ BY POSITION | ( col_name [ , <col_name> ... ] ) ]
  FROM { source_clause |
         ( SELECT expression_list FROM source_clause ) }
  FILEFORMAT = data_source
  [ VALIDATE [ ALL | num_rows ROWS ] ]
  [ FILES = ( file_name [, ...] ) | PATTERN = glob_pattern ]
  [ FORMAT_OPTIONS ( { data_source_reader_option = value } [, ...] ) ]
  [ COPY_OPTIONS ( { copy_option = value } [, ...] ) ]

source_clause
  source [ WITH ( [ CREDENTIAL { credential_name |
                                 (temporary_credential_options) } ]
                  [ ENCRYPTION (encryption_options) ] ) ]
```

---

## target_table

Die Zieltabelle muss eine **bestehende Delta-Tabelle** sein. Zeitreise-Angaben (`VERSION AS OF`) oder Options-Angaben sind im Namen nicht erlaubt.

```sql
COPY INTO main.bronze.events            -- dreiteiliger Name
FROM '/Volumes/main/raw/landing/events'
FILEFORMAT = JSON;
```

Das Ziel kann auch ein Pfad sein. Dann regelt Unity Catalog den Schreibzugriff. Du brauchst `WRITE FILES` auf der External Location oder auf einer Storage Credential.

```sql
COPY INTO delta.`s3://my-bucket/tables/events` WITH (CREDENTIAL my_write_credential)
FROM 's3://my-bucket/raw/events'
FILEFORMAT = JSON;
```

Der Tabellenname darf auch über `IDENTIFIER()` kommen, zum Beispiel aus einer Variable:

```sql
DECLARE OR REPLACE VARIABLE tbl STRING DEFAULT 'main.bronze.events';

COPY INTO IDENTIFIER(tbl)
FROM '/Volumes/main/raw/landing/events'
FILEFORMAT = JSON;
```

---

## BY POSITION und Spaltenliste (ab Databricks Runtime 15.2)

Diese Varianten gibt es **nur für CSV ohne Kopfzeile**. `FILEFORMAT = CSV` ist Pflicht. `headers` muss `false` sein, was ohnehin der Standard ist. Die Typen werden automatisch umgewandelt.

**Variante 1 – `BY POSITION`:** Die 1. Quellspalte geht in die 1. Zielspalte, die 2. in die 2. und so weiter. Spaltennamen spielen keine Rolle.

```sql
-- Ziel: id BIGINT, name STRING, amount DOUBLE
-- Datei: 1,Anna,9.5
COPY INTO main.bronze.payments BY POSITION
FROM '/Volumes/main/raw/landing/payments'
FILEFORMAT = CSV;
```

- `IDENTITY`- und `GENERATED`-Spalten der Zieltabelle werden übersprungen.
- Die Zahl der Quellspalten muss zur Zahl der übrigen Zielspalten passen. Sonst gibt es einen Fehler.

**Variante 2 – Spaltenliste:** Du gibst die Zielspalten in der Reihenfolge der Datei an.

```sql
-- Datei: Anna,9.5   (nur 2 Spalten)
COPY INTO main.bronze.payments (name, amount)
FROM '/Volumes/main/raw/landing/payments'
FILEFORMAT = CSV;
-- id wird mit dem Default-Wert gefüllt, falls es einen gibt, sonst mit NULL
```

- `IDENTITY`- und `GENERATED`-Spalten dürfen nicht in der Liste stehen.
- Keine Spalte darf doppelt vorkommen.
- Die Anzahl muss genau zur Datei passen.
- Nicht genannte Spalten bekommen ihren Default-Wert oder `NULL`. Ist so eine Spalte `NOT NULL`, gibt es einen Fehler.

---

## source

Der Quellpfad als URI. Alle Dateien dort müssen das Format aus `FILEFORMAT` haben.

```sql
FROM '/Volumes/main/raw/landing/orders'         -- Volume (empfohlen)
FROM 's3://landing-bucket/raw-data/orders'      -- Cloud-URL (External Location)
FROM 's3://my-bucket/'                          -- Root-Pfad: Schrägstrich am Ende nötig
```

Der Zugriff auf die Quelle kann so erfolgen:

- über eine External Location, auf die du `READ FILES` hast. Dann sind keine Credentials nötig.
- über eine benannte Storage Credential mit `READ FILES`: `WITH (CREDENTIAL name)`
- über temporäre Credentials direkt im Befehl

Details stehen in [06 Datenzugriff](06%20Datenzugriff/).

---

## SELECT expression_list

Mit einem `SELECT` kannst du die Daten vor dem Laden umformen. Erlaubt ist alles, was in `SELECT` geht, auch Fensterfunktionen. Aggregationen gehen nur global, `GROUP BY` ist nicht möglich.

```sql
COPY INTO my_delta_table
FROM (SELECT to_date(dt) dt, event AS measurement, quantity::double
      FROM 's3://my-bucket/avroData')
FILEFORMAT = AVRO;
```

Typische Nutzung: Konstanten oder Metadaten ergänzen.

```sql
COPY INTO main.bronze.orders
FROM (SELECT *,
             _metadata.file_name AS src_file,
             current_timestamp() AS ingest_ts
      FROM '/Volumes/main/raw/landing/orders')
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');
```

---

## FILEFORMAT

Einer von `CSV`, `JSON`, `AVRO`, `ORC`, `PARQUET`, `TEXT`, `BINARYFILE`. Außerdem `XML` und `EXCEL`, siehe [04 Dateiformate](04%20Dateiformate%20und%20Format-Optionen.md).

---

## VALIDATE (ab Databricks Runtime 10.4 LTS)

Die Daten werden geprüft, aber **nicht geschrieben**. Geprüft wird:

- ob die Daten geparst werden können,
- ob das Schema passt oder weiterentwickelt werden müsste,
- ob alle NOT-NULL- und CHECK-Constraints erfüllt sind.

```sql
-- Alles prüfen (Standard)
COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
VALIDATE ALL
FORMAT_OPTIONS ('header' = 'true');

-- Nur 15 Zeilen prüfen; bei weniger als 50 Zeilen kommt eine Vorschau zurück
COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
VALIDATE 15 ROWS
FORMAT_OPTIONS ('header' = 'true');
```

`VALIDATE 0 ROWS` oder eine negative Zahl führt zu `COPY_INTO_SYNTAX_ERROR.VALIDATE_INVALID_ROWS`, denn `ROWS` braucht eine positive ganze Zahl.

---

## FILES und PATTERN

Mit beiden wählst du Dateien aus. Du kannst **nicht beide** zusammen verwenden.

**`FILES`:** eine Liste von Dateinamen, **höchstens 1000**.

```sql
COPY INTO my_json_data
FROM 's3://my-bucket/jsonData'
FILEFORMAT = JSON
FILES = ('f1.json', 'f2.json', 'f3.json', 'f4.json', 'f5.json');
```

**`PATTERN`:** ein Glob-Muster relativ zum Quellordner.

```sql
COPY INTO target_table
FROM (SELECT key, index, textData, 'constant_value'
      FROM 's3://bucket/base/path')
FILEFORMAT = CSV
PATTERN = 'folder1/file_[a-g].csv'
FORMAT_OPTIONS ('header' = 'true');
```

Die Glob-Zeichen:

- `?` passt auf genau ein Zeichen. `file_?.csv` findet `file_1.csv`, aber nicht `file_10.csv`.
- `*` passt auf beliebig viele Zeichen. `*.csv` findet alle CSV-Dateien.
- `[abc]` passt auf ein Zeichen aus der Menge. `file_[abc].csv` findet `file_a.csv`.
- `[a-z]` passt auf ein Zeichen aus dem Bereich. `file_[a-g].csv`
- `[^a]` passt auf ein Zeichen, das **nicht** in der Menge ist. Das `^` muss direkt nach `[` stehen.
- `{ab,cd}` passt auf einen der Texte. `{2025,2026}/*.csv`
- `{ab,c{de,fh}}` darf verschachtelt sein und passt auf `ab`, `cde` oder `cfh`.

Die Reader-Option `pathGlobFilter` entspricht `PATTERN` in `COPY INTO`.

---

## FORMAT_OPTIONS

Optionen für den Spark-Reader des gewählten Formats, zum Beispiel `header`, `delimiter` oder `multiLine`. Siehe [04 Dateiformate](04%20Dateiformate%20und%20Format-Optionen.md).

```sql
FORMAT_OPTIONS ('header' = 'true', 'delimiter' = '|', 'inferSchema' = 'true')
```

---

## COPY_OPTIONS

Es gibt genau zwei Optionen:

**Die Copy-Option `force`** (Typ Boolean, Standard `false`): Bei `'force' = 'true'` ist die **Idempotenz abgeschaltet**. Dann werden alle Dateien geladen, auch solche, die schon geladen wurden. Das heißt, sie werden **zusätzlich** angehängt. Überschrieben wird trotzdem nichts. Siehe [02 Idempotenz](02%20Idempotenz,%20File%20Tracking%20und%20force.md).

```sql
COPY_OPTIONS ('force' = 'true')    -- Idempotenz aus: auch bereits geladene Dateien laden
COPY_OPTIONS ('force' = 'false')   -- Standard: bereits geladene Dateien überspringen
```

**Die Copy-Option `mergeSchema`** (Typ Boolean, Standard `false`): Bei `true` darf sich das Schema der Zieltabelle an die Daten anpassen. Siehe [03 Zieltabelle und Schema](03%20Zieltabelle%20und%20Schema.md).

```sql
COPY_OPTIONS ('mergeSchema' = 'true')
```

Beides zusammen:

```sql
COPY_OPTIONS ('force' = 'true', 'mergeSchema' = 'true')
```
