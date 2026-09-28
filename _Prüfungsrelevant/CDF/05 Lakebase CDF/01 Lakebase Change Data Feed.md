[← Übersicht](../00%20Uebersicht.md)

# Lakebase Change Data Feed

> Quellen: [Lakebase Change Data Feed](https://docs.databricks.com/aws/en/oltp/projects/lakebase-cdf) (Stand 11.06.2026) · [Lakebase use cases](https://docs.databricks.com/aws/en/oltp/projects/use-cases) · [Integrations](https://docs.databricks.com/aws/en/oltp/projects/lakehouse-integrations) · [Glossar](https://docs.databricks.com/aws/en/resources/glossary) · [Lakebase Release Notes](https://docs.databricks.com/aws/en/release-notes/lakebase/) · [Lakebase-Sink für Structured Streaming](https://docs.databricks.com/aws/en/structured-streaming/lakebase)

> **Status:** Public Preview (seit 12.05.2026; vorher ab 12.03.2026 als Beta „Lakehouse sync“). Ein **Workspace-Admin** muss das Preview auf der Previews-Seite aktivieren.

## Was ist Lakebase CDF, und wie unterscheidet es sich vom Delta-CDF?

**Lakebase** ist die OLTP-Datenbank (Postgres) von Databricks. **Lakebase CDF** erfasst jedes `INSERT`, `UPDATE` und `DELETE` auf einer Lakebase-Postgres-Tabelle aus dem **Write-Ahead Log (WAL)** und speichert es als **neue Zeile** in einer **Unity-Catalog-Managed-Delta-Tabelle**. Die Änderungen werden gebündelt und etwa **alle 15 Sekunden** geschrieben.

| | Delta-CDF | Lakebase CDF |
|---|---|---|
| Quelle | Delta-/Iceberg-Tabelle im Lakehouse | Postgres-Tabelle in Lakebase |
| Wo liegen die Änderungen? | in der Tabelle selbst (gelesen per `table_changes` / `readChangeFeed`) | in einer **eigenen Delta-Tabelle** `lb_<table_name>_history` |
| Metadatenspalten | `_change_type`, `_commit_version`, `_commit_timestamp` | `_pg_change_type`, `_pg_lsn`, `_pg_xid`, `_timestamp`, `_sort_by` |
| Lebensdauer | transient (Retention) | dauerhafte, **unveränderliche** Delta-Historie |
| Richtung | Lakehouse → nachgelagert | Postgres → Lakehouse |

Die Zieltabellen haben **dieselbe Form wie der Delta-CDF** (dieselben vier Änderungstypen). Deshalb funktionieren dieselben nachgelagerten Muster, **ohne externen CDC-Stack**. Der Erfassungspfad läuft auf **eigener Compute**, sodass Produktionsabfragen nicht beeinträchtigt werden.

> Die **umgekehrte Richtung** (Lakehouse → Lakebase) übernehmen **Synced Tables** oder der **Lakebase-Sink** für Structured Streaming → [03 Synced Tables und LTAP](03%20Synced%20Tables%20und%20LTAP.md).

## Einsatzfälle

| Einsatzfall | Beschreibung |
|---|---|
| ETL-Pipelines | Lakebase als **Bronze-Quelle** für Medallion-Pipelines; inkrementelle Lakeflow Pipelines oder Structured-Streaming-Jobs auf dem Change Feed |
| Audit Logs | vollständige, abfragbare Historie jeder Änderung für Compliance und Forensik; die Historie ist unveränderliches Delta |
| Externe Systeme | offenes Format: auch Nicht-Databricks-Reader können den Feed direkt lesen |

---

## Voraussetzungen

- **Lakebase-Projekt** mit Postgres **16, 17 oder 18**.
- **Quelldatenbank:** beliebige **eine** Datenbank im Projekt (ein Feed pro Datenbank), nicht nur `databricks_postgres`.
- **Unity Catalog:** Die einrichtende Identität braucht `USE CATALOG`, `USE SCHEMA` und `CREATE TABLE` auf Zielkatalog und -schema.
- **Default Storage:** Zielkataloge mit Default Storage werden **nicht** unterstützt. *(Free Edition: eigenen Katalog anlegen, dessen Managed Storage eine External Location ist.)*
- **Projektrechte:** Die Postgres-Rolle braucht `CAN MANAGE` auf dem Lakebase-Projekt (Owner haben das standardmäßig).
- **Datentypen:** Typen ohne direktes Delta-Gegenstück werden als `STRING` gespeichert.

---

## Einrichtung

### Schritt 1: `REPLICA IDENTITY FULL` setzen

Standardmäßig protokolliert Postgres bei Updates und Deletes nur den Primärschlüssel. `REPLICA IDENTITY FULL` sorgt dafür, dass der **Vorher- und Nachher-Zustand** der Zeile im WAL landet. Das braucht CDF für eine vollständige Historie.

Einzelne Tabelle:

```sql
ALTER TABLE <table_name> REPLICA IDENTITY FULL;
```

Alle bestehenden Tabellen eines Schemas (hier `public`):

```sql
DO $$
DECLARE r record;
BEGIN
  FOR r IN
    SELECT table_schema, table_name
    FROM information_schema.tables
    WHERE table_schema = 'public'
      AND table_type = 'BASE TABLE'
  LOOP
    EXECUTE format(
      'ALTER TABLE %I.%I REPLICA IDENTITY FULL;',
      r.table_schema, r.table_name
    );
  END LOOP;
END $$;
```

Automatisch für **künftige** Tabellen per Event Trigger:

```sql
CREATE OR REPLACE FUNCTION public.set_full_replica_identity()
RETURNS event_trigger
LANGUAGE plpgsql
AS $$
DECLARE
  obj record;
BEGIN
  FOR obj IN
    SELECT * FROM pg_event_trigger_ddl_commands()
    WHERE command_tag = 'CREATE TABLE'
  LOOP
    EXECUTE format(
      'ALTER TABLE %s REPLICA IDENTITY FULL;',
      obj.object_identity
    );
  END LOOP;
END $$;

CREATE EVENT TRIGGER set_full_replica_identity_on_create
ON ddl_command_end
WHEN TAG IN ('CREATE TABLE')
EXECUTE FUNCTION public.set_full_replica_identity();
```

Schleife und Event Trigger kombiniert decken bestehende **und** künftige Tabellen ab.

Prüfen, welche Tabellen bereit sind:

```sql
SELECT n.nspname AS table_schema,
       c.relname AS table_name,
       CASE c.relreplident
         WHEN 'd' THEN 'default'
         WHEN 'n' THEN 'nothing'
         WHEN 'f' THEN 'full'
         WHEN 'i' THEN 'index'
       END AS replica_identity
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind = 'r'
  AND n.nspname = 'public'
ORDER BY n.nspname, c.relname;
```

Nur Zeilen mit `replica_identity = 'full'` sind bereit für CDF.

### Schritt 2: Feed starten

Lakebase CDF wird auf **Schema-Ebene** konfiguriert: Alle aktuellen **und künftigen** Tabellen des Quellschemas sind enthalten.

1. Im Workspace **Lakebase Postgres** über den App-Switcher (oben rechts) öffnen.
2. Projekt und Branch wählen (z. B. `production` oder `main`).
3. **Branch overview** öffnen (Branch-Name im Breadcrumb), Tab **Lakebase CDF**.
4. **Start** klicken und konfigurieren: *Database* (Quelldatenbank, Pflichtauswahl) · *Schema* (Quellschema) · *To Catalog* (UC-Zielkatalog) · *Schema* (UC-Zielschema).
5. **Start** bestätigen.

Die Tabellen erscheinen als **`lb_<table_name>_history`** im Zielschema. Der Tab zeigt zwei Unterreiter:

- **Schemas:** Quellschema, Ziel in Unity Catalog, Status.
- **Tables:** Quelltabelle, Zieltabelle, Status (`Streaming` oder `Snapshotting`), **Committed LSN** (während des Initial-Snapshots `-`), letzte Aktualisierung.

Status auch direkt in Postgres:

```sql
SELECT * FROM wal2delta.tables;
```

Liefert pro Tabelle `table_oid`, `status` (`STREAMING` oder `SNAPSHOTTING`), `committed_lsn` und `last_write_time`.

> **Was ist `wal2delta`?** Lakebase CDF basiert auf der Postgres-Erweiterung **wal2delta**, die in der Lakebase-Compute läuft. Sie nutzt **Logical Decoding**, um WAL-Änderungen zu erfassen, und schreibt sie in Delta-Tabellen in Unity Catalog.

Einrichtung per API: [02 Quickstart und REST-API](02%20Quickstart%20und%20REST-API.md)

---

## Schema der Zieltabelle

Eine Delta-Tabelle pro Quelltabelle (`lb_<table_name>_history`), mit allen Quellspalten plus:

| Spalte | Typ | Beschreibung |
|---|---|---|
| `_pg_change_type` | TEXT | `insert`, `delete`, `update_preimage` oder `update_postimage` |
| `_pg_lsn` | BIGINT | Postgres Log Sequence Number |
| `_pg_xid` | INTEGER | Postgres Transaction ID |
| `_timestamp` | TIMESTAMP | Verarbeitungszeitpunkt der Änderung (ohne Zeitzone) |
| `_sort_by` | BIGINT | monotoner Sortierschlüssel über alle Änderungen |

### Typische Änderungsmuster

- **Initial-Snapshot:** Beim ersten Lauf wird jede bestehende Zeile mit `_pg_change_type = 'insert'` geschrieben.
- **Update:** zwei Zeilen: `update_preimage` (alt) und `update_postimage` (neu).
- **Delete:** eine Zeile mit `delete`.

Das sind **dieselben Ereignistypen wie beim Delta-CDF**, dieselben Muster gelten.

### Betriebsverhalten

- **Namenskollisionen:** Würden zwei Quelltabellen auf denselben Zielnamen fallen (z. B. `sales.users` und `marketing.users` → `lb_users_history`), bekommt die zweite automatisch das Suffix `_1`. Zieltabellen dürfen in Unity Catalog umbenannt werden; der Feed läuft weiter.
- **Leere Tabellen** werden übersprungen, bis sie mindestens eine Zeile haben.
- **Gelöschte Quelltabellen:** Die Zieltabelle in Unity Catalog bleibt erhalten.

---

## Nachgelagerte Pipelines

**Beispielszenario:** Eine E-Commerce-App schreibt Bestellungen in die Postgres-Tabelle `orders` (`item_id`, `quantity`). Die Logistik braucht Live-Lagerbestände. Jede Änderung an `orders` landet in `lb_orders_history`; nachgelagerte Pipelines aktualisieren daraus `inventory_levels`.

### Variante 1: Materialized View (am einfachsten)

```sql
CREATE MATERIALIZED VIEW inventory_levels AS
SELECT
  item_id,
  SUM(
    CASE
      -- New orders (and the "new half" of updates) decrement inventory
      WHEN _pg_change_type IN ('insert', 'update_postimage') THEN -quantity
      -- Cancellations (and the "old half" of updates) restore inventory
      WHEN _pg_change_type IN ('delete', 'update_preimage') THEN quantity
      ELSE 0
    END
  ) AS current_inventory,
  MAX(_timestamp) AS last_transaction_ts,
  MAX(_pg_lsn) AS last_lsn
FROM lb_orders_history
GROUP BY item_id;
```

**Trick:** Pre- und Postimage eines Updates heben sich bis auf die **Netto-Änderung** auf. Die laufende Summe bleibt deshalb korrekt, auch wenn Bestellungen geändert werden. Die MV aktualisiert sich inkrementell.

### Variante 2: Spark Declarative Pipelines (Medallion)

```python
import dlt
from pyspark.sql import functions as F

@dlt.table
def inventory_adjustments():
    return (
        spark.readStream.table("<catalog>.<schema>.lb_orders_history")
        .withColumn(
            "delta",
            F.when(F.col("_pg_change_type").isin("insert", "update_postimage"), -F.col("quantity"))
             .when(F.col("_pg_change_type").isin("delete", "update_preimage"), F.col("quantity"))
             .otherwise(0),
        )
        .select("item_id", "delta", "_timestamp")
    )

@dlt.expect_or_drop("non_negative_stock", "on_hand >= 0")
@dlt.table
def inventory_levels():
    return (
        spark.read.table("LIVE.inventory_adjustments")
        .groupBy("item_id")
        .agg(F.sum("delta").alias("on_hand"))
    )
```

`inventory_adjustments` liest die History-Tabelle inkrementell und erzeugt pro Event ein Delta; `inventory_levels` aggregiert pro Artikel. Die Expectation verwirft Zeilen, die den Bestand negativ machen würden (Hinweis auf einen Fehler upstream).

> Das Doku-Beispiel nutzt noch das ältere Modul `dlt` und `LIVE.`; aktuelle Pipelines verwenden `from pyspark import pipelines as dp`.

### Variante 3: Structured Streaming mit `foreachBatch` (maximale Kontrolle)

```python
from pyspark.sql import functions as F
from delta.tables import DeltaTable

def update_inventory(batch_df, batch_id):
    deltas = (
        batch_df
        .withColumn(
            "delta",
            F.when(F.col("_pg_change_type").isin("insert", "update_postimage"), -F.col("quantity"))
             .when(F.col("_pg_change_type").isin("delete", "update_preimage"), F.col("quantity"))
             .otherwise(0),
        )
        .groupBy("item_id")
        .agg(F.sum("delta").alias("delta"))
    )
    target = DeltaTable.forName(spark, "<catalog>.<schema>.inventory_levels")
    (target.alias("t")
        .merge(deltas.alias("s"), "t.item_id = s.item_id")
        .whenMatchedUpdate(set={"on_hand": F.expr("t.on_hand + s.delta")})
        .whenNotMatchedInsert(values={"item_id": "s.item_id", "on_hand": "s.delta"})
        .execute())

(spark.readStream.table("<catalog>.<schema>.lb_orders_history")
    .writeStream
    .foreachBatch(update_inventory)
    .option("checkpointLocation", "/Volumes/<catalog>/<schema>/checkpoints/inventory_levels")
    .start())
```

Jeder Micro-Batch aggregiert die Events pro `item_id` und merged die Netto-Deltas.

> **Inkrementell by Design:** Jede `lb_<table_name>_history`-Tabelle ist **append-only**. MVs, Pipeline-Flows und Structured Streaming verarbeiten neue Zeilen inkrementell aus dem Delta-Log. **Der Delta-CDF muss auf der History-Tabelle nicht aktiviert werden**, weil die Änderungssemantik bereits in den Zeilen steckt.

---

## Datentyp-Mapping

| PostgreSQL | Delta | Hinweis |
|---|---|---|
| BOOLEAN | BOOLEAN | |
| INT, SMALLINT, BIGINT | INT, SMALLINT, BIGINT | |
| TEXT, VARCHAR, CHAR | STRING | |
| JSONB | STRING | als JSON-String |
| ENUM | STRING | als Enum-Label |
| NUMERIC / DECIMAL | DECIMAL oder STRING | Quell-Precision/Scale wo möglich; verlustfreies Reskalieren; STRING bei Precision > 38 oder undefinierter Precision/Scale. Alle NUMERIC/DECIMAL-Spalten sind nullable (NaN → NULL). |
| DATE | DATE | |
| TIMESTAMP | TIMESTAMP_NTZ | |
| TIMESTAMPTZ | TIMESTAMP | |
| FLOAT, DOUBLE | FLOAT, DOUBLE | |

Als **STRING** gespeichert: PostGIS-Typen (`geometry`, `geography`), `vector` (pgvector), Composite-/Struct-Typen (`CREATE TYPE ... AS (...)`), Map-artige Typen wie `hstore`.

## Schemaänderungen

- **Tabelle umbenennen** (`ALTER TABLE users RENAME TO customers`): Feed läuft weiter, Zieltabelle behält ihren Namen (`lb_users_history`).
- **Spalte hinzufügen, löschen oder Typ ändern:** löst einen **Re-Snapshot** aus. CDF liest die ganze Tabelle neu aus Postgres und schreibt die Zieltabelle neu.

## Lakebase CDF deaktivieren

Deaktivieren stoppt den Feed für **alle** Lakebase-Schemas im Projekt: Lakebase Postgres → Projekt und Branch → Branch overview → Tab **Lakebase CDF** → **Disable** → im Dialog erneut **Disable**. Die Compute wird dabei **nicht** neu gestartet.

---

## Einschränkungen und Troubleshooting

Status pro Tabelle (snapshotting, skipped, streaming) im Tab oder per `SELECT * FROM wal2delta.tables;`.

**Warum erscheint eine Tabelle nicht?**

- `REPLICA IDENTITY FULL` fehlt → `ALTER TABLE <table_name> REPLICA IDENTITY FULL;`
- **Partitionierte Tabellen** werden nicht unterstützt und schlagen fehl.
- **Leere Tabellen** werden übersprungen.

> **Warnung: Die Zieltabellen `lb_<table_name>_history` nicht verändern:**
> - **Keine Row Filter oder Column Masks** hinzufügen: CDF hört sonst auf, in die Tabelle zu schreiben.
> - **Keinen Delta-CDF aktivieren**: Das bricht den `ALTER TABLE`-Re-Snapshot bei Schemaänderungen der Quelle.

> **Private Endpoints:** Nicht unterstützt, wenn der Managed Storage des Zielkatalogs **nur** über einen Private Endpoint erreichbar ist (z. B. AWS PrivateLink Interface Endpoint). Workaround: Katalog mit öffentlich erreichbarem Managed Storage als Ziel verwenden.

**Nächste Schritte laut Doku:** inkrementelles ETL mit Spark Declarative Pipelines, Bronze-Schicht mit Databricks SQL abfragen, **Historie per Time Travel** auf den Ziel-Delta-Tabellen prüfen.

---
[← Übersicht](../00%20Uebersicht.md) · [Nächste Datei →](02%20Quickstart%20und%20REST-API.md)
