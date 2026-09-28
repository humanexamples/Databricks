# Semi-strukturierte Daten abfragen (JSON-Strings)

Databricks SQL erlaubt das Abfragen/Transformieren von als **JSON-Strings** gespeicherten semi-strukturierten Daten — **ohne die Dateien zu flatten**.

- **Empfehlung:** für optimale Performance verschachtelte Spalten mit korrekten Datentypen extrahieren.

## 1. Grundsyntax

```
<column-name>:<extraction-path>
```
`<column-name>`: String-Spalte. `<extraction-path>`: Zielfeld. Ergebnisse werden immer als **Strings** zurückgegeben.

## 2. Beispieltabelle (stark verschachtelt)

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

Alle folgenden Beispiele beziehen sich auf `store_data`.

## 3. Top-Level-Spalte extrahieren

- **Case-insensitiv (Standard):** Feldreferenzen ohne Klammern — `raw:owner` und `RAW:owner` funktionieren beide.
- **Case-sensitiv mit Klammern `[ ]`:** in Klammern referenzierte Spalten werden case-sensitiv abgeglichen.
- **Backticks** escapen Leerzeichen/Sonderzeichen im Feldnamen — Feldnamen bleiben dabei case-insensitiv; nur Klammern machen zusätzlich case-sensitiv.
- **Mehrdeutige Treffer:** liefert case-insensitives Matching mehrere passende Spalten, Fehler mit Aufforderung, Klammern zu verwenden.

```sql
SELECT raw:owner, RAW:owner FROM store_data;
-- Ergebnis: owner='amy', owner='amy'

SELECT raw:OWNER case_insensitive, raw:['OWNER'] case_sensitive FROM store_data;
-- Ergebnis: case_insensitive='amy', case_sensitive=NULL  (kein Feld "OWNER" exakt groß geschrieben)

SELECT raw:`zip code`, raw:`Zip Code`, raw:['fb:testid'] FROM store_data;
-- Ergebnis: '94025', '94025', '1234'
```

## 4. Verschachtelte Felder extrahieren

Punktnotation oder Klammern; bei Klammern case-sensitiv.

```sql
SELECT raw:store.bicycle FROM store_data;
-- Ergebnis: {"price":19.95,"color":"red"}

SELECT raw:store['bicycle'], raw:store['BICYCLE'] FROM store_data;
-- Ergebnis: {"price":19.95,"color":"red"}, NULL
```

## 5. Werte aus Arrays extrahieren

- **0-basierte Indizierung.**
- **Wildcard `*`** (gefolgt von Punkt-/Klammernotation): extrahiert Subfelder aus **allen** Array-Elementen.
- **Einschränkung:** `[*]` nur innerhalb eines JSON-Path-Ausdrucks gültig — **nicht** für native `ARRAY`-Spalten (Fehler `[INVALID_USAGE_OF_STAR_OR_REGEX]`) und **nicht** für `VARIANT`-Spalten. Bei Arrays von Structs stattdessen `array_column.field_name`, `transform` oder `explode` verwenden.

```sql
SELECT raw:store.fruit[0], raw:store.fruit[1] FROM store_data;
-- Ergebnis: {"weight":8,"type":"apple"}, {"weight":9,"type":"pear"}

SELECT raw:store.book[*].isbn FROM store_data;
-- Ergebnis: [null, "0-553-21311-3", "0-395-19395-8"] — erstes Buch hat kein isbn-Feld -> null

SELECT
    raw:store.basket[*],
    raw:store.basket[*][0] first_of_baskets,
    raw:store.basket[0][*] first_basket,
    raw:store.basket[*][*] all_elements_flattened,
    raw:store.basket[0][2].b subfield
FROM store_data;
-- Ergebnis:
-- basket[*]               = [[1,2,{"b":"y","a":"x"}],[3,4],[5,6]]
-- first_of_baskets        = [1,3,5]
-- first_basket            = [1,2,{"b":"y","a":"x"}]
-- all_elements_flattened  = [1,2,{"b":"y","a":"x"},3,4,5,6]
-- subfield                = "y"
```

## 6. Werte casten

- **`::`** castet in einfache Datentypen.
- **`from_json()`** castet verschachtelte Ergebnisse in komplexere Typen (Arrays, Structs).

```sql
SELECT raw:store.bicycle.price::double FROM store_data;
-- Ergebnis: 19.95  (DOUBLE statt String)

SELECT from_json(raw:store.bicycle, 'price double, color string') bicycle FROM store_data;
-- Ergebnis: bicycle = {price: 19.95, color: "red"}   (Struct<price:double,color:string>)

SELECT from_json(raw:store.basket[*], 'array<array<string>>') baskets FROM store_data;
-- Ergebnis: [["1","2","{\"b\":\"y\",\"a\":\"x\"}"],["3","4"],["5","6"]] — auch das verschachtelte Objekt wird zu einem String
```

**Verwandte Funktionen:** `:`-JSON-Path-Operator, `from_json`, `parse_json`, `schema_of_json`, Cast-Operatoren `::`/`CAST`.

## 7. NULL-Verhalten

JSON-Feld mit Wert `null` → Abfrage liefert **SQL-`NULL`**, **nicht** den Text `"null"`.

```sql
select '{"key":null}':key is null sql_null, '{"key":null}':key == 'null' text_null;
-- Ergebnis: sql_null = true, text_null = false
```

## 8. Verschachtelte Daten mit Spark-SQL-Operatoren transformieren

Apache Spark bietet zahlreiche eingebaute Funktionen für komplexe/verschachtelte Daten. Zusätzlich **Higher-Order Functions** für Arrays/Maps: `transform`, `filter`, `exists`, `reduce` (auf Array-Spalten).

**Stand:** 2026-09-14.
