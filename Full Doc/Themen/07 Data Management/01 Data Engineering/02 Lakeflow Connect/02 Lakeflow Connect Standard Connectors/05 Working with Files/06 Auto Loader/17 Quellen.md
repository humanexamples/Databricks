# Auto Loader — Quellen und Verifikationsmethodik

Die Dateien in diesem Ordner fassen die Funktionsweise von Databricks **Auto Loader** (die `cloudFiles`-Streaming-Quelle) zusammen. Sie sind aus der früheren Sammeldatei `_autoloader.md` hervorgegangen und decken gezielt alle 14 in den Databricks-Quellen gelisteten Auto-Loader-Unterseiten ab.

**Methodik:** Jede faktische Aussage wurde per `WebFetch` gegen die offizielle Databricks-Online-Dokumentation verifiziert; bei spezifischen/auffälligen Behauptungen (Zahlen, Default-Werte, Options-Namen, wörtliche Zitate) wurde ein zweiter, unabhängiger Abruf (meist die AWS- und die Azure/Microsoft-Learn-Spiegelseite) zur Gegenprüfung durchgeführt. Aussagen, die sich nicht bestätigen ließen, sind als "**Ungeklärt:**" gekennzeichnet, korrigierte Annahmen als "**Korrektur:**".

Letzter vollständiger Abruf aller Seiten: **07.09.2026** (vorherige Fassung 18.08.2026).

---

## Die 14 vorgegebenen Databricks-Seiten

| # | Seite | Zugeordnete Datei | URL |
|---|---|---|---|
| 1 | What is Auto Loader? | [00 Überblick.md](00%20Überblick.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/ |
| 2 | Using Auto Loader with Unity Catalog | [03 Unity-Catalog-Integration.md](03%20Unity-Catalog-Integration.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/unity-catalog |
| 3 | Configure schema inference and evolution in Auto Loader | [01 Schema-Inferenz und -Evolution.md](01%20Schema-Inferenz%20und%20-Evolution.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema |
| 4 | Automatic type widening with Auto Loader | [02 Automatisches Type Widening.md](02%20Automatisches%20Type%20Widening.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/type-widening |
| 5 | Compare Auto Loader file detection modes | [04 Datei-Erkennungsmodi.md](04%20Datei-Erkennungsmodi.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-detection-modes |
| 6 | Configure Auto Loader streams in directory listing mode | [05 Directory Listing Mode.md](05%20Directory%20Listing%20Mode.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/directory-listing-mode |
| 7 | Configure Auto Loader streams in file notification mode | [06 File Notification Mode.md](06%20File%20Notification%20Mode.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-notification-mode |
| 8 | Auto Loader with file events explained | [07 Wie File Events funktionieren.md](07%20Wie%20File%20Events%20funktionieren.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-events-explained |
| 9 | Migrating to file events | [08 Migration zu File Events.md](08%20Migration%20zu%20File%20Events.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/migrating-to-file-events |
| 10 | Configure Auto Loader for production workloads | [12 Produktionsbetrieb.md](12%20Produktionsbetrieb.md), [09 Datei-Tracking und Checkpoints.md](09%20Datei-Tracking%20und%20Checkpoints.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production |
| 11 | Auto Loader best practices | [11 Best Practices.md](11%20Best%20Practices.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/best-practices |
| 12 | Clean up processed files with Auto Loader | [10 Clean Source (Quelldateien aufräumen).md](10%20Clean%20Source%20%28Quelldateien%20aufräumen%29.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/clean-source |
| 13 | Monitor and observe Auto Loader | [13 Observability.md](13%20Observability.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/observability |
| 14 | Common data loading patterns with Auto Loader | [14 Common Data Loading Patterns.md](14%20Common%20Data%20Loading%20Patterns.md) | https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/patterns |

Zusätzlich: **Auto Loader FAQ** → [15 FAQ.md](15%20FAQ.md) — https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/faq.html

---

## Für Gegenprüfungen zusätzlich abgerufene Referenzseiten

- Compare Auto Loader file detection modes (Azure-Spiegelseite): https://learn.microsoft.com/en-us/azure/databricks/ingestion/cloud-object-storage/auto-loader/file-detection-modes
- Auto Loader FAQ (Azure-Spiegelseite): https://learn.microsoft.com/en-us/azure/databricks/ingestion/cloud-object-storage/auto-loader/faq
- Ingest data from cloud object storage (Auto Loader vs. COPY INTO): https://docs.databricks.com/aws/en/ingestion/cloud-object-storage
- Spark API options reference (`cloudFiles.*`-Defaultwerte): https://docs.databricks.com/aws/en/spark/api-options
- cloud_files_state table-valued function (AWS): https://docs.databricks.com/aws/en/sql/language-manual/functions/cloud_files_state
- cloud_files_state table-valued function (Azure-Spiegelseite): https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/functions/cloud_files_state
- Flows in Lakeflow pipelines: https://docs.databricks.com/aws/en/ldp/flows
- Use flows in Lakeflow pipelines (`raw_orders_us`/`eu`/`apac`): https://docs.databricks.com/aws/en/ldp/flow-examples
- Load data with Lakeflow Declarative Pipelines: https://docs.databricks.com/aws/en/dlt/load

---

## Diagramme

Die einzigen Bilder in den 14 Seiten stammen von "Auto Loader with file events explained" und sind in [07 Wie File Events funktionieren.md](07%20Wie%20File%20Events%20funktionieren.md) eingebunden:

- `https://docs.databricks.com/aws/en/assets/images/cloud-storage-event-notification-systems-dfa53e36957ad28b1c038182a76a64fc.png`
- `https://docs.databricks.com/aws/en/assets/images/auto-loader-with-file-events-a22c49fbd36146c6bc2be943e51213c0.png`
- `https://docs.databricks.com/aws/en/assets/images/file-events-vs-classic-file-events-761dedde768661a357b53a42602e862c.png`

---

## Sekundäre, in Schwesterdateien verifizierte Quellen

- [`../_read_files.md`](../_read_files.md) — SQL-Tabellenfunktion `read_files` (Batch und `STREAM read_files`).
- [`../_spark_read.md`](../_spark_read.md) — `spark.read` / `spark.readStream`.
- [`../05 Diagnose- und Herkunftsspalten/_rescued_data.md`](../05%20Diagnose-%20und%20Herkunftsspalten/_rescued_data.md) — werkzeugübergreifende Rescued-Data-Column.
- [`../05 Diagnose- und Herkunftsspalten/_metadata.md`](../05%20Diagnose-%20und%20Herkunftsspalten/_metadata.md) — `_metadata`-Spalte.

---

## Als "Ungeklärt" verbliebene Punkte

- Das Verhalten einer per `schemaHints` vorab deklarierten, aber noch nicht in den Daten vorhandenen Spalte unter `addNewColumns` ([01 Schema-Inferenz und -Evolution.md](01%20Schema-Inferenz%20und%20-Evolution.md)).
- Die konkrete technische Begründung, warum File Notification performanter ist als Directory Listing ([04 Datei-Erkennungsmodi.md](04%20Datei-Erkennungsmodi.md)).
- Detailtiefe des Abschnitts "Handle out-of-order data" ([00 Überblick.md](00%20Überblick.md)).
- Die Diskrepanz zwischen dem dokumentierten `ingestion_state`-Wert `INGESTED` und dem in einem Beispiel der Observability-Seite selbst auftauchenden, nicht dokumentierten Wert `COMMITTED` ([13 Observability.md](13%20Observability.md)).
- Widersprüchliche DBR-Versionsangabe (15.3 vs. 15.4 LTS) für die Startzeit-Optimierung — zugunsten des zweifach bestätigten Werts 15.4 LTS aufgelöst.
