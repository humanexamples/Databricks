# Auto Loader vs. `read_files` vs. generisches `spark.readStream` vs. `COPY INTO`

## Schnittstellen zur Auto-Loader-Engine

| Situation | Empfehlung |
|---|---|
| Python-/Scala-Pipeline, volle Kontrolle über `cloudFiles.*`-Optionen | `spark.readStream.format("cloudFiles")` (direkter Auto-Loader-Zugriff) |
| SQL-/Lakeflow-Pipeline, deklarative Streaming Table | `STREAM read_files(...)` (nutzt Auto Loader intern) |
| Einmaliger Batch-Import, kein Tracking nötig | `read_files` ohne `STREAM` bzw. `spark.read` — kein Auto Loader, zustandslos |
| Datei-Tracking, Exactly-once über Neustarts hinweg benötigt | Zwingend Auto Loader (`cloudFiles`, direkt oder über `STREAM read_files`) |
| Sehr große/wachsende Verzeichnisse, kontinuierliche Ingestion, Millionen Dateien/Stunde | Auto Loader mit File Events |
| Generische, nicht-`cloudFiles`-Streaming-Quelle (z. B. Delta, Kafka) über `spark.readStream` | `spark.readStream` ohne `cloudFiles`-Format — eigener Offset-/Commit-Checkpoint-Mechanismus statt RocksDB-Tracking |
| Ingestion-Zustand pro Datei einsehen/debuggen | `cloud_files_state`-Tabellenfunktion — nur im Streaming-/Auto-Loader-Kontext verfügbar |
| Einzelne Spaltentypen gezielt überschreiben, Rest inferieren lassen | `schemaHints` (Auto Loader/`read_files`) — bei reinem `spark.read` nicht verfügbar |

Siehe auch die Schwesterdateien [`../_read_files.md`](../_read_files.md) und [`../_spark_read.md`](../_spark_read.md) für die jeweils werkzeugeigene Syntax.

---

## Auto Loader vs. `COPY INTO`

`COPY INTO` ist ein eigenständiger SQL-Batch-Ingestion-Mechanismus mit eigenem Tracking über das **Delta-Log der Zieltabelle** — kein `cloudFiles`, kein RocksDB.

- Sollen im Laufe der Zeit Dateien in der Größenordnung von **Tausenden** aufgenommen werden, kann `COPY INTO` verwendet werden.
- Werden Dateien in der Größenordnung von **Millionen oder mehr** erwartet, sollte Auto Loader verwendet werden. Auto Loader benötigt insgesamt weniger Operationen zur Datei-Erkennung als `COPY INTO` und kann die Verarbeitung in mehrere Batches aufteilen, wodurch es im großen Maßstab kostengünstiger und effizienter ist.

Zwei weitere Abwägungskriterien:

- Wird sich das Daten-Schema häufig weiterentwickeln, bietet Auto Loader bessere grundlegende Fähigkeiten rund um Schema-Inferenz und -Evolution.
- Umgekehrter Vorteil von `COPY INTO`: Das Laden einer Teilmenge erneut hochgeladener Dateien lässt sich mit `COPY INTO` etwas einfacher handhaben. Mit Auto Loader ist es schwieriger, eine ausgewählte Teilmenge von Dateien erneut zu verarbeiten. `COPY INTO` kann jedoch verwendet werden, um die Teilmenge der Dateien neu zu laden, während gleichzeitig ein Auto-Loader-Stream läuft.

Quelle: [Ingest data from cloud object storage](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage).
