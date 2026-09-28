# Quiz

1. **Welchen Zweck hat die Rescued-Data-Spalte beim Ingestieren von Daten in Databricks?**
   - Datensätze behandeln, die nicht zum Schema der Zieltabelle passen ✅
   - Ingestion-Fehler protokollieren
   - Doppelte Datensätze speichern
   - Metadaten über Ingestion-Jobs speichern

2. **Wofür ist die Bronze-Schicht in der Medallion-Architektur speziell vorgesehen?**
   - Bereinigte und gefilterte Daten
   - Erstellung von BI-Reports
   - Geschäftliche Aggregation
   - Ingestion von Rohdaten ✅

3. **Welche der folgenden Metadaten können beim Ingestieren von Daten in eine Bronze-Tabelle mithilfe der Spalte `**_metadata**` aus den Eingabedateien extrahiert werden?**

- Nur der Erstellungszeitstempel der Datei
- Nur Dateigröße und Dateiberechtigungen
- Dateiname, Änderungszeitpunkt der Datei und Dateipfad ✅
- Dateiinhalt und Informationen zum Datenschema

4. **Wie wird Partner Connect beim Ingestieren von Daten in Databricks üblicherweise verwendet?**

- Um Ingestion-Tools von Partnern zu konfigurieren und zu starten, die Daten aus externen Systemen in Databricks laden ✅
- Um für jede externe Datenquelle eigenen Spark-Code zu schreiben
- Um Dateien manuell von einem lokalen Rechner in Unity-Catalog-Volumes hochzuladen
- Um eingebaute Databricks-Ingestion-Funktionen wie Auto Loader zu ersetzen

5. **Sie entwerfen eine Ingestion-Pipeline mit Lakeflow Connect in Databricks.**

- **Ein Teil Ihrer Daten liegt bereits als Dateien im Cloud Object Storage, auf den Databricks direkt zugreifen kann.**
- **Andere Daten befinden sich in einem externen System, etwa einer transaktionalen Datenbank oder einer SaaS-Anwendung, und wurden noch nicht im Cloud-Speicher abgelegt.**

​	**Welche Auswahl ordnet jedem Szenario korrekt den zu verwendenden Connector-Typ zu?**

- Standard Connectors für Daten, die bereits im Cloud-Speicher liegen, und Managed Connectors für Daten in externen Systemen verwenden
- Managed Connectors für Daten, die bereits im Cloud-Speicher liegen, und Standard Connectors für Daten in externen Systemen verwenden
- Managed Connectors sowohl für Daten im Cloud-Speicher als auch für externe Systeme verwenden ✅
- Standard Connectors sowohl für Daten im Cloud-Speicher als auch für externe Systeme verwenden

6. **Für welche Art von Ingestion-Aufgabe ist CREATE TABLE AS (CTAS) laut Zusammenfassung am besten geeignet?**

- Skalierung auf Millionen von Dateien
- Einmalige Ad-hoc-Ingestion ✅
- Komplexes Change Data Capture
- Ingestion nahezu in Echtzeit

7.**Sie verwenden MERGE INTO in Databricks SQL, um Daten aus einer Quelltabelle per Upsert in eine Delta-Zieltabelle zu schreiben. Die Quelltabelle kann gelegentlich neue Spalten enthalten, die in der Zieltabelle noch nicht existieren. Die Merge-Operation soll diese Änderungen automatisch behandeln.**
**Welche Anweisung erreicht dies am besten?**

- MERGE WITH SCHEMA EVOLUTION INTO target t ✅
  USING source s
  ON t.id = s.id
  WHEN MATCHED THEN UPDATE SET *
  WHEN NOT MATCHED THEN INSERT *;

- MERGE INTO target t
  USING source s
  ON t.id = s.id
  WHEN MATCHED THEN UPDATE SET *
  WHEN NOT MATCHED THEN INSERT *;

- MERGE INTO target t
  USING source s
  ON t.id = s.id
  WHEN MATCHED THEN UPDATE SET t.col1 = s.col1;

- ALTER TABLE target ADD COLUMNS (...);

​	MERGE INTO target t
​	USING source s
​	ON t.id = s.id
​	WHEN MATCHED THEN UPDATE SET *
​	WHEN NOT MATCHED THEN INSERT *;

8. **Was ist das empfohlene Ziel für die Synchronisierung ingestierter Daten-Pipelines in Databricks?**

- Unity Catalog (Katalog und Schema) ✅
- Lokale Festplatte
- Externer Cloud-Speicher
- DBFS

9. **Welchen Tabellentyp erstellt die Anweisung CREATE TABLE AS (CTAS) standardmäßig?**

- CSV-Tabelle
- Parquet-Tabelle
- Delta-Tabelle ✅
- Hive-Tabelle

10. **Welche Fähigkeit unterstützt Auto Loader automatisch, wenn neue Spalten in den Daten auftauchen?**

- Tabellenkomprimierung
- Time Travel
- Schema Evolution ✅
- Nachverfolgung der Data Lineage

11. **Sie müssen CSV-Dateien mit den folgenden Eigenschaften ingestieren:**

- **Die Dateien sind durch Semikolon (`;`) statt durch Komma getrennt**
- **Die Dateien enthalten Header in der ersten Zeile**
- **Die Dateien können fehlerhafte Daten enthalten, die für eine spätere Analyse erfasst werden sollen**
- **Sie möchten ein bestimmtes Schema erzwingen: `order_id BIGINT, customer_email STRING, order_total DECIMAL(10,2)`**

​	**Welche `read_files()`-Konfiguration erfüllt alle diese Anforderungen korrekt?**

- SELECT * FROM read_files(
  "/path/to/files",
  format => "csv",
  sep => ";",
  header => true,
  schema => "order_id:BIGINT, customer_email:STRING, order_total:DECIMAL(10,2)",
  rescuedDataColumn => "_rescued_data"
  );

- SELECT * FROM read_files(  ✅
  "/path/to/files",
  format => "csv",
  sep => ";",
  header => true,
  schema => "order_id BIGINT, customer_email STRING, order_total DECIMAL(10,2)",
  rescuedDataColumn => "_rescued_data"
  );

- SELECT * FROM read_files(
  "/path/to/files",
  format => "csv",
  delimiter => ";",
  header => true,
  schema => "order_id BIGINT, customer_email STRING, order_total DECIMAL(10,2)"
  );

- SELECT * FROM read_files(
  "/path/to/files",
  format => "csv",
  separator => ";",
  headers => true,
  enforceSchema => "order_id BIGINT, customer_email STRING, order_total DECIMAL(10,2)",
  rescueColumn => "_rescued_data"
  );

12. **Sie ingestieren einen Datensatz in Databricks, bei dem eine Spalte JSON-formatierte Daten als String enthält. Sie möchten flexibel verschachtelte Felder abfragen, Schema Evolution unterstützen und bei wachsender Nutzung eine gute Abfrage-Performance beibehalten. Was ist der beste Ansatz?**

- Die Spalte mit dem Datentyp VARIANT speichern und verschachtelte Felder nach Bedarf abfragen ✅
- Die Spalte als einfachen STRING belassen und JSON in jeder Abfrage manuell parsen
- Die Spalte in einen festen STRUCT konvertieren, bei dem alle erwarteten Felder vorab definiert sind
- Das JSON während der Ingestion in mehrere STRING-Spalten aufteilen

13. **Von wem werden Lakeflow Connect Managed Connectors laut Definition vollständig verwaltet?**

- Partner Connect
- Cloud-Anbieter
- Eigentümer der Datenquelle
- Databricks ✅

14. **Durch welche automatisch ausgeführte Aktion erreicht COPY INTO bei inkrementeller Batch-Ingestion seine Effizienz?**

- Überspringen bereits geladener Dateien ✅
- Manuelles Zusammenführen von Schemas
- Löschen von Quelldateien
- Komprimieren kleiner Dateien

15. **Welcher der folgenden Punkte ist ein wesentlicher Vorteil von Lakeflow Connect für die Daten-Ingestion in Databricks?**

- Es bietet eine skalierbare und vereinfachte Ingestion aus verschiedenen Datenquellen ✅
- Es unterstützt nur Streaming-Daten
- Es unterstützt keinen Cloud Object Storage
- Es erfordert für jede Tabelle eine manuelle Schemazuordnung

16. **Was ist die empfohlene Alternative zum Legacy-SQL-Befehl COPY INTO für die inkrementelle Ingestion (Auto Loader) aus Cloud Object Storage?**

- CREATE STREAMING TABLE SQL ✅
- MERGE-INTO-Anweisungen
- Lakeflow Jobs
- CREATE TABLE AS (CTAS)

17. **Worauf liegt der Hauptfokus der in der Gold-Schicht gespeicherten Daten?**

- Inkrementelle Updates
- Unstrukturierte Rohdateien
- Duplikate aus Quellsystemen
- Aggregationen auf Geschäftsebene ✅

18. **Welchen Zweck hat die Komponente Ingestion Gateway im Datenbank-Ingestion-Ablauf?**

- Speichern der finalen Streaming Tables
- Ausführen von BI-Reports
- Verbinden mit der Quelldatenbank ✅
- Verwalten von Benutzerberechtigungen

19. **Welche Ingestion-Methode verarbeitet bei jedem Pipeline-Lauf alle Datensätze erneut?**

- Batch ✅
- Streaming
- Declarative
- Inkrementeller Batch

20. **Welche Schicht speichert typischerweise bereinigte und gefilterte Daten, die für die nachgelagerte Nutzung bereitstehen?**

- Data Lake
- Silver ✅
- Gold
- Bronze
