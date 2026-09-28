# Standalone Streaming Tables (Databricks SQL)

Dieses Dokument beschreibt Streaming Tables, die **außerhalb einer Lakeflow-Pipeline** über Databricks SQL bzw. Notebooks erstellt und betrieben werden.

## Abschnittsübersicht

1. [Grundkonzept](#grundkonzept)
2. [Voraussetzungen](#voraussetzungen)
3. [Erstellung und Refresh](#erstellung)
4. [Compute für den Refresh](#compute)
5. [Auto Loader über `read_files`](#auto-loader)
6. [Ingestion aus anderen Quellen (Kafka)](#andere-quellen)
7. [Change Data Capture mit `AUTO CDC`](#cdc)
8. [Selektive Batch-Ersetzung: `REPLACE WHERE`-Flows](#replace-where)
9. [Partielle Snapshot-Ersetzung: `REPLACE USING`-Flows (Beta)](#replace-using)
10. [Nur neue Daten aufnehmen](#neue-daten)
11. [Runtime-Version](#runtime-version)
12. [Sensible Daten verbergen](#sensible-daten)
13. [Refresh: manuell, vollständig, Funktionsweise](#refresh)
14. [Refreshes planen und überwachen](#planen)
15. [Zugriffskontrolle](#zugriff)
16. [Datensätze dauerhaft löschen (`REORG … PURGE`)](#loeschen)
17. [Runs über die Query History überwachen](#query-history)
18. [Zugriff über externe Clients (Compatibility Mode)](#external-clients)
19. [Weitere Ressourcen](#weitere-ressourcen)
20. [Quellen](#quellen)

---

## <a id="grundkonzept">1. Grundkonzept</a>

Eine Standalone Streaming Table ist eine *"table registered to Unity Catalog with extra support for streaming or incremental data processing, defined outside of a Lakeflow pipeline"*. Für jede Streaming Table erstellt das System **automatisch eine zugehörige (Serverless-)Pipeline** für die Verarbeitung. Der Ersteller wird zum Owner.

Bei der Erstellung befüllt zunächst der bereits vorhandene Quelldatenbestand die Tabelle; nachfolgende Refreshes hängen nur neue Daten an ("append"). (Eine frühere Doku-Fassung nannte für den Betrieb auf systemverwalteten Serverless-Pipelines Databricks Runtime 18.2.)

## <a id="voraussetzungen">2. Voraussetzungen</a>

> *"For compute options, permissions, and other requirements for creating, refreshing, and querying standalone streaming tables, see Requirements for standalone pipelines."* (`/aws/en/ldp/dbsql/compute`)

Erstellung und Refresh laufen über **SQL-Warehouses** oder **Serverless General Compute**.

## <a id="erstellung">3. Erstellung und Refresh</a>

Streaming Tables werden über SQL-Abfragen definiert. Die Basissyntax verwendet `CREATE OR REFRESH STREAMING TABLE` zusammen mit dem Schlüsselwort `STREAM`, um Streaming-Semantik für die Quelle zu aktivieren. Refreshes verarbeiten nur neue Zeilen seit dem letzten Update und hängen diese an.

```sql
CREATE OR REFRESH STREAMING TABLE sales
  SCHEDULE EVERY 1 hour
  AS SELECT product, price FROM STREAM raw_data;
```

## <a id="compute">4. Compute für den Refresh</a>

> *"When you create a streaming table using the `CREATE OR REFRESH STREAMING TABLE` statement, the initial data refresh and population begin immediately. These operations do not consume Databricks SQL warehouse compute."*

Der initiale Refresh und die Erstbefüllung starten also **sofort** und verbrauchen **kein** SQL-Warehouse-Compute — sie laufen auf der automatisch erzeugten Serverless-Pipeline.

## <a id="auto-loader">5. Auto Loader über `read_files`</a>

Dateien lassen sich inkrementell aus Volumes oder Cloud-Speicher laden, über die `read_files`-Funktion (intern Auto Loader):

```sql
CREATE OR REFRESH STREAMING TABLE sales
  SCHEDULE EVERY 1 hour
  AS SELECT * FROM STREAM read_files(
    "/Volumes/my_catalog/my_schema/my_volume/path/to/data",
    format => "json"
  );
```

```sql
CREATE OR REFRESH STREAMING TABLE sales
  SCHEDULE EVERY 1 hour
  AS SELECT *
  FROM STREAM read_files(
  's3://mybucket/analysis/*/*/*.json',
    format => "json"
  );
```

## <a id="andere-quellen">6. Ingestion aus anderen Quellen (Kafka)</a>

> *"For example of ingestion from other sources, including Kafka, see Load data in pipelines."* (`/aws/en/ldp/load`)

Für Streaming-Ingestion aus Message-Brokern steht in Databricks SQL die tabellenwertige Funktion `read_kafka` zur Verfügung (siehe Abschnitt 19).

## <a id="cdc">7. Change Data Capture mit `AUTO CDC`</a>

Mit `FLOW AUTO CDC` lassen sich nicht-geordnet eintreffende Datensätze (out-of-order records) verarbeiten, wahlweise als SCD Type 1 (direkte Updates) oder SCD Type 2 (Historienverfolgung):

```sql
-- SCD Type 1
CREATE OR REFRESH STREAMING TABLE target
  FLOW AUTO CDC
  FROM stream(cdc_data.users)
  KEYS (userId)
  SEQUENCE BY sequenceNum
  STORED AS SCD TYPE 1;
```

```sql
-- SCD Type 2
CREATE OR REFRESH STREAMING TABLE target
  FLOW AUTO CDC
  FROM stream(cdc_data.users)
  KEYS (userId)
  APPLY AS DELETE WHEN operation = "DELETE"
  SEQUENCE BY sequenceNum
  COLUMNS * EXCEPT (operation, sequenceNum)
  STORED AS SCD TYPE 2;
```

## <a id="replace-where">8. Selektive Batch-Ersetzung: `REPLACE WHERE`-Flows</a>

> *"Use the `FLOW REPLACE WHERE` clause to recompute and overwrite a targeted subset of a streaming table without reprocessing your entire table history. `REPLACE WHERE` flows are well-suited for incremental batch processing of joins and aggregations, late-arriving data, upstream reprocessing, schema evolution, and backfills."*

`REPLACE WHERE`-Flows arbeiten **prädikatsbasiert**: Sie berechnen eine gezielte Teilmenge der Streaming Table neu und überschreiben sie, ohne die gesamte Tabellenhistorie erneut zu verarbeiten. Gut geeignet für inkrementelle Batch-Verarbeitung von Joins/Aggregationen, spät eintreffende Daten, Upstream-Reprocessing, Schema-Evolution und Backfills.

Vollständige Details (Anforderungen, Predicate Overrides, Incremental Refresh): *REPLACE WHERE flows for standalone streaming tables* (`/aws/en/ldp/dbsql/flows-replace-where`) bzw. Datei „Flows mit REPLACE WHERE (DBSQL).md".

## <a id="replace-using">9. Partielle Snapshot-Ersetzung: `REPLACE USING`-Flows (Beta)</a>

> **Beta:** `REPLACE USING`-Flows befinden sich derzeit in Beta.

`FLOW REPLACE USING` hält eine Streaming Table mit **partiellen Snapshot-Streams** synchron. Bei Updates werden die Zeilen ersetzt, die den angegebenen **Key-Spalten** entsprechen:

```sql
CREATE OR REFRESH STREAMING TABLE payments_current
FLOW REPLACE USING (payment_id) SEQUENCE BY payment_date BY NAME
SELECT payment_id, booking_id, status, payment_date
FROM STREAM(samples.wanderbricks.payments);
```

- Die Klausel **`BY NAME` ist verpflichtend** — Spalten werden nach Name statt nach Position abgeglichen.
- Gegenüber der Lakeflow-Pipeline-Variante unterscheidet sich `REPLACE USING` für Standalone Streaming Tables nur darin, **wie** es definiert wird (Inline-SQL) und dass das Compute automatisch auf systemverwalteten Serverless-Pipelines verwaltet wird.

**Abgrenzung:** `REPLACE USING` ist Snapshot-/Key-basiert, `REPLACE WHERE` (Abschnitt 8) ist Prädikat-basiert.

## <a id="neue-daten">10. Nur neue Daten aufnehmen</a>

Standardmäßig nimmt `read_files` bei der Erstellung **alle** vorhandenen Quelldaten auf und verarbeitet danach neue Dateien. Mit `includeExistingFiles => false` werden beim Erstanlauf bereits vorhandene Dateien übersprungen — es werden nur ab diesem Zeitpunkt neu eintreffende Dateien aufgenommen:

```sql
CREATE OR REFRESH STREAMING TABLE sales
  SCHEDULE EVERY 1 hour
  AS SELECT *
  FROM STREAM read_files(
    '/path/to/files',
    includeExistingFiles => false
  );
```

## <a id="runtime-version">11. Runtime-Version</a>

> *"Streaming tables always run on the latest Databricks SQL runtime version. The `pipelines.channel` property is no longer supported."*

**Wichtige Änderung:** Der früher verwendete Ansatz, über `TBLPROPERTIES ('pipelines.channel' = 'preview')` einen Runtime-Channel zu setzen, wird **nicht mehr unterstützt**. Standalone Streaming Tables laufen immer auf der aktuellsten Databricks-SQL-Runtime.

## <a id="sensible-daten">12. Sensible Daten verbergen</a>

Die Query-Definition kann sensible Spalten oder Zeilen ausschließen oder — abhängig von den Berechtigungen des zugreifenden Nutzers — **Column Masks** und **Row Filters** über `ROW FILTER`- und `MASK`-Syntax anwenden. Der Owner lässt sich über den Catalog Explorer ändern (siehe Abschnitt 15).

## <a id="refresh">13. Refresh: manuell, vollständig, Funktionsweise</a>

Streaming Tables nutzen für Refreshes automatisch erzeugte Serverless-Pipelines. Ein manueller Refresh kann jederzeit ausgelöst werden:

```sql
-- Manueller (inkrementeller) Refresh
REFRESH STREAMING TABLE sales;
```

Den Refresh-Status prüft man mit `DESCRIBE TABLE EXTENDED`.

### Wie ein Refresh funktioniert

> *"A streaming table refresh only evaluates new rows that have arrived after the last update, and appends only the new data."*

Änderungen an der Definition berechnen **bestehende** Daten **nicht** rückwirkend neu. Inkompatible Änderungen (z. B. Datentyp-Änderungen) führen zu Refresh-**Fehlern**. Beispiele für Auswirkungen von Definitionsänderungen:

- Das Entfernen von Filtern verarbeitet zuvor herausgefilterte Zeilen **nicht** nachträglich.
- Eine geänderte Spaltenprojektion wirkt sich **nicht** auf bereits verarbeitete Daten aus.
- Joins mit statischen Snapshots verwenden den Snapshot-Zustand zum Zeitpunkt der **ersten** Verarbeitung.
- Das Ändern von `CAST`-Operationen auf bestehenden Spalten erzeugt **Fehler**.

> **Hinweis:** Ggf. muss die Streaming Table vor der Nutzung von **Time-Travel**-Abfragen aktualisiert werden.

### Vollständiger Refresh

```sql
-- Vollständiger Refresh
REFRESH STREAMING TABLE sales FULL;
```

Ein Full Refresh verarbeitet **alle** verfügbaren Quelldaten mit der aktuellen Definition neu. Für Quellen **ohne** vollständige Historie oder mit kurzer Aufbewahrungsfrist (z. B. Kafka) wird das **nicht empfohlen**, da bestehende Daten dabei abgeschnitten werden und alte Datensätze u. U. nicht wiederherstellbar sind.

## <a id="planen">14. Refreshes planen und überwachen</a>

> *"You can refresh a streaming table automatically on a schedule or when upstream data changes, and you can configure refresh timeouts, notifications, and performance modes. See Schedule refreshes."* (`/aws/en/ldp/dbsql/schedule-refreshes`)

Streaming Tables unterstützen also geplante Refreshes **oder** Refreshes, die durch Änderungen an Upstream-Daten ausgelöst werden — mit konfigurierbaren Timeouts, Benachrichtigungen und Performance-Modi. Details siehe Datei „Refresh-Zeitplaene.md".

## <a id="zugriff">15. Zugriffskontrolle</a>

Table-Owner bzw. Nutzer mit `MANAGE`-Privileg können `SELECT`-Privilegien vergeben, **ohne** dass die Empfänger `SELECT`-Zugriff auf die zugrunde liegenden Quelltabellen benötigen.

```sql
GRANT <privilege_type> ON <st_name> TO <principal>;
```

| Privileg | Bedeutung |
|---|---|
| `SELECT` | Erlaubt das Abfragen der Streaming Table |
| `REFRESH` | Erlaubt das Aktualisieren der Tabelle (mit den Berechtigungen des Owners) |

```sql
CREATE OR REFRESH STREAMING TABLE st_name AS SELECT * FROM source_table;
-- Nur-Lese-Zugriff gewähren:
GRANT SELECT ON st_name TO read_only_user;
-- Lese- und Refresh-Zugriff gewähren:
GRANT SELECT ON st_name TO refresh_user;
GRANT REFRESH ON st_name TO refresh_user;
```

```sql
-- Privileg entziehen
REVOKE privilege_type ON <st_name> FROM principal;
```

```sql
REVOKE SELECT ON st_name FROM read_only_user;
```

**Verhalten bei entzogenem Quellzugriff:** Werden `SELECT`-Privilegien auf Quelltabellen entzogen oder Quelltabellen gelöscht, können Inhaber des Streaming-Table-Zugriffs **weiterhin vorhandene Daten abfragen**, aber **nicht mehr `REFRESH`** ausführen. Geplante Refreshes schlagen fehl oder laufen nicht — die Tabelle veraltet.

### Owner einer Streaming Table ändern

Nutzer mit `MANAGE`-Berechtigung können die Ownership über den **Catalog Explorer** an sich selbst oder an einen von ihnen kontrollierten Service Principal übertragen:

1. Data-Icon anklicken, um den Catalog Explorer zu öffnen.
2. Streaming Table auswählen.
3. In der rechten Seitenleiste unter „About this streaming table" bei **Owner** das Bearbeiten-Icon anklicken.
4. Neuen Owner wählen (Service Principals benötigen die Rolle „Service Principal User").
5. Fehlen dem neuen Owner `SELECT`- oder `MANAGE`-Privilegien und wechselt man von der eigenen Ownership weg, beide Grant-Optionen auswählen.
6. **Save** klicken.

> **Hinweis:** Erscheint eine Meldung, den Owner über den **Run as**-Nutzer in den Pipeline-Einstellungen zu ändern, ist die Streaming Table in einer Lakeflow-Pipeline definiert — **nicht** als Standalone-Tabelle.

Verliert der (neue) Owner den Zugriff auf die Quelltabellen, bleiben vorhandene Daten abfragbar, aber `REFRESH`-Operationen schlagen fehl und geplante Refreshes laufen nicht.

## <a id="loeschen">16. Datensätze dauerhaft löschen (`REORG … PURGE`)</a>

> **Public Preview:** Die `REORG`-Unterstützung für Streaming Tables ist in Public Preview.

**Voraussetzungen:**

- Databricks Runtime 15.4 und höher.
- Nur nötig für Streaming Tables mit aktivierten **Deletion Vectors**.

**Ablauf:**

1. Datensätze der Streaming Table aktualisieren oder löschen.
2. `REORG` mit `APPLY (PURGE)` ausführen:
   ```sql
   REORG TABLE <streaming-table-name> APPLY (PURGE);
   ```
3. Die Datenaufbewahrungsfrist abwarten (Standard: **sieben Tage**, konfigurierbar über `delta.deletedFileRetentionDuration`).
4. Die Streaming Table per `REFRESH` aktualisieren.
5. Automatische `VACUUM`-Operationen laufen innerhalb von **24 Stunden** nach dem Refresh.

## <a id="query-history">17. Runs über die Query History überwachen</a>

> **Public Preview:** Dieses Feature ist in Public Preview; Workspace-Admins steuern den Zugriff über die Previews-Seite.

Die Query History zeigt alle Streaming-Table-bezogenen Anweisungen an, einschließlich `CREATE` und der zugehörigen **asynchronen `REFRESH`-Operationen**. `REFRESH`-Anweisungen liefern detaillierte Query-Pläne für die Performance-Optimierung.

Zugriff auf `REFRESH`-Anweisungen:

1. History-Icon in der linken Seitenleiste anklicken.
2. Im Statement-Dropdown-Filter `REFRESH` auswählen.
3. Auf den Query-Namen klicken für Zusammenfassungsdetails.
4. „See query profile" für die detaillierte Analyse anklicken.
5. Über „Query Source"-Links verwandte Queries oder Pipelines öffnen.

## <a id="external-clients">18. Zugriff über externe Clients (Compatibility Mode)</a>

> *"To access streaming tables from external Delta Lake or Iceberg clients that don't support open APIs, you can use Compatibility Mode. Compatibility Mode creates a read-only version of your streaming table that can be accessed by any Delta Lake or Iceberg client."* (`/aws/en/external-access/compatibility-mode`)

## <a id="weitere-ressourcen">19. Weitere Ressourcen</a>

- Spark Declarative Pipelines
- `read_files` table-valued function — siehe [[_read_files]]
- `read_kafka` table-valued function
- `CREATE STREAMING TABLE` — `/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table`
- `ALTER STREAMING TABLE`
- Use standalone materialized views
- The AUTO CDC APIs: Simplify change data capture with pipelines
- Delta Lake table streaming reads and writes — `/aws/en/structured-streaming/delta-lake`

---

## <a id="quellen">20. Quellen</a>

1. Use standalone streaming tables (AWS): https://docs.databricks.com/aws/en/ldp/dbsql/streaming
2. Requirements for standalone pipelines: https://docs.databricks.com/aws/en/ldp/dbsql/compute
3. REPLACE WHERE flows for standalone streaming tables: https://docs.databricks.com/aws/en/ldp/dbsql/flows-replace-where
4. Schedule refreshes: https://docs.databricks.com/aws/en/ldp/dbsql/schedule-refreshes
5. Load data in pipelines (Ingestion aus Kafka u. a.): https://docs.databricks.com/aws/en/ldp/load
6. Compatibility Mode: https://docs.databricks.com/aws/en/external-access/compatibility-mode

**Stand:** 2026-09-02.
