# Manuelle Bundle-Erstellung und Ressourcen-Migration

Ein vollständiges Beispiel für ein Bundle ohne Template ("baby-names") sowie die zwei Wege, bestehende Jobs/Pipelines nachträglich in ein Bundle einzubinden (`bundle generate` + `bundle deployment bind`, oder manuell über die UI). Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Bundle manuell erstellen: Voraussetzungen](#voraussetzungen)
2. [Tutorial: baby-names-Bundle](#tutorial)
3. [Bestehende Ressourcen migrieren: Überblick](#migration-ueberblick)
4. [Programmatische Job-/Pipeline-Generierung](#programmatisch)
5. [UI-basierter Ressourcen-Import](#ui-import)
6. [Ressourcen binden](#binden)
7. [Multi-Workspace-Migrationsstrategie](#multi-workspace)
8. [Quelle](#quelle)

---

## <a id="voraussetzungen">1. Bundle manuell erstellen: Voraussetzungen</a>

- Databricks CLI ≥ 0.218.0 (`databricks -v`).
- konfigurierte CLI-Authentifizierung (U2M-Authentifizierung reicht zum Testen).
- Remote-Workspace mit aktivierten Workspace-Dateien.

## <a id="tutorial">2. Tutorial: baby-names-Bundle</a>

### Schritt 1 — Bundle-Verzeichnis initialisieren

Ein leeres Verzeichnis anlegen und hineinwechseln. Optional ein Git-Repository nutzen — Databricks empfiehlt, es sauber zu halten, um unnötige Datei-Synchronisation zu vermeiden.

### Schritt 2 — Zwei Notebooks erstellen

**`retrieve-baby-names.py`:**

```python
# Databricks notebook source
import requests
response = requests.get('http://health.data.ny.gov/api/views/jxy9-yhdk/rows.csv')
csvfile = response.content.decode('utf-8')
dbutils.fs.put("/Volumes/main/default/my-volume/babynames.csv", csvfile, True)
```

**`filter-baby-names.py`:**

```python
# Databricks notebook source
babynames = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load("/Volumes/main/default/my-volume/babynames.csv")
babynames.createOrReplaceTempView("babynames_table")
years = spark.sql("select distinct(Year) from babynames_table").toPandas()['Year'].tolist()
years.sort()
dbutils.widgets.dropdown("year", "2014", [str(x) for x in years])
display(babynames.filter(babynames.Year == dbutils.widgets.get("year")))
```

### Schritt 3 — Bundle-Schema generieren (optional, empfohlen)

Für IDE-Unterstützung (VS Code, PyCharm, IntelliJ):

```bash
databricks bundle schema > bundle_config_schema.json
```

Kommentar in der Konfigurationsdatei ergänzen: `# yaml-language-server: $schema=bundle_config_schema.json`.

### Schritt 4 — Bundle-Konfigurationsdatei erstellen

`databricks.yml` (`<workspace-url>` ersetzen):

```yaml
# yaml-language-server: $schema=bundle_config_schema.json
bundle:
  name: baby-names
resources:
  jobs:
    retrieve-filter-baby-names-job:
      name: retrieve-filter-baby-names-job
      job_clusters:
        - job_cluster_key: common-cluster
          new_cluster:
            spark_version: 12.2.x-scala2.12
            node_type_id: i3.xlarge
            num_workers: 1
      tasks:
        - task_key: retrieve-baby-names-task
          job_cluster_key: common-cluster
          notebook_task:
            notebook_path: ./retrieve-baby-names.py
        - task_key: filter-baby-names-task
          depends_on:
            - task_key: retrieve-baby-names-task
          job_cluster_key: common-cluster
          notebook_task:
            notebook_path: ./filter-baby-names.py
targets:
  development:
    workspace:
      host: <workspace-url>
```

### Schritt 5 — Validieren

```bash
databricks bundle validate
```

### Schritt 6 — Deployen

```bash
databricks bundle deploy -t development
```

Verifikation: **Workspace > Users > `<username>` > .bundle > baby-names > development > files** (beide Notebooks); **Jobs & Pipelines** (erstellter Job).

### Schritt 7 — Job ausführen

```bash
databricks bundle run -t development retrieve-filter-baby-names-job
```

Die zurückgegebene **Run URL** im Browser öffnen.

### Schritt 8 — Aufräumen

```bash
databricks bundle destroy
```

**Hinweis:** Entfernt nur deployte Ressourcen, nicht Nebeneffekte wie die während der Ausführung erzeugte CSV-Datei.

## <a id="migration-ueberblick">3. Bestehende Ressourcen migrieren: Überblick</a>

`bundle generate` erzeugt automatisch Konfiguration für bestehende Workspace-Ressourcen. Nach Generierung und Deployment verknüpft `bundle deployment bind` Bundle-Ressourcen mit ihren Workspace-Gegenstücken.

## <a id="programmatisch">4. Programmatische Job-/Pipeline-Generierung</a>

1. Die Ressourcen-ID aus dem **Job details**- bzw. **Pipeline details**-Panel der UI ermitteln, oder CLI-List-Befehle nutzen.
2. Den passenden Generate-Befehl mit der ID ausführen.
3. Das System erstellt eine Konfigurationsdatei im `resources`-Ordner des Bundles und lädt Artefakte nach `src` herunter.

**Für Spark-Pipelines:** das vollständige Spark-Pipeline-Projekt (mit `spark-pipeline.yml`) in den `src`-Ordner des Bundles verschieben, dann den Pipeline-Generierungsbefehl ausführen.

```bash
databricks bundle generate job --existing-job-id 6565621249
databricks bundle generate pipeline --existing-pipeline-id 6565621249
databricks pipelines generate --existing-pipeline-dir src/my_pipeline
```

## <a id="ui-import">5. UI-basierter Ressourcen-Import</a>

**Job:** **Jobs & Pipelines** → Job-Namen öffnen → Menü → **Edit as YAML** → YAML in die Bundle-Konfiguration kopieren → referenzierte Python-Dateien/Notebooks herunterladen → Dateipfad-Referenzen auf lokale Pfade aktualisieren (z. B. `../src/hello.ipynb`).

**Pipeline:** **Jobs & Pipelines** → Filter **Pipelines** → Pipeline öffnen → Menü-Icon → **View settings YAML** → YAML in die Konfiguration kopieren → referenzierte Artefakte herunterladen und hinzufügen → Referenzen auf lokale Pfade aktualisieren.

## <a id="binden">6. Ressourcen binden</a>

```bash
databricks bundle deployment bind hello_job 6565621249
databricks bundle deployment unbind hello_job
```

## <a id="multi-workspace">7. Multi-Workspace-Migrationsstrategie</a>

Separate Targets in `databricks.yml` definieren, Konfiguration für die Dev-Umgebung generieren, produktionsspezifische Einstellungen anpassen, dann Ressourcen je Workspace einzeln binden, bevor in jedes Target deployt wird:

```bash
databricks bundle generate job --existing-job-id <dev_job_id> --target dev
databricks bundle deployment bind my_job <dev_job_id> --target dev
databricks bundle deployment bind my_job <prod_job_id> --target prod
databricks bundle deploy --target dev
databricks bundle deploy --target prod
```

## <a id="quelle">8. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/manual-bundle
- https://docs.databricks.com/aws/en/dev-tools/bundles/migrate-resources

**Stand:** 2026-08-21.
