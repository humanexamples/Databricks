# Predictive Optimization — Zusammenspiel mit anderen Features

PO ist die **Hintergrund-Engine** für mehrere andere Automatisierungen. Wer PO deaktiviert, verliert auch diese.

| Feature | Braucht PO? | Was PO dafür tut |
|---|---|---|
| Automatic Liquid Clustering (`CLUSTER BY AUTO`) | ✅ | Wählt Clustering-Keys, führt Clustering aus |
| Liquid Clustering mit festen Keys | ❌ (aber empfohlen) | Führt `OPTIMIZE` (inkrementelles Clustering) automatisch aus |
| Automatische Statistiken / Data Skipping | ✅ für die intelligente Spaltenauswahl | Stats-on-Write, `ANALYZE` im Hintergrund |
| Auto-TTL (`DELETE ROWS … DAYS AFTER`) | ✅ | Führt `DELETE` → `PURGE` → `VACUUM` aus |
| Automatic Upgrades | ❌ (eigenes Feature) | ergänzend: PO pflegt Layout, Upgrades aktivieren Table Features |
| Lakeflow Pipelines (Streaming Tables, MVs) | ergänzend | ersetzt `pipelines.autoOptimize.managed` |

---

## 1. Automatic Liquid Clustering (`CLUSTER BY AUTO`)

```sql
CREATE OR REPLACE TABLE table1 (column01 INT, column02 STRING) CLUSTER BY AUTO;
ALTER TABLE table1 CLUSTER BY AUTO;   -- bestehende Tabelle
ALTER TABLE table1 CLUSTER BY NONE;   -- deaktivieren
```

**Voraussetzungen:** DBR **15.4 LTS+** (Delta) bzw. **18.0+** (Iceberg v3, **nicht** v2), **UC-Managed-Table**, **PO aktiviert**.

**Wie PO die Keys wählt:**
1. **Workload-Analyse:** historische Query-Filter (`WHERE`, `JOIN`) der Tabelle auswerten.
2. **Modellierung:** vergangene Queries mit Kandidaten-Keys simulieren.
3. **Kosten-Nutzen:** Keys werden nur geändert, „when the predicted cost savings from data skipping improvements outweigh the data clustering cost".

Die Keys erscheinen **nicht sofort** — PO braucht zuerst genug Query-History. In der Systemtabelle sichtbar als `AUTO_CLUSTERING_COLUMN_SELECTION`.

**OPTIMIZE-Empfehlung:**
- **Ohne PO:** regelmäßige `OPTIMIZE`-Jobs planen, bei vielen Updates/Inserts **alle 1–2 Stunden**.
- **Mit PO:** „Databricks recommends disabling any scheduled OPTIMIZE jobs."

---

## 2. Statistiken und Data Skipping

| | External Table | UC-Managed-Table mit PO |
|---|---|---|
| Welche Spalten bekommen Min/Max-Statistiken? | Die **ersten 32 Spalten** (`delta.dataSkippingNumIndexedCols`) | Die Spalten, die **am häufigsten in Query-Filtern** vorkommen |
| 32-Spalten-Grenze | ja | **nein** |
| Wann werden Statistiken aktualisiert? | Beim Schreiben (nur indizierte Spalten), sonst manuell `ANALYZE` | Stats-on-Write + automatisches `ANALYZE`, sobald Statistiken veralten |

Ohne PO steuert man die Spalten manuell (ab DBR 13.3 LTS):

```sql
ALTER TABLE t SET TBLPROPERTIES ('delta.dataSkippingStatsColumns' = 'col1, col2, col3');
```

> `dataSkippingStatsColumns` hat Vorrang vor `dataSkippingNumIndexedCols`.

---

## 3. Auto-TTL (automatisches Löschen alter Zeilen)

```sql
ALTER TABLE my_catalog.my_schema.my_table DELETE ROWS 30 DAYS AFTER created_at;
ALTER TABLE my_catalog.my_schema.my_table DROP ROW DELETION;   -- deaktivieren
```

- **PO muss aktiviert sein** — ohne PO führt Auto-TTL keine Löschungen aus.
- DBR **17.3+**, `MODIFY`-Recht, Timestamp-Spalte vom Typ `DATE`/`TIMESTAMP`/`TIMESTAMP_NTZ`.
- PO führt nacheinander aus: **`DELETE`** (logisch) → **`PURGE`** (bei Deletion Vectors physisch umschreiben) → **`VACUUM`** (endgültig entfernen).
- Nicht für Materialized Views.
- Streaming-Leser einer Auto-TTL-Tabelle brauchen `skipChangeCommits`.

Details: [Full Doc: DROP, OPTIMIZE, VACUUM und Auto-TTL](../../../Full%20Doc/Themen/01%20Platform/02%20Tables/10%20Tabellenoperationen/02%20DROP%2C%20OPTIMIZE%2C%20VACUUM%20und%20Auto-TTL.md)

---

## 4. Automatic Upgrades

Beide Features ergänzen sich, sind aber **unterschiedlich**:

> „Predictive optimization maintains your data layout through operations such as compaction and vacuum, with the option to use automatic liquid clustering. Automatic upgrades turn on new table features, such as row tracking or Checkpoint V2."

| | Predictive Optimization | Automatic Upgrades |
|---|---|---|
| Aufgabe | **Datenlayout pflegen** (Compaction, Clustering, VACUUM, ANALYZE) | **Table Features aktivieren** (Row Tracking, Checkpoint V2, Catalog Commits, Parquet v2, …) |
| Monitoring | `system.storage.predictive_optimization_operations_history` | `system.storage.table_auto_upgrade_operations_history` |
| Kosten | Serverless-Jobs-SKU | kostenlos |
| Abschaltbar | ja (`DISABLE` auf jeder Ebene) | nicht komplett, nur einzelne Features pro Tabelle (`DROP FEATURE`) |

Berührungspunkt: `CLUSTER BY AUTO` wird **neuen** Tabellen über Automatic Upgrades zugewiesen (nie bestehenden); die Key-Auswahl und das Clustering übernimmt danach PO.

---

## 5. Lakeflow Spark Declarative Pipelines

Pipelines haben eine eigene Tabelleneigenschaft für automatische Wartung:

- `pipelines.autoOptimize.managed` (Default `true`) — „Enables or disables automatically scheduled optimization of this table."
- Wichtig: „**For pipelines managed by predictive optimization, this property is not used.**"

→ Wird die Pipeline von PO verwaltet, ist diese Eigenschaft wirkungslos und PO übernimmt die Optimierung. Für `pipelines.autoOptimize.zOrderCols` empfiehlt Databricks stattdessen Liquid Clustering bzw. `CLUSTER BY AUTO` (`cluster_by_auto=True` in Python); `CLUSTER BY AUTO` wird für Streaming Tables und Materialized Views unterstützt.

---

## 6. Change Data Feed und Time Travel

PO-`VACUUM` löscht nach Ablauf der Retention auch
- alte Datendateien → **Time Travel** auf diese Versionen ist danach nicht mehr möglich,
- alte CDF-Dateien (`_change_data`) → der **Change Feed** lässt sich nicht beliebig weit zurücklesen.

Wer länger zurückgreifen muss, erhöht `delta.deletedFileRetentionDuration` (und ggf. `delta.logRetentionDuration`). → [../../CDF/01 Grundlagen/03 Tabelleneigenschaften, Protokoll und Speicher.md](../../CDF/01%20Grundlagen/03%20Tabelleneigenschaften%2C%20Protokoll%20und%20Speicher.md)

## Quellen

- [Use liquid clustering for tables](https://docs.databricks.com/aws/en/delta/clustering)
- [Data skipping](https://docs.databricks.com/aws/en/delta/data-skipping)
- [Table properties reference](https://docs.databricks.com/aws/en/tables/table-properties)
- [Automatic upgrades](https://docs.databricks.com/aws/en/tables/automatic-upgrades)
- [Pipeline properties reference](https://docs.databricks.com/aws/en/ldp/properties)
- [Remove unused data files with vacuum](https://docs.databricks.com/aws/en/tables/operations/vacuum)
