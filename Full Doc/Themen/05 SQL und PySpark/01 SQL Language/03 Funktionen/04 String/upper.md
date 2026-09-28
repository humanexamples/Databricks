# `upper` — in Großbuchstaben

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/upper>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt `expr` mit allen Zeichen in Großbuchstaben zurück (gemäß der Collation von `expr`). Synonym für `ucase`.

## Syntax

```
upper(expr)
```

## Argumente

- **`expr`**: ein `STRING`-Ausdruck.

## Rückgabe

Ein `STRING`.

## Beispiele

```sql
> SELECT upper('SparkSql');
SPARKSQL
```

## Verwandte Funktionen

- `lower` function
- `initcap` function
- `ucase` function
