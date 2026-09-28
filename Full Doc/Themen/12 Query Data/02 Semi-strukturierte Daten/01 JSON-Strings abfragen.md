# JSON-Strings abfragen

> Quelle: <https://docs.databricks.com/aws/en/semi-structured/json>

Dieser Artikel beschreibt die Databricks-SQL-Operatoren, mit denen sich **semi-strukturierte Daten**, die als JSON-Strings gespeichert sind, abfragen und transformieren lassen. Man kann semi-strukturierte Daten lesen, ohne die Dateien zu flatten.

> **Empfehlung:** Für optimale Performance sollten verschachtelte Spalten mit den korrekten Datentypen extrahiert werden.

## Syntax

Das Grundmuster für die Extraktion lautet:

```
<column-name>:<extraction-path>
```

Dabei ist `<column-name>` eine String-Spalte und `<extraction-path>` verweist auf das Zielfeld. Ergebnisse werden als **Strings** zurückgegeben.

---

## Tabelle mit stark verschachtelten Daten anlegen

```sql
CREATE TABLE store_data AS SELECT
'{
   "store":{
      "fruit": [
        {"weight":8,"type":"apple"},
        {"weight":9,"type":"pear"}
      ],
      "basket":[
        [1,2,{"b":"y","a":"x"}],
        [3,4],
        [5,6]
      ],
      "book":[
        {
          "author":"Nigel Rees",
          "title":"Sayings of the Century",
          "category":"reference",
          "price":8.95
        },
        {
          "author":"Herman Melville",
          "title":"Moby Dick",
          "category":"fiction",
          "price":8.99,
          "isbn":"0-553-21311-3"
        },
        {
          "author":"J. R. R. Tolkien",
          "title":"The Lord of the Rings",
          "category":"fiction",
          "reader":[
            {"age":25,"name":"bob"},
            {"age":26,"name":"jack"}
          ],
          "price":22.99,
          "isbn":"0-395-19395-8"
        }
      ],
      "bicycle":{
        "price":19.95,
        "color":"red"
      }
    },
    "owner":"amy",
    "zip code":"94025",
    "fb:testid":"1234"
 }' as raw
```

---

## Eine Top-Level-Spalte extrahieren

Regeln für die Feld-Extraktion:

- **Case-insensitiv (Standard):** Feldreferenzen ohne Klammern werden case-insensitiv abgeglichen – `raw:owner` und `RAW:owner` funktionieren beide.
- **Case-sensitiv mit Klammern `[ ]`:** In Klammern referenzierte Spalten werden case-sensitiv abgeglichen.
- **Backticks für Sonderzeichen:** Backticks escapen Leerzeichen und Sonderzeichen; die Feldnamen werden dabei case-insensitiv abgeglichen. Klammern machen sie case-sensitiv.
- **Mehrdeutige Treffer:** Enthält ein JSON-Datensatz durch case-insensitives Matching mehrere passende Spalten, kommt es zu einem Fehler mit der Aufforderung, Klammern zu verwenden.

```sql
SELECT raw:owner, RAW:owner FROM store_data
```

```sql
SELECT raw:OWNER case_insensitive, raw:['OWNER'] case_sensitive FROM store_data
```

```sql
SELECT raw:`zip code`, raw:`Zip Code`, raw:['fb:testid'] FROM store_data
```

---

## Verschachtelte Felder extrahieren

Verschachtelte Felder werden über **Punktnotation** oder **Klammern** angesprochen. Bei Klammern werden Spalten case-sensitiv abgeglichen.

```sql
SELECT raw:store.bicycle FROM store_data
```

```sql
SELECT raw:store['bicycle'], raw:store['BICYCLE'] FROM store_data
```

---

## Werte aus Arrays extrahieren

- **0-basierte Indizierung:** Indizes beginnen bei `0`.
- **Wildcard-Extraktion:** Ein Sternchen `*` gefolgt von Punkt- oder Klammernotation extrahiert Subfelder aus allen Elementen eines Arrays.
- **Einschränkung:** Die `[*]`-Syntax ist nur innerhalb eines JSON-Path-Ausdrucks gültig. Sie wird **nicht** unterstützt für native `ARRAY`-Spalten (Fehler `[INVALID_USAGE_OF_STAR_OR_REGEX]`) und **nicht** für `VARIANT`-Spalten. Bei Arrays von Structs stattdessen `array_column.field_name`, `transform` oder `explode` verwenden.

```sql
SELECT raw:store.fruit[0], raw:store.fruit[1] FROM store_data
```

```sql
SELECT raw:store.book[*].isbn FROM store_data
```

```sql
SELECT
    raw:store.basket[*],
    raw:store.basket[*][0] first_of_baskets,
    raw:store.basket[0][*] first_basket,
    raw:store.basket[*][*] all_elements_flattened,
    raw:store.basket[0][2].b subfield
FROM store_data
```

---

## Werte casten

- **Basistypen:** `::` castet Werte in einfache Datentypen.
- **Komplexe Typen:** `from_json()` castet verschachtelte Ergebnisse in komplexere Datentypen wie Arrays oder Structs.

> Funktions-Einzelreferenzen: `../../05 SQL Language/03 Funktionen/` — u. a. [`:` (JSON-Path)](../../05%20SQL%20Language/03%20Funktionen/06%20JSON,%20CSV%20und%20VARIANT/colonsign.md), [`from_json`](../../05%20SQL%20Language/03%20Funktionen/06%20JSON,%20CSV%20und%20VARIANT/from_json.md), [`parse_json`](../../05%20SQL%20Language/03%20Funktionen/06%20JSON,%20CSV%20und%20VARIANT/parse_json.md), [`schema_of_json`](../../05%20SQL%20Language/03%20Funktionen/06%20JSON,%20CSV%20und%20VARIANT/schema_of_json.md), [`::`](../../05%20SQL%20Language/03%20Funktionen/01%20Cast%20und%20Typkonvertierung/coloncolonsign.md), [`cast`](../../05%20SQL%20Language/03%20Funktionen/01%20Cast%20und%20Typkonvertierung/cast.md).

```sql
SELECT raw:store.bicycle.price::double FROM store_data
```

```sql
SELECT from_json(raw:store.bicycle, 'price double, color string') bicycle FROM store_data
```

```sql
SELECT from_json(raw:store.basket[*], 'array<array<string>>') baskets FROM store_data
```

---

## NULL-Verhalten

Wenn ein JSON-Feld mit dem Wert `null` existiert, liefert die Abfrage einen **SQL-`NULL`**-Wert für diese Spalte zurück – nicht den Text `"null"`.

```sql
select '{"key":null}':key is null sql_null, '{"key":null}':key == 'null' text_null
```

---

## Verschachtelte Daten mit Spark-SQL-Operatoren transformieren

Apache Spark bietet zahlreiche eingebaute Funktionen für die Arbeit mit komplexen und verschachtelten Daten. Zusätzlich stellen **Higher-Order Functions** weitere Transformationsmöglichkeiten bereit.

---

## Verwandte Themen

- [JSON-Dateien lesen und schreiben](../01%20Dateiformate/02%20JSON%20lesen%20und%20schreiben.md)
- Higher-Order Functions (Spark SQL)
