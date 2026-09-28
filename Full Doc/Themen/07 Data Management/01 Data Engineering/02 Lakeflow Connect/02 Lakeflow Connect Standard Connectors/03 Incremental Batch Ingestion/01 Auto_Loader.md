# Inkrementelle Verarbeitung

## 1. Was ist Auto Loader?

Auto Loader verarbeitet neue Datendateien inkrementell und effizient, sobald sie in Cloud-Speicher eintreffen — ohne zusätzliche Einrichtung. Technisch ist Auto Loader eine **Structured-Streaming-Quelle** namens **`cloudFiles`**: Bei einem angegebenen Eingabeverzeichnispfad im Cloud-Dateispeicher verarbeitet die `cloudFiles`-Quelle automatisch neue Dateien, sobald sie eintreffen, optional auch bereits vorhandene Dateien im Verzeichnis.



### Python (PySpark)

```python
df = (
    spark.readStream
    # --- Format (Abschnitt 13) ---
    .format("cloudFiles")
    .option("cloudFiles.format", "json")                       # json, csv, xml, text, binaryFile, parquet, avro, orc

    # --- Datei-Erkennungsmodus (Abschnitt 5) ---
    .option("cloudFiles.useNotifications", "false")             # false = Directory Listing (Standard), true = File Notification

    # --- Schema-Inferenz und schemaHints (Abschnitt 6) ---
    .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
    .option("cloudFiles.schemaHints", "id int, amount double")
    .option("cloudFiles.inferColumnTypes", "true")

    # --- Schema-Evolution (Abschnitt 7) ---
    .option("cloudFiles.schemaEvolutionMode", "addNewColumns")  # addNewColumns | rescue | failOnNewColumns | none | addNewColumnsWithTypeWidening

    # --- Rescued-Data-Spalte (Abschnitt 8) ---
    .option("rescuedDataColumn", "_rescued_data")

    # --- Datei-Tracking (Abschnitt 9) ---
    .option("cloudFiles.allowOverwrites", "false")
    .option("cloudFiles.includeExistingFiles", "true")
    .option("cloudFiles.maxFileAge", "90 days")

    # --- Datenretention (Abschnitt 11) ---
    .option("cloudFiles.cleanSource", "MOVE")
    .option("cloudFiles.cleanSource.moveDestination", "/Volumes/analytics/bronze/_archive")

    # --- Micro-Batch-Größe (Streaming-Option) ---
    .option("cloudFiles.maxFilesPerTrigger", "1000")
    .option("cloudFiles.maxBytesPerTrigger", "1g")

    # --- Quellpfad (load) ---
    .load("/Volumes/analytics/bronze/events")
)

(
    df.writeStream
    .format("delta")                                            # Ziel-Format
    .option("checkpointLocation", "/Volumes/analytics/bronze/_checkpoint")
    .outputMode("append")                                        # append | update | complete
    .trigger(availableNow=True)                                  # availableNow | processingTime | once | continuous
    .table("workspace.default.events_delta")                     # Ziel: Tabelle (alternativ: .start(path) für Pfad-Sink)
)
```

### SQL (über `read_files` mit `STREAM`-Schlüsselwort)

Wenn `read_files` in einer `CREATE STREAMING TABLE`-Anweisung innerhalb von Lakeflow-Pipelines verwendet wird, werden Checkpoint- und Schema-Speicherorte automatisch verwaltet.

### Zuordnung Wort für Wort

| Teil                                              | Gehört zu       | Rolle                                                        |
| ------------------------------------------------- | --------------- | ------------------------------------------------------------ |
| `CREATE OR REFRESH STREAMING TABLE orders_bronze` | **SDP**         | Erzeugt/aktualisiert das Ziel-Dataset, das SDP als Streaming Table verwaltet und orchestriert |
| `SELECT * FROM STREAM`                            | **SDP**         | `STREAM` signalisiert dem SDP-Flow-Mechanismus, die Quelle inkrementell zu lesen |
| `read_files('..', format => 'json')`              | **Auto Loader** | Die eigentliche Leselogik — läuft intern über `cloudFiles`, mit RocksDB-Checkpoint, Tracking etc. |

```sql
CREATE OR REFRESH STREAMING TABLE workspace.default.events_delta
COMMENT 'Auto-Loader-Ingestion mit vollständiger Optionsübersicht'
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/analytics/bronze/events',

  -- Format (Abschnitt 13)
  format => 'json',                                  -- json, csv, xml, text, binaryFile, parquet, avro, orc

  -- Datei-Erkennungsmodus (Abschnitt 5)
  `cloudFiles.useNotifications` => 'false',           -- false = Directory Listing (Standard), true = File Notification

  -- Schema-Inferenz und schemaHints (Abschnitt 6)
  schemaHints => 'id int, amount double',
  inferColumnTypes => true,

  -- Schema-Evolution (Abschnitt 7)
  schemaEvolutionMode => 'addNewColumns',             -- addNewColumns | rescue | failOnNewColumns | none | addNewColumnsWithTypeWidening

  -- Datei-Tracking (Abschnitt 9)
  allowOverwrites => false,
  includeExistingFiles => true,
  `cloudFiles.maxFileAge` => '90 days',

  -- Datenretention (Abschnitt 11)
  `cloudFiles.cleanSource` => 'MOVE',
  `cloudFiles.cleanSource.moveDestination` => '/Volumes/analytics/bronze/_archive',

  -- Micro-Batch-Größe (Streaming-Option)
  maxFilesPerTrigger => 1000,
  maxBytesPerTrigger => '1g'
);
```

**Hinweis:** Nicht jede hier gezeigte Option muss gleichzeitig gesetzt werden — in der Praxis wählt man nur die für den eigenen Anwendungsfall relevanten Optionen aus (siehe die jeweiligen Abschnitte für Details und Standardwerte). Optionen mit Punkten im Namen (z. B. `cloudFiles.maxFileAge`) müssen in SQL laut Doku in Backticks gesetzt werden, während die über `read_files` direkt geerbten Auto-Loader-Optionen (`schemaHints`, `schemaEvolutionMode`, `allowOverwrites`, `includeExistingFiles`, `maxFilesPerTrigger`, `maxBytesPerTrigger`) ohne Präfix und ohne Backticks angegeben werden.

---

## 2. Grundsyntax in PySpark

Auto Loader wird über `spark.readStream.format("cloudFiles")` angesprochen. Optionen mit dem `cloudFiles.`-Präfix konfigurieren das Verhalten der Quelle.

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .load("/Volumes/analytics/bronze/events"))

(df.writeStream
   .format("delta")
   .option("checkpointLocation", "/Volumes/analytics/bronze/_checkpoint")
   .trigger(availableNow=True)
   .table("workspace.default.events_delta"))
```

Die Option `cloudFiles.schemaLocation` gibt den Speicherort für das abgeleitete Schema und dessen spätere Änderungen an; `checkpointLocation` bestimmt, wo der Fortschritts- und Tracking-Zustand des Streams abgelegt wird.

---

## 3. Auto Loader in SQL

Auto Loader ist nicht auf PySpark/Scala beschränkt — es unterstützt sowohl Python als auch SQL in Lakeflow-Pipelines. In SQL wird Auto Loader über die `STREAM read_files(...)`-Syntax angesprochen, den offiziellen Weg, um Auto-Loader-Funktionalität aus SQL heraus aufzurufen.

```sql
CREATE OR REFRESH STREAMING TABLE ingestion_st
AS SELECT * FROM STREAM read_files(
  "/databricks-datasets/retail-org/sales_orders",
  format => "json"
);
```

Dieselbe Streaming Table lässt sich äquivalent auch in Python über `spark.readStream.format("cloudFiles")` in einer Lakeflow-Pipeline definieren — SQL und Python sind zwei gleichwertige Schnittstellen zu derselben zugrunde liegenden `cloudFiles`-Quelle:

```python
@dp.table
def sales_orders():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/databricks-datasets/retail-org/sales_orders")
    )
```

---

## 4. Vorteile gegenüber generischer Structured-Streaming-File-Source

Die Doku vergleicht Auto Loader explizit mit der klassischen, generischen Structured-Streaming-File-Source (`spark.readStream.format(fileFormat).load(directory)` ohne `cloudFiles`). Dabei werden folgende Vorteile genannt:

| Vorteil | Beschreibung laut Doku |
|---|---|
| **Skalierbarkeit** | Auto Loader kann Milliarden Dateien effizient entdecken. Backfills können asynchron durchgeführt werden, ohne Rechenressourcen zu verschwenden. |
| **Performance** | Die Kosten der Dateierkennung skalieren mit der Anzahl der eingelesenen Dateien, nicht mit der Anzahl der Verzeichnisse, in denen die Dateien liegen. |
| **Schema-Inferenz und -Evolution** | Auto Loader kann Schema-Drifts erkennen, über Schema-Änderungen benachrichtigen und Daten "retten", die andernfalls ignoriert oder verloren gegangen wären. |
| **Kosten** | Auto Loader nutzt native Cloud-APIs, um Dateilisten abzurufen. Zusätzlich kann der File-Notification-Modus Cloud-Kosten weiter senken, indem das Directory Listing vollständig vermieden wird. |

```python
# Klassische Structured Streaming File Source (OHNE Auto Loader) —
# Kosten skalieren mit der Anzahl der Verzeichnisse, keine RocksDB-Zustandsverwaltung
plain_df = spark.readStream.format("json").load("/Volumes/analytics/bronze/events")

# Auto Loader (cloudFiles) — Kosten skalieren mit der Anzahl der Dateien,
# RocksDB-Checkpoint, Schema-Drift-Erkennung, optionale Kostensenkung via File Notifications
autoloader_df = (spark.readStream
                  .format("cloudFiles")
                  .option("cloudFiles.format", "json")
                  .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
                  .load("/Volumes/analytics/bronze/events"))
```

Zusätzlich gilt: Auto Loader benötigt laut Doku keinen selbst verwalteten Zustand, um Fehlertoleranz oder exactly-once-Semantik zu erreichen — das übernimmt der interne Checkpoint-Mechanismus (siehe Abschnitt 9).

---

## 5. Zwei Datei-Erkennungsmodi: Directory Listing vs. File Notification

Auto Loader bietet zwei unterschiedliche Mechanismen, um neue Dateien zu erkennen:

- **Directory Listing (Standard):** Auto Loader erkennt neue Dateien durch Auflisten des Eingabeverzeichnisses. Dieser Modus lässt sich ohne zusätzliche Berechtigungskonfiguration starten, abgesehen vom Zugriff auf die Daten im Cloud-Speicher selbst.
- **File Notification (empfohlen für die meisten Workloads):** Auto Loader nutzt Benachrichtigungs- und Warteschlangendienste der Cloud-Infrastruktur, die auf Datei-Ereignisse im Eingabeverzeichnis abonniert sind. Dieser Modus ist performanter und skalierbarer als Directory Listing, da kein wiederholtes Auflisten des Verzeichnisses nötig ist.

Beide Modi lassen sich über Stream-Neustarts hinweg wechseln, wobei weiterhin exactly-once-Garantien gelten. In keinem der beiden Modi garantiert Auto Loader eine bestimmte Reihenfolge, in der Dateien entdeckt oder verarbeitet werden.

```python
# Directory Listing (Standard) — keine zusätzliche Konfiguration nötig
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .load("/Volumes/analytics/bronze/events"))
```

```python
# File Notification Mode — performanter/skalierbarer, benötigt Cloud-Berechtigungen
# für automatisch eingerichtete Benachrichtigungs-/Warteschlangendienste
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.useNotifications", "true")
      .load("/Volumes/analytics/bronze/events"))
```

---

## 6. Schema-Inferenz und `schemaHints`

Wird kein Schema angegeben, leitet Auto Loader es automatisch aus einer Stichprobe der Daten ab und kann das Schema weiterentwickeln, während mehr Daten verarbeitet werden.

`schemaHints` erlaubt es, gezielt einzelne Spaltentypen zu überschreiben, ohne das restliche Schema von der automatischen Inferenz auszuschließen — etwa wenn eine Spalte in unterschiedlichen Dateien verschiedene Datentypen aufweist und Auto Loader dabei standardmäßig den breitesten Typ wählt.

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaHints", "id int, amount double")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .load("/Volumes/analytics/bronze/events"))
```

```sql
-- Äquivalent in SQL über read_files
SELECT * FROM read_files(
    's3://bucket/path',
    format => 'json',
    schemaHints => 'id int, amount double');
```

---

## 7. Schema-Evolution-Modi und automatische Typ-Erweiterung

Auto Loader unterstützt mehrere Arten von Schema-Änderungen über die Zeit:

| Änderungstyp | Verhalten laut Doku |
|---|---|
| **Neue Spalten** | Unterstützt, abhängig vom gewählten `schemaEvolutionMode` |
| **Spalten umbenennen** | Unterstützt — wird als neue Spalte behandelt; die alte Spalte erhält für neue Zeilen `NULL` |
| **Gelöschte Spalten** | Unterstützt als "Soft Delete" — neue Zeilen erhalten für die gelöschte Spalte `NULL` |
| **Typ-Erweiterung (Type Widening)** | Unterstützt ab Databricks Runtime 16.4 mit `schemaEvolutionMode => 'addNewColumnsWithTypeWidening'` |

### Die fünf `schemaEvolutionMode`-Werte

- **`addNewColumns`** (Standard, wenn kein Schema angegeben ist): Neue Spalten führen dazu, dass der Stream mit einer `UnknownFieldException` stoppt. Vor diesem Fehler leitet Auto Loader das Schema aus dem letzten Micro-Batch ab und aktualisiert den Schema-Speicherort — beim Neustart wird das erweiterte Schema verwendet.
- **`rescue`**: Schema bleibt eingefroren, der Stream läuft ohne Unterbrechung weiter. Neue oder nicht passende Spalten landen ausschließlich in der `rescuedDataColumn`.
- **`failOnNewColumns`**: Der Stream schlägt bei neuen Spalten fehl und startet erst nach manueller Schema-Aktualisierung neu.
- **`none`** (Standard, wenn ein Schema angegeben ist): Schema entwickelt sich nicht weiter, neue Spalten werden ignoriert. Daten werden dabei nicht gerettet, außer die `rescuedDataColumn`-Option ist zusätzlich explizit gesetzt.
- **`addNewColumnsWithTypeWidening`**: Verhält sich wie `addNewColumns`, erweitert zusätzlich automatisch kompatible Datentypen (z. B. `int` → `long`, `float` → `double`), ohne dass Daten neu geschrieben werden müssen.

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaEvolutionMode", "rescue")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .load("/Volumes/analytics/bronze/events"))
```

### Type Widening im Detail

Unterstützte, verlustfreie Typ-Erweiterungen laut Doku:

| Quelltyp | Mögliche Zieltypen |
|---|---|
| `byte` | `short`, `int`, `long`, `decimal`, `double` |
| `short` | `int`, `long`, `decimal`, `double` |
| `int` | `long`, `decimal`, `double` |
| `long` | `decimal` |
| `float` | `double` |
| `decimal` | `decimal` mit höherer Präzision/Skala |

Type Widening funktioniert für alle Formate mit Schema-Evolution-Unterstützung — sowohl Textformate (JSON, CSV, XML) als auch Binärformate (Avro, Parquet).

**Wichtige Einschränkung:** Der `from_json`-Parser unterstützt keine Schema-Evolution.

---

## 8. Die Rescued-Data-Spalte

Die Rescued-Data-Spalte stellt sicher, dass beim ETL-Prozess keine Daten verloren gehen. Sie enthält alle Daten, die nicht geparst werden konnten — etwa weil ein Feld im angegebenen Schema fehlte, ein Typkonflikt vorlag, oder die Groß-/Kleinschreibung der Spalte nicht mit dem Schema übereinstimmte. Zurückgegeben wird die Spalte als JSON-Blob mit den geretteten Spalten sowie dem Quelldateipfad des Datensatzes.

Bei Auto Loader ist die `_rescued_data`-Spalte standardmäßig Teil des zurückgegebenen Schemas, sobald das Schema per Inferenz ermittelt wird.

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .load("/Volumes/analytics/bronze/events"))
# _rescued_data erscheint automatisch als Spalte im Ergebnis-DataFrame
```

### Parser-Modi: `PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`

Die JSON-/CSV-Parser unterstützen drei Modi. In Kombination mit der `rescuedDataColumn` führen Typkonflikte in `DROPMALFORMED` nicht dazu, dass Datensätze verworfen werden, und lösen in `FAILFAST` keinen Fehler aus — nur wirklich korrupte Datensätze (unvollständiges oder fehlerhaftes JSON/CSV) führen zum Verwerfen bzw. zu einem Fehler und landen in `badRecordsPath`.

**Wichtige Unterscheidung:**
- **Typ-Mismatches** (z. B. Text statt Zahl) → landen in `_rescued_data`, werden nicht verworfen.
- **Wirklich korrupte/unvollständige Datensätze** → landen in `badRecordsPath`, oder lösen im `FAILFAST`-Modus einen Fehler aus.

---

## 9. Datei-Tracking

### Grundmechanismus

Entdeckte Dateien werden mit ihren Metadaten in einem skalierbaren Key-Value-Store (RocksDB) im Checkpoint-Verzeichnis der Pipeline gespeichert, was eine exactly-once-Verarbeitung sicherstellt.

### Standard-Tracking-Parameter: Dateipfad

Auto Loader verfolgt Dateien primär anhand ihres Pfads — jede Datei wird standardmäßig nur einmal anhand ihres Pfads verarbeitet.

### `cloudFiles.allowOverwrites`: zusätzlicher Tracking-Parameter

Standardmäßig (`cloudFiles.allowOverwrites = false`) wird jede Datei exakt einmal verarbeitet, unabhängig von späteren Änderungen. Wird die Option auf `true` gesetzt, erweitert sich der Tracking-Parameter um den Änderungszeitpunkt der Datei — geänderte Dateien werden dann erneut verarbeitet. <mark style="background:#fff59d;color:#1b1f23;">Dabei muss man Duplikate selbst behandeln, und Auto Loader verarbeitet die gesamte Datei erneut, auch bei nur teilweisen Änderungen.</mark> Databricks empfiehlt generell, Auto Loader nur für unveränderliche Dateien einzusetzen und die Standardeinstellung (`false`) beizubehalten.

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "csv")
      .option("cloudFiles.allowOverwrites", "true")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .load("/Volumes/analytics/bronze/daily_drop"))
```

### `cloudFiles.includeExistingFiles`: Anfangszustand steuern

Diese Option legt fest, ob beim allerersten Start eines Streams bereits vorhandene Dateien in die Verarbeitung aufgenommen werden, oder ob nur Dateien berücksichtigt werden, die nach dem Start neu hinzukommen. Wichtig: Diese Option wird nur beim allerersten Start eines Streams mit frischem Checkpoint ausgewertet — ein späteres Ändern hat keine Wirkung. Auch bei `includeExistingFiles = false` führt Auto Loader weiterhin eine Verzeichnisauflistung durch, um mit dem Dateiereignis-Cache auf demselben Stand zu sein.

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.includeExistingFiles", "false")
      .load("/Volumes/analytics/bronze/events"))
```

### `cloudFiles.maxFileAge`: Tracking-Zustand zeitlich begrenzen

Diese Option steuert, wie lange Auto Loader sich ein einzelnes Datei-Ereignis merkt, bevor es aus dem Tracking-Zustand entfernt wird — als Kostenkontrollmechanismus für sehr große Datensätze. Der Mindestwert liegt bei 14 Tagen, empfohlen wird ein konservativer Wert (z. B. 90 Tage). Zu aggressive Einstellungen können Datenqualitätsprobleme verursachen, etwa doppelte Ingestion, wenn bereits verarbeitete Dateien "verjähren" und danach erneut verarbeitet werden.

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.maxFileAge", "90 days")
      .load("/Volumes/analytics/bronze/events"))
```

### Tracking vollständig zurücksetzen

Der Tracking-Zustand ist an das Checkpoint-Verzeichnis gebunden. Ein Wechsel oder Löschen dieses Verzeichnisses setzt das Tracking vollständig zurück — die nächste Ausführung beginnt von Neuem.

---

## 10. Beobachtbarkeit: `cloud_files_state`

Auto Loader erlaubt es, den internen Ingestion-Zustand direkt abzufragen. Damit lässt sich pro Datei nachvollziehen, ob sie bereits verarbeitet wurde, sich noch in Verarbeitung befindet oder aufgrund von Beschädigung übersprungen wurde.

```sql
SELECT * FROM cloud_files_state(TABLE(workspace.default.events_delta));
```

Mögliche Zustände pro Datei umfassen unter anderem: nicht verarbeitet (`NULL`), in Verarbeitung (`PROCESSING`) oder wegen Beschädigung übersprungen (`SKIPPED_CORRUPTED`).

---

## 11. Datenretention: `cloudFiles.cleanSource`

Diese Option verschiebt oder löscht Quelldateien, nachdem sie von Auto Loader verarbeitet wurden — das reduziert indirekt auch die Menge an Zustand, die für die Dateierkennung durchsucht werden muss.

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.cleanSource", "MOVE")
      .option("cloudFiles.cleanSource.moveDestination", "/Volumes/analytics/bronze/_archive")
      .load("/Volumes/analytics/bronze/events"))
```

---

## 12. Authentifizierung und Unity Catalog

Auto Loader liest Dateien aus Unity-Catalog-External-Locations oder Unity-Catalog-Volumes (verwaltet und extern). Erforderlich ist entweder eine `READ FILES`-Berechtigung auf der External Location, oder eine `READ VOLUME`-Berechtigung auf dem Volume, das die zu lesenden Dateien enthält.

---

## 13. Unterstützte Dateiformate

Auto Loader unterstützt dieselben Dateiformate wie `read_files`: JSON, CSV, XML, TEXT, BINARYFILE, PARQUET, AVRO und ORC. Format und Schema können automatisch erkannt werden.

---

## 14. Auto Loader in Lakeflow Declarative Pipelines

Auto Loader ist die zentrale Ingestion-Quelle für **Streaming Tables** innerhalb von Lakeflow Declarative Pipelines (früher: Delta Live Tables). Innerhalb einer Pipeline lässt sich Auto Loader sowohl über `STREAM read_files(...)` (SQL) als auch über `spark.readStream.format("cloudFiles")` (Python) ansprechen — beide erzeugen dieselbe Art von Streaming Table.

```sql
CREATE OR REFRESH STREAMING TABLE orders_bronze
AS SELECT * FROM STREAM read_files('/Volumes/raw/orders', format => 'json');
```

Ein zentraler Vorteil von Lakeflow Declarative Pipelines gegenüber manuell entwickelten Structured-Streaming-Jobs mit Auto Loader ist die automatische Orchestrierung: Verarbeitungsschritte ("Flows") werden in korrekter Reihenfolge mit maximaler Parallelität ausgeführt, und vorübergehende Fehler werden gestuft wiederholt.

Streaming Tables mit Auto Loader lassen sich auch außerhalb einer vollständigen Pipeline direkt in Databricks SQL erstellen, aktualisieren und abfragen.

---

## 15. Zusammenfassung

Auto Loader (`cloudFiles`) ist Databricks' dedizierte Streaming-Quelle für die inkrementelle, fortlaufende Verarbeitung neuer Dateien aus Cloud-Speicher. Die zentralen Eigenschaften:

- **Inkrementell und zustandsbehaftet:** verarbeitet nur neue Dateien, Tracking über RocksDB-Checkpoint, kein selbst verwalteter Zustand nötig.
- **Skalierbar:** Milliarden Dateien, Millionen Dateien pro Stunde, Kosten skalieren mit Dateianzahl statt Verzeichnisanzahl.
- **Zwei Erkennungsmodi:** Directory Listing (Standard) oder File Notification (performanter, für die meisten Workloads empfohlen).
- **Schema-Handling:** automatische Inferenz, `schemaHints` zur gezielten Typüberschreibung, fünf Schema-Evolution-Modi, automatische Typ-Erweiterung.
- **Datensicherheit:** Rescued-Data-Spalte als Standard-Sicherheitsnetz gegen Datenverlust bei Typkonflikten.
- **Einstellbares Tracking:** `allowOverwrites`, `includeExistingFiles`, `maxFileAge` steuern das Verhalten des internen Zustands.
- **Beobachtbar:** `cloud_files_state` erlaubt direkte Abfrage des Ingestion-Zustands pro Datei.
- **Zugänglich über SQL und Python:** gleichwertig nutzbar direkt oder innerhalb von Lakeflow Declarative Pipelines.

---

## 16. Quellen

- What is Auto Loader?: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/
- Auto Loader FAQ: https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/faq.html
- Auto Loader options: https://docs.databricks.com/en/ingestion/cloud-object-storage/auto-loader/options.html
- Configure Auto Loader for production workloads: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/production
- Configure schema inference and evolution in Auto Loader: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema
- Automatic type widening with Auto Loader: https://docs.databricks.com/gcp/en/ingestion/cloud-object-storage/auto-loader/type-widening
- Schema evolution in Databricks: https://docs.databricks.com/aws/en/data-engineering/schema-evolution
- Compare Auto Loader file detection modes: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/file-detection-modes
- cloud_files_state table-valued function: https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/functions/cloud_files_state
- read_files table-valued function: https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files
- CREATE STREAMING TABLE: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table
- Develop Lakeflow Spark Declarative Pipelines code with SQL: https://docs.databricks.com/aws/en/ldp/developer/sql-dev
- Load data with Lakeflow Declarative Pipelines: https://docs.databricks.com/gcp/delta-live-tables/load
- What are Lakeflow pipelines?: https://docs.databricks.com/aws/en/ldp/concepts/
- Spark API options reference: https://docs.databricks.com/aws/en/spark/api-options
- Best practices for reliability: https://docs.databricks.com/en/lakehouse-architecture/reliability/best-practices.html
- Using Auto Loader with Unity Catalog: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/unity-catalog
