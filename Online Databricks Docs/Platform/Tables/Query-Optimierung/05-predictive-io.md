# Predictive I/O

Predictive I/O ist eine Sammlung von Databricks-Optimierungen, die die Performance bei Datenzugriffen verbessern. Diese Seite erklärt beschleunigtes Lesen und beschleunigte Updates.

## Was ist Predictive I/O?

Predictive I/O gliedert sich in zwei Kategorien:

- Beschleunigtes Lesen reduziert die Zeit zum Scannen und Lesen von Daten.
- Beschleunigte Updates reduzieren die Datenmenge, die bei Updates, Deletes und Merges neu geschrieben werden muss.

Predictive I/O steht ausschließlich auf der Photon-Engine zur Verfügung.

## Predictive I/O für beschleunigtes Lesen

Predictive I/O beschleunigt das Scannen und Filtern von Daten bei allen Operationen auf unterstützten Compute-Typen.

Predictive I/O für Lesevorgänge wird von Serverless- und Pro-SQL-Warehouses unterstützt. Es wird auch von Photon-beschleunigten Clustern ab Databricks Runtime 11.3 LTS unterstützt.

Predictive I/O verbessert die Scan-Performance durch den Einsatz von Deep-Learning-Techniken:

- Es bestimmt das effizienteste Zugriffsmuster und scannt nur die tatsächlich benötigten Daten.
- Es vermeidet das Dekodieren von Spalten und Zeilen, die für das Abfrageergebnis nicht benötigt werden.
- Es berechnet Wahrscheinlichkeiten dafür, dass die Suchkriterien einer selektiven Abfrage zu einer Zeile passen. Während die Abfrage läuft, nutzt Databricks diese Wahrscheinlichkeiten, um vorherzusagen, wo die nächste passende Zeile liegt. Es liest dann nur diese Daten aus dem Cloud-Speicher.

## Predictive I/O für beschleunigte Updates

Predictive I/O für Updates wird automatisch für alle Tabellen mit aktivierten Deletion Vectors verwendet, auf folgenden Photon-fähigen Compute-Typen:

- Serverless-SQL-Warehouses.
- Pro-SQL-Warehouses.
- Cluster mit Databricks Runtime 14.0 oder höher.

Predictive I/O für Updates wird bereits ab Databricks Runtime 12.2 LTS unterstützt. Für die beste Performance empfiehlt Databricks jedoch Runtime 14.0 oder höher.

Eine Admin-Einstellung im Workspace steuert, ob Deletion Vectors für neue Delta-Tabellen automatisch aktiviert werden.

Sie aktivieren die Unterstützung für Deletion Vectors auf einer Delta-Lake-Tabelle über eine Tabelleneigenschaft. Das geht bei der Tabellenerstellung oder nachträglich per `ALTER TABLE`, wie in folgenden Beispielen:

```sql
%sql
CREATE TABLE <table-name> [options] TBLPROPERTIES ('delta.enableDeletionVectors' = true);
ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.enableDeletionVectors' = true);
```

Beim Aktivieren von Deletion Vectors wird die Tabellen-Protokollversion angehoben. Nach dem Upgrade kann die Tabelle nicht mehr von Delta-Lake-Clients gelesen werden, die keine Deletion Vectors unterstützen.

Ab Databricks Runtime 14.1 können Sie das Deletion-Vectors-Tabellenfeature wieder entfernen, um die Kompatibilität mit anderen Delta-Clients herzustellen.

Predictive I/O nutzt Deletion Vectors, um Updates zu beschleunigen. Es reduziert, wie oft ganze Dateien bei Datenänderungen an Delta-Tabellen neu geschrieben werden müssen. Predictive I/O optimiert die Befehle `DELETE`, `MERGE` und `UPDATE`.

Statt beim Ändern oder Löschen eines Datensatzes alle Datensätze einer Datei neu zu schreiben, markiert Predictive I/O über Deletion Vectors, welche Datensätze aus den Zieldateien entfernt wurden. Ergänzende Dateien enthalten die Updates.

Nachfolgende Lesevorgänge auf der Tabelle ermitteln den aktuellen Tabellenzustand. Dazu wenden sie die vermerkten Änderungen auf die neueste Tabellenversion an.

Predictive I/O für Updates teilt alle Einschränkungen von Deletion Vectors. Ab Databricks Runtime 12.2 LTS gelten folgende Einschränkungen:

- OpenSharing wird auf Tabellen mit aktivierten Deletion Vectors nicht unterstützt.
- Für eine Tabelle mit vorhandenen Deletion Vectors können Sie keine Manifestdatei erzeugen. Führen Sie `REORG TABLE ... APPLY (PURGE)` aus und stellen Sie sicher, dass keine gleichzeitigen Schreiboperationen laufen, um ein Manifest zu erzeugen.
- Für eine Tabelle mit aktivierten Deletion Vectors können Sie Manifestdateien nicht inkrementell erzeugen.

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/predictive-io  
**Stand:** 2026-08-06
