# Change Data Capture (CDC) — Übersicht

**CDC** beschreibt, **wie Änderungen erfasst und weitergegeben werden**: Welche Zeilen wurden in der Quelle eingefügt, geändert oder gelöscht? Das Ergebnis ist ein Strom von Change-Events.

**SCD** (Slowly Changing Dimensions) beschreibt dagegen, **wie diese Änderungen im Ziel gespeichert werden** (überschreiben oder versionieren) → siehe [../SCD/00 Uebersicht.md](../SCD/00%20Uebersicht.md).

> Kurz: **CDC ist der Input**, **SCD ist die Speicherstrategie**. Beide treten oft zusammen auf, aber nicht immer (siehe [06 CDC ohne SCD](06%20CDC%20ohne%20SCD.md)).

> Konventionen in den Beispielen: `catalog.schema` = Unity-Catalog-Ziel, `/Volumes/catalog/schema/landing/` = Quellordner. Innerhalb von Pipelines werden Tabellen ohne Katalog/Schema angesprochen (Default der Pipeline).

---

## Wie CDC-Events entstehen

| Verfahren | Funktionsweise | Erkennt Deletes? | Typische Technik |
|---|---|---|---|
| **Log-basiert** | Transaktionslog der Quelldatenbank wird ausgelesen | ✅ | Debezium, Kafka, Lakeflow Connect (Managed Connectors) |
| **Timestamp-basiert** | `WHERE last_modified > letzter_watermark` | ❌ (nur Soft Deletes) | Lakeflow Jobs + Control-Tabelle, Lakehouse Federation |
| **Snapshot-Vergleich** | zwei Voll-Snapshots werden verglichen | ✅ | `AUTO CDC FROM SNAPSHOT`, `MERGE … WHEN NOT MATCHED BY SOURCE` |
| **Change Data Feed (CDF)** | Delta-Tabelle protokolliert ihre eigenen Zeilenänderungen | ✅ | `table_changes()`, `readChangeFeed` |

---

## Die Dateien in diesem Ordner

| # | Datei | Kombination |
|---|---|---|
| 1 | [Debezium-Dateien mit Auto Loader und AUTO CDC](01%20Debezium-Dateien%20mit%20Auto%20Loader%20und%20AUTO%20CDC.md) | **End-to-End:** Auto Loader → Bronze → Expectations → Silver SCD 1 **und** SCD 2 → Gold MV |
| 2 | [CDC aus Kafka](02%20CDC%20aus%20Kafka.md) | Kafka → `from_json` → AUTO CDC · mehrere Topics per Fan-in |
| 3 | [CDC prozedural mit foreachBatch und MERGE](03%20CDC%20prozedural%20mit%20foreachBatch%20und%20MERGE.md) | Structured Streaming + `foreachBatch` + `MERGE` (ohne Pipeline) |
| 4 | [Change Data Feed – Änderungen weiterreichen](04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md) | CDF → Silver/Gold · CDF → AUTO CDC · DSGVO-Löschungen propagieren |
| 5 | [Timestamp-basiertes CDC mit Lakeflow Jobs](05%20Timestamp-basiertes%20CDC%20mit%20Lakeflow%20Jobs.md) | Watermark-Control-Tabelle + For-Each-Task + `MERGE` + DAB |
| 6 | [CDC ohne SCD](06%20CDC%20ohne%20SCD.md) | Change-Log (Append) · Event-Weitergabe an Kafka (Sink) · inkrementelle Aggregation |

---

## Entscheidungshilfe

| Situation | Empfehlung |
|---|---|
| Change-Events (insert/update/delete + Sequenz) kommen als Dateien oder Stream | `AUTO CDC INTO` / `create_auto_cdc_flow` → [01](01%20Debezium-Dateien%20mit%20Auto%20Loader%20und%20AUTO%20CDC.md), [02](02%20CDC%20aus%20Kafka.md) |
| Kein Pipeline-Kontext, freie Merge-Logik nötig | `foreachBatch` + `MERGE` → [03](03%20CDC%20prozedural%20mit%20foreachBatch%20und%20MERGE.md) |
| Änderungen **innerhalb** des Lakehouse weiterreichen (Bronze → Silver → Gold) | Change Data Feed → [04](04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md) |
| Quelle hat nur eine `last_modified`-Spalte | Timestamp-basiert mit Watermark → [05](05%20Timestamp-basiertes%20CDC%20mit%20Lakeflow%20Jobs.md) |
| Quelle liefert nur Voll-Snapshots | `create_auto_cdc_from_snapshot_flow` → [../SCD/01](../SCD/01%20SCD%20Type%201%20-%20Umsetzungswege.md) |
| Relationale Quelle (SQL Server, Postgres, …) oder SaaS (Salesforce, …) | Lakeflow Connect Managed Connector → [../SCD/07](../SCD/07%20SCD%20in%20Lakeflow%20Connect.md) |

**Merksatz:** `AUTO CDC` bringt Änderungen an der Ingestion-Grenze **herein**, CDF trägt sie durchs Lakehouse **weiter**.

---

## Verwandte Themen

- Vollständige AUTO-CDC-Referenz (alle Parameter, Sequenzierung, Limitierungen): [../Data Transformation and Modeling/Vertiefung …/03 Change Data Capture (CDC).md](../Data%20Transformation%20and%20Modeling/Vertiefung%20%28ueber%20Pruefungsumfang%20hinaus%29/Lakeflow%20Declarative%20Pipelines%20-%20Transformation%20und%20CDC/03%20Change%20Data%20Capture%20%28CDC%29.md)
- CDC-Grundbegriffe: [../Data Transformation and Modeling/04 DML und Kernkonzepte/03 Schema Evolution, CDC-Grundbegriffe, Join und Aggregation.md](../Data%20Transformation%20and%20Modeling/04%20DML%20und%20Kernkonzepte/03%20Schema%20Evolution%2C%20CDC-Grundbegriffe%2C%20Join%20und%20Aggregation.md)
- Datei-Fälle: [Fall 5 – Voll-Snapshots](../Ingestion/Datei%20Ingestion%20Varianten/05%20Periodische%20Voll-Snapshots.md) · [Fall 6 – Change-Events in Dateien](../Ingestion/Datei%20Ingestion%20Varianten/06%20Change-Events%20in%20Dateien.md) · [Dedup- und Upsert-Muster](../Ingestion/Datei%20Ingestion%20Varianten/99%20Dedup%20und%20Upsert%20Muster.md)

## Quellen

- [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)
- [Change data capture and snapshots](https://docs.databricks.com/aws/en/data-engineering/what-is-cdc)
- [Use Delta Lake change data feed on Databricks](https://docs.databricks.com/aws/en/delta/delta-change-data-feed)
- [Upsert into a Delta Lake table using merge](https://docs.databricks.com/aws/en/delta/merge)
