### Materialized View

Eine **Materialized View** ist eine View, die ihre Abfrageergebnisse vorab berechnet und speichert. Die Ergebnisse spiegeln den Datenstand zum Zeitpunkt der letzten Aktualisierung der Materialized View wider.

Das Berechtigungsmodell für Materialized Views entspricht dem von Standard-Views. Zusätzlich zu `SELECT` und `MANAGE` unterstützen Materialized Views das `REFRESH`-Privileg, mit dem ein Nutzer eine Aktualisierung der Materialized-View-Ergebnisse auslösen kann. Nutzer mit nur `SELECT` und den passenden [Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges) können die gespeicherten Ergebnisse abfragen, aber keine Aktualisierung auslösen.

Weitere Informationen zu Materialized Views siehe [Materialized Views](https://docs.databricks.com/aws/en/ldp/concepts/materialized-views).

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### CREATE MATERIALIZED VIEW

Legt eine Materialized View an, optional mit einem Aktualisierungsplan (`SCHEDULE`/`TRIGGER ON UPDATE`), Constraints, Partitionierung oder Zeilen-/Spaltensicherheit.

```sql
-- Materialized View, die aktualisiert wird, sobald sich die Quelldaten ändern
CREATE MATERIALIZED VIEW IF NOT EXISTS subscribed_movies
  TRIGGER ON UPDATE
  AS SELECT mo.member_id, mb.full_name, mo.movie_title
       FROM movies AS mo INNER JOIN members AS mb ON mo.member_id = mb.id;

-- Täglich per Zeitplan aktualisierte Materialized View
CREATE MATERIALIZED VIEW daily_sales
  COMMENT 'Daily sales numbers'
  SCHEDULE EVERY 1 DAY
  AS SELECT date AS date, sum(sales) AS sumOfSales
       FROM table1
       GROUP BY date;

-- Materialized View mit Row Filter und Column Mask
CREATE MATERIALIZED VIEW masked_view (
    id int,
    name string,
    region string,
    ssn string MASK catalog.schema.ssn_mask_fn
  )
  WITH ROW FILTER catalog.schema.us_filter_fn ON (region)
  AS SELECT id, name, region, ssn
       FROM employees;
```

Quelle: [CREATE MATERIALIZED VIEW](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-materialized-view)

### ALTER MATERIALIZED VIEW

Ändert den Aktualisierungsplan, Spalten-Eigenschaften oder den Besitzer einer Materialized View.

```sql
-- Aktualisierung auslösen, sobald sich die Quelldaten ändern
ALTER MATERIALIZED VIEW my_mv ADD TRIGGER ON UPDATE;

-- Zeitplan auf alle 2 Stunden ändern
ALTER MATERIALIZED VIEW my_mv ALTER SCHEDULE EVERY 2 HOURS;

-- Zeitplan per Cron-Ausdruck ändern (täglich um Mitternacht, Zeitzone Los Angeles)
ALTER MATERIALIZED VIEW my_mv ALTER SCHEDULE CRON '0 0 0 * * ? *' AT TIME ZONE 'America/Los_Angeles';
```

Quelle: [ALTER MATERIALIZED VIEW](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-materialized-view)

### EXPLAIN CREATE MATERIALIZED VIEW

Prüft, ob eine Materialized View inkrementell aktualisiert werden kann (statt vollständiger Neuberechnung), bevor sie tatsächlich angelegt wird.

```sql
EXPLAIN CREATE MATERIALIZED VIEW foo
AS
SELECT k, sum(v) FROM source.src_schema.table GROUP BY k;
```

Quelle: [EXPLAIN CREATE MATERIALIZED VIEW](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-explain-materialized-view)
