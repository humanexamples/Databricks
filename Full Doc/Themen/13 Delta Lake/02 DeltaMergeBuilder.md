# `DeltaMergeBuilder` — Python-Referenz (Delta Lake)

## Abschnittsübersicht
1. [Zweck](#zweck)
2. [Vollständiges Beispiel](#beispiel)
3. [`whenMatchedUpdate()`](#whenmatchedupdate)
4. [`whenMatchedUpdateAll()`](#whenmatchedupdateall)
5. [`whenMatchedDelete()`](#whenmatcheddelete)
6. [`whenNotMatchedInsert()`](#whennotmatchedinsert)
7. [`whenNotMatchedInsertAll()`](#whennotmatchedinsertall)
8. [`whenNotMatchedBySourceUpdate()`](#whennotmatchedbysourceupdate)
9. [`whenNotMatchedBySourceDelete()`](#whennotmatchedbysourcedelete)
10. [`withSchemaEvolution()`](#withschemaevolution)
11. [`execute()`](#execute)
12. [Quellen](#quellen)

## <a id="zweck">1. Zweck</a>

`DeltaMergeBuilder` ist das Builder-Objekt für einen MERGE-Befehl (Upsert). Man erhält eine Instanz über `DeltaTable.merge(source, condition)` und hängt daran beliebig viele `whenMatched...`-, `whenNotMatched...`- und `whenNotMatchedBySource...`-Klauseln, bevor `execute()` den Befehl tatsächlich ausführt. `source` ist ein DataFrame, `condition` die Bedingung (str oder Column), auf der Ziel- und Quelltabelle gematcht werden — z. B. `"target.id = source.id"`.

## <a id="beispiel">2. Vollständiges Beispiel</a>

Realistisches Beispiel mit Update- und Insert-Klausel in einem Merge-Aufruf (Events-Tabelle, die per `eventId` upgedatet oder neu eingefügt wird):

```python
from pyspark.sql.functions import col, expr, lit

deltaTable.alias("events").merge(
    source=updatesDF.alias("updates"),
    condition=expr("events.eventId = updates.eventId")
).whenMatchedUpdate(
    set={
        "data": col("updates.data"),
        "count": col("events.count") + 1
    }
).whenNotMatchedInsert(
    values={
        "date": col("updates.date"),
        "eventId": col("updates.eventId"),
        "data": col("updates.data"),
        "count": lit("1")
    }
).execute()
```

Alle `whenMatched*`- und `whenNotMatched*`-Aufrufe lassen sich mehrfach hintereinanderhängen (z. B. mehrere `whenMatchedUpdate`-Klauseln mit unterschiedlichen Bedingungen). Delta Lake prüft die Klauseln der Reihe nach — daher muss innerhalb jeder Klausel-Gruppe (`whenMatched*`, `whenNotMatched*`, `whenNotMatchedBySource*`) nur die letzte Klausel ohne `condition` bleiben dürfen, alle davor benötigen eine unterscheidende Bedingung.

## <a id="whenmatchedupdate">3. `whenMatchedUpdate()`</a>

- Aktualisiert Spalten gematchter Zeilen gemäß den Regeln in `set`, wenn die optionale `condition` erfüllt ist (oder immer, wenn keine `condition` angegeben wird).
- Parameter:
  - `condition` (str, Column oder None, optional) — Zusatzbedingung für diese Klausel; referenziert typischerweise Quelle und Ziel.
  - `set` (Dict[str, str | Column]) — Mapping Zielspalte → Ausdruck/Wert (str-SQL-Ausdruck oder Column).
- Rückgabe: `DeltaMergeBuilder` (Chaining).

```python
deltaTable.alias("t").merge(
    source=sourceDF.alias("s"),
    condition="t.id = s.id"
).whenMatchedUpdate(
    condition="s.status = 'active'",
    set={"value": "s.value", "updatedAt": "s.ts"}
).execute()
```

## <a id="whenmatchedupdateall">4. `whenMatchedUpdateAll()`</a>

- Aktualisiert bei gematchten Zeilen alle Zielspalten mit den entsprechenden Werten aus der Quelle (entspricht `whenMatchedUpdate` mit `set`, das jede Spalte 1:1 abbildet).
- Parameter:
  - `condition` (str, Column oder None, optional, Default `None`) — Zusatzbedingung; ohne Angabe gilt die Klausel für alle gematchten Zeilen.
- Rückgabe: `DeltaMergeBuilder`.

```python
deltaTable.alias("t").merge(
    source=sourceDF.alias("s"),
    condition="t.id = s.id"
).whenMatchedUpdateAll().execute()
```

## <a id="whenmatcheddelete">5. `whenMatchedDelete()`</a>

- Löscht gematchte Zeilen, wenn die optionale `condition` erfüllt ist (oder immer, wenn keine `condition` angegeben wird).
- Parameter:
  - `condition` (str, Column oder None, optional, Default `None`).
- Rückgabe: `DeltaMergeBuilder`.

```python
deltaTable.alias("t").merge(
    source=sourceDF.alias("s"),
    condition="t.id = s.id"
).whenMatchedDelete(condition="s.deleted = true").execute()
```

## <a id="whennotmatchedinsert">6. `whenNotMatchedInsert()`</a>

- Fügt für Quellzeilen ohne Match in der Zieltabelle eine neue Zeile gemäß `values` ein, wenn die optionale `condition` erfüllt ist.
- Parameter:
  - `condition` (str, Column oder None, optional) — Zusatzbedingung auf der Quellzeile.
  - `values` (Dict[str, str | Column]) — Mapping Zielspalte → Ausdruck/Wert für die neue Zeile.
- Rückgabe: `DeltaMergeBuilder`.

```python
deltaTable.alias("t").merge(
    source=sourceDF.alias("s"),
    condition="t.id = s.id"
).whenNotMatchedInsert(
    values={"id": "s.id", "value": "s.value"}
).execute()
```

## <a id="whennotmatchedinsertall">7. `whenNotMatchedInsertAll()`</a>

- Fügt für nicht gematchte Quellzeilen alle Zielspalten mit den entsprechenden Quellwerten ein (entspricht `whenNotMatchedInsert` mit 1:1-Spaltenmapping).
- Parameter:
  - `condition` (str, Column oder None, optional, Default `None`).
- Rückgabe: `DeltaMergeBuilder`.

```python
deltaTable.alias("t").merge(
    source=sourceDF.alias("s"),
    condition="t.id = s.id"
).whenNotMatchedInsertAll().execute()
```

## <a id="whennotmatchedbysourceupdate">8. `whenNotMatchedBySourceUpdate()`</a>

- Aktualisiert Zielzeilen, für die es **keine** passende Quellzeile gibt, gemäß `set`, wenn die optionale `condition` erfüllt ist. Die Bedingung darf sich nur auf die Zieltabelle beziehen, da für diese Zeilen keine Quellzeile existiert.
- Parameter:
  - `condition` (str, Column oder None, optional) — Bedingung, die nur Zielspalten referenzieren darf.
  - `set` (Dict[str, str | Column]) — Mapping Zielspalte → Ausdruck/Wert.
- Rückgabe: `DeltaMergeBuilder`.

```python
deltaTable.alias("t").merge(
    source=sourceDF.alias("s"),
    condition="t.id = s.id"
).whenNotMatchedBySourceUpdate(
    condition="t.status = 'active'",
    set={"status": "'inactive'"}
).execute()
```

## <a id="whennotmatchedbysourcedelete">9. `whenNotMatchedBySourceDelete()`</a>

- Löscht Zielzeilen, für die es keine passende Quellzeile gibt, wenn die optionale `condition` erfüllt ist (oder immer, ohne `condition`).
- Parameter:
  - `condition` (str, Column oder None, optional, Default `None`) — darf nur Zielspalten referenzieren.
- Rückgabe: `DeltaMergeBuilder`.

```python
deltaTable.alias("t").merge(
    source=sourceDF.alias("s"),
    condition="t.id = s.id"
).whenNotMatchedBySourceDelete().execute()
```

## <a id="withschemaevolution">10. `withSchemaEvolution()`</a>

- Aktiviert automatische Schema-Evolution der Zieltabelle: Spalten, die im Quell-DataFrame vorhanden, aber im Ziel-Schema noch nicht bekannt sind, werden beim `execute()` automatisch zum Zielschema hinzugefügt.
- Parameter: keine.
- Rückgabe: `DeltaMergeBuilder`.

```python
deltaTable.alias("t").merge(
    source=sourceDF.alias("s"),
    condition="t.id = s.id"
).withSchemaEvolution().whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

## <a id="execute">11. `execute()`</a>

- Führt den zusammengebauten MERGE-Befehl mit allen konfigurierten Klauseln aus.
- Parameter: keine.
- Rückgabe: `DataFrame` mit den Ausführungs-Metriken des MERGE-Vorgangs.

```python
deltaTable.alias("t").merge(
    source=sourceDF.alias("s"),
    condition="t.id = s.id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

## <a id="quellen">12. Quellen</a>
- `DeltaMergeBuilder` — vollständige Klassenreferenz (Signaturen, Parameter, Beispiele): https://docs.delta.io/api/latest/python/spark/

**Stand:** 2026-09-21.
