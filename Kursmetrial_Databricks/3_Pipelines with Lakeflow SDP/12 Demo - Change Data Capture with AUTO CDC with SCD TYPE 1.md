

Wir bauen unsere Pipeline weiter aus, indem wir **Kunden**daten ingestieren. 

Wie können wir neue Rohdaten-Quelldateien (JSON) mit Kundenaktualisierungen in unsere Pipeline ingestieren, um die Tabelle **customers_silver** bei Inserts, Updates oder Deletes zu aktualisieren, ohne historische Datensätze zu führen (SCD Type 1)?

```sql
CREATE STREAMING TABLE 1_bronze_db.customers_bronze_clean_demo12
(
CONSTRAINT valid_id EXPECT (customer_id IS NOT NULL) ON VIOLATION FAIL UPDATE,
CONSTRAINT valid_operation EXPECT (operation IS NOT NULL) ON VIOLATION DROP ROW,
CONSTRAINT valid_name EXPECT (name IS NOT NULL OR operation = "DELETE"),
CONSTRAINT valid_address EXPECT (
(address IS NOT NULL AND
city IS NOT NULL AND
state IS NOT NULL AND
zip_code IS NOT NULL) OR
operation = "DELETE"),
CONSTRAINT valid_email EXPECT (
rlike(email, '^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$') OR
operation = "DELETE") ON VIOLATION DROP ROW
)
COMMENT "Clean raw bronze timestamp column and add data quality constraints"
AS
SELECT
*,
CAST(from_unixtime(timestamp) AS timestamp) AS timestamp_datetime
FROM STREAM 1_bronze_db.customers_bronze_raw_demo12;
```



### D4. SCHRITT 3: CDC-Daten mit **`AUTO CDC INTO`** verarbeiten
Spark Declarative Pipelines führt eine neue syntaktische Struktur ein, die die Verarbeitung von CDC-Feeds vereinfacht: `AUTO CDC INTO` (früher `APPLY CHANGES INTO`).



**`AUTO CDC INTO`** bietet folgende Garantien und hat folgende Anforderungen:
- Führt eine inkrementelle/Streaming-Ingestion von CDC-Daten durch
- Standardannahme ist, dass Zeilen Inserts und Updates enthalten
- Kann optional Deletes anwenden
- Ordnet verspätet eintreffende Datensätze automatisch anhand eines vom Benutzer angegebenen Sequenzierungsschlüssels (Reihenfolge der Zeilenverarbeitung)
- Verwendet eine einfache Syntax, um mit dem Schlüsselwort **`EXCEPT`** zu ignorierende Spalten anzugeben



### D5. SCHRITT 4: Den Pipeline-Graphen für Customers erkunden
Nachdem Sie die Pipeline ausgeführt und die Code-Zellen durchgesehen haben, nehmen Sie sich Zeit, die Pipeline-Ergebnisse für den **customers**-Flow anhand der folgenden Schritte zu erkunden.

**Lauf mit 1 JSON-Datei**

![demo12_cdc_run01.png](https://files.training.databricks.com/binder/prod_main/build-data-pipelines-with-apache-spark-declarative-pipelines-en_us-3.2.0/images/20260724T200107Z/Build Data Pipelines with Apache Spark Declarative Pipelines/Includes/images/change-data-capture/demo12_cdc_run_1.png)

Beachten Sie Folgendes:
1. Im **customers**-Flow des Pipeline-Graphen sehen Sie, dass **939** Zeilen in die drei Streaming Tables gestreamt wurden.
- Da alle Datensätze neue und gültige Einträge sind, wurden sie durch den gesamten Flow ingestiert.

2. Suchen Sie im Tabellenfenster unten die Tabelle **scd_type_1_customers_silver_demo12** und wählen Sie **Table metrics**. 

Beachten Sie Folgendes:

- Die Spalte **Upserted** zeigt, dass alle **939** Zeilen per Upsert in die Tabelle geschrieben wurden, da alle Zeilen neu sind.

## E. Neue Daten in Ihrem Datenquellen-Volume ablegen
Führen Sie die folgenden Schritte aus, nachdem Sie den **customers**-Flow der Pipeline ausgeführt und überprüft haben, bei dem eine Datei (**00.json**) aus dem Cloud-Speicher ingestiert wurde.

1. Führen Sie die folgende Zelle aus, um in jedem Volume (**customers**, **status** und **orders**) eine neue JSON-Datei abzulegen und so das Hinzufügen neuer Dateien zu Ihren Cloud-Speicherorten zu simulieren.

```python
%python

## Daten im Datenordner des Workspace finden
# data_path = find_folder('Includes/data')
data_path = "/Volumes/dbacademy/default/data"

## JSON-Dateien in Ihrem Orders-Volume ablegen
copy_workspace_files_to_volume(
    src_workspace_folder=f'{data_path}/orders',
    target_volume_path=f'{source_volume_path}/orders',
    n=2
)

## JSON-Dateien in Ihrem Status-Volume ablegen
copy_workspace_files_to_volume(
    src_workspace_folder=f'{data_path}/status',
    target_volume_path=f'{source_volume_path}/status',
    n=2
)

## JSON-Dateien in Ihrem Customers-Volume ablegen
copy_workspace_files_to_volume(
    src_workspace_folder=f'{data_path}/customers',
    target_volume_path=f'{source_volume_path}/customers',
    n=2
)
```

2. Führen Sie die folgende Zelle aus, um die Dateien in Ihrem Volume `/Volumes/labuser/sdp_1_bronze/source/customers` programmatisch anzuzeigen.

Bestätigen Sie, dass Ihr Volume nun die ursprüngliche Datei **00.json** und die neue Datei **01.json** enthält.

```python
%python
spark.sql(f'LIST "{source_volume_path}/customers"').display()
```

3. Führen Sie die Zelle aus, um die Rohdaten in der neuen Datei **01.json** zu erkunden, bevor Sie sie in Ihrer Pipeline ingestieren.

   Beachten Sie Folgendes:

   - Diese Datei enthält **23** Zeilen.

   - Die Spalte **operation** gibt die Operationen **UPDATE**, **DELETE** und **NEW** für Kunden an.
- **In der neuen Datei 01.json gibt es**:
- 12 Kunden mit **UPDATE**-Werten
- 1 Kunden mit einem **DELETE**-Wert
- 10 neue Kunden mit einem **NEW**-Wert

```sql
SELECT *
FROM read_files(
  source_volume_path || '/customers/01.json',
  format => "JSON"
)
ORDER BY customer_id;
```

4. Führen Sie die Zelle aus, um die **customer_id**-Werte *23225* und *23617* in der Datei **01.json** anzuzeigen.

   - Suchen Sie in den folgenden Ergebnissen die Zeile mit **customer_id** *23225* und beachten Sie Folgendes:

- Die ursprüngliche Adresse von **Sandy Adams** (aus der Streaming Table, Datei **00.json**) lautete: `76814 Jacqueline Mountains Suite 815`, `TX`
- Die aktualisierte Adresse von **Sandy Adams** (aus der folgenden Datei) lautet: `512 John Stravenue Suite 239`, `TN`

   - Suchen Sie in den folgenden Ergebnissen die Zeile mit **customer_id** *23617* und beachten Sie Folgendes:
- Die **operation** für diesen Kunden ist **DELETE**.
- Wenn die Spalte **operation** delete ist, sind alle anderen Spaltenwerte `null`.

```sql
SELECT *
FROM read_files(
  source_volume_path || '/customers/01.json',
  format => "JSON"
)
WHERE customer_id IN (23225, 23617)
ORDER BY customer_id;
```

### E1. Die SDP mit der neuen Datei ausführen

##### Kehren Sie zu Ihrer Pipeline zurück und klicken Sie auf die Schaltfläche `Run pipeline`, um die neue JSON-Datei (**01.json**) inkrementell zu ingestieren und CDC SCD Type 1 auf die Tabelle `scd_type_1_customers_silver_demo12` anzuwenden.

## F. Die Customers-Pipeline erkunden

Nachdem Sie jeweils 1 neue JSON-Datei in Ihren Cloud-Datenquellen erkundet und abgelegt haben, führen Sie die folgenden Schritte aus, um den **customers**-Flow im **Pipeline graph** zu erkunden:

a. 23 Zeilen wurden eingelesen in:

  - die Streaming Table **customers_bronze_raw_demo12**
  - die Streaming Table **customers_bronze_clean_demo12** (alle Datenqualitätsprüfungen bestanden)
  - Die Pipeline hat nur die NEUE Datei **01.json** ingestiert und verarbeitet

b. Die Details der Streaming Table **scd_type_1_customers_silver_demo12** (die CDC-SCD-Type-1-Tabelle) zeigen:
  - **Upserted = 22**:
- 12 Kunden mit UPDATE-Werten (bestehende Kunden wurden einfach mit den neuen Werten aktualisiert)
- 10 neue Kunden mit einem NEW-Wert (neue Kunden wurden in die Tabelle eingefügt)
  - **Deleted records = 1**:
- 1 Kunde war als DELETE markiert und wurde aus der Tabelle gelöscht

![Run 2](https://files.training.databricks.com/binder/prod_main/build-data-pipelines-with-apache-spark-declarative-pipelines-en_us-3.2.0/images/20260724T200107Z/Build Data Pipelines with Apache Spark Declarative Pipelines/Includes/images/change-data-capture/demo12_cdc_run_2.png)

## G. CDC SCD Type 1 auf der Streaming Table `scd_type_1_customers_silver_demo12` erkunden

1. Sehen Sie sich die Daten in der Streaming Table **scd_type_1_customers_silver_demo12** mit SCD Type 1 an und beachten Sie Folgendes:

   a. Die Tabelle enthält **948 Zeilen**:
- **ursprünglich 939 Kunden**
- \+ **10** neue Kunden
- \- **1** gelöschter Kunde
- **HINWEISE:**
- Die **12** Updates an bestehenden Kunden wurden direkt vorgenommen und haben den ursprünglichen Datensatz aktualisiert (SCD Type 1 bewahrt keine historischen Datensätze).
- Der **1** zur Löschung markierte Datensatz wurde aus der Tabelle gelöscht.

```sql
SELECT customer_id, address, name
FROM sdp_2_silver.scd_type_1_customers_silver_demo12 LIMIT 10;
```

2. Fragen Sie die Tabelle **sdp_2_silver.scd_type_1_customers_silver_demo12** nach den folgenden **customer_id**-Werten ab: *23225* und *23617*. Das sind die Werte, die wir uns zuvor angesehen haben.

Beachten Sie Folgendes:

- **customer_id** *23225* wurde auf die neue Adresse aktualisiert. Die historische Adresse wurde nicht beibehalten, da wir SCD Type 1 verwendet haben.
- **customer_id** *23617* wurde aus der Tabelle gelöscht. Sie existiert nicht mehr, da wir SCD Type 1 verwendet haben.

```sql
SELECT *
FROM sdp_2_silver.scd_type_1_customers_silver_demo12
WHERE customer_id IN (23225, 23617);
```
