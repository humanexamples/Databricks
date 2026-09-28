# Beispiele (bundle-examples-Repository)

Katalog vollständiger Bundle-Beispiele aus dem offiziellen `bundle-examples`-GitHub-Repository, nach Anwendungsfall gruppiert. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Apps und Dashboards](#apps-dashboards)
2. [Job-Workflows](#jobs)
3. [Infrastruktur und Daten](#infrastruktur)
4. [Fortgeschrittene Muster](#fortgeschritten)
5. [Quelle](#quelle)

---

## <a id="apps-dashboards">1. Apps und Dashboards</a>

| Beispiel | Beschreibung |
|---|---|
| `app_with_database` | Databricks App, unterstützt von einer OLTP-Postgres-Datenbank |
| `app_with_genie_space` | Bundle mit einer App, die einen Genie-Agent nutzt |
| `databricks_app` | grundlegendes App-Definitionsbeispiel |
| `dashboard_nyc_taxi` | AI/BI-Dashboard plus Job, der einen Snapshot des Dashboards erfasst und per E-Mail versendet |
| `genie_space_nyc_taxi` | Genie-Agent, der Fragen zur Tabelle `samples.nyctaxi.trips` beantwortet |

## <a id="jobs">2. Job-Workflows</a>

| Beispiel | Beschreibung |
|---|---|
| `job_backfill_data` | SQL-Task mit Datumsparametern für historische Datenverarbeitung (vgl. [09 Backfill-Jobs.md](../../07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/02%20Job%20erstellen%20und%20konfigurieren/09%20Backfill-Jobs.md)) |
| `job_conditional_execution` | Job mit bedingter Task-Ausführung basierend auf Data-Quality-Checks |
| `job_file_arrival` | Job mit Datei-Ankunfts-Trigger zur automatischen Verarbeitung neuer Dateien |
| `job_read_secret` | Secret-Scope-Integration in Job-Tasks |
| `job_table_update_trigger` | ereignisgesteuerter Workflow, ausgelöst durch Tabellen-Updates |
| `job_with_multiple_wheels` | mehrere Python-Wheel-Abhängigkeiten in einem Job |
| `job_with_run_job_tasks` | Orchestrierung mehrerer Jobs über `run_job_task` |
| `job_with_sql_notebook` | Ausführung eines SQL-Notebook-Tasks |

## <a id="infrastruktur">3. Infrastruktur und Daten</a>

| Beispiel | Beschreibung |
|---|---|
| `database_with_catalog` | OLTP-Database-Instance plus Database-Catalog |
| `development_cluster` | Definition und Nutzung eines All-Purpose-Clusters |
| `metric_view` | Unity-Catalog Metric View, abfragbar über die `MEASURE()`-SQL-Funktion |
| `pipeline_with_schema` | Pipeline mit Schema-Verwaltung |

## <a id="fortgeschritten">4. Fortgeschrittene Muster</a>

| Beispiel | Beschreibung |
|---|---|
| `private_wheel_packages` | private Paketverteilung aus Jobs heraus (siehe [21 Private Artefakte.md](21%20Private%20Artefakte.md)) |
| `python_wheel_poetry` | Wheel-Build auf Basis von Poetry |
| `serverless_job` | Ausführung auf Serverless Compute |
| `share_files_across_bundles` | Datei-Sharing über Bundle-Grenzen hinweg (siehe [08 Zusammenarbeit und gemeinsame Dateien.md](08%20Zusammenarbeit%20und%20gemeinsame%20Dateien.md)) |
| `spark_jar_task` | Ausführung eines Java-Artefakts |
| `target_includes` | Job-Konfigurationen über verschiedene Umgebungen hinweg organisieren, ohne Duplizierung |
| `vector_search_product_discovery` | semantische Produktsuche mit Databricks Vector Search |
| `write_from_job_to_volume` | Schreiboperation von einem Job in ein Unity-Catalog-Volume |

**Weitere inline dokumentierte Konfigurationsmuster:** JAR-Uploads nach Unity Catalog, Dashboard-Parametrisierung über Catalog/Schema, Job auf Serverless Compute mit Environment-Spezifikation, Job-Parametrisierung und -Zeitplanung, Pipeline auf Serverless Compute mit stündlichem Trigger.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/examples

**Stand:** 2026-08-26.
