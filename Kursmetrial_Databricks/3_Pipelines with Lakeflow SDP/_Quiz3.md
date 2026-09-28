# Quiz

1. **Ein Team hat eine inkrementelle Batch-Pipeline mit Spark Declarative Pipelines, die täglich neue Dateien verarbeitet. Die Datenquelle beginnt, Dateien kontinuierlich zu liefern, und das Team möchte eine Verarbeitung nahezu in Echtzeit, ohne Transformationen neu zu schreiben. Welche Änderung ist erforderlich?**

   - Die Pipeline in einen Notebook-basierten Streaming-Job umwandeln
   - Den Pipeline-Trigger von zeitgesteuerter auf kontinuierliche Ausführung umstellen ✅
   - Jeder Abfrage manuelle Watermark-Logik hinzufügen
   - Alle Tabellen als reines Streaming-SQL neu schreiben

2. **Was ist in Spark Declarative Pipelines die Hauptaufgabe einer Materialized View?**

   - Aggregierte oder abgeleitete Ergebnisse aus vorgelagerten Tabellen erzeugen ✅
   - Schemas für eingehende Daten erzwingen
   - Rohdaten aus externen Quellen ingestieren
   - Jede historische Änderung an Datensätzen im Zeitverlauf nachverfolgen

3. **Welcher Mechanismus ermöglicht es Spark Declarative Pipelines, bei nachfolgenden Läufen effizient nur neue Daten zu verarbeiten?**

   - Manuelles Watermarking, definiert in SQL-Abfragen
   - Auto Loader in Kombination mit Checkpoints zur Nachverfolgung des Ingestion-Fortschritts ✅
   - Periodische Batch-Planung, die begrenzt, wie oft Pipelines laufen
   - Vollständiges Neuschreiben der Tabellen bei jedem Pipeline-Lauf

4. **Welche Compute-Option wird bei der Konfiguration einer Spark Declarative Pipeline für eine kosteneffiziente, skalierbare Verarbeitung empfohlen?**

   - Single-Node-Cluster
   - Multi-Node-Cluster
   - Serverless Compute ✅
   - Shared Cluster

5. **Welche Funktion verbessert die Zuverlässigkeit und verringert den Wartungsaufwand in Spark Declarative Pipelines?**

   - Versionskontrolle
   - Vereinfachte Pipeline-Erstellung
   - Governance
   - Automatisierte Skalierung und Wiederherstellung ✅

6. **Sie definieren eine Lakeflow Spark Declarative Pipeline, in der:**

   - **eine Bronze-Streaming-Table neue JSON-Dateien ingestiert, sobald sie im Cloud-Speicher eintreffen.**
   - **eine nachgelagerte Silber-Streaming-Table Transformationen wie Filterung und Anreicherung auf die Bronze-Streaming-Table anwendet**
   - **eine Materialized View die transformierten Ergebnisse aggregiert.**

**Was passiert, wenn neue Dateien im Cloud-Speicher eintreffen und die Pipeline ausgeführt wird?**

   - Nur die neuen Dateien werden ingestiert, nachgelagerte Streaming Tables werden inkrementell aktualisiert, und die Materialized View wird nach Möglichkeit inkrementell aktualisiert. ✅
   - Die gesamte Pipeline wird von Grund auf neu ausgeführt und verarbeitet alle historischen Daten erneut, um aktualisierte Ergebnisse zu erzeugen.
   - Nur die neuen Dateien werden ingestiert und nachgelagerte Streaming Tables inkrementell aktualisiert, aber die Materialized View muss manuell aktualisiert werden.
   - Nur die neuen Dateien werden ingestiert und nachgelagerte Streaming Tables inkrementell aktualisiert, aber die Materialized View wird immer vollständig neu berechnet.

7. **Sie bauen eine Spark Declarative Pipeline mit folgenden Anforderungen:**

   - **Eine Silber-Streaming-Table `orders_silver` existiert bereits und wird inkrementell aktualisiert**
   - **Sie möchten ein Dataset der Gold-Schicht erstellen, das die Bestellanzahlen pro Kunde aggregiert**
   - **Die aggregierten Ergebnisse sollen als Objekt gespeichert und bei Eintreffen neuer Daten nach Möglichkeit inkrementell aktualisiert werden**
   - **Die Pipeline-Engine soll die Aktualisierungslogik automatisch verwalten**

**Welche SQL-Definition erfüllt diese Anforderungen am besten?**

   - `CREATE STREAMING TABLE customer_order_summary`
`AS`
`SELECT`
`customer_id,`
`COUNT(order_id) AS order_count`
`FROM STREAM(orders_silver)`
`GROUP BY customer_id;`

   - `INSERT INTO customer_order_summary`
`SELECT`
`customer_id,`
`COUNT(order_id)`
`FROM orders_silver`
`GROUP BY customer_id;`

   - `CREATE OR REFRESH MATERIALIZED VIEW customer_order_summary` ✅
`AS`
`SELECT`
`customer_id,`
`COUNT(order_id) AS order_count`
`FROM orders_silver`
`GROUP BY customer_id;`

   - `CREATE OR REPLACE VIEW customer_order_summary`
`AS`
`SELECT`
`customer_id,`
`COUNT(order_id) AS order_count`
`FROM orders_silver`
`GROUP BY customer_id;`

8. **Welche Verarbeitungs- oder Kostenüberlegung motiviert Teams bei Notebook-basiertem Batch-ETL für große Datenmengen häufig zur Migration zu Spark Declarative Pipelines?**

- Notebook-basiertes Batch-ETL kann Auto Loader nicht verwenden, Spark Declarative Pipelines hingegen schon
- Notebook-basiertes Batch-ETL unterstützt keine verteilte Verarbeitung, Spark Declarative Pipelines hingegen schon
- Notebook-basiertes Batch-ETL verarbeitet Daten oft bei jedem Lauf vollständig neu, was die Compute-Kosten erhöht, während Spark Declarative Pipelines die inkrementelle Verarbeitung automatisch verwalten ✅
- Notebook-basiertes Batch-ETL kann nicht geplant werden, Spark Declarative Pipelines hingegen schon

9. **Welchen Zweck hat das Event Log in Lakeflow Spark Declarative Pipelines, und welche Informationen liefert es?**

- Es protokolliert nur Schemaänderungen an Zieltabellen während der Schema Evolution
- Es zeichnet Benutzerzugriffe und Berechtigungsänderungen an Pipeline-Definitionen auf
- Es speichert die von Streaming Tables ingestierten Rohdaten vor der Verarbeitung
- Es verfolgt Pipeline-Läufe, einschließlich Start- und Endzeit, Anzahl verarbeiteter Datensätze sowie Fehler oder Warnungen aus Expectations oder Transformationen ✅

10. **Sie bauen eine Pipeline in Lakeflow Spark Declarative Pipelines. Der Pfad zu Ihren Eingabedaten soll je nach Umgebung (dev, test, prod) konfigurierbar sein. Sie legen einen Pipeline-Konfigurationsparameter namens input_path fest.** 

​	**Welcher SQL-Ausschnitt referenziert diesen Parameter korrekt, um eine Streaming Table zu definieren, die diesen Pfad verwendet?**

- `CREATE OR REFRESH STREAMING TABLE raw_events` ✅
  `AS SELECT *`
  `FROM STREAM read_files('${input_path}', format => 'json');`

- `CREATE OR REFRESH STREAMING TABLE raw_events`
  `AS`
  `SELECT *`
  `FROM STREAM read_files($$input_path$$, format => 'json');`

- `CREATE OR REFRESH STREAMING TABLE raw_events`
  `AS`
  `SELECT *`
  `FROM STREAM read_files({input_path}, format => 'json');`

- `CREATE OR REFRESH STREAMING TABLE raw_events`
  `AS`
  `SELECT *`
  `FROM STREAM read_files(input_path, format => 'json');`

11. **Sie migrieren einen klassischen Batch-ETL-Workflow, bei dem bei jedem Job-Lauf der gesamte Datensatz vollständig neu verarbeitet wird, in eine Lakeflow Spark Declarative Pipeline mit einer Bronze > Silber > Gold-Architektur.**

**Im bestehenden Workflow:**

- **werden Rohdateien in einem einzigen Batch-Job ingestiert, bereinigt, verknüpft und aggregiert.**
- **verarbeitet jeder Lauf alle historischen Daten, auch wenn neue Daten eingetroffen sind.**

**Welcher Ansatz spiegelt am besten wider, wie dieser Workflow mit Spark Declarative Pipelines neu gestaltet werden sollte?**

- Die Logik in separate Batch-Jobs aufteilen und diese manuell nacheinander orchestrieren

- Eine Bronze-Streaming-Table für die Rohdaten-Ingestion, Silber-Tabellen für Bereinigung und Anreicherung und Gold-Materialized-Views für Aggregationen definieren und die Pipeline Abhängigkeiten und inkrementelle Updates verwalten lassen ✅

- Das Batch-SQL in Python umwandeln und unverändert in einem Pipeline-Notebook ausführen

- Den einzelnen Batch-Job beibehalten und häufiger ausführen, um die Datenlatenz zu verringern

12. **Sie haben eine Lakeflow Spark Declarative Pipeline mit Streaming Tables, nachgelagerten Transformationen und Materialized Views.**

**Sie möchten:**

- **alle Pipeline-Checkpoints löschen**
- **alle Daten aus Streaming Tables entfernen**
- **alle Quelldaten von Grund auf neu verarbeiten**
- **alle nachgelagerten Tabellen und Materialized Views vollständig neu aufbauen**

**Welche Aktion sollten Sie ausführen?**

- Die Pipeline mit einem Full Table Refresh ausführen ✅
- Die Pipeline mit anderen Einstellungen ausführen
- Die Pipeline manuell löschen und neu starten
- „Alle löschen“ auswählen und die Pipeline ausführen

13. **Welche der folgenden Aussagen beschreibt den Kernzweck von Lakeflow Spark Declarative Pipelines am besten?**

- Es übernimmt nur die Ingestion; Transformationen müssen von separaten Spark-Jobs außerhalb des Frameworks durchgeführt werden.
- Es ist nur für Batch-ETL-Jobs gedacht und unterstützt keine Echtzeit- oder Streaming-Daten.
- Es ist eine Low-Level-Bibliothek, die eine manuelle Orchestrierung von Spark-Structured-Streaming-Jobs erfordert.
- Es ist ein deklaratives Framework, mit dem Sie inkrementelle Batch- oder Streaming-Daten-Pipelines in SQL oder Python definieren, während Orchestrierung, inkrementelle Verarbeitung und Fehlerwiederherstellung automatisch übernommen werden. ✅

14. **Wie werden neue Daten in die Zieltabelle geschrieben, wenn eine Streaming Table in Spark Declarative Pipelines neue Daten aus ihrer Quelle verarbeitet?**

- Datensätze werden mit MERGE-INTO-Semantik in die Tabelle gemergt
- Neue Datensätze werden inkrementell an die Streaming Table angehängt ✅
- Daten werden bis zur nächsten Aktualisierung nur in einer temporären View gespeichert
- Vorhandene Daten in der Tabelle werden vollständig überschrieben

15. **Angenommen, JSON-Logdateien treffen kontinuierlich im Cloud-Speicher unter `/Volumes/logs/events` ein. Sie möchten sie in eine Streaming Table namens `events_bronze` ingestieren.** 

**Welche SQL-Anweisung definiert diese Streaming Table in Databricks SQL korrekt?**

- `CREATE OR REFRESH STREAMING TABLE events_bronze` ✅
`AS`
`SELECT *`
`FROM STREAM read_files('/Volumes/logs/events', format => 'json');`

- `CREATE STREAMING TABLE events_bronze`
`AS`
`SELECT *`
`FROM read_files('/Volumes/logs/events', format => 'json');`

- `CREATE OR REFRESH TABLE events_bronze`
`AS`
`SELECT *`
`FROM read_files('/Volumes/logs/events', format => 'json');`

- `CREATE STREAMING TABLE events_bronze`
`AS`
`SELECT *`
`FROM read_files('/Volumes/logs/events', format => 'json')`
`SCHEDULE EVERY 1 HOUR;`

16. **Was ist in Lakeflow Spark Declarative Pipelines der Hauptzweck einer Expectation bei der Definition einer Streaming Table oder Materialized View?**

- Einen Datenqualitäts-Constraint anwenden, der jeden durchfließenden Datensatz validiert und ungültige Datensätze optional verwirft oder kennzeichnet ✅
- Ein statisches Schema erzwingen, sodass alle Daten exakt den angegebenen Spalten entsprechen müssen
- Daten auf Basis von Qualitätsprüfungen automatisch partitionieren
- JSON-Strings in strukturierte Spalten umwandeln, um Abfragen zu verbessern

17. **Was ist in Spark Declarative Pipelines der Hauptunterschied zwischen einer Streaming Table und einer Materialized View?**

- Streaming Tables ingestieren eingehende Daten aus einer Quelle und verarbeiten sie inkrementell, während Materialized Views die Ergebnisse einer Abfrage über vorgelagerte Tabellen nach Möglichkeit inkrementell pflegen ✅
- Streaming Tables werden nur für Rohdaten verwendet, Materialized Views nur für finale Reporting-Tabellen
- Streaming Tables berechnen bei jedem Lauf immer alle Daten neu, während Materialized Views Daten nie neu berechnen
- Streaming Tables werden nur für Batch-Workloads verwendet, Materialized Views nur für Streaming-Workloads

18. **Sie bauen eine Spark Declarative Pipeline mit den folgenden Datasets:**

- **Eine Streaming Table `orders_stream`, die neue Bestellungen ingestiert, sobald sie eintreffen.**
- **Eine statische Tabelle `customers_dim` mit Kundenattributen, die sich selten ändern.**

**Sie möchten jede eingehende Bestellung mit Kundendetails anreichern und die Pipeline die inkrementelle Verarbeitung und Ausführungsreihenfolge übernehmen lassen.**

**Welcher Ansatz passt am besten zu Spark Declarative Pipelines?**

- customers_dim in eine Streaming Table umwandeln, sodass beide Eingaben Streaming sind
- Einen separaten Batch-Job ausführen, der die Ergebnisse regelmäßig verknüpft und überschreibt
- Die Streaming Table in einer deklarativen Transformation mit der statischen Tabelle verknüpfen und die Pipeline inkrementelle Updates verwalten lassen ✅
- Die statische Tabelle bei jedem Lauf manuell innerhalb der Pipeline cachen

19. **Wie viele Zeilen sollten verarbeitet werden, wenn eine Spark Declarative Pipeline nach dem Ablegen neuer Daten zum zweiten Mal ausgeführt wird?**

- Nur die seit dem letzten Lauf hinzugekommenen neuen Zeilen ✅
- Null Zeilen; eine manuelle Aktualisierung ist erforderlich
- Alle Zeilen im Quell-Volume
- Nur die ursprünglichen Zeilen

20. **Was bewirkt die Syntax AUTO CDC INTO in Lakeflow Declarative Pipelines?**

- Sie vereinfacht Change Data Capture, indem Inserts, Updates und Deletes inkrementell auf eine Zieltabelle angewendet werden ✅
- Sie erstellt automatisch Dashboards für CDC-Daten
- Sie löscht alle Daten in der Pipeline
- Sie plant Pipeline-Läufe
