# Die `_metadata`-Spalte

## Was ist `_metadata`?

Eine **versteckte Spalte**, verfügbar für **alle Eingabe-Dateiformate**. Sie liefert **dateibezogene Metadaten zu jeder gelesenen Zeile** — ohne dass diese Info aus dem Dateiinhalt geparst werden muss.

Typische Nutzung: Herkunftsnachweis (Lineage), Debugging, Quelldatei/Ladezeitpunkt jeder Bronze-Zeile.

---

## Felder

`_metadata` ist ein `STRUCT`:

| Feld | Typ | Beschreibung | Min. Runtime |
|---|---|---|---|
| `file_path` | `STRING` | Dateipfad der Eingabedatei | 10.5 |
| `file_name` | `STRING` | Dateiname inkl. Erweiterung | 10.5 |
| `file_size` | `LONG` | Dateigröße in Bytes | 10.5 |
| `file_modification_time` | `TIMESTAMP` | letzter Änderungszeitstempel der Eingabedatei | 10.5 |
| `file_block_start` | `LONG` | Startversatz des gelesenen Blocks (Bytes) | 13.0 |
| `file_block_length` | `LONG` | Länge des gelesenen Blocks (Bytes) | 13.0 |

Zukünftige Releases können der `_metadata`-Struktur weitere Felder hinzufügen. Deshalb sollten besser **einzelne Felder** selektiert werden, statt die ganze Struktur weiterzureichen.

---

## Explizite Selektion erforderlich

`_metadata` erscheint **nicht** bei `SELECT *` / `.select("*")` — sie muss ausdrücklich referenziert werden.

```python
df = (spark.read.format("csv").schema(schema)
      .load("/Volumes/<c>/<s>/<v>/data/*")
      .select("*", "_metadata"))
```

Einzelne Felder per Punktnotation:

```python
.select("_metadata.file_name", "_metadata.file_size")
```

```sql
SELECT * EXCEPT (content), _metadata.file_name, _metadata.file_size
FROM read_files('/Volumes/<c>/<s>/<v>', format => 'binaryFile');
```

---

### Beispiele je Methode — wann nötig, wann nicht

**1. `read_files()`** 

```sql
SELECT *, _metadata 
FROM read_files(
        "/Volumes/dbacademy_ecommerce/v01/raw/sales-csv",
        format => "csv",
        sep => "|",
        header => true
      );
```

**2. Auto Loader**

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("sep","|")
  .option("cloudFiles.schemaLocation", "dbfs:/tmp/schema")
  .load("/Volumes/dbacademy_ecommerce/v01/raw/sales-csv")
  .select("*", "_metadata")
  .limit(5).display())
```

**3. `spark.readStream()`** 

```python
(spark.readStream
    .format("csv")
    .option("header", True)
    .option("sep", "|")
    .schema("order_id INT, .. , unique_items INT, items STRING")
    .load("/Volumes/dbacademy_ecommerce/v01/raw/sales-csv")
).select("*", "_metadata").limit(10).display()
```

**4. `spark.read` — IMMER nötig, auch ohne Schema (mit Inferenz):**

```python
(spark.read
    .format("csv")
    .option("header", True)
    .option("sep", "|")
    .schema("order_id INT, email STRING, transactions_timestamp BIGINT, total_item_quantity INT, purchase_revenue_in_usd DOUBLE, unique_items INT, items STRING")
    .load("/Volumes/dbacademy_ecommerce/v01/raw/sales-csv")
).select("*", "_metadata").limit(5).display()
```

**5. `COPY INTO`** — IMMER

```sql
DROP TABLE IF EXISTS sales_csv_temp_copy_into;
CREATE TABLE IF NOT EXISTS sales_csv_temp_copy_into;

-- Use COPY INTO to load CSV files into the temp table
COPY INTO sales_csv_temp_copy_into
FROM '/Volumes/dbacademy_ecommerce/v01/raw/sales-csv'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',
  'delimiter' = '|'
)
COPY_OPTIONS ('mergeSchema' = 'true');

SELECT *, _metadata FROM sales_csv_temp_copy_into LIMIT 5;
```

---

## `_rescued_data` vs. `_corrupt_record` / `badRecordsPath`

------



## Verfügbar über alle vier Zugriffswege





```sql
-- read_files (SQL)
SELECT * EXCEPT (content), _metadata
FROM read_files('/Volumes/<c>/<s>/<v>', format => 'binaryFile');
```

```python
# spark.read (Batch)
(spark.read.format("csv")
 .schema(schema)
 .load("/Volumes/<c>/<s>/<v>/data/*")
 .select("*", "_metadata"))
```

```python
# Auto Loader (Streaming) — _metadata umbenennen!
(spark.readStream
  .format("cloudFiles").option("cloudFiles.format", "csv").schema(schema)
  .load("abfss://…/csvData")
  .selectExpr("*", "_metadata as source_metadata")
  .writeStream.option("checkpointLocation", cp).start(targetTable))
```

```sql
-- COPY INTO (legacy)
COPY INTO my_delta_table
FROM (SELECT *, _metadata FROM 'abfss://…/csvData')
FILEFORMAT = CSV;
```

---

## Fallstricke

**Namenskonflikt (allgemein):** Enthält die Datenquelle bereits eine Spalte namens `_metadata`, liefern Abfragen diese Datenspalte zurück, nicht die Datei-Metadaten. Die Datenspalte hat Vorrang.

**Auto Loader — umbenennen:** Enthalten die Quelldaten eine Spalte namens `_metadata`, muss sie zu `source_metadata` umbenannt werden. Ohne Umbenennung ist die Datei-Metadaten-Spalte in der Zieltabelle nicht zugänglich: `.selectExpr("*", "_metadata as source_metadata")`.

**Auto Loader — `foreachBatch`:** `_metadata` muss **vor** dem `foreachBatch`-Aufruf im Streaming-Read-DataFrame referenziert werden, sonst ist die Spalte innerhalb der Funktion nicht enthalten.

```python
(spark.readStream.format("cloudFiles").option("cloudFiles.format", "csv")
  .load("abfss://…/csvData")
  .select("*", "_metadata")          # VOR foreachBatch
  .writeStream.foreachBatch(process_batch).start())
```

---

## In Filtern verwendbar

```sql
SELECT * EXCEPT (content), _metadata
FROM read_files('/Volumes/<c>/<s>/<v>', format => 'binaryFile',
    fileNamePattern => '*.{jpg,jpeg,png}')
WHERE _metadata.file_size BETWEEN 20000 AND 1000000;
```

---

## Bronze-Muster (Herkunft + Ladezeitpunkt)

```sql
CREATE TABLE historical_users_bronze AS
SELECT
  *,
  _metadata.file_modification_time AS file_modi_time,  -- Änderungszeitpunkt der Quelldatei
  _metadata.file_name              AS source_file,     -- Name der Quelldatei
  current_timestamp()              AS ingestion_time   -- Zeitpunkt der Ingestion selbst
FROM read_files('/Volumes/dbacademy_ecommerce/v01/raw/users-historical', format => 'parquet');
```

`current_timestamp()` (wann geladen?) ist klar von `_metadata.file_modification_time` (wann Datei geändert?) zu unterscheiden — beide werden in der Praxis oft gemeinsam mitgeführt.

---

## `_object_metadata` — Cloud-Objekt-Metadaten (verwandt)

**Public Preview, ab Databricks Runtime 18.2.** Separate versteckte Spalte mit über Cloud-APIs abgerufenen Speicher-Eigenschaften:

| Feld | Typ | Beschreibung |
|---|---|---|
| `mime_type` | `STRING` | MIME-Typ, z. B. `application/parquet` |
| `etag` | `STRING` | ETag (Änderungs-/Versionserkennung) |
| `user_metadata` | `VARIANT` | benutzerdefinierte Metadaten (z. B. S3 User-Defined Metadata) |
| `system_metadata` | `VARIANT` | vom Cloud-Anbieter gesetzte System-Metadaten |
| `tags` | `VARIANT` | benutzerdefinierte Objekt-Tags (z. B. S3 Object Tags) |

```sql
SELECT
  *,
  _object_metadata.user_metadata:my_key::STRING AS my_key,
  _object_metadata.tags:environment::STRING     AS env_tag
FROM csv.`<path>`;
```

**Einschränkungen:** S3 / Azure DFS / Azure Blob / GCP; jede Feld-Selektion → bis zu **2 zusätzliche Cloud-API-Aufrufe pro Datei** (Latenz bei vielen kleinen Dateien); `tags` nur S3 + Azure Blob (non-HNS), sonst `{}` bzw. `NULL` (fehlt `s3:GetObjectTagging`); bei Databricks-verwaltetem Speicher sind `system_metadata`/`user_metadata`/`tags` `NULL`; Namenskonflikt-Regel wie bei `_metadata` (Umgehung: `__object_metadata`).

---

## Verwandte Themen

- Deep-Dive im Projekt: [07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/05 Working with Files/05 Diagnose- und Herkunftsspalten/_metadata.md](07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/05%20Diagnose-%20und%20Herkunftsspalten/_metadata.md)
- [File Tracking.md](File%20Tracking.md) · [Rescued Data.md](Rescued%20Data.md) · [Schema Inference.md](Schema%20Inference.md) · [File Filter.md](File%20Filter.md) · [Select Möglichkeiten.md](Select%20Möglichkeiten.md)
- `read_files`-Referenz Abschnitt 5: [.../05 Working with Files/_read_files.md](07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/_read_files.md)
