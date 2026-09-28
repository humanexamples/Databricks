# Auto Loader — Überblick

Auto Loader ist im Kern eine Structured-Streaming-Quelle namens `cloudFiles`, die neu ankommende Dateien in einem Cloud-Verzeichnis inkrementell und effizient erkennt und lädt, sobald sie im Cloud-Speicher eintreffen — ohne zusätzliche Einrichtung. Auto Loader kann außerdem verwendet werden, um Milliarden von Dateien zu verarbeiten, etwa um eine Tabelle zu migrieren oder einen Backfill durchzuführen.

> *"Auto Loader incrementally and efficiently processes new data files as they arrive in cloud storage without any additional setup."*

Auto Loader kann Millionen von Dateien pro Stunde für nahezu Echtzeit-Ingestion verarbeiten und wird sowohl über Python als auch über SQL innerhalb von Lakeflow-Pipelines unterstützt.

Quelle: [What is Auto Loader?](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/) — siehe [17 Quellen.md](17%20Quellen.md) für die vollständige Quellenliste und Verifikationsmethodik.

---

## Unterstützte Speicherquellen

Auto Loader kann Datendateien aus folgenden Quellen laden:

| Quelle | URI-Schema |
|---|---|
| Amazon S3 | `s3://` |
| Azure Data Lake Storage (ADLS) | `abfss://` |
| Google Cloud Storage (GCS) | `gs://` |
| Unity-Catalog-Volumes | `/Volumes/` |
| Azure Blob Storage | `wasbs://` (WASB ist veraltet) |

## Unterstützte Dateiformate

Auto Loader kann die Dateiformate `JSON`, `CSV`, `XML`, `PARQUET`, `AVRO`, `ORC`, `TEXT` und `BINARYFILE` einlesen — einschließlich vorkomprimierter Varianten.

> **Beta:** `FILE`-Referenzen für Dokumente und Bilder.

---

## Fortschrittsverfolgung (Kurzfassung)

Sobald Dateien erkannt werden, wird ihre Metadaten in einem skalierbaren Key-Value-Store (RocksDB) am Checkpoint-Speicherort der Auto-Loader-Pipeline persistiert. Dieser Zustand ermöglicht Exactly-once-Verarbeitung und Recovery ohne manuelle Zustandsverwaltung. Details in [09 Datei-Tracking und Checkpoints.md](09%20Datei-Tracking%20und%20Checkpoints.md).

---

## Empfehlung: Auto Loader in Lakeflow-Pipelines

Databricks empfiehlt Auto Loader in Lakeflow-Pipelines für inkrementelle Datenaufnahme. Innerhalb von Lakeflow-Pipelines werden Checkpoint- und Schema-Speicherorte automatisch verwaltet. Dieser Ansatz wird gegenüber direktem Structured Streaming auf Cloud-Objektspeicher bevorzugt.

---

## Umgang mit nicht-geordnet eintreffenden Daten ("Handle out-of-order data")

Auto Loader garantiert **in keinem** Datei-Erkennungsmodus eine Reihenfolge, in der Dateien erkannt oder verarbeitet werden. Pipelines sollten so gestaltet sein, dass sie nicht-geordnet eintreffende Dateien handhaben können.

- **Lakeflow-Pipelines mit AUTO CDC:** Über `pipelines.cdc.tombstoneGCThresholdInSeconds` gelöschte Datensätze länger aufbewahren als die maximal erwartete Verzögerung. Standard-Retention: zwei Tage.
- **Structured Streaming ohne Lakeflow-Pipelines:** Soft Deletes mit Lösch-Flag und Zeitstempel verwenden; Zeitstempel vor dem Anwenden von Updates vergleichen, um das Überschreiben mit veralteten Daten zu vermeiden.

---

## Vorteile von Auto Loader gegenüber direktem Structured Streaming auf Dateien

- **Skalierbarkeit:** Auto Loader kann Milliarden von Dateien effizient entdecken ("Auto Loader can discover billions of files efficiently"); asynchrone Backfills schonen Compute-Ressourcen.
- **Performance:** *"The cost of discovering files with Auto Loader scales with the number of files being ingested instead of the number of directories."*
- **Schema-Unterstützung:** Erkennt Schema-Drift und rettet Daten (siehe [01 Schema-Inferenz und -Evolution.md](01%20Schema-Inferenz%20und%20-Evolution.md)).
- **Kosten:** Nutzt native Cloud-APIs und File-Notification-Dienste für Effizienz.

---

## Einstiegspunkte laut Doku

Die Overview-Seite verlinkt auf ETL-Pipeline-Tutorials, eine Amazon-S3-Setup-Anleitung sowie die Dokumentation zu Streaming über den Databricks-SQL-Editor; zusätzlich referenziert sie die Seite "Common data loading patterns" ([14 Common Data Loading Patterns.md](14%20Common%20Data%20Loading%20Patterns.md)) sowie die vollständige Options-Referenz (Spark-API-Optionen) für alle `cloudFiles.*`-Konfigurationen. Als Customization-Themen listet die Seite: Schema-Inferenz, Type Widening, Produktionskonfiguration, Retention-Management und Observability.

---

## Verhältnis zu `read_files` / `STREAM read_files` / `spark.readStream`

Auto Loader ist kein eigenständiges Werkzeug mit eigener Syntax, sondern eine **Engine**, die über mehrere Schnittstellen angesprochen werden kann:

- **Python/Scala, direkt:** `spark.readStream.format("cloudFiles")` — die "native" Ansprache der Engine über die `DataStreamReader`-Klasse.
- **SQL, über `read_files`:** `STREAM read_files(...)` innerhalb einer `CREATE OR REFRESH STREAMING TABLE`-Anweisung nutzt intern Auto Loader; alle `cloudFiles.*`-Optionen sind dabei über denselben Namensraum (in Backticks, da er einen Punkt enthält) ansprechbar.
- **Batch-Gegenstücke ohne Auto-Loader-Fähigkeiten:** `read_files` ohne `STREAM` bzw. `spark.read` sind zustandslose Batch-Operationen ohne Datei-Tracking, Schema-Evolution über mehrere Läufe hinweg oder `cloud_files_state`-Abfragbarkeit.

```python
# Python: Auto Loader direkt über spark.readStream ansprechen
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .load("/Volumes/analytics/bronze/events"))

(df.writeStream
   .option("checkpointLocation", "/Volumes/analytics/bronze/_checkpoint")
   .trigger(availableNow=True)
   .toTable("workspace.default.events_bronze"))
```

```sql
-- SQL: Auto Loader über STREAM read_files() innerhalb einer Streaming Table ansprechen
CREATE OR REFRESH STREAMING TABLE workspace.default.events_bronze
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json'
);
```

Das allgemeine Syntax-Muster (Basisform der Schema-Seite) mit generischem Ziel und `.start()` statt `.toTable()`:

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "parquet")
  .option("cloudFiles.schemaLocation", "<path-to-schema>")
  .load("<path-to-source-data>")
  .writeStream
  .option("checkpointLocation", "<path-to-checkpoint>")
  .start("<path-to-target>"))
```

Bereits das Angeben eines Zielverzeichnisses für `cloudFiles.schemaLocation` aktiviert Schema-Inferenz und -Evolution.

---

## Themenübersicht dieses Ordners

| Datei | Inhalt |
|---|---|
| [00 Überblick.md](00%20Überblick.md) | Grundzweck, Quellen, Formate, Engine-Charakter |
| [01 Schema-Inferenz und -Evolution.md](01%20Schema-Inferenz%20und%20-Evolution.md) | Schema-Inferenz, `schemaHints`, Evolution-Modi, Rescued-Data-Column |
| [02 Automatisches Type Widening.md](02%20Automatisches%20Type%20Widening.md) | `addNewColumnsWithTypeWidening` |
| [03 Unity-Catalog-Integration.md](03%20Unity-Catalog-Integration.md) | External Locations, Berechtigungen, Managed/External Tables |
| [04 Datei-Erkennungsmodi.md](04%20Datei-Erkennungsmodi.md) | Directory Listing vs. File Notification im Überblick |
| [05 Directory Listing Mode.md](05%20Directory%20Listing%20Mode.md) | API-Aufrufe, lexikalische Reihenfolge, Incremental Listing |
| [06 File Notification Mode.md](06%20File%20Notification%20Mode.md) | File Events vs. klassischer Modus, Cloud-Ressourcen, Troubleshooting |
| [07 Wie File Events funktionieren.md](07%20Wie%20File%20Events%20funktionieren.md) | Drei-Phasen-Mechanismus, 7-Tage-/24-Stunden-Regel |
| [08 Migration zu File Events.md](08%20Migration%20zu%20File%20Events.md) | Migration von Directory Listing / klassischen File Notifications |
| [09 Datei-Tracking und Checkpoints.md](09%20Datei-Tracking%20und%20Checkpoints.md) | RocksDB, `allowOverwrites`, `includeExistingFiles`, `maxFileAge`, Rate Limiting |
| [10 Clean Source (Quelldateien aufräumen).md](10%20Clean%20Source%20%28Quelldateien%20aufräumen%29.md) | `cloudFiles.cleanSource` MOVE/DELETE |
| [11 Best Practices.md](11%20Best%20Practices.md) | Trigger-Typen, Modus-Vergleich, Datenqualität, Kosten |
| [12 Produktionsbetrieb.md](12%20Produktionsbetrieb.md) | Kosten, Retention, Rate Limiting, Monitoring-Einstieg |
| [13 Observability.md](13%20Observability.md) | `cloud_files_state`, Metriken, Alarme, Troubleshooting |
| [14 Common Data Loading Patterns.md](14%20Common%20Data%20Loading%20Patterns.md) | Doku-Patterns + Praxis-Patterns (Multi-Flow, Bronze-Design) |
| [15 FAQ.md](15%20FAQ.md) | Auto Loader FAQ |
| [16 Auto Loader vs read_files vs COPY INTO.md](16%20Auto%20Loader%20vs%20read_files%20vs%20COPY%20INTO.md) | Entscheidungshilfe zwischen den Ingestion-Mechanismen |
| [17 Quellen.md](17%20Quellen.md) | Quellen, Gegenprüfungen, offene Punkte |
| [Options/](Options/README.md) | Eine Datei pro `cloudFiles.*`-Option (Referenz) |
