# Serverless Compute für Lakeflow Pipelines

Dieses Dokument fasst die Databricks-Referenzseite "Configure a serverless pipeline" zusammen. Verifiziert per `WebFetch` gegen die AWS-Seite (`docs.databricks.com/aws/en/ldp/serverless`) und wörtlich vollständig extrahiert von der inhaltlich übereinstimmenden Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/serverless`) — die 4–6-Minuten-Startlatenz für den Standard-Performance-Modus wurde in beiden Abrufen übereinstimmend genannt.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Voraussetzungen](#voraussetzungen)
3. [Empfohlene Konfiguration](#konfiguration)
4. [Weitere Konfigurationsaspekte](#weitere-aspekte)
5. [Serverless Usage Policy](#usage-policy)
6. [Performance-Modus wählen](#performance-modus)
7. [Serverless-Pipeline-Features](#features)
8. [Bestehende Pipeline zu Serverless konvertieren](#konvertieren)
9. [DBU-Nutzung ermitteln](#dbu-nutzung)
10. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick</a>

Serverless-Pipelines laufen auf von Databricks verwaltetem Compute, was den Großteil der Infrastrukturkonfiguration entfallen lässt.

Databricks empfiehlt, neue Pipelines mit Serverless zu entwickeln. Manche Workloads könnten die Konfiguration von Classic Compute oder die Arbeit mit dem Legacy-Hive-Metastore erfordern.

**Hinweise aus der Doku:**

- Serverless-Pipelines verwenden **immer** Unity Catalog.
- Die Structured-Streaming-Trigger-Limitierungen der allgemeinen Serverless-Compute-Limitierungen gelten **nicht** für Pipeline-Modi — Serverless-Pipelines unterstützen Triggered-, Continuous- und Real-Time-Modi (siehe `Echtzeit-Verarbeitung.md`).
- Compute-Einstellungen können in der JSON-Konfiguration einer Serverless-Pipeline **nicht** manuell in einem `clusters`-Objekt hinzugefügt werden. Der Versuch führt zu einem Fehler.
- Für eine Azure-Private-Link-Verbindung mit Serverless-Lakeflow-Pipelines muss der Databricks-Ansprechpartner kontaktiert werden.

## <a id="voraussetzungen">2. Voraussetzungen</a>

- Der Workspace muss Unity Catalog aktiviert haben, um Serverless-Pipelines zu nutzen.
- Der Workspace muss sich in einer Serverless-fähigen Region befinden.
- Die Serverless-Nutzungsbedingungen müssen akzeptiert sein.

## <a id="konfiguration">3. Empfohlene Konfiguration</a>

**Wichtig:** Compute-Erstellungsberechtigung ist zur Konfiguration von Serverless-Pipelines **nicht** erforderlich. Standardmäßig können alle Workspace-Nutzer Serverless-Pipelines verwenden.

Serverless-Pipelines entfernen die meisten Konfigurationsoptionen, da Databricks die gesamte Infrastruktur verwaltet. Beim Erstellen einer neuen Pipeline ist Serverless der Standard.

## <a id="weitere-aspekte">4. Weitere Konfigurationsaspekte</a>

Auch für Serverless-Pipelines verfügbar:

- Die **Continuous**-Pipeline-Modus-Option für den Produktivbetrieb.
- **Notifications** für E-Mail-Updates bei Erfolgs- oder Fehlschlagbedingungen.
- Das **Configuration**-Feld für Key-Value-Paare — dient zum einen zur Referenzierung beliebiger Parameter im Quellcode, zum anderen zur Konfiguration von Pipeline-Einstellungen und Spark-Konfigurationen.
- Der **Preview**-Channel zum Testen gegen anstehende Runtime-Änderungen.
- Externe Python-Abhängigkeiten über die **Environment**-Einstellungen der Pipeline. Das manuelle Neustarten des Python-Prozesses (`dbutils.library.restartPython()`) wird **nicht** unterstützt — Abhängigkeiten können also zur Laufzeit nicht installiert oder neu geladen werden.

## <a id="usage-policy">5. Serverless Usage Policy</a>

**Public Preview.** Serverless Usage Policies erlauben es, benutzerdefinierte Tags auf Serverless-Nutzung anzuwenden, für eine granulare Billing-Zuordnung. Nach Auswahl der Checkbox **Serverless** erscheint die Einstellung **Usage policy**, über die die gewünschte Policy ausgewählt werden kann. Die Tags werden von der Serverless-Usage-Policy geerbt und können nur von Workspace-Admins bearbeitet werden.

**Hinweis aus der Doku:** Nach Zuweisung einer Serverless-Usage-Policy werden bestehende Pipelines **nicht automatisch** mit dieser Policy getaggt — bestehende Pipelines müssen manuell aktualisiert werden, um eine Policy anzuhängen.

## <a id="performance-modus">6. Performance-Modus wählen</a>

Für Triggered-Pipelines lässt sich der Serverless-Compute-Performance-Modus über die Einstellung **Performance optimized** im Pipeline-Scheduler wählen.

- **Standard Performance Mode** (Einstellung deaktiviert): reduziert Kosten für Workloads, bei denen eine etwas höhere Startlatenz akzeptabel ist. Serverless-Workloads im Standard-Performance-Modus starten typischerweise **innerhalb von vier bis sechs Minuten** nach Auslösung, abhängig von Compute-Verfügbarkeit und optimierter Planung.
- **Performance Optimized** (Einstellung aktiviert): optimiert die Pipeline auf Performance, was zu schnellerem Start und schnellerer Ausführung für zeitkritische Workloads führt.

Beide Modi nutzen dieselbe SKU; der Standard-Performance-Modus verbraucht jedoch weniger DBUs, was die geringere Compute-Nutzung widerspiegelt.

**Hinweis aus der Doku:** Um Standard Performance Mode mit einer Continuous-Pipeline zu nutzen, muss die Pipeline mit einem Continuous Job ausgeführt werden, und die Checkbox **Performance optimized** im Zeitplan muss deaktiviert werden.

## <a id="features">7. Serverless-Pipeline-Features</a>

Neben der vereinfachten Konfiguration bieten Serverless-Pipelines folgende Features:

- **Incremental Refresh für Materialized Views**: Updates für Materialized Views werden wo möglich inkrementell aktualisiert. Incremental Refresh liefert dieselben Ergebnisse wie eine vollständige Neuberechnung. Lassen sich Ergebnisse nicht inkrementell berechnen, verwendet das Update einen Full Refresh.
- **Stream Pipelining**: Zur Verbesserung von Auslastung, Durchsatz und Latenz bei Streaming-Daten-Workloads wie Datenaufnahme werden Micro-Batches *pipelined* — anstatt Micro-Batches sequenziell wie im Standard-Spark-Structured-Streaming auszuführen, führen Serverless-Lakeflow-Pipelines Micro-Batches gleichzeitig aus, was die Auslastung der Compute-Ressourcen verbessert. Stream Pipelining ist in Serverless-Pipelines standardmäßig aktiviert.
- **Vertical Autoscaling**: Serverless-Lakeflow-Pipelines ergänzen die horizontale Autoscaling-Funktion von Databricks Enhanced Autoscaling, indem automatisch die kosteneffizientesten Instanztypen zugewiesen werden, die die Pipeline ohne Out-of-Memory-Fehler ausführen können (Details siehe `Autoscaling.md`).

## <a id="konvertieren">8. Bestehende Pipeline zu Serverless konvertieren</a>

Bestehende, mit Unity Catalog konfigurierte Pipelines lassen sich zu Serverless-Pipelines konvertieren:

1. In der Workspace-Sidebar auf **Jobs & Pipelines** klicken.
2. Auf den **Namen** der Pipeline klicken.
3. Auf **Settings** klicken.
4. In der rechten Seitenleiste unter **Compute** auf das Stift-Symbol klicken.
5. Die Checkbox neben **Serverless** aktivieren.
6. Auf **Save** klicken.

**Wichtig:** Beim Aktivieren von Serverless werden alle für die Pipeline konfigurierten Compute-Einstellungen entfernt. Wird eine Pipeline zurück auf Non-Serverless-Updates umgestellt, müssen die gewünschten Compute-Einstellungen erneut konfiguriert werden.

## <a id="dbu-nutzung">9. DBU-Nutzung ermitteln</a>

Die DBU-Nutzung von Serverless-Lakeflow-Pipelines lässt sich durch Abfrage der Billable-Usage-Tabelle ermitteln, Teil der Databricks-System-Tabellen.

---

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/serverless
- https://learn.microsoft.com/en-us/azure/databricks/ldp/serverless (wörtliche Vollzitat-Quelle, inhaltlich mit AWS-Seite abgeglichen)
