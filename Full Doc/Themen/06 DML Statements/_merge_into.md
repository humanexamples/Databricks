# `MERGE INTO` — Referenz

Kurzeinführung (Grundstruktur, einfaches Upsert-Beispiel) siehe [07 Data Management/01 Data Engineering/01 Concepts/08-merge.md](../07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/08-merge.md).

## Abschnittsübersicht

1. [Grundzweck und Kontext](#grundzweck)
2. [Formale Syntax](#syntax)
3. [Fehlerfall: Mehrfach-Treffer im Source](#mehrfach-treffer)
4. [Schema Evolution bei `MERGE`](#schema-evolution)
5. [Praxis-Pattern: Datendeduplizierung](#deduplizierung)
6. [Praxis-Pattern: Inkrementelle Synchronisation](#inkrementelle-sync)
7. [SCD Type 1/2 und Change Data Capture](#scd-cdc)
8. [Operation-Metriken (`DESCRIBE HISTORY`)](#operation-metriken)
9. [Quellen](#quellen)

---

## <a id="grundzweck">1. Grundzweck und Kontext</a>

`MERGE INTO` erlaubt es, Daten aus 

- einer Quelltabelle, -view oder 
- einem DataFrame 

per Upsert-Operation in eine Ziel-Delta-Lake-Tabelle einzuspielen — in einer einzigen atomaren Anweisung lassen sich abhängig vom Abgleich zwischen Quelle und Ziel Zeilen einfügen (`INSERT`), aktualisieren (`UPDATE`) oder löschen (`DELETE`).

---

## <a id="syntax">2. Formale Syntax</a>

```
[ common_table_expression ]  MERGE [ WITH SCHEMA EVOLUTION ] INTO target_table_name [target_alias]
    USING source_table_reference [source_alias]
    ON merge_condition
    { WHEN MATCHED [ AND matched_condition ] THEN matched_action |
      WHEN NOT MATCHED [BY TARGET] [ AND not_matched_condition ] THEN not_matched_action |
      WHEN NOT MATCHED BY SOURCE [ AND not_matched_by_source_condition ] THEN not_matched_by_source_action } [...]
```

Ein `MERGE`-Statement besteht damit aus drei Bausteinen: der Zieltabelle (`target_table_name`), der Quelle (`source_table_reference` — Tabelle, View oder Unterabfrage) sowie der `ON`-Verknüpfungsbedingung, gefolgt von einer beliebigen Anzahl von `WHEN`-Klauseln. Die drei Klauseltypen — `WHEN MATCHED`, `WHEN NOT MATCHED [BY TARGET]` und `WHEN NOT MATCHED BY SOURCE` — sowie deren jeweilige Bedingungspflicht bei mehreren Klauseln desselben Typs sind direkt im folgenden Beispiel mit `UPDATE`/`DELETE`/`INSERT`-Aktionen illustriert.

**Formale Grammatik der drei Aktionstypen** (aus der Sprachreferenz, ergänzt zur Haupt-Syntax oben):

```
matched_action {
  DELETE |
  UPDATE SET * [ EXCEPT ( column [, ...] ) ] |
  UPDATE SET { column = { expr | DEFAULT } } [, ...]
}

not_matched_action {
  INSERT * [ EXCEPT ( column [, ...] ) ] |
  INSERT (column1 [, ...] ) VALUES ( expr | DEFAULT ] [, ...] )
}

not_matched_by_source_action {
  DELETE |
  UPDATE SET { column = { expr | DEFAULT } } [, ...]
}
```

Bemerkenswert: `not_matched_by_source_action` kennt **kein** `INSERT` (logisch, da hier Zielzeilen ohne Quellentsprechung behandelt werden) und `not_matched_action` kein `DELETE`.

**Einschränkungen zu Ziel/Quelle laut Sprachreferenz:** `target_table_name` darf keine Options-Angaben enthalten und keine Foreign Table sein; weder `target_alias` noch `source_alias` dürfen eine Spaltenliste enthalten.

### Reales Beispiel mit allen Bausteinen der formalen Syntax

Das folgende, aus den einzeln verifizierten Bausteinen dieses Dokuments zusammengesetzte Beispiel (kein wörtliches Einzelzitat einer Doku-Seite, sondern eigene Anwendung der bestätigten Syntax) deckt jeden optionalen Bestandteil der formalen Syntax gleichzeitig ab — common table expression, `WITH SCHEMA EVOLUTION`, Ziel- **und** Quell-Alias, sowie alle drei `WHEN`-Klauseltypen jeweils mit eigener Bedingung:

```sql
WITH update_users_source AS (
  SELECT * FROM staging.users_updates WHERE update_date = current_date()
)
MERGE WITH SCHEMA EVOLUTION 
INTO main.sales.users AS target
USING update_users_source AS source
ON target.id = source.id

WHEN MATCHED AND source.status = 'update' THEN
  UPDATE SET
    target.email = source.email,
    target.status = source.status

WHEN MATCHED AND source.status = 'delete' THEN
  DELETE

WHEN NOT MATCHED BY TARGET AND source.status = 'new' THEN
  INSERT (id, first_name, email, sign_up_date, status)
  VALUES (source.id, source.first_name, source.email, source.sign_up_date, source.status)

WHEN NOT MATCHED BY SOURCE AND target.last_seen < current_date() - INTERVAL '30' DAY THEN
  UPDATE SET target.status = 'inactive';
```

UPDATE und INSERT: Beide lassen sich mit `EXCEPT` gezielt um einzelne Spalten einschränken: `UPDATE SET * EXCEPT (spalte)` bzw. `INSERT * EXCEPT (spalte)`.

### Dasselbe Beispiel über die Python-API

Dieselbe Logik, über die `DeltaMergeBuilder`-API der Python-`DeltaTable`-Klasse — `withSchemaEvolution()` entspricht `WITH SCHEMA EVOLUTION`, die vier `when*`-Methoden entsprechen den vier `WHEN`-Klauseln oben (Reihenfolge und Bedingungen identisch zum SQL-Beispiel):

```python
from delta.tables import DeltaTable

update_users_source = spark.sql("""
  SELECT * FROM staging.users_updates WHERE update_date = current_date()
""")

target_table = DeltaTable.forName(spark, "main.sales.users")

(target_table.alias("target")
  .merge(update_users_source.alias("source"), "target.id = source.id")
  .withSchemaEvolution()
  .whenMatchedUpdate(
    condition = "source.status = 'update'",
    set = {
      "email": "source.email",
      "status": "source.status"
    })
  .whenMatchedDelete(condition = "source.status = 'delete'")
  .whenNotMatchedInsert(
    condition = "source.status = 'new'",
    values = {
      "id": "source.id",
      "first_name": "source.first_name",
      "email": "source.email",
      "sign_up_date": "source.sign_up_date",
      "status": "source.status"
    })
  .whenNotMatchedBySourceUpdate(
    condition = "target.last_seen < current_date() - INTERVAL '30' DAY",
    set = {"status": "'inactive'"})
  .execute())
```

Die vorbereitende CTE aus dem SQL-Beispiel (`WITH update_users_source AS (...)`) entspricht hier einem separat per `spark.sql(...)` erzeugten DataFrame, der anschließend wie jede andere Quelle in `.merge(...)` verwendet wird.

---

## <a id="mehrfach-treffer">3. Fehlerfall: Mehrfach-Treffer im Source</a>

`MERGE`-Operationen sind auf eine **1:n-Beziehung von Ziel zu Quelle** ausgelegt: Nur eine einzelne Quellzeile darf zu einer gegebenen Zielzeile passen. Trifft mehr als eine Quellzeile auf dieselbe Zielzeile gemäß den in `ON` und `WHEN MATCHED` angegebenen Bedingungen zu, schlägt die Operation mit der Fehlerklasse `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE` fehl.

**Praktische Konsequenz:** Enthält die Quelle potenzielle Duplikate bezogen auf den Merge-Schlüssel, muss die Quelle **vor** dem `MERGE` selbst dedupliziert werden (siehe Abschnitt 5) — `MERGE` dedupliziert die Quelle nicht automatisch.

---

## <a id="schema-evolution">4. Schema Evolution bei `MERGE`</a>

Zwei unabhängige Wege, damit ein `MERGE`-Statement neue Spalten aus der Quelle automatisch in die Zieltabelle übernimmt:

**1. `MERGE WITH SCHEMA EVOLUTION INTO`** — laut SQL-Sprachreferenz verfügbar ab **Databricks Runtime 15.2 oder höher**. **Korrektur (nachrecherchiert):** Die separate Schema-Evolution-Referenzseite ("Update Delta Lake table schema") nennt für dieselbe Funktion zusätzlich **Databricks Runtime 15.4 LTS oder höher**. Ein direkter Abgleich mit den offiziellen Databricks-Runtime-15.2-Release-Notes löst diesen scheinbaren Widerspruch auf: Die Release Notes zu Runtime 15.2 bestätigen wörtlich *"You can now add the `WITH SCHEMA EVOLUTION` clause to a SQL merge statement to enable schema evolution for the operation"* — das Feature wurde also tatsächlich in 15.2 eingeführt. Da 15.2 selbst **keine** LTS-Version ist (die nächste LTS-Version danach ist 15.4 LTS), sind beide Angaben gleichzeitig korrekt: 15.2 ist die erste Runtime-Version mit diesem Feature überhaupt, 15.4 LTS die erste **LTS**-Version, die es enthält. Aktualisiert das Zielschema automatisch, damit es zum Quellschema passt:

```sql
MERGE WITH SCHEMA EVOLUTION INTO target
USING source
ON source.key = target.key
WHEN MATCHED THEN
  UPDATE SET *
WHEN NOT MATCHED THEN
  INSERT *
WHEN NOT MATCHED BY SOURCE THEN
  DELETE
```

**2. Spark-Konfiguration `spark.databricks.delta.schema.autoMerge.enabled`** — von Databricks selbst explizit als "**legacy**" gekennzeichnet. Aktiviert Schema-Evolution session-weit für **alle** Schreiboperationen der aktuellen SparkSession (nicht nur `MERGE`, sondern z. B. auch `INSERT` sowie Batch-/Streaming-Schreiboperationen):

```python
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", True)
```

```sql
SET spark.databricks.delta.schema.autoMerge.enabled = true;
```

Databricks empfiehlt ausdrücklich, Schema-Evolution stattdessen **pro einzelner Schreiboperation** zu aktivieren statt session-weit: bei `MERGE` über die `WITH SCHEMA EVOLUTION`-Syntax aus Weg 1 bzw. `.withSchemaEvolution()` in der Python-API, bei `INSERT` über eine analoge `INSERT WITH SCHEMA EVOLUTION`-Syntax, und bei sonstigen Batch-/Streaming-Schreiboperationen über `.option("mergeSchema", "true")`. Wird Schema-Evolution auf diese gezielte Art für eine einzelne Operation aktiviert, hat das laut Doku **Vorrang** vor der session-weiten Spark-Konfiguration.

### Verhalten bei neuen Spalten in der Quelle

Die Doku unterscheidet zwei Fälle für Spalten, die nur auf einer der beiden Seiten vorkommen:

**Fall A — Spalte existiert in der Quelle, aber nicht im Ziel:** Wird sie per Name direkt zugewiesen (`UPDATE SET target.newcol = source.newcol`) oder per Star-Syntax (`UPDATE SET *`/`INSERT *`) übernommen, wird sie bei aktiver Schema Evolution automatisch zum Ziel hinzugefügt und mit den Quellwerten befüllt. **Wichtige Einschränkung, wörtlich bestätigt:** Das gilt nur, *"wenn Spaltenname und Struktur in der Merge-Quelle exakt der Ziel-Zuweisung entsprechen"* — eine berechnete Zuweisung wie `UPDATE SET target.newcol = source.x + source.y` löst laut Doku **keine** Schema Evolution aus, obwohl `newcol` dabei neu im Ziel wäre; ebenso wenig eine Umbenennung wie `UPDATE SET target.newcol = source.someothercol`.

Ohne Schema Evolution bleibt das Zielschema unverändert, und `UPDATE`/`INSERT` schlagen mit einem Fehler fehl, sobald eine im Statement referenzierte Spalte nicht im Ziel existiert.

**Fall B — Spalte existiert im Ziel, aber nicht in der Quelle:** Das Zielschema ändert sich hier **nicht** — unabhängig davon, ob Schema Evolution aktiv ist. Bei `UPDATE SET *` bleibt der bestehende Wert dieser Spalte unverändert; bei `INSERT *` wird sie für neue Zeilen `NULL`. Eine explizite Zuweisung in der Aktionsklausel (z. B. `UPDATE SET target.onlyintarget = 5`) überschreibt dieses Verhalten weiterhin.

**Vollständiges Doku-Beispiel als Vergleichstabelle:**

| Spalten | Statement | Ohne Schema Evolution (Standard) | Mit Schema Evolution |
|---|---|---|---|
| Ziel: `key, value` / Quelle: `key, value, new_value` | `WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *` | Zielschema bleibt unverändert; nur `key`, `value` werden aktualisiert/eingefügt. | Zielschema wird zu `(key, value, new_value)`; Treffer werden inkl. `new_value` aktualisiert, neue Zeilen mit allen drei Spalten eingefügt. |
| Ziel: `key, old_value` / Quelle: `key, new_value` | `WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *` | `UPDATE`/`INSERT` schlagen fehl, da `old_value` nicht in der Quelle vorkommt. | Zielschema wird zu `(key, old_value, new_value)`; Treffer erhalten `new_value`, `old_value` bleibt unverändert; neue Zeilen erhalten `NULL` für `old_value`. |
| Ziel: `key, old_value` / Quelle: `key, new_value` | `WHEN MATCHED THEN UPDATE SET new_value = s.new_value` | `UPDATE` schlägt fehl, da `new_value` nicht im Ziel existiert. | Zielschema wird zu `(key, old_value, new_value)`; Treffer erhalten `new_value`, `old_value` bleibt unverändert; nicht getroffene Zeilen erhalten `NULL` für `new_value` (ab Databricks Runtime 12.2 LTS — darunter Fehler). |
| Ziel: `key, old_value` / Quelle: `key, new_value` | `WHEN NOT MATCHED THEN INSERT (key, new_value) VALUES (s.key, s.new_value)` | `INSERT` schlägt fehl, da `new_value` nicht im Ziel existiert. | Zielschema wird zu `(key, old_value, new_value)`; neue Zeilen erhalten `key`/`new_value` und `NULL` für `old_value`; bestehende Zeilen erhalten `NULL` für `new_value`, `old_value` bleibt unverändert (ab Databricks Runtime 12.2 LTS — darunter Fehler). |

**Versionsgrenzen laut Doku:** Bis einschließlich Databricks Runtime 11.3 LTS sind nur `INSERT *`/`UPDATE SET *` für Schema Evolution mit `MERGE` nutzbar. Ab Databricks Runtime 12.2 LTS lassen sich einzelne Spalten/Struct-Felder der Quelle auch namentlich in `INSERT`-/`UPDATE`-Aktionen angeben. Ab Databricks Runtime 13.3 LTS wird Schema Evolution zusätzlich für Structs innerhalb von Maps unterstützt (z. B. `map<int, struct<a: int, b: int>>`).

### Verhalten bei Typkonflikten zwischen Quelle und Ziel

Für eine Spalte, die in **beiden** Seiten existiert, aber mit unterschiedlichem Datentyp, gilt ein anderer Mechanismus als für neue Spalten: Unabhängig davon, ob `WITH SCHEMA EVOLUTION` verwendet wird, greift laut Schema-Enforcement-Doku zunächst grundsätzlich: *"If the data type in the source statement does not match the target column, MERGE tries to safely cast column data types to match the target table."* Dieser **Safe-Cast-Versuch** ändert **nicht** den deklarierten Zieltyp der Spalte, sondern castet lediglich den eingehenden Wert verlustfrei auf den bestehenden Zieltyp (z. B. `int` nach `bigint`).

**Ungeklärt (erneut geprüft):** Welche Typumwandlungen konkret als "sicher" gelten und was bei einer nicht sicher castbaren Typabweichung (z. B. `string` in eine `int`-Zielspalte) genau passiert — die geprüfte Schema-Enforcement-Seite nennt weder eine vollständige Liste erlaubter/verbotener Casts noch einen konkreten, `MERGE`-spezifischen Fehlertext für den Fehlschlag. Das deckt sich mit den bereits in `_read_files.md` Abschnitt 14.3 und `_spark_read.md` Abschnitt 10.2 dokumentierten Lücken zu Delta-Schema-Enforcement-Fehlertexten. Eine gezielte Suche in der Fehlerklassen-Referenz ergab zwei plausible Kandidaten — `CANNOT_UP_CAST_DATATYPE` (*"Cannot up cast `<expression>` from `<sourceType>` to `<targetType>`."*) und `CANNOT_MERGE_INCOMPATIBLE_DATA_TYPE` (*"Failed to merge incompatible data types `<left>` and `<right>`."*) —, deren Beschreibungen aber laut zweifacher Prüfung **nicht** explizit auf `MERGE INTO` als auslösendes Statement verweisen (`CANNOT_UP_CAST_DATATYPE` ist eine allgemeine Spark-SQL-Cast-Fehlerklasse, `CANNOT_MERGE_INCOMPATIBLE_DATA_TYPE` bezieht sich trotz des Namens erkennbar auf Schema-Merging allgemein, nicht auf das `MERGE`-DML-Statement). Ob eine dieser beiden Klassen tatsächlich bei einem gescheiterten Safe Cast in `MERGE` auftritt, bleibt daher unbestätigt.

**Type Widening — der eigentliche schema-ändernde Mechanismus:** Damit sich der **deklarierte Zieltyp selbst** ändert (echtes Type Widening, z. B. `int`-Spalte wird zu `bigint`), müssen laut Doku **alle vier** folgenden Bedingungen gleichzeitig erfüllt sein:

1. Das Schreibkommando läuft mit aktivierter automatischer Schema Evolution (`WITH SCHEMA EVOLUTION` bzw. `.withSchemaEvolution()`).
2. Type Widening ist auf der Zieltabelle aktiviert (`delta.enableTypeWidening = true`).
3. Der Quelltyp ist breiter als der Zieltyp.
4. Die konkrete Typänderung wird von Type Widening unterstützt (siehe die Typtabelle in `_schema_Aspekte.md` Abschnitt 6).

Fehlt auch nur eine dieser vier Bedingungen, greift stattdessen ausschließlich der oben beschriebene **Safe-Cast**-Mechanismus, **keine** echte Schema-Änderung.

```sql
ALTER TABLE main.sales.users SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');

MERGE WITH SCHEMA EVOLUTION INTO main.sales.users AS target
USING update_users_source AS source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

**Zusammenfassung — vier Kombinationen:**

| Situation | Ohne `WITH SCHEMA EVOLUTION` | Mit `WITH SCHEMA EVOLUTION` |
|---|---|---|
| Neue Spalte in der Quelle, direkt namentlich oder per `*` zugewiesen | Fehlschlag (Spalte existiert nicht im Ziel) | Spalte wird automatisch zum Ziel hinzugefügt, befüllt aus der Quelle |
| Spalte existiert nur im Ziel | Bleibt unverändert (`UPDATE SET *`) bzw. wird `NULL` (`INSERT *`) — unabhängig von Schema Evolution | Identisch — Schema Evolution betrifft nur neue Quellspalten, nicht fehlende |
| Typkonflikt, per Type Widening abgedeckt, Zieltabelle mit `delta.enableTypeWidening` | Nur Safe Cast auf bestehenden Zieltyp (kein Schema-Wechsel) | Zieltyp wird selbst erweitert (z. B. `int` → `bigint`) |
| Typkonflikt, nicht sicher castbar/nicht widenbar | Ungeklärter Fehlerfall (kein bestätigter Fehlertext) | Ungeklärter Fehlerfall (kein bestätigter Fehlertext) — die Type-Widening-Bedingungen greifen hier nicht |

---

## <a id="deduplizierung">5. Praxis-Pattern: Datendeduplizierung</a>

Ein häufiger ETL-Anwendungsfall: Logs werden per Append in eine Delta-Tabelle geschrieben, wobei die Quelle mitunter doppelte Log-Datensätze erzeugt. Über eine Insert-only-`MERGE`-Operation mit einer eindeutigen ID lassen sich echte Duplikate herausfiltern:

```sql
MERGE INTO logs
USING newDedupedLogs
ON logs.uniqueId = newDedupedLogs.uniqueId
WHEN NOT MATCHED THEN
  INSERT *
```

```python
(deltaTable.alias("logs")
  .merge(newDedupedLogs.alias("newDedupedLogs"), "logs.uniqueId = newDedupedLogs.uniqueId")
  .whenNotMatchedInsertAll()
  .execute())
```

**Wichtige Voraussetzung laut Doku:** Der Datensatz mit den neuen Logs muss bereits **innerhalb sich selbst** dedupliziert sein — `MERGE` löst nur Duplikate zwischen Quelle und bereits vorhandener Zieltabelle auf (siehe Abschnitt 3 zum Mehrfach-Treffer-Fehler bei nicht selbst-deduplizierter Quelle), nicht Duplikate innerhalb der Quelle selbst.

**Performance-Optimierung:** Wenn Duplikate nur innerhalb eines bekannten Zeitfensters zu erwarten sind, lässt sich die Suche gezielt eingrenzen, z. B. durch Partitionierung nach Datum und eine zeitlich begrenzte `ON`-Bedingung — die Doku nennt als Beispiel die Suche nach Duplikaten nur innerhalb der letzten 7 Tage an Logs statt in der gesamten Tabelle.

**Streaming-Kontext:** `MERGE` lässt sich auch innerhalb von `foreachBatch` einsetzen, um eine fortlaufende Deduplizierung von Logs in einer Structured-Streaming-Pipeline umzusetzen.

---

## <a id="inkrementelle-sync">6. Praxis-Pattern: Inkrementelle Synchronisation</a>

Um eine Zieltabelle inkrementell mit einer sich ändernden Quelle synchron zu halten — inklusive Löschungen —, lässt sich `WHEN NOT MATCHED BY SOURCE` mit einer zeitlich begrenzten Quellabfrage kombinieren:

```sql
MERGE INTO target AS t
USING (SELECT * FROM source WHERE created_at >= (current_date() - INTERVAL '5' DAY)) AS s
ON t.key = s.key
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE AND created_at >= (current_date() - INTERVAL '5' DAY) THEN DELETE
```

Dieses Muster dient laut Doku dazu, Änderungen aus der Quelle dynamisch zur Zieltabelle zu propagieren, **einschließlich** Löschungen — begrenzt auf ein Zeitfenster, um den Suchraum wie in Abschnitt 5 beschrieben einzugrenzen.

**Performance-Warnung laut Sprachreferenz, wörtlich:** *"Adding a `WHEN NOT MATCHED BY SOURCE` clause to update or delete target rows when the `merge_condition` evaluates to false can lead to a large number of target rows being modified. For best performance, apply `not_matched_by_source_condition`s to limit the number of target rows updated or deleted."* Eine `WHEN NOT MATCHED BY SOURCE`-Klausel ohne einschränkende Zusatzbedingung wirkt potenziell auf **alle** nicht getroffenen Zielzeilen — genau der Grund, warum das Muster oben die Klausel zusätzlich mit `created_at >= (current_date() - INTERVAL '5' DAY)` eingrenzt, statt sie unbedingt zu verwenden.

---

## <a id="scd-cdc">7. SCD Type 1/2 und Change Data Capture</a>

Lakeflow-Pipelines bieten native Unterstützung, um SCD Type 1 und Type 2 nachzuverfolgen und anzuwenden. Für die korrekte Behandlung nicht-chronologisch eintreffender Datensätze beim Verarbeiten von CDC-Feeds empfiehlt die Doku, `AUTO CDC ... INTO` innerhalb von Lakeflow-Pipelines zu verwenden, statt SCD/CDC-Logik manuell über `MERGE INTO` nachzubilden.

**Einordnung:** `MERGE INTO` ist damit zwar technisch in der Lage, SCD-/CDC-ähnliche Upsert-Logik selbst nachzubilden, aber für den expliziten SCD-Type-2-Anwendungsfall (Historisierung mit `__START_AT`/`__END_AT`) verweist Databricks selbst auf `AUTO CDC` statt auf handgeschriebene `MERGE`-Statements. Details zu `AUTO CDC`/`AUTO CDC FROM SNAPSHOT` siehe `_fileIngestionScenarios.md` (Ordner "Working with Files") Abschnitt 5c bzw. 1c.

---

## <a id="operation-metriken">8. Operation-Metriken (`DESCRIBE HISTORY`)</a>

Nach einem `MERGE` lässt sich per `DESCRIBE HISTORY <tabelle>` u. a. folgende, für `MERGE` spezifische Operation-Metriken einsehen:

| Metrik | Bedeutung |
|---|---|
| `numSourceRows` | Anzahl der Zeilen im Quell-DataFrame |
| `numTargetRowsInserted` | Anzahl der in die Zieltabelle eingefügten Zeilen |
| `numTargetRowsUpdated` | Anzahl der in der Zieltabelle aktualisierten Zeilen |
| `numTargetRowsDeleted` | Anzahl der in der Zieltabelle gelöschten Zeilen |
| `numTargetRowsCopied` | Anzahl der kopierten Zielzeilen |
| `numOutputRows` | Gesamtzahl der geschriebenen Zeilen |
| `numTargetFilesAdded` | Anzahl der zum Ziel hinzugefügten Dateien |
| `numTargetFilesRemoved` | Anzahl der aus dem Ziel entfernten Dateien |
| `executionTimeMs` | Gesamtausführungszeit der Operation |
| `scanTimeMs` | Zeit zum Scannen der Dateien nach Treffern |
| `rewriteTimeMs` | Zeit zum Neuschreiben der getroffenen Dateien |

```sql
MERGE INTO main_users_target target
USING update_users_source source
ON target.id = source.id
WHEN MATCHED AND source.status = 'update' THEN
  UPDATE SET target.email = source.email, target.status = source.status
WHEN MATCHED AND source.status = 'delete' THEN
  DELETE
WHEN NOT MATCHED THEN
  INSERT (id, first_name, email, sign_up_date, status)
  VALUES (source.id, source.first_name, source.email, source.sign_up_date, source.status);

DESCRIBE HISTORY main_users_target;
```

---

## <a id="quellen">9. Quellen</a>

- MERGE INTO (SQL-Sprachreferenz — formale Syntax, Star-Syntax-Definition, Mehrfach-Treffer-Fehlerklasse, Verfügbarkeit ab Runtime-Version): https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into
- Upsert into a Delta Lake table using merge (Praxis-Patterns: Deduplizierung, inkrementelle Synchronisation, SCD/CDC-Verweis, Operation-Metrik-Grundlagen): https://docs.databricks.com/aws/en/delta/merge
- Update Delta Lake table schema (Schema-Evolution-Syntax für `MERGE`, `spark.databricks.delta.schema.autoMerge.enabled`): https://docs.databricks.com/aws/en/tables/update-schema
- History and audit logging for Delta Lake (`DESCRIBE HISTORY`-Operation-Metriken für `MERGE`): https://docs.databricks.com/aws/en/delta/history
- Change data capture with Lakeflow Declarative Pipelines (`AUTO CDC`, Verweisziel aus Abschnitt 7): https://docs.databricks.com/aws/en/ldp/cdc
- DeltaMergeBuilder (Python-API-Referenz für `DeltaTable.merge()`, u. a. `whenMatchedUpdate`/`whenMatchedDelete`/`whenNotMatchedInsert`/`whenNotMatchedBySourceUpdate`/`withSchemaEvolution`): https://docs.delta.io/latest/api/python/spark/index.html
- Schema enforcement (Safe-Cast-Verhalten bei Typkonflikten für `INSERT`/`MERGE`, Spalten-Existenz-Prüfung): https://docs.databricks.com/aws/en/tables/schema-enforcement
- Type widening (Bedingungen für automatisches Type Widening bei `MERGE WITH SCHEMA EVOLUTION`, `delta.enableTypeWidening`): https://docs.databricks.com/aws/en/delta/type-widening
- Update table schemas with schema evolution (Azure-Spiegelseite, für Gegenprüfung der Vergleichstabelle "neue Spalten" sowie der Runtime-Versionsangabe 15.4 LTS): https://learn.microsoft.com/en-us/azure/databricks/tables/update-schema
- Databricks Runtime 15.2 release notes (löst den scheinbaren 15.2-vs.-15.4-LTS-Widerspruch auf, bestätigt Einführung von `WITH SCHEMA EVOLUTION` in `MERGE`): https://docs.databricks.com/aws/en/release-notes/runtime/15.2.html
- Error conditions in Databricks (Fehlerklassen-Referenz, geprüft auf `CANNOT_UP_CAST_DATATYPE`/`CANNOT_MERGE_INCOMPATIBLE_DATA_TYPE` als mögliche, aber nicht `MERGE`-spezifisch bestätigte Kandidaten für Typkonflikt-Fehler): https://docs.databricks.com/aws/en/error-messages/error-classes
- Nicht-Databricks-Quelle (privates Kursmaterial, Anstoß für das Codebeispiel in Abschnitt 8): `_Zusammenfassung/_Code Beispiele/Data Ingestion/MERGE INTO.md`

**Stand:** 2026-08-18.

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

Die formale `MERGE INTO`-Referenzseite selbst zeigt neben dem in Abschnitt 2 bereits übernommenen Vollbeispiel eine Reihe kompakter Einzelklausel-Beispiele, die zwei in diesem Dokument bislang nicht demonstrierte Sprachmittel illustrieren:

### `DEFAULT`-Werte in `WHEN MATCHED`/`WHEN NOT MATCHED BY SOURCE`

Statt eines konkreten Werts oder einer Quellspalte lässt sich in `UPDATE SET` auch das Schlüsselwort `DEFAULT` verwenden, um eine Spalte auf ihren in der Tabellendefinition hinterlegten Default-Wert zurückzusetzen — hier kombiniert mit einer bedingten Löschung markierter Zeilen:

```sql
MERGE INTO target USING source
ON target.key = source.key
WHEN MATCHED AND target.marked_for_deletion THEN DELETE
WHEN MATCHED THEN UPDATE SET target.updated_at = source.updated_at,
  target.value = DEFAULT
```

Dasselbe Muster funktioniert spiegelbildlich auch in `WHEN NOT MATCHED BY SOURCE`, um Zielzeilen ohne Quellentsprechung statt zu löschen auf ihren Default-Wert zurückzusetzen:

```sql
MERGE INTO target USING source
ON target.key = source.key
WHEN NOT MATCHED BY SOURCE AND target.marked_for_deletion THEN DELETE
WHEN NOT MATCHED BY SOURCE THEN UPDATE SET target.value = DEFAULT
```

### Bedingter Insert mit Zeitfilter und `EXCEPT`

Die `WHEN NOT MATCHED BY TARGET`-Klausel lässt sich mit einer eigenen Zusatzbedingung sowie einer expliziten Spaltenliste kombinieren, um nur kürzlich entstandene Quellzeilen mit vordefinierten Werten für die übrigen Spalten einzufügen:

```sql
MERGE INTO target USING source
ON target.key = source.key
WHEN NOT MATCHED BY TARGET AND source.created_at > now() - INTERVAL "1" DAY
THEN INSERT (created_at, value) VALUES (source.created_at, DEFAULT)
```

**Quelle:** https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into
