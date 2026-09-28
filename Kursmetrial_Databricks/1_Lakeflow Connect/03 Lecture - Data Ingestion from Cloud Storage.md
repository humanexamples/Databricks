## Methoden zur Daten-Ingestion

#### Methode 1 – Batch – `CREATE TABLE AS (CTAS)`

**`CREATE TABLE AS (CTAS)`**: Batch-Ingestion mit `read_files()`, die UC-Tabellen aus Rohdateien erstellt. Am besten geeignet für kleinere Ad-hoc-Datensätze.

1. Unterstützt das Lesen von **Dateiformaten** wie:
   | JSON | CSV | XML | TEXT | BINARYFILE | PARQUET | AVRO | ORC
2. Kann das Dateiformat automatisch erkennen und **ein einheitliches Schema** über alle Dateien hinweg **ableiten**.
3. Geben Sie **dateiformatspezifische Optionen** an, um die Daten entsprechend dem Quelldateiformat einzulesen.
4. Kann in **Streaming Tables** verwendet werden, um Dateien mit Auto Loader **inkrementell** in Delta Lake zu ingestieren.

```sql
CREATE TABLE new_table AS
SELECT *
FROM read_files(
  <path_to_file(s)>,
  format => '<file_type>',
  <other_format_specific_options>
);
```

`CREATE TABLE AS (CTAS)` erstellt **standardmäßig** eine UC-Tabelle aus Dateien im Cloud Object Storage.

Die Funktion `read_files()` liest Dateien an einem angegebenen Speicherort und gibt die Daten in **tabellarischer Form** zurück.

#### Methode 2 – Inkrementeller Batch – `COPY INTO`

**`COPY INTO`**: Inkrementelle Batch-Ingestion, die idempotent und wiederholbar ist. Überspringt bereits geladene Dateien und unterstützt Format- und Kopieroptionen für eine feingranulare Steuerung.

Verwenden Sie die Anweisung `COPY INTO`, um Dateien aus dem Cloud-Speicher in die UC-Tabelle zu kopieren. Dieser Befehl führt einen Massenimport (Bulk Load) aus Dateien im Cloud Object Storage in die Tabelle durch; in diesem Beispiel werden die Dateien in die leere Tabelle new_table geladen. Die `FROM`-Klausel gibt den Speicherort der CSV-Dateien an.

`COPY INTO` ist ideal für Situationen, in denen am Cloud-Speicherort laufend Dateien hinzukommen, da es sich um eine wiederholbare und idempotente Operation handelt, die für inkrementelle Batch-Ingestion konzipiert ist.
**Wichtige Aspekte von `COPY INTO`**:

- **Idempotent**: Überspringt alle Dateien, die bereits in die Tabelle geladen wurden; nur neue Dateien werden ingestiert
- **Unterstützte Dateiformate**: Parquet, JSON, XML und weitere
- **`FROM clause`**: Gibt den Pfad des Cloud-Speicherorts an, an dem laufend neue Dateien hinzukommen
- **`FORMAT_OPTIONS()`**: Steuert, wie die Quelldateien geparst und interpretiert werden (Optionen hängen vom Dateiformat ab)
- **`COPY_OPTIONS()`**: Steuert das Verhalten der `COPY INTO`-Operation selbst, zum Beispiel:
  - Schema Evolution mit (**mergeSchema**)
  - Idempotenz mit (**force**)

```sql
CREATE TABLE new_table;
COPY INTO new_table
FROM '<dir_path>'
FILEFORMAT = <file_type>
FORMAT_OPTIONS (<options>)
COPY_OPTIONS (<options>)
```

Verwenden Sie die Anweisung `COPY INTO`, um Dateien aus dem Cloud-Speicher in die UC-Tabelle zu kopieren; dies führt einen Bulk Load aus Dateien im Cloud Object Storage in die Tabelle durch.

`COPY INTO` überspringt alle Dateien, die bereits in die Tabelle geladen wurden, und ingestiert nur neue Dateien.

#### Methode 3 – Inkrementeller Batch oder Streaming – `AUTO LOADER`

**`AUTO LOADER`**: Die am besten skalierbare Methode, basierend auf Spark Structured Streaming. Unterstützt sowohl Python als auch SQL (über Declarative Pipelines), verarbeitet Milliarden von Dateien und behandelt Schema Evolution automatisch.

1. Inkrementelle Batch- oder Streaming-Ingestion mit Auto Loader.
   - Neue Datendateien **inkrementell** verarbeiten, sobald sie im Cloud-Speicher eintreffen (Batch oder Streaming)
   - Daten **ohne zusätzliches Setup** oder komplexe Konfiguration ingestieren
   - Neue Dateien **automatisch** erkennen und in UC-Tabellen laden
   - Den Umgang mit inkrementellen und Streaming-Daten vereinfachen
   - Sowohl mit **Python** als auch mit **SQL** (über Declarative Pipelines) nutzbar
   - Skaliert auf die **Verarbeitung von Milliarden von Dateien**
   - Nutzt **Spark Structured Streaming** für eine effiziente und zuverlässige Ingestion

2. Auto Loader in Python zum Lesen von Streaming-Daten aus dem Cloud-Speicher:
   - Wir beginnen mit **`.readStream`** und setzen das **Format** auf "`cloudFiles`", wodurch Auto Loader aktiviert wird.
   - Dann geben wir das **Dateiformat** als **JSON** an und definieren den **Schema-Speicherort** mit `cloudFiles.schemaLocation`, der zur Nachverfolgung von Schema-Inferenz und -Evolution verwendet wird.
   - Anschließend zeigen wir mit **`.load()`** auf den Speicherort der Dateien, in diesem Fall ein Pfad unter /Volumes, der auf Unity Catalog verweist.
   - Auf der Schreibseite konfigurieren wir **`.writeStream`** mit einem **Checkpoint-Speicherort**, um Zustand und Fortschritt zu speichern, und setzen ein **Trigger**-Intervall von **alle 5 Sekunden**.
   - Schließlich schreiben wir die Daten mit **`.toTable()`** in eine UC-Tabelle, die durch Katalog, Datenbank und Tabellennamen angegeben ist.

3. Auto Loader mit Databricks SQL
   - Databricks empfiehlt, Streaming Tables zum Ingestieren von Daten mit Databricks SQL zu verwenden (anstelle von COPY INTO). Eine Streaming Table ist eine in **Unity Catalog** registrierte Tabelle, die zusätzliche Unterstützung für Streaming- oder inkrementelle Datenverarbeitung bietet.
     - Wenn Sie eine Streaming Table erstellen, wird automatisch eine **Pipeline** dafür generiert.
     - Streaming Tables können für das inkrementelle Laden von Daten sowohl aus **Kafka** als auch aus **Cloud Object Storage** verwendet werden.
   - Um eine Streaming Table aus Dateien in einem Volume zu erstellen, verwenden Sie Auto Loader. Databricks empfiehlt **Auto Loader mit Apache Spark™ Declarative Pipelines** für die meisten Ingestion-Aufgaben aus Cloud Object Storage. Zusammen sind Auto Loader und Declarative Pipelines darauf ausgelegt, kontinuierlich wachsende Datensätze inkrementell und idempotent zu laden, sobald sie eintreffen.
   - Streaming Tables in Databricks SQL basieren auf **serverlosen** Spark Declarative Pipelines. Ihr Workspace muss serverlose Pipelines unterstützen, um diese Funktion zu nutzen. Alternativ können Sie **eigene** Spark Declarative Pipelines für inkrementelle Verarbeitung, Optimierung und Monitoring erstellen. Declarative Pipelines bieten eine Reihe zusätzlicher Funktionen, über die Sie [hier](https://docs.databricks.com/aws/en/dlt/) mehr erfahren können.
   - Um Auto Loader in Databricks SQL zu verwenden, nutzen Sie die Funktion **`read_files`** mit dem Schlüsselwort **`STREAM`** in der **`FROM`**-Klausel.

**Python Auto Loader**

```python
(spark
  .readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "json")
    .option("cloudFiles.schemaLocation", "<checkpoint_path>")
    .load("/Volumes/catalog/schema/files")
  .writeStream
    .option("checkpointLocation", "<checkpoint_path>")
    .trigger(processingTime="5 seconds")
    .toTable("catalog.database.table")
)
```

**Auto Loader mit SQL (Declarative Pipelines)**

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.table
SCHEDULE EVERY 1 HOUR
AS
SELECT *
FROM STREAM read_files('<dir_path>', format => '<file_type>')
```

## C. Ingestion-Methoden auf einen Blick
Hier eine kurze Zusammenfassung aller drei Methoden zur Daten-Ingestion.

| MERKMAL | CREATE TABLE AS (CTAS) + spark.read | COPY INTO | Auto Loader |
| --- | --- | --- | --- |
| Ingestion-Typ | Batch | Inkrementeller Batch | Inkrementell (Batch oder Streaming) |
| Anwendungsfälle | Am besten für kleinere Datensätze | Ideal für Tausende von Dateien | Skaliert auf Millionen+ Dateien pro Stunde, Backfills mit Milliarden von Dateien |
| Syntax/Schnittstelle | - Python (spark.read) - SQL (CTAS) | SQL | - Python (spark.readStream) - SQL mit Declarative Pipelines (CREATE OR REFRESH STREAMING TABLES) - Streaming Tables in Databricks SQL |
| Idempotenz | Nein | Ja | Ja |
| Schema Evolution | Manuell oder beim Lesen abgeleitet | Mit Optionen unterstützt | Auto Loader erkennt und entwickelt Schemas automatisch weiter. Behandelt neue Spalten, sobald sie auftreten. |
| Latenz | Hoch | Mittel (zeitgesteuert) | Niedrig oder hoch, je nach Konfiguration |
| Benutzerfreundlichkeit | Einfach | Einfach und SQL-basiert | Mittel bis fortgeschritten, je nach Implementierung |
| Zusammenfassung | Am besten für einmalige Ad-hoc-Ingestion. Kann zeitgesteuert werden, um immer alle Daten zu lesen und zu verarbeiten. | Einfach und wiederholbar für inkrementelle Datei-Ingestion. Ideal für zeitgesteuerte Jobs oder Pipelines. | Am besten für Streaming nahezu in Echtzeit oder inkrementelle Ingestion, mit hoher Automatisierung und Skalierbarkeit. |
