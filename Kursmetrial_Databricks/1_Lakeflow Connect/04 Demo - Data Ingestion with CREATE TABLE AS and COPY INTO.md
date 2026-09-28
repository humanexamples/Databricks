```sql
-- Die Parquet-Dateien abfragen
SELECT * 
FROM parquet.`/Volumes/dbacademy_ecommerce/v01/raw/users-historical`;
```

Apache Parquet ist ein spaltenorientiertes Speicherformat, das für analytische Abfragen optimiert ist. Es enthält eingebettete Schema-Metadaten (z. B. Spaltennamen und Datentypen), die eine automatische Schema-Inferenz beim Erstellen von Tabellen aus Parquet-Dateien ermöglichen. Dadurch entfällt die Notwendigkeit manueller Schemadefinitionen, und die Konvertierung von Parquet-Dateien in das Delta-Format wird durch die Nutzung der eingebauten Schema-Metadaten vereinfacht.

### C1. CTAS mit der Funktion `read_files()`

Der Code in der nächsten Zelle erstellt eine Tabelle mit CTAS und der Funktion `read_files()`.

Die tabellenwertige Funktion (TVF) `read_files()` ermöglicht das Lesen verschiedenster Dateiformate und bietet zusätzliche Optionen für die Daten-Ingestion.

Die Funktion `read_files` bietet ein breites Spektrum an Möglichkeiten und spezifischen Optionen für jeden Dateityp. Die zuvor verwendete Methode zum Erstellen einer Tabelle funktioniert nur, wenn keine zusätzlichen Optionen erforderlich sind.

Eine Spalte **_rescued_data** wird standardmäßig automatisch hinzugefügt, um alle Daten zu erfassen, die nicht zum abgeleiteten Schema passen.

```sql
SELECT * 
FROM read_files(
    '/Volumes/dbacademy_ecommerce/v01/raw/users-historical', format => 'parquet');
```

Als Nächstes verwenden wir `read_files()` mit einer CTAS-Anweisung, um die Tabelle **historical_users_bronze_ctas_rf** zu erstellen, und zeigen die Tabelle anschließend an.

Beachten Sie, dass die Parquet-Dateien ingestiert wurden, um eine Tabelle (standardmäßig Delta) zu erstellen.

```sql
-- Tabelle zu Demonstrationszwecken löschen, falls sie existiert
DROP TABLE IF EXISTS historical_users_bronze_ctas_rf;

-- Die UC-Tabelle erstellen
CREATE TABLE historical_users_bronze_ctas_rf 
SELECT * 
FROM read_files(
        '/Volumes/dbacademy_ecommerce/v01/raw/users-historical',
        format => 'parquet');
```

```sql
DESCRIBE TABLE EXTENDED historical_users_bronze_ctas_rf;
```

#### Managed vs. External Tables in Databricks

##### Managed Tables
- Databricks **verwaltet sowohl die Daten als auch die Metadaten**.
- Die Daten werden **im von Databricks verwalteten Speicher** abgelegt.
- **Beim Löschen der Tabelle werden auch die Daten gelöscht**.
- Empfohlen für das Erstellen neuer Tabellen.

##### External Tables
- Databricks **verwaltet nur die Metadaten der Tabelle**.
- **Beim Löschen der Tabelle werden die Daten nicht gelöscht**.
- Unterstützt **mehrere Formate**, einschließlich Delta Lake.
- Ideal zum **plattformübergreifenden Teilen von Daten** oder zur Nutzung bestehender externer Daten.

### C2. (BONUS) Ingestion mit Python
Der Code verwendet Python, um die Parquet-Dateien zu ingestieren.

```python
# 1. Die Parquet-Dateien aus dem Volume in einen Spark DataFrame einlesen
df = (spark
      .read
      .format("parquet")
      .load("/Volumes/dbacademy_ecommerce/v01/raw/users-historical")
    )


# 2. Den DataFrame in eine UC-Tabelle schreiben (Tabelle überschreiben, falls sie existiert)
(df
 .write
 .mode("overwrite")
 .saveAsTable(f"{my_catalog}.data_ingestion.historical_users_bronze_python")
)


## 3. Die Tabelle lesen und anzeigen
users_bronze_table = spark.table(f"{my_catalog}.data_ingestion.historical_users_bronze_python")
users_bronze_table.display()
```

## D. Inkrementelle Daten-Ingestion mit `COPY INTO`
Führen Sie die folgende Zelle aus und sehen Sie sich den Fehler an. Sie sollten den Fehler `[COPY_INTO_SCHEMA_MISMATCH_WITH_TARGET_TABLE]` sehen. Dieser Fehler tritt auf, weil die Schemas nicht übereinstimmen: Die Parquet-Dateien enthalten 3 Spalten, die Zieltabelle **historical_users_bronze_ci** hat jedoch nur 2 Spalten.

Wie können Sie diesen Fehler behandeln?

```sql
-- Tabelle zu Demonstrationszwecken löschen, falls sie existiert
DROP TABLE IF EXISTS historical_users_bronze_ci;


-- Eine leere Tabelle mit dem angegebenen Tabellenschema erstellen (nur 2 der 3 Spalten)
CREATE TABLE historical_users_bronze_ci (
  user_id STRING,
  user_first_touch_timestamp BIGINT
);


-- COPY INTO verwenden, um die UC-Tabelle zu befüllen
COPY INTO historical_users_bronze_ci
  FROM '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
  FILEFORMAT = parquet;
```

Wir können diesen Fehler beheben, indem wir `COPY_OPTIONS` mit der Option `mergeSchema = 'true'` hinzufügen. Wenn diese Option auf `true` gesetzt ist, kann sich das Schema anhand der eingehenden Daten weiterentwickeln.

```sql
COPY INTO historical_users_bronze_ci
  FROM '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
  FILEFORMAT = parquet
  COPY_OPTIONS ('mergeSchema' = 'true');     -- Das Schema jeder Datei zusammenführen
```

```sql
SELECT * FROM historical_users_bronze_ci LIMIT 10;
```

#### Beispiel 2: Schema Evolution vorausschauend behandeln

Eine andere Möglichkeit, dieselben Dateien in eine UC-Tabelle zu ingestieren, besteht darin, zunächst eine leere Tabelle namens **historical_users_bronze_ci_no_schema** zu erstellen. Fügen Sie dann die Option `COPY_OPTIONS ('mergeSchema' = 'true')` hinzu, um Schema Evolution für die Tabelle zu aktivieren.

```sql
-- Tabelle zu Demonstrationszwecken löschen, falls sie existiert
DROP TABLE IF EXISTS historical_users_bronze_ci_no_schema;


-- Eine leere Tabelle ohne angegebenes Schema erstellen
CREATE TABLE historical_users_bronze_ci_no_schema;


-- COPY INTO verwenden, um die UC-Tabelle zu befüllen
COPY INTO historical_users_bronze_ci_no_schema
  FROM '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
  FILEFORMAT = parquet
  COPY_OPTIONS ('mergeSchema' = 'true');
```

### D2. Idempotenz (inkrementelle Ingestion)

`COPY INTO` merkt sich die Dateien, die es bereits ingestiert hat. Wird der Befehl erneut ausgeführt, werden keine zusätzlichen Daten ingestiert, da sich die Dateien im Quellverzeichnis nicht geändert haben.

Wenn dem Cloud-Speicherort neue Dateien hinzugefügt werden, ingestiert `COPY INTO` nur diese Dateien. `COPY INTO` ist eine hervorragende Option, wenn Sie einen Job für inkrementelle Batch-Ingestion von einem Cloud-Speicherort ausführen möchten, ohne bereits geladene Dateien erneut einzulesen.

```sql
COPY INTO historical_users_bronze_ci_no_schema
  FROM '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
  FILEFORMAT = parquet
  COPY_OPTIONS ('mergeSchema' = 'true');
```

**HINWEIS:** In den restlichen Demos konzentrieren wir uns nicht auf `COPY INTO`, sondern auf die Nutzung der Funktion `read_files`. Mit wachsender Erfahrung können Sie beginnen, Streaming Tables für inkrementelle oder Streaming-Ingestion mit SQL und Apache Spark Declarative Pipelines zu erstellen.
