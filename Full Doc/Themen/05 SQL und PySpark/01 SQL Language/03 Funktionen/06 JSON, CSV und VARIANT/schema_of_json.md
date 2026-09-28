# `schema_of_json` — Schema eines JSON-Strings

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/schema_of_json>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt das Schema eines JSON-Strings im DDL-Format zurück.

## Syntax

```
schema_of_json(jsonStr [, options] )
```

## Argumente

- **`jsonStr`**: ein `STRING`-Ausdruck mit einem JSON-String.
- **`options`**: ein optionales `MAP`-Literal, dessen Keys und Werte `STRING` sind. Vollständige Optionsliste siehe JSON-Optionen.

## Rückgabe

Ein `STRING` mit der Definition eines Arrays von Structs mit `n` String-Feldern, deren Spaltennamen aus den JSON-Keys abgeleitet werden. Die Feldwerte enthalten die abgeleiteten formatierten SQL-Typen.

Für das aggregierte Schema einer Gruppe von JSON-Strings die Aggregatfunktion [`schema_of_json_agg`](schema_of_json_agg.md) verwenden.

## Beispiele

```sql
> SELECT schema_of_json('[{"col":0}]');
ARRAY<STRUCT<`col`: BIGINT>>

> SELECT schema_of_json('[{"col":01}]', map('allowNumericLeadingZeros', 'true'));
ARRAY<STRUCT<`col`: BIGINT>>
```

## Verwandte Funktionen

- [`from_json` function](from_json.md)
- [`schema_of_json_agg` aggregate function](schema_of_json_agg.md)
