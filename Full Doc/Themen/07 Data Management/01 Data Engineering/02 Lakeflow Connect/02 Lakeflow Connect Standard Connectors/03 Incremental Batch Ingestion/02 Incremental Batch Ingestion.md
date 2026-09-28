Beim Laden von Daten in Databricks mit Lakeflow Connect Standard Connectors stehen mehrere Ingestion-Methoden zur Auswahl:


## Incremental Batch Ingestion
- Während klassische Batch Ingestion bei jeder Ausführung alle Datensätze verarbeitet, erkennt Incremental Batch Ingestion automatisch neue Datensätze in der Datenquelle und überspringt bereits geladene Datensätze.
- Gängige Techniken:
  - Die SQL-Anweisung: `COPY INTO`
  - Die Python-Methode: `spark.readStream` (Auto Loader mit einem zeitgesteuerten Trigger)
  - Declarative Pipelines: `CREATE OR REFRESH STREAMING TABLE`

- **Es werden nur neue Daten geladen** — bereits geladene Datensätze werden **automatisch übersprungen**
- Bietet eine **schnellere** und **ressourceneffizientere** Ingestion, da weniger Daten verarbeitet werden

> Vollständige Syntax- und Parameterreferenz (inkl. `BY POSITION`, `WITH (CREDENTIAL … ENCRYPTION …)`, `VALIDATE`, `FILES`/`PATTERN`, Nebenläufigkeit): siehe `06 DML Statements/_copy_into.md`.

Wichtige Aspekte von [COPY INTO](https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into):
- **Idempotent:** Überspringt alle Dateien, die bereits in die Tabelle geladen wurden; es werden nur neue Dateien geladen. Wörtlich laut Doku: *"This is a retryable and idempotent operation. Files in the source location that have already been loaded are skipped."* — die Nachverfolgung, welche Dateien bereits geladen wurden, erfolgt über Metadaten im Delta Log.
- **Unterstützte Dateiformate:** Parquet, JSON, XML und weitere
- **`FROM clause`:** Gibt den Pfad des Cloud-Speicherorts an, an dem fortlaufend neue Dateien hinzugefügt werden
- **`FORMAT_OPTIONS()`:** Steuert, wie die Quelldateien geparst und interpretiert werden (Optionen abhängig vom Dateiformat)
- **`COPY_OPTIONS()`**: Steuert das Verhalten der COPY INTO-Operation selbst, z. B.:
  - Schema-Evolution mittels (`mergeSchema`)
  - Idempotenz mittels (`force`) — die Option, die Idempotenz bewusst zu **deaktivieren**: *"force: boolean, default false. If set to true, idempotency is disabled and files are loaded regardless of whether they've been loaded before."* Relevant, falls Dateien absichtlich erneut geladen werden sollen, z. B. nach einer Datenkorrektur an der Quelle.


```python
-- Batch Ingestion mit CTAS
CREATE TABLE new_table AS
  SELECT *
  FROM read_files(
     <path_to_file(s)>,
     format => '<file_type>',
     <other_format_specific_options>
  );
```


```python
-- Verwende die COPY INTO-Anweisung, um Dateien aus dem Cloud-Speicher in die Delta-Tabelle zu kopieren; 
-- dies führt ein Bulk Load von Dateien aus dem Cloud-Objektspeicher in die Tabelle durch.

-- COPY INTO überspringt alle Dateien, die bereits in die Tabelle geladen wurden, 
-- und lädt nur neue Dateien.
CREATE TABLE new_table;
        
COPY INTO new_table
  FROM '<dir_path>'
  FILEFORMAT = <file_type>
  FORMAT_OPTIONS (<options>)
  COPY_OPTIONS (<options>)
```


```python
CREATE TABLE historical_users_bronze_ci (
  user_id STRING,
  user_first_touch_timestamp BIGINT
);


-- Verwende COPY INTO, um die Delta-Tabelle zu befüllen
COPY INTO historical_users_bronze_ci
  FROM '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
  FILEFORMAT = parquet;
```


```python
COPY INTO historical_users_bronze_ci
  FROM '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
  FILEFORMAT = parquet
  COPY_OPTIONS ('mergeSchema' = 'true');     -- Schema jeder Datei zusammenführen
```

## [AUTO LOADER](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)

Auto Loader verarbeitet neue Datendateien inkrementell und effizient, sobald sie im Cloud-Speicher eintreffen — ohne zusätzliche Einrichtung.

1. Incremental Batch oder Streaming Ingestion mit Auto Loader.
    - Neue Datendateien **inkrementell** verarbeiten, sobald sie im Cloud-Speicher eintreffen (Batch oder Streaming)
    - Daten **ohne zusätzliche Einrichtung** oder komplexe Konfiguration laden
    - Neue Dateien **automatisch** erkennen und in Delta-Tabellen laden
    - Handhabung von inkrementellen und Streaming-Daten vereinfachen
    - Verwendung sowohl mit **Python** als auch mit **SQL** (über Declarative Pipelines)
    - Skalierung auf die **Verarbeitung von Milliarden von Dateien**
    - Verlässt sich auf **Spark Structured Streaming** für eine effiziente und zuverlässige Ingestion

2. Auto Loader in Python zum Lesen von Streaming-Daten aus dem Cloud-Speicher:
    - Wir beginnen mit `.readStream` und setzen das **Format** auf „`cloudFiles`", wodurch Auto Loader aktiviert wird.
    - Anschließend legen wir das **Dateiformat** als **JSON** fest und definieren den **Schema-Speicherort** über cloudFiles.schemaLocation, der zur Nachverfolgung der Schema-Inferenz und -Evolution dient.
    - Danach verwenden wir `.load()`, um auf den Speicherort der Dateien zu verweisen, in diesem Fall einen Pfad unter /Volumes, der auf Unity Catalog verweist.
    - Auf der Schreibseite konfigurieren wir `.writeStream` mit einem **Checkpoint-Speicherort**, um Zustand und Fortschritt zu bewahren, und legen ein **Trigger**-Intervall von **alle 5 Sekunden** fest.
    - Abschließend verwenden wir `.toTable()`, um die Daten in eine Delta-Tabelle zu schreiben, die durch Katalog, Datenbank und Tabellennamen angegeben wird.

3. Auto Loader mit Databricks SQL
    - Databricks empfiehlt, Streaming Tables zum Laden von Daten mit Databricks SQL zu verwenden (anstelle von COPY INTO). Eine Streaming Table ist eine bei **Unity Catalog** registrierte Tabelle mit zusätzlicher Unterstützung für Streaming- oder inkrementelle Datenverarbeitung.
      - Beim Erstellen einer Streaming Table wird automatisch eine **Pipeline** dafür generiert.
      - Streaming Tables können für inkrementelles Laden von Daten sowohl aus **Kafka** als auch aus **Cloud-Objektspeicher** verwendet werden.
    - Um eine Streaming Table aus Dateien in einem Volume zu erstellen, wird Auto Loader verwendet. Databricks empfiehlt für die meisten Ingestion-Aufgaben aus Cloud-Objektspeicher die Verwendung von **Auto Loader mit Lakeflow Declarative Pipelines**. Zusammen sind Auto Loader und Declarative Pipelines darauf ausgelegt, kontinuierlich wachsende Datensätze inkrementell und idempotent zu laden, sobald sie eintreffen.
    - Streaming Tables in Databricks SQL werden von **serverlosen** Lakeflow Declarative Pipelines betrieben. Ihr Workspace muss serverlose Pipelines unterstützen, um diese Funktionalität zu nutzen. Alternativ können Sie **eigene** Lakeflow Declarative Pipelines für inkrementelle Verarbeitung, Optimierung und Überwachung erstellen. Declarative Pipelines bieten eine Reihe zusätzlicher Funktionen, über die Sie [hier](https://docs.databricks.com/aws/en/ldp) mehr erfahren können.
    - Um Auto Loader in Databricks SQL zu verwenden, nutzen Sie die Funktion `read_files` mit dem `STREAM`-Schlüsselwort in der `FROM`-Klausel.


---
#### Weitere Ressourcen

- [Streaming Tables Dokumentation](https://docs.databricks.com/gcp/en/dlt/streaming-tables)

- [CREATE STREAMING TABLE Syntax](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-streaming-table)

- [Verwendung von Streaming Tables in Databricks SQL](https://docs.databricks.com/aws/en/dlt/dbsql/streaming)

- [REFRESH (MATERIALIZED VIEW or STREAMING TABLE)](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-refresh-full)

- [COPY INTO (legacy)](https://docs.databricks.com/aws/en/ingestion/#copy-into-legacy)

- [Lakeflow Declarative Pipelines](https://docs.databricks.com/aws/en/dlt/)


```python
# Python Auto Loader
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

Im untenstehenden Code:
- **Spark Declarative Pipelines** ist das übergeordnete Framework, das hier verwendet wird. Erkennbar an der deklarativen Syntax `CREATE OR REFRESH STREAMING TABLE ... SCHEDULE EVERY 1 HOUR`. Dies ist kein reines Spark SQL — es gehört zum Pipelines-Framework, das die Streaming Table definiert, ihre Aktualisierung verwaltet und den Zeitplan (stündlich) steuert.
- **Auto Loader** wird darin als Datenquelle verwendet, erkennbar an **STREAM read_files(...)**. Diese Funktion ist die SQL-Schnittstelle zu Auto Loader und übernimmt die inkrementelle, effiziente Ingestion neuer Dateien aus dem angegebenen Verzeichnis (einschließlich der automatischen Verwaltung von Checkpoint- und Schema-Informationen, wie auf der zuvor geöffneten Auto-Loader-Dokumentationsseite beschrieben).


```python
CREATE OR REFRESH STREAMING TABLE catalog.schema.table   -- 
SCHEDULE EVERY 1 HOUR
AS
SELECT *
FROM STREAM read_files(
  '<dir_path>',
  format => '<file_type>'
)

DESCRIBE HISTORY catalog.schema.table;
```


```python
-- Beispiel

CREATE OR REFRESH STREAMING TABLE mytable
SCHEDULE EVERY 1 WEEK     -- Die Zeitplanung der Aktualisierung ist optional
AS
SELECT *
FROM STREAM read_files(
  '/Volumes/dbacademy/your-labuser-name/csv_files_autoloader_source',  -- Pfad zu Ihrem csv_files_autoloader_source-Volume einfügen (Beispiel gezeigt)
  format => 'CSV',
  sep => '|',
  header => true
);

SELECT * FROM mytable;
DESCRIBE TABLE EXTENDED mytable;
DESCRIBE HISTORY mytable;
```

## C. Ingestion-Methoden im Überblick

Hier eine kurze Zusammenfassung aller drei Data-Ingestion-Methoden.


<table style="width: 100%; border-collapse: collapse; line-height: 1.5;">
  <thead>
    <tr style="background: #1B5162; color: white;">
      <th style="padding: 10px 14px; text-align: left; border: 1px solid #EEEDE9; width: 140px;">MERKMAL</th>
      <th style="padding: 10px 14px; text-align: left; border: 1px solid #EEEDE9;">CREATE TABLE AS (CTAS) + spark.read</th>
      <th style="padding: 10px 14px; text-align: left; border: 1px solid #EEEDE9;">COPY INTO</th>
      <th style="padding: 10px 14px; text-align: left; border: 1px solid #EEEDE9;">Auto Loader</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background: #F9F7F4;">
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Ingestion-Typ</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Batch</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Incremental Batch</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Inkrementell (Batch oder Streaming)</td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Anwendungsfälle</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Am besten für kleinere Datensätze</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Ideal für Tausende von Dateien</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Skaliert auf Millionen+ Dateien pro Stunde, Backfills mit Milliarden von Dateien</td>
    </tr>
    <tr style="background: #F9F7F4;">
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Syntax/Schnittstelle</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">
        <ul style="margin: 0; padding-left: 16px;">
          <li>Python (spark.read)</li>
          <li>SQL (CTAS)</li>
        </ul>
      </td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">SQL</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">
        <ul style="margin: 0; padding-left: 16px;">
          <li>Python (spark.readStream)</li>
          <li>SQL mit Declarative Pipelines (CREATE OR REFRESH STREAMING TABLES)</li>
          <li>Streaming Tables in Databricks SQL</li>
        </ul>
      </td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Idempotenz</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Nein</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Ja</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Ja</td>
    </tr>
    <tr style="background: #F9F7F4;">
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Schema-Evolution</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Manuell oder beim Lesen abgeleitet</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Mit Optionen unterstützt</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Auto Loader erkennt und entwickelt Schemas automatisch weiter. Behandelt neue Spalten, sobald sie auftauchen.</td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Latenz</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Hoch</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Moderat (geplant)</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Niedrig oder hoch, abhängig von der Konfiguration</td>
    </tr>
    <tr style="background: #F9F7F4;">
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Benutzerfreundlichkeit</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Einfach</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Einfach und SQL-basiert</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Mittel bis fortgeschritten, abhängig von der Implementierung</td>
    </tr>
    <tr>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9; font-weight: 700;">Zusammenfassung</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Am besten für einmalige, ad hoc Ingestion. Kann so geplant werden, dass stets alle Daten gelesen und verarbeitet werden.</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Einfach und wiederholbar für inkrementelle Datei-Ingestion. Gut geeignet für geplante Jobs oder Pipelines.</td>
      <td style="padding: 10px 14px; border: 1px solid #EEEDE9;">Am besten für nahezu Echtzeit-Streaming oder inkrementelle Ingestion, mit hoher Automatisierung und Skalierbarkeit.</td>
    </tr>
  </tbody>
</table>
