# Schema Governance

**Schema Governance** ist über **Unity Catalog** (Berechtigungen, Lineage, Auditing) relevant, aber eher ein **organisatorisches** als ein technisches Thema — es geht um Kontrolle, nicht um Mechanik.

## Zwei Bedeutungen von „Schema" — wichtige Vorab-Klärung

Der Begriff „Schema" meint in Databricks zwei verschiedene Dinge, die beide für Governance relevant sind:

1. **Tabellenschema** — die Spalten-/Typ-Struktur einer Tabelle (Thema der übrigen Dateien in diesem Ordner: [Schema Evolution.md](Schema%20Evolution.md), [Schema Enforcement.md](Schema%20Enforcement.md) usw.).
2. **Unity-Catalog-„Schema"** — das **Securable Object** eine Ebene unter Catalog im Drei-Ebenen-Namespace (`catalog.schema.table`), grob vergleichbar mit einer „Datenbank" in anderen Systemen. Enthält Tabellen, Views, Volumes, Functions, Models.

Diese Datei behandelt Governance für **beide** Bedeutungen — im Folgenden klar getrennt als „UC-Schema" (Container) und „Tabellenschema" (Struktur).

---

## A. Governance des UC-Schema-Containers

### Anlegen

```sql
CREATE SCHEMA [IF NOT EXISTS] catalog_name.schema_name
  [COMMENT 'Beschreibung']
  [MANAGED LOCATION 'path'];
```

### Berechtigungen vergeben

```sql
GRANT USE SCHEMA ON SCHEMA main.default TO `finance-team`;
GRANT CREATE TABLE ON SCHEMA main.default TO `finance-team`;
GRANT USE CATALOG ON CATALOG main TO `finance-team`;
```

Verifizierte Privilegien **auf Schema-Ebene** (u. a.): `USE SCHEMA`, `CREATE TABLE`, `CREATE FUNCTION`, `CREATE MODEL`, `CREATE VOLUME`, `CREATE MATERIALIZED VIEW`, `APPLY TAG`, `MANAGE`, `READ METADATA`, `EXTERNAL USE SCHEMA`, `ALL PRIVILEGES`. Zusätzlich wirken auf Schema-Ebene vergebene Objekt-Privilegien (`SELECT`, `MODIFY`, `INSERT`, `UPDATE`, `DELETE`, `EXECUTE` u. a.) auf **alle enthaltenen Objekte**.

> Konkretes Beispiel aus der Doku: *„To add a table, you must be the schema owner or have USE SCHEMA and CREATE TABLE on the schema and USE CATALOG on the parent catalog."*

### Vererbung im Drei-Ebenen-Namespace

*„A privilege granted on a catalog applies to all schemas in that catalog, and all tables, views, volumes, and functions in those schemas."*

- Ein `GRANT SELECT ... ON CATALOG main TO ...` wirkt also automatisch auf **alle** aktuellen **und künftigen** Schemas/Tabellen darin — nicht nur auf den Ist-Zustand.
- `USE CATALOG` auf der übergeordneten Catalog-Ebene ist zusätzlich zu `USE SCHEMA` **immer** nötig, um überhaupt bis zum Schema durchzugreifen (die Ebenen wirken kumulativ, nicht alternativ).

### Ownership

Jedes Securable Object (Catalog, Schema, Tabelle, …) hat **genau einen** Owner. Ownership wird nicht wie ein Privileg gegrantet, sondern per `ALTER SCHEMA catalog.schema SET OWNER TO principal` (analog `ALTER TABLE ... SET OWNER TO`) übertragen — nur der aktuelle Owner oder ein Metastore-Admin kann das. Ownership vererbt sich **nicht** automatisch nach unten: Owner eines Schemas zu sein macht einen nicht automatisch zum Owner der enthaltenen Tabellen.

---

## B. Governance von Tabellenschema-Änderungen

Für strukturelle `ALTER TABLE`-Operationen (Spalten hinzufügen/ändern/löschen) gilt laut Doku:

> *„If you use Unity Catalog you must have `MODIFY` permission to: `ALTER COLUMN`, `ADD COLUMN`, `DROP COLUMN`, `SET TBLPROPERTIES`, `UNSET TBLPROPERTIES`."*

- **`MODIFY`** genügt also für Schema-Änderungen per `ALTER TABLE` — dieselbe Berechtigung, die auch Dateninhalte ändern darf (`INSERT`/`UPDATE`/`DELETE`), deckt strukturelle Änderungen mit ab.
- **Ownership-only-Operationen:** *„If you use Unity Catalog you must have `MANAGE` permission or ownership to: `SET OWNER TO`, `PREDICTIVE OPTIMIZATION`."* Sowie: *„All other operations require ownership of the table, including `SET MANAGED` and `UNSET MANAGED`."*
- Für Tag-Änderungen (`SET TAGS`/`UNSET TAGS`) gilt eine eigene, engere Berechtigung: `APPLY TAG` (siehe Abschnitt „Spalten-Tags" unten).
- Syntaxdetails zu `ALTER TABLE` selbst: siehe [Schema Evolution.md](Schema%20Evolution.md).

---

## C. Lineage vs. Schema-Historie — nicht verwechseln

**Bestätigte Abgrenzung:** Unity-Catalog-Lineage trackt **Datenfluss** (welche Query/welcher Job hat welche Upstream-Spalte in welche Downstream-Spalte transformiert) — **nicht** die Änderungshistorie des Tabellenschemas selbst.

- Lineage wird automatisch für Queries erfasst, die die Spark-DataFrame- oder Databricks-SQL-Schnittstellen nutzen, bis auf **Spaltenebene**, sichtbar im **Lineage-Tab** des Catalog Explorers oder abfragbar über die System-Tabellen `system.access.table_lineage` / `system.access.column_lineage`.
- Zweck laut Doku: *Impact-Analyse* (welche Downstream-Objekte sind betroffen, bevor eine Tabelle/Spalte geändert wird), *Root-Cause-Analyse*, *Sensitive-Data-Tracking*.
- **Explizite Doku-Einschränkung, die die Abgrenzung stützt:** *„Lineage is not preserved for renamed catalogs, schemas, tables, views, or columns."* — würde Lineage eine Schema-Änderungshistorie führen, müsste eine Umbenennung gerade **erfasst** statt **verworfen** werden. Das bestätigt: Lineage ist ein Datenfluss-Graph, kein Schema-Audit-Trail.
- Lineage-Daten werden **unbegrenzt** in Catalog Explorer vorgehalten (ab 1. September 2024); die Lineage-System-Tabellen halten ein **rollierendes 1-Jahres-Fenster**.

**Was Lineage nicht ersetzt:** Die tatsächliche Historie von Schema-Edits (wann wurde welche Spalte hinzugefügt/umbenannt/gelöscht) liefert Delta Lakes eigenes Transaktionsprotokoll (`DESCRIBE HISTORY`) — siehe [Schema Versioning.md](Schema%20Versioning.md).

---

## D. Auditing

Unity-Catalog-Ereignisse (inkl. DDL wie `CREATE TABLE`, `ALTER TABLE`) werden im Audit-Log unter `service_name = 'unityCatalog'` erfasst und über die System-Tabelle `system.access.audit` abfragbar — Aktionsnamen wie `createTable`, `updateTable`, `updateSchema`, `deleteTable` tauchen dort als `action_name` auf.

- **Ungeklärt/nicht abschließend verifiziert:** Die vollständige, autoritative Liste aller `unityCatalog`-Aktionsnamen ließ sich über die abgerufenen Doku-Seiten nicht lückenlos bestätigen (die Referenzseite ist sehr lang und wurde beim Abruf mehrfach abgeschnitten) — die oben genannten Aktionsnamen sind über mehrere unabhängige Quellen konsistent, aber nicht wörtlich aus der Primärseite zitiert. Vor Prüfungsnutzung ggf. gegen die aktuelle „Audit Unity Catalog events"-Referenzseite gegenprüfen.

---

## E. Spalten-Tags als Governance-Mechanismus

Tags markieren z. B. sensible Spalten für Klassifikation (PII, Vertraulichkeitsstufe):

```sql
ALTER TABLE main.schema1.test ALTER COLUMN col1 SET TAGS ('classification' = 'pii');
ALTER TABLE main.schema1.test ALTER COLUMN col1 UNSET TAGS ('classification');
```

Benötigt die Berechtigung **`APPLY TAG`** (bestätigt: *„You need to have `APPLY TAG` permission to add tags to the table."* — gilt analog für Spalten-Tags).

Abfragbar über die Information-Schema-View:

```sql
SELECT * FROM main.information_schema.column_tags WHERE tag_name = 'classification';
```

(Spalten: `catalog_name`, `schema_name`, `table_name`, `column_name`, `tag_name`, `tag_value`.)

**Verwandter, aber separater Mechanismus:** Column Masking und Row Filters (Daten selbst verbergen/filtern statt nur zu markieren) sind ein eigenes Governance-Thema, an anderer Stelle im Projekt behandelt — hier nicht vertieft.

---

## Verwandte Themen

- [Schema Definition.md](Schema%20Definition.md) · [Schema Enforcement.md](Schema%20Enforcement.md) · [Schema Evolution.md](Schema%20Evolution.md) · [Schema Inference.md](Schema%20Inference.md)
- [Schema Versioning.md](Schema%20Versioning.md) (Delta-Transaktionshistorie/`DESCRIBE HISTORY`, Abgrenzung zu Lineage siehe Abschnitt C)
- [Schema Migration.md](Schema%20Migration.md) · [Schema-on-Read vs. Schema-on-Write.md](Schema-on-Read%20vs.%20Schema-on-Write.md) · [Schema Mapping und Transformation.md](Schema%20Mapping%20und%20Transformation.md)
