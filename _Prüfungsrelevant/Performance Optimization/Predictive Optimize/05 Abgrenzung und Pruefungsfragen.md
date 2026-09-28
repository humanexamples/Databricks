# Predictive Optimization — Abgrenzung und Prüfungsfragen

## 1. Welcher Weg automatisiert was?

| Weg | `OPTIMIZE` | `VACUUM` | `ANALYZE` | Wann greift es? | Tabellen |
|---|---|---|---|---|---|
| **Predictive Optimization** | ✅ (Compaction + Liquid Clustering, kein Z-Order) | ✅ | ✅ | Im Hintergrund, bedarfsgesteuert | Nur UC-Managed |
| **Auto Optimize** (`optimizeWrite`, `autoCompact`) | teilweise: Compaction **beim/nach dem Schreiben** | ❌ | ❌ | Während des Writes | Alle Delta-Tabellen |
| **Geplanter Lakeflow Job** mit `OPTIMIZE`/`VACUUM` | ✅ | ✅ | ✅ (wenn eingeplant) | Fester Zeitplan, selbst gepflegt | Alle, auch External |
| **`pipelines.autoOptimize.managed`** | ✅ (Pipeline-Tabellen) | ⚠️ ungeklärt (Doku nennt nur „scheduled optimization") | — | Pipeline-intern | Nicht genutzt, wenn PO aktiv |
| **AQE** (Adaptive Query Execution) | ❌ | ❌ | ❌ | Zur **Laufzeit einer Query** | — |

### Auto Optimize kurz erklärt

```sql
ALTER TABLE t SET TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',   -- größere Dateien schon beim Schreiben
  'delta.autoOptimize.autoCompact'   = 'auto'     -- kleine Dateien nach dem Write zusammenfassen
);
```

Hilft gegen das **Small-File-Problem**, **ersetzt aber kein `VACUUM`** und pflegt keine Statistiken.

### AQE kurz erklärt

AQE passt den **Ausführungsplan einer laufenden Query** an echte Laufzeitstatistiken an:
- Skew-Partitionen aufteilen (Skew Join),
- Shuffle-Partitionen zusammenfassen (Coalesce),
- Join-Strategie wechseln (z. B. Sort-Merge → Broadcast unter ~30 MB).

AQE **ändert keine Dateien** auf dem Storage. Es ist seit Spark 3.x standardmäßig aktiv (`spark.sql.adaptive.enabled = true`).

---

## 2. Typische Fallen

| Aussage | Richtig? | Begründung |
|---|---|---|
| „PO führt `ZORDER` aus" | ❌ | PO macht Compaction und Liquid Clustering, **kein** Z-Order |
| „PO funktioniert auch für External Tables" | ❌ | Nur UC-Managed-Tables |
| „PO läuft auf meinem All-Purpose-Cluster" | ❌ | Serverless Compute für Jobs, eigene SKU |
| „Mit PO sollte ich meine `OPTIMIZE`-Jobs behalten" | ❌ | Databricks empfiehlt, geplante `OPTIMIZE`-Jobs abzuschalten |
| „Retention 1 Tag → PO löscht nach 1 Tag" | ❌ | PO hält bei `VACUUM FULL` mindestens **7 Tage** ein |
| „`DISABLE` auf Schema wird durch Account-`ENABLE` überschrieben" | ❌ | Explizite Einstellungen bleiben bestehen, zurücksetzen mit `INHERIT` |
| „`CLUSTER BY AUTO` geht ohne PO" | ❌ | Die Key-Auswahl läuft über PO |
| „Auto-TTL löscht ohne PO" | ❌ | Auto-TTL setzt PO voraus |
| „AQE automatisiert Tabellenwartung" | ❌ | AQE optimiert nur Query-Pläne zur Laufzeit |

---

## 3. Übungsfragen

**1. Ein Data Engineer führt täglich manuell `OPTIMIZE` und `VACUUM` auf UC-Managed-Tables aus und möchte das automatisieren, ohne selbst Jobs zu pflegen. Was ist die beste Lösung?**
- A) Adaptive Query Execution aktivieren
- B) `delta.autoOptimize.autoCompact` setzen
- C) Predictive Optimization aktivieren ✅
- D) Einen Lakeflow Job mit Cron-Trigger anlegen

*B automatisiert kein `VACUUM`. D automatisiert zwar, erfordert aber eigene Planung und Pflege. A hat nichts mit Wartung zu tun.*

**2. Predictive Optimization unterstützt `OPTIMIZE` und welchen weiteren Wartungsbefehl?**
- A) `DESCRIBE` · B) `ZORDER` · C) `REFRESH` · D) `VACUUM` ✅

**3. Für welche Tabellen läuft Predictive Optimization nicht?**
- A) UC-Managed-Delta-Tabellen · B) UC-Managed-Iceberg-Tabellen · C) External Tables ✅ · D) Streaming Tables in UC-Pipelines

**4. Mit welcher Systemtabelle lassen sich Kosten und Wirkung von PO auswerten?**
- A) `system.billing.usage` · B) `system.storage.predictive_optimization_operations_history` ✅ · C) `system.access.audit` · D) `system.compute.clusters`

*(Nur die PO-Systemtabelle zeigt geschätzte DBUs pro Operation und Tabelle samt `operation_metrics`.)*

**5. PO ist auf Account-Ebene aktiviert, auf dem Schema `dev` wurde früher `DISABLE` gesetzt. Was gilt für Tabellen in `dev`?**
- A) PO ist aktiv, weil der Account Vorrang hat
- B) PO ist aus, bis das Schema auf `ENABLE` oder `INHERIT` gesetzt wird ✅

**6. Welche Berechtigung braucht man, um PO für ein Schema zu aktivieren?**
- A) `MODIFY` · B) `USE SCHEMA` · C) Schema Owner oder `MANAGE` ✅ · D) `SELECT`

**7. Welche Voraussetzung gilt für `CLUSTER BY AUTO`?**
- A) External Table · B) Predictive Optimization aktiviert ✅ · C) Z-Order vorher ausführen · D) DBR 11.3

**8. Wie findet man heraus, warum PO eine Tabelle nicht kompaktiert hat?**
- A) `SHOW TBLPROPERTIES` · B) `DESCRIBE TABLE EXTENDED … AS JSON` → `predictive_optimization_evaluations` ✅ · C) `EXPLAIN` · D) Spark UI

## Quellen

- [Predictive optimization for Unity Catalog managed tables](https://docs.databricks.com/aws/en/optimizations/predictive-optimization)
- [Table properties reference](https://docs.databricks.com/aws/en/tables/table-properties)
- [Use liquid clustering for tables](https://docs.databricks.com/aws/en/delta/clustering)
- Kurs-Quiz: [_Quiz.md](../../../Kursmetrial_Databricks/7_Databricks%20Performance%20Optimization/_Quiz.md)
