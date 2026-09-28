# `from_csv` — CSV-String in Struct/Variant parsen

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/from_csv>
> Gilt für: Databricks SQL, Databricks Runtime.

Parst einen CSV-String in einen Struct- oder Variant-Wert anhand eines angegebenen Schemas.

## Syntax

```
from_csv(csvStr, schema [, options])
```

## Argumente

- **`csvStr`**: ein `STRING`-Ausdruck, der eine Zeile CSV-Daten angibt.
- **`schema`**: ein `STRING`-Literal oder das Ergebnis der [`schema_of_csv`](schema_of_csv.md)-Funktion; in Databricks Runtime 16.4+ auch ein einzelner `VARIANT`-Typ.
- **`options`**: ein optionales `MAP<STRING,STRING>` mit CSV-Parsing-Direktiven, u. a. `sep` (`,`), `encoding` (`UTF-8`), `quote` (`"`), `escape` (`\`), `charToEscapeQuoteEscaping`, `comment`, `header` (`false`), `enforceSchema` (`true`), `inferSchema`, `samplingRatio` (`1.0`), `ignoreLeadingWhiteSpace`, `ignoreTrailingWhiteSpace`, `nullValue`, `emptyValue`, `nanValue` (`NaN`), `positiveInf`, `negativeInf`, `dateFormat` (`yyyy-MM-dd`), `timestampFormat` (`yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]`), `maxColumns` (`20480`), `maxCharsPerColumn` (`-1`), `unescapedQuoteHandling`, `mode` (`PERMISSIVE`), `columnNameOfCorruptRecord`, `multiLine` (`false`), `locale`, `lineSep`, `pathGlobFilter`.

## Rückgabe

Ein `STRUCT` mit Feldern gemäß Schema, oder ein `VARIANT`-Wert, wenn das Schema ein `VARIANT`-Typ ist.

## Beispiele

```sql
> SELECT from_csv('1, 0.8', 'a INT, b DOUBLE');
{1,0.8}

> SELECT from_csv('26/08/2015', 'time Timestamp', map('timestampFormat', 'dd/MM/yyyy'));
{"time":2015-08-26 00:00:00}

> SELECT from_csv('abc', 'a INT', map('mode', 'FAILFAST'));
Error: MALFORMED_RECORD_IN_PARSING
```

## Verwandte Funktionen

- [`from_json` function](from_json.md)
- [`schema_of_csv` function](schema_of_csv.md)
- [`schema_of_json` function](schema_of_json.md)
- `to_json` function
- `to_csv` function
