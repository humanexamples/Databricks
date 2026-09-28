# `VARIANT`-Typ (SQL-Datentyp-Referenz)

> **Gilt für:** Databricks SQL, Databricks Runtime 15.3 und höher.

Der `VARIANT`-Typ repräsentiert **semi-strukturierte Daten**.

> **Hinweis:** *"Iceberg v2 tables do not support `VARIANT` columns. Apache Iceberg v3 supports `VARIANT` columns."*

---

## Syntax

```
VARIANT
```

## Limits

Der Typ unterstützt das Speichern semi-strukturierter Daten als `OBJECT`, `ARRAY` und **Skalartypen**. Um `STRUCT` und `MAP` zu speichern, die Funktion **`to_variant_object`** verwenden. `MAP`-Schlüssel müssen vom Typ `STRING` sein.

## Literale

Details zum Erzeugen eines `VARIANT`-Werts stehen in der Doku zur **`parse_json`**-Funktion. Alternativ lässt sich ein Literal mit **`CAST`** in `VARIANT` umwandeln.

## Notes

**Werte aus einem `VARIANT` extrahieren:**

- `variant_get` mit einem JSON-Path-Ausdruck
- der `:`-Operator, um mit einem JSON-Path zu parsen
- `try_variant_get` für Fehlertoleranz
- `cast` bzw. der `::`-Operator, um in konkrete Typen zu konvertieren
- `try_cast` für Typkonvertierung mit Fehlerbehandlung

**`VARIANT`-Typinformationen inspizieren:**

- `schema_of_variant` für einzelne Werte
- `schema_of_variant_agg` für Sammlungen von Werten

---

## Beispiele

```sql
> SELECT parse_json('{"key": 123, "data": [4, 5, "str"]}');
  {"data":[4,5,"str"],"key":123}

> SELECT parse_json(null);
  null

> SELECT parse_json('123');
  123

> SELECT CAST(123.456 AS VARIANT);
  123.456

> SELECT to_variant_object(map('key', 'val'));
  { "key": "val" }

> SELECT to_variant_object(struct('field', 'val'));
  { "field": "val" }
```

---

## Verwandte Funktionen / Operatoren

- `::`-Operator
- `cast`-Funktion
- `parse_json`-Funktion
- `schema_of_variant`-Funktion
- `schema_of_variant_agg`-Aggregatfunktion
- `try_cast`-Funktion
- `try_variant_get`-Funktion
- `variant_get`-Funktion

> Einzelreferenzen unter `../03 Funktionen/`: [`parse_json`](../03%20Funktionen/06%20JSON,%20CSV%20und%20VARIANT/parse_json.md) · [`schema_of_variant`](../03%20Funktionen/06%20JSON,%20CSV%20und%20VARIANT/schema_of_variant.md) · [`schema_of_variant_agg`](../03%20Funktionen/06%20JSON,%20CSV%20und%20VARIANT/schema_of_variant_agg.md) · [`typeof`](../03%20Funktionen/01%20Cast%20und%20Typkonvertierung/typeof.md) · [`cast`](../03%20Funktionen/01%20Cast%20und%20Typkonvertierung/cast.md) · [`::`](../03%20Funktionen/01%20Cast%20und%20Typkonvertierung/coloncolonsign.md) · [`?::`](../03%20Funktionen/01%20Cast%20und%20Typkonvertierung/questiondoublecolonsign.md) · [`isnull`](../03%20Funktionen/03%20NULL-Behandlung/isnull.md) / [`isnotnull`](../03%20Funktionen/03%20NULL-Behandlung/isnotnull.md) (VARIANT-Verhalten).

---

## Verwandte Themen im Projekt

- **Delta-/Iceberg-Tabellenfeature, Aktivierung, Einschränkungen, Hintergrund/Blog:** [15 Variant.md](../../01%20Platform/02%20Tables/07%20Table%20Features/15%20Variant.md)
- **Variant Shredding (Performance):** [16 Variant Shredding.md](../../01%20Platform/02%20Tables/07%20Table%20Features/16%20Variant%20Shredding.md)
- **Semi-strukturierte Daten abfragen (`:`-Operator, `from_json`):** [01 JSON-Strings abfragen.md](../../12%20Query%20Data/02%20Semi-strukturierte%20Daten/01%20JSON-Strings%20abfragen.md)

---

## Quellen

- VARIANT type — SQL-Datentyp-Referenz: https://docs.databricks.com/aws/en/sql/language-manual/data-types/variant-type

**Stand:** 2026-09-02.
