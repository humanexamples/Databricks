# Schema-Aspekte bei der Datei-Ingestion — werkzeugübergreifende Referenz

Dieses Dokument bündelt **alle Schema-bezogenen Aspekte** der Datei-Ingestion in Databricks — Schema-Inferenz, `schemaHints`, Schema-Evolution, Type Widening, Rescued Data Column, Partitionsspalten, `schemaLocation`, Groß-/Kleinschreibung und Schema-bedingte Exceptions —, die in den drei Schwesterdateien dieses Ordners bereits einzeln gegen die offizielle Databricks-Dokumentation verifiziert wurden:

- `_read_files.md` (SQL-Tabellenfunktion `read_files`, Batch und `STREAM read_files`)
- `_spark_read.md` (`spark.read` / `spark.readStream`)
- Ordner `06 Auto Loader/` (Auto Loader / `cloudFiles`)

Es handelt sich um eine **reine Zusammenführung und Neuordnung nach Thema statt nach Werkzeug** — es wurde keine neue Web-Recherche für diese Datei durchgeführt. Jede Aussage ist bereits in einer der drei Quelldateien verifiziert; wo eine Aussage dort als "**Ungeklärt:**" oder "**Korrektur:**" markiert ist, wird das hier unverändert übernommen. Jeder Abschnitt verweist auf den jeweiligen Quellabschnitt zur Nachvollziehbarkeit.

## Abschnittsübersicht

1. [Schema-Inferenz je Werkzeug](#inferenz)
2. [Explizites Schema angeben](#explizites-schema)
3. [Partitionsspalten](#partitionsspalten)
4. [`schemaHints`](#schemahints)
5. [Schema-Evolution-Modi](#evolution)
6. [Automatisches Type Widening](#type-widening)
7. [Die Rescued-Data-Column (`_rescued_data`)](#rescued-data)
8. [Parser-Modi (`PERMISSIVE`/`DROPMALFORMED`/`FAILFAST`)](#parser-modi)
9. [`schemaLocation` / Schema-Speicherort](#schema-location)
10. [Groß-/Kleinschreibung bei der Schema-Inferenz](#case-sensitivity)
11. [Schema-bedingte Exceptions](#exceptions)
12. [Werkzeugübergreifender Gesamtvergleich](#vergleich)
13. [Praxis-Pattern: Resilientes Bronze-Layer-Design](#praxis-pattern)
14. [Quellen](#quellen)

---

## <a id="inferenz">1. Schema-Inferenz je Werkzeug</a>

### `read_files` (Batch und Streaming)

Wird kein Schema angegeben, leitet `read_files` ein einheitliches Schema über alle entdeckten Dateien ab. Ohne `LIMIT` werden dafür grundsätzlich **alle** Dateien gelesen; auch mit `LIMIT` kann `read_files` mehr Dateien lesen als für das Limit nötig wären, um ein repräsentativeres Schema zu liefern — es ist also nicht garantiert, dass genau so viele Dateien gelesen werden, wie für `LIMIT n` Zeilen minimal nötig wären. Databricks fügt SQL-Abfragen in Notebooks/SQL-Editor automatisch ein `LIMIT` hinzu, falls keines angegeben wurde.

**Zwei Lesedurchläufe:** Ohne Schema entsteht faktisch ein zusätzlicher, separater Lesevorgang — zuerst zur Schema-Inferenz (alle Dateien), dann zum eigentlichen Laden. Ein explizit angegebenes Schema überspringt den Inferenz-Durchlauf vollständig und beschleunigt dadurch das Laden.

**`inferColumnTypes`** (Standardwert **`true`**) steuert, ob beim Ableiten des Schemas die exakten Spaltentypen bestimmt werden. Das ist laut Doku selbst explizit das **Gegenteil** des Standardverhaltens von Auto Loader bei CSV und JSON (dort standardmäßig `false`). Die Doku macht dabei keine Unterscheidung zwischen Batch- und Streaming-Nutzung — der Standardwert `true` gilt unabhängig davon, ob `STREAM` verwendet wird.

*(Quelle: `_read_files.md` Abschnitt 2)*

### `spark.read` (Batch)

Verhält sich **format-abhängig unterschiedlich** — anders als bei `read_files`, wo `inferColumnTypes` einheitlich für alle Formate gilt:

- **JSON:** Ohne `schema`-Angabe liest `DataFrameReader.json()` laut Methodenreferenz wörtlich den Input einmal vollständig, um das Schema zu bestimmen (*"If `schema` is not specified, this function reads the input once to determine the input schema."*) — automatische Inferenz ist hier der Standard.
- **CSV:** Schema-Inferenz ist **nicht** standardmäßig aktiv. Die Option `inferSchema` hat den Standardwert **`false`** (zweifach bestätigt) — ohne explizites Setzen werden alle Spalten als `string` gelesen.

**Einschränkung:** Weder die `schema()`-Referenz noch die JSON-/CSV-Optionsseite benennen eine feste Anzahl an Lesevorgängen (z. B. "genau zweimal"). Bestätigt ist nur: (a) JSON ohne Schema liest den Input laut Doku-Wortlaut einmal vollständig zur Inferenz, und (b) ein explizites Schema erlaubt der Datenquelle, diesen Inferenzschritt zu überspringen.

*(Quelle: `_spark_read.md` Abschnitt 2)*

### Auto Loader (`cloudFiles`, direkt oder über `STREAM read_files`)

**Stichprobengröße:** Auto Loader sampelt beim ersten Lesen die ersten **50 GB oder 1000 Dateien**, je nachdem, welches Limit zuerst erreicht wird — und zwar nach Aktualität sortiert: die *neuesten* (nach Dateiänderungszeitpunkt) Dateien/Bytes werden für die Inferenz ausgewählt, keine beliebige Stichprobe. Die Stichprobengröße lässt sich anpassen:

```sql
SET spark.databricks.cloudFiles.schemaInference.sampleSize.numBytes = '10gb';
SET spark.databricks.cloudFiles.schemaInference.sampleSize.numFiles = 500;
```

**Standardverhalten je Format:**

| Format | Standard-Inferenztyp |
|---|---|
| JSON | `string` (auch verschachtelte Felder) |
| CSV | `string` |
| XML | `string` |
| Avro | im Avro-Schema kodierte Typen |
| Parquet | im Parquet-Schema kodierte Typen |

Bei JSON/CSV/XML wird **bewusst** standardmäßig `string` gewählt, um Schema-Evolution-Probleme durch Typkonflikte zu vermeiden — das exakte **Gegenteil** des Standardverhaltens von `read_files` (dort `inferColumnTypes = true`). Um dasselbe stichprobenbasierte Typ-Verhalten wie der generische `DataFrameReader` zu erhalten, muss `cloudFiles.inferColumnTypes` explizit auf `true` gesetzt werden (Standardwert **`false`**):

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "csv")
      .option("cloudFiles.inferColumnTypes", True)
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .load("/Volumes/analytics/bronze/csv_data"))
```

**Parquet/Avro-Typkonflikte:** Hat eine Spalte in zwei Dateien unterschiedliche Datentypen, wählt Auto Loader den breitesten Typ; `schemaHints` kann diese Wahl überschreiben. Bei einem Konflikt rettet Auto Loader die Spalte in die Rescued-Data-Spalte, statt sie zu casten.

**CSV-Header:** Auto Loader geht bei CSV-Schema-Inferenz davon aus, dass Header vorhanden sind — ohne Header muss `.option("header", "false")` gesetzt werden.

**Unterstützung nach Format/Runtime:**

| Dateiformat | Unterstützte Versionen für Schema-Inferenz/-Evolution |
|---|---|
| JSON | Alle Versionen |
| CSV | Alle Versionen |
| XML | Ab Databricks Runtime 14.3 LTS |
| Avro | Ab Databricks Runtime 10.4 LTS |
| Parquet | Ab Databricks Runtime 11.3 LTS |
| ORC | Nicht unterstützt |
| Text / Binaryfile | Nicht anwendbar (festes Schema) |

**Wann wird inferiert?** Das Schema wird bei der erstmaligen Definition des DataFrames im Code inferiert; während jedes Micro-Batches werden Schema-Änderungen dynamisch ausgewertet — keine vollständige Neu-Inferenz pro Batch. Bei leerem Quellverzeichnis verlangt Auto Loader die Angabe eines Schemas. Bei sehr großen Quellverzeichnissen kann die initiale Inferenz einige Minuten dauern.

*(Quelle: `06 Auto Loader/01 Schema-Inferenz und -Evolution.md` und `06 Auto Loader/15 FAQ.md`)*

### Gegenüberstellung

| Werkzeug | Standard-Inferenzverhalten | Steueroption |
|---|---|---|
| `read_files` (Batch/Streaming) | Exakte Typen (`inferColumnTypes = true`) | `inferColumnTypes` |
| `spark.read.json()` | Exakte Typen (automatisch, ein Lesedurchlauf) | kein separater Schalter nötig |
| `spark.read.csv()` | Alles `string` (`inferSchema = false`) | `inferSchema` |
| Auto Loader (JSON/CSV/XML) | Alles `string` | `cloudFiles.inferColumnTypes` |
| Auto Loader (Parquet/Avro) | Im Dateiformat kodierte Typen | — |

---

## <a id="explizites-schema">2. Explizites Schema angeben</a>

Alle drei Werkzeuge unterstützen ein DDL-formatiertes Schema mit verschachtelten Typen über dieselbe Syntax: `STRUCT<feldname: typ, ...>` (optional `NOT NULL`, `COMMENT` je Feld) und `ARRAY<typ>`. Bestätigtes Doku-Beispiel zur `STRUCT`-Syntax: `STRUCT<Field1:INT NOT NULL COMMENT 'The first field.',Field2:ARRAY<INT>>`.

**`read_files`** (SQL, `schema`-Parameter):

```sql
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schema => '
      id INT,
      user STRUCT<name: STRING, age: INT>,
      tags ARRAY<STRING>,
      address STRUCT<street: STRING, city: STRING, geo: STRUCT<lat: DOUBLE, lon: DOUBLE>>,
      orders ARRAY<STRUCT<order_id: STRING, amount: DOUBLE>>
    ');
```

**`spark.read`** (Python, `.schema()` akzeptiert entweder einen DDL-String oder ein `StructType`-Objekt):

```python
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, DoubleType, ArrayType
)

schema = StructType([
    StructField("id", IntegerType(), True),
    StructField("user", StructType([
        StructField("name", StringType(), True),
        StructField("age", IntegerType(), True),
    ]), True),
    StructField("tags", ArrayType(StringType()), True),
])

df = spark.read.schema(schema).json("s3://bucket/path")
```

Gleichwertig als DDL-String in einer Variable:

```python
schema_ddl = """
  id INT,
  user STRUCT<name: STRING, age: INT>,
  tags ARRAY<STRING>
"""
df = spark.read.schema(schema_ddl).json("s3://bucket/path")
```

**Auto Loader** (`cloudFiles`, Python) — die zusammenfassenden Beispiele in `06 Auto Loader/02 Automatisches Type Widening.md` und `06 Auto Loader/14 Common Data Loading Patterns.md` (Praxis-Pattern) zeigen dieselbe DDL-String-Übergabe an `.schema(...)`:

```python
schema = "id BIGINT, event_type STRING, event_ts TIMESTAMP"

events_stream = (
  spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .schema(schema)
    .load("/Volumes/analytics/bronze/events"))
```

**Zweck laut Doku:** Ein explizit angegebenes Schema erlaubt der Datenquelle, den Inferenz-Lesedurchlauf zu überspringen, was das Laden beschleunigt — bei allen drei Werkzeugen übereinstimmend dokumentiert.

*(Quellen: `_read_files.md` Abschnitt 2, `_spark_read.md` Abschnitt 2, `06 Auto Loader/02 Automatisches Type Widening.md` und `06 Auto Loader/14 Common Data Loading Patterns.md`)*

---

## <a id="partitionsspalten">3. Partitionsspalten</a>

Bei Hive-Style-partitionierten Verzeichnissen kodiert die Verzeichnisstruktur selbst Spaltenwerte als Schlüssel-Wert-Paare (`<base-path>/a=x/b=1/c=y/file.format`). Werte stehen dann nicht im Dateiinhalt, sondern im Pfad selbst.

**`read_files`:** Automatische Erkennung bei Schema-Inferenz mit `<base-path>`. Die Option `partitionColumns` (kommagetrennte Liste) steuert, welche Ebenen übernommen werden — ein leerer String (`""`) ignoriert alle Partitionsspalten vollständig. Nützlich bei inkonsistenter Verzeichnistiefe: Fehlende Ebenen werden für die jeweiligen Dateien `NULL`, vorhandene Ebenen werden korrekt geparst. Bei Namenskonflikt (Spalte existiert sowohl als Partitions- als auch als Datenspalte) gewinnt der Pfad-Wert. Wird stattdessen ein explizites `schema` angegeben, müssen die Partitionsspalten darin enthalten sein — sonst werden sie ignoriert.

```sql
SELECT * FROM read_files(
    '/base-path',
    format => 'csv',
    partitionColumns => 'year,month,day');
-- /base-path/year=2022/week=1/file1.csv        -> year=2022, month=NULL, day=NULL
-- /base-path/year=2022/month=2/day=3/file2.csv -> year=2022, month=2,    day=3
```

**Auto Loader:** Ebenfalls automatische Inferenz aus der Verzeichnisstruktur, sofern Hive-Stil vorliegt; bei widersprüchlichen oder fehlenden Hive-Partitionen werden Partitionsspalten ignoriert. **Wichtige Einschränkung, die bei `read_files` nicht dokumentiert ist:** Auto Loader berücksichtigt Partitionsspalten **nicht** bei der Schema-Evolution — treffen z. B. nach `base_path/event=click/date=2021-04-01/f0.json` neue Dateien unter `base_path/event=click/date=2021-04-01/hour=01/f1.json` ein, ignoriert Auto Loader die neue Spalte `hour`, sofern `cloudFiles.partitionColumns` nicht explizit auf `event,date,hour` gesetzt wird. Binärdatei- und Text-Formate haben zwar ein festes Datenschema, unterstützen aber dennoch Partitionsspalten-Inferenz; Databricks empfiehlt hierfür `cloudFiles.schemaLocation` zu setzen, um wiederholte Inferenz bei jedem Neustart zu vermeiden.

**`spark.read` (Batch):** `partitionColumns` ist laut Spark-API-Optionsreferenz **kein** `DataFrameReader`-Parameter — der Name taucht dort nur als `read_files`-Parameter (SQL) bzw. als Auto-Loader-Streaming-Option (`cloudFiles.partitionColumns`, `DataStreamReader`) auf. Reines `spark.read` inferiert Hive-Style-Partitionsspalten zwar automatisch aus dem Pfad, bietet aber keine Option, diese gezielt einzuschränken.

*(Quellen: `_read_files.md` Abschnitt 3, `06 Auto Loader/01 Schema-Inferenz und -Evolution.md`, `_fileIngestionScenarios.md` Abschnitt 2)*

---

## <a id="schemahints">4. `schemaHints`</a>

`schemaHints` überschreibt gezielt einzelne Spaltentypen während der Schema-Inferenz, ohne das restliche Schema von der automatischen Inferenz auszuschließen. **Zentrale Regel, für `read_files` und Auto Loader übereinstimmend belegt:** `schemaHints` greift nur, wenn **kein** explizites `schema` angegeben ist.

**`read_files`** (SQL):

```sql
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaHints => 'id int');
```

`schemaHints` lässt sich auch für Partitionsspalten verwenden, um deren inferiertes Schema zu überschreiben. Array-/Map-Unterstützung ist ab Databricks Runtime 9.1 LTS verfügbar. Als normaler String-Parameter lässt sich `schemaHints` vorab in einer Python-Variable zusammenbauen und per f-String einsetzen:

```python
hints = "loyalty_tier STRING, region_code STRING, signup_ts TIMESTAMP"
spark.sql(f"""
  SELECT * FROM read_files(
    's3://bucket/path', format => 'json', schemaHints => '{hints}')
""")
```

**Ungeklärt:** Ob sich `schemaHints` auch direkt als SQL-Session-Variable übergeben lässt, konnte nicht verifiziert werden — die dedizierte `DECLARE VARIABLE`-Referenzseite war bei der Recherche nicht erreichbar (zweifach HTTP 404).

**Auto Loader** (`cloudFiles.schemaHints`, Python) — dieselbe Grundregel, mit ausführlich dokumentierten Beispielen für verschachtelte Strukturen:

```python
.option("cloudFiles.schemaHints", "tags map<string,string>, version int")
```

Vollständiges Doku-Beispiel für Structs/Maps — Ausgangsschema:

```
|-- date: string
|-- user_info: struct
|    |-- dob: string
|-- purchase_options: struct
|    |-- delivery_address: string
```

Angewendet: `.option("cloudFiles.schemaHints", "date DATE, user_info.dob DATE, purchase_options MAP<STRING,STRING>, time TIMESTAMP")` → Ergebnis: `date`, `user_info.dob` werden zu `DATE`, `purchase_options` wird zu `MAP<STRING,STRING>`, `time` (neu) wird `TIMESTAMP`. Für Arrays gilt die Punktnotation `.element` (Array-Elemente) bzw. `.key`/`.value` (Map-Einträge), z. B. `products ARRAY<INT>, users.element.id INT, discounts.key.id INT`. Array-/Map-Hints sind ebenfalls ab Databricks Runtime 9.1 LTS verfügbar.

**Vorab-Deklaration künftiger Spalten:** `schemaHints` kann auch verwendet werden, um eine zu Beginn des Streams noch nicht vorhandene Spalte bereits jetzt zum inferierten Schema hinzuzufügen — Spalten, die erst in künftigen Dateien auftauchen werden, lassen sich so vorab deklarieren:

```sql
CREATE OR REFRESH STREAMING TABLE bronze_events
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaHints => 'loyalty_tier STRING, region_code STRING'
);
```

**Ungeklärt (in beiden Quelldateien gezielt nachgeprüft, kein Ergebnis):** Löst eine so vorab deklarierte Spalte, sobald sie tatsächlich in den Daten auftaucht, unter `addNewColumns` noch eine `UnknownFieldException` aus — oder verhindert die Vorab-Deklaration diesen Fehlschlag? Die Doku stellt nur die Vorab-Deklaration selbst fest, klärt aber nicht, ob sie die spätere Exception für genau diese Spalte verhindert.

**`schemaHints` und Schema-Evolution-Modi:** Da der Evolution-Modus `none` genau dann Standard ist, wenn ein Schema angegeben wird, schließen sich `schemaHints` und Modus `none` im jeweiligen Standardfall gegenseitig aus. Einzig direkt dokumentierter Interaktionspunkt: *"`addNewColumns` ist nicht erlaubt, wenn das Schema des Streams angegeben wird, funktioniert aber, wenn das Schema als Schema Hint angegeben wird."* Für alle anderen Modi (`addNewColumnsWithTypeWidening`, `rescue`, `failOnNewColumns`) ist die Kombinierbarkeit mit `schemaHints` **ungeklärt** — plausibel, aber nicht explizit dokumentiert.

**`spark.read`: Kein `schemaHints`-Äquivalent.** Zweifach belegt: Die `DataFrameReader`-Klassenreferenz erwähnt keine solche Option, und auf der Spark-API-Optionsreferenz erscheint `schemaHints` ausschließlich im Auto-Loader-Abschnitt (Streaming-Optionen), nicht bei den generischen `DataFrameReader`/Batch-Optionen. **Konsequenz:** Mit `spark.read` lässt sich keine einzelne Spalte gezielt überschreiben, ohne das restliche Schema von der Inferenz auszuschließen — es muss entweder das komplette Schema definiert oder vollständig auf Inferenz gesetzt werden. Diese Einschränkung gilt nur für reines Batch-`spark.read`; über `spark.readStream.format("cloudFiles")` steht `cloudFiles.schemaHints` wie oben beschrieben zur Verfügung.

*(Quellen: `_read_files.md` Abschnitt 4, `_spark_read.md` Abschnitt 4, `06 Auto Loader/01 Schema-Inferenz und -Evolution.md`)*

---

## <a id="evolution">5. Schema-Evolution-Modi</a>

Schema-Evolution steuert, wie mit neu auftauchenden Spalten, umbenannten/gelöschten Spalten und Typänderungen in **nachfolgenden** Lieferungen/Micro-Batches umgegangen wird — im Unterschied zur reinen Erstinferenz (Abschnitt 1). **Diese Fähigkeit ist ausschließlich im Streaming-Kontext verfügbar** (`STREAM read_files` bzw. Auto Loader/`cloudFiles`); im Batch-Modus (`read_files` ohne `STREAM`, `spark.read`) existiert kein über mehrere Läufe hinweg wirksames Evolutions-Konzept — jede Ausführung leitet das Schema unabhängig neu ab.

Gesteuert wird das Verhalten über den benannten Parameter `schemaEvolutionMode` (`read_files`) bzw. die Option `cloudFiles.schemaEvolutionMode` (Auto Loader) — inhaltlich identisch, da `STREAM read_files` intern Auto Loader nutzt.

### Die fünf Modi

| Modus | Verhalten |
|---|---|
| `addNewColumns` (Standard **ohne** angegebenes Schema) | Neue Spalten führen dazu, dass der Stream mit einer `UnknownFieldException` stoppt. Vor dem Abbruch wird das Schema aus dem letzten Micro-Batch abgeleitet und der Schema-Speicherort aktualisiert; ein Neustart übernimmt das erweiterte Schema automatisch. Bestehende Spalten behalten ihren Datentyp. |
| `addNewColumnsWithTypeWidening` | Verhält sich wie `addNewColumns`, erweitert zusätzlich automatisch kompatible Datentypen (z. B. `int` → `long`), ohne dass Daten neu geschrieben werden müssen (siehe Abschnitt 6). Nicht unterstützte Typänderungen (z. B. `int` → `string`) landen in der Rescued-Data-Spalte. |
| `rescue` | Schema entwickelt sich nie weiter, der Stream schlägt nie wegen Schema-Änderungen fehl. Neue oder nicht passende Spalten landen ausschließlich in der Rescued-Data-Spalte. |
| `failOnNewColumns` | Der Stream schlägt bei neuen Spalten fehl und startet **nicht** automatisch neu — strikter als `addNewColumns`, da keine automatische Schema-Aktualisierung im Hintergrund erfolgt; erst nach manueller Schema-Aktualisierung oder Entfernen der betroffenen Datei. |
| `none` (Standard, **wenn** ein Schema angegeben ist) | Schema entwickelt sich nicht weiter, neue Spalten werden ignoriert, der Stream schlägt nicht wegen Schema-Änderungen fehl. Daten werden **nicht** gerettet, außer `rescuedDataColumn` ist zusätzlich explizit gesetzt. |

**Wichtige, wörtlich bestätigte Zusatzregel:** `addNewColumns` ist der Standard, wenn kein Schema angegeben wird; `none` ist der Standard, wenn ein Schema angegeben wird. `addNewColumns` ist nicht erlaubt, wenn das Schema des Streams explizit angegeben wird, funktioniert aber, wenn dieselbe Typinformation stattdessen als `schemaHints` übergeben wird (siehe Abschnitt 4).

```python
query = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .option("cloudFiles.schemaEvolutionMode", "rescue")
  .load("/Volumes/analytics/bronze/events"))
```

```sql
CREATE OR REFRESH STREAMING TABLE events_rescue_only
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'rescue'
);
```

Databricks empfiehlt ausdrücklich, den Stream über Lakeflow Jobs zu konfigurieren, damit er nach einer `UnknownFieldException` automatisch neu startet.

### Welche Änderungsarten werden abgedeckt?

| Änderungstyp | Verhalten |
|---|---|
| Neue Spalten | Unterstützt, abhängig vom gewählten Modus |
| Spalten umbenennen | Wird als neue Spalte behandelt; die alte Spalte erhält für neue Zeilen `NULL` |
| Gelöschte Spalten | Unterstützt als "Soft Delete" — neue Zeilen erhalten `NULL` |
| Typ-Erweiterung | Unterstützt ab Databricks Runtime 16.4 mit `addNewColumnsWithTypeWidening` (siehe Abschnitt 6) |

### Verwandte, aber eigenständige Bausteine

- **`rescuedDataColumn`** fungiert als Sicherheitsnetz über alle Evolution-Modi hinweg — selbst bei `addNewColumns` oder `failOnNewColumns` lässt sie sich zusätzlich aktivieren (siehe Abschnitt 7).
- **Delta-Table-Ebene (`mergeSchema`/`overwriteSchema`)**: Beim Schreiben in Delta-Tabellen existieren zusätzlich eigene Schema-Evolution-Mechanismen (additiv bei `mergeSchema`, überschreibend bei `overwriteSchema`) — eine separate Ebene, unabhängig vom `schemaEvolutionMode` des Streaming-Modus.
- **Einschränkung:** Der `from_json`-Parser unterstützt keine Schema-Evolution.

*(Quellen: `_read_files.md` Abschnitt 10, `06 Auto Loader/01 Schema-Inferenz und -Evolution.md`, Abschnitt Schema-Evolution-Modi)*

---

## <a id="type-widening">6. Automatisches Type Widening</a>

Mit `schemaEvolutionMode => 'addNewColumnsWithTypeWidening'` erweitert Auto Loader/`read_files` zusätzlich zum Hinzufügen neuer Spalten automatisch kompatible Datentypänderungen, ohne dass Daten neu geschrieben werden müssen.

### Unterstützte, verlustfreie Typänderungen

| Quelltyp | Mögliche Zieltypen |
|---|---|
| `byte` | `short`, `int`, `long`, `decimal`, `double` |
| `short` | `int`, `long`, `decimal`, `double` |
| `int` | `long`, `decimal`, `double` |
| `long` | `decimal` |
| `float` | `double` |
| `decimal` | `decimal` mit höherer Präzision/Skala |
| `date` | `timestampNTZ` (nur Parquet) |

Type Widening gilt für alle Formate mit Schema-Evolution-Unterstützung — Textformate (JSON, CSV, XML) und Binärformate (Avro, Parquet) gleichermaßen.

**Präzision bei Erweiterung auf `decimal`:** Auto Loader erweitert auf ein `decimal` mit mindestens der Ausgangs-Präzision der Integer-Typen (`byte`/`short`/`int`: `10`, `long`: `20`). Beispiel aus der Doku: Wird eine Spalte als `int` gelesen und tritt in einer Datei `decimal(5, 2)` für dieselbe Spalte auf, erweitert Auto Loader auf `decimal(12, 2)`.

### Voraussetzungen

- **Databricks Runtime 16.4 oder höher.**
- Bei Delta-Lake-Zieltabellen muss Type Widening zusätzlich auf der Tabelle aktiviert sein:

```sql
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');
```

```python
query = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.inferColumnTypes", True)
  .option("cloudFiles.schemaLocation", "<schemaPath>")
  .option("cloudFiles.schemaEvolutionMode", "addNewColumnsWithTypeWidening")
  .load("<inputPath>")
  .writeStream
  .option("mergeSchema", "true")
  .option("checkpointLocation", "<checkpointPath>")
  .trigger(availableNow=True)
  .toTable("table_name"))
```

**Einschränkungen:** Die Option `prefersDecimal` kann bei `addNewColumnsWithTypeWidening` nicht auf `false` gesetzt werden. `date`-zu-`timestampNTZ`-Widening wird nur für Parquet-Dateien unterstützt.

### Verhalten bei nicht-widenbaren bzw. nicht aktivierten Modi

Beispiel aus der Doku: Eine Spalte `id` wird zunächst als `INT` inferiert, anschließend erscheint ein Wert außerhalb des `INT`-Bereichs (z. B. `2147483648`):

| Modus | Verhalten bei typ-erweiterbarer Änderung |
|---|---|
| `addNewColumns` (Standard) | Datentyp entwickelt sich **nicht** weiter; kein Fehlschlag wegen der Typänderung; die Zeile erhält für diese Spalte `NULL`, der Originalwert landet in der Rescued-Data-Spalte. |
| `rescue` | Kein Fehlschlag; abweichender Wert wird `NULL` + gerettet. |
| `failOnNewColumns` | Wie `addNewColumns` bei Typänderungen (kein Fehlschlag, Rettung); Fehlschlag ausschließlich bei **neuen** Spalten. |
| `none` | Keine Evolution, keine Rettung (außer `rescuedDataColumn` separat gesetzt). |
| `addNewColumnsWithTypeWidening` | Stream schlägt (bewusst) fehl. Neue Spalten werden hinzugefügt, unterstützte Typänderungen erweitert; beim Neustart wird auf den passenden Zieltyp erweitert (`INT` → `BIGINT`), der Wert bleibt erhalten statt gerettet zu werden. |

*(Quelle: `06 Auto Loader/02 Automatisches Type Widening.md`; siehe auch `_read_files.md` Abschnitt 10 für die `read_files`-eigene Kurzfassung derselben Fakten)*

---

## <a id="rescued-data">7. Die Rescued-Data-Column (`_rescued_data`)</a>

Die Rescued-Data-Spalte stellt sicher, dass beim Einlesen keine Daten stillschweigend verloren gehen. Sie enthält Daten, die nicht geparst werden konnten — etwa weil ein Feld im Schema fehlte, ein Typkonflikt vorlag, oder die Groß-/Kleinschreibung der Spalte nicht mit dem Schema übereinstimmte. Zurückgegeben wird sie als JSON-Blob mit den geretteten Spalten sowie dem Quelldateipfad.

### Zentraler Unterschied zwischen den drei Werkzeugen: Standardverhalten

| Werkzeug | `rescuedDataColumn` standardmäßig aktiv? |
|---|---|
| `read_files` | **Ja**, sofern Schema-Inferenz aktiv ist (kein explizites Schema bzw. Evolution zugelassen) — deaktivierbar über `schemaEvolutionMode => 'none'`. |
| Auto Loader (`cloudFiles`) | **Ja, automatisch** — beim Inferieren des Schemas fügt Auto Loader die Spalte automatisch als `_rescued_data` hinzu. Umbenennbar/einbindbar über die Option `rescuedDataColumn`. |
| `spark.read` (`DataFrameReader`) | **Nein** — zweifach bestätigt: In allen geprüften Optionstabellen (CSV, JSON, Parquet, Avro, XML) ist der Standardwert durchgängig `None`; die Doku zeigt das Aktivieren explizit als notwendigen Schritt (*"To enable the rescued data column, set the `rescuedDataColumn` option to a column name when reading"*). |

**Praktische Konsequenz:** Bei `spark.read` ist das Risiko stiller Typ-Fehlparsierungen bzw. unerwarteter `FAILFAST`-Abbrüche bei Typkonflikten höher als bei `read_files`/Auto Loader, sofern die Option nicht bewusst gesetzt wird:

```python
# spark.read: rescuedDataColumn muss explizit gesetzt werden
df = (spark.read
      .option("rescuedDataColumn", "_rescued_data")
      .format("json")
      .load("/Volumes/<catalog>/<schema>/<volume>/events_json"))
```

```sql
-- read_files: Standardmäßig aktiv bei Schema-Inferenz; gezielt deaktivierbar
SELECT * FROM read_files(
    's3://bucket/path', format => 'json', schemaEvolutionMode => 'none');
```

```python
# Auto Loader: explizites Umbenennen der automatisch aktiven Spalte
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaHints", "_corrupt_record string")
  .option("columnNameOfCorruptRecord", "_corrupt_record")
  .load("/Volumes/analytics/bronze/events"))
```

### Zusammenspiel mit den Parser-Modi (alle drei Werkzeuge einheitlich)

Bei aktiver `rescuedDataColumn` führen reine **Typkonflikte** nicht dazu, dass Datensätze in `DROPMALFORMED` verworfen oder in `FAILFAST` ein Fehler ausgelöst wird — unabhängig vom `mode` landen sie in der Rescued-Data-Spalte, nicht in einer Exception. Nur wirklich **korrupte/unvollständige** Datensätze (defektes JSON/CSV) gelten als korrupt und landen stattdessen in `_corrupt_record` bzw. `badRecordsPath`, oder lösen in `FAILFAST` einen Fehler aus. Databricks empfiehlt `columnNameOfCorruptRecord` gegenüber `badRecordsPath`, um mögliche Race Conditions zu vermeiden.

*(Quellen: `_read_files.md` Abschnitt 13, `_spark_read.md` Abschnitt 9, `06 Auto Loader/01 Schema-Inferenz und -Evolution.md`, Abschnitt Rescued-Data-Column)*

---

## <a id="parser-modi">8. Parser-Modi (`PERMISSIVE`/`DROPMALFORMED`/`FAILFAST`)</a>

Für CSV/JSON gilt bei allen drei Werkzeugen `PERMISSIVE` als Standard-`mode`; verfügbare Werte: `PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`. **Abweichung bei Avro:** Dort ist der Standardwert von `mode` bei `spark.read.format("avro")` **`FAILFAST`** — abweichend vom `PERMISSIVE`-Standard bei CSV/JSON (zweifach bestätigt in `_spark_read.md`).

```sql
-- read_files: mode "FAILFAST" bricht das Parsen mit einer RuntimeException ab
SELECT * FROM read_files(
    's3://bucket/path/file.csv', format => 'csv', mode => 'FAILFAST');
```

Wie in Abschnitt 7 dargelegt, greift dieser Modus bei Typkonflikten nur dann tatsächlich, wenn `rescuedDataColumn` **nicht** aktiv ist — mit aktiver Rescued-Data-Spalte landen Typkonflikte unabhängig vom `mode` in `_rescued_data`.

*(Quellen: `_read_files.md` Abschnitte 3 und 13, `_spark_read.md` Abschnitte 3 und 9)*

---

## <a id="schema-location">9. `schemaLocation` / Schema-Speicherort</a>

`schemaLocation` (`read_files`-Parameter) bzw. `cloudFiles.schemaLocation` (Auto Loader) ist **ausschließlich im Streaming-Modus** relevant. Auto Loader legt an diesem Pfad ein Unterverzeichnis `_schemas` an, in dem das inferierte Schema und dessen Änderungen über die Zeit gespeichert werden — wörtlich bestätigt (zweifach abgerufen, identischer Wortlaut): *"Auto Loader stores the schema information in a directory `_schemas` at the configured `cloudFiles.schemaLocation` to track schema changes to the input data over time."*

```sql
CREATE OR REFRESH STREAMING TABLE events_bronze
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaLocation => '/Volumes/analytics/bronze/_schema'
);
```

**Korrektur (in beiden Quelldateien identisch vorgenommen):** Eine frühere Fassung behauptete zusätzlich, bei einem Neustart werde das gespeicherte Schema wiederverwendet statt erneut vollständig zu inferieren. Das ist **nicht belegt** — die Quelle sagt nur, dass Schemaänderungen über die Zeit nachverfolgt werden, äußert sich aber nicht explizit zum allgemeinen Neustart-Verhalten. Bestätigt ist eine Wiederverwendung nur für den spezifischen, enger gefassten Fall der Schema-Evolution nach einer `UnknownFieldException` (Abschnitt 5): Vor dem Abbruch wird der Schema-Speicherort bereits mit dem erweiterten Schema aktualisiert, und ein Neustart übernimmt dieses automatisch.

**Ungeklärt:** Ob sich der Inhalt von `_schemas` gezielt selbst vorbefüllen lässt (um z. B. ein eigenes Startschema vorzugeben, ohne den `schema`-Parameter zu nutzen), ist nicht dokumentiert — das Verzeichnis wird als interner Tracking-Mechanismus beschrieben, nicht als für Nutzer zum direkten Schreiben vorgesehene Schnittstelle.

**Unity-Catalog-Einschränkung:** Unity Catalog erlaubt es nicht, Checkpoint- oder Schema-Inferenz-/-Evolution-Dateien innerhalb des Tabellenverzeichnisses zu verschachteln — sie müssen an einem eigenen, von Unity Catalog verwalteten Speicherort liegen.

**Für reines Batch-`spark.read`/`read_files` ohne `STREAM` gibt es kein Äquivalent** — dort wird bei jeder Ausführung neu inferiert, ohne dass etwas persistiert würde.

*(Quellen: `_read_files.md` Abschnitt 3, `_spark_read.md` Abschnitt 7, `06 Auto Loader/03 Unity-Catalog-Integration.md`)*

---

## <a id="case-sensitivity">10. Groß-/Kleinschreibung bei der Schema-Inferenz</a>

Ohne aktivierte Case-Sensitivity behandelt Auto Loader die Spalten `abc`, `Abc` und `ABC` für Zwecke der Schema-Inferenz als dieselbe Spalte; welche Schreibweise tatsächlich verwendet wird, wählt Auto Loader arbiträr anhand der Stichprobendaten. `schemaHints` kann verwendet werden, um die zu verwendende Schreibweise gezielt festzulegen — nach der Wahl betrachtet Auto Loader die nicht gewählten Schreibweisen-Varianten nicht mehr als mit dem Schema konsistent.

Ist die Rescued-Data-Spalte aktiv, lädt Auto Loader Felder, deren Schreibweise von der des Schemas abweicht, in `_rescued_data`. Über die Option `readerCaseSensitive => false` lässt sich dieses Verhalten ändern, sodass Auto Loader case-insensitiv liest.

*(Quelle: `06 Auto Loader/01 Schema-Inferenz und -Evolution.md`, Abschnitt Rescued-Data-Column)*

---

## <a id="exceptions">11. Schema-bedingte Exceptions</a>

### Grundunterscheidung (für alle drei Werkzeuge strukturell identisch)

- **Lese-Ebene** (Batch bzw. Parsen einzelner Datensätze im Streaming-Modus): Ein Typ- oder Struktur-Konflikt in einem *einzelnen Datensatz* führt in der Regel **nicht** automatisch zu einer Exception — er wird geparst, verworfen oder gerettet, abhängig vom `mode` (siehe Abschnitt 8).
- **Schreib-Ebene** (Ergebnis wird in eine Delta-Tabelle geschrieben): Hier ist eine Exception bei Schema-Abweichung der **dokumentierte Standardfall** (Schema Enforcement) — betrifft aber nicht das Lesewerkzeug selbst, sondern die nachgelagerte Schreiboperation.
- **Streaming-Ebene** (nur `STREAM read_files`/Auto Loader): Eine `UnknownFieldException` bei neuen Spalten ist der **dokumentierte Normalfall**, sofern nicht `rescue` gewählt wurde.

### Der zentrale Schema-Auslöser: `UnknownFieldException` (nur Streaming)

| Auslöser | Exception | Bedingung |
|---|---|---|
| Neue, bisher unbekannte Spalte, `schemaEvolutionMode => 'addNewColumns'` (Standard ohne Schema) | `UnknownFieldException` (`org.apache.spark.sql.catalyst.util.UnknownFieldException: Encountered unknown field(s) during parsing: <column name>`) | Der Stream stoppt **bewusst** — vor dem Abbruch wird der Schema-Speicherort bereits mit dem erweiterten Schema aktualisiert; ein Neustart übernimmt dieses automatisch. |
| Neue Spalte **oder** durch Type-Widening abgedeckte Typänderung, `schemaEvolutionMode => 'addNewColumnsWithTypeWidening'` | Ebenfalls `UnknownFieldException`, nach demselben Muster | Ab Databricks Runtime 16.4; Type Widening muss zusätzlich auf Ziel-Tabellenebene aktiviert sein. |
| Neue Spalte, `schemaEvolutionMode => 'failOnNewColumns'` | Stream schlägt fehl und startet **nicht** automatisch mit erweitertem Schema neu | Strikter als `addNewColumns` — keine automatische Hintergrundaktualisierung. |
| Schema wurde explizit angegeben, gleichzeitig `schemaEvolutionMode => 'addNewColumns'` gewählt | Konfigurationsfehler: nicht zulässig bei explizitem Schema (funktioniert dort nur als `schemaHints`) | Siehe Abschnitt 4/5. |

**Ungeklärt:** Ob dies auch explizit für neue Felder *innerhalb bestehender verschachtelter Structs* (nicht nur neue Top-Level-Spalten) so dokumentiert ist, wurde nicht bestätigt.

### Format-spezifische Lese-Ebenen-Auslöser (Batch)

| Auslöser | Verhalten | Werkzeug |
|---|---|---|
| Avro: kein `mode` gesetzt, nicht parsbarer Datensatz | Abbruch, da Avro-Standard `FAILFAST` ist | `spark.read`/`read_files` |
| Avro: `avroSchemaEvolutionMode => 'restart'` + Schema-Änderung erkannt | *"raises an `UnknownFieldException` when schema changes are detected and requires a job restart"* | `spark.read` (Batch-Avro-Option) |
| CSV: `failOnUnknownFields => true` | Abbruch, sobald ein Datensatz Spalten enthält, die nicht im Schema stehen | Beide |
| CSV: `failOnWidenedFields => true` | Abbruch, sobald ein Feldwert nur durch Typ-Erweiterung zum Schema-Typ passt | Beide |
| `format("binaryFile")` mit explizitem `schema`, der nicht zum festen Binary-File-Schema passt | Fehlerklasse `BINARY_FILE_DATA_SOURCE_SCHEMA_MISMATCH`: *"The schema provided to the binary file data source does not match the expected schema."* | Beide |
| CTAS: deklarierte Spaltenanzahl passt nicht zur Query-Ausgabe | Fehlerklassen `INSERT_COLUMN_ARITY_MISMATCH` / `CREATE_VIEW_COLUMN_ARITY_MISMATCH` (Format: *"not enough/too many data columns"*) | `read_files` |

**Wichtige Einschränkung (alle Werkzeuge):** Reine Typkonflikte gelten bei aktiver `rescuedDataColumn` explizit **nicht** als korrupt — sie landen unabhängig vom `mode` (auch bei `FAILFAST`) in der Rescued-Data-Spalte, nicht in einer Exception.

**Kein Fehler, aber fehleranfällig:** Ein explizites Schema, das nicht zur tatsächlichen Spaltenreihenfolge einer CSV-Datei passt, löst **keine** Exception aus — CSV besitzt keine Spaltennamen-Metadaten, die Zuordnung erfolgt rein positionsbasiert.

### Schreib-Ebene: Delta-Tabellen (Schema Enforcement)

Betrifft nicht das Lesewerkzeug selbst, sondern das anschließende `DataFrame.write`/`INSERT`/CTAS. **Zentraler, in beiden Quelldateien identisch bestätigter Befund:** Weder die kanonische Schema-Enforcement-Seite noch die Schema-Update-Seite zeigen an irgendeiner Stelle einen wörtlich zitierbaren Exception-Text in einem Code-Block — beide Seiten wurden gezielt danach befragt, beide Antworten bestätigen übereinstimmend: kein Code-Block mit realem Fehlertext, nur Prosa-Beschreibung.

| Auslöser | Verhalten laut Doku | Einschränkung |
|---|---|---|
| Neue Spalten gegenüber Ziel-Delta-Tabelle, `mergeSchema` nicht gesetzt | Schlägt mit `AnalysisException` fehl — dokumentiertes Standardverhalten | **Ungeklärt:** Exakter Exception-Wortlaut nicht belegt; die KB zeigt einen Beispieltext nur als explizit "illustrativ" gekennzeichnet, kein realer Systemoutput. Lösung: `.option("mergeSchema", "true")`. |
| Nested Fields bei `MERGE INTO` mit automatischer Schema-Evolution | Schlägt fehl — automatische Schema-Evolution unterstützt laut KB nur Top-Level-Spalten | Bezieht sich explizit auf `MERGE INTO`, nicht auf einfache Append-Schreibvorgänge (der bei `read_files`/`spark.read` übliche Fall). |
| Spaltentyp weicht ab, nicht kompatibel erweiterbar (außerhalb `MERGE INTO`) | **Ungeklärt:** Kein bestätigter Fehlertext in irgendeiner geprüften Quelle gefunden. Eine früher zitierte generische Meldung ließ sich nicht bestätigen und wurde entfernt. |
| Reine Parquet-Tabellen (nicht Delta) mit abweichendem Schema | **Ungeklärt:** Ebenfalls kein bestätigter Fehlertext gefunden. |

**Korrektur (in beiden Quelldateien identisch vorgenommen):** Zuvor als wörtliches Zitat dargestellte Texte — die vollständige `AnalysisException`-Meldung sowie eine generische "Failed to merge fields..."-Meldung — ließen sich bei erneuter Recherche nicht bestätigen und wurden durch "Ungeklärt"-Markierungen ersetzt.

**Wichtig:** Diese Schreib-Ebene betrifft nicht `read_files`/`spark.read` selbst — dieselben Delta-Schema-Enforcement-Fehler träten unabhängig davon auf, ob die Daten aus `read_files`, `spark.read` oder einer anderen Quelle stammen.

*(Quellen: `_read_files.md` Abschnitt 14, `_spark_read.md` Abschnitt 10)*

---

## <a id="vergleich">12. Werkzeugübergreifender Gesamtvergleich</a>

| Aspekt | `read_files` (Batch) | `STREAM read_files` / Auto Loader | `spark.read` (Batch) |
|---|---|---|---|
| Standard-Typinferenz | Exakte Typen (`inferColumnTypes = true`) | JSON/CSV/XML: `string`; Parquet/Avro: kodierte Typen | JSON: exakte Typen (automatisch); CSV: `string` (`inferSchema = false`) |
| `schemaHints` verfügbar? | Ja | Ja (`cloudFiles.schemaHints`) | **Nein** |
| Schema-Evolution über mehrere Läufe? | **Nein** (zustandslos) | Ja (5 Modi, siehe Abschnitt 5) | **Nein** (zustandslos) |
| `rescuedDataColumn` Standard | Aktiv bei Inferenz | Automatisch aktiv | **Inaktiv**, muss explizit gesetzt werden |
| `partitionColumns`-Einschränkung möglich? | Ja | Ja (`cloudFiles.partitionColumns`) | **Nein** (nur automatische Inferenz, keine Option) |
| Datei-Tracking/Exactly-once | **Nein** | Ja (RocksDB-Checkpoint) | **Nein** |
| `schemaLocation`/`_schemas`-Verzeichnis | Nur mit `STREAM` relevant | Ja | Nicht anwendbar |
| Type Widening | Nur mit `STREAM` (`addNewColumnsWithTypeWidening`) | Ja | Nicht verfügbar |

*(Zusammengeführt aus den Einzelvergleichen in `_read_files.md` Abschnitte 12/15, `_spark_read.md` Abschnitt 11, `06 Auto Loader/16 Auto Loader vs read_files vs COPY INTO.md`)*

---

## <a id="praxis-pattern">13. Praxis-Pattern: Resilientes Bronze-Layer-Design</a>

**Kein wörtliches Einzelzitat, sondern eine Kombination bereits einzeln verifizierter Fakten** zu einem in Praxis-/Kursmaterialien gängigen Bronze-Layer-Muster: Da Textformate (JSON, CSV, XML) ohne `cloudFiles.inferColumnTypes` standardmäßig als `string` inferiert werden (Abschnitt 1) und `schemaEvolutionMode => 'rescue'` bewirkt, dass sich das Schema nie weiterentwickelt und der Stream nicht wegen Schema-Änderungen fehlschlägt (Abschnitt 5), lässt sich die Bronze-Schicht so konfigurieren, dass kein Datensatz wegen eines Typ- oder Schema-Konflikts verworfen wird oder den Stream stoppt — die Typ-Durchsetzung wird bewusst auf die Silber-Schicht per `TRY_CAST` verschoben (liefert bei Cast-Fehlschlag `NULL` statt eines Fehlers):

```sql
-- Bronze: Schema eingefroren, rescue-Modus verhindert Stream-Abbruch bei Schema-Drift
CREATE OR REFRESH STREAMING TABLE bronze_events
COMMENT 'Bronze: rescue-Modus verhindert Stream-Abbruch bei Schema-Drift'
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'rescue'
);
```

```sql
-- Silver: Typ-Durchsetzung mit TRY_CAST statt hartem CAST
CREATE OR REFRESH STREAMING TABLE silver_events (
  CONSTRAINT valid_amount EXPECT (
    CASE WHEN amount IS NOT NULL THEN amount >= 0 ELSE TRUE END
  ) ON VIOLATION DROP ROW
)
AS SELECT *,
  TRY_CAST(amount_str AS DOUBLE) AS amount
FROM STREAM bronze_events;
```

**Ungeklärt/Einordnung:** Die Seite "Common data loading patterns with Auto Loader" beschreibt den Rescue-Modus zur Datenrettung bei einem **vordefinierten** Schema, aber **nicht** explizit die Kombination mit einer bewusst durchgängigen `STRING`-Bronze-Schicht. Das Muster ist damit eine plausible Anwendung einzeln verifizierter Bausteine, aber **keine** wörtlich zitierbare Einzelempfehlung von Databricks.

**Zusatzregel bei Constraints auf nachträglich hinzugekommenen Spalten:** Wird eine Spalte per Schema-Evolution oder `schemaHints` neu hinzugefügt, tragen alle davor eingelesenen Datensätze für diese Spalte `NULL` (Abschnitt 4). Ein `EXPECT`-Constraint auf einer solchen Spalte sollte daher NULL-tolerant formuliert werden (`CASE WHEN ... IS NOT NULL THEN ... ELSE TRUE END`), da sonst historische Datensätze fälschlich als Constraint-Verletzung markiert würden — eine plausible, aber nicht separat als eigenständiger Satz in der Doku gefundene Ableitung.

*(Quelle: `06 Auto Loader/14 Common Data Loading Patterns.md`, Praxis-Patterns)*

---

## <a id="quellen">14. Quellen</a>

Diese Datei führt ausschließlich bereits verifizierte Inhalte zusammen; es wurde keine neue Web-Recherche durchgeführt. Für die vollständige Liste der ursprünglich per `WebFetch` geprüften URLs (inkl. Zweitabrufen zur Gegenprüfung) siehe die Quellen-Abschnitte der drei Ausgangsdateien:

- `_read_files.md` Abschnitt 16 (Quellen)
- `_spark_read.md` Abschnitt 12 (Quellen)
- `06 Auto Loader/17 Quellen.md`

Zentrale, mehrfach referenzierte Einzelseiten darunter:

- read_files table-valued function: https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files
- Spark API options reference: https://docs.databricks.com/aws/en/spark/api-options
- Configure schema inference and evolution in Auto Loader: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema
- Automatic type widening with Auto Loader: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/type-widening
- Using Auto Loader with Unity Catalog: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/unity-catalog
- DataFrameReader class: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader
- schema (DataFrameReader): https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/schema
- Schema enforcement: https://docs.databricks.com/aws/en/tables/schema-enforcement
- Update Delta Lake table schema: https://docs.databricks.com/aws/en/delta/update-schema
- Error conditions in Databricks: https://docs.databricks.com/aws/en/error-messages/error-classes

**Stand:** 2026-08-18.
