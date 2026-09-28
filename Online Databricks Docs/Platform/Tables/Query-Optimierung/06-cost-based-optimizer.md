# Kostenbasierter Optimizer (CBO)

Spark SQL kann einen kostenbasierten Optimizer (Cost-Based Optimizer, CBO) nutzen, um Ausführungspläne zu verbessern. Das hilft besonders bei komplexen Abfragen mit mehreren Joins. Wie gut der Optimizer arbeitet, hängt von aktuellen Tabellen- und Spaltenstatistiken ab.

## Statistiken erfassen

Sowohl Spalten- als auch Tabellenstatistiken sind wichtig, um den größten Nutzen aus dem CBO zu ziehen. Mit dem Befehl `ANALYZE TABLE` erfassen Sie Statistiken manuell. Databricks empfiehlt, diesen Befehl nach dem Schreiben in Tabellen auszuführen, damit die Statistiken aktuell bleiben.

Predictive Optimization führt `ANALYZE` automatisch auf von Unity Catalog verwalteten Tabellen aus. Diese Funktion vereinfacht die Datenwartung und senkt die Speicherkosten. Verursachen Statistiken Probleme bei der Planung, können Sie sie auch wieder entfernen.

## Query-Pläne prüfen

### EXPLAIN verwenden

Der Befehl `EXPLAIN` zeigt, ob Statistiken in den Query-Plan eingeflossen sind. Fehlende Statistiken können zu einem suboptimalen Plan führen. Die Statistik `rowCount` ist besonders wichtig bei Abfragen mit mehreren Joins. Fehlt sie, deutet das auf fehlende Spaltenstatistiken hin.

Ab Databricks Runtime 16.0 zeigt die Ausgabe von `EXPLAIN` an, welche Tabellen fehlende, teilweise oder vollständige Statistiken haben. Sie schlägt außerdem folgenden Befehl vor:

```sql
%sql
ANALYZE TABLE <table-name> COMPUTE STATISTICS FOR ALL COLUMNS
```

### Analyse über die Spark-SQL-UI

Die Spark-SQL-UI zeigt ausgeführte Pläne und die Genauigkeit der Statistiken:

- `rows output: 2.451.005 est: N/A` bedeutet: keine Statistiken verfügbar.
- `rows output: 2.451.005 est: 1616404 (1X)` bedeutet: gute Schätzgenauigkeit.
- `rows output: 2.451.005 est: 2626656323` bedeutet: schlechte Schätzung, um den Faktor 1000 daneben.

## CBO deaktivieren

Der CBO ist standardmäßig aktiv. Sie deaktivieren ihn, indem Sie `spark.sql.cbo.enabled` auf `false` setzen.

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/cbo  
**Stand:** 2026-08-06
