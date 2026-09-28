# `typeof` — Datentyp einer Eingabe als DDL-String

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/typeof>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt einen DDL-formatierten Typ-String für den Datentyp der Eingabe zurück.

## Syntax

```
typeof(expr)
```

## Argumente

- **`expr`**: ein beliebiger Ausdruck.

## Rückgabe

Ein `STRING`.

> **Hinweis:** Für den Typ eines `VARIANT`-**Werts** stattdessen [`schema_of_variant`](../06%20JSON,%20CSV%20und%20VARIANT/schema_of_variant.md) verwenden; für die kombinierte Schema einer Gruppe von `VARIANT`-Werten [`schema_of_variant_agg`](../06%20JSON,%20CSV%20und%20VARIANT/schema_of_variant_agg.md).

## Beispiele

```sql
> SELECT typeof(1);
int

> SELECT typeof(array(1));
array<int>

> SELECT typeof(123.4::VARIANT);
variant

> SELECT schema_of_variant(123.4::VARIANT);
DECIMAL(4,1)

> SELECT typeof('hello' COLLATE UTF8_LCASE);
string collate UTF8_LCASE
```

## Verwandte Funktionen

- [`schema_of_variant` function](../06%20JSON,%20CSV%20und%20VARIANT/schema_of_variant.md)
- [`schema_of_variant_agg` aggregate function](../06%20JSON,%20CSV%20und%20VARIANT/schema_of_variant_agg.md)
