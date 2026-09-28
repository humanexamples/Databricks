# JSON, CSV und VARIANT

## Der `VARIANT`-Datentyp

- `VARIANT` speichert `OBJECT`, `ARRAY` und Skalartypen. `STRUCT`/`MAP` → `VARIANT`: kein direkter Cast, `to_variant_object` verwenden (`MAP`-Keys müssen `STRING` sein).
- Iceberg v2 unterstützt keine `VARIANT`-Spalten; Iceberg v3 schon.
- Extraktion: `variant_get`/`try_variant_get` mit JSON-Path, der `:`-Operator, oder `cast`/`::`/`try_cast`.
- Typinspektion: `schema_of_variant` (einzelner Wert), `schema_of_variant_agg` (Sammlung).

```sql
SELECT parse_json('{"key": 123, "data": [4, 5, "str"]}');  -- {"data":[4,5,"str"],"key":123}
SELECT parse_json(null);                                    -- null
SELECT parse_json('123');                                   -- 123
SELECT CAST(123.456 AS VARIANT);                             -- 123.456
SELECT to_variant_object(map('key', 'val'));                 -- { "key": "val" }
SELECT to_variant_object(struct('field', 'val'));             -- { "field": "val" }
```

## `:` (Colon) — JSON-Path-Extraktion

**Syntax:** `jsonExpr : jsonPath`

- Funktioniert auf `VARIANT`-Ausdrücken **und** `STRING`-Ausdrücken mit gültigem JSON. Ergebnistyp entspricht dem Typ von `jsonExpr`.
- Ungültiges JSON oder ungültiger Pfad → `NULL`. Un-delimited JSON-`null` → SQL-`NULL`.

```sql
SELECT c1:price FROM VALUES('{ "price": 5 }') AS T(c1);                       -- 5
SELECT c1:['price']::decimal(5,2) FROM VALUES('{ "price": 5 }') AS T(c1);     -- 5.00

SELECT c1:item[1].price::double
FROM VALUES('{ "item": [ { "model":"basic","price":6.12 }, { "model":"medium","price":9.24 } ] }') AS T(c1);
-- 9.24

SELECT c1:item[*].price
FROM VALUES('{ "item": [ { "model":"basic","price":6.12 }, { "model":"medium","price":9.24 } ] }') AS T(c1);
-- [6.12,9.24]

SELECT from_json(c1:item[*], 'ARRAY<STRUCT<model STRING, price DOUBLE>>')
FROM VALUES('{ "item": [ { "model":"basic","price":6.12 }, { "model":"medium","price":9.24 } ] }') AS T(c1);
-- [{"model":"basic","price":6.12},{"model":"medium","price":9.24}]

SELECT PARSE_JSON('{ "price": 5 }'):price;              -- 5
SELECT PARSE_JSON('{ "price": 5 }'):price::decimal(5,2); -- 5.00
```

## `parse_json` — JSON-String in `VARIANT`

- Ungültiges JSON → `MALFORMED_RECORD_IN_PARSING` (`try_parse_json` gibt stattdessen `NULL`).
- `to_json` ist die logische (nicht exakte) Umkehrung: Whitespace nicht perfekt erhalten, Key-Reihenfolge kann sich ändern, nachlaufende Nullen entfernt (`{"a": 0.01000}` → `{"a": 0.01}`).

```sql
SELECT parse_json('{"key": 123, "data": [4, 5, "str"]}');  -- {"data":[4,5,"str"],"key":123}
SELECT parse_json('123');                                    -- 123 (auch Skalare sind gültig)
SELECT parse_json('{ bad }');                                -- Error: MALFORMED_RECORD_IN_PARSING
```

## `from_json` — JSON-String in Struct parsen

**Syntax:** `from_json(jsonStr, schema [, options])`

- `schema`: `STRING`-Literal (Spaltenname/Typ-Paare) oder `schema_of_json`; alternativ `NULL` für automatische Inferenz in Lakeflow-Pipelines via `schemaLocationKey`. Vor DBR 12.2 muss `schema` ein Literal sein.
  > Spalten-/Feldnamen sind **case-sensitiv** und müssen exakt zu `jsonStr` passen.
- `options` (`MAP<STRING,STRING>`): u. a. `primitivesAsString`, `prefersDecimal`, `allowComments`, `allowUnquotedFieldNames`, `allowSingleQuotes`, `mode`, `columnNameOfCorruptRecord`, `dateFormat`, `timestampFormat`, `multiLine`, `encoding`, `lineSep`, `samplingRatio`, `dropFieldIfAllNull`, `locale`.
- `mode => 'FAILFAST'` → `MALFORMED_RECORD_IN_PARSING` bei Schema-Abweichung.

```sql
SELECT from_json('{"a":1, "b":0.8}', 'a INT, b DOUBLE');
-- {"a":1,"b":0.8}

-- Spaltenname muss exakt der Groß-/Kleinschreibung des JSON-Feldes entsprechen
SELECT from_json('{"a":1}', 'A INT');
-- {"A":null}

SELECT from_json('{"datetime":"26/08/2015"}', 'datetime Timestamp',
  map('timestampFormat', 'dd/MM/yyyy'));
-- {"datetime":2015-08-26 00:00:00}

SELECT from_json('invalid', 'a INT', map('mode', 'FAILFAST'));
-- Error: MALFORMED_RECORD_IN_PARSING
```

## `from_csv` — CSV-String in Struct/Variant parsen

**Syntax:** `from_csv(csvStr, schema [, options])`

- `schema`: `STRING`-Literal oder `schema_of_csv`; ab DBR 16.4 auch ein einzelner `VARIANT`-Typ (liefert dann `VARIANT` statt `STRUCT`).
- `options`: u. a. `sep` (Default `,`), `encoding` (`UTF-8`), `quote` (`"`), `escape` (`\`), `header` (`false`), `enforceSchema` (`true`), `inferSchema`, `nullValue`, `emptyValue`, `dateFormat` (`yyyy-MM-dd`), `timestampFormat`, `maxColumns` (`20480`), `mode` (`PERMISSIVE`), `multiLine` (`false`).

```sql
SELECT from_csv('1, 0.8', 'a INT, b DOUBLE');
-- {1,0.8}

SELECT from_csv('26/08/2015', 'time Timestamp', map('timestampFormat', 'dd/MM/yyyy'));
-- {"time":2015-08-26 00:00:00}

SELECT from_csv('abc', 'a INT', map('mode', 'FAILFAST'));
-- Error: MALFORMED_RECORD_IN_PARSING
```

## Schema-Ableitung für einzelne Werte

| Funktion | Eingabe | Rückgabe |
|---|---|---|
| `schema_of_json(jsonStr [, options])` | JSON-String | Array-von-Structs-Definition mit String-Feldern; Spaltennamen aus JSON-Keys, Werte als abgeleitete SQL-Typen |
| `schema_of_csv(csv [, options])` | CSV-String | Struct-Beschreibung mit positionsbasierten Feldnamen `_c0`, `_c1`, … |
| `schema_of_variant(variantExpr)` | `VARIANT`-Ausdruck | Schema-Definition mit abgeleiteten SQL-Typen |

```sql
SELECT schema_of_json('[{"col":0}]');
-- ARRAY<STRUCT<`col`: BIGINT>>

DESCRIBE SELECT schema_of_csv('1,abc');
-- STRUCT<`_c0`: INT, `_c1`: STRING>

SELECT schema_of_variant(parse_json('{"key": 123, "data": [4, 5]}'));
-- OBJECT<data: ARRAY<BIGINT>, key: BIGINT>

-- Widersprüchliche Elementtypen im Array werden zu VARIANT
SELECT schema_of_variant(parse_json('{"data": [{"a":"a"}, 5]}'));
-- OBJECT<data: ARRAY<VARIANT>>

-- Kontrast: schema_of_variant() liefert den konkreten Typ, typeof() immer nur "variant"
SELECT schema_of_variant(123.4::VARIANT);   -- DECIMAL(4,1)
SELECT typeof(123.4::VARIANT);              -- VARIANT
```

## Ergebnisse in `from_json()`/`from_csv()` weiterverwenden

`schema_of_json` und `schema_of_csv` liefern DDL-Schema-Strings genau im Format, das `from_json` bzw. `from_csv` als `schema`-Parameter erwarten — beide Funktionsreferenzen nennen die jeweils andere explizit als gültigen `schema`-Wert: *"A STRING expression or invocation of schema_of_json function"* (`from_json`) bzw. *"A STRING literal or invocation of schema_of_csv function"* (`from_csv`). Man kann den Aufruf also direkt verschachteln, statt das Schema manuell abzutippen:

```sql
-- Schema aus einer Beispielzeile ableiten und direkt zum Parsen weiterer Zeilen nutzen
SELECT from_json('{"a":2, "b":1.5}', schema_of_json('{"a":1, "b":0.8}'));
-- {"a":2,"b":1.5}

SELECT from_csv('2, 1.5', schema_of_csv('1, 0.8'));
-- {2,1.5}
```

**Wichtige Einschränkung bei `from_json`:** Vor Databricks Runtime 12.2 musste `schema` ein reines Literal sein — `schema_of_json(...)` direkt als Argument war also **nicht** erlaubt und musste stattdessen vorab in einer Variablen berechnet werden. Seit DBR 12.2 ist die direkte Verschachtelung wie oben erlaubt.

**`schema_of_variant` ist anders zu benutzen:** Das Ergebnis nutzt die eigene `OBJECT<...>`-Notation für Variant-Schemata (statt `STRUCT<...>` bei `schema_of_json`/`schema_of_csv`) und ist **nicht** dafür dokumentiert, direkt als `schema`-Argument in `from_json`/`from_csv` eingesetzt zu werden. Der praktische Nutzen liegt eher im **Inspizieren**: Man ruft `schema_of_variant(...)` einmalig auf einem `VARIANT`-Wert auf, um dessen abgeleiteten Typ zu sehen, und leitet daraus bei Bedarf von Hand ein passendes `STRUCT<...>`-Schema für `from_json`/`CAST` ab — bzw. nutzt `schema_of_variant_agg` für das gemergte Schema einer ganzen Gruppe von Variant-Werten.

## Schema-Ableitung für Gruppen (Aggregatfunktionen)

`schema_of_json_agg` und `schema_of_variant_agg` liefern das **kombinierte** Schema aller Werte einer Gruppe (je Feld gemergt über *Least-Common-Type*). Kein gemeinsamer Typ → `schema_of_json_agg` fällt auf `STRING` zurück, `schema_of_variant_agg` auf `VARIANT` (z. B. `TIMESTAMP` + `STRING`). Beide unterstützen `FILTER (WHERE cond)` und `OVER` als Window-Funktion.

```sql
SELECT schema_of_json_agg(a) FROM VALUES('{"foo": "bar"}') AS data(a);
-- STRUCT<foo: STRING>

CREATE TEMPORARY VIEW data(a) AS VALUES
  ('{"foo": "bar", "wing": {"ding": "dong"}}'),
  ('{"top": "level", "wing": {"stop": "go"}}');
SELECT schema_of_json_agg(a) FROM data;
-- STRUCT<foo: STRING,top: STRING,wing: STRUCT<ding: STRING, stop: STRING>>

SELECT schema_of_variant_agg(a) FROM VALUES(parse_json('{"foo": "bar"}')) AS data(a);
-- OBJECT<foo: STRING>

CREATE TEMPORARY VIEW data2(a) AS VALUES
  (parse_json('{"foo": "bar", "wing": {"ding": "dong"}}')),
  (parse_json('{"wing": 123}'));
SELECT schema_of_variant_agg(a) FROM data2;
-- OBJECT<foo: STRING, wing: VARIANT>  -- wing: STRUCT vs. INT -> kein gemeinsamer Typ -> VARIANT
```

## Die `IDENTIFIER`-Klausel

**Syntax:** `IDENTIFIER(strLiteral)` bzw. `IDENTIFIER(strExpr)`

- Wandelt zur Laufzeit einen String in einen Bezeichner um (Tabellen-, Spalten-, View-, Funktions-, Schema-, Katalogname) — für **SQL-Injection-sichere Parametrisierung** von Objektnamen statt unsicherer String-Konkatenation.
- Einsetzbar als Subjektname in `CREATE`/`ALTER`/`DROP`/`UNDROP`, als Zieltabelle in `MERGE`/`UPDATE`/`DELETE`/`INSERT`/`COPY INTO`, als Ziel von `SHOW`/`DESCRIBE`, als Schema-/Katalogreferenz in `USE`, in Funktionsaufrufen, in Spalten-/Tabellen-/View-Referenzen.
- Vor DBR 18.0: `IDENTIFIER` kann weder selbst qualifiziert werden noch als Qualifizierer dienen (`myschema.IDENTIFIER('tab')` bzw. `IDENTIFIER('default').mytab` → `PARSE_SYNTAX_ERROR`). Alternative ohne SQL-Injection-Bedarf: `EXECUTE IMMEDIATE`.

```sql
-- Katalog über eine Variable setzen
DECLARE mycat = 'main';
USE CATALOG IDENTIFIER(mycat);

-- Tabelle über eine Variable anlegen
DECLARE mytab = 'tab1';
CREATE TABLE IDENTIFIER(mytab)(c1 INT);

-- Tabelle mit festem Schema und parametrisiertem Tabellennamen ändern
ALTER TABLE IDENTIFIER('default.' || mytab) ADD COLUMN c2 INT;

-- Tabelle mit getrennten Schema- und Tabellenparametern löschen
DECLARE myschema = 'default';
SET VAR mytab = 'tab1';
DROP TABLE IDENTIFIER(myschema || '.' || mytab);

-- Parametrisierte Spaltenreferenz
DECLARE col = 't.c1';
SELECT IDENTIFIER(col) FROM VALUES(1) AS T(c1);   -- 1

-- Name einer Aggregatfunktion als Parameter übergeben
DECLARE agg = 'max';
SELECT IDENTIFIER(agg)(c1) FROM VALUES(1), (2) AS T(c1);   -- 2
```

## Identifier-Regeln (Bezeichner-Syntax)

- Nicht-delimited Identifier darf nicht ausschließlich aus Ziffern bestehen; führende Ziffern sonst erlaubt.
- Delimited Identifiers (Backticks) erlauben beliebige Unicode-Zeichen; ein Backtick im Namen wird durch Verdopplung escaped.
- Nicht-ASCII-Zeichen erfordern stets Backticks.

```sql
DESCRIBE SELECT 5 AS 1st;          -- gültig: Ziffer am Anfang ohne Backticks
DESCRIBE SELECT 5 AS `a-b`;        -- Bindestrich nur mit Backticks erlaubt
DESCRIBE SELECT 5 AS `a b`;        -- Leerzeichen nur mit Backticks erlaubt
DESCRIBE SELECT 5 AS `a``b`;       -- escapter Backtick im Namen (verdoppelt)

USE CATALOG hive_metastore;
CREATE CATALOG `cat-a-log`;                 -- Bindestrich nur delimited
CREATE SCHEMA main.`a-b`;
SELECT * FROM hive_metastore.default.tab;   -- voll qualifiziert: Katalog.Schema.Tabelle
SELECT * FROM delta.`somedir/delta_table`;  -- pfadbasierte Tabelle (kein Katalogname)
```

**Stand:** 2026-09-14.
