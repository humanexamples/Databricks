# `concat` — Argumente verketten

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/concat>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt die Verkettung der Argumente zurück. Synonym für den `||`-Operator (pipe pipe sign).

## Syntax

```
concat(expr1, expr2 [, ...] )
```

## Argumente

- **`exprN`**: Ausdrücke, die alle `STRING`, alle `BINARY` **oder** alle `ARRAY`s von `STRING`/`BINARY` sind.

## Rückgabe

Der Ergebnistyp entspricht den Argumenttypen. Es muss **mindestens ein** Argument geben.

Beim Verketten von Arrays löst Databricks `COLLECTION_SIZE_LIMIT_EXCEEDED` aus, wenn das Ergebnis das Array-Größenlimit überschreitet.

**Fehlerklassen:** `COLLECTION_SIZE_LIMIT_EXCEEDED`.

## Beispiele

```sql
> SELECT concat('Spark', 'SQL');
SparkSQL

> SELECT concat(array(1, 2, 3), array(4, 5), array(6));
[1,2,3,4,5,6]
```

## Verwandte Funktionen

- `||` (pipe pipe sign) operator
- `array_join` function
- `array_union` function
- [`concat_ws` function](concat_ws.md)
