# `isnotnull` — prüft auf nicht-`NULL`

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/isnotnull>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt `true` zurück, wenn `expr` **nicht** `NULL` ist. Synonym für `expr IS NOT NULL`.

## Syntax

```
isnotnull(expr)
```

## Argumente

- **`expr`**: ein Ausdruck beliebigen Typs.

## Rückgabe

Ein `BOOLEAN`.

> **Wichtig — VARIANT:** Ist `expr` ein `VARIANT` aus einem JSON-Path-Ausdruck, der `parse_json`-Funktion, `variant_explode` oder `variant_explode_outer`, ist das Ergebnis **immer `true`**. Mit `is_variant_null` prüfen, ob der `VARIANT`-kodierte Wert `NULL` ist, oder den `VARIANT` in einen konkreten Typ casten.

## Beispiele

```sql
> SELECT isnotnull(1);
true

> SELECT isnotnull(NULL:INTEGER);
false

> SELECT isnotnull(parse_json('{"key": null}'):key);
true

> SELECT isnotnull(parse_json('{"key": null}'):wrongkey);
false

> SELECT !is_variant_null(parse_json('{"key": null}'):key);
false
```

## Verwandte Funktionen

- [`isnull` function](isnull.md)
- `isnan` function
- `is null` operator
- `is_variant_null` function
