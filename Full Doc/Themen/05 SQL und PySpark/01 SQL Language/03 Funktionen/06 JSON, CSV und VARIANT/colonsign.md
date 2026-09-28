# `:` (colon sign) operator — JSON-Path-Extraktion

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/colonsign>
> Gilt für: Databricks SQL, Databricks Runtime.

Extrahiert Inhalt aus einem JSON-String über einen JSON-Path-Ausdruck.

## Syntax

```
jsonExpr : jsonPath
```

## Argumente

- **`jsonExpr`**: ein `VARIANT`-Ausdruck **oder** ein `STRING`-Ausdruck mit gültigem JSON.
- **`jsonPath`**: ein JSON-Path-Ausdruck.

## Rückgabe

Das Ergebnis entspricht dem Typ von `jsonExpr`. Ist die Eingabe kein gültiges JSON oder der Path für den JSON-Wert nicht gültig, ist das Ergebnis `NULL`. Ist der extrahierte Wert ein un-delimited `null`, ist das Ergebnis der SQL-`NULL`-Wert.

## Beispiele

```sql
> SELECT c1:price FROM VALUES('{ "price": 5 }') AS T(c1);
5

> SELECT c1:['price']::decimal(5,2) FROM VALUES('{ "price": 5 }') AS T(c1);
5.00

> SELECT c1:item[1].price::double FROM VALUES('{ "item": [ { "model" : "basic", "price" : 6.12 }, { "model" : "medium", "price" : 9.24 } ] }') AS T(c1);
9.24

> SELECT c1:item[*].price FROM VALUES('{ "item": [ { "model" : "basic", "price" : 6.12 }, { "model" : "medium", "price" : 9.24 } ] }') AS T(c1);
[6.12,9.24]

> SELECT from_json(c1:item[*].price, 'ARRAY<DOUBLE>')[0] FROM VALUES('{ "item": [ { "model" : "basic", "price" : 6.12 }, { "model" : "medium", "price" : 9.24 } ] }') AS T(c1);
6.12

> SELECT from_json(c1:item[*], 'ARRAY<STRUCT<model STRING, price DOUBLE>>') FROM VALUES('{ "item": [ { "model" : "basic", "price" : 6.12 }, { "model" : "medium", "price" : 9.24 } ] }') AS T(c1);
[{"model":"basic","price":6.12},{"model":"medium","price":9.24}]

> SELECT inline(from_json(c1:item[*], 'ARRAY<STRUCT<model STRING, price DOUBLE>>')) FROM VALUES('{ "item": [ { "model" : "basic", "price" : 6.12 }, { "model" : "medium", "price" : 9.24 } ] }') AS T(c1);
basic     6.12
medium    9.24

> SELECT PARSE_JSON('{ "price": 5 }'):price
5

> SELECT PARSE_JSON('{ "price": 5 }'):price::decimal(5,2)
5.00

> SELECT PARSE_JSON('{ "item": [ { "model" : "basic", "price" : 6.12 }, { "model" : "medium", "price" : 9.24 } ] }'):item[1].price::double
9.24
```

## Verwandte Funktionen

- [`::` operator](../01%20Cast%20und%20Typkonvertierung/coloncolonsign.md)
- `explode` function
- [`from_json` function](from_json.md)
- `inline` function
- JSON path expression (`/aws/en/sql/language-manual/sql-ref-json-path-expression`)
