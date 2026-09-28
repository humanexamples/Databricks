# `unbase64` — Base64 dekodieren

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/unbase64>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt einen dekodierten Base64-String als `BINARY` zurück.

## Syntax

```
unbase64(expr)
```

## Argumente

- **`expr`**: ein `STRING`-Ausdruck im Base64-Format.

## Rückgabe

Ein `BINARY`.

## Beispiele

```sql
> SELECT cast(unbase64('U3BhcmsgU1FM') AS STRING);
Spark SQL
```

## Verwandte Funktionen

- `base64` function
