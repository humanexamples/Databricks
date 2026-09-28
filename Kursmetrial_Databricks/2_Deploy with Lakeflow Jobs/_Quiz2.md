# Quiz

1. **Sie betreiben einen geschäftskritischen Lakeflow Job auf Databricks mit Serverless Compute.**

**Der Job muss:**

   - **so schnell wie möglich starten**
   - **die Gesamtausführungszeit minimieren**
   - **darf höhere Kosten verursachen, wenn dies Zuverlässigkeit und Performance verbessert**

**Was ist die beste Maßnahme?**

   - Autoscaling deaktivieren, um den Overhead zu verringern
   - Den Job seltener ausführen lassen
   - Den Performance Optimized Mode für den Serverless-Job aktivieren ✅
   - Auf einen interaktiven Cluster wechseln, damit das Compute immer läuft

2. **Sie konfigurieren einen Databricks-Job, der mehrere Tasks ausführt. Sie möchten einen Parameter (z. B. input_path) definieren, dessen Wert standardmäßig für alle Tasks gilt, sofern er nicht für einen bestimmten Task überschrieben wird.** 

**Wo sollten Sie diesen Parameterwert angeben?**

   - Nur im ersten Task; nachfolgende Tasks übernehmen ihn automatisch
   - Im Abschnitt „Job parameters“ auf Job-Ebene bei der Konfiguration des Jobs✅
   - In den individuellen Parametereinstellungen jedes Tasks
   - In einer globalen Workspace-Konfiguration außerhalb der Job-Einstellungen 

3. **Für die Automatisierung von Jobs mit welchem Ingestion-Muster sind File Arrival Trigger ideal?**

   - Unvorhersehbare oder unregelmäßige Daten-Ingestion ✅
   - Gleichmäßige, stündliche Planung
   - Ausschließlich manuelle Daten-Uploads
   - Sehr gut vorhersehbare tägliche Batches

4. **In welchen Szenarien können Benachrichtigungen in Lakeflow Jobs ausgelöst werden?**

   - Nur wenn die Spark UI einen Fehler erkennt
   - Wenn der Task startet, abgeschlossen wird oder fehlschlägt ✅
   - Nur bei einem Job-Fehler
   - Nur bei manuellem Eingreifen

5. **Was ist der Hauptzweck von Lakeflow Jobs in Databricks?**

   - End-to-End-Workflows für Daten, Analytics und KI orchestrieren und automatisieren ✅
   - Interaktive Dashboards und Visualisierungen erstellen
   - Workspace-Benutzer und Berechtigungen verwalten
   - SQL- und Spark-Transformationen schreiben

6. **Was ist erforderlich, bevor eine SQL-Abfragedatei in einem Task eines Lakeflow Jobs verwendet werden kann?**

   - Die Abfrage darf nur SELECT-Anweisungen verwenden
   - Die Abfragedatei muss im Workspace gespeichert sein ✅
   - Die Abfrage muss auf Performance optimiert sein
   - Die Abfrage muss kürzer als 1000 Zeichen sein

7. **Sie entwerfen einen Lakeflow Job mit folgendem Workflow:**

   1. **Zuerst läuft ein Task zur Daten-Ingestion**
   2. **Nach der Ingestion laufen zwei Validierungs-Tasks parallel**
   3. **Ein Publish-Task soll nur laufen, wenn beide Validierungs-Tasks erfolgreich sind**

**Wie sollte der Publish-Task konfiguriert werden?**

   - Abhängigkeiten entfernen und den Publish-Task separat planen
   - Den Publish-Task so einstellen, dass er läuft, wenn alle Abhängigkeiten erfolgreich sind ✅
   - Den Publish-Task so einstellen, dass er läuft, wenn mindestens eine Abhängigkeit erfolgreich ist
   - Den Publish-Task so einstellen, dass er läuft, wenn eine beliebige Abhängigkeit abgeschlossen ist

8. **Sie betreiben einen Lakeflow Job für einen Produktions-Workflow, der:**

   - **nach einem Zeitplan ausgeführt wird**
   - **keinen dauerhaft laufenden Cluster benötigt**
   - **das Compute nach Abschluss des Jobs automatisch herunterfahren soll, um Kosten zu kontrollieren**

**Welche Compute-Option passt am besten zu diesem Anwendungsfall?**

   - All-Purpose Cluster
   - SQL Endpoint
   - Interactive Clusters
   - Job Clusters✅

9. **Was ist der grundlegende Zweck eines For-Each-Tasks in Lakeflow Jobs?**

   - Bedingte Verzweigungslogik behandeln
   - Tasks sequenziell ohne parallele Ausführung ausführen
   - Globale Parameter für alle Tasks in einem Job definieren
   - Denselben verschachtelten Task mehrfach ausführen – einmal pro Element in einem Eingabe-Array ✅

10. **Welchem wesentlichen Nachteil unterliegen Job-Cluster im Vergleich zu Serverless-Clustern?**

- Fehlende Python-Unterstützung
- Höhere Betriebskosten 
- Eingeschränkte Data Governance
- Startzeit✅

11. **Was ist bei der Verwendung von Dashboard-Tasks in Lakeflow Jobs erforderlich, damit das Dashboard ordnungsgemäß funktioniert?**

- Das Dashboard muss ausschließlich mit Python-Notebooks erstellt werden
- Das Dashboard darf nur Echtzeit-Datenquellen verwenden
- Das Dashboard muss veröffentlicht und mit einem SQL Warehouse verbunden sein ✅
- Das Dashboard muss für den Ersteller des Jobs privat sein

12. **Sie erstellen einen Lakeflow Job, um einen Workflow mit mehreren Schritten wie Datenvorbereitung, Modelltraining und Validierung zu automatisieren.**

**Welche Aussage beschreibt korrekt, wie Jobs und Tasks in diesem Workflow zusammenhängen?**

- Ein Job führt die eigentliche Berechnung durch, während Tasks nur Konfiguration speichern
- Jobs und Tasks sind austauschbare Konzepte
- Ein Task definiert eine einzelne Arbeitseinheit, während ein Job die Ausführung eines oder mehrerer Tasks orchestriert und verwaltet ✅
- Ein Task ist optional, wenn ein Job eine Pipeline ausführt

13. **Welche Komponente ist beim Vergleich von kontinuierlicher und zeitgesteuerter Ausführung einzigartig für das Setup des Continuous Triggers?**

- Manuelle Run-Optionen
- Eingebaute Retry-Verwaltung ✅
- Aktivierung des Trigger-Status
- Einstellung eines Cron-Ausdrucks

14. **Sie entwerfen einen Lakeflow Job, der einem Fan-out-Muster folgt:**

- **Ein einzelner Quell-Task bereitet Daten vor**
- **Mehrere nachgelagerte Tasks führen unabhängige Verarbeitungen auf derselben Ausgabe durch**

**Wie werden die nachgelagerten Tasks im Verhältnis zum Quell-Task typischerweise ausgeführt?**

- Sie müssen zu einem einzigen Task zusammengefasst werden, um Duplikate zu vermeiden
- Sie laufen parallel, nachdem der Quell-Task abgeschlossen ist, und hängen jeweils vom selben vorgelagerten Task ab ✅
- Sie laufen sequenziell, einer nach dem anderen, nachdem der Quell-Task abgeschlossen ist
- Sie laufen vor dem Quell-Task, um Ergebnisse vorab zu berechnen

15. **Wie verbessert die dynamische Natur des If/Else-Tasks Job-Pipelines?**

- Sie macht den Workflow anpassungsfähig und reaktionsfähig gegenüber den tatsächlichen Ergebnissen ✅
- Sie verringert den Aufwand für die Verwaltung von Task-Parametern
- Sie macht Clustering überflüssig
- Sie vereinfacht die Einrichtung der Data Governance

16. **Welche Art von Parametereinstellung wird üblicherweise verwendet, um fortgeschrittene Orchestrierungslogik wie Schleifen oder bedingte Ausführung für eine bestimmte Arbeitseinheit zu unterstützen?**

- Job Parameters
- Benachrichtigungseinstellungen
- Globale Umgebungsvariablen
- Task Parameters ✅

17. **Sie entwerfen einen Lakeflow Job, der:**

- **je nachdem, ob vorgelagerte Tasks erfolgreich sind oder fehlschlagen, zu unterschiedlichen nachgelagerten Tasks verzweigen muss**
- **bei Bedarf einen Task mithilfe schleifenbasierter Ausführung über mehrere Iterationen wiederholen muss**

**Welche Funktion von Lakeflow Jobs unterstützt dieses Verhalten?**

- Konfigurationen von SQL-Warehouse-Tasks
- Cluster-Richtlinien und Compute-Konfiguration
- Refresh-Task und Qualitätsregeln einer Spark Declarative Pipeline
- Task-Orchestrierungslogik einschließlich bedingter und iterativer Tasks ✅

18. **Welche drei Komponenten bilden das einheitliche Data Engineering in Databricks Lakeflow?**

- Jobs, MLflow und Data Warehousing
- Connect, Spark Declarative Pipelines und Jobs✅
- Unity Catalog, Connect und Processing Engine 
- Connect, Storage und Governance

19. **Sie erstellen einen Lakeflow Job, um einen Workflow zu orchestrieren. Was ist in seiner einfachsten Form die minimal erforderliche Struktur für einen gültigen Job?**

- Ein einzelner Task, der die auszuführende Arbeit definiert ✅
- Mindestens zwei Tasks, damit Abhängigkeiten definiert werden können
- Eine Pipeline und ein Dashboard
- Ein Notebook und ein SQL-Task zusammen

20. **Welche anderen Tasks werden automatisch für die erneute Ausführung ausgewählt, wenn Sie einen Repair Run für einen bestimmten fehlgeschlagenen Task starten?**

- Der fehlgeschlagene Task und alle davon abhängigen nachgelagerten Tasks✅
- Alle Tasks im Job-DAG
- Nur der fehlgeschlagene Task selbst 
- Alle vorgelagerten Tasks
