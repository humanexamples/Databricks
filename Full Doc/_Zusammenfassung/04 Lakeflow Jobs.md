# 04 Lakeflow Jobs — Gesamtübersicht

Konsolidierte Übersicht aller 61 Original-Markdown-Dateien im Ordner `07 Data Management\01 Data Engineering\04 Lakeflow Jobs\` (7 Unterordner: Übersicht, Job erstellen und konfigurieren, Trigger und Zeitplanung, Tasks und Control Flow, Task-Typen, Berechtigungen und Monitoring, Parameter) mit **allen** enthaltenen Code-Beispielen und einer kurzen, einfachen Einführung pro Thema. Jede Originaldatei bleibt die primäre, ausführliche Quelle — dieses Dokument dient als kompakter Überblick plus vollständige Code-Referenz an einem Ort.

Lakeflow Jobs ist Databricks' Orchestrierungs-Werkzeug für beliebige Workloads (Notebooks, Skripte, SQL, Pipelines, dbt, JARs, ...) — früher als **Databricks Workflows** bekannt und seit der Lakeflow-GA (Juni 2025) Teil der vereinheitlichten Lakeflow-Plattform (zusammen mit Lakeflow Connect und Lakeflow Declarative Pipelines).

## Inhalt

1. Was sind Lakeflow Jobs?
2. Schnellstart: Erster Workflow mit zwei Notebooks
3. Job-Erstellung und -Verwaltung automatisieren (CLI, SDK, REST API)
4. Best Practices für Produktions-Jobs (Checkliste)
5. Jobs konfigurieren und bearbeiten
6. Tutorial: Wiederkehrenden Job mit Backfill-Unterstützung erstellen
7. Compute für Jobs konfigurieren
8. Classic Compute für Jobs
9. Serverless Compute für Jobs
10. Umgebungsvariablen für Serverless Jobs (Beta)
11. Git mit Lakeflow Jobs nutzen
12. Jobs mit vielen Tasks
13. Backfill-Jobs
14. Trigger-Typen im Überblick
15. Jobs zeitgesteuert ausführen (Scheduled Trigger)
16. Einen einzelnen Job-Lauf auslösen (Run Now)
17. Jobs kontinuierlich ausführen (Continuous Trigger)
18. Jobs bei neuen Dateien auslösen (File Arrival Trigger)
19. Jobs bei Tabellen-Updates auslösen (Table Update Trigger)
20. Jobs bei Modell-Updates auslösen (Model Update Trigger, Beta)
21. Tasks konfigurieren und bearbeiten
22. Kontrollfluss von Tasks steuern
23. Task-Abhängigkeiten konfigurieren (Run If)
24. If/else-Task: Verzweigungslogik
25. For-Each-Task: Task in einer Schleife ausführen
26. Lookup-Tabellen für große Parameter-Arrays bei For-Each-Tasks
27. Tutorial: Control-Tabelle für einen For-Each-Job nutzen (SQL-Lookup)
28. Tutorial: Mehrere Tabellen inkrementell mit For-Each und Watermarks kopieren
29. Run-Job-Task: andere Jobs auslösen
30. Modulares Job-Design (Master-Child-Pattern)
31. Deaktivierte Tasks in Lakeflow Jobs
32. Notebook-Task
33. Python-Script-Task
34. Python-Wheel-Task
35. Tutorial: Python-Wheel-Datei in Lakeflow Jobs nutzen
36. SQL-Task
37. Pipeline-Task
38. Dashboard-Task
39. SQL-Alert-Task
40. dbt-Task
41. dbt-Platform-Task (Public Preview)
42. dbt-Core-Transformationen in Lakeflow Jobs nutzen
43. JAR-Task
44. Eine Databricks-kompatible JAR erstellen
45. JARs auf Serverless Compute erstellen und ausführen (Tutorial)
46. Spark-Submit-Task: Deprecation und Migration
47. Spark Submit (Legacy, Deprecated, Entfernung Mitte 2026 geplant)
48. Power-BI-Task (Public Preview)
49. Clean-Room-Notebook-Task
50. Lakeflow Jobs mit Apache Airflow orchestrieren
51. Identitäten, Berechtigungen und Privilegien für Jobs
52. Lakeflow Jobs überwachen
53. Benachrichtigungen für Jobs
54. Job-Fehlschläge diagnostizieren und reparieren (Repair)
55. Job-Performance diagnostizieren
56. Jobs parametrisieren — Überblick
57. Job-Parameter konfigurieren
58. Task-Parameter konfigurieren
59. Parameterwerte in einem Task abrufen
60. Dynamische Wertreferenzen
61. Task Values: Informationen zwischen Tasks weitergeben
62. Weitere Airflow-Operatoren: SQL, COPY INTO und DLT-Pipeline-Trigger

---

## 1. Was sind Lakeflow Jobs?

**Einfach erklärt:** Lakeflow Jobs ist Databricks' Werkzeug zur Workflow-Automatisierung — es plant und orchestriert Datenverarbeitungsaufgaben wie ETL-Läufe, Notebook-Ausführungen oder ML-Pipelines. Ein Job besteht aus einem oder mehreren Tasks, die als gerichteter azyklischer Graph (DAG) mit Abhängigkeiten und bedingter Logik verknüpft sind. Ein Trigger (zeitgesteuert oder ereignisbasiert) löst die Ausführung aus.

**Drei Grundkonzepte:** Job (Koordinationsressource mit Triggern, Parametern, Benachrichtigungen, Git-Einstellungen), Task (konkrete Arbeitseinheit, z. B. Notebook/Pipeline/Skript) und Trigger (löst einen Lauf aus).

| Grenzwert | Wert |
|---|---|
| Gleichzeitige Task-Läufe pro Workspace | 2.000 |
| Erstellbare Jobs pro Stunde | 10.000 |
| Maximal gespeicherte Jobs pro Workspace | 12.000 |
| Maximale Tasks pro Job | 1.000 |
| Zeichenlimit für dynamische Job-Parameter | 10.000 |

Jobs lassen sich über die Databricks CLI, Declarative Automation Bundles, die VS-Code-Extension, SDKs, die Jobs-REST-API oder externe Tools wie Apache Airflow verwalten/orchestrieren.

Keine Code-Beispiele in dieser Datei.

---

## 2. Schnellstart: Erster Workflow mit zwei Notebooks

**Einfach erklärt:** Dieses Tutorial zeigt den einfachsten Weg zu einem lauffähigen Job: ein Notebook lädt Beispieldaten herunter, ein zweites filtert und zeigt sie an. Beide Notebooks werden als Tasks in einem Job verkettet, per "Run Now" gestartet und die Ergebnisse in der Run-Ansicht kontrolliert.

Voraussetzungen: Unity-Catalog-aktivierter Workspace (idealerweise mit Serverless Jobs), sowie `READ VOLUME`/`WRITE VOLUME` auf `my-volume`, `USE SCHEMA` auf `default`, `USE CATALOG` auf `main`.

**Notebook 1 — Daten laden:**

```python
import requests
response = requests.get('https://health.data.ny.gov/api/views/jxy9-yhdk/rows.csv')
csvfile = response.content.decode('utf-8')
dbutils.fs.put("/Volumes/main/default/my-volume/babynames.csv", csvfile, True)
```

**Notebook 2 — Daten filtern und anzeigen:**

```python
babynames = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load("/Volumes/main/default/my-volume/babynames.csv")
babynames.createOrReplaceTempView("babynames_table")
years = spark.sql("select distinct(Year) from babynames_table").toPandas()['Year'].tolist()
years.sort()
dbutils.widgets.dropdown("year", "2014", [str(x) for x in years])
display(babynames.filter(babynames.Year == dbutils.widgets.get("year")))
```

Ablauf: Job mit erstem Task (`retrieve-baby-names`, Typ Notebook) erstellen, zweiten Task (`filter-baby-names`) mit Parameter `year=2014` hinzufügen, per **Run Now** starten, Ergebnisse im Tab **Runs** prüfen und optional über **Run now with different settings** mit anderem Jahr (z. B. `2015`) erneut ausführen.

---

## 3. Job-Erstellung und -Verwaltung automatisieren (CLI, SDK, REST API)

**Einfach erklärt:** Jobs lassen sich nicht nur über die UI, sondern auch programmatisch mit der Databricks CLI, den Databricks SDKs oder der REST API erstellen, abfragen und löschen. Für CI/CD empfiehlt Databricks stattdessen Declarative Automation Bundles oder den Terraform Provider. Die CLI kapselt dabei direkt REST-API-Aufrufe (z. B. entspricht `databricks jobs get` dem Endpunkt `GET /api/2.2/jobs/get`).

| Werkzeug | Beschreibung |
|---|---|
| **Databricks CLI** | Kommandozeilen-Interface, das die REST API kapselt. Ideal für Einzelaufgaben, Experimente, Shell-Skripte. |
| **Databricks SDKs** | Entwicklungsbibliotheken für Python, Java, Go, R zum Erstellen eigener Workflows. |
| **Databricks REST API** | Direkter API-Zugriff, wenn keine passende SDK-Sprache verfügbar ist. |

**Job abrufen (CLI):**

```bash
databricks jobs get 478701692316314
```

Beispielhafte Antwort (Multi-Task-Job mit Abhängigkeiten, Retries, Notifications):

```json
{
  "created_time": 1730983530082,
  "creator_user_name": "someone@example.com",
  "job_id": 478701692316314,
  "run_as_user_name": "someone@example.com",
  "settings": {
    "email_notifications": {
      "no_alert_for_skipped_runs": false
    },
    "format": "MULTI_TASK",
    "max_concurrent_runs": 1,
    "name": "job_name",
    "tasks": [
      {
        "email_notifications": {},
        "notebook_task": {
          "notebook_path": "/Workspace/Users/someone@example.com/directory",
          "source": "WORKSPACE"
        },
        "run_if": "ALL_SUCCESS",
        "task_key": "success",
        "timeout_seconds": 0,
        "webhook_notifications": {}
      },
      {
        "depends_on": [
          { "task_key": "success" }
        ],
        "disable_auto_optimization": true,
        "email_notifications": {},
        "max_retries": 3,
        "min_retry_interval_millis": 300000,
        "notebook_task": {
          "notebook_path": "/Workspace/Users/someone@example.com/directory",
          "source": "WORKSPACE"
        },
        "retry_on_timeout": false,
        "run_if": "ALL_SUCCESS",
        "task_key": "fail",
        "timeout_seconds": 0,
        "webhook_notifications": {}
      }
    ],
    "timeout_seconds": 0,
    "webhook_notifications": {}
  }
}
```

**Job erstellen** — zunächst JSON in eine Datei speichern (auch über **View JSON** in der Job-UI abrufbar):

```json
{
  "name": "My hello notebook job",
  "tasks": [
    {
      "task_key": "my_hello_notebook_task",
      "notebook_task": {
        "notebook_path": "/Workspace/Users/someone@example.com/hello",
        "source": "WORKSPACE"
      }
    }
  ]
}
```

```bash
databricks jobs create --json @<file-path>
```

**Job ausführen — Zeitplan-Beispiel in der Job-Definition:**

```json
"schedule": {
  "quartz_cron_expression": "46 0 9 * * ?",
  "timezone_id": "America/Los_Angeles",
  "pause_status": "UNPAUSED"
},
"max_concurrent_runs": 1,
```

Alternativ: `databricks jobs run-now` (startet bestehenden Job) oder `databricks jobs submit` (führt eine Job-Definition einmalig aus, ohne sie zu speichern — erscheint nicht in der UI und wird bei Fehlschlag nicht automatisch für Serverless optimiert).

**Mit dem Python SDK** — bei Databricks Runtime 12.2 LTS oder darunter muss das SDK zunächst manuell installiert werden:

```python
%pip install --upgrade databricks-sdk==0.74.0
%restart_python
```

```python
from databricks.sdk.service.jobs import JobSettings as Job
from databricks.sdk import WorkspaceClient

job_name            = input("Provide a short name for the job, for example, my-job: ")
notebook_path       = input("Provide the workspace path of the notebook to run, for example, /Users/someone@example.com/my-notebook: ")
task_key            = input("Provide a unique key to apply to the job's tasks, for example, my-key: ")

test_sdk = Job.from_dict(
   {
       "name": job_name ,
       "tasks": [
           {
               "task_key": task_key,
               "notebook_task": {
                   "notebook_path": notebook_path,
                   "source": "WORKSPACE",
               },
           },
       ],
   })

w = WorkspaceClient()
j = w.jobs.create(**test_sdk.as_shallow_dict())
print(f"View the job at {w.config.host}/#job/{j.job_id}\n")
```

**Mit der REST API** — vorausgesetzt `DATABRICKS_HOST`/`DATABRICKS_TOKEN` sind gesetzt:

```bash
curl --request GET "https://${DATABRICKS_HOST}/api/2.2/jobs/get" \
     --header "Authorization: Bearer ${DATABRICKS_TOKEN}" \
     --data '{ "job": "11223344" }'
```

**Jobs als Code ansehen:** In der Job-UI über Kebab-Menü → **View as code** → Format **YAML** (für Bundles), **Python** (SDK- oder Bundles-Code) oder **JSON** (für CLI/SDK/REST API) wählen.

**Aufräumen:**

```bash
databricks jobs delete <job-id>
```

---

## 4. Best Practices für Produktions-Jobs (Checkliste)

**Einfach erklärt:** Diese Checkliste fasst zusammen, worauf beim Übergang eines Jobs von Entwicklung zu Produktion zu achten ist: richtige Compute-Wahl, modulare Orchestrierung, sowie Monitoring/Governance. Sie ist eine Bündelung von Punkten, die andernorts im Kurs bereits im Detail behandelt werden.

**Compute & Kostenoptimierung:** Job- oder Serverless-Compute statt All-Purpose/Interactive-Cluster in Produktion einsetzen; Photon aktivieren (bei Serverless standardmäßig an); Compute zwischen Tasks teilen, wo sinnvoll, um Start-Latenz zu reduzieren.

**Orchestrierung & Modularität:** Komplexe Pipelines in modulare Jobs zerlegen (Master-Child-Pattern über Run-Job-Tasks); Multi-Task-Jobs für parallele, skalierbare Ausführung; bedingte Logik (Run If, If/Else, For Each) für reale, verzweigte Anwendungsfälle; Task-Anzahl pro Job begrenzt halten (Hard Limit: 1.000 Tasks pro Job).

**Monitoring & Governance:** Service Principal statt persönlichem Account als Run-as-Identität; Benachrichtigungen für Fehlschläge, Verzögerungen und Abschlüsse konfigurieren; Repair & Run statt vollständigem Neustart nutzen (auf Idempotenz der Tasks achten); Tasks parametrisieren für Wiederverwendbarkeit über Umgebungen hinweg.

Keine Code-Beispiele in dieser Datei.

---

## 5. Jobs konfigurieren und bearbeiten

**Einfach erklärt:** Jeder Job braucht mindestens einen Task mit ausführbarer Logik, eine Compute-Ressource, einen Zeitplan oder eine manuelle Auslösung sowie einen eindeutigen Namen. Über die Jobs-&-Pipelines-UI lassen sich neue Jobs anlegen und bestehende Jobs (Zeitpläne, Parameter, Compute, Tags, Benachrichtigungen, Concurrency-Limits, Git-Einstellungen, Berechtigungen) bearbeiten, umbenennen, klonen oder löschen.

Job-Tags dienen als nicht-sensible Schlüssel-Wert-Labels zum Filtern/Monitoring und vererben sich an Job-Cluster — keine PII oder Passwörter in Tags speichern. Jobs können Quellcode direkt aus einem Remote-Git-Repository auschecken (inkl. Sparse Checkout für große Repositories). Für Laufdauer und Streaming-Backlog lassen sich Schwellenwerte definieren (Warnung bzw. "Timed Out"). Seit dem 15. April 2024 ist Job-Run-Queueing für über die UI erstellte Jobs standardmäßig aktiv (Läufe werden bis zu 48 Stunden in eine Warteschlange gestellt statt übersprungen zu werden). Der Standard für gleichzeitige Läufe ist **1**, einstellbar über **Edit concurrent runs**.

Keine Code-Beispiele in dieser Datei.

---

## 6. Tutorial: Wiederkehrenden Job mit Backfill-Unterstützung erstellen

**Einfach erklärt:** Dieses Tutorial zeigt, wie man eine parametrisierte SQL-Query (Kosten pro Databricks-Produkt aus System-Tabellen) als täglich laufenden Job einrichtet und anschließend historische Tage per Backfill nachträglich befüllt. Der Trick ist, den Zeitraum über Query-Parameter (`lookback_days`, `data_interval_end`) zu steuern, die der Job bei jedem Lauf bzw. Backfill-Lauf automatisch mit passenden Werten befüllt.

**Schritt 1 — Query erstellen** (`<catalog>`/`<schema>` ersetzen):

```sql
USE CATALOG <catalog>;
USE SCHEMA <schema>;

CREATE TABLE IF NOT EXISTS tutorial_databricks_product_spend (
  billing_origin_product STRING,
  usage_date DATE,
  total_dollar_cost DECIMAL(12, 2)
);

-- Process the last N days specified by :lookback_days ending on :data_interval_end
INSERT INTO TABLE tutorial_databricks_product_spend
  REPLACE WHERE
    usage_date >= date_add(:data_interval_end, - CAST(:lookback_days AS INT))
    AND usage_date < :data_interval_end
  SELECT
    usage.billing_origin_product,
    usage.usage_date,
    SUM(usage.usage_quantity * list_prices.pricing.effective_list.default) AS total_dollar_cost
  FROM
    system.billing.usage AS usage
      JOIN system.billing.list_prices AS list_prices
        ON usage.sku_name = list_prices.sku_name
        AND usage.usage_end_time >= list_prices.price_start_time
        AND (
          list_prices.price_end_time IS NULL
          OR usage.usage_end_time < list_prices.price_end_time
        )
  WHERE
    usage.usage_date >=
      date_add(:data_interval_end, -CAST(:lookback_days AS INT))
    AND usage.usage_date <
      :data_interval_end
  GROUP BY
    usage.billing_origin_product,
    usage.usage_date
```

Parameter (**Edit** → **Add parameter**):

| Name | Standardwert |
|---|---|
| `lookback_days` | `1` |
| `data_interval_end` | *(keiner — immer erforderlich)* |

**Schritt 2 — Job zum Zeitplanen der Query erstellen:** Notebook-Task anlegen, Parameter `lookback_days = 1` setzen, Parameter `data_interval_end` über `{{job.trigger.time.iso_date}}` aus der Liste parametrisierter Werte befüllen, dann unter **Schedules & Triggers** einen **Scheduled**-Trigger (täglich) hinzufügen. Über **Pause** lässt sich der Zeitplan konfiguriert lassen, ohne tägliche Kosten zu verursachen.

**Schritt 3 — Backfill für ältere Daten ausführen:** Über den Pfeil neben **Run now** → **Run backfill**, Zeitraum (z. B. 7 Tage zurück, `09/14/2025, 12:00 AM` bis `09/21/2025, 12:00 AM`) und Intervall (**Every 1 Day**) wählen. Job-Parameter prüfen: `data_interval_end = {{backfill.iso_datetime}}`, `lookback_days = 1`, dann **Run**.

---

## 7. Compute für Jobs konfigurieren

**Einfach erklärt:** Für Produktions-Jobs gibt es drei Compute-Optionen mit unterschiedlichen Kosten-/Latenz-Tradeoffs: Interactive/All-Purpose-Cluster (nur für Entwicklung, nicht für Produktion geeignet), klassische Job-Cluster (volle Infrastrukturkontrolle, aber Start-Latenz und Wartungsaufwand) und Serverless Compute (Standardempfehlung, automatische Optimierung, aber kein manuelles Tuning). Mehrere Tasks können sich dieselbe Compute-Ressource teilen, um Start-Latenz zu sparen — dabei bleibt das Compute zwischen Tasks im Leerlauf, und da alle geteilten Tasks auf derselben JVM laufen, teilen sie sich Scala-Singletons/Companion-Objects.

| Task-Typ | Empfohlenes Compute |
|---|---|
| Notebooks, Python-Skripte, Python-Wheels | Serverless Jobs |
| SQL-Tasks | Serverless SQL-Warehouse |
| Lakeflow Pipelines | Serverless Pipeline |
| JAR und Spark Submit | nur Classic Jobs Compute |

| Compute-Typ | Eignung | Nachteile |
|---|---|---|
| **Interactive/All-Purpose Cluster** | Ad-hoc-Analyse, Exploration, Entwicklung — **nicht für Produktion** | Teuer für Job-Läufe (läuft auch im Leerlauf weiter), begrenzte Skalierbarkeit, Verfügbarkeitsrisiko durch parallele Nutzung mehrerer Nutzer/Teams |
| **Job Cluster (Classic)** | Produktions-Jobs mit Bedarf an voller Infrastrukturkontrolle | Terminiert nach Job-Ende (günstiger als Interactive), aber Start-Latenz durch Cloud-Provider-Bereitstellung; höherer Wartungsaufwand |
| **Serverless Compute** | Standardempfehlung für die meisten Produktions-Workloads | Kein manuelles Infrastruktur-Tuning möglich; nicht für alle Task-Typen verfügbar |

Kontinuierliche Zeitplanung wird auf Serverless Compute nur mit begrenzten Structured-Streaming-Triggern wie `Trigger.AvailableNow` unterstützt — Standard- oder zeitintervallbasierte Trigger werden nicht unterstützt. Preislich bündelt Serverless Compute DBU-, Infrastruktur- und operationale Kosten in einem einzigen DBU-Satz, während Classic Compute diese getrennt abrechnet (DBUs an Databricks, Infrastruktur an den Cloud-Provider, operationale Kosten intern).

Keine Code-Beispiele in dieser Datei.

---

## 8. Classic Compute für Jobs

**Einfach erklärt:** Databricks empfiehlt Serverless Compute für die meisten Job-Workloads; Classic Compute bleibt für nicht-kompatible Workloads (z. B. JAR/Spark-Submit-Tasks). All-Purpose Compute wird für Jobs nicht empfohlen — andere Abrechnungssätze, anderes Auto-Termination-Verhalten und Ressourcenkonkurrenz zwischen Teams; Ausnahmen sind iterative Entwicklung und sehr kurzlebige, häufige Jobs (hier ist meist Serverless die bessere Alternative).

Für Jobs empfiehlt Databricks den **Standard Access Mode** (Standardeinstellung "Auto", sofern Cluster-Policies nichts anderes vorgeben); bei Kompatibilitätsfehlern und passenden Berechtigungen lässt sich auf **Dedicated Access Mode** wechseln. Workspace-Admins sollten job-spezifische Compute-Policies einrichten — Databricks stellt dafür eine Standard-Policy bereit.

Keine Code-Beispiele in dieser Datei.

---

## 9. Serverless Compute für Jobs

**Einfach erklärt:** Serverless Compute übernimmt die komplette Infrastrukturkonfiguration automatisch — Autoscaling und Photon sind standardmäßig aktiv, und Databricks optimiert Instanztypen und Speicher fortlaufend an die Workload. Voraussetzung ist ein Unity-Catalog-aktivierter Workspace mit Standard-Access-Mode-kompatiblen Workloads. Unterstützte Task-Typen: Notebook, Python-Skript, dbt, Python-Wheel, JAR — bei diesen ist Serverless beim Anlegen standardmäßig ausgewählt.

| Modus | Eigenschaft |
|---|---|
| **Standard Performance** | geringerer Compute-Einsatz, niedrigere Kosten, für Workloads mit tolerierbarer Startlatenz von 4–6 Minuten |
| **Performance Optimized** | schnellerer Start und schnellere Ausführung für zeitkritische Workloads |

Beide Modi nutzen dieselbe SKU mit unterschiedlichem DBU-Verbrauch. Weitere Konfigurationsoptionen: Spark-Konfigurationsparameter nur auf Session-Ebene setzbar, High Memory für Notebook-Tasks (Public Preview), Steuerung des Auto-Optimierungs-Retry-Verhaltens für nicht-idempotente Jobs, Kostenüberwachung über Billable-Usage-System-Tabellen.

Keine Code-Beispiele in dieser Datei.

---

## 10. Umgebungsvariablen für Serverless Jobs (Beta)

**Einfach erklärt:** Umgebungsvariablen erlauben es, Konfigurationswerte (z. B. Deployment-Einstellungen) an Task-Code weiterzugeben, ohne sie im Notebook-/Skript-Code hart zu kodieren. Einträge werden auf Job-Ebene mit eindeutigen Schlüsseln definiert; jeder Task wählt genau einen Eintrag über `environment_variables_key` — Einträge werden nie kombiniert und können nicht voneinander erben. Das Feature muss von einem Workspace-Admin über die Previews-Seite aktiviert werden, und Tasks müssen auf Serverless Environment Version 5+ laufen. UDFs können nicht auf Umgebungsvariablen zugreifen, da sie in der Spark-Ausführungslogik statt im Task-Prozess laufen.

| Konfiguration | Grenzwert |
|---|---|
| Umgebungsvariablen-Einträge pro Job | 10 |
| Länge des Eintragsschlüssels | 1–100 Zeichen, Muster `^[\w\-_]+$` |
| Inline-Variablen pro Eintrag | 100 |
| Länge des Inline-Variablennamens | 1–256 Zeichen, Muster `^[A-Za-z_][A-Za-z0-9_]*$` |
| Länge des Inline-Variablenwerts | 512 Zeichen |

Konfiguration über die API: Feld `environment_variables` bei `POST /api/2.2/jobs/create` (für Notebook- und JAR-Tasks). Variablen im Code lesen:

```python
os.environ["VARIABLE_NAME"]
```

```scala
sys.env("VARIABLE_NAME")
```

---

## 11. Git mit Lakeflow Jobs nutzen

**Einfach erklärt:** Jobs können Notebooks, Python-Skripte, SQL-Dateien und dbt-Projekte direkt aus einem Remote-Git-Repository ausführen. Alle Tasks eines Laufs nutzen denselben Commit-Snapshot. Git-Ordner (workspace-synchronisierte Ordner) eignen sich für schnelle Entwicklung, weil sie manuell synchronisiert werden müssen; für Staging/Produktion sind direkt referenzierte Remote-Git-Repositories besser, da sie bei jedem Lauf automatisch den neuesten Stand ziehen. Mit Remote-Git konfigurierte Tasks können nicht in Workspace-Dateien schreiben — temporäre Daten gehören auf ephemeren Driver-Speicher, persistente Daten in ein Volume oder eine Tabelle.

**Sparse Checkout** importiert bei großen Repositories nur bestimmte Verzeichnisse, um Checkout-Zeit zu sparen — falsch konfiguriert kann es jedoch Cache-Fragmentierung verursachen. Databricks cacht jeden Git-Checkout anhand von Workspace, Repository-URL, Commit-Hash und Fingerprint des Sparse-Checkout-Musters, mit bis zu einer Woche Gültigkeit. Sparse Checkout lohnt sich bei großen Repos (über ca. 2.500 Dateien) mit stabilem Zielbranch (selten aktualisiert); empfohlen werden Standardisierung (max. drei gemeinsame Checkout-Muster je Repository) und Micro-Targeting (wenige Dateien pro Muster, idealerweise unter 200).

**Importrate berechnen:**

```
Files Per Hour = Job Runs Per Hour × Cache Miss Rate × Files Imported Per Miss
```

Beispiel: 180 Läufe/Stunde × 10 % Miss-Rate × 6.000 Dateien/Miss = 108.000 Dateien/Stunde.

| Dateien importiert pro Stunde | Erwartete Auswirkung |
|---|---|
| unter 150.000 | Normalbetrieb |
| 150.000–300.000 | Verschlechterte Performance, ggf. Verzögerungen/Fehlschläge |
| über 300.000 | Jobs schließen nicht mehr zuverlässig ab |

**Best Practices:** Muster standardisieren (max. drei genehmigte Sparse-Muster je Repository, keine individuellen Team-Muster); Commit-Churn steuern (Jobs auf einen stabilen Release-Branch statt `main`/`master` zeigen lassen); Last steuern (große Binärdateien/generierte Artefakte aus der Versionskontrolle entfernen, Trigger-Frequenz redundanter Jobs senken).

**Beispiel — GitHub Actions für stündlichen Release-Cut:**

```yaml
name: Cut Hourly Release Candidate
on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:
jobs:
  update-branch:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout main branch
        uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 0
      - name: Update release-candidate branch
        run: |
          git push origin HEAD:release-candidate --force
```

**Sparse Checkout über die Jobs API aktivieren:**

```json
{
  "git_source": {
    "git_url": "https://github.com/example/my-repo",
    "git_provider": "gitHub",
    "git_branch": "release-candidate",
    "sparse_checkout": {
      "patterns": ["src/models", "src/utils"]
    }
  }
}
```

---

## 12. Jobs mit vielen Tasks

**Einfach erklärt:** Databricks erlaubt Jobs mit bis zu 1.000 Tasks, aber ab mehr als 100 Tasks können technische Probleme auftreten, die eine aktuelle SDK-/CLI-Version oder Anpassungen an der Cluster-Verteilung erfordern.

Beim Fehler "Only 100 tasks allowed" benötigen Ressourcen mit mehr als 100 Tasks API 2.2 oder höher:

| SDK/Sprache | Mindestversion |
|---|---|
| Go | 0.60.0 |
| Python | 0.45.0 |
| Java | 0.42.0 |
| Databricks CLI | 0.244.0 |

Beim Fehler "Only 150 execution contexts allowed" müssen Tasks auf mehrere Cluster verteilt werden. Bei großen Task-Mengen (z. B. 500 Tasks über 100 Job-Läufe) kann die Matrix-Ansicht der UI langsamer werden oder nur noch Kurzübersichten statt Einzeldetails zeigen — Filtern auf kürzere Zeiträume verbessert die Performance.

Keine Code-Beispiele in dieser Datei.

---

## 13. Backfill-Jobs

**Einfach erklärt:** Ein Backfill lässt einen bestehenden, zeitgesteuerten Job mit derselben Automatisierung nochmal für einen zurückliegenden Datumsbereich laufen — etwa weil ein Systemfehler Daten ausgelassen hat oder historische Daten von vor Systemstart nachgeladen werden sollen. Dazu wird der Job mehrfach mit unterschiedlichen Parametern ausgeführt, um frühere Läufe nachzubilden; der Job muss die übergebenen Parameter korrekt verarbeiten können.

Ein Backfill nutzt in der Regel dasselbe Zeitintervall wie der reguläre Job (damit bestehende Performance-Optimierungen erhalten bleiben) und teilt den Datumsbereich in mehrere, parallelisierbare Läufe auf. Beispiel: Fehler in der stündlichen Verarbeitung am 9. und 10. August → Backfill für diese zwei Tage mit 1-Stunden-Intervall löst bis zu 48 Läufe aus. Jobs haben standardmäßig ein Concurrency-Limit von 1 (einstellbar unter **Advanced settings**) — Jobs mit Pipeline-Tasks können jedoch nicht parallel laufen.

**Ablauf:** Job öffnen → Pfeil neben **Run now** → **Run backfill** → Datums-/Zeitbereich wählen → Zeitintervall anpassen (Standard aus Trigger/Zeitplan abgeleitet, z. B. `1 Hour`; über 100 generierte Läufe blockieren den Start und erfordern Aufteilung) → unter **Job parameters** bestehende Parameter überschreiben (z. B. `{{backfill.iso_datetime}}`) oder neue hinzufügen (z. B. `backfill = true`) → **Run**. Backfill-Läufe erscheinen in der Run-Liste mit dem Zusatz "Backfill".

**Einschränkungen:** Backfills laufen immer vollständig (keine Teilmenge von Tasks/Tabellen möglich). Bei Lakeflow-Pipeline-Tasks werden Pipeline-Tasks nicht parametrisiert und nicht parallel ausgeführt (Jobs mit Pipeline-Tasks laufen sequenziell) — empfohlen wird stattdessen die Append-Once-Funktionalität der Pipeline selbst.

Keine Code-Beispiele in dieser Datei.

---

## 14. Trigger-Typen im Überblick

**Einfach erklärt:** Lakeflow Jobs kennen sechs Arten, wie ein Lauf ausgelöst werden kann: zeitgesteuert, bei Tabellen-Updates, bei Datei-Ankunft, bei Modell-Updates, kontinuierlich oder komplett manuell/extern. Standardmäßig kann nur ein Lauf gleichzeitig aktiv sein — dieses Limit lässt sich in den Advanced Settings erhöhen.

| Trigger-Typ | Verhalten |
|---|---|
| **Scheduled** | Löst einen Job-Lauf zeitbasiert aus |
| **Table update** | Löst einen Lauf aus, wenn Quelltabellen aktualisiert werden |
| **File arrival** | Löst einen Lauf aus, wenn neue Dateien in einem überwachten Unity-Catalog-Speicherort eintreffen |
| **Model update** | Löst einen Lauf aus, wenn ein Unity-Catalog-Modell erstellt wird, eine Modellversion bereit ist, oder ein Modell-Alias gesetzt wird (Beta) |
| **Continuous** | Hält den Job dauerhaft am Laufen — ein neuer Lauf startet, sobald der vorherige abschließt oder fehlschlägt |
| **None (manuell)** | Läufe werden manuell über **Run now** oder programmatisch über andere Orchestrierungstools ausgelöst |

**Trigger konfigurieren:** Job öffnen → im **Job details**-Panel zu **Schedules & Triggers** scrollen → **Add trigger** → Typ wählen und Optionen konfigurieren → **Save**. Bestehende Trigger lassen sich über **Edit trigger**, **Pause** oder **Delete** verwalten; der Status kann direkt zwischen **Active** und **Paused** umgeschaltet werden.

Keine Code-Beispiele in dieser Datei.

---

## 15. Jobs zeitgesteuert ausführen (Scheduled Trigger)

**Einfach erklärt:** Der Scheduled-Trigger löst Jobs zeitbasiert aus, in zwei Varianten: "Simple" (periodische Ausführung nach Zeiteinheit und Intervall, z. B. alle 12 Stunden — der erste Startzeitpunkt wird vom Scheduler selbst gewählt) und "Advanced" (mehr Kontrolle über Periode, Uhrzeit, Zeitzone, mit optionaler Quartz-Cron-Syntax-Anzeige).

**Ablauf:** **Jobs & Pipelines** → Job öffnen → im Job-details-Panel **Add trigger** → **Trigger type: Scheduled** → **Schedule type: Simple** (Intervall + Zeiteinheit) oder **Advanced** (Periode, Startzeit, Zeitzone, optional **Show Cron Syntax**) → **Save**. Ein Notebook-Job lässt sich auch direkt aus der Notebook-UI heraus zeitplanen.

**Wichtige Hinweise:** Databricks erzwingt ein Mindestintervall von 10 Sekunden zwischen aufeinanderfolgenden, zeitplanausgelösten Läufen. Die Zeitzonenwahl beeinflusst das Verhalten bei der Sommerzeitumstellung — für stündliche, absolute Ausführungszeiten wird UTC empfohlen. Der Job-Scheduler ist nicht für niedrige Latenzanforderungen ausgelegt; Verzögerungen von bis zu mehreren Minuten sind möglich.

Keine Code-Beispiele in dieser Datei.

---

## 16. Einen einzelnen Job-Lauf auslösen (Run Now)

**Einfach erklärt:** Neben Triggern lässt sich jeder Job jederzeit manuell per "Run Now" sofort starten — praktisch auch als Testlauf. Über "Run now with different settings" lassen sich eine Teilmenge der Tasks aus-/abwählen, neue Job-Parameter als Key-Value-Paare eingeben und die Einstellung "Performance optimized" für Serverless-Workloads ändern.

**Teilmenge von Tasks samt Abhängigkeiten ausführen** (auch über REST API und CLI nutzbar):

| Syntax | Bedeutung |
|---|---|
| `my_task` | nur dieser Task |
| `+my_task` | Task plus vorgelagerte Abhängigkeiten |
| `my_task+` | Task plus nachgelagerte Abhängigkeiten |
| `+my_task+` | Task mit vor- und nachgelagerten Abhängigkeiten |

**Manuelle Trigger bei Continuous Jobs:** Bei kontinuierlichen Jobs ersetzt der Button **Restart run** den "Run now"-Button, um weiterhin nur einen gleichzeitigen Lauf zu gewährleisten. Beim Pausieren des Triggers erscheint wieder "Run now".

Keine Code-Beispiele in dieser Datei.

---

## 17. Jobs kontinuierlich ausführen (Continuous Trigger)

**Einfach erklärt:** Der Continuous-Modus ist Databricks' empfohlener Weg für dauerhaft laufende Streaming-Workloads — er ersetzt die frühere Empfehlung, unbegrenzte Retry-Policies mit maximal einem gleichzeitigen Lauf für Structured-Streaming-Tasks zu kombinieren. Ein neuer Lauf startet automatisch, sobald der vorherige abgeschlossen ist oder fehlschlägt.

Auf Serverless Compute funktionieren kontinuierliche Zeitpläne nur mit begrenzten Structured-Streaming-Triggern wie `Trigger.AvailableNow` — der Job-Scheduler startet Tasks nach Abschluss neu, Streaming-Checkpoints verhindern erneute Verarbeitung. Zeitbasierte Trigger wie `Trigger.ProcessingTime` und `Trigger.Continuous` werden auf Serverless **nicht** unterstützt.

**Konfiguration:** **Jobs & Pipelines** → Job öffnen → **Add trigger**, Typ **Continuous** → optional **Task retry mode** (**On failure** [Standard] oder **Never**) → **Save**. Steuerung über **Pause**/**Resume**.

**Wichtige Einschränkungen:** nur eine laufende Instanz pro Continuous Job; Verzögerung zwischen Läufen typischerweise unter 60 Sekunden; keine Task-Abhängigkeiten oder Retry-Policies auf Task-Ebene (stattdessen automatisches Job-Level-Retry mit Exponential Backoff, optionale Task-Level-Retries verfügbar); für Konfigurationsänderungen an pausierten Jobs **Run now** nutzen, sonst **Restart run**.

**Fehlerbehandlung:** Fehlschläge nutzen Exponential Backoff. Bei "On failure"-Retry-Modus werden fehlgeschlagene Tasks mit wachsenden Verzögerungen erneut versucht (maximal drei bei Ein-Task-Jobs). Nach Erreichen der maximalen Retries wird der Lauf abgebrochen und ein neuer gestartet; bei wiederholten Fehlschlägen verlängert das System die Wartezeit progressiv bis zu einem Schwellenwert. Nach erfolgreichem Abschluss (oder Ausbleiben weiterer Fehler) kehrt der Job in den gesunden Zustand zurück, und die Backoff-Sequenz wird zurückgesetzt.

Keine Code-Beispiele in dieser Datei.

---

## 18. Jobs bei neuen Dateien auslösen (File Arrival Trigger)

**Einfach erklärt:** File-Arrival-Trigger lösen einen Job aus, sobald neue Dateien in einem externen Speicherort (S3, Azure Storage, GCS) eintreffen — ideal für unregelmäßigen statt planbaren Dateneingang. Das System prüft ca. einmal pro Minute auf neue Dateien; überwacht werden können der Root eines Unity-Catalog External Location/Volume oder Unterpfade davon, rekursiv über alle Unterverzeichnisse. Keine Zusatzkosten über die üblichen Cloud-Gebühren für Dateiauflistung hinaus.

Beispiel gültiger Pfade für ein Volume `/Volumes/mycatalog/myschema/myvolume/`:

```
/Volumes/mycatalog/myschema/myvolume/
/Volumes/mycatalog/myschema/myvolume/mydirectory/
```

**Mit File Events** (empfohlen für optimale Performance): Databricks nutzt dann einen internen Dienst, der Ingestion-Metadaten über Cloud-Provider-Änderungsbenachrichtigungen verfolgt — bestehende Trigger profitieren innerhalb von Minuten, neue innerhalb von Sekunden.

**Voraussetzungen:** Unity Catalog aktiviert; Speicherort ist ein Volume oder eine Unity-Catalog-External-Location; `READ`-Berechtigung auf dem Speicherort und `CAN MANAGE` auf dem Job; empfohlen: External Locations für Managed File Events aktivieren (`MANAGE`-Privileg oder Eigentümerschaft erforderlich).

**Trigger hinzufügen:** **Jobs & Pipelines** → Job öffnen → **Add trigger** → Typ **File arrival** → Speicherort-URL eingeben → optional erweiterte Ratenbegrenzungs-Optionen → **Test connection** → **Save**.

**Lauffrequenz steuern:** **Minimum time between triggers (seconds)** (Cooldown, max. ein Lauf pro Zeitraum) und **Wait after last change (seconds)** (Debouncing, wartet bis für die angegebene Dauer keine neuen Dateien mehr eintreffen; jede neue Ankunft setzt den Timer zurück) — unabhängig oder kombiniert nutzbar. Beispiele: maximal alle 15 Minuten → `Minimum time between triggers: 900`; auf vollständigen Batch warten → `Wait after last change: 60`; beides kombiniert → `900` + `60`.

**Dateien mit Auto Loader verarbeiten — Beispiel 1 (in Delta-Tabelle laden):**

```python
file_location = "[REPLACE]" # dieselbe URL wie im File-Arrival-Trigger
checkpoint_location = "[REPLACE]" # separate URL außerhalb von file_location
sink_table = "[REPLACE]"

streamingQuery = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "json") \
  .option("cloudFiles.schemaLocation", checkpoint_location) \
  .option("cloudFiles.useManagedFileEvents","true") \
  .load(file_location) \
  .writeStream \
  .option("checkpointLocation", checkpoint_location) \
  .trigger(availableNow = True) \
  .toTable(sink_table)
```

**Beispiel 2 (benutzerdefinierte Verarbeitung mit `foreachBatch`):**

```python
file_location = "[REPLACE]"
checkpoint_location = "[REPLACE]"

def process_batch(batch_df, batch_id):
  file_url = batch_df.select("path").collect()[0].path
  # [REPLACE] eigene Verarbeitungslogik für neu eingetroffene Dateien

streamingQuery = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "binaryFile") \
  .option("cloudFiles.useManagedFileEvents","true") \
  .load(file_location) \
  .drop("content") \
  .writeStream \
  .foreachBatch(process_batch) \
  .option("checkpointLocation", checkpoint_location) \
  .start()
```

`foreachBatch` garantiert nur At-least-once-Verarbeitung.

**Einschränkungen — Allgemein:** Nur neue Dateien lösen Läufe aus (Überschreiben bestehender Dateien nicht); Pfade dürfen keine External Tables oder Managed Locations enthalten; keine Wildcards (`*`, `?`) in Pfaden.

**Mit File Events:** keine Mengenbegrenzung für Dateien; Trigger können bei sehr vielen irrelevanten Datei-Updates timeouten; Unterpfad-Trigger können bei häufigen Root-Level-Änderungen fehlerhaft reagieren (Workaround: eigenes Unity-Catalog-Volume direkt auf das Zielverzeichnis mappen); geänderte Dateien mit Metadaten außerhalb des Rolling-Retention-Zeitraums gelten als neue Ankünfte.

**Ohne File Events:** maximal 50 Jobs mit File-Arrival-Triggern pro Workspace; Speicherort auf 10.000 Dateien begrenzt (Unterpfad, nicht Root).

**Nicht existierende Pfade (S3, GCS):** Der Trigger wertet fehlerfrei aus, auch wenn der Pfad nicht (mehr) existiert — kein Fehlschlag, keine Fehlerbenachrichtigung, einfach kein Auslösen, bis Dateien hinzukommen.

---

## 19. Jobs bei Tabellen-Updates auslösen (Table Update Trigger)

**Einfach erklärt:** Table-Update-Trigger lösen einen Job automatisch aus, wenn sich überwachte Quelltabellen ändern — ganz ohne dauerhaft laufende Cluster oder manuelles Monitoring. Es können eine oder mehrere Tabellen überwacht werden, wahlweise mit Auslösung bei jedem Update oder erst, wenn alle überwachten Tabellen aktualisiert wurden. Unterstützt werden Unity-Catalog-Delta- und Iceberg-Managed-Tables, External Tables auf Delta-Basis, Materialized Views, Streaming Tables sowie UC-Views/Metric-Views, die von unterstützten Tabellen abhängen. Keine Zusatzkosten über die üblichen Cloud-Gebühren hinaus.

**Trigger hinzufügen:** **Jobs & Pipelines** → Job auswählen → **Schedules & Triggers** → **Add trigger** → Typ **Table update** → zu überwachende Tabellen angeben → bei mehreren Tabellen Auslöseverhalten (jede/alle) konfigurieren → optional **Minimum time between triggers (seconds)** und **Wait after last change (seconds)** → **Test trigger** → speichern. Sind beide erweiterten Optionen gesetzt, wartet der Trigger zuerst das Mindestintervall ab, danach die angegebene Zeit nach der letzten Änderung (Beispiel: 120 s Minimum + 60 s Wait-after-Change → Ausführung frühestens nach 120 Sekunden, selbst bei Updates innerhalb der ersten 60 Sekunden).

**OpenSharing und System-Tabellen (Beta):** Table-Update-Trigger können auch über OpenSharing geteilte Daten und System-Tabellen überwachen — nur Databricks-zu-Databricks-Sharing wird unterstützt, Betas müssen auf Recipient-/Provider-Seite aktiviert sein (bei System-Tabellen nur Recipient-seitig), der Trigger-Ersteller benötigt `SELECT` auf die geteilten Objekte/System-Tabellen.

**File-Events-Optimierung:** aktivierte File Events auf externen Speicherorten verbessern Performance/Skalierbarkeit deutlich; Tabellen im Metastore-Root-Speicher müssen zuvor in External Locations konvertiert werden.

**Job-Parameter:**

| Referenz | Bedeutung |
|---|---|
| `{{job.trigger.table_update.updated_tables}}` | JSON-Liste geänderter Tabellen seit dem letzten Lauf |
| `{{job.trigger.table_update.<catalog.schema.table>.commit_timestamp.iso_datetime}}` | jüngster Commit-Zeitstempel, der den Job ausgelöst hat |
| `{{job.trigger.table_update.<catalog.schema.table>.version}}` | jüngste Commit-Version, die den Job ausgelöst hat |

Benachrichtigungen (E-Mail oder System-Ziel) lassen sich konfigurieren, wenn die Trigger-Auswertung fehlschlägt.

**Einschränkungen:** maximal 10 Managed-/Delta-Tabellen pro Trigger; ohne File Events maximal 1.000 Jobs mit Table-Update-Triggern pro Workspace; maximal 1.000 OpenSharing-/System-Tabellen-Trigger pro Workspace; bei Unity-Catalog-View-Triggern werden Views mit `read_files`, Abhängigkeit von Nicht-UC-Tabellen oder Federated Tables nicht unterstützt, abhängige Tabellen zählen zum 10-Tabellen-Limit, maximal 10 abhängige Views pro überwachter View.

Keine Code-Beispiele in dieser Datei.

---

## 20. Jobs bei Modell-Updates auslösen (Model Update Trigger, Beta)

**Einfach erklärt:** Model-Update-Trigger lösen einen Job aus, wenn sich Modelle in Unity Catalog ändern — ganz ohne Cron-Zeitpläne oder dauerhafte Überwachungs-Cluster. Data Scientists können damit Validierungs-, Test- oder Promotion-Jobs automatisch auslösen, wenn Modellversionen bereit werden oder Aliase gesetzt werden; Administratoren können alle Modelle eines Metastores oder Schemas überwachen, um jede Neuerstellung zu auditieren.

**Scope:**

| Scope | Bedeutung |
|---|---|
| Model | ein einzelnes registriertes Modell |
| Schema | alle Modelle in einem Schema |
| Metastore | alle Modelle im Metastore (Metastore-Admin-Rechte erforderlich) |

**Bedingung:** "Model is created" (neues registriertes Modell im Scope), "Model version is ready" (neue Modellversion wird bereit), "Model alias is set" (angegebener Alias wird gesetzt, bis zu 10 Aliase pro Trigger).

**Batching:** Der Trigger pollt ca. einmal pro Minute; erkannte Änderungen werden pro Intervall gebündelt und als Parameter an den Job übergeben. Ein Batch darf das 10.000-Zeichen-Limit für Job-Parameterwerte nicht überschreiten (Richtwerte bei kurzen Namen: 212 Updates/Lauf bei "Model is created", 163 bei "Model version is ready", 117 bei "Model alias is set").

**Hoher Event-Durchsatz:** Treffen Updates schneller ein, als ein Lauf verarbeiten kann, und läuft der Trigger etwa eine Stunde durchgehend in jedem Poll-Intervall, schlägt er fehl und stoppt automatisch. Erholung: Update-Rate reduzieren (engerer Scope oder mehrere Trigger) oder Trigger pausieren/fortsetzen. Bei hohem Volumen empfohlen: Schema-/Model-Scope statt Metastore-Scope, Überwachung auf mehrere Trigger/Jobs aufteilen, ausgelöste Jobs schlank halten und For-Each-Tasks zur Verarbeitung nutzen.

**Voraussetzungen:** Unity Catalog aktiviert; `EXECUTE`-Privileg auf Ziel-Modell/-Schema; für Metastore-Scope Metastore-Admin mit `EXECUTE` auf allen aktuellen und künftigen Catalogs.

**Trigger hinzufügen:** **Jobs & Pipelines** → Job auswählen → **Add trigger** → Typ **Model update** → Scope und Ziel wählen → Bedingung wählen (ggf. bis zu 10 Aliase) → optional **Minimum time between triggers**/**Wait after last change** (Sekunden) → **Test trigger** → **Save**. Nach dem Speichern dauert die Initialisierung ca. eine Minute ("The trigger will be evaluated soon").

**Job-Parameter** — `{{job.trigger.model.updates}}` liefert eine JSON-Liste gebündelter Updates:

```json
[{ "full_name": "model.full.name1", "version": 123, "alias_name": "prod" }]
```

`full_name` ist immer gesetzt; `version` bei "Model version is ready" und "Model alias is set"; `alias_name` nur bei "Model alias is set".

**Beispiel — Verarbeitung im Notebook:**

```python
import json
json_list = dbutils.widgets.get("events")
data = json.loads(json_list)
for item in data:
    print(f"Full Name: {item['full_name']}, Version: {item.get('version')}, Alias Name: {item.get('alias_name')}")
```

**Mit einem For-Each-Task verarbeiten** — ein For-each-Task führt einen verschachtelten Task einmal je Listenelement aus (Input `{{job.trigger.model.updates}}`); jedes Update steht dem verschachtelten Task als Widget-Parameter zur Verfügung:

```python
full_name = dbutils.widgets.get("full_name")
version = dbutils.widgets.get("version")
alias_name = dbutils.widgets.get("alias_name")
print(f"Full Name: {full_name}, Version: {version}, Alias Name: {alias_name}")
```

**Über die Jobs API konfigurieren:**

```json
{
  "job_id": 574587036927544,
  "new_settings": {
    "trigger": {
      "pause_status": "UNPAUSED",
      "model": {
        "securable_name": "main.default",
        "condition": "MODEL_ALIAS_SET",
        "aliases": ["alias1", "alias2"],
        "min_time_between_triggers_seconds": 3600,
        "wait_after_last_change_seconds": 120
      }
    },
    "parameters": [
      {
        "default": "{{job.trigger.model.updates}}",
        "name": "events"
      }
    ]
  }
}
```

`securable_name` (Schema/Modell, leer = ganzer Metastore), `condition` (`MODEL_CREATED`, `MODEL_VERSION_READY`, `MODEL_ALIAS_SET`), `aliases` (nur für `MODEL_ALIAS_SET`).

**Einschränkungen:** maximal 100 Model-Update-Trigger pro Workspace; ein Job-Lauf trägt Updates bis zum 10.000-Zeichen-Limit (typischerweise 100+ Updates); maximal 10 Aliase pro Trigger; Trigger schlägt nach ca. einer Stunde durchgehenden Pollings ohne manuelle Erholung fehl; Metastore-Scope erfordert Metastore-Admin-Status und `EXECUTE` auf allen Catalogs.

**Model-Update-Trigger vs. Deployment Jobs:** Model-Update-Trigger eignen sich für Modellerstellung/Alias-Änderungen über einen breiteren Scope (Schema/Metastore) mit einem Trigger für viele Modelle. Deployment Jobs eignen sich für enge UI-Kopplung und Aktivitätsprotokolle zu Modellversion-Erstellung und Job-Lauf-Beziehungen.

---

## 21. Tasks konfigurieren und bearbeiten

**Einfach erklärt:** Ein Job besteht aus einem oder mehreren Tasks, die über die Jobs & Pipelines-UI angelegt und bearbeitet werden. Jeder Task hat eine eigene Compute-Ressource (bei Serverless automatisch konfiguriert) und lässt sich klonen, deaktivieren oder löschen, ohne dass Konfiguration und Lauf-Historie verloren gehen. Zusätzliche Werkzeuge sind die Jobs-REST-API, die Databricks CLI und zeitgesteuerte Notebook-Jobs.

**Task erstellen/bearbeiten:**
1. **Jobs & Pipelines** in der Sidebar.
2. Optional Filter **Jobs**/**Owned by me**.
3. Job-Namen anklicken.
4. Tab **Tasks** — der Task-Graph erscheint.
5. Zum Bearbeiten: Task-Namen anklicken — die Konfiguration erscheint unterhalb des Graphen.
6. Zum Hinzufügen: bei leerem Job Buttons für zuletzt genutzte Task-Typen nutzen oder **Add another task type**; bei bestehenden Tasks **Add task** im Graphen.

**Verfügbare Task-Typen:** Notebook, Visual Data Prep, Clean Room Notebook, Python Script, Python Wheel, SQL, Pipeline, Database Table Sync Pipeline, Ingestion Pipeline, SQL Alert (Public Preview), Dashboards, Power BI, dbt, dbt Platform (Public Preview), JAR, Spark Submit, Run Job, If/else, For each.

**Task klonen:** Kopiert alle Konfigurationen eines bestehenden Tasks inkl. vorgelagerter Abhängigkeiten — Task im Graphen wählen → Klon-Button → **Cloned task name** vergeben → **Clone**.

**Task deaktivieren:** Überspringt den Task zur Laufzeit, ohne ihn zu entfernen — Konfiguration und Lauf-Historie bleiben erhalten. Typische Szenarien: vorübergehendes Ausschließen beim Debugging, Pausieren eines kaputten Tasks während der Rest des Jobs weiterläuft, oder DAG/Historie erhalten, während über eine Entfernung entschieden wird. Task im DAG wählen → Deaktivieren-Button; für einen einmaligen Überspringen-Lauf ohne Job-Änderung stattdessen **Run now with different settings** nutzen.

**Task löschen:** Task wählen → Papierkorb-Button → **Delete task**. Um Konfiguration/Historie zu erhalten, stattdessen deaktivieren statt löschen.

**Task-Pfad kopieren:** Bei Typen wie Notebook-Tasks: Tab **Tasks** → Task wählen → Kopiersymbol neben dem Task-Pfad.

**Erweiterte Task-Einstellungen:**
- **Retry-Policy:** Standard hängt von der Job-Konfiguration ab — meist werden Tasks bei Fehlschlag standardmäßig nicht erneut versucht. Serverless Jobs optimieren Retries automatisch, Continuous Jobs nutzen Exponential-Backoff-Retries. Sind Timeout und Retries beide gesetzt, gilt der Timeout für jeden einzelnen Retry.
- **Metric thresholds** (Streaming Observability, Public Preview): **Warning**-Feld = erwartete Fertigstellungszeit, **Timeout**-Feld = maximale Zeit (Status „Timed Out" bei Überschreitung).

Keine Code-Beispiele in dieser Datei.

---

## 22. Kontrollfluss von Tasks steuern

**Einfach erklärt:** Jobs mit mehreren Tasks brauchen eine Ausführungsreihenfolge — sequenziell oder parallel, gesteuert über Abhängigkeiten. Lakeflow Jobs bietet dafür mehrere Mechanismen: Retries, Run-if-Bedingungen, If/else-Verzweigung, For-each-Schleifen und deaktivierte Tasks.

**Mechanismen im Überblick:**
- **Retries:** legen fest, wie oft ein fehlgeschlagener Task erneut ausgeführt wird. Viele Fehler sind transient und lösen sich durch einen Neustart. Manche Features (z. B. Schema Evolution mit Structured Streaming) setzen Retries voraus, um die Umgebung zurückzusetzen. Continuous-Jobs nutzen automatisch Exponential-Backoff-Retries.
- **Run-if-Bedingungen:** der Task-Typ **Run if** erlaubt bedingte Ausführung nachgelagerter Tasks anhand des Ergebnisses vorgelagerter Tasks — unterstützte Bedingungen: All succeeded, At least one succeeded, None failed, All done, At least one failed, All failed.
- **If/else-Tasks:** bedingte Verzweigung anhand berechneter Werte (Task Values, Job-Parameter, dynamische Werte). Unterstützte Operatoren: `==`, `!=`, `>`, `>=`, `<`, `<=`.
- **For-each-Tasks:** führt einen anderen Task iterativ mit unterschiedlichen Parametern je Durchlauf aus — benötigt einen `For each`-Task plus einen verschachtelten Standard-Task.
- **Deaktivierte Tasks:** übersprungen zur Laufzeit, Konfiguration/Historie bleiben erhalten; Lakeflow Jobs wertet die Run-if-Bedingungen nachgelagerter Tasks entsprechend aus.

**Gängige Workload-Muster:** Drei wiederkehrende DAG-Formen (keine offiziellen Databricks-Begriffe):
- **Sequence:** lineare Kette von Tasks, typisch für Transformationsschritte oder die Medallion-Architektur (Bronze → Silver → Gold).
- **Funnel:** mehrere Quell-Tasks laufen in einen gemeinsamen nachgelagerten Task zusammen (Fan-in) — typisch beim Einsammeln mehrerer Datenquellen.
- **Fan-out:** ein einzelner Quell-Task verzweigt sich sternförmig in mehrere nachgelagerte Tasks — typisch bei der Verteilung einer Quelle an mehrere Ziele.

Keine Code-Beispiele in dieser Datei.

---

## 23. Task-Abhängigkeiten konfigurieren (Run If)

**Einfach erklärt:** Das Feld **Run if dependencies** steuert, ob ein Task abhängig vom Ergebnis (Erfolg, Fehlschlag, Abschluss) seiner vorgelagerten Tasks läuft. Abhängigkeiten erscheinen als Linien im Job-DAG; Databricks führt vorgelagerte Tasks vor nachgelagerten aus und parallelisiert, wo möglich. Das Feld **Depends on** erscheint nur bei Jobs mit mehreren Tasks.

**Verwandte Kontrollfluss-Features:**
- **If/else-Condition-Task:** führt Job-Abschnitte anhand eines Boolean-Ausdrucks aus.
- **For-each-Task:** fügt Schleifenlogik über Eingabe-Arrays hinzu.
- **Run-Job-Task:** löst andere Workspace-Jobs aus.

**Run-if-Bedingung hinzufügen:**
1. Task auswählen.
2. Im Feld **Depends on** Tasks per X entfernen oder neue aus dem Dropdown wählen.
3. Bedingung unter **Run if dependencies** wählen.
4. **Save task**.

**Bedingungsoptionen:**

| Bedingung | Verhalten |
|---|---|
| **All succeeded** (Standard) | Alle Abhängigkeiten liefen und waren erfolgreich; sonst „Upstream failed" |
| **At least one succeeded** | Mindestens eine Abhängigkeit erfolgreich; sonst „Upstream failed" |
| **None failed** | Keine fehlgeschlagene Abhängigkeit, mindestens eine lief; sonst „Upstream failed" |
| **All done** | Läuft, sobald alle Abhängigkeiten abgeschlossen sind — unabhängig vom Status |
| **At least one failed** | Mindestens eine Abhängigkeit fehlgeschlagen; sonst „Excluded" |
| **All failed** | Alle Abhängigkeiten fehlgeschlagen; sonst „Excluded" |

**Wichtige Hinweise:**
- „Excluded" markierte vorgelagerte Tasks zählen in Auswertungen als erfolgreich.
- „Upstream failed" oder „Upstream canceled" zählen als fehlgeschlagen.
- Tasks mit nicht erfüllter Bedingung werden als „Excluded" markiert und übersprungen.
- Ausschluss kaskadiert entlang linearer Abhängigkeitsketten.
- Task-Abbruch propagiert nachgelagert an Fehlerbehandlungs-Tasks.
- Deaktivierte vorgelagerte Tasks lösen die Auswertung der Run-if-Bedingungen nachgelagerter Tasks entsprechend aus.

**Beispiel: mehrere Abhängigkeiten (Fan-in).** Der Code nutzt `DAJobConfig`, eine kurseigene SDK-Hilfsklasse der Databricks-Academy-Trainingsumgebung. Das ist **keine öffentliche Databricks-API**. Er zeigt aber ein reales Muster: Ein Task (`customers_sales_summary`) startet erst, wenn **beide** vorgelagerten Tasks (`ingesting_customers` und `ingesting_sales`) abgeschlossen sind. Das ist ein Fan-in über das `depends_on`-Feld mit mehreren Einträgen:

```python
job_tasks = [
        {
            'task_name': 'ingesting_orders',
            'file_path': '/Task Files/Lesson 04 Files/4.1 - Creating orders table',
            'depends_on': None
        },
        {
            'task_name': 'ingesting_sales',
            'file_path': '/Task Files/Lesson 04 Files/4.2 - Creating sales table',
            'depends_on': None
        },
        {
            'task_name': 'ingesting_customers',
            'file_path': '/Task Files/Lesson 07 Files/7.1 - Creating customers table',
            'depends_on': None
        }
        ,{
            'task_name': 'customers_sales_summary',
            'file_path': '/Task Files/Lesson 09 Files/9.1 - Joining Customers and Sales Table',
            'depends_on': [
                        {'task_key':'ingesting_customers'},
                        {'task_key': 'ingesting_sales'}
                        ]
        }
        ,{
            'task_name' : 'customers_orders_report',
            'file_path': '/Task Files/Lesson 09 Files/9.2 - Joining Customers and Orders Table',
            'depends_on': None
        }
    ]

myjob = DAJobConfig(job_name=f"Demo_09_Retail_Job_{DA.schema_name}",
                    job_tasks=job_tasks,
                    job_parameters=[
                        {'name':'catalog', 'default':'dbacademy'},
                        {'name':'schema', 'default':f'{DA.schema_name}'}
                    ])
```

In der realen Jobs-UI/-API entspricht das genau dem Feld **Depends on** mit mehreren gewählten Tasks — Standardbedingung `All succeeded` bedeutet hier: `customers_sales_summary` läuft erst, wenn sowohl `ingesting_customers` als auch `ingesting_sales` erfolgreich abgeschlossen sind.

---

## 24. If/else-Task: Verzweigungslogik

**Einfach erklärt:** Der If/else-Condition-Task ermöglicht Boolean-Bedingungslogik in Task-Graphen über einen Operator und ein Operandenpaar. Operanden können den Job-/Task-Zustand über konfigurierte oder dynamische Parameter und Task Values referenzieren — so lässt sich der Job-DAG anhand eines berechneten Werts in zwei Zweige aufteilen.

**Beispiel:** Ein Task `process_records` führt einen Zähler ungültiger Datensätze `bad_records` als Task Value. Ein If/else-Task mit dem Ausdruck `{{tasks.process_records.values.bad_records}} > 0` verzweigt die Verarbeitung, wenn ungültige Datensätze auftreten. Nach dem Lauf lassen sich Ergebnis und Auswertungsdetails in den Job-Run-Details der UI einsehen.

**Wichtige Hinweise zur Wertauswertung:**
- `==` und `!=` vergleichen als **String** (`12.0 == 12` ist `false`).
- `>`, `>=`, `<`, `<=` vergleichen **numerisch** (`12.0 >= 12` ist `true`).
- Nur numerische, String- und Boolean-Werte sind bei Task-Value-Referenzen erlaubt; andere Typen werden zu Strings serialisiert.

**If/else-Task konfigurieren:**
1. Plus-Icon → **Add task**.
2. Task-Namen eingeben.
3. Typ **If/else condition** wählen.
4. Ersten Operanden im Condition-Feld eingeben — möglich sind:
   - Job-Parameter: `{{job.parameters.<name>}}`
   - Task-Parameter
   - Task Value: `{{tasks.<task_name>.values.<value_name>}}`
5. Boolean-Operator wählen.
6. Vergleichswert im zweiten Condition-Feld eingeben.
7. Optional Retries, Laufdauer-/Streaming-Backlog-Schwellen oder Benachrichtigungen konfigurieren.
8. **Save task**.

**Abhängigkeiten vom If/else-Ergebnis konfigurieren:**
1. If/else-Task im Task-Graphen wählen.
2. Plus-Icon → **Add task**.
3. **Depends on** ist standardmäßig `<task-name> (true)`.
4. Für den False-Zweig `<task-name> (false)` wählen.

Mehrere Tasks lassen sich seriell oder parallel je nach If/else-Ergebnis konfigurieren; für zusätzliche Fehlerbehandlung eignet sich „Run if dependencies".

**Einschränkung:** Ein If/else-Task schlägt fehl, wenn der vorgelagerte Task, der seinen Bedingungswert liefert, deaktiviert ist.

Keine Code-Beispiele in dieser Datei.

---

## 25. For-Each-Task: Task in einer Schleife ausführen

**Einfach erklärt:** Der For-each-Task führt einen verschachtelten Task wiederholt in einer Schleife aus, mit unterschiedlichen Parametern je Durchlauf — nützlich, um gleiche Transformationen auf mehrere Datasets anzuwenden. Er besteht aus zwei Komponenten: dem For-each-Task selbst und einem verschachtelten Task (muss ein normaler Lakeflow-Task-Typ sein, kein weiterer For-each-Task).

**Einrichtung:**
1. **Add task** → Typ **For each**.
2. Iterationswerte im **Inputs**-Feld als JSON-Array definieren.
3. Optional Concurrency-Limit setzen (Standard: 1).
4. Verschachtelten Task konfigurieren, der pro Iteration läuft.
5. Übergebene Parameter mit `{{input}}` bzw. `{{input.<key>}}` referenzieren.

**Parameterquellen für Inputs:**

| Quelle | Grenze |
|---|---|
| Direktes JSON-Array | max. 5.000 Zeichen |
| Task-Value-Referenz `{{tasks.<task_name>.values.<value_name>}}` | max. 48 KB |
| Job-Parameter `{{job.parameters.<name>}}` | max. 10.000 Zeichen |

**Einschränkung:** Bei größeren Datenmengen als den Zeichengrenzen: Lookup-Tabellen verwenden statt der Werte direkt.

Keine Code-Beispiele in dieser Datei.

---

## 26. Lookup-Tabellen für große Parameter-Arrays bei For-Each-Tasks

**Einfach erklärt:** Da Parameter-Arrays auf 5.000 Zeichen (bzw. 48 KB bei Task-Value-Referenzen) begrenzt sind, lassen sich umfangreiche Daten nicht direkt an einen For-each-Task übergeben. Der empfohlene Ansatz: Task-Daten als JSON speichern und nur einen kompakten Lookup-Key als Task-Input übergeben — der verschachtelte Task lädt sich die passende Konfiguration darüber selbst.

**Beispiel-Workflow:** Eine JSON-Konfigurationsdatei enthält Schritte mit zugehörigen Parametern, organisiert nach Keys. Der For-each-Task iteriert über diese Keys und übergibt sie an verschachtelte Tasks, die daraus die passenden Konfigurationsdetails abrufen.

**Konfigurationsdatei** (`/Workspace/Users/<user>/copy-filtered-table-config.json`):

```json
{
  "steps": [
    {
      "key": "table_1",
      "args": {
        "catalog": "my-catalog",
        "schema": "my-schema",
        "source_table": "raw_data_table_1",
        "destination_table": "filtered_table_1",
        "filter_column": "col_a",
        "filter_value": "value_1"
      }
    },
    {
      "key": "table_2",
      "args": {
        "catalog": "my-catalog",
        "schema": "my-schema",
        "source_table": "raw_data_table_2",
        "destination_table": "filtered_table_2",
        "filter_column": "col_b",
        "filter_value": "value_2"
      }
    },
    {
      "key": "table_3",
      "args": {
        "catalog": "my-catalog",
        "schema": "my-schema",
        "source_table": "raw_data_table_3",
        "destination_table": "filtered_table_3",
        "filter_column": "col_c",
        "filter_value": "value_3"
      }
    }
  ]
}
```

Der For-each-Task erhält als Input nur die Keys: `["table_1","table_2","table_3"]` — weit unter dem 5.000-Zeichen-Limit. Da die Schritte keine Abhängigkeiten haben, lässt sich die Concurrency über 1 setzen.

Der verschachtelte Task erhält den Key als Parameter `key` = `{{input}}` und lädt darüber die passende Konfiguration:

```python
# copy-filtered-table (iteratable task code to read a table, filter by a value, and write as a new table)
from pyspark.sql.functions import expr
from types import SimpleNamespace
import json

dbutils.widgets.text("key", "table_1", "key")

config_path = "/Workspace/Users/<user>/copy-filtered-table-config.json"
with open(config_path, "r") as file:
    config = json.loads(file.read())

key = dbutils.widgets.get("key")
current_step = next((step for step in config['steps'] if step['key'] == key), None)
if current_step is None:
    raise ValueError(f"Could not find step '{key}' in the configuration")
args = SimpleNamespace(**current_step["args"])

df = spark.read.table(f"{args.catalog}.{args.schema}.{args.source_table}") \
          .filter(expr(f"{args.filter_column} like '%{args.filter_value}%'"))

df.write.mode("overwrite").saveAsTable(f"{args.catalog}.{args.schema}.{args.destination_table}")
```

---

## 27. Tutorial: Control-Tabelle für einen For-Each-Job nutzen (SQL-Lookup)

**Einfach erklärt:** Statt eine Liste (Märkte, Quelltabellen, Kunden, Datumspartitionen) im Job-Code fest zu hinterlegen, wird sie in einer Control-Tabelle gespeichert, die der Job zur Laufzeit liest — die Daten, nicht der Code, bestimmen, was verarbeitet wird. Ein SQL-Task liest die Control-Tabelle, ein For-each-Task führt eine Analyse einmal je Zeile aus.

Beispielszenario: eine Ferienimmobilien-Plattform (Wanderbricks-Beispieldatensatz) führt dieselbe Preisanalyse für jedes Objektsegment (`Ski Resort`, `Urban Year-Round`, …) aus. Eine Control-Tabelle listet die Segmente.

**Ablauf:**

| Task | Typ | Aufgabe |
|---|---|---|
| `read_segments` | SQL | liest die Control-Tabelle, erfasst die Zeilen als JSON-Array |
| `process_segments` | For each | iteriert über das Zeilen-Array, startet den verschachtelten Task je Zeile |
| `run_segment_analysis` | Notebook oder SQL (verschachtelt) | läuft einmal je Zeile, analysiert ein Segment |

Die SQL-Task-Ausgabe (JSON-Array von Zeilenobjekten) fließt über `{{tasks.read_segments.output.rows}}` in das **Inputs**-Feld des For-each-Tasks; dieser übergibt Zeilenfelder als `{{input.property_type}}` und `{{input.min_price}}` an den verschachtelten Task.

**Voraussetzungen:** Workspace mit Recht, Jobs/Notebooks zu erstellen; Recht, Tabellen/Schemas in Unity Catalog zu erstellen; SQL-Warehouse für SQL-Tasks; Zugriff auf den `samples`-Catalog (`samples.wanderbricks.properties`).

**Schritt 1: Control-Tabelle erstellen**

```sql
USE CATALOG <catalog-name>;
CREATE SCHEMA IF NOT EXISTS config;
CREATE OR REPLACE TABLE config.property_segments AS
SELECT * FROM VALUES
  ('Urban Year-Round', 150),
  ('Summer Getaway', 200),
  ('Ski Resort', 250)
AS t(property_type, min_price);
```

**Schritt 2: Analyselogik schreiben.** Notebook-Variante (für prozeduralen Code, mehrere Sprachen, Bibliotheken):

```python
dbutils.widgets.text("property_type", "Ski Resort", "Property type")
dbutils.widgets.text("min_price", "250", "Minimum price")

property_type = dbutils.widgets.get("property_type")
min_price = dbutils.widgets.get("min_price")

result = spark.sql(
    """
    SELECT :property_type AS property_type,
           COUNT(*) AS property_count,
           ROUND(AVG(base_price), 2) AS avg_price
    FROM samples.wanderbricks.properties
    WHERE property_type = :property_type
      AND base_price >= :min_price
    """,
    args={"property_type": property_type, "min_price": min_price},
)
display(result)
```

**Hinweis:** `dbutils.widgets.text()` vor `dbutils.widgets.get()` aufrufen — sonst `InputWidgetNotDefined`-Fehler außerhalb eines Jobs.

SQL-Variante (für eine einzelne deklarative Query):

```sql
SELECT :property_type AS property_type,
       COUNT(*) AS property_count,
       ROUND(AVG(base_price), 2) AS avg_price
FROM samples.wanderbricks.properties
WHERE property_type = :property_type
  AND base_price >= :min_price;
```

SQL-Tasks nutzen `:param_name`-Syntax; anders als Notebook-Widgets unterstützen SQL-Named-Parameters keine Standardwerte.

**Schritt 3: Lookup-Query erstellen**

```sql
SELECT property_type, min_price FROM <catalog-name>.config.property_segments;
```

Als Query `read_segments` speichern.

**Schritt 4: Job erstellen und konfigurieren.** SQL-Lookup-Task: Kachel **SQL query** → Task-Name `read_segments` → Query `read_segments` auswählen → SQL-Warehouse setzen → **Create task**.

Die Ausgabe wird als JSON-Array in `tasks.read_segments.output.rows` erfasst:

```json
[
  { "property_type": "Urban Year-Round", "min_price": 150 },
  { "property_type": "Summer Getaway", "min_price": 200 },
  { "property_type": "Ski Resort", "min_price": 250 }
]
```

For-each-Task: **Add task** → **For each** → Task-Name `process_segments` → **Depends on** = `read_segments` → **Inputs** = `{{tasks.read_segments.output.rows}}` → **Concurrency** = `2` → verschachtelten Task konfigurieren (Notebook oder SQL aus Schritt 2), Parameter `property_type` = `{{input.property_type}}`, `min_price` = `{{input.min_price}}`.

**Schritt 5: Job ausführen und prüfen.** **Run now** → Tab **Runs** → Knoten `process_segments` aufklappen — zeigt eine Zeile je Segment mit Status, Startzeit, Dauer. Einzelne fehlgeschlagene Iterationen lassen sich isoliert erneut ausführen.

**Muster erweitern.** Neues Segment hinzufügen — ohne Job-/Notebook-Änderung:

```sql
INSERT INTO <catalog-name>.config.property_segments VALUES ('Historical Place', 100);
```

Weitere Anwendungsfälle: Pro-Kunde-Verarbeitung, Tabellen-Ingestion, Backfill-Verarbeitung nach Datumspartition, Feature-Flag-gesteuerte Ausführung.

Um eine Zeile zu deaktivieren, ohne sie zu löschen: eigene Spalte (z. B. `active`) ergänzen und in der Lookup-Query filtern:

```sql
ALTER TABLE <catalog-name>.config.property_segments ADD COLUMN active BOOLEAN;
UPDATE <catalog-name>.config.property_segments SET active = TRUE;
```

```sql
SELECT property_type, min_price FROM <catalog-name>.config.property_segments WHERE active = TRUE;
```

---

## 28. Tutorial: Mehrere Tabellen inkrementell mit For-Each und Watermarks kopieren

**Einfach erklärt:** Ein metadatengetriebener Job kopiert mehrere Quelltabellen inkrementell nach Unity Catalog. Watermarks (die zuletzt verarbeitete Zeile je Tabelle) sorgen dafür, dass bei Folgeläufen nur neue Daten kopiert werden — vollständiges Kopieren bei jedem Lauf wäre langsam und teuer.

**Architektur:**

| Task | Typ | Aufgabe |
|---|---|---|
| `read_watermarks` | SQL | fragt eine Control-Tabelle mit Quelltabellen-Metadaten ab |
| `copy_tables` | For each | iteriert über die Ergebnisse, verarbeitet Tabellen parallel |
| `copy_incremental` | verschachteltes Notebook | führt den Datentransfer aus und schreibt den Watermark fort |

**Schritte:**
1. **Control-Tabelle einrichten:** `config.watermarks` mit Quell-/Ziel-Tabellen-Mapping, Watermark-Spalte und letztem verarbeiteten Zeitstempel. Anfangswert `1970-01-01` löst beim ersten Lauf einen vollständigen Load aus.
2. **Notebook-Logik:** filtert Quellzeilen, deren Watermark-Spalte über dem gespeicherten Schwellenwert liegt, hängt neue Daten an die Zieltabelle an, aktualisiert den Watermark auf den maximal kopierten Wert.
3. **Job konfigurieren:** SQL-Task-Ausgabe fließt über `{{tasks.read_watermarks.output.rows}}` in den For-each-Task; einzelne Zeilenfelder werden über `{{input.source_table}}` u. Ä. an das verschachtelte Notebook übergeben.
4. **Ausführen:** Job starten, Iterationen beobachten, Watermark-Fortschritt über die Control-Tabelle prüfen.

**Erweiterungen:** Neue Tabellen durch Einfügen von Control-Tabellen-Zeilen hinzufügen; Verarbeitung über eine `active`-Flag-Spalte pausieren; Watermarks zurücksetzen, um bestimmte Datumsbereiche erneut zu befüllen (Backfill).

Keine Code-Beispiele in dieser Datei (rein beschreibender Aufbau, keine konkreten Codeblöcke im Original).

---

## 29. Run-Job-Task: andere Jobs auslösen

**Einfach erklärt:** Der Run-Job-Task löst einen anderen, im Workspace konfigurierten Job aus — damit lassen sich Jobs aus anderen Jobs heraus starten und so modulare Workflows bauen. Zirkuläre Abhängigkeiten (Job A löst Job B aus, Job B löst Job A aus, direkt oder indirekt) sowie mehr als drei verschachtelte Run-Job-Tasks werden nicht unterstützt — Databricks kann das Deployment solcher Muster in künftigen Releases blockieren.

**Konfiguration:**
1. Tab **Tasks** → **Add task**.
2. Task-Namen eingeben.
3. Typ **Run Job**.
4. Job aus dem Dropdown wählen (durchsuchbar).
5. Optional Job-Parameter zum Überschreiben der Standardwerte des Ziel-Jobs setzen.
6. Optional Retries, Laufdauer-/Streaming-Backlog-Schwellen oder Benachrichtigungen unter Advanced Task Settings konfigurieren.
7. **Save task**.

Für Bearbeiten, Klonen, Deaktivieren oder Löschen siehe den Abschnitt „Tasks konfigurieren und bearbeiten".

Keine Code-Beispiele in dieser Datei.

---

## 30. Modulares Job-Design (Master-Child-Pattern)

**Einfach erklärt:** Ein einzelner, monolithischer Job mit sehr vielen Tasks wird mit wachsender Größe schwer wartbar — Änderungen erfordern Verständnis des gesamten DAGs, Teams stoßen sich gegenseitig bei parallelen Änderungen, und ein Fehler in einem Teilbereich erschwert den Überblick. Modulare Orchestrierung verwandelt einen monolithischen Workflow in wartbare, wiederverwendbare Komponenten über das Master-Child-Pattern.

**Dekompositionsstrategie:** Komplexe DAGs werden nach fachlichen Einheiten (Business-Units) zerlegt, nicht nach technischen Komponenten. Jedes Modul sollte eine in sich geschlossene Geschäftsfunktion abbilden, die unabhängig entwickelt, getestet und deployt werden kann — z. B. ein eigener Job pro Fachbereich oder Datendomäne statt ein Job pro technischem Schritt (Extract/Transform/Load quer über alle Domänen).

**Master-Child-Pattern:** Ein Master-Job orchestriert mehrere Child-Jobs über Run-Job-Tasks — er ruft die Child-Jobs auf und koordiniert deren Reihenfolge/Abhängigkeiten, während die eigentliche fachliche Logik in den Child-Jobs steckt. Das ergibt eine klare Trennung von Koordination (Master) und Ausführung (Child), bei gleichzeitig erhaltener Gesamt-Workflow-Steuerung.

**Vorteile:**
- **Maintainability:** Kleinere Jobs sind leichter zu verstehen, zu ändern und zu debuggen als ein großer monolithischer Job.
- **Reusability:** Child-Jobs lassen sich in mehreren Master-Workflows wiederverwenden.
- **Team-Collaboration:** Unterschiedliche Teams können unterschiedliche Module eigenständig verantworten und trotzdem am Gesamt-Workflow mitwirken.
- **Unabhängiges Testen:** Einzelne Module lassen sich isoliert testen — das verbessert die Qualität und senkt das Deployment-Risiko.

Der 1.000-Task-Limit pro Job ist ein weiterer praktischer Grund, große Workflows über das Master-Child-Pattern statt als einzelnen Riesen-Job zu bauen.

**Beispiel:** Im Bonus-Lab „Modular Orchestration" wird ein Master-Job namens `Lab_15<Schema-Name>` gebaut, der zwei Zweige kombiniert:
- Ein direkter Notebook-Task (`creating_high_risk_borrower_gold_table`) innerhalb des Master-Jobs selbst, abhängig von zwei vorgelagerten Tasks.
- Ein Run-Job-Task (`creating_low_risk_borrower_gold_table`), der einen separaten, eigenständigen Job namens `Lab_15_Run_Job` als Child-Job aufruft — ebenfalls abhängig von vorgelagerten Tasks im Master-Job, mit „Run if dependencies: All Succeeded".

Damit kombiniert der Master-Job Inline-Tasks für einfache Schritte mit ausgelagerten Child-Jobs für Teile, die eigenständig wiederverwendbar oder von einem anderen Team gepflegt werden sollen.

Keine Code-Beispiele in dieser Datei.

---

## 31. Deaktivierte Tasks in Lakeflow Jobs

**Einfach erklärt:** Ein deaktivierter Task wird zur Laufzeit übersprungen, ohne aus dem Job entfernt zu werden — Konfiguration und Lauf-Historie bleiben erhalten, sodass er später ohne Neuaufbau reaktiviert werden kann. Bei jedem Lauf wertet Lakeflow Jobs die Run-if-Bedingung jedes nachgelagerten Tasks gegen seine vorgelagerten Tasks aus, um zu entscheiden, ob er läuft, übersprungen oder deaktiviert wird.

Deaktivierte Tasks schließen mit dem Terminierungscode `Disabled` ab. Kann die Run-if-Bedingung eines nachgelagerten Tasks wegen deaktivierter Elternteile nicht erfüllt werden, markiert Lakeflow Jobs auch ihn für diesen Lauf als deaktiviert — sichtbar über ein Icon oben rechts im DAG.

**Verhalten nachgelagerter Tasks je Run-if-Bedingung:**

| Run-if-Bedingung | Verhalten bei deaktiviertem Elternteil | Beispiel |
|---|---|---|
| **All succeeded** (Standard) | Läuft nicht — ein deaktivierter Elternteil erfüllt „succeeded" nicht | `A (disabled) → B`: B läuft nicht |
| **At least one succeeded** | Läuft, wenn mindestens ein anderer Elternteil erfolgreich war | `A (disabled)` + `C (succeeded) → B`: B läuft |
| **None failed** | Läuft, wenn mindestens ein Elternteil ohne Fehlschlag abgeschlossen wurde | `A (disabled)` + `C (skipped) → B`: B läuft |
| **All done** | Läuft normal — ein deaktivierter Elternteil gilt als abgeschlossen | `A (disabled) → B`: B läuft |
| **At least one failed** | Läuft, wenn mindestens ein anderer Elternteil fehlschlug — ein deaktivierter Elternteil zählt nicht als Fehlschlag | `A (disabled)` + `C (failed) → B`: B läuft |
| **All failed** | Läuft nicht — ein deaktivierter Elternteil gilt nicht als Fehlschlag | `A (disabled) → B`: B läuft nicht |

**Hinweis:** Nur explizit deaktivierte Tasks tragen `disabled: true` in der Job-Definition. Die Deaktivierung nachgelagerter Tasks wird zur Lauf-Erstellungszeit ermittelt, nicht in den Job-Einstellungen gespeichert.

**Task deaktivieren über API/Bundle:** `disabled: true` auf dem Task setzen (Jobs REST API, CLI, SDK oder Declarative Automation Bundles):

```json
{
  "tasks": [
    {
      "task_key": "load_raw_data",
      "disabled": true,
      "notebook_task": {
        "notebook_path": "/Shared/etl/load_raw_data"
      }
    }
  ]
}
```

`jobs/get` und `jobs/list` liefern `disabled: true` nur für explizit deaktivierte Tasks — zur Laufzeit dynamisch deaktivierte Tasks erscheinen nicht in den gespeicherten Job-Einstellungen.

**Bei Repairs und Partial Runs:**
- **Repairs:** Lakeflow Jobs nutzt den Lauf-Status jedes Tasks zur Bestimmung, was repariert wird — nicht den Deaktivierungsstatus. Um einen deaktivierten Task im Rahmen eines Repairs zu erzwingen, in `rerun_tasks` der Repair-Anfrage aufnehmen.
- **Partial Runs:** Deaktivierte Tasks sind standardmäßig nicht vorausgewählt, lassen sich aber für einen einmaligen Lauf gezielt auswählen, ohne sie in den Job-Einstellungen zu reaktivieren. Bei `+`-Modifikatoren im `only`-Feld werden deaktivierte Tasks **nicht** automatisch mit eingeschlossen — sie müssen explizit hinzugefügt werden.

**Einschränkungen:**
- Ein If/else-Task schlägt fehl, wenn der vorgelagerte Task, der seinen Bedingungswert liefert, deaktiviert ist.
- Ein For-each-Task schlägt fehl, wenn der vorgelagerte Task, der seine Eingabewerte liefert, deaktiviert ist.
- Nur nutzerseitig deaktivierte Tasks erscheinen als `disabled: true` — die DAG-Ansicht in der Jobs-UI zeigt, welche nachgelagerten Tasks vor einem Lauf betroffen wären.

---

## 32. Notebook-Task

**Einfach erklärt:** Notebooks lassen sich direkt als Task in Lakeflow Jobs bereitstellen. Das Notebook muss an einem für den konfigurierenden Nutzer zugänglichen Ort liegen (Workspace oder Remote-Git-Repository).

**Konfiguration:**
1. Tab **Tasks** → **Add task**.
2. Task-Namen eingeben.
3. Typ **Notebook** wählen.

**Quellort:**
- **Workspace:** Pfad-Feld anklicken → **Select Notebook**-Dialog → Notebook wählen. Unterstützt Notebooks in Databricks-Git-Ordnern (Databricks empfiehlt jedoch Git-Provider-Optionen für die Versionierung zeitgesteuerter Assets).
- **Git Provider:** für Notebooks in Remote-Git-Repositories. Nur ein Remote-Repository über alle Job-Tasks hinweg nutzbar. Relative Pfade ohne führendes `/` oder `./` (z. B. `etl/bronze/ingest.py`).

**Wichtig:** Von Lakeflow Jobs aus Remote-Git-Repositories heraus ausgeführte Notebooks sind ephemer und eignen sich nicht zuverlässig zum Tracking von MLflow-Runs, -Experimenten oder -Modellen.

**Compute und Bibliotheken:** SQL-Warehouses eignen sich nur als Compute für reine SQL-Notebooks mit SQL als Standardsprache. Bei Serverless Compute werden Bibliotheken direkt im Notebook installiert; sonst über die UI (bestehende Bibliothek wählen oder neue hochladen).

**Parameter:** Optionale Task-Parameter als Key-Value-Paare, zugänglich über `dbutils.widgets`.

**Visual Data Prep:** Erstellt Notebook-Tasks aus `.designer.ipynb`-Dateien, die mit Lakeflow Designer gebaut wurden.

**Einschränkung:** Die gesamte Zellen-Ausgabe eines Notebooks ist auf **30 MB** begrenzt, einzelne Zellen-Ausgaben auf **8 MB**.

Keine Code-Beispiele in dieser Datei.

---

## 33. Python-Script-Task

**Einfach erklärt:** Der Python-Script-Task führt eine Python-Datei innerhalb eines Jobs aus. Databricks empfiehlt Workspace-Dateien für Python-Skripte, unterstützt aber auch DBFS/S3 und Git-Provider als Quelle.

**Konfiguration:**
1. Tab **Tasks** → **Add task**.
2. Task-Namen eingeben.
3. Typ **Python script**.

**Quellorte:**
- **Workspace:** Datei über Dialog auswählen; unterstützt Skripte in Databricks-Git-Ordnern.
- **DBFS/S3:** für Skripte in Volumes, Cloud-Speicher oder DBFS-Root, z. B. `dbfs:/path/to/script.py` oder `s3://bucket-name/path/to/script.py`.
- **Git Provider:** relativer Pfad, ohne führendes `/` oder `./`.

**Compute und Bibliotheken:** Passenden Compute-Cluster wählen. Bei Serverless: Environment und Bibliotheken konfigurieren. Sonst: abhängige Bibliotheken über die UI hinzufügen.

**Abschluss:** Optional Parameter als CLI-Argumente konfigurieren; optional erweiterte Task-Einstellungen (Retries, Benachrichtigungen); **Save task**.

Keine Code-Beispiele in dieser Datei.

---

## 34. Python-Wheel-Task

**Einfach erklärt:** Der Python-Wheel-Task führt paketierten Python-Code über eine Python-Wheel-Datei aus. Das Wheel muss an einem kompatiblen Ort hochgeladen sein; Paketname und Entry Point aus `setup.py` müssen bekannt sein.

**Konfiguration:**
1. Task hinzufügen, Namen vergeben.
2. Typ **Python wheel**.
3. **Package name** aus `setup.py` eingeben.
4. **Entry point**-Funktion aus dem `entry_points`-Dictionary angeben.
5. Passendes Compute wählen/konfigurieren.
6. Bei Serverless: Environment und Bibliotheken konfigurieren; sonst: Wheel-Dateien hochladen/auswählen.
7. Optional Parameter als positionale oder Keyword-Argumente konfigurieren.
8. Optional erweiterte Einstellungen (Retries, Benachrichtigungen).
9. Task speichern.

**Hinweis:** Die Jobs-UI zeigt Optionen dynamisch je nach anderen konfigurierten Einstellungen an. Wheel-Dateien müssen an einem von der Compute-Konfiguration unterstützten Ort liegen.

Keine Code-Beispiele in dieser Datei.

---

## 35. Tutorial: Python-Wheel-Datei in Lakeflow Jobs nutzen

**Einfach erklärt:** Dieses Tutorial zeigt Schritt für Schritt, wie man eine eigene Python-Wheel-Datei erstellt (Code, Metadaten, `setup.py` mit Entry Point) und diese anschließend als Python-Wheel-Task in einem Job ausführt.

**Voraussetzungen:** Python 3, Pakete `wheel` und `setuptools`:

```bash
pip install wheel setuptools
```

**Schritt 1: Lokales Verzeichnis anlegen.** Z. B. `databricks_wheel_test`.

**Schritt 2: Beispiel-Python-Skript erstellen.** Speichern unter `my_test_code/__main__.py`:

```python
"""The entry point of the Python Wheel"""
import sys

def main():
  # This method will print the provided arguments
  print('Hello from my func')
  print('Got arguments:')
  print(sys.argv)

if __name__ == '__main__':
  main()
```

**Schritt 3: Metadaten-Datei erstellen.** Speichern unter `my_test_code/__init__.py`:

```python
__version__ = "0.0.1"
__author__ = "Databricks"
```

**Schritt 4: Python-Wheel-Datei erstellen.** `setup.py` im Root-Verzeichnis. **Hinweis:** Der Teil vor `=` in `entry_points` (hier `run`) ist der Name des Entry Points, der bei der Konfiguration des Python-Wheel-Tasks verwendet wird.

```python
from setuptools import setup, find_packages
import my_test_code

setup(
  name='my_test_package',
  version=my_test_code.__version__,
  author=my_test_code.__author__,
  url='https://databricks.com',
  author_email='john.doe@databricks.com',
  description='my test wheel',
  packages=find_packages(include=['my_test_code']),
  entry_points={
    'group_1': 'run=my_test_code.__main__:main'
  },
  install_requires=[
    'setuptools'
  ]
)
```

Paketieren:

```bash
python3 setup.py bdist_wheel
```

Erzeugt `dist/my_test_package-0.0.1-py3.none-any.whl`.

**Schritt 5: Job erstellen.**
1. **Jobs & Pipelines** → **Create** → **Job**.
2. Kachel **Python wheel** (ggf. über **Add another task type** suchen).
3. Job optional umbenennen.
4. Task-Namen vergeben.
5. Typ **Python wheel**.
6. **Package name**: `my_test_package`.
7. **Entry point**: `run`.
8. **Compute**: bestehenden Job-Cluster wählen oder **Add new job cluster**.
9. Wheel-Datei angeben: unter **Environment and Libraries** → Stift neben **Default** → **Add dependency** → Ordner-Icon → Wheel-Datei per Drag & Drop → **Confirm**.
10. Unter **Parameters**: **Positional arguments** (JSON-Array, z. B. `["first argument","first value","second argument","second value"]`) oder **Keyword arguments** (Key/Value über **Add**).
11. **Save task**.

**Schritt 6: Job ausführen.** **Run Now** → Tab **Runs** → Link in Spalte **Start time** → Ausgabe im **Output**-Panel prüfen, inkl. übergebener Argumente.

---

## 36. SQL-Task

**Einfach erklärt:** Der SQL-Task konfiguriert eine SQL-Query, einen SQL-Alert oder eine SQL-Datei als Job-Task. Er benötigt Databricks SQL und ein Serverless- oder Pro-SQL-Warehouse; das SQL-Asset muss an einem für den konfigurierenden Nutzer zugänglichen Ort liegen.

**Konfiguration:**
1. Tab **Tasks** → Typ **SQL** wählen.
2. Im SQL-Task-Dropdown den Typ wählen:

| Typ | Beschreibung |
|---|---|
| **Query** | eine SQL-Query gegen das angegebene Warehouse ausführen |
| **Alert** | einen SQL-Alert über das angegebene Warehouse auswerten; optional Subscriber für Benachrichtigungen |
| **File** | eine `.sql`-Datei ausführen (mehrere per `;` getrennte Statements möglich) — Quelle **Workspace** oder **Git provider** (relativer Pfad ohne führendes `/` oder `./`, z. B. `etl/bronze/ingest.sql`) |

3. Optional Parameter als Key-Value-Paare.
4. Optional Retries, Laufdauer oder Benachrichtigungen.
5. **Save task**.

Keine Code-Beispiele in dieser Datei.

---

## 37. Pipeline-Task

**Einfach erklärt:** Lakeflow Jobs definiert Beziehungen zwischen Tasks prozedural; Lakeflow Pipelines definieren Beziehungen zwischen Datasets und Transformationen deklarativ. Eine Pipeline lässt sich als Task in einem Job zeitplanen — über Jobs-UI, Lakeflow-Pipelines-UI oder SQL. Ein Pipeline-Task läuft je nach Job-Zeitplan unterschiedlich: bei einem Triggered/Scheduled Job startet er ein einzelnes Update und stoppt nach dessen Abschluss; bei einem Continuous Job läuft die Pipeline kontinuierlich — der Job-Zeitplan bestimmt den Ausführungsmodus, auch wenn der eigene Pipeline-Mode der Pipeline auf „triggered" steht.

**Konfiguration über die Jobs-UI:**
1. Neuen Task anlegen, Typ **Pipeline**.
2. Im **Pipeline**-Dropdown bestehende Pipeline wählen.
3. Optional Full Refresh der Pipeline auslösen.
4. Optional Parameter-Overrides im **Parameters**-Feld setzen.
5. Optional Retries, Laufdauer-/Streaming-Backlog-Schwellen oder Benachrichtigungen konfigurieren.

Über **New ingestion pipeline** im Add-Task-Panel bzw. Type-Dropdown lässt sich auch direkt eine neue Ingestion-Pipeline anlegen.

**Kontinuierlich mit einem Continuous Job ausführen:** Der eingebaute **Pipeline mode** muss nicht auf continuous gesetzt werden — der Job-Zeitplan bestimmt den Ausführungsmodus und hat Vorrang. Gilt nur für Lakeflow Pipelines; eigenständige Materialized Views/Streaming Tables laufen immer getriggert. Eine in einem Continuous Job laufende Pipeline kann Serverless-Performance-Modi wie Standard nutzen, die der eingebaute Continuous-Modus der Pipeline nicht unterstützt. Databricks empfiehlt, kontinuierliche Pipelines über einen Continuous Job statt über die eingebaute Continuous-Einstellung der Pipeline laufen zu lassen — dabei den Pipeline Mode auf **triggered** (Standard) belassen.

**Beispiel — Declarative Automation Bundles:**

```yaml
# resources/continuous_job.yml
resources:
  jobs:
    continuous_pipeline_job:
      name: continuous_pipeline_job
      performance_target: STANDARD
      continuous:
        pause_status: UNPAUSED
      email_notifications:
        on_failure:
          - your_email@example.com
      tasks:
        - task_key: refresh_pipeline
          pipeline_task:
            pipeline_id: ${resources.pipelines.example_pipeline.id}
```

Migration einer bestehenden Continuous-Pipeline zu einem Continuous Job: `continuous`-Feld aus der Pipeline-Definition entfernen — der Job übernimmt die kontinuierliche Ausführung.

**Database Table Sync Pipeline:** Ein Pipeline-Task, der die Pipeline für eine Lakebase-Synced-Table pflegt — zum zeitgesteuerten Refresh oder bei Änderung der Unity-Catalog-Quelltabelle, damit operative Anwendungen aktuelle Daten aus Lakebase Postgres lesen. Erscheint im Type-Dropdown unter „Ingestion and Transformation". Im **Pipeline**-Feld die zur Synced Table gehörige Pipeline wählen (Lakebase Autoscaling oder Lakebase Provisioned, je nach Angebot).

**Ingestion Pipeline:** Ein Pipeline-Task, der eine Ingestion-Pipeline ausführt. Über **Ingestion pipeline** im Type-Dropdown startet der **Add data**-Assistent, der einen Pipeline-Task für eine Ingestion-Pipeline erstellt — die erste Seite fragt nach der Datenquelle.

**Parameter (Beta):** Job- oder Task-Parameter lassen sich über dynamische Wertreferenzen im Pipeline-Task nutzen; Overrides über Key-Value-Paare im **Parameters**-Feld des Tasks.

**Concurrency-Grenzen:** Eine Pipeline kann immer nur ein Update gleichzeitig ausführen:
- Ein Job mit `max_concurrent_runs > 1`, der einen Pipeline-Task enthält, wird auf einen gleichzeitigen Lauf begrenzt (Hinweis in der Job-UI).
- Ein in einem For-each-Task verpackter Pipeline-Task ist unabhängig von der konfigurierten Loop-Concurrency auf eine gleichzeitige Iteration begrenzt.

**Pipeline über die Pipeline-UI zeitplanen:** Erzeugt einen Job mit einem einzelnen Pipeline-Task:
1. **Jobs & Pipelines** → Pipeline-Namen anklicken.
2. **Schedule** klicken (bzw. **Add schedule**, falls bereits Zeitpläne existieren).
3. Trigger-Typ wählen: **Scheduled** (zeitbasiert, mit Advanced-/Cron-Optionen) oder **Continuous**.
4. Eindeutigen Job-Namen vergeben.
5. Optional **Performance optimized** deaktivieren für Standard Performance Mode.
6. Optional E-Mail-Benachrichtigungen bei Start/Erfolg/Fehlschlag unter **More options**.
7. **Create**.

Bei kontinuierlichem Zeitplan startet Databricks den Lauf automatisch; **Stop** auf der Pipeline-Seite oder Pausieren des Zeitplans beendet ihn (und bricht das aktive Update ab). Ist die Pipeline in mehreren Zeitplänen enthalten, zeigt der Schedule-Button deren Anzahl (z. B. „Schedule (5)").

**Zeitplan für Materialized View/Streaming Table in Databricks SQL:** In Databricks SQL definierte Materialized Views und Streaming Tables unterstützen zeitbasierte Zeitpläne direkt über `CREATE`/`ALTER`.

---

## 38. Dashboard-Task

**Einfach erklärt:** Der Dashboard-Task aktualisiert die Ergebnisse eines veröffentlichten Databricks-Dashboards als Teil eines Job-Workflows.

**Voraussetzungen:** Dashboard muss veröffentlicht und für den konfigurierenden Nutzer zugänglich sein; mindestens `CAN VIEW` auf dem Dashboard für das Deployment.

**Konfiguration:**
1. Tab **Tasks** → Task-Namen eingeben.
2. Typ **Dashboard**.
3. Zu aktualisierendes Dashboard im Dropdown wählen.
4. Optional SQL-Warehouse für den Refresh wählen (Serverless oder Pro erforderlich).
5. Optional Subscriber für E-Mail-Benachrichtigungen wählen.
6. Optional **Dashboard filters** konfigurieren: **Add filter** → Filter-Widget des Dashboards wählen → Wert eingeben.
7. Optional Duration Threshold, Notifications oder Retries in den Advanced Task Settings.
8. **Save task**.

**Ausführung und Zugriff.** Abhängig von der Veröffentlichungsart:
- **Mit Shared-Data-Permissions:** Betrachter greifen mit den Credentials des Dashboard-Publishers auf Daten zu.
- **Ohne Shared-Data-Permissions:** Die „Run as"-Identität des Jobs (standardmäßig der Job-Eigentümer) aktualisiert das Dashboard.

Keine Code-Beispiele in dieser Datei.

---

## 39. SQL-Alert-Task

**Einfach erklärt:** Der SQL-Alert-Task wertet einen Databricks-SQL-Alert als Teil eines Jobs aus — er integriert Alert-basiertes Monitoring in Datenpipelines, unabhängig vom eigenen Zeitplan des Alerts.

**Voraussetzungen:** Ein bestehender Databricks-SQL-Alert im Workspace; mindestens `CAN RUN` auf dem Alert; Zugriff auf ein Serverless- oder Pro-SQL-Warehouse.

**Konfiguration:**
1. **Jobs & Pipelines** → **Create** → **Job**.
2. **Add another task type** → „SQL Alert" suchen und wählen.
3. Task-Namen eingeben.
4. Im **Alert**-Dropdown den auszuwertenden Alert wählen.
5. Optional **SQL warehouse** wählen (sonst wird das interne Warehouse des Alerts genutzt) — muss Serverless oder Pro sein.
6. Optional **Subscribers** für Ergebnisbenachrichtigungen wählen (sonst interne Subscriber des Alerts, falls vorhanden). Anpassung von Betreff/Inhalt der Benachrichtigung über die Notification-Vorlage des zugrunde liegenden Alerts.
7. Optional **Notifications** für Start/Abschluss/Fehlschlag des Tasks (E-Mail/Webhook).
8. Optional **Duration threshold**/**Retries**.
9. **Save task**.

**Verhalten:**
1. Die Alert-Query läuft auf dem angegebenen Warehouse.
2. Die Alert-Bedingung wird gegen das Ergebnis ausgewertet.
3. Konfigurierte Subscriber erhalten Benachrichtigungen je nach Ergebnis.

**Status:** „Succeeded" — Alert erfolgreich ausgewertet, unabhängig davon, ob die Bedingung ausgelöst wurde. „Failed" — Fehler bei der Auswertung (z. B. Warehouse-Verbindungsproblem, Query-Fehler).

**Einschränkungen:** Keine Parameter-Unterstützung — für parametrisierte Queries stattdessen einen SQL-Task nutzen. Nur Databricks-SQL-Alerts unterstützt, keine Legacy-Alerts.

Keine Code-Beispiele in dieser Datei.

---

## 40. dbt-Task

**Einfach erklärt:** Der dbt-Task konfiguriert und führt dbt-Projekte auf Databricks aus. Beim Lauf injiziert Databricks das `DBT_ACCESS_TOKEN` für den im **Run As**-Feld konfigurierten Principal, sodass dbt gegen ein SQL-Warehouse ausgeführt wird.

**Voraussetzungen.** Der Run-As-Principal benötigt:
- `CAN USE` auf dem SQL-Warehouse, das den von dbt generierten SQL-Code ausführt.
- die von den dbt-Modellen benötigten Unity-Catalog-Privilegien (z. B. `USE CATALOG`/`USE SCHEMA` auf Ziel-Catalog/-Schema, `SELECT`/`MODIFY` auf gelesenen/geschriebenen Objekten).

**Konfiguration:**
1. Tab **Tasks** → **Add task**.
2. Task-Namen eingeben, Typ **dbt**.
3. **Source**: **Workspace** (dbt-Projekt in Workspace-Ordnern) oder **Git provider** (Remote-Repository).
4. **Project directory** über den Dateibrowser wählen bzw. Git-Informationen eingeben.
5. **dbt commands** — Standard: `dbt deps`, `dbt seed`, `dbt run` (sequenziell, anpassbar).
6. **SQL warehouse** wählen (nur Serverless/Pro).
7. **Warehouse catalog** (Standard: Workspace-Default) und **Warehouse schema** (Standard: `default`) angeben.
8. **dbt CLI compute** wählen, auf dem dbt Core läuft (Serverless oder Classic Jobs Compute mit Single-Node-Cluster empfohlen).
9. `dbt-databricks`-Version festlegen: bei Serverless über **Environment and Libraries**; sonst über **Dependent libraries** (Standard `dbt-databricks>=1.0.0,<2.0.0`) — Version zum Pinnen löschen und neu setzen.
10. Optional Retries, Laufdauer-/Streaming-Backlog-Schwellen oder Benachrichtigungen.
11. **Save task**.

**Empfehlung:** dbt-Tasks auf eine feste `dbt-databricks`-Version pinnen, damit Entwicklung und Produktion dieselbe Version nutzen.

**dbt-Kommandos.** Das Feld **dbt commands** akzeptiert dbt-CLI-Befehle.

**Optionen übergeben:** Die dbt-Node-Selection-Syntax erlaubt `--select`/`--exclude` bei `run`/`build`, plus weitere Konfigurations-Flags.

**Variablen übergeben:** Über `--vars`, als einfach-quotiertes JSON mit doppelt-quotierten Keys/Values:

```
dbt run --vars '{"volume_path": "/Volumes/path/to/data", "date": "2024/08/16"}'
```

**Parametrisierte Beispiele:**

| Parametername | Wert |
|---|---|
| `volume_path` | `/Volumes/path/to/data` |
| `table_name` | `my_table` |
| `select_clause` | `--select "tag:nightly"` |
| `dbt_refresh` | `--full-refresh` |

```
dbt run '{"volume_path": "{{job.parameters.volume_path}}"}'
dbt run --select "{{job.parameters.table_name}}"
dbt run {{job.parameters.select_clause}}
dbt run {{job.parameters.dbt_refresh}}
dbt run '{"volume_path": "{{job.parameters.volume_path}}"}' {{job.parameters.dbt_refresh}}
```

Dynamische Parameter/Task Values:

```
dbt run --vars '{"date": "{{job.start_time.iso_date}}"}'
dbt run --vars '{"sales_count": "{{tasks.sales_task.values.sales_count}}"}'
```

---

## 41. dbt-Platform-Task (Public Preview)

**Einfach erklärt:** Mit dem dbt-Platform-Task lässt sich ein bereits in der dbt Platform (dem SaaS-Produkt von dbt Labs) definierter dbt-Job direkt aus einem Databricks-Job heraus auslösen und überwachen. Der eigentliche dbt-Lauf passiert weiterhin in der dbt Platform — Databricks übernimmt nur die zentrale Orchestrierung und Zeitplanung, die dbt-Platform-Vorteile (Monitoring, eigene Zeitplanung) bleiben dabei erhalten. Das unterscheidet sich vom "dbt task", der ein dbt-Core-Projekt direkt auf Databricks-Compute ausführt.

| Task-Typ | Einsatz |
|---|---|
| **dbt platform task** | orchestriert bestehende dbt-Platform-Jobs über die dbt-Platform-API — zentrale Orchestrierung in Databricks, dbt-Platform-Vorteile (Monitoring, Zeitplanung) bleiben erhalten |
| **dbt task** | führt dbt-Core-Projekte auf einem Databricks-Cluster mit Code aus Git aus — volle Kontrolle über die Ausführungsumgebung |

Voraussetzungen: Workspace-Admin muss die Preview aktivieren; `CREATE CONNECTION` auf dem Unity-Catalog-Metastore; bestehendes dbt-Projekt mit definiertem Job in der dbt Platform; Recht, einen Service-Token in der dbt Platform zu erzeugen (Service-Account-Token statt persönlichem Token empfohlen).

**dbt-Platform-Details beschaffen:**
- Account ID: dbt Platform → Settings → Account Settings → aus der URL `https://cloud.getdbt.com/settings/accounts/{account_id}`.
- API Key: Settings → Profile Setting → Your Profile → Access API → API Key.
- Host-URL: abhängig von Tenancy, z. B. Multi-Tenant Nordamerika `https://cloud.getdbt.com`, Cell-based Nordamerika `https://12345.us1.dbt.com`.

**dbt-Platform-Connection einrichten:** Catalog-Icon in der Sidebar → Plus-Icon im Schema-Browser → **Create a connection** → Namen vergeben, Typ **dbt platform** → **Next** → Host-URL (ohne abschließenden Slash) → Account ID und API-Token → **Create connection** → optional Privilegien vergeben.

**Job mit dbt-Platform-Task erstellen:** Jobs & Pipelines → Create → Job → Add another task type → "dbt platform" suchen → Task-Namen eingeben → dbt-Platform-Connection wählen → dbt-Platform-Job wählen → optional Retries, Laufdauer-/Streaming-Backlog-Schwellen, Benachrichtigungen → Save task → optional Run now zum Testen.

Zeitbasiert oder ereignisbasiert konfigurierbar. **Continuous-Trigger werden für dbt-Platform-Jobs nicht unterstützt.**

Läufe überwachen: Jobs & Pipelines → Job öffnen → Lauf in Spalte "Start time" anklicken → "View in dbt" für Details in der dbt Platform.

Keine Code-Beispiele in dieser Datei.

---

## 42. dbt-Core-Transformationen in Lakeflow Jobs nutzen

**Einfach erklärt:** dbt-Core-Projekte lassen sich als eigener Task-Typ in Lakeflow Jobs ausführen — mit Zeitplanung, Monitoring, Benachrichtigungen, Artefakt-Archivierung (Logs, Ergebnisse, Manifeste, Konfigurationen) und Kombination mit anderen Task-Typen wie Auto Loader oder Notebooks. In der Entwicklung arbeitet man am besten direkt gegen ein SQL-Warehouse (einfacheres Debuggen über Query History), in Produktion läuft der dbt-Python-Prozess auf Databricks-Compute, während das generierte SQL gegen das gewählte SQL-Warehouse ausgeführt wird.

Voraussetzungen: Kenntnis von dbt Core und dem `dbt-databricks`-Paket (bevorzugt gegenüber `dbt-spark`); dbt-Projekte in Databricks-Git-Ordnern (nicht DBFS); Serverless- oder Pro-SQL-Warehouses aktiviert; Databricks-SQL-Entitlement.

**Ersten dbt-Job erstellen (Beispiel jaffle_shop):** Jobs & Pipelines → Create → Job → Kachel dbt wählen → Job-/Task-Namen vergeben → Source = Git provider, Repository `https://github.com/dbt-labs/jaffle_shop.git` → dbt-Kommandos in Reihenfolge (`deps`, `seed`, `run`) → SQL-Warehouse wählen (nur Serverless/Pro) → optional Catalog/Schema → optional dbt-CLI-Compute anpassen → Environment and Libraries auf `dbt-default` belassen → Save task → Run Now.

Ergebnisse prüfen:

```sql
SHOW tables IN <schema>;
```

```sql
SELECT * from <schema>.customers LIMIT 10;
```

API-Beispiel für einen dbt-Job:

```json
{
  "name": "jaffle_shop dbt job",
  "max_concurrent_runs": 1,
  "git_source": {
    "git_url": "https://github.com/dbt-labs/jaffle_shop",
    "git_provider": "gitHub",
    "git_branch": "main",
    "sparse_checkout": {
      "patterns": ["models", "seeds"]
    }
  },
  "job_clusters": [
    {
      "job_cluster_key": "dbt_CLI",
      "new_cluster": {
        "spark_version": "10.4.x-photon-scala2.12",
        "node_type_id": "i3.xlarge",
        "num_workers": 0,
        "spark_conf": {
          "spark.master": "local[*, 4]",
          "spark.databricks.cluster.profile": "singleNode"
        },
        "custom_tags": {
          "ResourceClass": "SingleNode"
        }
      }
    }
  ],
  "tasks": [
    {
      "task_key": "transform",
      "job_cluster_key": "dbt_CLI",
      "dbt_task": {
        "commands": ["dbt deps", "dbt seed", "dbt run"],
        "warehouse_id": "1a234b567c8de912"
      },
      "libraries": [
        {
          "pypi": {
            "package": "dbt-databricks>=1.0.0,<2.0.0"
          }
        }
      ]
    }
  ]
}
```

**dbt-Task-Ausgabe und Artefakte abrufen** über Databricks CLI oder Jobs API — bei Multi-Task-Jobs die Task-Run-ID nutzen, nicht die übergeordnete Job-Run-ID:

| Feld | Beschreibung |
|---|---|
| `dbt_output.artifacts_link` | Download-URL für gepackte dbt-Artefakte (z. B. `dbt-output.tar.gz`) |
| `logs` | Inline-dbt-Logs des Task-Laufs |
| `logs_truncated` | ob Logs wegen Antwortgröße gekürzt wurden |
| `metadata` | Task-Run-Metadaten (Status, Timing, IDs, Konfiguration) |

```bash
databricks jobs get-run-output <task_run_id> --output JSON
```

```
GET /api/2.0/jobs/runs/get-output?run_id=<task_run_id>
```

**Fortgeschritten: eigenes Profil nutzen.** Für ein individuelles `profiles.yml` gegen SQL-Warehouse oder All-Purpose-Compute:

```bash
git clone https://github.com/<username>/jaffle_shop.git
```

```yaml
jaffle_shop:
  target: databricks_job
  outputs:
    databricks_job:
      type: databricks
      method: http
      schema: '<schema>'
      host: '<http-host>'
      http_path: '<http-path>'
      token: "{{ env_var('DBT_ACCESS_TOKEN') }}"
```

```bash
git add profiles.yml
git commit -m "adding profiles.yml for my Databricks job"
git push
```

Im Job: Edit in Source, Fork-Repository-Details eingeben, SQL-Warehouse auf "None (Manual)" setzen, relativen Pfad zum `profiles.yml`-Verzeichnis in Profiles Directory eingeben (leer = Repository-Root). Wichtig: Catalog-/Schema-Einstellungen vor dem Wechsel zu "None (Manual)" leeren.

**Fortgeschritten: dbt-Python-Modelle (Beta, dbt 1.3+).** Python-Modelle lassen sich für Databricks-Transformationen nutzen; Einschränkung: nicht über SQL-Warehouse ausführbar — benötigt All-Purpose- oder Job-Compute.

**Fehlerbehebung:** "Profile file does not exist" — `profiles.yml` wurde am erwarteten Pfad nicht gefunden, sicherstellen, dass es im Repository-Root liegt.

---

## 43. JAR-Task

**Einfach erklärt:** Der JAR-Task führt in Scala oder Java kompilierten und als JAR-Datei verpackten Code aus. Man gibt die vollständig qualifizierte Main-Class an, die die auszuführende `main`-Methode enthält, sowie optional Parameter, die als Argumente an diese Methode übergeben werden.

Voraussetzungen: passende Compute-Konfiguration wählen; JAR-Datei an einem kompatiblen Ort oder Maven-Repository hochladen; bei Standard Access Mode müssen Admins Maven-Koordinaten und JAR-Pfade auf eine Allowlist setzen.

**Konfiguration:** Tab Tasks → Add task → Task-Namen eingeben, Typ JAR → Main class angeben (voller Klassenname mit der `main`-Methode; muss in einer als Dependent Library konfigurierten JAR enthalten sein) → Compute wählen (Classic oder Serverless) → Environment und Abhängigkeiten (Classic: Add unter Dependent libraries, bestehende JAR wählen oder hochladen; Serverless: Environment wählen/bearbeiten, Environment Version 4+, JAR-Datei und weitere Abhängigkeiten hinzufügen, Spark-Abhängigkeiten ausgenommen) → Parameters als optionale String-Liste, die als Argumente an die Main-Class übergeben werden → optional erweiterte Einstellungen (Retries, Laufdauer-/Streaming-Backlog-Schwellen, Benachrichtigungen) → Save task.

Keine Code-Beispiele in dieser Datei.

---

## 44. Eine Databricks-kompatible JAR erstellen

**Einfach erklärt:** Damit eine selbst gebaute JAR auf Databricks-Compute läuft, müssen JDK-, Scala- und Spark-Versionen zum Compute passen, benötigte Abhängigkeiten müssen entweder gebündelt oder auf dem Compute installiert sein, der Code muss die Spark-Session über `SparkSession.builder().getOrCreate()` holen statt selbst eine zu erzeugen, und bei Standard Compute muss die JAR auf eine Allowlist gesetzt werden.

**Architekturunterschiede:** Serverless und Standard Compute nutzen die Spark-Connect-Architektur (Isolation, Governance, kein direkter Spark-Context-/RDD-Zugriff). Dedicated Compute nutzt die klassische Spark-Architektur mit vollem API-Zugriff.

**Versionen ermitteln:** Serverless — Tabellen zu Serverless Environment Version 4+; Standard/Dedicated — Abschnitt "System Environment" der Databricks-Runtime-Release-Notes.

**Beispiel-Build-Konfiguration (Databricks Runtime 17.3 LTS):** Scala-Version 2.13.16, JDK 17, Maven-Compiler-Source/Target 17.

**Abhängigkeiten:** Empfohlen wird, Databricks Connect mit `provided`-Scope zu nutzen, um Spark nicht mitzupacken. Laufzeit-bereitgestellte Bibliotheken als `provided` markieren; Anwendungsabhängigkeiten mit sbt-assembly oder Maven Shade Plugin bündeln.

**Erforderliche Code-Muster:** Spark-Session über `SparkSession.builder().getOrCreate()` abrufen. Für Aufräumarbeiten `try`-`finally`-Blöcke statt Shutdown Hooks nutzen, da Databricks Container-Lebenszeiten verwaltet und Hooks ggf. nicht ausgeführt werden.

**Serverless-Logging:** SLF4J-Logging über die `log4j-slf4j2-impl`-Bridge konfigurieren (passend zur Log4j-Version der Serverless-Umgebung) — entweder in der Fat JAR oder als separate Abhängigkeit.

Keine Code-Beispiele in dieser Datei.

---

## 45. JARs auf Serverless Compute erstellen und ausführen (Tutorial)

**Einfach erklärt:** Dieses Tutorial zeigt Schritt für Schritt, wie eine einfache Java-JAR gebaut, hochgeladen und als JAR-Task auf Serverless Compute ausgeführt wird. Serverless Compute nutzt Spark Connect — die JAR läuft gegen eine schlanke Client-Bibliothek mit den öffentlichen Spark-APIs, während die eigentliche Spark-Engine serverseitig läuft. Statt JARs manuell zu bauen, empfiehlt Databricks alternativ Declarative Automation Bundles mit vorkonfigurierten Scala-, JDK- und Databricks-Connect-Versionen.

Voraussetzungen: sbt 1.11.7+ (Scala) bzw. Maven 3.9.0+ (Java); JDK-, Scala- und Databricks-Connect-Versionen passend zur Serverless-Umgebung. Für Serverless Environment 4: Scala-2.13-Kompilierung, JDK 17 (Class File Version 61), Databricks Connect 17.3, nur öffentliche Spark-APIs (keine RDDs/Internals).

**Einschränkungen:** nicht verfügbar sind die RDD-API und SparkContext/JavaSparkContext, Spark-interne APIs (catalyst, util, sql/util, sql/internal), native Bibliotheken (.so, .dll, JNI).

**Schritt 1 — JAR bauen (Java-Beispiel):**

```java
package com.examples;
import org.apache.spark.sql.SparkSession;
import java.util.stream.Collectors;

public class SparkJar {
  public static void main(String[] args) {
    SparkSession spark = SparkSession.builder().getOrCreate();
    System.out.println(String.join(", ", args));
    System.out.println(spark.version());
    System.out.println(
      spark.range(10).limit(3).collectAsList().stream()
        .map(Object::toString)
        .collect(Collectors.joining(" "))
    );
  }
}
```

**Abhängigkeiten verwalten:** drei Strategien — mitgelieferte Bibliotheken nutzen (Serverless enthält Databricks Connect und gängige Libraries), als Environment Library hinzufügen falls nicht vorhanden, oder für externe Datenbanken JDBC-Connections statt eingebetteter Treiber nutzen. Mitgelieferte Bibliotheken in Environment 4 (Auswahl): `databricks-connect_2.13` (17.3.2), `scala-library_2.13` (2.13.16), `slf4j-api` (2.0.10), `log4j-core` (2.20.0), `jackson-databind` (2.15.2), `guava` (32.0.1-jre), `databricks-sdk-java` (0.52.0), u. a.

**Schritt 2 — Job zum Ausführen erstellen:** Jobs & Pipelines → Create → Job → Kachel JAR → Job-/Task-Namen vergeben → Main class: `com.examples.SparkJar` → Compute: Serverless → Serverless-Environment konfigurieren (Version 4+) → JAR-Datei per Drag & Drop oder Dateibrowser hochladen → Parameter hinzufügen (Beispiel: `["Hello", "World!"]`) → Save task.

**Schritt 3 — Ausführen und prüfen:** Run Now → Ausgabe erscheint im Output-Panel.

**Fehlerbehebung:**

| Fehler | Ursache | Lösung |
|---|---|---|
| `NoSuchMethodError` (scala.*) | mit Scala 2.12 kompiliert, Serverless nutzt 2.13 | mit `scalaVersion := "2.13.16"` neu kompilieren |
| `NoClassDefFoundError: scala/...` | Scala-2.12-/2.13-Konflikt | 2.13.16 mit `_2.13`-Suffix für Abhängigkeiten |
| `UnsupportedClassVersionError` | mit JDK 18+ kompiliert, Serverless nutzt JDK 17 | `--release 17` verwenden |
| `NoClassDefFoundError` (org/apache/spark/...) | Spark-Internals/RDD-API genutzt | nur öffentliche Spark-API nutzen |
| `ClassNotFoundException` (JDBC-Treiber) | Treiber nicht im Classpath | JDBC-Connection nutzen |
| `ClassNotFoundException` (Drittanbieter) | Bibliothek nicht im Serverless-Classpath | zur JAR/Environment hinzufügen |
| `UnsatisfiedLinkError` | native Bibliothek in der JAR | reines-Java-Äquivalent oder Classic Compute nutzen |
| `NoSuchMethodError` (Drittanbieter) | Versionskonflikt mit mitgelieferten Bibliotheken | mitgelieferte Version nutzen, als "provided" markieren |

---

## 46. Spark-Submit-Task: Deprecation und Migration

**Einfach erklärt:** Databricks stuft den Spark-Submit-Task-Typ wegen technischer Einschränkungen und Feature-Lücken gegenüber JAR-, Notebook- und Python-Script-Tasks als veraltet ein. Ab November 2025 ist das Erstellen neuer Spark-Submit-Tasks auf Nutzer beschränkt, die Spark Submit im Vormonat aktiv genutzt haben — der Task-Typ soll perspektivisch ganz verschwinden.

**Migrationswege:**
- JVM-Workloads: zu JAR-Tasks migrieren — Main-Class-Name und JAR-Dateipfad aus den Spark-Submit-Parametern extrahieren und im JAR-Task-Format konfigurieren.
- R-Workloads: entweder R-Skripte zu Databricks-Notebooks migrieren (voller Funktionsumfang), oder R-Skripte per `source()` aus einem Notebook-Task heraus bootstrappen.

**Betroffene Jobs finden:** zwei Python-Skripte von Databricks — Fast Scan (empfohlener erster Schritt, scannt nur persistente Jobs über die `/jobs/create`-API, deutlich schneller) und Comprehensive Scan (untersucht alle Läufe der letzten 30 Tage inkl. ephemerer Jobs über `/runs/submit`, kann in großen Workspaces Stunden dauern). Beide liefern CSV-Ergebnisse mit Job-IDs, Eigentümer-E-Mails und Job-Namen.

Keine Code-Beispiele in dieser Datei.

---

## 47. Spark Submit (Legacy, Deprecated, Entfernung Mitte 2026 geplant)

**Einfach erklärt:** Der Spark-Submit-Task ist der ursprüngliche, veraltete Ansatz, um JARs als Task zu konfigurieren — er wird komplett entfernt (geplant Mitte 2026), für neue Implementierungen sollte der modernere JAR-Task-Typ genutzt werden.

**Einschränkungen:** läuft nur auf neuen Clustern; JAR-Dateien müssen an kompatiblen Orten oder Maven-Repositories liegen; JAR-Dateien in Volumes sind nicht zugänglich; Cluster-Autoscaling wird nicht unterstützt; Cluster-Auto-Termination wird nicht unterstützt — Anwendungen müssen `System.exit` beim Abschluss explizit aufrufen; `dbutils` wird nicht unterstützt; Unity-Catalog-aktivierte Cluster benötigen Dedicated Access Mode (Standard Access Mode ist inkompatibel); Structured-Streaming-Jobs benötigen `max_concurrent_runs = 1` und den Cron-Ausdruck `"* * * * * ?"` (jede Minute), Streaming-Tasks müssen als letztes in der Job-Sequenz stehen.

**Konfiguration:** Tab Tasks → Add task → Task-Namen eingeben → Typ Spark Submit → Compute konfigurieren → Argumente/Konfiguration im Parameters-Feld als JSON-Array von Strings:

```json
["--class", "org.apache.spark.mainClassName", "dbfs:/Filestore/libraries/jar_path.jar"]
```

**Hinweise:** die ersten drei Argumente identifizieren Main-Class und JAR-Pfad; `master`, `deploy-mode` und `executor-cores` lassen sich nicht überschreiben; `--jars` und `--py-files` für abhängige Bibliotheken, `--conf` für Spark-Konfigurationen — beide unterstützen DBFS- und S3-Pfade (ebenso `--files`); standardmäßig wird der gesamte verfügbare Speicher genutzt (abzüglich Databricks-Service-Reserven) — anpassbar über `--driver-memory` und `--executor-memory`.

Save task.

---

## 48. Power-BI-Task (Public Preview)

**Einfach erklärt:** Der Power-BI-Task orchestriert Power-BI-Semantikmodelle über Databricks Jobs — Semantikmodelle werden automatisiert nach Microsoft Power BI Online veröffentlicht, ohne dass ein manueller Refresh-Klick nötig ist. Damit lässt sich die Aktualisierung von Power-BI-Dashboards direkt an den Rhythmus der Databricks-Datenpipelines koppeln.

Voraussetzungen: Power-BI-Connection in Unity Catalog eingerichtet; `USE CONNECTION`-Privileg; Zugriff auf die benötigten Tabellen und ein SQL-Warehouse (General-Purpose-Compute wird nicht unterstützt).

**Konfiguration:** Tab Tasks → Task hinzufügen → Task-Namen eingeben, Typ Power BI → erforderliche Eigenschaften konfigurieren: SQL-Warehouse, Power-BI-Connection, Workspace, Semantikmodell → optional erweiterte Einstellungen (Retries, Benachrichtigungen, Schwellen) → Task speichern.

**Zentrale Eigenschaften:**

SQL-Warehouse: erforderlich für Refreshes im Import-Modus oder Queries im DirectQuery-Modus.

| Modus | Verhalten |
|---|---|
| **Import** | Daten werden in Power BI gecacht; Refresh vor Nutzung fragt das SQL-Warehouse ab |
| **DirectQuery** | fragt das SQL-Warehouse bei Erstellen/Laden von Dashboards ab |

Authentifizierung: OAuth oder PAT (Personal Access Token) — Credentials ggf. zusätzlich in der Power-BI-UI nach dem Deployment zu konfigurieren.

Metadatenverwaltung: Checkbox "Overwrite existing model" propagiert alle Updates; standardmäßig werden nur Metadaten angehängt.

**Credential-Konfiguration über REST-APIs:** zwei Wege — Microsoft Fabric Connections API (Cloud-Connections und beide Gateway-Typen) oder Power BI REST API (Aktualisierung von Datenquellen-Credentials). Beide benötigen Microsoft-Entra-ID-Access-Tokens und unterstützen Basic Authentication mit Service-Principal-Application-IDs und -Secrets.

**Wichtige Hinweise:** Databricks empfiehlt einen Service Principal als Run-As-Identität für optimale Governance. Semantikmodelle während der Task-Ausführung nicht im Power-BI-Service bearbeiten — sonst können Modelle im Status "Pending changes" hängen bleiben.

Keine Code-Beispiele in dieser Datei.

---

## 49. Clean-Room-Notebook-Task

**Einfach erklärt:** Dieser Task-Typ führt ein Databricks-Notebook innerhalb eines Clean Rooms als Teil eines Workflows aus — so lassen sich Clean-Room-Analysen (datenschutzsichere Zusammenarbeit mehrerer Parteien) genauso zeitgesteuert und überwacht orchestrieren wie andere Job-Tasks auch.

Voraussetzung: Der ausführende Principal benötigt das Privileg `EXECUTE CLEAN ROOM TASK` auf dem betreffenden Clean Room.

**Konfiguration:** Neuer Job — Jobs & Pipelines → New → Job → Typ "Clean Room notebook". Bestehender Job — Jobs & Pipelines → Job wählen → Tab Tasks → Add task → Clean Room notebook.

**Einrichtung:** Clean Room mit dem gewünschten Notebook wählen → Notebook auswählen → optional Abhängigkeiten über Depends on konfigurieren → nutzt das Notebook `dbutils.widgets`, Parameter als Key-Value-Paare konfigurieren → optional Retries, Laufdauer-/Streaming-Backlog-Schwellen oder Benachrichtigungen setzen → Task speichern → Notebook-Vorschau prüfen → Continue klicken.

Keine Code-Beispiele in dieser Datei.

---

## 50. Lakeflow Jobs mit Apache Airflow orchestrieren

**Einfach erklärt:** Wer bereits Apache Airflow für die Orchestrierung nutzt, kann über den quelloffenen Databricks-Provider Databricks-Jobs auch von dort aus auslösen und überwachen. Airflow bildet Datenpipelines als gerichtete azyklische Graphen (DAGs) von Operationen ab; diese Airflow-Pakete werden allerdings nicht direkt von Databricks selbst unterstützt.

Voraussetzungen: Airflow 2.5.0+ (getestet mit 2.6.1); Python 3.8–3.11 (getestet mit 3.8); `pipenv` für virtuelle Python-Umgebungen.

**Databricks-Operatoren für Airflow:**

| Operator | Verhalten |
|---|---|
| `DatabricksRunNowOperator` | benötigt einen bestehenden Databricks-Job, nutzt `POST /api/2.1/jobs/run-now` |
| `DatabricksSubmitRunOperator` | benötigt keinen bestehenden Job, nutzt `POST /api/2.1/jobs/runs/submit` |
| `DatabricksCreateJobsOperator` | erstellt/setzt Jobs zurück über `POST /api/2.1/jobs/create`/`reset` |

Databricks empfiehlt `DatabricksRunNowOperator` — reduziert doppelte Job-Definitionen, ausgelöste Läufe erscheinen in der Jobs-UI.

**Installation:**

```bash
mkdir airflow
cd airflow
pipenv --python 3.8
pipenv shell
export AIRFLOW_HOME=$(pwd)
pipenv install apache-airflow
pipenv install apache-airflow-providers-databricks
mkdir dags
airflow db init
airflow users create --username admin --firstname <firstname> --lastname <lastname> --role Admin --email <email>
```

**Airflow starten — Webserver:**

```bash
pipenv shell
export AIRFLOW_HOME=$(pwd)
airflow webserver
```

**Scheduler (neues Terminal):**

```bash
pipenv shell
export AIRFLOW_HOME=$(pwd)
airflow scheduler
```

Installation testen: `http://localhost:8080/home` öffnen, einloggen, ein Beispiel-DAG (z. B. `example_python_operator`) entpausieren, Trigger DAG, DAG-Namen anklicken zur Lauf-Ansicht.

**Personal Access Token:** als Sicherheits-Best-Practice empfiehlt Databricks OAuth-Tokens; alternativ Personal Access Tokens von Service Principals (statt Workspace-Nutzern).

**Databricks-Connection konfigurieren:** `http://localhost:8080/connection/list/` → `databricks_default` bearbeiten → Host auf die Workspace-Instanz setzen (z. B. `https://adb-123456789.cloud.databricks.com`) → Token ins Password-Feld → Save.

**Beispiel: Airflow-DAG für einen Databricks-Job.**

Schritt 1 — Notebook erstellen:

```python
dbutils.widgets.text("greeting", "world", "Greeting")
greeting = dbutils.widgets.get("greeting")
```

```python
print("hello {}".format(greeting))
```

Schritt 2 — Job erstellen: Notebook-Task mit Parameter `greeting` = `Airflow user`, Job-ID aus dem Job-Details-Panel kopieren.

Schritt 3 — Airflow-DAG erstellen (`airflow/dags/databricks_dag.py`):

```python
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.utils.dates import days_ago

default_args = {
  'owner': 'airflow'
}

with DAG('databricks_dag',
  start_date = days_ago(2),
  schedule_interval = None,
  default_args = default_args
  ) as dag:
  opr_run_now = DatabricksRunNowOperator(
    task_id = 'run_now',
    databricks_conn_id = 'databricks_default',
    job_id = JOB_ID
  )
```

`JOB_ID` durch die tatsächliche Job-ID ersetzen.

Schritt 4 — DAG auslösen und prüfen: `http://localhost:8080/home` → `databricks_dag` entpausieren → Trigger DAG → Lauf in Spalte Runs öffnen.

---

## 51. Identitäten, Berechtigungen und Privilegien für Jobs

**Einfach erklärt:** Lakeflow Jobs trennt zwei Berechtigungsebenen: Job-Privilegien regeln, wer einen Job sehen, ausführen oder verwalten darf, während die Run-as-Identität bestimmt, mit welchen Rechten der Job tatsächlich auf Daten und Ressourcen zugreift. Diese Trennung erlaubt es, dass ein Job auf Ressourcen zugreifen kann, die der Ersteller selbst gar nicht besitzt, solange die Run-as-Identität entsprechende Rechte hat.

**Secrets in Logs:** Secrets bleiben standardmäßig in Spark-Driver-Logs von Classic Compute sichtbar. Nur Nutzer mit `CAN MANAGE` können die Logs einsehen, sofern nicht `spark.databricks.acl.needAdminPermissionToViewLogs` auf `false` gesetzt ist. Für Legacy "No Isolation Shared" Access Mode gelten abweichende Regeln.

**Standard-Privilegien:** Job-Ersteller erhalten `IS OWNER`; Workspace-Admins erhalten `CAN MANAGE`; der Job-Ersteller ist standardmäßig der Run-as-Nutzer. Workspace-Admins können Eigentümerschaft und Run-as-Konfiguration standardmäßig ändern; die Einstellung `RestrictWorkspaceAdmins` erlaubt Account-Admins, das einzuschränken.

**Unity-Catalog-Interaktion:** Jobs laufen als Run-as-Identität und werden gegen folgende Berechtigungen ausgewertet: Unity-Catalog-verwaltete Assets (Tabellen, Volumes, Modelle, Views), Legacy-Hive-Metastore-ACLs, Workspace-Asset-ACLs (Compute, Notebooks, Queries), Databricks Secrets. Job-Privilegien werden bei Aktionen am Job geprüft; Run-as-Privilegien während der Ausführung — teils erst bei Task-Start, teils fortlaufend. Wichtig: Werden Run-as-Rechte während eines laufenden Jobs entzogen, kann der Job vor Abschluss fehlschlagen.

**SQL-Tasks und Berechtigungen:** Nur File-Tasks respektieren den Run-as-Nutzer vollständig. SQL-Queries folgen den Sharing-Einstellungen der Query: "Run as owner" läuft mit der Identität des Query-Eigentümers, "Run as viewer" läuft mit der Run-as-Identität des Jobs. Beispiel: Nutzer A besitzt Query `my_query` mit "Run as owner". Nutzer B plant sie in Job `my_job` mit Service Principal `prod_sp` als Run-as. Der Job läuft als Nutzer A. Ändert A das Sharing auf "Run as viewer", läuft der Job als `prod_sp`.

**Run-as-Nutzer konfigurieren:** Nutzer mit `CAN MANAGE` oder `IS OWNER` können Run-as ändern — auf sich selbst oder einen Service Principal mit "Service Principal User"-Entitlement. Jobs & Pipelines → Job öffnen → Stift-Icon neben Run as im Job-Details-Panel → Nutzer/Service Principal suchen und wählen → Save.

**Run-as auf eine Gruppe setzen (Public Preview):** Alle Tasks laufen dann mit den Rechten der Gruppe; Workspace-Assets gehören der Gruppe. Audit-Logs zeigen `identity_metadata.run_as` als Gruppe und `identity_metadata.run_by` als Jobs-Service-Application-Service-Principal. Voraussetzung: Gruppenmitgliedschaft oder `Assume`-Privileg auf der Gruppe.

**Best Practices für Produktions-Jobs:** Service Principals als Run-as verwenden (verhindert Fehlschläge, wenn Ersteller den Workspace verlassen oder Rechte verlieren); Unity-Catalog-kompatibles Compute nutzen (Serverless und SQL-Warehouses nutzen immer Unity Catalog; Classic Compute nach Möglichkeit im Standard Access Mode); Job-Privilegien einschränken (`CAN VIEW` für Beobachter, `CAN MANAGE RUN` für Nutzer, die Läufe auslösen, `CAN MANAGE`/`IS OWNER` nur für vertrauenswürdige Nutzer, die Produktionscode ändern).

**Job-Berechtigungen:**

| Berechtigung | Umfang |
|---|---|
| `IS OWNER` | standardmäßige Run-as-Identität; überschreibbar |
| `CAN MANAGE` | Job-Definition, Konfiguration, Tasks, Berechtigungen bearbeiten; Zeitplan pausieren/fortsetzen |
| `CAN MANAGE RUN` | Läufe auslösen und abbrechen |
| `CAN VIEW` | Lauf-Ergebnisse, Details, Historie, Status einsehen |

Jede Berechtigung schließt die darunterliegenden ein. Nur ein Job-Eigentümer möglich; Gruppen können nicht `IS OWNER` erhalten. Über "Run Now" ausgelöste Läufe übernehmen die Rechte des Run-as-Nutzers, nicht des auslösenden Nutzers. Job-Zugriffskontrolle gilt für die Jobs-&-Pipelines-UI, nicht für Notebook-Workflows oder API-eingereichte Jobs (außer `access_control_list` ist explizit gesetzt).

**Berechtigungen konfigurieren:** Jobs & Pipelines → Job öffnen → Edit permissions im Job-Details-Panel → Nutzer/Gruppen/Service Principals suchen → Add → Save.

**Job-Eigentümer verwalten:** Nur Workspace-Admins können den Eigentümer ändern; genau ein Eigentümer ist Pflicht (Nutzer oder Service Principal).

**Notebook-Tasks und API-Zugriff:** Notebook-Task-Ausgabe über die UI erfordert Notebook-Zugriff. Derselbe Lauf über die API zeigt die Ausgabe dem API-Aufrufer auch mit nur Job-Level-Zugriff.

Keine Code-Beispiele in dieser Datei.

---

## 52. Lakeflow Jobs überwachen

**Einfach erklärt:** Die Databricks-UI zeigt alle zugänglichen Jobs, ihre Lauf-Historien und Details einzelner Läufe — ergänzt durch CLI-Befehle und das `system.lakeflow`-Schema, mit dem sich Job-Läufe und Task-Datensätze account-übergreifend per SQL abfragen lassen, inklusive Integration mit Billing-Tabellen für Kosten- und Performance-Monitoring.

CLI: `databricks jobs list -h`, `databricks jobs get -h`, `databricks jobs run-now -h`.

**Tabellen im `system.lakeflow`-Schema:**

| Tabelle | Inhalt |
|---|---|
| `jobs` | erfasst alle im Account erstellten Jobs |
| `job_tasks` | erfasst alle im Account laufenden Job-Tasks |
| `job_run_timeline` | Job-Läufe und zugehörige Metadaten |
| `job_task_run_timeline` | Task-Läufe und zugehörige Metadaten |
| `pipelines` (Public Preview) | erfasst alle im Account erstellten Lakeflow-Pipelines |
| `pipeline_update_timeline` (Public Preview) | Pipeline-Updates und zugehörige Metadaten |

Alle Tabellen unterstützen Streaming-Lesezugriff und behalten Daten kostenlos für 365 Tage; `jobs`, `job_tasks` und `pipelines` sind SCD2-Tabellen, die den jeweils aktuellsten Datensatz pro Entität unbegrenzt aufbewahren.

**Beispiel: `system.lakeflow` abfragen.** Das Grundmuster: Job- und Task-Lauf-Historie direkt per SQL aus dem `system.lakeflow`-Schema abfragen, statt über die UI zu navigieren:

```sql
-- Verfügbare Tabellen im system.lakeflow-Schema anzeigen
SHOW SCHEMAS IN system;
SHOW TABLES IN system.lakeflow;

-- Job- und Task-Lauf-Historie für einen bestimmten Job per Namensmuster verbinden
SELECT jobs.workspace_id,
        jobs.name as job_name,
        jobs.job_id,
        timeline.run_id,
        timeline.period_start_time,
        timeline.period_end_time,
        timeline.task_key,
        timeline.result_state
FROM system.lakeflow.jobs as jobs
INNER JOIN
system.lakeflow.job_task_run_timeline as timeline
ON jobs.job_id = timeline.job_id
WHERE lower(jobs.name) LIKE 'demo_12_retail_job_%'
ORDER BY timeline.period_start_time
```

`system.lakeflow.jobs` liefert die Job-Stammdaten (Name, ID, Workspace), `system.lakeflow.job_task_run_timeline` die einzelnen Task-Läufe mit Zeitfenster und Ergebnisstatus (`result_state`) — der Join darüber ergibt eine vollständige, abfragbare Lauf-Historie je Task, geeignet für eigene Dashboards oder Alerting außerhalb der Jobs-UI.

**Jobs und Pipelines ansehen:** Workflows-Icon in der Sidebar → Tab Jobs & pipelines listet alle zugänglichen Jobs/Pipelines mit Ersteller, Triggern und Ergebnissen der letzten fünf Läufe. Filter: Textsuche (Name/Job-ID), Tags, Typ (Jobs/Pipelines/alle), Eigentümer, Favoriten, Run-as-Nutzer (bis zu zwei Werte).

**Aktuelle Läufe über alle Jobs/Pipelines:** Tab Runs zeigt laufende und kürzlich abgeschlossene Läufe aller zugänglichen Jobs/Pipelines, inkl. extern ausgelöster (z. B. über Apache Airflow, Azure Data Factory). Filter: Job-/Pipeline-Name, Typ, Pipeline-Typ (ETL, Ingestion, MV/ST, Database Table Sync), Run-as-Nutzer, Run-ID, Startzeit (letzte 48 h), Status, Fehlercode.

**Diagramm abgeschlossener Läufe:** zeigt Läufe der letzten 48 Stunden (Standard: failed, skipped, successful). Zeitraum über Filter oder Ziehen im Diagramm wählbar; "Top 5 error types"-Tabelle zeigt häufigste Fehlerursachen. Erscheint nur bei Filterung auf Jobs oder Pipelines, nicht bei "All". Admins sehen alle Läufe; Nicht-Admins müssen "Run as" und "me" wählen.

**Runs-Liste:** zeigt Läufe der letzten 60 Tage (Standard: failed, skipped, successful) mit Startzeit, Name, Typ, Nutzername, Trigger-Quelle, Laufzeit, Status, Fehlercodes, Lauf-Parametern. Über `runs/submit` eingereichte Läufe haben keinen zugeordneten Job-Namen — Suche über Run-ID, Run-as oder Startzeit; unterstützen keine Retries.

**Läufe eines einzelnen Jobs:** Jobs & Pipelines → Job öffnen → Tab Runs mit Matrix- und Listenansicht. Matrixansicht: Farbcodierung — grün: Erfolg, rot: Fehlschlag, pink: übersprungen, gelb: wartet auf Retry, grau: ausstehend/abgebrochen/timeout; Balkenhöhe zeigt Laufdauer. Listenansicht: Startzeit, Lauf-ID, Trigger-Methode, Laufzeit, Status, Fehlercodes, Parameter; aktive Läufe zeigen einen Stop-Button, Dropdown erlaubt Abbruch aktiver oder aller wartenden Läufe. Databricks bewahrt 60 Tage Lauf-Historie — Export vor Ablauf empfohlen.

**Lauf-Details ansehen:** zeigt Output- und Log-Links, Erfolgs-/Fehlschlag-Informationen je Task. Bei Multi-Task-Jobs: Graph-, Timeline- und Listenansicht. Graph-Ansicht: Klick auf Task-Knoten zeigt Metadaten (Run as, Startmethode, Zeiten, Dauer, Status), Quellcode, Cluster-Informationen mit Query-History/Log-Links, Task-Metriken. Timeline-Ansicht: identifiziert lange laufende Tasks, zeigt Abhängigkeiten/Überlappungen zum Debugging; bei Serverless-Jobs integriert sich Query-Profiling direkt in die Timeline. Listenansicht (Standard): Status, Name, Typ, Ressource, Dauer, Abhängigkeiten — Spalten anpassbar, durchsuchbar, filterbar, sortierbar.

**Lauf-Status-Bestimmung** (basierend auf den Ergebnissen der Leaf-Tasks ohne nachgelagerte Abhängigkeiten):

| Status | Bedeutung |
|---|---|
| Succeeded | alle Tasks erfolgreich |
| Succeeded with failures | einige Tasks fehlgeschlagen, aber alle Leaf-Tasks erfolgreich |
| Failed | mindestens ein Leaf-Task fehlgeschlagen |
| Skipped | Lauf wurde übersprungen |
| Timed Out | maximale Laufzeit überschritten |
| Canceled | vom Nutzer abgebrochen |

Einzelne Tasks können zudem "Disabled" zeigen (explizit oder wegen deaktivierter vorgelagerter Tasks).

**Performance-Metriken:** Streaming-Task-Metriken und Serverless-Query-Performance-Metriken über Performance-Diagnose-Tools (siehe Abschnitt "Job-Performance diagnostizieren").

**Task-Lauf-Historie:** Task auf der Job-Run-Details-Seite anklicken, Historie im Dropdown wählen.

**For-Each-Task-Lauf-Historie:** läuft als Iterationstabelle. "Only failed iterations" filtert; Start-/End-Zeiten anklicken zeigt Iterations-Output.

**Lineage-Informationen:** bei aktiviertem Unity Catalog erscheinen Upstream-/Downstream-Tabellenzahlen in Job-Details-, Job-Run-Details- oder Task-Run-Details-Panels; Links führen zu Tabellenlisten und Catalog Explorer.

**Über Declarative Automation Bundles erstellte Jobs:** standardmäßig read-only in der UI. "Disconnect from source" erlaubt Bearbeitung — Änderungen fließen nicht in die Bundle-Konfiguration zurück (manuell nachpflegen); erneutes Deployment verbindet den Job wieder.

**Lauf-Ergebnisse exportieren:** Notebook-Ergebnisse — bei Ein-Task-Jobs View Details → Export to HTML, bei Multi-Task-Jobs zuerst den Notebook-Task anklicken. Lauf-Logs — automatische Log-Zustellung nach DBFS/S3 über die Compute-Konfiguration des Jobs oder das `new_cluster.cluster_log_conf`-Objekt der Jobs-API.

---

## 53. Benachrichtigungen für Jobs

**Einfach erklärt:** Für Job-Läufe und einzelne Tasks lassen sich Benachrichtigungen bei bestimmten Ereignissen einrichten — Start, erfolgreicher Abschluss, Fehlschlag, Überschreitung eines Laufdauer-Schwellenwerts oder eines Streaming-Backlog-Schwellenwerts. Als Ziel dienen E-Mail-Adressen oder Drittanbieter-Systeme wie Slack, Microsoft Teams, PagerDuty oder eigene Webhooks.

**Drittanbieter-Ziele einrichten:** Ein Admin konfiguriert System-Ziele über die Admin-Einstellungen — Edit system notifications → Create new destination. Maximal drei System-Ziele je Benachrichtigungsereignis pro Job/Task. Externe Systeme wie Amazon SES/SNS lassen sich über E-Mail-Benachrichtigungen integrieren. Der Inhalt von Slack-/Teams-Nachrichten kann sich in künftigen Releases ändern — für feste Schema-Anforderungen einen benutzerdefinierten Webhook konfigurieren.

**Zu beachten beim Konfigurieren:**
- Job-Level-Benachrichtigungen werden bei Retries fehlgeschlagener Tasks **nicht** gesendet — dafür Task-Benachrichtigungen nutzen.
- Maximal drei System-Ziele je Ereignistyp pro Job/Task.
- Läufe im Status "Succeeded with failures" gelten als erfolgreich — für Benachrichtigungen Success wählen.
- Für Laufdauer-Schwellen-Benachrichtigungen muss ein Duration Limit gesetzt sein.

Benötigtes Privileg: `CAN MANAGE` oder `IS OWNER` auf dem Job.

**Schritte:** Job-Details-Panel → Abschnitt Job notifications → Edit notifications → Add notification unten links → Ziel wählen (E-Mail-Adresse oder System-Ziel) → Ereignistypen ankreuzen (Start, Success, Failure, Duration warning, Streaming backlog) → weitere Ziele analog hinzufügen → Save. Zum Entfernen: Edit notifications → Papierkorb-Icon → speichern.

**Benachrichtigungen für langsame Jobs:** Bei konfigurierter erwarteter Laufdauer Duration Warning beim Hinzufügen/Bearbeiten einer Benachrichtigung wählen. Für Streaming-Backlog-Metriken: Benachrichtigung, wenn der durchschnittliche Backlog über 10 Minuten den Schwellenwert überschreitet; eine 30-Minuten-Wartezeit verhindert zu viele Nachrichten, danach alle 30 Minuten erneute Updates, solange der Backlog hoch bleibt. Streaming-Backlog-Benachrichtigungen setzen voraus, dass der Jobs-Service die aktive Streaming-Query verfolgen kann — `awaitTermination()` in Jobs vermeiden.

**Benachrichtigungen für übersprungene/abgebrochene Läufe filtern:** "Mute notifications for skipped runs", "Mute notifications for canceled runs". Für Task-Benachrichtigungen: "Mute notifications until the last retry" (Tasks werden standardmäßig dreimal wiederholt). Job-Level-Filterung filtert **nicht** automatisch Task-Level-Benachrichtigungen — getrennt konfigurieren.

**HTTP-Webhook-Payloads:**

| `event_type`-Code | Ausgelöst bei |
|---|---|
| `jobs.on_start` | Laufstart |
| `jobs.on_success` | Abschluss in Status "successful" oder "succeeded with failures" |
| `jobs.on_failure` | Abschluss in nicht erfolgreichem Status |
| `jobs.on_duration_warning_threshold_exceeded` | Überschreitung des konfigurierten Laufdauer-Schwellenwerts |

Beispiel — Job-Run-Start:

```json
{
  "event_type": "jobs.on_start",
  "workspace_id": "your_workspace_id",
  "run": {
    "run_id": "run_id"
  },
  "job": {
    "job_id": "job_id",
    "name": "job_name"
  }
}
```

Beispiel — Task-Run-Start:

```json
{
  "event_type": "jobs.on_start",
  "workspace_id": "your_workspace_id",
  "task": {
    "task_key": "task_name"
  },
  "run": {
    "run_id": "run_id_of_task",
    "parent_run_id": "run_id_of_parent_job_run"
  },
  "job": {
    "job_id": "job_id",
    "name": "job_name"
  }
}
```

Beispiel — Job-Run-Fehlschlag:

```json
{
  "event_type": "jobs.on_failure",
  "workspace_id": "your_workspace_id",
  "run": {
    "run_id": "run_id"
  },
  "job": {
    "job_id": "job_id",
    "name": "job_name"
  }
}
```

Beispiel — Task-Run-Erfolg:

```json
{
  "event_type": "jobs.on_success",
  "workspace_id": "your_workspace_id",
  "task": {
    "task_key": "task_name"
  },
  "run": {
    "run_id": "run_id_of_task",
    "parent_run_id": "run_id_of_parent_job_run"
  },
  "job": {
    "job_id": "job_id",
    "name": "job_name"
  }
}
```

---

## 54. Job-Fehlschläge diagnostizieren und reparieren (Repair)

**Einfach erklärt:** Schlägt ein Job fehl, hilft die Jobs-UI beim Eingrenzen der Ursache (Task-Konfiguration, Cluster-Ressourcen, Concurrency-Limits), und die Repair-Funktion erlaubt es, bei einem Multi-Task-Job nur die fehlgeschlagenen Tasks und ihre Abhängigkeiten erneut laufen zu lassen — statt den gesamten Job neu zu starten. Das spart Zeit und Ressourcen, birgt aber das Risiko doppelt geschriebener Daten, wenn Tasks nicht idempotent sind.

**Ursache identifizieren:** Workflows-Icon (Jobs & Pipelines) in der Sidebar → Job-Namen anklicken → Tab Runs zeigt aktive und abgeschlossene Läufe → über einen fehlgeschlagenen Task hovern (Start-/Endzeit, Status, Dauer, Cluster-Details, Fehlermeldung) → fehlgeschlagenen Task anklicken → Task run details mit Output, Fehlermeldung, Metadaten.

**Ursache beheben — häufige Ursachen und Abhilfen:**
- Task-Konfigurationsprobleme: Edit task → Konfiguration anpassen → Save task.
- Cluster-Ressourcenprobleme: ggf. auf einen geteilten All-Purpose-Cluster wechseln; Cluster-Konfiguration über Edit task → Configure ändern (Worker-Anzahl, Instanztypen); über Swap auf einen anderen verfügbaren Cluster wechseln; ggf. Admin um höhere Ressourcen-Quotas bitten.
- Maximum Concurrent Runs überschritten: auf Abschluss anderer Läufe warten, oder über Edit task → Edit concurrent runs den Wert erhöhen.

Liegt die Ursache upstream (z. B. externe Datenquelle nicht verfügbar), lässt sich nach Behebung trotzdem die Repair-Funktion nutzen.

**Fehlgeschlagene/übersprungene Tasks erneut ausführen (Repair):** repariert einen fehlgeschlagenen/abgebrochenen Multi-Task-Job, indem nur die nicht erfolgreichen Tasks und deren Abhängigkeiten erneut laufen. Job-/Task-Einstellungen lassen sich vor dem Reparieren ändern — nicht erfolgreiche Tasks laufen dann mit den aktuellen Einstellungen.

**Wichtig:** Ein Repair führt jeden nicht erfolgreichen Task von vorn erneut aus. Lakeflow Jobs macht Tasks nicht automatisch idempotent — hat ein Task vor dem Fehlschlag bereits einen Teil seiner Ausgabe geschrieben, kann ein erneuter Lauf diese Daten duplizieren. Vor dem Reparieren prüfen, was jeder Task schreibt, und wo nötig idempotente Operationen (Overwrite/Merge statt Append) nutzen.

**Weitere Hinweise:**
- Teilen sich mehrere Tasks einen Job-Cluster, erstellt ein Repair-Lauf einen neuen Cluster (z. B. `my_job_cluster_v1` bei ursprünglich `my_job_cluster`) mit denselben aktuellen Einstellungen.
- Repair ist nur für Jobs mit zwei oder mehr Tasks verfügbar — bei Ein-Task-Jobs stattdessen Run now erneut auslösen.
- Die angezeigte Duration umfasst die Zeit vom Start des ersten Laufs bis zum Ende des letzten Repair-Laufs.
- Repairs nutzen den Lauf-Status jedes Tasks, nicht dessen Deaktivierungsstatus — ein deaktivierter Task lässt sich über `rerun_tasks` in der Repair-Anfrage erzwingen.

**Ablauf:** Link des fehlgeschlagenen Laufs in Spalte Start time oder in der Matrixansicht anklicken → Repair run klicken (der Repair job run-Dialog listet alle nicht erfolgreichen Tasks und deren Abhängigkeiten) → optional Parameter für die zu reparierenden Tasks anpassen (überschreiben bestehende Werte; bei erneutem Repair Feld leeren, um zum Originalwert zurückzukehren) → Repair run im Dialog klicken → nach Abschluss zeigt die Matrixansicht eine neue Spalte für den Repair-Lauf — zuvor rote Tasks sollten nun grün sein.

**Fehlschläge bei Continuous Jobs:** Überschreiten aufeinanderfolgende Fehlschläge eines Continuous Jobs einen Schwellenwert, nutzt Lakeflow Jobs Exponential Backoff für Retries. Im Backoff-Zustand zeigt das Job-Details-Panel: Anzahl aufeinanderfolgender Fehlschläge, Zeitraum fehlerfreien Laufs bis "erfolgreich", Zeit bis zum nächsten Retry. Restart run bricht den aktiven Lauf ab, setzt die Retry-Periode zurück und startet einen neuen Lauf.

**Mit Genie Code diagnostizieren:** fehlgeschlagenen Job in der Jobs-UI öffnen → Diagnose Error wählen.

Keine Code-Beispiele in dieser Datei.

---

## 55. Job-Performance diagnostizieren

**Einfach erklärt:** Läuft ein Job oder Task länger als erwartet, hilft die Jobs-UI dabei, herauszufinden, wo die Zeit tatsächlich verbraucht wird — etwa beim Warten auf Ressourcen, beim Installieren von Bibliotheken oder in der eigentlichen Ausführung — und liefert bei Streaming- und Serverless-Workloads zusätzliche Detail-Metriken.

**Lauf-Aufschlüsselung nach Phase:** Beim Ansehen der Job-Run-Details zeigt das Hovern über das Duration-Feld: Queued, Waiting for resources, Library installation, Running. Gilt für Job- und Task-Läufe. Bei Multi-Task-Jobs zählt "Waiting for resources" auf Job-Ebene nur bis zum Start des ersten Tasks — vollständige, taskbezogene Aufschlüsselungen erscheinen im Task-Run-Output.

- **Queued:** Job/Task wartet wegen Concurrency-Limits (max. gleichzeitige Läufe desselben Jobs oder Workspace-weites Limit). Abhilfe: Limit erhöhen oder Zeitpläne entzerren.
- **Waiting for resources:** wartet auf Compute-Verfügbarkeit. Bei Serverless: Standard Performance Mode hat 4–6 Minuten Startlatenz — Performance Optimized reduziert sie. Bei Classic Compute: langsame VM-Starts oder Quota-Probleme — Abhilfe: Serverless, Instance Pools mit Idle-Termination, mehrere Tasks in einem Multi-Task-Job auf einem Cluster bündeln, Flexible Node Types für automatischen Fallback aktivieren.
- **Library installation:** Zeit für Abhängigkeiten vor der Ausführung. Bei Serverless: ungecachte Environment oder viele Pakete aus langsamen Custom-PyPI-Repositories. Bei Classic Compute: große, komplexe Cluster-Environments, insbesondere mit Init-Skripten. Abhilfe: Paketanforderungen reduzieren, Workspace-Base-Environments in Betracht ziehen.
- **Running:** längere Laufzeiten durch mehr Daten, Konfigurationsänderungen oder langsamere Queries. Prüfen: System-Tabellen für Änderungen, Query-History/-Profile bei Serverless, Spark UI bei Classic Compute.

**Streaming-Task-Metriken (Public Preview):** Streaming Observability für Apache Kafka, Amazon Kinesis, Auto Loader, Google Pub/Sub, Delta-Tabellen. Metriken: Backlog-Sekunden, -Bytes, -Records, -Dateien, als Diagramme (Maximalwerte, minutenweise aggregiert, bis zu 48 Stunden).

| Quelle | Backlog Bytes | Backlog Records | Backlog Seconds | Backlog Files |
|---|---|---|---|---|
| Kafka | ✓ | ✓ | | |
| Kinesis | ✓ | ✓ | | |
| Delta | ✓ | ✓ | | |
| Auto Loader | ✓ | ✓ | | |
| Google Pub/Sub | ✓ | ✓ | | |

Ansehen: Job-Run-Details → Task wählen → Tab Metrics im Task-Run-Panel → Caret-Icon zum Aufklappen der Diagramme → Stream-IDs zum Filtern eingeben → Zeitraum über Dropdown anpassen → Next/Previous zum Navigieren zwischen Streams.

Einschränkungen: Metriken aktualisieren minütlich (bei 4+ Streams alle 5 Minuten). Nur die ersten 50 Streams pro Lauf werden erfasst. Erfassung im 1-Sekunden-Takt — kürzere Intervalle verhindern ggf. die Sichtbarkeit. Für Quellen ohne Standard-Metrik-Erfassung: `spark.sql.streaming.metricsEnabled` aktivieren.

**Query-Performance-Metriken für Serverless Jobs (Beta):** Query-Profile-Metriken und Performance-Insights direkt in der Job-Run-UI — aggregierte Metriken umfassen gelesene/geschriebene Zeilen pro Task und Gesamt-Query-Anzahl.

Voraussetzungen: Preview "Improved Lakeflow Performance Observability" aktiviert; Workspace-Zugriff auf Query Performance Insights (für die Lightbulb-Indikatoren — aggregierte Metriken auch ohne diese sichtbar).

Angezeigte Metriken: gelesene/geschriebene Zeilen je Task-Lauf, Gesamt-Query-Anzahl je Task-Lauf, Performance-Insights-Indikator (Glühbirne) bei Tasks mit erkannten Insights.

| Ort | Anzeige |
|---|---|
| Task-Run-Sidebar | Zeilen gelesen/geschrieben, Query-Anzahl, Insights-Indikator |
| DAG-Ansicht | Glühbirnen-Badge auf Task-Knoten mit Insights |
| Timeline-Ansicht | Glühbirne neben Task-Namen mit Insight-Anzahl; Glühbirne bei einzelnen Queries |
| Listenansicht | Glühbirne in Insights-Spalte |

Untersuchungsablauf: Job-Lauf öffnen → Timeline-Ansicht → länger als erwartete Tasks anhand der Dauerverteilung identifizieren → über Tasks hovern (verarbeitete Zeilen, Query-Anzahl, Indikatoren) → Tasks aufklappen für Einzel-Queries → Query-Text mit Glühbirnen-Icon anklicken für Insights → Empfehlungen umsetzen, Job erneut ausführen.

Läufe vergleichen: langsamen mit vorherigem schnellem Lauf nebeneinander vergleichen — Unterschiede bei Zeilen (Datenvolumen), Query-Anzahl (Workload-Form), Insights (Ineffizienzen).

Einschränkungen: nur für Serverless Lakeflow Jobs — Classic Compute ohne diese Informationen. Aggregation über die ersten 100 Queries; darüber hinaus nur Teilsummen.

Keine Code-Beispiele in dieser Datei.

---

## 56. Jobs parametrisieren — Überblick

**Einfach erklärt:** Parameter erlauben es, Werte an einen Job und seine Tasks zu übergeben und Werte zwischen Tasks zu referenzieren. Quellcode-Assets, die als Tasks konfiguriert sind, müssen dafür entsprechend angepasst werden, um Parameter zu referenzieren — die konkrete Syntax unterscheidet sich je Sprache und Task-Typ.

**Grundbegriffe:**

| Begriff | Bedeutung |
|---|---|
| **Job-Parameter** | Key-Value-Paar auf Job-Ebene, an Tasks weitergereicht |
| **Task-Parameter** | Key-Value-Paar oder JSON-Array auf Task-Ebene |
| **Dynamische Wertreferenzen** | Syntax zur Referenzierung von Job-Zuständen, Metadaten und Parametern bei der Task-Konfiguration |
| **Task Values** | Syntax zum Erfassen und Referenzieren von während des Task-Laufs erzeugten Werten |
| **Parameterwerte im Code lesen** | wie Parameterwerte im Task-Code gelesen werden, je Task-Typ |

Hinweis: Für deployment-spezifische Konfiguration eignen sich statt Parametern auch Umgebungsvariablen für Serverless Jobs.

**Anwendungsfälle:** erweiterbare Logik in Code-Assets einbauen; Läufe bedingt gestalten; gemeinsame Parameter über mehrere Tasks referenzieren; in einem Task erzeugte Informationen in einem anderen Task nutzen; Metadaten und Zustandsinformationen des Job-Laufs referenzieren.

**Job- vs. Task-Parameter:** Job-Parameter sind Key-Value-Paare auf Job-Ebene, überschreibbar über "Run now with different parameters" oder die REST-API, und werden mit Key-Value-Parametern an Tasks weitergereicht. Task-Parameter sind Key-Value-Paare oder JSON-Arrays auf Task-Ebene. Jeder Task-Typ übergibt Werte unterschiedlich — Notebook-Tasks nutzen `dbutils.widgets`, Python-Skripte erhalten sie als Kommandozeilenargumente. Hinweis: Jeder Nutzer mit `CAN MANAGE RUN` oder höher kann Job-Parameterwerte für manuelle Läufe überschreiben.

**Workflows mit dynamischen Werten bauen:** Statische Task-Parameter lassen sich nur durch Ändern der Task-Definition überschreiben. Dynamische Wertreferenzen ermöglichen Muster wie: Job-Parameter über Tasks hinweg nutzen, Notebook-Query-Ausgaben als Listen erfassen, Verzweigungslogik erstellen, oder Parameter aus anderen Tasks referenzieren.

Keine Code-Beispiele in dieser Datei.

---

## 57. Job-Parameter konfigurieren

**Einfach erklärt:** Job-Parameter sind Key-Value-Paare, die einen Job mit statischen oder dynamischen Standardwerten versehen — beim manuellen Auslösen eines Laufs lassen sie sich optional überschreiben. Sie werden zentral am Job definiert und automatisch an alle Tasks weitergereicht, die Key-Value-Parameter unterstützen.

Parameter-Schlüssel dürfen nur Unterstriche, Bindestriche, Punkte und alphanumerische Zeichen enthalten. Werte sind Strings oder dynamische Wertreferenzen. Job-Parameterwerte können auch beliebiges gültiges JSON sein, einschließlich Arrays.

**Hinzufügen/Bearbeiten:** Jobs & Pipelines in der Sidebar → optional Filter Jobs/Owned by me → Job über den Namenslink auswählen → Job-Details-Sidebar → Edit parameters → Parameter über Key/Value-Felder hinzufügen/ändern → Papierkorb-Icon zum Entfernen → Save. Über { } lassen sich verfügbare dynamische Wertreferenzen zur Einfügung in Value-Felder anzeigen.

**Weitergabe an Tasks (Pushdown):** Unterschiedliche Task-Typen erhalten Job-Parameter über unterschiedliche Mechanismen. Teilen sich Job- und Task-Parameter denselben Schlüssel, hat der Job-Parameter bei Key-Value-Parameter-Tasks Vorrang. JSON-Array-Parameter-Tasks benötigen dagegen die explizite Referenz `{{job.parameters.<name>}}`.

**Mit anderen Parametern ausführen:** Konfigurierte Job-Parameter lassen sich bei "Run now with different parameters" überschreiben/ergänzen — ebenso bei der Reparatur fehlgeschlagener/übersprungener Tasks.

Keine Code-Beispiele in dieser Datei.

---

## 58. Task-Parameter konfigurieren

**Einfach erklärt:** Task-Parameter parametrisieren einzelne Tasks mit statischen, dynamischen oder von vorgelagerten Tasks erzeugten Werten. Es gibt zwei grundlegende Formen — Key-Value-Parameter und JSON-Array-Parameter — je nach Task-Typ wird die eine oder die andere Form unterstützt.

Hinweis: Manche Tasks unterstützen Parametrisierung ohne eigenes Parameter-Feld, z. B. dbt-Kommandos oder die Verzweigungslogik des If/else-Tasks.

**Key-Value-Parameter:** gilt für Notebook-Tasks, Python-Wheel-Tasks (nur Keyword-Argumente), SQL-Query-/-File-Tasks, Run-Job-Tasks. Job-Parameter propagieren automatisch an Tasks, die Key-Value-Parameter unterstützen. Die UI warnt, wenn Task-Parameter dieselben Schlüssel wie Job-Parameter verwenden.

**JSON-Array-Parameter:** gilt für Python-Script-Tasks, Python-Wheel-Tasks (nur positionale Argumente), JAR-Tasks, Spark-Submit-Tasks, For-each-Tasks. Der For-each-Task iteriert über dieses Array für bedingte Logik; andere Task-Typen erhalten den Array-Inhalt als Kommandozeilenargumente. Job-Parameter propagieren **nicht** automatisch an JSON-Array-Tasks, lassen sich aber über `{{job.parameters.<name>}}` referenzieren. Job-Parameterwerte unterstützen beliebige gültige JSON-Konstrukte, was dynamische Wertreferenzen zur Task-Bedingungslogik ermöglicht.

Keine Code-Beispiele in dieser Datei.

---

## 59. Parameterwerte in einem Task abrufen

**Einfach erklärt:** Diese Übersicht zeigt, wie sich Parameterwerte im Code eines Tasks (Notebook, Python-Skript, SQL-Datei) lesen lassen — Parameter umfassen nutzerdefinierte Werte, Ausgaben vorgelagerter Tasks und job-generierte Metadaten. Der Zugriff erfolgt jeweils über den Schlüssel (Parameternamen), die konkrete Syntax hängt aber vom Task-Typ ab.

**Vier gängige Methoden:** Databricks-Utilities-Widgets (`dbutils.widgets`), SQL-Named-Parameter-Syntax, dynamische Wertreferenzen, Code-Argumente.

**`dbutils` im Notebook:**

```python
# Retrieve a job-level parameter
year_value = dbutils.widgets.get("year_param")
# Use the value in your code
display(babynames.filter(babynames.Year == year_value))
```

Wichtig: Teilen sich Job- und Task-Parameter denselben Schlüssel, hat der Job-Parameter Vorrang.

Für eigenständiges Testen außerhalb eines Jobs Standardwert setzen:

```python
# Set a default (for when not running in a job)
dbutils.widgets.text("year_param", "2012", "Year Parameter")
# Retrieve a job-level parameter (will use default if it doesn't exist)
year_value = dbutils.widgets.get("year_param")
display(babynames.filter(babynames.Year == year_value))
```

**Named Parameters in SQL:**

```sql
SELECT *
FROM baby_names_prepared
WHERE Year_Of_Birth = :year_param
GROUP BY First_Name
```

**Code-Argumente:** Task-Typen mit Argument-Übergabe — Python Script, Python Wheel, JAR, Spark Submit. Bei dbt-Tasks erfolgt die Übergabe über dbt-Kommandos.

**Dynamische Wertreferenzen:** Syntax `{{job.parameters.<name>}}` in der Task-Konfiguration, z. B. ein Parameterwert `Year_{{job.parameters.year_param}}`. Weitere zugängliche dynamische Werte, z. B. `{{job.id}}`.

**Übersicht je Task-Typ:**

| Task-Typ | Konfiguration | Code |
|---|---|---|
| Notebooks | dynamische Wertreferenzen in der UI; überschreibbar via "Run a job with different settings" | Named SQL Parameters oder `dbutils.widgets` |
| Python script | Parameter als Argumente übergeben; dynamische Wertreferenzen im Parameters-Feld | Positionale Argumente oder `argparse` |
| Python wheel | dynamische Wertreferenzen in Parameterwerten | Keyword-Argumente |
| SQL | dynamische Wertreferenzen in der Konfiguration | Named Parameters |
| Pipeline (Beta) | dynamische Wertreferenzen im Parameters-Feld | Named Parameters |
| Dashboard | Dashboard-Filter mit URL-Identifiern passend zu Parameter-Keys | — |
| Power BI | nicht unterstützt | nicht unterstützt |
| dbt | dynamische Wertreferenzen als dbt-Kommandos | dbt-Kommandos |
| JAR | dynamische Wertreferenzen im Parameters-Feld | Argumente an die Main-Methode |
| Spark Submit | dynamische Wertreferenzen im Parameters-Feld | Argumente an die Main-Methode |
| Run Job | dynamische Wertreferenzen für Job-Parameter | — |
| If/else condition | dynamische Wertreferenzen in der Condition | — |
| For each | dynamische Wertreferenzen in Inputs | abhängig vom verschachtelten Task-Typ |
| Clean room notebook | dynamische Wertreferenzen in der UI | Named SQL Parameters oder `dbutils.widgets` |

---

## 60. Dynamische Wertreferenzen

**Einfach erklärt:** Dynamische Wertreferenzen sind Platzhalter in doppelten geschweiften Klammern (`{{ }}`), die bei der Konfiguration von Jobs und Tasks verfügbar sind und beim Job-Lauf automatisch durch String-Literale ersetzt werden — etwa Job-Metadaten (ID, Name, Run-ID), erzeugte Informationen, Repair-Versuche, Task-Ergebniszustände sowie nutzerkonfigurierte Job-/Task-Parameter. Damit lassen sich Task-Konfigurationen dynamisch statt fest verdrahtet gestalten.

**Syntax und Regeln:** Beispiel: `{"job_run_id": "job_{{job.run_id}}"}` mit Run-ID `550315892394120` ergibt `job_550315892394120`.

**Wichtige Einschränkungen:**
- Der Inhalt der doppelten geschweiften Klammern wird **nicht** als Ausdruck ausgewertet — keine Operationen/Funktionen innerhalb von `{{ }}` möglich.
- Syntaxfehler werden stillschweigend als Literal-String übernommen.
- Ungültige Referenzen aus bekannten Namespaces (z. B. `{{job.notebook_url}}`) erzeugen Fehlermeldungen.

**Kategorien:**

- Job-Referenzen: `{{job.id}}`, `{{job.name}}`, `{{job.run_id}}`, `{{job.repair_count}}`, `{{job.start_time.<argument>}}`, `{{job.parameters.<name>}}`, `{{job.trigger.type}}`
- Task-Referenzen: `{{task.name}}`, `{{task.run_id}}`, `{{task.execution_count}}`, `{{task.notebook_path}}`, `{{tasks.<task_name>.run_id}}`, `{{tasks.<task_name>.result_state}}`
- Workspace-Referenzen: `{{workspace.id}}`, `{{workspace.url}}`
- Backfill-Referenzen: `{{backfill.day}}`, `{{backfill.iso_date}}`, `{{backfill.month}}`, `{{backfill.year}}`

**Datum/Zeit-Argumente:** Zeitbasierte Variablen unterstützen: `iso_weekday`, `is_weekday`, `iso_date`, `iso_datetime`, `year`, `month`, `day`, `hour`, `minute`, `second`, `timestamp_ms`.

**SQL-Ausgabe referenzieren:** Nachgelagerte Tasks können die Ausgabe eines vorgelagerten SQL-Tasks referenzieren: `{{tasks.<task_name>.output.rows}}`, `{{tasks.<task_name>.output.first_row}}`, `{{tasks.<task_name>.output.first_row.<column_alias>}}`. Ausgaben sind auf 1.000 Zeilen und 48 KB begrenzt, 7 Tage aufbewahrt.

**Veraltete Referenzen:** Ältere Variablen wie `{{job_id}}`, `{{run_id}}`, `{{start_date}}`, `{{task_retry_count}}` sind zugunsten der neuen namespaced Syntax veraltet.

---

## 61. Task Values: Informationen zwischen Tasks weitergeben

**Einfach erklärt:** Task Values sind eine Databricks-Utilities-Subutility (`taskValues`), mit der sich beliebige Werte zwischen Tasks eines Jobs übergeben lassen — ein Task setzt mit `dbutils.jobs.taskValues.set()` ein Key-Value-Paar, ein nachgelagerter Task liest es über Task-Namen und Key wieder aus. So können zur Laufzeit ermittelte Ergebnisse (z. B. eine Produktliste oder ein Bestellstatus) an folgende Tasks weitergereicht werden, ohne den Umweg über eine Tabelle.

Hinweis: `dbutils.jobs.taskValues.set()`/`.get()` sind Python-Funktionen und funktionieren nur in Python-Notebooks. Über dynamische Wertreferenzen lassen sich Task Values jedoch in allen parameterfähigen Tasks referenzieren.

**Task Values setzen.** Schlüssel müssen Strings und (bei mehreren Werten) eindeutig sein. Nur JSON-valide Werte, maximal 48 KiB.

Statischer String:

```python
dbutils.jobs.taskValues.set(key = "fave_food", value = "beans")
```

Query-Ergebnisse:

```python
from pyspark.sql.functions import col
order_num = dbutils.widgets.get("order_num")
query = (spark.read.table("orders")
  .orderBy(col("updated"), ascending=False)
  .select(col("order_status"))
  .where(col("order_num") == order_num))
dbutils.jobs.taskValues.set(key = "record_count", value = query.count())
dbutils.jobs.taskValues.set(key = "order_status", value = query.take(1)[0][0])
```

Listen:

```python
prod_list = list(spark.read.table("products").select("prod_id").distinct().toPandas()["prod_id"])
dbutils.jobs.taskValues.set(key = "prod_list", value = prod_list)
```

**Task Values referenzieren.** Empfohlen: dynamische Wertreferenz `{{tasks.<task_name>.values.<value_name>}}` — z. B. für `prod_list` aus Task `product_inventory`: `{{tasks.product_inventory.values.prod_list}}`.

Alternative — `dbutils.jobs.taskValues.get()`:

```python
order_status = dbutils.jobs.taskValues.get(taskKey = "order_lookup", key = "order_status", debugValue = "Delivered")
```

Benötigt den Namen des vorgelagerten Tasks, optional einen `debugValue` für interaktives Testen.

**Ansehen:** Task-Value-Ausgaben erscheinen im Output-Panel der Task-Run-Details.

---

## 62. Weitere Airflow-Operatoren: SQL, COPY INTO und DLT-Pipeline-Trigger

**Einfach erklärt:** Über die in Abschnitt 50 beschriebenen jobauslösenden Operatoren (`DatabricksRunNowOperator`, `DatabricksSubmitRunOperator`, `DatabricksCreateJobsOperator`) hinaus bietet der Databricks-Airflow-Provider weitere Operatoren. Damit lassen sich SQL-Statements und Dateiladevorgänge direkt aus Airflow-DAGs heraus orchestrieren — nützlich für gemischte SQL-/Notebook-/ML-Pipelines ohne den Umweg über einen vorab in Databricks angelegten Job.

| Operator | Zweck |
|---|---|
| `DatabricksSqlOperator` | führt beliebige SQL-Statements auf Databricks-Compute (u. a. SQL-Warehouses) aus, z. B. `CREATE TABLE` |
| `DatabricksCopyIntoOperator` | erzeugt idempotente `COPY INTO`-Statements zum Laden von Dateien aus Cloud-Speicher in Zieltabellen |
| `PythonOperator` | kombiniert mit Databricks-Operatoren für eigene Python-Logik, z. B. Abruf externer APIs |
| `LocalFilesystemToWasbOperator` (bzw. S3-/GCS-Pendants) | überträgt lokale Dateien in Cloud-Speicher als Zwischenschritt vor `COPY INTO` |

**Beispiel-Pipeline (Wetterdaten):** `DatabricksSqlOperator` legt eine Delta-Tabelle an → `PythonOperator` ruft eine Wetter-API ab und schreibt die Antwort als JSON → ein Dateitransfer-Operator lädt die JSON-Datei in Cloud-Speicher hoch → `DatabricksCopyIntoOperator` lädt sie idempotent in die Zieltabelle.

**Weitere Ergänzungen:** `DatabricksSubmitRunOperator` wurde auf die Jobs-API v2.1 angehoben (feingranularere Zugriffskontrolle); Möglichkeit, Delta-Live-Tables-Pipelines direkt aus Airflow auszulösen; Parameterübergabe für JAR-Task-Typen; Angabe von Branch/Tag bei Databricks Repos als Quelle; Azure-Active-Directory-Token-Authentifizierung als Alternative zu Personal Access Tokens.
