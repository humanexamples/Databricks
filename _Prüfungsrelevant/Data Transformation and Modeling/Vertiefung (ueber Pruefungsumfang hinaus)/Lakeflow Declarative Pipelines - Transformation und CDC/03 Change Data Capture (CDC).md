# Change Data Capture (CDC) in Lakeflow Declarative Pipelines

## 1. Die AUTO-CDC-APIs im Überblick

- `AUTO CDC`-APIs ersetzen ältere `APPLY CHANGES`-APIs, identische Syntax. `APPLY CHANGES` bleibt verfügbar, Databricks empfiehlt `AUTO CDC`.
- **Gotcha:** `AUTO CDC`-APIs werden von Apache Spark Declarative Pipelines **nicht** unterstützt.

| Variante | Wann | Details |
|---|---|---|
| **`AUTO CDC`** | Quelle hat aktivierten CDC-Feed | verarbeitet Insert/Update/Delete-Events; SQL: `AUTO CDC ... INTO`; Python: `create_auto_cdc_flow()` |
| **`AUTO CDC FROM SNAPSHOT`** | kein CDC, nur Snapshots | vergleicht in-order eintreffende Snapshots; **nur Python**: `create_auto_cdc_from_snapshot_flow()` |

- Beide unterstützen **SCD Typ 1** (nur aktueller Zustand) und **SCD Typ 2** (vollständige Historie) — Abschnitt 2.
- Nur `AUTO CDC`: **Bitemporal Storage** (Beta, Abschnitt 10.6), **partielle Updates** (Abschnitt 10.5).
- Voraussetzung: Serverless Lakeflow Pipelines oder Edition **Pro**/**Advanced**.

### 1.1 Vollständige Signatur von `create_auto_cdc_flow()` (alle Parameter im Überblick)

Nur die ersten vier Parameter sind Pflicht, alle übrigen optional. Jeder Parameter wird mit eigenem Codebeispiel in den folgenden Abschnitten vertieft (Verweise in den Kommentaren):

```python
from pyspark import pipelines as dp

dp.create_auto_cdc_flow(
# Pflicht: Zieltabelle, vorher per create_streaming_table() angelegt
  target = "<target-table>",     
# Pflicht: View/Tabelle mit den CDC-Change-Events
  source = "<data-source>",       
# Pflicht: Spalte(n), die eine Zeile eindeutig identifizieren
  keys = ["key1", "key2", "keyN"],   
# Pflicht: legt fest, welches Event pro Key gewinnt (höchster Wert gewinnt
  sequence_by = "<sequence-column>",   
# optional, nur bitemporal: zweite Sequenzspalte "wann wusste das System davon"
  system_sequence_by = None,    
# optional: True = null in Updates überschreibt für ALLE Spalten nicht den Zielwert
  ignore_null_updates = False,      
# optional: wie ignore_null_updates, aber nur für diese Spaltenliste
  ignore_null_updates_column_list = None,   
# optional: wie ignore_null_updates, für alle AUSSER diesen Spalten
  ignore_null_updates_except_column_list = None,   
# optional: Quellspalte, die pro Change-Datensatz die zu aktualisierenden Zielspalten als Array nennt
  columns_to_update = None,                        
# optional: Ausdruck, wann ein Event als DELETE statt Upsert behandelt wird
  apply_as_deletes = None,         
# optional, nur SCD Typ 1: Ausdruck, wann ein Event die ganze Zieltabelle leert
  apply_as_truncates = None,     
# optional: Einschlussliste — nur diese Spalten landen im Ziel    
  column_list = None,                              
# optional: Ausschlussliste — alle Spalten außer diesen landen im Ziel
  except_column_list = None,                       
# optional: "1" (nur aktueller Stand), "2" (volle Historie) oder "bitemporal"    
  stored_as_scd_type = "1",                        
# optional, nur SCD Typ 2: nur Änderungen dieser Spalten erzeugen neue Version
  track_history_column_list = None,                
# optional, nur SCD Typ 2: alle Spalten AUSSER diesen erzeugen neue Version
  track_history_except_column_list = None,         
# optional: eigener Flow-/Checkpoint-Name, Default = Wert von target    
  name = None,                                     
# optional: True = einmaliger Lauf (Backfill/Seed), läuft nur bei Full Refresh erneut
  once = False                                     
)
```

**Gegenseitig ausschließende Parameterpaare** (jeweils nur einer der beiden gleichzeitig angeben): `column_list`/`except_column_list`, 

`track_history_column_list`/`track_history_except_column_list`, `ignore_null_updates_column_list`/`ignore_null_updates_except_column_list`. 

Ebenfalls unvereinbar: 

`columns_to_update` mit `ignore_null_updates*`, 

`system_sequence_by`/`stored_as_scd_type="bitemporal"` nur zusammen mit- statt anstelle von SCD Typ 2.

### 1.2 Vollständige Syntax von `AUTO CDC ... INTO` (SQL, alle Klauseln im Überblick)

SQL-Gegenstück zu Abschnitt 1.1 — eckige Klammern `[...]` markieren optionale Klauseln, `{a | b}` eine Wahlmöglichkeit:

```sql
CREATE OR REFRESH STREAMING TABLE table_name;   -- Zieltabelle muss vorher als Streaming Table angelegt sein

CREATE FLOW flow_name AS AUTO CDC [ONCE] INTO table_name
  -- flow_name: Name des Flows (= Checkpoint-Identität, Abschnitt 5 in 01 Flows.md)
  -- ONCE optional: einmaliger Insert/Backfill statt fortlaufendem Flow
FROM source
  -- Pflicht: CDC-Quelle; muss eine Streaming-Quelle sein, z. B. stream(cdc_data.users)
KEYS (keys)
  -- Pflicht: Spalte(n), die eine Zeile eindeutig identifizieren (mehrere = zusammengesetzter Key, Abschnitt 10.8)
[IGNORE NULL UPDATES [ON {columnList | * EXCEPT (exceptColumnList)}]]
  -- optional: null in einem Update überschreibt NICHT den Zielwert;
  -- ohne ON für alle Spalten, mit ON nur/außer den genannten Spalten
[APPLY AS DELETE WHEN condition]
  -- optional: Bedingung, wann ein Event als DELETE statt Upsert behandelt wird
[APPLY AS TRUNCATE WHEN condition]
  -- Für SCD TYPE 1: Bedingung, wann ein Event die ganze Zieltabelle leert
SEQUENCE BY orderByColumn
  -- Pflicht: legt fest, welches Event pro Key gewinnt — höchster Wert gewinnt
[SYSTEM SEQUENCE BY systemOrderByColumn]
  -- Für STORED AS BITEMPORAL: zweite Sequenzspalte "wann wusste das System davon"
[COLUMNS {columnList | * EXCEPT (exceptColumnList)}]
  -- optional: Einschluss- oder Ausschlussliste der Zielspalten, Default = alle Spalten (Abschnitt 4.1, 10.8)
[STORED AS {SCD TYPE 1 | SCD TYPE 2 | BITEMPORAL}]
  -- optional: Speichermodus, Default SCD TYPE 1 (Abschnitt 2, 10.6)
[TRACK HISTORY ON {columnList | * EXCEPT (exceptColumnList)}]
  -- optional, nur bei SCD TYPE 2: welche Spaltenänderungen eine neue Version erzeugen, Default = alle Spalten (Abschnitt 4.3, 10.8)
[COLUMNS TO UPDATE columnName]
  -- optional: Quellspalte, die pro Change-Datensatz die zu aktualisierenden Zielspalten als Array nennt (Abschnitt 10.5)
```

**Gegenseitig ausschließende Klauseln:** `COLUMNS TO UPDATE` nicht mit `IGNORE NULL UPDATES` kombinierbar; `APPLY AS TRUNCATE WHEN` nur bei `STORED AS SCD TYPE 1` zulässig (nicht bei Typ 2/bitemporal); `SYSTEM SEQUENCE BY` gehört ausschließlich zu `STORED AS BITEMPORAL` und schließt `STORED AS SCD TYPE 2` aus.

## 2. Slowly Changing Dimensions (SCD): Typ 1 vs. Typ 2

- **SCD Typ 1:** nur **aktueller Zustand** — überschreibt alte mit neuen Daten, keine Historie. Einsatz: nur aktueller Stand nötig, inkrementelle statt volle MV-Neuberechnung, stabile Surrogate Keys für Joins.
- **SCD Typ 2:** **vollständige Historie** — mehrere Versionen über Zeit, Metadaten-Zeitstempel (`__START_AT`/`__END_AT`); aktive Zeile hat `__END_AT = NULL`. Einsatz: Auditierbarkeit/Regulatorik, Kundenanalyse über Zeit, Point-in-Time-Reporting, Trendvergleiche.

| Operation | SCD Typ 1 | SCD Typ 2 |
|---|---|---|
| **INSERT** | neuer Datensatz eingefügt | neue Zeile als erste aktive Version (`__START_AT` gesetzt, `__END_AT=NULL`) |
| **UPDATE** | bestehender Datensatz direkt überschrieben, alter Wert weg | alte aktive Version geschlossen (`__END_AT`=Sequenzwert), neue aktive Version eingefügt (`__END_AT=NULL`); beide Zeilen bleiben |
| **DELETE** | Datensatz entfernt (via `APPLY AS DELETE WHEN`) | aktive Version geschlossen, keine neue aktive Zeile — Datensatz in keiner aktiven Zeile mehr |

- Klausel: `STORED AS SCD TYPE 1`/`STORED AS SCD TYPE 2` (SQL) bzw. `stored_as_scd_type` (Python).
- **Default:** `AUTO CDC` speichert als **SCD Typ 1**, wenn `STORED AS` fehlt.

## 3. Sequenzierung

### 3.1 Was ist Sequenzierung?

`SEQUENCE BY`/`sequence_by` legt die **logische** Reihenfolge der CDC-Ereignisse fest — also welches Event für einen bestimmten Key das "neuere" ist. Das ist etwas anderes als die **physische** Ankunftsreihenfolge in der Pipeline: Events können verspätet, mehrfach oder außer der Reihe eintreffen (Netzwerk-Retries, parallele Producer, wiederholte Kafka-Batches). Ohne `SEQUENCE BY` wüsste `AUTO CDC` nicht, welches von zwei Change-Events für denselben Key gewinnen soll, und würde einfach das zuletzt physisch angekommene übernehmen — das kann ein veraltetes Update sein.

`AUTO CDC` löst das, indem es pro Key **nicht** das zuletzt angekommene, sondern das Event mit dem **höchsten Sequenzwert** gewinnen lässt — unabhängig von der Ankunftsreihenfolge:

```
-- Zwei Update-Events für denselben Key (userId = 125):
-- Event A: sequenceNum = 6, city = 'Guadalajara'   -- kommt in der Pipeline ZUERST an
-- Event B: sequenceNum = 5, city = 'Mexicali'      -- kommt DANACH an, ist aber inhaltlich älter

-- Ohne Sequenzierung ("letztes Ankommen gewinnt"): Mexicali würde Guadalajara überschreiben -> falsch
-- Mit SEQUENCE BY sequenceNum ("höchster Wert gewinnt"): Guadalajara bleibt stehen -> richtig
```

```sql
SEQUENCE BY sequenceNum
```
```python
sequence_by = "sequenceNum"
```

Das vollständige, durchgerechnete Beispiel mit genau diesem Fall (User 125, nicht-chronologisch eintreffende `sequenceNum`-Werte 5 und 6) steht in Abschnitt 4.1. Praktisch ist `sequence_by` meist eine Zeitstempel- oder Versionsspalte aus der Quelle (z. B. `updated_at`, ein Commit-Zeitstempel oder eine monoton steigende Change-Sequenznummer) — **nicht** die Systemzeit der Pipeline-Verarbeitung selbst. Die Spalte muss einen sortierbaren Datentyp haben; `NULL`-Sequenzwerte werden nicht unterstützt (Abschnitt 6).

**Abgrenzung zu `SYSTEM SEQUENCE BY`:** Normales `SEQUENCE BY` sequenziert nach einer einzigen (Business-)Zeitachse. Bei bitemporalen Zieltabellen kommt zusätzlich `SYSTEM SEQUENCE BY` als zweite, unabhängige Sequenzierungs-Dimension hinzu (wann das System das Ereignis erfuhr, statt wann es geschah) — siehe Abschnitt 10.6.

### 3.2 Sequenzierung nach mehreren Spalten

`STRUCT` — erst nach erstem Feld, bei Gleichstand nach zweitem usw.:

```sql
SEQUENCE BY STRUCT(timestamp_col, id_col)
```

```python
sequence_by = struct("timestamp_col", "id_col")
```

## 4. `AUTO CDC`-Beispiele: SCD Typ 1 und Typ 2

Beispieldaten (Inserts, ein Delete, Updates, teils nicht-chronologisch):

| userId | name | city | operation | sequenceNum |
|---|---|---|---|---|
| 124 | Raul | Oaxaca | INSERT | 1 |
| 123 | Isabel | Monterrey | INSERT | 1 |
| 125 | Mercedes | Tijuana | INSERT | 2 |
| 126 | Lily | Cancun | INSERT | 2 |
| 123 | null | null | DELETE | 6 |
| 125 | Mercedes | Guadalajara | UPDATE | 6 |
| 125 | Mercedes | Mexicali | UPDATE | 5 |
| 123 | Isabel | Chihuahua | UPDATE | 5 |

### 4.1 SCD Typ 1 verarbeiten

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, expr

@dp.view
def users():
  return spark.readStream.table("main.cdc_tutorial.users_cdf")

dp.create_streaming_table("users_current")

dp.create_auto_cdc_flow(
  target = "users_current",
  source = "users",
  keys = ["userId"],
  sequence_by = col("sequenceNum"),
  apply_as_deletes = expr("operation = 'DELETE'"),
  apply_as_truncates = expr("operation = 'TRUNCATE'"),
  except_column_list = ["operation", "sequenceNum"],
  stored_as_scd_type = 1
)
```

```sql
CREATE OR REFRESH STREAMING TABLE users_current;

CREATE FLOW apply_cdc AS AUTO CDC INTO
  users_current
FROM
  stream(main.cdc_tutorial.users_cdf)
KEYS
  (userId)
APPLY AS DELETE WHEN
  operation = "DELETE"
APPLY AS TRUNCATE WHEN
  operation = "TRUNCATE"
SEQUENCE BY
  sequenceNum
COLUMNS * EXCEPT
  (operation, sequenceNum)
STORED AS
  SCD TYPE 1;
```

**Ergebnis:**

| userId | name | city |
|---|---|---|
| 124 | Raul | Oaxaca |
| 125 | Mercedes | Guadalajara |
| 126 | Lily | Cancun |

- Nutzer 123 (Isabel) gelöscht. Nutzer 125 zeigt nur neueste Stadt (Guadalajara, `sequenceNum=6`) — früheres `UPDATE` bei `sequenceNum=5` verworfen (traf nicht-chronologisch nach dem 6er-Update ein).
- `APPLY AS DELETE WHEN`/`APPLY AS TRUNCATE WHEN` optional. `TRUNCATE`-Event leert Tabelle zum Sequenzwert vollständig.

### 4.2 SCD Typ 2 verarbeiten

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, expr

@dp.view
def users():
  return spark.readStream.table("main.cdc_tutorial.users_cdf")

dp.create_streaming_table("users_history")

dp.create_auto_cdc_flow(
  target = "users_history",
  source = "users",
  keys = ["userId"],
  sequence_by = col("sequenceNum"),
  apply_as_deletes = expr("operation = 'DELETE'"),
  except_column_list = ["operation", "sequenceNum"],
  stored_as_scd_type = "2"
)
```

```sql
CREATE OR REFRESH STREAMING TABLE users_history;

CREATE FLOW apply_cdc AS AUTO CDC INTO
  users_history
FROM
  stream(main.cdc_tutorial.users_cdf)
KEYS
  (userId)
APPLY AS DELETE WHEN
  operation = "DELETE"
SEQUENCE BY
  sequenceNum
COLUMNS * EXCEPT
  (operation, sequenceNum)
STORED AS
  SCD TYPE 2;
```

**Ergebnis:**

| userId | name | city | __START_AT | __END_AT |
|---|---|---|---|---|
| 123 | Isabel | Monterrey | 1 | 5 |
| 123 | Isabel | Chihuahua | 5 | 6 |
| 124 | Raul | Oaxaca | 1 | null |
| 125 | Mercedes | Tijuana | 2 | 5 |
| 125 | Mercedes | Mexicali | 5 | 6 |
| 125 | Mercedes | Guadalajara | 6 | null |
| 126 | Lily | Cancun | 2 | null |

- Nutzer 123: zwei Versionen (endet Sequenz 6 durch Löschung). `__END_AT = null` = aktuell aktiv.

### 4.3 Spaltenteilmenge mit SCD Typ 2 verfolgen (`TRACK HISTORY`)

- Standard: jede Spaltenwertänderung → neue Version. Ausgeschlossene Spaltenmenge: Änderung aktualisiert aktuelle Version in-place, kein neuer Historieneintrag.

```python
dp.create_auto_cdc_flow(
  target = "users_history",
  source = "users",
  keys = ["userId"],
  sequence_by = col("sequenceNum"),
  apply_as_deletes = expr("operation = 'DELETE'"),
  except_column_list = ["operation", "sequenceNum"],
  stored_as_scd_type = "2",
  track_history_except_column_list = ["city"]
)
```

```sql
CREATE FLOW apply_cdc AS AUTO CDC INTO
  users_history
FROM
  stream(main.cdc_tutorial.users_cdf)
KEYS
  (userId)
APPLY AS DELETE WHEN
  operation = "DELETE"
SEQUENCE BY
  sequenceNum
COLUMNS * EXCEPT (operation, sequenceNum)
STORED AS SCD TYPE 2
TRACK HISTORY ON * EXCEPT (city)
```

- Ergebnis: `city`-Änderungen überschreiben die aktuelle Zeile statt neue Version anzulegen (da nicht verfolgt).

## 5. `AUTO CDC FROM SNAPSHOT`-Beispiele

### Vollständige Signatur von `create_auto_cdc_from_snapshot_flow()` (alle Parameter im Überblick)

Nur die ersten drei Parameter sind Pflicht:

```python
from pyspark import pipelines as dp

dp.create_auto_cdc_from_snapshot_flow(
  target = "<target-table>",               # Pflicht: Zieltabelle, vorher per create_streaming_table() angelegt
  source = Any,                            # Pflicht: Tabellen-/View-Name ODER Lambda-Funktion, die (DataFrame, Version) liefert (Abschnitt 5.2)
  keys = ["key1", "key2", "keyN"],          # Pflicht: Spalte(n), die eine Zeile eindeutig identifizieren (mehrere = zusammengesetzter Key)
  stored_as_scd_type = "1",                # optional: "1" (nur aktueller Stand, Default) oder "2" (volle Historie mit __START_AT/__END_AT)
  track_history_column_list = None,        # optional, nur SCD Typ 2: Einschlussliste — nur Änderungen dieser Spalten erzeugen neue Version (Abschnitt 5.1a)
  track_history_except_column_list = None  # optional, nur SCD Typ 2: Ausschlussliste — alle Spalten AUSSER diesen erzeugen neue Version (Abschnitt 5.1a)
)
```

**Auffällig im Vergleich zu `create_auto_cdc_flow()` (Abschnitt 1.1):** Kein `sequence_by`-Parameter — die Reihenfolge ergibt sich hier nicht aus einer Sequenzspalte in den Daten, sondern daraus, dass die Runtime Snapshots strikt **aufsteigend nach ihrer Versionsnummer** verarbeitet (Abschnitt 5.2). Ebenso fehlen `apply_as_deletes`/`apply_as_truncates` und `ignore_null_updates*` — Inserts/Updates/Deletes werden automatisch durch den **Vergleich zweier aufeinanderfolgender Snapshots** erkannt, nicht durch explizite Change-Event-Flags wie bei `AUTO CDC`. Kein SQL-Äquivalent: nur Python (Abschnitt 6).

### 5.1 Snapshots nach Pipeline-Ingestion-Zeit verarbeiten

Bei regelmäßigen, geordnet eintreffenden Snapshots, Pipeline-Lauf-Zeitstempel zur Versionierung. Jeder Pipeline-Lauf liest neuen Snapshot (Delta, Cloud-Storage-Dateien, JDBC):

```python
# Option A: aus einer Delta-Tabelle lesen
@dp.view(name="source")
def source():
  return spark.read.table("main.cdc_tutorial.snapshot")

# Option B: aus Cloud-Storage lesen
@dp.view(name="source")
def source():
  return spark.read.format("csv").option("header", True).load("<snapshot-path>")

# Option C: via JDBC lesen (nur Classic Compute)
@dp.view(name="source")
def source():
  return (spark.read
    .format("jdbc")
    .option("url", "<jdbc-url>")
    .option("dbtable", "<table-name>")
    .option("user", "<username>")
    .option("password", "<password>")
    .load())
```

```python
dp.create_streaming_table("target")

dp.create_auto_cdc_from_snapshot_flow(
  target = "target",
  source = "source",
  keys = ["userId"],
  stored_as_scd_type = 2
)
```

- Ergebnis nach erstem Lauf: alle Datensätze als aktive Zeilen (`__START_AT=0`, `__END_AT=null`). SCD Typ 1 (`stored_as_scd_type=1`): keine `__START_AT`/`__END_AT`-Spalten, nur aktueller Stand.
- Beim nächsten Lauf: neuer Snapshot vs. vorheriger → erkennt gelöschte/aktualisierte/neu eingefügte Datensätze, erzeugt internen Change Feed, verarbeitet via `AUTO CDC`.

### 5.1a Historie-Teilmenge bei Snapshot-CDC (`track_history_column_list`/`track_history_except_column_list`)

Gleiches Prinzip wie bei `AUTO CDC` (Abschnitt 4.3) — nur bestimmte Spaltenänderungen sollen bei SCD Typ 2 eine neue Version erzeugen. Nur Python, da `AUTO CDC FROM SNAPSHOT` keine SQL-Schnittstelle hat (Abschnitt 6):

```python
# Ausschlussliste: city-Änderungen aktualisieren die aktuelle Version in-place, keine neue Historienzeile
dp.create_auto_cdc_from_snapshot_flow(
  target = "target",
  source = "source",
  keys = ["userId"],
  stored_as_scd_type = 2,
  track_history_except_column_list = ["city"]
)

# Einschlussliste (Gegenstück): nur name-Änderungen erzeugen eine neue Version, alle anderen Spalten nicht
dp.create_auto_cdc_from_snapshot_flow(
  target = "target",
  source = "source",
  keys = ["userId"],
  stored_as_scd_type = 2,
  track_history_column_list = ["name"]
)
```

### 5.2 Snapshots über Versions-Funktionen verarbeiten

Bei explizitem Kontrollbedarf (mehrere gleichzeitig eintreffende/nicht-geordnete Snapshots). Python-Funktion legt fest, welcher Snapshot als nächstes + Versionsnummer. API verarbeitet stets aufsteigend; nicht-geordnet eintreffender Snapshot wird übersprungen; keine neuen Snapshots → `None` → keine Verarbeitung.

```python
from pyspark import pipelines as dp
from typing import Optional, Tuple
from pyspark.sql import DataFrame

def next_snapshot_and_version(latest_snapshot_version: Optional[int]) -> Optional[Tuple[DataFrame, int]]:
  snapshot_dir = "/Volumes/main/cdc_tutorial/snapshots/"
  files = dbutils.fs.ls(snapshot_dir)
  snapshot_files = [f.name for f in files if f.name.startswith("snapshot_") and f.name.endswith(".csv")]
  snapshot_versions = sorted(
    int(f.replace("snapshot_", "").replace(".csv", "")) for f in snapshot_files
  )

  if latest_snapshot_version is None:
    next_version = snapshot_versions[0] if snapshot_versions else None
  else:
    later = [v for v in snapshot_versions if v > latest_snapshot_version]
    next_version = later[0] if later else None

  if next_version is None:
    return None

  snapshot_path = f"{snapshot_dir}snapshot_{next_version}.csv"
  df = spark.read.format("csv").option("header", True).load(snapshot_path)
  return (df, next_version)

dp.create_streaming_table("main.cdc_tutorial.target_versioned")

dp.create_auto_cdc_from_snapshot_flow(
  target = "main.cdc_tutorial.target_versioned",
  source = next_snapshot_and_version,
  keys = ["userId"],
  stored_as_scd_type = 2
)
```

- SCD Typ 1 (`stored_as_scd_type=1`): Zieltabelle sieht wie jüngster Snapshot aus; nachgelagerte Queries können über internen Change Feed nur geänderte Datensätze verarbeiten.

## 6. Limitierungen der AUTO-CDC-APIs

- Sequenzierungsspalte muss sortierbaren Datentyp haben. `NULL`-Sequenzwerte nicht unterstützt.
- `AUTO CDC FROM SNAPSHOT` nur Python — keine SQL-Schnittstelle.
- Streamen aus dem Ziel eines `AUTO CDC`-Prozesses: aus dessen Change Data Feed lesen (Abschnitt 10).

## 7. `AUTO CDC INTO` vs. `MERGE INTO` — wann was?

**Problem mit manuellem `MERGE INTO`:** muss Inserts, Updates, Deletes, doppelte Events, verspätete Änderungen, Keys/Match-Bedingungen selbst korrekt behandeln:

```sql
MERGE INTO target_table AS t
USING source_stream AS s
ON t.id = s.id
WHEN MATCHED AND s.operation = 'UPDATE'
  THEN UPDATE SET *
WHEN MATCHED AND s.operation = 'DELETE'
  THEN DELETE
WHEN NOT MATCHED AND s.operation = 'INSERT'
  THEN INSERT *
```

- Wächst leicht zu brüchigem, schwer testbarem SQL-Block. `AUTO CDC INTO` deckt nicht-chronologische Events, SCD Typ 1/2, Metriken mit deutlich weniger Code ab.

**Wann `MERGE INTO` dennoch passender:**
- Frei kombinierbare `MATCHED`/`NOT MATCHED`-Logik, die nicht ins feste `AUTO CDC INTO`-Schema (Keys, Sequenzspalte, Delete-/Truncate-Bedingung) passt.
- Kein Pipeline-Kontext nötig — läuft direkt gegen Delta-Tabelle in jedem Notebook/Job/SQL-Warehouse, leichtgewichtiger für Ad-hoc-Korrekturen.
- Transparenz/Debugging — explizite SQL-Anweisung, `EXPLAIN`-fähig, in Transaktionen einbettbar; `AUTO CDC INTO` abstrahiert intern.
- Keine Zusatzinfrastruktur nötig — `AUTO CDC INTO` erfordert Streaming Table + Serverless/Pro/Advanced.

---

## 8. Change Data Feed (CDF) im CDC-Kontext

- CDF verfolgt **Row-Level-Änderungen zwischen Versionen** einer Delta- oder Iceberg-v3-Tabelle (inkl. Insert/Update/Delete-Metadaten). Delta-Lake-Feature auf **einer** Tabelle.
- **Stream-Modus:** Structured-Streaming-Job verarbeitet CDF fortlaufend als Micro-Batches ab letztem Checkpoint — mehrere Änderungen desselben Datensatzes im selben Batch: Logik muss aktuellsten Stand selbst auswählen.
- **Batch-Modus:** periodische Verarbeitung, Logik führt selbst High-Watermark (letzte verarbeitete Version/Zeitstempel).
- Anwendungsfälle: inkrementelle Silver-/Gold-Updates, MVs ohne teure Re-Aggregation, Propagierung von Löschungen durchs Lakehouse.

### 8.1 Abgrenzung: CDF vs. `AUTO CDC INTO`

- **`AUTO CDC INTO`** = **von außen nach innen** (Ingestion): nimmt Change-Records einer externen Quelle, wendet sie auf **eine** Ziel-Delta-Tabelle an.
- **CDF** = **von innen nach außen** (Propagation): "Was änderte sich seit Version X (inkl. Deletes)?" — unabhängig von der Ursache (`DELETE`, `MERGE`, `AUTO CDC INTO`-Flow). Passendes Werkzeug, um Löschungen durchs gesamte Lakehouse zu propagieren (z. B. DSGVO/CCPA von Bronze bis alle Gold-Tabellen).
- Kurz: `AUTO CDC INTO` bringt Änderungen an der Ingestion-Grenze **herein**, CDF trägt sie durchs Lakehouse **weiter**.

---

## 9. Externe RDBMS-Tabelle mit AUTO CDC replizieren (End-to-End-Muster)

Kombiniert einmaligen Voll-Kopie-Lauf (`once`-Flow) mit fortlaufender Change-Feed-Verarbeitung.

- **Voraussetzungen:** vollständiger Snapshot der Quelltabelle im Cloud-Speicher + fortlaufender Change Feed am selben Ort (z. B. Debezium, Kafka, Log-basiertes CDC).

### 9.1 Source Views einrichten

Zwei Streaming Views über Rohdaten — effizienter als Zwischenspeichern vor `AUTO CDC`:

```python
@dp.view()
def full_orders_snapshot():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.includeExistingFiles", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(orders_snapshot_path)
        .select("*")
    )

@dp.view()
def rdbms_orders_change_feed():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.includeExistingFiles", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(orders_cdc_path)
    )
```

```sql
CREATE OR REFRESH VIEW full_orders_snapshot
AS SELECT *
FROM STREAM read_files("${orders_snapshot_path}", "json", map(
  "cloudFiles.includeExistingFiles", "true",
  "cloudFiles.inferColumnTypes", "true"
));

CREATE OR REFRESH VIEW rdbms_orders_change_feed
AS SELECT *
FROM STREAM read_files("${orders_cdc_path}", "json", map(
  "cloudFiles.includeExistingFiles", "true",
  "cloudFiles.inferColumnTypes", "true"
));
```

### 9.2 Initiale Befüllung (Once Flow)

`AUTO CDC`-Flow mit `ONCE=TRUE` kopiert vollständigen RDBMS-Inhalt, ohne bei künftigen Updates erneut abzuspielen:

```python
from pyspark import pipelines as dp

dp.create_streaming_table("rdbms_orders")

dp.create_auto_cdc_flow(
  name = "initial_load_orders",
  once = True,
  target = "rdbms_orders",
  source = "full_orders_snapshot",
  keys = ["order_id"],
  sequence_by = "timestamp",
  stored_as_scd_type = "1"
)
```

```sql
CREATE OR REFRESH STREAMING TABLE rdbms_orders;

CREATE FLOW rdbms_orders_hydrate
AS AUTO CDC ONCE INTO rdbms_orders
FROM stream(full_orders_snapshot)
KEYS (order_id)
SEQUENCE BY timestamp
STORED AS SCD TYPE 1;
```

- **Gotcha:** Full Refresh der Streaming Table führt den `once`-Flow erneut aus — wurden Snapshot-Daten zwischenzeitlich entfernt → Datenverlust.

### 9.3 Fortlaufender Change Feed (Change Flow)

```python
dp.create_auto_cdc_flow(
  flow_name = "orders_incremental_cdc",
  target = "rdbms_orders",
  source = "rdbms_orders_change_feed",
  keys = ["order_id"],
  sequence_by = "timestamp",
  stored_as_scd_type = "1"
)
```

```sql
CREATE FLOW rdbms_orders_continuous
AS AUTO CDC INTO rdbms_orders
FROM stream(rdbms_orders_change_feed)
KEYS (order_id)
SEQUENCE BY timestamp
STORED AS SCD TYPE 1;
```

- Mehrere Change Flows für Korrekturen/verspätete Daten/alternative Feeds möglich — müssen Schema+Keys teilen. Flow-Ausführungsreihenfolge spielt für Endergebnis keine Rolle.

### 9.4 SCD-Ziel während einer Migration befüllen

Siehe Kapitel Flows (Backfill-Abschnitt) für `AUTO CDC ONCE` als Seed-Flow + cutover-sicherer Sequenzierung bei Legacy-SCD-Tabellen ohne verfügbaren Original-Change-Feed.

---

## 10. Fortgeschrittene AUTO-CDC-Themen

### 10.1 DML auf einer Ziel-Streaming-Table

- Nach Unity Catalog publiziert: DML (Insert, Update, Delete, Merge) auf `AUTO CDC ... INTO`-Zieltabellen möglich.
- DML, die Schema ändert: nicht unterstützt.
- Erfordert Shared-UC-Cluster oder SQL-Warehouse mit DBR 13.3 LTS+.
- Gestreamt von Quell-Streaming-Table mit solchen Änderungen: `skipChangeCommits`-Flag setzen (ignoriert löschende/ändernde Transaktionen); alternativ MV als Ziel.
- DML muss gültige `__START_AT`/`__END_AT` (SCD Typ 2) mitgeben:

```sql
INSERT INTO my_streaming_table (id, name, __START_AT, __END_AT) VALUES (123, 'John Doe', 5, NULL);
```

Umbenennen von `__START_AT`/`__END_AT` für nachgelagerte Anforderungen via View:

```sql
CREATE VIEW my_employees_view AS
SELECT *, __START_AT AS valid_from, __END_AT AS valid_to
FROM my_scd2_target_table;
```

### 10.2 Change Data Feed vom AUTO-CDC-Ziel lesen

- Ab **DBR 15.2**: CDF aus Streaming Table lesbar, die Ziel von `AUTO CDC`/`AUTO CDC FROM SNAPSHOT` ist — wie jede andere Delta-Tabelle. Voraussetzung: Ziel nach UC publiziert, lesende Pipeline ebenfalls 15.2+.
- Aktualisierter Datensatz: `_change_type` typischerweise `update_preimage`/`update_postimage`. Ändern Updates Primärschlüsselwerte: `insert`/`delete` (z. B. manuelles Update eines Key-Felds, oder SCD-Typ-2 bei geändertem `__start_at`).

| SCD-Typ | Primärschlüssel |
|---|---|
| SCD Typ 1 | `keys`-Parameter/`KEYS`-Klausel |
| SCD Typ 2 | `keys`/`KEYS` plus `coalesce(__START_AT, __END_AT)` |

### 10.3 Change Data Feed von einer Materialized View lesen (Beta)

- Nützlich für Replikation außerhalb Databricks oder Auditing/Reporting-Historie. MVs nutzen automatischen CDF (keine separate Aktivierung).
- Voraussetzungen: **DBR 18 LTS+** (Classic/Serverless/DBSQL); MV/erzeugende/lesende Pipeline auf `PREVIEW`-Channel; MV muss Row Tracking aktiviert haben (Serverless default an): `SHOW TBLPROPERTIES my_mv ('delta.enableRowTracking');`; Metadaten synchron — Pipeline-MVs: `pipelines.externalMetadata.enabled: "true"`; eigenständige MVs: einmalig `REPAIR TABLE my_mv SYNC METADATA;`.

```sql
CREATE OR REFRESH STREAMING TABLE sales
TBLPROPERTIES ('pipelines.channel' = 'preview')
  AS SELECT * FROM STREAM my_mv WITH (readChangeFeed=true)
```

- **Limitierungen:** CDF enthält unveränderte Zeilen bei vollständigem MV-Neuschreiben, konsolidiert nicht mehrere Updates zu einem Event. Nur Databricks kann den CDF einer MV abfragen (keine externen Delta/Iceberg-Clients). Innerhalb Pipelines nur aus **anderer** Pipeline lesbar (ebenfalls `PREVIEW`) — nicht aus der erzeugenden Pipeline selbst. Kein Vector-Search-Index aus MV.

### 10.4 Metriken zu verarbeiteten CDC-Datensätzen

Nur von `AUTO CDC`-Queries erfasst (nicht `AUTO CDC FROM SNAPSHOT`):

- `num_upserted_rows` — upgeserte Ausgabezeilen je Update.
- `num_deleted_rows` — gelöschte Ausgabezeilen je Update.
- `num_output_rows` (sonst üblich für Nicht-CDC-Flows) wird für `AUTO CDC` **nicht** erfasst.

### 10.5 Partielle Updates anwenden

- Sendet Quelle nur geänderte Spalten: `AUTO CDC` muss unterscheiden zwischen **fehlender** Spalte (Zielwert unverändert) und explizitem `null` (Zielwert überschreiben). Standard `IGNORE NULL UPDATES`: jedes `null` = "nicht aktualisieren".

| Methode | Einsatz wenn | Verhalten |
|---|---|---|
| `IGNORE NULL UPDATES ON columnList` | kleine feste Spaltenmenge soll `null` ignorieren | gelistete Spalten behalten Wert bei `null`; alle anderen wenden `null` an |
| `IGNORE NULL UPDATES ON * EXCEPT (exceptColumnList)` | die meisten Spalten sollen `null` ignorieren | gelistete Spalten wenden `null` an; alle anderen behalten Wert |
| `COLUMNS TO UPDATE` | jeder Change Record aktualisiert andere Spaltenmenge, ändert sich über Zeit | Quellspalte benennt je Record zu aktualisierende Spalten (inkl. explizitem `null`); nicht gelistete bleiben unverändert |

- `COLUMNS TO UPDATE` nicht kombinierbar mit `IGNORE NULL UPDATES`, nicht für bitemporale Tabellen.
- Faustregel: `COLUMNS TO UPDATE` wenn Produzent weiß, welche Spalten sich je Datensatz änderten und dies mitführen kann; `IGNORE NULL UPDATES ON` wenn Pipeline-Owner feste Spaltenmenge vorab kennt.

```python
dp.create_streaming_table("target")

dp.create_auto_cdc_flow(
  target = "target",
  source = "cdc_source",
  keys = ["id"],
  sequence_by = "sequenceNum",
  stored_as_scd_type = 1,
  columns_to_update = "columnsToUpdate"
)
```

```sql
CREATE OR REFRESH STREAMING TABLE target;

CREATE FLOW apply_cdc AS AUTO CDC INTO
  target
FROM
  stream(cdc_source)
KEYS
  (id)
SEQUENCE BY
  sequenceNum
STORED AS
  SCD TYPE 1
COLUMNS TO UPDATE
  columnsToUpdate;
```

### 10.6 Bitemporal AUTO CDC (Beta)

- SCD Typ 1/2 = unitemporal (eine Zeitdimension). **Bitemporal** erweitert SCD-Typ-2-Historie um zweite Dimension:
  - **Business Time:** wann das Ereignis stattfand.
  - **System Time:** wann das System das Ereignis erfasste.
- Aktivierung: `STORED AS BITEMPORAL` (SQL) / `stored_as_scd_type="bitemporal"` (Python), mit `SEQUENCE BY` (Business Time) und `SYSTEM SEQUENCE BY` (System Time). Zieltabelle ergänzt `__SYSTEM_START_AT`/`__SYSTEM_END_AT` neben `__START_AT`/`__END_AT`.

```python
from pyspark import pipelines as dp

dp.create_streaming_table(name="cdc_source")

@dp.append_flow(target="cdc_source", once=True)
def load_cdc_source():
  return spark.createDataFrame(
    [(1, "x10", "y10", 10, 100), (1, "x20", "y20", 20, 200)],
    schema="id INT, x STRING, y STRING, bt INT, st INT",
  )

dp.create_streaming_table(name="target_bitemporal")

dp.create_auto_cdc_flow(
  target = "target_bitemporal",
  source = "cdc_source",
  keys = ["id"],
  sequence_by = "bt",
  system_sequence_by = "st",
  stored_as_scd_type = "bitemporal"
)
```

```sql
CREATE OR REFRESH STREAMING TABLE cdc_source_sql;

CREATE FLOW cdc_source_sql AS INSERT INTO ONCE
  cdc_source_sql BY NAME
SELECT * FROM VALUES
  (1, 'x10', 'y10', 10, 100),
  (1, 'x20', 'y20', 20, 200)
  AS t(id, x, y, bt, st);

CREATE OR REFRESH STREAMING TABLE target_bitemporal_sql;

CREATE FLOW target_bitemporal_sql AS AUTO CDC INTO
  target_bitemporal_sql
FROM
  stream(cdc_source_sql)
KEYS
  (id)
SEQUENCE BY
  bt
SYSTEM SEQUENCE BY
  st
STORED AS
  BITEMPORAL;
```

| Spalte | Bedeutung |
|---|---|
| `__START_AT` | Business Time, ab der Zeile gültig wurde |
| `__END_AT` | Business Time, ab der Gültigkeit endet (`null` = unbegrenzt) |
| `__SYSTEM_START_AT` | System Time, ab der Daten + Business-Time-Intervall als wahr bekannt sind |
| `__SYSTEM_END_AT` | System Time, ab der Daten als ungültig bekannt sind (`null` = unbegrenzt wahr bekannt) |

- System handhabt Events beliebiger Reihenfolge über beide Zeitleisten. Früheres Event als bereits verarbeitete: System korrigiert Historie rückwirkend statt nur anzuhängen — bei Update bis zu drei Zeilen (geschlossene alte Systemsicht, korrigierte Business-Historie, neue aktive Version). Delete erzeugt keine Ersatzzeile, dokumentiert Ende + Kenntnisnahme-Zeitpunkt.
- **Beispiel aus Doku:** Hedgefonds liest Aktienkurse. Acme-Corp-Kurs ändert sich am 1. Januar, wird aber erst am 5. Januar eingelesen. Bitemporal beantwortet: tatsächlicher Kurs am 1. Januar (Business Time)? Vom System am 3. Januar angenommener Kurs bei der Trading-Entscheidung (System Time)? Nützlich für Auditing/Regulatorik/Finanzentscheidungen.

### 10.7 Datenobjekte für CDC-Verarbeitung (Hive Metastore)

- Zieltabelle im Hive Metastore deklariert → zwei Strukturen: View mit Zieltabellennamen + interne Backing Table (`__apply_changes_storage_<zieltabellenname>`) zur CDC-Verwaltung.
- Abgefragt wird die View — Backing Table nicht direkt modifizieren. Gilt nur für `AUTO CDC` (nicht `AUTO CDC FROM SNAPSHOT`), nur Hive Metastore (nicht Unity Catalog).

### 10.8 Restliche `AUTO CDC`-Parameter mit Beispiel

Vier Parameter/Klauseln, die in den bisherigen Beispielen dieses Kapitels noch nicht eigenständig vorkamen:

**`ignore_null_updates` — pauschal statt spaltenweise:** `null` in einem Update-Datensatz behält für **alle** Spalten den bestehenden Zielwert, statt ihn zu überschreiben (Standard: `null` überschreibt).

```python
dp.create_auto_cdc_flow(
  target = "target", source = "cdc_source", keys = ["id"], sequence_by = "sequenceNum",
  ignore_null_updates = True
)
```
```sql
CREATE FLOW apply_cdc AS AUTO CDC INTO target
FROM stream(cdc_source)
KEYS (id)
IGNORE NULL UPDATES
SEQUENCE BY sequenceNum;
```

**`ignore_null_updates_column_list` / `IGNORE NULL UPDATES ON columnList`** — nur die gelisteten Spalten behalten bei `null` ihren bestehenden Wert, alle anderen wenden `null` an:

```python
dp.create_auto_cdc_flow(
  target = "target", source = "cdc_source", keys = ["id"], sequence_by = "sequenceNum",
  ignore_null_updates_column_list = ["email", "phone"]
)
```
```sql
IGNORE NULL UPDATES ON (email, phone)
```

**`ignore_null_updates_except_column_list` / `IGNORE NULL UPDATES ON * EXCEPT (...)`** — Kehrseite: alle Spalten außer den gelisteten behalten bei `null` ihren bestehenden Wert:

```python
dp.create_auto_cdc_flow(
  target = "target", source = "cdc_source", keys = ["id"], sequence_by = "sequenceNum",
  ignore_null_updates_except_column_list = ["status"]
)
```
```sql
IGNORE NULL UPDATES ON * EXCEPT (status)
```

**`column_list` / `COLUMNS (...)` — Einschlussliste** (in Abschnitt 4 wurde bisher nur die Ausschlussliste `except_column_list`/`COLUMNS * EXCEPT` gezeigt):

```python
dp.create_auto_cdc_flow(
  target = "users_current", source = "users", keys = ["userId"], sequence_by = "sequenceNum",
  column_list = ["userId", "name", "city"]   # nur diese drei Spalten landen im Ziel
)
```
```sql
COLUMNS (userId, name, city)
```

**`track_history_column_list` / `TRACK HISTORY ON (...)` — Einschlussliste** (Gegenstück zur Ausschlussliste aus Abschnitt 4.3):

```python
dp.create_auto_cdc_flow(
  target = "users_history", source = "users", keys = ["userId"], sequence_by = "sequenceNum",
  stored_as_scd_type = "2",
  track_history_column_list = ["name", "city"]   # nur Änderungen dieser Spalten erzeugen eine neue Version
)
```
```sql
TRACK HISTORY ON (name, city)
```

**Zusammengesetzte Keys** — `keys`/`KEYS` akzeptiert mehrere Spalten, wenn eine einzelne Spalte eine Zeile nicht eindeutig identifiziert (z. B. Kombination aus Region + Kunden-ID):

```python
dp.create_auto_cdc_flow(
  target = "regional_customers", source = "cdc_source",
  keys = ["region", "customer_id"], sequence_by = "sequenceNum"
)
```
```sql
KEYS (region, customer_id)
```

**`name` — eigener Flow-Name, unabhängig vom Zieltabellennamen:** Python-Default ist sonst der Wert von `target`; in SQL entspricht das direkt dem `flow_name` nach `CREATE FLOW`:

```python
dp.create_auto_cdc_flow(
  name = "users_cdc_flow",   # eigener Flow-/Checkpoint-Name statt Default "users_current"
  target = "users_current",
  source = "users", keys = ["userId"], sequence_by = "sequenceNum"
)
```
```sql
CREATE FLOW users_cdc_flow AS AUTO CDC INTO users_current
FROM stream(users) KEYS (userId) SEQUENCE BY sequenceNum;
```

**Stand:** 2026-09-14.
