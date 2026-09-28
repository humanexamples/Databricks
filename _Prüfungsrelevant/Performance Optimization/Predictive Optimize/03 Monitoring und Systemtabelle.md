# Predictive Optimization — Monitoring und Systemtabelle

Es gibt drei Wege, um zu sehen, was PO tut:

| Weg | Frage, die er beantwortet |
|---|---|
| `system.storage.predictive_optimization_operations_history` | **Was** wurde ausgeführt, mit welcher Wirkung, zu welchen Kosten? (account-weit) |
| `DESCRIBE TABLE EXTENDED … AS JSON` | **Warum** wurde eine Operation übersprungen? (pro Tabelle) |
| Catalog Explorer → **History**-Tab | Dasselbe in der UI: „Auto" (ausgeführt) oder „Not applied" (übersprungen) |

---

## 1. Systemtabelle `system.storage.predictive_optimization_operations_history`

- Die Systemtabelle ist in **Public Preview**.
- Wird **innerhalb von 2 Stunden** aktualisiert. **Abrechnungsdaten** können **bis zu 24 Stunden** brauchen.
- Laufen mehrere Operationen auf demselben Cluster, wird der DBU-Anteil pro Operation **geschätzt**.
- Nur in Regionen verfügbar, in denen PO verfügbar ist.

### Spalten

| Spalte | Typ | Beschreibung |
|---|---|---|
| `account_id` | string | Account-ID |
| `workspace_id` | string | Workspace, in dem die Operation lief |
| `start_time` | timestamp | Beginn (UTC) |
| `end_time` | timestamp | Ende (UTC) |
| `metastore_name` | string | Metastore |
| `metastore_id` | string | Metastore-ID |
| `catalog_name` | string | Katalog |
| `schema_name` | string | Schema |
| `table_id` | string | Tabellen-ID |
| `table_name` | string | Tabellenname |
| `operation_type` | string | Art der Operation (siehe unten) |
| `operation_id` | string | ID der Operation |
| `operation_status` | string | Ergebnis (siehe unten) |
| `operation_metrics` | map<string,string> | Details zur Operation (je Typ unterschiedlich) |
| `usage_unit` | string | Immer `ESTIMATED_DBU` |
| `usage_quantity` | decimal | Geschätzte verbrauchte DBUs |

### `operation_type`-Werte

| Wert | Bedeutung | Wichtige `operation_metrics` |
|---|---|---|
| `COMPACTION` | Kleine Dateien zusammenfassen (Teil von `OPTIMIZE`) | `number_of_compacted_files`, `amount_of_data_compacted_bytes`, `number_of_output_files`, `amount_of_output_data_bytes` |
| `CLUSTERING` | Inkrementelles Liquid Clustering (Teil von `OPTIMIZE`) | `number_of_removed_files`, `number_of_clustered_files`, `amount_of_data_removed_bytes`, `amount_of_clustered_data_bytes` |
| `VACUUM` | Nicht referenzierte Dateien löschen | `number_of_deleted_files`, `amount_of_data_deleted_bytes` |
| `ANALYZE` | Statistiken aktualisieren | `amount_of_scanned_bytes`, `number_of_scanned_files`, `staleness_percentage_reduced` |
| `AUTO_CLUSTERING_COLUMN_SELECTION` | Keys für `CLUSTER BY AUTO` wählen/ändern | `old_clustering_columns`, `new_clustering_columns`, `has_column_selection_changed`, `additional_reason` |
| `DATA_SKIPPING_COLUMN_SELECTION` | Spalten für Data-Skipping-Statistiken wählen | `added_…`/`removed_…`/`old_…`/`new_data_skipping_columns`, gescannte Bytes/Dateien |
| `COMPATIBILITY_MODE_REFRESH` | Erkennt, ob der Compatibility Mode (Lesezugriff externer Engines) veraltet ist, und aktualisiert ihn | — |
| `DELETE` | Auto-TTL: abgelaufene Zeilen löschen | `number_of_deleted_rows`, `amount_of_data_deleted_bytes` |
| `PURGE` | Auto-TTL: Soft-Deletes physisch umschreiben | `number_of_purged_rows` |

### `operation_status`-Werte

- `SUCCESSFUL`
- `FAILED: INTERNAL_ERROR`
- `FAILED: AUTO_TTL_COLUMN_DOES_NOT_EXIST_ERROR`
- `FAILED: PRIVATE_LINK_SETUP_ERROR`

---

## 2. Beispielabfragen (aus der Dokumentation)

**Geschätzte DBUs der letzten 30 Tage:**

```sql
SELECT SUM(usage_quantity)
FROM system.storage.predictive_optimization_operations_history
WHERE usage_unit = "ESTIMATED_DBU"
  AND timestampdiff(day, start_time, Now()) < 30;
```

**Für welche Tabellen hat PO in den letzten 30 Tagen am meisten ausgegeben?**

```sql
SELECT metastore_name, catalog_name, schema_name, table_name,
       SUM(usage_quantity) AS totalDbus
FROM system.storage.predictive_optimization_operations_history
WHERE usage_unit = "ESTIMATED_DBU"
  AND timestampdiff(day, start_time, Now()) < 30
GROUP BY ALL
ORDER BY totalDbus DESC;
```

**Auf welchen Tabellen führt PO die meisten Operationen aus?**

```sql
SELECT metastore_name, catalog_name, schema_name, table_name, operation_type,
       COUNT(DISTINCT operation_id) AS operations
FROM system.storage.predictive_optimization_operations_history
GROUP BY ALL
ORDER BY operations DESC;
```

**Wie viele Bytes wurden in einem Katalog kompaktiert?**

```sql
SELECT schema_name, table_name,
       SUM(operation_metrics["amount_of_data_compacted_bytes"]) AS bytesCompacted
FROM system.storage.predictive_optimization_operations_history
WHERE metastore_name = :metastore_name
  AND catalog_name = :catalog_name
  AND operation_type = "COMPACTION"
GROUP BY ALL
ORDER BY bytesCompacted DESC;
```

**Welche Tabellen hatten die meisten per VACUUM gelöschten Bytes?**

```sql
SELECT metastore_name, catalog_name, schema_name, table_name,
       SUM(operation_metrics["amount_of_data_deleted_bytes"]) AS bytesVacuumed
FROM system.storage.predictive_optimization_operations_history
WHERE operation_type = "VACUUM"
GROUP BY ALL
ORDER BY bytesVacuumed DESC;
```

**Erfolgsquote aller PO-Operationen:**

```sql
WITH operation_counts AS (
  SELECT COUNT(DISTINCT (CASE WHEN operation_status = "SUCCESSFUL" THEN operation_id END)) AS successes,
         COUNT(DISTINCT operation_id) AS total_operations
  FROM system.storage.predictive_optimization_operations_history
)
SELECT successes / total_operations AS success_rate
FROM operation_counts;
```

---

## 3. Skip-Reasons: Warum wurde nichts gemacht?

Ab **Databricks Runtime 18 LTS**:

```sql
DESCRIBE TABLE EXTENDED catalog.schema.table AS JSON;
```

Das Feld **`predictive_optimization_evaluations`** enthält die letzte Bewertung pro Operationstyp:

- `COMPACTION`
- `CLUSTERING`
- `AUTO_CLUSTERING_COLUMN_SELECTION`
- `VACUUM`

Die Ergebnisse können **bis zu 24 Stunden** brauchen. Gezeigt wird **nur die letzte Bewertung** je Operationstyp, ohne Historie. Für **`ANALYZE`** werden **keine** Skip-Gründe angezeigt.

Dokumentierte Gründe, warum `CLUSTER BY AUTO` keine Keys wählt: Tabelle zu klein; bereits wirksames Clustering (manuelle Keys oder passende Einfügereihenfolge); keine häufigen Queries; DBR unter 15.4 LTS.

**In der UI:** Catalog Explorer → Tabelle → **History** → Dropdown **Automatic runs** → Zeilen mit **„Auto"** (ausgeführt) oder **„Not applied"** (übersprungen, anklickbar mit Begründung). „Auto" umfasst auch andere automatische Operationen, z. B. Streaming-Auto-Compaction.

| `DESCRIBE TABLE EXTENDED` | Operation im Catalog Explorer |
|---|---|
| `COMPACTION` | `OPTIMIZE` |
| `CLUSTERING` | `OPTIMIZE` |
| `AUTO_CLUSTERING_COLUMN_SELECTION` | `AUTO LIQUID` |
| `VACUUM` | `VACUUM` |

---

## 4. Ergänzend: Tabellenhistorie

`VACUUM` schreibt Audit-Informationen ins Transaktionslog (bei UC-Managed-Tables standardmäßig aktiv), sichtbar über:

```sql
DESCRIBE HISTORY catalog.schema.table;
```

> ⚠️ Ungeklärt: Die abgerufene Dokumentation beschreibt nicht, mit welchem Benutzer bzw. Principal PO-Operationen in `DESCRIBE HISTORY` erscheinen.

## Quellen

- [Predictive optimization system table reference](https://docs.databricks.com/aws/en/admin/system-tables/predictive-optimization)
- [Predictive optimization for Unity Catalog managed tables](https://docs.databricks.com/aws/en/optimizations/predictive-optimization)
- [System tables overview](https://docs.databricks.com/aws/en/admin/system-tables/)
