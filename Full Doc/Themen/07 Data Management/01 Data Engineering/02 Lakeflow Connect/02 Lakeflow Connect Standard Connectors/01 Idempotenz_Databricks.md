# Idempotenz in Databricks

## Was bedeutet idempotent?

**Idempotent** bedeutet: Ein Vorgang liefert **immer das gleiche Endergebnis**, egal wie oft man ihn ausführt – auch bei mehrfacher Wiederholung, Wiederholung nach einem Fehler, oder erneutem Anstoßen desselben Jobs.

- **Nicht idempotent** (Beispiel): Ein einfaches `INSERT INTO ... SELECT` aus einer Quelle. Führt man denselben Job zweimal aus, werden die Daten **doppelt** eingefügt – jeder erneute Lauf verändert das Ergebnis.
- **Idempotent**: Ein Vorgang, der bei erneuter Ausführung **keine Duplikate oder falschen Zustände** erzeugt, weil er sich merkt, was bereits verarbeitet wurde, oder das Ziel komplett neu setzt.

## Wo Idempotenz in Databricks konkret eine Rolle spielt

### `COPY INTO`

Merkt sich intern (über Metadaten im Delta Log), welche Dateien bereits geladen wurden. Erneutes Ausführen lädt dieselben Dateien **nicht** noch einmal. Über die Option `force = true` lässt sich dieses Verhalten gezielt deaktivieren, etwa um Dateien nach einer Datenkorrektur an der Quelle absichtlich erneut zu laden.

> Wörtlich: *"This is a retryable and idempotent operation. Files in the source location that have already been loaded are skipped."* Zur `force`-Option: *"force: boolean, default false. If set to true, idempotency is disabled and files are loaded regardless of whether they've been loaded before."*

```sql
-- Lädt bereits geladene Dateien nicht erneut
COPY INTO workspace.default.orders
FROM '/Volumes/raw/orders/'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');
```

### Auto Loader

Nutzt Checkpoints (RocksDB-basierter Key-Value-Store), um bereits verarbeitete Dateien zu tracken – bei Neustart wird nur ab dem letzten Checkpoint weitergemacht.

> Wörtlich: *"This key-value store ensures that data is processed exactly once."*

```python
# Nutzt Checkpoints, um bereits verarbeitete Dateien nicht erneut zu lesen
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .load("/Volumes/analytics/bronze/user_events"))

(df.writeStream
   .format("delta")
   .option("checkpointLocation", "/Volumes/analytics/bronze/_checkpoint")
   .trigger(availableNow=True)
   .table("workspace.default.user_events_delta"))
```

### `MERGE INTO`

Bei eindeutigem Matching-Key führt ein erneuter Lauf mit denselben Quelldaten nur zu `UPDATE`, nicht zu neuen Duplikaten. Das gilt aber nur, wenn pro Matching-Key (z. B. `customer_id`) **maximal eine Zeile** in der Quelle vorkommt – enthält die Quelle mehrere Zeilen mit demselben Schlüssel (z. B. bei API-Pulls mit Duplikaten), schlägt der Merge mit einem Fehler fehl. Die Quelle muss dafür ggf. vorher dedupliziert werden (z. B. per `ROW_NUMBER() OVER (PARTITION BY id ORDER BY ...)`).

> Grundprinzip von Upsert-Operationen. Zum Fehlerfall wörtlich: *"MERGE operations fail with a DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE error if more than one row in the source table matches the same row in the target table."*

```sql
-- Vorher deduplizieren, um DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE zu vermeiden
CREATE OR REPLACE TEMP VIEW customers_changes_dedup AS
SELECT * EXCEPT(rn) FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) AS rn
  FROM workspace.default.customers_changes
) WHERE rn = 1;

MERGE INTO workspace.default.customers AS target
USING customers_changes_dedup AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN
    UPDATE SET *
WHEN NOT MATCHED THEN
    INSERT *;
```

### `CREATE OR REPLACE TABLE ... AS SELECT` (CTAS)

Erzeugt bei jedem Lauf denselben, vollständigen Snapshot der Quelle (Full Refresh) – keine Duplikate, da die Zieltabelle komplett neu geschrieben wird. Die Doku bezeichnet CTAS dabei nicht wörtlich als "idempotent"; treffender ist **"deterministisch bei gleichbleibender Quelle"**, da bei jedem Lauf eine vollständige Neuerstellung stattfindet statt einer inkrementellen "exactly-once"-Verarbeitung wie bei `COPY INTO` oder Auto Loader.

> Die Doku beschreibt `CREATE OR REPLACE TABLE` als Full-Refresh-Mechanismus, der die Zieltabelle ersetzt und dabei Tabellenhistorie sowie Berechtigungen erhält.

```sql
-- Erzeugt bei jedem Lauf denselben, vollständigen Snapshot
CREATE OR REPLACE TABLE workspace.default.daily_summary AS
SELECT
    order_date,
    SUM(quantity * unit_price) AS revenue
FROM workspace.default.orders
GROUP BY order_date;
```

### `INSERT INTO` (ohne Bedingung) vs. `INSERT OVERWRITE`

Reines `INSERT INTO` ist **nicht** idempotent – jeder Lauf hängt neue Zeilen an, auch wenn die Quelle unverändert ist. `INSERT OVERWRITE` dagegen leert die Zieltabelle (bzw. die betroffenen Partitionen) vor dem Einfügen und liefert bei gleichbleibender Quelle bei jedem Lauf dasselbe Ergebnis – dasselbe Full-Refresh-Prinzip wie bei CTAS.

> Wörtlich zu `OVERWRITE`: *"Without a partition_spec the table is truncated before inserting the first row."* Für reines `INSERT INTO` nicht wörtlich als Warnung dokumentiert, aber logisch zwingend und indirekt durch den Kontrast zu `COPY INTO`/`MERGE INTO` in der Doku bestätigt.

```sql
-- Jeder erneute Lauf fügt Daten doppelt hinzu
INSERT INTO workspace.default.orders
SELECT * FROM workspace.staging.orders_new;
```

### `foreachBatch`

`foreachBatch` bietet laut Doku nur "at-least-once"-Garantien – Idempotenz muss selbst implementiert werden.

> Wörtlich: *"foreachBatch() provides only at-least-once write guarantees."*

```python
# Idempotenz muss selbst implementiert werden, z. B. via MERGE:
def upsert_to_delta(batch_df, batch_id):
    batch_df.createOrReplaceTempView("updates")
    batch_df.sparkSession.sql("""
        MERGE INTO workspace.default.target_table t
        USING updates s
        ON t.id = s.id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

streaming_df.writeStream.foreachBatch(upsert_to_delta).start()
```

Das `MERGE`-Pattern oben löst Duplikate auf **Zeilenebene** (über den Business-Key). Für die eigentliche `foreachBatch`-Ausführung selbst – d. h. gegen den Fall, dass Spark denselben Microbatch nach einem Retry ein zweites Mal an die Funktion übergibt – dokumentiert Databricks einen eigenen, offiziellen Mechanismus: die Delta-Schreiboptionen `txnAppId` und `txnVersion`, gebunden an die `batchId`. Delta erkennt daran ein bereits geschriebenes `(txnAppId, txnVersion)`-Paar und überspringt den doppelten Schreibvorgang – das funktioniert auch beim Schreiben in mehrere Zieltabellen innerhalb derselben `foreachBatch`-Funktion:

```python
app_id = "orders_pipeline"  # pro Streaming-Query stabil und eindeutig

def write_idempotent(batch_df, batch_id):
    batch_df.write \
        .format("delta") \
        .mode("append") \
        .option("txnVersion", batch_id) \
        .option("txnAppId", app_id) \
        .saveAsTable("workspace.default.target_table")

streaming_df.writeStream.foreachBatch(write_idempotent).start()
```

**Wichtig:** Wird der Checkpoint gelöscht und die Query neu gestartet, muss eine neue `txnAppId` vergeben werden – sonst kann dieselbe `batchId` bei einem Neustart erneut vergeben und der zugehörige Datenstand fälschlich als "bereits geschrieben" übersprungen werden.

## Idempotenz bei externen APIs und Schnittstellen

**Wichtige Einordnung:** Die folgenden Konzepte sind **allgemeine Software-/API-Engineering-Praxis** und **nicht spezifisch in der Databricks-Dokumentation behandelt** – im Gegensatz zu `COPY INTO` und Auto Loader, die Databricks explizit und offiziell als "idempotent" bzw. "exactly-once" dokumentiert.

- **Idempotency-Key-Header** beim Senden von Daten an externe APIs (z. B. Stripe-Konvention) – gängiges Branchenmuster, keine Databricks-Funktion.
- **Watermark-/Cursor-basiertes Pulling** mit persistiertem Zustand (z. B. `last_updated_at`) – muss bei API-Ingestion selbst implementiert werden, da es kein Databricks-natives Äquivalent zu Auto-Loader-Checkpoints für API-Requests gibt.
- **Deduplizierung nach Landing** via `ROW_NUMBER()` – technisch notwendig, u. a. um den oben genannten `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE`-Fehler bei nachgelagerten `MERGE INTO`-Schritten zu vermeiden.

## CTAS, `read_files()` und `spark.read()` – welche Kategorie gehört wirklich zur Idempotenz?

Die obigen Abschnitte listen CTAS als eigene Kategorie, nicht `read_files()` oder `spark.read()`. Das ist korrekt, aber die drei Mechanismen liegen auf unterschiedlichen Ebenen und sollten nicht verwechselt werden:

- **`spark.read()`** (Batch-DataFrame-Reader) und **`read_files()` im Batch-Modus** sind **reine Lesevorgänge ohne eigenen Zustand**. Sie führen bei jedem Aufruf einfach alle aktuell zum Pfad passenden Dateien erneut ein – es gibt kein Konzept von "bereits gelesen". Für sich genommen sind sie deshalb **weder idempotent noch nicht-idempotent** – Idempotenz ist auf dieser Ebene schlicht keine sinnvolle Eigenschaft, weil kein Schreibvorgang stattfindet.
- **CTAS (`CREATE OR REPLACE TABLE ... AS SELECT`)** kombiniert einen solchen zustandslosen Lesevorgang (SELECT) mit einem **vollständig überschreibenden Schreibvorgang**. Die Wiederholbarkeit entsteht also nicht durch das Lesen, sondern durch das `CREATE OR REPLACE`: Bei gleichbleibender Quelle liefert jeder Lauf dasselbe Endergebnis, weil die Zieltabelle jedes Mal komplett neu aufgebaut wird. CTAS ist damit die richtige Kategorie für die Abschnitte oben, weil es tatsächlich ein Materialisierungs-Pattern beschreibt – `spark.read()` und `read_files()` (Batch) beschreiben dagegen nur den Lese-Baustein, der in CTAS, in einem `MERGE INTO` oder in einem `INSERT INTO` weiterverwendet werden kann.
- **`read_files()` mit dem `STREAM`-Schlüsselwort** ist ein Sonderfall: In diesem Modus nutzt `read_files()` intern Auto Loader und erbt dessen Checkpoint-basierte Exactly-once-Garantie. Es gehört also inhaltlich in dieselbe Zeile wie **Auto Loader**, nicht in eine eigene Kategorie.

**Fazit:** CTAS ist die korrekte Kategorie für die Idempotenz-Betrachtung, weil Idempotenz eine Eigenschaft von Schreib-/Materialisierungsvorgängen ist, nicht von Lesevorgängen. `spark.read()` und `read_files()` (Batch) sind die zustandslosen Bausteine, die diese Eigenschaft erst durch das umgebende Pattern (Full Refresh via CTAS, Upsert via `MERGE INTO`, oder Checkpoint-Tracking via Auto Loader bzw. `read_files(STREAM ...)`) erhalten.

## Warum das wichtig ist

Bei Pipelines, die z. B. bei einem Fehler **neu gestartet** oder **retried** werden (Job-Retries, Scheduler-Fehler, manuelle Wiederholung), will man sicherstellen, dass dadurch **keine doppelten oder inkonsistenten Daten** entstehen. Idempotente Operationen machen Pipelines robuster und einfacher zu betreiben, weil man sie gefahrlos erneut anstoßen kann.

**Kurz gesagt:** Idempotenz = *"Ergebnis bleibt gleich, egal wie oft ich es ausführe"* – ein zentrales Designprinzip für zuverlässige Batch- und Streaming-Pipelines in Databricks. `COPY INTO` und Auto Loader (bzw. `read_files(STREAM ...)`, das intern Auto Loader nutzt) sind von Databricks **offiziell** als idempotent/exactly-once dokumentiert; für `foreachBatch` dokumentiert Databricks mit `txnAppId`/`txnVersion` ebenfalls einen offiziellen Mechanismus, der aber – anders als bei `COPY INTO`/Auto Loader – explizit selbst aktiviert werden muss. Bei `MERGE INTO`, CTAS/`INSERT OVERWRITE` und API-Ingestion muss die Idempotenz durch bewusstes Design (eindeutige Keys, Deduplizierung, Full-Refresh-Logik) selbst sichergestellt werden.

## Quellen (Databricks-Dokumentation)

- COPY INTO Referenz (idempotent, `force`-Option): https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into
- Get started using COPY INTO: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/
- What is Auto Loader? (RocksDB-Checkpoint, exactly-once): https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/
- foreachBatch (at-least-once-Hinweis, `txnAppId`/`txnVersion`-Pattern für idempotente Writes): https://docs.databricks.com/aws/en/structured-streaming/foreach
- INSERT INTO / INSERT OVERWRITE Referenz: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-dml-insert-into
- MERGE INTO Referenz (DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE): https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into
- CREATE TABLE ... AS SELECT (CTAS als Full-Refresh-Mechanismus): https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-using
- read_files table-valued function (Batch vs. STREAM/Auto-Loader-Modus): https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files
- How do pipelines refresh? (Full vs. Incremental Refresh): https://docs.databricks.com/aws/en/ldp/concepts/refresh
