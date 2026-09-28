# Schema Evolution

**Schema Evolution** = das **kontrollierte Ändern** des Tabellenschemas: Spalten hinzufügen, umordnen, umbenennen, Typen erweitern (Type Widening). Gegenstück zu [Schema Enforcement](Schema%20Enforcement.md) (das Änderungen abweist).

Änderungen erfolgen **explizit** über DDL (`ALTER TABLE`) oder **implizit** über DML (`mergeSchema`, `WITH SCHEMA EVOLUTION`).

> **Wichtig (Doku-Callout):** *"Schema updates conflict with all concurrent write operations. Databricks recommends coordinating schema changes to avoid write conflicts. Updating a table schema terminates any streams reading from that table."*

---

## A. Explizite Änderungen (`ALTER TABLE`)

**Python:** Es gibt **kein** natives DataFrame-/`DeltaTable`-API für `ALTER TABLE` auf einer **bestehenden** Tabelle. Der Standardweg aus Python ist, dieselbe DDL über `spark.sql(...)` auszuführen.

### Spalten hinzufügen

```sql
ALTER TABLE table_name ADD COLUMNS (col_name data_type [COMMENT col_comment] [FIRST|AFTER colA_name], ...);
```

Nullability standardmäßig `true`. Verschachtelte Felder über Punktnotation; für Structs in `ARRAY`/`MAP`:

```sql
-- points ARRAY<STRUCT<x: DOUBLE, y: DOUBLE>>
ALTER TABLE my_table ADD COLUMNS (points.element.z DOUBLE);
-- points MAP<STRUCT<...>, BIGINT>
ALTER TABLE my_table ADD COLUMNS (points.key.z DOUBLE);
-- points MAP<STRING, STRUCT<...>>
ALTER TABLE my_table ADD COLUMNS (points.value.z DOUBLE);
```

### Umordnen / Kommentar ändern

```sql
ALTER TABLE table_name ALTER [COLUMN] col_name (COMMENT col_comment | FIRST | AFTER colA_name);

ALTER TABLE table_name ALTER COLUMN col_name COMMENT 'col_comment';
ALTER TABLE table_name ALTER COLUMN col_name FIRST;
ALTER TABLE table_name ALTER COLUMN col_name AFTER colA_name;
```

### Spalten ersetzen / umbenennen / löschen

```sql
ALTER TABLE table_name REPLACE COLUMNS (col_name1 col_type1 [COMMENT ...], ...);

-- RENAME / DROP erfordern aktiviertes Column Mapping
ALTER TABLE table_name RENAME COLUMN old_col_name TO new_col_name;
ALTER TABLE boxes RENAME COLUMN colB.field1 TO field001;

ALTER TABLE table_name DROP COLUMN col_name;
ALTER TABLE table_name DROP COLUMNS (col_name_1, col_name_2);
```

> **Hinweis:** *"Dropping a column from metadata does not delete the underlying data for the column in files."* Physische Bereinigung: `REORG TABLE` gefolgt von `VACUUM`.

```sql
-- Dateien mit "soft-deleted" Spaltendaten physisch neu schreiben (Column Mapping vorausgesetzt)
REORG TABLE table_name APPLY (PURGE);

-- Alte Dateiversionen (die die gedroppte Spalte noch enthalten, u. a. für Time Travel) endgültig löschen
VACUUM table_name;
```

**Python:** `REORG TABLE` hat **kein** natives API — nur über `spark.sql()`. `VACUUM` dagegen existiert als native `DeltaTable`-Methode:

```python
spark.sql("REORG TABLE table_name APPLY (PURGE)")

from delta.tables import DeltaTable
DeltaTable.forName(spark, "table_name").vacuum()   # Standard-Retention: 168 Stunden (7 Tage)
```

### Typ-/Namensänderung über `overwriteSchema` (ganze Tabelle neu schreiben)

```python
(spark.read.table(...)
  .withColumn("birthDate", col("birthDate").cast("date"))
  .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(...))

(spark.read.table(...)
  .withColumnRenamed("dateOfBirth", "birthDate")
  .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(...))
```

`overwriteSchema` ist **nicht** mit Dynamic Partition Overwrite kombinierbar.

---

## B. Automatische Evolution bei `INSERT` und `MERGE`

### `INSERT WITH SCHEMA EVOLUTION` (SQL, DBR 18.1+)

```sql
INSERT WITH SCHEMA EVOLUTION INTO target_table
SELECT * FROM source_table;
```

Spalten der Quelle, die im Ziel nicht existieren, werden **automatisch hinzugefügt**. Unterstützt `INSERT INTO`, `INSERT OVERWRITE`, `INSERT INTO … REPLACE`. Ziel muss **Delta Lake** oder **Apache Iceberg** sein. Für DBR ≤ 18.0: `mergeSchema`-Option.

### `mergeSchema` (DataFrame-API / Streaming)

```python
(spark.read.table("source_table")
  .write.option("mergeSchema", "true").mode("append").saveAsTable("target_table"))
```

```python
(spark.readStream.format("cloudFiles").option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "<path>")
  .load("<source>")
  .writeStream.option("mergeSchema", "true")
  .option("checkpointLocation", "<checkpoint>")
  .trigger(availableNow=True).toTable("table_name"))
```

### `MERGE WITH SCHEMA EVOLUTION` (SQL DBR 15.4 LTS+ / Python)

```sql
MERGE WITH SCHEMA EVOLUTION INTO target
USING source ON source.key = target.key
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE;
```

```python
(targetTable.merge(sourceDF, "source.key = target.key")
  .withSchemaEvolution()
  .whenMatchedUpdateAll().whenNotMatchedInsertAll().whenNotMatchedBySourceDelete()
  .execute())
```

**Regeln bei `MERGE`:**

Taucht in der Quelle eine Spalte auf, die im Ziel nicht existiert (namentlich oder per `*` zugewiesen), führt das **ohne** Schema Evolution zu einem Fehlschlag — **mit** Schema Evolution wird sie zum Ziel hinzugefügt und aus der Quelle befüllt. Existiert eine Spalte dagegen nur im Ziel, ändert sich durch Schema Evolution nichts: Bei `UPDATE SET *` bleibt sie unverändert, bei `INSERT *` wird sie `NULL` — Evolution betrifft ausschließlich neue Quellspalten. Bei einem Typkonflikt, der grundsätzlich Type-Widening-fähig ist und bei aktiviertem `delta.enableTypeWidening`, erlaubt der Weg **ohne** Schema Evolution nur einen Safe Cast (kein Schema-Wechsel), während **mit** Schema Evolution der Zieltyp tatsächlich erweitert wird (z. B. `int` → `bigint`).

Evolution wird **nur** ausgelöst, wenn Spaltenname/-struktur in der Quelle **exakt** der Ziel-Zuweisung entsprechen. Berechnete Zuweisungen (`SET target.newcol = source.x + source.y`), Umbenennungen (`= source.someothercol`) und verschachtelte Quellpfade (`= source.output.newcol`) lösen **keine** Evolution aus.

`EXCEPT`-Klausel (ab DBR 12.2 LTS): ausgeschlossene Spalten werden nicht dem Schema hinzugefügt.

**Versionsgrenzen:** bis DBR 11.3 LTS nur `INSERT *`/`UPDATE SET *`; ab 12.2 LTS namentliche Spalten; ab 13.3 LTS Structs in Maps.

### Legacy: `spark.databricks.delta.schema.autoMerge.enabled`

```sql
SET spark.databricks.delta.schema.autoMerge.enabled = true;
```

Session-weit für **alle** Schreiboperationen — von Databricks als **Legacy** markiert, **nicht** für Produktion empfohlen. Per-Operation-Optionen haben **Vorrang**.

---

## C. Schema-Evolution-Modi bei Auto Loader / `STREAM read_files` (`schemaEvolutionMode`)

Steuert das Verhalten bei **neu auftauchenden Spalten** im Streaming-Modus. Es gibt fünf Modi:

- **`addNewColumns`** (Default, wenn kein Schema angegeben ist): Bei einer neuen Spalte stoppt der Stream mit einer `UnknownFieldException`. Der Schema-Speicherort wird **vorher** aktualisiert, sodass ein Neustart das erweiterte Schema automatisch übernimmt.
- **`rescue`**: Das Schema bleibt eingefroren, der Stream läuft ungestört weiter. Neue oder nicht passende Spalten landen stattdessen in der `rescuedDataColumn`.
- **`failOnNewColumns`**: Der Stream schlägt bei einer neuen Spalte fehl, aber **ohne** automatisches Update — ein Neustart ist erst nach manueller Schema-Aktualisierung möglich.
- **`none`** (Default, wenn ein Schema explizit angegeben ist): Das Schema entwickelt sich nicht weiter, neue Spalten werden einfach ignoriert. Der Stream schlägt dabei nicht fehl, die ignorierten Daten werden aber auch **nicht** gerettet — außer die `rescuedDataColumn` ist explizit gesetzt.
- **`addNewColumnsWithTypeWidening`** (ab DBR 16.4): verhält sich wie `addNewColumns`, ergänzt um automatische, verlustfreie Typ-Erweiterung (z. B. `int` → `long`).

Type Widening (verlustfrei): `byte`→`short`/`int`/`long`/`decimal`/`double`; `int`→`long`/`decimal`/`double`; `float`→`double`; `date`→`timestampNTZ` (nur Parquet); u. a.

### Beispiele je Modus — SQL (`STREAM read_files`) vs. Python (`cloudFiles`)

```sql
-- addNewColumns (Default ohne Schema-Angabe)
CREATE OR REFRESH STREAMING TABLE events_evolving
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'addNewColumns'
);
```
```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.schemaEvolutionMode", "addNewColumns")
      .load("/Volumes/analytics/bronze/events"))
```

```sql
-- rescue — Schema eingefroren, neue Spalten landen in _rescued_data
CREATE OR REFRESH STREAMING TABLE events_rescue_only
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'rescue'
);
```
```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.schemaEvolutionMode", "rescue")
      .load("/Volumes/analytics/bronze/events"))
```

```sql
-- failOnNewColumns — Stream schlägt fehl, kein automatisches Schema-Update
CREATE OR REFRESH STREAMING TABLE events_strict
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'failOnNewColumns'
);
```
```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.schemaEvolutionMode", "failOnNewColumns")
      .load("/Volumes/analytics/bronze/events"))
```

```sql
-- none (Default MIT angegebenem Schema) — neue Spalten werden ignoriert
CREATE OR REFRESH STREAMING TABLE events_fixed_schema
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schema => 'id LONG, event STRING, ts TIMESTAMP',
  schemaEvolutionMode => 'none'
);
```
```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .schema("id LONG, event STRING, ts TIMESTAMP")
      .option("cloudFiles.schemaEvolutionMode", "none")
      .load("/Volumes/analytics/bronze/events"))
```

```sql
-- addNewColumnsWithTypeWidening — zusätzlich automatische, verlustfreie Typ-Erweiterung
CREATE OR REFRESH STREAMING TABLE events_type_widening
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'addNewColumnsWithTypeWidening'
);
```
```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.schemaEvolutionMode", "addNewColumnsWithTypeWidening")
      .load("/Volumes/analytics/bronze/events"))
```

---

## Verwandte Themen

- [Schema Definition (StructType).md](Schema%20Definition%20%28StructType%29.md) · [Schema Enforcement.md](Schema%20Enforcement.md) · [Schema Inference.md](Schema%20Inference.md) · [Rescued Data.md](Rescued%20Data.md)
- Deep-Dive: [01 Platform/02 Tables/06 Schema und Tabellenhistorie.md](01%20Platform/02%20Tables/06%20Schema%20und%20Tabellenhistorie.md) (Abschnitt 4) · [06 DML Statements/_merge_into.md](06%20DML%20Statements/_merge_into.md) (Abschnitt 4)
- [07 Data Management/01 Data Engineering/01 Concepts/04-schema-evolution.md](07%20Data%20Management/01%20Data%20Engineering/01%20Concepts/04-schema-evolution.md)
- Type Widening: [01 Platform/02 Tables/07 Table Features/13 Type Widening.md](01%20Platform/02%20Tables/07%20Table%20Features/13%20Type%20Widening.md)
