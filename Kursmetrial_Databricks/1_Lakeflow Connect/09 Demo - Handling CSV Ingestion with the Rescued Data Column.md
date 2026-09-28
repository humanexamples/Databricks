

- Das erste Argument gibt den Pfad zu den CSV-Dateien an.

- `format => "csv"` — Gibt an, dass die Dateien im CSV-Format vorliegen.

- `sep => "|"` — Legt fest, dass die Spalten durch das Pipe-Zeichen (`|`) getrennt sind.

- `header => true` — Weist den Reader an, die erste Zeile als Spaltenüberschriften zu verwenden.

- Obwohl wir in dieser Demonstration CSV-Dateien verwenden, können durch Angabe anderer Optionen auch andere Dateitypen (wie JSON oder Parquet) genutzt werden.

**Eine Spalte _rescued_data wird automatisch hinzugefügt, um alle Daten zu erfassen, die nicht zum abgeleiteten oder angegebenen Schema passen.**

```sql
SELECT * 
FROM read_files(
        "/Volumes/dbacademy_ecommerce/v01/raw/sales-csv",
        format => "csv",
        sep => "|",
        header => true
      )
LIMIT 5;
```

**Metadatenspalten:** Um Dateimetadaten einzubeziehen, verwenden Sie die Spalte [`_metadata`](https://docs.databricks.com/en/ingestion/file-metadata-column.html), die für alle Eingabedateiformate verfügbar ist. Diese versteckte Spalte ermöglicht den Zugriff auf verschiedene Metadatenattribute der Eingabedateien.

- Verwenden Sie `_metadata.file_modification_time`, um den Zeitpunkt der letzten Änderung der Eingabedatei zu erfassen.
- Verwenden Sie `_metadata.file_name`, um den Namen der Eingabedatei zu erfassen.
- [File metadata column](https://docs.databricks.com/gcp/en/ingestion/file-metadata-column)

```sql
-- Tabelle zu Demonstrationszwecken löschen, falls sie existiert
DROP TABLE IF EXISTS sales_bronze;

-- Die UC-Tabelle erstellen
CREATE TABLE sales_bronze AS
SELECT 
  *,
  _metadata.file_modification_time AS file_modification_time,
  _metadata.file_name AS source_file, 
  current_timestamp() as ingestion_time 
FROM read_files(
        "/Volumes/dbacademy_ecommerce/v01/raw/sales-csv",
        format => "csv",
        sep => "|",
        header => true
      );


-- Die Tabelle anzeigen
SELECT *
FROM sales_bronze
```

3. Sehen Sie sich die Datentypen der Spalten der Tabelle **sales_bronze** an. Beachten Sie, dass die Funktion `read_files()` das Schema automatisch ableitet, wenn keines explizit angegeben ist.

      **HINWEIS:** Wenn kein Schema angegeben ist, versucht `read_files()`, ein einheitliches Schema über alle gefundenen Dateien abzuleiten. Dazu müssen alle Dateien gelesen werden, sofern keine LIMIT-Anweisung verwendet wird. Selbst bei einer LIMIT-Abfrage kann eine größere Menge an Dateien als nötig gelesen werden, um ein repräsentativeres Schema der Daten zu erhalten.

     - [Schema inference](https://docs.databricks.com/aws/en/sql/language-manual/functions/read_files#csv-options)

```sql
DESCRIBE TABLE EXTENDED sales_bronze;
```

### B3. (BONUS) Python-Entsprechung

```python
df = (spark
      .read 
      .option("header", True) 
      .option("sep","|") 
      .option("rescuedDataColumn", "_rescued_data")
      .csv("/Volumes/dbacademy_ecommerce/v01/raw/sales-csv")
    )

df.display()
```

### C1. Ein Schema während der Ingestion definieren

```sql
SELECT *
FROM read_files(
        '/Volumes/' || my_catalog || '/data_ingestion/landing_folder/csv_demo_files/malformed_example_1_data.csv',
        format => "csv",
        sep => "|",
        header => true,
        schema => '''
            order_id INT, 
            email STRING, 
            transactions_timestamp BIGINT''', 
            rescueddatacolumn => '_rescued_data'    -- Die Spalte _rescued_data erstellen
      );
```

Die Rescued-Data-Spalte stellt sicher, dass Zeilen, die nicht zum Schema passen, gerettet statt verworfen werden. Die Rescued-Data-Spalte enthält alle Daten, die aus den folgenden Gründen nicht geparst werden.
### C2. Fehlende Header während der Ingestion behandeln
```sql
-- Tabelle zu Demonstrationszwecken löschen, falls sie existiert
DROP TABLE IF EXISTS demo_4_example_2_bronze;

-- UC-Tabelle durch Ingestieren der CSV-Datei erstellen
CREATE OR REPLACE TABLE demo_4_example_2_bronze AS
SELECT *
FROM read_files(
        '/Volumes/../malformed_example_2_data.csv',
        format => "csv",
        sep => "|",
        header => true
      );
```

Um den Wert aus dem Feld **_c0** zu erhalten, können Sie die Syntax `_rescued_data:_c0` verwenden, wie in der nächsten Zelle gezeigt.

```sql
SELECT
  cast(_rescued_data:_c0 AS BIGINT) AS order_id,
  *
FROM read_files(
        '/Volumes/' || my_catalog || '/data_ingestion/landing_folder/csv_demo_files/malformed_example_2_data.csv',
        format => "csv",
        sep => "|",
        header => true
      )
```

