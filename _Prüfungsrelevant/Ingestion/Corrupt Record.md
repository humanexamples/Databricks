# Corrupt Record (`_corrupt_record`)

Sammelt **wirklich korrupte/unvollständige** Datensätze (defektes JSON, CSV-Zeile mit falscher Spaltenanzahl) im `PERMISSIVE`-Modus — im Unterschied zu [Rescued Data](Rescued%20Data.md) (`_rescued_data`), die reine Typ-/Schema-Mismatches rettet. Details zur Abgrenzung und den Parser-Modi siehe dort, Abschnitt "`_rescued_data` vs. `_corrupt_record`".

**Was ist `PERMISSIVE`?** Der Standard-Parser-Modus für CSV und JSON (Option `mode`). Statt das Einlesen bei einem defekten Datensatz abzubrechen, setzt `PERMISSIVE` für nicht parsbare Felder `NULL` und legt den gesamten problematischen Rohdatensatz zusätzlich in einer eigenen Spalte ab — dem `columnNameOfCorruptRecord` (Standardname `_corrupt_record`). Die beiden Alternativ-Modi: `DROPMALFORMED` verwirft betroffene Zeilen komplett, `FAILFAST` bricht das Einlesen beim ersten defekten Datensatz sofort ab. `PERMISSIVE` ist also die Voraussetzung dafür, dass `_corrupt_record` überhaupt befüllt wird — mit `DROPMALFORMED`/`FAILFAST` gibt es diese Spalte faktisch nicht.

**Voraussetzung bei allen Methoden:** Die Spalte `_corrupt_record` muss explizit Teil des angegebenen Schemas sein (als `string`) — sonst wird sie nicht befüllt bzw. taucht nicht im Ergebnis auf.

### Beispiele je Methode — wann unterstützt, wann nicht

**1. `read_files()`**

```sql
SELECT * FROM read_files(
  '/Volumes/<c>/<s>/<v>/reviews_csv',
  format => 'csv', header => true, mode => 'PERMISSIVE',
  schema => 'review_id string, rating int, comment string, _corrupt_record string')
WHERE _corrupt_record IS NOT NULL;
```

**2. Auto Loader** — unterstützt (laut Doku: *"Supported for Auto Loader."*)

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("header", "true")
  .option("mode", "PERMISSIVE")
  # Explizites Schema statt cloudFiles.schemaLocation, da _corrupt_record
  # als Spalte im Schema stehen muss, damit sie befüllt wird.
  .schema("review_id STRING, rating INT, comment STRING, _corrupt_record STRING")
  .option("columnNameOfCorruptRecord", "_corrupt_record")
  .load("/Volumes/<c>/<s>/<v>/reviews_csv")).limit(5).display()
```

**3. `spark.readStream()`**

```python
df = (spark.readStream
    .format("csv")
    # Angabe von Schema notwendig (inkl. _corrupt_record)
    .schema("review_id STRING, rating INT, comment STRING, _corrupt_record STRING")
    .option("header", True)
    .option("mode", "PERMISSIVE")
    .option("columnNameOfCorruptRecord", "_corrupt_record")
    .load("/Volumes/<c>/<s>/<v>/reviews_csv"))
```

**4. `spark.read`**

```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

schema = StructType([
  StructField("review_id", StringType(), True),
  StructField("rating", IntegerType(), True),
  StructField("comment", StringType(), True),
  StructField("_corrupt_record", StringType(), True)])

df = (spark.read.format("csv")
      .option("header", "true")
      .option("mode", "PERMISSIVE")
      .schema(schema)
      .load("/Volumes/<c>/<s>/<v>/reviews_csv"))
display(df.filter(df["_corrupt_record"].isNotNull()))
```

**5. `COPY INTO`** — **nicht unterstützt** (laut Doku: *"Not supported for `COPY INTO` (legacy)."*). Alternative: `badRecordsPath`, das fehlerhafte Datensätze in einen separaten Pfad statt in eine DataFrame-Spalte schreibt.

```sql
COPY INTO reviews_bronze
FROM '/Volumes/<c>/<s>/<v>/reviews_csv'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header' = 'true',
  -- 'columnNameOfCorruptRecord' würde hier NICHT greifen.
  'badRecordsPath' = '/Volumes/<c>/<s>/<v>/_bad_records'
);
```

> `badRecordsPath` hat **Vorrang** vor `_corrupt_record` — in den Pfad geschriebene fehlerhafte Zeilen erscheinen **nicht** im DataFrame (siehe [Rescued Data.md](Rescued%20Data.md)).

## Quellen

- Spark API Options (CSV, Zeile `columnNameOfCorruptRecord`): https://docs.databricks.com/aws/en/spark/api-options
- COPY INTO: https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into
- CSV lesen und schreiben: https://docs.databricks.com/aws/en/query/formats/csv

**Stand:** 2026-09-14, per `WebFetch` verifiziert.
