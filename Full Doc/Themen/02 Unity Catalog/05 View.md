## View

Innerhalb eines [Schemas](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#schema) ist eine **View** ein schreibgeschütztes Objekt, definiert durch eine gespeicherte SQL-Abfrage über eine oder mehrere Tabellen oder andere Views. Views berechnen ihre Ergebnisse bei jeder Abfrage neu.

Die folgende Tabelle fasst wichtige Details zu Views zusammen:

| Detail | Beschreibung |
| :--------------- | :----------------------------------------------------------- |
| Nutzungsprivilegien | Um auf eine View zuzugreifen, benötigt ein Nutzer `USE CATALOG` auf dem übergeordneten Katalog und `USE SCHEMA` auf dem übergeordneten Schema ([Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges)), zusätzlich zu `SELECT` auf der View. Der Nutzer benötigt keine Privilegien auf den zugrunde liegenden Tabellen, die die View abfragt — die Privilegien des View-Eigentümers werden zur Laufzeit verwendet, um die zugrunde liegenden Tabellen aufzulösen. Für Tabelleneigentümer macht das Views nützlich, um Zugriff auf bestimmte Zeilen oder Spalten einzuschränken, ohne die zugrunde liegenden Tabellen direkt offenzulegen. |
| Vererbung | Auf Schema- oder Katalog-Ebene vergebenes `SELECT` gilt für alle aktuellen und künftigen Views in diesem Schema bzw. Katalog. Siehe [Privilegienvererbung](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#inheritance). |

Weitere Informationen zu Views siehe [Was ist eine View?](https://docs.databricks.com/aws/en/views/).

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### ALTER VIEW

Ändert Name, Definition, Eigentümer oder Eigenschaften einer bestehenden View.

```sql
-- View umbenennen
ALTER VIEW tempsc1.v1 RENAME TO tempsc1.v2;

-- View-Definition (Abfrage) ändern
ALTER VIEW tempsc1.v2 AS SELECT * FROM tempsc1.v1;

-- Besitzer übertragen
ALTER VIEW v1 OWNER TO `alf@melmak.et`;
```

Quelle: [ALTER VIEW](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-view)

### ALTER VIEW … SET MANAGED

Wandelt eine Foreign View (z. B. aus HMS-Föderation) in eine reguläre, von Unity Catalog verwaltete View um; danach wird die Definition nicht mehr automatisch mit dem externen Katalog synchronisiert.

```sql
ALTER VIEW hms_federated_catalog.my_schema.my_view SET MANAGED;
```

Quelle: [ALTER VIEW SET MANAGED](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-view-set-managed)

### CREATE VIEW

Legt eine neue View auf Basis einer Abfrage an, optional mit Spaltenkommentaren, Schema-Binding-Verhalten oder als temporäre View.

```sql
-- View mit Kommentaren und WHERE-Filter
CREATE OR REPLACE VIEW experienced_employee
    (id COMMENT 'Unique identification number', Name)
    COMMENT 'View for experienced employees'
    AS SELECT id, name
         FROM all_employee
        WHERE working_years > 5;

-- Temporäre View (nur für die aktuelle Session sichtbar)
CREATE TEMPORARY VIEW subscribed_movies
    AS SELECT mo.member_id, mb.full_name, mo.movie_title
         FROM movies AS mo
         INNER JOIN members AS mb
            ON mo.member_id = mb.id;

-- View mit SCHEMA EVOLUTION, damit sie Änderungen der Basistabelle automatisch übernimmt
CREATE VIEW emp_v WITH SCHEMA EVOLUTION AS SELECT * FROM emp;
```

Quelle: [CREATE VIEW](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-view)

### DROP VIEW

Löscht eine View (oder mit `MATERIALIZED VIEW` eine Materialized View).

```sql
DROP VIEW IF EXISTS employeeView;
DROP VIEW usersc.employeeView;
```

Quelle: [DROP VIEW](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-view)

### SHOW VIEWS

Listet Views eines Schemas auf, inklusive temporärer Views, optional gefiltert per `LIKE`-Muster.

```sql
SHOW VIEWS FROM usersc;
SHOW VIEWS LIKE 'sam*';
```

Quelle: [SHOW VIEWS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-views)
