# Data Skipping

Data Skipping überspringt beim Abfragen Dateien, die für das Ergebnis nicht relevant sind. Das beschleunigt Abfragen deutlich.

> Statistiken für das Data Skipping werden automatisch erfasst, wenn Sie Daten in eine Delta-Lake-Tabelle oder eine Managed-Apache-Iceberg-Tabelle schreiben.

Databricks nutzt dafür Statistiken pro Datei: Minimalwert, Maximalwert, Anzahl der Nullwerte und Gesamtzahl der Datensätze. Anhand dieser Werte kann Databricks bei einer Abfrage irrelevante Dateien überspringen und so die Performance verbessern.

Statistiken müssen für die Spalten erfasst werden, die in `ZORDER`-Anweisungen verwendet werden.

## Statistik-Spalten festlegen

Bei Unity-Catalog-External-Tables werden standardmäßig Statistiken für die ersten 32 Spalten erfasst. Managed Tables nutzen Predictive Optimization, um Statistik-Spalten intelligent auszuwählen, ohne diese 32-Spalten-Grenze.

Zwei Tabelleneigenschaften steuern das Verhalten bei der Statistikerfassung:

| Eigenschaft | Runtime-Unterstützung | Funktion |
| --- | --- | --- |
| `dataSkippingNumIndexedCols` | Alle Versionen | Anzahl der Spalten für die Statistikerfassung anpassen |
| `dataSkippingStatsColumns` | Ab 13.3 LTS | Konkrete Spalten für die Statistikerfassung benennen; ersetzt die ältere Eigenschaft |

## Konfigurationsbeispiele

Für Delta Lake:

```sql
%sql
ALTER TABLE table_name SET TBLPROPERTIES('delta.dataSkippingStatsColumns' = 'col1, col2, col3')
```

Für Iceberg-Tabellen:

```sql
%sql
ALTER TABLE table_name SET TBLPROPERTIES('iceberg.dataSkippingStatsColumns' = 'col1, col2, col3')
```

Statistiken ab Databricks Runtime 14.3 LTS manuell neu berechnen:

```sql
%sql
ANALYZE TABLE table_name COMPUTE DELTA STATISTICS
```

## Was ist Z-Ordering?

> Z-Ordering ist eine Technik, um verwandte Informationen in derselben Menge von Dateien zusammenzulegen.

Sie setzen Z-Ordering um, indem Sie Spalten in der `ZORDER BY`-Klausel angeben:

```sql
%sql
OPTIMIZE events
WHERE date >= current_timestamp() - INTERVAL 1 day
ZORDER BY (eventType)
```

Z-Ordering wirkt am besten bei Spalten mit hoher Kardinalität, die häufig in Abfragefiltern vorkommen. Sie können mehrere Spalten angeben, kommagetrennt. Mit jeder zusätzlichen Spalte sinkt jedoch die Wirksamkeit.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/data-skipping  
**Stand:** 2026-08-06
