# Joins in Databricks

Databricks unterstützt ANSI-Standard-Join-Syntax und unterscheidet zwischen verschiedenen Join-Arten je nach Verarbeitungsmodus.

## Batch-Joins

Alle Batch-Joins sind zustandslos und liefern das Ergebnis sofort. Databricks unterstützt Standard-SQL-Join-Syntax, einschließlich Inner-, Outer-, Semi-, Anti- und Cross-Joins.

## Stream-Stream-Joins

Diese Joins sind zustandsbehaftet: Databricks verfolgt Informationen über die Datenquellen und Ergebnisse und aktualisiert die Ergebnisse iterativ. Unterstützt werden Inner Joins, Left/Right/Full Outer Joins und Left-Semi-Joins. Für beide Seiten aller Stream-Stream-Joins sollten Watermarks angegeben werden.

## Stream-Static-Joins

Diese zustandslosen Joins verbinden die jeweils aktuellste gültige Version einer Delta-Tabelle (die statischen Daten) mit einem Datenstrom. Wichtige Einschränkung: Wird die statische Tabelle zwischen zwei Ausführungen aktualisiert, kann die erneute Verarbeitung derselben Streaming-Daten zu unterschiedlichen Ergebnissen führen.

Beispiel: Ein Python-Beispiel verbindet eine streamende `bookings`-Tabelle mit einer statischen `users`-Tabelle über den Trigger `availableNow`:

```python
checkpoint_path = f"/Volumes/{catalog}/{schema}/checkpoints/bookings_with_user_info"
streamingDF = spark.readStream.table("samples.wanderbricks.bookings")
staticDF = spark.read.table("samples.wanderbricks.users")
query = (streamingDF.join(staticDF, "user_id", "inner")
  .writeStream.option("checkpointLocation", checkpoint_path)
  .trigger(availableNow=True).table(f"{catalog}.{schema}.bookings_with_user_info"))
```

## Join-Optimierung

Databricks optimiert Skew-Joins automatisch. Range-Join-Hints können die Performance bei Ungleichheits-Joins verbessern, etwa bei Timestamps oder Clustering-IDs.

---
**Quelle:** https://docs.databricks.com/aws/en/transform/join  
**Stand:** 2026-08-09

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

Die formale `JOIN`-Syntaxreferenz zeigt für dieselbe `ON`-Bedingung alle Join-Varianten aus Abschnitt "Batch-Joins" nebeneinander — insbesondere die in diesem Dokument nur textuell erwähnten Semi- und Anti-Joins, die in Databricks SQL über eigene Schlüsselwörter angesprochen werden statt über `EXISTS`/`NOT EXISTS`-Subqueries:

```sql
-- Inner Join: nur Zeilen mit Treffer auf beiden Seiten
SELECT id, name, employee.deptno, deptname
FROM employee
INNER JOIN department ON employee.deptno = department.deptno;

-- Semi Join: nur Spalten aus employee, aber nur Zeilen mit Treffer in department
SELECT *
FROM employee
SEMI JOIN department ON employee.deptno = department.deptno;

-- Anti Join: nur Zeilen aus employee OHNE Treffer in department
SELECT *
FROM employee
ANTI JOIN department ON employee.deptno = department.deptno;
```

Cross Join ohne `ON`-Bedingung erzeugt das kartesische Produkt beider Tabellen:

```sql
SELECT id, name, employee.deptno, deptname
FROM employee
CROSS JOIN department;
```

**Quelle:** https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-join
