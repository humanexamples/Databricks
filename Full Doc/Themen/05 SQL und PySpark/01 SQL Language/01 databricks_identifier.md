# Die `IDENTIFIER`-Klausel in Databricks

Die `IDENTIFIER`-Klausel in Databricks SQL wandelt einen String zur Laufzeit in einen **Bezeichner** um – also in einen Tabellen-, Spalten-, View-, Funktions-, Schema- oder Katalognamen.

**Zweck:** Sichere, SQL-Injection-freie Parametrisierung von Objektnamen. 
Statt Tabellen-/Spaltennamen unsicher per String-Konkatenation in eine Query einzubauen, schreibt man z. B.:



```python
DECLARE myschema = 'default';
SET VAR mytab = 'tab1';
DROP TABLE IDENTIFIER(myschema || '.' || mytab);
```

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### Names — Regel- und Delimited Identifiers (`sql-ref-identifiers`)

Ein nicht-delimited (unbegrenzter) Identifier darf nicht ausschließlich aus Ziffern bestehen, ansonsten sind auch führende Ziffern erlaubt. Delimited Identifiers (in Backticks) erlauben beliebige Unicode-Zeichen — ein Backtick im Namen selbst wird durch Verdopplung escaped:

```sql
DESCRIBE SELECT 5 AS 1st;          -- gültig: Ziffer am Anfang ohne Backticks
DESCRIBE SELECT 5 AS `a-b`;        -- Bindestrich nur mit Backticks erlaubt
DESCRIBE SELECT 5 AS `a b`;        -- Leerzeichen nur mit Backticks erlaubt
DESCRIBE SELECT 5 AS `a``b`;       -- escapter Backtick im Namen (verdoppelt)
```

### Names — Qualifizierung von Objektnamen (`sql-ref-names`)

Katalog-, Schema- und Tabellennamen lassen sich in Databricks SQL sowohl unqualifiziert als auch voll qualifiziert referenzieren; nicht-ASCII-Zeichen erfordern dabei stets Backticks:

```sql
USE CATALOG hive_metastore;
CREATE CATALOG `cat-a-log`;                 -- Bindestrich nur delimited
CREATE SCHEMA main.`a-b`;
SELECT * FROM hive_metastore.default.tab;   -- voll qualifiziert: Katalog.Schema.Tabelle
SELECT * FROM delta.`somedir/delta_table`;  -- pfadbasierte Tabelle (kein Katalogname)
```

### IDENTIFIER-Klausel — vollständige Referenz (`sql-ref-names-identifier-clause`)

> Gilt für: Databricks SQL, Databricks Runtime 13.3 LTS und höher.

Die `IDENTIFIER`-Klausel ermöglicht die **SQL-Injection-sichere Parametrisierung von Bezeichnern** in SQL-Anweisungen. Argumente bestehen dabei ausschließlich aus einem String-Literal oder einem String-Parametermarker (bzw. deren Verkettung) und werden zur Laufzeit als Bezeichner interpretiert.

**Einsetzbar an folgenden Stellen:**

- Subjektname in `CREATE`, `ALTER`, `DROP`, `UNDROP`
- Zieltabellenname in `MERGE`, `UPDATE`, `DELETE`, `INSERT`, `COPY INTO`
- Ziel von `SHOW` oder `DESCRIBE`
- Schema- oder Katalogreferenz in `USE`
- Funktionsaufrufe
- Spalten-, Tabellen- oder View-Referenzen in Abfragen (auch eingebettet in DDL oder DML)

> **Hinweis:** Wo die `IDENTIFIER`-Klausel nicht unterstützt wird und SQL-Injection kein Thema ist, kann stattdessen `EXECUTE IMMEDIATE` verwendet werden.

#### Syntax

```
IDENTIFIER ( strLiteral )
IDENTIFIER ( strExpr )
```

#### Parameter

- **`strLiteral`**: Ein `STRING`-Literal, das typischerweise aus einem oder mehreren String-Parametermarkern und literalen Bestandteilen zusammengesetzt (coalesced) ist.
- **`strExpr`**: Ein konstanter `STRING`-Ausdruck, typischerweise mit einem oder mehreren Parametermarkern. Ab Databricks Runtime 18.0 ist diese Schreibweise veraltet (deprecated); stattdessen werden nebeneinandergestellte Literale/Marker zusammengefasst.

#### Beispiele

```sql
-- Katalog über eine Variable setzen.
> DECLARE mycat = 'main';
> USE CATALOG IDENTIFIER(mycat);

-- Tabelle über eine Variable anlegen.
> DECLARE mytab = 'tab1';
> CREATE TABLE IDENTIFIER(mytab)(c1 INT);

-- Tabelle mit festem Schema und parametrisiertem Tabellennamen ändern.
> ALTER TABLE IDENTIFIER('default.' || mytab) ADD COLUMN c2 INT;

-- Dasselbe in DBR 18.0 und höher (nebeneinandergestellte Bestandteile):
> ALTER TABLE IDENTIFIER('default.' mytab) ADD COLUMN c2 INT;

-- Einfügen über einen parametrisierten Tabellennamen. Der Name ist qualifiziert und nutzt Backticks.
> SET VAR mytab = '`default`.`tab1`';
> INSERT INTO IDENTIFIER(mytab) VALUES(1, 2);

-- Parametrisierte Tabellenreferenz in einer Abfrage.
> SELECT * FROM IDENTIFIER(mytab);
  1   2

-- Tabelle mit getrennten Schema- und Tabellenparametern löschen.
> DECLARE myschema = 'default';
> SET VAR mytab = 'tab1';
> DROP TABLE IDENTIFIER(myschema || '.' || mytab);

-- In DBR 18.0 und höher:
> DROP TABLE IDENTIFIER(myschema '.' mytab);

-- Vor DBR 18.0 kann die IDENTIFIER-Klausel weder qualifiziert werden noch selbst als Qualifizierer dienen.
> SELECT * FROM myschema.IDENTIFIER('tab');
Error: PARSE_SYNTAX_ERROR

> SELECT * FROM IDENTIFIER('default').mytab;
Error: PARSE_SYNTAX_ERROR

-- Parametrisierte Spaltenreferenz.
> DECLARE col = 't.c1';
> SELECT IDENTIFIER(col) FROM VALUES(1) AS T(c1);
  1

-- Name einer Aggregatfunktion als Parameter übergeben.
> DECLARE agg = 'max';
> SELECT IDENTIFIER(agg)(c1) FROM VALUES(1), (2) AS T(c1);
  2
```

#### Verwandte Artikel

- `EXECUTE IMMEDIATE` — `sql-ref-syntax-aux-execute-immediate`
- Identifiers — `sql-ref-identifiers`
- Parameter markers — `sql-ref-parameter-marker`
- Names — `sql-ref-names`

**Quellen:**
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-identifiers
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-names-identifier-clause
