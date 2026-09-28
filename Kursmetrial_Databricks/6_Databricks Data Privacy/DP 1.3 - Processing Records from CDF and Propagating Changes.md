In diesem Notebook zeigen wir, wie Sie Änderungen (Einfügungen, Aktualisierungen und Löschungen) einfach durch ein Lakehouse mit Delta Lake [Change Data Feed (CDF)](https://docs.databricks.com/en/delta/delta-change-data-feed.html) weitergeben können – per Stream oder durch Abfrage einer bestimmten Version.

## Erstellen einer Bronze-Users-Tabelle und Laden von Daten mit Auto Loader

```sql
-- Tabelle löschen, falls vorhanden
DROP TABLE IF EXISTS bronze_users;  

-- Tabelle bronze_users erstellen
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
# Schema für die eingehenden Daten definieren
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

# Streamingdaten aus dem angegebenen Pfad mit dem definierten Schema 
# in die Bronze-Tabelle einlesen
from pyspark.sql.functions import col, expr,date_add

bronze_users_stream = (
      spark
      .readStream
        .format("cloudFiles")  # Format als cloudFiles für Auto Loader angeben
        .option("cloudFiles.format", "json")  # Dateiformat als JSON angeben
        .schema(schema)        # Definiertes Schema auf die eingehenden Daten anwenden
        .load(DA.paths.cdc_stream)            # Daten aus dem angegebenen Pfad laden
      .writeStream
        .format("delta")                      # Streamdaten im Delta-Format schreiben
        .outputMode("append")                 # Neue Datensätze an die Tabelle anhängen
        .trigger(processingTime='3 seconds')
    	# Checkpoint-Speicherort angeben
        .option("checkpointLocation", f"{DA.paths.checkpoints}/bronze")  
        .table("bronze_users"))          # Streamdaten in die Bronze-Tabelle schreiben


# Datei in das Volume laden: DA.paths.cdc_stream
DA.load(copy_from=DA.paths.stream_source.cdf_demo, 
        copy_to=DA.paths.cdc_stream, 
        n=1)
```


## Erstellen einer Zieltabelle **silver_users** und Laden mit unseren Produktionsdaten

Unsere Tabelle **silver_users** wird mit Produktionsdaten unserer Benutzer geladen, um als Basis zu dienen. Hier verwenden wir `DEEP CLONE`, um schreibgeschützte Daten aus PROD in unsere Umgebung zu verschieben, in der wir vollen Schreib-/Löschzugriff haben.

In diesem Fall sind unsere Produktionsdaten als Delta-Tabelle am folgenden Speicherort abgelegt: `Volumes/dbacademy_gym_data/v01/pii/silver`

```sql
DROP TABLE IF EXISTS silver_users;

CREATE OR REPLACE TABLE silver_users
DEEP CLONE delta.`/Volumes/dbacademy_gym_data/v01/pii/silver/`;
```

Um CDF global für jede neue Tabelle zu aktivieren, verwenden Sie folgende Syntax:

```spark.conf.set("spark.databricks.delta.properties.defaults.enableChangeDataFeed", True)```

Tabellen, die nicht mit aktiviertem CDF erstellt wurden, haben dieses standardmäßig nicht aktiviert, können jedoch mit der `ALTER TABLE`-Anweisung so geändert werden, dass Änderungen erfasst werden:

```sql
ALTER TABLE silver_users 
SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
```

## Upsert von Daten von Bronze nach Silver Users

In diesem Abschnitt streamen wir Daten von der Tabelle **bronze_users** in die Tabelle **silver_users**. Wir erstellen die Funktion `upsert_to_delta`, um den Streaming-`MERGE INTO`-Vorgang für die Tabelle **silver_users** zu übernehmen.

Hier erstellen wir die Upsert-Logik für die Tabelle **silver_users** mithilfe eines Streaming-Reads aus der Tabelle **bronze_users**.

```python
def upsert_to_delta(microBatchDF, batchId):
    # Temporäre View für den Micro-Batch-DataFrame erstellen oder ersetzen
    microBatchDF.createOrReplaceTempView("updates")
    
    # MERGE-Operation ausführen, um Daten in die Silver-Tabelle upzuserten
    # Die MERGE-Anweisung gleicht Datensätze in der Tabelle 'silver' mit Datensätzen in der View 'updates' anhand des Felds 'mrn' ab
    # Wird eine Übereinstimmung gefunden und unterscheidet sich mindestens eines der angegebenen Felder, wird der vorhandene Datensatz in 'silver' mit den neuen Werten aus 'updates' aktualisiert
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

Jetzt erstellen und starten wir den Stream von **bronze_users** nach **silver_users**. Die Methode `foreachBatch` verwendet die oben definierte Funktion `upsert_to_delta`, um Daten aus einer Streaming-Abfrage upzuserten.

> **Terminologie-Hinweis (verifiziert gegen [Databricks-Doku „Use foreachBatch to write to arbitrary data sinks"](https://docs.databricks.com/aws/en/structured-streaming/foreach)):** `upsert_to_delta` wird an `foreachBatch` übergeben und von diesem bei jedem Micro-Batch aufgerufen – im allgemeinen Sinne eine **Callback-Funktion**. Die offizielle Databricks-Doku selbst verwendet den Begriff „Callback" jedoch nicht, sondern spricht von einer **„batch function"**, die zwei Parameter erhält: den Micro-Batch-DataFrame und die Batch-ID. Dort steht außerdem explizit: „You must use `foreachBatch` for Delta Lake merge operations in Structured Streaming."

```python
# Stream1: Der erste Stream liest Daten aus unserem Quellordner (Roh-JSON-Dateien) 
# in die Tabelle **bronze_users** ein.
silver_users_stream = (
              spark
              .readStream
                .table("bronze_users")
              .writeStream
                # Micro-Batch-Daten per Upsert in die Silber-Tabelle schreiben
                .foreachBatch(upsert_to_delta)  
                # Die Stream-Verarbeitung alle 3 Sekunden auslösen
                .trigger(processingTime='3 seconds') 
                .start()
        )
```

## Zugriff auf und Lesen des Change Data Feed (CDF)

Um die erfassten CDC-Daten in einem Stream zu erhalten, fügen wir zwei Optionen hinzu:
- **`readChangeData` = True**
- **`startingVersion` = 2** (Dies bezieht sich auf den Versionsverlauf; alternativ können Sie **`startingTimestamp`** verwenden)

Beim Lesen aus dem Change Data Feed enthält das Schema die folgenden Metadatenspalten:

| Spaltenname        | Typ       | Beschreibung                                    |
|--------------------|-----------|--------------------------------------------------|
| _change_type       | String    | Der Typ des Änderungsereignisses: `insert`, `delete`, `update_preimage`, `update_postimage`. |
| _commit_version    | Long      | Die Delta-Log- oder Tabellenversion, die die Änderung enthält |
| _commit_timestamp  | Timestamp | Der Zeitstempel, zu dem der Commit erstellt wurde |

In diesem Abschnitt zeigen wir alle Änderungen an Patienten in der Tabelle **silver_users** ab Version *2* an.

Führen Sie die folgende Zelle aus und betrachten Sie die Ergebnisse. Beachten Sie, dass die Ergebnisse zeigen, dass 1.530 Datensätze geändert wurden.

Scrollen Sie dann nach rechts in der Tabelle. Sie werden die neuen Spalten **_change_type**, **_commit_version** und **_commit_timestamp** bemerken.

**HINWEIS:** Benutzer mit Änderungen haben zwei Datensätze: einen für *update_preimage* und einen für *update_postimage*.

```python
# Stream2: Der zweite Stream synchronisiert Daten per `MERGE INTO` von der 
# Tabelle **bronze_users** in die Tabelle **silver_users**.

cdf_df = (spark.read
          .format("delta")
          .option("readChangeData", True)   # Änderungsdaten lesen
          # Da wir ab Version 2 mit dem Lesen der Änderungen beginnen möchten 
          # (als die Daten gemerged wurden)     
          .option("startingVersion", 2)     
          .table("silver_users"))

## Geänderte Daten anzeigen
display(cdf_df)
```

## F. Die Funktion table_changes

```sql
-- Vorhandene Variable löschen, falls sie existiert
DROP TEMPORARY VARIABLE IF EXISTS latest_version;

-- Variable deklarieren
DECLARE VARIABLE latest_version INT;

-- Variable auf die neueste Version der Tabelle setzen
-- Es erfasst die neueste Version der Tabelle **silver_users** 
-- und speichert sie in einer SQL-Variablen.
SET VARIABLE latest_version = (
  SELECT max(version) AS latest_version
  FROM (DESCRIBE HISTORY silver_users)
);

-- Variable auswählen
SELECT latest_version;
```

- **numTargetRowsInserted**: Die Anzahl der in der neuesten Version eingefügten Zeilen (147 eingefügt).
- **numTargetRowsUpdated**: Die Anzahl der in der neuesten Version aktualisierten Zeilen (809 aktualisiert).
- **numTargetRowsDeleted**: Die Anzahl der in der neuesten Version gelöschten Zeilen (0 gelöscht).

```sql
SELECT 
  operationMetrics['numTargetRowsInserted'],
  operationMetrics['numTargetRowsUpdated'],
  operationMetrics['numTargetRowsDeleted']
FROM (DESCRIBE HISTORY silver_users)
WHERE version = latest_version
```

Um die erfassten CDC-Daten für einen bestimmten Bereich von Versionen im Verlauf einer Tabelle abzurufen, gibt es die Funktion **`table_changes`**, die Teil der Delta Lake Change Data Feed (CDF)-Funktion ist.

Die Spalte **_change_type** ermöglicht es uns, leicht zu erkennen, wie Zeilen geändert wurden.

- *insert*: Zeigt an, dass eine neue Zeile zur Tabelle hinzugefügt wurde.
- *delete*: Zeigt an, dass eine Zeile aus der Tabelle entfernt wurde.
- *update_preimage*: Stellt den Wert einer Zeile vor der Aktualisierung dar.
- *update_postimage*: Stellt den Wert einer Zeile nach der Aktualisierung dar.

```sql
SELECT * 
FROM table_changes("silver_users", latest_version)    -- Neueste Aktualisierung abfragen
WHERE _change_type = "insert"                         -- Alle eingefügten Zeilen anzeigen
ORDER BY _commit_version
```


## G. Weitergabe von Löschungen

Während einige Anwendungsfälle die Verarbeitung von Löschungen zusammen mit Aktualisierungen und Einfügungen erfordern, sind die wichtigsten Löschanfragen diejenigen, die es Unternehmen ermöglichen, die Einhaltung von Datenschutzbestimmungen wie der DSGVO und dem CCPA zu gewährleisten. Die meisten Unternehmen haben festgelegte SLAs, wie lange die Bearbeitung dieser Anfragen dauern darf, aber aus verschiedenen Gründen werden diese oft in Pipelines behandelt, die von ihrer Kern-ETL getrennt sind.

Dieser Abschnitt konzentriert sich auf die Weitergabe von Löschungen, die in **silver_users** angewendet wurden, an die Tabelle **gold_users**.

**HINWEIS:** Bitte befolgen Sie alle regulatorischen Standards für Ihre Daten.


### G1. Einrichtung der Tabelle Gold Users

Erstellen wir zunächst die Tabelle **gold_users**, unsere finale Produktionstabelle.

Führen Sie die folgende Abfrage aus, um die Tabelle **gold_users** zu erstellen und mit dem neuesten Snapshot der Tabelle **silver_users** zu befüllen. Betrachten Sie nach Ausführung der Abfrage die Ergebnisse und bestätigen Sie, dass die Tabelle *3.407* Datensätze enthält.

```sql
DROP TABLE IF EXISTS gold_users;

-- Tabelle gold_users aus der Tabelle silver_users erstellen
CREATE OR REPLACE TABLE gold_users as
SELECT 
     mrn,
     street_address,
     zip,
     city,
     state,
     updated
FROM silver_users;

-- Gold-Tabelle anzeigen
SELECT * 
FROM gold_users;
```


### G2. Verarbeitung von "Recht auf Vergessenwerden"-Anfragen

Obwohl es möglich ist, Löschungen gleichzeitig mit Anfügungen und Aktualisierungen zu verarbeiten, können die Bußgelder im Zusammenhang mit "Recht auf Vergessenwerden"-Anfragen einen separaten Prozess rechtfertigen.

Beginnen wir, indem wir die Tabelle **user_delete_requests** nutzen. Diese Tabelle enthält die **mrn** und das **request_date** (zum heutigen Datum) für Benutzer, die gelöscht werden sollen, wie vom Compliance-Team bereitgestellt.

Fragen wir die Tabelle ab und betrachten wir die Löschanfragen. Bestätigen Sie, dass die Tabelle derzeit 20 Löschanfragen enthält.

```sql
SELECT *
FROM user_delete_requests;
```


Wir erstellen einen neuen Read-Stream aus der Tabelle **user_delete_requests**, um Folgendes umzusetzen:
- Hinzufügen einer Spalte namens **deadline**, die einen Zeitraum von 30 Tagen für die Bearbeitung angibt, mit einem Standardstatus von *requested*.
- Hinzufügen einer Spalte namens **status**, die von *requested* auf *deleted* aktualisiert wird, sobald die Änderungen weitergegeben wurden.


Führen Sie die Abfrage aus und betrachten Sie die Ergebnisse.

```python
requests_df = (spark.readStream
                    .table("user_delete_requests")
                    .select(
                            "mrn",
                            "request_date",
                            F.date_add("request_date", 30).alias("deadline"),
                            F.lit("requested").alias("status")))


display(requests_df)
```

### G3. Hinzufügen von Commit-Nachrichten im Verlauf

Delta Lake unterstützt beliebige Commit-Nachrichten, die im Delta-Transaktionsprotokoll erfasst und im Tabellenverlauf sichtbar sind. Diese Funktion kann bei der Auditierung helfen.

Das Setzen einer globalen Commit-Nachricht mit SQL stellt sicher, dass sie für alle nachfolgenden Vorgänge im Notebook verwendet wird.

Weitere Informationen finden Sie in der Dokumentation [Enrich Delta Lake tables with custom metadata](https://docs.databricks.com/en/delta/custom-metadata.html#enrich-delta-lake-tables-with-custom-metadata).

```sql
SET spark.databricks.delta.commitInfo.userMetadata=Deletes committed
```




Bei DataFrames können Commit-Nachrichten auch als Teil der Schreiboptionen mit `option("userMetadata","comment")` angegeben werden.

In diesem Abschnitt erstellen wir eine neue Streaming-Tabelle namens **delete_requests**, um anzuzeigen, dass wir diese Anfragen manuell im Notebook verarbeiten, anstatt einen automatisierten Job zu verwenden.

```python
query = (requests_df
         .writeStream
            .outputMode("append")        # Append-Modus, um neue Zeilen an die Ausgabetabelle anzuhängen
            .option("checkpointLocation", f"{DA.paths.checkpoints}/delete_requests")  # Checkpoint-Speicherort angeben
            .option("userMetadata", "Requests processed interactively")  # Benutzer-Metadaten hinzufügen
            .trigger(availableNow=True)  # Abfrage auslösen, um alle verfügbaren Daten jetzt zu verarbeiten
            .table("delete_requests"))   # Ausgabe in die Tabelle delete_requests schreiben


query.awaitTermination()  # Auf den Abschluss der Streaming-Abfrage warten
```

Betrachten Sie den Verlauf der Tabelle **delete_requests**. Beachten Sie, dass die Meldungen in der Spalte **operation** im Tabellenverlauf deutlich *CREATE TABLE* und *STREAMING UPDATE* anzeigen.

Scrollen Sie nach rechts in der Tabelle. Beachten Sie Folgendes:
- Die Spalte **userMetadata** enthält die oben für den Stream gesetzte Metadatennotiz *Requests processed interactively*.
- Der anfängliche *CREATE TABLE*-Eintrag enthält die Benutzer-Metadaten *Deletes committed* für die Erstellung der Tabelle. 

```sql
DESCRIBE HISTORY delete_requests
```




### G4. Verarbeitung von Löschanfragen

Die Tabelle **delete_requests** wird verwendet, um Anfragen von Benutzern auf Vergessenwerden nachzuverfolgen. 

Es ist möglich, Löschanfragen zusammen mit Einfügungen und Aktualisierungen bestehender Daten im Rahmen einer normalen **`MERGE`**-Anweisung zu verarbeiten.

Da PII an mehreren Stellen im aktuellen Lakehouse vorhanden ist, kann die Nachverfolgung von Anfragen und deren asynchrone Verarbeitung eine bessere Performance für Produktions-Jobs mit niedrigen Latenz-SLAs bieten. Der hier modellierte Ansatz gibt außerdem den Zeitpunkt an, zu dem die Löschung angefragt wurde, sowie die Frist, und bietet ein Feld zur Angabe des aktuellen Bearbeitungsstatus der Anfrage.

Fragen Sie die neue Tabelle **delete_requests** ab und betrachten Sie die Ergebnisse. Beachten Sie, dass die Löschanfragen aktiv sind, mit dem **status** *requested*.

```sql
SELECT * 
FROM delete_requests;
```

### G5. Überprüfen der zu löschenden Datensätze

Beim Arbeiten mit statischen Daten ist das Committen von Löschungen unkompliziert. Führen Sie die folgende Zelle aus, um eine Vorschau der aus der Tabelle **silver_users** zu löschenden Datensätze anzuzeigen. Beachten Sie, dass die Tabelle **silver_users** alle Benutzer enthält, die eine Löschung beantragt haben.

```sql
SELECT *
FROM silver_users
WHERE mrn IN (SELECT mrn FROM delete_requests)
```


### G6. Committen von Löschungen in Silver Users

Die folgende Zelle löscht Datensätze aus der Tabelle **silver_users**, indem alle Datendateien, die von der `DELETE`-Anweisung betroffene Datensätze enthalten, neu geschrieben werden. 

**HINWEIS:** Denken Sie daran, dass bei Delta Lake das Löschen von Daten neue Datendateien erzeugt, anstatt vorhandene Datendateien zu löschen.

```sql
DELETE FROM silver_users
WHERE mrn IN (SELECT mrn FROM delete_requests)
```

Beschreiben Sie den Verlauf der Tabelle **silver_users** und bestätigen Sie, dass *4* Versionen der Tabelle existieren. Die neueste Version enthält den Wert *DELETE* in der Spalte **operation**.

```sql
DESCRIBE HISTORY silver_users;
```

### G7. Gelöschte Silver Users zur Weitergabe mit CDF erfassen

Der folgende Code konfiguriert einen inkrementellen Read aller an die Tabelle **silver_users** committeten Änderungen, beginnend bei Version *4*, dem Löschvorgang.

Führen Sie die Zelle aus und betrachten Sie die Ergebnisse. Scrollen Sie nach rechts in der Tabelle und beachten Sie, dass in dieser Version *20* Zeilen aus der Tabelle **silver_users** gelöscht wurden. Sie können mit CDF genau sehen, welche Zeilen gelöscht wurden.

```python
deleteDF = (spark.readStream
                 .format("delta")
                 .option("readChangeFeed", "true")
                 .option("startingVersion", 4)     # Start_version 4, an der der Löschvorgang stattfand
                 .table("silver_users"))


display(deleteDF)
```

### G8. Funktion zur Weitergabe von Löschungen

Die Beziehungen zwischen unseren natürlichen Schlüsseln (**mrn**) werden in der Tabelle **silver_users** gespeichert. Diese Schlüssel ermöglichen es uns, die Daten eines Benutzers über verschiedene Pipelines und Quellen hinweg zu verknüpfen. Der Change Data Feed (CDF) dieser Tabelle behält alle diese Felder bei, wodurch die Datensätze, die in nachgelagerten Tabellen gelöscht oder geändert werden sollen, erfolgreich identifiziert werden können. Dieser Ansatz kann erweitert werden, um Hash-Werte oder andere relevante Schlüssel zu verwenden.

Die folgende Funktion zeigt, wie Löschungen in zwei Tabellen mit unterschiedlichen Schlüsseln und unterschiedlicher Syntax committet werden. Beachten Sie, dass in diesem Fall die `MERGE INTO`-Syntax nicht unbedingt die einzige Methode ist, um Löschungen in der Tabelle **gold_users** zu verarbeiten. Dieser Codeblock zeigt jedoch die grundlegende Syntax, die erweitert werden könnte, wenn Einfügungen und Aktualisierungen zusammen mit Löschungen in derselben Operation verarbeitet würden.

Unter der Annahme, dass diese beiden Tabellenänderungen erfolgreich abgeschlossen wurden, wird auch eine Aktualisierung an die Tabelle **delete_requests** zurückgeschrieben. 

Der folgende Code führt für jeden Batch Folgendes aus:
- Löscht angeforderte Zeilen in der Tabelle **gold_users**.
- Aktualisiert den Status der angeforderten Löschungen in der Tabelle **delete_requests**.

```python
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


### G9. Weitergabe von Änderungen an Gold Users und Delete Requests

Denken Sie daran, dass dieser Workload durch inkrementelle Änderungen an der Tabelle **silver_users** gesteuert wird (nachverfolgt über den Change Data Feed).

Das Ausführen der folgenden Zelle gibt Löschungen von einer einzelnen Tabelle an mehrere Tabellen im gesamten Lakehouse weiter.

```python
query = (deleteDF.writeStream
                 .foreachBatch(process_deletes)
                 .outputMode("update")
                 .option("checkpointLocation", f"{DA.paths.checkpoints}/deletes")
                 .trigger(availableNow=True)
                 .start())

query.awaitTermination()
```


### G10. Überprüfung der Löschungs-Commits
Beachten Sie, dass der **status** für die Datensätze in der Tabelle **delete_requests** nun auf *deleted* aktualisiert ist.

```sql
SELECT * 
FROM delete_requests;
```


Beschreiben Sie den Verlauf der Tabelle **gold_users**.

Beachten Sie, dass in der neuesten Version unsere Commit-Nachricht in der äußersten rechten Spalte unseres Verlaufs unter der Spalte **userMetadata** zu finden ist.

Für die Tabelle **gold_users** zeigt die Spalte **operation** im Verlauf einen Merge an, aufgrund der gewählten Syntax, obwohl nur Löschungen committet wurden. Die Anzahl der gelöschten Zeilen kann in **operationMetrics** unter dem Schlüssel *numTargetRowsDeleted* überprüft werden.

```sql
DESCRIBE HISTORY gold_users;
```

Zählen Sie die Anzahl der Zeilen in der aktuellen Tabelle **gold_users**. Bestätigen Sie, dass die Tabelle jetzt *3.387* Zeilen enthält.

```sql
SELECT count(*) AS TotalRows
FROM gold_users;
```

### G11. Sind Löschungen vollständig committet?

Nicht ganz.

Aufgrund der Art und Weise, wie die Verlaufs- und CDF-Funktionen von Delta Lake implementiert sind, sind gelöschte Werte in älteren Versionen der Daten weiterhin vorhanden.

Führen Sie die folgende Abfrage aus, um die Anzahl der Datensätze in Version 0 der Tabelle **gold_users** zu zählen. Die Ergebnisse zeigen, dass die ursprüngliche Tabelle 3.407 Zeilen enthält, einschließlich der gelöschten Zeilen.

Bei Delta-Tabellen können Sie die ursprünglichen Daten weiterhin in einer früheren Version der Tabelle einsehen.

```sql
SELECT count(*) AS TotalRows
FROM gold_users VERSION AS OF 0;
```

Weitere Informationen finden Sie unter [GDPR and CCPA compliance with Delta Lake](https://docs.databricks.com/en/security/privacy/gdpr-delta.html#how-delta-lake-simplifies-point-deletes) und der [VACUUM](https://docs.databricks.com/en/sql/language-manual/delta-vacuum.html)-Anweisung.


## H. Aktive Streams beenden
Stellen Sie sicher, dass Sie die folgende Zelle ausführen, um alle aktiven Streams zu beenden. Seien Sie vorsichtig beim Umgang mit Streaming. Wenn Sie einen aktiven Stream nicht beenden, läuft der Cluster kontinuierlich weiter. Wir sind mit dem Streaming von Daten in dieser Demonstration fertig.

```python
for stream in spark.streams.active:
    stream.stop()
    stream.awaitTermination()
```

&copy; 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der <a href="https://www.apache.org/" target="_blank">Apache Software Foundation</a>.<br/><br/><a href="https://databricks.com/privacy-policy" target="_blank">Datenschutzrichtlinie</a> | <a href="https://databricks.com/terms-of-use" target="_blank">Nutzungsbedingungen</a> | <a href="https://help.databricks.com/" target="_blank">Support</a>
