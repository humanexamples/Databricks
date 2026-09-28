# `substring_index` — Teilzeichenkette vor dem n-ten Trenner

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/substring_index>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt die Teilzeichenkette von `expr` **vor** dem `count`-ten Vorkommen des Trennzeichens `delim` zurück.

## Syntax

```
substring_index(expr, delim, count)
```

## Argumente

- **`expr`**: ein `STRING`- oder `BINARY`-Ausdruck.
- **`delim`**: ein Ausdruck vom Typ von `expr`, der das Trennzeichen angibt.
- **`count`**: ein `INTEGER`-Ausdruck zum Zählen der Trenner.

## Rückgabe

Das Ergebnis entspricht dem Typ von `expr`.

Ist `count` positiv, wird alles **links** vom letzten Trenner (von links gezählt) zurückgegeben. Ist `count` negativ, wird alles **rechts** vom letzten Trenner (von rechts gezählt) zurückgegeben.

## Beispiele

```sql
> SELECT substring_index('www.apache.org', '.', 2);
www.apache

> SELECT substring_index('555A66A777' COLLATE UTF8_BINARY, 'a', 2);
555A66A777

> SELECT substring_index('555A66A777' COLLATE UTF8_LCASE, 'a', 2);
555A66
```

## Verwandte Funktionen

- [`substr` function](substr.md)
- [`substring` function](substring.md)
