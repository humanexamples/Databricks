# Was ist Auto Loader?

Auto Loader verarbeitet neue Datendateien inkrementell und effizient, sobald sie im Cloud-Speicher ankommen – ohne zusätzliche Einrichtung. Es stellt dazu eine Structured-Streaming-Quelle namens `cloudFiles` bereit, die neue Dateien in Cloud-Verzeichnissen automatisch erkennt und einliest.

## Skalierung

Auto Loader verarbeitet Milliarden von Dateien bei Migrationsaufgaben und skaliert auf Millionen von Dateien pro Stunde. Es unterstützt sowohl Python- als auch SQL-Implementierungen.

## Unterstützte Speicherquellen

- Amazon S3
- Azure Data Lake Storage (ADLS)
- Google Cloud Storage (GCS)
- Unity-Catalog-Volumes
- Azure Blob Storage

## Unterstützte Dateiformate

JSON, CSV, XML, PARQUET, AVRO, ORC, TEXT und BINARYFILE, einschließlich vorkomprimierter Varianten.

## Fortschrittsverfolgung

Sobald Dateien entdeckt werden, werden ihre Metadaten in einem skalierbaren Key-Value-Store (RocksDB) am Checkpoint-Speicherort persistiert. Das garantiert Exactly-once-Verarbeitung und ermöglicht Fehlertoleranz, ohne dass der Zustand manuell verwaltet werden muss.

## Vorteile gegenüber Standard-Streaming

- Effiziente Dateierkennung skaliert mit der Anzahl eingelesener Dateien, nicht mit der Anzahl der Verzeichnisse.
- Eingebaute Schema-Inferenz und Erkennung von Schema Evolution.
- Native Integration mit Cloud-APIs senkt die Kosten.
- Der optionale File-Notification-Modus senkt die Kosten zusätzlich.

## Empfehlung

Databricks empfiehlt, Auto Loader innerhalb von Lakeflow-Pipelines zu nutzen. Dort werden Schemas und Checkpoints automatisch verwaltet, ohne dass eine manuelle Konfiguration nötig ist.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/  
**Stand:** 2026-08-07
