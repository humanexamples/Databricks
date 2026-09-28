# Built-in SQL Functions — Übersicht

Je eine Datei pro Funktion, thematisch in Unterordnern. Quelle jeweils `docs.databricks.com/aws/en/sql/language-manual/functions/<name>` (in der jeweiligen Datei verlinkt).

## 01 Cast und Typkonvertierung

- [`cast`](01%20Cast%20und%20Typkonvertierung/cast.md) — Wert in Zieldatentyp casten
- [`::` (coloncolonsign)](01%20Cast%20und%20Typkonvertierung/coloncolonsign.md) — Cast-Operator (Synonym für `cast`)
- [`?::` (questiondoublecolonsign)](01%20Cast%20und%20Typkonvertierung/questiondoublecolonsign.md) — fehlertoleranter Cast (Synonym für `try_cast`, DBR 15.3+)
- [`string`](01%20Cast%20und%20Typkonvertierung/string.md) — Wert in `STRING`
- [`date`](01%20Cast%20und%20Typkonvertierung/date.md) — Wert in `DATE`
- [`timestamp`](01%20Cast%20und%20Typkonvertierung/timestamp.md) — Wert in `TIMESTAMP`
- [`typeof`](01%20Cast%20und%20Typkonvertierung/typeof.md) — Datentyp als DDL-String

## 02 Datum und Zeit

- [`to_date`](02%20Datum%20und%20Zeit/to_date.md) — String → `DATE` (mit Format)
- [`to_timestamp`](02%20Datum%20und%20Zeit/to_timestamp.md) — String → `TIMESTAMP` (mit Format)
- [`to_char`](02%20Datum%20und%20Zeit/to_char.md) — Ausdruck formatiert → `STRING` (DBR 11.3 LTS+)
- [`unix_timestamp`](02%20Datum%20und%20Zeit/unix_timestamp.md) — UNIX-Zeitstempel
- [`trunc`](02%20Datum%20und%20Zeit/trunc.md) — Datum auf Einheit kürzen

## 03 NULL-Behandlung

- [`coalesce`](03%20NULL-Behandlung/coalesce.md) — erstes nicht-`NULL`-Argument
- [`isnull`](03%20NULL-Behandlung/isnull.md) — prüft auf `NULL`
- [`isnotnull`](03%20NULL-Behandlung/isnotnull.md) — prüft auf nicht-`NULL`

## 04 String

- [`concat`](04%20String/concat.md) · [`concat_ws`](04%20String/concat_ws.md) · [`upper`](04%20String/upper.md) · [`trim`](04%20String/trim.md)
- [`substr`](04%20String/substr.md) · [`substring`](04%20String/substring.md) · [`substring_index`](04%20String/substring_index.md)
- [`split`](04%20String/split.md) — Regex-Split → Array
- [`unbase64`](04%20String/unbase64.md) — Base64 dekodieren → `BINARY`

## 05 Array

- [`slice`](05%20Array/slice.md) — Teilausschnitt eines Arrays

## 06 JSON, CSV und VARIANT

- [`:` (colonsign)](06%20JSON,%20CSV%20und%20VARIANT/colonsign.md) — JSON-Path-Extraktion
- [`parse_json`](06%20JSON,%20CSV%20und%20VARIANT/parse_json.md) — JSON-String → `VARIANT` (DBR 15.3+)
- [`from_json`](06%20JSON,%20CSV%20und%20VARIANT/from_json.md) · [`from_csv`](06%20JSON,%20CSV%20und%20VARIANT/from_csv.md) — String → Struct/Variant
- [`schema_of_json`](06%20JSON,%20CSV%20und%20VARIANT/schema_of_json.md) · [`schema_of_csv`](06%20JSON,%20CSV%20und%20VARIANT/schema_of_csv.md) · [`schema_of_variant`](06%20JSON,%20CSV%20und%20VARIANT/schema_of_variant.md)
- [`schema_of_json_agg`](06%20JSON,%20CSV%20und%20VARIANT/schema_of_json_agg.md) (DBR 13.2+) · [`schema_of_variant_agg`](06%20JSON,%20CSV%20und%20VARIANT/schema_of_variant_agg.md) (DBR 15.3+) — kombiniertes Schema einer Gruppe

## 07 Datei-Funktionen

- [`copy_file`](07%20Datei-Funktionen/copy_file.md) — Datei kopieren (DBR 18 LTS+, Beta)
- [`read_files`](07%20Datei-Funktionen/read_files/00%20%C3%9Cbersicht.md) — tabellenwertige Funktion zum Lesen von Dateien (DBR 13.3 LTS+; Batch & `STREAM`)
