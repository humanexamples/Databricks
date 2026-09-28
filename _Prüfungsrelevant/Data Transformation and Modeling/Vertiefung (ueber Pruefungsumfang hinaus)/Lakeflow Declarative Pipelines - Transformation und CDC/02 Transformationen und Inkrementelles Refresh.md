# Transformationen und Inkrementelles Refresh in Lakeflow Declarative Pipelines

## 1. Grundprinzip

- Ein Dataset lässt sich gegen jede Query definieren, die einen DataFrame zurückgibt: Spark-Built-ins, UDFs, benutzerdefinierte Logik, MLflow-Modelle.
- Muster: Stream-Static-Joins, inkrementelle Aggregationen, Mischen von Streaming Tables und Materialized Views.

## 2. Private Zwischentabellen (`PRIVATE`)

- `PRIVATE` verhindert Publizierung einer Zwischentabelle in ein Schema (kein externer Zugriff) — Speicherung/Verarbeitung folgt weiterhin der Pipeline-Semantik.
- Besteht für die Lebensdauer der erzeugenden Pipeline.

```sql
CREATE PRIVATE STREAMING TABLE private_table
AS SELECT ... ;
```

```python
@dp.table(private=True)
def private_table():
  return ("...")
```

## 3. Streaming Tables und Materialized Views kombinieren

- Streaming Tables erben Spark-Structured-Streaming-Garantien, für Append-only-Quellen konfiguriert (`skipChangeCommits` übersteuert das bei Bedarf).
- Muster: Bronze (Ingestion, einfache Transformation) = Streaming Table; Gold (komplexe Aggregation, oder Lesen aus `AUTO CDC ... INTO`-Ziel) = Materialized View — solche Operationen erzeugen inhärent Updates, als Streaming-Table-Input nicht unterstützt.

```python
@dp.table
def streaming_bronze():
  # Streaming-Quelle -> inkrementelle Tabelle
  return spark.readStream.format("cloudFiles") \
      .option("cloudFiles.format", "json") \
      .load("abfss://path/to/raw/data")

@dp.table
def streaming_silver():
  # Bronze als Stream lesen -> ebenfalls inkrementell
  return spark.readStream.table("streaming_bronze").where(...)

@dp.materialized_view
def live_gold():
  # Bei jedem Update vollständig aus ganzer Silver-Tabelle neu berechnet
  return spark.read.table("streaming_silver").groupBy("user_id").count()
```

```sql
CREATE OR REFRESH STREAMING TABLE streaming_bronze
AS SELECT * FROM STREAM read_files("abfss://path/to/raw/data", format => "json");

CREATE OR REFRESH STREAMING TABLE streaming_silver
AS SELECT * FROM STREAM(streaming_bronze) WHERE ...;

CREATE OR REFRESH MATERIALIZED VIEW live_gold
AS SELECT count(*) FROM streaming_silver GROUP BY user_id;
```

## 4. Join-Muster

### 4.1 Stream-Static-Join

- Kontinuierlicher Append-only-Stream + überwiegend statische Dimensionstabelle. Bei jedem Update: neue Stream-Datensätze mit aktuellstem Snapshot gejoint.
- **Gotcha:** Ändert sich die statische Tabelle, nachdem entsprechende Streamdaten schon verarbeitet wurden, werden Ergebnisse **nicht** neu berechnet ohne Full Refresh.
- Getriggert: statische Tabelle liefert Stand zum Update-Start. Kontinuierlich: bei jeder Verarbeitung jeweils neueste Version.

```python
@dp.table
def customer_sales():
  return spark.readStream.table("sales").join(spark.read.table("customers"), ["customer_id"], "left")
```

```sql
CREATE OR REFRESH STREAMING TABLE customer_sales
AS SELECT * FROM STREAM(sales)
  INNER JOIN LEFT customers USING (customer_id)
```

### 4.2 Weitere Join-Typen

| Join-Typ | Quellen | Ausgabetyp | Verarbeitete Daten |
|---|---|---|---|
| Stream-Static (Stream-Snapshot) | Streaming + Statisch | Streaming Table | nur neue Zeilen |
| MV-Join | Streaming + Streaming | Materialized View | alle Zeilen je Lauf |
| Stream-Stream | Streaming + Streaming | Streaming Table | nur neue Zeilen (windowed) |

- **Join zweier Streaming Tables via Materialized View:** MV als Ziel, wenn beide Seiten regelmäßig vollständig gejoint werden sollen — verarbeitet bei jedem Update alle (bzw. inkrementell möglichen) Zeilen neu, konsistent zum aktuellen Stand.
- **Stream-Stream-Join:** verarbeitet je Update nur neue Daten beider Streams inkrementell — für zeitlich eng korrelierte Events (z. B. Clickstream + Ad-Impressions). Erfordert Windowing/Watermark (Abschnitt 8).

## 5. Aggregate effizient berechnen

- Streaming Tables berechnen einfache distributive Aggregate (`count`, `min`, `max`, `sum`) und algebraische Aggregate (Durchschnitt, Standardabweichung) inkrementell.
- Empfohlen bei begrenzter Gruppenzahl, z. B. `GROUP BY country` — bei jedem Update nur neue Eingabedaten gelesen.

## 6. MLflow-Modelle in Pipelines verwenden

- **Gotcha:** MLflow-Modelle in Unity-Catalog-aktivierter Pipeline benötigen `preview`-Channel; für `current`-Channel muss Pipeline stattdessen auf Hive Metastore publizieren.
- MLflow-Modelle wirken als Transformation: Spark-DataFrame → Spark-DataFrame. Pipelines installieren MLflow nicht standardmäßig — vorher `%pip install mlflow`.
- Ablauf: (1) Run-ID + Modellname → Modell-URI; (2) Spark-UDF über URI definieren; (3) UDF in Tabellendefinition aufrufen.

```python
%pip install mlflow==2.20.2

from pyspark import pipelines as dp
import mlflow
from pyspark.sql.functions import struct

run_id = "mlflow_run_id"
model_name = "the_model_name_in_run"
model_uri = f"runs:/{run_id}/{model_name}"
loaded_model_udf = mlflow.pyfunc.spark_udf(spark, model_uri=model_uri)

categoricals = ["term", "home_ownership", "purpose",
  "addr_state", "verification_status", "application_type"]
numerics = ["loan_amnt", "emp_length", "annual_inc", "dti", "delinq_2yrs",
  "revol_util", "total_acc", "credit_length_in_years"]
features = categoricals + numerics

@dp.materialized_view(
  comment="GBT ML predictions of loan risk",
  table_properties={"quality": "gold"}
)
def loan_risk_predictions():
  return spark.read.table("loan_risk_input_data") \
    .withColumn('predictions', loaded_model_udf(struct(features)))
```

## 7. Manuelle Löschungen/Updates erhalten

- Standard: Tabellenergebnisse werden bei jedem Update aus den Eingabedaten neu berechnet — ein manuell gelöschter Datensatz würde sonst wieder aus der Quelle geladen.
- `pipelines.reset.allowed = false` verhindert **Refreshes** (insb. Full Refresh) — verhindert **nicht** inkrementelle Writes/neue Daten.

Beispiel: `raw_user_table` (Rohdaten) → `bmi_table` (inkrementell BMI). Manuelle Löschung in `raw_user_table` soll bei künftigem Refresh nicht rückgängig gemacht werden, `bmi_table` weiter bei jedem Update neu berechnet:

```sql
CREATE OR REFRESH STREAMING TABLE raw_user_table
TBLPROPERTIES(pipelines.reset.allowed = false)
AS SELECT * FROM STREAM read_files("/databricks-datasets/iot-stream/data-user", format => "csv");

CREATE OR REFRESH STREAMING TABLE bmi_table
AS SELECT userid, (weight/2.2) / pow(height*0.0254,2) AS bmi FROM STREAM(raw_user_table);
```

- Derselbe Schutz greift bei automatischem Verschwinden aus der Quelle (z. B. Lifecycle-Richtlinie) — ohne `pipelines.reset.allowed = false` würden bei Full Table Refresh nicht mehr vorhandene Quelldaten nicht erneut eingelesen.

---

## 8. Inkrementelles Refresh für Materialized Views

Erkennt Änderungen in Quelldaten, berechnet nur betroffene Ergebnisse neu statt der gesamten Query — spart Rechenkosten.

### 8.1 Refreshes laufen auf Serverless Compute

- Eigenständige MVs: Workspace muss nicht für Serverless Lakeflow Pipelines aktiviert sein — Refresh nutzt automatisch Serverless Pipeline.
- Über Lakeflow-Pipeline definierte MVs: Pipeline selbst muss auf Serverless konfiguriert sein.

### 8.2 Refresh-Semantik

MVs garantieren zu Batch-Queries äquivalente Ergebnisse (Best-Effort nur neue/geänderte Daten verarbeiten — zu unterscheiden von automatischem Query-Caching):

```sql
CREATE OR REPLACE MATERIALIZED VIEW transaction_summary AS
SELECT account_id, COUNT(txn_id) txn_count, SUM(txn_amount) account_revenue
FROM transactions_table
GROUP BY account_id
```

```python
@dp.materialized_view()
def transaction_summary():
  return (spark.read.table("transactions_table")
    .groupBy("account_id")
    .agg(count("*").alias("txn_count"), sum("txn_amount").alias("account_revenue")))
```

### 8.3 Datenquellen-Überlegungen

- Alle Quellen sollten robust gegenüber Full-Refresh-Semantik sein, selbst wenn inkrementell möglich.
- Sehr große Tabellen mit kostenprohibitivem Full Refresh → Streaming Tables (Exactly-once) statt MV.
- **Gotcha:** MVs **nicht** gegen Quellen definieren, deren Datensätze nur einmal verarbeitet werden sollen — Kafka (keine Historie), Auto-Loader-Ingestion, Quellen mit gelöschten/archivierten Datensätzen, deren Info nachgelagert erhalten bleiben muss.
- Inkrementell-fähige Quellen: Delta-Tabellen (UC-Managed + External), MVs, Streaming Tables (inkl. `AUTO CDC ... INTO`-Ziele), UC-Managed-Iceberg v2/v3 (v3 empfohlen; Foreign Iceberg nicht unterstützt).
- Manche Operationen benötigen **Row Tracking** auf Quelltabellen (Delta-only).
- Quellen mit Row Filters/Column Masks unterstützen kein inkrementelles Refresh.

### 8.4 Optimierung: empfohlene Delta-Features

```sql
ALTER TABLE <table-name> SET TBLPROPERTIES (
  delta.enableDeletionVectors = true,
  delta.enableRowTracking = true,
  delta.enableChangeDataFeed = true);
```

### 8.5 Refresh-Typen

- **Refresh (Default):** versucht inkrementell, fällt bei Bedarf auf vollständige Neuberechnung zurück; nur Serverless. Kostenanalyse entscheidet, Ausgabe identisch. Nur über Serverless Pipelines aktualisierte MVs können inkrementell refresht werden.
- **Full Refresh:** berechnet immer alles neu, leert Tabelle + Checkpoints.

```sql
REFRESH MATERIALIZED VIEW mv_name FULL
```

- **Gotcha:** Full Refresh gegen Quelle mit entfernten Datensätzen (Retention/manuelle Löschung) spiegelt diese nicht im Ergebnis — ggf. nicht wiederherstellbar, Schema kann sich für weggefallene Spalten ändern.

### 8.6 Unterstützung für inkrementelles Refresh nach SQL-Konstrukt

`EXPLAIN CREATE MATERIALIZED VIEW` testet Inkrementalisierbarkeit. \* = benötigt Row Tracking auf Quellen.

| SQL-Konstrukt | Unterstützt? | Hinweis |
|---|---|---|
| `SELECT`-Ausdrücke\* | Ja | deterministische Built-ins, unveränderliche UDFs |
| `GROUP BY` | Ja | |
| `WITH` | Ja | CTEs unterstützt |
| `WITH RECURSIVE` | Nein | Full Refresh |
| `UNION ALL`\* | Ja | |
| `FROM` | teilweise | nur Delta, UC-Managed-Iceberg, MV, Streaming Table als Basis |
| `WHERE`, `HAVING`\* | Ja | |
| `INNER/LEFT/FULL/RIGHT JOIN`\* | Ja | |
| `OVER` | Ja | `PARTITION BY`-Spalten nötig |
| `QUALIFY` | Ja | |
| `EXPECTATIONS` | Ja | nicht wenn MV aus View mit Expectations liest, oder MV `DROP`-Expectation UND `NOT NULL`-Spalten hat |
| UDFs | bedingt | Verhaltensänderungen meist automatisch erkannt; UDFs mit anderen Bibliotheken evtl. unerkannt — Full Refresh dann in eigener Verantwortung |
| Nicht-deterministische Funktionen | teilweise | Zeitfunktionen in `WHERE` erlaubt, sonst nicht |
| `FLOAT`/`DOUBLE`-Aggregationen | riskant | `SUM`/`AVG`/Kovarianz nicht-deterministisch — nach `DECIMAL` casten |
| Volumes, External Locations, Foreign Catalogs, Foreign Iceberg | Nein | nicht unterstützt |

### 8.7 Incrementalization Insights

- Pipeline-Editor Tables-Panel zeigt Spalte **Incrementalization**: **Incremental**, **Full recompute**, **No change**.
- Bei erkannten Problemen: Lightbulb-Insight-Icon mit Ursache/Lösung (z. B. Row Tracking/Deletion Vectors aktivieren, Operator umschreiben, Serverless konfigurieren).
- Insights auch bei "No change" oder Dry Run möglich; Fehlen garantiert nicht Inkrementalisierbarkeit. Genie Code befragbar.

### 8.8 Refresh-Typ eines Updates bestimmen

| Technik | Inkrementell? |
|---|---|
| `FULL_RECOMPUTE` | Nein |
| `NO_OP` | n/a (keine Änderung erkannt) |
| `ROW_BASED`, `PARTITION_OVERWRITE`, `WINDOW_FUNCTION`, `APPEND_ONLY`, `GROUP_AGGREGATE`, `GENERIC_AGGREGATE` | Ja |

```sql
SELECT timestamp, message
FROM event_log(TABLE(<fully-qualified-table-name>))
WHERE event_type = 'planning_information'
ORDER BY timestamp desc;
-- Ergebnis (message-Auszug): "Flow '<mv>' has been planned to be executed as ROW_BASED."
```

### 8.9 Refresh Policy

Standard: Databricks wählt automatisch kosteneffektivste Strategie. Für vorhersehbareres Verhalten: `REFRESH POLICY`.

- **`AUTO`** (Standard) — kostenbasierte Auswahl, für die meisten Workloads.
- **`INCREMENTAL`** — bevorzugt inkrementell, Fallback Full Refresh (z. B. Row Tracking temporär deaktiviert).
- **`INCREMENTAL STRICT`** — strikt inkrementell; nicht möglich → Refresh/Create schlägt fehl. Für harte Kosten-/Performance-/SLA-Vorgaben.
- **`FULL`** — immer vollständig, auch wenn inkrementalisierbar; für kleine Datasets oder häufig strukturell wechselnde Queries.

```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS my_mv
REFRESH POLICY INCREMENTAL
AS SELECT a, sum(b) FROM my_catalog.example.my_table GROUP BY a;
```

```python
from pyspark import pipelines as dp

@dp.materialized_view(refresh_policy = 'incremental_strict')
def my_mv():
  return spark.read("main.default.source_table")
```

---

## 9. Full Refresh für Streaming Tables

Verwirft alle Daten/Metadaten, startet Stream neu: Tabelle geleert, alle Checkpoint-Daten entfernt, neue Checkpoints je schreibendem Flow.

### 9.1 Auswirkung auf Datenquellen

- **Gotcha:** Bei Quellen mit Retention-Limits (z. B. Kafka kurze Retention) können historische Daten nach Full Refresh unwiederbringlich verloren sein — bei hochvolumigen Streams/begrenzter Retention nicht empfohlen.
- Nachgelagerte abhängige Tabellen: Pipeline schlägt fehl, bis auch diese vollständig refresht wurden (außer `skipChangeCommits` aktiv) — nachgelagerte MVs müssen ebenfalls vollständig refresht werden.

### 9.2 Wann ein Full Refresh nötig ist

Muss explizit ausgelöst werden (**Full Refresh** in Pipeline-UI oder Auto Full Refresh in Lakeflow Connect). Auslöser:

- **Schema-Änderungen** (nicht rückwärtskompatibel): Spalten umbenennen ohne Column Mapping, geänderte Dedup-Spalten, Typänderungen (Verengung `BIGINT→INT`/`DOUBLE→FLOAT`, inkompatibel `STRING→INT`), hartes Spalten-Löschen. Empfehlung: neue Spalte anlegen + `UNION`-View über alte/neue Werte.
- **Physisches Daten-Layout:** Legacy-Partitionierung → neues Clustering-Schema.
- **Upstream-Quelländerungen:** geänderte Quelltabellen, Quelltyp-Wechsel (Kafka→Delta), geänderte Speicherorte/Subscriptions, gedroppte+neu angelegte Quell-Delta-Tabelle (auch bei gleichem Schema).
- **Zustandsbehaftete Verarbeitung:** geänderte Aggregations-Keys/-Funktionen, hinzugefügte/entfernte Aggregationen, geänderte Join-Keys/-Typen, hinzugefügte/entfernte Joins, geänderte Dedup-Spalten/-Logik.
- **Datenkontinuitätsprobleme:** abgelaufene CDC-Log-Retention, beschädigtes/gelöschtes Checkpoint-Verzeichnis, beschädigte/verlorene Schema-Tracking-Dateien.

### 9.3 Limitierungen

- Full Refresh verarbeitet keine Daten erneut, sofern Quelle nicht vollständige Historie vorhält.
- Große Datasets: kostenintensiv/zeitaufwändig.
- Nachgelagerte Konsumenten können fehlschlagen/unvollständige Ergebnisse liefern, bis Refresh abgeschlossen.

### 9.4 Best Practices

| Situation | Best Practice |
|---|---|
| Auf Stabilität designen | Spalten hinzufügen meist sicher; bestehende Spalten/Partitionierung ändern erfordert meist Neuberechnung |
| Quellen mit kurzer Retention | Rohdaten zunächst in Bronze-Streaming-Table mit flexiblen Typen (`variant`/`string`) — behält Historie, auch wenn nachgelagerte typisierte Tabellen Full Refresh brauchen |
| Alternativen erwägen | neuen Flow anlegen (bewahrt Daten, Duplikat-Risiko) oder Checkpoint zurücksetzen (ebenfalls Duplikat-Risiko); alternativ neue Streaming Table + `UNION`-View mit alter |
| Wenn Full Refresh nötig | in Dev/Staging testen, Abhängigkeiten dokumentieren, Wartungsfenster einplanen, genug historische Quelldaten sicherstellen |

- Nachträgliches Einspielen nach Full Refresh: `append once`-Flow (siehe Kapitel Flows) — einmaliger Backfill, läuft danach nicht weiter bis zum nächsten Full Refresh.

---

## 10. Zustandsbehaftete Verarbeitung mit Watermarks

### 10.1 Was ist ein Watermark?

- Für inkrementelle statt bei-jedem-Update-vollständige Aggregations-Queries nötig.
- Zeitbasierter Schwellenwert bei zustandsbehafteten Operationen (Aggregation, Join, Dedup) — Fenster schließt, wenn Schwellenwert erreicht.
- Vermeidet hohe Latenz/OOM durch übermäßigen State, unterstützt korrekte Berechnung bei ungeordnet eintreffenden Daten.

### 10.2 Watermark definieren

Zeitstempel-Feld + Schwellenwert für "verspätete Daten" (danach eintreffend → verwerfbar). Kleiner Schwellenwert = frühere Ergebnisse, mehr Verwurf-Risiko; großer = vollständiger, aber höhere Latenz/State-Größe.

```python
withWatermark("timestamp", "3 minutes")
```

```sql
WATERMARK timestamp DELAY OF INTERVAL 3 MINUTES
```

### 10.3 Watermarks bei Stream-Stream-Joins

- **Gotcha:** Auf **beiden** Seiten Watermark + Zeitintervall-Klausel (gleiche Felder wie Watermarks) nötig — teilt der Engine mit, wann keine Matches mehr möglich sind.
- Unterschiedliche Watermark-Schwellenwerte je Stream möglich; Engine pflegt globalen Watermark nach dem langsamsten Stream (Datenverlustvermeidung).

```python
from pyspark import pipelines as dp

dp.create_streaming_table("adImpressionClicks")

@dp.append_flow(target = "adImpressionClicks")
def joinClicksAndImpressions():
  clicksDf = read_stream("rawClicks").withWatermark("clickTimestamp", "3 minutes")
  impressionsDf = read_stream("rawAdImpressions").withWatermark("impressionTimestamp", "3 minutes")
  joinDf = impressionsDf.alias("imp").join(
    clicksDf.alias("click"),
    expr("""
      imp.userId = click.userId AND
      clickAdId = impressionAdId AND
      clickTimestamp >= impressionTimestamp AND
      clickTimestamp <= impressionTimestamp + interval 3 minutes
    """),
    "inner"
  ).select("imp.userId", "impressionAdId", "clickTimestamp", "impressionSeconds")
  return joinDf
```

```sql
CREATE OR REFRESH STREAMING TABLE silver.adImpressionClicks
AS SELECT imp.userId, impressionAdId, clickTimestamp, impressionSeconds
FROM STREAM (bronze.rawAdImpressions)
WATERMARK impressionTimestamp DELAY OF INTERVAL 3 MINUTES imp
INNER JOIN STREAM (bronze.rawClicks)
WATERMARK clickTimestamp DELAY OF INTERVAL 3 MINUTES click
ON imp.userId = click.userId
AND clickAdId = impressionAdId
AND clickTimestamp >= impressionTimestamp
AND clickTimestamp <= impressionTimestamp + interval 3 minutes
```

### 10.4 Windowed Aggregations

- **Tumbling (feste) Fenster:** fest, nicht überlappend, zusammenhängend — ein Datensatz gehört zu genau einem Fenster.
- **Sliding Windows:** feste Größe, überlappend — ein Datensatz kann in mehrere Fenster fallen.
- Nach Fensterende + Watermark-Länge: keine neuen Daten für dieses Fenster, Ergebnis ausgegeben, State verworfen. `window(...)` muss auf derselben Zeitstempel-Spalte wie Watermark basieren, Teil der `GROUP BY`-Klausel.

```sql
CREATE OR REFRESH STREAMING TABLE gold.adImpressionSeconds
AS SELECT impressionAdId, window(clickTimestamp, "5 minutes") as impressions_window,
  sum(impressionSeconds) as totalImpressionSeconds
FROM STREAM (silver.adImpressionClicks)
WATERMARK clickTimestamp DELAY OF INTERVAL 3 MINUTES
GROUP BY impressionAdId, window(clickTimestamp, "5 minutes")
```

```python
from pyspark import pipelines as dp

@dp.table()
def profit_by_hour():
  return (
    spark.readStream.table("sales")
      .withWatermark("timestamp", "1 hour")
      .groupBy(window("timestamp", "1 hour").alias("time"))
      .aggExpr("sum(profit) AS profit")
  )
```

### 10.5 Streaming-Datensätze deduplizieren

- Structured Streaming: Exactly-once-Verarbeitung, aber **keine automatische Dedup aus der Quelle** — bei At-least-once-Message-Queues Duplikate erwarten.
- `dropDuplicatesWithinWatermark()`: dedupliziert nach beliebigen Feldern, auch bei abweichenden anderen Feldern (Event Time vs. Arrival Time); Watermark zwingend erforderlich — Duplikate innerhalb des Watermark-Zeitraums verworfen.
- **Gotcha:** ungeordnete Daten können den Watermark fälschlich zu weit vorspringen lassen. `withEventTimeOrder` (nur Python) verarbeitet initialen Snapshot geordnet nach Watermark-Spalte:

```json
{
  "spark_conf": {
    "spark.databricks.delta.withEventTimeOrder.enabled": "true"
  }
}
```

```python
clicksDedupDf = (
  spark.readStream.table
    .option("withEventTimeOrder", "true")
    .table("rawClicks")
    .withWatermark("clickTimestamp", "5 seconds")
    .dropDuplicatesWithinWatermark(["userId", "clickAdId"]))
```

### 10.6 Pipeline-Konfiguration optimieren

- Für großen Zwischenzustand: RocksDB-basiertes State Management empfohlen. **Serverless Pipelines verwalten State-Store-Config automatisch.** Manuell vor Deployment:

```json
{
  "configuration": {
    "spark.sql.streaming.stateStore.providerClass": "com.databricks.sql.streaming.state.RocksDBStateStoreProvider"
  }
}
```

- Für Millisekunden-Latenz zusätzlich: *Real-Time Mode* für Lakeflow Pipelines.

**Stand:** 2026-09-14.
