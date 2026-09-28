# `to_date` — String in `DATE` konvertieren

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/to_date>
> Gilt für: Databricks SQL, Databricks Runtime.

Konvertiert einen String-Ausdruck in ein Datum, optional mit angegebenem Format.

## Syntax

```
to_date(expr [, fmt] )
```

## Argumente

- **`expr`**: ein `STRING`-Ausdruck, der ein Datum darstellt.
- **`fmt`**: optionaler Format-`STRING` gemäß [Datetime patterns](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-datetime-pattern).

## Rückgabe

Ein `DATE`-Wert.

Ohne `fmt` verhält sich die Funktion wie `cast(expr AS DATE)`. Bei fehlerhaftem Format-String oder ungültigem Datum wird ein Fehler ausgelöst. Für `NULL` stattdessen `try_cast(expr AS DATE)` verwenden oder [`spark.sql.ansi.enabled`](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-ansi-compliance) deaktivieren.

**Fehlerklassen:**

- **`CAST_INVALID_INPUT`** — kein Format angegeben und die Eingabe ist nicht als Datum parsebar.
- **`CANNOT_PARSE_TIMESTAMP`** — Format angegeben, aber die Eingabe passt nicht zum Muster.

## Beispiele

```sql
-- Parsen mit Default-Format (yyyy-MM-dd)
> SELECT to_date('2009-07-30 04:17:52');
2009-07-30

-- Parsen mit explizitem Format
> SELECT to_date('2016-12-31', 'yyyy-MM-dd');
2016-12-31

-- Nicht-Default-Datumsformat
> SELECT to_date('31/12/2016', 'dd/MM/yyyy');
2016-12-31

-- Fehler: keine gültige Datums-Zeichenkette
> SELECT to_date('not-a-date');
Error: CAST_INVALID_INPUT

-- Fehler: Eingabeformat passt nicht zum Default yyyy-MM-dd
> SELECT to_date('31/12/2016');
Error: CAST_INVALID_INPUT

-- try_cast gibt NULL statt Fehler zurück
> SELECT try_cast('not-a-date' AS DATE);
NULL
```

## Verwandte Funktionen

- [`cast` function](../01%20Cast%20und%20Typkonvertierung/cast.md)
- [`date` function](../01%20Cast%20und%20Typkonvertierung/date.md)
- [`to_timestamp` function](to_timestamp.md)
- `try_cast` function
- [Datetime patterns](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-datetime-pattern)
