# Datum- und Zeit-Funktionen

## `to_date` — String in `DATE` konvertieren

**Syntax:** `to_date(expr [, fmt])`

- Ohne `fmt`: verhält sich wie `cast(expr AS DATE)`, Default-Format `yyyy-MM-dd`.
- `fmt`: Format-String gemäß Datetime-Patterns.
- Fehlerklassen: `CAST_INVALID_INPUT` (kein Format, nicht parsebar), `CANNOT_PARSE_TIMESTAMP` (Format angegeben, passt nicht).
- Für `NULL` statt Fehler: `try_cast(expr AS DATE)` oder ANSI-Modus (`spark.sql.ansi.enabled`) deaktivieren.

```sql
SELECT to_date('2009-07-30 04:17:52');          -- 2009-07-30 (Default-Format)
SELECT to_date('2016-12-31', 'yyyy-MM-dd');     -- 2016-12-31 (explizites Format)
SELECT to_date('31/12/2016', 'dd/MM/yyyy');     -- 2016-12-31 (Nicht-Default-Format)
SELECT to_date('not-a-date');                   -- Error: CAST_INVALID_INPUT
SELECT to_date('31/12/2016');                   -- Error: CAST_INVALID_INPUT (passt nicht zu yyyy-MM-dd)
SELECT try_cast('not-a-date' AS DATE);          -- NULL (fehlertolerant)
```

## `to_timestamp` — String in `TIMESTAMP` konvertieren

**Syntax:** `to_timestamp(expr [, fmt])` — analog zu `to_date`, ohne `fmt` entspricht es `cast(expr AS TIMESTAMP)`.

- Fehlerklassen: `CAST_INVALID_INPUT`, `CANNOT_PARSE_TIMESTAMP`. Für `NULL` statt Fehler: `try_to_timestamp`.
- Bei `spark.sql.ansi.enabled = false`: `NULL` statt Fehler bei fehlerhaften Zeitstempeln.

```sql
SELECT to_timestamp('2016-12-31 00:12:00');                 -- 2016-12-31 00:12:00
SELECT to_timestamp('2016-12-31', 'yyyy-MM-dd');             -- 2016-12-31 00:00:00
SELECT to_timestamp('not-a-timestamp');                      -- Error: CAST_INVALID_INPUT
```

## `to_char` — Ausdruck formatiert in `STRING`

**Gilt für:** DBR 11.3 LTS+. **Syntax:** `to_char(expr, { numericFormat | datetimeFormat | stringFormat })`

Numerische Format-Elemente:

| Element | Bedeutung |
|---|---|
| `0` / `9` | Ziffernplatzhalter (füllt mit Nullen bzw. Leerzeichen) |
| `.` / `D` | Position des Dezimalpunkts (max. einmal) |
| `,` / `G` | Tausendertrennzeichen |
| `$` | Währungszeichen (max. einmal) |
| `S` / `MI` | Vorzeichen (`S` druckt `+`/`-`, `MI` Leerzeichen/`−`), nur am Anfang/Ende |
| `PR` | negative Werte in spitzen Klammern (nur am Ende) |

- Zu wenige Ziffernstellen → Auffüllung mit `#`. `stringFormat` für `BINARY`: `'base64'`, `'hex'`, `'utf-8'` (case-insensitiv). Fehlerklasse: `INVALID_FORMAT`.

```sql
SELECT to_char(454, '999');              -- 454
SELECT to_char(454, '000.00');           -- 454.00
SELECT to_char(12454, '99,999');         -- 12,454
SELECT to_char(78.12, '$99.99');         -- $78.12
SELECT to_char(-12454.8, '99,999.9S');   -- 12,454.8-
SELECT to_char(12454.8, '99,999.9S');    -- 12,454.8+
SELECT to_char(1.1, '99');               -- ## (zu wenig Ziffernstellen)
SELECT to_char(date'2016-04-08', 'y');   -- 2016
SELECT to_char(x'537061726b2053514c', 'base64');  -- U3BhcmsgU1FM
SELECT to_char(x'537061726b2053514c', 'hex');     -- 537061726B2053514C
SELECT to_char(111, 'wrong');             -- Error: INVALID_FORMAT
```

## `unix_timestamp` — UNIX-Zeitstempel

**Syntax:** `unix_timestamp([expr [, fmt]])` → `BIGINT`.

- `expr`: `DATE`, `TIMESTAMP` oder `STRING`. `fmt` greift nur bei `STRING` (Default `'yyyy-MM-dd HH:mm:ss'`), wird bei `DATE`/`TIMESTAMP` ignoriert. Ohne Argumente → aktueller Zeitstempel.
- Bei `spark.sql.ansi.enabled = false`: `NULL` statt Fehler.

```sql
SELECT unix_timestamp();                                    -- 1476884637 (Beispielwert)
SELECT unix_timestamp('2016-04-08', 'yyyy-MM-dd');           -- 1460041200
SELECT unix_timestamp('not-a-timestamp', 'yyyy-MM-dd');      -- Error: CANNOT_PARSE_TIMESTAMP
```

## `trunc` — Datum auf eine Einheit kürzen

**Syntax:** `trunc(expr, unit)` — `expr`: `DATE`-Ausdruck.

- `unit` (case-insensitiv): `'YEAR'/'YYYY'/'YY'` (Jahresanfang), `'QUARTER'` (Quartalsanfang), `'MONTH'/'MM'/'MON'` (Monatsanfang), `'WEEK'` (Montag der Woche).
- Nicht wohlgeformte `unit` → `NULL` (kein Fehler). Für `TIMESTAMP` stattdessen `date_trunc` verwenden.

```sql
SELECT trunc('2019-08-04', 'week');      -- 2019-07-29
SELECT trunc('2019-08-04', 'quarter');   -- 2019-07-01
SELECT trunc('2009-02-12', 'MM');        -- 2009-02-01
SELECT trunc('2015-10-27', 'YEAR');      -- 2015-01-01
SELECT trunc('2015-10-27', 'JAHR');      -- NULL ('JAHR' ist keine erkannte Einheit)
```

**Stand:** 2026-09-14.
