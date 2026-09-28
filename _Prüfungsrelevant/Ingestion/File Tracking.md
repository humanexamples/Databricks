# File Tracking bei der Datei-Ingestion

## Was ist File Tracking?

**File Tracking** = die Engine **merkt sich, welche Dateien bereits verarbeitet wurden**, und überspringt sie bei einem erneuten Lauf.

- **Mit Tracking** → „nur neue Dateien" werden verarbeitet; wiederholte Läufe lesen bereits verarbeitete Dateien nicht erneut.
- **Ohne Tracking** → jeder Lauf liest **alle** aktuell zum Pfad passenden Dateien erneut.

Wonach wird getrackt (laut Doku)?

- **Auto Loader:** primär **Dateipfad**; optional zusätzlich **letzter Änderungszeitpunkt** (`cloudFiles.allowOverwrites = true`).
- **`COPY INTO`:** Dateiidentität über Metadaten im **Delta-Transaktionslog der Zieltabelle** — explizit **unabhängig** vom Änderungszeitpunkt.
- **Kein inhaltsbasiertes Tracking** (keine Prüfsumme/Checksumme) dokumentiert.

---

## Kurzübersicht

| Methode | Trackt gelesene Dateien? | Wo liegt der Zustand? | Tracking deaktivieren |
|---|---|---|---|
| **CTAS** (`CREATE OR REPLACE TABLE … AS SELECT`) | ❌ Nein | — | entfällt (ohnehin zustandslos) |
| **CTAS mit `read_files()`** | ❌ Nein (`read_files()` Batch ist zustandslos) | — | entfällt (ohnehin zustandslos) |
| **`spark.read(...).write(...)`** | ❌ Nein | — | entfällt (ohnehin zustandslos) |
| **`INSERT INTO … SELECT … FROM read_files(…)`** | ❌ Nein | — | entfällt (ohnehin zustandslos) |
| **`COPY INTO`** | ✅ Ja | **Delta-Transaktionslog der Zieltabelle** | `COPY_OPTIONS ('force' = 'true')` — pro Lauf gezielt ignorieren |
| **Auto Loader** (Python: `cloudFiles` /  SQL: `STREAM read_files`) | ✅ Ja | **RocksDB-Checkpoint** (`checkpointLocation`) | `checkpointLocation` löschen/wechseln — setzt das Tracking vollständig zurück (kein Per-Lauf-Schalter wie bei `COPY INTO`). <br>Über `cloudFiles.maxFileAge` lässt sich die Speicherung von Dateinamen bis mindestens 14 Tage herunter begrenzen. |

---

## Umsetzung je Methode

### 1. CTAS — `CREATE OR REPLACE TABLE … AS SELECT`

**Kein File Tracking.** Die `SELECT`-Quelle (andere Tabelle, `read_files()`, `spark.read`) wird zustandslos gelesen — es gibt kein „schon verarbeitet".

```sql
CREATE OR REPLACE TABLE workspace.default.daily_summary AS
SELECT order_date, SUM(quantity * unit_price) AS revenue
FROM workspace.default.orders
GROUP BY order_date;
```

- **Geeignet für:** kleinere Datasets, einmalige/geplante Ad-hoc-Verarbeitung.
- **Nachteil:** verarbeitet jedes Mal *alle* Quelldaten neu → hohe Latenz, keine Skalierung.

### 2. CTAS mit `read_files()` — `CREATE OR REPLACE TABLE … AS SELECT … FROM read_files(…)`

**Kein File Tracking.** `read_files()` **im Batch-Modus** (ohne `STREAM`-Schlüsselwort) ist ein **zustandsloser Lese-Baustein**: es liest bei jedem Aufruf *alle* aktuell zum Pfad passenden Dateien neu.

```sql
CREATE OR REPLACE TABLE workspace.default.orders_bronze AS
SELECT *
FROM read_files(
  '/Volumes/raw/orders/',
  format => 'csv',
  header => true
);
```

- **Kein** „nur neue Dateien"-Verhalten — dafür `COPY INTO` oder Auto Loader.
- `read_files()` **mit** `STREAM`-Schlüsselwort ist ein Sonderfall: dann nutzt es intern Auto Loader und **erbt dessen Checkpoint-Tracking** (siehe Punkt 5).

### 3. `spark.read(...).write(...)` — DataFrame-API (Batch)

**Kein File Tracking.** `spark.read` ist ein reiner, zustandsloser Lesevorgang — unabhängig vom Schreibmodus (`overwrite`/`append`) wird bei jedem Lauf die gesamte Quelle erneut gelesen.

```python
df = (spark.read
      .format("csv")
      .option("header", "true")
      .load("/Volumes/raw/orders/"))

(df.write
   .format("delta")
   .mode("overwrite")
   .saveAsTable("workspace.default.orders_bronze"))
```

- Für Streaming: `spark.readStream` + `writeStream` mit `checkpointLocation` → dann File Tracking über den Checkpoint (das ist der **Auto-Loader-Fall**, Punkt 5).

### 4. `INSERT INTO … SELECT … FROM read_files(…)`

**Kein File Tracking.** Jeder Lauf liest **alle** Dateien und **hängt** alle Zeilen an die Zieltabelle an.

```sql
INSERT INTO workspace.default.orders_bronze
SELECT * FROM read_files('/Volumes/raw/orders/', format => 'csv', header => true);
```

### 5. `COPY INTO`

**File Tracking über das Delta-Transaktionslog der Zieltabelle.**

`COPY INTO` merkt sich (über Metadaten im Delta Log), welche Dateien bereits geladen wurden, und überspringt sie bei erneuten Läufen — **auch wenn sie seither geändert wurden**.

> Wörtlich: *"Files in the source location that have already been loaded are skipped. This is true even if the files have been modified since they were loaded."*

```sql
COPY INTO workspace.default.orders_bronze
FROM '/Volumes/raw/orders/'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');
```

Tracking gezielt deaktivieren (z. B. um Dateien nach einer Datenkorrektur an der Quelle bewusst erneut zu laden):

```sql
COPY INTO workspace.default.orders_bronze
FROM '/Volumes/raw/orders/'
FILEFORMAT = CSV
COPY_OPTIONS ('force' = 'true');   -- File Tracking wird ignoriert
```

- **Besonderheit:** Zustand liegt in der **Zieltabelle selbst** → kein separater Checkpoint nötig, über `DESCRIBE HISTORY` nachvollziehbar.
- **Geeignet für:** inkrementelle Datei-Ingestion im Bereich **Tausender** Dateien, wenn SQL bevorzugt wird — kein Checkpoint/Schema-Location-Setup nötig.

### 6. Auto Loader (`cloudFiles` bzw. `STREAM read_files`)

**File Tracking über einen RocksDB-Checkpoint.**

Entdeckte Dateimetadaten werden in einem skalierbaren Key-Value-Store (RocksDB) am **`checkpointLocation`** gespeichert. Bei Neustart/Wiederholung setzt der Stream vom letzten Checkpoint fort und verarbeitet bereits gesehene Dateien **nicht** erneut → **exactly-once**.

> Wörtlich: *"This key-value store ensures that data is processed exactly once."*

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "csv")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .load("/Volumes/raw/orders/"))

(df.writeStream
   .option("checkpointLocation", "/Volumes/analytics/bronze/_checkpoint")
   .trigger(availableNow=True)
   .toTable("workspace.default.orders_bronze"))
```

SQL-Äquivalent (Streaming Table, intern Auto Loader):

```sql
CREATE OR REFRESH STREAMING TABLE workspace.default.orders_bronze
AS SELECT * FROM STREAM read_files('/Volumes/raw/orders/', format => 'csv', header => true);
```

**Tracking-Optionen:**

| Option | Wirkung |
|---|---|
| `cloudFiles.allowOverwrites` (Default `false`) | bei `true` zusätzlich Tracking nach **Änderungszeitpunkt** → geänderte Dateien werden erneut verarbeitet (dann Duplikate selbst behandeln) |
| `cloudFiles.maxFileAge` (min. `'14 days'`) | begrenzt, wie lange sich Auto Loader ein Datei-Ereignis merkt — zu aggressiv → Gefahr von Re-Ingestion/Duplikaten |
| `cloudFiles.includeExistingFiles` (Default `true`) | ob beim ersten Start bereits vorhandene Dateien ins Tracking aufgenommen werden |
| `checkpointLocation` löschen/wechseln | **setzt das Tracking vollständig zurück** → alle Dateien werden neu verarbeitet |
| `cloud_files_state(TABLE(...))` | Tabellenfunktion zum **direkten Abfragen** des Tracking-Zustands pro Datei (`NULL` / `PROCESSING` / `SKIPPED_CORRUPTED`) |

- **Geeignet für:** nahezu Echtzeit oder große, laufend wachsende Verzeichnisse; Skalierung auf **Millionen+** Dateien/Stunde.

---

## `COPY INTO` vs. Auto Loader — Auswahlkriterien

Beide tracken Dateien zuverlässig, unterscheiden sich aber darin, ab welcher Größenordnung sich der jeweilige Ansatz lohnt (laut Databricks-Doku):

- **Dateivolumen:** *"If you're going to ingest files in the order of thousands over time, you can use `COPY INTO`. If you are expecting files in the order of millions or more over time, use Auto Loader."* Grund: Auto Loader braucht insgesamt weniger Operationen zur Dateierkennung und verarbeitet in Batches → günstiger und effizienter bei großem Volumen.
- **Warum nicht einfach immer Auto Loader?** Bei nur Tausenden Dateien ist der Streaming-Apparat von Auto Loader unnötiger Overhead: Jeder Micro-Batch (Default ~1000 Dateien) durchläuft Listing/Discovery, Abgleich mit dem RocksDB-Checkpoint-State, Planung/Ausführung eines Spark-Jobs und einen Delta-Commit. Zusätzlich braucht Auto Loader eine `checkpointLocation` (und meist eine Schema-Location) als Setup-Aufwand, den `COPY INTO` nicht hat, da der Tracking-Zustand direkt im Delta-Log der Zieltabelle liegt. Databricks-Blog dazu: *"COPY INTO is a simple and powerful command to use when your source directory contains a small number of files (i.e., thousands of files or less), and if you prefer SQL."*
- **Schema Evolution:** Bei häufig wechselndem Quellschema bietet Auto Loader die besseren Primitive zur Schema-Inferenz und -Evolution.
- **Reprocessing:** Einen gezielten Teil bereits geladener (z. B. korrigierter) Dateien erneut laden ist mit `COPY INTO` einfacher steuerbar (`force = true` gezielt auf eine Teilmenge); bei Auto Loader ist selektives Reprocessing schwieriger — man kann aber `COPY INTO` parallel zu einem laufenden Auto-Loader-Stream nutzen, um gezielt nachzuladen.
- **Streaming:** Für Structured-Streaming-Ingestion aus Cloud-Speicher empfiehlt Databricks generell Auto Loader.

Einordnung: Das ist primär eine **Kapazitäts-/Zweckmäßigkeits-Empfehlung**, kein technisches Defizit von Auto Loader bei kleinen Mengen — File Tracking funktioniert bei beiden zuverlässig, Auto Loader ist bei Tausenden Dateien nur unnötig komplex.

---

## Filter-Optionen ≠ File Tracking

`modifiedAfter`, `modifiedBefore`, `pathGlobFilter` / `fileNamePattern`, `recursiveFileLookup` (gemeinsam für `spark.read`, `read_files`, `COPY INTO`, Auto Loader) bestimmen **welche Dateien überhaupt in Frage kommen** — nicht, **welche davon schon verarbeitet** wurden. Sie sind kein Ersatz für Checkpoint bzw. Delta-Log-Tracking. Vollständige Options-Referenz: [File Filter.md](File%20Filter.md).

---

## Eigene Datei-ID (Hash/UUID) — unabhängig von File Tracking

Es gibt **kein eingebautes UUID-Feld pro Datei** (weder in `_metadata` noch in `_object_metadata`, siehe `_metadata.md`). Eine eigene Datei-Identitäts-Spalte lässt sich aber bei **jeder** Methode ergänzen — unabhängig davon, ob die Methode selbst File Tracking betreibt oder nicht.

**Wichtig — reiner Pfad-Hash reicht nicht:** Wird am selben Pfad/Dateinamen zu einem späteren Zeitpunkt eine **neue** Datei (neuer Inhalt) abgelegt (siehe [Fall 3 — Gleiche Datei wird überschrieben](Datei%20Ingestion%20Varianten/03%20Gleiche%20Datei%20wird%20ueberschrieben.md)), liefert `sha2(_metadata.file_path, 256)` für beide Versionen **denselben** Wert — der Pfad ändert sich ja nicht. Damit zwei zu unterschiedlichen Zeitpunkten unter gleichem Namen/Pfad ingestierte Dateien unterschiedliche IDs bekommen, muss zusätzlich ein Merkmal einfließen, das sich bei einem Überschreiben ändert:

- **Deterministische ID pro Dateiversion (empfohlen):** Hash über `file_path` **plus** `file_modification_time` (optional zusätzlich `file_size`) — bleibt für dieselbe, unveränderte Datei über mehrere Läufe/Full Refreshs stabil, ändert sich aber automatisch, sobald die Datei am selben Pfad überschrieben wird (neue `file_modification_time`).
  ```sql
  SELECT *,
    sha2(concat_ws('|', _metadata.file_path, _metadata.file_modification_time, _metadata.file_size), 256) AS file_id
  FROM read_files('/Volumes/raw/orders/', format => 'csv', header => true);
  ```
  Reiner Pfad-Hash (`sha2(_metadata.file_path, 256)`) ist nur dann ausreichend, wenn Dateinamen garantiert **nie** wiederverwendet werden (z. B. Zeitstempel/UUID bereits im Dateinamen).
- **Echte Zufalls-UUID (`uuid()`):** liefert einen 36-stelligen UUID-String, ist aber **nicht-deterministisch** und wirkt pro **Zeile**, nicht pro Datei — direkt in `SELECT *, uuid() FROM read_files(...)` geschrieben, bekommt jede Zeile ihre eigene UUID. Für eine UUID *pro Datei* wäre ein Zwischenschritt nötig (distinct `file_path` + `file_modification_time` → `uuid()` zuweisen → zurück-joinen). Da jeder Aufruf einen neuen Zufallswert erzeugt, erfüllt diese Variante die Anforderung "unterschiedliche Dateiversion = unterschiedliche ID" ohnehin automatisch — vorausgesetzt, die UUID wird wirklich pro *Ingestion-Lauf* neu vergeben und nicht aus einer alten, zwischengespeicherten Zuordnung wiederverwendet.

**Bezug zu File Tracking:** Diese Spalte ersetzt kein File Tracking (sie verhindert keine erneute Verarbeitung), sondern macht Dateiversionen nachträglich identifizierbar/join-/dedupfähig — nützlich gerade bei Methoden **ohne** Tracking (Punkte 1–4), wo dieselbe Datei bei jedem Lauf erneut erscheint. Bei Methoden **mit** Tracking (`COPY INTO`, Auto Loader) wird eine unveränderte Datei ohnehin übersprungen; erst wenn `force = true` bzw. `cloudFiles.allowOverwrites = true` eine geänderte Datei am selben Pfad erneut verarbeiten lässt, greift die neue `file_modification_time` und erzeugt zuverlässig eine neue `file_id`.

---

## Verwandte Themen

- [File Filter.md](File%20Filter.md) — welche Dateien beim Lesen überhaupt in Frage kommen (unabhängig von File Tracking)
- [Select Möglichkeiten.md](Select%20Möglichkeiten.md) — Spaltenauswahl, `_metadata`-Selektion, `select()` vs. `selectExpr()`
- [Metadata.md](Metadata.md) — vollständige `_metadata`-Feldliste (Basis für die Datei-ID oben)
