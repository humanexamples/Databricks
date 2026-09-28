[← Übersicht](../00%20Uebersicht.md)

# Lakebase CDF: Quickstart und REST-API

> Quellen: [Quickstart: Store Postgres changes in the lakehouse](https://docs.databricks.com/aws/en/oltp/projects/quickstart-lakebase-cdf) (Stand 18.09.2026) · [Postgres API: CDF config](https://docs.databricks.com/api/postgres/v1/cdf-config) · [Postgres API: CDF status](https://docs.databricks.com/api/postgres/v1/cdf-status) · [Lakebase API usage](https://docs.databricks.com/aws/en/oltp/projects/api-usage) · [Upgrade to Autoscaling](https://docs.databricks.com/aws/en/oltp/upgrade-to-autoscaling) · [What's coming](https://docs.databricks.com/aws/en/release-notes/whats-coming)

## Quickstart in vier Schritten

**Vorbereitung:** ein Lakebase-Projekt mit der Beispieltabelle `playing_with_lakebase` (aus „Get a Postgres database“) und ein Unity-Catalog-Katalog/-Schema mit `CREATE TABLE`-Recht.

### ① Change Capture aktivieren

Im Lakebase SQL Editor:

```sql
ALTER TABLE playing_with_lakebase REPLICA IDENTITY FULL;
```

### ② Feed starten

Branch `production` → **Branch overview** → Tab **Lakebase CDF** → **Start**. Quellschema `public`, dann Zielkatalog und -schema wählen. Der Initial-Snapshot beginnt sofort; `lb_playing_with_lakebase_history` erscheint als Delta-Tabelle.

### ③ Eine Zeile ins Lakehouse verfolgen

In Lakebase (PostgreSQL):

```sql
SELECT * FROM playing_with_lakebase WHERE id = 2;
```

In einem Databricks SQL Warehouse oder Notebook:

```sql
SELECT * FROM <catalog>.<schema>.lb_playing_with_lakebase_history
WHERE id = 2;
```

Die Zeile `id=2` hat dieselben Werte (`name`, `value`) wie in Lakebase, plus Metadatenspalten. Der Initial-Snapshot hat sie als `insert`-Event geschrieben.

### ④ Die Zeile ändern und den Fluss beobachten

In Lakebase:

```sql
UPDATE playing_with_lakebase SET value = 55.5 WHERE id = 2;
```

Einige Sekunden warten, dann im Lakehouse:

```sql
SELECT id, value, _pg_change_type, _timestamp
FROM <catalog>.<schema>.lb_playing_with_lakebase_history
WHERE id = 2
ORDER BY _pg_lsn DESC;
```

Die Zeile `id=2` steht jetzt **dreimal** da: das ursprüngliche `insert`, ein `update_preimage` mit dem alten und ein `update_postimage` mit dem neuen Wert. Jede Änderung wird zu einer neuen Historienzeile, also ein vollständiger Audit Trail. Ein Delete hängt entsprechend eine Zeile mit `_pg_change_type = 'delete'` an.

---

## REST-API: CDF-Konfigurationen (Beta)

CDF-Operationen sind auf einen **Branch** bezogen. Eine **CdfConfig** gibt es **pro Postgres-Schema und Datenbank**; sie repliziert die Tabellen dieses Schemas in ein Unity-Catalog-Schema und ist nach dem Anlegen **unveränderlich (immutable)**. API-Scope: `postgres`.

### Endpunkte

| Operation | Methode und Pfad |
|---|---|
| Konfiguration anlegen (Feed starten) | `POST /api/2.0/postgres/{parent=projects/*/branches/*/databases/*}/cdf-configs` |
| Konfigurationen auflisten | `GET /api/2.0/postgres/{parent=projects/*/branches/*/databases/*}/cdf-configs` |
| eine Konfiguration abrufen | `GET /api/2.0/postgres/{name=projects/*/branches/*/databases/*/cdf-configs/*}` |
| Konfiguration löschen | `DELETE /api/2.0/postgres/{name=projects/*/branches/*/databases/*/cdf-configs/*}` |

Die Seite „API usage“ listet zusätzlich **Get CDF status** und **List CDF statuses** (`GET`).

### Das CdfConfig-Objekt

```json
{
  "name": "string",
  "catalog": "string",
  "schema": "string",
  "create_time": "string",
  "cdf_config_id": "string",
  "postgres_schema": "string"
}
```

| Feld | Bedeutung |
|---|---|
| `name` | vollständiger Ressourcenname (Output): `projects/{project}/branches/{branch}/databases/{database}/cdf-configs/{cdf_config}` |
| `catalog` | UC-Katalog, in den geschrieben wird (**Pflicht** beim Anlegen, immutable) |
| `schema` | UC-Schema, in das geschrieben wird (**Pflicht**, immutable) |
| `postgres_schema` | Postgres-Quellschema; eindeutig innerhalb der Datenbank (**Pflicht**, immutable) |
| `create_time` | Anlagezeitpunkt (Output) |
| `cdf_config_id` | vom Nutzer vergebene ID = letztes Segment von `name`; Default: Name des Postgres-Schemas |

Beim **Anlegen** sind `catalog`, `schema` und `postgres_schema` Pflicht; alle anderen Felder sind Output und werden ignoriert. Danach wird die Änderungshistorie jeder Tabelle fortlaufend in ihre Lakehouse-Tabelle geschrieben.

### Löschen: Parameter `force`

| `force` | Wirkung |
|---|---|
| `false` (Default) | Konfiguration und Tabellen-Mappings werden entfernt; die **Delta-Tabellen bleiben** im letzten Stand erhalten |
| `true` | zusätzlich werden die replizierten **Delta-Tabellen in Unity Catalog gelöscht** |

Für die programmatische Verwaltung gibt es die CDF-Operationen in der Postgres-REST-API und in den **Databricks SDKs**.

---

## Einordnung: Lakebase CDF ersetzt „Forward ETL“

- Auf **Lakebase Provisioned** gab es das Private-Preview-Feature **Forward ETL** zum Synchronisieren ins Lakehouse.
- Alle Provisioned-Instanzen wurden bis **Juli 2026** auf **Lakebase Autoscaling** umgestellt. Forward ETL wird dort nicht mehr unterstützt.
- Ersatz: **Lakebase Change Data Feed** auf der Autoscaling-Plattform.

---
[← Vorherige Datei](01%20Lakebase%20Change%20Data%20Feed.md) · [Übersicht](../00%20Uebersicht.md) · [Nächste Datei →](03%20Synced%20Tables%20und%20LTAP.md)
