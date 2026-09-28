# Constraints

Constraints sichern die Datenintegrität von Delta-Lake-Tabellen — unterschieden wird zwischen durchgesetzten (enforced) und rein informativen (nicht durchgesetzten) Constraints. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Constraint-Typen

**Durchgesetzte (Enforced) Constraints:**

| Typ | Bedeutung |
|---|---|
| `NOT NULL` | „gibt an, dass Werte in bestimmten Spalten nicht null sein dürfen" |
| `CHECK` | „gibt an, dass ein festgelegter boolescher Ausdruck für jede eingehende Zeile wahr sein muss" |

**Informative (nicht durchgesetzte) Constraints:** Primary Key, Foreign Key, Unique. Diese „definieren Beziehungen zwischen Feldern in Tabellen und werden nicht durchgesetzt", können aber die Query-Performance durch Optimierung verbessern.

## 2. NOT-NULL-Constraints

```sql
CREATE TABLE people10m (
  id INT NOT NULL,
  firstName STRING,
  middleName STRING NOT NULL
);

ALTER TABLE people10m ALTER COLUMN middleName DROP NOT NULL;
ALTER TABLE people10m ALTER COLUMN ssn SET NOT NULL;
```

**Wichtiges Verhalten:** Beim Hinzufügen von `NOT NULL` zu bestehenden Tabellen prüft Databricks zunächst, ob alle aktuellen Zeilen den Constraint erfüllen.

**Verschachtelungsregeln:** Ist eine Spalte innerhalb eines Structs verschachtelt, muss auch das übergeordnete Struct `NOT NULL` sein. Spalten, die in Array- oder Map-Typen verschachtelt sind, können keinen `NOT NULL`-Constraint tragen.

## 3. CHECK-Constraints

```sql
ALTER TABLE people10m ADD CONSTRAINT dateWithinRange
  CHECK (birthDate > '1900-01-01');

ALTER TABLE people10m DROP CONSTRAINT dateWithinRange;
```

**Einschränkung:** `CHECK`-Ausdrücke dürfen keine benutzerdefinierten, Aggregat-, Window- oder Multi-Row-Funktionen nutzen.

**Constraints einsehen:**

```sql
DESCRIBE DETAIL people10m;
SHOW TBLPROPERTIES people10m;
```

## 4. Primary Key, Foreign Key und Unique Constraints

**Bei Tabellenerstellung:**

```sql
CREATE TABLE T(pk1 INTEGER NOT NULL, pk2 INTEGER NOT NULL,
  CONSTRAINT t_pk PRIMARY KEY(pk1, pk2));

CREATE TABLE S(pk INTEGER NOT NULL PRIMARY KEY,
  fk1 INTEGER, fk2 INTEGER,
  CONSTRAINT s_t_fk FOREIGN KEY(fk1, fk2) REFERENCES T);

CREATE TABLE U(id INTEGER NOT NULL, email STRING NOT NULL,
  CONSTRAINT u_uq_email UNIQUE(email));
```

**Bei bestehenden Tabellen:**

```sql
ALTER TABLE T ADD CONSTRAINT t_pk PRIMARY KEY(pk1, pk2);
ALTER TABLE S ADD CONSTRAINT s_t_fk FOREIGN KEY(fk1, fk2) REFERENCES T;
ALTER TABLE U ADD CONSTRAINT u_uq_email UNIQUE(email);
```

## 5. Wichtige Anforderungen

- Alle Constraints erfordern Delta Lake.
- Das Hinzufügen durchgesetzter Constraints hebt das Tabellen-Writer-Protokoll auf Version 3+ an.
- Unique-Spalten können nullable sein (NULL-Werte gelten als unterschiedlich); mehrere Unique-Constraints pro Tabelle sind erlaubt.
- **Runtime-Verfügbarkeit:** Primary-/Foreign-Key-Constraints sind ab Runtime 13.3 LTS verfügbar (allgemein verfügbar ab 15.2+); Unique-Constraints befinden sich ab Runtime 18.2+ in Public Preview.
- Foreign-Key-Constraints müssen einen Primary-Key- oder Unique-Constraint referenzieren.
- `CTAS`-Statements (`CREATE TABLE AS SELECT`) unterstützen keine Constraint-Klauseln.

## 6. Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

Constraints werden — wie im Feature-Compatibility-Kontext beschrieben — von Unity Catalog validiert. Databricks setzt Primary-/Foreign-Key-Constraints standardmäßig **nicht** zur Schreibzeit durch (informativ, nicht erzwungen), sie dienen vor allem Query-Optimierung und Dokumentation.

**Primary Key — mehrspaltig und einspaltig:**

```sql
CREATE TABLE persons(
  first_name STRING NOT NULL,
  last_name STRING NOT NULL,
  nickname STRING,
  CONSTRAINT persons_pk PRIMARY KEY(first_name, last_name));

CREATE TABLE customers(customerid STRING NOT NULL PRIMARY KEY, name STRING);
```

**Foreign Key — referenziert mehrere Spalten bzw. eine benannte Unique-Spalte:**

```sql
CREATE TABLE pets(
  name STRING, owner_first_name STRING, owner_last_name STRING,
  CONSTRAINT pets_persons_fk FOREIGN KEY (owner_first_name, owner_last_name)
    REFERENCES persons);

CREATE TABLE orders(
  orderid BIGINT NOT NULL CONSTRAINT orders_pk PRIMARY KEY,
  customerid STRING CONSTRAINT orders_customers_fk REFERENCES customers);
```

**Unique Constraint — einspaltig und mehrspaltig:**

```sql
CREATE TABLE person_contacts(
  first_name STRING NOT NULL, last_name STRING NOT NULL,
  nickname STRING UNIQUE);

CREATE TABLE person_accounts(
  first_name STRING NOT NULL, last_name STRING NOT NULL, account_id STRING,
  CONSTRAINT person_accounts_uq UNIQUE(first_name, last_name));
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-constraint

## 7. Verwandte Themen

- `checkConstraints` lässt sich per `DROP FEATURE` entfernen: siehe [07 Drop Feature.md](07%20Drop%20Feature.md).
- Generated Columns können keine maskierten Spalten referenzieren: siehe [09 Generated Columns.md](09%20Generated%20Columns.md), Abschnitt 5.

### Quelle

- https://docs.databricks.com/aws/en/tables/constraints
