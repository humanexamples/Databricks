# Delta Lake in Databricks – Übersicht

Delta Lake ist die optimierte Speicherschicht, die die Grundlage für Tabellen in einem Lakehouse auf Databricks bildet. Diese Seite gibt einen Überblick über alle Delta-Lake-Themen.

## Was ist Delta Lake?

Delta Lake erweitert Parquet-Dateien um ein Transaktionsprotokoll. Dadurch werden ACID-Transaktionen und eine strukturierte Metadaten-Verwaltung möglich.

## Wichtige Eigenschaften

- **Standardformat:** Alle Tabellen in Databricks nutzen standardmäßig Delta Lake.
- **Open Source:** Delta Lake basiert auf Open-Source-Software mit einem offenen Transaktionsprotokoll.
- **Spark-kompatibel:** Delta Lake ist vollständig kompatibel mit den Apache-Spark-APIs.
- **Streaming-fähig:** Delta Lake ist für die Integration mit Structured Streaming ausgelegt.

## Kernfunktionen

### Datenoperationen

- Tabellen erstellen, lesen und schreiben
- Daten mergen und upserten
- Selektives Überschreiben mit Filtern und Partitionen
- Schema-Evolution ohne vollständiges Neuschreiben der Daten

### Performance-Funktionen

- Liquid Clustering für optimierte Datenlayouts
- Data Skipping über Spaltenstatistiken
- Datei-Optimierung und Kompaktierung
- Vacuum-Operationen zur Reduzierung des Speicherbedarfs

### Qualität und Governance

- Schema-Durchsetzung beim Schreiben
- Integritätsbedingungen wie Primär- und Fremdschlüssel
- Generierte Spalten für berechnete Werte
- Angereicherte, benutzerdefinierte Metadaten

### Erweiterte Funktionen

- Change Data Feed zur Nachverfolgung von Änderungen
- Time-to-Live zur automatischen Löschung
- Abfrage der Versionshistorie einer Tabelle
- Column Mapping zum Umbenennen und Löschen von Spalten

## Themenbereiche in der Dokumentation

Die Dokumentation gliedert sich in folgende Hauptabschnitte:

- Was ist Delta Lake in Databricks?
- Erste Schritte mit Delta Lake
- Daten zu Delta Lake konvertieren und einlesen
- Delta-Lake-Tabellen aktualisieren und ändern
- Inkrementelle und Streaming-Workloads mit Delta Lake
- Frühere Tabellenversionen abfragen
- Schema-Erweiterungen in Delta Lake
- Dateien verwalten und Daten indizieren mit Delta Lake
- Delta-Lake-Einstellungen konfigurieren und überprüfen
- Datenpipelines mit Delta Lake und Lakeflow-Pipelines
- Kompatibilität der Delta-Lake-Funktionen
- Delta-Lake-API-Dokumentation

## Weiterführende Ressourcen

- Tutorial: Delta-Lake-Tabellen erstellen und verwalten
- Best Practices für Delta Lake
- Tutorial: ETL-Pipeline mit Lakeflow-Pipelines erstellen
- Inkrementelle Ingestion aus Amazon S3 einrichten
- Upsert in eine Delta-Lake-Tabelle mit Merge

## Einordnung dieser Seite

Diese Seite ist eine reine Übersichtsseite ohne eigene Code-Beispiele. Ein praktisches Tutorial mit vollständigen Code-Beispielen findet sich auf der nächsten Seite dieses Kursordners.

---
**Quelle:** https://docs.databricks.com/aws/en/delta/  
**Stand:** 2026-08-06
