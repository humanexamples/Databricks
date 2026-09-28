# Tabellenschema aktualisieren

Databricks-Tabellen unterstützen Schema-Evolution. Sie können Spalten an beliebiger Position hinzufügen, Spalten neu anordnen, umbenennen und Typen erweitern.

Schema-Änderungen stehen im Konflikt mit allen gleichzeitigen Schreibvorgängen. Databricks empfiehlt, Schema-Änderungen zu koordinieren, um Schreibkonflikte zu vermeiden. Außerdem beendet eine Schema-Aktualisierung alle aktiven Streams, die von der Tabelle lesen.

## Schema manuell ändern

### Spalten hinzufügen

```sql
%sql
ALTER TABLE table_name ADD COLUMNS (col_name data_type [COMMENT col_comment] [FIRST|AFTER colA_name], ...)
```

Neue Spalten sind standardmäßig nullable. Für verschachtelte Structs sieht die Syntax so aus:

```sql
%sql
ALTER TABLE table_name ADD COLUMNS (col_name.nested_col_name data_type [COMMENT col_comment] [FIRST|AFTER colA_name], ...)
```

### Kommentare und Reihenfolge ändern

```sql
%sql
ALTER TABLE table_name ALTER [COLUMN] col_name (COMMENT col_comment | FIRST | AFTER colA_name)
```

Für verschachtelte Felder:

```sql
%sql
ALTER TABLE table_name ALTER [COLUMN] col_name.nested_col_name (COMMENT col_comment | FIRST | AFTER colA_name)
```

### Spalten ersetzen

Dieser Befehl definiert die gesamte Spaltenliste in einer einzigen Transaktion neu.

```sql
%sql
ALTER TABLE table_name REPLACE COLUMNS (col_name1 col_type1 [COMMENT col_comment1], ...)
```

### Spalten umbenennen

Für ein Umbenennen ohne Neuschreiben der Daten muss Column Mapping aktiviert sein.

```sql
%sql
ALTER TABLE table_name RENAME COLUMN old_col_name TO new_col_name
```

Für verschachtelte Felder:

```sql
%sql
ALTER TABLE table_name RENAME COLUMN col_name.old_nested_field TO new_nested_field
```

### Spalten löschen

Für ein reines Löschen aus den Metadaten muss Column Mapping aktiviert sein. Einzelne Spalte:

```sql
%sql
ALTER TABLE table_name DROP COLUMN col_name
```

Mehrere Spalten:

```sql
%sql
ALTER TABLE table_name DROP COLUMNS (col_name_1, col_name_2)
```

Ein Löschen aus den Metadaten entfernt die zugrunde liegenden Daten nicht. Mit `REORG TABLE` gefolgt von `VACUUM` werden die Daten der gelöschten Spalte physisch entfernt.

### Spaltentyp oder -namen per Overwrite ändern

Python-Beispiel für eine Typ-Änderung:

```python
(spark.read.table(...)
 .withColumn("birthDate", col("birthDate").cast("date"))
 .write
 .mode("overwrite")
 .option("overwriteSchema", "true")
 .saveAsTable(...))
```

Für eine Umbenennung:

```python
(spark.read.table(...)
 .withColumnRenamed("dateOfBirth", "birthDate")
 .write
 .mode("overwrite")
 .option("overwriteSchema", "true")
 .saveAsTable(...))
```

## Schema-Evolution aktivieren

Es gibt drei Hauptmethoden:

1. `INSERT WITH SCHEMA EVOLUTION` (ab Runtime 18.1)
2. Option `mergeSchema` bei Schreibvorgängen
3. `MERGE WITH SCHEMA EVOLUTION` (ab Runtime 15.4)

Databricks empfiehlt eine Aktivierung pro Operation statt einer sitzungsweiten Konfiguration.

### INSERT mit Schema-Evolution (SQL, ab Runtime 18.1)

```sql
%sql
INSERT WITH SCHEMA EVOLUTION INTO target_table
SELECT * FROM source_table
```

Dieser Befehl fügt automatisch Spalten aus der Quelle hinzu, die in der Zieltabelle noch nicht existieren. Bestehende Zeilen erhalten für neue Spalten NULL. Unterstützt werden `INSERT INTO`, `INSERT OVERWRITE` und `INSERT INTO ... REPLACE`. Die Zieltabelle muss Delta Lake oder Apache Iceberg sein.

### INSERT mit Schema-Evolution (DataFrame API)

```python
(spark.read
 .table("source_table")
 .write
 .option("mergeSchema", "true")
 .mode("append")
 .saveAsTable("target_table"))
```

### Structured Streaming mit Auto Loader

```python
(spark.readStream
 .format("cloudFiles")
 .option("cloudFiles.format", "json")
 .option("cloudFiles.schemaLocation", "<path-to-schema-location>")
 .load("<path-to-source-data>")
 .writeStream
 .option("mergeSchema", "true")
 .option("checkpointLocation", "<path-to-checkpoint>")
 .trigger(availableNow=True)
 .toTable("table_name"))
```

## Automatische Schema-Evolution bei MERGE

Schema-Evolution bei MERGE deckt zwei Situationen ab.

**Fall 1:** Eine Quellspalte, die in der Zieltabelle fehlt, wird namentlich in einer INSERT- oder UPDATE-Aktion genannt, oder es gibt `UPDATE SET *` beziehungsweise `INSERT *`. Die Spalte wird dann zum Zielschema hinzugefügt und aus der Quelle befüllt.

Gültige Beispiele:

```sql
%sql
UPDATE SET target.newcol = source.newcol
UPDATE SET target.somestruct.newfield = source.somestruct.newfield
UPDATE SET target.newcol = source.newcol + 1
UPDATE SET *
INSERT *
```

Ungültige Beispiele (lösen keine Evolution aus, wenn `newcol` nicht im Quellschema vorkommt):

```sql
%sql
UPDATE SET target.newcol = source.someothercol
UPDATE SET target.newcol = source.x + source.y
UPDATE SET target.newcol = source.output.newcol
```

**Fall 2:** Eine Zielspalte, die in der Quelle fehlt, bleibt bei `UPDATE SET *` unverändert, wird bei `INSERT *` auf NULL gesetzt oder lässt sich explizit in der Aktion setzen.

### MERGE mit Schema-Evolution (SQL, ab Runtime 15.4)

```sql
%sql
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

### MERGE mit Schema-Evolution (Python)

```python
from delta.tables import *

(targetTable
 .merge(sourceDF, "source.key = target.key")
 .withSchemaEvolution()
 .whenMatchedUpdateAll()
 .whenNotMatchedInsertAll()
 .whenNotMatchedBySourceDelete()
 .execute())
```

## Spalten mit MERGE ausschließen

Ab Runtime 12.2 sind EXCEPT-Klauseln möglich. Ohne Schema-Evolution bezieht sich EXCEPT auf Zielspalten: Sie werden von Updates oder Inserts ausgenommen und auf NULL gesetzt. Mit Schema-Evolution bezieht sich EXCEPT auf Quellspalten: Neue Spalten werden dadurch nicht zum Zielschema hinzugefügt.

```sql
%sql
MERGE INTO target t
USING source s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET last_updated = current_date()
WHEN NOT MATCHED THEN INSERT * EXCEPT (last_updated)
```

## Legacy Spark-Konfiguration

Eine sitzungsweite Aktivierung (für Produktionsumgebungen nicht empfohlen):

```python
spark.conf.set("spark.databricks.delta.schema.autoMerge.enabled", True)
```

```sql
%sql
SET spark.databricks.delta.schema.autoMerge.enabled=true
```

Optionen pro Operation haben Vorrang vor dieser Konfiguration.

## Tabellenschema ersetzen

Die Option `overwriteSchema` ersetzt sowohl das Schema als auch die Partitionierung.

```python
df.write.option("overwriteSchema", "true")
```

Diese Option lässt sich nicht mit dynamischem Partition-Overwrite-Modus kombinieren.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/update-schema  
**Stand:** 2026-08-06
