# `timestamp` — Wert in `TIMESTAMP` casten

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/timestamp>
> Gilt für: Databricks SQL, Databricks Runtime.

Castet `expr` in `TIMESTAMP`. Synonym für `CAST(expr AS TIMESTAMP)`.

## Syntax

```
timestamp(expr)
```

## Argumente

- **`expr`**: ein beliebiger Ausdruck, der in `TIMESTAMP` castbar ist.

## Rückgabe

Ein `TIMESTAMP`.

## Beispiele

```sql
> SELECT timestamp('2020-04-30 12:25:13.45');
2020-04-30 12:25:13.45

> SELECT timestamp(date'2020-04-30');
2020-04-30 00:00:00

> SELECT timestamp(123);
1969-12-31 16:02:03
```

## Verwandte Funktionen

- [`cast` function](cast.md)
