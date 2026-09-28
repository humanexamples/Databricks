# `schema_of_variant_agg` (Aggregatfunktion) — kombiniertes `VARIANT`-Schema einer Gruppe

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/schema_of_variant_agg>
> Gilt für: Databricks SQL, Databricks Runtime **15.3 und höher**.

Gibt das kombinierte Schema aller `VARIANT`-Werte einer Gruppe im DDL-Format zurück.

## Syntax

```
schema_of_variant_agg ( variantExpr ) [FILTER ( WHERE cond ) ]
```

## Argumente

- **`variantExpr`**: ein `VARIANT`-Ausdruck.
- **`cond`**: ein optionaler `BOOLEAN`-Ausdruck, der die für die Aggregation verwendeten Zeilen filtert.

## Rückgabe

Ein `STRING` mit einer Schema-Definition. Haben Felder über Datensätze hinweg denselben Namen, aber unterschiedliche Typen, wendet Databricks Typ-Coercion über den Least Common Type an. Existiert kein gemeinsamer Typ, wird das Feld `VARIANT` (z. B. mergen `TIMESTAMP` und `STRING` zu `VARIANT`).

## Beispiele

```sql
> SELECT schema_of_variant_agg(a) FROM VALUES(parse_json('{"foo": "bar"}')) AS data(a);
OBJECT<foo: STRING>

> SELECT schema_of_variant_agg(a) FROM VALUES(parse_json('[1]')) AS data(a);
ARRAY<BIGINT>

> CREATE TEMPORARY VIEW data(a) AS VALUES
  (parse_json('{"foo": "bar", "wing": {"ding": "dong"}}')),
  (parse_json('{"wing": 123}'));
> SELECT schema_of_variant_agg(a) FROM data;
OBJECT<foo: STRING, wing: VARIANT>
```

## Verwandte Funktionen

- [`schema_of_variant` function](schema_of_variant.md)
- [`schema_of_json_agg` aggregate function](schema_of_json_agg.md)
