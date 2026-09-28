# Data Engineering Agent (Genie Code Agent Mode) — Referenz

Dieses Dokument fasst zusammen, wie sich Genie Code im Agent-Modus (in der Doku-URL als "de-agent" / Data Engineering Agent bezeichnet) zur Pipeline-Entwicklung im Lakeflow Pipelines Editor nutzen lässt. Jede faktische Aussage wurde per `WebFetch` gegen die offizielle Databricks-Online-Dokumentation verifiziert. Die AWS-Seite lieferte zunächst zusammengefasste Auszüge; für den vollständigen, wörtlich zitierbaren Text wurde zusätzlich die Azure/Microsoft-Learn-Spiegelseite im Roh-Markdown-Format abgerufen. Beide Fassungen stimmten inhaltlich überein; produktbezogene Unterschiede ("Databricks" vs. "Azure Databricks") wurden im Fließtext neutral als "Databricks" wiedergegeben. Der offizielle Seitentitel lautet "Use Genie Code for pipeline development" — die Datei behält den vom Auftrag vorgegebenen Namen "Data Engineering Agent" bei, da dies der Name im URL-Pfad (`ldp/de-agent`) ist.

## Abschnittsübersicht

1. [Was ist Genie Code für Pipeline-Entwicklung?](#einleitung)
2. [Voraussetzungen](#voraussetzungen)
3. [Genie Code für Pipeline-Entwicklung nutzen](#nutzung)
4. [Fähigkeiten im Agent-Modus](#faehigkeiten)
5. [Migration von anderen ETL-Frameworks zu Lakeflow-Pipelines](#migration)
6. [Beispiel-Prompts](#beispiele)
7. [Quellen](#quellen)

---

## <a id="einleitung">1. Was ist Genie Code für Pipeline-Entwicklung?</a>

Genie Code im Agent-Modus ist der KI-Data-Engineering-Partner für Entwickler im Lakeflow Pipelines Editor. Er erkundet Daten, generiert und führt Pipeline-Code aus und behebt Fehler ausgehend von einem einzigen Prompt.

**Hinweis der Doku:** Diese Seite beschreibt die Nutzung von Genie Code, um Spark Declarative Pipelines on Lakeflow (SDP) zu entwickeln und zu migrieren. Um Legacy-SQL aus anderen Dialekten (z. B. T-SQL, Snowflake oder Oracle) nach ANSI SQL zu konvertieren, wird stattdessen der agentische Code Converter verwendet.

Genie Code im Agent-Modus ist ein autonomer Partner, der komplette mehrstufige Data-Engineering-Workflows im Lakeflow Pipelines Editor automatisieren kann.

![Use the Data Engineering Agent](images/assistant-de-agent.gif)

Im Vergleich zum Genie-Code-Chat-Modus besitzt der Agent-Modus erweiterte Fähigkeiten: Planung einer Lösung, Abrufen relevanter Assets, Ausführen von Code, Nutzung von Pipeline-Outputs zur Verbesserung der Ergebnisse, automatisches Beheben von Fehlern und mehr.

Genie Code im Agent-Modus kann ganze Pipelines End-to-End von Grund auf planen und generieren oder die Arbeit an einer bestehenden Pipeline beschleunigen. Der Agent arbeitet mit dem Nutzer zusammen, um seine Pläne genehmigen zu lassen und die nächsten Schritte zu bestätigen, bevor er fortfährt. Mit Zustimmung des Nutzers kann Genie Code Tools nutzen, um Aufgaben auszuführen wie das Durchsuchen von Tabellen, das Bearbeiten einer SQL- oder Python-Quelldatei, das Ausführen von Pipeline-Updates und das Lesen von Pipeline-Datensätzen.

Der Zugriff und die Aktionen von Genie Code werden durch die Berechtigungen des Nutzers gesteuert. Er kann nur auf Daten zugreifen, auf die der Nutzer Zugriff hat, und nur Operationen ausführen, für die der Nutzer Berechtigungen besitzt.

**Hinweis der Doku:** Wird der Agent-Modus in Genie Code aktiviert, passt Genie Code seine Fähigkeiten an die Funktionen an, die gerade in Databricks genutzt werden. Im Lakeflow Pipelines Editor fokussiert sich Genie Code beispielsweise auf Pipeline-Editing und Data-Engineering-Aufgaben. In Notebooks und im SQL-Editor unterstützt Genie Code Datenexploration und -analyse.

## <a id="voraussetzungen">2. Voraussetzungen</a>

Um Genie Code für Data Engineering zu nutzen, benötigt der Workspace Folgendes:

- Partner-powered-AI-Features aktiviert sowohl für den Account als auch für den Workspace.
- Der Workspace muss sich in einer unterstützten Region befinden. Genie Code ist ein "Designated Service", der Geos zur Verwaltung der Datenresidenz nutzt.

## <a id="nutzung">3. Genie Code für Pipeline-Entwicklung nutzen</a>

Um die agentischen Fähigkeiten von Genie Code für die Pipeline-Entwicklung zu nutzen:

1. Im Lakeflow Pipelines Editor wird das Genie-Code-Seitenpanel geöffnet, indem oben rechts im Workspace auf **Genie Code** geklickt wird.
2. Unten rechts wird **Agent** ausgewählt. Dies schaltet den Agent-Modus von Genie Code ein und ermöglicht die Nutzung der agentischen Data-Engineering-Fähigkeiten von Genie Code.
3. Ein Prompt wird für Genie Code eingegeben. Beispielsweise können Fragen zur Pipeline gestellt werden, etwa "describe this pipeline". Es kann auch darum gebeten werden, neue Datensätze hinzuzufügen, zum Beispiel: "create silver_sales_data in a new file that reads from bronze_sales_data and cleans the data and adds useful quality expectations."

   **Hinweis der Doku:** Genie Code respektiert die Unity-Catalog-Berechtigungen des Nutzers, sodass er nur auf die Daten und den Pipeline-Quellcode zugreifen kann, auf die der Nutzer Zugriff hat.
4. Während Genie Code seine Antwort generiert, pausiert er häufig, um Eingaben vom Nutzer einzuholen:
   - Bei komplexeren Aufgaben kann Genie Code einen Schritt-für-Schritt-Plan erstellen und klärende Fragen stellen. Diese Fragen sollten beantwortet werden, um dem Agenten zu helfen, seinen Plan zu verfeinern.
   - Wenn Genie Code Code ausführen oder eine Pipeline aktualisieren muss, fragt er vor der Ausführung um Genehmigung. Die Anfrage kann mit **Allow** oder **Decline** beantwortet werden. Auch **Allow in this thread** (bezogen auf den Genie-Code-Konversations-Thread) oder **Always allow** kann ausgewählt werden.

     **Wichtiger Hinweis der Doku:** Genie Code im Agent-Modus kann Code in der Pipeline generieren und ausführen. Obwohl Schutzmechanismen ("guardrails") vorhanden sind, um gefährliche Aktionen zu verhindern, besteht weiterhin ein Risiko. Er sollte nur mit vertrauenswürdigen Daten genutzt werden, und Code sollte vor der Ausführung überprüft werden.
   - Während Genie Code weiterarbeitet, kann eine Aufforderung erscheinen, **Continue** oder **Reject** auszuwählen. Die bisherige Arbeit sollte überprüft werden; anschließend wird **Continue** ausgewählt, um mit den nächsten Schritten fortzufahren, oder **Reject**, um dem Agenten mitzuteilen, etwas anderes zu versuchen.
   - Um Genie Code während der Arbeit zu stoppen, wird das rote Stop-Icon angeklickt.

Genie Code kann neue Dateien erstellen, Text, Queries und Code generieren, die Dateien oder Pipelines ausführen und auf die Output-Datensätze zugreifen, um die Ergebnisse zu interpretieren.

**Hinweis der Doku:** Damit Genie Code seine Arbeit fortsetzen und weitere Schritte unternehmen kann, muss der Nutzer auf dem aktuellen Tab bleiben, an dem der Agent arbeitet.

**Tipp der Doku:** Es lassen sich Instruktionen für Genie Code hinzufügen, die in den meisten Antworten genutzt werden. Bestehen beispielsweise Code-Konventionen oder bevorzugte Bibliotheken, können diese Richtlinien als Instruktionen für Genie Code hinzugefügt werden. Es lassen sich außerdem "Skills" erstellen, um Genie Code mit spezialisierten Fähigkeiten für domänenspezifische Aufgaben zu erweitern.

## <a id="faehigkeiten">4. Fähigkeiten im Agent-Modus</a>

Im Agent-Modus kann Genie Code bei den meisten Aufgaben der Pipeline-Entwicklung helfen. Zu den wichtigsten Fähigkeiten gehören:

- **Data discovery (Datenerkennung):** Genie Code kann Tabellen im Workspace durchsuchen, um die für eine Aufgabe benötigten Daten zu finden.
- **Pipeline code edits (Pipeline-Code-Bearbeitungen):** Genie Code kann mehrere Dateien gleichzeitig erstellen und bearbeiten. Er hält den Nutzer darüber auf dem Laufenden, welche Dateien geändert werden, und zeigt den Code-Diff in jeder Datei an, sodass die Änderungen einzeln oder alle zusammen am Ende überprüft werden können.
- **Pipeline execution (Pipeline-Ausführung):** Genie Code kann einzelne Dateien ausführen, die Pipeline im Dry-Run-Modus oder regulär ausführen oder einen vollständigen Refresh durchführen. Möchte Genie Code fortfahren, fragt er vorher um Bestätigung.
- **Understanding and improving pipeline behavior (Pipeline-Verhalten verstehen und verbessern):** Genie Code kann Datensätze und Pipeline-Outputs untersuchen, um zu verstehen, was eine Pipeline End-to-End tut und warum. Er kann beispielsweise Transformationen zusammenfassen, nachvollziehen, wie Daten in nachgelagerte Tabellen fließen, und unerwartete Änderungen bei Zeilenzahlen oder Schemata hervorheben. Wenn er potenzielle Datenqualitätsprobleme aufdeckt, kann Genie Code helfen, deren Ursache zu ergründen, und vorschlagen, wo und wie sie in der Pipeline behoben werden sollten.

Diese Fähigkeiten unterstützen gängige Anwendungsfälle wie:

- **Authoring a new pipeline (eine neue Pipeline verfassen):** Genie Code kann bei allen Schritten der Erstellung einer neuen Medallion-Architektur-Pipeline helfen, von der Datenaufnahme über die Standardisierung und Bereinigung der Daten bis zur Transformation und Analyse der Daten.
- **Explain a pipeline (eine Pipeline erklären):** Genie Code kann eine bestehende Pipeline analysieren und erklären, um schnell einen Überblick zu gewinnen.
- **Fix issues (Probleme beheben):** Bei Fehlern kann Genie Code helfen, die Probleme zu diagnostizieren und zu beheben, indem er iterativ mehrere Dateien durchgeht, bis das Problem gelöst ist.
- **Fix incremental refresh (inkrementellen Refresh reparieren):** Werden materialisierte Views in der Pipeline über die Full-Recompute-Strategie aktualisiert, kann Genie Code die Ursache anhand der Incrementalization Insights der Pipeline diagnostizieren, Query-Verbesserungen vorschlagen und anwenden, die sie besser für den inkrementellen Refresh geeignet machen, und harte Blocker markieren.

## <a id="migration">5. Migration von anderen ETL-Frameworks zu Lakeflow-Pipelines</a>

**Wichtiger Hinweis der Doku:** Dieses Feature befindet sich im **Beta**-Status.

Genie Code kann ein bestehendes Datentransformationsprojekt in eine Lakeflow-Pipeline migrieren. Der Nutzer verweist dabei auf das hochgeladene Projekt, und Genie Code plant und führt die Migration End-to-End aus. Diese Migrationsfähigkeit ist Teil von Lakebridge und ist auch über den Lakebridge-Switch-Transpiler verfügbar.

**Hinweis der Doku:** Die Migration unterstützt aktuell ausschließlich dbt- und Informatica-Projekte. Unterstützung für weitere Quellen ist geplant.

### Ein Projekt migrieren

1. **Das Projekt zu Databricks hochladen.** Dazu eine der folgenden Optionen nutzen:
   - **Catalog:** Ein Volume öffnen, dann **Upload to this Volume**.
   - **Workspace:** Ein Verzeichnis öffnen, dann das Kebab-Menü und **Import** anklicken.
2. **Eine leere Lakeflow-Pipeline erstellen.** Zu **Jobs & Pipelines** gehen und eine **ETL pipeline** erstellen.
3. **Genie Code bitten, das Projekt zu migrieren.** Genie Code öffnen und mit dem Pfad zum hochgeladenen Projekt promptn, zum Beispiel:

   ```
   Migrate the project at /Volumes/my_catalog/my_schema/my_volume/my_project
   ```

### Wie die Migration funktioniert

Nach dem Start der Migration generiert Genie Code einen Plan und führt ihn anschließend aus:

1. **Read the source (Quelle lesen):** Genie Code liest das Quellprojekt, um dessen Modelle, Transformationen und Abhängigkeiten zu verstehen.
2. **Gather inputs (Eingaben einholen):** Er pausiert, um nach erforderlichen Eingaben zu fragen, etwa ob SQL- oder Python-Pipeline-Quellcode generiert werden soll.
3. **Research and generate an intermediate representation (IR) (Zwischenrepräsentation erforschen und generieren):** Er analysiert das Projekt und erstellt eine Zwischenrepräsentation, die die Logik der Pipeline unabhängig vom Quell-Tool erfasst.
4. **Convert, validate, and repair (konvertieren, validieren und reparieren):** Er konvertiert die Zwischenrepräsentation in Pipeline-Quellcode, validiert das Ergebnis und iteriert in einer Reparaturschleife, bis die Pipeline korrekt ist.

**Hinweis der Doku:** Die migrierte Pipeline-Quelle sollte überprüft und die Pipeline ausgeführt werden, um zu bestätigen, dass die Ergebnisse mit dem ursprünglichen Projekt übereinstimmen, bevor sie in der Produktion genutzt wird.

## <a id="beispiele">6. Beispiel-Prompts</a>

Die Doku listet folgende Beispiel-Prompts zum Einstieg:

- "Build and run a medallion architecture pipeline for fraud detection using the table transactions and customers in my_catalog.my_schema."
- "Explain every step of this pipeline."
- "Fix the failure in this pipeline."

---

## <a id="quellen">7. Quellen</a>

Beide Fassungen der Seite wurden am 19.08.2026 per `WebFetch` abgerufen. Die AWS-Fassung lieferte zunächst zusammengefasste, aber inhaltlich mit der Azure-Fassung übereinstimmende Auszüge; der vollständige, wörtlich zitierbare Roh-Markdown-Text stammt aus dem Abruf der Azure/Microsoft-Learn-Spiegelseite. Beide Fassungen stimmten inhaltlich vollständig überein.

- Use Genie Code for pipeline development (AWS, URL-Pfad `de-agent`): https://docs.databricks.com/aws/en/ldp/de-agent
- Use Genie Code for pipeline development (Azure-Spiegelseite, für vollständigen Wortlaut genutzt): https://learn.microsoft.com/en-us/azure/databricks/ldp/de-agent

**Bilder:** Das animierte GIF "Use the Data Engineering Agent" wurde erfolgreich heruntergeladen und liegt im Unterordner `images/` neben dieser Datei:

- `images/assistant-de-agent.gif`

**Ungeklärt:** Die Seite verweist auf eine gesonderte Unterseite "Geo availability of Genie Code features" für Details zur Regionsverfügbarkeit sowie auf "Partner-powered AI features" für die genauen Aktivierungsschritte — beide Unterseiten wurden im Rahmen dieser Aufgabe nicht separat abgerufen, da sie außerhalb der drei zugewiesenen URLs liegen. Ebenso wurde die Seite "Convert SQL with the agentic code converter" (verlinkt als Abgrenzung zu diesem Feature) nicht separat verifiziert.
