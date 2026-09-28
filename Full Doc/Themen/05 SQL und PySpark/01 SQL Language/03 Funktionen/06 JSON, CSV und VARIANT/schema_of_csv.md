# `schema_of_csv` — Schema eines CSV-Strings

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/schema_of_csv>
> Gilt für: Databricks SQL, Databricks Runtime.

Gibt das Schema eines CSV-Strings im DDL-Format zurück.

## Syntax

```
schema_of_csv(csv [, options] )
```

## Argumente

- **`csv`**: ein `STRING`-Literal mit gültigen CSV-Daten.
- **`options`**: ein optionales `MAP`-Literal, dessen Keys und Werte `STRING` sind.

## Rückgabe

Ein `STRING`, der einen Struct beschreibt. Die Feldnamen werden positionsbasiert als `_cN` abgeleitet. Die Werte enthalten die abgeleiteten formatierten SQL-Typen. Vollständige Optionsliste siehe CSV-Funktionsdokumentation.

## Beispiele

```sql
> DESCRIBE SELECT schema_of_csv('1,abc');
STRUCT<`_c0`: INT, `_c1`: STRING>
```

## Verwandte Funktionen

- [`from_csv` function](from_csv.md)
