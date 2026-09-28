# Liquid Clustering für Tabellen nutzen

Liquid Clustering ist eine Technik zur Datenlayout-Optimierung. Sie ersetzt klassische Tabellenpartitionierung und `ZORDER`. Liquid Clustering vereinfacht die Tabellenpflege und verbessert die Abfrageperformance automatisch.

Anders als bei klassischer Partitionierung können Sie die Clustering-Keys neu definieren, ohne bestehende Daten neu zu schreiben. So kann sich das Datenlayout an veränderte Analyseanforderungen anpassen. Liquid Clustering funktioniert auch bei Streaming Tables und materialisierten Views.

**Wichtig:** Liquid Clustering ist für Delta-Lake-Tabellen ab Databricks Runtime 15.4 LTS allgemein verfügbar (GA). Für Apache-Iceberg-Tabellen befindet es sich ab Runtime 16.4 LTS in Public Preview. Databricks empfiehlt die jeweils neueste Runtime für beste Performance.

Managed Apache-Iceberg-v3-Tabellen unterstützen zusätzlich Deletion Vectors, Row Tracking, zeilenweise Nebenläufigkeit (Row-Level Concurrency) und automatisches Liquid Clustering. Diese Funktionen benötigen Databricks Runtime 18.0 oder höher.

## Wann Liquid Clustering sinnvoll ist

Databricks empfiehlt Liquid Clustering für alle neuen Tabellen, auch für Streaming Tables und materialisierte Views. Besonders profitieren folgende Szenarien:

- Abfragen, die nach Spalten mit hoher Kardinalität filtern
- Tabellen mit starker Datenschiefe (Data Skew)
- Schnell wachsende Tabellen mit hohem Pflege- und Tuning-Aufwand
- Tabellen mit gleichzeitigen Schreibzugriffen
- Tabellen mit unterschiedlichen oder sich ändernden Zugriffsmustern
- Tabellen, bei denen ein typischer Partitionsschlüssel zu viele oder zu wenige Partitionen liefert

## Liquid Clustering aktivieren

Sie können Liquid Clustering bei der Tabellenerstellung oder nachträglich auf einer unpartitionierten Tabelle aktivieren. Clustering ist nicht mit Partitionierung oder `ZORDER` kombinierbar. Nach der Aktivierung führen Sie `OPTIMIZE`-Jobs aus, um Daten schrittweise zu clustern.

## Tabellen mit Clustering erstellen

Fügen Sie die Klausel `CLUSTER BY` zur Tabellenerstellung hinzu. Ab Databricks Runtime 14.3 LTS können Sie auch die DataFrame- und DeltaTable-APIs in Python nutzen.

Eine leere Tabelle mit Clustering erstellen:

```sql
%sql
CREATE TABLE table1 (col0 INT, col1 STRING) CLUSTER BY (col0);
```

Eine Tabelle aus bestehenden Daten erstellen. `CLUSTER BY` muss nach dem Tabellennamen stehen, nicht in der `SELECT`-Klausel:

```sql
%sql
CREATE TABLE table2 CLUSTER BY (col0) AS SELECT * FROM table1;
```

Eine Tabellenstruktur samt Clustering-Konfiguration kopieren:

```sql
%sql
CREATE TABLE table3 LIKE table1;
```

Eine leere Tabelle mit der `DeltaTable`-API in Python erstellen:

```python
(DeltaTable.create()
    .tableName("table1")
    .addColumn("col0", dataType = "INT")
    .addColumn("col1", dataType = "STRING")
    .clusterBy("col0")
    .execute())
```

Eine Tabelle aus einem bestehenden DataFrame erstellen:

```python
df = spark.read.table("table1")
df.write.clusterBy("col0").saveAsTable("table2")
```

Eine Tabelle mit der `DataFrameWriterV2`-API erstellen (ab Runtime 14.2):

```python
df = spark.read.table("table1")
df.writeTo("table1").using("delta").clusterBy("col0").create()
```

**Wichtig:** Setzen Sie Clustering-Spalten über DataFrame-APIs nur bei der Tabellenerstellung oder im `overwrite`-Modus (zum Beispiel bei `CREATE OR REPLACE TABLE`). Im `append`-Modus können Sie die Clustering-Keys nicht ändern. Nutzen Sie dafür SQL-`ALTER TABLE`-Befehle getrennt von den Schreiboperationen.

Ab Databricks Runtime 16.4 LTS können Sie Tabellen mit aktiviertem Liquid Clustering auch über Structured-Streaming-Writes erstellen:

```sql
%sql
CREATE TABLE table1 (
  col0 STRING,
  col1 DATE,
  col2 BIGINT)
CLUSTER BY (col0, col1);
```

```python
(spark.readStream.table("source_table")
    .writeStream
    .clusterBy("column_name")
    .option("checkpointLocation", checkpointPath)
    .toTable("target_table"))
```

**Achtung:** Delta-Lake-Tabellen mit aktiviertem Liquid Clustering nutzen Delta Writer Version 7 und Reader Version 3. Clients, die diese Protokolle nicht unterstützen, können diese Tabellen nicht lesen. Ein Downgrade der Protokollversion ist nicht möglich.

## Auf bestehenden Tabellen aktivieren

So aktivieren Sie Liquid Clustering auf einer bestehenden, unpartitionierten Delta-Lake-Tabelle:

```sql
%sql
ALTER TABLE <table_name>
CLUSTER BY (<clustering_columns>)
```

Für Managed-Apache-Iceberg-Tabellen gilt: Bei der v2-Spezifikation müssen Sie Deletion Vectors und Row Tracking explizit deaktivieren, bevor Sie Liquid Clustering aktivieren. Bei der v3-Spezifikation ist das nicht nötig, da diese Funktionen dort unterstützt werden.

Das Standardverhalten wendet Clustering nicht auf bereits geschriebene Daten an. Um ein erneutes Clustering zu erzwingen, nutzen Sie `OPTIMIZE FULL` oder `OPTIMIZE FULL WHERE <predicate>`.

## Eine partitionierte Tabelle zu Liquid Clustering konvertieren

Ab Databricks Runtime 18.1 nutzen Sie `REPLACE PARTITIONED BY WITH CLUSTER BY` in einem `ALTER TABLE`-Befehl, um eine partitionierte Delta-Lake-Tabelle zu konvertieren. Die Konvertierung minimiert Ausfallzeiten für Leser und Schreiber und unterstützt sowohl externe als auch Managed Tables. Nach der Konvertierung unterstützt die Tabelle Lesezugriffe ab Databricks Runtime 13.3 LTS.

Für Managed-Iceberg-Tabellen ist die Konvertierung nicht nötig, da diese Tabellen Partitionsdefinitionen bereits als Clustering-Keys verwenden. Der Konvertierungsbefehl liefert dort einen Fehler.

Vorteile der Konvertierung von partitionierten Tabellen:

- Bessere Performance bei Tabellen mit schlechtem Data Skipping oder Über-Partitionierung
- Automatische Performance-Verbesserungen mit `CLUSTER BY AUTO` bei häufig wechselnden Abfragemustern
- Flexible und einfach änderbare Clustering-Spalten, während Partitionierung starr ist
- Weniger Schreibkonflikte, da Liquid Clustering zeilenweise Nebenläufigkeit erlaubt

## Syntax

```sql
%sql
ALTER TABLE <table_name>
REPLACE PARTITIONED BY WITH CLUSTER BY [( <clustering_columns> ) | AUTO]
```

Die `CLUSTER BY`-Klausel unterstützt folgende Optionen:

- **(<clustering_columns>):** Legt neue Clustering-Spalten fest. Halten Sie diese möglichst ähnlich zu den ursprünglichen Partitionsspalten. Sehr unterschiedliche Spalten lösen beim ersten `OPTIMIZE` ein großes Reclustering aus.
- **AUTO:** Nutzt die aktuellen Partitionsspalten als Startpunkt. Predictive Optimization passt die Auswahl danach automatisch an. Nur für Unity-Catalog-Managed-Tables verfügbar.
- **Keine Angabe:** Nutzt die aktuellen Partitionsspalten als neue Clustering-Spalten.

## Beispiele

Clustering auf andere Spalten als die ursprüngliche Partitionierung anwenden, etwa bei einer Tabelle mit Partitionierung nach `(year, month, day)`:

```sql
%sql
ALTER TABLE t1 REPLACE PARTITIONED BY WITH CLUSTER BY (day, id);
OPTIMIZE t1;
```

Um vom Ändern der Clustering-Spalten zu profitieren, müssen Sie `OPTIMIZE` ausführen.

Automatisches Liquid Clustering mit den aktuellen Partitionsspalten starten:

```sql
%sql
ALTER TABLE t2 REPLACE PARTITIONED BY WITH CLUSTER BY AUTO;
```

Die aktuellen Partitionsspalten als Clustering-Spalten beibehalten:

```sql
%sql
ALTER TABLE t3 REPLACE PARTITIONED BY WITH CLUSTER BY;
```

## Gleichzeitige Lese- und Schreibzugriffe während der Konvertierung

Nach der Konvertierung werden Lese- und Schreibzugriffe ab Databricks Runtime 13.3 LTS unterstützt. Databricks empfiehlt Runtime 15.4 LTS oder höher für Workloads, die während der Konvertierung lesen oder schreiben.

| Workload-Typ | Lesen während der Konvertierung | Schreiben während der Konvertierung |
| --- | --- | --- |
| Batch | Keine Ausfallzeit. Alle Runtime-Versionen können während der Konvertierung lesen. | Keine Ausfallzeit ab Runtime 15.4. Bei Runtime 15.3 und darunter empfiehlt Databricks, Workloads vor der Konvertierung zu pausieren und danach neu zu starten. |
| Streaming | Mit Schema Tracking und Column Mapping: Neustart ohne Verlust von Commits. Ohne diese Funktionen: Der Stream wirft eine Exception. Neustart mit neuem Checkpoint und Startversion nötig, Commits gehen nicht verloren. | Neustart ohne Verlust von Commits. |

## Konvertierung prüfen oder rückgängig machen

Zur Bestätigung der Konvertierung führen Sie `DESCRIBE EXTENDED` aus, um die neuen Clustering-Spalten zu sehen. Mit `DESCRIBE HISTORY` sehen Sie eine Reihe von `REORG`-Operationen, eine `UPGRADE PROTOCOL`-Operation und eine `REPLACE PARTITIONED BY WITH CLUSTER BY`-Operation.

Um eine Konvertierung rückgängig zu machen, nutzen Sie `RESTORE`, um zur vorherigen Version zurückzukehren:

```sql
%sql
ALTER TABLE my_table CLUSTER BY NONE;
ALTER TABLE my_table UNSET TBLPROPERTIES ('delta.liquid.hierarchicalClusteringColumns');
RESTORE TABLE my_table TO VERSION AS OF <version_number_before_conversion>;
```

## Eine nach Zeitstempel partitionierte Tabelle konvertieren

Um eine Tabelle `t1`, die nach einer Zeitstempelspalte `timestamp_col` partitioniert ist, zu konvertieren und diese Spalte als Clustering-Key zu nutzen, benötigen Sie zusätzliche Konfigurationen:

```sql
%sql
SET spark.databricks.delta.liquidConversion.statsGeneration.enabled = false;
ALTER TABLE t1 REPLACE PARTITIONED BY WITH CLUSTER BY (timestamp_col, id);
ANALYZE TABLE t1 COMPUTE DELTA STATISTICS;
```

Ohne diese Konfiguration liefert der Befehl folgenden Fehler:

```sql
%sql
ALTER TABLE REPLACE PARTITIONED BY WITH CLUSTER BY cannot auto-generate stats on table
with column event_ts due to unsupported type: timestamp. Disable stats auto-generation
by setting 'spark.databricks.delta.liquidConversion.statsGeneration.enabled' to 'false'
and retry the command again. SQLSTATE: 42000
```

## Einschränkungen bei der Konvertierung

- Streaming Tables und materialisierte Views aus Lakeflow-Pipelines werden nicht unterstützt. Nutzen Sie stattdessen `CLUSTER BY` statt `PARTITIONED BY` in der Pipeline-Definition.
- Tabellen, die Delta Sharing mit Partitionsfilterung nutzen, werden nicht unterstützt.

## Clustering-Keys entfernen

```sql
%sql
ALTER TABLE table_name CLUSTER BY NONE;
```

## Clustering-Keys auswählen

Wählen Sie Clustering-Keys auf Basis der Spalten, die am häufigsten in Filtern verwendet werden. Die richtigen Keys verbessern Data Skipping und Abfrageperformance deutlich.

**Tipp:** Databricks empfiehlt automatisches Liquid Clustering, um Clustering-Keys intelligent anhand der Abfragemuster auszuwählen.

## Auswahlrichtlinien

Wenn Sie Clustering-Keys manuell festlegen, wählen Sie Spalten, die am häufigsten in Abfragefiltern vorkommen. Die Reihenfolge der Keys spielt keine Rolle. Sind zwei Spalten stark korreliert, reicht es, nur eine davon als Clustering-Key zu nehmen.

Sie können bis zu vier Clustering-Keys angeben. Bei kleineren Tabellen (unter 10 TB) kann eine höhere Anzahl an Keys die Performance bei Filterung nach nur einer Spalte verschlechtern. Bei wachsender Tabellengröße wird dieser Unterschied vernachlässigbar.

Clustering-Keys müssen Spalten sein, für die Statistiken erfasst werden. Standardmäßig sammelt Delta Lake Statistiken für die ersten 32 Spalten.

## Unterstützte Datentypen

- Date
- Timestamp
- TimestampNTZ (ab Databricks Runtime 14.3 LTS)
- String
- Integer, Long, Short, Byte
- Float, Double, Decimal

Sie können auch nach einem `StructField` per Punktnotation clustern, zum Beispiel `CLUSTER BY (struct_col.field)`. Verschachtelte Struct-Felder sind bis zu beliebiger Tiefe möglich, etwa `CLUSTER BY (struct_col.nested.field)`. Der Datentyp des Feldes muss unterstützt sein.

Nicht möglich ist Clustering nach:

- Komplexen Typen wie `StructType`, `MapType` oder `ArrayType`
- Elementen von `MapType` und `ArrayType`, etwa `map_col['key']`, `array_col[0]` oder `map_col.key`

## Migration von Partitionierung oder Z-Order

**Wichtig:** Databricks empfiehlt die automatische Konvertierung mit `REPLACE PARTITIONED BY WITH CLUSTER BY`.

| Aktuelle Optimierungstechnik | Empfehlung für Clustering-Keys |
| --- | --- |
| Hive-Style-Partitionierung | Partitionsspalten als Clustering-Keys verwenden |
| Z-Order-Indexierung | `ZORDER BY`-Spalten als Clustering-Keys verwenden |
| Hive-Style-Partitionierung und Z-Order | Beide Spaltensätze als Clustering-Keys verwenden |
| Generierte Spalten zur Reduktion der Kardinalität (z. B. Datum aus einem Zeitstempel) | Die Originalspalte als Clustering-Key verwenden, keine generierte Spalte erstellen |

## Automatisches Liquid Clustering

Ab Databricks Runtime 15.4 LTS können Sie automatisches Liquid Clustering für Unity-Catalog-Managed-Delta-Lake-Tabellen aktivieren. Für Unity-Catalog-Managed-Apache-Iceberg-v3-Tabellen benötigt automatisches Liquid Clustering Runtime 18.0 oder höher. Databricks wählt dabei die Clustering-Keys intelligent selbst, über die Klausel `CLUSTER BY AUTO`.

Automatisches Liquid Clustering wird auch für materialisierte Views und Streaming Tables unterstützt, inklusive Lakeflow-Pipelines und eigenständiger Pipelines. Geben Sie dafür `CLUSTER BY AUTO` in der Pipeline- oder SQL-Definition an.

## So funktioniert automatisches Liquid Clustering

Automatisches Liquid Clustering benötigt Predictive Optimization für die automatische Auswahl der Keys und läuft asynchron im Hintergrund.

- **Analysiert das Abfrage-Workload:** Databricks analysiert die historischen Abfragen der Tabelle und identifiziert die besten Kandidatenspalten für das Clustering.
- **Passt sich Änderungen an:** Ändern sich Abfragemuster oder Datenverteilung, wählt automatisches Liquid Clustering neue Keys, um die Performance zu optimieren.
- **Kostenbewusste Auswahl:** Databricks ändert Clustering-Keys nur, wenn die erwartete Ersparnis durch besseres Data Skipping die Kosten des Clusterings übersteigt.

Automatisches Liquid Clustering wählt möglicherweise keine Keys aus, wenn:

- die Tabelle zu klein ist, um von Liquid Clustering zu profitieren
- die Tabelle bereits ein wirksames Clustering-Schema hat, etwa durch frühere manuelle Keys oder eine natürliche Einfügereihenfolge, die zu den Abfragemustern passt
- die Tabelle nicht häufig abgefragt wird
- Sie nicht Databricks Runtime 15.4 LTS oder höher verwenden

Sie können automatisches Liquid Clustering für alle Unity-Catalog-Managed-Tables aktivieren, unabhängig von Daten- und Abfrageeigenschaften. Heuristiken entscheiden, ob eine Auswahl von Clustering-Keys kosteneffizient ist.

## Kompatibilität mit Databricks-Runtime-Versionen

Tabellen mit automatischem Clustering können Sie mit allen Databricks-Runtime-Versionen lesen und schreiben, die Liquid Clustering unterstützen. Die intelligente Key-Auswahl basiert jedoch auf Metadaten, die erst mit Databricks Runtime 15.4 LTS eingeführt wurden.

Nutzen Sie Databricks Runtime 15.4 LTS oder höher, damit automatisch gewählte Keys allen Workloads zugutekommen und diese bei der Auswahl neuer Keys berücksichtigt werden.

## Automatisches Liquid Clustering aktivieren oder deaktivieren

Eine Tabelle mit automatischem Liquid Clustering erstellen:

```sql
%sql
CREATE OR REPLACE TABLE table1 (column01 int, column02 string) CLUSTER BY AUTO;
```

Automatisches Liquid Clustering auf einer bestehenden Tabelle aktivieren, auch bei Tabellen mit manuell festgelegten Keys:

```sql
%sql
ALTER TABLE table1 CLUSTER BY AUTO;
```

Initiale Hinweise für die Key-Auswahl setzen und danach automatisches Clustering aktivieren:

```sql
%sql
ALTER TABLE table1 CLUSTER BY (c1, c2);
ALTER TABLE table1 CLUSTER BY AUTO;
```

Automatisches Liquid Clustering deaktivieren:

```sql
%sql
ALTER TABLE table1 CLUSTER BY NONE;
```

Deaktivieren und gleichzeitig Clustering-Spalten festlegen:

```sql
%sql
ALTER TABLE table1 CLUSTER BY (column01, column02);
```

Führen Sie bei einer Tabelle mit aktiviertem automatischem Clustering `CREATE OR REPLACE table_name` ohne `CLUSTER BY AUTO` aus, wird automatisches Clustering deaktiviert und die Clustering-Spalten gehen verloren. Um automatisches Liquid Clustering samt bisher gewählter Spalten zu erhalten, geben Sie `CLUSTER BY AUTO` auch im Replace-Befehl an.

Die Python-API ist ab Databricks Runtime 16.4 verfügbar und nur beim Erstellen oder Ersetzen einer Tabelle nutzbar. Für Änderungen des `clusterByAuto`-Status auf einer bestehenden Tabelle verwenden Sie SQL.

Eine Tabelle mit automatischem Liquid Clustering über DataFrameWriter erstellen:

```python
df = spark.read.table("table1")
df.write \
    .format("delta") \
    .option("clusterByAuto", "true") \
    .saveAsTable(...)
```

Initiale Hinweise für die Key-Auswahl mit `DataFrameWriter` setzen:

```python
df.write \
    .format("delta") \
    .clusterBy("clusteringColumn1", "clusteringColumn2") \
    .option("clusterByAuto", "true") \
    .saveAsTable(...)
```

Eine Tabelle mit automatischem Liquid Clustering über `DataFrameWriterV2` erstellen:

```python
df.writeTo(...).using("delta") \
    .option("clusterByAuto", "true") \
    .create()
```

Initiale Hinweise für die Key-Auswahl mit `DataFrameWriterV2`:

```python
df.writeTo(...).using("delta") \
    .clusterBy("clusteringColumn1", "clusteringColumn2") \
    .option("clusterByAuto", "true") \
    .create()
```

Eine Streaming Table mit automatischem Liquid Clustering erstellen:

```python
spark.readStream.table("source_table") \
    .writeStream \
    .option("clusterByAuto", "true") \
    .option("checkpointLocation", checkpointPath) \
    .toTable("target_table")
```

Initiale Hinweise für die Key-Auswahl bei einer Streaming Table setzen:

```python
spark.readStream.table("source_table") \
    .writeStream \
    .clusterBy("column1", "column2") \
    .option("clusterByAuto", "true") \
    .option("checkpointLocation", checkpointPath) \
    .toTable("target_table")
```

Verwenden Sie `.clusterBy` zusammen mit `.option('clusterByAuto', 'true')`, gilt Folgendes: Wird automatisches Liquid Clustering dadurch zum ersten Mal aktiviert, werden die Clustering-Spalten auf die in `.clusterBy` angegebenen Spalten gesetzt. Ist automatisches Liquid Clustering bei einer bestehenden Tabelle bereits aktiv, wird ein `.clusterBy`-Hinweis nur einmal akzeptiert. Das heißt, die Spalten aus `.clusterBy` werden nur gesetzt, wenn die Tabelle noch keine Clustering-Spalten hat.

**Wichtig:** Bei DataFrame-APIs kann die Option `clusterByAuto` nur im `overwrite`-Modus gesetzt werden, nicht im `append`-Modus. Das entspricht der Regel beim manuellen Setzen von Clustering-Spalten. Um den `clusterByAuto`-Status bei einer bestehenden Tabelle während des Anfügens (append) von Daten zu ändern, nutzen Sie separate SQL-`ALTER TABLE`-Befehle.

## Prüfen, ob automatisches Clustering aktiv ist

Nutzen Sie `DESCRIBE TABLE` oder `SHOW TBLPROPERTIES`. Ist automatisches Liquid Clustering aktiv, steht die Eigenschaft `clusterByAuto` auf `true`. Die Eigenschaft `clusteringColumns` zeigt die aktuellen, automatisch oder manuell gewählten Clustering-Spalten.

## Einschränkungen

Automatisches Liquid Clustering steht für Managed-Apache-Iceberg-v2-Tabellen nicht zur Verfügung. Für Managed-Apache-Iceberg-v3-Tabellen wird es ab Databricks Runtime 18.0 unterstützt.

## Daten in eine geclusterte Tabelle schreiben

Um in eine geclusterte Delta-Lake-Tabelle zu schreiben, benötigen Sie einen Delta-Writer-Client, der alle vom Liquid Clustering genutzten Delta-Write-Protokoll-Funktionen unterstützt. Für geclusterte Iceberg-Tabellen können Sie die Iceberg-REST-Catalog-API von Unity Catalog nutzen. Auf Databricks benötigen Sie mindestens Databricks Runtime 13.3 LTS.

## Operationen, die Clustering beim Schreiben unterstützen

- `INSERT INTO`-Operationen
- `CTAS`- und `RTAS`-Anweisungen
- `COPY INTO` aus dem Parquet-Format
- `spark.write.mode("append")`

## Größenschwellen für Clustering beim Schreiben

Clustering beim Schreiben wird nur ausgelöst, wenn die Daten in der Transaktion eine bestimmte Größenschwelle erreichen. Diese Schwellen hängen von der Anzahl der Clustering-Spalten ab und sind bei Unity-Catalog-Managed-Tables niedriger als bei anderen Delta-Lake-Tabellen.

| Anzahl Clustering-Spalten | Schwelle für Unity-Catalog-Managed-Tables | Schwelle für andere Delta-Lake-Tabellen |
| --- | --- | --- |
| 1 | 64 MB | 256 MB |
| 2 | 256 MB | 1 GB |
| 3 | 512 MB | 2 GB |
| 4 | 1 GB | 4 GB |

Da nicht alle Operationen Liquid Clustering direkt anwenden, empfiehlt Databricks, regelmäßig `OPTIMIZE` auszuführen.

## Streaming-Workloads

Structured-Streaming-Workloads unterstützen Clustering beim Schreiben, wenn Sie die Spark-Konfiguration `spark.databricks.delta.liquid.eagerClustering.streaming.enabled` auf `true` setzen. Bei solchen Workloads löst Clustering nur aus, wenn mindestens eines der letzten fünf Streaming-Updates die Größenschwelle aus obiger Tabelle überschreitet.

## Clustering auslösen

Predictive Optimization führt für aktivierte Tabellen automatisch `OPTIMIZE`-Befehle aus. Bei aktivierter Predictive Optimization empfiehlt Databricks, geplante `OPTIMIZE`-Jobs zu deaktivieren.

Um Clustering manuell auszulösen, benötigen Sie Databricks Runtime 13.3 LTS oder höher. Für schnellere `OPTIMIZE`-Performance bei großen Tabellen empfiehlt Databricks Runtime 17.3 LTS oder höher. Nutzen Sie den `OPTIMIZE`-Befehl:

```sql
%sql
OPTIMIZE table_name;
```

Liquid Clustering arbeitet **inkrementell**: `OPTIMIZE` schreibt nur die Daten neu, die tatsächlich noch geclustert werden müssen. Dateien, deren Clustering-Keys bereits zu den geclusterten Daten passen, werden nicht neu geschrieben.

Ohne Predictive Optimization empfiehlt Databricks, regelmäßige `OPTIMIZE`-Jobs zu planen. Bei Tabellen mit vielen Updates oder Inserts empfiehlt Databricks, `OPTIMIZE` alle ein bis zwei Stunden auszuführen. Da Liquid Clustering inkrementell arbeitet, laufen die meisten `OPTIMIZE`-Jobs für geclusterte Tabellen schnell.

## Erneutes Clustering erzwingen

Ab Databricks Runtime 16.4 LTS können Sie ein erneutes Clustering aller Datensätze mit folgender Syntax erzwingen:

```sql
%sql
OPTIMIZE table_name FULL;
```

**Wichtig:** `OPTIMIZE FULL` clustert alle vorhandenen Daten neu, soweit nötig. Bei großen Tabellen, die bisher noch nicht nach den festgelegten Keys geclustert wurden, kann das mehrere Stunden dauern.

Führen Sie `OPTIMIZE FULL` aus, wenn Sie Clustering erstmals aktivieren oder die Clustering-Keys ändern. Haben Sie zuvor bereits `OPTIMIZE FULL` ausgeführt und die Keys nicht geändert, verhält sich `OPTIMIZE FULL` wie ein normales `OPTIMIZE`: inkrementell, es werden nur noch nicht komprimierte Dateien neu geschrieben. Nutzen Sie `OPTIMIZE FULL` stets, um sicherzustellen, dass das Datenlayout die aktuellen Clustering-Keys widerspiegelt.

## Teilweises Reclustering

Ab Databricks Runtime 18.1 können Sie ein erzwungenes Reclustering für eine Teilmenge der Datensätze mit `OPTIMIZE FULL WHERE <predicate>` durchführen. Eine Datei wird einbezogen, wenn ihr Wertebereich mit dem Prädikat überlappt.

```sql
%sql
OPTIMIZE events FULL WHERE event_date >= '2025-01-01';
```

## Daten aus einer geclusterten Tabelle lesen

Sie können Daten in einer geclusterten Delta-Lake-Tabelle mit jedem Delta-Lake-Client lesen, der Deletion Vectors unterstützt. Für geclusterte Iceberg-Tabellen nutzen Sie die Iceberg-REST-Catalog-API. Liquid Clustering verbessert die Abfrageperformance durch automatisches Data Skipping bei Filterung auf Clustering-Keys.

```sql
%sql
SELECT * FROM table_name WHERE cluster_key_column_name = "some_value";
```

## Clustering-Keys verwalten

### Clustering einer Tabelle anzeigen

```sql
%sql
DESCRIBE TABLE table_name;
DESCRIBE DETAIL table_name;
```

### Clustering-Keys ändern

```sql
%sql
ALTER TABLE table_name CLUSTER BY (new_column1, new_column2);
```

Nach dem Ändern der Clustering-Keys nutzen nachfolgende `OPTIMIZE`- und Schreiboperationen den neuen Ansatz. Bestehende Daten werden dabei nicht neu geschrieben. Um bestehende Daten mit den neuen Keys neu zu schreiben, nutzen Sie erneutes Clustering (siehe oben).

Clustering vollständig deaktivieren:

```sql
%sql
ALTER TABLE table_name CLUSTER BY NONE;
```

Das Setzen auf `NONE` schreibt bereits geclusterte Daten nicht neu, verhindert aber, dass zukünftige `OPTIMIZE`-Operationen die Clustering-Keys nutzen.

## Liquid Clustering über eine externe Engine nutzen

Sie können Liquid Clustering auf Managed-Iceberg-Tabellen auch über externe Iceberg-Engines aktivieren. Geben Sie dazu beim Erstellen der Tabelle Partitionsspalten an. Unity Catalog interpretiert diese Partitionen als Clustering-Keys. Beispiel mit Open-Source-Spark:

```sql
%sql
CREATE OR REPLACE TABLE main.schema.icebergTable
PARTITIONED BY c1;
```

Liquid Clustering deaktivieren:

```sql
%sql
ALTER TABLE main.schema.icebergTable DROP PARTITION FIELD c2;
```

Clustering-Keys über Iceberg Partition Evolution ändern:

```sql
%sql
ALTER TABLE main.schema.icebergTable ADD PARTITION FIELD c2;
```

Geben Sie eine Partition mit Bucket-Transformation an, verwirft Unity Catalog den Ausdruck und nutzt die Spalte als Clustering-Key:

```sql
%sql
CREATE OR REPLACE TABLE main.schema.icebergTable
PARTITIONED BY (bucket(c1, 10));
```

## Kompatibilität von Tabellen mit Liquid Clustering

Liquid Clustering nutzt Delta-Lake-Tabellenfunktionen, die bestimmte Databricks-Runtime-Versionen für Lesen und Schreiben voraussetzen. Tabellen mit Liquid Clustering, die in Databricks Runtime 14.3 LTS oder höher erstellt wurden, nutzen standardmäßig Checkpoint V2. Sie können Tabellen mit Checkpoint V2 ab Databricks Runtime 13.3 LTS lesen und schreiben.

Um Leser mit Databricks Runtime 12.2 LTS bis 13.2 zu unterstützen, deaktivieren Sie Checkpoint V2 und stufen das Tabellenprotokoll herab.

## Standard-Funktionsaktivierung überschreiben (optional)

Sie können die Standardaktivierung von Delta-Lake-Tabellenfunktionen bei der Aktivierung von Liquid Clustering überschreiben. Das verhindert Upgrades der Reader- und Writer-Protokolle, die mit diesen Funktionen verbunden sind. Dafür muss bereits eine bestehende Tabelle vorhanden sein.

1. Setzen Sie mit `ALTER TABLE` die Tabelleneigenschaft, die eine oder mehrere Funktionen deaktiviert. Um zum Beispiel Deletion Vectors zu deaktivieren:

```sql
%sql
ALTER TABLE table_name SET TBLPROPERTIES ('delta.enableDeletionVectors' = false);
```

2. Aktivieren Sie Liquid Clustering auf der Tabelle:

```sql
%sql
ALTER TABLE <table_name>
CLUSTER BY (<clustering_columns>)
```

Folgende Tabelle zeigt, welche Delta-Funktionen sich überschreiben lassen und wie sich das auf die Kompatibilität mit Databricks-Runtime-Versionen auswirkt:

| Delta-Funktion | Runtime-Kompatibilität | Eigenschaft zum Überschreiben | Auswirkung auf Liquid Clustering bei Deaktivierung |
| --- | --- | --- | --- |
| Deletion Vectors | Lesen und Schreiben benötigen Runtime 12.2 LTS oder höher | `'delta.enableDeletionVectors' = false` | Deaktiviert auch zeilenweise Nebenläufigkeit. Transaktionen und Clustering-Operationen geraten eher in Konflikt. `DELETE`, `MERGE` und `UPDATE` können langsamer laufen. |
| Row Tracking | Schreiben benötigt Runtime 13.3 LTS oder höher. Lesen ist mit jeder Version möglich. | `'delta.enableRowTracking' = false` | Deaktiviert ebenfalls zeilenweise Nebenläufigkeit, mit denselben Konfliktrisiken. |
| Checkpoint V2 | Lesen und Schreiben benötigen Runtime 13.3 LTS oder höher | `'delta.checkpointPolicy' = 'classic'` | Kein Effekt auf das Verhalten von Liquid Clustering. |

## Einschränkungen

- **Databricks Runtime 15.1 und darunter:** Clustering beim Schreiben unterstützt keine Quellabfragen mit Filtern, Joins oder Aggregationen.
- **Databricks Runtime 15.4 LTS und darunter:** Sie können keine Tabelle mit aktiviertem Liquid Clustering über einen Structured-Streaming-Write erstellen. Structured Streaming kann aber in eine bestehende Tabelle mit Liquid Clustering schreiben.
- **Apache Iceberg v2:** Zeilenweise Nebenläufigkeit wird für Managed-Apache-Iceberg-v2-Tabellen nicht unterstützt, da Deletion Vectors und Row Tracking dort fehlen. Bei Managed-Apache-Iceberg-v3-Tabellen wird zeilenweise Nebenläufigkeit unterstützt, da die v3-Spezifikation Deletion Vectors und Row Tracking unterstützt.

