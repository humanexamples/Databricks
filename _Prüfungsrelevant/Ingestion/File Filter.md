# File Filter — welche Dateien werden überhaupt gelesen?

Ein Filter kann eine Datei ausschließen, die noch nie verarbeitet wurde.

Tracking kann eine Datei überspringen, die der Filter an sich zulassen würde.

## Generische Datei-Optionen (`spark.read`, `read_files`, Auto Loader — ohne `cloudFiles.`-Präfix)

| Option | Standard | Beschreibung |
|---|---|---|
| `modifiedAfter` | `None` | *"An optional timestamp as a filter to only ingest files that have a modification timestamp after the specified timestamp."* |
| `modifiedBefore` | `None` | *"An optional timestamp as a filter to only ingest files that have a modification timestamp before the specified timestamp."* |
| `pathGlobFilter` / `fileNamePattern` | `None` | *"A potential glob pattern for choosing files."* |
| `recursiveFileLookup` | `false` | Bei `true` werden auch verschachtelte Verzeichnisse durchsucht, selbst wenn sie keinem Partitionierungs-Namensschema folgen. |
| `ignoreCorruptFiles` | `false` | Bei `true` laufen Spark-Jobs beim Auftreten korrupter Dateien weiter, statt abzubrechen (ab DBR 11.3 LTS). |
| `ignoreMissingFiles` | `false` (Auto Loader) / `true` (`COPY INTO`, Legacy) | Bei `true` laufen Spark-Jobs weiter, wenn Dateien zwischen Auflistung und Lesevorgang verschwinden (ab DBR 11.3 LTS). |
| `ignoredPathSegmentRegex` | `^[._]` | Regex, die steuert, welche Dateien/Verzeichnisse beim Listing als "versteckt" übersprungen werden (ab DBR 19). |

```python
df = (spark.read.format("json")
  .option("pathGlobFilter", "*.json")
  .option("modifiedAfter", "2026-01-01T00:00:00")
  .load("/Volumes/analytics/bronze/events"))
```

```sql
SELECT * FROM read_files(
  '/Volumes/catalog/schema/landing/',
  format => 'json',
  modifiedAfter  => date_sub(current_date(), 7),
  modifiedBefore => current_date());
```

> **Pfad vs. `pathGlobFilter`:** Der Lade-Pfad selbst (`.load(...)` bzw. erstes Argument von `read_files`) erlaubt nur **Präfix**-Filterung über Wildcards im Pfad (z. B. `.../*/files`); für **Suffix**-Muster (z. B. nur `*.png`) ist `pathGlobFilter` nötig.

---

## Glob-Syntax-Referenz

Dieselbe Muster-Syntax gilt für `pathGlobFilter` / `fileNamePattern` **und** für `COPY INTO … PATTERN`:

| Muster | Bedeutung |
|---|---|
| `?` | Genau ein beliebiges Zeichen |
| `*` | Null oder mehr Zeichen |
| `[abc]` | Ein Zeichen aus der Menge `{a, b, c}` |
| `[a-z]` | Ein Zeichen aus dem Bereich `{a…z}` |
| `[^a]` | Ein Zeichen, das **nicht** aus der Menge/dem Bereich stammt |
| `{ab,cd}` | Ein String aus der Menge `{ab, cd}` |
| `{ab,c{de,fh}}` | Ein String aus der Menge `{ab, cde, cfh}` |

---

## Auto-Loader-spezifische Filter-Optionen

| Option | Standard | Wirkung |
|---|---|---|
| `cloudFiles.useStrictGlobber` | `false` | Bei `true` verhält sich die Glob-Auswertung wie bei anderen Apache-Spark-Dateiquellen, statt des lockereren Auto-Loader-Standardverhaltens (ab DBR 12.2 LTS). |
| `cloudFiles.includeExistingFiles` | `true` | Ob beim **ersten Start** eines Streams bereits vorhandene Dateien mit einbezogen werden (bei `false` werden nur ab dem Start neu ankommende Dateien berücksichtigt). |
| `cloudFiles.maxFileAge` | `None` (min. `'14 days'` bei Nutzung) | Begrenzt, wie lange Auto Loader sich ein Datei-Ereignis fürs Dedup-Tracking merkt — wirkt damit wie ein zeitliches Filterfenster, ist aber primär eine Tracking-Option (siehe [File Tracking.md](File%20Tracking.md)). |

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "binaryFile")
  .option("pathGlobFilter", "*.png")
  .option("cloudFiles.useStrictGlobber", "true")
  .load("/Volumes/catalog_name/schema_name/volume_name/path"))
```

---

## `COPY INTO`: `FILES` vs. `PATTERN`

| Parameter | Bedeutung | Kombinierbar mit dem jeweils anderen? |
|---|---|---|
| `FILES = (file_name [, ...])` | Explizite Liste von **bis zu 1000** konkreten Dateinamen | ❌ Nein |
| `PATTERN = glob_pattern` | Glob-Muster zur Dateiauswahl (Syntax siehe oben) | ❌ Nein |

```sql
COPY INTO workspace.default.orders_bronze
FROM '/Volumes/raw/orders/'
FILEFORMAT = CSV
PATTERN = 'orders_2026*.csv'
FORMAT_OPTIONS ('header' = 'true');
```

---

## Fehlertoleranz beim Filtern

```sql
SELECT * FROM read_files(
  '/Volumes/catalog/schema/landing/',
  format => 'json',
  ignoreCorruptFiles => true,
  ignoreMissingFiles => true);
```

```sql
COPY INTO workspace.default.orders_bronze
FROM '/Volumes/raw/orders/'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'ignoreCorruptFiles' = 'true');
```

---

## Filter-Optionen ≠ File Tracking

`modifiedAfter`, `modifiedBefore`, `pathGlobFilter` / `fileNamePattern`, `recursiveFileLookup` bestimmen **welche Dateien überhaupt in Frage kommen** — nicht, **welche davon schon verarbeitet** wurden. Sie sind kein Ersatz für Checkpoint- bzw. Delta-Log-Tracking (Details: [File Tracking.md](File%20Tracking.md#filter-optionen--file-tracking)).

---

## Übersicht: Bei welchen Methoden ist File Tracking überhaupt möglich?

Nur zwei der gängigen Lesewege merken sich, welche Dateien bereits verarbeitet wurden — alle anderen sind zustandslos und lesen bei jedem Lauf erneut **alle** aktuell zum Pfad/Filter passenden Dateien, unabhängig davon, ob sie schon einmal gelesen wurden.

**Kein File Tracking möglich:** `CREATE OR REPLACE TABLE ... AS SELECT` (CTAS), auch mit `read_files()` als Quelle; `spark.read(...).write(...)` (Batch-DataFrame-API); `INSERT INTO ... SELECT ... FROM read_files(...)`. Bei all diesen ist die Lese-Quelle zustandslos — es gibt schlicht keinen Mechanismus, der sich "schon gesehene" Dateien merkt.

**File Tracking möglich:** `COPY INTO` — Zustand liegt im **Delta-Transaktionslog der Zieltabelle** selbst, kein separater Checkpoint nötig. Und Auto Loader (`cloudFiles` bzw. `STREAM read_files`) — Zustand liegt in einem **RocksDB-Checkpoint** unter `checkpointLocation`. `read_files()` **mit** `STREAM`-Schlüsselwort ist dabei ein Sonderfall: Es nutzt intern Auto Loader und erbt dessen Checkpoint-Tracking — nur `read_files()` **ohne** `STREAM` ist zustandslos.

Vollständige Aufschlüsselung je Methode inkl. Code-Beispielen und Tracking-Optionen: [File Tracking.md](File%20Tracking.md).
