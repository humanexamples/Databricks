# `CREATE STREAMING TABLE` (Pipelines) — Referenz

## Abschnittsübersicht

1. [Grundzweck](#grundzweck)
2. [Formale Syntax](#syntax)
3. [Parameter](#parameter)
4. [Notwendige Berechtigungen](#berechtigungen)
5. [Einschränkungen](#einschraenkungen)
6. [Doku-eigene Beispiele](#doku-beispiele)
7. [Databricks-SQL-Variante der Sprachreferenz (`sql-ref-syntax-ddl-create-streaming-table`)](#dbsql-variante)
8. [Quellen](#quellen)

---

## <a id="grundzweck">1. Grundzweck</a>

Eine Streaming Table ist eine Tabelle mit Unterstützung für Streaming- oder inkrementelle Datenverarbeitung. Streaming Tables werden von Pipelines unterstützt. Bei jeder Aktualisierung einer Streaming Table werden der Quelltabelle hinzugefügte Daten an die Streaming Table angefügt. Streaming Tables lassen sich manuell oder nach Zeitplan aktualisieren.

---

## <a id="syntax">2. Formale Syntax</a>

```
CREATE [OR REFRESH] [PRIVATE] STREAMING TABLE
  table_name
  [ table_specification ]
  [ table_clauses ]
  [ {flow_clause | AS query} ]

table_specification
  ( { column_identifier column_type [column_properties] } [, ...]
    [ column_constraint ] [, ...]
    [ , table_constraint ] [...] )

   column_properties
      { NOT NULL | GENERATED ALWAYS AS ( expr ) | GENERATED { ALWAYS | BY DEFAULT } AS IDENTITY [ ( [ START WITH start | INCREMENT BY step ] [ ...] ) ] | DEFAULT default_expression | COMMENT column_comment | column_constraint | MASK clause } [ ... ]

table_clauses
  { USING DELTA
    PARTITIONED BY (col [, ...]) |
    CLUSTER BY clause |
    LOCATION path |
    COMMENT view_comment |
    TBLPROPERTIES clause |
    WITH { ROW FILTER clause } } [ ... ]
   } [ ... ]

flow_clause
  FLOW { { INSERT [ONCE] BY NAME query } |
  { AUTO CDC auto_cdc_flow_spec } |
  { REPLACE WHERE predicate BY NAME query } |
  { REPLACE USING ( column_name [, ...] ) SEQUENCE BY sequence_column BY NAME query } }
```

Alternativ zu einem inline über `flow_clause` definierten Flow lässt sich eine Streaming Table auch ohne Flow anlegen (`CREATE OR REFRESH STREAMING TABLE table_name;`) und anschließend über separate `CREATE FLOW`-Statements befüllen — siehe `CREATE FLOW.md` in diesem Ordner.

### Reales Beispiel mit möglichst vielen Bausteinen der formalen Syntax

Die vier `flow_clause`-Varianten (`INSERT BY NAME`, `AUTO CDC`, `REPLACE WHERE`, `REPLACE USING`) schließen sich gegenseitig aus, ebenso `PARTITIONED BY`/`CLUSTER BY` und `flow_clause`/`AS query` (`FLOW INSERT BY NAME` ist äquivalent zu `AS query`). Das folgende, aus den einzeln verifizierten Bausteinen dieses Dokuments zusammengesetzte Beispiel (kein wörtliches Einzelzitat einer Doku-Seite) kombiniert daher die größtmögliche gemeinsam nutzbare Untermenge — vollständige `table_specification` mit `NOT NULL`, `GENERATED ALWAYS AS IDENTITY`, `DEFAULT`, `COMMENT`, informationellem Primary-Key-`column_constraint`, `MASK`-Klausel, `table_constraint` als Foreign Key, die `table_clauses` `CLUSTER BY`, `LOCATION`, `COMMENT`, `TBLPROPERTIES`, `WITH ROW FILTER`, sowie eine `FLOW INSERT ONCE BY NAME`-Klausel mit Read-Option:

```sql
CREATE OR REFRESH PRIVATE STREAMING TABLE main.sales.customers_bronze (
  customer_id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1000 INCREMENT BY 1),
  ssn STRING NOT NULL PRIMARY KEY MASK main.sales.ssn_mask_fn COMMENT 'Sozialversicherungsnummer, maskiert',
  region STRING DEFAULT 'UNKNOWN' COMMENT 'Herkunftsregion',
  status STRING GENERATED ALWAYS AS (upper(region)),
  CONSTRAINT fk_region FOREIGN KEY (region) REFERENCES main.sales.regions(region)
)
CLUSTER BY (region)
LOCATION '/mnt/bronze/customers'
COMMENT 'Rohdaten zu Kunden, einmaliger Backfill'
TBLPROPERTIES ('quality' = 'bronze')
WITH ROW FILTER main.sales.region_filter_fn ON (region)
FLOW INSERT ONCE BY NAME
  SELECT * FROM STREAM read_files('/databricks-datasets/retail-org/customers/*', format => 'csv')
  WITH (SKIPCHANGECOMMITS);
```

Separat zu betrachten, da mit obigem Beispiel nicht kombinierbar:

- **`PARTITIONED BY`** als Alternative zu `CLUSTER BY` — Databricks empfiehlt für Pipelines jedoch `CLUSTER BY`.
- **`AS query`** als Kurzform, äquivalent zu `FLOW INSERT BY NAME query` (ohne `ONCE`, für laufende Streaming-Befüllung statt Backfill):

  ```sql
  CREATE OR REFRESH STREAMING TABLE raw_data
  AS SELECT * FROM STREAM read_files('abfss://my_path');
  ```
- **`FLOW AUTO CDC`** (Beta, Databricks Runtime 17.3 und höher sowie `PREVIEW`-Pipelines-Channel) — verarbeitet Change-Data-Capture(CDC)-Datensätze aus einer Quelle inline in die Tabelle; siehe `AUTO CDC INTO.md` in diesem Ordner für die vollständige `auto_cdc_flow_spec`:

  ```sql
  CREATE OR REFRESH STREAMING TABLE target
  FLOW AUTO CDC
  FROM stream(cdc_data.users)
  KEYS (userId)
  SEQUENCE BY sequenceNum
  STORED AS SCD TYPE 1;
  ```
- **`FLOW REPLACE WHERE predicate BY NAME query`** — berechnet und überschreibt nur die Zeilen neu, die `predicate` entsprechen, alle übrigen bleiben unverändert; für inkrementelle Batch-Verarbeitung von Joins, Aggregationen, spät eintreffenden Daten, Schema Evolution und Backfills:

  ```sql
  FLOW REPLACE WHERE region = 'EU' BY NAME
  SELECT * FROM eu_customers_batch;
  ```
- **`FLOW REPLACE USING ( column_name [, ...] ) SEQUENCE BY sequence_column BY NAME query`** (Beta, Databricks Runtime 18.2 und höher) — ersetzt alle Zeilen, die den angegebenen Schlüsselspalten entsprechen, und lässt übrige Zeilen unverändert; die Quelle muss eine Streaming-Quelle sein:

  ```sql
  FLOW REPLACE USING (payment_id) SEQUENCE BY payment_date BY NAME
  SELECT payment_id, booking_id, status, payment_date
  FROM STREAM(samples.wanderbricks.payments);
  ```

---

## <a id="parameter">3. Parameter</a>

- **`REFRESH`** — erstellt bei Angabe die Tabelle oder aktualisiert eine bestehende Tabelle samt Inhalt.
- **`PRIVATE`** — erstellt eine private Streaming Table. Private Streaming Tables werden nicht dem Katalog hinzugefügt und sind nur innerhalb der definierenden Pipeline zugänglich; sie können denselben Namen wie ein bestehendes Katalogobjekt tragen — innerhalb der Pipeline lösen Referenzen dann zur privaten Streaming Table auf; sie bestehen nur über die Lebensdauer der Pipeline fort, nicht nur ein einzelnes Update. Private Streaming Tables wurden zuvor mit dem Parameter `TEMPORARY` erstellt.
- **`table_name`** — der Name der neu erstellten Tabelle. Der vollqualifizierte Tabellenname muss eindeutig sein.
- **`table_specification`** — definiert optional die Liste der Spalten, ihre Typen, Eigenschaften, Beschreibungen und Spalten-Constraints.
  - **`column_identifier`** — die Spaltennamen müssen eindeutig sein und den Ausgabespalten der Abfrage entsprechen.
  - **`column_type`** — legt den Datentyp der Spalte fest. Nicht alle von Databricks unterstützten Datentypen werden von Streaming Tables unterstützt.
  - **`column_comment`** — ein optionales `STRING`-Literal zur Beschreibung der Spalte. Muss zusammen mit `column_type` angegeben werden; ist der Spaltentyp nicht angegeben, wird der Spaltenkommentar übersprungen.
  - **`GENERATED ALWAYS AS ( expr )`** — der Wert der Spalte wird durch den angegebenen `expr` bestimmt. Die `DEFAULT COLLATION` der Tabelle muss `UTF8_BINARY` sein. `expr` darf aus Literalen, Spaltenbezeichnern innerhalb der Tabelle sowie deterministischen, eingebauten SQL-Funktionen oder Operatoren bestehen — mit Ausnahme von Aggregatfunktionen, analytischen Window-Funktionen, Ranking-Window-Funktionen, tabellenwertigen Generatorfunktionen und Spalten mit einer anderen Collation als `UTF8_BINARY`; außerdem darf `expr` keine Subquery enthalten.
  - **`GENERATED { ALWAYS | BY DEFAULT } AS IDENTITY [ ( [ START WITH start ] [ INCREMENT BY step ] ) ]`** — verfügbar ab Databricks SQL bzw. Databricks Runtime 10.4 LTS und höher. Definiert eine Identity-Spalte. Werden beim Schreiben keine Werte für die Identity-Spalte angegeben, wird automatisch ein eindeutiger, statistisch steigender (bzw. fallender bei negativem `step`) Wert zugewiesen. Nur für Delta-Tabellen unterstützt, nur für Spalten mit Datentyp `BIGINT`. Die automatisch zugewiesenen Werte beginnen bei `start` und erhöhen sich um `step`. Zugewiesene Werte sind eindeutig, aber nicht garantiert lückenlos. Beide Parameter sind optional, Standardwert ist 1; `step` darf nicht `0` sein. Liegen die automatisch zugewiesenen Werte außerhalb des Wertebereichs des Identity-Spaltentyps, schlägt die Abfrage fehl. Bei `ALWAYS` lassen sich keine eigenen Werte für die Identity-Spalte angeben. Nicht unterstützt: `PARTITIONED BY` einer Identity-Spalte, `UPDATE` einer Identity-Spalte. Hinweis: Die Deklaration einer Identity-Spalte auf einer Tabelle deaktiviert nebenläufige Transaktionen — Identity-Spalten sollten daher nur verwendet werden, wenn nebenläufige Schreibvorgänge auf die Zieltabelle nicht erforderlich sind.
  - **`DEFAULT default_expression`** — verfügbar ab Databricks SQL bzw. Databricks Runtime 11.3 LTS und höher. Definiert einen `DEFAULT`-Wert für die Spalte, der bei `INSERT`, `UPDATE` und `MERGE ... INSERT` verwendet wird, wenn die Spalte nicht angegeben ist. Ist kein Default angegeben, wird `DEFAULT NULL` für nullbare Spalten angewendet. `default_expression` darf aus Literalen sowie eingebauten SQL-Funktionen oder Operatoren bestehen — mit Ausnahme von Aggregatfunktionen, analytischen Window-Funktionen, Ranking-Window-Funktionen und tabellenwertigen Generatorfunktionen; außerdem darf `default_expression` keine Subquery enthalten. `DEFAULT` wird für `CSV`-, `JSON`-, `PARQUET`- und `ORC`-Quellen unterstützt.
  - **`column_constraint`** — fügt einer Spalte in einer Streaming Table einen informationellen Primary-Key- oder Foreign-Key-Constraint hinzu.
  - **`MASK`-Klausel** — fügt eine Column-Mask-Funktion zur Anonymisierung sensibler Daten hinzu.
  - **`CONSTRAINT expectation_name EXPECT (expectation_expr) [ ON VIOLATION { FAIL UPDATE | DROP ROW } ]`** — fügt der Streaming Table Datenqualitäts-Expectations hinzu, die über die Zeit nachverfolgt und über das Event-Log der Streaming Table eingesehen werden können. Eine `FAIL UPDATE`-Expectation lässt die Verarbeitung sowohl beim Erstellen als auch beim Aktualisieren der Tabelle fehlschlagen. Eine `DROP ROW`-Expectation verwirft die gesamte Zeile, wenn die Expectation nicht erfüllt ist. `expectation_expr` darf aus Literalen, Spaltenbezeichnern innerhalb der Tabelle sowie deterministischen, eingebauten SQL-Funktionen oder Operatoren bestehen — mit denselben Ausnahmen wie bei `GENERATED ALWAYS AS` (Aggregatfunktionen inkl. Window-Funktionen, tabellenwertige Generatorfunktionen); außerdem darf `expr` keine Subquery enthalten.
- **`table_constraint`** — bei Angabe eines Schemas lassen sich Primary und Foreign Keys definieren; die Constraints sind informationell und werden nicht erzwungen. Um Table Constraints zu definieren, muss die Pipeline eine Unity-Catalog-fähige Pipeline sein.
- **`table_clauses`** — legt optional Partitionierung, Kommentare und benutzerdefinierte Eigenschaften der Tabelle fest. Jede Unterklausel darf nur einmal angegeben werden.
  - **`USING DELTA`** — legt das Datenformat fest. Einzig verfügbare Option ist DELTA. Optional, Standard ist DELTA.
  - **`PARTITIONED BY`** — optionale Liste von einer oder mehreren Spalten zur Partitionierung der Tabelle. Schließt `CLUSTER BY` gegenseitig aus. Liquid Clustering bietet eine flexible, optimierte Lösung für Clustering — Databricks empfiehlt, für Pipelines `CLUSTER BY` statt `PARTITIONED BY` zu verwenden.
  - **`CLUSTER BY`** — aktiviert Liquid Clustering auf der Tabelle und legt die als Clustering-Keys zu verwendenden Spalten fest. Mit `CLUSTER BY AUTO` wählt Databricks die Clustering-Keys intelligent zur Optimierung der Abfrageperformance. Schließt `PARTITIONED BY` gegenseitig aus. Ausführliche Behandlung von Liquid Clustering (Vor-/Nachteile von `AUTO`, Wahl der Keys, Diagnose der Wirksamkeit) in [Liquid Clustering.md](../../../../../09%20Performance%20Optimization/01%20Foundation%20Design/05%20Liquid%20Clustering.md).
    - **Ohne `CLUSTER BY`:** Die Streaming Table bleibt ungeclustert — es wird kein Clustering-Key-Layout angelegt, und neu geschriebene Daten werden nicht anhand von Spaltenwerten organisiert (die generelle Delta-Lake-Dateigrößen-Verwaltung bleibt davon unberührt).
    - **Nachträglich hinzufügen:** `ALTER TABLE`-Befehle sind für Streaming Tables generell nicht zulässig (siehe Abschnitt 5), und auch das eigens dafür vorgesehene `ALTER STREAMING TABLE`-Statement unterstützt keine Änderung der Clustering-Spalten — es deckt ausschließlich Schedule (`ADD`/`ALTER`/`DROP SCHEDULE`), `ALTER COLUMN`, `SET`/`DROP ROW FILTER`, `SET`/`UNSET TAGS` und `SET OWNER TO` ab. `CLUSTER BY` lässt sich bei einer bestehenden Streaming Table daher ausschließlich durch erneutes Ausführen von `CREATE OR REFRESH STREAMING TABLE table_name CLUSTER BY (...)` (bzw. `CLUSTER BY AUTO`) mit sonst unveränderter Definition hinzufügen oder ändern. Das gilt auch für die Migration von `PARTITIONED BY` zu `CLUSTER BY` — die dafür bei regulären Tabellen vorgesehene `ALTER TABLE ... REPLACE PARTITIONED BY WITH CLUSTER BY`-Syntax (siehe [Liquid Clustering.md](../../../../../09%20Performance%20Optimization/01%20Foundation%20Design/05%20Liquid%20Clustering.md), Abschnitt 6) wird für Streaming Tables und Materialized Views in Pipelines nicht unterstützt.

      Die Definitionsänderung selbst wirkt sich zunächst nur auf neu geschriebene Daten aus — bereits vorhandene Daten bleiben unverändert im alten Layout, bis eine Wartungsoperation läuft. Wie bei jeder Delta-Tabelle mit Liquid Clustering ist dafür regulär `OPTIMIZE table_name FULL;` das richtige Werkzeug: Es reorganisiert die bestehenden Dateien anhand der neuen Clustering-Keys, ohne die Quelle erneut zu lesen (`OPTIMIZE` ist — anders als `ALTER TABLE` — für Streaming Tables nicht ausgeschlossen). Ein vollständiger `REFRESH STREAMING TABLE table_name FULL;` ist dafür nicht notwendig und deutlich einschneidender: Er leert die Tabelle (Truncate), entfernt sämtliche Checkpoint-Daten und verarbeitet die Quelle komplett neu — sinnvoll nur, wenn tatsächlich eine vollständige Neuverarbeitung nötig ist (z. B. bei der genannten Migration von `PARTITIONED BY` auf `CLUSTER BY`, laut Doku explizit als „physical data layout change" mit Full-Refresh-Bedarf genannt). Bei Quellen mit begrenzter Historie/Retention (z. B. Kafka) rät Databricks von einem vollständigen Refresh ausdrücklich ab, da nicht mehr verfügbare historische Daten dabei unwiederbringlich verloren gehen.
  - **`LOCATION`** — optionaler Speicherort für Tabellendaten. Ist keiner gesetzt, verwendet das System standardmäßig den Pipeline-Speicherort.
  - **`COMMENT`** — optionales `STRING`-Literal zur Beschreibung der Tabelle.
  - **`TBLPROPERTIES`** — optionale Liste von Tabelleneigenschaften für die Tabelle.
  - **`WITH ROW FILTER`** — fügt der Tabelle eine Row-Filter-Funktion hinzu. Nachfolgende Abfragen für diese Tabelle erhalten nur die Teilmenge der Zeilen, für die die Funktion `TRUE` liefert — nützlich für feingranulare Zugriffskontrolle, da die Funktion Identität und Gruppenmitgliedschaften des aufrufenden Nutzers prüfen kann.
  - **`FLOW`** — definiert optional einen Flow inline mit der Tabellenerstellung. Ein Flow ist eine zustandsbehaftete Abfrage, die den Inhalt der Tabelle aktualisiert. Ist `FLOW` nicht angegeben, lässt sich stattdessen `AS query` verwenden, oder Flows werden separat mit `CREATE FLOW` definiert (siehe `CREATE FLOW.md` in diesem Ordner). Es lässt sich einer der folgenden Flow-Typen angeben:
    - **`INSERT BY NAME`** — fügt Daten nach Spaltennamen in die Tabelle ein. Ist die Option `ONCE` nicht angegeben, muss die Abfrage eine Streaming-Abfrage sein. Das Schlüsselwort `STREAM` liest die Quelle mit Streaming-Semantik; trifft der Lesevorgang auf eine Änderung oder Löschung eines bestehenden Datensatzes, wird ein Fehler ausgelöst — am sichersten ist das Lesen aus statischen oder nur anfügenden Quellen. Hinweis: `FLOW INSERT BY NAME` ist äquivalent zur Verwendung von `AS query` — beide folgenden Statements verhalten sich identisch:

      ```sql
      CREATE OR REFRESH STREAMING TABLE raw_data
      AS SELECT * FROM STREAM read_files('abfss://my_path');

      CREATE OR REFRESH STREAMING TABLE raw_data
      FLOW INSERT BY NAME SELECT * FROM STREAM read_files('abfss://my_path');
      ```
    - **`ONCE`** — definiert den Flow optional als einmaligen Flow, etwa als Backfill. Bei Angabe von `ONCE` ist die Abfrage keine Streaming-Abfrage, und der Flow läuft standardmäßig einmalig. Wird die Tabelle per vollständigem Refresh aktualisiert, läuft der `ONCE`-Flow erneut, um die Daten neu zu erzeugen. `ONCE` gilt nur für `INSERT BY NAME`-Flows.
    - **`AUTO CDC`** (Beta, verfügbar in Databricks Runtime 17.3 und höher sowie im `PREVIEW`-Pipelines-Channel) — definiert einen `AUTO CDC`-Flow, der Change-Data-Capture(CDC)-Datensätze aus einer Quelle in die Tabelle verarbeitet. `AUTO CDC` wird verwendet, wenn die Quelldaten CDC-Semantik enthalten.
    - **`REPLACE WHERE predicate BY NAME query`** — definiert einen `REPLACE WHERE`-Flow, der nur die `predicate` entsprechenden Zeilen neu berechnet und überschreibt, alle übrigen Zeilen bleiben unverändert. `REPLACE WHERE` dient der inkrementellen Batch-Verarbeitung von Joins und Aggregationen, spät eintreffenden Daten, Schema Evolution und Backfills. `BY NAME` ist erforderlich.
    - **`REPLACE USING ( column_name [, ...] ) SEQUENCE BY sequence_column BY NAME query`** (Beta, erfordert Databricks Runtime 18.2 und höher) — definiert einen `REPLACE USING`-Flow, der alle Zeilen ersetzt, die den angegebenen Schlüsselspalten entsprechen, und alle übrigen Zeilen unverändert lässt. `REPLACE USING` wird verwendet, wenn die Quelle eine Reihe partieller, nach Spalte geschlüsselter Snapshots ist. `SEQUENCE BY` ordnet die Updates so, dass für einen Schlüssel der höchste Sequenzwert gewinnt, auch wenn Updates nicht chronologisch eintreffen. Die Quelle muss eine Streaming-Quelle sein. `BY NAME` ist erforderlich.
- **`AS query`** — befüllt die Tabelle mit den Daten aus `query`. Diese Abfrage muss eine **Streaming**-Abfrage sein. Das Schlüsselwort `STREAM` liest die Quelle mit Streaming-Semantik; trifft der Lesevorgang auf eine Änderung oder Löschung eines bestehenden Datensatzes, wird ein Fehler ausgelöst — am sichersten ist das Lesen aus statischen oder nur anfügenden Quellen. Um Daten mit Änderungscommits einzulesen, lässt sich die Read-Option `skipChangeCommits` ergänzen. Werden `query` und `table_specification` gemeinsam angegeben, muss das in `table_specification` angegebene Tabellenschema alle von `query` zurückgegebenen Spalten enthalten, sonst tritt ein Fehler auf. In `table_specification` angegebene, aber von `query` nicht zurückgegebene Spalten liefern beim Abfragen `null`-Werte.
  - **Read Options** — lassen sich in der Abfrage angeben, um zu konfigurieren, wie Daten aus der Quelle gelesen werden, z. B. `skipChangeCommits`, um Änderungscommits in den Quelldaten zu überspringen. Read Options werden als Map in der `WITH`-Klausel der Abfrage angegeben, z. B. `SELECT * FROM STREAM source_table WITH (SKIPCHANGECOMMITS=TRUE, STARTINGVERSION=X)`. Das `=TRUE` ist optional, ein boolescher Wert lässt sich auch als `WITH (SKIPCHANGECOMMITS)` angeben. Read Options werden nur für Databricks Runtime 17.3 und höher unterstützt. Für Delta werden folgende Read Options unterstützt: `maxFilesPerTrigger`, `maxBytesPerTrigger`, `startingVersion`, `startingTimestamp`, `readChangeFeed`, `withEventTimeOrder`, `skipChangeCommits`.

---

## <a id="berechtigungen">4. Notwendige Berechtigungen</a>

Der Run-as-Nutzer einer Pipeline benötigt folgende Berechtigungen:

- `SELECT`-Privileg auf die von der Streaming Table referenzierten Basistabellen.
- `USE CATALOG`-Privileg auf den übergeordneten Katalog und `USE SCHEMA`-Privileg auf das übergeordnete Schema.
- `CREATE MATERIALIZED VIEW`-Privileg auf das Schema, das die Streaming Table enthält.

Um die Pipeline, in der die Streaming Table definiert ist, aktualisieren zu können, sind zusätzlich erforderlich:

- `USE CATALOG`-Privileg auf den übergeordneten Katalog und `USE SCHEMA`-Privileg auf das übergeordnete Schema.
- Eigentümerschaft an der Streaming Table oder `REFRESH`-Privileg auf die Streaming Table.
- Der Eigentümer der Streaming Table muss `SELECT`-Privileg auf die referenzierten Basistabellen besitzen.

Um die resultierende Streaming Table abfragen zu können, sind erforderlich:

- `USE CATALOG`-Privileg auf den übergeordneten Katalog und `USE SCHEMA`-Privileg auf das übergeordnete Schema.
- `SELECT`-Privileg auf die Streaming Table.

---

## <a id="einschraenkungen">5. Einschränkungen</a>

- Nur Tabelleneigentümer können Streaming Tables aktualisieren, um die aktuellsten Daten zu erhalten.
- `ALTER TABLE`-Befehle sind für Streaming Tables nicht zulässig. Definition und Eigenschaften der Tabelle müssen über `CREATE OR REFRESH` oder das `ALTER STREAMING TABLE`-Statement geändert werden.
- Die Evolution des Tabellenschemas über DML-Befehle wie `INSERT INTO` und `MERGE` wird nicht unterstützt.
- Folgende Befehle werden für Streaming Tables nicht unterstützt: `CREATE TABLE ... CLONE <streaming_table>`, `COPY INTO`, `ANALYZE TABLE`, `RESTORE`, `TRUNCATE`, `GENERATE MANIFEST`, `[CREATE OR] REPLACE TABLE`.
- Das Umbenennen der Tabelle oder das Ändern des Eigentümers wird nicht unterstützt.

---

## <a id="doku-beispiele">6. Doku-eigene Beispiele</a>

```sql
-- Define a streaming table from a volume of files:
CREATE OR REFRESH STREAMING TABLE customers_bronze
AS SELECT * FROM STREAM read_files("/databricks-datasets/retail-org/customers/*", format => "csv")

-- Define a streaming table from a streaming source table:
CREATE OR REFRESH STREAMING TABLE customers_silver
AS SELECT * FROM STREAM(customers_bronze)

-- Use automatic liquid clustering to let Databricks choose the clustering columns:
CREATE OR REFRESH STREAMING TABLE customers_bronze_auto
CLUSTER BY AUTO
AS SELECT * FROM STREAM read_files("/databricks-datasets/retail-org/customers/*", format => "csv")

-- Define a table with a row filter and column mask:
CREATE OR REFRESH STREAMING TABLE customers_silver (
  id int COMMENT 'This is the customer ID',
  name string,
  region string,
  ssn string MASK catalog.schema.ssn_mask_fn COMMENT 'SSN masked for privacy'
)
WITH ROW FILTER catalog.schema.us_filter_fn ON (region)
AS SELECT * FROM STREAM(customers_bronze)

-- Define a streaming table with an identity column:
CREATE OR REFRESH STREAMING TABLE customers_with_id (
  customer_id BIGINT GENERATED ALWAYS AS IDENTITY,
  name string,
  region string
)
AS SELECT name, region FROM STREAM(customers_bronze)

-- Define a streaming table that you can add flows into:
CREATE OR REFRESH STREAMING TABLE orders;

-- Define a streaming table with an inline append flow:
CREATE OR REFRESH STREAMING TABLE raw_data
FLOW INSERT BY NAME SELECT * FROM STREAM read_files('abfss://my_path');

-- Define a streaming table with an inline AUTO CDC flow:
CREATE OR REFRESH STREAMING TABLE target
FLOW AUTO CDC
FROM stream(cdc_data.users)
KEYS (userId)
SEQUENCE BY sequenceNum
STORED AS SCD TYPE 1;

-- Define a streaming table with an inline REPLACE USING flow that keeps the latest
-- row for each payment_id:
CREATE OR REFRESH STREAMING TABLE payments_current
FLOW REPLACE USING (payment_id) SEQUENCE BY payment_date BY NAME
SELECT payment_id, booking_id, status, payment_date
FROM STREAM(samples.wanderbricks.payments);
```

---

## <a id="dbsql-variante">7. Databricks-SQL-Variante der Sprachreferenz (`sql-ref-syntax-ddl-create-streaming-table`)</a>

Neben der oben behandelten **Pipelines-Entwickler-Referenz** (`/ldp/developer/ldp-sql-ref-create-streaming-table`) existiert die **klassische SQL-Sprachreferenz** (`/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table`). Sie beschreibt dieselbe Anweisung aus Sicht von **Databricks SQL** und weicht in einigen Punkten ab.

> **Gilt für:** Databricks SQL.
> **Hinweis:** *"Streaming tables are only supported in Lakeflow pipelines and on Databricks SQL with Unity Catalog."*

### Abweichende formale Syntax

```
{ CREATE OR REFRESH STREAMING TABLE | CREATE STREAMING TABLE [ IF NOT EXISTS ] }
  table_name
  [ table_specification ]
  [ table_clauses ]
  [ {flow_clause | AS query} ]

table_specification
  ( { column_identifier column_type [column_properties] } [, ...]
    [ CONSTRAINT expectation_name EXPECT (expectation_expr)
      [ ON VIOLATION { FAIL UPDATE | DROP ROW } ] ] [, ...]
    [ , table_constraint ] [...] )

column_properties
  { NOT NULL |
    GENERATED ALWAYS AS ( expr ) |
    GENERATED { ALWAYS | BY DEFAULT } AS IDENTITY [ ( [ START WITH start | INCREMENT BY step ] [ ...] ) ] |
    DEFAULT default_expression |
    COMMENT column_comment |
    column_constraint |
    MASK clause } [ ... ]

table_clauses
  { PARTITIONED BY (col [, ...]) |
    CLUSTER BY clause |
    COMMENT table_comment |
    DEFAULT COLLATION UTF8_BINARY |
    TBLPROPERTIES clause |
    schedule |
    WITH { ROW FILTER clause } } [...]

flow_clause
  FLOW { { INSERT BY NAME query } |
  { AUTO CDC auto_cdc_flow_spec } |
  { REPLACE WHERE predicate BY NAME query } |
  { REPLACE USING ( column_name [, ...] ) SEQUENCE BY sequence_column BY NAME query } }

schedule
  { SCHEDULE [ REFRESH ] schedule_clause |
    TRIGGER ON UPDATE [ AT MOST EVERY trigger_interval ] }

schedule_clause
  { EVERY number { HOUR | HOURS | DAY | DAYS | WEEK | WEEKS } |
    CRON cron_string [ AT TIME ZONE timezone_id ] }
```

**Unterschiede gegenüber der Pipelines-Referenz (Abschnitt 2):**

- Zusätzlich: `CREATE STREAMING TABLE [ IF NOT EXISTS ]` als Alternative zu `CREATE OR REFRESH`.
- **Kein** `PRIVATE`, **kein** `USING DELTA`, **kein** `LOCATION` in dieser Variante.
- Zusätzliche `table_clauses`: **`DEFAULT COLLATION UTF8_BINARY`** und die **`schedule`**-Klausel direkt inline.
- Die `schedule`-Klausel bietet zwei Modi: zeitgesteuert (`SCHEDULE [REFRESH] EVERY n HOURS|DAYS|WEEKS` bzw. `SCHEDULE [REFRESH] CRON '<cron>' [AT TIME ZONE '<tz>']`) **oder** ereignisgesteuert (`TRIGGER ON UPDATE [ AT MOST EVERY <interval> ]`, Refresh bei Upstream-Änderungen, höchstens einmal je Intervall).
- Die Doku-Abschnitte heißen hier: *Parameters*, *Differences between streaming tables and other tables*, *Row filters and column masks*, *Limitations*, *Examples*, *Related articles*.

### Zusätzliche Hinweise dieser Seite

- **Identity-Spalten:** *"Declaring an identity column on a table disables concurrent transactions. Only use identity columns in use cases where concurrent writes are not required."*
- **`FLOW INSERT BY NAME` ≡ `AS query`:** *"The following two statements have identical behavior."*
- **Full Refresh:** *"It is not recommended to call full refreshes on sources that don't keep the entire history of the data or have short retention periods, such as Kafka."*
- **CRON:** *"`AT TIME ZONE LOCAL` is not supported."*

### Zusätzliche Doku-Beispiele dieser Variante

```sql
-- Creates a streaming table with liquid clustering on order_date and customer_id.
CREATE OR REFRESH STREAMING TABLE orders_with_cluster_by
  CLUSTER BY (order_date, customer_id)
  AS SELECT
    o_orderkey   AS order_id,
    o_custkey    AS customer_id,
    o_orderdate  AS order_date,
    o_totalprice AS total_price
  FROM STREAM(samples.tpch.orders);
```

```sql
-- Stores the data from Kafka in an append-only streaming table.
CREATE OR REFRESH STREAMING TABLE firehose_raw
  COMMENT 'Stores the raw data from Kafka'
  TBLPROPERTIES ('delta.appendOnly' = 'true')
  AS SELECT
    value raw_data,
    offset,
    timestamp,
    timestampType
  FROM STREAM read_kafka(bootstrapServers => 'ips', subscribe => 'topic_name');
```

```sql
-- Creates a streaming table that scheduled to refresh when upstream data is updated.
-- The refresh frequency of triggered_data is at most once an hour.
CREATE STREAMING TABLE triggered_data
  TRIGGER ON UPDATE AT MOST EVERY INTERVAL 1 hour
  AS SELECT *
  FROM STREAM source_stream_data;
```

```sql
-- Read data from another streaming table scheduled to run every hour.
CREATE STREAMING TABLE firehose_bronze
  SCHEDULE EVERY 1 HOUR
  AS SELECT
    from_json(raw_data, 'schema_string') data,
    * EXCEPT (raw_data)
  FROM STREAM firehose_raw;
```

```sql
-- Creates a streaming table with schema evolution and data quality expectations.
-- The table creation or refresh fails if the data doesn't satisfy the expectation.
CREATE OR REFRESH STREAMING TABLE avro_data (
    CONSTRAINT date_parsing EXPECT (to_date(dt) >= '2000-01-01') ON VIOLATION FAIL UPDATE
  )
  AS SELECT *
  FROM STREAM read_files('gs://my-bucket/avroData');
```

```sql
-- Creates a streaming table with a column constraint
CREATE OR REFRESH STREAMING TABLE csv_data (
    id int PRIMARY KEY,
    ts timestamp,
    event string
  )
  AS SELECT *
  FROM STREAM read_files(
      's3://bucket/path',
      format => 'csv',
      schema => 'id int, ts timestamp, event string');
```

```sql
-- Creates a streaming table with a table constraint
CREATE OR REFRESH STREAMING TABLE csv_data (
    id int,
    ts timestamp,
    event string,
    CONSTRAINT pk_id PRIMARY KEY (id)
  )
  AS SELECT *
  FROM STREAM read_files(
      's3://bucket/path',
      format => 'csv',
      schema => 'id int, ts timestamp, event string');
```

```sql
-- Creates a streaming table with a row filter and a column mask
CREATE OR REFRESH STREAMING TABLE masked_csv_data (
    id int,
    name string,
    region string,
    ssn string MASK catalog.schema.ssn_mask_fn
  )
  WITH ROW FILTER catalog.schema.us_filter_fn ON (region)
  AS SELECT *
  FROM STREAM read_files('s3://bucket/path/sensitive_data')
```

**Related articles dieser Seite:** `read_files`, `read_kafka`, `DROP TABLE`, `SHOW CREATE TABLE`, constraint clause, *Filtering sensitive table data with row filters and column masks*, `ALTER STREAMING TABLE`, `REFRESH TABLE` (siehe `09 REFRESH (MV oder ST).md`), *AUTO CDC FLOW Clause*, *The AUTO CDC APIs*, *Load and process data incrementally with Lakeflow pipeline flows*.

---

## <a id="quellen">8. Quellen</a>

- CREATE STREAMING TABLE (pipelines) — SQL-Sprachreferenz (formale Syntax, alle Parameter, notwendige Berechtigungen, Einschränkungen, neun Doku-Beispiele, Versionsangaben zu `GENERATED ALWAYS AS IDENTITY`/`DEFAULT`/Read-Options/`AUTO CDC`/`REPLACE USING`): https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-streaming-table
- CREATE STREAMING TABLE — klassische SQL-Sprachreferenz / Databricks-SQL-Variante (Abschnitt 7: `IF NOT EXISTS`, `DEFAULT COLLATION`, `schedule`-Klausel mit `SCHEDULE`/`CRON`/`TRIGGER ON UPDATE`, `read_kafka`-Beispiele, Hinweis „`AT TIME ZONE LOCAL` is not supported"): https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table
- ALTER STREAMING TABLE — SQL-Sprachreferenz (vollständige Liste der unterstützten Unterklauseln, `CLUSTER BY` explizit nicht enthalten): https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-streaming-table
- Full refresh for streaming tables (welche Änderungen einen Full Refresh erfordern, was ein Full Refresh konkret tut, Warnung zu Quellen mit begrenzter Retention): https://docs.databricks.com/aws/en/ldp/full-refresh-st
- REFRESH (MATERIALIZED VIEW or STREAMING TABLE) — SQL-Sprachreferenz (formale Syntax inkl. `FULL`-Option): https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-refresh-full

**Stand:** 2026-09-02.
