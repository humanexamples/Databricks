# Datei Ingestion Varianten — Übersicht

Referenz auf Basis der Databricks-Onlinedokumentation (Stand 2026-09). Diese Übersicht listet die unterschiedlichen Datei-Ingestion-**Fälle**; jede verlinkte Datei zeigt für ihren Fall **alle** gängigen Umsetzungswege mit Code-Beispielen.

> Konventionen in den Beispielen: `catalog.schema` = Unity-Catalog-Ziel, `/Volumes/catalog/schema/landing/` = Quellordner, `/Volumes/catalog/schema/_checkpoints/…` = Checkpoint/Schema-Location.

---

## Die Fälle im Überblick

| # | Fall | Kurzbeschreibung | Umsetzung mit |
|---|---|---|---|
| 1 | [Einmaliger, statischer Bestand](01%20Einmaliger%2C%20statischer%20Bestand.md) | alle Dateien liegen bereits vor, es kommen keine neuen dazu | CTAS mit `read_files()` · `spark.read` + `overwrite` · `COPY INTO` einmalig · Auto Loader `availableNow` · `INSERT INTO … FROM read_files()` (nicht idempotent) |
| 2 | [Append-only](02%20Append-only.md) | neue, **unveränderliche** Dateien kommen laufend dazu (Standardfall) – inkl. **periodischer Drop mit eindeutigem Dateinamen** (z. B. täglich `orders_2026-09-04.csv`) | Auto Loader (Streaming / `availableNow` / `STREAM read_files` in Streaming Table) · `COPY INTO` im geplanten Job · Python-Pipeline (`@dp.table`) · optional gezielt nur die neueste Datei (`PATTERN` / `modifiedAfter`) |
| 3 | [Gleiche Datei wird überschrieben](03%20Gleiche%20Datei%20wird%20ueberschrieben.md) | neuer Inhalt, **gleicher Name/Pfad** – Standard: neuer Inhalt wird ignoriert. Gegliedert nach Ziel-Verhalten: **1** komplett überschreiben · **2** Append · **3** Upsert ohne Historie (SCD 1) · **4** Upsert mit Historie (SCD 2) | je Abschnitt SQL + Python-DataFrame-API + Auto Loader + deklarativ (`@dp.*` / `create_auto_cdc_from_snapshot_flow`), jeweils **⏱ feste Periode** (Job-Cron / `SCHEDULE REFRESH`) *und* **⚡ ereignisgesteuert bei Überschreiben** (Auto Loader `useNotifications` / Streaming Table `TRIGGER ON UPDATE`). Kernbausteine `CREATE OR REPLACE TABLE`/`INSERT OVERWRITE`, `INSERT INTO`, `COPY INTO force`, `allowOverwrites`, `MERGE` / `DeltaTable.merge`, CDF |
| 4 | [Datei wächst](04%20Datei%20waechst.md) | Daten werden an **dieselbe** Datei angehängt – von Databricks nicht sauber unterstützt | `allowOverwrites` (liest ganze Datei neu) + Dedup · **besser:** rotierende Dateien → Fall 2 · Streaming direkt aus der Quelle (Kafka/Kinesis/Zerobus) |
| 5 | [Periodische Voll-Snapshots](05%20Periodische%20Voll-Snapshots.md) | jede Lieferung = kompletter aktueller Stand | `create_auto_cdc_from_snapshot_flow` (SCD 1/2) · manuell `MERGE` (+ `WHEN NOT MATCHED BY SOURCE THEN DELETE`) · `CREATE OR REPLACE` |
| 6 | [Change-Events in den Dateien](06%20Change-Events%20in%20Dateien.md) | Datei enthält insert/update/delete mit Sequenz | `AUTO CDC INTO` (SQL) / `create_auto_cdc_flow` (Python), SCD 1/2 · manuell `foreachBatch` + `MERGE` |
| 7 | [Backfill zusätzlich zum Stream](07%20Backfill%20zusaetzlich%20zum%20Stream.md) | großer Altbestand + laufender Zulauf | Auto Loader `includeExistingFiles` (Default `true`) · `cloudFiles.backfillInterval` (Notification-Modus) · getrennte Backfill-Ladung (`COPY INTO`/CTAS aus Archivpfad) · Durchsatz via `maxFilesPerTrigger` |
| 8 | [Späte / unsortierte Dateien](08%20Spaete%2C%20unsortierte%20Dateien.md) | Datei von gestern kommt heute an | Auto Loader verarbeitet sie normal (Reihenfolge egal) · fachliche Reihenfolge über `SEQUENCE BY` / `row_number()` · Watermark bei Aggregation |
| 9 | [Korrektur / Teilmenge neu laden](09%20Korrektur%2C%20Teilmenge%20neu%20laden.md) | einzelne Dateien nachträglich korrigiert | `COPY INTO` mit `FILES` / `PATTERN` + `force` · Auto Loader: neue Namen **oder** `allowOverwrites` · `INSERT OVERWRITE` / `REPLACE WHERE` für Ziel-Bereich |
| 10 | [Mehrere Quellordner → eine Zieltabelle](10%20Mehrere%20Quellordner%20%28Multiplex%29.md) | Multiplex mehrerer Landing-Ordner | mehrere Append-Flows (`CREATE FLOW … INSERT INTO … BY NAME`) · Python `@dp.append_flow` · gemeinsamer Wurzelpfad `recursiveFileLookup` · Glob-Pfad |
| 11 | [Schema ändert sich über die Zeit](11%20Schema%20aendert%20sich%20ueber%20die%20Zeit.md) | neue Spalten, Typänderungen | Auto Loader `schemaEvolutionMode` (`addNewColumns` / `rescue` / `none` / `failOnNewColumns`) + `schemaHints` · `COPY INTO` `mergeSchema` · alles als `VARIANT` · `MERGE WITH SCHEMA EVOLUTION` |
| 12 | [Zeitfenster- / gefilterte Ingestion](12%20Zeitfenster-%20und%20gefilterte%20Ingestion.md) | nur bestimmte Dateien laden | `modifiedAfter` / `modifiedBefore` · `pathGlobFilter` / `PATTERN` · Unterordner-Filter · `ignoreCorruptFiles` / `ignoreMissingFiles` |
| 13 | [Verarbeitete Dateien aufräumen](13%20Verarbeitete%20Dateien%20aufraeumen.md) | archivieren oder löschen nach der Verarbeitung | Auto Loader `cloudFiles.cleanSource` (`MOVE` / `DELETE`) · manuell `dbutils.fs.mv` / `rm` nach dem Lauf |

Grundempfehlung von Databricks: **nur unveränderliche (immutable) Dateien** ingestieren; für sehr große / häufige Dateimengen Auto Loader statt `COPY INTO`.

---

## Wie eine Datei als „bereits verarbeitet" erkannt wird

| Verfahren | Erkennungsmerkmal | Reaktion auf **gleichen Namen, neuen Inhalt** |
|---|---|---|
| `read_files()` Batch | – (kein Tracking) | Inhalt wird bei jedem Lauf neu gelesen |
| `COPY INTO` | Dateiliste in der Delta-Historie | Datei wird **übersprungen**, auch wenn sie geändert wurde – Neuladen nur mit `force = true` |
| Auto Loader (Standard) | **Dateipfad** im Checkpoint | Datei gilt als erledigt, neuer Inhalt wird **ignoriert** |
| Auto Loader mit `cloudFiles.allowOverwrites = true` | Pfad **+ last-modified-Timestamp (+ Größe)** | Datei wird **komplett** neu verarbeitet → Duplikate downstream selbst auflösen |
| File-Arrival-Trigger (Job) | gesehene Pfade | Überschreiben mit gleichem Namen **löst keinen Lauf aus** |

Auto-Loader-Zustand inspizieren:

```sql
SELECT * FROM cloud_files_state('/Volumes/catalog/schema/_checkpoints/bronze');
```

Ausführlicher: [../File Tracking.md](../File%20Tracking.md).

---

## Entscheidungshilfe

| Frage | Empfehlung |
|---|---|
| Einmalige/kleine Ad-hoc-Ladung? | `CREATE TABLE AS … read_files()` |
| Inkrementell, ~Tausende Dateien, SQL-Job? | `COPY INTO` |
| Inkrementell/Streaming, viele Dateien, Schema Evolution? | Auto Loader (`cloudFiles` bzw. `STREAM read_files`) |
| Gleiche Datei wird überschrieben, Zeilen-Updates? | Auto Loader `allowOverwrites` **+** `foreachBatch`/`MERGE` |
| Jede Lieferung = Voll-Snapshot? | `create_auto_cdc_from_snapshot_flow` (SCD 1/2) |
| Dateien enthalten Change-Events? | `AUTO CDC INTO` / `create_auto_cdc_flow` |
| Nur eine Teilmenge neu laden? | `COPY INTO` mit `FILES` / `PATTERN` + `force` |
| Quelle liefert wachsende Einzeldatei? | auf rotierende Dateien umstellen; sonst `allowOverwrites` + Upsert |

### Die drei Datei-Kernmethoden im Vergleich

| Merkmal | CTAS + `read_files()` / `spark.read` | `COPY INTO` | Auto Loader (`cloudFiles` / `STREAM read_files`) |
|---|---|---|---|
| Ingestion-Typ | Batch (Full Refresh) | Incremental Batch | Inkrementell (Batch oder Streaming) |
| Anwendungsfälle | kleine Datasets, einmalige/Ad-hoc-Ladung | ideal für **Tausende** Dateien | skaliert auf **Millionen+** Dateien/Stunde, Backfills mit Milliarden Dateien |
| Schnittstelle | Python (`spark.read`), SQL (CTAS) | SQL | Python (`spark.readStream`), SQL mit Declarative Pipelines, Streaming Tables in DBSQL |
| Idempotenz / File Tracking | ❌ kein Tracking (✅ via Full Refresh mit `CREATE OR REPLACE`) | ✅ Tracking im Delta-Transaktionslog der Zieltabelle | ✅ RocksDB-Checkpoint, exactly-once |
| Schema-Evolution | manuell / beim Lesen abgeleitet | mit Optionen (`mergeSchema`) | automatische Erkennung + Evolution (`schemaEvolutionMode`) |
| Latenz | hoch | moderat (geplant) | niedrig oder hoch, je nach Konfiguration |

---

## Referenzabschnitte

- [98 Trigger und Zeitplanung.md](98%20Trigger%20und%20Zeitplanung.md)
- [99 Dedup und Upsert Muster.md](99%20Dedup%20und%20Upsert%20Muster.md)

## Verwandte Themen

- [../File Tracking.md](../File%20Tracking.md) · [../Schema Evolution.md](../Schema%20Evolution.md) · [../Schema Inference.md](../Schema%20Inference.md) · [../Rescued Data.md](../Rescued%20Data.md)
- Methodenvergleich (Kurs): [../../07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/04 Streaming Ingestion/01 Data Ingestion.md](../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/04%20Streaming%20Ingestion/01%20Data%20Ingestion.md)
- Standard Connector wählen: [../../07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/00 Standard Connector waehlen.md](../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/00%20Standard%20Connector%20waehlen.md)

## Quellen

- [Auto Loader FAQ](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/faq)
- [What is Auto Loader?](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)
- [Auto Loader – Spark API options reference](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options)
- [Common data loading patterns (Auto Loader)](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/patterns)
- [Configure Auto Loader for production workloads](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production)
- [COPY INTO (SQL language manual)](https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into)
- [Common data loading patterns using COPY INTO](https://docs.databricks.com/en/ingestion/cloud-object-storage/copy-into/examples.html)
- [Get started using COPY INTO to load data](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/)
- [Ingest data from cloud object storage](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/)
- [read_files table-valued function](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files)
- [CREATE STREAMING TABLE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table)
- [Load data using streaming tables in Databricks SQL](https://docs.databricks.com/aws/en/sql/load-data-streaming-table)
- [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)
- [Change data capture and snapshots](https://docs.databricks.com/aws/en/data-engineering/what-is-cdc)
- [create_auto_cdc_from_snapshot_flow](https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-apply-changes-from-snapshot)
- [Upsert into a Delta Lake table using merge](https://docs.databricks.com/aws/en/delta/merge)
- [Use foreachBatch to write to arbitrary data sinks](https://docs.databricks.com/aws/en/structured-streaming/foreach)
- [Trigger jobs when new files arrive](https://docs.databricks.com/aws/en/jobs/file-arrival-triggers)
- [cloud_files_state table-valued function](https://docs.databricks.com/en/sql/language-manual/functions/cloud_files_state.html)
