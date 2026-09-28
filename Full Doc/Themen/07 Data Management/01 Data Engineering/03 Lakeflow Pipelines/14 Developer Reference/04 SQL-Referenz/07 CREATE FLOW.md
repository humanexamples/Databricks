# `CREATE FLOW` (Pipelines) — Referenz

## Abschnittsübersicht

1. [Grundzweck](#grundzweck)
2. [Formale Syntax](#syntax)
3. [Parameter](#parameter)
4. [Doku-eigene Beispiele](#doku-beispiele)
5. [Quellen](#quellen)

---

## <a id="grundzweck">1. Grundzweck</a>

Das Statement `CREATE FLOW` erstellt Flows oder Backfills für Tabellen in einer Pipeline.

---

## <a id="syntax">2. Formale Syntax</a>

```
CREATE FLOW flow_name [COMMENT comment] AS
{
  AUTO CDC [ONCE] INTO target_table create_auto_cdc_flow_spec |
  INSERT [ONCE] INTO target_table BY NAME [ replace_using_spec ] query
}

replace_using_spec
  REPLACE USING ( column_name [, ...] ) SEQUENCE BY sequence_column
```

### Reales Beispiel mit möglichst vielen Bausteinen der formalen Syntax

`AUTO CDC ... INTO` und `INSERT ... INTO` schließen sich gegenseitig aus, ebenso `ONCE` und `REPLACE USING` (`REPLACE USING` erfordert eine Streaming-Quelle, `ONCE` schließt genau das aus). Das folgende, aus den einzeln verifizierten Bausteinen dieses Dokuments zusammengesetzte Beispiel (kein wörtliches Einzelzitat einer Doku-Seite) kombiniert daher die größtmögliche gemeinsam nutzbare Untermenge — `COMMENT`, `INSERT INTO ... BY NAME` und `REPLACE USING (...) SEQUENCE BY`:

```sql
CREATE FLOW payments_replace_flow COMMENT "Hält je payment_id nur die aktuellste Snapshot-Zeile" AS
INSERT INTO main.sales.payments_latest BY NAME
REPLACE USING (payment_id) SEQUENCE BY payment_date
SELECT payment_id, booking_id, status, payment_date
FROM STREAM(samples.wanderbricks.payments);
```

Separat zu betrachten, da mit obigem Beispiel nicht kombinierbar:

- **`AUTO CDC ... INTO`** als Alternative zu `INSERT INTO ... BY NAME`, wenn die Quellabfrage Change-Data-Semantik verwendet — siehe `AUTO CDC INTO.md` in diesem Ordner für die vollständige `create_auto_cdc_flow_spec`.
- **`ONCE`** als Alternative zu `REPLACE USING`, für einen einmaligen Backfill:

  ```sql
  CREATE FLOW backfill_users AS
  INSERT ONCE INTO users BY NAME
  SELECT * FROM user_backfill_table;
  ```

---

## <a id="parameter">3. Parameter</a>

- **`flow_name`** — der Name des zu erstellenden Flows.
- **`COMMENT`** — optionale Beschreibung für den Flow.
- **`AUTO CDC ... INTO`** — ein `AUTO CDC ... INTO`-Statement, das den Flow mit einer `create_auto_cdc_flow_spec` definiert. Es muss entweder ein `AUTO CDC ... INTO`- oder ein `INSERT INTO`-Statement angegeben werden. `AUTO CDC ... INTO` wird verwendet, wenn die Quellabfrage Change-Data-Semantik nutzt. Siehe `AUTO CDC INTO.md` in diesem Ordner.
- **`target_table`** — die zu aktualisierende Tabelle. Diese muss eine Streaming Table sein.
- **`INSERT INTO`** — definiert eine Tabellenabfrage, die in die Zieltabelle eingefügt wird. Ist die Option `ONCE` nicht angegeben, muss die Abfrage eine **Streaming**-Abfrage sein. Das Schlüsselwort `STREAM` liest die Quelle mit Streaming-Semantik. Trifft der Lesevorgang auf eine Änderung oder Löschung eines bestehenden Datensatzes, wird ein Fehler ausgelöst — am sichersten ist das Lesen aus statischen oder nur anfügenden Quellen. Um Daten mit Änderungscommits einzulesen, kann in Python die Option `skipChangeCommits` zur Fehlerbehandlung verwendet werden. `INSERT INTO` schließt sich gegenseitig mit `AUTO CDC ... INTO` aus: `AUTO CDC ... INTO` wird verwendet, wenn die Quelldaten Change-Data-Capture(CDC)-Funktionalität enthalten, `INSERT INTO`, wenn die Quelle das nicht tut.
- **`REPLACE USING ( column_name [, ...] ) SEQUENCE BY sequence_column`** — **Beta**, erfordert Databricks Runtime 18.2 und höher. Definiert den Flow als `REPLACE USING`-Flow, der alle Zeilen in der Zieltabelle ersetzt, die den angegebenen Schlüsselspalten entsprechen, und alle übrigen Zeilen unverändert lässt. `REPLACE USING` wird verwendet, wenn die Quelle eine Reihe partieller, nach Spalte geschlüsselter Snapshots ist. `SEQUENCE BY` ordnet die Updates so, dass für einen Schlüssel der höchste Sequenzwert gewinnt, auch wenn Updates nicht chronologisch eintreffen. Mindestens eine Schlüsselspalte und genau eine `SEQUENCE BY`-Spalte müssen angegeben werden. Die Abfrage muss eine Streaming-Abfrage sein, und `BY NAME` ist erforderlich. `REPLACE USING` lässt sich nicht mit `ONCE` oder mit `AUTO CDC ... INTO` kombinieren.
- **`ONCE`** — definiert den Flow optional als einmaligen Flow, etwa als Backfill. Die Verwendung von `ONCE` ändert den Flow auf zwei Arten: Die Quellabfrage `query` bzw. `create_auto_cdc_flow_spec` ist keine Streaming-Table-Abfrage; und der Flow wird standardmäßig einmalig ausgeführt — wird die Pipeline per vollständigem Refresh aktualisiert, läuft der `ONCE`-Flow erneut, um die Daten neu zu erzeugen. `ONCE` lässt sich nicht mit `REPLACE USING` verwenden, das eine Streaming-Quelle erfordert.

---

## <a id="doku-beispiele">4. Doku-eigene Beispiele</a>

```sql
-- EXAMPLE 1:
-- Create a streaming table, and add two flows that append data to it:
CREATE OR REFRESH STREAMING TABLE users;

-- first flow into target_table:
CREATE FLOW users_flow AS
INSERT INTO users BY NAME
SELECT * FROM stream(raw_data.users);

-- second flow into target_table:
CREATE FLOW backfill_users AS
INSERT ONCE INTO users BY NAME
SELECT * FROM user_backfill_table;

-- EXAMPLE 2:
-- Create a streaming table, and add a flow that applies CDC changes to it:
CREATE OR REFRESH STREAMING TABLE admins_cdc_target_table;

-- first flow into target_table:
CREATE FLOW admin_cdc_flow AS
AUTO CDC INTO admins_cdc_target_table
FROM stream(cdc_data.admins)
KEYS (userId)
APPLY AS DELETE WHEN
  operation = "DELETE"
SEQUENCE BY sequenceNum
COLUMNS * EXCEPT (operation, sequenceNum)
STORED AS SCD TYPE 2;

-- EXAMPLE 3:
-- Create a streaming table, and add a REPLACE USING flow that keeps the latest
-- row for each payment_id from a stream of partial snapshots:
CREATE OR REFRESH STREAMING TABLE payments_latest;

CREATE FLOW payments_replace_flow AS
INSERT INTO payments_latest BY NAME
REPLACE USING (payment_id) SEQUENCE BY payment_date
SELECT payment_id, booking_id, status, payment_date
FROM STREAM(samples.wanderbricks.payments);
```

---

## <a id="quellen">5. Quellen</a>

- CREATE FLOW (pipelines) — SQL-Sprachreferenz (formale Syntax, alle Parameter, drei Doku-Beispiele, Beta-Hinweis zu `REPLACE USING` ab Databricks Runtime 18.2): https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-flow

**Stand:** 2026-08-19.
