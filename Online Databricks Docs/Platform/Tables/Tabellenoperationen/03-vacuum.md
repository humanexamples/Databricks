# Nicht mehr benötigte Dateien entfernen mit VACUUM

Der Befehl `VACUUM` entfernt Datendateien, die von einer Tabelle nicht mehr referenziert werden und älter sind als die Aufbewahrungsschwelle. Regelmäßiges Ausführen senkt die Speicherkosten.

## Warum VACUUM ausführen?

Das Löschen ungenutzter Dateien senkt die Cloud-Speicherkosten. Das dauerhafte Entfernen dieser Dateien aus dem Cloud-Speicher stellt sicher, dass diese Datensätze nicht mehr zugänglich sind.

## Wichtige Hinweise

- Die Standard-Aufbewahrungsschwelle beträgt 7 Tage.
- Leere Verzeichnisse können nach dem Löschen der Dateien bestehen bleiben.
- `VACUUM` entfernt alle Dateien aus nicht verwalteten Verzeichnissen, außer solchen, die mit `_` oder `.` beginnen.
- Rein metadatenbasierte Löschfunktionen wie Deletion Vectors benötigen vor `VACUUM` ein `REORG TABLE ... APPLY (PURGE)`.
- Für Versionen, die älter sind als die Aufbewahrungsfrist, geht die Time-Travel-Funktion verloren.
- Bei aktiviertem Disk Caching können gelöschte Daten bis zum Cluster-Neustart weiterhin abfragbar bleiben.

## Grundlegende Syntax

```sql
%sql
VACUUM table_name
```

Ein Testlauf ohne tatsächliches Löschen:

```sql
%sql
VACUUM table_name DRY RUN
```

## Full- und Lite-Modus

**Lite-Modus** (verfügbar ab Runtime 16.4 LTS) nutzt das Transaktionsprotokoll anstelle einer vollständigen Dateiliste. Das verbessert die Performance bei großen Tabellen:

```sql
%sql
VACUUM table_name LITE
```

**Full-Modus** (Standard):

```sql
%sql
VACUUM table_name FULL
```

Der Lite-Modus setzt voraus, dass innerhalb der Aufbewahrungsschwelle des Transaktionsprotokolls (standardmäßig 30 Tage) mindestens ein erfolgreicher `VACUUM`-Lauf stattgefunden hat.

## Empfehlungen für den Cluster

Für optimale Performance: 1 bis 4 Worker mit je 8 Kernen, sowie ein Driver mit 8 bis 32 Kernen. Vergrößern Sie den Driver, wenn mehr als 10.000 Dateien verarbeitet werden oder der Lauf länger als 30 Minuten dauert.

## Konfigurationsbeispiele

Die Prüfung der Aufbewahrungsdauer deaktivieren (Vorsicht, nur für Sonderfälle):

```sql
%sql
SET spark.databricks.delta.retentionDurationCheck.enabled = false
```

```sql
%sql
SET spark.databricks.iceberg.retentionDurationCheck.enabled = false
```

Protokollierung von VACUUM-Läufen aktivieren:

```sql
%sql
SET spark.databricks.delta.vacuum.logging.enabled = true
```

```sql
%sql
SET spark.databricks.iceberg.vacuum.logging.enabled = true
```

Als Cluster-Policy-Konfiguration:

```json
{
  "spark_conf.spark.databricks.delta.vacuum.logging.enabled": {
    "type": "fixed",
    "value": "true"
  }
}
```

```json
{
  "spark_conf.spark.databricks.iceberg.vacuum.logging.enabled": {
    "type": "fixed",
    "value": "true"
  }
}
```

---
**Quelle:** https://docs.databricks.com/aws/en/tables/operations/vacuum  
**Stand:** 2026-08-06
