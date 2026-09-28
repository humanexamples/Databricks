# Isolationsstufen und Schreibkonflikte

Diese Seite beschreibt Isolationsstufen und das Verhalten bei Schreibkonflikten für Delta-Lake-Tabellen in Databricks.

## ACID-Garantien

Delta Lake bietet ACID-Transaktionsgarantien zwischen Lese- und Schreibvorgängen:

- **Writer:** Mehrere Writer über mehrere Cluster hinweg können gleichzeitig eine Tabellenpartition ändern. Writer sehen dabei eine konsistente Snapshot-Sicht auf die Tabelle. Schreibvorgänge erfolgen in einer seriellen Reihenfolge.
- **Reader:** Reader sehen weiterhin die konsistente Snapshot-Sicht der Tabelle, mit der ein Databricks-Job gestartet wurde. Das gilt auch, wenn die Tabelle während des Jobs geändert wird.

Databricks nutzt standardmäßig Delta Lake für alle Tabellen.

## Themen zur Isolation

| Thema | Beschreibung |
| --- | --- |
| Isolationsstufen (WriteSerializable und Serializable) | Wie die beiden Isolationsstufen gleichzeitige Operationen beeinflussen und wie Sie sie konfigurieren. |
| Row-Level Concurrency | Wie die Konflikterkennung auf Zeilenebene Schreibkonflikte bei gleichzeitigen Operationen auf denselben Datendateien reduziert. |

Informationen zu Transaktionsisolation, Snapshot-Verhalten und Konfliktbehandlung finden Sie im Abschnitt „Transaktionsisolation" der Databricks-Dokumentation zu Transaktionen.

## Konflikte durch Metadatenänderungen

Metadatenänderungen lassen alle gleichzeitig laufenden Schreiboperationen fehlschlagen. Dazu zählen Änderungen am Tabellenprotokoll, an Tabelleneigenschaften oder am Datenschema.

Streaming-Lesevorgänge schlagen fehl, wenn sie auf einen Commit stoßen, der Tabellenmetadaten ändert. Soll der Stream weiterlaufen, müssen Sie ihn neu starten.

Die folgenden Beispiele zeigen Abfragen, die Metadaten ändern:

```sql
%sql
-- Set a table property
ALTER TABLE table_name SET TBLPROPERTIES ('delta.isolationLevel' = 'Serializable')

-- Enable a feature using a table property and update the table protocol
ALTER TABLE table_name SET TBLPROPERTIES ('delta.enableDeletionVectors' = true);

-- Drop a table feature
ALTER TABLE table_name DROP FEATURE deletionVectors;

-- Upgrade to UniForm
REORG TABLE table_name APPLY (UPGRADE UNIFORM(ICEBERG_COMPAT_VERSION=2));

-- Update the table schema
ALTER TABLE table_name ADD COLUMNS (col_name STRING);
```

## Nächste Schritte

- Weiterführende Informationen finden Sie unter „Transaktionen" in der Databricks-Dokumentation.

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/isolation/  
**Stand:** 2026-08-06
