# Gängige Datenlademuster mit Auto Loader

Diese Seite stellt praktische Beispiele für häufige Anwendungsfälle bei der Cloud-Datenaufnahme mit Auto Loader vor.

<cell_type>markdown</cell_type>## Laden als Variant-Spalte

Auto Loader kann alle Daten aus unterstützten Dateiquellen als eine einzige `VARIANT`-Spalte laden. Dieser Ansatz ist flexibel gegenüber Schema- und Typänderungen und erhält dabei Groß-/Kleinschreibung sowie NULL-Werte der Quelldaten.

## Filtern mit Glob-Mustern

Muster-Matching ermöglicht die selektive Auswahl von Dateien und Verzeichnissen:

- `?` – ein beliebiges Zeichen
- `*` – null oder mehr beliebige Zeichen
- `[abc]` – Auswahl aus einer Zeichenmenge
- `[a-z]` – Zeichenbereich
- `[^a]` – Ausschluss bestimmter Zeichen
- `{ab,cd}` – Auswahl aus einer String-Menge

**Wichtige Unterscheidung:** Der Parameter `path` wird für Präfix-Muster verwendet, `pathGlobFilter` für Suffix-Muster.

## ETL-Implementierung

Die Kombination aus Schema-Inferenz, `mergeSchema` und Checkpoint-Speicherorten ergibt automatisierte, robuste Pipelines, die sich für die Ausführung als Databricks-Job eignen.

## Datenverlust vermeiden

Zwei Ansätze schützen die Datenintegrität:

1. **Rescue-Modus:** Erfasst unerwartete Felder und Typkonflikte in `_rescued_data`.
2. **Strikte Validierung:** Der Stream hält bei Schemaverletzungen über `failOnNewColumns` an.

## Umgang mit semi-strukturierten Daten

Mit `schemaHints` und Schema Evolution können Pipelines Daten von Anbietern verarbeiten, deren Spalten sich unvorhersehbar ändern – ohne manuellen Eingriff.

## Verarbeitung verschachtelter JSON-Daten

Mit den APIs für semi-strukturierten Datenzugriff lassen sich komplexe JSON-Inhalte über Punktnotation und Typumwandlung weiter transformieren.

## Umgang mit CSV-Dateien

Die CSV-Aufnahme unterstützt sowohl kopflose als auch Dateien mit Header, über eine explizite Schema-Angabe.

## Binär-/Bilddaten

Nach der Speicherung von Bildern in Delta Lake lässt sich mit einer Pandas-UDF verteilte Inferenz durchführen.

## Syntax in Lakeflow-Pipelines

Sowohl Python-Decorators als auch SQL-`CREATE STREAMING TABLE`-Anweisungen integrieren Auto Loader mit verwalteter Schema- und Checkpoint-Behandlung.

<cell_type>markdown</cell_type>---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/patterns  
**Stand:** 2026-08-09
