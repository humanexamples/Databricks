# `unix_timestamp` — UNIX-Zeitstempel

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/unix_timestamp>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt den UNIX-Zeitstempel der aktuellen oder einer angegebenen Zeit zurück.

## Syntax

```
unix_timestamp([expr [, fmt] ] )
```

## Argumente

- **`expr`**: ein optionaler `DATE`-, `TIMESTAMP`- oder `STRING`-Ausdruck in gültigem Datetime-Format.
- **`fmt`**: ein optionaler Format-`STRING`, wenn `expr` ein `STRING` ist. Default `'yyyy-MM-dd HH:mm:ss'`. Bei `DATE`/`TIMESTAMP` wird `fmt` ignoriert.

## Rückgabe

Ein `BIGINT` mit dem UNIX-Zeitstempel.

Ohne Argument wird der aktuelle Zeitstempel zurückgegeben. Bei `spark.sql.ansi.enabled = false` gibt die Funktion `NULL` statt eines Fehlers für fehlerhafte Zeitstempel zurück.

## Beispiele

```sql
> SELECT unix_timestamp();
1476884637

> SELECT unix_timestamp('2016-04-08', 'yyyy-MM-dd');
1460041200

> SELECT unix_timestamp('not-a-timestamp', 'yyyy-MM-dd');
Error: CANNOT_PARSE_TIMESTAMP
```

## Verwandte Funktionen

- [`timestamp` function](../01%20Cast%20und%20Typkonvertierung/timestamp.md)
