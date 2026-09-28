# `from_json` — JSON-String in Struct parsen

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/from_json>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt einen Struct-Wert aus `jsonStr` und `schema` zurück.

## Syntax

```
from_json(jsonStr, schema [, options])
```

## Argumente

- **`jsonStr`**: ein `STRING`-Ausdruck mit einem JSON-Dokument.
- **`schema`**: ein `STRING`-Ausdruck oder Aufruf der [`schema_of_json`](schema_of_json.md)-Funktion. Muss als kommagetrennte Paare aus Spaltenname und Datentyp definiert sein. Vor Databricks Runtime 12.2 muss das Schema ein Literal sein. Alternativ kann `schema` auf `NULL` gesetzt werden — für Lakeflow-Pipelines mit automatischer Schema-Inferenz über einen `schemaLocationKey`.
  > **Hinweis:** Die Spalten- und Feldnamen im `schema` sind **case-sensitiv** und müssen exakt den Namen in `jsonStr` entsprechen.
- **`options`**: ein optionales `MAP<STRING,STRING>`-Literal (`primitivesAsString`, `prefersDecimal`, `allowComments`, `allowUnquotedFieldNames`, `allowSingleQuotes`, `allowNumericLeadingZeros`, `allowBackslashEscapingAnyCharacter`, `allowUnquotedControlChars`, `mode`, `columnNameOfCorruptRecord`, `dateFormat`, `timestampFormat`, `multiLine`, `encoding`, `lineSep`, `samplingRatio`, `dropFieldIfAllNull`, `locale`, `allowNonNumericNumbers`, `readerCaseSensitive`).

## Rückgabe

Ein Struct mit Feldnamen und -typen gemäß der Schema-Definition. Bei `mode => 'FAILFAST'` wird `MALFORMED_RECORD_IN_PARSING` ausgelöst, wenn die Eingabe nicht dem Schema entspricht.

## Beispiele

```sql
> SELECT from_json('{"a":1, "b":0.8}', 'a INT, b DOUBLE');
{"a":1,"b":0.8}

-- Der Spaltenname muss die Groß-/Kleinschreibung des JSON-Feldes treffen
> SELECT from_json('{"a":1}', 'A INT');
{"A":null}

> SELECT from_json('{"datetime":"26/08/2015"}', 'datetime Timestamp',
  map('timestampFormat', 'dd/MM/yyyy'));
{"datetime":2015-08-26 00:00:00}

-- Feldnamen mit unterschiedlicher Groß-/Kleinschreibung disambiguieren
> SELECT cast(from_json('{"a":1, "A":0.8}', 'a INT, A DOUBLE')
  AS STRUCT<a: INT, b: DOUBLE>);
{"a":1, "b":0.8}

> SELECT from_json('invalid', 'a INT', map('mode', 'FAILFAST'));
Error: MALFORMED_RECORD_IN_PARSING
```

## Verwandte Funktionen

- [`:` operator](colonsign.md)
- [`from_csv` function](from_csv.md)
- [`schema_of_json` function](schema_of_json.md)
- `to_json` function
- `json_object_keys` / `json_array_length` / `json_tuple` / `get_json_object` functions
- JSON path expression
