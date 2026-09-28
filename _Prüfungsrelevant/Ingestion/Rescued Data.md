# Rescued Data (`_rescued_data`)

## Übersicht: Automatisch dabei oder extra angeben?

| Methode | `_rescued_data` automatisch in der Zieltabelle? | Was muss ggf. angegeben werden? |
|---|---|---|
| **`read_files()`** (Batch, SQL) | ✅ Ja — immer, unabhängig davon, ob `schema` gesetzt ist | Nichts nötig; `rescuedDataColumn => 'resCol'` nur zum **Umbenennen** |
| **Auto Loader** (`cloudFiles` / `STREAM read_files`) | ✅ Ja — existiert bereits ganz ohne die Option | Nichts nötig; `rescuedDataColumn` nur zum **Umbenennen** |
| **`spark.readStream()`** ohne Auto Loader | ❌ Nein | `.option("rescuedDataColumn", "...")` explizit setzen, sonst erscheint die Spalte gar nicht |
| **`spark.read`** (Batch-DataFrameReader) | ❌ Nein — auch nicht bei Schema-Inferenz | `.option("rescuedDataColumn", "...")` explizit setzen, sonst erscheint die Spalte gar nicht |
| **`COPY INTO`** | ❌ Nein | `FORMAT_OPTIONS ('rescuedDataColumn' = '...')` explizit setzen, sonst erscheint die Spalte gar nicht |

**Muster:** Nur die beiden Auto-Loader-nahen Lesewege (`read_files()` und Auto Loader selbst) bringen `_rescued_data` von sich aus mit — dort steuert die Option nur den **Namen** der Spalte. Bei `spark.readStream()` ohne Auto Loader, `spark.read` und `COPY INTO` entscheidet die Option dagegen darüber, ob die Spalte **überhaupt erscheint**.

### Beispiele je Methode — wann nötig, wann nicht

**1. `read_files()`** 

```sql
SELECT * FROM read_files(
  '/Volumes/dbacademy_ecommerce/v01/raw/sales-csv',
  format => 'csv',
  header => true,
  schema => '..', # Es spielt keine Rolle ob 'schema' gesetzt ist oder  
                  # nicht, die 'rescued_data' Spalte wird immer generiert.
  rescuedDataColumn => 'resCol' # Umbenennung von _rescued_data Spalte in resCol. Wenn keine Umbenennung angegeben ist, erscheint die Spalte unter den Namen '_rescued_data'
); 
```

**2. Auto Loader**

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("sep","|")
  .option("cloudFiles.schemaLocation", "dbfs:/tmp/schema")
  # Umbenennung von _rescued_data Spalte in resCol
  # Selbst wenn .option("rescuedDataColumn", ..) nicht angegeben ist, 
  # erscheint die Spalte '_rescued_data'.
  .option("rescuedDataColumn", "resCol")
  .load("/Volumes/dbacademy_ecommerce/v01/raw/sales-csv")).limit(5).display()
# _rescued_data existiert bereits, ganz ohne rescuedDataColumn-Option
```

**3. `spark.readStream()`** 

```python
df = (spark.readStream
    .format("csv")
      # Angabe von Schema notwendig
    .schema("..")
    .option("header", True)
    .option("sep", "|")
# Umbenennung von _rescued_data Spalte in resCol
# Erst durch die Angabe von .option("rescuedDataColumn", ..) erscheint die Spalte.
    .option("rescuedDataColumn", "resCol")
    .load("/Volumes/dbacademy_ecommerce/v01/raw/sales-csv")
```

**4. `spark.read` — IMMER nötig, auch ohne Schema (mit Inferenz):**

```python
df = (spark.read.format("csv")
      .option("header", "true")
 # Umbenennung von _rescued_data Spalte in resCol
 # Erst durch die Angabe von .option("rescuedDataColumn", ..) erscheint die Spalte.
      .option("rescuedDataColumn", "resCol")
      .load(".."))
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
  'delimiter' = '|',
  # Umbenennung von _rescued_data Spalte in resCol
  # Erst durch die Angabe von .option("rescuedDataColumn", ..) erscheint die Spalte.
  'rescuedDataColumn' = '_rescued_data'
)
COPY_OPTIONS ('mergeSchema' = 'true');

-- Display the results
SELECT * FROM sales_csv_temp_copy_into LIMIT 5;
```

---

## `_rescued_data` vs. `_corrupt_record` / `badRecordsPath`

Zwei **verschiedene** Fehlerkategorien:

| Kategorie | Beispiel | Landet in | Verhalten mit aktiver `rescuedDataColumn` |
|---|---|---|---|
| **Typ-/Schema-Mismatch** | Text statt Zahl, fehlendes Feld, Case-Abweichung | `_rescued_data` | wird **gerettet**, Datensatz **nicht** verworfen — auch nicht in `DROPMALFORMED`, kein Fehler in `FAILFAST` |
| **Wirklich korrupter/unvollständiger Datensatz** | defektes JSON, CSV-Zeile mit falscher Spaltenanzahl | `_corrupt_record` bzw. `badRecordsPath` | wird verworfen (`DROPMALFORMED`) bzw. löst Fehler aus (`FAILFAST`) |

`_corrupt_record` prüfen (im `PERMISSIVE`-Modus, Spalte muss im Schema stehen):

```sql
SELECT * FROM read_files(
  '/Volumes/<c>/<s>/<v>/reviews_csv',
  format => 'csv', header => true, mode => 'PERMISSIVE',
  schema => 'review_id string, rating int, comment string, _corrupt_record string')
WHERE _corrupt_record IS NOT NULL;
```

> `badRecordsPath` hat **Vorrang** vor `_corrupt_record` — in den Pfad geschriebene fehlerhafte Zeilen erscheinen **nicht** im DataFrame.

---

## Parser-Modi (`PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`)

Über die zugrunde liegenden CSV-/JSON-Parser. In Kombination mit `rescuedDataColumn`:

- **Typkonflikte** → immer in `_rescued_data`, unabhängig vom Modus (auch `FAILFAST`).
- **Korrupte/unvollständige Datensätze** → in `DROPMALFORMED` verworfen, in `FAILFAST` Fehler.

Regeln im `PERMISSIVE`-Modus **mit** `rescuedDataColumn` (CSV):

- Die **erste Zeile** (Header oder Daten) legt die erwartete Zeilenlänge fest.
- Zeilen mit abweichender Spaltenanzahl gelten als **unvollständig** (korrupt).
- Datentyp-Abweichungen gelten **nicht** als korrupte Datensätze.
- Nur unvollständige/fehlerhafte CSV-Datensätze werden in `_corrupt_record` bzw. `badRecordsPath` aufgezeichnet.

> **Avro-Besonderheit:** Standard-`mode` ist `FAILFAST` (abweichend von `PERMISSIVE` bei CSV/JSON).

---

## Zusammenhang mit Schema Evolution

- Im Modus **`rescue`** (`schemaEvolutionMode => 'rescue'`) bleibt das Schema eingefroren; **alle** neuen/nicht passenden Spalten landen in `_rescued_data`, der Stream läuft ohne Unterbrechung weiter.
- Bei **`addNewColumnsWithTypeWidening`** landen nicht unterstützte Typänderungen (die sich nicht verlustfrei erweitern lassen) in `_rescued_data`; bei **`addNewColumns`** und **`failOnNewColumns`** ist laut Doku **keine** Nutzung von `_rescued_data` beschrieben. *(Einordnung: Da `rescuedDataColumn` eine eigenständige, vom Evolution-Modus unabhängige Option ist, ist ein zusätzliches explizites Setzen als Sicherheitsnetz auch bei diesen Modi plausibel — die Doku bestätigt das aber nicht ausdrücklich.)*
- Bei **`none`** werden Daten **nicht** gerettet, außer `rescuedDataColumn` ist explizit gesetzt.

Siehe [Schema Evolution.md](Schema%20Evolution.md), Abschnitt C.
