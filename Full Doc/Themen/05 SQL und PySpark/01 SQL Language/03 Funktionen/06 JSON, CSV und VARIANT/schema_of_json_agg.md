# `schema_of_json_agg` (Aggregatfunktion) — kombiniertes JSON-Schema einer Gruppe

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/schema_of_json_agg>
> Gilt für: Databricks SQL, Databricks Runtime **13.2 und höher**.

Gibt das kombinierte Schema aller JSON-Strings einer Gruppe im DDL-Format zurück.

## Syntax

```
schema_of_json_agg(jsonStr [, options] ) [FILTER ( WHERE cond ) ]
```

Diese Funktion kann auch als Window-Funktion über die `OVER`-Klausel aufgerufen werden.

## Argumente

- **`jsonStr`**: ein `STRING`-Literal mit JSON.
- **`options`**: ein optionales `MAP`-Literal, dessen Keys und Werte `STRING` sind. Details zu den Optionen siehe [`from_json`](from_json.md).
- **`cond`**: ein optionaler `BOOLEAN`-Ausdruck, der die für die Aggregation verwendeten Zeilen filtert.

## Rückgabe

Ein `STRING` mit der Definition eines Arrays von Structs mit `n` String-Feldern, deren Spaltennamen aus der eindeutigen Menge der JSON-Keys abgeleitet werden.

Das Schema jedes Datensatzes wird je Feldname gemergt. Haben gleichnamige Felder über Datensätze hinweg unterschiedliche Typen, verwendet Databricks die Least-Common-Type-Auflösung. Existiert kein solcher Typ, wird der Typ standardmäßig `STRING`.

## Beispiele

```sql
> SELECT schema_of_json_agg(a) FROM VALUES('{"foo": "bar"}') AS data(a);
STRUCT<foo: STRING>

> SELECT schema_of_json_agg(a) FROM VALUES('[1]') AS data(a);
ARRAY<BIGINT>

> CREATE TEMPORARY VIEW data(a) AS VALUES
  ('{"foo": "bar", "wing": {"ding": "dong"}}'),
  ('{"top": "level", "wing": {"stop": "go"}}')

> SELECT schema_of_json_agg(a) FROM data;
STRUCT<foo: STRING,top: STRING,wing: STRUCT<ding: STRING, stop: STRING>>
```

## Verwandte Funktionen

- [`from_json` function](from_json.md)
- [`schema_of_json` function](schema_of_json.md)
