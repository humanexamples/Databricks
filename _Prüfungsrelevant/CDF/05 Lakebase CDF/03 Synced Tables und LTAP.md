[← Übersicht](../00%20Uebersicht.md)

# Synced Tables und LTAP: CDF in Richtung Lakehouse → Lakebase

> Quellen: [Serve lakehouse data with synced tables](https://docs.databricks.com/aws/en/oltp/projects/sync-tables) · [LTAP architecture](https://docs.databricks.com/aws/en/oltp/projects/ltap-overview) · [Managed Iceberg limitations](https://docs.databricks.com/aws/en/iceberg/) · [Typical project with DABs](https://docs.databricks.com/aws/en/oltp/projects/dabs-typical-project) · [Typical project with Terraform](https://docs.databricks.com/aws/en/oltp/projects/terraform-typical-project) · [Lakebase sink](https://docs.databricks.com/aws/en/structured-streaming/lakebase)

**Lakebase CDF** ([01](01%20Lakebase%20Change%20Data%20Feed.md)) bringt Änderungen von Postgres **ins Lakehouse**. **Synced Tables** gehen den umgekehrten Weg: Sie liefern Unity-Catalog-Tabellen **nach Lakebase**, damit Anwendungen sie mit niedriger Latenz lesen können. Dafür nutzen sie den **Delta-CDF der Quelltabelle**.

---

## Sync-Modi und ihr CDF-Bedarf

| Modus | Beschreibung | Wann verwenden | Performance |
|---|---|---|---|
| **Snapshot** | einmalige Kopie aller Daten | Quelle ändert > 10 % der Zeilen pro Zyklus | 10× effizienter, wenn > 10 % der Quelldaten geändert werden |
| **Triggered** | geplante Updates, auf Abruf oder in Intervallen | Quellzeilen ändern sich in bekanntem Rhythmus; Inserts, Updates und Deletes werden je Refresh weitergegeben | gutes Verhältnis Kosten/Verzögerung; teuer bei Intervallen < 5 Min. |
| **Continuous** | Echtzeit-Streaming mit Sekunden-Latenz | Änderungen müssen nahezu in Echtzeit in Lakebase erscheinen | geringste Verzögerung, höchste Kosten; Minimum 15-Sekunden-Intervalle |

**Quell-Anforderung:**

- **Snapshot** kopiert jedes Mal alles; die Quelle muss nur `SELECT *` unterstützen.
- **Triggered und Continuous** wenden Zeilenänderungen **inkrementell** an: Die Quelle **muss einen Change Data Feed liefern**. Entweder Write-Time-CDF (Legacy) aktivieren oder **Automatic CDF** nutzen. Fehlt der CDF, zeigt die UI eine Warnung mit dem exakten `ALTER TABLE`-Befehl.

Automatic CDF erlaubt Triggered/Continuous auch für weitere Quelltypen, **einschließlich Apache-Iceberg-Tabellen**.

Write-Time-CDF auf einer Delta-Quelle aktivieren:

```sql
ALTER TABLE your_catalog.your_schema.your_table
SET TBLPROPERTIES (delta.enableChangeDataFeed = true)
```

> **Ausnahme:** Laut Iceberg-Doku wird bei **Managed Iceberg Tables** als Quelle für Synced Tables die inkrementelle Verarbeitung mit **Automatic CDF nicht** unterstützt.

---

## Synced Table anlegen

**Voraussetzungen:** Workspace mit Lakebase, Lakebase-Projekt, zu synchronisierende UC-Tabelle, `USE_SCHEMA` und `CREATE_TABLE` auf den verwendeten Schemas; für Triggered/Continuous den CDF (siehe oben).

**UI:** Catalog → Tabelle wählen → **Create > Synced table** → Name, *Database type* „Lakebase Serverless (Autoscaling)“, **Sync mode**, Projekt/Branch/Datenbank, Primary Key prüfen (Key-Spalten sind im Ziel nicht nullable; Zeilen mit `NULL` im Key werden nicht synchronisiert), optional **Timeseries key** zur Deduplizierung → **Create**.

Die Doku-Beispiele verwenden den Modus `SNAPSHOT`; für Triggered/Continuous wird `scheduling_policy` entsprechend gesetzt.

CLI:

```bash
databricks postgres create-synced-table my-catalog.sales.orders \
  --json '{
    "spec": {
      "source_table_full_name": "main.sales.orders",
      "branch": "projects/my-project/branches/production",
      "primary_key_columns": ["order_id"],
      "scheduling_policy": "SNAPSHOT",
      "postgres_database": "mydb",
      "create_database_objects_if_missing": true
    }
  }'
```

Python SDK:

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.postgres import (
    SyncedTable,
    SyncedTableSyncedTableSpec,
    SyncedTableSyncedTableSpecSyncedTableSchedulingPolicy,
)

w = WorkspaceClient()

synced_table = w.postgres.create_synced_table(
    synced_table=SyncedTable(spec=SyncedTableSyncedTableSpec(
        source_table_full_name="main.sales.orders",
        branch="projects/my-project/branches/production",
        primary_key_columns=["order_id"],
        scheduling_policy=SyncedTableSyncedTableSpecSyncedTableSchedulingPolicy.SNAPSHOT,
        postgres_database="mydb",
        create_database_objects_if_missing=True,
    )),
    synced_table_id="my-catalog.sales.orders",
).wait()

print(f"Synced table created: {synced_table.name}")
```

Java SDK:

```java
import com.databricks.sdk.WorkspaceClient;
import com.databricks.sdk.service.postgres.*;
import java.util.List;

WorkspaceClient w = new WorkspaceClient();

SyncedTable syncedTable = w.postgres().createSyncedTable(
    new CreateSyncedTableRequest()
        .setSyncedTableId("my-catalog.sales.orders")
        .setSyncedTable(new SyncedTable()
            .setSpec(new SyncedTableSyncedTableSpec()
                .setSourceTableFullName("main.sales.orders")
                .setBranch("projects/my-project/branches/production")
                .setPrimaryKeyColumns(List.of("order_id"))
                .setSchedulingPolicy(SyncedTableSyncedTableSpecSyncedTableSchedulingPolicy.SNAPSHOT)
                .setPostgresDatabase("mydb")
                .setCreateDatabaseObjectsIfMissing(true))))
    .waitForCompletion();

System.out.println("Synced table created: " + syncedTable.getName());
```

curl:

```bash
curl -X POST "https://your-workspace.cloud.databricks.com/api/2.0/postgres/synced_tables?synced_table_id=my-catalog.sales.orders" \
  -H "Authorization: Bearer ${DATABRICKS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "spec": {
      "source_table_full_name": "main.sales.orders",
      "branch": "projects/my-project/branches/production",
      "primary_key_columns": ["order_id"],
      "scheduling_policy": "SNAPSHOT",
      "postgres_database": "mydb",
      "create_database_objects_if_missing": true
    }
  }'
```

### LTAP Direct Writes (Beta)

Beschleunigt große Ladevorgänge, indem direkt in den Storage des Lakebase-Branches geschrieben wird. Für **Triggered und Continuous** betrifft das nur den **Initial-Load**; spätere Updates laufen **inkrementell über den Change Data Feed**, nicht als Bulk-Load. Erfordert Postgres 17 und Admin-Aktivierung; gilt nur für danach angelegte Synced Tables.

### Infrastructure as Code

Die Doku-Vorlagen für **Declarative Automation Bundles** und **Terraform** setzen als Sync-Quelle eine **UC-Delta-Tabelle mit aktiviertem CDF** voraus.

---

## LTAP: wie Lakebase CDF und Synced Tables zusammenpassen

LTAP ist die Lakebase-Architektur, in der OLTP und Lakehouse **eine gemeinsame Datenkopie** nutzen.

| Fähigkeit | Status | Beschreibung |
|---|---|---|
| Lakebase in Unity Catalog registrieren | GA | Governance für analytischen Zugriff, Cross-Source-Queries |
| Synced Tables | GA | UC-Tabellen für OLTP-Reads mit niedriger Latenz in Lakebase bereitstellen |
| Lakehouse//RT auf Lakebase | Beta | transaktional konsistente OLAP-Abfragen auf Live-Postgres-Daten |
| **Lakebase Change Data Feed** | **Public Preview** | Zeilenänderungen aus Postgres als UC-Delta-Tabellen für Pipelines und Audit |

**Lakehouse//RT vs. Lakebase CDF:** Beide lesen dieselben Daten, stellen sie aber unterschiedlich dar. Lakehouse//RT liefert den **aktuellen Zustand** für Analysen, Lakebase CDF einen **Strom von Zeilenänderungen** für Pipelines und Audit.

**Governance:** Unity Catalog regelt den **analytischen** Zugriff (externe Compute wie Lakehouse//RT und CDF). Der **transaktionale** Zugriff über Postgres-Clients läuft weiter über Postgres-`GRANT`/`REVOKE`.

### Richtungsentscheidung: Wer besitzt den Schreibvorgang?

| Besitzer | Weg | Beispiel |
|---|---|---|
| **Lakebase** schreibt | Lakehouse//RT (Live-Dashboard) oder **Lakebase CDF** (jede Änderung in Pipeline oder Audit-Log) | Vertriebs-App schreibt Bestellungen nach Postgres |
| **Lakehouse** schreibt | **Synced Tables** (braucht Delta-CDF der Quelle für Triggered/Continuous) | nächtlicher Job berechnet Empfehlungen oder Preistabellen |

Für niedrige Latenz beim Schreiben **aus einem Stream nach Lakebase** gibt es außerdem den **Lakebase-Sink** für Structured Streaming; für die Gegenrichtung verweist dessen Doku auf Lakebase CDF.

---
[← Vorherige Datei](02%20Quickstart%20und%20REST-API.md) · [Übersicht](../00%20Uebersicht.md) · [Weiter: Weitere Einsatzgebiete →](../06%20Weitere%20Einsatzgebiete.md)
