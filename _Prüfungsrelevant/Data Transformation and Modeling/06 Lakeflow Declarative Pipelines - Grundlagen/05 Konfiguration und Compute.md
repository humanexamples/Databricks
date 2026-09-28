# Konfiguration und Compute

## 1. Pipeline-Einstellungen im Überblick

Zwei Kategorien: **Quellcode** (Dateien mit Dataset-Deklarationen) und **Infrastruktur** (Compute, Update-Verarbeitung, Tabellen-Speicherort). Vor Produktivbetrieb besonders wichtig: **Ziel-Catalog/-Schema** (Default: Unity Catalog, siehe Abschnitt 3) und **Datenzugriff** (Compute braucht konfigurierte Berechtigungen für Quellen/Storage).

- Einstellungen als JSON anzeig-/editierbar; manche erweiterten Optionen nur via JSON.
- **Publishing-Modus:** Default gilt für alle neuen Pipelines. Vor 5. Februar 2025 erstellte Pipelines könnten noch Legacy-Modus (virtuelles `LIVE`-Schema) nutzen.

**Neue Pipeline:** **New → ETL pipeline** → Name, Standard-Catalog/-Schema, Erstellungsoption (**Start with sample code in SQL/Python**, **Start with a single transformation**, **Add existing assets**, **Create a source-controlled project**). Eine ETL-Pipeline kann SQL+Python mischen — die gewählte Sprache betrifft nur den Beispielcode. Default: Unity Catalog, Current Channel, Serverless Compute. Alternative Wege: Workspace-Browser, **Jobs & Pipelines → New → ETL Pipeline**.

- **Produktedition** (Abschnitt 2), **Pipeline mode** (Abschnitt 8).
- Kontinuierlicher Produktivbetrieb: Pipeline in **Continuous Job** einbetten statt eingebauten Continuous-Modus.
- **Notifications:** 4 Ereignisse — Update erfolgreich; Update fehlgeschlagen (jeder Fehlschlag); Update fatal fehlgeschlagen (nur fatale); einzelner Data Flow fehlgeschlagen.
- **Parameters-Feld:** Key-Value für SQL Named-Parameter-Syntax, überschreibbar beim Update-Start/Job.
- **Configuration-Feld:** Spark-Config (z. B. `pipelines.enzyme.enabled`); Python zusätzlich via `spark.conf.get()`.
- **Tags:** Key-Value, sichtbar in Liste — **nicht** mit Billing verknüpft.
- **Preview-Channel:** zum Testen kommender Runtime-Änderungen/Features.

**Wirksamwerden von Änderungen:** gilt ab dem nächsten Update. Bei **Continuous Job**: kein Neustart nötig, Änderung greift beim nächsten Update (Job-Zeitplan bestimmt Ausführungsmodus, nicht die Pipeline-eigene Pipeline-Mode-Einstellung). Bei eingebauter **Pipeline mode**-Einstellung: Continuous-Pipelines starten automatisch neu (kann aktives Update unterbrechen); Triggered→Continuous startet automatisch neues Update; Continuous→Triggered bricht aktives Update ab.

- Quellcode-Konfiguration über Asset-Browser; Default-Ordner `transformations`; Reihenfolge egal (automatische Abhängigkeitsanalyse).
- Externe Abhängigkeiten/Python-Module: über Git Folders oder Workspace-Dateien, v. a. für Code über mehrere Pipelines/Notebooks hinweg.

## 2. Produktedition wählen

| Edition | Geeignet für |
|---|---|
| `Core` | Streaming-Ingest, ohne CDC/Expectations |
| `Pro` | Streaming-Ingest + CDC (`Core` + Tabellen-Updates anhand Quelländerungen) |
| `Advanced` | Streaming-Ingest + CDC + Expectations (`Core`/`Pro` + Datenqualitäts-Constraints) |

- Wählbar bei Erstellung/Bearbeitung; jede Pipeline kann eigene Edition haben.
- Nicht unterstütztes Feature (z. B. Expectations bei `Core`) → erklärende Fehlermeldung, Umstellung auf passende Edition möglich.
- Pipelines behalten **60 Tage** Update-Historie in UI/API; aktive Updates immer sichtbar, ältere aus Listen ausgeschlossen (bleiben im Event-Log).

## 3. Ziel-Catalog und -Schema

**Default location for data assets** (Konfigurations-UI) legt Standard-Catalog/-Schema fest — für alle Dataset-Definitionen/Lesevorgänge, sofern nicht in der Query überschrieben. (Legacy-Modus: virtuelles `LIVE`-Schema, im Default-Modus ignoriert.)

```python
from pyspark import pipelines as dp

@dp.materialized_view(name="main.stores.regional_sales")
def func():
  return spark.read.table("partners")
```

```sql
CREATE OR REPLACE MATERIALIZED VIEW main.stores.regional_sales
  AS SELECT * FROM partners;
-- Ergebnis: Tabelle main.stores.regional_sales, unabhängig vom Pipeline-Default-Catalog/-Schema
```

`USE CATALOG` / `USE SCHEMA` — gültig nur innerhalb der Datei/des Notebooks; nachfolgende un-/teilqualifizierte Identifier lösen sich dagegen auf statt gegen die Pipeline-Defaults.

| Operation | Verhalten bei nicht existierendem Dataset |
|---|---|
| Read | Update schlägt fehl |
| Write | Update versucht, Dataset (+ nötigenfalls Schema) zu erstellen |

> **Wichtig:** "Dataset existiert nicht" kann auch bei unzureichenden Berechtigungen erscheinen.

## 4. Classic Compute konfigurieren

Serverless empfohlen für neue Pipelines. Classic bei: bestimmten Instanztypen, benutzerdefinierten Compute-Policies, Init-Skripten, extern installiertem JDBC-Treiber, Region ohne Serverless. Classic braucht Compute-Erstellungsberechtigung (uneingeschränkt oder Policy-Zugriff) — Serverless nicht. Manche Einstellungen (Spark-Version, Cluster-Namen) nicht manuell setzbar (Pipeline-Runtime verwaltet Lebenszyklus).

**Umschalten:** Settings → Compute → Stift-Symbol → **Serverless**-Checkbox deaktivieren → **Save**.

**Compute Policy** (optional, von Workspace-Admin): bei Pipelines-API `"apply_policy_default_values": true` in `clusters` nötig:

```json
{
  "clusters": [
    { "label": "default", "policy_id": "<policy-id>", "apply_policy_default_values": true }
  ]
}
```

- **Compute-Tags:** benutzerdefiniert, auf Cloud-Ressourcen + Usage-System-Tabellen erfasst — via UI oder JSON.
- **Instance-Typen:** standardmäßig automatisch gewählt; manuell via Settings → Compute → Stift → Advanced → **Worker type**/**Driver type**.

**Update- vs. Maintenance-Cluster:** Update-Cluster (Updates), Maintenance-Cluster (tägliche Pflege inkl. Predictive Optimization). Standardmäßig gilt Konfig für beide; `label`-Feld im JSON: `maintenance`, `updates`, `default` (beide). Bei Konflikt überschreibt `updates`/`maintenance` `default`. Maintenance-Cluster nur genutzt bei: Hive-Metastore-Pipelines, fehlenden Serverless-Nutzungsbedingungen, falsch konfiguriertem Private Link zu Serverless.

```json
{
  "clusters": [
    { "label": "default", "autoscale": { "min_workers": 1, "max_workers": 5, "mode": "ENHANCED" } },
    { "label": "updates", "spark_conf": { "key": "value" } }
  ]
}
```

```json
{
  "clusters": [
    { "label": "updates", "node_type_id": "Standard_D12_v2", "driver_node_type_id": "Standard_D3_v2" }
  ]
}
```

**Compute-Shutdown verzögern** (`pipelines.clusterShutdown.delay`):

```json
{ "configuration": { "pipelines.clusterShutdown.delay": "60s" } }
```
Default: **0s** bei automatischem Retry-/Restart-Verhalten, **2h** bei Ad-hoc-Updates (Fast-Start/Debugging). `autotermination_minutes` in einer Compute Policy führt zu Fehler (Compute fährt automatisch bei Nichtnutzung herunter).

**Single-Node-Compute** (geringe Datenmengen):

```json
{ "clusters": [ { "num_workers": 0 } ] }
```

**Liquid Clustering** direkt in der ST-/MV-Definition, kein separates `OPTIMIZE` nötig:

```sql
-- Databricks wählt die Clustering-Spalten automatisch anhand der Query-Historie
CREATE OR REFRESH STREAMING TABLE my_table
CLUSTER BY AUTO
AS SELECT * FROM STREAM source_table;

-- Explizit angegebene Clustering-Spalten
CREATE OR REFRESH STREAMING TABLE my_table
CLUSTER BY (region, order_date)
AS SELECT * FROM STREAM source_table;
```
`AUTO`: passt bei unbekannten/sich entwickelnden Query-Mustern (Databricks beobachtet Nutzung, kein initialer Key). `(columns)`: passt bei bekannten stabilen Filterspalten, volle Kontrolle, vorhersehbares Layout. Hybrid möglich: explizite Startspalten + Auto-Clustering zusätzlich.

## 5. Serverless Compute

Von Databricks verwaltet, kaum Infrastrukturkonfiguration nötig; empfohlen für neue Pipelines. **Immer** Unity Catalog. Structured-Streaming-Trigger-Limitierungen gelten **nicht** für Pipeline-Modi — Triggered/Continuous/Real-Time alle unterstützt. `clusters`-Objekt in Serverless-JSON manuell hinzufügen → Fehler. Azure Private Link + Serverless: Databricks-Kontakt nötig.

Voraussetzungen: UC aktiviert; Serverless-fähige Region; akzeptierte Nutzungsbedingungen. Keine Compute-Erstellungsberechtigung nötig (alle Nutzer standardmäßig). Neue Pipelines: Serverless default.

Auch für Serverless: **Continuous**-Modus, Notifications, **Configuration**-Feld, **Preview**-Channel, externe Python-Deps via **Environment** — aber: `dbutils.library.restartPython()` **nicht** unterstützt (keine Laufzeit-Installation/-Reload).

**Serverless Usage Policy (Public Preview):** benutzerdefinierte Tags für Billing-Zuordnung — nach **Serverless**-Checkbox erscheint **Usage policy**-Auswahl; Tags von Policy geerbt, nur von Admins editierbar. Bestehende Pipelines werden bei neuer Policy-Zuweisung **nicht** automatisch getaggt (manuell nötig).

**Performance-Modus** (Triggered, **Performance optimized**):
- **Standard** (aus): niedrigere Kosten, Start typ. **innerhalb 4–6 Min.**
- **Optimized** (an): schnellerer Start/Ausführung für zeitkritische Workloads.

Gleiche SKU, Standard verbraucht weniger DBUs. Standard Mode + Continuous-Pipeline: nur via Continuous Job, mit deaktivierter **Performance optimized**-Checkbox im Zeitplan.

**Serverless-Features:** Incremental Refresh für MV (Full Refresh als Fallback wenn inkrementell nicht möglich); Stream Pipelining (Micro-Batches gleichzeitig, standardmäßig an); Vertical Autoscaling (Abschnitt 6).

**Konvertierung zu Serverless:** **Jobs & Pipelines** → Pipeline → **Settings** → Compute → Stift → **Serverless**-Checkbox aktivieren → **Save**.
> **Wichtig:** Aktivieren entfernt alle konfigurierten Compute-Einstellungen; bei Rückumstellung müssen sie neu konfiguriert werden.

DBU-Nutzung: über Billable-Usage-System-Tabelle ermittelbar.

## 6. Autoscaling

**Enhanced Autoscaling** — standardmäßig aktiv für neue Pipelines; bei Serverless immer aktiv, nicht deaktivierbar. Ggü. regulärem Autoscaling: für Streaming-/Batch-Workloads optimiert, proaktives Herunterskalieren unterausgelasteter Knoten ohne Task-Fehlschläge (reguläres Autoscaling nur bei komplett leerlaufenden Knoten).

Zwei Steuer-Metriken: **Task Slot Utilization**, **Task Queue Size**.

**Aktivieren:** **Cluster mode** → **Enhanced autoscaling**, oder `mode: "ENHANCED"` in `autoscale`:

```json
{
  "clusters": [
    { "autoscale": { "min_workers": 5, "max_workers": 10, "mode": "ENHANCED" } }
  ]
}
```
Produktion: **Min workers** auf Default lassen, **Max workers** nach Budget/Priorität (`max_workers` ≥ `min_workers`).

- Nur für `updates`-Cluster verfügbar; `maintenance`-Cluster nutzen Legacy Autoscaling.
- Modi: `LEGACY`, `ENHANCED`.
- Continuous-Ausführung: nach Config-Änderung automatischer Neustart, kurze erhöhte Latenz bis Einpendelung.
- Serverless: keine Worker konfigurierbar; **Max workers** begrenzt Kosten (kann Latenz erhöhen).

**Monitoring (Classic, Event-Typ `autoscale`):**

| Event | Meldung |
|---|---|
| Resize started | `Scaling [up or down] to <y> executors from current cluster size of <x>` |
| Resize succeeded | `Achieved cluster size <x> for cluster <cluster-id> with status SUCCEEDED` |
| Resize partially succeeded | `... status PARTIALLY_SUCCEEDED` |
| Resize failed | `... status FAILED` |

**Vertical Autoscaling** (Serverless, für **alle** Serverless-Pipelines inkl. Standalone MV/ST): ergänzt horizontales Scaling um automatische Wahl kosteneffizienter Instanztypen ohne OOM. Erkennt OOM-Fehlschläge → größere Instanztypen (automatischer Retry bei Retry-/Restart-Verhalten, sonst beim nächsten manuellen Update); erkennt durchgängige Unterauslastung → skaliert Instanztypen für nächstes Update herunter.

## 7. Echtzeit-Verarbeitung (Real-Time Mode, Public Preview)

**Status:** Public Preview, DBR 18.1.3, Preview-Channel. End-to-End-Latenz **bis zu 5 ms** — Betrugserkennung, Echtzeit-Personalisierung. Auch direkt in Structured Streaming außerhalb Pipelines.

**Wie niedrige Latenz erreicht wird:**
- **Long-running Batches** — Verarbeitung sobald Daten da sind, innerhalb langer Batches (Default 5 Min.).
- **Simultaneous Stage Scheduling** — alle Stages gleichzeitig eingeplant (genug Task-Slots nötig).
- **Streaming Shuffle** — Daten fließen zwischen Stages sofort weiter statt auf Stage-Abschluss zu warten.

`pipelines.trigger.interval` steuert Checkpoint-Häufigkeit (State/Offsets) — länger = weniger Overhead/mehr Recovery-Zeit, kürzer = mehr Durability/mehr Overhead.

Real-Time Mode = spezialisierter Continuous-Trigger-Typ (Continuous ist Voraussetzung, ergänzt Flow-Level-Optimierungen für Sub-Sekunden-Latenz).

Voraussetzungen: DBR 18.1.3 auf Preview-Channel; Classic oder Serverless.

**Konfiguration (3 Schritte):**
1. **Pipeline mode** = **Continuous** (`"continuous": true`).
2. Advanced → Spark config: `spark.databricks.streaming.realTimeMode.enabled = true`.
3. Real-Time-Update-Flow definieren (`dp.create_sink()` + `@dp.update_flow` mit `pipelines.trigger: "RealTime"`):

```python
from pyspark import pipelines as dp

dp.create_sink(
    "my_kafka_sink", "kafka",
    { "kafka.bootstrap.servers": "<bootstrap-servers>", "topic": "<output-topic>" }
)

@dp.update_flow(
    name="my_rtm_flow",
    target="my_kafka_sink",
    spark_conf={
        "pipelines.trigger": "RealTime",
        "pipelines.trigger.interval": "5 minutes",  # optional, Standard: 5 minutes
    }
)
def my_real_time_flow():
    return (
        spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", "<bootstrap-servers>")
            .option("subscribe", "<input-topic>")
            .load()
    )
```
`pipelines.trigger` erforderlich (`"RealTime"`); `pipelines.trigger.interval` optional (Default `"5 minutes"`).

**Broadcast-Join-Anreicherung** (nur Stream-zu-Static, **kein** Stream-zu-Stream):

```python
from pyspark.sql.functions import broadcast, expr

@dp.update_flow(
    name="enriched_events_flow", target="enriched_output_sink",
    spark_conf={"pipelines.trigger": "RealTime", "pipelines.trigger.interval": "5 minutes"}
)
def enriched_events():
    lookup = spark.read.table("catalog.schema.lookup_table")
    return (
        spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", broker_address)
            .option("subscribe", input_topic)
            .load()
            .withColumn("event_key", expr("CAST(value AS STRING)"))
            .join(broadcast(lookup), expr("event_key = lookup_key"))
            .select("event_key", "lookup_value", "timestamp")
    )
```

**Aggregation** (zustandsbehaftetes `groupBy`; `spark.sql.shuffle.partitions` an Input-Partitionen anpassen):

```python
@dp.update_flow(
    name="event_counts_flow", target="event_counts_sink",
    spark_conf={"pipelines.trigger": "RealTime", "pipelines.trigger.interval": "5 minutes", "spark.sql.shuffle.partitions": "8"}
)
def event_counts():
    return (
        spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", broker_address)
            .option("subscribe", input_topic)
            .load()
            .selectExpr("CAST(key AS STRING) AS event_type", "timestamp")
            .groupBy(col("event_type")).count()
    )
```

**Unterstützte Quellen/Senken:**

| Connector | Quelle | Senke | Hinweis |
|---|---|---|---|
| Apache Kafka | Ja | Ja | — |
| AWS MSK | Ja | Ja | Kafka-kompatibel |
| Azure Event Hubs (Kafka-Connector) | Ja | Ja | Kafka-kompatibel |
| Amazon Kinesis | Ja | Nein | nur EFO-Modus |
| Delta | Nein | Nein | — |

**Compute-Sizing** (Task-Slots müssen alle Tasks über alle Stages abdecken):

| Pipeline-Typ | Konfiguration | Benötigte Task-Slots |
|---|---|---|
| Single-Stage stateless (Kafka-Quelle+Senke) | `maxPartitions` = 8 | 8 |
| Two-Stage stateful (Kafka+Shuffle) | `maxPartitions` = 8, Shuffle-Partitionen = 20 | 28 |
| Three-Stage (Kafka+2 Shuffles) | `maxPartitions` = 8, 2×20 Shuffle | 48 |

Ohne `maxPartitions`: Partitionsanzahl des Kafka-Topics wird verwendet.

**Unterstützte Operatoren:** Selection/Projection, Scala-/Python-UDFs (mit Einschränkungen), Aggregationen (`sum`, `count`, `max`, `min`, `avg`), Tumbling/Sliding Windowing, `dropDuplicates` (unbounded state), Broadcast Table Join, `transformWithState` (Verhaltensunterschiede), `union` (Einschränkungen).
**Nicht unterstützt:** Session Windowing, `dropDuplicatesWithinWatermark`, Stream-to-Stream Join, `forEach`, `flatMapGroupsWithState`, `mapPartitions`, `forEachBatch`.

Bei `transformWithState`: `handleInputRows` läuft pro Zeile (nicht pro Schlüssel/Batch); Event-Time-Timer nicht unterstützt (Processing-Time-Timer feuern beim Batch-Ende ohne Daten); `transformWithStateInPandas` nicht unterstützt. Für Pandas-UDFs: `spark.sql.execution.arrow.maxRecordsPerBatch = 1` minimiert Latenz (kostet Durchsatz; bei Durchsatzbedarf `100`+).

**Monitoring** — `StreamingQueryProgress.latencies` via `StreamingQueryListener`/`lastProgress`:

| Metrik | Beschreibung |
|---|---|
| `processingLatencyMs` | Einlesen bis vollständige Flow-Verarbeitung |
| `sourceQueuingLatencyMs` | Schreiben in Message Bus bis erstes Einlesen |
| `e2eLatencyMs` | Gesamte End-to-End-Latenz |

Jeweils p50/p90/p95/p99. **Limitierung:** empfohlen 1 Real-Time-Flow/Pipeline (mehrere möglich, aber Task-Slot-Konkurrenz erhöht Latenz).

## 8. Pipeline-Modus festlegen

**Triggered** (Standard): aktualisiert alle verfügbaren Daten, stoppt dann — Compute nur für Update-Dauer. **Continuous**: hält Tabellen laufend aktuell — niedrigere Latenz, dauerhafter Cluster; nur bei nachgewiesenem Low-Latency-Bedarf wählen.

## 9. Workflows-Integration

Pipeline löst interne Dataset-Abhängigkeiten automatisch, handhabt einfache pipeline-interne Orchestrierung selbst. Für bedingte Ausführung, Verzweigung nach Task-Ergebnissen, Retries, Koordination mit anderen Arbeitsarten: dedizierter Orchestrator — **Lakeflow Jobs**, **Apache Airflow**, **Azure Data Factory**.

Vorbereitung: jede Pipeline sollte klar abgegrenzte, separat planbare Einheit sein — große Pipelines ggf. aufteilen (Tabellen per `ALTER ... SET TBLPROPERTIES("pipelines.pipelineId"=...)` in eine neue Pipeline verschieben, ohne Full Refresh/Datenverlust).

**Lakeflow Jobs:** Pipeline eingebunden über den **Pipeline**-Task.

**Apache Airflow:** Workflows als DAGs (Python). Einbindung über `DatabricksSubmitRunOperator`. Anforderungen: Airflow ≥ 2.1.0, Databricks-Provider ≥ 2.1.0.

```python
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from airflow.utils.dates import days_ago

default_args = {'owner': 'airflow'}

with DAG('ldp', start_date=days_ago(2), schedule_interval="@once", default_args=default_args) as dag:
  opr_run_now = DatabricksSubmitRunOperator(
    task_id='run_now',
    databricks_conn_id='CONNECTION_ID',
    pipeline_task={"pipeline_id": "8279d543-063c-4d63-9926-dae38e35ce8b"}
  )
```

**Azure Data Factory:**
> **Wichtig:** Retry sowohl in Pipeline als auch ADF-Aktivität konfiguriert → Gesamt-Retry = **Produkt** beider Werte (Beispiel: 5 × 3 = bis zu **15** Versuche). Retry auf einer Seite begrenzen. Pipeline-seitig: `pipelines.numUpdateRetryAttempts`.

Einbindung über ADF-**Web-Aktivität** (ruft Pipeline-REST-API auf):
1. Data Factory öffnen → **Open Azure Data Factory Studio**.
2. **New → Pipeline** → **Web**-Aktivität aus **Activities** auf Canvas.
3. Tab **Settings**: **URL** `https://<databricks-instance>/api/2.0/pipelines/<pipeline-id>/updates`, **Method** `POST`, **Headers** `Authorization: Bearer <personal-access-token>`, **Body** z. B. `{"full_refresh": "true"}` (leer `{}` ohne Zusatzparameter).

> **Sicherheitshinweis:** Für automatisierte Tools: Personal Access Tokens von Service Principals statt Workspace-Nutzern.

Testen: **Debug** in ADF-UI (Ausgabe im Tab **Output**). Der `updates`-Request ist **asynchron** (kehrt bei Update-Start zurück, nicht -Abschluss) → Warten-Muster: **Wait-Aktivität** + Web-Aktivität (Status via Pipeline-Update-Details, Feld `state`) als Abbruchbedingung einer **Until-Aktivität**, optional mit **Set-Variable-Aktivität**.

---

**Stand:** 2026-09-14.
