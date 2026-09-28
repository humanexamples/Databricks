# `REFRESH` (MATERIALIZED VIEW oder STREAMING TABLE) — Referenz

> **Gilt für:** Databricks SQL

Aktualisiert die Daten einer Streaming Table oder einer Materialized View. Der Refresh erfolgt standardmäßig **synchron**. Den Status eines Refreshs verfolgt man mit `DESCRIBE EXTENDED`.

> **Hinweis:** Create- und Refresh-Operationen auf Materialized Views und Streaming Tables werden von **serverlosen Lakeflow-Pipelines** ausgeführt. Details zu den dahinterliegenden Pipelines lassen sich im Catalog Explorer einsehen.

> **Hinweis:** `REFRESH MATERIALIZED VIEW` gilt auch für **materialisierte Metric Views** — damit lassen sich die Materialisierungen hinter einer Metric View manuell aktualisieren.

---

## Syntax

```
REFRESH { MATERIALIZED VIEW | [ STREAMING ] TABLE } table_name
  [ FULL ] [ WHERE predicate ] [ SYNC | ASYNC ]
```

`FULL`, `WHERE` und `SYNC`/`ASYNC` lassen sich in beliebiger Teilmenge im selben Befehl kombinieren.

---

## Parameter

### `table_name`

Identifiziert die zu aktualisierende Materialized View oder Streaming Table. Der Name darf **keine** temporale Angabe und **keine** Options-Spezifikation enthalten. Wird das Objekt nicht gefunden, wirft Databricks den Fehler `TABLE_OR_VIEW_NOT_FOUND`.

### `FULL`

Ob ein vollständiger Refresh durchgeführt wird.

- **Materialized Views:** Ein Full Refresh verarbeitet **alle** in der Quelle verfügbaren Daten.
- **Streaming Tables:** Ein Full Refresh **leert die Tabelle (Truncate)** und verarbeitet alle in der Quelle verfügbaren Daten mit der **aktuellsten Definition** der Streaming Table neu.

> Für Quellen **ohne** vollständige Historie oder mit kurzer Aufbewahrungsfrist (z. B. Kafka) wird ein Full Refresh **nicht empfohlen**, da er bestehende Daten abschneidet — alte Daten sind ggf. nicht wiederherstellbar, wenn sie in der Quelle nicht mehr verfügbar sind.

### `WHERE predicate`

> **Gilt für:** Streaming Tables, die mit einer `FLOW REPLACE WHERE`-Klausel erstellt wurden.

Überschreibt das `REPLACE WHERE`-Prädikat des Flows für **diesen einen** Refresh. Der Refresh löscht nur die Zeilen, die `predicate` entsprechen, aus dem Ziel und berechnet sie aus der Quelle neu. Das im Flow definierte Prädikat bleibt unverändert und gilt beim nächsten Refresh wieder — ein Predicate-Override ist also eine **einmalige** Operation, die die Tabellendefinition nicht ändert. Anwendung: einmalige Backfills oder Korrekturen.

Die `WHERE`-Klausel wird **nur** für Streaming Tables unterstützt, deren Flow mit `FLOW REPLACE WHERE` erstellt wurde. `WHERE` auf einer anderen Streaming Table oder auf einer Materialized View liefert einen Fehler.

### `SYNC`

Synchroner Refresh — der Befehl **blockiert**, bis die Materialized View bzw. Streaming Table erstellt und der initiale Datenladevorgang abgeschlossen ist. Dies ist das **Standardverhalten**.

### `ASYNC`

Asynchroner Refresh — startet einen Hintergrund-Job auf Lakeflow-Pipelines. Der Befehl kehrt **sofort** zurück (vor Abschluss des Datenladevorgangs) und liefert einen Link zur Pipeline hinter der Materialized View bzw. Streaming Table, über den sich der Status einsehen lässt. `ASYNC` muss explizit angegeben werden; ohne Schlüsselwort läuft die Operation synchron.

---

## Beispiele

```sql
-- Refreshes the materialized view to reflect the latest available data
REFRESH MATERIALIZED VIEW catalog.schema.view_name;

-- Refreshes the streaming table to process the latest available data
-- The current catalog and schema will be used to qualify the table
REFRESH STREAMING TABLE st_name;

-- Truncates the table and processes all data from scratch for the streaming table
REFRESH STREAMING TABLE cat.db.st_name FULL;

-- Overrides the REPLACE WHERE predicate for a single asynchronous refresh.
-- Only rows matching id = 3 are recomputed. The flow's static predicate is unchanged.
REFRESH STREAMING TABLE rep_st WHERE id = 3 ASYNC;
```

---

## Verwandte Anweisungen

- `CREATE MATERIALIZED VIEW` — siehe `03 CREATE MATERIALIZED VIEW.md`
- `CREATE STREAMING TABLE` — siehe `05 CREATE STREAMING TABLE.md`
- REPLACE WHERE flows for standalone streaming tables: `/aws/en/ldp/dbsql/flows-replace-where`
- Materialization for metric views: `/aws/en/uc-semantics/metric-views/materialization`

---

## Quellen

- REFRESH (MATERIALIZED VIEW or STREAMING TABLE) — SQL-Sprachreferenz: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-refresh-full

**Stand:** 2026-09-02.
