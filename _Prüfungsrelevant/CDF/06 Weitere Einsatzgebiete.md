[← Übersicht](00%20Uebersicht.md)

# Weitere Einsatzgebiete: Wo Databricks-Features CDF voraussetzen

> Quellen: [Online feature stores](https://docs.databricks.com/aws/en/machine-learning/feature-store/online-feature-store) · [Feature serving tutorial](https://docs.databricks.com/aws/en/machine-learning/feature-store/feature-serving-tutorial) · [Feature views](https://docs.databricks.com/aws/en/machine-learning/feature-store/feature-views) · [Create an AI Search index](https://docs.databricks.com/aws/en/ai-search/create-ai-search) · [AI Search](https://docs.databricks.com/aws/en/ai-search/ai-search) · [Data profiling (API)](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring/data-profiling/create-monitor-api) · [Data profiling (UI)](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring/data-profiling/create-monitor-ui) · [Incremental refresh for MVs](https://docs.databricks.com/aws/en/ldp/incremental-refresh) · [Lakeflow Connect FAQ](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/faq)

Viele Databricks-Dienste arbeiten **inkrementell**, indem sie den CDF ihrer Quelltabelle lesen. Deshalb taucht „CDF aktivieren“ in vielen Anleitungen als Voraussetzung auf.

## Überblick

| Feature | Braucht CDF? | Wofür |
|---|---|---|
| **Online Feature Store** (Publish) | ja, für `TRIGGERED` und `CONTINUOUS` | Änderungen der Offline-Feature-Tabelle inkrementell in den Online Store übertragen |
| **Feature Views** (Streaming-Features aus `DeltaTableSource`) | ja | inkrementelle Materialisierung |
| **AI Search** (Standard-Endpoints) | ja; bei Row Tracking automatisch | Index inkrementell aktualisieren |
| **Data Profiling** (`TimeSeries`, `Inference`) | empfohlen | nur neu angehängte Daten verarbeiten |
| **Materialized Views** | empfohlen (Row Tracking Pflicht) | schnelleres inkrementelles Refresh |
| **Synced Tables** (Lakebase) | ja, für Triggered und Continuous | → [05/03](05%20Lakebase%20CDF/03%20Synced%20Tables%20und%20LTAP.md) |
| **Lakeflow-Connect-Zieltabellen** | bereits aktiviert | nachgelagerte Verarbeitung |

---

## Feature Store: Online-Publishing

**Voraussetzungen für jede Feature-Tabelle vor dem Publizieren:**

- **Primary-Key-Constraint** (Pflicht für Online-Publishing)
- **Nicht-nullable Primärschlüssel**
- **Change Data Feed aktiviert**: Pflicht für die Publish-Modi `CONTINUOUS` und `TRIGGERED`

```sql
-- Enable CDF if not already enabled
ALTER TABLE catalog.schema.your_feature_table
SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');

-- Ensure primary key columns are not nullable
ALTER TABLE catalog.schema.your_feature_table
ALTER COLUMN user_id SET NOT NULL;
```

Aus dem Feature-Serving-Tutorial (Python):

```python
# Enable Change Data Feed to enable CONTINOUS and TRIGGERED publish modes
spark.sql(f"ALTER TABLE {feature_table_name} SET TBLPROPERTIES (delta.enableChangeDataFeed = 'true')")
```

### Publish-Modi (`publish_mode`)

| Modus | Beschreibung | CDF |
|---|---|---|
| `TRIGGERED` | **Default.** Inkrementelles Update des Online Stores per API oder Zeitplan (z. B. Notebook mit `publish_table` als geplanter Lakeflow Job) | **erforderlich** |
| `CONTINUOUS` | Streaming-Pipeline, die den Online Store sofort aktualisiert | **erforderlich** |
| `SNAPSHOT` | einmaliger Voll-Sync; effizient bei vielen Updates bestehender Zeilen zwischen zwei Syncs | nicht nötig |

`publish_mode` ersetzt ab v0.13.0.1 den Parameter `streaming`; `streaming=True` entspricht `publish_mode="CONTINUOUS"`.

## Feature Views: Streaming-Features aus Delta-Tabellen

Für ein Streaming-Feature auf einer `DeltaTableSource` muss die Quelltabelle **`delta.enableChangeDataFeed=true`** haben. Allgemein gilt: Für Features mit Delta-Quelle nutzt Databricks den CDF, um Quelldaten **inkrementell** zu verarbeiten.

```python
from databricks.feature_engineering import FeatureEngineeringClient
from databricks.feature_engineering.entities import (
    DeltaTableSource,
    AggregationFunction,
    OnlineStoreConfig,
    Sum,
    RollingWindow,
    StreamingMode,
)
from datetime import timedelta

client = FeatureEngineeringClient()

source = DeltaTableSource(
    catalog_name="my_catalog",
    schema_name="my_schema",
    table_name="transactions",
)

feature = client.create_feature(
    catalog_name="my_catalog",
    schema_name="my_schema",
    name="user_purchase_sum",
    source=source,
    entity=["user_id"],
    timeseries_column="event_time",
    function=AggregationFunction(
        operator=Sum(input="amount"),
        time_window=RollingWindow(window_duration=timedelta(hours=1)),
    ),
)

online_config = OnlineStoreConfig(
    catalog_name="my_catalog",
    schema_name="my_schema",
    table_name_prefix="streaming_features",
    online_store_name="my_online_store",
)

client.materialize_features(
    features=[feature],
    online_config=online_config,
    trigger=StreamingMode(),
)
```

> **Zerobus:** Eine von Zerobus befüllte Delta-Tabelle kann Streaming-Feature-Quelle sein. Zerobus setzt `delta.enableChangeDataFeed=true` aber **nicht automatisch**; die Eigenschaft muss vorher manuell gesetzt werden.

---

## AI Search (Vector Search)

Anforderung für **Standard-Endpoints:** Die Quelltabelle muss einen **Change Data Feed verwenden**. Tabellen mit **Row Tracking** nutzen automatisch einen CDF, ohne manuelle Konfiguration. Das gilt für Delta-Tabellen und Managed Tables mit **Iceberg v3** oder höher.

Weitere Anforderungen: Unity Catalog, Serverless Compute, `CREATE TABLE` auf dem Zielschema des Index.

> Aus einer **Materialized View** lässt sich kein Vector-Search-Index erstellen.

---

## Data Quality Monitoring: Data Profiling

Für die Profiltypen **`TimeSeries`** und **`Inference`** ist es **Best Practice, CDF zu aktivieren**. Dann werden bei jedem Refresh nur die **neu angehängten Daten** verarbeitet statt der ganzen Tabelle. Das spart Kosten, besonders bei vielen Tabellen.

Weitere Hinweise:

- Beim ersten Anlegen analysiert ein TimeSeries- oder Inference-Profil nur die Daten der **letzten 30 Tage**; danach alle neuen Daten.
- Profile auf **Materialized Views** unterstützen keine inkrementelle Verarbeitung.

---

## Materialized Views und Lakeflow Connect

- **Materialized Views:** Row Tracking ist Voraussetzung für inkrementelles Refresh, CDF wird zusätzlich empfohlen → [01/03](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md). Den CDF **einer MV selbst** lesen → [03/03](03%20Pipelines%20und%20Muster/03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md).
- **Lakeflow Connect:** CDF ist auf **allen Zieltabellen** aktiviert. **Ausnahme Smartsheet:** Der Connector nutzt Column Mapping, deshalb ist CDF dort **nicht** unterstützt → [07](07%20Einschraenkungen%20und%20Fehlermeldungen.md).

---
[← Übersicht](00%20Uebersicht.md) · [Nächste Datei →](07%20Einschraenkungen%20und%20Fehlermeldungen.md)
