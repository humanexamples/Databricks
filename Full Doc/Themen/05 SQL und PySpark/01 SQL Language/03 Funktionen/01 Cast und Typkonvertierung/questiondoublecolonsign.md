# `?::` (question double colon sign) operator — fehlertoleranter Cast-Operator

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/questiondoublecolonsign>
> Gilt für: Databricks Runtime **15.3 und höher**.

Castet den Wert `expr` in den Zieldatentyp `type` **mit Fehlertoleranz**. **Synonym für die `try_cast`-Funktion.**

## Syntax

```
expr ?:: type
```

## Argumente

- **`expr`**: ein beliebiger castbarer Ausdruck.

## Rückgabe

Ergebnis vom Typ `type`. Bei nicht castbarer Eingabe wird `NULL` zurückgegeben (statt eines Fehlers wie bei [`::`](coloncolonsign.md)).

## Beispiele

```sql
> SELECT '20'?::INTEGER;
20

> SELECT 'twenty'?::INTEGER;
NULL

> SELECT typeof(NULL?::STRING);
string
```

## Verwandte Funktionen

- [`::` (colon colon sign) operator](coloncolonsign.md)
- [`cast` function](cast.md)
- `try_cast` function
