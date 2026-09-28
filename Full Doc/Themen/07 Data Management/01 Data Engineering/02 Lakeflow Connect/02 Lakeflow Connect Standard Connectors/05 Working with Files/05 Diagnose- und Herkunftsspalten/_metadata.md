# Die `_metadata`-Spalte — Referenz

Dieses Dokument fasst die dateibezogene `_metadata`-Spalte werkzeugübergreifend zusammen — für `read_files`, `spark.read` und Auto Loader. Es enthält die vollständige Feldliste mit Mindest-Runtime, Auto-Loader-spezifische Fallstricke sowie `_object_metadata` als verwandtes, neueres Feature.

## Abschnittsübersicht

1. [Grundzweck](#grundzweck)
2. [Vollständige Feldliste](#feldliste)
3. [Explizite Selektion erforderlich](#explizite-selektion)
4. [Verwendung je Werkzeug](#verwendung)
5. [Auto-Loader-spezifische Fallstricke](#autoloader-fallstricke)
6. [Namenskonflikt mit einer Datenspalte `_metadata`](#namenskonflikt)
7. [Verwendung in Filtern](#filter)
8. [`_object_metadata` — Cloud-Objekt-Metadaten (verwandtes, neueres Feature)](#object-metadata)
9. [Beispiel: Metadaten- und Ingestion-Zeitstempel-Spalten](#eigenes-beispiel)

---

## <a id="grundzweck">1. Grundzweck</a>

Die `_metadata`-Spalte ist eine versteckte Spalte und für alle Eingabe-Dateiformate verfügbar. Sie liefert dateibezogene Metadaten zu jedem gelesenen Datensatz, ohne dass diese Information selbst aus dem Dateiinhalt geparst werden müsste — nützlich u. a. für Herkunftsnachweis (Lineage), Debugging und um z. B. den Ladezeitpunkt oder die Quelldatei jeder Zeile im Bronze-Layer nachzuvollziehen.

---

## <a id="feldliste">2. Vollständige Feldliste</a>

Die `_metadata`-Spalte ist ein `STRUCT` mit folgenden Feldern:

| Feld | Typ | Beschreibung | Mindest-Runtime |
|---|---|---|---|
| `file_path` | `STRING` | Dateipfad der Eingabedatei | 10.5 |
| `file_name` | `STRING` | Dateiname inkl. Erweiterung | 10.5 |
| `file_size` | `LONG` | Dateigröße in Bytes | 10.5 |
| `file_modification_time` | `TIMESTAMP` | Letzter Änderungszeitstempel der Eingabedatei | 10.5 |
| `file_block_start` | `LONG` | Startversatz des gelesenen Blocks, in Bytes | 13.0 |
| `file_block_length` | `LONG` | Länge des gelesenen Blocks, in Bytes | 13.0 |

**Warnung:** Künftig können neue Felder zur `_metadata`-Spalte hinzukommen. Um dadurch verursachte Schema-Evolution-Fehler zu vermeiden, empfiehlt Databricks, gezielt einzelne Felder aus der Spalte zu selektieren, statt die gesamte Struktur ungefiltert weiterzureichen (siehe Abschnitt 3).

---

## <a id="explizite-selektion">3. Explizite Selektion erforderlich</a>

Da `_metadata` eine **versteckte** Spalte ist, muss sie in der Abfrage ausdrücklich selektiert werden, um im Ergebnis zu erscheinen. Sie erscheint **nicht** automatisch bei `SELECT *`/`.select("*")`.

```python
df = (spark.read
      .format("csv")
      .schema(schema)
      .load("/Volumes/catalog_name/schema_name/volume_name/data/*")
      .select("*", "_metadata"))
```

Dokumentiertes Ergebnisbeispiel für eine Zeile (Ausschnitt):

```
{
  "file_path": "/Volumes/catalog_name/schema_name/volume_name/data/f0.csv",
  "file_name": "f0.csv",
  "file_size": 12,
  "file_block_start": 0,
  "file_block_length": 12,
  "file_modification_time": "2021-07-02 01:05:21"
}
```

Einzelne Felder lassen sich per Punktnotation gezielt selektieren (empfohlen, siehe Warnung in Abschnitt 2):

```python
(spark.read
 .format("csv")
 .schema(schema)
 .load("/Volumes/catalog_name/schema_name/volume_name/data/*")
 .select("_metadata.file_name", "_metadata.file_size"))
```

```sql
-- read_files (SQL): dieselbe Punktnotation
SELECT * EXCEPT (content), _metadata.file_name, _metadata.file_size
FROM read_files('/Volumes/my_catalog/my_schema/my_volume', format => 'binaryFile');
```

---

## <a id="verwendung">4. Verwendung je Werkzeug</a>

`_metadata` ist **kein** auf ein einzelnes Werkzeug beschränktes Feature. Es ist über die gemeinsame Dateibasis aller vier Zugriffswege — `spark.read`, `read_files`/SQL, Auto Loader und `COPY INTO` (legacy) — identisch verfügbar.

```sql
-- read_files (SQL)
SELECT * EXCEPT (content), _metadata
FROM read_files('/Volumes/my_catalog/my_schema/my_volume', format => 'binaryFile');
```

```python
# spark.read (Batch)
df = (spark.read
      .format("csv")
      .schema(schema)
      .load("/Volumes/catalog_name/schema_name/volume_name/data/*")
      .select("*", "_metadata"))
```

```python
# Auto Loader (Streaming)
(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .schema(schema)
  .load("abfss://my-container@storage-account.dfs.core.windows.net/csvData")
  .selectExpr("*", "_metadata as source_metadata")
  .writeStream
  .option("checkpointLocation", checkpointLocation)
  .start(targetTable))
```

```sql
-- COPY INTO (legacy)
COPY INTO my_delta_table
FROM (
  SELECT *, _metadata FROM 'abfss://my-container@storage-account.dfs.core.windows.net/csvData'
)
FILEFORMAT = CSV
```

---

## <a id="autoloader-fallstricke">5. Auto-Loader-spezifische Fallstricke</a>

Zwei Besonderheiten treten **ausschließlich** im Auto-Loader-/Streaming-Kontext auf:

**1. Umbenennung bei Namenskonflikt in der Quelle:** Enthalten die Quelldaten bereits eine Spalte namens `_metadata`, muss sie zu `source_metadata` umbenannt werden. Ohne Umbenennung ist die Datei-Metadaten-Spalte in der Zieltabelle nicht zugänglich — Abfragen liefern dann stattdessen die Quellspalte. Deshalb im obigen Beispiel `.selectExpr("*", "_metadata as source_metadata")` statt eines einfachen `.select("*", "_metadata")`.

**2. Referenzierung vor `foreachBatch` nötig:** Wird `foreachBatch` verwendet und soll die `_metadata`-Spalte im Streaming-DataFrame verfügbar sein, muss sie **vor** dem `foreachBatch`-Aufruf im Streaming-Read-DataFrame referenziert werden — wird sie erst innerhalb der `foreachBatch`-Funktion referenziert, ist die Spalte dort **nicht** enthalten:

```python
(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .load("abfss://my-container@storage-account.dfs.core.windows.net/csvData")
  .select("*", "_metadata")          # Muss VOR foreachBatch referenziert werden
  .writeStream
  .foreachBatch(process_batch)
  .start())
```

---

## <a id="namenskonflikt">6. Namenskonflikt mit einer Datenspalte `_metadata`</a>

Enthält die Datenquelle bereits eine Spalte namens `_metadata` (gilt allgemein für `spark.read`/`read_files`/`COPY INTO`), liefern Abfragen die Spalte aus der Datenquelle, nicht die Datei-Metadaten. Die Datenspalte hat also Vorrang vor der versteckten Metadaten-Spalte gleichen Namens — ein direkter Zugriff auf die Datei-Metadaten ist in diesem Fall über den regulären Spaltennamen nicht mehr möglich (für Auto Loader gilt stattdessen die in Abschnitt 5 beschriebene Umbenennungs-Empfehlung).

---

## <a id="filter">7. Verwendung in Filtern</a>

`_metadata`-Felder lassen sich wie jede andere Spalte in `WHERE`/`.filter(...)` verwenden, z. B. um nach Dateigröße oder Änderungszeitpunkt einzuschränken:

```python
(spark.read
 .format("csv")
 .schema(schema)
 .load("/Volumes/catalog_name/schema_name/volume_name/data/*")
 .select("*")
 .filter(col("_metadata.file_name") == lit("test.csv")))
```

```sql
-- read_files (SQL): Dateigröße in Bytes eingrenzen
SELECT * EXCEPT (content), _metadata
FROM read_files(
    '/Volumes/my_catalog/my_schema/my_volume',
    format => 'binaryFile',
    fileNamePattern => '*.{jpg,jpeg,png,JPG,JPEG,PNG}')
WHERE _metadata.file_size BETWEEN 20000 AND 1000000;
```

---

## <a id="object-metadata">8. `_object_metadata` — Cloud-Objekt-Metadaten (verwandtes, neueres Feature)</a>

**Public Preview, ab Databricks Runtime 18.2.** Während `_metadata` reine Dateisystem-Information liefert (Pfad, Größe, Änderungszeit), stellt die separate, ebenfalls versteckte Spalte `_object_metadata` zusätzliche, über Cloud-APIs abgerufene Speicher-Ebene-Eigenschaften bereit — MIME-Typ, ETag, benutzerdefinierte Metadaten sowie Objekt-Tags:

| Feld | Typ | Beschreibung |
|---|---|---|
| `mime_type` | `STRING` | MIME-Typ des Objekts, z. B. `application/parquet` |
| `etag` | `STRING` | ETag des Objekts (nützlich zur Änderungs-/Versionserkennung) |
| `user_metadata` | `VARIANT` | Benutzerdefinierte Metadaten-Schlüssel-Wert-Paare (z. B. S3 User-Defined Metadata Headers) |
| `system_metadata` | `VARIANT` | Vom Cloud-Speicheranbieter gesetzte System-Metadaten |
| `tags` | `VARIANT` | Benutzerdefinierte Objekt-Tags (z. B. S3 Object Tags) |

```python
df = spark.read.format("csv").load(path)
display(df.select("*", "_metadata", "_object_metadata"))
```

Einzelwerte aus den `VARIANT`-Feldern lassen sich über den `::`-Cast-Operator extrahieren:

```sql
SELECT
  *,
  _object_metadata.user_metadata:my_key::STRING AS my_key,
  _object_metadata.tags:environment::STRING AS env_tag
FROM csv.`<path-to-load-from>`
```

**Wichtige Einschränkungen:**
- Verfügbar für Amazon S3, Azure DFS, Azure Blob und GCP.
- Jede Selektion eines Felds aus `_object_metadata` löst bis zu **zwei zusätzliche Cloud-API-Aufrufe pro Datei** aus — bei vielen kleinen Dateien kann das die Latenz spürbar erhöhen.
- `tags` wird nur für S3 und Azure Blob Storage (non-HNS) unterstützt; auf anderen Anbietern liefert es `{}`. Fehlt bei S3 die Berechtigung `s3:GetObjectTagging`, liefert `tags` stattdessen `NULL`.
- Für Databricks-verwaltete Speicherorte sind `system_metadata`, `user_metadata` und `tags` nicht verfügbar (`NULL`).
- Bei Namenskonflikt mit einer gleichnamigen Datenspalte gilt dieselbe Vorrangregel wie bei `_metadata` (Abschnitt 6); ein zusätzlicher Unterstrich-Präfix (`__object_metadata`) umgeht den Konflikt, wiederholbar bei erneuter Kollision.

**Auto Loader mit `_object_metadata`:**

```python
(spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "text")
    .option("cloudFiles.schemaLocation", schema_location)
    .load(path)
    .selectExpr("*", "_metadata as md", "_object_metadata as obj_md")
    .writeStream
    .format("delta")
    .option("checkpointLocation", checkpoint)
    .trigger(once=True)
    .start(table))
```

---

## <a id="eigenes-beispiel">9. Beispiel: Metadaten- und Ingestion-Zeitstempel-Spalten</a>

Das folgende Beispiel reichert eine Bronze-Tabelle beim Einlesen um Metadaten- und Ingestion-Zeitstempel-Spalten an — ein gängiges Muster, um Herkunft und Ladezeitpunkt jeder Zeile nachvollziehbar zu machen:

```sql
CREATE TABLE historical_users_bronze AS
SELECT
  *,
  _metadata.file_modification_time AS file_modi_time,  -- letzter Änderungszeitpunkt der Quelldatei
  _metadata.file_name AS source_file,                  -- Name der Quelldatei
  current_timestamp() AS ingestion_time                -- Zeitpunkt der Ingestion selbst
FROM read_files(
  '/Volumes/dbacademy_ecommerce/v01/raw/users-historical',
  format => 'parquet');
```

Dasselbe Muster über `spark.read` (Python):

```python
from pyspark.sql.functions import col, current_timestamp

df = (spark.read
      .format("parquet")
      .load("/Volumes/dbacademy_ecommerce/v01/raw/users-historical"))

df_with_metadata = (
    df.withColumn("file_modification_time", col("_metadata.file_modification_time"))
      .withColumn("source_file", col("_metadata.file_name"))
      .withColumn("ingestion_time", current_timestamp())
)

(df_with_metadata
 .write
 .format("delta")
 .mode("overwrite")
 .saveAsTable("dbacademy.default.historical_users_bronze_python_metadata"))
```

**Einordnung:** `current_timestamp()` liefert den Zeitpunkt der Ingestion selbst und ist damit klar von `_metadata.file_modification_time` (Änderungszeitpunkt der Quelldatei im Speicher) zu unterscheiden — beide Zeitstempel beantworten unterschiedliche Fragen ("Wann ist die Datei entstanden/geändert worden?" vs. "Wann wurde die Zeile ins Bronze-Layer geladen?") und werden in der Praxis oft gemeinsam mitgeführt.
