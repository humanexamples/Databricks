**Data Skipping** ist eine Optimierung, bei der Spark das Lesen von Dateien (oder Teilen von Dateien) vermeidet, die unmöglich für die Query relevante Daten enthalten können — basierend auf Statistiken, die über jede Datei gesammelt wurden, ohne die Datei jemals selbst zu öffnen.

**Funktionsweise:**

1. Beim Schreiben von Daten (insbesondere in Delta Lake) sammelt Spark Statistiken pro Datei — typischerweise **Min-/Max-Werte**, Null-Counts und Zeilenanzahlen für jede Spalte (standardmäßig üblicherweise für die ersten 32 Spalten).
2. Diese Statistiken liegen im **Transaction Log/Metadaten, nicht in den Dateien selbst**.
3. Wenn Sie eine Query mit einem Filter ausführen (z. B. `WHERE date = '2026-07-01'`), prüft Spark zunächst die Statistiken: Wenn sich der Min-/Max-Bereich einer Datei für `date` nicht mit `'2026-07-01'` überschneidet, wird diese Datei **vollständig übersprungen** — sie wird nie von der Festplatte gelesen.

```sql
# Einfache, bekannte I/O-Pruning-Technik
# . Dateiweise Statistiken wie Min & Max erfassen
# . Sie nutzen, um das Scannen irrelevanter Dateien zu vermeiden
SELECT 
	input_file_name() as "file_name",
	min(col) AS "col_min",
	max(col) AS "col_max"
FROM table
GROUP BY input_file_name()
```

**Warum das wichtig ist:**

- Weniger I/O = schnellere Queries, insbesondere bei großen Tabellen mit vielen Dateien.
- Es funktioniert am besten, wenn die Daten auf natürliche Weise **nach den Spalten geclustert sind, nach denen gefiltert wird** — z. B. Dateien, bei denen jede Datei nur einen Datumsbereich abdeckt, sodass die Min-/Max-Statistiken tatsächlich selektiv sind.
