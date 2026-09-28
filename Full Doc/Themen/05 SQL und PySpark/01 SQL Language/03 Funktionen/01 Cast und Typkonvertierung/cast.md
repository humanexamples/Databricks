# `cast` — Wert in Zieldatentyp casten

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/cast>
> Gilt für: Databricks SQL, Databricks Runtime.

Castet den Wert `sourceExpr` in den Zieldatentyp `targetType`.

## Syntax

```
cast(sourceExpr AS targetType)
```

## Argumente

- **`sourceExpr`**: ein beliebiger castbarer Ausdruck.
- **`targetType`**: der Datentyp des Ergebnisses.

## Rückgabe

Ergebnis vom Typ `targetType`. Vollständige Liste gültiger Quell-/Ziel-Kombinationen und Regeln: *SQL data type rules* (`/aws/en/sql/language-manual/sql-ref-datatype-rules`).

- **Fehlerklassen:** `CAST_INVALID_INPUT`, `CAST_OVERFLOW`, `DATATYPE_MISMATCH`, `NUMERIC_VALUE_OUT_OF_RANGE`, `UNSUPPORTED_DATATYPE`. Mit [`try_cast`](#) werden ungültige Eingaben und Overflow zu `NULL`.
- **`STRUCT`/`MAP` → `VARIANT`** wird nicht direkt unterstützt (Feldreihenfolge nicht erhaltbar) — stattdessen `to_variant_object`. `MAP`-Keys müssen `STRING` sein. `VARIANT` bewahrt numerische Präzision (`DECIMAL` ≤ 38); integrale Zahlen → `BIGINT`.
- `BOOLEAN` aus String: `'T'`/`'TRUE'`/`'Y'`/`'YES'`/`'1'` → `true`; `'F'`/`'FALSE'`/`'N'`/`'NO'`/`'0'` → `false`. Aus Zahl: `0` → `false`, sonst `true`. Integer-Casts schneiden ab, Decimal-Casts runden.

## Beispiele

```sql
-- numeric
> SELECT cast(5.6 AS INT);                                5
> SELECT cast(5.6 AS DECIMAL(2, 0));                      6
> SELECT cast(-5.6 AS INT);                               -5
> SELECT cast(-5.6 AS DECIMAL(2, 0));                     -6
> SELECT cast(128 AS TINYINT);                            Error: CAST_OVERFLOW
> SELECT cast(128 AS DECIMAL(2, 0));                      Error: CAST_OVERFLOW
> SELECT cast('123' AS INT);                              123
> SELECT cast('123.0' AS INT);                            Error: CAST_INVALID_INPUT
> SELECT cast(TIMESTAMP'1970-01-01 00:00:01' AS LONG);    1
> SELECT cast(TIMESTAMP'1970-01-01 00:00:00.000001' AS DOUBLE);  1.0E-6
> SELECT cast(INTERVAL '1-2' YEAR TO MONTH AS INTEGER);   14
> SELECT cast(INTERVAL '1:30.5' MINUTE TO SECOND AS DECIMAL(5, 2));  90.50
> SELECT cast(TRUE AS INT);                               1
> SELECT cast('15'::VARIANT AS INT);                      15

-- STRING
> SELECT cast(-3Y AS STRING);                             -3
> SELECT cast(5::DECIMAL(10, 5) AS STRING);               5.00000
> SELECT cast(12345678e-4 AS STRING);                     1234.5678
> SELECT cast(1e7 as string);                             1.0E7
> SELECT cast(1e6 as string);                             1000000.0
> SELECT cast(1e-4 as string);                            1.0E-4
> SELECT cast(1e-3 as string);                            0.001
> SELECT cast(DATE'-0044-03-15' AS STRING);               -0044-03-15
> SELECT cast(DATE'100000-12-31' AS STRING);              +100000-12-31
> SELECT cast(TIMESTAMP_NTZ'2023-01-01' AS STRING);       2023-01-01 00:00:00
> SELECT cast(INTERVAL -'13-02' YEAR TO MONTH AS STRING); INTERVAL '-13-2' YEAR TO MONTH
> SELECT cast(x'33800033' AS STRING);                     3�3
> SELECT cast(array('hello', NULL, 'world') AS STRING);   [hello, null, world]
> SELECT cast(map('hello', 1, 'world', null) AS STRING);  {hello -> 1, world -> null}
> SELECT cast(named_struct('a', 5, 'b', 6, 'c', NULL) AS STRING);  {5, 6, null}
> SELECT cast(DATE'2024-01-05'::VARIANT AS STRING);       2024-01-05
> SELECT cast(5 AS STRING) COLLATE UNICODE;               5

-- DATE / TIMESTAMP / TIMESTAMP_NTZ / TIME
> SELECT cast('1900-02-30' AS DATE);                      Error: CAST_INVALID_INPUT
> SELECT cast(TIMESTAMP'1900-10-01 12:13:14' AS DATE);    1900-10-01
> SELECT cast('1900' AS TIMESTAMP);                       1900-01-01 00:00:00
> SELECT cast(0.0 AS TIMESTAMP);                          1970-01-01 00:00:00   -- nach SET TIME ZONE '+00:00'
> SELECT cast(1e20 AS TIMESTAMP);                         Error: CAST_OVERFLOW
> SELECT cast(TIMESTAMP_NTZ'2023-01-01 02:03:04.567' as TIMESTAMP);  2023-01-01 02:03:04.567
> SELECT CAST('25:00:00' AS TIME);                        Error: CAST_INVALID_INPUT
> SELECT CAST(TIME'09:15:30.123456' AS TIME(3));          09:15:30.123

-- BOOLEAN / BINARY
> SELECT cast('T' AS BOOLEAN);                            true
> SELECT cast('on' AS BOOLEAN);                           Error: CAST_INVALID_INPUT
> SELECT cast(0.1 AS BOOLEAN);                            true
> SELECT cast('NaN'::FLOAT AS BOOLEAN);                   true
> SELECT hex(cast('Spark SQL' AS BINARY));                537061726B2053514C
> SELECT hex(cast('Oдesa'::VARIANT AS BINARY));           4FD0B4657361

-- ARRAY / MAP / STRUCT / VARIANT
> SELECT cast(array('t', 'f', NULL) AS ARRAY<BOOLEAN>);   [true, false, NULL]
> SELECT cast(array('t', 'f', 'o') AS ARRAY<BOOLEAN>);    Error: CAST_INVALID_INPUT
> SELECT cast(map('10', 't', '15', 'f', '20', NULL) AS MAP<INT, BOOLEAN>);  {10 -> true, 15 -> false, 20 -> null}
> SELECT CAST(parse_json('{"cars": 12, "bicycles": 5 }') AS MAP<STRING, INTEGER>);  {bicycles -> 5, cars -> 12}
> SELECT cast(named_struct('a', 't', 'b', '1900-01-01') AS STRUCT<b:BOOLEAN, c:DATE NOT NULL COMMENT 'Hello'>);  {"b":true,"c":1900-01-01}
> SELECT CAST(parse_json('{"name": "jason", "age": 25 }') AS STRUCT<id: BIGINT, name: STRING>);  {"id":null,"name":"jason"}
> SELECT cast(5.1000 AS VARIANT);                         5.1
> SELECT schema_of_variant(cast(5 AS VARIANT));           BIGINT
```

## Verwandte Funktionen

- [`::` (colon colon sign) operator](coloncolonsign.md)
- [`?::` (question double colon sign) operator](questiondoublecolonsign.md)
- `try_cast` function
