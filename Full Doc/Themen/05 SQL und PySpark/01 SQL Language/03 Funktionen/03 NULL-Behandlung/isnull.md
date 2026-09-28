# `isnull` — prüft auf `NULL`

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/isnull>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt `true` zurück, wenn `expr` `NULL` ist. Synonym für den `is null`-Operator.

## Syntax

```
isnull(expr)
```

## Argumente

- **`expr`**: ein Ausdruck beliebigen Typs.

## Rückgabe

Ein `BOOLEAN`-Wert.

> **Wichtig — VARIANT:** Ist `expr` ein `VARIANT` aus einem JSON-Path-Ausdruck, der `parse_json`-Funktion, `variant_explode` oder `variant_explode_outer`, ist das Ergebnis **immer `false`**. Mit der `is_variant_null`-Funktion prüfen, ob der `VARIANT`-kodierte Wert `NULL` ist, oder den `VARIANT` in einen konkreten Typ casten.

## Beispiele

```sql
> SELECT isnull(1);
false

> SELECT isnull(NULL:INTEGER);
true

> SELECT isnull(parse_json('{"key": null}'):key);
false

> SELECT isnull(parse_json('{"key": null}'):key::STRING);
true

> SELECT isnull(parse_json('{"key": null}'):wrongkey);
true

> SELECT is_variant_null(parse_json('{"key": null}'):key);
true
```

## Verwandte Funktionen

- [`isnotnull` function](isnotnull.md)
- `isnan` function
- `is null` operator
- `is_variant_null` function
