# `COPY INTO` — Referenz

> **Gilt für:** Databricks SQL, Databricks Runtime

## Abschnittsübersicht

1. [Grundzweck und Kontext](#grundzweck)
2. [Formale Syntax](#syntax)
3. [Parameter im Detail](#parameter)
4. [Idempotenz und die `force`-Option](#idempotenz)
5. [Schema-Evolution: `mergeSchema` in `COPY_OPTIONS` vs. `FORMAT_OPTIONS`](#schema-evolution)
6. [`VALIDATE` — Trockenlauf ohne Schreiben](#validate)
7. [Nebenläufige Ausführung](#nebenlaeufig)
8. [Hinweis: Root-Pfade brauchen einen abschließenden Slash](#rootpfad)
9. [Verwandte Anweisungen](#verwandt)

---

## <a id="grundzweck">1. Grundzweck und Kontext</a>

`COPY INTO` lädt Daten aus einem Dateispeicherort in eine **Delta-Tabelle**. Die Operation ist **wiederholbar und idempotent**: Bereits geladene Dateien werden bei erneuten Läufen übersprungen — auch dann, wenn sie seit dem Laden verändert wurden. Die Nachverfolgung, welche Dateien bereits geladen wurden, erfolgt über Metadaten im Delta Log.

**Einordnung gegenüber Auto Loader / `read_files`:** `COPY INTO` ist die Batch-Variante der inkrementellen Datei-Ingestion (Incremental Batch). Empfehlung: bei Dateien im Bereich von **Tausenden** `COPY INTO`, bei **Millionen+** Dateien Auto Loader (`STREAM read_files`). Siehe [[_read_files]] und den Ordner *Incremental Batch Ingestion*.

---

## <a id="syntax">2. Formale Syntax</a>

```sql
COPY INTO target_table [ BY POSITION | ( col_name [ , <col_name> ... ] ) ]
FROM { source_clause |
       ( SELECT expression_list FROM source_clause ) }
FILEFORMAT = data_source
[ VALIDATE [ ALL | num_rows ROWS ] ]
[ FILES = ( file_name [, ...] ) | PATTERN = glob_pattern ]
[ FORMAT_OPTIONS ( { data_source_reader_option = value } [, ...] ) ]
[ COPY_OPTIONS ( { copy_option = value } [, ...] ) ]

source_clause
  source [ WITH ( [ CREDENTIAL { credential_name |
                                 (temporary_credential_options) } ]
                  [ ENCRYPTION (encryption_options) ] ) ]
```

---

## <a id="parameter">3. Parameter im Detail</a>

### `target_table`

Bezeichner einer **bestehenden Delta-Tabelle**. Darf **keine** temporalen Angaben (Time Travel) und **keine** Options-Spezifikation enthalten. Wird der Ort als Pfad angegeben (z. B. `` delta.`/path/to/table` ``), regelt Unity Catalog den Zugriff; für External Locations sind `WRITE FILES`-Berechtigungen oder benannte Storage Credentials nötig.

### `BY POSITION` | `( col_name [, ...] )`

Ordnet Quellspalten den Zielspalten **positionsbasiert** (nach Ordinalposition) zu, mit automatischem Typ-Cast.

- **`BY POSITION`** gilt ausschließlich für **headerlose CSV** mit `FORMAT_OPTIONS ('headers' = 'false')`.
- Die **geklammerte Spaltenliste** ordnet Quellspalten nach relativer Position zu und ignoriert dabei die Spaltenreihenfolge der Tabelle.
- `IDENTITY`- und `GENERATED`-Spalten dürfen **nicht** in der Liste stehen.
- Nicht angegebene Spalten erhalten ihren Default-Wert bzw. `NULL`.

### `source` und `WITH (...)`

`source` ist die **URI des Dateispeicherorts** mit den Daten im angegebenen Format. Zugriff über benannte Credentials, inline übergebene temporäre Credentials oder External-Location-Berechtigungen.

**`CREDENTIAL` (temporäre Credentials inline):**

| Cloud | Akzeptierte Optionen |
|---|---|
| AWS S3 | `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_SESSION_TOKEN` |
| ADLS / Azure Blob Storage | `AZURE_SAS_TOKEN` |

**`ENCRYPTION` (encryption_options):**

| Cloud | Akzeptierte Optionen |
|---|---|
| AWS S3 | `TYPE = 'AWS_SSE_C'`, `MASTER_KEY` |

### `SELECT expression_list`

Wählt vor dem Kopieren gezielt Spalten oder Ausdrücke aus den Quelldaten aus — auch **Window-Funktionen** sind erlaubt. **Nur globale Aggregate**; `GROUP BY` wird mit dieser Syntax **nicht** unterstützt.

### `FILEFORMAT = data_source`

Pflichtangabe. Einer von: `CSV`, `JSON`, `AVRO`, `ORC`, `PARQUET`, `TEXT`, `BINARYFILE`.

### `VALIDATE`

Prüft Parsebarkeit, Schema-Kompatibilität und Constraint-Erfüllung der Daten, **ohne** zu schreiben. Standardmäßig wird der gesamte Datenbestand geprüft; `VALIDATE num_rows ROWS` prüft nur eine Teilmenge. Siehe Abschnitt 6.

### `FILES` / `PATTERN`

- **`FILES`**: Liste von **bis zu 1000** konkreten Dateinamen. Nicht mit `PATTERN` kombinierbar.
- **`PATTERN`**: Glob-Muster zur Dateiauswahl. Nicht mit `FILES` kombinierbar.

| Muster | Bedeutung |
|---|---|
| `?` | Genau ein beliebiges Zeichen |
| `*` | Null oder mehr Zeichen |
| `[abc]` | Ein Zeichen aus der Menge {a, b, c} |
| `[a-z]` | Ein Zeichen aus dem Bereich {a…z} |
| `[^a]` | Ein Zeichen, das **nicht** aus der Menge/dem Bereich stammt |
| `{ab,cd}` | Ein String aus der Menge {ab, cd} |
| `{ab,c{de,fh}}` | Ein String aus der Menge {ab, cde, cfh} |

### `FORMAT_OPTIONS`

Format-spezifische **Leseoptionen** (z. B. `header`, `sep`, `multiLine`, `mergeSchema` für Parquet). Die Optionen teilen sich die gemeinsame Optionsbasis mit `spark.read`, `read_files` und Auto Loader (Spark-API-Optionsreferenz).

### `COPY_OPTIONS`

Steuert das Verhalten der `COPY INTO`-Operation **selbst**:

| Option | Typ | Standard | Bedeutung |
|---|---|---|---|
| `force` | boolean | `false` | Bei `true` wird Idempotenz deaktiviert; Dateien werden unabhängig davon geladen, ob sie bereits geladen wurden. |
| `mergeSchema` | boolean | `false` | Bei `true` wird Schema-Evolution passend zu den eingehenden Daten erlaubt. |

---

## <a id="idempotenz">4. Idempotenz und die `force`-Option</a>

`COPY INTO` merkt sich über das Delta Log, welche Dateien bereits geladen wurden, und überspringt sie bei Folgeläufen — auch bei zwischenzeitlicher Änderung der Datei (siehe Abschnitt 1).

Um dieses Verhalten **bewusst zu deaktivieren** (z. B. um Dateien nach einer Datenkorrektur an der Quelle erneut zu laden):

```sql
COPY INTO historical_users_bronze_ci
  FROM '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
  FILEFORMAT = parquet
  COPY_OPTIONS ('force' = 'true');
```

---

## <a id="schema-evolution">5. Schema-Evolution: `mergeSchema` in `COPY_OPTIONS` vs. `FORMAT_OPTIONS`</a>

`mergeSchema` existiert an **zwei** Stellen mit unterschiedlicher Bedeutung:

- **`COPY_OPTIONS ('mergeSchema' = 'true')`** — steuert die Schema-Evolution der **`COPY INTO`-Operation**: neue Spalten aus den Quelldateien werden zum **Zieltabellen-Schema** hinzugefügt.
- **`FORMAT_OPTIONS ('mergeSchema' = 'true')`** — Leseoption des **Parquet-Readers**: führt die Schemata **mehrerer Parquet-Dateien** beim Lesen zusammen (bevor überhaupt in die Zieltabelle geschrieben wird).

```sql
-- Schema-Evolution auf Operationsebene: neue Spalten landen im Zieltabellen-Schema
COPY INTO historical_users_bronze_ci
  FROM '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
  FILEFORMAT = parquet
  COPY_OPTIONS ('mergeSchema' = 'true');
```

```sql
-- Reader-Ebene: Schemata mehrerer Parquet-Quelldateien vor dem Laden zusammenführen
COPY INTO meine_tabelle
  FROM '/mnt/rohdaten/verkaeufe'
  FILEFORMAT = PARQUET
  FORMAT_OPTIONS ('mergeSchema' = 'true')
  COPY_OPTIONS ('mergeSchema' = 'true');
```

---

## <a id="validate">6. `VALIDATE` — Trockenlauf ohne Schreiben</a>

Mit `VALIDATE` lässt sich eine `COPY INTO`-Anweisung ausführen, **ohne** Daten in die Zieltabelle zu schreiben — geprüft werden Parsebarkeit, Schema-Kompatibilität und Constraints.

- `VALIDATE` bzw. `VALIDATE ALL`: prüft den **gesamten** Datenbestand.
- `VALIDATE num_rows ROWS`: prüft nur `num_rows` Zeilen.

Bei `VALIDATE n ROWS` mit `n < 50` wird eine Vorschau von bis zu `n` Zeilen zurückgegeben, ansonsten bis zu 50.

```sql
COPY INTO my_table
  FROM '/path/to/files'
  FILEFORMAT = CSV
  VALIDATE 15 ROWS
  FORMAT_OPTIONS ('header' = 'true');
```

---

## <a id="nebenlaeufig">7. Nebenläufige Ausführung</a>

`COPY INTO` kann nebenläufig aufgerufen werden, wenn:

- mehrere Datenproduzenten keine einfache Möglichkeit haben, sich zu koordinieren, und keinen einzelnen Aufruf absetzen können;
- ein sehr großes Verzeichnis Unterverzeichnis für Unterverzeichnis eingelesen werden soll.

Sichere Nebenläufigkeit setzt voraus, dass die parallelen Aufrufe auf **disjunkten Dateimengen** arbeiten. Ein einzelner Aufruf mit mehreren Dateien ist in der Regel performanter als mehrere nebenläufige Aufrufe.

---

## <a id="rootpfad">8. Hinweis: Root-Pfade brauchen einen abschließenden Slash</a>

Ist der Quellpfad ein Root-Pfad, muss er mit einem abschließenden Slash (`/`) enden, z. B. `s3://my-bucket/`.

---

## <a id="verwandt">9. Verwandte Anweisungen</a>

- [Credentials](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-external-locations)
- [DELETE](https://docs.databricks.com/aws/en/sql/language-manual/delta-delete-from)
- [INSERT](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-dml-insert-into)
- [MERGE](https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into) — siehe [[_merge_into]]
- [PARTITION](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-partition#partition)
- [query](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-qry-query)
- [UPDATE](https://docs.databricks.com/aws/en/sql/language-manual/delta-update)
- [Get started using COPY INTO to load data](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/) — enthält eine ausführliche Beispielsammlung.
