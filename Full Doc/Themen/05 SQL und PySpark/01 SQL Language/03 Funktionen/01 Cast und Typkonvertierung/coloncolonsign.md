# `::` (colon colon sign) operator — Cast-Operator

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/coloncolonsign>
> Gilt für: Databricks SQL, Databricks Runtime.

Castet den Wert `expr` in den Zieldatentyp `type`. **Synonym für die [`cast`-Funktion](cast.md).**

## Syntax

```
expr :: type
```

## Argumente

- **`expr`**: ein beliebiger castbarer Ausdruck.

## Rückgabe

Ergebnis vom Typ `type`. Wirft dieselben Fehler wie `cast`. Für `NULL` bei Fehler stattdessen den [`?::`-Operator](questiondoublecolonsign.md) verwenden.

**Häufige Fehlerklassen:** `CAST_INVALID_INPUT`, `CAST_OVERFLOW`, `DATATYPE_MISMATCH`, `NUMERIC_VALUE_OUT_OF_RANGE`, `UNSUPPORTED_DATATYPE`.

## Beispiele

```sql
> SELECT '20'::INTEGER;
20

> SELECT typeof(NULL::STRING);
string

> SELECT 'abc'::INT;
Error: CAST_INVALID_INPUT
```

## Verwandte Funktionen

- [`cast` function](cast.md)
- `try_cast` function
