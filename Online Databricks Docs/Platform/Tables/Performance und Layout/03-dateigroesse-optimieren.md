# Dateigröße kontrollieren und optimieren

Die richtige Dateigröße beeinflusst die Performance einer Tabelle stark. Dieser Artikel zeigt, wie Databricks Dateigrößen automatisch steuert und wie Sie das bei Bedarf manuell anpassen.

## Automatische Größensteuerung

Für Unity-Catalog-Managed-Tables wendet Databricks automatisches File Size Tuning an. Manuelle Tuning-Empfehlungen gelten für diese Tabellen nicht, da Databricks die Dateigröße selbst steuert.

Bei Tabellen über 1 TB empfiehlt Databricks, `OPTIMIZE` regelmäßig geplant auszuführen, um Dateien weiter zu konsolidieren.

## Auto Optimize

Auto Optimize besteht aus zwei Einstellungen: `autoOptimize.autoCompact` und `autoOptimize.optimizeWrite`.

## Auto Compaction

Auto Compaction fasst kleine Dateien innerhalb einer Tabellenpartition zusammen. Das läuft synchron, direkt nach erfolgreichen Schreiboperationen. Es werden nur bisher unkomprimierte Dateien komprimiert.

### Konfigurationseinstellungen

| Einstellung | Delta | Iceberg | Beschreibung |
| --- | --- | --- | --- |
| Auto Compaction aktivieren (Tabelleneigenschaft) | `autoOptimize.autoCompact` | `autoOptimize.autoCompact` | Aktiviert Auto Compaction auf Tabellenebene |
| Auto Compaction aktivieren (SparkSession) | `spark.databricks.delta.autoCompact.enabled` | `spark.databricks.iceberg.autoCompact.enabled` | Aktiviert Auto Compaction auf Session-Ebene |
| Maximale Ausgabedateigröße | `spark.databricks.delta.autoCompact.maxFileSize` | `spark.databricks.iceberg.autoCompact.maxFileSize` | Steuert die angestrebte Ausgabedateigröße |
| Minimale Dateianzahl zum Auslösen | `spark.databricks.delta.autoCompact.minNumFiles` | `spark.databricks.iceberg.autoCompact.minNumFiles` | Legt fest, wie viele kleine Dateien mindestens vorhanden sein müssen |

### Mögliche Werte

| Option | Verhalten |
| --- | --- |
| `auto` | Passt die Zieldateigröße an, unter Berücksichtigung des übrigen Autotunings |
| `legacy` | Alias für `true` |
| `true` | Nutzt eine feste Zieldateigröße von 128 MB, kein dynamisches Sizing |
| `false` | Schaltet Auto Compaction aus |

## Optimized Writes

Optimized Writes verbessern die Dateigröße bereits beim Schreiben der Daten. Davon profitieren auch nachfolgende Lesezugriffe. Besonders wirksam sind Optimized Writes bei partitionierten Tabellen, da sie kleine Dateien pro Partition reduzieren.

Optimized Writes sind standardmäßig aktiviert für:

- `MERGE`
- `UPDATE` mit Subqueries
- `DELETE` mit Subqueries

Sie sind außerdem für `CTAS`-Anweisungen und `INSERT`-Operationen aktiviert, wenn SQL Warehouses genutzt werden.

### Konfigurationsoptionen

| Option | Verhalten |
| --- | --- |
| `true` | Nutzt eine Zieldateigröße von 128 MB |
| `false` | Schaltet Optimized Writes aus |

## Eine Zieldateigröße festlegen

Konfigurieren Sie die Tabelleneigenschaft `targetFileSize`, um eine gewünschte Dateigröße festzulegen.

| Eigenschaft | Beschreibung |
| --- | --- |
| `delta.targetFileSize` (Delta) | Größe in Bytes oder größeren Einheiten (z. B. `104857600` oder `100mb`) |
| `iceberg.targetFileSize` (Iceberg) | Größe in Bytes oder größeren Einheiten (z. B. `104857600` oder `100mb`) |

**Wichtiger Hinweis:** Bei Unity-Catalog-Managed-Tables mit SQL Warehouses oder Databricks Runtime 11.3 LTS und höher berücksichtigen nur `OPTIMIZE`-Befehle die Einstellung `targetFileSize`.

Beispielbefehl:

```sql
%sql
ALTER TABLE <table_name> SET TBLPROPERTIES (delta.targetFileSize = '100mb')
```

## Automatisches Tuning nach Tabellengröße

Databricks passt die Zieldateigröße automatisch an die Tabellengröße an:

- Tabellen unter 2,56 TB: Zielgröße 256 MB
- Tabellen zwischen 2,56 und 10 TB: Zielgröße wächst linear von 256 MB auf 1 GB
- Tabellen über 10 TB: Zielgröße 1 GB

### Erwartete Dateianzahl nach Tabellengröße

| Tabellengröße | Zieldateigröße | Ungefähre Dateianzahl |
| --- | --- | --- |
| 10 GB | 256 MB | 40 |
| 1 TB | 256 MB | 4.096 |
| 2,56 TB | 256 MB | 10.240 |
| 3 TB | 307 MB | 12.108 |
| 5 TB | 512 MB | 17.339 |
| 7 TB | 716 MB | 20.784 |
| 10 TB | 1 GB | 24.437 |
| 20 TB | 1 GB | 34.437 |
| 50 TB | 1 GB | 64.437 |
| 100 TB | 1 GB | 114.437 |

## Anzahl Zeilen pro Datei begrenzen

Nutzen Sie diese Session-Konfiguration, um die Anzahl der Datensätze pro Datei zu begrenzen: `spark.sql.files.maxRecordsPerFile`

Oder mit dem DataFrameWriter:

```python
.option("maxRecordsPerFile", value)
```

Geben Sie `null` oder einen negativen Wert an, entfällt die Begrenzung.

## Upgrade auf Background Auto Compaction

Für die Migration bestehender (legacy) Workloads:

1. Entfernen Sie die Spark-Konfiguration:

```
spark.databricks.delta.autoCompact.enabled
spark.databricks.iceberg.autoCompact.enabled
```

2. Entfernen Sie die alten Tabelleneigenschaften:

```sql
%sql
ALTER TABLE <table_name> UNSET TBLPROPERTIES (delta.autoOptimize.autoCompact)
ALTER TABLE <table_name> UNSET TBLPROPERTIES (iceberg.autoOptimize.autoCompact)
```

Danach läuft Background Auto Compaction automatisch für alle Unity-Catalog-Managed-Tables.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/tune-file-size  
**Stand:** 2026-08-06
