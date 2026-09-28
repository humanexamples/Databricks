# MERGE INTO

Upsert in einer atomaren Anweisung: `INSERT`/`UPDATE`/`DELETE` je nach Abgleich zwischen Quelle (Tabelle/View/DataFrame) und Zieltabelle.

### Vollständiges Beispiel (SQL)

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

### Dieselbe Logik über die Python-API (`DeltaMergeBuilder`)

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
    set = {"email": "source.email", "status": "source.status"})
  .whenMatchedDelete(condition = "source.status = 'delete'")
  .whenNotMatchedInsert(
    condition = "source.status = 'new'",
    values = {
      "id": "source.id", "first_name": "source.first_name",
      "email": "source.email", "sign_up_date": "source.sign_up_date",
      "status": "source.status"})
  .whenNotMatchedBySourceUpdate(
    condition = "target.last_seen < current_date() - INTERVAL '30' DAY",
    set = {"status": "'inactive'"})
  .execute())
```

Grundmuster (`whenMatchedUpdateAll`, `whenNotMatchedInsertAll`, `whenNotMatchedBySourceDelete`):

```python
(targetDF
  .merge(sourceDF, "source.key = target.key")
  .whenMatchedUpdateAll()
  .whenNotMatchedInsertAll()
  .whenNotMatchedBySourceDelete()
  .execute())
```

```sql
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

### `DEFAULT`-Werte in Aktionen

`DEFAULT` in `UPDATE SET` setzt eine Spalte auf ihren in der Tabellendefinition hinterlegten Default-Wert zurück; funktioniert spiegelbildlich auch in `WHEN NOT MATCHED BY SOURCE`.

```sql
MERGE INTO target USING source
ON target.key = source.key
WHEN MATCHED AND target.marked_for_deletion THEN DELETE
WHEN MATCHED THEN UPDATE 
		SET target.updated_at = source.updated_at, target.value = DEFAULT
```

## Fehlerfall: Mehrfach-Treffer im Source

- `MERGE` ist auf **1:n von Ziel zu Quelle** ausgelegt: nur eine Quellzeile darf zu einer Zielzeile passen.
- Mehrere Treffer gemäß `ON`/`WHEN MATCHED` → `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE`.
- `MERGE` dedupliziert die Quelle **nicht** automatisch — bei Duplikaten bzgl. Merge-Key vorher separat deduplizieren.

## Schema Evolution bei `MERGE`

1. **`MERGE WITH SCHEMA EVOLUTION INTO`** — Aktualisiert das Zielschema automatisch passend zur Quelle.
2. **`spark.databricks.delta.schema.autoMerge.enabled`** — "legacy", aktiviert Schema-Evolution session-weit für **alle** Schreiboperationen. Databricks empfiehlt gezielte Aktivierung pro Operation (`WITH SCHEMA EVOLUTION`/`.withSchemaEvolution()` bei `MERGE`, `.option("mergeSchema", "true")` sonst) — hat Vorrang vor der session-weiten Config.

```python
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", True)
```

**Neue Spalten in der Quelle:**

- **Fall A — Spalte in Quelle, nicht im Ziel:** wird per Name oder Star-Syntax (`UPDATE SET *`/`INSERT *`) übernommen und bei aktiver Schema Evolution automatisch zum Ziel hinzugefügt — **nur** wenn Name/Struktur exakt der Ziel-Zuweisung entsprechen. Berechnete Zuweisung (`target.newcol = source.x + source.y`) oder Umbenennung lösen **keine** Schema Evolution aus. Ohne Schema Evolution: `UPDATE`/`INSERT` schlägt fehl, sobald eine referenzierte Spalte im Ziel fehlt.
- **Fall B — Spalte im Ziel, nicht in Quelle:** Zielschema ändert sich **nie**. Bei `UPDATE SET *` bleibt der Wert unverändert, bei `INSERT *` wird er `NULL` für neue Zeilen.
- Versionsgrenzen: bis DBR 11.3 LTS nur `INSERT *`/`UPDATE SET *`; ab 12.2 LTS auch einzelne benannte Spalten/Struct-Felder; ab 13.3 LTS zusätzlich Structs innerhalb von Maps.

**Typkonflikte:** `MERGE` versucht zunächst unabhängig von `WITH SCHEMA EVOLUTION` einen **Safe Cast** (z. B. `int` → `bigint`) — der deklarierte Zieltyp ändert sich dabei nicht.

**Echtes Type Widening** (Änderung des deklarierten Zieltyps) erfordert alle vier Bedingungen:
1. Schreibkommando mit `WITH SCHEMA EVOLUTION`.
2. Type Widening auf der Zieltabelle aktiviert (`delta.enableTypeWidening = true`).
3. Quelltyp breiter als Zieltyp.
4. Die konkrete Typänderung wird von Type Widening unterstützt.

```sql
ALTER TABLE main.sales.users SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');

MERGE WITH SCHEMA EVOLUTION INTO main.sales.users AS target
USING update_users_source AS source
ON target.id = source.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

## Praxis-Pattern: Datendeduplizierung

Insert-only-`MERGE` mit eindeutiger ID filtert Duplikate beim Append in eine Log-Tabelle heraus. Die neue Log-Menge muss bereits **innerhalb sich selbst** dedupliziert sein — `MERGE` löst nur Duplikate zwischen Quelle und Ziel, nicht innerhalb der Quelle. Bei bekanntem Zeitfenster (z. B. nur letzte 7 Tage) lässt sich die Suche per Partitionierung + zeitlich begrenzter `ON`-Bedingung eingrenzen. Auch innerhalb von `foreachBatch` für kontinuierliche Deduplizierung in Structured-Streaming-Pipelines einsetzbar.

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

## Praxis-Pattern: Inkrementelle Synchronisation

`WHEN NOT MATCHED BY SOURCE` + zeitlich begrenzte Quellabfrage hält eine Zieltabelle inkrementell synchron — inklusive Löschungen.

```sql
MERGE INTO target AS t
USING (SELECT * FROM source WHERE created_at >= (current_date() - INTERVAL '5' DAY)) AS s
ON t.key = s.key
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE AND created_at >= (current_date() - INTERVAL '5' DAY) THEN DELETE
```

> **Performance:** `WHEN NOT MATCHED BY SOURCE` ohne einschränkende Zusatzbedingung kann sehr viele Zielzeilen betreffen — `not_matched_by_source_condition` sollte die Anzahl begrenzen.

## Bedingter Insert mit Zeitfilter

```sql
MERGE INTO target USING source
ON target.key = source.key
WHEN NOT MATCHED BY TARGET AND source.created_at > now() - INTERVAL "1" DAY
THEN INSERT (created_at, value) VALUES (source.created_at, DEFAULT)
```

## Einordnung gegenüber SCD/CDC

`MERGE INTO` kann SCD-/CDC-ähnliche Upsert-Logik technisch nachbilden. Für SCD Type 2 (Historisierung mit `__START_AT`/`__END_AT`) empfiehlt Databricks stattdessen `AUTO CDC ... INTO` in Lakeflow-Pipelines — insbesondere für nicht-chronologisch eintreffende Datensätze.

## Operation-Metriken (`DESCRIBE HISTORY`)

| Metrik | Bedeutung |
|---|---|
| `numSourceRows` | Anzahl Zeilen im Quell-DataFrame |
| `numTargetRowsInserted` | Anzahl eingefügter Zeilen |
| `numTargetRowsUpdated` | Anzahl aktualisierter Zeilen |
| `numTargetRowsDeleted` | Anzahl gelöschter Zeilen |
| `numTargetRowsCopied` | Anzahl kopierter Zielzeilen |
| `numOutputRows` | Gesamtzahl geschriebener Zeilen |
| `numTargetFilesAdded` | Anzahl hinzugefügter Dateien |
| `numTargetFilesRemoved` | Anzahl entfernter Dateien |
| `executionTimeMs` | Gesamtausführungszeit |
| `scanTimeMs` | Zeit zum Scannen der Dateien nach Treffern |
| `rewriteTimeMs` | Zeit zum Neuschreiben der getroffenen Dateien |

```sql
DROP TEMPORARY VARIABLE IF EXISTS latest_version;

DECLARE VARIABLE latest_version INT;

SET VARIABLE latest_version = (
  SELECT max(version) AS latest_version
  FROM (DESCRIBE HISTORY target_table)
);

SELECT 
  operationMetrics['numTargetRowsInserted'],
  operationMetrics['numTargetRowsUpdated'],
  operationMetrics['numTargetRowsDeleted']
FROM (DESCRIBE HISTORY target_table)
WHERE version = latest_version
```

```sql
SELECT * FROM table_changes('main.sales.orders',latest_version)
WHERE _change_type = "update_preimage"
ORDER BY _commit_version
```

Ergebnis:

```
order_id|customer|amount|_change_type    |_commit_version| _commit_timestamp
--------|--------|------|----------------|---------------|--------------------

       1|   Alice|   100|update_preimage |             5 | 2026-09-18T10:15:00
       1|   Alice|   150|update_postimage|             5 | 2026-09-18T10:15:00
       2|     Bob|   200|delete          |             5 | 2026-09-18T10:15:00
       4|    Dana|   400|insert          |             5 | 2026-09-18T10:15:00
```

**Was die vier `_change_type`-Werte bedeuten**:

- **`insert`** — eine **neue** Zeile wurde hinzugefügt. Es gibt keinen "Vorher"-Zustand.
- **`delete`** — eine Zeile wurde **entfernt**. Die CDF-Zeile zeigt die Werte, die die Zeile unmittelbar **vor** dem Löschen hatte — es gibt keinen "Nachher"-Zustand.
- **`update_preimage`** — der Zustand einer Zeile **unmittelbar vor** einer Aktualisierung ("pre" = vorher; "image" = Momentaufnahme der Werte).
- **`update_postimage`** — der Zustand **derselben** Zeile **unmittelbar nach** derselben Aktualisierung ("post" = nachher).

## Zeilen-Ebene: `MERGE` und Change Data Feed (`_change_type`)

```sql
DESCRIBE HISTORY target_table;
```

Mit `DESCRIBE HISTORY tbl` bekommt man unter anderem die folgenden Spalten, die 



oben zeigen nur **aggregierte Zahlen** ("wie viele Zeilen wurden eingefügt/aktualisiert/gelöscht"). Für die **zeilengenaue** Sicht — *welche konkrete Zeile* sich *wie* verändert hat, inklusive Vorher-/Nachher-Wert bei Updates — ist stattdessen der **Change Data Feed (CDF)** zuständig. Laut Doku enthält jeder CDF-Änderungseintrag *"the row data along with metadata that indicates whether the row was inserted, updated, or deleted"* — `MERGE` ist als DML-Befehl, der intern `INSERT`/`UPDATE`/`DELETE` ausführt, also genauso ein Auslöser für CDF-Einträge wie eigenständige `UPDATE`/`DELETE`/`INSERT`-Anweisungen.

Jede Aktualisierung erzeugt also **immer ein Paar** — eine `update_preimage`- und eine `update_postimage`-Zeile für dieselbe logische Änderung, nie nur eine von beiden. Das gilt unabhängig davon, ob die Änderung über ein eigenständiges `UPDATE` oder über den `WHEN MATCHED ... THEN UPDATE`-Zweig eines `MERGE` ausgelöst wurde.

**Voraussetzung — CDF muss auf der Zieltabelle aktiviert sein.** Es gibt zwei Varianten: das hier gezeigte **Legacy CDF** (manuelle Aktivierung per Tabellen-Property, materialisiert Änderungen beim Schreiben) sowie neueres **Automatic CDF** (ab DBR 19, Unity-Catalog-Managed-Tabellen mit Row Tracking, berechnet Änderungen erst beim Lesen — spart dafür laut Doku Schreib-Performance genau bei `MERGE INTO`/`UPDATE`). Beide liefern **dasselbe** Ausgabeschema (`_change_type`/`_commit_version`/`_commit_timestamp`) über dieselben Lese-APIs (`table_changes()`/`readChangeFeed`). Legacy-Aktivierung:

```sql
ALTER TABLE main.sales.orders SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

**Beispiel-`MERGE`, das alle vier `_change_type`-Fälle gleichzeitig auslöst:**

```sql
-- Ausgangsstand orders: (1, Alice, 100), (2, Bob, 200), (3, Carol, 300)
MERGE INTO main.sales.orders AS t
USING order_updates AS s
ON t.order_id = s.order_id
WHEN MATCHED AND s.action = 'update' THEN UPDATE SET amount = s.amount
WHEN MATCHED AND s.action = 'delete' THEN DELETE
WHEN NOT MATCHED THEN INSERT (order_id, customer, amount) VALUES (s.order_id, s.customer, s.amount);
-- order_updates: (1, action='update', amount=150) · (2, action='delete') · (4, customer='Dana', amount=400)
```

**Ergebnis beim anschließenden Auslesen des CDF** (`SELECT * FROM table_changes('main.sales.orders', <version_vor_dem_merge>)`):

```
order_id|customer|amount|_change_type    |_commit_version| _commit_timestamp
--------|--------|------|----------------|---------------|--------------------

       1|   Alice|   100|update_preimage |             5 | 2026-09-18T10:15:00
       1|   Alice|   150|update_postimage|             5 | 2026-09-18T10:15:00
       2|     Bob|   200|delete          |             5 | 2026-09-18T10:15:00
       4|    Dana|   400|insert          |             5 | 2026-09-18T10:15:00
```

- **`insert`** — order_id 4 (der `WHEN NOT MATCHED`-Zweig): eine neue Zeile, kein Vorherwert.
- **`delete`** — order_id 2 (der `WHEN MATCHED AND s.action = 'delete'`-Zweig): zeigt den **letzten Stand vor dem Löschen** (200), keine Nachher-Zeile.
- **`update_preimage`/`update_postimage`** — order_id 1 (der `WHEN MATCHED AND s.action = 'update'`-Zweig): **zwei** Zeilen für dieselbe logische Änderung — `preimage` der Wert vor dem `MERGE` (`amount=100`), `postimage` der Wert danach (`amount=150`). Order_id 3 (Carol) taucht **gar nicht** auf, da sie von keinem `WHEN`-Zweig getroffen wurde — unveränderte Zeilen erzeugen keinen CDF-Eintrag.
- Alle vier Zeilen teilen sich `_commit_version`/`_commit_timestamp`, weil sie aus **demselben** `MERGE`-Aufruf (derselben Tabellenversion) stammen.

**Stand:** 2026-09-18.
