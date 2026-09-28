# Schema Versioning

**Kurz gesagt:** Delta Lake merkt sich zu jeder Tabellenversion auch, wie das Schema zu diesem Zeitpunkt aussah — das steckt im **Transaction Log** (`_delta_log`), das jede Tabelle automatisch mitführt. Eine **eigenständige "Schema Registry"**, wie man sie z. B. aus der Kafka-Welt (Confluent Schema Registry) kennt, gibt es bei Databricks für Delta-Tabellen dagegen **nicht**.

---

## Gibt es eine Schema Registry für Delta-Tabellen?

**Nein.** Es gibt kein Databricks-Produkt, das speziell dafür da ist, Delta-Tabellenschemata zentral zu verwalten oder zu versionieren. Was es stattdessen gibt, ist das Transaction Log: Jede Version einer Tabelle bekommt dort automatisch einen eigenen Eintrag, der u. a. das zu diesem Zeitpunkt gültige Schema enthält (mehr dazu unten bei `DESCRIBE HISTORY`).

**Die eine Stelle, an der Databricks tatsächlich mit einer "Schema Registry" zu tun hat — und warum das etwas anderes ist:** Wenn man Avro-Daten aus Kafka einliest, kann man sich über die Funktionen `from_avro`/`to_avro` an eine **externe** Schema Registry anbinden, zum Beispiel die Confluent Schema Registry:

> *"Databricks supports the `from_avro` and `to_avro` functions to build streaming pipelines with Avro data in Kafka and metadata in Schema Registry."*

> *"In Databricks Runtime 12.2 LTS and above, you can authenticate to an external Confluent Schema Registry."*

Wichtig ist der Unterschied: Diese Anbindung betrifft nur das **Avro-Format der eingehenden Kafka-Nachricht**. Sie hat nichts mit dem Schema der Delta-Tabelle zu tun, in die man die Daten am Ende schreibt. Es sind zwei völlig unabhängige Dinge — die Confluent-Registry kümmert sich um das Avro-Schema der Nachricht, das Delta-Transaction-Log kümmert sich um das Schema der Zieltabelle.

---

## Die Schema-Historie einer Tabelle ansehen: `DESCRIBE HISTORY`

```sql
DESCRIBE HISTORY catalog.schema.table_name;
```

Dieser Befehl zeigt alle bisherigen Versionen einer Tabelle als Tabelle mit insgesamt 14 Spalten. Für das Thema Schema sind vor allem diese vier interessant:

- **`version`** — die Versionsnummer
- **`timestamp`** — wann diese Version entstanden ist
- **`operation`** — welche Art von Vorgang die Version erzeugt hat (z. B. `WRITE`, `MERGE`, `RESTORE`)
- **`operationParameters`** — Details zu diesem Vorgang

---

## Time Travel und Schema

Mit Time Travel kann man eine Tabelle so abfragen, wie sie zu einem früheren Zeitpunkt aussah:

```sql
SELECT * FROM catalog.schema.table_name VERSION AS OF 12;
SELECT * FROM catalog.schema.table_name TIMESTAMP AS OF '2026-01-15';
```

Da jede Version im Transaction Log ihr eigenes Schema mitführt, liest man mit Time Travel automatisch auch das **damalige** Schema mit — nicht das heutige. Wie genau sich das im Detail auf einzelne Spalten auswirkt (z. B. ob eine Spalte, die erst später hinzugefügt wurde, in einer älteren Version dann einfach fehlt), ist in der offiziellen Databricks-Doku nicht mit einem eindeutigen Satz belegt. Das bleibt hier bewusst offen, statt es zu vermuten.

---

## Eine Tabelle zurücksetzen: `RESTORE TABLE`

```sql
RESTORE TABLE catalog.schema.table_name TO VERSION AS OF 12;
RESTORE TABLE catalog.schema.table_name TO TIMESTAMP AS OF '2026-01-15';
```

Ein paar Dinge, die man dazu wissen sollte:

- **Berechtigung:** *"To restore a table, you must have `MODIFY` permission for the table."*
- **Gelöschte Dateien:** *"After data files are deleted, manually or by `VACUUM`, you can't restore a table to an older version that references those files."* — man kann also nicht auf eine Version zurück, deren Datendateien inzwischen physisch gelöscht wurden.
- **Protokoll-Version:** Ein `RESTORE` stuft die Delta-Protokollversion standardmäßig **nicht** herunter, selbst wenn die Zielversion eine ältere, niedrigere Protokollversion hatte. Gesteuert wird das über `spark.databricks.delta.restore.protocolDowngradeAllowed` (per Default deaktiviert) — nach einem Restore läuft die Tabelle also weiterhin mit der neuesten Reader-/Writer-Protokollversion.
- **Offene Frage:** Ob `RESTORE` auch reine Schema-Änderungen rückgängig macht (z. B. eine Spalte, die nach der Zielversion per `ADD COLUMNS` hinzukam), oder nur den Datenstand zurücksetzt, ist in der offiziellen Doku nicht ausdrücklich beschrieben.

Praktischer Anwendungsfall als Rollback nach einer fehlgeschlagenen Migration: [Schema Migration.md](Schema%20Migration.md).

---

## Wie weit zurück reicht das alles? (Retention)

Zwei Tabelleneigenschaften bestimmen, wie lange man in der Vergangenheit einer Tabelle "graben" kann:

- **`delta.logRetentionDuration`** (Standardwert: `interval 30 days`) — so lange bleiben die Log-Einträge selbst erhalten, also auch das, was `DESCRIBE HISTORY` anzeigen kann.
- **`delta.deletedFileRetentionDuration`** (Standardwert: `interval 7 days`) — ab diesem Alter darf `VACUUM` nicht mehr benötigte Datendateien tatsächlich löschen.

`VACUUM` löscht Datendateien anhand von `deletedFileRetentionDuration`. Sind die Dateien einer bestimmten Version einmal gelöscht, schlagen sowohl Time Travel als auch `RESTORE` auf diese Version fehl — unabhängig davon, ob der Log-Eintrag selbst noch da ist.

Das führt zu einer wichtigen Feinheit: *"In Databricks Runtime 18.0 and above, time travel queries are blocked if they request a version older than the `deletedFileRetentionDuration` table property (default 7 days). For Unity Catalog managed tables, this applies to Databricks Runtime 12.2 and above."* Praktisch begrenzt also meist die **kürzere** Frist `deletedFileRetentionDuration` (7 Tage), wie weit man mit Time Travel tatsächlich zurückkommt — auch wenn der Log-Eintrag selbst dank `logRetentionDuration` noch 30 Tage sichtbar bliebe.

---

## Schema manuell sichern, mangels eigener Registry

Weil es keine dedizierte Schema Registry gibt, kann man einen Schema-Stand nur **manuell/extern** ablegen, falls man das braucht — zum Beispiel als Datei oder in einer eigenen Tabelle. Zwei Wege dafür:

- In Python: `df.schema.json()` erzeugt das Schema als JSON-Text; mit `StructType.fromJson(...)` lässt es sich später wieder einlesen.
- In SQL: `DESCRIBE EXTENDED table_name AS JSON` (ab Databricks Runtime 16.2) liefert strukturierte Tabellenmetadaten inklusive Schema als JSON.

Details und Code dazu: [Schema Definition.md](Schema%20Definition.md).

---

## Verwandte Themen

- [Schema Definition.md](Schema%20Definition.md) · [Schema Evolution.md](Schema%20Evolution.md) · [Schema Migration.md](Schema%20Migration.md)
- [Schema-on-Read vs. Schema-on-Write.md](Schema-on-Read%20vs.%20Schema-on-Write.md) · [Schema Governance.md](Schema%20Governance.md)
