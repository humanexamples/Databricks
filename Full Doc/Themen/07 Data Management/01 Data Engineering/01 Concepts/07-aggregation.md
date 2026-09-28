# Aggregation in Databricks

Diese Seite erklärt die Semantik von Aggregationen in Databricks anhand von vier grundlegenden Ansätzen zur Berechnung aggregierter Statistiken.

## Batch-Aggregate

Standardverhalten für Ad-hoc-SQL-Abfragen und Spark-DataFrame-Verarbeitung. Latenz und Rechenkosten von Batch-Aggregationen können mit wachsender Datenmenge steigen. Für häufig genutzte Aggregatwerte empfiehlt Databricks materialisierte Views.

## Zustandsbehaftete Aggregate (Stateful Aggregates)

Werden in Streaming-Workloads eingesetzt, um Datensätze über die Zeit zu verfolgen. Wichtige Anforderung: Für zustandsbehaftete Aggregationen müssen Watermarks verwendet werden. Ohne Watermarks wächst der Zustand unbegrenzt, was zu Performance-Problemen und möglichen Speicherfehlern führt.

## Inkrementelle Aggregate

Materialisierte Views ermöglichen inkrementelle Berechnung. Sie überwachen automatisch Änderungen an der Quelle und wenden beim Refresh nur die notwendigen Updates an – das Ergebnis entspricht einer vollständigen Batch-Neuberechnung.

## Näherungsweise Aggregate (Approximate Aggregates)

Wenn keine exakte Genauigkeit erforderlich ist, bietet Spark SQL drei native Funktionen:

- `approx_count_distinct`
- `approx_percentile`
- `approx_top_k`

Zusätzlich erzeugt die Klausel `TABLESAMPLE` zufällige Stichproben eines Datensatzes für näherungsweise Berechnungen.

## Datenqualitätsüberwachung

Data Profiling nutzt aggregierte Statistiken, um Qualitätskennzahlen über die Zeit zu verfolgen – als Grundlage für Trendvisualisierung und Anomalie-Alarme.

---
**Quelle:** https://docs.databricks.com/aws/en/transform/aggregation  
**Stand:** 2026-08-07

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### `GROUP BY` — Mehrfach-Gruppierung mit `GROUPING SETS`, `ROLLUP`, `CUBE`

Über die einfache Gruppierung hinaus erlaubt `GROUP BY GROUPING SETS`, mehrere Gruppierungs-Kombinationen in einer einzigen Abfrage zu berechnen — äquivalent zur `UNION` mehrerer separat gruppierter Abfragen, aber in einem Durchlauf:

```sql
SELECT city, car_model, sum(quantity) AS sum
FROM dealer
GROUP BY GROUPING SETS ((city, car_model), (city), (car_model), ())
ORDER BY city;
```

`ROLLUP` und `CUBE` sind Kurzformen für gängige `GROUPING SETS`-Muster: `ROLLUP` liefert hierarchische Zwischensummen (z. B. je Stadt und Gesamtsumme), `CUBE` alle möglichen Kombinationen der Gruppierungsspalten:

```sql
SELECT city, car_model, sum(quantity) AS sum
FROM dealer
GROUP BY city, car_model WITH ROLLUP
ORDER BY city, car_model;
```

Zusätzlich unterstützt Databricks SQL `GROUP BY ALL` als Kurzschreibweise, die automatisch nach allen nicht-aggregierten Spalten der `SELECT`-Liste gruppiert:

```sql
SELECT car_model, count(DISTINCT city) AS count
FROM dealer GROUP BY ALL;
```

### `HAVING` — Filtern nach Aggregatwerten

`HAVING` filtert im Gegensatz zu `WHERE` nach dem Gruppieren und kann sich sowohl auf eine Aggregatfunktion beziehen, die gar nicht in der `SELECT`-Liste steht, als auch auf den Alias eines berechneten Aggregats:

```sql
-- Filtert nach einer Aggregatfunktion, die im SELECT gar nicht auftaucht
SELECT city, sum(quantity) AS sum FROM dealer GROUP BY city
HAVING max(quantity) > 15;

-- Filtert über den Alias des Aggregats aus der SELECT-Liste
SELECT city, sum(quantity) AS sum FROM dealer GROUP BY city
HAVING sum > 15;
```

`HAVING` funktioniert laut Doku auch ganz ohne `GROUP BY` — dann bezieht es sich auf ein einziges globales Aggregat über die gesamte Tabelle:

```sql
SELECT sum(quantity) AS sum FROM dealer HAVING sum(quantity) > 10;
```

**Quellen:**
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-groupby
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-select-having
