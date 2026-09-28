# Der VARIANT-Datentyp

Der Datentyp `VARIANT` ermöglicht das Abfragen semi-strukturierter Daten (ab Databricks Runtime 15.4). Databricks empfiehlt `VARIANT` gegenüber JSON-Strings für semi-strukturierte Daten. Wichtige Einschränkung: `VARIANT`-Spalten können nicht als Clustering-Keys, Partitionen oder Z-Order-Keys verwendet werden.

## Variant-Spalten erzeugen

Mit `parse_json` lassen sich Variant-Spalten erzeugen:

```sql
%sql
CREATE TABLE store_data AS
SELECT parse_json('{...json content...}') as raw
```

Python-Äquivalent nutzt `parse_json(col("json"))` auf DataFrames.

## Variant-Felder abfragen

Mit der Funktion `variant_get` lassen sich Werte auslesen, z. B. `variant_get(col("raw"), "$.owner", "string")`.

SQL-Kurzschreibweisen:

- `:` für Top-Level-Felder: `raw:owner`
- `.` für verschachtelten Zugriff: `raw:store.bicycle`
- `[<index>]` für Arrays: `raw:store.fruit[0]`

## Sonderzeichen in Feldnamen

Mit Klammer-Notation und einfachen Anführungszeichen: `raw:['zip code']` oder `raw:['fb:testid']`. Das erlaubt beliebige Sonderzeichen im Feldnamen, einschließlich Leerzeichen, Punkten, Doppelpunkten und eckigen Klammern.

## Schema-Operationen

- `schema_of_variant()`: liefert das Schema eines einzelnen Variant-Werts.
- `schema_of_variant_agg()`: liefert das kombinierte Schema über eine Gruppe von Variant-Werten.

## Daten flach machen (Flattening)

Die Table-Valued-Function `variant_explode` expandiert Arrays und Objekte in mehrere Zeilen:

```sql
%sql
SELECT key, value FROM store_data,
  LATERAL variant_explode(store_data.raw);
```

## Typumwandlung

Mit `try_variant_get()` oder dem `::`-Operator:

```sql
%sql
SELECT try_variant_get(raw, '$.store.bicycle.price', 'double') as price FROM store_data
```

## Umgang mit NULL-Werten

Die Funktion `is_variant_null()` unterscheidet zwischen SQL-`NULL`-Werten und im Variant gespeicherten NULL-Werten. Ein Variant-NULL zeigt an, dass der Variant explizit einen NULL-Wert enthält.

## Python-Integration

Variant-Werte lassen sich als `VariantVal`-Objekte extrahieren, mit den Methoden `.toJson()` und `.toPython()` zur Konvertierung zwischen den Formaten.

---
**Quelle:** https://docs.databricks.com/aws/en/semi-structured/variant  
**Stand:** 2026-08-09
