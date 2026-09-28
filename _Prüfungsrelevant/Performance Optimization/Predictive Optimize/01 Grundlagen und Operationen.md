# Predictive Optimization — Grundlagen und Operationen

## 1. Was ist Predictive Optimization?

Ohne Predictive Optimization (PO) muss ein Data Engineer selbst entscheiden,
- **welche** Tabellen gewartet werden,
- **wann** und **wie oft** `OPTIMIZE`, `VACUUM` und `ANALYZE` laufen,
- auf **welchem Cluster** das passiert,

und dafür Jobs anlegen und überwachen. PO übernimmt genau das:

> „Predictive optimization automatically runs `OPTIMIZE`, `VACUUM`, and `ANALYZE` on Unity Catalog managed tables (Delta Lake and Iceberg) on Databricks, eliminating manual maintenance and time spent tracking performance issues."
>
> „Databricks recommends predictive optimization for all Unity Catalog managed tables."

Databricks
1. **identifiziert** Tabellen, die von Wartung profitieren würden (anhand von Nutzung, Schreibmustern und Dateilayout),
2. **reiht** die passenden Operationen **ein** und
3. **führt** sie auf Serverless Compute **aus**.

Zusätzlich sammelt PO **Statistiken schon beim Schreiben** in Managed Tables (Stats-on-Write).

Es gibt **keinen festen Zeitplan** — die Dokumentation beschreibt eine bedarfsgesteuerte Ausführung („identifies tables that would benefit from maintenance operations"). Deshalb gilt: **Einrichten und vergessen.**

---

## 2. Die drei Operationen

| Operation | Zweck | Wichtige Details |
|---|---|---|
| **`OPTIMIZE`** | Verbessert die Query-Performance durch optimale Dateigrößen (Compaction) | Löst **inkrementelles Liquid Clustering** für geclusterte Tabellen aus. **Führt kein `ZORDER` aus** — Z-geordnete Dateien werden ignoriert |
| **`VACUUM`** | Senkt Speicherkosten durch Löschen von Datendateien, die die Tabelle nicht mehr referenziert | Retention über `delta.deletedFileRetentionDuration` (Standard 7 Tage). Bei aktiviertem Iceberg-Read werden auch nicht mehr erreichbare Iceberg-Metadaten entfernt |
| **`ANALYZE`** | Scannt die Tabelle und sammelt Statistiken für den Optimizer | Läuft im Hintergrund, wenn Statistiken veralten. Wählt die Spalten für Data Skipping nach Query-Filtern aus |

> **Falle:** „PO führt Z-Ordering aus" ist **falsch**. PO unterstützt Liquid Clustering, nicht `ZORDER BY`.

### VACUUM und Retention

```sql
-- Retention auf 30 Tage erhöhen (z. B. für längeres Time Travel)
ALTER TABLE catalog.schema.orders
SET TBLPROPERTIES ('delta.deletedFileRetentionDuration' = '30 days');
```

- Standard: **7 Tage** (`interval 1 week`).
- Setzt man den Wert **unter 7 Tage**, hält PO bei `VACUUM FULL` trotzdem **mindestens 7 Tage** ein — Schutz vor dem Löschen noch nicht committeter Dateien lang laufender Jobs.
- `delta.logRetentionDuration` (Standard **30 Tage**) steuert, wie lange die Tabellenhistorie (Transaktionslog) aufbewahrt wird.
- Nach `VACUUM` ist **Time Travel** auf Versionen, deren Dateien gelöscht wurden, **nicht mehr möglich**.

Zum Vergleich die manuellen Varianten (die PO ersetzt):

```sql
VACUUM catalog.schema.orders;            -- FULL (Standard): listet das Verzeichnis
VACUUM catalog.schema.orders LITE;       -- Public Preview ab DBR 16.4 LTS: nutzt das Transaktionslog statt Directory-Listing;
                                         -- setzt ein erfolgreiches VACUUM innerhalb der Log-Retention (30 Tage) voraus
VACUUM catalog.schema.orders DRY RUN;    -- nur anzeigen, was gelöscht würde
REORG TABLE catalog.schema.orders APPLY (PURGE);  -- Soft-Deletes (Deletion Vectors) physisch umschreiben, danach VACUUM
```

---

## 3. Voraussetzungen

| Voraussetzung | Wert |
|---|---|
| Plan | **Premium** oder höher |
| Region | Unterstützte Region (Serverless Compute muss verfügbar sein) |
| Compute für Lese-/Schreibzugriffe | SQL Warehouses oder **Databricks Runtime 12.2 LTS+** |
| Tabellentyp | **Nur Unity-Catalog-Managed-Tables** (Delta Lake, Apache Iceberg) |

## 4. Wo PO **nicht** läuft

- **External Tables** (Daten an einem selbst verwalteten Speicherort)
- Tabellen, die als **OpenSharing-(Delta-Sharing-)Empfänger** geladen werden
- Hive-Metastore-Tabellen (kein Unity Catalog)

→ Für diese Tabellen bleibt der klassische Weg: `OPTIMIZE`/`VACUUM` in einem geplanten Lakeflow Job.

---

## 5. Kosten und Abrechnung

- Die Operationen laufen auf **Serverless Compute für Jobs**.
- Abgerechnet wird über die **Serverless-Jobs-SKU** (eigene, separat sichtbare Kosten).
- Kosten pro Operation und Tabelle stehen als **geschätzte DBUs** (`usage_unit = 'ESTIMATED_DBU'`) in der Systemtabelle → [03 Monitoring und Systemtabelle](03%20Monitoring%20und%20Systemtabelle.md).
- Laufen mehrere Operationen auf demselben Cluster, wird der DBU-Anteil pro Operation **geschätzt**.

**Warum lohnt sich das trotzdem?** Man spart eigene Wartungs-Cluster, und PO führt nur Operationen aus, deren Nutzen die Kosten übersteigt (bei Clustering explizit: „only when the predicted cost savings … outweigh the data clustering cost").

---

## 6. Standardzustand

- **Standardmäßig aktiviert** für Accounts, die ab dem **11. November 2024** erstellt wurden.
- Bestehende Accounts wurden **schrittweise bis August 2026** aktiviert.
- Ob PO für ein Objekt aktiv ist, zeigt `DESCRIBE … EXTENDED` → [02 Aktivierung](02%20Aktivierung%2C%20Vererbung%20und%20Berechtigungen.md#status).

---

## 7. Best Practice

> „When using predictive optimization, Databricks recommends disabling any scheduled OPTIMIZE jobs."

1. UC-Managed-Tables verwenden (Standardtabellentyp).
2. PO auf Account- oder Catalog-Ebene aktiviert lassen.
3. Vorhandene `OPTIMIZE`/`VACUUM`-Jobs **abschalten** — sonst doppelte Arbeit und doppelte Kosten.
4. Retention bewusst setzen (`delta.deletedFileRetentionDuration`), wenn längeres Time Travel oder längeres CDF-Lesen gebraucht wird.
5. Kosten und Wirkung über die Systemtabelle beobachten.

## Quellen

- [Predictive optimization for Unity Catalog managed tables](https://docs.databricks.com/aws/en/optimizations/predictive-optimization)
- [Remove unused data files with vacuum](https://docs.databricks.com/aws/en/tables/operations/vacuum)
- [Table properties reference](https://docs.databricks.com/aws/en/tables/table-properties)
- [Use liquid clustering for tables](https://docs.databricks.com/aws/en/delta/clustering)
