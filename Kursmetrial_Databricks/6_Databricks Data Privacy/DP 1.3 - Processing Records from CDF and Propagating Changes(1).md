```sql
-- Drop Table if exists
DROP TABLE IF EXISTS bronze_users;  

-- Create bronze_users table
CREATE TABLE IF NOT EXISTS bronze_users ( 
  mrn BIGINT, 
  dob DATE, 
  sex STRING, 
  gender STRING, 
  first_name STRING, 
  last_name STRING, 
  street_address STRING, 
  zip BIGINT, city STRING, 
  state STRING, 
  updated timestamp
);
```

```python
# Das Schema für die eingehenden Daten definieren
schema = """
  mrn BIGINT, 
  dob DATE, 
  sex STRING, 
  gender STRING, 
  first_name STRING, 
  last_name STRING, 
  street_address STRING, 
  zip BIGINT, 
  city STRING, 
  state STRING, 
  updated TIMESTAMP
"""

# Die Streaming-Daten mit dem definierten Schema aus dem angegebenen Pfad in die Bronze-Tabelle lesen
from pyspark.sql.functions import col, expr,date_add

bronze_users_stream = (
      spark
      .readStream
        .format("cloudFiles")                 # Format cloudFiles für Auto Loader angeben
        .option("cloudFiles.format", "json")  # Dateiformat JSON angeben
        .schema(schema)                       # Das definierte Schema auf die eingehenden Daten anwenden
        .load(DA.paths.cdc_stream)            # Die Daten aus dem angegebenen Pfad laden
      .writeStream
        .format("delta")                      # Die Stream-Daten im Delta-Format schreiben
        .outputMode("append")                 # Neue Datensätze an die Tabelle anhängen
        .trigger(processingTime='3 seconds')
        .option("checkpointLocation", f"{DA.paths.checkpoints}/bronze")  # Specify the checkpoint location
        .table("bronze_users"))               # Die Stream-Daten in die Bronze-Tabelle schreiben


# Eine Datei in das Volume laden: DA.paths.cdc_stream
DA.load(copy_from=DA.paths.stream_source.cdf_demo, 
        copy_to=DA.paths.cdc_stream, 
        n=1)
```

```sql
SELECT * FROM bronze_users limit 2;
```

```sql
DROP TABLE IF EXISTS silver_users;

CREATE OR REPLACE TABLE silver_users
DEEP CLONE delta.`/Volumes/dbacademy_gym_data/v01/pii/silver/`;
```

```sql
-- Um CDF global für jede neue Tabelle zu aktivieren, verwenden Sie folgende Syntax:
-- spark.conf.set("spark.databricks.delta.properties.defaults.enableChangeDataFeed", True)

ALTER TABLE silver_users SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

```sql
-- Prüfen, ob CDF aktiviert ist: Sehen Sie sich in der Ausgabe die letzte Zeile unter Table Properties an und bestätigen Sie, dass CDF mit der Eigenschaft [delta.enableChangeDataFeed=true] gesetzt ist.
-- DESCRIBE TABLE EXTENDED silver_users;
-- Mit diesem Befehl sieht man nur Table Properties
SHOW TBLPROPERTIES silver_users ('delta.enableChangeDataFeed');
```

```sql
SELECT * FROM silver_users limit 2;
```

```python
def upsert_to_delta(microBatchDF, batchId):
    # Eine temporäre View für den Micro-Batch-DataFrame erstellen oder ersetzen
    microBatchDF.createOrReplaceTempView("updates")
    
    # Eine MERGE-Operation ausführen, um Daten per Upsert in die Silber-Tabelle zu schreiben
    # Die MERGE-Anweisung gleicht Datensätze der Tabelle 'silver' anhand des Felds 'mrn' mit Datensätzen der View 'updates' ab
    # Wird eine Übereinstimmung gefunden und unterscheidet sich eines der angegebenen Felder, wird der vorhandene Datensatz in 'silver' mit den neuen Werten aus 'updates' aktualisiert
    # Wird keine Übereinstimmung gefunden, wird ein neuer Datensatz mit den Werten aus 'updates' in 'silver' eingefügt
    microBatchDF._jdf.sparkSession().sql("""
        MERGE INTO silver_users s
        USING updates u
        ON s.mrn = u.mrn
        WHEN MATCHED AND s.dob <> u.dob OR
                         s.sex <> u.sex OR
                         s.gender <> u.gender OR
                         s.first_name <> u.first_name OR
                         s.last_name <> u.last_name OR
                         s.street_address <> u.street_address OR
                         s.zip <> u.zip OR
                         s.city <> u.city OR
                         s.state <> u.state OR
                         s.updated <> u.updated
            THEN UPDATE SET *
        WHEN NOT MATCHED
            THEN INSERT *
    """)
```

```python

silver_users_stream = (
              spark
              .readStream
                .table("bronze_users")
              .writeStream
                .foreachBatch(upsert_to_delta)  # Micro-Batch-Daten per Upsert in die Silber-Tabelle schreiben
                .trigger(processingTime='3 seconds')  # Trigger the stream processing every 3 seconds
                .start()
        )
```

```sql
-- Beim Ausführen der Zelle wird die Historie dieser Tabelle angezeigt; es sollte drei Protokolleinträge geben:
-- Version 0: The initial clone
-- Version 1: Setzen der Tabelleneigenschaften, um CDF auf der Tabelle zu aktivieren
-- Version 2: Der MERGE-Stream aus der Tabelle bronze_users.
SELECT version, operation FROM (DESCRIBE HISTORY silver_users)
```

```python
# Beim Lesen aus dem Change Data Feed enthält das Schema die folgenden Metadatenspalten: _change_type, _commit_version, _commit_timestamp
cdf_df = (spark.read
               .format("delta")
               .option("readChangeData", True)   # Read the change data
               .option("startingVersion", 2)     # Da wir Änderungen ab Version 2 lesen möchten (als wir die Daten gemergt haben)
               .table("silver_users"))

## Display the changed data
display(cdf_df.where("mrn = 63729051").select("updated", "_change_type", "_commit_version", "_commit_timestamp"))
```

```python
# Dateien in das Volume laden: DA.paths.cdc_stream
DA.load(copy_from=DA.paths.stream_source.cdf_demo, 
        copy_to=DA.paths.cdc_stream, 
        n=2)
```

```sql
-- Sehen Sie sich nach dem Ausführen der Zelle die Ergebnisse an und bestätigen Sie, dass Version 3 nun in der Historie verfügbar ist 
-- mit einer MERGE-Operation. Dies sollte der letzten Zelle entsprechen, in der neue Dateien geladen wurden.
SELECT version, operation FROM (DESCRIBE HISTORY silver_users);
```

```sql
-- Die vorhandene Variable löschen, falls sie existiert
DROP TEMPORARY VARIABLE IF EXISTS latest_version;

-- Declare the variable
DECLARE VARIABLE latest_version INT;

-- Die Variable auf die neueste Version der Tabelle setzen
SET VARIABLE latest_version = (
  SELECT max(version) AS latest_version
  FROM (DESCRIBE HISTORY silver_users)
);

-- Die Variable auswählen
SELECT latest_version;
```

```sql
-- Diese Zelle fragt mithilfe der Variablen latest_version die neueste Historie der Tabelle ab
SELECT 
  operationMetrics['numTargetRowsInserted'],
  operationMetrics['numTargetRowsUpdated'],
  operationMetrics['numTargetRowsDeleted']
FROM (DESCRIBE HISTORY silver_users)
WHERE version = latest_version
```

```sql
-- mögliche Werte in _change_type sind insert, update_postimage, update_preimage, delete
SELECT mrn, _change_type, _commit_version, _commit_timestamp
FROM table_changes("silver_users", latest_version)
WHERE _change_type = "insert" -- insert, update_postimage, update_preimage, delete
ORDER BY _commit_version
LIMIT 2;
```

```sql
DROP TABLE IF EXISTS gold_users;

CREATE OR REPLACE TABLE gold_users as
SELECT mrn, street_address, zip, city, state, updated
FROM silver_users;

SELECT * FROM gold_users LIMIT 2;
```

```sql
-- Gesamtzahl von Zeilen ist 20
SELECT * FROM user_delete_requests LIMIT 2;
```

```python
requests_df = (spark.readStream
                    .table("user_delete_requests")
                    .select(
                            "mrn",
                            "request_date",
                            F.date_add("request_date", 30).alias("deadline"),
                            F.lit("requested").alias("status")))


display(requests_df.limit(2))
```

```sql
-- Delta Lake unterstützt beliebige Commit-Nachrichten, die im Delta-Transaktionsprotokoll aufgezeichnet werden und in der Tabellenhistorie sichtbar sind.
-- Wird mit SQL eine globale Commit-Nachricht gesetzt, wird sie für alle nachfolgenden Operationen im Notebook verwendet.
SET spark.databricks.delta.commitInfo.userMetadata=Deletes committed
```

```python
# Bei DataFrames können Commit-Nachrichten auch als Teil der Schreiboptionen über 'option("userMetadata","comment")' angegeben werden.
query = (requests_df
         .writeStream
            .outputMode("append")        # Append-Modus, um neue Zeilen zur Ausgabetabelle hinzuzufügen
            .option("checkpointLocation", f"{DA.paths.checkpoints}/delete_requests")  # Specify checkpoint location
            .option("userMetadata", "Requests processed interactively")  # Add user metadata
            .trigger(availableNow=True)  # Die Abfrage auslösen, um jetzt alle verfügbaren Daten zu verarbeiten
            .table("delete_requests"))   # Die Ausgabe in die Tabelle delete_requests schreiben


query.awaitTermination()  # Warten, bis die Streaming-Abfrage beendet ist
```

```sql
-- Beachten Sie, dass die Meldungen in der Spalte operation in der Tabellenhistorie eindeutig CREATE TABLE und STREAMING UPDATE anzeigen.
-- Beachten Sie Folgendes:
--     dass die Spalte userMetadata die oben für den Stream gesetzte Metadatennotiz Requests processed interactively enthält.
--     das anfängliche CREATE TABLE enthält für die Erstellung der Tabelle die Benutzer-Metadaten Deletes committed.
SELECT version, operation, userMetadata FROM (DESCRIBE HISTORY delete_requests)
```

```sql
-- Beachten Sie, dass die Löschanfragen aktiv sind und den Status requested haben.
-- Count of rows: 20
SELECT * FROM delete_requests limit 2;
```

```sql
-- Beachten Sie, dass die Tabelle silver_users alle Benutzer enthält, die eine Löschung angefordert haben.
SELECT COUNT(*) FROM silver_users WHERE mrn IN (SELECT mrn FROM delete_requests)
```

```sql
-- Die folgende Zelle löscht Datensätze aus der Tabelle silver_users, indem alle Datendateien neu geschrieben werden, die von der DELETE-Anweisung betroffene Datensätze enthalten.
DELETE FROM silver_users WHERE mrn IN (SELECT mrn FROM delete_requests)
```

```sql
-- Die Historie der Tabelle silver_users beschreiben und bestätigen, dass 4 Versionen der Tabelle existieren. Die neueste Version enthält in der Spalte operation den Wert DELETE.
SELECT version, operation, userMetadata FROM (DESCRIBE HISTORY silver_users);
```

```python
# Beachten Sie, dass in dieser Version 20 Zeilen aus der Tabelle silver_users gelöscht wurden. 
# Mit CDF können Sie genau sehen, welche Zeilen gelöscht wurden.
deleteDF = (spark.readStream
                 .format("delta")
                 .option("readChangeFeed", "true")
                 .option("startingVersion", 4)     # Startversion 4, in der die Löschoperation stattfand
                 .table("silver_users"))


display(deleteDF)
```

```python
# Function to Propagate Deletes:
#    Löscht die angeforderten Zeilen in der Tabelle gold_users.
#    Aktualisiert den Status der angeforderten Löschungen in der Tabelle delete_requests.
def process_deletes(microBatchDF, batchId):
    
    (microBatchDF
        .createOrReplaceTempView("deletes"))
    
    microBatchDF._jdf.sparkSession().sql("""
        MERGE INTO gold_users u
        USING deletes d
        ON u.mrn = d.mrn
        WHEN MATCHED
            THEN DELETE
    """)

    
    microBatchDF._jdf.sparkSession().sql("""
        MERGE INTO delete_requests dr
        USING deletes d
        ON d.mrn = dr.mrn
        WHEN MATCHED
          THEN UPDATE SET status = "deleted"
    """)
```

```python
# Änderungen in Gold Users und Delete Requests weitergeben
# Die folgende Zelle gibt Löschungen aus einer einzelnen Tabelle an mehrere Tabellen im gesamten Lakehouse weiter.
query = (deleteDF.writeStream
                 .foreachBatch(process_deletes)
                 .outputMode("update")
                 .option("checkpointLocation", f"{DA.paths.checkpoints}/deletes")
                 .trigger(availableNow=True)
                 .start())

query.awaitTermination()
```

```sql
-- Beachten Sie, dass der Status der Datensätze in der Tabelle delete_requests nun auf deleted aktualisiert wurde.
SELECT * FROM delete_requests limit 2;
```

```sql
-- Beachten Sie, dass unsere Commit-Nachricht in der neuesten Version ganz rechts in unserer Historie in der Spalte userMetadata steht.
-- Für die Tabelle gold_users zeigt die Spalte operation in der Historie aufgrund der gewählten Syntax einen Merge an, obwohl nur Löschungen committet wurden. 
-- Die Anzahl der gelöschten Zeilen lässt sich in operationMetrics unter dem Schlüssel numTargetRowsDeleted prüfen.
SELECT version, operation, userMetadata FROM (DESCRIBE HISTORY gold_users);
```

```sql
-- Die Zeilen in der aktuellen Tabelle gold_users zählen. Bestätigen, dass die Tabelle jetzt 3.387 Zeilen hat.
SELECT count(*) AS TotalRows FROM gold_users;
```

```sql
-- Die folgende Abfrage ausführen, um die Datensätze aus Version 0 der Tabelle gold_users zu zählen. 
SELECT count(*) AS TotalRows FROM gold_users VERSION AS OF 0;
```

```python
# Führen Sie unbedingt die folgende Zelle aus, um alle aktiven Streams zu stoppen.
for stream in spark.streams.active:
    stream.stop()
    stream.awaitTermination()
```
