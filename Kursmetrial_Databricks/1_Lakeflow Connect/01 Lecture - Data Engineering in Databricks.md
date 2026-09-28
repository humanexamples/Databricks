## Ingestion-Methoden

Beim Ingestieren von Daten in Databricks mit den LakeFlow Connect Standard Connectors können Sie zwischen mehreren Ingestion-Methoden wählen.

### C1. Batch-, inkrementelle Batch- und Streaming-Ingestion
Wählen Sie jeden Tab aus, um die drei in LakeFlow Connect verfügbaren Ingestion-Methoden kennenzulernen.

#### 1_Batch-Ingestion

1. Batch-Ingestion eignet sich gut für große Mengen historischer Daten, bei denen keine Echtzeitverarbeitung erforderlich ist.
2. Sie ist in der Regel einfacher zu implementieren und zu verwalten und daher eine häufige Wahl für zeitgesteuerte Daten-Pipelines.

- Daten werden als **Batches von Zeilen in Databricks geladen**, oft nach einem Zeitplan
- Die klassische Batch-Ingestion **verarbeitet bei jedem Lauf alle Datensätze**

**Gängige Techniken sind:**

1. Die SQL-Anweisung: `CREATE TABLE AS SELECT`
2. Die Python-Methode: `spark.read.load()`



#### 2_Inkrementelle Batch-Ingestion

1. Databricks unterstützt sowohl klassische Batch-Ingestion als auch inkrementelle Batch-Ingestion.
2. Während die klassische Batch-Ingestion bei jedem Lauf alle Datensätze verarbeitet, erkennt die inkrementelle Batch-Ingestion automatisch neue Datensätze in der Datenquelle und überspringt bereits ingestierte Datensätze.

- **Nur neue Daten werden ingestiert** – bereits geladene Datensätze werden **automatisch übersprungen**
- Ermöglicht eine **schnellere** und **ressourceneffizientere** Ingestion, da weniger Daten verarbeitet werden

**Gängige Techniken sind:**

1. Die SQL-Anweisung: `COPY INTO`
2. Die Python-Methode: `spark.readStream` (Auto Loader mit zeitgesteuertem Trigger)
3. Declarative Pipelines: `CREATE OR REFRESH STREAMING TABLE`

#### 3_Streaming-Ingestion

1. Bei der Streaming-Ingestion werden Daten kontinuierlich geladen, sobald sie erzeugt werden, sodass Sie sie nahezu in Echtzeit abfragen können. Diese Methode ist ideal zum Laden von Streaming-Daten aus Quellen wie Apache Kafka, Amazon Kinesis, Google Pub/Sub und Apache Pulsar.
2. Streaming-Ingestion verarbeitet Daten, sobald sie eintreffen, und ermöglicht so Analysen mit geringer Latenz und sofortiges Handeln. Im Gegensatz dazu sammelt die Micro-Batch-Ingestion Daten über kurze, häufige Intervalle (Sekunden oder Minuten) und verarbeitet sie in kleinen Batches – ein Kompromiss zwischen Latenz und Systemeffizienz.

- **Kontinuierliches Laden** von Datenzeilen oder Batches von Datenzeilen, sobald sie erzeugt werden, sodass Sie sie abfragen können, sobald sie **nahezu in Echtzeit eintreffen**
- **Micro-Batch** verarbeitet kleine Batches in sehr **kurzen, häufigen Intervallen**

**Gängige Techniken sind:**

1. `spark.readStream` (Auto Loader mit kontinuierlichem Trigger)
2. Declarative Pipelines (Trigger-Modus continuous)

## D. Delta Lake im Überblick

Delta Lake bietet offenes, zuverlässiges und skalierbares Datenmanagement für das Lakehouse. Damit können Sie Daten aus externen Quellen ingestieren und effizient über die Schichten **Bronze (roh)**, **Silber (bereinigt)** und **Gold (kuratiert)** verwalten – mit vollständigen ACID-Transaktionen, Time Travel, Schema Enforcement sowie Unterstützung für Batch- und Streaming-Workloads.

### D1. Daten in Delta Lake ingestieren
Ziel ist es, Dateien aus **externen Datenquellen** wie Cloud Object Storage als **UC-Tabellen in Delta Lake** zu ingestieren.

Delta Lake ist ein Open-Source-Protokoll zum Lesen und Schreiben von Dateien in Cloud-Speicher. UC-Tabellen bieten ein offenes Tabellenformat, das die **Lakehouse-Architektur** und die Speicherung in Cloud Data Lakes auf AWS, Azure und GCP unterstützt.

### D2. Überblick über die Komponenten von UC-Tabellen
Innerhalb von Delta Lake arbeiten Sie mit UC-Tabellen. Das folgende Diagramm zeigt, wie Daten intern gespeichert werden.

1. Daten werden in UC-Tabellen gespeichert.
2. Intern speichern diese Tabellen Daten als Dateien in einem Ordnerverzeichnis.

UC-Tabellen speichern Daten als Dateien in einem Ordnerverzeichnis.

1. Daten werden als Parquet-Dateien im Verzeichnis gespeichert.
2. Delta Lake legt neben diesen Dateien JSON-basierte Delta Logs an.
3. Delta Logs protokollieren Transaktionen und Tabellenversionen.

Delta Lake speichert Daten als Parquet-Dateien und führt Transaktionsprotokolle.

### D3. Wichtige Funktionen von UC-Tabellen

- ACID-Transaktionen  **A**tomicity (Atomarität), **C**onsistency (Konsistenz), **I**solation, **D**urability (Dauerhaftigkeit) für alle Operationen, sodass **mehrere Benutzer gleichzeitig Daten lesen und schreiben** können, ohne dass Konflikte entstehen.
- Data Manipulation Language (DML)  Unterstützt DML-Operationen wie **INSERT, UPDATE, DELETE und MERGE** und ermöglicht so ein flexibles Datenmanagement.
- Time Travel  Ermöglicht es Benutzern, frühere Datenversionen **abzufragen** und **wiederherzustellen**, was **Auditing und Wiederherstellung** erleichtert.
-   Schema Evolution und Enforcement  Erzwingt ein definiertes **Schema für die Datenintegrität** und erlaubt gleichzeitig Schema Evolution, sodass strukturelle Änderungen möglich sind, ohne bestehende Workflows zu beschädigen.
-   Und vieles mehr!  Einheitliche **Batch- und Streaming**-Verarbeitung, **Optimierung und Performance** sowie **Skalierbarkeit** – und Delta Lake ist **Open Source**.

##### FÜR ZUSÄTZLICHE HINWEISE AUFKLAPPEN

Das **Transaktionsprotokoll** ermöglicht zentrale Funktionen von UC-Tabellen, indem es die Tabellenzustände verwaltet.
- Es zeichnet jedes **Insert, Update und Delete** als Transaktion auf und stellt so sicher, dass die Tabelle konsistent und aktuell bleibt.
- Dies ermöglicht **zuverlässige Datenansichten und Time Travel**, wodurch der Zugriff auf frühere Datenversionen einfach wird.
Früher erforderte das Ändern von Daten in einem Data Lake das **manuelle Neuerstellen von Dateien und Nachverfolgen von Änderungen**, was komplex und ineffizient war.
- Mit Delta Lake lassen sich Datenänderungen **einfacher, schneller und effizienter verwalten**.
