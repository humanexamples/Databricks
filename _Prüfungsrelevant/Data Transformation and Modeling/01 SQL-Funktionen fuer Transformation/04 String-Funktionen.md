# String-Funktionen

## `COLLATE` — Vergleichs-/Sortierregeln für Strings

Legt fest, **wie** Strings verglichen und sortiert werden — u. a. Groß-/Kleinschreibung, Akzente und abschließende Leerzeichen. Wird unten bei mehreren Funktionen (`trim`, `substring_index`, `split`) für case-insensitives Matching verwendet.

**Syntax:**
```sql
-- Spaltenebene bei CREATE TABLE
CREATE TABLE catalog.schema.t (name STRING COLLATE UTF8_LCASE);

-- Ad-hoc in einer Abfrage/Expression
expr COLLATE collation_name
```

Verfügbar ab **Databricks Runtime 16.4 LTS** (spaltenweise Collations auf Delta-Lake-Tabellen); die `COLLATE`-Klausel selbst ab Databricks Runtime 16.1.

### `UTF8_BINARY` (Default)

Vergleicht zwei Strings **byteweise** anhand ihrer UTF-8-Repräsentation — case- **und** akzent-sensitiv. Wichtig dabei: Die Reihenfolge folgt den UTF-8-Byte-Werten, nicht dem Alphabet-Gefühl — Großbuchstaben liegen komplett **vor** den Kleinbuchstaben, und Umlaute/Akzentzeichen liegen sogar **hinter** allen Klein- und Großbuchstaben:

```sql
SELECT 'A' = 'a' COLLATE UTF8_BINARY;   -- false: unterschiedliche Bytes, kein Angleichen der Groß-/Kleinschreibung
SELECT 'Z' < 'a' COLLATE UTF8_BINARY;   -- true: 'Z' (Byte-Wert kleiner) liegt vor allen Kleinbuchstaben
SELECT 'z' < 'Ä' COLLATE UTF8_BINARY;   -- true: Umlaute liegen im UTF-8-Code hinter a-z/A-Z
```

### `UTF8_LCASE`

Wandelt **beide Seiten vor dem Vergleich in Kleinbuchstaben um** und vergleicht dann wieder byteweise (`UTF8_BINARY`). Dadurch wird Groß-/Kleinschreibung ignoriert — Akzente bleiben aber weiterhin relevant, weil das Lowercasing daran nichts ändert:

```sql
SELECT 'Café' = 'café' COLLATE UTF8_LCASE;   -- true: nur der Groß-/Kleinschreibungs-Unterschied wird ignoriert
SELECT 'Cafe' = 'café' COLLATE UTF8_LCASE;   -- false: 'e' vs. 'é' bleibt ein Unterschied, Akzente werden NICHT ignoriert
```

### `UNICODE`

Nutzt statt einem reinen Byte-Vergleich die ICU-Bibliothek für eine **sprachneutrale** Ordnung, die ähnliche Zeichen näher zusammen einsortiert (laut Doku z. B. `'a' < 'A' < 'Ä' < 'b'` — Umlaute stehen also bei ihrem Basis-Buchstaben, nicht ganz hinten wie bei `UTF8_BINARY`). `UNICODE` ist dabei **standardmäßig weiterhin case- und akzent-sensitiv** — dafür sind erst die Modifikatoren unten zuständig:

```sql
SELECT 'a' = 'A' COLLATE UNICODE;   -- false: UNICODE allein ist ohne Modifikator weiterhin case-sensitiv

-- Sortier-Unterschied zu UTF8_LCASE anhand desselben Datensatzes:
SELECT col FROM VALUES('Banana'), ('apple'), ('Ångström'), ('äpfel') AS t(col)
  ORDER BY col COLLATE UTF8_LCASE;
-- apple, Banana, Ångström, äpfel   (reine Byte-Sortierung: 'B' liegt vor den Umlauten)

SELECT col FROM VALUES('Banana'), ('apple'), ('Ångström'), ('äpfel') AS t(col)
  ORDER BY col COLLATE UNICODE_CI;
-- apple, Ångström, äpfel, Banana   (linguistische Ähnlichkeit: alle a-Varianten vor b)
```

### Sprachspezifische Collations (`DE`, `FR_CAN`, `zh_Hant_MAC`, ...)

Locale-basierte Sortierung über CLDR-Tabellen (Sprachcode, optional Skript- und Ländercode) — berücksichtigt landesspezifische Sortierregeln, z. B. wo Umlaute im jeweiligen Alphabet einsortiert werden:

```sql
-- Deutsche Vornamen nach deutscher Sortierregel statt purer Byte-Ordnung sortieren
SELECT vorname FROM mitarbeiter ORDER BY vorname COLLATE DE;

-- Sprache + Modifikatoren kombiniert: 'Ä', 'A' und 'a' gelten dann alle als gleich
SELECT 'Ä' = 'a' COLLATE de_CI_AI;   -- true
```

### Modifikatoren (`CS`, `CI`, `AS`, `AI`, `RTRIM`)

Werden an `UNICODE` oder eine Locale angehängt (nicht an `UTF8_BINARY`/`UTF8_LCASE`). `CS` und `AS` sind jeweils das **Standardverhalten** und müssen normalerweise nicht explizit angegeben werden; `CI`/`AI`/`RTRIM` schalten das jeweilige Verhalten gezielt ab. Es ist höchstens einer von `CS`/`CI` und höchstens einer von `AS`/`AI` gleichzeitig erlaubt.

- **`CI`** — case-insensitiv, Akzente bleiben aber relevant:
  ```sql
  SELECT 'Café' = 'café' COLLATE UNICODE_CI;   -- true: nur Groß-/Kleinschreibung wird ignoriert
  SELECT 'Café' = 'cafe' COLLATE UNICODE_CI;   -- false: der Akzent-Unterschied bleibt bestehen
  ```
- **`AI`** — akzent-insensitiv, meist mit `CI` kombiniert (`_CI_AI`), damit **beides** ignoriert wird:
  ```sql
  SELECT 'Cafe' = 'café' COLLATE UNICODE_CI_AI;     -- true: Groß-/Kleinschreibung UND Akzent werden ignoriert
  SELECT 'resume' = 'résumé' COLLATE UNICODE_CI_AI; -- true: typischer Anwendungsfall für Volltext-/Nutzersuche
  ```
- **`RTRIM`** — ignoriert abschließende Leerzeichen (nicht führende!) beim Vergleich:
  ```sql
  SELECT 'hello' = 'hello   ' COLLATE UNICODE_RTRIM;   -- true
  ```

**Grenze von `CI`/`AI`:** Das ist keine vollständige sprachliche Normalisierung — laut Doku bleibt z. B. `'ß' = 'ss'` (deutsches scharfes S) auch mit `UNICODE_CI_AI` **`false`**, obwohl beide umgangssprachlich oft als gleichwertig gelten.

**Einschränkung:** `LIKE`, `ILIKE`, `RLIKE` und die `regexp_*`-Funktionen unterstützen **nur** `UTF8_BINARY` und `UTF8_LCASE` — mit `UNICODE`/Locale-Collations werfen sie einen Fehler. Für Mustersuche auf so kollationierten Spalten stattdessen `contains()`, `startswith()` oder `endswith()` verwenden.

## `concat` — Argumente verketten

**Syntax:** `concat(expr1, expr2 [, ...])` — Synonym für `||`.

- Alle Argumente müssen entweder alle `STRING`, alle `BINARY` oder alle `ARRAY`s von `STRING`/`BINARY` sein. Mind. ein Argument nötig.
- Array-Verkettung über dem Größenlimit → `COLLECTION_SIZE_LIMIT_EXCEEDED`.

```sql
SELECT concat('Spark', 'SQL');                          -- SparkSQL
SELECT concat(array(1, 2, 3), array(4, 5), array(6));    -- [1,2,3,4,5,6]
```

## `concat_ws` — Strings mit Trennzeichen verketten

**Syntax:** `concat_ws(sep [, expr1 [, ...]])` — `exprN`: `STRING` oder `ARRAY` von `STRING`.

- `sep = NULL` → Ergebnis `NULL`.
- `NULL`-Werte unter `exprN` werden **ignoriert** (anders als bei `concat`, wo ein `NULL`-Argument das Gesamtergebnis zu `NULL` machen kann).
- Nur Separator angegeben oder alle `exprN` `NULL` → leerer String.

```sql
SELECT concat_ws(' ', 'Spark', 'SQL');                          -- Spark SQL
SELECT concat_ws('s');                                          -- '' (leerer String)
SELECT concat_ws(',', 'Spark', array('S', 'Q', NULL, 'L'), NULL); -- Spark,S,Q,L
```

## `upper` / `lower` — Groß-/Kleinschreibung

**Syntax:** `upper(expr)` (Synonym `ucase`), Gegenstück `lower`. Berücksichtigt die Collation von `expr`.

```sql
SELECT upper('SparkSql');    -- SPARKSQL
```

## `trim` — Zeichen am Rand entfernen

**Syntax:**
```sql
trim(str)
trim(BOTH | LEADING | TRAILING FROM str)
trim(trimStr FROM str)
trim(BOTH | LEADING | TRAILING trimStr FROM str)
```

- Ohne `trimStr`: führende/abschließende Leerzeichen. Mit `trimStr`: dessen Zeichen. `BOTH`/`LEADING`/`TRAILING` steuert die Seite (Default `BOTH`).
- Collation beeinflusst das Matching der zu entfernenden Zeichen.
- Verwandte Funktionen: `ltrim`, `rtrim`, `btrim`, `lpad`, `rpad`.

```sql
SELECT '+' || trim('    SparkSQL   ') || '+';                  -- +SparkSQL+
SELECT '+' || trim(LEADING FROM '    SparkSQL   ') || '+';     -- +SparkSQL   +
SELECT '+' || trim(TRAILING FROM '    SparkSQL   ') || '+';    -- +    SparkSQL+
SELECT trim('SL' FROM 'SSparkSQLS');                            -- parkSQ
SELECT trim(LEADING 'SL' FROM 'SSparkSQLS');                    -- parkSQLS
SELECT trim(TRAILING 'SL' FROM 'SSparkSQLS');                   -- SSparkSQ

-- Collation beeinflusst das Matching der zu entfernenden Zeichen
SELECT trim(BOTH 'sl' COLLATE UTF8_BINARY FROM 'SSparkSQLS');   -- SSparkSQLS (kein Treffer, case-sensitiv)
SELECT trim(BOTH 'sl' COLLATE UTF8_LCASE FROM 'SSparkSQLS');    -- parkSQ (case-insensitiv)
```

## `substr` / `substring` — Teilzeichenkette

**Syntax (Synonyme):**
```sql
substr(expr, pos [, len])
substr(expr FROM pos [FOR len])
substring(expr, pos [, len])
substring(expr FROM pos [FOR len])
```

- `expr`: `BINARY`/`STRING`. `pos`: **1-basiert**; negativ → vom Ende gezählt.
- `len`: optional; `len < 1` → leeres Ergebnis; ohne `len` alle Zeichen/Bytes ab `pos`.

```sql
SELECT substr('Spark SQL', 5);              -- k SQL
SELECT substr('Spark SQL', -3);              -- SQL
SELECT substr('Spark SQL', 5, 1);            -- k
SELECT substr('Spark SQL' FROM -10 FOR 5);   -- Spar
```

## `substring_index` — Teilzeichenkette vor dem n-ten Trenner

**Syntax:** `substring_index(expr, delim, count)`

- `count` positiv → alles **links** vom letzten (von links gezählten) Trenner.
- `count` negativ → alles **rechts** vom letzten (von rechts gezählten) Trenner.
- Collation beeinflusst das Matching des Trennzeichens.

```sql
SELECT substring_index('www.apache.org', '.', 2);   -- www.apache
SELECT substring_index('555A66A777' COLLATE UTF8_BINARY, 'a', 2);  -- 555A66A777 (kein Treffer, case-sensitiv)
SELECT substring_index('555A66A777' COLLATE UTF8_LCASE, 'a', 2);   -- 555A66 (case-insensitiv)
```

## `split` — String anhand Regex in Array teilen

**Syntax:** `split(str, regex [, limit])`

- `limit`: Default `0` (kein Limit). `limit > 0` → höchstens `limit` Elemente, letztes Element enthält den Rest. `limit <= 0` → Regex wird so oft wie möglich angewendet.
- Verwandte Funktionen: `regexp_extract`, `regexp_extract_all`, `split_part`.

```sql
SELECT split('oneAtwoBthreeC', '[ABC]');          -- [one,two,three,]
SELECT split('apple,banana,cherry', ',');          -- [apple,banana,cherry]
SELECT split('the   quick  brown', r'\s+');        -- [the,quick,brown]
SELECT split('oneAtwoBthreeC', '[ABC]', 2);        -- [one,twoBthreeC]
SELECT split('oneAtwoBthreeC', '[ABC]', -1);       -- [one,two,three,]

-- Collation beeinflusst das Matching
SELECT split('oneAtwoBthreeC' COLLATE UTF8_BINARY, '[abc]');   -- [oneAtwoBthreeC] (kein Treffer)
SELECT split('oneAtwoBthreeC' COLLATE UTF8_LCASE, '[abc]');    -- [one,two,three,]
```

## `base64` / `unbase64` — Base64 kodieren/dekodieren

**Syntax:**
```sql
base64(expr)     -- BINARY/STRING -> STRING (Base64-kodiert, RFC2045)
unbase64(expr)    -- STRING (Base64) -> BINARY
```

- `base64`: `expr` ist `BINARY` oder `STRING` (wird dabei als `BINARY` interpretiert); Ergebnis ein `STRING` in Base64-Darstellung.
- `unbase64`: liefert `BINARY` zurück — für lesbaren Text zusätzlich `CAST(... AS STRING)` nötig (setzt UTF-8-Inhalt voraus).

```sql
SELECT base64('Spark SQL');                        -- U3BhcmsgU1FM
SELECT unbase64('U3BhcmsgU1FM');                    -- BINARY-Wert, nicht direkt lesbar
SELECT cast(unbase64('U3BhcmsgU1FM') AS STRING);    -- Spark SQL
```

## `hex` / `unhex` — Hexadezimal kodieren/dekodieren

**Syntax:**
```sql
hex(expr)     -- BIGINT/BINARY/STRING -> STRING (Hex-Darstellung)
unhex(expr)   -- STRING (Hex) -> BINARY
```

- `hex`: akzeptiert `BIGINT`, `BINARY` oder `STRING`; liefert die hexadezimale Darstellung als `STRING`.
- `unhex`: dekodiert einen Hex-`STRING` zurück zu `BINARY`. Bei **ungerader** Zeichenzahl wird das erste Zeichen verworfen und das Ergebnis mit einem Null-Byte aufgefüllt; enthält der String Nicht-Hex-Zeichen, liefert die Funktion `NULL`.

```sql
SELECT hex(17);                 -- 11
SELECT hex('Spark SQL');        -- 537061726B2053514C
SELECT unhex('537061726B2053514C');                       -- BINARY-Wert, nicht direkt lesbar
SELECT decode(unhex('537061726B2053514C'), 'UTF-8');      -- Spark SQL
```

**Stand:** 2026-09-17.
