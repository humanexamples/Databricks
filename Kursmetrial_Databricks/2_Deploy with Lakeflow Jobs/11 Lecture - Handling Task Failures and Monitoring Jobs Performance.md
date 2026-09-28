Nach Task-Fehlern wiederherstellen und die Performance von Lakeflow Jobs überwachen. Sie sehen, wie Repair and Rerun eine effiziente Wiederherstellung nach fehlgeschlagenen Job-Runs unterstützt und wie Systemtabellen und Details in der Spark UI Ihnen helfen, die Job-Performance zu überwachen.

![Repair and rerun workflow showing failed task recovery](./Includes/images/lecture_handling_task_failures/repair_rerun.png)

Die **Repair**-Funktion ermöglicht es, Tasks **erneut auszuführen** und Task-Parameter zu überschreiben

**Verringert den Zeit-** und Ressourcenaufwand für die Wiederherstellung nach fehlgeschlagenen Job-Runs

Bei einem **Task-Fehler** können Sie:

- den **Task** ändern und erneut ausführen
- die **Parameter** ändern und erneut ausführen

##### Zusätzliche Hinweise
**Die Repair-Funktion steht für einen ausgefeilten Ansatz zur Fehlerbehebung:**

- **Gezielte Wiederherstellung:** Anstatt ganze Workflows neu zu starten, können Sie bestimmte fehlgeschlagene Tasks ändern und nur das Nötige erneut ausführen. Das spart erheblich Zeit und Rechenressourcen.
- **Überschreiben von Parametern:** Die Möglichkeit, Parameter während Repair-Runs zu ändern, erlaubt es Ihnen, Konfigurationsprobleme zu beheben, die Ressourcenzuweisung anzupassen oder die Verarbeitungslogik zu ändern, ohne den gesamten Job neu aufzubauen.
- **Wiederherstellungsszenarien:**
- **Konfigurationskorrekturen:** Parameterwerte korrigieren, die Task-Fehler verursacht haben
- **Ressourcenanpassungen:** Arbeitsspeicher oder Compute-Ressourcen für Tasks erhöhen, die aufgrund von Ressourcenengpässen fehlgeschlagen sind
- **Code-Updates:** Korrekturen für Logikfehler bereitstellen und nur betroffene Tasks erneut ausführen
- **Datenqualitätsprobleme:** Die Verarbeitungslogik anpassen, um während der Ausführung entdeckte Datenqualitätsprobleme zu behandeln

**Kosteneffizienz:** Indem Sie nur fehlgeschlagene Tasks erneut ausführen, minimieren Sie unnötige Berechnungen und senken die Kosten – besonders wichtig bei großen, komplexen Workflows.

### A2. Repair Run (Reparatur-Lauf)

Klicken Sie auf die hervorgehobenen Felder, um zu erfahren, wie Sie einen Task reparieren.





##### Zusätzliche Hinweise
**Die selektive erneute Ausführung bietet enorme operative Vorteile:**

- **Ressourcenoptimierung:** Wenn nur fehlgeschlagene Tasks statt ganzer Workflows ausgeführt werden, kann die Wiederherstellungszeit in komplexen Pipelines um 80–90 % sinken – das spart Zeit und Geld.
- **Geringeres Risiko:** Kleinere Wiederherstellungsvorgänge belasten die Systemressourcen weniger und verringern das Risiko von Kaskadenfehlern während der Wiederherstellungsversuche.
- **Schnellere Behebung:** Teams können schneller auf Fehler reagieren, wenn sie nicht auf den Abschluss ganzer Workflows warten müssen, was die Einhaltung von SLAs und die geschäftliche Reaktionsfähigkeit verbessert.

**Beachten Sie, dass das Reparieren eines Tasks nicht das Reparieren des Jobs bedeutet.**
Beispiel: Wenn Sie einen falschen Parameter übergeben und ihn mit der Repair-Run-Funktion korrigieren, müssen Sie ihn trotzdem noch in Ihrem Job anpassen.

### A3. Nach dem Repair Run

- **Audit Trail**: Vollständige Transparenz darüber, was wann und von wem repariert wurde – wichtige Informationen für Fehlerbehebung und Prozessverbesserung.
- **Erfolgsvalidierung**: Klare Anzeige, welche Tasks erfolgreich wiederhergestellt wurden, was Vertrauen in den Repair-Prozess schafft.
- **Lernchancen**: Historische Repair-Daten helfen Teams, Fehlermuster zu erkennen und das ursprüngliche Job-Design zu verbessern, um künftige Probleme zu vermeiden.

## B. Job-Performance überwachen

Fehlerbehandlung bedeutet nicht nur, Tasks neu zu starten – es geht darum, robuste Systeme zu bauen, die sich effizient erholen und die Datenkonsistenz auch dann wahren, wenn Komponenten ausfallen.

### system.lakeflow
**system.lakeflow** ist ein eingebauter, schreibgeschützter Katalog, der sämtliche Job-Aktivitäten über alle Workspaces in der Region protokolliert.

### Timeline-Tabellen
Timeline-Tabellen unterteilen lange Runs mithilfe von **period_start_time** und **period_end_time** in Stundenabschnitte und ermöglichen so zuverlässige Analysen von Dauer, Parallelität und SLAs.

### Wichtige Tabellen

| Tabelle | Beschreibung |
| --- | --- |
| `jobs` | Grundlegende Job-Informationen |
| `job_tasks` | Grundlegende Task-Definitionen |
| `job_run_timeline` | Jeder Job-Run im Zeitverlauf |
| `job_task_run_timeline` | Jeder Task-Run im Zeitverlauf |
| `Pipelines` | Grundlegende Pipeline-Informationen |

![system.lakeflow catalog system tables UI](./Includes/images/lecture_monitoring_jobs_performance/system_lakeflow_catalog_ui.png)

### Abfrage-/Code-Details
![Spark UI query and code details panel](./Includes/images/lecture_monitoring_jobs_performance/spark_query_details_ui.png)

### Timeline
![Spark UI job run timeline showing task duration and overlap](./Includes/images/lecture_monitoring_jobs_performance/spark_timeline_ui.png)

- Die **Timeline** im Job-Run hebt Start/Ende, Dauer und Überschneidungen von Tasks hervor, um Engpässe schnell zu erkennen.
- Klicken Sie auf einen Task, um Status, Zeitstempel, Dauer, Cluster/Runtime, Logs und eine kurze I/O-Übersicht zu sehen.
- Klicken Sie auf die **Query/Code**-Details, um den vollständigen Text, die Run-ID, die Aufteilung der Laufzeit (Optimieren/Pruning vs. Ausführen), Details zu gelesenen/geschriebenen Dateien, Dateien & Partitionen sowie Spill-Details zu sehen.
**Hohe Planungszeit**

Pruning/Partitionierung verbessern**Hohe Ausführungszeit**

Joins/Aggregationen optimieren (Broadcast, Skew-Korrekturen)

##### Zusätzliche Hinweise
Der Katalog **system.lakeflow** bietet Monitoring-Funktionen auf Enterprise-Niveau:
- **Umfassendes Logging:** Sämtliche Job-Aktivitäten über alle Workspaces in der Region werden automatisch protokolliert und bieten vollständige Transparenz über Ausführungsmuster und Performance-Trends von Workflows.
- **Timeline-Analyse:** Timeline-Tabellen verwenden **period_start_time** und **period_end_time**, um lang laufende Jobs in Stundenabschnitte zu unterteilen, und ermöglichen so eine genaue Analyse der Dauer, die Verfolgung der Parallelität und SLA-Messungen – auch für komplexe, lang laufende Workflows.
- **Funktionen der wichtigsten Tabellen:** **jobs:** Grundlegende Job-Metadaten und Konfigurationsinformationen
- **job_tasks:** Task-Definitionen und Konfigurationsdetails
- **job_run_timeline:** Vollständige Ausführungshistorie für jeden Job-Run
- **job_task_run_timeline:** Detaillierte Ausführungshistorie für einzelne Tasks
- **pipelines:** Informationen über Delta-Live-Tables-Pipelines
**Analysemöglichkeiten:** Diese Daten ermöglichen anspruchsvolle Analysen, darunter Kostenanalysen, Performance-Trends, die Verfolgung der SLA-Einhaltung und die Optimierung der Ressourcennutzung.

Die Spark UI bietet detaillierte Performance-Einblicke zur Optimierung:
- **Timeline-Analyse:** Die Ausführungs-Timeline hebt sofort Task-Dauer, Überschneidungen und Engpässe hervor und ermöglicht so eine schnelle Identifizierung von Performance-Problemen.
- **Details auf Task-Ebene:** Ein Klick auf einzelne Tasks zeigt umfassende Informationen wie Ausführungszeitstempel, Ressourcennutzung, Cluster-Konfiguration, Logs und I/O-Statistiken.
- **Details zur Abfrage-Performance:** Eine detaillierte Abfrageanalyse zeigt Ausführungspläne, Optimierungsentscheidungen, Dateizugriffsmuster, Partitionsinformationen und Details zu Daten-Spills – unverzichtbar für das Performance-Tuning.
- **Umsetzbare Erkenntnisse:** **Hohe Planungszeit:** Weist auf den Bedarf an besseren Partitionierungsstrategien oder Metadaten-Optimierung hin
- **Hohe Ausführungszeit:** Deutet auf Optimierungsmöglichkeiten bei Joins, Broadcast-Strategien oder der Behandlung von Skew hin
- **Ressourcenengpässe:** Identifiziert Speicher-, CPU- oder I/O-Engpässe, die Anpassungen der Cluster-Konfiguration erfordern

## C. Fazit

- Mit Repair Runs können Sie nur fehlgeschlagene Tasks erneut ausführen, Parameter überschreiben, Wiederherstellungszeit/-kosten senken und die Wiederherstellung in der Historie der Job-Runs nachverfolgen.
- **system.lakeflow** protokolliert Job-Aktivitäten und stellt Timeline-Tabellen für Analysen von Dauer, Parallelität und SLAs bereit.
- Die Spark UI hilft, Engpässe zu erkennen, indem sie Task-Timing, Überschneidungen, Planungszeit und Ausführungszeit zur Optimierung anzeigt.
