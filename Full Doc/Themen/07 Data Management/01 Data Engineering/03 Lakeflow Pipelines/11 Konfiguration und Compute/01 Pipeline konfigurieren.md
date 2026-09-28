# Pipeline konfigurieren

Dieses Dokument fasst die Databricks-Referenzseite "Configure pipelines" zusammen. Verifiziert per `WebFetch` gegen die AWS-Seite (`docs.databricks.com/aws/en/ldp/configure-pipeline`) und wörtlich vollständig extrahiert von der inhaltlich übereinstimmenden Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/configure-pipeline`).

## Abschnittsübersicht

1. [Pipeline-Einstellungen im Überblick](#einstellungen)
2. [Neue Pipeline konfigurieren](#neue-pipeline)
3. [Compute-Konfigurationsoptionen](#compute-optionen)
4. [Run-as-User festlegen](#run-as)
5. [Weitere Konfigurationsaspekte](#weitere-aspekte)
6. [Pipeline-Modus festlegen](#pipeline-modus)
7. [Wie Konfigurationsänderungen wirksam werden](#config-changes)
8. [Produktedition wählen](#produktedition)
9. [Quellcode konfigurieren](#quellcode)
10. [Externe Abhängigkeiten und Python-Module](#abhaengigkeiten)
11. [Quellen](#quellen)

---

## <a id="einstellungen">1. Pipeline-Einstellungen im Überblick</a>

Pipeline-Einstellungen lassen sich in zwei Kategorien einteilen:

- **Quellcode**: Die Sammlung von Dateien, die Datasets mittels Pipeline-Syntax deklarieren.
- **Infrastruktur**: Einstellungen, die Compute, die Art der Update-Verarbeitung und den Speicherort von Tabellen steuern.

Die meisten Einstellungen haben sinnvolle Standardwerte, aber zwei erfordern vor dem Produktivbetrieb besondere Aufmerksamkeit:

- **Ziel-Catalog und -Schema**: Um Daten außerhalb der Pipeline verfügbar zu machen, müssen ein Ziel-Catalog und -Schema deklariert werden. Standardmäßig werden Daten in Unity Catalog veröffentlicht (siehe `Ziel-Schema.md`).
- **Datenzugriff**: Das für die Ausführung verwendete Compute benötigt konfigurierte Berechtigungen für die Datenquellen und, falls angegeben, einen Storage-Speicherort.

**Hinweis aus der Doku:** Die UI bietet eine Option, Einstellungen als JSON anzuzeigen und zu bearbeiten. Die meisten Einstellungen lassen sich sowohl über die UI als auch über eine JSON-Spezifikation konfigurieren; manche erweiterten Optionen sind ausschließlich über die JSON-Konfiguration verfügbar. JSON-Konfigurationsdateien sind auch beim Deployment von Pipelines in neue Umgebungen oder bei Verwendung der CLI bzw. REST-API hilfreich.

Diese Seite behandelt den aktuellen Standard-Publishing-Modus. Vor dem 5. Februar 2025 erstellte Pipelines könnten den Legacy-Publishing-Modus mit dem virtuellen `LIVE`-Schema verwenden (siehe `Ziel-Schema.md`).

## <a id="neue-pipeline">2. Neue Pipeline konfigurieren</a>

Um eine neue Pipeline zu konfigurieren:

1. Oben in der Sidebar auf **New** klicken und dann **ETL pipeline** auswählen.
2. Der Pipeline oben einen eindeutigen Namen geben.
3. Unter dem Namen werden der Standard-Catalog und das Standard-Schema angezeigt — diese lassen sich anpassen.
4. Bevorzugte Option zum Erstellen einer Pipeline auswählen:
   - **Start with sample code in SQL**
   - **Start with sample code in Python**
   - **Start with a single transformation**
   - **Add existing assets**
   - **Create a source-controlled project** (Databricks Asset Bundles)

   Eine ETL-Pipeline kann sowohl SQL- als auch Python-Quellcodedateien enthalten; die bei der Erstellung gewählte Sprache betrifft nur den mitgelieferten Beispielcode.
5. Nach der Auswahl wird zur neu erstellten Pipeline weitergeleitet.

Die ETL-Pipeline wird mit folgenden **Standardeinstellungen** erstellt:

- Unity Catalog
- Current Channel
- Serverless Compute

Diese Konfiguration wird für viele Anwendungsfälle empfohlen, einschließlich Entwicklung und Test, und eignet sich auch für produktive, geplant ausgeführte Workloads.

Alternative Wege zum Erstellen einer ETL-Pipeline: über den Workspace-Browser (**Workspace** → Ordner auswählen → **Create** → **ETL pipeline**) oder über die Jobs-&-Pipelines-Seite (**Jobs & Pipelines** → unter **New** → **ETL Pipeline**).

## <a id="compute-optionen">3. Compute-Konfigurationsoptionen</a>

Databricks empfiehlt, **immer Enhanced Autoscaling** zu verwenden. Die Standardwerte anderer Compute-Konfigurationen funktionieren für viele Pipelines gut.

Serverless-Pipelines entfernen Compute-Konfigurationsoptionen (siehe `Serverless.md`).

Folgende Einstellungen dienen der Anpassung klassischer Compute-Konfigurationen (Details siehe `Compute konfigurieren.md`):

- Workspace-Admins können eine **Cluster policy** konfigurieren.
- **Cluster mode** optional auf **Fixed size** oder **Legacy autoscaling** setzen.
- Für Workloads mit aktiviertem Autoscaling: **Min workers** und **Max workers** setzen (siehe `Autoscaling.md`).
- Photon-Beschleunigung optional deaktivierbar.
- **Cluster tags** zur Kostenüberwachung.
- **Instance types** für Worker- und Driver-Knoten konfigurierbar — ein vom Worker-Typ abweichender Driver-Typ kann sinnvoll sein, um Kosten bei großen Worker-Typen und geringer Driver-Auslastung zu senken, oder um Out-of-Memory-Probleme bei vielen kleinen Workern zu vermeiden.

## <a id="run-as">4. Run-as-User festlegen</a>

Run-as-User erlaubt es, die Identität zu ändern, unter der eine Pipeline läuft, sowie den Eigentümer der von ihr erstellten oder aktualisierten Tabellen. Das ist nützlich, wenn der ursprüngliche Ersteller der Pipeline deaktiviert wurde — zum Beispiel, weil er das Unternehmen verlassen hat. In solchen Fällen kann die Pipeline aufhören zu funktionieren, und die von ihr veröffentlichten Tabellen können für andere unzugänglich werden. Durch Aktualisieren der Pipeline auf eine andere Identität (etwa ein Service Principal) und Neuzuweisung des Eigentums an den veröffentlichten Tabellen lässt sich der Zugriff wiederherstellen. Das Ausführen von Pipelines als Service Principals gilt als Best Practice, da diese nicht an einzelne Nutzer gebunden und dadurch sicherer, stabiler und zuverlässiger für automatisierte Workloads sind.

### Erforderliche Berechtigungen

**Für den Nutzer, der die Änderung vornimmt:**

- `CAN_MANAGE`-Berechtigung auf die Pipeline
- `CAN_USE`-Rolle auf das Service Principal (falls Run-as auf ein Service Principal gesetzt wird)

**Für den Run-as-Nutzer bzw. das Service Principal:**

- **Workspace-Zugriff:** Workspace-Access-Berechtigung; Can-use-Berechtigung auf verwendete Cluster-Policies; Compute-Erstellungsberechtigung im Workspace
- **Quellcode-Zugriff:** Can-read-Berechtigung auf alle im Pipeline-Quellcode enthaltenen Notebooks; Can-read-Berechtigung auf Workspace-Dateien, falls verwendet
- **Unity-Catalog-Berechtigungen** (für Pipelines mit Unity Catalog): `USE CATALOG` auf den Ziel-Catalog; `USE SCHEMA` und `CREATE TABLE` auf das Ziel-Schema; `MODIFY`-Berechtigung auf bestehende Tabellen, die die Pipeline aktualisiert; `CREATE SCHEMA`, falls die Pipeline neue Schemas erstellt
- **Legacy-Hive-Metastore-Berechtigungen** (für Pipelines mit Hive-Metastore): `SELECT` und `MODIFY` auf Ziel-Datenbanken und -Tabellen
- **Zusätzlicher Cloud-Storage-Zugriff** (falls zutreffend): Leseberechtigungen für Quell-Speicherorte; Schreibberechtigungen für Ziel-Speicherorte

### Vorgehen

1. **Jobs & Pipelines** öffnen und den Namen der zu bearbeitenden Pipeline auswählen.
2. Auf der Pipeline-Monitoring-Seite auf **Settings** klicken.
3. In der Seitenleiste **Pipeline settings** neben **Run as** auf das Stift-Symbol **Edit** klicken.
4. Im Bearbeitungs-Widget eine Option auswählen: das eigene Nutzerkonto oder ein Service Principal, für das `CAN_USE`-Berechtigung besteht.
5. Auf **Save** klicken.

Nach erfolgreicher Aktualisierung des Run-as-Users:

- Die Pipeline-Identität wechselt für alle künftigen Läufe zum neuen Nutzer bzw. Service Principal.
- Bei Unity-Catalog-Pipelines wird der Eigentümer der von der Pipeline veröffentlichten Tabellen auf die neue Run-as-Identität aktualisiert.
- Künftige Pipeline-Updates verwenden die Berechtigungen und Credentials der neuen Run-as-Identität.
- Wie bei jeder Einstellungsänderung gilt die neue Identität für das nächste Pipeline-Update: Continuous-Pipelines starten automatisch mit der neuen Identität neu, Triggered-Pipelines wenden sie beim nächsten Lauf an. Die Run-as-Änderung kann ein aktives Update unterbrechen.

**Hinweis aus der Doku:** Schlägt die Aktualisierung des Run-as-Users fehl, wird eine Fehlermeldung mit dem Grund angezeigt — häufige Ursache sind unzureichende Berechtigungen auf das Service Principal.

## <a id="weitere-aspekte">5. Weitere Konfigurationsaspekte</a>

- Die **Advanced**-Produktedition gewährt Zugriff auf alle Pipeline-Features. Pipelines können optional mit **Pro**- oder **Core**-Edition betrieben werden (siehe Abschnitt 8).
- **Pipeline mode** steuert die Datenverarbeitung (siehe Abschnitt 6).
- Für den kontinuierlichen Produktivbetrieb empfiehlt Databricks, die Pipeline in einen **Continuous Job** einzubetten, statt den eingebauten **Continuous**-Modus der Pipeline zu verwenden.
- **Notifications**: Eine oder mehrere E-Mail-Adressen lassen sich für Benachrichtigungen bei folgenden vier Ereignissen konfigurieren (laut Doku-Seite "Add email notifications for pipeline events"; **Korrektur**: nicht nur Erfolg/Fehlschlag — eine "Pipeline Starts"-Bedingung existiert laut aktueller Doku nicht):
  - Ein Pipeline-Update wird erfolgreich abgeschlossen.
  - Ein Pipeline-Update schlägt fehl, entweder mit einem wiederholbaren oder einem nicht-wiederholbaren Fehler (Benachrichtigung bei jedem Fehlschlag).
  - Ein Pipeline-Update schlägt mit einem nicht-wiederholbaren (fatalen) Fehler fehl (Benachrichtigung nur bei fatalen Fehlern).
  - Ein einzelner Data Flow schlägt fehl.

  Konfiguriert werden die E-Mail-Benachrichtigungen über die Pipeline-Einstellungen (siehe `13 Observability/Monitoring-UI.md`).
- **Parameters**-Feld: Key-Value-Paare, die SQL-Quellcode über Named-Parameter-Syntax referenzieren kann und die beim Start eines Updates oder von einem Job aus überschrieben werden können.
- **Configuration**-Feld: Spark-Konfigurationswerte, die das Pipeline-Verhalten steuern, etwa `pipelines.enzyme.enabled`. Für Python-Pipelines, die Parametrisierung benötigen, macht das Configuration-Feld Werte zusätzlich über `spark.conf.get()` verfügbar.
- **Tags**: Key-Value-Paare für die Pipeline, sichtbar in der Jobs-&-Pipelines-Liste. Pipeline-Tags sind **nicht** mit Billing verknüpft.
- **Preview**-Channel: zum Testen der Pipeline gegen anstehende Pipeline-Runtime-Änderungen und neue Features.

## <a id="pipeline-modus">6. Pipeline-Modus festlegen</a>

Die Einstellung **Pipeline mode** steuert, wie eine Pipeline Daten verarbeitet:

- **Triggered** (Standard): Die Pipeline aktualisiert alle Tabellen mit den beim Update-Start verfügbaren Daten und stoppt dann — Compute läuft nur für die Dauer des Updates. Triggered-Pipelines werden bedarfsgesteuert oder geplant ausgeführt.
- **Continuous**: Hält Tabellen aktuell, indem neue Daten verarbeitet werden, sobald sie in den Quellen eintreffen. Das reduziert die Verzögerung zwischen neuen Daten und aktualisierten Ergebnissen — auf Kosten eines dauerhaft laufenden Clusters. Continuous-Modus sollte nur bei einer nachgewiesenen Low-Latency-Anforderung gewählt werden.

## <a id="config-changes">7. Wie Konfigurationsänderungen wirksam werden</a>

Wird eine Pipeline-Einstellung bearbeitet und gespeichert, gilt die Änderung für das nächste Pipeline-Update. Wird die Pipeline von einem **Continuous Job** orchestriert, muss der Job nicht neu gestartet werden, damit die aktualisierten Einstellungen wirksam werden — der Job wendet sie beim nächsten Update an. Der Zeitplan des Jobs bestimmt dabei den Ausführungsmodus, nicht die Pipeline-eigene **Pipeline mode**-Einstellung.

Wird stattdessen die eingebaute **Pipeline mode**-Einstellung der Pipeline verwendet:

- **Continuous-Pipelines** starten automatisch mit der aktualisierten Konfiguration neu — das kann ein aktives Update unterbrechen.
- Ein Wechsel von Triggered zu Continuous startet automatisch ein neues Update mit den aktualisierten Einstellungen. Umgekehrt bricht ein Wechsel von Continuous zu Triggered ein aktives Update ab.

## <a id="produktedition">8. Produktedition wählen</a>

Verfügbare Produkteditionen:

- **`Core`**: für Streaming-Ingest-Workloads. Geeignet, wenn keine fortgeschrittenen Features wie CDC oder Expectations benötigt werden.
- **`Pro`**: für Streaming-Ingest- und CDC-Workloads. Unterstützt alle `Core`-Features zuzüglich Unterstützung für Workloads, die Tabellen anhand von Änderungen in Quelldaten aktualisieren.
- **`Advanced`**: für Streaming-Ingest-, CDC- und Expectations-Workloads. Unterstützt die Features von `Core` und `Pro` sowie Datenqualitäts-Constraints mit Expectations (siehe `08 Data Quality (Expectations)/`).

Die Produktedition lässt sich beim Erstellen oder Bearbeiten einer Pipeline auswählen; pro Pipeline kann eine andere Edition gewählt werden.

Pipelines behalten **60 Tage** vergangener Updates in der Pipeline-UI und der Pipelines-API. Aktive (nicht-terminale) Updates erscheinen immer; ist ein Update älter als das Retention-Fenster, schließt Databricks es aus Listenantworten aus, behält es aber im zugrunde liegenden Event-Log.

**Hinweis aus der Doku:** Enthält die Pipeline Features, die von der gewählten Produktedition nicht unterstützt werden (etwa Expectations), wird eine erklärende Fehlermeldung angezeigt. Die Pipeline kann dann bearbeitet werden, um die passende Edition auszuwählen.

## <a id="quellcode">9. Quellcode konfigurieren</a>

Der Asset-Browser im Lakeflow Pipelines Editor dient zur Konfiguration des Quellcodes einer Pipeline. Pipeline-Quellcode wird in SQL- oder Python-Skripten definiert, die als Workspace-Dateien gespeichert sind. Standardmäßig liegt der Pipeline-Quellcode im Ordner `transformations` im Root-Ordner der Pipeline.

Da Pipelines Dataset-Abhängigkeiten automatisch analysieren, um den Verarbeitungsgraphen aufzubauen, können Quellcode-Assets in beliebiger Reihenfolge hinzugefügt werden.

## <a id="abhaengigkeiten">10. Externe Abhängigkeiten und Python-Module</a>

Pipelines unterstützen die Verwendung externer Abhängigkeiten, etwa Python-Pakete und -Bibliotheken. Zusätzlich zur Implementierung von Python-Code direkt in Pipeline-Quellcodedateien lassen sich Databricks Git Folders oder Workspace-Dateien nutzen, um Code als Python-Module zu speichern — besonders nützlich für gemeinsam genutzte Funktionalität über mehrere Pipelines oder Notebooks hinweg.

---

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/configure-pipeline
- https://learn.microsoft.com/en-us/azure/databricks/ldp/configure-pipeline (wörtliche Vollzitat-Quelle, inhaltlich mit AWS-Seite abgeglichen)
- Add email notifications for pipeline events (vollständige Liste der vier Notification-Bedingungen, per AWS- und Azure-Seite wörtlich cross-verifiziert): https://docs.databricks.com/aws/en/ldp/monitoring-ui, https://learn.microsoft.com/en-us/azure/databricks/ldp/monitoring-ui — siehe auch `13 Observability/Monitoring-UI.md` Abschnitt 1 in diesem Projekt.

**Stand:** 2026-08-21.
