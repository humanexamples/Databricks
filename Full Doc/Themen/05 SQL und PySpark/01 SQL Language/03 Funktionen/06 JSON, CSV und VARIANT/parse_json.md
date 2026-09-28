# `parse_json` — JSON-String in `VARIANT`

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/parse_json>
> Gilt für: Databricks SQL, Databricks Runtime **15.3 und höher**.

Gibt einen `VARIANT`-Wert aus `jsonStr` zurück.

## Syntax

```
parse_json ( jsonStr )
```

## Argumente

- **`jsonStr`**: ein `STRING`-Ausdruck mit einem JSON-Dokument.

## Rückgabe

Ein `VARIANT`-Wert, der dieselben Daten wie der Eingabe-JSON-String repräsentiert. Ist der JSON-String ungültig, löst Databricks `MALFORMED_RECORD_IN_PARSING` aus. Mit `try_parse_json` wird stattdessen `NULL` zurückgegeben.

## Notes

`to_json` ist die logische (nicht exakte) Umkehrung von `parse_json`. Unterschiede:

- Whitespace wird nicht perfekt erhalten: `{ "a" : 1, "b" : 2 }` = `{"a":1,"b":2}`
- Key-Reihenfolge kann beliebig sein: `{"a" : 1, "b": 2}` = `{"b": 2, "a" : 1}`
- Nachlaufende Nullen in Zahlen werden entfernt: `{"a" : 0.01000}` = `{"a" : 0.01}`

## Beispiele

```sql
-- Einfaches Beispiel
> SELECT parse_json('{"key": 123, "data": [4, 5, "str"]}');
  {"data":[4,5,"str"],"key":123}

-- Skalaren Wert parsen
> SELECT parse_json('123');
  123

-- Ungültiger JSON-String
> SELECT parse_json('{ bad }');
  Error: MALFORMED_RECORD_IN_PARSING
```

## Verwandte Funktionen

- `try_parse_json` function
- `to_json` function
- `variant_get` function
- [`from_json` function](from_json.md)
