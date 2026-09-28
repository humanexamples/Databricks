# `split` — String anhand Regex in Array teilen

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/split>
> Gilt für: Databricks SQL, Databricks Runtime.

Teilt einen String anhand von Regex-Treffern in ein Array, optional mit Längenbegrenzung.

## Syntax

```
split(str, regex [, limit] )
```

## Argumente

- **`str`**: ein zu teilender `STRING`-Ausdruck.
- **`regexp`**: ein `STRING`-Ausdruck, der ein regulärer Ausdruck ist und `str` teilt. Zur unterstützten Syntax siehe *Regular expressions*.
- **`limit`**: ein optionaler `INTEGER`-Ausdruck, Default `0` (kein Limit).

## Rückgabe

Ein `ARRAY<STRING>`.

Ist `limit > 0`: Die Array-Länge ist höchstens `limit`, und das letzte Element enthält alle Eingaben nach dem letzten Regex-Treffer. Ist `limit <= 0`: Der Regex wird so oft wie möglich angewendet, das Array kann beliebig groß sein.

## Beispiele

```sql
-- Nach einer Menge von Trennzeichen teilen
> SELECT split('oneAtwoBthreeC', '[ABC]');
[one,two,three,]

-- Kommaseparierten String teilen
> SELECT split('apple,banana,cherry', ',');
[apple,banana,cherry]

-- An einem oder mehreren Whitespace-Zeichen teilen
> SELECT split('the   quick  brown', r'\s+');
[the,quick,brown]

-- Anzahl der Elemente begrenzen
> SELECT split('oneAtwoBthreeC', '[ABC]', 2);
[one,twoBthreeC]

> SELECT split('oneAtwoBthreeC', '[ABC]', -1);
[one,two,three,]

-- Collation beeinflusst das Matching
> SELECT split('oneAtwoBthreeC' COLLATE UTF8_BINARY, '[abc]');
[oneAtwoBthreeC]

> SELECT split('oneAtwoBthreeC' COLLATE UTF8_LCASE, '[abc]');
[one,two,three,]
```

## Verwandte Funktionen

- `regexp_extract` function
- `regexp_extract_all` function
- `split_part` function
