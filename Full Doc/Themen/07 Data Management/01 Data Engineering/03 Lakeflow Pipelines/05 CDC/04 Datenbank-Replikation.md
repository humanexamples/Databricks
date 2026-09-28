# Externe RDBMS-Tabelle mit AUTO CDC replizieren — Referenz

Dieses Dokument zeigt das End-to-End-Muster, um eine Tabelle aus einem externen relationalen Datenbanksystem (RDBMS) mit der `AUTO CDC`-API in eine Lakeflow-Declarative-Pipeline zu replizieren — kombiniert einen einmaligen Voll-Kopie-Lauf (`once`-Flow) mit fortlaufender Change-Feed-Verarbeitung. Baut auf `CDC-Grundlagen.md` (diesem Ordner) auf.

## Abschnittsübersicht

1. [Ziel dieses Musters](#ziel)
2. [Voraussetzungen](#voraussetzungen)
3. [Source Views einrichten](#source-views)
4. [Initiale Befüllung (Once Flow)](#once-flow)
5. [Fortlaufender Change Feed (Change Flow)](#change-flow)
6. [Weitere Überlegungen](#ueberlegungen)

---

## <a id="ziel">1. Ziel dieses Musters</a>

Dieses Muster eignet sich, um SCD-Tabellen aufzubauen oder eine Zieltabelle mit einem externen System of Record synchron zu halten. Behandelt werden:

- verbreitete Muster zum Aufsetzen der Quellen,
- eine einmalige Vollkopie der bestehenden Daten über einen `once`-Flow,
- fortlaufende Ingestion neuer Änderungen über einen `change`-Flow.

## <a id="voraussetzungen">2. Voraussetzungen</a>

Dieses Muster setzt Zugriff auf folgende Datasets aus der Quelle voraus:

- Ein vollständiger Snapshot der Quelltabelle im Cloud-Speicher — für die initiale Befüllung.
- Ein fortlaufender Change Feed, abgelegt am selben Cloud-Speicherort (z. B. über Debezium, Kafka oder Log-basiertes CDC) — Eingabe für den laufenden `AUTO CDC`-Prozess.

## <a id="source-views">3. Source Views einrichten</a>

Zunächst werden zwei Source Views definiert, um die Zieltabelle `rdbms_orders` aus einem Cloud-Speicherpfad `orders_snapshot_path` zu befüllen. Beide werden als Streaming Views über Rohdaten im Cloud-Speicher aufgebaut. Die Nutzung von Views ist effizienter, da Daten nicht erst geschrieben werden müssen, bevor sie im `AUTO CDC`-Prozess verwendet werden können.

- Die erste Source View ist ein vollständiger Snapshot (`full_orders_snapshot`).
- Die zweite ist ein fortlaufender Change Feed (`rdbms_orders_change_feed`).

Die Beispiele nutzen Cloud-Speicher als Quelle, es lässt sich aber jede von Streaming Tables unterstützte Quelle verwenden.

### `full_orders_snapshot()`

Liest den initialen vollständigen Snapshot der Orders-Daten.

**Python** — nutzt `spark.readStream` mit Auto Loader (`format("cloudFiles")`), liest JSON-Dateien aus einem über `orders_snapshot_path` definierten Verzeichnis, setzt `includeExistingFiles` auf `true`, um bereits vorhandene historische Daten im Pfad zu verarbeiten, setzt `inferColumnTypes` auf `true` zur automatischen Schema-Inferenz, und gibt alle Spalten über `.select("*")` zurück:

```python
@dp.view()
def full_orders_snapshot():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.includeExistingFiles", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(orders_snapshot_path)
        .select("*")
    )
```

**SQL** — übergibt Optionen als Map von String-Schlüssel-Wert-Paaren; `orders_snapshot_path` steht als SQL-Variable zur Verfügung (z. B. über Pipeline-Parameter definiert oder manuell interpoliert):

```sql
CREATE OR REFRESH VIEW full_orders_snapshot
AS SELECT *
FROM STREAM read_files("${orders_snapshot_path}", "json", map(
  "cloudFiles.includeExistingFiles", "true",
  "cloudFiles.inferColumnTypes", "true"
));
```

### `rdbms_orders_change_feed()`

Liest inkrementelle Änderungsdaten (z. B. aus CDC-Logs oder Change Tables) aus `orders_cdc_path`, wobei CDC-artige JSON-Dateien regelmäßig in diesen Pfad abgelegt werden:

```python
@dp.view()
def rdbms_orders_change_feed():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.includeExistingFiles", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(orders_cdc_path)
    )
```

```sql
CREATE OR REFRESH VIEW rdbms_orders_change_feed
AS SELECT *
FROM STREAM read_files("${orders_cdc_path}", "json", map(
  "cloudFiles.includeExistingFiles", "true",
  "cloudFiles.inferColumnTypes", "true"
));
```

(`${orders_cdc_path}` ist auch hier eine Variable, interpolierbar über Pipeline-Einstellungen oder explizit im Code gesetzt.)

## <a id="once-flow">4. Initiale Befüllung (Once Flow)</a>

Nachdem die Quellen eingerichtet sind, führt `AUTO CDC`-Logik beide Quellen in einer Ziel-Streaming-Table zusammen. Zunächst wird ein einmaliger `AUTO CDC`-Flow mit `ONCE=TRUE` verwendet, um den vollständigen Inhalt der RDBMS-Tabelle in eine Streaming Table zu kopieren. Das befüllt die Zieltabelle mit historischen Daten, ohne sie bei künftigen Updates erneut abzuspielen.

```python
from pyspark import pipelines as dp

# Step 1: Create the target streaming table
dp.create_streaming_table("rdbms_orders")

# Step 2: Once Flow — Load initial snapshot of full RDBMS table
dp.create_auto_cdc_flow(
  flow_name = "initial_load_orders",
  once = True,  # one-time load
  target = "rdbms_orders",
  source = "full_orders_snapshot",  # e.g., ingested from JDBC into bronze
  keys = ["order_id"],
  sequence_by = "timestamp",
  stored_as_scd_type = "1"
)
```

```sql
-- Step 1: Create the target streaming table
CREATE OR REFRESH STREAMING TABLE rdbms_orders;

-- Step 2: Once Flow for initial snapshot
CREATE FLOW rdbms_orders_hydrate
AS AUTO CDC ONCE INTO rdbms_orders
FROM stream(full_orders_snapshot)
KEYS (order_id)
SEQUENCE BY timestamp
STORED AS SCD TYPE 1;
```

Der `once`-Flow läuft nur ein einziges Mal. Nach der Pipeline-Erstellung zu `full_orders_snapshot` hinzugefügte neue Dateien werden ignoriert.

**Wichtig:** Ein Full Refresh der `rdbms_orders`-Streaming-Table führt den `once`-Flow erneut aus. Wurden die initialen Snapshot-Daten im Cloud-Speicher zwischenzeitlich entfernt, führt das zu Datenverlust.

## <a id="change-flow">5. Fortlaufender Change Feed (Change Flow)</a>

Nach der initialen Snapshot-Befüllung wird ein weiterer `AUTO CDC`-Flow verwendet, um fortlaufend Änderungen aus dem CDC-Feed der RDBMS zu übernehmen — hält `rdbms_orders` mit Inserts, Updates und Deletes aktuell.

```python
from pyspark import pipelines as dp

# Step 3: Change Flow — Ingest ongoing CDC stream from source system
dp.create_auto_cdc_flow(
  flow_name = "orders_incremental_cdc",
  target = "rdbms_orders",
  source = "rdbms_orders_change_feed", # e.g., ingested from Kafka or Debezium
  keys = ["order_id"],
  sequence_by = "timestamp",
  stored_as_scd_type = "1"
)
```

```sql
-- Step 3: Continuous CDC ingestion
CREATE FLOW rdbms_orders_continuous
AS AUTO CDC INTO rdbms_orders
FROM stream(rdbms_orders_change_feed)
KEYS (order_id)
SEQUENCE BY timestamp
STORED AS SCD TYPE 1;
```

## <a id="ueberlegungen">6. Weitere Überlegungen</a>

| Thema | Hinweis |
|---|---|
| Backfill-Idempotenz | Ein `once`-Flow läuft nur erneut, wenn die Zieltabelle vollständig refresht wird. |
| Mehrere Flows | Mehrere Change Flows lassen sich einsetzen, um Korrekturen, verspätet eintreffende Daten oder alternative Feeds einzumischen — alle müssen jedoch Schema und Keys teilen. |
| Full Refresh | Ein Full Refresh der `rdbms_orders`-Streaming-Table führt den `once`-Flow erneut aus — das kann zu Datenverlust führen, wenn der initiale Cloud-Speicherort die Snapshot-Daten zwischenzeitlich bereinigt hat. |
| Ausführungsreihenfolge der Flows | Die Reihenfolge der Flow-Ausführung spielt keine Rolle — das Endergebnis ist dasselbe. |
