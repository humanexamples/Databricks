# Speicherorte für Schema- und Transaktionsdaten

**Zwei getrennte Dinge, die leicht verwechselt werden:** Zum einen der **Lese-seitige Zustand** — wo ein Lesemechanismus sein inferiertes Schema und seinen Verarbeitungsfortschritt ablegt (falls überhaupt). Zum anderen der **Tabellen-seitige Zustand** — das Transaction Log (`_delta_log`) der Ziel-Delta-Tabelle, das Schema und Schreibhistorie unabhängig davon speichert, mit welchem Lesemechanismus die Daten hineingeschrieben wurden. Diese Datei ordnet beides für die vier gängigen Lesewege ein.

---

## `read_files()` — Batch, SQL, ohne `STREAM`

**Zustandslos.** Es gibt keinen `schemaLocation`-Parameter im Batch-Modus und keinen Checkpoint. Jeder Aufruf inferiert das Schema unabhängig neu aus dem aktuellen Dateiinhalt (siehe [Schema Inference.md](Schema%20Inference.md)) bzw. verwendet das explizit übergebene `schema`. Zwischen zwei Aufrufen wird nichts gemerkt — ändert sich der Dateiinhalt, kann ein späterer Aufruf ein anderes Schema liefern.

Schreibt man das Ergebnis in eine Delta-Tabelle (`CREATE TABLE ... AS SELECT`, `INSERT INTO`), bekommt **die Tabelle** trotzdem ihr eigenes persistiertes Schema — siehe Abschnitt „Tabellenseite" unten.

---

## Auto Loader / `STREAM read_files()` — Streaming

Hier gibt es **zwei getrennte, persistierte Zustände**, die beide im (ggf. gemeinsamen) Auto-Loader-Verzeichnis liegen:

**Schema-Zustand — `schemaLocation` (SQL) / `cloudFiles.schemaLocation` (Python):** Auto Loader legt das inferierte Schema und dessen spätere Änderungen in einem Unterverzeichnis `_schemas` ab (siehe [Schema Inference.md](Schema%20Inference.md), Abschnitt zu `schemaLocation`). Ohne diesen Pfad findet keine Schema-Inferenz/-Evolution statt.

**Verarbeitungs-/Fortschrittszustand — `checkpointLocation`:** Laut Doku gilt: *"As files are discovered, their metadata is persisted in a scalable key-value store (RocksDB) in the checkpoint location of your Auto Loader pipeline. This key-value store ensures that data is processed exactly once."* Auto Loader merkt sich hier also pro entdeckter Datei Metadaten in einer RocksDB-basierten Key-Value-Datenbank, um jede Datei garantiert genau einmal zu verarbeiten — auch nach einem Neustart des Streams.

Dieser Zustand lässt sich per SQL-Funktion `cloud_files_state()` direkt einsehen — entweder über den Checkpoint-Pfad oder über die Streaming-Tabelle, die daraus befüllt wird:

```sql
-- Direkt über den Checkpoint-Pfad
SELECT path FROM cloud_files_state('/Volumes/analytics/bronze/_checkpoint');

-- Über die Streaming-Tabelle, die read_files/Auto Loader befüllt
SELECT path FROM cloud_files_state(TABLE(bronze_events));
```

`schemaLocation` und `checkpointLocation` **dürfen identisch sein** — in der Praxis liegen Schema-Tracking (`_schemas`) und Datei-Tracking (RocksDB) dann im selben Wurzelverzeichnis nebeneinander. Da `STREAM read_files` intern Auto Loader nutzt, gilt hier alles Gesagte identisch — unabhängig davon, ob man die SQL-Syntax oder die native Python-API `cloudFiles` verwendet.

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")   # -> _schemas
  .load("/Volumes/analytics/bronze/events")
  .writeStream
  .option("checkpointLocation", "/Volumes/analytics/bronze/_checkpoint")     # -> RocksDB-Datei-Tracking
  .toTable("bronze_events"))
```

---

## `spark.read()` — Batch-DataFrameReader

Wie `read_files()` im Batch: **zustandslos.** Es gibt weder einen `schemaLocation`- noch einen `checkpointLocation`-Begriff für Batch-Lesevorgänge. Ohne `.schema(...)` wird bei jedem Aufruf neu inferiert (siehe [Schema Inference.md](Schema%20Inference.md)); mit `.schema(...)` wird die Inferenz übersprungen, aber auch dieses Schema wird nirgends für spätere Aufrufe gemerkt — es steckt nur im aufrufenden Code selbst.

---

## `spark.readStream()` ohne Auto Loader — klassische File-Source

Kein Schema-Zustand: Wie in [Schema-Pflicht.md](Schema-Pflicht.md) beschrieben, ist hier standardmäßig ein explizites `.schema(...)` zwingend erforderlich — es gibt nichts zu inferieren und folglich auch keinen `_schemas`-Mechanismus, der etwas persistieren müsste.

Verarbeitungs-/Fortschrittszustand: Auch diese generische Structured-Streaming-Quelle benötigt eine `checkpointLocation`, über die Spark den Streaming-Fortschritt (u. a. welche Eingabedaten bereits verarbeitet wurden) fehlertolerant nachvollziehbar macht — das ist der allgemeine Checkpoint-Mechanismus von Structured Streaming, **nicht** das RocksDB-basierte Datei-Tracking von Auto Loader. Die beiden Mechanismen sind unterschiedlich implementiert, auch wenn beide über dieselbe Option `checkpointLocation` konfiguriert werden.

---

## Tabellenseite: Schema und Transaktionshistorie liegen immer im `_delta_log`

Unabhängig davon, mit welchem der vier Lesewege Daten eingelesen wurden — sobald sie in eine **Delta-Tabelle** geschrieben werden, übernimmt ab da das Transaction Log der Tabelle selbst (`_delta_log`): Jede Tabellenversion trägt dort ihre eigene Metadaten-Aktion inklusive des zu diesem Zeitpunkt gültigen Schemas, plus die vollständige Schreibhistorie (`DESCRIBE HISTORY`). Dieser Tabellen-Zustand ist vom Lese-seitigen Zustand oben vollständig unabhängig — er existiert für jede Delta-Tabelle gleich, ob die Daten per `read_files`, Auto Loader, `spark.read` oder `spark.readStream` hineingeschrieben wurden. Details: [Schema Versioning.md](Schema%20Versioning.md).

---

## Verwandte Themen

- [Schema Inference.md](Schema%20Inference.md) · [Schema-Pflicht.md](Schema-Pflicht.md) · [Schema Versioning.md](Schema%20Versioning.md) · [Schema Evolution.md](Schema%20Evolution.md)

## Quellen

- Auto Loader (RocksDB-Zitat): https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/
- Auto Loader schema (schemaLocation/`_schemas`): https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema
- `cloud_files_state`: https://docs.databricks.com/aws/en/sql/language-manual/functions/cloud_files_state

**Stand:** 2026-09-16, per `WebFetch` verifiziert (Beispiele für `cloud_files_state()` gegen AWS-Doku und Microsoft-Learn-Spiegel wortgleich bestätigt).
