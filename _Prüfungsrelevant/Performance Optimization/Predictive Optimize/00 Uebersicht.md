# Predictive Optimization — Übersicht

**Predictive Optimization** automatisiert die Tabellenwartung für **Unity-Catalog-Managed-Tables** (Delta Lake und Apache Iceberg). Databricks erkennt selbst, welche Tabellen von Wartung profitieren, und führt `OPTIMIZE`, `VACUUM` und `ANALYZE` im Hintergrund auf **Serverless Compute** aus — ohne Jobs, Zeitpläne oder Cluster, die man selbst pflegen muss.

> **Prüfungs-Merksatz:** „Tägliches manuelles `OPTIMIZE`/`VACUUM` automatisieren" → **Predictive Optimization**. Nicht AQE (Laufzeit-Optimierung einer Query), nicht Auto Optimize (nur Compaction beim Schreiben, kein `VACUUM`).

---

## Auf einen Blick

| Aspekt | Kurzantwort |
|---|---|
| Was wird automatisiert? | `OPTIMIZE` (Compaction + inkrementelles Liquid Clustering, **kein** Z-Order), `VACUUM`, `ANALYZE` |
| Für welche Tabellen? | Nur **UC-Managed-Tables** (Delta, Iceberg) — **nicht** External Tables, **nicht** Tabellen aus OpenSharing-Empfang |
| Wo läuft es? | Serverless Compute für Jobs, abgerechnet über die **Serverless-Jobs-SKU** |
| Voraussetzungen | Premium-Plan oder höher, unterstützte Region, SQL Warehouse oder DBR **12.2 LTS+** |
| Aktivierung | Account → Catalog → Schema → Tabelle, jeweils `ENABLE` / `DISABLE` / `INHERIT` |
| Standard | Aktiv für Accounts ab **11. November 2024**; bestehende Accounts schrittweise bis **August 2026** |
| Monitoring | `system.storage.predictive_optimization_operations_history`, `DESCRIBE … EXTENDED`, History-Tab im Catalog Explorer |
| Retention | `delta.deletedFileRetentionDuration` (Standard **7 Tage**, PO hält **mindestens 7 Tage** ein) |

---

## Die Dateien in diesem Ordner

| # | Datei | Inhalt |
|---|---|---|
| 1 | [Grundlagen und Operationen](01%20Grundlagen%20und%20Operationen.md) | Was PO tut, die drei Operationen, Voraussetzungen, Einschränkungen, Kosten |
| 2 | [Aktivierung, Vererbung und Berechtigungen](02%20Aktivierung%2C%20Vererbung%20und%20Berechtigungen.md) | `ALTER … PREDICTIVE OPTIMIZATION`, Vererbungsmodell, Privilegien, Status prüfen |
| 3 | [Monitoring und Systemtabelle](03%20Monitoring%20und%20Systemtabelle.md) | Systemtabelle mit allen Spalten und Operationstypen, Beispielabfragen, Skip-Reasons |
| 4 | [Zusammenspiel mit anderen Features](04%20Zusammenspiel%20mit%20anderen%20Features.md) | `CLUSTER BY AUTO`, Statistiken und Data Skipping, Auto-TTL, Automatic Upgrades, Lakeflow Pipelines |
| 5 | [Abgrenzung und Prüfungsfragen](05%20Abgrenzung%20und%20Pruefungsfragen.md) | PO vs. Auto Optimize vs. geplanter Job vs. AQE, typische Fallen, Übungsfragen |
| 6 | [VACUUM](06%20VACUUM.md) | Funktionsweise, FULL vs. LITE, Retention und Time Travel, Soft-Deletes/`REORG`, Frequenz, Compute |
| 7 | [OPTIMIZE](07%20OPTIMIZE.md) | Compaction, Liquid Clustering, Z-Order, `FULL`/`WHERE`, Dateigrößen, Auto Compaction/Optimized Writes, Frequenz |

---

## Entscheidungshilfe

| Situation | Empfehlung |
|---|---|
| UC-Managed-Table, Wartung soll „einfach laufen" | **Predictive Optimization** aktivieren, geplante `OPTIMIZE`/`VACUUM`-Jobs abschalten |
| External Table | PO greift nicht → `OPTIMIZE`/`VACUUM` als geplanten Lakeflow Job ausführen, ggf. Auto Optimize |
| Clustering-Keys unklar oder Query-Muster ändern sich | `CLUSTER BY AUTO` (setzt PO voraus) |
| Alte Zeilen nach N Tagen automatisch löschen | Auto-TTL (`DELETE ROWS … DAYS AFTER …`, setzt PO voraus) |
| Data Skew oder falsche Join-Strategie **zur Laufzeit** | AQE — hat mit Tabellenwartung nichts zu tun |

---

## Verwandte Themen im Repo

- Kurs: [PO 99 - Summary and Next Steps.md](../../../Kursmetrial_Databricks/7_Databricks%20Performance%20Optimization/PO%2099%20-%20Summary%20and%20Next%20Steps.md) · [2_2_5 Liquid Clustering.md](../../../Kursmetrial_Databricks/7_Databricks%20Performance%20Optimization/_MD/2_Designing%20the%20Foundation/2_2_5%20Liquid%20Clustering.md)
- Full Doc: [05 Liquid Clustering.md, Abschnitt 11](../../../Full%20Doc/Themen/09%20Performance%20Optimization/01%20Foundation%20Design/05%20Liquid%20Clustering.md) · [03 Managed Tables.md, Abschnitt 8](../../../Full%20Doc/Themen/01%20Platform/02%20Tables/03%20Managed%20Tables.md)
- CDF: [../../CDF/00 Uebersicht.md](../../CDF/00%20Uebersicht.md) — Hinweis: `VACUUM` entfernt auch alte CDF-Dateien (`_change_data`), d. h. die Retention begrenzt, wie weit man den Change Feed zurücklesen kann.

## Quellen

- [Predictive optimization for Unity Catalog managed tables](https://docs.databricks.com/aws/en/optimizations/predictive-optimization)
- [Predictive optimization system table reference](https://docs.databricks.com/aws/en/admin/system-tables/predictive-optimization)
- [Remove unused data files with vacuum](https://docs.databricks.com/aws/en/tables/operations/vacuum)
- [Use liquid clustering for tables](https://docs.databricks.com/aws/en/delta/clustering)
- [Data skipping](https://docs.databricks.com/aws/en/delta/data-skipping)
- [Automatic upgrades](https://docs.databricks.com/aws/en/tables/automatic-upgrades)
- [Table properties reference](https://docs.databricks.com/aws/en/tables/table-properties)
- [Pipeline properties reference](https://docs.databricks.com/aws/en/ldp/properties)
