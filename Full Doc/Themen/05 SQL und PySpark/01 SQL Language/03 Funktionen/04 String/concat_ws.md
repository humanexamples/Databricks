# `concat_ws` — Strings mit Trennzeichen verketten

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/concat_ws>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt die durch `sep` getrennte Verkettung der Strings zurück.

## Syntax

```
concat_ws(sep [, expr1 [, ...] ])
```

## Argumente

- **`sep`**: ein `STRING`-Ausdruck.
- **`exprN`**: jedes `exprN` kann ein `STRING` oder ein `ARRAY` von `STRING` sein.

## Rückgabe

Der Ergebnistyp ist `STRING`.

Ist `sep` `NULL`, ist das Ergebnis `NULL`. `exprN`, die `NULL` sind, werden ignoriert. Wird nur der Separator angegeben oder sind alle `exprN` `NULL`, ergibt sich ein leerer String.

## Beispiele

```sql
> SELECT concat_ws(' ', 'Spark', 'SQL');
Spark SQL

> SELECT concat_ws('s');
''

> SELECT concat_ws(',', 'Spark', array('S', 'Q', NULL, 'L'), NULL);
Spark,S,Q,L
```

## Verwandte Funktionen

- `||` (pipe pipe sign) operator
- [`concat` function](concat.md)
- `array_join` function
