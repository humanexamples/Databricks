# Schema Migration

**Was ist damit gemeint?** Es gibt in Databricks kein Menü und keinen Befehl namens "Schema Migration" — der Begriff beschreibt die **Aufgabe**, das Schema einer Produktions-Tabelle sicher weiterzuentwickeln (z. B. eine Spalte hinzufügen, umbenennen oder ihren Typ ändern), ohne bestehende Pipelines, Reports oder Streaming-Jobs kaputt zu machen. Die technischen Bausteine dafür (`ALTER TABLE`, Column Mapping) stehen in [Schema Evolution.md](Schema%20Evolution.md); diese Datei zeigt, **wie man sie in der Praxis sicher kombiniert** — Ablauf, Kompatibilität, Risiken, jeweils mit Codebeispiel.

**Abgrenzung:** Nicht zu verwechseln mit **Catalog-Migration** (z. B. Hive Metastore → Unity Catalog) — das ist ein anderes, unabhängiges Migrationsthema an anderer Stelle im Projekt.

---

## Warum ist das überhaupt riskant?

Eine Tabelle wird meistens von mehreren Stellen gleichzeitig genutzt: Dashboards, andere Pipelines, laufende Streaming-Jobs. Ändert sich das Schema, sehen **alle** diese Verbraucher die Änderung sofort — es gibt keine "alte Version" der Tabelle, die parallel weiterläuft, während die neue getestet wird. Manche Änderungen sind völlig harmlos (z. B. eine neue, optionale Spalte), andere brechen bestehenden Code, der z. B. eine Spalte über ihren Namen anspricht, den es danach nicht mehr gibt. Migration bedeutet deshalb vor allem: die **Reihenfolge und Absicherung** der Schritte so wählen, dass nichts überraschend kaputtgeht.

---

## Welche Änderungen sind unkritisch, welche brechend?

**Spalte hinzufügen (nullable).** Das ist der unkritischste Fall. Bestehende Reader, die die neue Spalte gar nicht kennen, ignorieren sie einfach; für bereits vorhandene (alte) Zeilen wird sie automatisch mit `NULL` befüllt. Es ist keine Voraussetzung nötig:

```sql
ALTER TABLE catalog.schema.table_name ADD COLUMNS (new_col STRING);
```

**Spalte umbenennen.** Das bricht jeden Reader bzw. jede gespeicherte Query, die noch den alten Namen verwendet — die Spalte existiert unter diesem Namen ab sofort nicht mehr. Ein dauerhaftes Umbenennen ist nur möglich, wenn **Column Mapping** aktiviert ist (Begründung dazu im nächsten Abschnitt):

```sql
ALTER TABLE catalog.schema.table_name RENAME COLUMN old_col_name TO new_col_name;
```

**Spalte löschen.** Genauso brechend wie Umbenennen — jeder Code, der die Spalte referenziert, schlägt danach fehl. Erfordert ebenfalls Column Mapping:

```sql
ALTER TABLE catalog.schema.table_name DROP COLUMN old_col_name;
```

**Datentyp ändern (Type Widening).** Meist unkritisch — aber nur, wenn es sich um eine reine **Verbreiterung** handelt (z. B. `INT` → `BIGINT`, `FLOAT` → `DOUBLE`), bei der jeder alte Wert verlustfrei in den neuen Typ passt. Erfordert die Tabelleneigenschaft `delta.enableTypeWidening` sowie mindestens Databricks Runtime 15.4 LTS (vollständige Liste erlaubter Typwechsel: [Schema Mapping und Transformation.md](Schema%20Mapping%20und%20Transformation.md)):

```sql
ALTER TABLE catalog.schema.table_name SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');
ALTER TABLE catalog.schema.table_name ALTER COLUMN price TYPE DOUBLE;
```

---

## Warum Column Mapping für Rename/Drop nötig ist

Spaltennamen sind normalerweise fest mit den physischen Spalten in den zugrunde liegenden Parquet-Dateien verdrahtet. Ohne Column Mapping müsste Databricks beim Umbenennen oder Löschen einer Spalte deshalb **alle** Datendateien der Tabelle neu schreiben — bei großen Tabellen teuer und langsam, und während der Migration blockierend.

Column Mapping trennt den sichtbaren Spaltennamen von der physischen Speicherung. Dadurch werden Rename und Drop zu reinen **Metadaten-Änderungen**, ohne dass eine einzige Datendatei angefasst wird: *"Delta Lake column mapping enables metadata-only changes to mark columns as deleted or renamed without rewriting data files."*

Voraussetzung ist mindestens Delta-Protokoll Reader-Version 2 / Writer-Version 5 — diese wird beim Aktivieren in der Regel automatisch mit angehoben. Aktivieren einer bestehenden Tabelle:

```sql
ALTER TABLE catalog.schema.table_name SET TBLPROPERTIES ('delta.columnMapping.mode' = 'name');
```

Details zu Modi (`name` vs. `id`) und weiteren Einschränkungen: siehe Table-Features-Referenz zu Column Mapping (nicht Teil dieser Datei).

---

## Produktionsauswirkung: laufende Streams

Eine Schema-Änderung betrifft nicht nur den historischen Datenbestand in der Tabelle, sondern auch alle **aktiven Streaming-Jobs**, die gerade von dieser Tabelle lesen. Laut Doku gilt: *"Updating a table schema terminates any streams reading from that table"* (bereits zitiert in [Schema Evolution.md](Schema%20Evolution.md)) — ein laufender Stream bricht also ab, sobald sich das Schema seiner Quelltabelle ändert. Das ist kein Fehlerfall, sondern erwartetes Verhalten.

Praktische Konsequenz für die Migrationsplanung: **jeder betroffene Streaming-Job muss nach der Schema-Änderung aktiv neu gestartet werden.** Das gehört von Anfang an fest in den Migrationsplan, nicht erst als reaktive Fehlerbehebung, nachdem der Stream überraschend abgebrochen ist.

---

## Rollback

Schlägt eine schemaändernde Migration fehl oder verursacht sie im Nachhinein Folgeprobleme, lässt sich die Tabelle per **Delta Time Travel** auf eine frühere Version zurücksetzen:

```sql
RESTORE TABLE catalog.schema.table_name TO VERSION AS OF 41;
```

Mechanik, Grenzen (Log-/Dateiretention, offene Fragen zum Schema-Rollback) und Zusammenspiel mit `VACUUM`: siehe [Schema Versioning.md](Schema%20Versioning.md).

---

## Beispielhafter Migrationsablauf (nicht-brechend)

Der folgende Ablauf zeigt, wie man eine neue Spalte einführt und am Ende sogar umbenennt, **ohne** dass zwischendurch etwas für bestehende Nutzer der Tabelle kaputtgeht.

**1. Neue Spalte nullable hinzufügen.** Sicherster erster Schritt — ändert nichts an bestehenden Daten oder Readern:

```sql
ALTER TABLE catalog.schema.table_name ADD COLUMNS (new_col STRING);
```

**2. Pipeline deployen**, die `new_col` ab sofort für neue Zeilen befüllt. Historische Zeilen bleiben vorerst `NULL` — das ist erwartet und unkritisch, da die Spalte nullable ist.

**3. Backfill und Validieren.** Historische `NULL`-Werte gezielt nachziehen, z. B. mit `UPDATE` oder `MERGE`, und danach die Datenqualität prüfen:

```sql
UPDATE catalog.schema.table_name
SET new_col = 'default_value'
WHERE new_col IS NULL;
```

**4. Erst nach erfolgreicher Validierung: verschärfen oder abschließen.** Jetzt, wo keine `NULL`-Werte mehr übrig sind, kann man z. B. eine `NOT NULL`-Bedingung erzwingen:

```sql
ALTER TABLE catalog.schema.table_name ALTER COLUMN new_col SET NOT NULL;
```

oder eine inhaltliche Prüfregel ergänzen:

```sql
ALTER TABLE catalog.schema.table_name
  ADD CONSTRAINT new_col_valid CHECK (new_col IN ('A', 'B', 'C'));
```

oder — falls gewünscht — die Spalte über Column Mapping endgültig umbenennen:

```sql
ALTER TABLE catalog.schema.table_name RENAME COLUMN new_col TO final_col_name;
```

**Kerngedanke:** additive, nullable Änderungen zuerst und isoliert ausrollen; restriktivere bzw. brechende Änderungen (Rename, Drop, `NOT NULL`) erst **nach** Validierung nachziehen.

---

## Verwandte Themen

- [Schema Evolution.md](Schema%20Evolution.md) · [Schema Enforcement.md](Schema%20Enforcement.md) · [Schema Versioning.md](Schema%20Versioning.md)
- [Schema-on-Read vs. Schema-on-Write.md](Schema-on-Read%20vs.%20Schema-on-Write.md) · [Schema Governance.md](Schema%20Governance.md) · [Schema Mapping und Transformation.md](Schema%20Mapping%20und%20Transformation.md)
