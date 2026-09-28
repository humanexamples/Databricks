# Die AUTO CDC APIs: Change Data Capture mit Pipelines — Referenz

Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/cdc`, vollständig als Rohtext abgerufen) und die inhaltlich übereinstimmende AWS-Seite (`docs.databricks.com/aws/en/ldp/cdc`).

## Abschnittsübersicht

1. [Überblick: Wann `AUTO CDC`, wann `AUTO CDC FROM SNAPSHOT`](#ueberblick)
2. [Voraussetzungen](#voraussetzungen)
3. [Wie `AUTO CDC` funktioniert](#wie-auto-cdc)
4. [Wie `AUTO CDC FROM SNAPSHOT` funktioniert](#wie-snapshot)
5. [Sequenzierung nach mehreren Spalten](#mehrspalten-sequenz)
6. [`AUTO CDC`-Beispiele: SCD Typ 1 und Typ 2](#auto-cdc-beispiele)
7. [`AUTO CDC FROM SNAPSHOT`-Beispiele](#snapshot-beispiele)
8. [Limitierungen](#limitierungen)
9. [`AUTO CDC INTO` vs. `MERGE INTO` — wann was?](#auto-cdc-vs-merge)
10. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick: Wann `AUTO CDC`, wann `AUTO CDC FROM SNAPSHOT`</a>

**Hinweis:** Die `AUTO CDC`-APIs ersetzen die älteren `APPLY CHANGES`-APIs und haben dieselbe Syntax. `APPLY CHANGES` ist weiterhin verfügbar, Databricks empfiehlt jedoch, stattdessen `AUTO CDC` zu verwenden.

Welche API verwendet wird, hängt von der Quelle der Änderungsdaten ab:

- **`AUTO CDC`:** Einsatz, wenn die Quelldatenbank über einen aktivierten CDC-Feed verfügt. Verarbeitet Änderungen aus einem Change Data Feed (CDF). Unterstützt sowohl die Pipeline-SQL- als auch die Python-Schnittstelle.

  Anweisungen: `AUTO CDC ... INTO`-Anweisung (SQL) bzw. die `create_auto_cdc_flow()`-Funktion (Python)

- **`AUTO CDC FROM SNAPSHOT`:** Einsatz, wenn CDC auf der Quelldatenbank nicht aktiviert ist und nur Snapshots verfügbar sind. Vergleicht Snapshots, um Änderungen zu ermitteln, und verarbeitet sie anschließend. Nur in der Python-Schnittstelle unterstützt.  `AUTO CDC FROM SNAPSHOT` ermittelt Änderungen in Quelldaten durch Vergleich in-order eintreffender Snapshots.

  Anweisungen: `AUTO CDC FROM SNAPSHOT` anschliessend create_auto_cdc_from_snapshot_flow()

  (Für `AUTO CDC FROM SNAPSHOT` bei Datei-basierten Snapshots (z. B. wachsende/überschriebene Dateien) siehe ergänzend `Lakeflow Connect/Lakeflow Connect Standard Connectors/Working with Files/_fileIngestionScenarios.md` Abschnitte 1c und 5c)

Beide APIs unterstützen Updates über SCD Typ 1 und Typ 2:

- **SCD Typ 1** aktualisiert Datensätze direkt — keine Historie für aktualisierte Datensätze.
- **SCD Typ 2** behält eine Historie der Datensätze bei, entweder für alle Updates oder für Updates einer festgelegten Spaltenmenge.

  Für den konzeptionellen Vergleich beider Typen (Verhalten bei Insert/Update/Delete, Entscheidungskriterien) siehe `SCD Type 1 vs Type 2.md` in diesem Ordner.

Für `AUTO CDC` allein steht zusätzlich Bitemporal Storage zur Verfügung, das SCD-Typ-2-Historie um eine zweite Zeitdimension (Business Time und System Time) erweitert (Beta). `AUTO CDC` unterstützt außerdem partielle Updates, bei denen ein Change Record nur eine Teilmenge der Spalten aktualisiert.

**Die `AUTO CDC`-APIs werden von Apache Spark Declarative Pipelines nicht unterstützt.**

Zur Nutzung der CDC-APIs muss die Pipeline für 

- **Serverless Lakeflow Pipelines** oder 
- die Lakeflow-Pipelines-Editionen `Pro` bzw. `Advanced` konfiguriert sein.

## <a id="mehrspalten-sequenz">5. Sequenzierung nach mehreren Spalten</a>

Um nach mehreren Spalten zu sequenzieren (z. B. ein Zeitstempel plus eine ID zum Auflösen von Gleichständen), wird ein `STRUCT` verwendet. Die API ordnet zuerst nach dem ersten Feld, bei Gleichstand nach dem zweiten Feld usw.

```sql
SEQUENCE BY STRUCT(timestamp_col, id_col)
```

```python
sequence_by = struct("timestamp_col", "id_col")
```

## <a id="auto-cdc-beispiele">6. `AUTO CDC`-Beispiele: SCD Typ 1 und Typ 2</a>

Die folgenden Beispiele demonstrieren SCD-Typ-1- und -Typ-2-Verarbeitung anhand einer Change-Data-Feed-Quelle. Die Beispieldaten legen neue Nutzerdatensätze an, löschen einen Nutzerdatensatz und aktualisieren Nutzerdatensätze. Im SCD-Typ-1-Beispiel treffen die letzten `UPDATE`-Operationen verspätet ein und werden aus der Zieltabelle verworfen — demonstriert die Behandlung nicht-geordnet eintreffender Events.

Eingabedaten:

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

Wird die letzte Zeile der Beispieldaten-Generierung einkommentiert, wird zusätzlich folgender Datensatz eingefügt, der die Tabelle bei `sequenceNum=3` leert (`TRUNCATE`):

| userId | name | city | operation | sequenceNum |
|---|---|---|---|---|
| null | null | null | TRUNCATE | 3 |

**Hinweis laut Doku:** Alle folgenden Beispiele enthalten Optionen, um sowohl `DELETE`- als auch `TRUNCATE`-Operationen anzugeben, aber beide sind optional.

### Beispieldaten anlegen

Dieser Code ist nicht Teil einer Pipeline-Definition — er wird aus dem Exploration-Ordner der Pipeline ausgeführt:

```sql
CREATE SCHEMA IF NOT EXISTS main.cdc_tutorial;

CREATE TABLE main.cdc_tutorial.users_cdf
AS SELECT
  col1 AS userId,
  col2 AS name,
  col3 AS city,
  col4 AS operation,
  col5 AS sequenceNum
FROM (
  VALUES
  -- Initial load.
  (124, "Raul",     "Oaxaca",      "INSERT", 1),
  (123, "Isabel",   "Monterrey",   "INSERT", 1),
  -- New users.
  (125, "Mercedes", "Tijuana",     "INSERT", 2),
  (126, "Lily",     "Cancun",      "INSERT", 2),
  -- Isabel is removed from the system and Mercedes moved to Guadalajara.
  (123, null,       null,          "DELETE", 6),
  (125, "Mercedes", "Guadalajara", "UPDATE", 6),
  -- This batch of updates arrived out of order. The batch at sequenceNum 6 is the final state.
  (125, "Mercedes", "Mexicali",    "UPDATE", 5),
  (123, "Isabel",   "Chihuahua",   "UPDATE", 5)
  -- Uncomment to test TRUNCATE.
  -- ,(null, null,      null,          "TRUNCATE", 3)
);
```

### SCD Typ 1 verarbeiten

SCD Typ 1 behält nur die neueste Version jedes Datensatzes:

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

Nach Ausführung enthält die Zieltabelle:

| userId | name | city |
|---|---|---|
| 124 | Raul | Oaxaca |
| 125 | Mercedes | Guadalajara |
| 126 | Lily | Cancun |

Nutzer 123 (Isabel) wurde gelöscht und erscheint nicht. Nutzer 125 (Mercedes) zeigt nur die neueste Stadt (Guadalajara), da SCD Typ 1 frühere Werte überschreibt. Das frühere `UPDATE` bei `sequenceNum=5` wurde verworfen, weil ein späteres Update bei `sequenceNum=6` eintraf.

Mit einkommentiertem `TRUNCATE`-Datensatz wird die Tabelle bei `sequenceNum=3` geleert — Datensätze 124 und 126 fehlen dann, die Zieltabelle enthält nur:

| userId | name | city |
|---|---|---|
| 125 | Mercedes | Guadalajara |

### SCD Typ 2 verarbeiten

SCD Typ 2 bewahrt eine vollständige Änderungshistorie, indem für jede Version eines Datensatzes eine neue Zeile angelegt wird, mit `__START_AT`- und `__END_AT`-Spalten, die angeben, wann jede Version aktiv war:

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

Nach Ausführung enthält die Zieltabelle:

| userId | name | city | __START_AT | __END_AT |
|---|---|---|---|---|
| 123 | Isabel | Monterrey | 1 | 5 |
| 123 | Isabel | Chihuahua | 5 | 6 |
| 124 | Raul | Oaxaca | 1 | null |
| 125 | Mercedes | Tijuana | 2 | 5 |
| 125 | Mercedes | Mexicali | 5 | 6 |
| 125 | Mercedes | Guadalajara | 6 | null |
| 126 | Lily | Cancun | 2 | null |

Die Tabelle bewahrt die vollständige Historie. Nutzer 123 hat zwei Versionen (endet bei Sequenz 6 durch Löschung). Nutzer 125 hat drei Versionen mit den Stadt-Änderungen. Datensätze mit `__END_AT = null` sind aktuell aktiv.

### Spaltenteilmenge mit SCD Typ 2 verfolgen

Standardmäßig legt SCD Typ 2 bei jeder Wertänderung einer Spalte eine neue Version an. Eine Teilmenge von Spalten lässt sich festlegen, deren Verfolgung ausgeschlossen wird, sodass Änderungen an anderen Spalten die aktuelle Version stattdessen in-place aktualisieren, ohne einen neuen Historieneintrag zu erzeugen. Das folgende Beispiel schließt die Spalte `city` von der Historienverfolgung aus:

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
  stored_as_scd_type = "2",
  track_history_except_column_list = ["city"]
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
COLUMNS * EXCEPT (operation, sequenceNum)
STORED AS SCD TYPE 2
TRACK HISTORY ON * EXCEPT (city)
```

Da `city`-Änderungen nicht verfolgt werden, überschreiben Stadt-Updates die aktuelle Zeile statt eine neue Version anzulegen:

| userId | name | city | __START_AT | __END_AT |
|---|---|---|---|---|
| 123 | Isabel | Chihuahua | 1 | 6 |
| 124 | Raul | Oaxaca | 1 | null |
| 125 | Mercedes | Guadalajara | 2 | null |
| 126 | Lily | Cancun | 2 | null |

## <a id="snapshot-beispiele">7. `AUTO CDC FROM SNAPSHOT`-Beispiele</a>

### Beispiel: Snapshots nach Pipeline-Ingestion-Zeit verarbeiten

Einsatz, wenn Snapshots regelmäßig und in Reihenfolge eintreffen und sich auf den Pipeline-Lauf-Zeitstempel zur Versionierung verlassen lässt. Bei jedem Pipeline-Update wird ein neuer Snapshot eingelesen. Snapshots lassen sich aus mehreren Quelltypen lesen — Delta-Tabellen, Cloud-Storage-Dateien und JDBC-Verbindungen.

**Schritt 1 — Beispieldaten anlegen:**

```sql
CREATE SCHEMA IF NOT EXISTS main.cdc_tutorial;

CREATE TABLE main.cdc_tutorial.snapshot (
  userId INT,
  city STRING
);

INSERT INTO main.cdc_tutorial.snapshot VALUES
  (1, 'Oaxaca'), (2, 'Monterrey'), (3, 'Tijuana');
```

**Schritt 2 — `AUTO CDC FROM SNAPSHOT` ausführen.** Der Quelltyp für die Snapshot-View ist wählbar (der Beispielcode oben erzeugt eine Delta-Tabelle):

Option A — aus einer Delta-Tabelle lesen:

```python
from pyspark import pipelines as dp

@dp.view(name="source")
def source():
  return spark.read.table("main.cdc_tutorial.snapshot")
```

Option B — aus Cloud-Storage lesen:

```python
from pyspark import pipelines as dp

@dp.view(name="source")
def source():
  return spark.read.format("csv").option("header", True).load("<snapshot-path>")
```

Option C — via JDBC lesen (nur Classic Compute):

```python
from pyspark import pipelines as dp

@dp.view(name="source")
def source():
  return (spark.read
    .format("jdbc")
    .option("url", "<jdbc-url>")
    .option("dbtable", "<table-name>")
    .option("user", "<username>")
    .option("password", "<password>")
    .load()
  )
```

Für alle drei Optionen anschließend Zieltabelle und Flow anlegen:

```python
dp.create_streaming_table("target")

dp.create_auto_cdc_from_snapshot_flow(
  target = "target",
  source = "source",
  keys = ["userId"],
  stored_as_scd_type = 2
)
```

Nach dem ersten Pipeline-Lauf werden alle Datensätze als aktive Zeilen eingefügt:

| userId | city | __START_AT | __END_AT |
|---|---|---|---|
| 1 | Oaxaca | 0 | null |
| 2 | Monterrey | 0 | null |
| 3 | Tijuana | 0 | null |

**Hinweis:** Um stattdessen SCD Typ 1 zu verwenden und nur den aktuellen Stand zu behalten, wird `stored_as_scd_type=1` gesetzt — die Zieltabelle enthält dann keine `__START_AT`-/`__END_AT`-Spalten.

**Schritt 3 — neuen Snapshot simulieren und erneut ausführen:**

```sql
TRUNCATE TABLE main.cdc_tutorial.snapshot;

INSERT INTO main.cdc_tutorial.snapshot VALUES
  (2, 'Carmel'),
  (3, 'Los Angeles'),
  (4, 'Death Valley'),
  (6, 'Kings Canyon');
```

Beim erneuten Pipeline-Lauf vergleicht `AUTO CDC FROM SNAPSHOT` den neuen Snapshot mit dem vorherigen und erkennt, dass Nutzer 1 gelöscht, Nutzer 2 und 3 aktualisiert und Nutzer 4 und 6 neu eingefügt wurden. Daraus wird ein Change Feed erzeugt und über `AUTO CDC` die Ausgabetabelle erstellt.

Nach dem zweiten Lauf mit SCD Typ 2:

| userId | city | __START_AT | __END_AT |
|---|---|---|---|
| 1 | Oaxaca | 0 | 1 |
| 2 | Monterrey | 0 | 1 |
| 2 | Carmel | 1 | null |
| 3 | Tijuana | 0 | 1 |
| 3 | Los Angeles | 1 | null |
| 4 | Death Valley | 1 | null |
| 6 | Kings Canyon | 1 | null |

Nach dem zweiten Lauf mit SCD Typ 1 (nur aktueller Stand):

| userId | city |
|---|---|
| 2 | Carmel |
| 3 | Los Angeles |
| 4 | Death Valley |
| 6 | Kings Canyon |

### Beispiel: Snapshots über Versions-Funktionen verarbeiten

Einsatz, wenn explizite Kontrolle über die Snapshot-Reihenfolge benötigt wird — etwa wenn mehrere Snapshots gleichzeitig eintreffen oder Snapshots nicht-geordnet eintreffen. Eine Funktion legt fest, welcher Snapshot als nächstes verarbeitet wird und welche Versionsnummer er hat. Die API verarbeitet Snapshots in aufsteigender Versionsreihenfolge:

- Liegen mehrere Snapshots vor, werden alle der Reihe nach verarbeitet.
- Trifft ein Snapshot nicht-geordnet ein (z. B. `snapshot_3` nach `snapshot_4`), wird er übersprungen.
- Gibt es keine neuen Snapshots, gibt die Funktion `None` zurück und es findet keine Verarbeitung statt.

**Schritt 1 — Snapshot-Dateien vorbereiten:** CSV-Dateien mit Snapshot-Daten anlegen und in einem Volume oder Cloud-Speicherort ablegen, chronologisch benannt (z. B. `snapshot_1.csv`, `snapshot_2.csv`), mit Spalten `userId` und `city`.

**Schritt 2 — `AUTO CDC FROM SNAPSHOT` mit Versions-Funktion ausführen:**

```python
from pyspark import pipelines as dp
from typing import Optional, Tuple
from pyspark.sql import DataFrame

def next_snapshot_and_version(latest_snapshot_version: Optional[int]) -> Optional[Tuple[DataFrame, int]]:
  snapshot_dir = "/Volumes/main/cdc_tutorial/snapshots/" # or the location you created the sample data

  files = dbutils.fs.ls(snapshot_dir)
  snapshot_files = [f.name for f in files if f.name.startswith("snapshot_") and f.name.endswith(".csv")]

  snapshot_versions = []
  for filename in snapshot_files:
    try:
      version = int(filename.replace("snapshot_", "").replace(".csv", ""))
      snapshot_versions.append(version)
    except ValueError:
      continue

  snapshot_versions.sort()

  if latest_snapshot_version is None:
    if snapshot_versions:
      next_version = snapshot_versions[0]
    else:
      return None
  else:
    next_versions = [v for v in snapshot_versions if v > latest_snapshot_version]
    if next_versions:
      next_version = next_versions[0]
    else:
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

**Hinweis:** Für SCD Typ 1 wird `stored_as_scd_type=1` gesetzt.

Nach Verarbeitung von `snapshot_1.csv`:

| userId | city | __START_AT | __END_AT |
|---|---|---|---|
| 1 | Oaxaca | 1 | null |
| 2 | Monterrey | 1 | null |
| 3 | Tijuana | 1 | null |

Nach Verarbeitung von `snapshot_2.csv`:

| userId | city | __START_AT | __END_AT |
|---|---|---|---|
| 1 | Oaxaca | 1 | 2 |
| 2 | Monterrey | 1 | 2 |
| 2 | Carmel | 2 | null |
| 3 | Tijuana | 1 | 2 |
| 3 | Los Angeles | 2 | null |
| 4 | Death Valley | 2 | null |

**Hinweis:** Bei SCD Typ 1 sieht die Tabelle exakt wie der jüngste Snapshot aus — der Unterschied ist, dass nachgelagerte Queries über den Change Feed nur geänderte Datensätze verarbeiten können.

## <a id="limitierungen">8. Limitierungen</a>

- Die Sequenzierungsspalte muss einen sortierbaren Datentyp haben. `NULL`-Sequenzierungswerte werden nicht unterstützt.
- `AUTO CDC FROM SNAPSHOT` wird nur in der Python-Pipeline-Schnittstelle unterstützt — die SQL-Schnittstelle wird nicht unterstützt.
- Um aus dem Ziel eines `AUTO CDC`-Prozesses zu streamen, wird aus dessen Change Feed gelesen (siehe `CDC fortgeschritten.md`).

## <a id="auto-cdc-vs-merge">9. `AUTO CDC INTO` vs. `MERGE INTO` — wann was?</a>

Aus einer privaten Kurs-Notiz übernommen, nicht gegen die offizielle Doku verifiziert — eine Architekturabwägung, keine Doku-Aussage.

### Das Problem: manuelle CDC-Logik ist brüchig

In vielen Pipelines wird Change Data Capture manuell implementiert. Das bedeutet üblicherweise, ein `MERGE INTO`-Statement zu schreiben und zu pflegen, das korrekt behandeln muss:

- Inserts, Updates und Deletes
- Doppelte Events und Replays
- Verspätet eintreffende Änderungen
- Korrekte Keys und Match-Bedingungen

Selbst wenn das SQL zunächst einfach aussieht, wird die Logik mit wachsenden Anforderungen leicht brüchig.

**Traditioneller Ansatz — manuelles `MERGE INTO`-Beispiel:**

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

**Warum das ein Problem ist:**

- Die Merge-Logik muss selbst gepflegt werden.
- Eingehenden `operation`-Werten muss vertraut werden, Edge Cases müssen selbst behandelt werden.
- Mit sich weiterentwickelnden Schemas und Regeln wächst der Merge häufig zu einem großen SQL-Block, der schwer zu testen und leicht falsch zu bekommen ist.

`AUTO CDC INTO` ersetzt dieses Muster: Die Pipeline wendet CDC-Änderungen automatisch an, mit deutlich weniger Code (siehe Abschnitt 6 dieses Dokuments sowie [08 AUTO CDC INTO.md](../14%20Developer%20Reference/04%20SQL-Referenz/08%20AUTO%20CDC%20INTO.md) für die vollständige Syntax).

### Wann `MERGE INTO` dennoch die passendere Wahl ist

`AUTO CDC INTO` ist für den klassischen CDC-Anwendungsfall (Upsert/Delete anhand von Keys und einer Sequenzierungsspalte, optional SCD-Historie) in der Regel vorzuziehen, da es nicht-chronologisch eintreffende Events, SCD Typ 1/2 und Metriken ohne handgeschriebenen Code abdeckt (siehe Abschnitt 1). In folgenden Fällen ist `MERGE INTO` dennoch die passendere Wahl:

- **Abweichende Update-Logik:** `MERGE INTO` ist eine generische SQL-Anweisung mit frei kombinierbaren `MATCHED`/`NOT MATCHED`-Bedingungen, mehreren bedingten Update-Zweigen oder komplexer Geschäftslogik, die nicht in das feste Schema von `AUTO CDC INTO` (Keys, Sequenzspalte, Delete-/Truncate-Bedingung) passt.
- **Kein Pipeline-Kontext nötig:** `MERGE INTO` läuft direkt gegen eine Delta-Tabelle in jedem Notebook, Job oder SQL-Warehouse — ohne eine deklarative Pipeline mit eigenem Ausführungsmodell, Checkpointing und Scheduling aufzusetzen. Das macht es leichtgewichtiger für einmalige Batch-Abgleiche oder Ad-hoc-Korrekturen außerhalb eines Pipeline-Kontexts.
- **Transparenz und Debugging:** Als einzelne, explizite SQL-Anweisung lässt sich `MERGE INTO` leicht mit `EXPLAIN` analysieren, in Transaktionen einbetten und debuggen. `AUTO CDC INTO` abstrahiert die Merge-Operationen intern, was das Debuggen von Edge Cases erschwert, wenn vom Standardverhalten abgewichen werden soll.
- **Keine Zusatzinfrastruktur:** `AUTO CDC INTO` erfordert eine Streaming Table als Ziel sowie Serverless Lakeflow Pipelines oder die Editionen Pro/Advanced (siehe Abschnitt 1). Für seltene, kleine Synchronisationsaufgaben ist ein einzelnes `MERGE INTO` oft schneller eingerichtet und mit weniger organisatorischem und lizenzbezogenem Mehraufwand verbunden.

---

## <a id="quellen">10. Quellen</a>

- The AUTO CDC APIs: Simplify change data capture with pipelines (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/ldp/cdc
- The AUTO CDC APIs (AWS): https://docs.databricks.com/aws/en/ldp/cdc
- Verwandte Datei in diesem Projekt: `Lakeflow Connect/Lakeflow Connect Standard Connectors/Working with Files/_fileIngestionScenarios.md` Abschnitte 1c/5c (Datei-basierte `AUTO CDC FROM SNAPSHOT`-Anwendungsfälle)

**Stand:** 2026-08-19.
