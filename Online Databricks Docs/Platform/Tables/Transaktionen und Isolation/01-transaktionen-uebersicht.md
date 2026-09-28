# Transaktionen: Übersicht

Transaktionen erlauben es, Operationen über mehrere SQL-Anweisungen und Tabellen hinweg zu koordinieren. Sie garantieren ACID-Eigenschaften: Atomarität, Konsistenz, Isolation und Dauerhaftigkeit. Alle Änderungen gelingen zusammen oder scheitern zusammen. Das sichert die Datenkonsistenz.

Transaktionen, die in Unity-Catalog-managed Iceberg-Tabellen schreiben, befinden sich in der Private Preview. Eine Teilnahme erfordert eine Anmeldung über ein offizielles Formular.

## Transaktionsmodi

Databricks unterstützt zwei Modi.

1. **Non-interactive (ATOMIC):** Automatischer Commit bei Erfolg, automatischer Rollback bei Fehler. Geeignet für feste Abfolgen und geplante Jobs.
2. **Interactive (BEGIN TRANSACTION):** Manueller Commit und Rollback. Geeignet für bedingte Logik, Validierung, Debugging und den programmatischen Zugriff über JDBC, ODBC oder PyODBC.

## Unterstützte Operationen

In Transaktionen sind erlaubt: SELECT-Unterabfragen, VALUES-Klauseln, verschiedene INSERT-Varianten, UPDATE, COPY INTO, DELETE FROM, MERGE INTO, USE CATALOG/SCHEMA, EXECUTE IMMEDIATE, DESCRIBE TABLE, SHOW COLUMNS und GET DIAGNOSTICS.

**Nicht unterstützt:** DDL-Operationen wie CREATE TABLE, ALTER TABLE, DROP TABLE, Time Travel sowie bestimmte Metadaten-Operationen wie SHOW TABLES oder SHOW DATABASES.

## Lese- und Schreibfähigkeiten

**Schreibziele:** Nur Unity-Catalog-managed Delta- oder Iceberg-Tabellen mit aktivierten Catalog Commits.

**Lesequellen:** Unity-Catalog-Tabellen, Streaming Tables, Views und materialisierte Sichten. Für nicht-transaktionale Quellen wird der Hinweis `allow_nontransactional_read` benötigt.

## Isolation und Nebenläufigkeit

Transaktionen ermöglichen wiederholbare Lesevorgänge über alle Anweisungen hinweg. Beim ersten Zugriff auf eine Tabelle innerhalb einer Transaktion erstellt Databricks einen konsistenten Snapshot dieser Tabelle.

Databricks nutzt optimistische Nebenläufigkeitskontrolle mit Konflikterkennung zum Commit-Zeitpunkt.

- **Non-interactive:** Konflikterkennung auf Zeilenebene.
- **Interactive:** Konflikterkennung auf Tabellenebene (außer bei INSERT ohne Lesevorgänge).
- **Konflikttypen:** Write-Write, Write-Read, Phantom Reads und Metadaten-Konflikte.

## Voraussetzungen

### Compute-Optionen

- Non-interactive: jedes SQL-Warehouse, Serverless Compute oder ein Cluster mit Databricks Runtime 18.0 oder höher.
- Interactive: jedes SQL-Warehouse.
- OpenSharing: Databricks Runtime 18.1 oder höher.

### Anforderungen an Tabellen

Alle beschriebenen Tabellen müssen Unity-Catalog-managed Tabellen mit aktivierten Catalog Commits sein.

## Fehlerbehandlung

| Szenario | Non-Interactive | Interactive |
|---|---|---|
| Fehler einer Anweisung | Automatischer Rollback | Manueller ROLLBACK nötig |
| Validierungsfehler | SIGNAL-Anweisung verwenden | Manueller ROLLBACK |
| Sitzungsabbruch | Automatischer Rollback | Automatischer Rollback |
| Timeout (10 Minuten Inaktivität) | Nicht anwendbar | Manueller ROLLBACK, falls Sitzung noch aktiv |
| Timeout (48 Stunden Maximum) | Automatischer Rollback | Automatischer Rollback nach Zustandsbereinigung |

## Wichtige Einschränkungen

- Interactive-Transaktionen erkennen Konflikte auf Tabellenebene.
- DDL-Operationen sind innerhalb von Transaktionen verboten.
- Pfadbasierter Dateizugriff wird nicht unterstützt, es müssen benannte Tabellen verwendet werden.
- Es gibt ein kombiniertes Limit von 100 Tabellen und 100 Views beim Lesen.
- 10 Minuten Idle-Timeout für interaktive Sitzungen.
- 48 Stunden maximale Transaktionsdauer.
- Gleichzeitige COPY-INTO-Ausführungen können in Konflikt geraten.
- Zeilenebenen-Nebenläufigkeit bei MERGE ist auf AWS GovCloud oder Single-User-Clustern nicht verfügbar.
- Kein Time-Travel-Support innerhalb von Transaktionen.

## Best Practices

Transaktionen sollten kurz gehalten werden. Lang laufende Transaktionen erhöhen die Wahrscheinlichkeit von Konflikten und halten Ressourcen länger belegt.

- Vorbedingungen früh validieren.
- `BEGIN ATOMIC` nutzen, um von Nebenläufigkeit auf Zeilenebene zu profitieren.
- Anwendungsseitige Wiederholungslogik implementieren.
- Interaktive Sitzungen mit einem ROLLBACK starten, um vorherigen Zustand zu bereinigen.

## Client-Unterstützung

Transaktionen funktionieren in: SQL Editor, Notebooks, JDBC (ab Version 3.0.5), ODBC (ab Version 2.10.0), dem Python-SQL-Connector (mit `autocommit=False`) sowie der Statement Execution API.

---
**Quelle:** https://docs.databricks.com/aws/en/transactions/  
**Stand:** 2026-08-06
