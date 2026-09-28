# Datei-Layout optimieren mit OPTIMIZE

Der Befehl `OPTIMIZE` ordnet Datendateien in Delta-Lake- und Apache-Iceberg-Tabellen neu an. Das verbessert die Datenorganisation und die Abfrageperformance.

## Was macht OPTIMIZE?

Bei Tabellen mit Liquid Clustering gruppiert `OPTIMIZE` die Daten nach den Clustering-Keys. Bei partitionierten Tabellen komprimiert `OPTIMIZE` die Dateien innerhalb jeder Partition und verbessert deren Layout.

## Predictive Optimization

Databricks empfiehlt, Predictive Optimization für Unity-Catalog-Managed-Tables zu aktivieren. Das vereinfacht die Datenpflege und senkt die Speicherkosten.

## Clustering-Optionen

Delta-Lake-Tabellen können `ZORDER BY`-Klauseln für besseres Clustering nutzen. Apache-Iceberg-Tabellen verwenden andere Clustering- und Sortierstrategien. Databricks empfiehlt grundsätzlich Liquid Clustering anstelle von Partitionen, `ZORDER` oder anderen Layout-Ansätzen.

## OPTIMIZE FULL

Ab Databricks Runtime 16.0 unterstützt `OPTIMIZE FULL` das erzwungene erneute Clustering bei Tabellen mit Liquid Clustering.

## Syntax-Beispiele

Grundlegende SQL-Syntax:

```sql
%sql
OPTIMIZE table_name
```

Mit einem Partitions-Prädikat:

```sql
%sql
OPTIMIZE table_name WHERE date >= '2022-11-18'
```

Python-Beispiel:

```python
from delta.tables import *
deltaTable = DeltaTable.forName(spark, "table_name")
deltaTable.optimize().executeCompaction()
```

Python mit WHERE-Klausel:

```python
from delta.tables import *
deltaTable = DeltaTable.forName(spark, "table_name")
deltaTable.optimize().where("date='2021-11-18'").executeCompaction()
```

## Wichtige Eigenschaften

- Bin-Packing ist idempotent. Mehrfaches Ausführen bringt keinen zusätzlichen Effekt.
- Lesende Abfragen erleben Snapshot-Isolation. Sie werden während der Optimierung nicht unterbrochen.
- Die eigentlichen Daten werden inhaltlich nicht verändert.
- `OPTIMIZE` liefert Statistiken zu entfernten und hinzugefügten Dateien zurück.

## Empfehlungen

**Häufigkeit:** Starten Sie mit einer täglichen Ausführung, idealerweise außerhalb der Spitzenzeiten. Passen Sie die Häufigkeit dann nach Kosten-Nutzen-Verhältnis an.

**Instanztypen:** Nutzen Sie rechenoptimierte Instanztypen ("Compute optimized"), idealerweise mit angeschlossenen SSDs. Die Parquet-Verarbeitung ist CPU-intensiv.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/operations/optimize  
**Stand:** 2026-08-06
