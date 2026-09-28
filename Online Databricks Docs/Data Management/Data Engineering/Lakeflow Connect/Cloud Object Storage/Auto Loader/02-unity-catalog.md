# Auto Loader mit Unity Catalog

Auto Loader kann Daten sicher aus External Locations lesen, die über Unity Catalog konfiguriert sind. Die Funktion arbeitet mit Structured Streaming für inkrementelle Datenverarbeitung und wird ab Databricks Runtime 11.3 LTS unterstützt, sowohl im Standard- als auch im Dedicated-Access-Modus.

<cell_type>markdown</cell_type>## Wichtige Konfigurationsanforderung

Databricks empfiehlt, Checkpoint- und Schema-Evolution-Dateien immer an einem von Unity Catalog verwalteten Speicherort abzulegen. Zudem erlaubt es Unity Catalog nicht, Checkpoint- oder Schema-Inferenz-/Evolution-Dateien innerhalb des Tabellenverzeichnisses zu verschachteln.

## Benötigte Berechtigungen

- `READ FILES` auf den Quell-External-Locations
- Owner-Rechte auf den Zieltabellen
- `READ FILES`, `WRITE FILES` und `CREATE TABLE` auf dem Bucket, der die Checkpoints speichert

## Laden in Managed Tables

Auto Loader streamt JSON-Daten im `cloudFiles`-Format. Der Python-Ansatz gibt einen Checkpoint-Pfad und einen Schema-Speicherort an und schreibt anschließend mit `.toTable()` in eine Unity-Catalog-Tabelle.

Alternativ können SQL-Nutzer `CREATE OR REFRESH STREAMING TABLE` mit `read_files()` verwenden – innerhalb von Lakeflow-Pipelines werden Checkpoint- und Schema-Speicherorte automatisch verwaltet.

## Laden in External Tables

Soll die Tabelle an einem bestimmten Speicherort erhalten bleiben, wird die Tabelle zunächst mit `CREATE TABLE ... LOCATION` registriert und die Daten anschließend über den Tabellennamen gestreamt. Der Checkpoint-Speicherort muss dabei einen separaten Pfad innerhalb einer von Unity Catalog verwalteten External Location nutzen, für die `CREATE EXTERNAL TABLE`-Berechtigungen vorliegen.

<cell_type>markdown</cell_type>---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/unity-catalog  
**Stand:** 2026-08-09
