# Die Lab-Umgebung erkunden

Diese Demonstration dient als Wiederholung zum Verständnis von Datenobjekten, die mit Databricks in Unity Catalog (UC) registriert sind. 

Die `IDENTIFIER`-Klausel kann einen konstanten String als eines der folgenden Objekte interpretieren:
- Name einer Relation (Tabelle oder View)
- Funktionsname
- Spaltenname
- Feldname
- Schemaname
- Katalogname

```sql
-- Standard-Katalog/-Schema ändern
USE CATALOG IDENTIFIER(my_catalog);
USE SCHEMA data_ingestion;


-- Aktuellen Katalog und aktuelles Schema anzeigen
SELECT 
  current_catalog(), 
  current_schema()
```

```sql
SHOW SCHEMAS;
```

```sql
-- Führen Sie die Anweisung `DESCRIBE SCHEMA EXTENDED` aus, um Informationen 
-- über Ihr Schema **data_ingestion** anzuzeigen
DESCRIBE SCHEMA EXTENDED data_ingestion;
```

```sql
-- Verwenden Sie die Anweisung `DESCRIBE TABLE EXTENDED`, um die Tabelle `mytable` zu beschreiben.
DESCRIBE TABLE EXTENDED mytable
```

```sql
DESCRIBE VOLUME dbacademy_ecommerce.v01.raw;
```

```sql
-- Verwenden Sie die Anweisung `LIST`, um die verfügbaren Dateien im Volume aufzulisten
LIST '/Volumes/dbacademy_ecommerce/v01/raw/users-historical'
```
