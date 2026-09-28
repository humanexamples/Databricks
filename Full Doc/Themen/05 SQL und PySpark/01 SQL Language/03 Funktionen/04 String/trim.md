# `trim` — Zeichen am Rand entfernen

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/trim>
> Gilt für: Databricks SQL, Databricks Runtime.

Entfernt die führenden bzw. abschließenden Leerzeichen aus `str` — bzw. die führenden/abschließenden `trimStr`-Zeichen.

## Syntax

```
trim(str)
trim(BOTH FROM str)
trim(LEADING FROM str)
trim(TRAILING FROM str)
trim(trimStr FROM str)
trim(BOTH trimStr FROM str)
trim(LEADING trimStr FROM str)
trim(TRAILING trimStr FROM str)
```

## Argumente

- **`trimStr`**: ein `STRING`-Ausdruck mit den zu entfernenden Zeichen.
- **`str`**: der zu trimmende `STRING`-Ausdruck.

## Rückgabe

Ein `STRING`.

## Beispiele

```sql
> SELECT '+' || trim('    SparkSQL   ') || '+';
+SparkSQL+

> SELECT '+' || trim(BOTH FROM '    SparkSQL   ') || '+';
+SparkSQL+

> SELECT '+' || trim(LEADING FROM '    SparkSQL   ') || '+';
+SparkSQL   +

> SELECT '+' || trim(TRAILING FROM '    SparkSQL   ') || '+';
+    SparkSQL+

> SELECT trim('SL' FROM 'SSparkSQLS');
parkSQ

> SELECT trim(BOTH 'SL' FROM 'SSparkSQLS');
parkSQ

> SELECT trim(LEADING 'SL' FROM 'SSparkSQLS');
parkSQLS

> SELECT trim(TRAILING 'SL' FROM 'SSparkSQLS');
SSparkSQ

> SELECT trim(BOTH 'sl' COLLATE UTF8_BINARY FROM 'SSparkSQLS');
SSparkSQLS

> SELECT trim(BOTH 'sl' COLLATE UTF8_LCASE FROM 'SSparkSQLS');
parkSQ
```

## Verwandte Funktionen

- `ltrim` function
- `rtrim` function
- `btrim` function
- `lpad` function
- `rpad` function
