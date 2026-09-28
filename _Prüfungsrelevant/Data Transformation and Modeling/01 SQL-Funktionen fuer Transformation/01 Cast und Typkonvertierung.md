# Cast und Typkonvertierung

## `cast` — Wert in Zieldatentyp casten

**Syntax:** `cast(sourceExpr AS targetType)`

- Fehlerklassen: `CAST_INVALID_INPUT`, `CAST_OVERFLOW`, `DATATYPE_MISMATCH`, `NUMERIC_VALUE_OUT_OF_RANGE`, `UNSUPPORTED_DATATYPE`. `try_cast` gibt bei ungültiger Eingabe/Overflow `NULL` statt Fehler.
- `STRUCT`/`MAP` → `VARIANT` **nicht direkt** möglich (Feldreihenfolge) — stattdessen `to_variant_object` (MAP-Keys müssen `STRING` sein).
- `VARIANT` bewahrt numerische Präzision (`DECIMAL` bis 38 Stellen); Integer werden zu `BIGINT`.
- `BOOLEAN` aus String: `'T'/'TRUE'/'Y'/'YES'/'1'` → `true`, `'F'/'FALSE'/'N'/'NO'/'0'` → `false`. Aus Zahl: `0` → `false`, sonst `true`.
- Integer-Casts trunkieren, Decimal-Casts runden.

```sql
-- Numerisch
SELECT cast(5.6 AS INT);                                -- 5
SELECT cast(5.6 AS DECIMAL(2, 0));                       -- 6
SELECT cast(-5.6 AS INT);                                -- -5
SELECT cast(-5.6 AS DECIMAL(2, 0));                      -- -6
SELECT cast(128 AS TINYINT);                             -- Error: CAST_OVERFLOW
SELECT cast('123' AS INT);                               -- 123
SELECT cast('123.0' AS INT);                             -- Error: CAST_INVALID_INPUT
SELECT cast(TRUE AS INT);                                -- 1
SELECT cast('15'::VARIANT AS INT);                       -- 15

-- STRING
SELECT cast(-3Y AS STRING);                              -- -3
SELECT cast(5::DECIMAL(10, 5) AS STRING);                -- 5.00000
SELECT cast(1e7 AS STRING);                              -- 1.0E7
SELECT cast(1e-3 AS STRING);                             -- 0.001
SELECT cast(DATE'2024-01-05'::VARIANT AS STRING);        -- 2024-01-05
SELECT cast(array('hello', NULL, 'world') AS STRING);    -- [hello, null, world]
SELECT cast(map('hello', 1, 'world', null) AS STRING);   -- {hello -> 1, world -> null}

-- DATE / TIMESTAMP
SELECT cast('1900-02-30' AS DATE);                       -- Error: CAST_INVALID_INPUT
SELECT cast(TIMESTAMP'1900-10-01 12:13:14' AS DATE);     -- 1900-10-01
SELECT cast('1900' AS TIMESTAMP);                        -- 1900-01-01 00:00:00
SELECT cast(1e20 AS TIMESTAMP);                          -- Error: CAST_OVERFLOW
SELECT CAST('25:00:00' AS TIME);                         -- Error: CAST_INVALID_INPUT

-- BOOLEAN / BINARY
SELECT cast('T' AS BOOLEAN);                             -- true
SELECT cast('on' AS BOOLEAN);                            -- Error: CAST_INVALID_INPUT
SELECT hex(cast('Spark SQL' AS BINARY));                 -- 537061726B2053514C

-- ARRAY / MAP / STRUCT / VARIANT
SELECT cast(array('t', 'f', NULL) AS ARRAY<BOOLEAN>);    -- [true, false, NULL]
SELECT cast(array('t', 'f', 'o') AS ARRAY<BOOLEAN>);     -- Error: CAST_INVALID_INPUT
SELECT cast(map('10', 't', '15', 'f', '20', NULL) AS MAP<INT, BOOLEAN>);
  -- {10 -> true, 15 -> false, 20 -> null}
SELECT CAST(parse_json('{"cars": 12, "bicycles": 5 }') AS MAP<STRING, INTEGER>);
  -- {bicycles -> 5, cars -> 12}
SELECT cast(5.1000 AS VARIANT);                          -- 5.1
SELECT schema_of_variant(cast(5 AS VARIANT));            -- BIGINT
```

## `::` — Cast-Operator

**Syntax:** `expr :: type` — Synonym für `cast`, wirft dieselben Fehlerklassen.

```sql
SELECT '20'::INTEGER;              -- 20
SELECT typeof(NULL::STRING);       -- string
SELECT 'abc'::INT;                 -- Error: CAST_INVALID_INPUT
```

## `?::` — fehlertoleranter Cast-Operator

**Gilt für:** DBR 15.3+. **Syntax:** `expr ?:: type` — Synonym für `try_cast`, gibt bei nicht castbarer Eingabe `NULL` statt Fehler zurück.

```sql
SELECT '20'?::INTEGER;             -- 20
SELECT 'twenty'?::INTEGER;         -- NULL
SELECT typeof(NULL?::STRING);      -- string
```

## Kurzform-Konvertierungsfunktionen

Synonyme für `cast(expr AS <Typ>)`. Bei `string(expr)` gilt: ist `expr` bereits `STRING`, übernimmt das Ergebnis dessen Collation, sonst die Default-Collation.

```sql
SELECT string(5);                     -- 5
SELECT date('2021-03-21');            -- 2021-03-21
SELECT timestamp('2020-04-30 12:25:13.45');  -- 2020-04-30 12:25:13.45
SELECT timestamp(date'2020-04-30');   -- 2020-04-30 00:00:00
SELECT timestamp(123);                -- 1969-12-31 16:02:03
```

## `typeof` — Datentyp als DDL-String

**Syntax:** `typeof(expr)`

> Für den Typ eines konkreten `VARIANT`-**Werts** `schema_of_variant` verwenden (`typeof` liefert für jede `VARIANT`-Spalte immer nur `variant`, egal was gespeichert ist); für kombinierte Schemas mehrerer `VARIANT`-Werte `schema_of_variant_agg`.

```sql
SELECT typeof(1);                        -- int
SELECT typeof(array(1));                 -- array<int>
SELECT typeof(123.4::VARIANT);           -- variant
SELECT schema_of_variant(123.4::VARIANT);-- DECIMAL(4,1)
SELECT typeof('hello' COLLATE UTF8_LCASE); -- string collate UTF8_LCASE
```

**Stand:** 2026-09-14.
