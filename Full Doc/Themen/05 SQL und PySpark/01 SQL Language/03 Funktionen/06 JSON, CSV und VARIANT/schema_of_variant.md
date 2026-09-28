# `schema_of_variant` — Schema eines `VARIANT`-Ausdrucks

> Quelle: <https://docs.databricks.com/aws/en/sql/language-manual/functions/schema_of_variant>
> Gilt für: Databricks SQL, Databricks Runtime **15.3 und höher**.

Gibt das Schema eines `VARIANT`-Ausdrucks im DDL-Format zurück.

## Syntax

```
schema_of_variant ( variantExpr )
```

## Argumente

- **`variantExpr`**: ein `VARIANT`-Ausdruck.

## Rückgabe

Ein `STRING` mit einer Schema-Definition von `variantExpr`. Die Typen im Schema sind die abgeleiteten formatierten SQL-Typen.

## Notes

Bei der Bestimmung des Schemas für ein `ARRAY<elementType>` kann `elementType` als `VARIANT` inferiert werden, wenn in den Daten widersprüchliche Typen gefunden werden.

Für das aggregierte Schema einer Sammlung von `VARIANT`-Werten die Aggregatfunktion [`schema_of_variant_agg`](schema_of_variant_agg.md) verwenden.

## Beispiele

```sql
-- Einfaches Beispiel
> SELECT schema_of_variant(parse_json('{"key": 123, "data": [4, 5]}'))
  OBJECT<data: ARRAY<BIGINT>, key: BIGINT>

-- Widersprüchliche Elementtypen im Array
> SELECT schema_of_variant(parse_json('{"data": [{"a":"a"}, 5]}'))
  OBJECT<data: ARRAY<VARIANT>>

-- Ein typisiertes Literal
> SELECT schema_of_variant(123.4::VARIANT);
  DECIMAL(4,1)

-- Kontrast schema_of_variant() vs. typeof()
> SELECT typeof(123.4::VARIANT);
  VARIANT
```

## Verwandte Funktionen

- [`schema_of_variant_agg` aggregate function](schema_of_variant_agg.md)
- [`schema_of_json` function](schema_of_json.md)
- [`schema_of_csv` function](schema_of_csv.md)
- `schema_of_xml` function
- [`typeof` function](../01%20Cast%20und%20Typkonvertierung/typeof.md)
