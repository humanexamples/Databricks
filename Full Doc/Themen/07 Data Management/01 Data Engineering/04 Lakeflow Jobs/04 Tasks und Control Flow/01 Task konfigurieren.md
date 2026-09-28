# Tasks konfigurieren und bearbeiten

Tasks werden über die **Jobs & Pipelines**-Workspace-UI erstellt, konfiguriert und bearbeitet. Ein Job besteht aus einem oder mehreren Tasks; der erste Task entsteht beim Erstellen des Jobs (siehe `02 Job erstellen und konfigurieren/Job konfigurieren.md`).

Jeder Task hat eine zugehörige Compute-Ressource. Bei Serverless konfiguriert Databricks das Compute automatisch; sonst siehe `Compute fuer Jobs.md`.

Weitere Werkzeuge zur Task-Konfiguration: Jobs-REST-API, Databricks CLI, zeitgesteuerte Notebook-Jobs.

## Task erstellen/bearbeiten

1. **Jobs & Pipelines** in der Sidebar.
2. Optional Filter **Jobs**/**Owned by me**.
3. Job-Namen anklicken.
4. Tab **Tasks** — der Task-Graph erscheint.
5. Zum Bearbeiten: Task-Namen anklicken — die Konfiguration erscheint unterhalb des Graphen.
6. Zum Hinzufügen: bei leerem Job Buttons für zuletzt genutzte Task-Typen nutzen oder **Add another task type**; bei bestehenden Tasks **Add task** im Graphen.

## Task-Typen

Notebook, Visual Data Prep, Clean Room Notebook, Python Script, Python Wheel, SQL, Pipeline, Database Table Sync Pipeline, Ingestion Pipeline, SQL Alert (Public Preview), Dashboards, Power BI, dbt, dbt Platform (Public Preview), JAR, Spark Submit, Run Job, If/else, For each (Details in `05 Task-Typen/` und weiter unten in diesem Ordner).

## Task klonen

Kopiert alle Konfigurationen eines bestehenden Tasks inkl. vorgelagerter Abhängigkeiten: Task im Graphen wählen → Klon-Button → **Cloned task name** vergeben → **Clone**.

## Task deaktivieren

Überspringt den Task zur Laufzeit, ohne ihn zu entfernen — Konfiguration und Lauf-Historie bleiben erhalten. Typische Szenarien: vorübergehendes Ausschließen bei Debugging, Pausieren eines kaputten Tasks, während der Rest des Jobs weiterläuft, oder DAG/Historie erhalten, während über eine Entfernung entschieden wird.

Task im DAG wählen → Deaktivieren-Button. Erneutes Aktivieren analog. Für einen einmaligen Überspringen-Lauf ohne Job-Änderung stattdessen **Run now with different settings** nutzen (siehe `03 Trigger und Zeitplanung/Jetzt ausfuehren.md`). Details zu Downstream-Effekten: `Deaktivierte Tasks.md`.

## Task löschen

Task wählen → Papierkorb-Button → **Delete task**. Um Konfiguration/Historie zu erhalten, stattdessen deaktivieren statt löschen.

## Task-Pfad kopieren

Bei Typen wie Notebook-Tasks: Tab **Tasks** → Task wählen → Kopiersymbol neben dem Task-Pfad.

## Erweiterte Task-Einstellungen

**Retry-Policy:** Die Standardeinstellung hängt von der Job-Konfiguration ab — meist werden Tasks bei Fehlschlag standardmäßig **nicht** erneut versucht. Serverless Jobs optimieren Retries standardmäßig automatisch. Continuous Jobs nutzen Exponential-Backoff-Retries. Konfiguration über **Add** neben **Retries**; das Retry-Intervall wird in Millisekunden zwischen Fehlschlag-Start und nächstem Retry berechnet. Sind **Timeout** und **Retries** beide gesetzt, gilt der Timeout für jeden einzelnen Retry.

**Schwellenwerte für Laufdauer/Streaming-Backlog** (Streaming Observability: Public Preview): über **Metric thresholds** im Task-Panel. Bei **Run duration**: **Warning**-Feld = erwartete Fertigstellungszeit (löst Event aus, wenn überschritten), **Timeout**-Feld = maximale Zeit (Status „Timed Out" bei Überschreitung). Bei Streaming-Backlog-Metriken analog, metrikspezifisch je Streaming-Quelle.

## Quelle

- https://docs.databricks.com/aws/en/jobs/configure-task
