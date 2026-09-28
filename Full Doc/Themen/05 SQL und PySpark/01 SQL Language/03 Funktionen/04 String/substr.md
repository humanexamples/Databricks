# `substr` — Teilzeichenkette

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/substr>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt die Teilzeichenkette von `expr` zurück, die an Position `pos` beginnt und die Länge `len` hat.

## Syntax

```
substr(expr, pos [, len] )
substr(expr FROM pos[ FOR len])
```

## Argumente

- **`expr`**: ein `BINARY`- oder `STRING`-Ausdruck.
- **`pos`**: ein integraler numerischer Ausdruck für die Startposition.
- **`len`**: ein optionaler integraler numerischer Ausdruck.

## Rückgabe

Das Ergebnis entspricht dem Typ von `expr`.

`pos` ist **1-basiert**. Ist `pos` negativ, wird der Start durch Zählen von Zeichen (bzw. Bytes bei `BINARY`) vom Ende bestimmt. Ist `len` kleiner als 1, ist das Ergebnis leer. Wird `len` weggelassen, gibt die Funktion alle Zeichen/Bytes ab `pos` zurück.

## Beispiele

```sql
> SELECT substr('Spark SQL', 5);
k SQL
> SELECT substr('Spark SQL', -3);
SQL
> SELECT substr('Spark SQL', 5, 1);
k
> SELECT substr('Spark SQL' FROM 5);
k SQL
> SELECT substr('Spark SQL' FROM -3);
SQL
> SELECT substr('Spark SQL' FROM 5 FOR 1);
k
> SELECT substr('Spark SQL' FROM -10 FOR 5);
Spar
```

## Verwandte Funktionen

- [`substring` function](substring.md)
