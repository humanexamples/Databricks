# `date` — Wert in `DATE` konvertieren

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/date>
> Gilt für: Databricks SQL, Databricks Runtime.

Konvertiert den Wert `expr` in den Typ `DATE`. Synonym für `CAST(expr AS DATE)`.

## Syntax

```
date(expr)
```

## Argumente

- **`expr`**: ein Ausdruck, der in `DATE` konvertierbar ist.

## Rückgabe

Ein `DATE`-Wert.

## Beispiele

```sql
> SELECT date('2021-03-21');
2021-03-21
```

## Verwandte Funktionen

- [`cast` function](cast.md)
