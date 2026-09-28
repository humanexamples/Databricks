# `to_timestamp` — String in `TIMESTAMP` konvertieren

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/to_timestamp>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt `expr` als Zeitstempel zurück, optional mit Formatierung.

## Syntax

```
to_timestamp(expr [, fmt] )
```

## Argumente

- **`expr`**: ein `STRING`-Ausdruck, der einen Zeitstempel darstellt.
- **`fmt`**: optionaler Format-`STRING` gemäß [Datetime patterns](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-datetime-pattern).

## Rückgabe

Ein `TIMESTAMP`-Wert.

Ohne `fmt` verhält sich die Funktion wie `cast(expr AS TIMESTAMP)`. Fehlerhafte Formate oder ungültige Ergebnisse lösen einen Fehler aus. Für `NULL` statt Fehler: `try_to_timestamp`.

**Fehlerklassen:** `CAST_INVALID_INPUT`, `CANNOT_PARSE_TIMESTAMP`.

> **Hinweis:** In Databricks Runtime mit `spark.sql.ansi.enabled = false` geben fehlerhafte Zeitstempel `NULL` zurück statt einen Fehler auszulösen.

## Beispiele

```sql
> SELECT to_timestamp('2016-12-31 00:12:00');
2016-12-31 00:12:00

> SELECT to_timestamp('2016-12-31', 'yyyy-MM-dd');
2016-12-31 00:00:00

> SELECT to_timestamp('not-a-timestamp');
Error: CAST_INVALID_INPUT
```

## Verwandte Funktionen

- [`cast` function](../01%20Cast%20und%20Typkonvertierung/cast.md)
- [`timestamp` function](../01%20Cast%20und%20Typkonvertierung/timestamp.md)
- `try_to_timestamp` function
- [`to_date` function](to_date.md)
- [Datetime patterns](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-datetime-pattern)
