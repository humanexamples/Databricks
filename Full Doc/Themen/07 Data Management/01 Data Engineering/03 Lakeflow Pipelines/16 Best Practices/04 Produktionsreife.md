# Produktionsreife für Lakeflow Pipelines

Dieses Dokument fasst die Checkliste für Produktionsreife von Lakeflow-Pipelines zusammen, gegliedert in sechs Dimensionen: Datenqualität, Zuverlässigkeit, Observability, Deployment, Kosten und Governance.

## Abschnittsübersicht

1. [Definition von Produktionsreife](#definition)
2. [Datenqualität](#datenqualitaet)
3. [Zuverlässigkeit](#zuverlaessigkeit)
4. [Observability](#observability)
5. [Deployment und Change Management](#deployment)
6. [Compute und Kosten](#kosten)
7. [Governance](#governance)
8. [Quellen](#quellen)

---

## <a id="definition">1. Definition von Produktionsreife</a>

Produktionsreife ist laut Doku "the point where a pipeline can run unattended against real business data" — der Punkt, an dem eine Pipeline unbeaufsichtigt gegen echte Geschäftsdaten laufen kann, wobei Fehlschläge automatisch erkannt werden. Eine produktionsreife Pipeline läuft nach einem Zeitplan gegen echte Geschäftsdaten; die Reife wird anhand von sechs Dimensionen bewertet: Datenqualität, Zuverlässigkeit, Observability, Deployment, Kosten und Governance.

## <a id="datenqualitaet">2. Datenqualität</a>

- Jedes Dataset, das für schlechte Daten anfällig ist, benötigt mindestens eine definierte Expectation — nicht nur Annahmen im Docstring.
- Bewusste Auswahl zwischen den Modi `warn`, `drop` und `fail`: "fail for conditions that should stop the world (such as a broken primary key), drop for records you can safely discard (with a quarantine table capturing what was dropped), and warn only where you actively watch the trend."
- Der Data-Quality-Tab oder das Event-Log sollte regelmäßig eingesehen werden, um aktuelle Expectation-Erfolgsraten zu verstehen.

## <a id="zuverlaessigkeit">3. Zuverlässigkeit</a>

- Bewusste Wahl zwischen Triggered- und Continuous-Pipeline-Modus.
- Die Pipeline sollte über den Job-Scheduler bzw. einen Lakeflow Job geplant werden, statt manuell gestartet zu werden.
- Fehlschlag-Benachrichtigungen sollten konfiguriert sein (E-Mail, Webhook oder Event Hook).
- Die Wiederherstellung nach einem Streaming-Checkpoint-Fehlschlag sollte getestet sein.
- Die Pipeline sollte unter einem Service Principal laufen, nicht unter einer persönlichen Nutzeridentität.

## <a id="observability">4. Observability</a>

- Der Speicherort des Event-Logs sollte bekannt sein, mit mindestens einer bereits ausgeführten Abfrage.
- Verifikation der `system.lakeflow.pipelines`-Tabellen oder Erstellung eines Dashboards für abfragbare Pipeline-Gesundheit.
- Nachverfolgung von Trends bei der Update-Dauer.

## <a id="deployment">5. Deployment und Change Management</a>

- Die Pipeline sollte über ein Bundle definiert und deployt werden, um Code-Review und Versionskontrolle zu ermöglichen.
- Mindestens dev- und prod-Targets (idealerweise dev, staging und prod).
- Umgebungsspezifische Werte sollten über Konfiguration parametrisiert statt hartkodiert werden.

## <a id="kosten">6. Compute und Kosten</a>

- Explizite Wahl zwischen Serverless und Classic Compute (mit Dokumentation der Entscheidung, falls Classic gewählt wird).
- Enhanced Autoscaling sollte auf Classic-Compute-Clustern aktiviert sein.
- Regelmäßige Überprüfung von `system.billing.usage` zur Analyse des DBU-Verbrauchs.

## <a id="governance">7. Governance</a>

- Zieltabellen sollten in Unity Catalog liegen, mit bewusstem Layout.
- Least-Privilege-Zugriff: Der Service Principal darf nur die notwendigen Objekte lesen und schreiben.

---

## <a id="quellen">8. Quellen</a>

1. Production readiness for Lakeflow pipelines (AWS): https://docs.databricks.com/aws/en/ldp/best-practices/production-readiness
