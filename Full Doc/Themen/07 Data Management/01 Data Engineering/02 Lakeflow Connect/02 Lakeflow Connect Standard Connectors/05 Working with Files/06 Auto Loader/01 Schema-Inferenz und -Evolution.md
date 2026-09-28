# Auto Loader — Schema-Inferenz und -Evolution

Quelle: [Configure schema inference and evolution in Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema).
Auto Loader ermöglicht automatische Schema-Erkennung, sodass eine Tabelle ohne explizite Schema-Deklaration initialisiert werden kann; Schema-Evolution wird unterstützt, während neue Spalten auftauchen. Zusätzlich "rettet" die Funktion unerwartete Daten in einer JSON-Blob-Spalte.

## Abschnitte

1. [Syntax zur Aktivierung](#syntax)
2. [Schema-Inferenz](#schema-inferenz)
3. [`schemaHints`](#schemahints)
4. [Schema-Evolution-Modi](#schema-evolution-modi)
5. [Partitionsspalten](#partitionsspalten)
6. [Rescued-Data-Column bei Auto Loader](#rescued-data)
7. [FAQ-Ergänzungen zur Schema-Inferenz](#faq)

---

## <a id="syntax">1. Syntax zur Aktivierung</a>

Schema-Inferenz und -Evolution werden aktiviert, indem ein Zielverzeichnis für `cloudFiles.schemaLocation` angegeben wird. Es darf dasselbe Verzeichnis wie `checkpointLocation` sein. In Lakeflow-Pipelines verwaltet Databricks dies automatisch.

> **Hinweis:** Mehrere Quelldaten-Speicherorte benötigen separate Streaming-Checkpoints je Auto-Loader-Workload.

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "parquet")
  # The schema location directory keeps track of your data schema over time
  .option("cloudFiles.schemaLocation", "<path-to-schema>")
  .load("<path-to-source-data>")
  .writeStream
  .option("checkpointLocation", "<path-to-checkpoint>")
  .start("<path-to-target>"))
```

### Unterstützte Formate für Schema-Inferenz und -Evolution

| Dateiformat | Unterstützte Versionen |
|---|---|
| `JSON` | Alle Versionen |
| `CSV` | Alle Versionen |
| `XML` | Ab Databricks Runtime 14.3 LTS |
| `Avro` | Ab Databricks Runtime 10.4 LTS |
| `Parquet` | Ab Databricks Runtime 11.3 LTS |
| `ORC` | Nicht unterstützt |
| `Text` | Nicht anwendbar (festes Schema) |
| `Binaryfile` | Nicht anwendbar (festes Schema) |

---

## <a id="schema-inferenz">2. Schema-Inferenz</a>

### Stichprobengröße

Um beim ersten Lesen der Daten das Schema zu inferieren, sampelt Auto Loader die ersten **50 GB oder 1000 Dateien**, die es entdeckt, je nachdem, welches Limit zuerst erreicht wird. Auto Loader speichert die Schema-Information anschließend in einem Verzeichnis `_schemas` am konfigurierten `cloudFiles.schemaLocation`-Pfad.

Die Stichprobengröße lässt sich über zwei SQL-Konfigurationen anpassen:

```sql
SET spark.databricks.cloudFiles.schemaInference.sampleSize.numBytes = '10gb';
SET spark.databricks.cloudFiles.schemaInference.sampleSize.numFiles = 500;
```

**Ergänzung aus der FAQ:** Beim erstmaligen Definieren des DataFrames listet Auto Loader das Quellverzeichnis auf und wählt die *neuesten* (nach Dateiänderungszeitpunkt) 50 GB bzw. 1000 Dateien für die Inferenz aus — es handelt sich also um eine nach Aktualität sortierte Stichprobe.

### Standardverhalten je Format

| Dateiformat | Standard-Inferenztyp |
|---|---|
| `JSON` | String |
| `CSV` | String |
| `XML` | String |
| `Avro` | Im Avro-Schema kodierte Typen |
| `Parquet` | Im Parquet-Schema kodierte Typen |

- **JSON, CSV, XML (Formate ohne kodierte Datentypen):** Auto Loader inferiert standardmäßig **alle** Spalten als `string` (auch verschachtelte Felder in JSON-Dateien) — bewusst so gewählt, um Schema-Evolution-Probleme durch Typkonflikte zu vermeiden.

  - Der Apache-Spark-`DataFrameReader` wählt Datentypen anhand von Stichprobendaten. Um dieses Verhalten mit Auto Loader zu aktivieren, wird `cloudFiles.inferColumnTypes` auf `true` gesetzt (Standardwert **`false`**). Das ist das **Gegenteil** des Standardwerts von `read_files`s `inferColumnTypes` (dort `true`).

    ```python
    df = (spark.readStream
          .format("cloudFiles")
          .option("cloudFiles.format", "csv")
          .option("cloudFiles.inferColumnTypes", True)
          .option("cloudFiles.schemaLocation",
                  "/Volumes/analytics/bronze/_schema")
          .load("/Volumes/analytics/bronze/csv_data"))
    ```

  - **CSV-Header:** Bei der Schema-Inferenz für CSV-Daten geht Auto Loader davon aus, dass die Dateien Header enthalten. Enthalten die CSV-Dateien keine Header, muss `.option("header", "false")` gesetzt werden.

  - **CSV-Schema-Merge:** Auto Loader führt die Schemata aller Dateien in der Stichprobe zu einem globalen Schema zusammen.

- **Parquet, Avro (Formate mit typisiertem Schema):** Auto Loader sampelt eine Teilmenge der Dateien und führt deren Einzelschemas zusammen.

  - **Parquet-Typkonflikte:** Hat eine Spalte in zwei Parquet-Dateien unterschiedliche Datentypen, wählt Auto Loader den breitesten Typ. `schemaHints` kann verwendet werden, um diese Wahl zu überschreiben. Werden Schema Hints angegeben, castet Auto Loader die Spalte nicht auf den angegebenen Typ, sondern weist den Parquet-Reader an, die Spalte als den angegebenen Typ zu lesen. Bei einem Konflikt rettet Auto Loader die Spalte in die Rescued-Data-Spalte.

### Wann wird das Schema inferiert?

Das Schema wird inferiert, wenn der DataFrame im Code erstmals definiert wird. Während jedes Micro-Batches werden Schema-Änderungen dynamisch ("on the fly") ausgewertet — es findet also keine vollständige Neu-Inferenz bei jedem Batch statt, sondern eine fortlaufende Prüfung auf neue Spalten gegenüber dem einmal inferierten Ausgangsschema.

---

## <a id="schemahints">3. `schemaHints`</a>

**Auto Loader verwendet Schema Hints nur, wenn kein Schema angegeben wird.** Schema Hints lassen sich unabhängig davon verwenden, ob `cloudFiles.inferColumnTypes` aktiviert oder deaktiviert ist.

Ist eine Spalte zu Beginn des Streams nicht vorhanden, können Sie Schema Hints auch verwenden, um diese Spalte dem inferierten Schema hinzuzufügen. Das erlaubt, Spalten, die erst in künftigen Dateien auftauchen werden, bereits vorab zu deklarieren.

Sie können Schema Hints verwenden, um bekannte und erwartete Schema-Informationen auf einem inferierten Schema durchzusetzen. Wenn Sie einen allgemeineren Datentyp wählen möchten (zum Beispiel ein `double` statt eines `integer`), können Sie eine beliebige Anzahl von Hints für Spaltendatentypen als String angeben, unter Verwendung der SQL-Schema-Spezifikationssyntax:

```python
.option("cloudFiles.schemaHints", "tags map<string,string>, version int")
```

Für die Liste der unterstützten Datentypen verweist die Doku auf die allgemeine Sprach-Mapping-Referenz ("Language mappings").

### Beispiel 1 — Verschachtelte Felder: Structs und Maps

Ausgangsschema (inferiert):

```
|-- date: string
|-- quantity: int
|-- user_info: struct
|    |-- id: string
|    |-- name: string
|    |-- dob: string
|-- purchase_options: struct
|    |-- delivery_address: string
```

Angewendete Schema Hints:

```python
.option("cloudFiles.schemaHints", "date DATE, user_info.dob DATE, purchase_options MAP<STRING,STRING>, time TIMESTAMP")
```

Ergebnis:

```
|-- date: string -> date
|-- quantity: int
|-- user_info: struct
|    |-- id: string
|    |-- name: string
|    |-- dob: string -> date
|-- purchase_options: struct -> map<string,string>
|-- time: timestamp
```

### Beispiel 2 — Arrays und weitere verschachtelte Typen

Ausgangsschema (inferiert):

```
|-- products: array<string>
|-- locations: array<string>
|-- users: array<struct>
|    |-- users.element: struct
|    |    |-- id: string
|    |    |-- name: string
|    |    |-- dob: string
|-- ids: map<string,string>
|-- names: map<string,string>
|-- prices: map<string,string>
|-- discounts: map<struct,string>
|    |-- discounts.key: struct
|    |    |-- id: string
|    |-- discounts.value: string
|-- descriptions: map<string,struct>
|    |-- descriptions.key: string
|    |-- descriptions.value: struct
|    |    |-- content: int
```

Angewendete Schema Hints (Punktnotation für verschachtelte Felder, `.element` für Array-Elemente, `.key`/`.value` für Map-Einträge):

```python
.option("cloudFiles.schemaHints", "products ARRAY<INT>, locations.element STRING, users.element.id INT, ids MAP<STRING,INT>, names.key INT, prices.value INT, discounts.key.id INT, descriptions.value.content STRING")
```

Ergebnis:

```
|-- products: array<string> -> array<int>
|-- locations: array<int> -> array<string>
|-- users: array<struct>
|    |-- users.element: struct
|    |    |-- id: string -> int
|    |    |-- name: string
|    |    |-- dob: string
|-- ids: map<string,string> -> map<string,int>
|-- names: map<string,string> -> map<int,string>
|-- prices: map<string,string> -> map<string,int>
|-- discounts: map<struct,string>
|    |-- discounts.key: struct
|    |    |-- id: string -> int
|    |-- discounts.value: string
|-- descriptions: map<string,struct>
|    |-- descriptions.key: string
|    |-- descriptions.value: struct
|    |    |-- content: int -> string
```

Die Unterstützung für Array- und Map-Schema-Hints ist ab **Databricks Runtime 9.1 LTS** verfügbar.

### Praxisbeispiel: Vorab-Deklaration künftiger Spalten

Eine per `schemaHints` vorab deklarierte, aber noch nicht vorhandene Spalte ist von Beginn an Teil des Schemas; alte Datensätze erhalten für sie `NULL`, neue Datensätze befüllen sie automatisch, sobald das Feld in den Quelldaten auftaucht (rückwärts- und vorwärtskompatibel). Diese Interpretation folgt aus dem allgemein bekannten Verhalten fehlender Spalten in Parquet/Delta, wurde aber **nicht wörtlich** als eigenständige Aussage auf der Schema-Seite gefunden.

```sql
-- Neue Spalten vorab deklarieren, damit alte Datensätze NULL erhalten
-- und neue automatisch befüllt werden
CREATE OR REFRESH STREAMING TABLE bronze_events
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaHints => 'loyalty_tier STRING, region_code STRING'
);
```

**Ungeklärt:** Löst eine so vorab deklarierte Spalte, sobald sie tatsächlich in den Daten auftaucht, unter `addNewColumns` noch eine `UnknownFieldException` aus — oder verhindert die Vorab-Deklaration diesen Fehlschlag? Die Doku klärt das nicht.

### Zusammenspiel mit Schema-Evolution

`schemaHints` und Schema-Evolution sind nicht unabhängig voneinander. Auto Loader verwendet Schema Hints nur, wenn kein `schema`-Parameter angegeben ist. Da der Evolution-Modus `none` genau dann Standard ist, wenn ein Schema angegeben wird, schließen sich `schemaHints` und Modus `none` im jeweiligen Standardfall gegenseitig aus.

*"`addNewColumns` ist nicht erlaubt, wenn das Schema des Streams angegeben wird, funktioniert aber, wenn das Schema als Schema Hint angegeben wird."* — Ein expliziter `schema`-Parameter würde `addNewColumns` blockieren (weil dann automatisch `none` greift). Übergibt man dieselbe Typinformation stattdessen über `schemaHints`, bleibt `addNewColumns` weiterhin nutzbar.

---

## <a id="schema-evolution-modi">4. Schema-Evolution-Modi</a>

Auto Loader erkennt das Hinzufügen neuer Spalten, während es Daten verarbeitet. Erkennt Auto Loader eine neue Spalte, stoppt der Stream mit einer `UnknownFieldException`. Bevor der Stream diesen Fehler wirft, führt Auto Loader eine Schema-Inferenz auf dem neuesten Micro-Batch durch und aktualisiert den Schema-Speicherort mit dem neuesten Schema, indem neue Spalten an das Ende des Schemas angefügt werden. Die Datentypen bestehender Spalten bleiben unverändert.

Über `cloudFiles.schemaEvolutionMode` lässt sich steuern, wie mit neu auftauchenden Spalten in nachfolgenden Micro-Batches umgegangen wird:

| Modus | Verhalten laut Doku |
|---|---|
| `addNewColumns` (Standard **ohne** angegebenes Schema) | Der Stream schlägt mit `UnknownFieldException` fehl, nachdem Auto Loader die neuen Spalten zum Schema hinzugefügt hat. Ein Neustart setzt die Verarbeitung mit dem aktualisierten Schema fort. Die Datentypen bestehender Spalten entwickeln sich nicht weiter. |
| `addNewColumnsWithTypeWidening` | Gleiches Verhalten wie `addNewColumns`, aber Auto Loader erweitert zusätzlich unterstützte Datentypen (z. B. `int` zu `long`). Nicht unterstützte Typänderungen (z. B. `int` zu `string`) werden der Rescued-Data-Spalte hinzugefügt. Siehe [02 Automatisches Type Widening.md](02%20Automatisches%20Type%20Widening.md). |
| `rescue` | Auto Loader entwickelt das Schema nie weiter, und der Stream schlägt nicht wegen Schema-Änderungen fehl. Alle neuen Spalten werden in der Rescued-Data-Spalte aufgezeichnet. |
| `failOnNewColumns` | Der Stream schlägt fehl und startet nicht neu, es sei denn, das bereitgestellte Schema wird aktualisiert oder die betroffene Datendatei entfernt. Das Schema wird nicht automatisch aktualisiert. |
| `none` (Standard, **wenn** ein Schema angegeben ist) | Entwickelt das Schema nicht weiter, neue Spalten werden ignoriert, und Daten werden nicht gerettet, sofern nicht die Option `rescuedDataColumn` gesetzt ist. Der Stream schlägt nicht wegen Schema-Änderungen fehl. |

**Wörtlich bestätigte Zusatzregel:** `addNewColumns` ist der Standard, wenn kein Schema angegeben wird; `none` ist der Standard, wenn ein Schema angegeben wird. `addNewColumns` ist nicht erlaubt, wenn das Schema des Streams angegeben wird, funktioniert aber, wenn das Schema als Schema Hint angegeben wird.

```python
query = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
  .option("cloudFiles.schemaEvolutionMode", "rescue")
  .load("/Volumes/analytics/bronze/events"))
```

```sql
-- Äquivalent über STREAM read_files
CREATE OR REFRESH STREAMING TABLE events_rescue_only
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',
  format => 'json',
  schemaEvolutionMode => 'rescue'
);
```

Databricks empfiehlt ausdrücklich, den Stream über Lakeflow Jobs zu konfigurieren, damit er nach Schema-Änderungen (`UnknownFieldException`) automatisch neu startet.

---

## <a id="partitionsspalten">5. Partitionsspalten</a>

Auto Loader versucht, Partitionsspalten aus der zugrunde liegenden Verzeichnisstruktur zu inferieren, sofern die Daten im Hive-Stil partitioniert abgelegt sind. Beispiel: Der Dateipfad `base_path/event=click/date=2021-04-01/f0.json` führt zur Inferenz von `date` und `event` als Partitionsspalten. Enthält die Verzeichnisstruktur widersprüchliche Hive-Partitionen oder liegt keine Hive-Style-Partitionierung vor, ignoriert Auto Loader Partitionsspalten.

Binärdatei- (`binaryFile`) und `text`-Dateiformate haben feste Datenschemata, unterstützen aber Partitionsspalten-Inferenz. Databricks empfiehlt, für diese Dateiformate `cloudFiles.schemaLocation` zu setzen, um Fehler oder Informationsverlust zu vermeiden und die wiederholte Inferenz von Partitionsspalten bei jedem Auto-Loader-Start zu verhindern.

**Wichtig:** Auto Loader berücksichtigt Partitionsspalten **nicht** bei der Schema-Evolution. Gab es zunächst eine Verzeichnisstruktur wie `base_path/event=click/date=2021-04-01/f0.json` und treffen anschließend neue Dateien als `base_path/event=click/date=2021-04-01/hour=01/f1.json` ein, ignoriert Auto Loader die Spalte `hour`. Um Informationen für neue Partitionsspalten zu erfassen, muss `cloudFiles.partitionColumns` auf `event,date,hour` gesetzt werden. Die Option nimmt eine kommagetrennte Liste von Spaltennamen entgegen; Auto Loader parst dabei nur Spalten, die als `key=value`-Paare in der Verzeichnisstruktur vorliegen.

---

## <a id="rescued-data">6. Die Rescued-Data-Column bei Auto Loader</a>

> Ausführliche werkzeugübergreifende Behandlung: [`../05 Diagnose- und Herkunftsspalten/_rescued_data.md`](../05%20Diagnose-%20und%20Herkunftsspalten/_rescued_data.md). Hier nur die Auto-Loader-spezifischen Aspekte.

Wenn Auto Loader das Schema inferiert, fügt es dem Schema automatisch eine Rescued-Data-Spalte als `_rescued_data` hinzu. Die Spalte kann umbenannt oder in ein explizit angegebenes Schema aufgenommen werden, über die Option `rescuedDataColumn`. **Wichtiger Unterschied zu `spark.read`:** Bei Auto Loader wird die Spalte bei Schema-Inferenz **automatisch** hinzugefügt — bei `spark.read` (`DataFrameReader`) ist `rescuedDataColumn` dagegen standardmäßig **aus**.

### Was landet in der Rescued-Data-Spalte?

Die Rescued-Data-Spalte stellt sicher, dass Auto Loader Spalten rettet, die nicht mit dem Schema übereinstimmen, statt sie zu verwerfen. Sie enthält Daten, die aus folgenden Gründen nicht geparst wurden:

- Die Spalte fehlt im Schema.
- Typ-Konflikte.
- Konflikte bei Groß-/Kleinschreibung.

Die Spalte enthält ein JSON-Blob mit den geretteten Spalten sowie dem Quelldateipfad des Datensatzes.

**Zusätzliches Szenario:** Datensätze mit leeren Struct-Typen (null Felder) in Avro und JSON werden in `_rescued_data` umgeleitet (Parquet verbietet leere Structs).

### Zusammenspiel mit den Parser-Modi

Die JSON- und CSV-Parser unterstützen beim Parsen von Datensätzen drei Modi: `PERMISSIVE`, `DROPMALFORMED` und `FAILFAST`. In Kombination mit `rescuedDataColumn` führen Typ-Konflikte nicht dazu, dass Auto Loader Datensätze im Modus `DROPMALFORMED` verwirft oder im Modus `FAILFAST` einen Fehler wirft. Nur beschädigte (corrupt) Datensätze schlagen fehl oder werfen Fehler, etwa unvollständiges oder fehlerhaft formatiertes JSON oder CSV. Wird `badRecordsPath` beim Parsen von JSON oder CSV verwendet, behandelt Auto Loader Typkonflikte bei aktivierter `rescuedDataColumn` nicht als "bad records" — dort werden ausschließlich unvollständige und fehlerhaft formatierte JSON- oder CSV-Datensätze gespeichert.

### Groß-/Kleinschreibung

Ohne aktivierte Case-Sensitivity behandelt Auto Loader die Spalten `abc`, `Abc` und `ABC` für Zwecke der Schema-Inferenz als dieselbe Spalte; Auto Loader wählt die tatsächlich verwendete Schreibweise arbiträr anhand der Stichprobendaten. `schemaHints` kann verwendet werden, um festzulegen, welche Schreibweise verwendet werden soll.

Ist die Rescued-Data-Spalte aktiv, lädt Auto Loader Felder, deren Schreibweise von der des Schemas abweicht, in die `_rescued_data`-Spalte. Dieses Verhalten lässt sich über `readerCaseSensitive => false` ändern, wodurch Auto Loader Daten case-insensitiv liest.

### `columnNameOfCorruptRecord` statt `badRecordsPath`

Databricks empfiehlt `columnNameOfCorruptRecord` gegenüber `badRecordsPath`, um mögliche Race Conditions zu vermeiden, die beschädigte Datensätze übersehen können.

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaHints", "_corrupt_record string")
  .option("columnNameOfCorruptRecord", "_corrupt_record")
  .load("/Volumes/analytics/bronze/events"))
```

---

## <a id="faq">7. FAQ-Ergänzungen zur Schema-Inferenz</a>

- **Performance-Einfluss:** Bei sehr großen Quellverzeichnissen kann die initiale Schema-Inferenz einige Minuten dauern.
- **Leeres Quellverzeichnis:** Ist das Quellverzeichnis leer, verlangt Auto Loader die Angabe eines Schemas, da keine Daten zur Inferenz vorhanden sind.
- **Fehlerhafte Datei hat das Schema drastisch verändert:** Der Databricks-Support sollte kontaktiert werden, um eine Schema-Änderung rückgängig zu machen.
