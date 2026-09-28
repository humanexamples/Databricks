# `string` — Wert in `STRING` konvertieren

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/string>
> Gilt für: Databricks SQL, Databricks Runtime.

Konvertiert einen Wert in den Typ `STRING`; entspricht `cast(expr AS STRING)`.

## Syntax

```
string(expr)
```

## Argumente

- **`expr`**: ein Ausdruck, der in `STRING` castbar ist.

## Rückgabe

Ein `STRING`. Ist `expr` kein `STRING`, erhält das Ergebnis die Default-Collation; andernfalls die Collation von `expr`.

## Beispiele

```sql
> SELECT string(5);
5

> SELECT string(current_date);
2021-04-01
```

## Verwandte Funktionen

- [`cast` function](cast.md)
