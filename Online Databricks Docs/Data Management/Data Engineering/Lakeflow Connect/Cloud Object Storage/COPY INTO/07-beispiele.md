# Gängige Ladeschemata mit COPY INTO

Diese Seite zeigt typische Anwendungsmuster für `COPY INTO` beim Laden von Daten aus Dateiquellen in Delta Lake. Temporäre Zugangsdaten lassen sich mit all diesen Mustern kombinieren. Eine vollständige Referenz aller Optionen bietet die SQL-Sprachreferenz zu `COPY INTO`.

## Zieltabellen erstellen

`COPY INTO` muss immer auf eine bereits bestehende Delta-Tabelle zielen:

```sql
%sql
CREATE TABLE IF NOT EXISTS my_table[(col_1 col_1_type, col_2 col_2_type, ...)][COMMENT <table-description>][TBLPROPERTIES (<table-properties>)];
```

Ab Databricks Runtime 11.3 LTS ist die Angabe des Schemas für Formate mit Schema-Evolution optional.

## JSON-Daten laden

Folgendes Beispiel lädt JSON-Daten aus fünf Dateien in S3 in die Delta-Tabelle `my_json_data`. Die Tabelle muss vorher existieren. Bereits geladene Daten aus einer Datei werden nicht erneut geladen:

```sql
%sql
COPY INTO my_json_data
  FROM 's3://my-bucket/jsonData'
  FILEFORMAT = JSON
  FILES = ('f1.json', 'f2.json', 'f3.json', 'f4.json', 'f5.json')

-- Der zweite Aufruf kopiert keine Daten, da der erste Befehl die Daten bereits geladen hat
COPY INTO my_json_data
  FROM 's3://my-bucket/jsonData'
  FILEFORMAT = JSON
  FILES = ('f1.json', 'f2.json', 'f3.json', 'f4.json', 'f5.json')
```

## Avro-Daten laden

Folgendes Beispiel lädt Avro-Daten aus S3 und verwendet zusätzliche SQL-Ausdrücke im `SELECT`-Statement:

```sql
%sql
COPY INTO my_delta_table
  FROM (SELECT to_date(dt) dt, event as measurement, quantity::double
          FROM 's3://my-bucket/avroData')
  FILEFORMAT = AVRO
```

## CSV-Dateien laden

Folgendes Beispiel lädt CSV-Dateien aus `s3://bucket/base/path/folder1` in eine Delta-Tabelle:

```sql
%sql
COPY INTO target_table
  FROM (SELECT key, index, textData, 'constant_value'
          FROM 's3://bucket/base/path')
  FILEFORMAT = CSV
  PATTERN = 'folder1/file_[a-g].csv'
  FORMAT_OPTIONS('header' = 'true')
```

Beispiel für CSV-Dateien ohne Header: Durch Casting und Umbenennen der Spalten lassen sich die Daten in das gewünschte Schema bringen:

```sql
%sql
COPY INTO target_table
  FROM (SELECT _c0::bigint key, _c1::int index, _c2 textData
        FROM 's3://bucket/base/path')
  FILEFORMAT = CSV
  PATTERN = 'folder1/file_[a-g].csv'
```

## Schema-Inferenz und -Evolution

Allgemeine Syntax:

```sql
%sql
COPY INTO my_table
FROM '/path/to/files'
FILEFORMAT = <format>
FORMAT_OPTIONS ('inferSchema' = 'true', `mergeSchema` = `true`)
COPY_OPTIONS ('mergeSchema' = 'true');
```

Folgende `FORMAT_OPTIONS` stehen zur automatischen Schema-Inferenz zur Verfügung:

- `inferSchema`: Ob die Datentypen der geparsten Datensätze inferiert werden oder alle Spalten als `StringType` angenommen werden.
- `mergeSchema`: Ob das Schema über mehrere Quelldateien hinweg inferiert und zusammengeführt wird.

Haben die Quelldateien dasselbe Schema, empfiehlt Databricks, die Standardeinstellung für `mergeSchema` in `FORMAT_OPTIONS` (`false`) beizubehalten.

Folgende `COPY_OPTIONS` stehen zur Evolution des Zielschemas zur Verfügung:

- `mergeSchema`: Ob das Schema der Ziel-Delta-Tabelle basierend auf dem Eingabeschema weiterentwickelt wird.

Sind Eingabe- und Zielschema identisch, kann `mergeSchema` in `COPY_OPTIONS` auf `false` gesetzt werden.

### CSV-Schema inferieren und weiterentwickeln

Folgendes Beispiel erzeugt eine schemalose Delta-Tabelle `my_pipe_data` und lädt Pipe-getrennte CSV-Daten mit Header. `mergeSchema` ist in `FORMAT_OPTIONS` auf `true` gesetzt, da die Eingabedateien unterschiedliche Header oder Trennzeichen aufweisen können:

```sql
%sql
CREATE TABLE IF NOT EXISTS my_pipe_data;

COPY INTO my_pipe_data
  FROM 's3://my-bucket/pipeData'
  FILEFORMAT = CSV
  FORMAT_OPTIONS ('mergeSchema' = 'true',
                  'delimiter' = '|',
                  'header' = 'true')
  COPY_OPTIONS ('mergeSchema' = 'true');
```

## Beschädigte Dateien ignorieren

Können Quelldateien wegen Beschädigung nicht gelesen werden, lassen sie sich überspringen, indem `ignoreCorruptFiles` in `FORMAT_OPTIONS` auf `true` gesetzt wird. Das Ergebnis von `COPY INTO` gibt in der Spalte `num_skipped_corrupt_files` an, wie viele Dateien wegen Beschädigung übersprungen wurden. Diese Kennzahl erscheint nach `DESCRIBE HISTORY` auf der Delta-Tabelle auch in der Spalte `operationMetrics` unter `numSkippedCorruptFiles`. Beschädigte Dateien werden von `COPY INTO` nicht nachverfolgt und können daher in einem späteren Lauf erneut geladen werden, sobald die Beschädigung behoben ist. Mit dem `VALIDATE`-Modus lässt sich prüfen, welche Dateien beschädigt sind:

```sql
%sql
COPY INTO my_table
FROM '/path/to/files'
FILEFORMAT = <format>
[VALIDATE ALL]
FORMAT_OPTIONS ('ignoreCorruptFiles' = 'true')
```

`ignoreCorruptFiles` ist ab Databricks Runtime 11.3 LTS verfügbar.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/examples  
**Stand:** 2026-08-07
