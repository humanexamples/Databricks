# Build und Entwicklung

## 1. Überblick

Pipeline-Building umfasst: Daten laden/transformieren, Datenqualität prüfen, in Zieltabellen schreiben, Identitäten/Berechtigungen verwalten, im Editor entwickeln/debuggen/versionieren.

## 2. Der Lakeflow Pipelines Editor (Multi-File-Editor)

Standard-IDE: code-first, ordnerbasiert, selektive Ausführung, Data Previews, Pipeline-Graph, Versionskontrolle, Code-Reviews, geplante Ausführung.

**Kernbestandteile:**
1. Pipeline-Asset-Browser — Assets erstellen/löschen/umbenennen/organisieren, Config-Shortcuts.
2. Multi-File-Code-Editor mit Tabs.
3. Pipeline-Toolbar — Konfiguration + Ausführungsaktionen.
4. Interaktiver Pipeline-Graph — Data Previews, tabellenbezogene Aktionen.
5. Tabellen-Ausführungs-Insights zum letzten Lauf.
6. Issues-Panel — Fehler/Warnungen/Insights, Navigation zur Fehlerstelle.
7. Selektive Ausführung — z. B. **Run file**.
8. Genie Code — agentenbasiert (siehe Abschnitt 9).

**Neue ETL-Pipeline:** **New → ETL pipeline** → Default: Unity Catalog, Current Channel, Serverless Compute. Leere Startdatei `my_transformation` (Sprache umschaltbar). Einstieg über **Create with Genie Code** oder **Use sample code**. Kebab-Menü: **Add existing source code**, **Set up as source controlled** (siehe Abschnitt 6), **Use Hive metastore**.

Alternative Wege: Workspace-Browser (Ordner → **Create → ETL pipeline**), **Jobs & Pipelines → New → ETL Pipeline**, CLI-Gruppe `databricks pipelines`.

**Standard-Ordnerstruktur:**

| Ordner | Inhalt |
|---|---|
| `<pipeline_root_folder>` | Root mit allen Ordnern/Dateien |
| `transformations` | Quellcode (Python/SQL mit Tabellendefinitionen) |
| `explorations` | Nicht-Quellcode (Notebooks, Queries) |
| `utilities` | Nicht-Quellcode-Python-Module, importierbar |

- Quellcode-Dateien: `*.py`, `*.sql`, `*.md` (Doku, beim Update ignoriert); Code in einer Datei kann Objekte aus anderer Datei referenzieren.
- Nicht-Quellcode-Dateien: im Root, werden nicht ausgewertet.
- Externe Dateien: außerhalb des Root-Ordners.

> **Wichtig:** Dateien/Ordner nur über den Pipeline-Asset-Browser (Tab **Pipeline**) verwalten — Verschieben/Umbenennen über Workspace-Browser oder Tab **All files** beschädigt die Pipeline-Konfiguration.

**Praxisbeispiel:** `transformations` oft je Medaillon-Schicht in `.sql`-Dateien geteilt (`bronze_ingestion.sql`, `silver_transformation.sql`, `gold_analytics.sql`) — Konvention, keine Pflicht (alle Dateien eines Ordners werden gemeinsam ausgewertet).

**Fünf Ausführungsoptionen:**

| # | Option | Details |
|---|---|---|
| 1 | Gesamte Pipeline | **Run pipeline** / **... with full table refresh**; zusätzlich **Dry run** (nur Validierung) |
| 2 | Einzelne Datei | **Run file** / **... with full table refresh** — andere Dateien nicht ausgewertet, referenzierte Tabellen nutzen letzte materialisierte Version, Graph ggf. unvollständig |
| 3 | Einzelne Tabelle | **Run table** / **Refresh table** / **Full refresh table** — nur ST/MV, nicht Sinks/Views |
| 4 | Ausgewählte Tabellen | Graph → **Select table for refresh** → **Run** / **Run with full refresh** |
| 5 | Ausgewählter Code | SQL markieren → **Run selected code** — Ausgabe im Tab **Query Results**, keine Materialisierung |

Nach Datei-Debugging: gesamte Pipeline für End-to-End-Prüfung ausführen (Empfehlung).

**Graph/Previews/Insights:** Pipeline-Graph zeigt Abhängigkeiten + Knoten-Lebenszyklus (validiert/laufend/fehlerhaft); Klick → Preview + Definition. Notebooks in `explorations` laufen bei Updates standardmäßig nicht mit. Panels: **Tables** (Status/Metriken, MV: **Incrementalization**-Spalte), **Performance** (Query-Historie/-Pläne), **Issues panel** (inkl. **Diagnose error** für Genie Code), **Event log**.

**Konfiguration im Editor:**
- **Settings:** Root-Ordner, Quellcode, Compute, Benachrichtigungen, Advanced.
- **Schedule:** ein/mehrere Zeitpläne (erzeugt Job).
- **Share:** Berechtigungen (siehe Abschnitt 10).
- **Event Log:** Settings → Advanced settings → Edit advanced settings → Event logs → Publish to catalog. Standardmäßig nur Owner-abfragbar.
- **Pipeline environment:** Settings → Pipeline environment → Edit environment — Abhängigkeiten wie `requirements.txt`; Versionen mit `==` pinnen (empfohlen). Gilt für alle Quelldateien.
- **Notifications:** E-Mail bei Ereignissen; benutzerdefiniert über Python-Event-Hooks.

**Einschränkungen des Editors:**
- Data Previews nicht für reguläre (nicht materialisierte) Views.
- Python-Module in UDFs: Pfad muss innerhalb der UDF selbst an `sys.path` angehängt werden.
- `%pip install` in Dateien nicht unterstützt → Pipeline-Umgebung (Settings) oder Notebook nutzen.
- Workspace-Browser fokussiert die Pipeline nicht automatisch, wenn zuerst eine `explorations`-Datei/Notebook geöffnet wird.

## 3. Notebook-Entwicklungserfahrung (Legacy)

- **Veraltet/Public Preview**, nicht mehr neu aktivierbar, nur für Workspaces, die zuvor explizit dagegen optiert haben (gegen Wechsel zum neuen Editor); wird entfernt.
- Verbindung: Compute-Dropdown im Notebook listet alle Pipelines, die es als Quellcode nutzen.
- Voraussetzung: bestehende Pipeline mit Notebook-Quellcode + Owner-Status oder `CAN_MANAGE`.
- Einschränkungen: nur Databricks-Notebooks (keine Workspace-Dateien); Web-Terminal bei verbundenem Notebook nicht verfügbar.
- Validieren: **Validate**-Button, `Shift+Enter`, oder Zellen-Dropdown **Validate Pipeline**.
- Update starten: **Start**-Button; Status (Starting/Validating/Stopping) im oberen Panel; Fehler inline rot; untere Panels: Event Log, Dataflow-Graph; Treiber-Logs/Spark-UI über **View**-Menü.

## 4. Python-Module importieren (Git-Ordner / Workspace-Dateien)

**Weg 1 — Utility-Datei in der Pipeline** (pipeline-spezifisch): **Add → Utility** → z. B. `my_utils.py` im Ordner `utilities`; Root-Ordner wird automatisch an `sys.path` angehängt.

```python
from utilities import my_utils
```

**Weg 2 — Pipeline-Umgebung** (geteilte Module über mehrere Pipelines): `.py`-Dateien, Wheels (`.whl`) oder unverpackte Projekte mit `pyproject.toml`. Settings → Pipeline environment → Edit environment, z. B. `/Volumes/libraries/path/to/python_files/file.py`, `/Workspace/libraries/path/to/wheel_files/file.whl` oder `-e /Workspace/Users/<user_name>/path/to/add/`.

**Weg 3 — `import`-Anweisung:**

```python
import sys, os
sys.path.append(os.path.abspath('<module-path>'))
from my_module import *
```

**Praxisbeispiel:** `clickstream_raw_module.py` definiert `create_clickstream_raw_table(spark)` (mit `@dp.table`); `clickstream_prepared_module.py` importiert diese und definiert `create_clickstream_prepared_table(spark)` mit Expectations (`@dp.expect`, `@dp.expect_or_fail`); Pipeline-Datei ruft beide Funktionen und definiert zusätzlich eine eigene Tabelle:

```python
import sys, os
sys.path.append(os.path.abspath('<module-path>'))

from pyspark import pipelines as dp
from clickstream_prepared_module import *
from pyspark.sql.functions import *

create_clickstream_prepared_table(spark)

@dp.table(comment="A table containing the top pages linking to the Apache Spark page.")
def top_spark_referrers():
  return (
    spark.read.table("catalog_name.schema_name.clickstream_prepared")
      .filter(expr("current_page_title == 'Apache_Spark'"))
      .withColumnRenamed("previous_page_title", "referrer")
      .sort(desc("click_count"))
      .select("referrer", "click_count")
      .limit(10)
  )
-- Ergebnis: Top-10-Referrer-Seiten zur Apache_Spark-Seite nach Klickanzahl
```

- Git-Ordner-Import: Pfad braucht Präfix `/Workspace/`.
- Kein `sys.path`-Anhängen nötig bei: Modul im selben Verzeichnis wie importierende Datei, oder Import aus dem Root eines Git-Ordners.

## 5. Lokal entwickeln

Python-Quellcode: lokal schreiben/testen, dann validieren/deployen/als Update ausführen. Lakeflow ist Obermenge von SDP: reiner SDP-Code läuft lokal **und** auf Databricks; Lakeflow-spezifische Funktionen (`AUTO CDC`, Expectations) nur auf Databricks. Modul `pyspark.pipelines` (als `dp`) gibt IDE-Syntaxprüfung/Autovervollständigung/Typprüfung.

**Transformationslogik lokal testbar halten** — reine PySpark-Funktion, getrennt vom `dp`-Decorator:

```python
# transformations/clean.py — pure PySpark, unit-testable on its own
def clean_orders(df):
    return df.filter("quantity > 0").withColumn("amount_usd", df.amount.cast("double"))

# pipeline file — a thin dp wrapper that imports and calls the logic
from pyspark import pipelines as dp
from transformations.clean import clean_orders

@dp.table(name="orders_silver")
def orders_silver():
    return clean_orders(spark.readStream.table("orders_bronze"))
```

Geteilte Logik → als Wheel verpackbar.

**Drei Testebenen:**
- **Unit-Tests** (`pytest`) — rein lokal, keine Pipeline-Runtime.
- **Validierung (Dry Run)** — lokal via `spark-pipelines` CLI oder gegen den Workspace via `databricks pipelines dry-run`, jeweils ohne zu schreiben.
- **Expectations / `AUTO CDC`** — Runtime-Funktion, **nur auf Databricks**, nicht lokal.

**Von lokal nach Databricks:**

```bash
databricks pipelines init      # scaffold a pipeline project
databricks pipelines dry-run   # validate the pipeline graph without publishing data
databricks pipelines deploy    # deploy the project to your workspace
databricks pipelines run       # run an update
```

Updates laufen im Workspace (nicht lokal) auf konfigurierter Compute. Interoperabel mit `bundle`-Befehlen (Declarative Automation Bundles).

| Werkzeug | Details |
|---|---|
| Databricks CLI (`pipelines`) | Deploy/Run direkt aus lokaler Umgebung |
| Declarative Automation Bundles | Deploy jeder Komplexität (1 Datei bis Multi-Pipeline/Job) |
| Databricks-IDE-Erweiterung (VS Code) | Sync lokal ↔ Workspace + Bundle-Deploy |
| Workspace-Dateien | Hochladen, dann Import in Pipeline |
| Git-Ordner | Sync über Git-Repo |

## 6. Source Control mit Declarative Automation Bundles

- **Traceability** (Git-Historie), **Testing** (Dev-Workspace-Validierung, eigener Branch/Folder/Schema je Entwickler), **Collaboration** (Push nach Test), **Governance** (CI/CD-Standards).
- **Klarstellung:** Bundle = Packaging-/Deployment-Format, kein ETL-Framework — Datenlogik bleibt in Lakeflow-Pipelines (`@dp.table`, `CREATE STREAMING TABLE`, Expectations, `AUTO CDC`); Bundle definiert nur das Deployment.

**Neue source-controllte Pipeline** (Voraussetzung: konfigurierter Git-Folder, Lakeflow Pipelines Editor):
1. **New → ETL pipeline**.
2. Kebab-Menü → **Set up as source-controlled**.
3. **Create new project** → Git-Folder wählen.
4. Dialog **Create an asset bundle**: Bundle-Name, Initial catalog, **Use a personal schema** (isoliert Änderungen), Initial language.
5. **Create and deploy** → Bundle mit Pipeline im Git-Folder.

Bundle enthält: `databricks.yml` (Variablen, Ziel-Workspace-URLs, Berechtigungen — Bundle-Root) + Ordner `resources` (Ressourcendefinitionen). Beispiel-Bundle: Explorations-Notebook, 2 Transformations-Dateien, 1 Utility-Datei, Job-YAML, Pipeline-YAML (**muss bearbeitet werden**, sonst überschreibt der nächste Deploy auch UI-Änderungen!), README.

- Ausführen: **Run file** (Transformation) / **Run pipeline** (gesamt).
- Änderungen explizit nach Git pushen (Git-Icon / Kebab → **Git...**); Config-/Dateiänderungen werden erst beim expliziten Bundle-Deploy in den Ziel-Workspace propagiert.
- Bestehende Pipeline → zu bereits source-controlltem Bundle hinzufügbar (siehe Abschnitt 7).

## 7. Konvertierung einer bestehenden Pipeline in ein Bundle-Projekt

Voraussetzungen: Databricks CLI **≥ 0.218.0**, Pipeline-ID, Workspace-Autorisierung.

```bash
# Schritt 1 — Projektordner
mkdir -p ~/source/my-pipelines/ingestion/events/my-bundle
cd ~/source/my-pipelines/ingestion/events/my-bundle
databricks bundle init
-- Ergebnis: databricks.yml im neuen Projekt-Home
```

```bash
# Schritt 2 — Pipeline-Konfiguration generieren
databricks bundle generate pipeline --existing-pipeline-id <pipeline-id> --profile <profile-name>
-- Ergebnis: Bundle-Config in resources/, referenzierte Artefakte in src/
```

Existiert bereits `spark-pipeline.yml` (SDP-Projekt): nach `src` kopieren, dann `databricks pipelines generate` für Bundle-Config.

```
# Schritt 3 — Projektstruktur
├── databricks.yml
├── resources/
│   └── {your-pipeline-name.pipeline}.yml
└── src/
    └── {source folders and files...}
```

```bash
# Schritt 4 — an bestehende Pipeline binden
databricks bundle deployment bind <pipeline-name> <pipeline-ID> --profile <profile-name>
```
`<pipeline-name>` = Präfix des `.pipeline.yml`-Dateinamens (z. B. `ingestion_data_pipeline` bei `ingestion_data_pipeline.pipeline.yml`).

```bash
# Schritt 5 — Deployen
databricks bundle deploy --target <target-name> --profile <profile-name>
```
`--target` erforderlich (z. B. `development`, `production`).

### Targets (Umgebungen)

```yaml
bundle:
  name: orders_pipeline

variables:
  catalog:
    description: Unity Catalog to write to
    default: dev_catalog

targets:
  dev:
    mode: development
    default: true
    variables:
      catalog: dev_catalog

  prod:
    mode: production
    variables:
      catalog: prod_catalog
    run_as:
      service_principal_name: '12345678-90ab-cdef-1234-567890abcdef'
```

- `mode: development` → persönliches Scratch-Deployment (`[dev username]`-Präfix, Schedules pausiert).
- `mode: production` → deaktiviert diese Defaults; mit `run_as` läuft die Pipeline als Service Principal (empfohlen für Staging/Prod; `service_principal_name` = Application ID, nicht Anzeigename).

```bash
databricks bundle validate --target prod
databricks bundle deploy --target prod
databricks bundle run orders_pipeline --target prod
```

**Parameter (SQL)** via `${source_catalog}` / **Configuration (Python)** via `spark.conf.get("source_catalog")`:

```yaml
resources:
  pipelines:
    orders_pipeline:
      name: orders-pipeline
      parameters:
        source_catalog: ${var.catalog}
        source_schema: raw
      configuration:
        source_catalog: ${var.catalog}
        source_schema: raw
```

### CI/CD

PR-Baseline: `pytest` (Transformationsfunktionen) → `databricks bundle validate --target <env>` → optional `databricks bundle run` in Scratch-Target (Expectations-Check). Beispiel (GitHub Actions, OIDC statt gespeichertem Token):

```yaml
name: Deploy pipeline bundle

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    env:
      DATABRICKS_AUTH_TYPE: github-oidc
      DATABRICKS_HOST: ${{ vars.DATABRICKS_HOST }}
      DATABRICKS_CLIENT_ID: ${{ vars.DATABRICKS_CLIENT_ID }}
    steps:
      - uses: actions/checkout@v4
      - name: Install Databricks CLI
        uses: databricks/setup-cli@main
      - name: Validate bundle
        run: databricks bundle validate --target staging
      - name: Deploy bundle
        run: databricks bundle deploy --target staging
```

Produktions-Deploy: hinter manueller Freigabe, mit auf Prod-Workspace beschränktem Service Principal (`databricks bundle deploy --target prod`).

| Problem | Lösung |
|---|---|
| `databricks.yml not found` bei `bundle generate` | wird nicht automatisch erstellt — `databricks bundle init` oder manuell anlegen |
| Bestehende Pipeline-Settings ≠ generierte YAML | fehlende Werte (z. B. Pipeline-ID) manuell nachtragen |

## 8. Unit Testing für Pipelines (Beta)

Validierung von Python-/SQL-Transformationslogik mit Mock-Daten im webbasierten Editor: isolierte Testausführung (Test-SparkSession leitet namensbasierte Tabellenoperationen in temporäres Test-Schema im Standardkatalog um), flexibler Umfang (Tabellen/Ketten/ganze Pipeline), `pytest`-Assertions.

**Voraussetzungen:**
- Pipeline-Berechtigung **Owner** (nicht `CAN RUN`/`CAN MANAGE`) + `USE CATALOG`/`CREATE SCHEMA` auf Standardkatalog:

```sql
GRANT USE CATALOG, CREATE SCHEMA ON CATALOG <catalog_name> TO `<principal>`;
```

- Pipeline im **getriggerten** (nicht-kontinuierlichen) Modus.
- Pipeline auf **PREVIEW**-Channel.
- **Spark Connect nicht unterstützt.**

Umstellung via UI (Advanced settings → Channel → Preview; Pipeline mode → Triggered) oder JSON:

```json
"continuous": false,
"channel": "PREVIEW"
```

**Wichtige Einschränkungen:**
- Test-Isolation nur nach **Tabellenname** — Pfad-Operationen (`/Volumes/...`, `dbfs:/...`, `s3://...`, `abfss://...`) oder Connectoren (Kafka, Auto Loader) umgehen die Isolation und wirken auf echte Produktionsdaten, auch transitiv. Jede Tabelle mit vollem Namen (`catalog.schema.table`) referenzieren/mocken. `event_log()`-TVF nicht in Tests verwenden (ggf. Produktionsdaten) — stattdessen:

```python
status = test_pipeline.run(test_spark, set(["catalog.schema.table"]))
assert status.event_log_table_name is not None
events = test_spark.table(status.event_log_table_name)
```

- Governance-/DDL-Operationen nicht unterstützt (weder in Tests noch produktivem Code): `CREATE`/`DROP`/`ALTER CATALOG`/`SCHEMA`, `GRANT`/`REVOKE`, `ALTER ... OWNER TO`, `SET`/`UNSET TAGS`, `CREATE`/`DROP POLICY`.
- Betrieblich: keine Parallelität Test/Pipeline-Update; temporäre Schemas (`redirecting_<id>`) können bei Abbruch zurückbleiben (ggf. manuell löschen); Testläufe verbrauchen reguläre Pipeline-Compute (abgerechnet); kein Full Refresh, nur selektiv.
- Tests nur aus dem webbasierten Editor, in Python (auch für SQL-Pipelines); Mock-Daten erben keine Row Filters/Column Masks.

**Ablauf:**
1. **+ (Add) → Test** (legt `tests`-Ordner an).
2. **Generate tests** in der Testdatei, oder `/tests` im Genie-Code-Agent-Modus, oder manuell:

```python
import pytest
from pyspark.pipelines.testing import TestPipeline, test_spark

test_pipeline = TestPipeline.active()
```

3. Play-Symbol (einzelner Test) oder **Run tests in file**; Ergebnisse im unteren Panel.

| API | Beschreibung |
|---|---|
| `TestPipeline.active()` | aktuelle Pipeline im Editor (Quellcode, Konfig, Standardkatalog/-schema) |
| `test_pipeline.run(test_spark, set([...]))` | synchrones, selektives Update der angegebenen Tabellen |
| `test_spark`-Fixture | Test-SparkSession mit Umleitung namensbasierter Operationen ins Test-Schema |

**Mock-Daten:**

```python
# Per SQL
test_spark.sql("""
    CREATE TABLE catalog.schema.table_name AS
    SELECT * FROM VALUES (1, 'value1'), (2, 'value2') AS t(id, name)
""")

# Per createDataFrame
df = test_spark.createDataFrame([(1, 'value1'), (2, 'value2')], schema=["id", "name"])
df.write.saveAsTable("catalog.schema.table_name")
```

Größere Mengen: `Faker` (`%pip install faker`).

**Beispiel — Aggregation testen:**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, count, count_if

@dp.table
def counts():
    return (
        spark.read.table("catalog.schema.users")
        .withColumn("valid_email", col("email").isNotNull())
        .groupBy("user_type")
        .agg(count("user_id").alias("total_count"), count_if("valid_email").alias("count_valid_emails"))
    )
```

```python
def test_counts(test_spark):
    test_spark.sql("""
        CREATE TABLE catalog.schema.wanderbricks_users AS
        SELECT * FROM VALUES
            (1, 'alice@example.com', 'Alice', 'admin'),
            (2, NULL, 'Bob', 'user')
        AS t(user_id, email, name, user_type)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.users", "catalog.schema.counts"]))
    result = test_spark.table("catalog.schema.counts")
    admin_row = result.filter("user_type = 'admin'").collect()[0]
    assert admin_row["total_count"] == 1
    # Ergebnis: total_count=1 für user_type='admin' (nur ein Mock-Datensatz mit diesem Typ)
```

**Beispiel — Auto CDC testen (verspätete/unsortierte Events):**

```python
def test_auto_cdc_late_arriving(test_spark):
    test_spark.sql("""
        CREATE TABLE catalog.schema.change_feed AS
        SELECT * FROM VALUES (1, 'Alice', 1000), (2, 'Bob', 1001) AS t(userId, name, ts)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.target_autocdc"]))

    test_spark.sql("""
        INSERT INTO catalog.schema.change_feed VALUES
            (1, 'Alice Updated', 1003),
            (2, 'Bob (stale)', 999)
    """)
    test_pipeline.run(test_spark, set(["catalog.schema.target_autocdc"]))

    result = test_spark.table("catalog.schema.target_autocdc")
    alice = result.filter("userId = 1").collect()[0]
    assert alice["ts"] == 1003
    bob = result.filter("userId = 2").collect()[0]
    assert bob["ts"] == 1001  # stale event (ts=999) wurde durch sequence_by ignoriert
```

Analog testbar: `create_auto_cdc_from_snapshot_flow()` (SCD Type 2 aus Snapshots, simuliert via Truncate+Insert), Joins mit Expectations (`@dp.expect_or_drop`) — jeweils Eingabetabellen mocken, Ausgabetabelle per `pytest` prüfen.

## 9. Genie Code im Agent-Modus (Data Engineering Agent)

Autonomer KI-Partner im Editor: Datenerkennung, Code-Generierung, Pipeline-Ausführung, Fehlerbehebung — aus einem Prompt. Ggü. Chat-Modus zusätzlich: Planung, Asset-Retrieval, Code-Ausführung, Nutzung von Pipeline-Output, Auto-Fehlerbehebung. Zugriff begrenzt durch Rechte des aufrufenden Nutzers.

**Voraussetzungen:** Partner-powered-AI-Features aktiviert (Account + Workspace); unterstützte Region.

**Nutzung:** Genie-Code-Panel → **Agent** aktivieren → Prompt (z. B. "create silver_sales_data in a new file that reads from bronze_sales_data and cleans the data and adds useful quality expectations"). Pausiert bei komplexen Aufgaben für Rückfragen; fragt vor Ausführung/Updates um Genehmigung (**Allow**, **Decline**, **Allow in this thread**, **Always allow**).

> **Wichtig:** Trotz Guardrails Restrisiko — nur vertrauenswürdige Daten, Code vor Ausführung prüfen. Rotes Stop-Icon bricht ab. Instruktionen/domänenspezifische "Skills" hinzufügbar.

**Fähigkeiten:** Data discovery, Pipeline code edits (mehrere Dateien, Diff je Datei), Pipeline execution (Datei, Dry-Run, regulär, Full Refresh — jeweils mit Bestätigung), Understanding/Improving (Transformationen zusammenfassen, unerwartete Zeilen-/Schema-Änderungen hervorheben, Ursachenforschung Datenqualität). Anwendungsfälle: neue Pipeline, Erklärung, Fehlerbehebung, inkrementellen Refresh reparieren (Incrementalization Insights).

### Migration von anderen ETL-Frameworks (Beta)

Migriert bestehendes Transformationsprojekt in Lakeflow-Pipeline (Teil von Lakebridge). **Aktuell nur: dbt- und Informatica-Projekte.**

Ablauf: Projekt hochladen (Volume/Workspace-Import) → leere Pipeline erstellen → prompten:

```
Migrate the project at /Volumes/my_catalog/my_schema/my_volume/my_project
```

Generierter Plan: Quelle lesen (Modelle/Abhängigkeiten) → Eingaben einholen (Zielsprache SQL/Python) → Zwischenrepräsentation (IR) generieren → konvertieren/validieren/reparieren (iterative Schleife). Vor Produktivsetzung: Überprüfung + Ausführung gegen Originalprojekt.

## 10. Berechtigungen für Pipelines

Databricks empfiehlt Unity Catalog für alle neuen Pipelines. Standardmäßig: MV/ST nur vom Pipeline-Owner abfragbar.

### Run-as-Identität

Updates laufen unter dem **Run-as-Nutzer** (Default: Ersteller, änderbar auf anderen Nutzer/Service Principal). Empfohlen: **Service Principal** (nicht an Einzelperson gebunden), mit minimal nötigen UC-Privilegien (`USE CATALOG` Zielkatalog, `USE SCHEMA` + passendes `CREATE` Ausgabe-Schema, `SELECT` Quellen).

### Wer darf was?

- Update ausführen: `CAN RUN`, `CAN MANAGE` oder `IS OWNER`.
- Pipeline öffnen/Details: mind. `CAN VIEW`.
- Pipeline hinter ST/MV einsehen (Nicht-Admin): zusätzlich `REFRESH`-Privileg auf der Tabelle — sonst "Pipeline not available".

**ACLs konfigurieren** (erfordert `CAN MANAGE`/`IS OWNER`): **Jobs & Pipelines** → Pipeline → **Share** → **Select User, Group or Service Principal…** → Berechtigung → **Add** → **Save**.

| Fähigkeit | CAN VIEW | CAN RUN | CAN MANAGE | IS OWNER |
|---|---|---|---|---|
| Details ansehen, auflisten | ✓ | ✓ | ✓ | ✓ |
| Spark-UI/Treiber-Logs | ✓ | ✓ | ✓ | ✓ |
| Update starten/stoppen | | ✓ | ✓ | ✓ |
| Pipeline-Cluster stoppen | | ✓ | ✓ | ✓ |
| Einstellungen bearbeiten | | | ✓ | ✓ |
| Pipeline löschen | | | ✓ | ✓ |
| Runs/Experiments bereinigen | | | ✓ | ✓ |
| Berechtigungen ändern | | | ✓ | ✓ |

**Owner ändern:** Owner = Default-Run-as-Nutzer, also ändert Owner-Wechsel auch die Ausführungsidentität (für reine Ausführungsidentität separat Run-as-Nutzer setzen). **Owner-Änderung erfordert Metastore-Admin UND Workspace-Admin.** UI: **Share** → alten Owner entfernen → neuen wählen (Service Principal empfohlen) → **Save**. Alternativ REST API (**Set pipeline permissions**):

```json
{
  "access_control_list": [
    { "user_name": "new.owner@example.com", "permission_level": "IS_OWNER" }
  ]
}
```

**Weitere Themen:**
- Treiber-Logs für Nicht-Admins (Default: nur Owner + Admins):

```json
{ "configuration": { "spark.databricks.acl.needAdminPermissionToViewLogs": "false" } }
```

- Credentials nie hartkodieren, per Secret-Scope zur Laufzeit lesen:

```python
api_token = dbutils.secrets.get(scope="orders-pipeline-secrets", key="external_api_token")
```
Secret-Werte werden in Notebook-/Log-Ausgaben automatisch zu `[REDACTED]`; Secret-ACL steuert Scope-Lesezugriff zusätzlich.

- PII: über UC-Governance auf den Zieltabellen absichern (nicht eigene Maskierungslogik im Code) — **Column Masks** (Redigieren/Hashen je Nutzergruppe), **Row Filters** (Zeilen-Einschränkung); schützt konsistent alle Konsumenten. Zusätzlich: PII auf klar benannte, dedizierte Spalten/Tabellen/Schemas beschränken.

---

**Stand:** 2026-09-14.
