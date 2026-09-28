# Change Data Feed (CDF) — Übersicht

**Change Data Feed** verfolgt **Änderungen auf Zeilenebene** zwischen den Versionen einer Delta-Lake- oder Apache-Iceberg-v3-Tabelle. Jede Änderung trägt die Zeilendaten und die Metadaten `_change_type` (`insert`, `update_preimage`, `update_postimage`, `delete`), `_commit_version` und `_commit_timestamp`.

> Grundlage dieses Ordners: 100 Seiten der offiziellen Databricks-Dokumentation aus der Suche nach „Change Data Feed“ (abgerufen am 28.09.2026). Code ist **unverändert** übernommen; die Erklärungen sind auf Deutsch und eigenständig formuliert. Welche Seite wo verarbeitet wurde, zeigt die [Quellenzuordnung](#quellenzuordnung-aller-100-urls) am Ende.

---

## Das Wichtigste auf einen Blick

| Frage | Antwort |
|---|---|
| Wie schalte ich CDF ein? | **Legacy:** `ALTER TABLE t SET TBLPROPERTIES (delta.enableChangeDataFeed = true)` · **Automatic:** nichts einschalten; Voraussetzung ist Row Tracking + DBR 19 + Unity Catalog |
| Wie lese ich im Batch? | SQL `table_changes('t', start [, end])` · Python `spark.read.option("readChangeFeed", "true").option("startingVersion", n).table("t")` |
| Wie lese ich im Stream? | `spark.readStream.option("readChangeFeed", "true").table("t")`; Databricks empfiehlt Streaming, weil der Checkpoint die Position merkt |
| Was passiert beim ersten Stream-Start? | aktueller Snapshot kommt als `insert`, danach die Änderungen |
| Wie viele Zeilen erzeugt ein `UPDATE`? | **zwei**: `update_preimage` + `update_postimage` |
| Ist CDF ein dauerhaftes Archiv? | **Nein.** Er enthält nur Änderungen ab Aktivierung und verschwindet mit Retention/`VACUUM`. Für dauerhafte Historie in eine eigene Tabelle schreiben. |
| Wie wende ich CDF-Änderungen deklarativ an? | `AUTO CDC ... FROM STREAM t WITH (readChangeFeed = true) ... APPLY AS DELETE WHEN _change_type = 'delete' SEQUENCE BY _commit_timestamp` |
| Wie teile ich CDF? | CDF aktivieren **vor** dem Teilen, dann `ALTER SHARE s ADD TABLE t WITH HISTORY` |
| Was ist Lakebase CDF? | ein **anderes** Feature: Postgres-Änderungen aus dem WAL landen als Delta-Tabelle `lb_<table>_history` im Lakehouse |

---

## Aufbau des Ordners

| Datei | Inhalt |
|---|---|
| **01 Grundlagen** | |
| [01 Was ist CDF – Automatic vs. Legacy](01%20Grundlagen/01%20Was%20ist%20CDF%20-%20Automatic%20vs.%20Legacy.md) | Definition, Einsatzfälle, Automatic CDF (Row Tracking, DBR 19, GA), Legacy CDF, Migration |
| [02 Schema und Metadatenspalten](01%20Grundlagen/02%20Schema%20und%20Metadatenspalten.md) | `_change_type` & Co., Beispiel mit `DESCRIBE HISTORY`, reservierte Namen, Zeitzone ab DBR 15.4 |
| [03 Tabelleneigenschaften, Protokoll und Speicher](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) | Table Properties, Writer-Version 4, Retention, `VACUUM` und `_change_data`, `replaceWhere` |
| **02 Lesen** | |
| [01 Batch – table_changes und readChangeFeed](02%20Lesen/01%20Batch%20-%20table_changes%20und%20readChangeFeed.md) | Syntax, Berechtigungen, SQL/Python/Scala, Versionen außerhalb des Bereichs |
| [02 Streaming – readStream und Optionen](02%20Lesen/02%20Streaming%20-%20readStream%20und%20Optionen.md) | Stream-Start, Rate Limits, Startversion, Wiederanlauf, Archivierung, Optionsreferenz, vier Wege bei Quelländerungen |
| **03 Pipelines und Muster** | |
| [01 Demo – Silver nach Gold propagieren](03%20Pipelines%20und%20Muster/01%20Demo%20-%20Silver%20nach%20Gold%20propagieren.md) | offizielles Notebook, vollständig |
| [02 CDF und AUTO CDC](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) | SQL-ETL-Tutorial (CDF → SCD 2 → MV), Expectations-Workaround, Best Practices |
| [03 CDF von AUTO-CDC-Zielen und Materialized Views](03%20Pipelines%20und%20Muster/03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md) | CDF aus Streaming Tables (DBR 15.2) und MVs (Beta, DBR 18 LTS) |
| [04 Change Feeds bei Datei-Ingestion](03%20Pipelines%20und%20Muster/04%20Change%20Feeds%20bei%20Datei-Ingestion.md) | `read_files(..., readChangeFeed => true)`, SharePoint, AUTO CDC |
| **04 Delta Sharing** | |
| [01 CDF teilen (Provider)](04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md) | `WITH HISTORY`, Defaults je Runtime, Egress-Replikation |
| [02 CDF lesen (Empfänger)](04%20Delta%20Sharing/02%20CDF%20lesen%20%28Empfaenger%29.md) | Databricks-to-Databricks, Open Sharing (Spark, pandas), `responseFormat=delta`, `DS_CDF_*`-Fehler |
| **05 Lakebase CDF** | |
| [01 Lakebase Change Data Feed](05%20Lakebase%20CDF/01%20Lakebase%20Change%20Data%20Feed.md) | Postgres-WAL → Delta, Einrichtung, Schema, drei Pipeline-Varianten, Typ-Mapping |
| [02 Quickstart und REST-API](05%20Lakebase%20CDF/02%20Quickstart%20und%20REST-API.md) | vier Schritte, CdfConfig-Endpunkte |
| [03 Synced Tables und LTAP](05%20Lakebase%20CDF/03%20Synced%20Tables%20und%20LTAP.md) | Gegenrichtung: Synced Tables brauchen den Delta-CDF der Quelle |
| [06 Weitere Einsatzgebiete](06%20Weitere%20Einsatzgebiete.md) | Feature Store, Feature Views, AI Search, Data Profiling, MVs, Lakeflow Connect |
| [07 Einschränkungen und Fehlermeldungen](07%20Einschraenkungen%20und%20Fehlermeldungen.md) | Column Mapping, Type Widening, Transaktionen, alle CDF-Fehlerklassen |

**Empfohlene Lesereihenfolge für die Prüfung:** 01/01 → 01/02 → 02/01 → 02/02 → 03/01 → 03/02 → 04/01 → 07. Lakebase (05) und 06 sind Vertiefung.

---

## Verwandte Dateien im Repo

- CDF im CDC-Kontext mit eigenen Kombinationsbeispielen (Delete-Propagation, DSGVO): [../CDC/04 Change Data Feed – Änderungen weiterreichen](../CDC/04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md)
- Abgrenzung CDC / SCD: [../CDC/00 Uebersicht](../CDC/00%20Uebersicht.md) · [../SCD/00 Uebersicht](../SCD/00%20Uebersicht.md)
- Weitere CDF-Notizen: `Full Doc/Themen/01 Platform/02 Tables/07 Table Features/02 Change Data Feed.md` · `Full Doc/Themen/07 Data Management/01 Data Engineering/03 Lakeflow Pipelines/05 CDC/02 Change Data Feed.md` · Kursmaterial `Kursmetrial_Databricks/6_Databricks Data Privacy` (DP 1.3, DP 1.4L)

---

## Quellenzuordnung aller 100 URLs

Jede URL aus der Suchliste wurde abgerufen und nach CDF-Inhalten durchsucht. Seiten ohne CDF-Inhalt im Artikeltext sind als solche markiert. Auf ihnen hat die Suche vermutlich nur Navigations- oder Metadaten getroffen.

| # | URL | verarbeitet in |
|---|---|---|
| 1 | [aws/en/tables/features/change-data-feed](https://docs.databricks.com/aws/en/tables/features/change-data-feed) | [G1](01%20Grundlagen/01%20Was%20ist%20CDF%20-%20Automatic%20vs.%20Legacy.md) · [G2](01%20Grundlagen/02%20Schema%20und%20Metadatenspalten.md) · [G3](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) · [L1](02%20Lesen/01%20Batch%20-%20table_changes%20und%20readChangeFeed.md) · [L2](02%20Lesen/02%20Streaming%20-%20readStream%20und%20Optionen.md) · [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 2 | [aws/en/notebooks/source/delta/cdf-demo.html](https://docs.databricks.com/aws/en/notebooks/source/delta/cdf-demo.html) | [M1](03%20Pipelines%20und%20Muster/01%20Demo%20-%20Silver%20nach%20Gold%20propagieren.md) |
| 3 | [aws/en/oltp/projects/lakebase-cdf](https://docs.databricks.com/aws/en/oltp/projects/lakebase-cdf) | [B1](05%20Lakebase%20CDF/01%20Lakebase%20Change%20Data%20Feed.md) |
| 4 | [aws/en/query/formats/opensharing](https://docs.databricks.com/aws/en/query/formats/opensharing) | [S2](04%20Delta%20Sharing/02%20CDF%20lesen%20%28Empfaenger%29.md) |
| 5 | [aws/en/data-engineering/what-is-cdc](https://docs.databricks.com/aws/en/data-engineering/what-is-cdc) | [G1](01%20Grundlagen/01%20Was%20ist%20CDF%20-%20Automatic%20vs.%20Legacy.md) · [M2](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) · [M3](03%20Pipelines%20und%20Muster/03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md) |
| 6 | [aws/en/ldp/cdc](https://docs.databricks.com/aws/en/ldp/cdc) | [M2](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) · [M3](03%20Pipelines%20und%20Muster/03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md) |
| 7 | [aws/en/sql/language-manual/functions/table_changes](https://docs.databricks.com/aws/en/sql/language-manual/functions/table_changes) | [G2](01%20Grundlagen/02%20Schema%20und%20Metadatenspalten.md) · [L1](02%20Lesen/01%20Batch%20-%20table_changes%20und%20readChangeFeed.md) |
| 8 | [aws/en/ldp/dbsql/materialized](https://docs.databricks.com/aws/en/ldp/dbsql/materialized) | [M3](03%20Pipelines%20und%20Muster/03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md) |
| 9 | [aws/en/ldp/cdc-advanced](https://docs.databricks.com/aws/en/ldp/cdc-advanced) | [M3](03%20Pipelines%20und%20Muster/03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md) |
| 10 | [aws/en/ai-search/create-ai-search](https://docs.databricks.com/aws/en/ai-search/create-ai-search) | [W](06%20Weitere%20Einsatzgebiete.md) |
| 11 | [aws/en/oltp/projects/quickstart-lakebase-cdf](https://docs.databricks.com/aws/en/oltp/projects/quickstart-lakebase-cdf) | [B2](05%20Lakebase%20CDF/02%20Quickstart%20und%20REST-API.md) |
| 12 | [aws/en/release-notes/product/2026/september](https://docs.databricks.com/aws/en/release-notes/product/2026/september) | [G1](01%20Grundlagen/01%20Was%20ist%20CDF%20-%20Automatic%20vs.%20Legacy.md) |
| 13 | [aws/en/oltp/projects/sync-tables](https://docs.databricks.com/aws/en/oltp/projects/sync-tables) | [B3](05%20Lakebase%20CDF/03%20Synced%20Tables%20und%20LTAP.md) |
| 14 | [aws/en/structured-streaming/delta-lake](https://docs.databricks.com/aws/en/structured-streaming/delta-lake) | [L2](02%20Lesen/02%20Streaming%20-%20readStream%20und%20Optionen.md) |
| 15 | [aws/en/opensharing/read-data-open](https://docs.databricks.com/aws/en/opensharing/read-data-open) | [S2](04%20Delta%20Sharing/02%20CDF%20lesen%20%28Empfaenger%29.md) |
| 16 | [aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-share](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-share) | [S1](04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md) |
| 17 | [api/postgres/v1/cdf-status](https://docs.databricks.com/api/postgres/v1/cdf-status) | [B2](05%20Lakebase%20CDF/02%20Quickstart%20und%20REST-API.md) |
| 18 | [aws/en/oltp/projects/lakehouse-integrations](https://docs.databricks.com/aws/en/oltp/projects/lakehouse-integrations) | [B1](05%20Lakebase%20CDF/01%20Lakebase%20Change%20Data%20Feed.md) |
| 19 | [aws/en/ldp/developer/ldp-python-ref-apply-changes](https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-apply-changes) | [M2](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) |
| 20 | [aws/en/machine-learning/feature-store/online-feature-store](https://docs.databricks.com/aws/en/machine-learning/feature-store/online-feature-store) | [W](06%20Weitere%20Einsatzgebiete.md) |
| 21 | [aws/en/tables/operations/vacuum](https://docs.databricks.com/aws/en/tables/operations/vacuum) | [G3](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) |
| 22 | [aws/en/tables/features/row-tracking](https://docs.databricks.com/aws/en/tables/features/row-tracking) | [G2](01%20Grundlagen/02%20Schema%20und%20Metadatenspalten.md) |
| 23 | [aws/en/tables/table-properties](https://docs.databricks.com/aws/en/tables/table-properties) | [G3](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) |
| 24 | [api/postgres/v1/cdf-config](https://docs.databricks.com/api/postgres/v1/cdf-config) | [B2](05%20Lakebase%20CDF/02%20Quickstart%20und%20REST-API.md) |
| 25 | [aws/en/oltp/projects/api-usage](https://docs.databricks.com/aws/en/oltp/projects/api-usage) | [B2](05%20Lakebase%20CDF/02%20Quickstart%20und%20REST-API.md) |
| 26 | [aws/en/ldp/incremental-refresh](https://docs.databricks.com/aws/en/ldp/incremental-refresh) | [G3](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) · [W](06%20Weitere%20Einsatzgebiete.md) |
| 27 | [aws/en/opensharing/read-data-databricks](https://docs.databricks.com/aws/en/opensharing/read-data-databricks) | [S2](04%20Delta%20Sharing/02%20CDF%20lesen%20%28Empfaenger%29.md) |
| 28 | [aws/en/release-notes/whats-coming](https://docs.databricks.com/aws/en/release-notes/whats-coming) | [G1](01%20Grundlagen/01%20Was%20ist%20CDF%20-%20Automatic%20vs.%20Legacy.md) |
| 29 | [aws/en/release-notes/product/2026/august](https://docs.databricks.com/aws/en/release-notes/product/2026/august) | [M3](03%20Pipelines%20und%20Muster/03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md) |
| 30 | [aws/en/tables/features/feature-compatibility](https://docs.databricks.com/aws/en/tables/features/feature-compatibility) | [G3](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) |
| 31 | [aws/en/sql/get-started/sql-etl-tutorial](https://docs.databricks.com/aws/en/sql/get-started/sql-etl-tutorial) | [M2](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) |
| 32 | [aws/en/delta/iceberg-reads](https://docs.databricks.com/aws/en/delta/iceberg-reads) | [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 33 | [aws/en/iceberg/](https://docs.databricks.com/aws/en/iceberg/) | [B3](05%20Lakebase%20CDF/03%20Synced%20Tables%20und%20LTAP.md) · [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 34 | [aws/en/release-notes/runtime/19](https://docs.databricks.com/aws/en/release-notes/runtime/19) | [G1](01%20Grundlagen/01%20Was%20ist%20CDF%20-%20Automatic%20vs.%20Legacy.md) |
| 35 | [aws/en/oltp/projects/use-cases](https://docs.databricks.com/aws/en/oltp/projects/use-cases) | [B1](05%20Lakebase%20CDF/01%20Lakebase%20Change%20Data%20Feed.md) |
| 36 | [aws/en/ldp/recover-streaming](https://docs.databricks.com/aws/en/ldp/recover-streaming) | — Checkpoint-Wiederherstellung einer AUTO-CDC-Pipeline; kein CDF-spezifischer Inhalt |
| 37 | [aws/en/release-notes/dlt/2024/33/](https://docs.databricks.com/aws/en/release-notes/dlt/2024/33/) | [M3](03%20Pipelines%20und%20Muster/03%20CDF%20von%20AUTO-CDC-Zielen%20und%20Materialized%20Views.md) |
| 38 | [aws/en/release-notes/serverless/](https://docs.databricks.com/aws/en/release-notes/serverless/) | [G3](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) · [S2](04%20Delta%20Sharing/02%20CDF%20lesen%20%28Empfaenger%29.md) |
| 39 | [aws/en/ai-search/ai-search](https://docs.databricks.com/aws/en/ai-search/ai-search) | [W](06%20Weitere%20Einsatzgebiete.md) |
| 40 | [aws/en/ldp/tutorial-pipelines](https://docs.databricks.com/aws/en/ldp/tutorial-pipelines) | [M2](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) |
| 41 | [aws/en/error-messages/delta-concurrent-delete-delete-error-class](https://docs.databricks.com/aws/en/error-messages/delta-concurrent-delete-delete-error-class) | [G2](01%20Grundlagen/02%20Schema%20und%20Metadatenspalten.md) · [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 42 | [aws/en/tables/features/type-widening](https://docs.databricks.com/aws/en/tables/features/type-widening) | [S2](04%20Delta%20Sharing/02%20CDF%20lesen%20%28Empfaenger%29.md) · [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 43 | [aws/en/oltp/projects/ltap-overview](https://docs.databricks.com/aws/en/oltp/projects/ltap-overview) | [B3](05%20Lakebase%20CDF/03%20Synced%20Tables%20und%20LTAP.md) |
| 44 | [aws/en/delta/](https://docs.databricks.com/aws/en/delta/) | [G1](01%20Grundlagen/01%20Was%20ist%20CDF%20-%20Automatic%20vs.%20Legacy.md) |
| 45 | [aws/en/release-notes/runtime/15.4lts](https://docs.databricks.com/aws/en/release-notes/runtime/15.4lts) | [G2](01%20Grundlagen/02%20Schema%20und%20Metadatenspalten.md) · [G3](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) |
| 46 | [aws/en/error-messages/error-classes](https://docs.databricks.com/aws/en/error-messages/error-classes) | [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) · [S2](04%20Delta%20Sharing/02%20CDF%20lesen%20%28Empfaenger%29.md) · [M2](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) · [M4](03%20Pipelines%20und%20Muster/04%20Change%20Feeds%20bei%20Datei-Ingestion.md) |
| 47 | [aws/en/error-messages/delta-concurrent-delete-read-error-class](https://docs.databricks.com/aws/en/error-messages/delta-concurrent-delete-read-error-class) | [G2](01%20Grundlagen/02%20Schema%20und%20Metadatenspalten.md) · [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 48 | [aws/en/error-messages/delta-concurrent-append-error-class](https://docs.databricks.com/aws/en/error-messages/delta-concurrent-append-error-class) | [G2](01%20Grundlagen/02%20Schema%20und%20Metadatenspalten.md) · [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 49 | [aws/en/machine-learning/feature-store/feature-serving-tutorial](https://docs.databricks.com/aws/en/machine-learning/feature-store/feature-serving-tutorial) | [W](06%20Weitere%20Einsatzgebiete.md) |
| 50 | [aws/en/release-notes/lakebase/](https://docs.databricks.com/aws/en/release-notes/lakebase/) | [B1](05%20Lakebase%20CDF/01%20Lakebase%20Change%20Data%20Feed.md) |
| 51 | [aws/en/tables/features/column-mapping](https://docs.databricks.com/aws/en/tables/features/column-mapping) | [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 52 | [aws/en/oltp/projects/dabs-typical-project](https://docs.databricks.com/aws/en/oltp/projects/dabs-typical-project) | [B3](05%20Lakebase%20CDF/03%20Synced%20Tables%20und%20LTAP.md) |
| 53 | [aws/en/opensharing/manage-egress](https://docs.databricks.com/aws/en/opensharing/manage-egress) | [S1](04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md) |
| 54 | [aws/en/data-governance/unity-catalog/data-quality-monitoring/data-profiling/create-monitor-api](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring/data-profiling/create-monitor-api) | [W](06%20Weitere%20Einsatzgebiete.md) |
| 55 | [aws/en/ldp/database-replication](https://docs.databricks.com/aws/en/ldp/database-replication) | — AUTO-CDC-Replikation einer RDBMS-Tabelle; verlinkt über M2 (vorhandene Referenz, Abschnitt 9) |
| 56 | [aws/en/structured-streaming/lakebase](https://docs.databricks.com/aws/en/structured-streaming/lakebase) | [B1](05%20Lakebase%20CDF/01%20Lakebase%20Change%20Data%20Feed.md) · [B3](05%20Lakebase%20CDF/03%20Synced%20Tables%20und%20LTAP.md) |
| 57 | [aws/en/spark/api-options](https://docs.databricks.com/aws/en/spark/api-options) | [L2](02%20Lesen/02%20Streaming%20-%20readStream%20und%20Optionen.md) |
| 58 | [aws/en/sql/language-manual/sql-ref-syntax-aux-describe-share](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-share) | nur Querverweis „Related articles: Change data feed“ → Inhalt siehe [04/01](04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md) |
| 59 | [aws/en/tables/features/deletion-vectors](https://docs.databricks.com/aws/en/tables/features/deletion-vectors) | — kein CDF-Inhalt im Artikeltext |
| 60 | [aws/en/release-notes/product/](https://docs.databricks.com/aws/en/release-notes/product/) | [G1](01%20Grundlagen/01%20Was%20ist%20CDF%20-%20Automatic%20vs.%20Legacy.md) |
| 61 | [aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-share](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-share) | nur Querverweis „Related articles: Change data feed“ → Inhalt siehe [04/01](04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md) |
| 62 | [aws/en/opensharing/create-share](https://docs.databricks.com/aws/en/opensharing/create-share) | [S1](04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md) |
| 63 | [aws/en/ingestion/lakeflow-connect/faq](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/faq) | [G3](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) · [W](06%20Weitere%20Einsatzgebiete.md) |
| 64 | [aws/en/release-notes/](https://docs.databricks.com/aws/en/release-notes/) | — kein CDF-Inhalt (Release-Notes-Index) |
| 65 | [aws/en/error-messages/transaction-not-supported-error-class](https://docs.databricks.com/aws/en/error-messages/transaction-not-supported-error-class) | [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 66 | [aws/en/sql/language-manual/sql-ref-syntax-aux-show-all-in-share](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-all-in-share) | [S1](04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md) |
| 67 | [aws/en/ingestion/lakeflow-connect/smartsheet-limits](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/smartsheet-limits) | [W](06%20Weitere%20Einsatzgebiete.md) · [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 68 | [aws/en/error-messages/multi-statement-transaction-not-supported-error-class](https://docs.databricks.com/aws/en/error-messages/multi-statement-transaction-not-supported-error-class) | [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 69 | [aws/en/admin/system-tables/](https://docs.databricks.com/aws/en/admin/system-tables/) | [L2](02%20Lesen/02%20Streaming%20-%20readStream%20und%20Optionen.md) · [S2](04%20Delta%20Sharing/02%20CDF%20lesen%20%28Empfaenger%29.md) |
| 70 | [aws/en/error-messages/config-not-available-error-class](https://docs.databricks.com/aws/en/error-messages/config-not-available-error-class) | [G3](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) · [E](07%20Einschraenkungen%20und%20Fehlermeldungen.md) |
| 71 | [aws/en/oltp/upgrade-to-autoscaling](https://docs.databricks.com/aws/en/oltp/upgrade-to-autoscaling) | [B2](05%20Lakebase%20CDF/02%20Quickstart%20und%20REST-API.md) |
| 72 | [aws/en/ldp/best-practices/](https://docs.databricks.com/aws/en/ldp/best-practices/) | [M2](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) |
| 73 | [aws/en/tables/automatic-upgrades](https://docs.databricks.com/aws/en/tables/automatic-upgrades) | [G1](01%20Grundlagen/01%20Was%20ist%20CDF%20-%20Automatic%20vs.%20Legacy.md) |
| 74 | [aws/en/ldp/flows-replace-using](https://docs.databricks.com/aws/en/ldp/flows-replace-using) | [M2](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) |
| 75 | [aws/en/release-notes/product/2026/march](https://docs.databricks.com/aws/en/release-notes/product/2026/march) | — kein CDF-Inhalt im Artikeltext |
| 76 | [aws/en/oltp/projects/terraform-typical-project](https://docs.databricks.com/aws/en/oltp/projects/terraform-typical-project) | [B3](05%20Lakebase%20CDF/03%20Synced%20Tables%20und%20LTAP.md) |
| 77 | [aws/en/machine-learning/feature-store/feature-views](https://docs.databricks.com/aws/en/machine-learning/feature-store/feature-views) | [W](06%20Weitere%20Einsatzgebiete.md) |
| 78 | [aws/en/structured-streaming/production](https://docs.databricks.com/aws/en/structured-streaming/production) | [L2](02%20Lesen/02%20Streaming%20-%20readStream%20und%20Optionen.md) |
| 79 | [aws/en/delta/presto-integration](https://docs.databricks.com/aws/en/delta/presto-integration) | — kein CDF-Inhalt im Artikeltext |
| 80 | [aws/en/sql/language-manual/sql-ref-sharing](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-sharing) | nur Querverweis „Related articles: Change data feed“ → Inhalt siehe [04/01](04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md) |
| 81 | [aws/en/sql/language-manual/sql-ref-syntax-ddl-create-share](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-share) | nur Querverweis „Related articles: Change data feed“ → Inhalt siehe [04/01](04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md) |
| 82 | [aws/en/ldp/concepts/](https://docs.databricks.com/aws/en/ldp/concepts/) | — kein CDF-Inhalt im Artikeltext |
| 83 | [aws/en/release-notes/product/2025/june](https://docs.databricks.com/aws/en/release-notes/product/2025/june) | [M2](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) |
| 84 | [aws/en/sql/release-notes/2024](https://docs.databricks.com/aws/en/sql/release-notes/2024) | [G3](01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md) |
| 85 | [aws/en/release-notes/product/2025/july](https://docs.databricks.com/aws/en/release-notes/product/2025/july) | — kein CDF-Inhalt im Artikeltext |
| 86 | [aws/en/ingestion/file](https://docs.databricks.com/aws/en/ingestion/file) | [M4](03%20Pipelines%20und%20Muster/04%20Change%20Feeds%20bei%20Datei-Ingestion.md) |
| 87 | [aws/en/error-messages/cf-invalid-change-feed-response-error-class](https://docs.databricks.com/aws/en/error-messages/cf-invalid-change-feed-response-error-class) | [M4](03%20Pipelines%20und%20Muster/04%20Change%20Feeds%20bei%20Datei-Ingestion.md) |
| 88 | [aws/en/data-engineering/schema-evolution](https://docs.databricks.com/aws/en/data-engineering/schema-evolution) | — kein CDF-Inhalt im Artikeltext |
| 89 | [aws/en/oltp/projects/lakebase-text](https://docs.databricks.com/aws/en/oltp/projects/lakebase-text) | — kein CDF-Inhalt im Artikeltext |
| 90 | [aws/en/delta/merge](https://docs.databricks.com/aws/en/delta/merge) | — kein CDF-Inhalt im Artikeltext (MERGE allgemein) |
| 91 | [aws/en/sql/language-manual/sql-ref-syntax-aux-show-shares](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-shares) | nur Querverweis „Related articles: Change data feed“ → Inhalt siehe [04/01](04%20Delta%20Sharing/01%20CDF%20teilen%20%28Provider%29.md) |
| 92 | [aws/en/ingestion/lakeflow-connect/postgresql-source-setup](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/postgresql-source-setup) | — kein CDF-Inhalt im Artikeltext |
| 93 | [aws/en/tables/features/variant-shredding](https://docs.databricks.com/aws/en/tables/features/variant-shredding) | — kein CDF-Inhalt im Artikeltext |
| 94 | [aws/en/tables/history](https://docs.databricks.com/aws/en/tables/history) | — kein CDF-Inhalt im Artikeltext (Tabellenhistorie allgemein) |
| 95 | [aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-view](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-view) | — kein CDF-Inhalt im Artikeltext |
| 96 | [aws/en/resources/glossary](https://docs.databricks.com/aws/en/resources/glossary) | [B1](05%20Lakebase%20CDF/01%20Lakebase%20Change%20Data%20Feed.md) |
| 97 | [aws/en/data-governance/unity-catalog/data-quality-monitoring/data-profiling/create-monitor-ui](https://docs.databricks.com/aws/en/data-governance/unity-catalog/data-quality-monitoring/data-profiling/create-monitor-ui) | [W](06%20Weitere%20Einsatzgebiete.md) |
| 98 | [aws/en/release-notes/runtime/maintenance-updates](https://docs.databricks.com/aws/en/release-notes/runtime/maintenance-updates) | [G2](01%20Grundlagen/02%20Schema%20und%20Metadatenspalten.md) |
| 99 | [aws/en/ldp/flows-backfill](https://docs.databricks.com/aws/en/ldp/flows-backfill) | [M2](03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md) |
| 100 | [aws/en/jobs/trigger-table-update](https://docs.databricks.com/aws/en/jobs/trigger-table-update) | — kein CDF-Inhalt im Artikeltext (Table-Update-Trigger) |

Kürzel: **G1** = 01 Was ist CDF - Automatic vs. Legacy · **G2** = 02 Schema und Metadatenspalten · **G3** = 03 Tabelleneigenschaften, Protokoll und Speicher · **L1** = 01 Batch - table_changes und readChangeFeed · **L2** = 02 Streaming - readStream und Optionen · **M1** = 01 Demo - Silver nach Gold propagieren · **M2** = 02 CDF und AUTO CDC · **M3** = 03 CDF von AUTO-CDC-Zielen und Materialized Views · **M4** = 04 Change Feeds bei Datei-Ingestion · **S1** = 01 CDF teilen (Provider) · **S2** = 02 CDF lesen (Empfaenger) · **B1** = 01 Lakebase Change Data Feed · **B2** = 02 Quickstart und REST-API · **B3** = 03 Synced Tables und LTAP · **W** = 06 Weitere Einsatzgebiete · **E** = 07 Einschraenkungen und Fehlermeldungen
