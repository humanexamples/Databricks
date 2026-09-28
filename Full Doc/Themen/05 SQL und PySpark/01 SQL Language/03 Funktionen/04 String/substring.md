# `substring` — Teilzeichenkette

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/substring>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt die Teilzeichenkette von `expr` zurück, die an Position `pos` beginnt und die Länge `len` hat. Synonym für [`substr`](substr.md).

## Syntax

```
substring(expr, pos [, len])
substring(expr FROM pos [FOR len] ] )
```

## Argumente

- **`expr`**: ein `BINARY`- oder `STRING`-Ausdruck.
- **`pos`**: ein integraler numerischer Ausdruck für die Startposition.
- **`len`**: ein optionaler integraler numerischer Ausdruck.

## Rückgabe

Ein `STRING`.

`pos` ist **1-basiert**. Ist `pos` negativ, wird der Start durch Zählen von Zeichen (bzw. Bytes bei `BINARY`) vom Ende bestimmt. Ist `len` kleiner als 1, ist das Ergebnis leer. Wird `len` weggelassen, gibt die Funktion alle Zeichen/Bytes ab `pos` zurück.

## Beispiele

```sql
> SELECT substring('Spark SQL', 5);
 k SQL
> SELECT substring('Spark SQL', -3);
 SQL
> SELECT substring('Spark SQL', 5, 1);
 k
> SELECT substring('Spark SQL' FROM 5);
 k SQL
> SELECT substring('Spark SQL' FROM -3);
 SQL
> SELECT substring('Spark SQL' FROM 5 FOR 1);
 k
> SELECT substring('Spark SQL' FROM -10 FOR 5);
 Spar
```

## Verwandte Funktionen

- [`substr` function](substr.md)
