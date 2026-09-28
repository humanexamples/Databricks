# Job-Performance diagnostizieren

Bei Jobs/Tasks, die länger als erwartet laufen, hilft die Jobs-UI, Zeitverteilung und Optimierungspotenzial zu identifizieren.

## Lauf-Aufschlüsselung nach Phase

Beim Ansehen der Job-Run-Details zeigt das Hovern über das **Duration**-Feld:

- **Queued**
- **Waiting for resources**
- **Library installation**
- **Running**

![Lauf-Aufschlüsselung eines Job-Laufs](images/jobs-run-breakdown.png)

Gilt für Job- und Task-Läufe. Bei Multi-Task-Jobs zählt „Waiting for resources" auf Job-Ebene nur bis zum Start des ersten Tasks — vollständige, taskbezogene Aufschlüsselungen erscheinen im Task-Run-Output.

**Queued:** Job/Task wartet wegen Concurrency-Limits (max. gleichzeitige Läufe desselben Jobs oder Workspace-weites Limit). Abhilfe: Limit erhöhen oder Zeitpläne entzerren.

**Waiting for resources:** wartet auf Compute-Verfügbarkeit. Bei Serverless: Standard Performance Mode hat 4–6 Minuten Startlatenz — Performance Optimized reduziert sie. Bei Classic Compute: langsame VM-Starts oder Quota-Probleme — Abhilfe: Serverless, Instance Pools mit Idle-Termination, mehrere Tasks in einem Multi-Task-Job auf einem Cluster bündeln, Flexible Node Types für automatischen Fallback aktivieren.

**Library installation:** Zeit für Abhängigkeiten vor der Ausführung. Bei Serverless: ungecachte Environment oder viele Pakete aus langsamen Custom-PyPI-Repositories. Bei Classic Compute: große, komplexe Cluster-Environments, insbesondere mit Init-Skripten. Abhilfe: Paketanforderungen reduzieren, Workspace-Base-Environments in Betracht ziehen.

**Running:** längere Laufzeiten durch mehr Daten, Konfigurationsänderungen oder langsamere Queries. Prüfen: System-Tabellen für Änderungen, Query-History/-Profile bei Serverless, Spark UI bei Classic Compute.

## Streaming-Task-Metriken (Public Preview)

Streaming Observability für Apache Kafka, Amazon Kinesis, Auto Loader, Google Pub/Sub, Delta-Tabellen. Metriken: Backlog-Sekunden, -Bytes, -Records, -Dateien, als Diagramme (Maximalwerte, minutenweise aggregiert, bis zu 48 Stunden).

| Quelle | Backlog Bytes | Backlog Records | Backlog Seconds | Backlog Files |
|---|---|---|---|---|
| Kafka | ✓ | ✓ | | |
| Kinesis | ✓ | ✓ | | |
| Delta | ✓ | ✓ | | |
| Auto Loader | ✓ | ✓ | | |
| Google Pub/Sub | ✓ | ✓ | | |

**Ansehen:** Job-Run-Details → Task wählen → Tab **Metrics** im Task-Run-Panel → Caret-Icon zum Aufklappen der Diagramme → Stream-IDs zum Filtern eingeben → Zeitraum über Dropdown anpassen → Next/Previous zum Navigieren zwischen Streams.

**Einschränkungen:** Metriken aktualisieren minütlich (bei 4+ Streams alle 5 Minuten). Nur die ersten 50 Streams pro Lauf werden erfasst. Erfassung im 1-Sekunden-Takt — kürzere Intervalle verhindern ggf. die Sichtbarkeit. Für Quellen ohne Standard-Metrik-Erfassung: `spark.sql.streaming.metricsEnabled` aktivieren.

## Query-Performance-Metriken für Serverless Jobs (Beta)

Query-Profile-Metriken und Performance-Insights direkt in der Job-Run-UI — aggregierte Metriken umfassen gelesene/geschriebene Zeilen pro Task und Gesamt-Query-Anzahl.

**Voraussetzungen:** Preview „Improved Lakeflow Performance Observability" aktiviert; Workspace-Zugriff auf Query Performance Insights (für die Lightbulb-Indikatoren — aggregierte Metriken auch ohne diese sichtbar).

**Angezeigte Metriken:** gelesene/geschriebene Zeilen je Task-Lauf, Gesamt-Query-Anzahl je Task-Lauf, Performance-Insights-Indikator (Glühbirne) bei Tasks mit erkannten Insights.

| Ort | Anzeige |
|---|---|
| Task-Run-Sidebar | Zeilen gelesen/geschrieben, Query-Anzahl, Insights-Indikator |
| DAG-Ansicht | Glühbirnen-Badge auf Task-Knoten mit Insights |
| Timeline-Ansicht | Glühbirne neben Task-Namen mit Insight-Anzahl; Glühbirne bei einzelnen Queries |
| Listenansicht | Glühbirne in Insights-Spalte |

**Untersuchungsablauf:** Job-Lauf öffnen → Timeline-Ansicht → länger als erwartete Tasks anhand der Dauerverteilung identifizieren → über Tasks hovern (verarbeitete Zeilen, Query-Anzahl, Indikatoren) → Tasks aufklappen für Einzel-Queries → Query-Text mit Glühbirnen-Icon anklicken für Insights → Empfehlungen umsetzen, Job erneut ausführen.

**Läufe vergleichen:** langsamen mit vorherigem schnellem Lauf nebeneinander vergleichen — Unterschiede bei Zeilen (Datenvolumen), Query-Anzahl (Workload-Form), Insights (Ineffizienzen).

**Einschränkungen:** nur für Serverless Lakeflow Jobs — Classic Compute ohne diese Informationen. Aggregation über die ersten 100 Queries; darüber hinaus nur Teilsummen.

## Quelle

- https://docs.databricks.com/aws/en/jobs/diagnose-job-performance
