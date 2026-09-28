# `trunc` — Datum auf eine Einheit kürzen

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/trunc>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt ein Datum zurück, das auf die durch das Formatmodell `unit` angegebene Einheit gekürzt ist.

## Syntax

```
trunc(expr, unit)
```

## Argumente

- **`expr`**: ein `DATE`-Ausdruck.
- **`unit`**: ein `STRING`-Ausdruck, wie gekürzt wird (case-insensitiv):
  - `'YEAR'`, `'YYYY'`, `'YY'` — erster Tag des Jahres
  - `'QUARTER'` — erster Tag des Quartals
  - `'MONTH'`, `'MM'`, `'MON'` — erster Tag des Monats
  - `'WEEK'` — Montag der Woche

## Rückgabe

Ein `DATE`. Ist `fmt` nicht wohlgeformt, gibt die Funktion `NULL` zurück.

> Für die Kürzung von `TIMESTAMP`-Werten `date_trunc` verwenden.

## Beispiele

```sql
> SELECT trunc('2019-08-04', 'week');
2019-07-29

> SELECT trunc('2019-08-04', 'quarter');
2019-07-01

> SELECT trunc('2009-02-12', 'MM');
2009-02-01

> SELECT trunc('2015-10-27', 'YEAR');
2015-01-01

-- 'JAHR' ist keine erkannte Einheit
> SELECT trunc('2015-10-27', 'JAHR');
NULL
```

## Verwandte Funktionen

- `date_trunc` function
