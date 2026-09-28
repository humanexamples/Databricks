# MERGE INTO in Delta Lake

Der `MERGE INTO`-Befehl führt Upsert-Operationen in Delta-Lake-Tabellen aus: Er fügt Zeilen ein, aktualisiert sie oder löscht sie, indem eine Zielt Tabelle mit Quelldaten verglichen wird.

**Vollständige Referenz** (formale Syntax, Fehlerfall bei Mehrfach-Treffern, Schema Evolution bei `MERGE`, Praxis-Patterns für Deduplizierung und inkrementelle Synchronisation, SCD/CDC-Einordnung, `DESCRIBE HISTORY`-Metriken) siehe [06 DML Statements/_merge_into.md](../../../06%20DML%20Statements/_merge_into.md) — dieser Artikel bleibt bei der Kurzeinführung.

## Grundstruktur

- **WHEN MATCHED:** Aktualisiert bestehende Zeilen, bei denen Quelle und Ziel übereinstimmen.
- **WHEN NOT MATCHED:** Fügt neue Zeilen aus der Quelle ein.
- **WHEN NOT MATCHED BY SOURCE:** Löscht oder aktualisiert Zielzeilen, für die es keine passende Quellzeile gibt.

Mehrere Bedingungsklauseln können verkettet werden:

- Alle Klauseln außer der letzten benötigen eine Bedingung.
- Matched-Klauseln unterstützen Update- und Delete-Aktionen.
- Unmatched-Klauseln unterstützen nur Insert-Aktionen.
- Not-matched-by-source-Klauseln unterstützen Update- und Delete-Aktionen.

Wichtige Einschränkung: Pro Zielzeile darf nur eine einzige Quellzeile matchen. Das genaue Verhalten bei der Auswertung der Bedingungen kann sich zwischen Databricks-Runtime-Versionen unterscheiden.

## Einfaches Upsert-Beispiel

```sql
%sql
MERGE INTO people10m
USING people10mupdates
ON people10m.id = people10mupdates.id
WHEN MATCHED THEN
  UPDATE SET
    id = people10mupdates.id,
    firstName = people10mupdates.firstName,
    middleName = people10mupdates.middleName,
    lastName = people10mupdates.lastName,
    gender = people10mupdates.gender,
    birthDate = people10mupdates.birthDate,
    ssn = people10mupdates.ssn,
    salary = people10mupdates.salary
WHEN NOT MATCHED
  THEN INSERT (
    id,
    firstName,
    middleName,
    lastName,
    gender,
    birthDate,
    ssn,
    salary
  )
  VALUES (
    people10mupdates.id,
    people10mupdates.firstName,
    people10mupdates.middleName,
    people10mupdates.lastName,
    people10mupdates.gender,
    people10mupdates.birthDate,
    people10mupdates.ssn,
    people10mupdates.salary
  )
```

```python
from delta.tables import *
deltaTablePeople = DeltaTable.forName(spark, "people10m")
deltaTablePeopleUpdates = DeltaTable.forName(spark, "people10mupdates")
dfUpdates = deltaTablePeopleUpdates.toDF()
deltaTablePeople.alias('people') \
  .merge(
    dfUpdates.alias('updates'),
    'people.id = updates.id'
  ) \
  .whenMatchedUpdate(set =
    {
      "id": "updates.id",
      "firstName": "updates.firstName",
      "middleName": "updates.middleName",
      "lastName": "updates.lastName",
      "gender": "updates.gender",
      "birthDate": "updates.birthDate",
      "ssn": "updates.ssn",
      "salary": "updates.salary"
    }
  ) \
  .whenNotMatchedInsert(values =
    {
      "id": "updates.id",
      "firstName": "updates.firstName",
      "middleName": "updates.middleName",
      "lastName": "updates.lastName",
      "gender": "updates.gender",
      "birthDate": "updates.birthDate",
      "ssn": "updates.ssn",
      "salary": "updates.salary"
    }
  ) \
  .execute()
```

## Alle nicht übereinstimmenden Zeilen ändern (`whenNotMatchedBySource`)

```python
(targetDF
  .merge(sourceDF, "source.key = target.key")
  .whenMatchedUpdateAll()
  .whenNotMatchedInsertAll()
  .whenNotMatchedBySourceDelete()
  .execute())
```

```sql
%sql
MERGE INTO target
USING source
ON source.key = target.key
WHEN MATCHED THEN
  UPDATE SET *
WHEN NOT MATCHED THEN
  INSERT *
WHEN NOT MATCHED BY SOURCE THEN
  DELETE
```

## Bedingte Updates mit whenNotMatchedBySource

```python
(targetDF
  .merge(sourceDF, "source.key = target.key")
  .whenMatchedUpdate(
    set = {"target.lastSeen": "source.timestamp"}
  )
  .whenNotMatchedInsert(
    values = {
      "target.key": "source.key",
      "target.lastSeen": "source.timestamp",
      "target.status": "'active'"
    }
  )
  .whenNotMatchedBySourceUpdate(
    condition="target.lastSeen >= (current_date() - INTERVAL '5' DAY)",
    set = {"target.status": "'inactive'"}
  )
  .execute())
```

```sql
%sql
MERGE INTO target
USING source
ON source.key = target.key
WHEN MATCHED THEN
  UPDATE SET target.lastSeen = source.timestamp
WHEN NOT MATCHED THEN
  INSERT (key, lastSeen, status) VALUES (source.key, source.timestamp, 'active')
WHEN NOT MATCHED BY SOURCE AND target.lastSeen >= (current_date() - INTERVAL '5' DAY) THEN
  UPDATE SET target.status = 'inactive'
```

## Weiterführende Praxis-Patterns

Die Anwendungsfälle **Datendeduplizierung** (Insert-only-`MERGE` mit eindeutiger ID, optional zeitlich eingegrenzt), **inkrementelle Synchronisierung** (inkl. Löschungen über `WHEN NOT MATCHED BY SOURCE`) sowie die Einordnung von `MERGE` gegenüber **SCD Type 1/2** und `AUTO CDC` sind mit Code-Beispielen in [06 DML Statements/_merge_into.md](../../../06%20DML%20Statements/_merge_into.md) (Abschnitte 5–7) beschrieben.

---
**Quelle:** https://docs.databricks.com/aws/en/delta/merge  
**Stand:** 2026-08-07
