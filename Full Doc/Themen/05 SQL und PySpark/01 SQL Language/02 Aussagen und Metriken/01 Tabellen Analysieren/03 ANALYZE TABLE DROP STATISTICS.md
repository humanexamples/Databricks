# `ANALYZE TABLE ... DROP STATISTICS`

Entfernt Optimizer-Statistiken von einer Unity-Catalog-Tabelle, damit der Query-Optimizer veraltete oder ungenaue Statistiken nicht mehr berücksichtigt.

Zum Erzeugen der Statistiken siehe [ANALYZE TABLE COMPUTE STATISTICS.md](01%20ANALYZE%20TABLE%20COMPUTE%20STATISTICS.md); zum Hintergrund der automatischen Statistik-Erfassung siehe [Predictive Optimization für Statistiken](../../../09%20Performance%20Optimization/01%20Foundation%20Design/04%20Data%20Skipping%20und%20Tabellenstatistiken.md#predictive-stats).

## Syntax

```sql
ANALYZE TABLE table_name DROP [ MANUAL | AUTO | ALL ] STATISTICS
```

## Parameter

| Parameter/Qualifier | Bedeutung |
|---|---|
| `table_name` | muss eine existierende **Unity-Catalog**-Tabelle referenzieren, ohne zeitliche oder Options-Spezifikation; löst `TABLE_OR_VIEW_NOT_FOUND` aus, falls nicht vorhanden |
| ohne Qualifier / `MANUAL` | (Standard) entfernt nur Statistiken, die über `ANALYZE TABLE ... COMPUTE STATISTICS` manuell erzeugt wurden |
| `AUTO` | entfernt Auto-Stats sowie über Predictive Optimization gesammelte Statistiken |
| `ALL` | entfernt sowohl manuelle als auch automatische Statistiken |

## Voraussetzungen

- Die Tabelle muss sich in **Unity Catalog** befinden — bei Hive-Metastore-Tabellen wird eine `AnalysisException` ausgelöst.
- Der Nutzer benötigt das **`MODIFY`**-Privileg auf der Zieltabelle.

## Beispiele

```sql
-- Nur manuelle Statistiken entfernen (Standardverhalten)
ANALYZE TABLE main.sales.orders DROP STATISTICS;

-- Auto-Stats und Predictive-Optimization-Statistiken entfernen
ANALYZE TABLE main.sales.orders DROP AUTO STATISTICS;

-- Alle Statistik-Typen entfernen
ANALYZE TABLE main.sales.orders DROP ALL STATISTICS;
```

**Quellen:**
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-analyze-drop-statistics
- https://docs.databricks.com/aws/en/optimizations/predictive-optimization
