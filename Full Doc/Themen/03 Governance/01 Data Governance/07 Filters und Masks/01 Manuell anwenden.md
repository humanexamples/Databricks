# Row Filter und Column Masks manuell anwenden

## Voraussetzungen

- Ein für Unity Catalog aktivierter Workspace.
- SQL-UDFs, in Unity Catalog registriert (Python-/Scala-Logik muss in eine SQL-UDF verpackt werden).
- Privilegien: `EXECUTE` auf der Funktion, `USE SCHEMA`, `USE CATALOG`.
- Für bestehende Tabellen: Eigentümerstatus, oder sowohl `MANAGE` als auch `SELECT`.
- Compute: SQL-Warehouses, Standard Access Mode (Runtime 12.2+), oder Dedicated Access Mode (Runtime 15.4+).

## Row Filter

Jede Tabelle unterstützt maximal **einen** Row Filter.

```sql
CREATE FUNCTION <function_name> (<parameter_name> <parameter_type>, ...)
RETURN {Filterausdruck, dessen Ergebnis ein Boolean sein muss};

ALTER TABLE <table_name> SET ROW FILTER <function_name> ON (<column_name>, ...);
```

**Beispiel — Zugriff nach Region:**

```sql
CREATE FUNCTION us_filter(region STRING)
RETURN IF(IS_ACCOUNT_GROUP_MEMBER('admin'), true, region='US');

ALTER TABLE sales SET ROW FILTER us_filter ON (region);
```

Admins sehen alle Zeilen uneingeschränkt; alle anderen Nutzer sehen nur Datensätze mit `region = 'US'`.

**Entfernen:**

```sql
ALTER TABLE <table_name> DROP ROW FILTER;
```

## Column Mask

```sql
CREATE FUNCTION <function_name> (<parameter_name> <parameter_type>, ...)
RETURN {Ausdruck mit demselben Typ wie der erste Parameter};

ALTER TABLE <table_name> ALTER COLUMN <col_name> SET MASK <mask_func_name> USING COLUMNS <additional_columns>;
```

**Beispiel — SSN maskieren:**

```sql
CREATE FUNCTION ssn_mask(ssn STRING)
RETURN CASE WHEN is_account_group_member('HumanResourceDept') THEN ssn ELSE '***-**-****' END;

ALTER TABLE users ALTER COLUMN ssn SET MASK ssn_mask;
```

### Python-UDF als Wrapper

Python-Logik muss über eine SQL-Wrapper-Funktion angewendet werden, nicht direkt:

```sql
CREATE FUNCTION email_mask_python(email STRING)
RETURNS STRING
LANGUAGE PYTHON
AS $$
import re
return re.sub(r'^[^@]+', lambda m: '*' * len(m.group()), email)
$$;

CREATE FUNCTION email_mask_sql(email STRING)
RETURN email_mask_python(email);
```

Angewendet wird der SQL-Wrapper (`email_mask_sql`), nicht die Python-UDF direkt.

### Bedingte Maskierung mit `USING COLUMNS`

```sql
CREATE FUNCTION mask_address_by_country(address STRING, country STRING, group_suffix STRING DEFAULT '_address_viewers')
RETURN IF(
  is_account_group_member(country || group_suffix),
  address,
  'REDACTED');

ALTER TABLE customers
ALTER COLUMN address
SET MASK mask_address_by_country USING COLUMNS (country, '_address_viewers');
```

## Mapping-Tabellen (Zugriffslisten)

Tabellen, die festlegen, welche Zeilen für bestimmte Nutzer/Gruppen zugänglich sind:

```sql
CREATE TABLE valid_users(username string);
INSERT INTO valid_users VALUES ('fred@databricks.com'), ('barney@databricks.com');

CREATE FUNCTION row_filter()
RETURN EXISTS(
  SELECT 1 FROM valid_users v
  WHERE v.username = SESSION_USER());
```

**Wichtiger Hinweis:** Alle Filter laufen mit den Rechten des Definierers ("definer's rights") — außer Funktionen, die den Nutzerkontext prüfen (z. B. `SESSION_USER`, `IS_ACCOUNT_GROUP_MEMBER`); diese laufen mit den Rechten des Aufrufers ("invoker's rights").

## Weiteres Beispiel aus Kursmaterial

Aus einer privaten Kursnotiz übernommen — zeigt dasselbe Muster (Row Filter + Column Mask über `is_account_group_member()`) an einem zweiten, eigenständigen Beispiel: einem Row Filter, der den Kundenstamm nach Treuestufe einschränkt, und einer Column Mask, die eine numerische ID durch einen Platzhalter ersetzt statt sie textuell zu maskieren.

```sql
-- Row Filter: Mitglieder der Gruppe 'supervisors' sehen alle Zeilen,
-- alle anderen nur Kunden mit loyalty_segment < 3
CREATE OR REPLACE FUNCTION loyalty_row_filter(loyalty_segment STRING)
RETURNS BOOLEAN
RETURN IF(is_account_group_member('supervisors'), true, loyalty_segment < 3);

ALTER TABLE customers_silver_with_row_filter
SET ROW FILTER loyalty_row_filter ON (loyalty_segment);
```

```sql
-- Column Mask: customer_id wird für alle außer 'supervisors' durch
-- einen festen Platzhalterwert ersetzt, statt Zeichen zu schwärzen
CREATE OR REPLACE FUNCTION redact_customer_id(customer_id BIGINT)
RETURN CASE WHEN is_account_group_member('supervisors')
  THEN customer_id
  ELSE 9999999
END;

ALTER TABLE customers_silver_with_row_filter
  ALTER COLUMN customer_id
  SET MASK redact_customer_id;
```

## Wichtige Warnungen

- Wird eine Funktion gelöscht, bevor der zugehörige Filter entfernt wurde, wird die Tabelle unzugänglich.
- Typkonflikte zwischen UDF-Parametern und Spalten führen zu impliziter Konvertierung; bei deaktiviertem ANSI-Modus werden inkompatible Werte stillschweigend zu `NULL`.
- Row Filter und Column Masks bleiben bei `REPLACE TABLE` erhalten, sofern die Schema-Spalten übereinstimmen.

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### Column Mask direkt bei `CREATE TABLE` inline anwenden

Neben `ALTER TABLE ... SET MASK` lässt sich eine Maske auch direkt bei der Spaltendefinition angeben (`sql-ref-syntax-ddl-column-mask`). Die `MASK`-Klausel wendet eine Funktion auf eine Spalte an, sobald Zeilen aus der Tabelle abgerufen werden — das ermöglicht feingranulare Zugriffskontrolle, indem die Funktion Nutzeridentität oder Gruppenzugehörigkeit prüft, um zu entscheiden, ob Werte geschwärzt werden.

**Anwendbar bei:**

- `CREATE TABLE`
- `ALTER TABLE ... ADD COLUMN`
- `ALTER TABLE ... ALTER COLUMN`

**Benötigte Privilegien:**

- Bei neuen Tabellen: `EXECUTE` auf der Funktion, `USE SCHEMA` auf dem Schema, `USE CATALOG` auf dem übergeordneten Catalog sowie `CREATE TABLE` auf dem Schema.
- Bei bestehenden Tabellen: Eigentümerstatus, oder sowohl `MANAGE` als auch `SELECT`. Bei Schemaänderungen zusätzlich `MODIFY` erforderlich.

**Syntax:**

```sql
MASK func_name [ USING COLUMNS ( other_column_name | constant_literal [, ...] ) ]
```

**Parameter:**

| Parameter | Beschreibung |
|---|---|
| `func_name` | Eine skalare SQL-UDF mit mindestens einem Parameter. Der erste Parameter entspricht 1:1 der maskierten Spalte und muss vom Spaltentyp castbar sein; der Rückgabetyp muss auf den Datentyp der maskierten Spalte castbar sein. |
| `other_column_name` | Weitere Spalten derselben Tabelle, die zusätzlich an die Funktion übergeben werden. Jede muss auf den entsprechenden Funktionsparameter castbar sein. |
| `constant_literal` | Ein konstanter Parameter (`STRING`, numerisch, `BOOLEAN`, `INTERVAL` oder `NULL`), der zum Funktionsparameter passt. |

```sql
CREATE FUNCTION mask_ssn(ssn STRING)
RETURN CASE WHEN is_member('HumanResourceDept') THEN ssn ELSE '***-**-****' END;

CREATE TABLE persons(name STRING, ssn STRING MASK mask_ssn);

INSERT INTO persons VALUES('James', '123-45-6789');
SELECT * FROM persons;
```

Mit `USING COLUMNS`, um eine zweite Spalte (hier die Region) als zusätzliches Funktionsargument einzubeziehen — analog zum bereits oben gezeigten `mask_address_by_country`-Beispiel:

```sql
CREATE FUNCTION mask_pii_regional(value STRING, region STRING)
RETURN IF(is_account_group_member(region || '_HumanResourceDept'), value, 'REDACTED');

CREATE TABLE persons(name STRING, address STRING MASK mask_pii_regional
  USING COLUMNS (region), region STRING);

INSERT INTO persons VALUES('James', '160 Spear St, San Francisco', 'US');
SELECT * FROM persons;
```

**Wichtige Hinweise:**

- Die Maske wird angewendet, sobald die Zeile aus der Datenquelle abgerufen wird — Ausdrücke, Prädikate und Sortierungen werden erst danach ausgeführt.
- Bei Typkonflikten und deaktiviertem `ANSI_MODE` werden nicht castbare Werte stillschweigend zu `NULL` konvertiert.
- Column Masks können nicht auf Spalten angewendet werden, die von Generated Columns referenziert werden.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-column-mask

### Row Filter direkt bei `CREATE TABLE` inline anwenden (`WITH ROW FILTER`)

Analog dazu lässt sich ein Row Filter auch direkt beim Anlegen der Tabelle setzen, statt nachträglich per `ALTER TABLE`. Die `ROW FILTER`-Klausel wendet eine Funktion an, die Zeilen bereits beim Abruf aus der Relation filtert.

**Anwendbar bei:**

- `CREATE TABLE` / `ALTER TABLE`
- `CREATE MATERIALIZED VIEW` / `ALTER MATERIALIZED VIEW`
- `CREATE STREAMING TABLE` / `ALTER STREAMING TABLE`

**Benötigte Privilegien:**

- Zum Zuweisen des Filters: `EXECUTE` auf der Funktion, `USE SCHEMA` auf dem Schema, `USE CATALOG` auf dem übergeordneten Catalog.
- Bei neuen Tabellen: `CREATE TABLE`-Privileg auf dem Schema.
- Bei bestehenden Tabellen: Eigentümerstatus, oder sowohl `MANAGE` als auch `SELECT`.
- Bei Schemaänderungen: zusätzlich `MODIFY` erforderlich.

**Syntax:**

```sql
ROW FILTER func_name ON ( [ column_name | constant_literal [, ...] ] ) [...]
```

**Parameter:**

| Parameter | Beschreibung |
|---|---|
| `func_name` | Eine skalare SQL-UDF mit Rückgabetyp `BOOLEAN`. Zeilen, für die die Funktion `FALSE` oder `NULL` zurückgibt, werden herausgefiltert. |
| `column_name` | Tabellenspalten, die an `func_name` übergeben werden. Jede Spalte muss auf den entsprechenden Funktionsparameter castbar sein; die Anzahl der Spalten muss zur Funktionssignatur passen. Weicht der Datentyp einer Spalte vom erwarteten Parametertyp ab, erfolgt eine implizite Konvertierung — bei deaktiviertem `ANSI_MODE` kann das zu unerwarteten Ergebnissen führen. |
| `constant_literal` | Konstante Parameter, die auf die Funktionsparameter passen. Unterstützte Typen: `STRING`, numerische Typen (`INTEGER`, `FLOAT`, `DOUBLE`, `DECIMAL`), `BOOLEAN`, `INTERVAL`, `NULL`. |

**Beispiel:**

```sql
CREATE FUNCTION filter_emps(dept STRING) RETURN is_account_group_member(dept);

CREATE TABLE employees(emp_name STRING, dept STRING) WITH ROW FILTER filter_emps ON (dept);

INSERT INTO employees VALUES ('Jones', 'Engineering'), ('Smith', 'Sales');
SELECT * FROM employees;
```

Hier filtert `filter_emps` danach, ob der abfragende Nutzer Mitglied der Gruppe ist, deren Name dem Wert der `dept`-Spalte entspricht — jede Zeile ist also nur für Mitglieder der jeweils passenden Abteilungsgruppe sichtbar.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-row-filter

### Column Masks auffinden: `INFORMATION_SCHEMA.COLUMN_MASKS`

Die View `INFORMATION_SCHEMA.COLUMN_MASKS` enthält Metadaten zu allen Column Masks in Unity Catalog (Runtime 12.2 LTS+, Public Preview). Angezeigt werden nur Spalten, auf die der abfragende Nutzer Zugriff hat.

**Spalten:**

| Spalte | Typ | Nullable | Bedeutung |
|---|---|---|---|
| `CATALOG_NAME` | STRING | Nein | Catalog, der die Tabelle enthält |
| `SCHEMA_NAME` | STRING | Nein | Schema, das die Tabelle enthält |
| `TABLE_NAME` | STRING | Nein | Name der Tabelle mit der maskierten Spalte |
| `COLUMN_NAME` | STRING | Nein | die maskierte Spalte |
| `MASK_CATALOG` | STRING | Nein | Catalog, der die Mask-Funktion enthält |
| `MASK_SCHEMA` | STRING | Nein | Schema, das die Mask-Funktion enthält |
| `MASK_NAME` | STRING | Nein | Name der Funktion, die die Maske implementiert |
| `MASK_COL_USAGE` | STRING | Ja | kommagetrennte Liste zusätzlicher Spalten, die an die Mask-Funktion übergeben werden (`NULL`, falls keine — entspricht `USING COLUMNS`) |

**Constraints:** Primary Key über `(CATALOG_NAME, SCHEMA_NAME, TABLE_NAME, COLUMN_NAME)`; Foreign Keys auf die `COLUMNS`-View (dieselben vier Spalten) sowie auf die `ROUTINES`-View (`MASK_CATALOG`, `MASK_SCHEMA`, `MASK_NAME`).

**Beispiel — alle im aktuellen Catalog verwendeten Mask-Funktionen zählen:**

```sql
SELECT mask_catalog, mask_schema, mask_name, count(1)
FROM information_schema.column_masks
GROUP BY ALL
ORDER BY ALL;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/information-schema/column_masks

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/filters-and-masks/manually-apply
