# Unity Catalog in Lakeflow Declarative Pipelines

Dieses Dokument beschreibt die Verwendung von Unity Catalog mit Lakeflow Declarative Pipelines (LDP): Voraussetzungen, Einschränkungen, das Zusammenspiel mit dem Hive Metastore, den Umgang mit inaktiven Tabellen, das Schreiben und Lesen von Daten sowie Berechtigungsverwaltung, Lineage und Row Filter/Column Masks.

## Abschnittsübersicht

1. [Grundlagen](#grundlagen)
2. [Voraussetzungen](#voraussetzungen)
3. [Einschränkungen](#einschraenkungen)
4. [Hive Metastore und Unity Catalog gemeinsam nutzen](#hms-und-uc)
5. [Inaktive Tabellen](#inaktive-tabellen)
6. [Tabellen nach Unity Catalog schreiben](#schreiben)
7. [Daten in eine Unity-Catalog-Pipeline einlesen](#einlesen)
8. [Materialized Views freigeben (GRANT/REVOKE)](#freigeben)
9. [Lineage anzeigen](#lineage)
10. [DML an Streaming Tables](#dml)
11. [Row Filter und Column Masks](#row-filter-column-mask)

---

## <a id="grundlagen">1. Grundlagen</a>

Databricks empfiehlt, Lakeflow-Pipelines mit Unity Catalog zu konfigurieren. Unity Catalog ist die Standardeinstellung für neu erstellte Pipelines. Mit Unity Catalog konfigurierte Pipelines veröffentlichen alle definierten Materialized Views und Streaming Tables im festgelegten Katalog und Schema. Unity-Catalog-Pipelines können aus anderen Unity-Catalog-Tabellen und -Volumes lesen. Zur Verwaltung von Berechtigungen auf den durch eine Unity-Catalog-Pipeline erzeugten Tabellen dienen `GRANT`- und `REVOKE`-Anweisungen.

**Hinweis zur Abgrenzung:** Dieses Dokument beschreibt die Funktionsweise des aktuellen **Default Publishing Mode**. Pipelines, die vor dem 5. Februar 2025 erstellt wurden, verwenden möglicherweise noch den Legacy Publishing Mode mit dem `LIVE`-Virtual-Schema (siehe `Live Schema.md`).

---

## <a id="voraussetzungen">2. Voraussetzungen</a>

### Erforderliche Berechtigungen

Um Streaming Tables und Materialized Views in einem Zielschema in Unity Catalog zu erstellen, sind folgende Berechtigungen auf Schema und übergeordnetem Katalog erforderlich:

- `USE CATALOG`-Berechtigung auf dem Zielkatalog.
- `CREATE MATERIALIZED VIEW`- und `USE SCHEMA`-Berechtigung auf dem Zielschema, falls die Pipeline Materialized Views erstellt.
- `CREATE TABLE`- und `USE SCHEMA`-Berechtigung auf dem Zielschema, falls die Pipeline Streaming Tables erstellt.
- `USE CATALOG`- und `CREATE SCHEMA`-Berechtigung auf dem Zielkatalog, falls die Pipeline neue Schemas erstellt.

### Compute-Anforderungen zum Ausführen einer Unity-Catalog-Pipeline

Die Compute-Ressource muss im Standard Access Mode konfiguriert sein — Dedicated Compute wird nicht unterstützt.

### Compute-Anforderungen zum Abfragen der erzeugten Tabellen

Um Tabellen abzufragen, die von Unity-Catalog-Pipelines erzeugt wurden (Streaming Tables und Materialized Views), ist eine der folgenden Optionen nötig:

- SQL Warehouses.
- Standard-Access-Mode-Compute auf Databricks Runtime 13.3 LTS oder höher.
- Dedicated-Access-Mode-Compute, sofern Fine-Grained Access Control auf dem Dedicated Compute aktiviert ist (d. h. Databricks Runtime 15.4 oder höher und Serverless Compute im Workspace aktiviert).
- Dedicated-Access-Mode-Compute auf 13.3 LTS bis 15.3, ausschließlich wenn der Tabelleneigentümer die Abfrage ausführt.

---

## <a id="einschraenkungen">3. Einschränkungen</a>

- Standardmäßig können nur der Pipeline-Owner und Workspace-Administratoren die Driver-Logs der Compute einsehen, die eine Unity-Catalog-Pipeline ausführt.
- Bestehende Pipelines, die den Hive Metastore verwenden, können **nicht** auf Unity Catalog aktualisiert werden. Um eine bestehende Hive-Metastore-Pipeline zu migrieren, muss eine neue Pipeline erstellt und die Daten aus der/den Datenquelle(n) neu eingelesen werden (siehe `HMS zu UC klonen.md` für den unterstützten Klon-Weg).
- Eine Unity-Catalog-Pipeline kann nicht in einem Workspace erstellt werden, der an einen Metastore angebunden ist, der während der Unity-Catalog-Public-Preview erstellt wurde.
- JAR-Dateien werden nicht unterstützt; nur Python-Bibliotheken von Drittanbietern sind unterstützt.
- DML-Abfragen (Data Manipulation Language), die das Schema einer Streaming Table ändern, werden nicht unterstützt.
- Eine in einer Pipeline erstellte Materialized View kann außerhalb dieser Pipeline nicht als Streaming-Quelle verwendet werden (z. B. nicht in einer anderen Pipeline oder einem nachgelagerten Notebook).
- Daten für Materialized Views und Streaming Tables werden am Speicherort des enthaltenden Schemas abgelegt. Ist kein Schema-Speicherort angegeben, werden die Tabellen im Katalog-Speicherort abgelegt. Sind weder Schema- noch Katalog-Speicherort angegeben, werden die Tabellen im Root-Speicherort des Metastore abgelegt.
- Der **History**-Tab im Catalog Explorer zeigt keine Historie für Materialized Views.
- Die `LOCATION`-Property wird bei der Tabellendefinition nicht unterstützt.
- Unity-Catalog-Pipelines können nicht in den Hive Metastore veröffentlichen.
- Globale Init-Skripte werden nicht unterstützt. Databricks empfiehlt, die pipeline-eigenen **Environment**-Einstellungen zur Installation von Abhängigkeiten zu nutzen. Auf klassischem Compute können Cluster-scoped Init-Skripte verwendet werden, Databricks empfiehlt aber die Environment-Einstellungen. Serverless-Pipelines unterstützen keine Init-Skripte.
- Die Unterstützung für Python-UDFs befindet sich in der Public Preview.

### Hinweis zu personenbezogenen Daten in Materialized-View-Speicherdateien

Die zugrunde liegenden Dateien, die eine Materialized View stützen, können Daten aus vorgelagerten Tabellen (einschließlich möglicher personenbezogener Daten) enthalten, die in der Materialized-View-Definition selbst nicht sichtbar sind — diese Daten werden automatisch zum zugrunde liegenden Speicher hinzugefügt, um das inkrementelle Refreshing von Materialized Views zu unterstützen. Databricks empfiehlt daher, den zugrunde liegenden Speicher nicht mit nicht vertrauenswürdigen nachgelagerten Konsumenten zu teilen. Beispiel: Enthält eine Materialized-View-Definition eine `COUNT(DISTINCT field_a)`-Klausel, enthalten die zugrunde liegenden Dateien trotzdem eine Liste aller tatsächlichen Werte von `field_a`. Die View-Definition selbst zeigt nur das Aggregat.

---

## <a id="hms-und-uc">4. Hive Metastore und Unity Catalog gemeinsam nutzen</a>

Ein Workspace kann sowohl Pipelines mit Unity Catalog als auch mit dem Legacy Hive Metastore enthalten. Eine einzelne Pipeline kann jedoch **nicht** gleichzeitig in den Hive Metastore und nach Unity Catalog schreiben. Bestehende Pipelines, die in den Hive Metastore schreiben, können nicht auf Unity Catalog aktualisiert werden — dafür ist eine neue Pipeline mit erneutem Einlesen der Quelldaten nötig.

Bestehende Pipelines ohne Unity Catalog sind von der Erstellung neuer Unity-Catalog-Pipelines nicht betroffen; sie persistieren Daten weiterhin im konfigurierten Speicherort des Hive Metastore. Sofern nicht anders angegeben, werden bei Unity-Catalog-Pipelines alle bestehenden Datenquellen und Pipeline-Funktionalitäten unterstützt; sowohl das Python- als auch das SQL-Interface werden unterstützt.

---

## <a id="inaktive-tabellen">5. Inaktive Tabellen</a>

Ist eine Pipeline so konfiguriert, dass sie Daten nach Unity Catalog persistiert, verwaltet die Pipeline den Lebenszyklus und die Berechtigungen der Tabelle.

**Ursachen für Inaktivität:** Tabellen werden inaktiv, wenn ihre Definition aus einer Pipeline entfernt wird — das nächste Pipeline-Update markiert den entsprechenden Materialized-View- oder Streaming-Table-Eintrag als inaktiv. Wird der Standardkatalog oder das Standardschema der Pipeline geändert, ohne dass im Pipeline-Quellcode vollständig qualifizierte Tabellennamen verwendet werden, erstellt der nächste Pipeline-Lauf die Materialized View bzw. Streaming Table im neuen Katalog/Schema, während die vorherige Tabelle am alten Ort als inaktiv markiert wird.

**Umgang mit inaktiven Tabellen:** Inaktive Tabellen bleiben abfragbar, werden aber nicht mehr durch die Pipeline aktualisiert. Zum Aufräumen muss die Tabelle explizit per `DROP` entfernt werden. Wird die gesamte Pipeline gelöscht (statt nur eine Tabellendefinition zu entfernen), werden auch alle in dieser Pipeline definierten Tabellen gelöscht; die UI fordert dafür eine Bestätigung an.

- Gelöschte Tabellen lassen sich innerhalb von **7 Tagen** per `UNDROP`-Befehl wiederherstellen.
- Um das Legacy-Verhalten beizubehalten, bei dem der Materialized-View- bzw. Streaming-Table-Eintrag beim nächsten Pipeline-Update aus Unity Catalog entfernt wird, kann die Pipeline-Konfiguration `"pipelines.dropInactiveTables": "true"` gesetzt werden. Die tatsächlichen Daten werden dabei ebenfalls für einen Zeitraum (7 Tage) aufbewahrt, sodass sie bei versehentlichem Löschen wiederhergestellt werden können — durch erneutes Hinzufügen der Materialized View bzw. Streaming Table zur Pipeline-Definition.

### Pipeline löschen

Beim Löschen einer Unity-Catalog-Pipeline werden auch die zugehörigen Materialized Views, Streaming Tables und Views gelöscht. Um eine Pipeline zu löschen und ihre Tabellen zu behalten, dient das `cascade`-Feld der API. Die dabei erhaltenen Tabellen sind inaktiv, aber weiterhin abfragbar. Inaktive Tabellen können in eine neue Pipeline verschoben werden; sind sie dort an einen Flow angebunden, werden sie reaktiviert (siehe `Tabellen verschieben.md`).

```
DELETE /api/2.0/pipelines/{pipeline_id}?cascade=false
```

---

## <a id="schreiben">6. Tabellen nach Unity Catalog schreiben</a>

Beim Erstellen einer Pipeline wird unter **Storage options** die Option **Unity Catalog** ausgewählt, ein Katalog im **Catalog**-Dropdown gewählt und im **Target schema**-Dropdown ein bestehendes Schema ausgewählt oder ein neuer Schema-Name eingegeben.

**Hinweis:** Beim Veröffentlichen einer Pipeline nach Unity Catalog speichert Databricks einen Teil der Backing-Daten im reservierten Katalog `__databricks_internal` — das ist erwartetes Verhalten.

---

## <a id="einlesen">7. Daten in eine Unity-Catalog-Pipeline einlesen</a>

Eine für Unity Catalog konfigurierte Pipeline kann Daten aus folgenden Quellen lesen:

- Unity-Catalog-Managed- und -External-Tables, Views, Materialized Views und Streaming Tables.
- Hive-Metastore-Tabellen und -Views.
- Auto Loader über die Funktion `read_files()` zum Lesen aus Unity-Catalog-External-Locations.
- Apache Kafka und Amazon Kinesis.

### Batch-Ingestion aus einer Unity-Catalog-Tabelle

```sql
CREATE OR REFRESH MATERIALIZED VIEW
  table_name
AS SELECT
  *
FROM
  my_catalog.my_schema.table1;
```

```python
@dp.materialized_view
def table_name():
  return spark.read.table("my_catalog.my_schema.table")
```

### Änderungen aus einer Unity-Catalog-Tabelle streamen

```sql
CREATE OR REFRESH STREAMING TABLE
  table_name
AS SELECT
  *
FROM
  STREAM(my_catalog.my_schema.table1);
```

```python
@dp.table
def table_name():
  return spark.readStream.table("my_catalog.my_schema.table")
```

### Daten aus dem Hive Metastore einlesen

Eine Unity-Catalog-Pipeline kann über den Katalog `hive_metastore` Daten aus Hive-Metastore-Tabellen lesen:

```sql
CREATE OR REFRESH MATERIALIZED VIEW
  table_name
AS SELECT
  *
FROM
  <hms_federation_catalog>.some_schema.table;
```

```python
@dp.materialized_view
def table3():
  return spark.read.table("<hms_federation_catalog>.some_schema.table")
```

### Daten via Auto Loader einlesen

```sql
CREATE OR REFRESH STREAMING TABLE table_name
AS SELECT *
FROM STREAM read_files(
  "/path/to/uc/external/location",
  format => "json"
)
```

```python
@dp.table(table_properties={"quality": "bronze"})
def table_name():
  return (
     spark.readStream.format("cloudFiles")
     .option("cloudFiles.format", "json")
     .load(f"{path_to_uc_external_location}")
 )
```

---

## <a id="freigeben">8. Materialized Views freigeben (GRANT/REVOKE)</a>

Standardmäßig darf nur der Pipeline-Owner die von der Pipeline erzeugten Datasets abfragen. Anderen Nutzern lässt sich Leserecht über `GRANT`-Anweisungen erteilen, per `REVOKE` wieder entziehen.

### SELECT auf eine Tabelle gewähren

```sql
GRANT SELECT ON TABLE
  my_catalog.my_schema.table_name
TO
  `user@databricks.com`
```

### SELECT auf eine Tabelle entziehen

```sql
REVOKE SELECT ON TABLE
  my_catalog.my_schema.table_name
FROM
  `user@databricks.com`
```

### CREATE-TABLE- bzw. CREATE-MATERIALIZED-VIEW-Rechte gewähren

```sql
GRANT CREATE { MATERIALIZED VIEW | TABLE } ON SCHEMA
  my_catalog.my_schema
TO
  { principal | user }
```

---

## <a id="lineage">9. Lineage anzeigen</a>

Die Lineage von in Pipelines definierten Tabellen ist im Catalog Explorer sichtbar. Die Lineage-UI im Catalog Explorer zeigt die vor- und nachgelagerten Tabellen für Materialized Views bzw. Streaming Tables einer Unity-Catalog-Pipeline. Für eine Materialized View oder Streaming Table einer Unity-Catalog-Pipeline verlinkt die Lineage-UI zusätzlich zur produzierenden Pipeline, sofern diese vom aktuellen Workspace aus zugänglich ist.

---

## <a id="dml">10. DML an Streaming Tables</a>

DML-Anweisungen (`INSERT`, `UPDATE`, `DELETE`, `MERGE`) können genutzt werden, um Streaming Tables zu ändern, die nach Unity Catalog veröffentlicht wurden — das ermöglicht z. B. DSGVO-konforme Anpassungen von Tabellen.

**Wichtige Regeln:**

- DML-Anweisungen, die das Tabellenschema einer Streaming Table ändern, werden nicht unterstützt.
- DML-Änderungen an einer Streaming Table können nur auf einem Shared-Unity-Catalog-Cluster oder einem SQL-Warehouse mit Databricks Runtime 13.3 LTS oder höher ausgeführt werden.
- Da Streaming append-only Datenquellen voraussetzt: Muss aus einer Quell-Streaming-Table mit Änderungen (z. B. durch DML) gestreamt werden, ist beim Lesen der Quelle die Option `skipChangeCommits` zu setzen — dann werden Transaktionen, die Datensätze löschen oder ändern, ignoriert. Ist keine Streaming Table erforderlich, kann stattdessen eine Materialized View (ohne Append-only-Einschränkung) als Zieltabelle verwendet werden.

### Beispiele

```sql
-- Datensätze mit bestimmter ID löschen
DELETE FROM my_streaming_table WHERE id = 123;
```

```sql
-- Datensätze mit bestimmter ID aktualisieren
UPDATE my_streaming_table SET name = 'Jane Doe' WHERE id = 123;
```

---

## <a id="row-filter-column-mask">11. Row Filter und Column Masks</a>

**Row Filter** erlauben, eine Funktion anzugeben, die als Filter angewendet wird, sobald ein Tabellen-Scan Zeilen abruft — nachfolgende Abfragen liefern dann nur Zeilen, für die das Filterprädikat `true` ergibt.

**Column Masks** erlauben, die Werte einer Spalte zu maskieren, sobald ein Tabellen-Scan Zeilen abruft — nachfolgende Abfragen dieser Spalte erhalten das Ergebnis der ausgewerteten Funktion statt des Originalwerts.

### Verwaltung

Row Filter und Column Masks auf Materialized Views und Streaming Tables sollten über die `CREATE OR REFRESH`-Anweisung hinzugefügt, geändert oder entfernt werden.

### Verhalten

- **Refresh als Owner:** Beim Aktualisieren einer Materialized View oder Streaming Table durch ein Pipeline-Update laufen Row-Filter- und Column-Mask-Funktionen mit den Rechten des Pipeline-Owners — der Tabellen-Refresh nutzt also den Sicherheitskontext des Nutzers, der die Pipeline erstellt hat. Funktionen, die den Nutzerkontext prüfen (z. B. `CURRENT_USER`, `IS_MEMBER`), werden dabei im Kontext des Pipeline-Owners ausgewertet.
- **Abfrage:** Beim Abfragen einer Materialized View oder Streaming Table werden Funktionen, die den Nutzerkontext prüfen (`CURRENT_USER`, `IS_MEMBER`), im Kontext des abfragenden Nutzers ausgewertet — das setzt nutzerspezifische Datensicherheit und Zugriffskontrollen basierend auf dem aktuellen Nutzerkontext durch.
- Werden Materialized Views über Quelltabellen erstellt, die Row Filter und Column Masks enthalten, ist der Refresh der Materialized View **immer ein Full Refresh**. Ein Full Refresh verarbeitet alle in der Quelle verfügbaren Daten neu und stellt sicher, dass Sicherheitsrichtlinien der Quelltabellen mit den aktuellsten Daten und Definitionen ausgewertet und angewendet werden.

### Audit

`DESCRIBE EXTENDED`, `INFORMATION_SCHEMA` oder der Catalog Explorer dienen dazu, bestehende Row Filter und Column Masks auf einer gegebenen Materialized View oder Streaming Table zu prüfen.
