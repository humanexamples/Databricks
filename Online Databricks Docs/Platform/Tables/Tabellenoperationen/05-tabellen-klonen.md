# Tabellen klonen

Mit dem Befehl `CLONE` erstellen Sie unabhängige Kopien einer Tabelle zu einer bestimmten Version. Databricks unterstützt zwei Klon-Arten: Deep Clone und Shallow Clone.

## Klon-Arten

**Deep Clone** (`CLONE` oder `DEEP CLONE`) kopiert sowohl Daten als auch Metadaten von der Quelle in das Ziel. Auch Stream-Metadaten werden übernommen. Ein Stream lässt sich auf dem Klon von seiner vorherigen Position aus anhalten und fortsetzen.

**Shallow Clone** (`SHALLOW CLONE`) kopiert nur die Metadaten. Die Daten bleiben am Ursprungsort. Ein Shallow Clone ist günstiger, da er weniger Rechenleistung und Speicher benötigt.

Geklonte Metadaten umfassen Schema, Partitionierung, Constraints, Nullability und Tabelleneigenschaften. Deep Clones übernehmen zusätzlich Stream- und `COPY INTO`-Metadaten. Nicht geklont werden: Tabellenbeschreibungen, benutzerdefinierte Commit-Metadaten, Delta-Lake-Historie und Unity-Catalog-Tags.

## Benötigte Berechtigungen

**Tabellenzugriffskontrolle:**
- `SELECT`-Recht auf die Quelltabelle
- `CREATE`-Recht auf die Zieldatenbank (bei neuen Tabellen)
- `MODIFY`-Recht auf die Zieltabelle (bei Ersetzung)

**Cloud-Provider-Berechtigungen:**
- Bei Deep Clone: Leser benötigen Lesezugriff auf das Klon-Verzeichnis, Schreiber benötigen Schreibzugriff
- Bei Shallow Clone: Leser benötigen Lesezugriff sowohl auf die Quelldateien als auch auf das Klon-Verzeichnis

## Grundlegende Syntax

Einen Deep Clone erstellen:

```sql
%sql
CREATE TABLE target_table CLONE source_table;
```

Ein bestehendes Ziel ersetzen:

```sql
%sql
CREATE OR REPLACE TABLE target_table CLONE source_table;
```

Nur erstellen, wenn noch nicht vorhanden:

```sql
%sql
CREATE TABLE IF NOT EXISTS target_table CLONE source_table;
```

Varianten für Shallow Clone:

```sql
%sql
CREATE TABLE target_table SHALLOW CLONE source_table;
CREATE TABLE target_table SHALLOW CLONE source_table VERSION AS OF version;
CREATE TABLE target_table SHALLOW CLONE source_table TIMESTAMP AS OF timestamp_expression;
```

## Klonen mit Python

Python – die neueste Version klonen:

```python
from delta.tables import *
deltaTable = DeltaTable.forName(spark, "source_table")
deltaTable.clone(target="target_table", isShallow=True, replace=False)
```

Python – eine bestimmte Version klonen:

```python
deltaTable.cloneAtVersion(version=1, target="target_table", isShallow=True, replace=False)
```

Python – auf Basis eines Zeitstempels klonen:

```python
deltaTable.cloneAtTimestamp(timestamp="2019-01-01", target="target_table", isShallow=True, replace=False)
```

## Beispiel: Metadaten prüfen

Zuerst eine Quelltabelle mit Eigenschaften und Tags anlegen und Daten einfügen:

```sql
%sql
CREATE OR REPLACE TABLE test_clone_source (id INT, val STRING)
TBLPROPERTIES ('my.custom.prop' = 'hello', 'delta.logRetentionDuration' = '12 days');
ALTER TABLE test_clone_source SET TAGS ('team' = 'data-eng', 'env' = 'prod');
INSERT INTO test_clone_source VALUES (1, 'a');
INSERT INTO test_clone_source VALUES (2, 'b');
```

Deep Clone und Shallow Clone erstellen:

```sql
%sql
CREATE OR REPLACE TABLE test_clone_deep DEEP CLONE test_clone_source;
CREATE TABLE test_clone_shallow SHALLOW CLONE test_clone_source;
```

Tabelleneigenschaften vergleichen:

```sql
%sql
SHOW TBLPROPERTIES test_clone_source;
SHOW TBLPROPERTIES test_clone_deep;
SHOW TBLPROPERTIES test_clone_shallow;
```

Prüfen, dass Tags nicht kopiert werden:

```sql
%sql
SELECT catalog_name, schema_name, table_name, tag_name, tag_value FROM
information_schema.table_tags WHERE table_name = 'test_clone_source';
SELECT catalog_name, schema_name, table_name, tag_name, tag_value FROM
information_schema.table_tags WHERE table_name = 'test_clone_deep';
SELECT catalog_name, schema_name, table_name, tag_name, tag_value FROM
information_schema.table_tags WHERE table_name = 'test_clone_shallow';
```

Prüfen, dass die Historie nicht kopiert wird:

```sql
%sql
DESCRIBE HISTORY test_clone_source;
DESCRIBE HISTORY test_clone_deep;
DESCRIBE HISTORY test_clone_shallow;
```

Aufräumen:

```sql
%sql
DROP TABLE IF EXISTS test_clone_shallow;
DROP TABLE IF EXISTS test_clone_source;
DROP TABLE IF EXISTS test_clone_deep;
```

## Praxisbeispiele

Monatliches Archiv synchronisieren:

```sql
%sql
CREATE OR REPLACE TABLE archive_table CLONE my_prod_table
```

Ein Datenset für ein ML-Modell archivieren:

```sql
%sql
CREATE TABLE model_dataset CLONE entire_dataset VERSION AS OF 15
```

Ein Shallow Clone zum Testen erstellen:

```sql
%sql
CREATE TABLE my_test SHALLOW CLONE my_prod_table;
```

Den Testklon ändern:

```sql
%sql
UPDATE my_test WHERE user_id is null SET invalid=true;
```

Änderungen zurück in die Produktionstabelle mergen:

```sql
%sql
MERGE INTO my_prod_table
USING my_test
ON my_test.user_id <=> my_prod_table.user_id
WHEN MATCHED AND my_test.user_id is null THEN UPDATE *;
```

Den Testklon löschen:

```sql
%sql
DROP TABLE my_test;
```

## Archivierung mit erweiterter Aufbewahrungsdauer

Für Delta Lake:

```sql
%sql
CREATE OR REPLACE TABLE archive_table CLONE prod.my_table
TBLPROPERTIES (delta.logRetentionDuration = '3650 days',
delta.deletedFileRetentionDuration = '3650 days')
```

Für Iceberg:

```sql
%sql
CREATE OR REPLACE TABLE archive_table CLONE prod.my_table
TBLPROPERTIES (iceberg.logRetentionDuration = '3650 days',
iceberg.deletedFileRetentionDuration = '3650 days')
```

Python – Delta-Lake-Klon mit Eigenschaften:

```python
dt = DeltaTable.forName(spark, "prod.my_table")
tblProps = {"delta.logRetentionDuration": "3650 days",
            "delta.deletedFileRetentionDuration": "3650 days"}
dt.clone(target="archive_table", isShallow=False, replace=True, tblProps)
```

## Wichtige Punkte

Shallow Clones referenzieren die Datendateien der Quelle. Läuft `VACUUM` auf der Quelltabelle, können daher Lesefehler im Klon auftreten. Deep Clones sind unabhängig von der Quelle, verursachen aber höhere Erstellungskosten.

Klonen unterscheidet sich von `Create Table As Select`: Beim Klonen werden die Metadaten der Quelltabelle direkt übernommen. Partitionierung, Format und andere Einstellungen müssen nicht manuell angegeben werden.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/operations/clone  
**Stand:** 2026-08-06
