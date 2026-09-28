# `to_char` — Ausdruck formatiert in `STRING` umwandeln

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/to_char>
> Gilt für: Databricks SQL, Databricks Runtime **11.3 LTS und höher**.

Konvertiert einen Ausdruck in einen `STRING` mit angegebener Formatierung (numerisch, datetime oder für `BINARY`).

## Syntax

```
to_char(expr, { numericFormat | datetimeFormat | stringFormat } )

numericFormat
  ' [ S ] [ L | $ ]
    [ 0 | 9 | G | , ] [...]
    [ . | D ]
    [ 0 | 9 ] [...]
    [ L | $ ] [ PR | MI | S ] '
```

## Argumente

- **`expr`**: ein Ausdruck vom Typ numerisch, datetime, `STRING` oder `BINARY`.
- **`numericFormat`**: `STRING`-Literal für formatierte numerische Ausgabe.
- **`datetimeFormat`**: `STRING`-Literal gemäß *Datetime patterns*.
- **`stringFormat`**: `STRING`-Literal für `BINARY` — case-insensitiv `'base64'`, `'hex'`, `'utf-8'`.

### Numerische Format-Elemente

- **`0`** / **`9`**: Ziffernplatzhalter (0–9); füllt mit Nullen bzw. Leerzeichen auf.
- **`.`** / **`D`**: Position des Dezimalpunkts (optional, nur einmal).
- **`,`** / **`G`**: Gruppierungs-/Tausendertrenner.
- **`$`**: Position des Währungszeichens (nur einmal).
- **`S`** / **`MI`**: Vorzeichenposition (optional, nur Anfang oder Ende); `S` druckt `+`/`-`, `MI` druckt Leerzeichen/`−`.
- **`PR`**: negative Werte in spitze Klammern (nur Ende).
- Zu wenige Ziffernstellen → Auffüllung mit `#`.

## Rückgabe

Ein `STRING` mit dem Ergebnis der Formatierung. Fehler: `INVALID_FORMAT`.

## Beispiele

```sql
> SELECT to_char(454, '999');            454
> SELECT to_char(454, '000.00');         454.00
> SELECT to_char(12454, '99,999');       12,454
> SELECT to_char(78.12, '$99.99');       $78.12
> SELECT to_char(-12454.8, '99,999.9S'); 12,454.8-
> SELECT to_char(12454.8, '99,999.9S');  12,454.8+
> SELECT '>' || to_char(123, '00000.00') || '<';   >00123.00<
> SELECT '>' || to_char(123, '99999.99') || '<';   >  123.00<
> SELECT to_char(1.1, '99');             ##
> SELECT to_char(111.11, '99.9');        ##.#
> SELECT to_char(111.11, '$99.9');       $##.#
> SELECT to_char(date'2016-04-08', 'y'); 2016
> SELECT to_char(x'537061726b2053514c', 'base64');   U3BhcmsgU1FM
> SELECT to_char(x'537061726b2053514c', 'hex');      537061726B2053514C
> SELECT to_char(encode('abc', 'utf-8'), 'utf-8');   abc
> SELECT to_char(111, 'wrong');          Error: INVALID_FORMAT
```

## Verwandte Funktionen

- [`cast` function](../01%20Cast%20und%20Typkonvertierung/cast.md)
- [`to_date` function](to_date.md)
- `to_number` function
- `to_varchar` function
