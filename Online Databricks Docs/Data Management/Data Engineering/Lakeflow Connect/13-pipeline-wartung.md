# Pipeline-Wartung

Diese Seite beschreibt wesentliche Wartungsaufgaben für Managed-Ingestion-Pipelines in Databricks.

## Ingestion-Pipeline neu starten

Verfügbar für SaaS-, Datenbank- und Query-basierte Connectors. Wird genutzt, um unerwartete Fehler, hängende Prozesse oder vorübergehende Probleme wie Netzwerkfehler und Timeouts zu beheben. Auslösbar über die Lakehouse-UI, die Pipelines-API oder die Databricks CLI.

## Ingestion-Gateway neu starten

Gilt für Datenbank-Connectors. Hilft, die Last auf der Quelldatenbank zu reduzieren, indem die Erkennung neuer Tabellen beschleunigt wird, die normalerweise alle sechs Stunden erfolgt. Nutzt dieselben Auslösemechanismen wie der Pipeline-Neustart.

## Full Refresh durchführen

Löscht vorhandene Daten und liest alle Datensätze erneut ein – für alle unterstützten Connector-Typen. Sinnvoll bei inkonsistenten oder unvollständigen Daten oder wenn eine erneute Verarbeitung nötig ist.

## Pipeline-Zeitplan anpassen

Ermöglicht die Anpassung der Ingestion-Frequenz, um Datenaktualität gegen die Ressourcenbelastung des Quellsystems abzuwägen. Konfigurierbar über die Lakehouse-UI, die Jobs-API oder die CLI.

## Alerts und Benachrichtigungen

Lakeflow Connect richtet automatisch Benachrichtigungen für Pipeline- und Job-Ereignisse ein. Die Benachrichtigungseinstellungen lassen sich individuell anpassen.

## Bereinigung von Staging-Daten

Für Pipelines, die nach dem 6. Januar 2025 erstellt wurden, plant Databricks automatisch die Entfernung von Staging-Daten nach 25 Tagen, mit physischer Löschung nach 30 Tagen. CDC-Datendateien, Snapshot-Dateien und Staging-Tabellendaten werden automatisch verwaltet.

## Tabellenauswahl

Die Pipelines-API unterstützt sowohl die Angabe einzelner Tabellen als auch schema-weite Ingestion-Konfiguration über das Feld `objects` in `ingestion_definition`.

## Verifizierung der Ingestion

Die Pipeline-Detailseite zeigt Datensatzzahlen, die während der Ingestion automatisch aktualisiert werden; über die Spaltenkonfiguration lassen sich optionale Spalten für aktualisierte (upserted) und gelöschte Datensätze einblenden.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/pipeline-maintenance  
**Stand:** 2026-08-07
