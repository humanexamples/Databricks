# Datei-Ingestion-Szenarien — eine Taxonomie

Dieses Dokument ordnet Datei-Ingestion-Konstellationen in Databricks nach fünf unabhängigen Dimensionen und ordnet jeder das passende, gegen die offizielle Dokumentation verifizierte Muster zu. Die Einteilung in "Dimensionen" ist eine eigene Kategorisierung; die einzelnen Fakten sind jeweils belegt oder als eigene Einordnung gekennzeichnet.

## Abschnittsübersicht

1. [Dimension 1: Dateiname-Verhalten](#dateiname)
2. [Dimension 2: Verzeichnis-/Pfadstruktur](#verzeichnis)
3. [Dimension 3: Ankunftsfrequenz](#frequenz)
4. [Dimension 4: Schema-Stabilität über die Zeit](#schema-stabilitaet)
5. [Dimension 5: Update-Semantik der gelieferten Daten](#update-semantik)
6. [Kombinierbarkeit der Dimensionen](#kombinierbarkeit)
7. [Quellen](#quellen)

---

## <a id="dateiname">1. Dimension 1: Dateiname-Verhalten</a>

### a) Neuer, eindeutiger Dateiname pro Ankunft

Jede Datei erhält einen neuen, bisher ungesehenen Namen (z. B. UUID oder Zeitstempel), der Inhalt wird nie verändert — der Normalfall, für den Auto Loader/`STREAM read_files` konzipiert ist. Dateien werden anhand ihres Pfads verfolgt und bei Standardeinstellung (`cloudFiles.allowOverwrites = false`) exactly-once pro Pfad verarbeitet.

### b) Gleicher Dateiname, Inhalt wird bei jeder Lieferung überschrieben

Ein wiederkehrender Prozess schreibt periodisch (z. B. täglich) eine Datei mit demselben Namen neu, mit jeweils anderem Inhalt. Da Auto Loader Dateien per Pfad verfolgt, gilt ein bereits gesehener Pfad standardmäßig als abgeschlossen — neuer Inhalt wird ignoriert, sofern `cloudFiles.allowOverwrites` nicht auf `true` gesetzt ist. Bei aktivem `allowOverwrites` verarbeitet Auto Loader bei jeder Änderung die **gesamte** Datei erneut, nicht nur den geänderten Teil; Duplikate müssen dann selbst behandelt werden. Die Auto-Loader-FAQ empfiehlt daher, Auto Loader nur für unveränderliche Dateien zu nutzen und die Standardeinstellung beizubehalten.

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.allowOverwrites", "true")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .load("/Volumes/analytics/bronze/daily_drop"))
```

SQL-Äquivalent: `STREAM read_files` erbt Auto-Loader-Tracking-Optionen als benannte Argumente, `allowOverwrites` also direkt ohne `cloudFiles.`-Präfix (bereits in `_read_files.md` Abschnitt 7 verifiziert):

```sql
CREATE OR REFRESH STREAMING TABLE daily_drop_bronze
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/daily_drop',
  format => 'csv',
  allowOverwrites => true
);
```

### c) Gleicher Dateiname, Inhalt wird angehängt (wachsende Datei, z. B. Logdatei)

Eine Datei wächst kontinuierlich statt komplett ersetzt zu werden (z. B. eine Logdatei mit laufend angehängten Zeilen) — ein Sonderfall von (b). Auto Loader trackt nur ganze Dateien, keine Byte-Offsets: Mit `allowOverwrites => true` würde bei jedem Wachstum die komplette Datei erneut gelesen, wodurch bereits verarbeitete Zeilen ohne nachgelagerte Deduplizierung mehrfach in Bronze erscheinen. Da eine wachsende Datei per Definition nicht unveränderlich ist, empfiehlt sich Auto Loader dafür nicht — ein zweifacher Stichwort-Check der offiziellen "Common data loading patterns"-Seite ergab zudem keine Erwähnung von "append", "grow" oder "log file": Databricks behandelt dieses Szenario nicht als eigenes benanntes Muster.

#### Lösungswege für Fall c)

Eine wachsende Datei ist bei jedem Lesevorgang technisch ein vollständiger Snapshot des kumulativen Stands — nur unter demselben Pfad statt in nummerierten Einzeldateien. Drei verifizierte Lösungswege, je nach Werkzeug:

**1. Spark Declarative Pipelines mit `AUTO CDC FROM SNAPSHOT` (robustester Weg — Inserts/Updates/Deletes werden automatisch erkannt)**

`AUTO CDC FROM SNAPSHOT` liest bei jedem Pipeline-Lauf dieselbe Quelle komplett neu und vergleicht sie automatisch mit dem zuvor gelesenen Stand, um Inserts/Updates/Deletes zu ermitteln. Das offizielle Beispiel "Process snapshots using pipeline ingestion time" nutzt dafür eine Tabelle als Quelle; da nur ein DataFrame geliefert werden muss, lässt sich derselbe Aufbau direkt auf eine Datei übertragen:

```python
from pyspark import pipelines as dp

@dp.view(name="source")
def source():
  return spark.read.format("csv").option("header", True).load("/Volumes/main/landing/growing_log.csv")

dp.create_streaming_table("target")
dp.create_auto_cdc_from_snapshot_flow(
  target = "target",
  source = "source",
  keys = ["log_id"],
  stored_as_scd_type = 1)
```

Nur die Differenz zum vorherigen Snapshot — die neu hinzugekommenen Zeilen — wird auf die Zieltabelle angewendet, bereits verarbeitete Zeilen werden nicht dupliziert. Es werden nur Änderungen zwischen zwei aufeinanderfolgenden Snapshots erkannt, keine Zwischenzustände dazwischen — für eine reine Anhänge-Datei ohne Löschungen unkritisch, da nichts zwischenzeitlich verschwindet.

**SQL:** Für diesen Lösungsweg gibt es kein SQL-Äquivalent. Die SQL-Sprachreferenz für Lakeflow-Pipelines kennt nur `AUTO CDC INTO` für **streaming** Quellen ("The source must be a streaming source") — eine `FROM SNAPSHOT`-Variante ist dort nicht dokumentiert (zweifach geprüft: Index der SQL-Referenzseite listet ausschließlich "AUTO CDC INTO", die zugehörige Syntaxseite verlangt explizit eine Streaming-Quelle). `AUTO CDC FROM SNAPSHOT` ist damit auf Python beschränkt.

**2. `read_files` (SQL) + `MERGE INTO` mit eindeutigem Schlüssel (ohne Declarative Pipeline)**

Alternativ mit dem bereits verifizierten `MERGE INTO`-Deduplizierungsmuster: Die komplette Datei wird gelesen, aber nur Zeilen mit einem bisher unbekannten eindeutigen Schlüssel werden eingefügt:

```sql
MERGE INTO bronze_log_events AS target
USING (
  SELECT * FROM read_files('/Volumes/main/landing/growing_log.csv', format => 'csv', header => true)
) AS source
ON target.log_id = source.log_id
WHEN NOT MATCHED THEN INSERT *
```

Voraussetzung ist ein stabiler, eindeutiger Schlüssel pro Zeile (z. B. Log-ID oder Zeitstempel plus unterscheidende Felder) — sonst lässt sich "bereits verarbeitet" nicht zuverlässig feststellen.

**3. `spark.read` (Python/Batch) + `DeltaTable.merge()` — dieselbe Logik programmatisch**

Funktional identisch zu Lösungsweg 2, nur über die Python-`DeltaTable`-API statt SQL:

```python
from delta.tables import DeltaTable

source_df = (spark.read
  .format("csv")
  .option("header", True)
  .load("/Volumes/main/landing/growing_log.csv"))

target_table = DeltaTable.forName(spark, "bronze_log_events")
(target_table.alias("target")
  .merge(source_df.alias("source"), "target.log_id = source.log_id")
  .whenNotMatchedInsertAll()
  .execute())
```

**Einordnung:** Alle drei Wege bestehen aus einzeln verifizierten Bausteinen — Weg 1 aus einem offiziellen Doku-Beispiel abgeleitet, Wege 2/3 aus dem verifizierten `MERGE`-Deduplizierungsmuster. Eine explizite Databricks-Empfehlung "so lösen Sie das Problem einer wachsenden Datei" existiert nicht — wie oben festgestellt ist das kein offiziell benanntes Muster.

---

## <a id="verzeichnis">2. Dimension 2: Verzeichnis-/Pfadstruktur</a>

### a) Flaches Verzeichnis

Alle Dateien liegen ohne Partitionslogik in einem Verzeichnis. Einfachster Fall, keine Besonderheiten.

### b) Hive-Style-partitioniertes Verzeichnis

Die Verzeichnisstruktur kodiert Spaltenwerte als Schlüssel-Wert-Paare (`<base-path>/a=x/b=1/c=y/file.format`). `read_files`/Auto Loader erkennen solche Partitionsspalten automatisch bei der Schema-Inferenz; über `partitionColumns` lässt sich steuern, welche Ebenen übernommen werden — ein leerer String ignoriert alle Partitionsspalten.

```sql
SELECT * FROM read_files(
    '/Volumes/main/sales/raw',
    format => 'csv',
    partitionColumns => 'year,month');
```

**Python:** `partitionColumns` ist laut Spark-API-Optionsreferenz **kein** Batch-`DataFrameReader`-Parameter — dort taucht der Name nur als `read_files`-Parameter (SQL) bzw. als Auto-Loader-Streaming-Option `cloudFiles.partitionColumns` (DataStreamReader) auf. Reines `spark.read` inferiert Hive-Style-Partitionsspalten zwar automatisch aus dem Pfad, bietet aber keine Option, diese gezielt einzuschränken:

```python
df = spark.read.format("csv").load("/Volumes/main/sales/raw")
```

Dieselbe gezielte Einschränkung wie in SQL steht im Streaming-Kontext über Auto Loader direkt zur Verfügung:

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.partitionColumns", "year,month")
  .load("/Volumes/main/sales/raw"))
```

### c) Inkonsistente Verzeichnistiefe zwischen Lieferungen

Manche Dateien liegen nur unter `year=2022/week=1/...`, andere zusätzlich unter `year=2022/month=2/day=3/...`. `partitionColumns` erzwingt trotzdem ein einheitliches Schema: fehlende Ebenen werden `NULL`, vorhandene korrekt geparst.

---

## <a id="frequenz">3. Dimension 3: Ankunftsfrequenz</a>

### a) Viele kleine Dateien, unregelmäßig/hochfrequent

Z. B. ein IoT- oder Event-Export mit kontinuierlichem, unregelmäßigem Zustrom. Empfohlen: Auto Loader mit File Events (empfohlener File-Notification-Modus) — skaliert laut Doku auf nahezu Echtzeit-Ingestion von Millionen Dateien pro Stunde.

### b) Periodischer Batch-Drop

Ein großer Dump wird z. B. einmal pro Nacht abgelegt. Da kein Niedriglatenz-Bedarf besteht, reicht ein Scheduled-Trigger (Lakeflow-Pipeline) oder sogar reines Batch-`read_files`/`COPY INTO` ohne Streaming-Zustand.

### c) Einmaliger historischer Backfill

Migration oder Erstbefüllung mit einer sehr großen Menge historischer Dateien auf einen Schlag. Auto Loader ist dafür explizit dokumentiert und lässt sich für Milliarden Dateien zur Tabellen-Migration/-Befüllung (Backfill) einsetzen.

---

## <a id="schema-stabilitaet">4. Dimension 4: Schema-Stabilität über die Zeit</a>

### a) Schema komplett stabil

Keine Besonderheiten — Standard-Schema-Inferenz bzw. explizites Schema reicht aus.

### b) Additive Entwicklung (neue Spalten kommen im Lauf der Zeit hinzu)

Modus `schemaEvolutionMode => 'addNewColumns'` (Standard ohne angegebenes Schema): Der Stream stoppt bewusst mit einer `UnknownFieldException`, sobald eine neue Spalte auftaucht; der Schema-Speicherort wird vor dem Abbruch bereits aktualisiert, ein Neustart übernimmt das erweiterte Schema automatisch. Databricks empfiehlt, den Stream über Lakeflow Jobs zu konfigurieren, damit er danach automatisch neu startet.

### c) Typänderungen einer Spalte zwischen Lieferungen

Bei kompatiblen Typänderungen (z. B. `int` → `long`) erweitert `schemaEvolutionMode => 'addNewColumnsWithTypeWidening'` automatisch, ohne Daten neu zu schreiben (ab Databricks Runtime 16.4, Public Preview, zusätzlich `delta.enableTypeWidening` auf der Zieltabelle nötig). Bei inkompatiblen Änderungen (z. B. `int` → `string`) landet der Wert stattdessen in der Rescued-Data-Spalte.

### d) Chaotisches, unvorhersehbares Schema zwischen Dateien

Wenn verschiedene Upstream-Systeme strukturell abweichende Daten in denselben Ordner liefern, ist `schemaEvolutionMode => 'rescue'` das robusteste Muster: Das Schema entwickelt sich nie weiter, der Stream schlägt nie wegen Schema-Änderungen fehl, neue Spalten landen in der Rescued-Data-Spalte. Kombiniert mit einer durchgängigen `STRING`-Bronze-Schicht und `TRY_CAST`-Typdurchsetzung erst in Silver ergibt das ein resilientes Bronze-Layer-Muster (jeder Baustein einzeln belegt, keine eigenständige Doku-Empfehlung für genau diese Kombination).

```sql
CREATE OR REFRESH STREAMING TABLE bronze_events
COMMENT 'Bronze: rescue-Modus verhindert Stream-Abbruch bei Schema-Drift'
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'rescue'
);
```

Python-Äquivalent über Auto Loader direkt (bereits in `06 Auto Loader/01 Schema-Inferenz und -Evolution.md` verifiziert):

```python
query = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .option("cloudFiles.schemaEvolutionMode", "rescue")
  .load("/Volumes/analytics/bronze/events"))
```

---

## <a id="update-semantik">5. Dimension 5: Update-Semantik der gelieferten Daten</a>

Diese Dimension bestimmt in der Praxis oft stärker als das Dateiname-Verhalten (Dimension 1), welches Schreibmuster nach Bronze nötig ist.

### a) Reines Append

Jede Datei enthält ausschließlich neue, vorher ungesehene Zeilen. Einfachster Fall — Standard-Append-Schreiben in eine Streaming Table reicht aus.

### b) Vollständiger Snapshot bei jeder Lieferung

Jede Datei enthält den kompletten aktuellen Datenstand, nicht nur ein Delta. Naives Append würde den Datenbestand bei jedem Lauf duplizieren. Zwei mögliche, offiziell dokumentierte Muster, je nach Ziel:

- **Nur der aktuelle Stand wird gebraucht, keine Historie:** `REPLACE WHERE`/`REPLACE USING` beim Schreiben ersetzt betroffene Zeilen atomar, statt sie anzuhängen (siehe `_read_files.md`).
- **Änderungsverfolgung über die Zeit wird gebraucht:** `AUTO CDC FROM SNAPSHOT` ist dafür explizit vorgesehen — einsetzbar, wenn CDC im Quellsystem fehlt, nur periodische Snapshots (volle Tabellendumps) verfügbar sind, oder die Vorteile von CDC (inkrementelle Verarbeitung, volle Historie) trotzdem erreicht werden sollen. Als Snapshot-Quellen nennt die Doku explizit: periodische DB-Exporte, **Cloud-Speicher-Datei-Dumps von Upstream-Systemen**, Delta-Tabellenversionen und OpenSharing — der hier beschriebene Datei-Dump-Fall ist also eine ausdrücklich vorgesehene Quellkategorie. Der Snapshot-Parameter wird als Tabellen-/View-Name oder als Python-Lambda angegeben, das einen DataFrame plus Versionsnummer liefert — die Doku zeigt dafür ein Beispiel mit Dateizugriff:

```python
def next_snapshot_and_version(latest_snapshot_version):
    if latest_snapshot_version is None:
        return (spark.read.load("filename.csv"), 1)
    else:
        return None
```

**SQL:** Wie in Fall 1c) festgestellt, existiert für `AUTO CDC FROM SNAPSHOT` — einschließlich dieser Versions-Lambda-Variante — kein SQL-Äquivalent; die SQL-Sprachreferenz kennt nur `AUTO CDC INTO` für streaming Quellen. Dieser Lösungsweg ist auf Python beschränkt.

### c) CDC/Change-Feed

Jede Lieferung enthält nur Insert-/Update-/Delete-Operationen seit der letzten Lieferung, nicht den vollen Datenbestand. Dafür sind `AUTO CDC` (SCD Typ 1: nur aktueller Stand, überschreibt) bzw. SCD Typ 2 (vollständige Historie mit `__START_AT`/`__END_AT`-Zeitstempeln) vorgesehen.

### d) Multi-Source, ein gemeinsames Ziel

Mehrere unabhängige Quellordner/-systeme (z. B. `orders/us`, `orders/eu`, `orders/apac`) sollen in dieselbe Zieltabelle einfließen. Statt `UNION` in einer Abfrage empfiehlt Databricks für jede Quelle einen eigenen `CREATE FLOW`, der unabhängig in dieselbe Ziel-Streaming-Table schreibt — jeder Flow führt seinen eigenen Auto-Loader-Zustand (Checkpoint, Datei-Tracking); ein neuer Flow lässt sich nachträglich ergänzen, ohne bestehende Flows oder die Zieltabelle neu aufzubauen.

```sql
CREATE OR REFRESH STREAMING TABLE raw_orders;

CREATE FLOW raw_orders_us
AS INSERT INTO raw_orders BY NAME
SELECT * FROM STREAM read_files("/path/to/orders/us", format => "csv");

CREATE FLOW raw_orders_eu
AS INSERT INTO raw_orders BY NAME
SELECT * FROM STREAM read_files("/path/to/orders/eu", format => "csv");
```

Python-Äquivalent von derselben Doku-Seite (zweifach abgerufen, identischer Code in beiden Abrufen):

```python
dp.create_streaming_table("raw_orders")

@dp.append_flow(target="raw_orders")
def raw_orders_us():
  return (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .load("/path/to/orders/us"))

@dp.append_flow(target="raw_orders")
def raw_orders_eu():
  return (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "csv")
    .load("/path/to/orders/eu"))
```

---

## <a id="kombinierbarkeit">6. Kombinierbarkeit der Dimensionen</a>

Die fünf Dimensionen sind unabhängig kombinierbar — ein konkretes Ingestion-Szenario ergibt sich erst aus der Kombination aller fünf, nicht aus einer einzelnen Achse. Zwei Beispiele zur Illustration:

- "Gleicher Dateiname, überschrieben" (Dimension 1b) **plus** "vollständiger Snapshot" (Dimension 5b) → `allowOverwrites => true` **und** `AUTO CDC FROM SNAPSHOT` bzw. `REPLACE WHERE`, je nachdem ob Historie gebraucht wird.
- "Gleicher Dateiname, überschrieben" (Dimension 1b) **plus** "reines Append" (Dimension 5a) ist ein Widerspruch: Kommen inhaltlich nur neue Zeilen hinzu, handelt es sich eigentlich um Dimension 1c (wachsende Datei), nicht 1b.

Die Dateiname-Konstellation allein (Dimension 1) legt also **nicht** automatisch das richtige Schreibmuster fest — erst zusammen mit der Update-Semantik (Dimension 5) ergibt sich die vollständige Handlungsanweisung.

---

## <a id="quellen">7. Quellen</a>

- Auto Loader FAQ (Immutabilitäts-Empfehlung, `allowOverwrites`-Verhalten): https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/faq.html
- Common data loading patterns with Auto Loader (geprüft auf "snapshot"/"append"/"overwrite" — keine Treffer): https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/patterns
- Change data capture (CDC) in Databricks — `AUTO CDC FROM SNAPSHOT`, Snapshot-Quellkategorien: https://docs.databricks.com/aws/en/data-engineering/what-is-cdc
- APPLY CHANGES FROM SNAPSHOT / `apply_changes_from_snapshot`-Syntaxreferenz (Lambda-Funktions-Beispiel): https://docs.databricks.com/aws/en/dlt-ref/dlt-python-ref-apply-changes-from-snapshot
- Change data capture with Lakeflow Declarative Pipelines (vollständige Code-Beispiele "Process snapshots using pipeline ingestion time" / "using version functions", Basis für Lösungsweg 1 in Fall 1c): https://docs.databricks.com/aws/en/ldp/cdc
- Pipeline SQL language reference (Index aller SQL-Statements für Lakeflow-Pipelines — Beleg dafür, dass nur "AUTO CDC INTO" existiert, keine "FROM SNAPSHOT"-Variante): https://docs.databricks.com/aws/en/ldp/developer/sql-ref
- AUTO CDC INTO (SQL-Syntaxreferenz, "The source must be a streaming source"): https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-apply-changes-into
- CREATE FLOW (SQL-Syntaxreferenz): https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-flow
- Use flows in Lakeflow pipelines (Multi-Flow-Beispielcode `raw_orders_us`/`eu`/`apac` in SQL **und** Python, `@dp.append_flow`, zweifach abgerufen): https://docs.databricks.com/aws/en/ldp/flow-examples
- Spark API options reference (Beleg, dass `partitionColumns` kein Batch-`DataFrameReader`-Parameter ist): https://docs.databricks.com/aws/en/spark/api-options
- Configure Auto Loader options (exakter Optionsname `cloudFiles.partitionColumns`): https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options
- Details zu `partitionColumns`, `schemaEvolutionMode`, `REPLACE WHERE`/`REPLACE USING`: `_read_files.md` (dieser Ordner)
- Details zu `allowOverwrites`, Type Widening, File Events, Multi-Flow-Pattern, resilientes Bronze-Layer-Design: Ordner `06 Auto Loader/` (dieser Ordner)

**Stand:** 2026-08-18. Die Kernfakten dieses Dokuments wurden im Verlauf dieser Session bereits einzeln (teils mehrfach, AWS- und Azure-Spiegelseite) verifiziert; die `AUTO CDC FROM SNAPSHOT`-Quellkategorien, das Datei-Lambda-Beispiel sowie die neu ergänzten Python-/SQL-Gegenstücke der Code-Beispiele wurden zusätzlich gezielt für dieses Dokument nachrecherchiert (teils zweifach gegengeprüft) und korrigieren eine frühere, an einer falschen Quellseite geprüfte Zwischenversion.
