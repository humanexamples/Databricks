# 03 Serverless Compute — Gesamtzusammenfassung

Konsolidierte Übersicht aller 11 Inhaltsdateien dieses Ordners mit **allen** enthaltenen Code-Beispielen. Jede Originaldatei bleibt die primäre, ausführliche Quelle — dieses Dokument dient als kompakter Überblick plus vollständige Code-Referenz an einem Ort.

## Inhalt

1. [Übersicht](#1-übersicht)
2. [Notebooks](#2-notebooks)
3. [Git Folder Serverless](#3-git-folder-serverless)
4. [Umgebung und Abhängigkeiten](#4-umgebung-und-abhängigkeiten)
5. [Best Practices](#5-best-practices)
6. [Migration von Classic zu Serverless](#6-migration-von-classic-zu-serverless)
7. [Streaming](#7-streaming)
8. [Sandbox](#8-sandbox)
9. [Einschränkungen](#9-einschränkungen)
10. [Lakehouse Replay](#10-lakehouse-replay)
11. [Serverless Compute verwalten](#11-serverless-compute-verwalten)
12. [Serverless-Infrastruktur: Netzwerkkonfiguration im großen Maßstab](#12-serverless-infrastruktur-netzwerkkonfiguration-im-großen-maßstab)
13. [Serverless-Infrastruktur: VM-Boot-Optimierung (7x schneller)](#13-serverless-infrastruktur-vm-boot-optimierung-7x-schneller)
14. [Serverless-Infrastruktur: Container-Image-Verteilung (Artifact Registry)](#14-serverless-infrastruktur-container-image-verteilung-artifact-registry)
15. [Versionless Apache Spark: Automatische Upgrades und Release Stability System](#15-versionless-apache-spark-automatische-upgrades-und-release-stability-system)

---

## 1. Übersicht

Serverless Compute ist ein von Databricks verwalteter Dienst für On-Demand-Ressourcen (Notebooks, Workflows, Lakeflow-Pipelines) ohne eigene Infrastruktur-Provisionierung — schnellerer Start, automatische Skalierung, weniger Verwaltungsaufwand. Primäre Workloads: Serverless Notebooks, Git Folder Serverless (Beta), Serverless Jobs, Serverless Lakeflow Pipelines, Streaming, AI Runtime (Preview, Serverless GPU). Separat konfigurierbare Serverless-Features: SQL Warehouses, Model Training (Forecasting), Data Quality Monitoring, Predictive Optimization.

Standardmäßig in den meisten Workspaces verfügbar, keine Enablement nötig; Workspaces mit Unity Catalog erhalten automatisch Zugriff, Workspaces ohne Unity Catalog müssen upgraden. Serverless ist ein „versionless product" — Runtime-Upgrades laufen automatisch und schrittweise, alle Workloads laufen stets auf der neuesten Runtime (separates Konzept: Environment-Versionen für Notebooks/Jobs, siehe Kapitel 4). Kostenschätzung über `system.billing.usage` und ein herunterladbares Cost-Observability-Dashboard; bis zu 24 Std. Abrechnungsverzögerung möglich. Data Quality Monitoring und Predictive Optimization laufen ebenfalls auf Serverless-Infrastruktur und werden unter der Serverless-Jobs-SKU abgerechnet. Private Repositories benötigen pre-signed URLs. Nur Lakehouse-Federation-Quellen werden als Custom Data Sources unterstützt. Serverless-Ressourcen laufen in einer eigenen, von Databricks verwalteten Serverless Compute Plane. Databricks Connect ermöglicht die Ausführung von Serverless-Workloads von lokalen Rechnern aus.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 2. Notebooks

Voraussetzung: Workspace mit aktiviertem Unity Catalog; keine zusätzlichen Berechtigungen nötig, sofern Serverless Interactive Compute aktiviert ist. Notebook-Anhängung über das Compute-Dropdown → **Serverless**; neue Notebooks nutzen dies standardmäßig beim ersten Zellenlauf. Nach Zellausführung liefert **„See performance"** SQL-/Python-Query-Metriken (alle Abfragen erscheinen in der Query History); Spark UI, Query-Profil-Download und Verbose-Metriken sind **nicht** verfügbar.

**Execution Timeout:** Standard 2,5 Std. (9.000 Sek.) für interaktive Notebooks, um „durchgehende" Abfragen zu verhindern — konfigurierbar auf Workspace-Ebene (Admin-Einstellungen) oder Notebook-Ebene über `spark.databricks.execution.timeout`. Jobs haben standardmäßig keinen Query-Execution-Timeout; maximale Serverless-Laufzeit generell 7 Tage.

Serverless nutzt Environment-Versionen statt klassischer Runtime-Versionen (siehe Kapitel 4). Unterstützte Sprachen: **Python und SQL** — Scala und R werden nicht unterstützt. Neue Notebooks verwenden standardmäßig das `.ipynb`-Format.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 3. Git Folder Serverless

**Beta.** Stellt eine einzige Serverless-Compute-Ressource bereit, die von allen Notebooks/Dateien in einem Git-Ordner gemeinsam genutzt wird — vermeidet separate Compute-Starts pro Notebook. Voraussetzungen: Projekt in einem Git-Ordner, geöffnet über den Git-Folder-Editor; existierende Root-`pyproject.toml` benötigt `environment_version >= 5`.

Nur Assets innerhalb des Git-Ordners können auf die geteilte Compute-Ressource zugreifen; in einem Notebook definierte Python-Variablen sind in einem anderen Notebook nicht sichtbar; Web-Terminals aus angehängten Notebooks laufen auf derselben Ressource.

**Aktivierung:** Workspace-Seitenbereich → Git-Ordner → „Open in editor" → Notebook/Datei öffnen → Compute-Dropdown → „Git Folder Serverless" wählen → ausführen, um die Compute-Ressource zu initialisieren.

Anders als bei Standard-Serverless-Notebooks (Abhängigkeiten pro Notebook) zentralisiert Git Folder Serverless die Python-Abhängigkeiten in einer Root-`pyproject.toml`.

**Zusammenarbeit:** Single-User-Modell — nur der startende Nutzer kann Workloads auf der Ressource ausführen; Mitarbeitende sollen das Repository in einen eigenen Git-Ordner im persönlichen Workspace-Ordner klonen (eigene Compute-Ressource/Umgebung, Austausch über Git). Einschränkung: Notebooks/Dateien mit unterschiedlichen Serverless Usage Policies erhalten separate statt einer gemeinsamen Compute-Ressource.

### Abhängigkeiten über Notebook-Befehle hinzufügen

```
%uv add cowsay
```

```
%uv sync
```

### `pyproject.toml` direkt bearbeiten

```toml
[project]
name = "my-project"
version = "0.1.0"
dependencies = [
  "simplejson==3.18.1",
]

[tool.databricks.environment]
environment_version = "5"
```

---

## 4. Umgebung und Abhängigkeiten

Konfiguration von Serverless-Umgebungen für Notebooks und Job-Tasks: Base Environments, Abhängigkeiten, Memory-/GPU-Optionen, Usage Policies.

**Base Environment** (Dropdown im Environment-Seitenpanel): **Standard** (Databricks-Standard-Libraries), **ML** (Databricks Runtime for ML Pakete), **AI** (GPU-optimiert, erfordert Accelerator-Wahl), **More** (frühere Versionen, benutzerdefinierte YAML, Workspace-Optionen). Empfehlung: neueste Version für aktuellste Notebook-Features.

**Abhängigkeiten hinzufügen:** Serverless unterstützt keine Compute-Policies/Init-Skripte — stattdessen Environment-Seitenpanel → Dependencies → Pfad/Paket eingeben → „+Add dependency" → „Apply" (installiert und startet Python-Prozess neu). Format wie `requirements.txt`; referenzierbar über Workspace-Dateien (`/Workspace/...`) oder Unity-Catalog-Volumes (`/Volumes/<catalog>/<schema>/<volume>/<path>.whl`). **Warnung:** PySpark selbst niemals als Abhängigkeit installieren — stoppt die Session mit Fehler.

Environment-Caching: installierte virtuelle Umgebungen werden gecacht, kein Neuinstallieren bei jedem Notebook-Öffnen; Job-Tasks mit gleichem Dependency-Set profitieren ebenfalls innerhalb eines Runs. Tab „Installed" zeigt installierte Pakete, „pip logs"-Link öffnet die Logs.

**Custom Environment Specification:** Abhängigkeiten in einem Notebook installieren → Kebab-Menü → „Export environment" → als Workspace-Datei oder in Unity-Catalog-Volume speichern → Wiederverwendung über „Custom" im Base-Environment-Dropdown.

### Gemeinsame Tools workspace-weit teilen

```
helper_utils/
├── helpers/
│   └── __init__.py
├── pyproject.toml
```

```toml
[project]
name = "common_utils"
version = "0.1.0"
```

Installation als Abhängigkeit über den Pfad `/Workspace/helper_utils`. Wichtig: bei Implementierungsänderung eines Custom-Python-Pakets in einem Job auf Serverless muss die Versionsnummer erhöht werden, damit Jobs die neue Implementierung übernehmen.

**AI Runtime (Serverless GPU, Public Preview):** Compute-Dropdown → „Serverless GPU" → Environment-Seitenpanel → Accelerator **A10** oder **H100** wählen → Base Environment „Standard" oder „AI" → Apply.

**High Memory Serverless Compute (Public Preview):** Standard 16 GB Gesamtspeicher, High 32 GB — Environment-Seitenpanel → Memory → „High memory" → Apply. Höhere DBU-Emissionsrate bei High Memory.

**Serverless Usage Policy (Public Preview):** Custom-Tagging für Billing-Attribution über das Environment-Seitenpanel; ist nur eine Policy zugewiesen, gilt diese standardmäßig.

### PEP-723-Format beim Source-File-Export

```python
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
```

**Environment zurücksetzen:** Pfeil neben „Apply" → „Reset to defaults" (leert Cache und installiert neu).

**Job-Task-Umgebungen:** jeder Task läuft isoliert. Notebook-Tasks nutzen standardmäßig die Notebook Environment (überschreibbar über Job-Level-Environment); Python-Script-/Wheel-Tasks benötigen explizite Environment-Konfiguration; DBT-Tasks nutzen Job-Level-Environments; JAR-Tasks unterstützen keine Workspace-Base-Environments (YAML-Specs + Environment-Version-Dropdown). Konfigurationsschritte für Python-/Wheel-Tasks: Task-Konfiguration → „Environment and Libraries" → „+ Add dependency" → Base Environment wählen → Abhängigkeiten im requirements.txt-Format → „Confirm".

**Kompatibilität:** Base Environment muss zum Compute-Typ (CPU/GPU) passen; bei GPU auf Job-Ebene muss auch das Base Environment auf Job-Ebene gesetzt sein; API-Nutzer: Kompatibilität wird zur Laufzeit geprüft, nicht bei Job-Erstellung. Architektur ist nicht garantiert — Notebooks/Jobs können auf `aarch64` oder `x86_64` laufen, auch wechselnd zwischen Runs; für Wheels mit nativen Extensions pure-Python-Wheels oder beide Architektur-Varianten mit Platform-Machine-Markern bereitstellen.

Private Package Repositories: Workspace-Admins können Default-pip-Quellen für interne/authentifizierte Repos konfigurieren (pre-signed URLs).

---

## 5. Best Practices

**Migration:** siehe Kapitel 6. Python-Abhängigkeiten in `requirements.txt` auf konkrete Versionen pinnen, sonst höhere Latenz durch abweichende Auflösung je Environment-Version:

```
numpy==2.2.2
pandas==2.2.3
```

**Temp-View-Benennung:** Serverless nutzt Spark Connect (Client-Server, lazy Auswertung von Temp-Views) — für jeden Temp-View eindeutige Namen verwenden, besonders in iterativem Code.

**Networking:** kein VPC-Peering — stattdessen Private Endpoints (VPC-intern/AWS-managed Services) oder Firewall-Konfigurationen; S3 als regionaler Dienst ohne VPC-Bindung ist davon nicht betroffen. Für Enterprise-Apps/Managed Databases: Lakeflow Connect; Egress Controls zur Überwachung/Beschränkung von Outbound-Traffic.

**Environment-Versionen:** stabile APIs bei unabhängigen Server-Upgrades, Rückwärtskompatibilität, 3-Jahre-Support-Lebenszyklus ab Release, Performance-/Security-Verbesserungen ohne Code-Änderungen.

**Dependency-Management:** keine Init-Skripte — stattdessen Serverless-Environments; Environments cachen installierte Pakete für geringere Startlatenz; pre-signed URLs für private Repositories.

**Performance-Modi:**

| Modus | Am besten für | Startzeit | Kosten |
|---|---|---|---|
| Performance-optimized (Default) | Interaktive Workloads, Notebooks | schnell | höher |
| Standard | Batch-Jobs, Pipelines | 4–6 Minuten | bis zu 70 % günstiger als Performance-optimized |

Standard-Modus ist für Notebooks nicht verfügbar.

**Streaming:** nur `Trigger.AvailableNow()`; Speicherfehler über `maxFilesPerTrigger`/`maxBytesPerTrigger` begrenzen — jeder Trigger verarbeitet alle verfügbaren Daten, was zu größeren Micro-Batches als bei zeitbasierten Triggern führt.

**Debugging:** Spark UI nicht verfügbar — Query Profile aus der Query History nutzen.

**Daten-Ingestion:** SQL-basiert (`COPY INTO`, Streaming Tables, Auto Loader) oder alternativ Partner-Connect, File-Upload-UI, OpenSharing, Lakehouse Federation.

**Nicht unterstützte Write-Targets:** Unity Catalog Iceberg REST Catalog nutzen, damit das Zielsystem direkt aus Databricks-Tabellen liest (Beispiel: Snowflake als Iceberg-Client).

**Spark-Konfiguration:** die meisten manuellen Spark-Konfigurationen werden nicht mehr unterstützt — nicht unterstützte Configs führen zu Job-Fehlern.

**Kosten-Monitoring:** Serverless Usage Policies zur Attribution, Systemtabellen für Dashboards/Alerts, Account-Level-Budget-Alerts, vorkonfigurierte Usage-Dashboards.

---

## 6. Migration von Classic zu Serverless

Serverless übernimmt Provisionierung, Skalierung, Runtime-Upgrades und Optimierung automatisch; die meisten Classic-Workloads lassen sich mit minimalen/keinen Code-Änderungen migrieren. Ausnahmen: `df.cache()` u. Ä. (noch nicht unterstützt), R-/Scala-Notebook-Workloads (bleiben auf Classic).

**6 Migrationsschritte:** (1) Voraussetzungen prüfen, (2) Code aktualisieren, (3) Workloads testen, (4) Performance-Modus wählen, (5) phasenweise migrieren, (6) Kosten überwachen.

**Voraussetzungen:**

| Voraussetzung | Aktion |
|---|---|
| Workspace für Unity Catalog aktiviert | Ggf. von Hive Metastore migrieren; Workspace upgraden |
| Networking konfiguriert | VPC-Peering durch NCCs, Private Link oder Firewall-Regeln ersetzen |
| Cloud-Storage-Zugriff | Legacy-Muster durch Unity-Catalog-External-Locations ersetzen; DBFS-Mounts mit Instance Profiles migrieren |

### Datenzugriff: Classic vs. Serverless

```python
# Classic
df = spark.read.csv("dbfs:/mnt/datalake/data.csv", header=True)
df.write.parquet("dbfs:/mnt/output/results")
df = spark.table("my_database.my_table")

# Serverless
df = spark.read.csv("/Volumes/main/sales/raw_data/data.csv", header=True)
df.write.parquet("/Volumes/main/analytics/output/results")
df = spark.table("main.my_database.my_table")  # three-level namespace
```

**Warnung:** DBFS-Zugriff ist auf Serverless eingeschränkt — alle `dbfs:/`-Pfade vor der Migration auf Unity-Catalog-Volumes umstellen.

### APIs und Code: RDD → DataFrame

```python
from pyspark.sql import functions as F

# Classic RDD parallelization → DataFrame creation
# Classic: rdd = sc.parallelize([1, 2, 3]); rdd.map(lambda x: x * 2).collect()
df = spark.createDataFrame([(1,), (2,), (3,)], ["value"])
result = df.select((F.col("value") * 2).alias("value")).collect()

# Classic flatMap → explode
# Classic: sc.parallelize(["hello world"]).flatMap(lambda l: l.split(" ")).collect()
df = spark.createDataFrame([("hello world",)], ["line"])
words = df.select(F.explode(F.split("line", " ")).alias("word")).collect()

# Classic groupByKey → DataFrame groupBy
# Classic: rdd.groupByKey().mapValues(list).collect()
df = spark.createDataFrame([("a", 1), ("b", 2), ("a", 3)], ["key", "value"])
grouped = df.groupBy("key").agg(F.collect_list("value").alias("values")).collect()

# mapPartitions → applyInPandas
import pandas as pd
def process_group(pdf: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({"total": [pdf["id"].sum()]})
result = (spark.range(100).repartition(4)
    .groupBy(F.spark_partition_id())
    .applyInPandas(process_group, schema="total long").collect())

# sc.textFile → spark.read.text
df = spark.read.text("/Volumes/catalog/schema/volume/file.txt")
```

```python
from pyspark.sql.functions import broadcast

# sc.broadcast → broadcast join
result = main_df.join(broadcast(lookup_df), "key")

# sc.accumulator → DataFrame aggregation
total = df.agg(F.sum("amount")).collect()[0][0]

# sqlContext.sql → spark.sql
result = spark.sql("SELECT * FROM main.db.table")

# df.cache() → remove caching calls
# Materialize expensive intermediate results to Delta as a workaround:
df = spark.read.parquet(path)
result = df.filter("status = 'active'")
expensive_df.write.format("delta").mode("overwrite").saveAsTable("main.scratch.temp")
result = spark.table("main.scratch.temp")
```

### Streaming-Trigger-Migration

| Spark-Trigger | Unterstützt | Hinweise |
|---|---|---|
| `Trigger.AvailableNow()` | Ja | empfohlen |
| `Trigger.Once()` | Ja | deprecated; `AvailableNow()` verwenden |
| `Trigger.ProcessingTime(interval)` | Nein | `INFINITE_STREAMING_TRIGGER_NOT_SUPPORTED` |
| `Trigger.Continuous(interval)` | Nein | auf Lakeflow-Pipelines Continuous Mode migrieren |
| Default (kein `.trigger()`) | Nein | immer explizit `.trigger(availableNow=True)` setzen |

```python
# Classic (nicht unterstützt — Default-Trigger ist ProcessingTime)
query = df.writeStream.format("delta").outputMode("append").start()

# Serverless (expliziter AvailableNow-Trigger)
query = (df.writeStream.format("delta").outputMode("append")
    .trigger(availableNow=True)
    .option("checkpointLocation", checkpoint_path)
    .start(output_path))
query.awaitTermination()

# Mit OOM-Prävention für große Quellen
query = (spark.readStream.format("delta")
    .option("maxFilesPerTrigger", 100)
    .option("maxBytesPerTrigger", "10g")
    .load(input_path)
    .writeStream.format("delta")
    .trigger(availableNow=True)
    .option("checkpointLocation", checkpoint_path)
    .start(output_path))
```

**Weitere Ersatzmuster:** DBFS-Pfade → Unity-Catalog-Volumes; Hive-Metastore-Tabellen → Unity-Catalog-Tabellen/HMS Federation; IAM Instance Profiles → Unity-Catalog-External-Locations; Custom JDBC-JARs → Lakehouse Federation; `spark.sparkContext`/`sqlContext` → direkt `spark`; Hive-Variablen (`${var}`) → SQL `DECLARE VARIABLE`/f-Strings; Init-Skripte → Serverless-Environments; Compute-scoped Libraries → Notebook-scoped/Environment-Libraries; Maven/JAR-Libraries → JAR-Task-Support (Jobs) / PyPI (Notebooks); Docker-Container → Serverless-Environments.

**Workloads testen:** (1) Schneller Kompatibilitätstest auf Classic mit Standard Access Mode + Runtime 14.3+; (2) A/B-Vergleich Classic vs. Serverless mit Output-Diff; (3) temporäre unterstützte Spark-Configs während Tests, danach entfernen.

**Performance-Modus:**

| Modus | Verfügbarkeit | Start | Am besten für |
|---|---|---|---|
| Standard | Jobs, Lakeflow Pipelines | 4–6 Minuten | kostensensitives Batch |
| Performance-optimized | Notebooks, Jobs, Lakeflow Pipelines | Sekunden | interaktiv, latenzsensitiv |

**Phasenweise Migration:** (1) neue Workloads direkt auf Serverless, (2) Low-Risk-Workloads (bereits Standard Access Mode + Runtime 14.3+), (3) komplexe Workloads mit nötigen Code-Änderungen, (4) restliche Workloads periodisch neu bewerten.

**Kosten:** Abrechnung nach DBU-Verbrauch statt Cluster-Uptime — vor Großmigration mit repräsentativen Workloads validieren.

---

## 7. Streaming

Zwei Streaming-Muster auf Serverless: **kontinuierliche** Pipelines (Sekunden-Latenz, laufen ohne Stopp) und **inkrementelle/getriggerte** Pipelines (Minuten-Latenz, verarbeiten nach Zeitplan und beenden sich). Zeitbasierte Trigger (`Trigger.ProcessingTime(interval)`, `Trigger.Continuous(interval)`) sind nicht verfügbar; **nur `Trigger.AvailableNow()`** wird unterstützt. Abfragen ohne expliziten Trigger schlagen mit `INFINITE_STREAMING_TRIGGER_NOT_SUPPORTED` fehl, da Sparks Default `Trigger.ProcessingTime("0 seconds")` auf Serverless nicht unterstützt wird.

**Empfohlene Ansätze nach Anwendungsfall:**

| Anwendungsfall | Empfohlener Ansatz |
|---|---|
| Kontinuierliche Low-Latency-ETL | Lakeflow Pipelines im Continuous Mode mit Streaming Tables |
| Cloud-Storage-Ingestion | Auto Loader in Lakeflow Pipelines **oder** Serverless Jobs mit `Trigger.AvailableNow()` |
| SaaS-/Datenbank-CDC | Lakeflow Connect Managed Connectors |
| SQL-basiertes Streaming | Streaming Tables mit SQL-Statements |
| Periodische Micro-Batches | Serverless Jobs mit `Trigger.AvailableNow()` nach Zeitplan |

### Inkrementelles Streaming — Beispiel

```python
(spark.readStream
   .format("cloudFiles")
   .option("cloudFiles.format", "json")
   .option("cloudFiles.maxFilesPerTrigger", 1000)
   .load(source_path)
   .writeStream
   .trigger(availableNow=True)
   .option("checkpointLocation", checkpoint_path)
   .toTable("catalog.schema.target_table"))
```

**Micro-Batch-Tuning:** `maxFilesPerTrigger`/`maxBytesPerTrigger`, um Speicherverbrauch vorhersehbar zu halten — jeder Trigger verarbeitet alle verfügbaren Daten, was zu größeren Batches als bei zeitbasierten Triggern führt. Für langlebige Verbindungen/HTTP-Endpunkte: Databricks Apps statt Serverless-Streaming.

---

## 8. Sandbox

**Beta.** Databricks Sandbox ist eine Compute-Umgebung für Menschen und Agents, erreichbar über SSH, laufend in der Databricks Serverless Compute Plane — persistente Entwicklungsumgebungen und Coding-Agent-Ausführung ohne lokale Ressourcen.

**Fähigkeiten:** persistenter SSH-Zugriff über Sitzungen hinweg; Agent-Ausführung über Databricks CLI oder Desktop-IDE-Anbindung (Cursor, Claude, Codex); ephemere Umgebungen für Experimente/Sub-Agent-Tasks; mehrere nebenläufige SSH-Sitzungen auf geteiltem Dateisystem/State.

**Vorteile:** Databricks-native Governance (läuft in der Serverless Compute Plane, Daten innerhalb der Workspace-Governance-Grenze, AI-Gateway-Integration für governte LLM-Inferenz/MCP-Aufrufe); für Agents gebaut (Sekundenstart, persistenter Home-Speicher, nebenläufige Sitzungen).

### Sandbox erstellen

```bash
databricks sandbox create      # Sandbox erstellen
databricks sandbox register    # optional: SSH-Keys registrieren
databricks sandbox ssh         # SSH zur Standard-Sandbox
```

Voraussetzung: Databricks CLI lokal installiert, Authentifizierung via `databricks auth login`.

**Datenpersistenz:** während der Beta nicht persistent, kann gelöscht werden. Home-Verzeichnis (`/home/sandbox-agent`): bis zu 100 GB, persistiert unbegrenzt (in Beta jedoch am Programmende löschbar); Nicht-Home-Speicher: bis zu 10 GB, gelöscht beim Stoppen der Sandbox. Alle nebenläufigen Sitzungen teilen dasselbe Dateisystem.

**Ressourcen:** 4 Cores, 16 GB RAM, bis zu 100 GB Speicher (aktuell fix); Limits: max. 40 Sandboxes je Nutzer, 100 je Workspace; öffentliche IPs können sich jederzeit ändern.

**Netzwerk/Filesystem:** läuft in der Serverless Compute Plane mit Workspace-Governance, integriert aber noch **nicht** mit Serverless Egress Controls (SEG) — Sandbox nicht in Workspaces mit aktiviertem SEG nutzen. Keine native Möglichkeit, Umgebungen außerhalb des Home-Verzeichnisses zu persistieren oder beim Start anzupassen.

**Verfügbare Regionen (14 AWS-Regionen):** `ap-northeast-1`, `ap-northeast-2`, `ap-south-1`, `ap-southeast-1`, `ap-southeast-2`, `ca-central-1`, `eu-central-1`, `eu-west-1`, `eu-west-2`, `eu-west-3`, `sa-east-1`, `us-east-1`, `us-east-2`, `us-west-2`.

**Kosten (erwartet):** stündliche Runtime-Compute-Abrechnung (Raten TBD), laufende Abrechnung für persistenten Home-Speicher auch bei Pause, Temp-Speicher in Runtime-Compute enthalten, bestehende Datentransfer-Ratenstruktur.

**Einschränkungen:** keine SEG-Integration, feste Instanzgröße, Sandbox-Limits (40/Nutzer, 100/Workspace), wechselnde öffentliche IPs, Beta-Datenlöschung, begrenzte Environment-Anpassung. Beim SSH-Login konfiguriert Databricks gängige Coding-Harnesses (Claude, Codex) automatisch für die Nutzung des AI Gateway, sofern für den Workspace konfiguriert.

---

## 9. Einschränkungen

Vollständige Limitierungsliste für Serverless Compute:

**Sprachen/APIs:** R nicht unterstützt; nur Spark-Connect-APIs (keine RDD-APIs) — Spark Connect verschiebt Analyse/Namensauflösung auf die Ausführungszeit, was das Codeverhalten ändern kann; ANSI SQL ist Standard (Opt-out: `spark.sql.ansi.enabled = false`); Zeilengröße aus `spark.createDataFrame` max. 128 MB.

**Datenzugriff/Storage:** Unity Catalog für externe Datenquellen erforderlich; Cloud-Speicher nur über Unity-Catalog-External-Locations; DBFS-Zugriff eingeschränkt (Volumes/Workspace-Dateien nutzen); Maven-Koordinaten nicht unterstützt; Global Temp Views nicht unterstützt (Session-Temp-Views/Tabellen nutzen); DBFS-Mounts mit AWS Instance Profiles nicht unterstützt.

**UDFs:** kein Internetzugriff, `CREATE FUNCTION (External)` nicht unterstützt; Custom-Code max. 1 GB Memory; Scala-UDFs nicht innerhalb von Higher-Order-Functions nutzbar.

**UI/Logging:** Spark UI nicht verfügbar (Query Profile nutzen); Spark-Logs nicht verfügbar (nur client-seitige Application-Logs).

**Networking/Workspace-Zugriff:** Cross-Workspace-Zugriff erfordert dieselbe Region und keine IP-ACL/kein Front-End-PrivateLink; Databricks Container Services nicht unterstützt.

**Streaming:** unterstützt `Trigger.AvailableNow()` (empfohlen) und `Trigger.Once()` (deprecated); nicht unterstützt: `Trigger.Continuous(interval)`, `Trigger.ProcessingTime(interval)`.

**Notebooks:** kein Scala/R; keine JAR-Libraries (JAR-Tasks in Jobs schon); Notebook-scoped Libraries werden nicht sitzungsübergreifend gecacht; kein Teilen von TEMP-Tabellen/-Views zwischen Nutzern; kein Autocomplete/Variable Explorer für DataFrames; `.ipynb` als Default-Format; keine Notebook-Tags (Serverless Usage Policies nutzen).

**Jobs:** Task-Logs nicht pro Run isoliert; Task-Libraries für Notebook-Tasks nicht unterstützt (Notebook-scoped Libraries nutzen); standardmäßig kein Query-Execution-Timeout (`spark.databricks.execution.timeout` konfigurierbar); maximale Laufzeit **7 Tage** — darüber hinaus terminiert die Plattform ohne Retry.

**Compute-spezifisch (nicht unterstützt):** Compute-Policies, Compute-scoped Init-Skripte, Compute-scoped Libraries (inkl. Custom Data Sources), Instance Pools, Compute Event Logs, die meisten Spark-Compute-Konfigurationen, Compute-scoped Environment-Variablen.

**Caching:** Metadata-Caching kann vollständigen Session-Kontext-Reset beim Katalogwechsel verhindern; DataFrame-/SQL-Cache-APIs nicht unterstützt (`df.cache()`, `df.persist()`, `df.unpersist()`, `df.checkpoint()`, `spark.catalog.cacheTable()`, `spark.catalog.uncacheTable()`, `spark.catalog.clearCache()`, `CACHE TABLE`, `UNCACHE TABLE`, `REFRESH TABLE`, `CLEAR CACHE`).

**Hive:** Hive-SerDe-Tabellen und `LOAD DATA` nicht unterstützt; unterstützte Datenquellen begrenzt auf `AVRO`, `BINARYFILE`, `CSV`, `DELTA`, `JSON`, `KAFKA`, `ORC`, `PARQUET`, `TEXT`, `XML`; Hive-Variablen/`${var}`-Syntax nicht unterstützt (`DECLARE VARIABLE`, `SET VARIABLE`, Session-Variablen, Parameter-Marker oder `IDENTIFIER`-Klausel nutzen).

**Unterstützte Datenquellen:** DML (write/update/delete): `CSV`, `JSON`, `AVRO`, `DELTA`, `KAFKA`, `PARQUET`, `ORC`, `TEXT`, `UNITY_CATALOG`, `BINARYFILE`, `XML`, `SIMPLESCAN`, `ICEBERG`. Read (zusätzlich): `MYSQL`, `POSTGRESQL`, `SQLSERVER`, `REDSHIFT`, `SNOWFLAKE`, `SQLDW`, `DATABRICKS`, `BIGQUERY`, `ORACLE`, `SALESFORCE`, `SALESFORCE_DATA_CLOUD`, `TERADATA`, `WORKDAY_RAAS`, `MONGODB`.

Keine eigenen Code-Beispiele in dieser Datei — reine Limitierungsliste.

---

## 10. Lakehouse Replay

**Public Preview.** Verbessert die Databricks-Runtime-Qualität, indem automatisch eine kleine Stichprobe **read-only-Workloads** aus dem eigenen Workspace gegen kommende Runtime-Versionen getestet wird, bevor diese in Produktion gehen. Fokus auf Serverless-Umgebungen; erkannte Regressionen kommen allen Databricks-Runtime-Releases zugute (Classic und Serverless).

**Funktionsweise (Shadow Execution, 4 Stufen):** (1) Produktions-Workloads laufen normal, (2) eine kleine Stichprobe sicherer read-only-Workloads wird automatisch ausgewählt, (3) deren Spark-Pläne laufen erneut auf von Databricks verwaltetem Shadow Compute mit Kandidaten-Runtime-Versionen, (4) Diskrepanzen lösen eine Untersuchung vor dem Release aus. Shadow Compute arbeitet unabhängig ohne Einfluss auf Produktions-Workloads/Jobs.

**Unterstützte Workload-Typen:** Read-only-SQL-/DataFrame-Workloads auf Serverless Compute, Serverless SQL Warehouses und Notebooks, Serverless Jobs, Unity-Catalog-Delta-Table-Reads. Bei DataFrame-Workloads wird nur der an den Produktionscluster übermittelte Spark-Plan replayt — vorangehende Python-Zellen werden nicht ausgeführt.

**Datensicherheit:** keine Datenextraktion (nur Ausführungsstatus/Runtime-Metriken werden verglichen); Berechtigungserhalt (Replay läuft unter ursprünglicher Nutzeridentität mit Unity-Catalog-Berechtigungen); isolierte Ausführung (kein Zugriff auf externe APIs/Datenbanken/andere Workspaces).

**Abrechnung:** Compute-Kosten der Replay-Ausführung trägt Databricks; minimale Object-Storage-API-Gebühren können anfallen. **Audit-Logging:** Aktivität erscheint unter dem Service-Identifier `lakehouseReplay` in der Audit-Log-Systemtabelle.

**Erste Schritte:** keine Konfiguration nötig — Workspace-Admins aktivieren das Feature über die Previews-Seite; Sampling erfolgt automatisch/probabilistisch, meiste Workloads werden innerhalb einer Stunde replayt. Replayte Workloads erscheinen nicht in Job-/Query-History, nur in Audit-Logs. Erkannt werden Ausführungsfehler (in Produktion erfolgreich, auf kommender Runtime fehlschlagend).

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 11. Serverless Compute verwalten

Jeder Workspace erhält automatisch zwei Serverless-Compute-Objekte, die Workspace-Admins konfigurieren: **Default Interactive Compute** (Zugriff auf Notebooks, Databricks Connect) und **Default Automated Compute** (Zugriff auf Jobs, Spark Declarative Pipelines/Lakeflow). Standardmäßig haben alle Nutzer „Can Use" auf beiden; Default-Objekte können nicht umbenannt/gelöscht werden.

**Berechtigungsstufen:** „Can Use" (Workloads ausführen) und „Can Manage" (zusätzlich Berechtigungen ändern) — Workspace-Admins haben standardmäßig „Can Manage".

**Interaktiven Zugriff einschränken:** Compute → Tab „Serverless" → Kebab-Menü bei „Default Interactive Compute" → „Edit permissions" → Gruppe „All Users" entfernen → Zugriff gezielt vergeben. Folgen für entfernte Nutzer: bestehende Notebook-Verbindungen schlagen fehl, „Serverless" verschwindet aus dem Compute-Picker, Databricks Connect gibt Fehler zurück.

**Automatisierten Zugriff einschränken:** analog über „Default Automated Compute"; betroffene Nutzer erleben Job-/Pipeline-Fehler — vorher aktive Workloads auditieren.

### Pre-Revocation-Audit-Query

```sql
SELECT *
FROM system.billing.usage
WHERE usage_date >= date_add(now(), -30)
  AND billing_origin_product IN ('JOBS', 'DLT')
  AND identity_metadata.run_as = '<user_email>';
```

Die Spalte `usage_metadata` prüfen, um betroffene Job-/Pipeline-IDs zu identifizieren.

### Serverless-Nutzung auditieren

```sql
SELECT
  usage_metadata.serverless_compute_id,
  identity_metadata.run_as,
  SUM(usage_quantity) AS total_dbus
FROM system.billing.usage
WHERE billing_origin_product IN ('JOBS', 'DLT', 'INTERACTIVE')
  AND usage_metadata.serverless_compute_id IS NOT NULL
  AND usage_date >= date_add(now(), -30)
GROUP BY 1, 2
ORDER BY 3 DESC;
```

**Access-Control-Abdeckung:** Interactive (Default Interactive Compute) deckt Notebooks + Serverless-GPU-Notebooks + Databricks Connect ab; Automated (Default Automated Compute) deckt Jobs + Serverless-GPU-Jobs + Spark Declarative Pipelines ab. **Nicht** steuerbar: Databricks SQL, Batch Inference (`ai_query()`), Model Serving, Foundation Model API Provisioned Throughput, Lakebase, Databricks Apps, Agent Evaluation/Synthetic Data, Vector Search Indexing, Predictive Optimization, Lakehouse Monitoring, Fine-Grained Access Control auf Dedicated Compute.

**Limitierungen:** bei Service-Störungen kann die Zugriffsprüfung permissiv fehlschlagen (Governance-Feature, kein Spend-Cap — Databricks übernimmt keine Kostenverantwortung bei solchen Vorfällen); Default-Objekte nicht umbenennbar/löschbar; „Background Compute" (systeminitiierte Jobs) umgeht die Serverless-Access-Controls.

**Rate Limits (Private Preview):** deckeln Autoscaling-Parameter automatisierter Workloads über custom Automated-Compute-Objekte. Gelten nur für Jobs/Spark Declarative Pipelines (interaktive Workloads unbeschränkt) und nur für Spark-Executor-Autoscaling (Driver, REPL-VMs, GPUs, MV-/Streaming-Table-Refreshes unberührt). Jeder Job/jede Pipeline erhält eigenständige Durchsetzung; Tasks innerhalb eines Jobs teilen sich einen Cap.

Voraussetzungen: Workspace-Admin oder unbeschränkte Cluster-Creation-Rechte, Runtime 17.3.1+ (automatisch für Jobs, Opt-in-Preview für Lakeflow Pipelines).

**Rate-limited Compute erstellen:** Compute → Tab „Serverless" → „Create serverless compute" → Name vergeben → Size (Small bis 2X-Large, Default = Workspace-Standard) → „Create". Erscheint als Typ „Automated"; Berechtigungen vergeben; Größen von Default-Objekten nicht änderbar.

**Rate-Limit-Größen (ungefährer stündlicher DBU-Cap):**

| Größe | Ungefährer stündlicher DBU-Cap |
|---|---|
| Small | ~60 DBUs |
| Medium | ~120 DBUs |
| Large | ~240 DBUs |
| X-Large | ~480 DBUs |
| 2X-Large | ~960 DBUs |

Default: Medium (Premium-Tier) bzw. Large (Enterprise-Tier) — Werte sind Richtwerte, tatsächlicher Verbrauch schwankt.

**Nutzung:** Jobs wählen Serverless Compute in den Compute-Einstellungen oder referenzieren die Compute-ID über die Jobs-API (Copy compute ID im Serverless-Tab); Spark Declarative Pipelines setzen Automated Compute im Lakeflow-Editor; Workloads ohne angegebenes Compute-Objekt nutzen „Default Automated Compute" (fehlender Zugriff → Ausführung schlägt fehl); Throttling erscheint in Query-History bzw. Lakeflow-Pipeline-Interface.

**Rate-Limit-Constraints:** nur Spark-Executor-Autoscaling beschränkt; DBU-Caps sind Schätzungen (tatsächlicher Verbrauch kann abweichen); 2X-Large kann wegen physischer Cluster-Größen-Cap (256 Executors) unterperformen; identische Workloads können bei unterschiedlichen Rate-Limit-Größen unterschiedlichen DBU-Verbrauch akkumulieren; Default-Compute-Objekte können keine Rate-Limit-Zuweisung erhalten.

---

## 12. Serverless-Infrastruktur: Netzwerkkonfiguration im großen Maßstab

**Hintergrund (Databricks-Engineering-Blog):** Jede Serverless-VM benötigt vor der Ausführung eine Netzwerkkonfiguration (u. a. aus Unity Catalog, Netzwerk-Policies, Delta Sharing). Bei täglich zig Millionen gestarteter Serverless-VMs führte die ursprüngliche **synchrone** Architektur (Live-Abfrage mehrerer Upstream-Dienste beim Cluster-Start) zu Milliarden täglicher Requests mit hoher Latenz (RPC-p99 ~5.000 ms) und Verfügbarkeitsrisiko bei Upstream-Ausfällen (Server-Erfolgsrate 99,8 %).

**Lösung — ereignisgetriebene Vorberechnung:** Upstream-Dienste senden Änderungsereignisse an eine Message Queue, statt abgefragt zu werden. Ein Event-Processor ermittelt betroffene Workspaces, ein lokaler Event-Manager berechnet die Netzwerkkonfiguration im Hintergrund neu und legt sie in einem **Snapshot-Store** ab; ein niedrigfrequenter Reconciler sichert Eventual Consistency als Fallback. Der eigentliche Serving-Pfad liest beim VM-Start nur noch **einen** Snapshot — ganz ohne Upstream-Aufrufe ("statische Stabilität" auch bei Upstream-Ausfällen).

**Ergebnis:**

| Metrik | Vorher | Nachher |
|---|---|---|
| RPC-p99-Latenz | ~5.000 ms | **125 ms** (−97,5 %) |
| Server-Erfolgsrate | 99,8 % | 99,99 % |
| Upstream-Aufrufvolumen | Baseline | **−86 %** |

Das System bedient heute Milliarden Netzwerkkonfigurations-Requests täglich über die gesamte globale Serverless-Flotte hinweg — bei ~125 ms Latenz und 99,99 % Verfügbarkeit. Kernprinzip: teure Aggregation aus dem kritischen Pfad in den Hintergrund verlagern, sodass der kritische Pfad nur noch einen einzelnen Storage-Read benötigt.

---

## 13. Serverless-Infrastruktur: VM-Boot-Optimierung (7x schneller)

**Hintergrund:** Damit Serverless Compute tatsächlich „in Sekunden" startet, müssen nicht nur Rechenressourcen, sondern auch alle darunterliegenden Systeme (inkl. vorinstallierter Software) bereitstehen. Ein Databricks-Engineering-Blogpost beschreibt drei Techniken, die den VM-Boot insgesamt **7x** beschleunigt haben:

1. **Purpose-Built Serverless OS:** minimalistisches, auf Container-Ausführung reduziertes Betriebssystem (u. a. ohne USB-Subsystem/nicht-essenzielle Dienste), optimiertes I/O-Buffering, kleinere Image-Größen für besseres Cloud-Provider-Caching.
2. **Lazy Container Filesystem (overlaybd-basiert):** statt das komplette Container-Image vorab herunterzuladen, werden zunächst nur Metadaten geladen (4-MB-Sektoren); Dateizugriffe lösen On-Demand-Callbacks aus, die den passenden Block aus der Registry nachladen. Reduziert die Image-Pull-Latenz von mehreren Minuten auf wenige Sekunden — Grundlage: nur **6,4 %** der Daten werden benötigt, damit ein Container mit sinnvoller Arbeit beginnen kann.
3. **Checkpoint/Restore vorgewärmter Container:** der wirkungsvollste Hebel — vollständig „warmgelaufene" Container-Zustände (Prozessbäume, geladene Libraries, offene File-Deskriptoren, Heap inkl. JIT-kompiliertem Code, Stack-Speicher) werden auf Disk eingefroren und als reguläres Container-Image verpackt. Reduziert Initialisierung/Warm-up der Databricks Runtime von mehreren Minuten auf **~10 Sekunden**.

**Technische Herausforderungen:** Databricks Runtime musste angepasst werden, damit host-spezifische Bindungen (Hostname, IP-Adressen) erst **nach** dem Restore erfolgen und Wall-Clock-Zeitsprünge korrekt gehandhabt werden; Checkpoint-Signaturen werden On-Demand erzeugt (abhängig von Runtime-Version, Konfiguration, Heap-Größe, CPU-Instruktionssatz); Post-Restore-Hooks resäen Zufallszahlengeneratoren, um identische Outputs zu vermeiden.

**Effekt:** spart laut Databricks „zig Millionen Compute-Minuten täglich" und reduziert den Bedarf an vorgehaltenen Warm-VM-Pools.

---

## 14. Serverless-Infrastruktur: Container-Image-Verteilung (Artifact Registry)

**Hintergrund:** Der Start jeder Serverless-VM lädt Container-Images — bei Serverless-Spitzenlast über **100x** höher als bei internen Databricks-Diensten. Die für kontrollierte interne Deployments ausgelegte Open-Source-Container-Registry konnte diese Bursts nicht zuverlässig/kosteneffizient bedienen; Databricks baute daher eine eigene, „Serverless-optimierte" Artifact Registry.

**Architekturprinzip — Minimalismus:** nur **eine Komponente** und **eine Cloud-Abhängigkeit** (Object Storage). Kein relationales Datenbank-Backend für Metadaten (alles in Object Storage), dafür umfangreiches **In-Memory-Caching** auf dem Hot Path statt entfernter Cache-Instanzen; identische Replikate je Cloud-/Regionskombination ermöglichen **geo-basiertes Failover** bei regionalen Storage-Ausfällen.

**Ergebnisse:**

| Metrik | Verbesserung |
|---|---|
| P99-Latenz | **>90 %** Reduktion ggü. Open-Source-Registry |
| CPU-Nutzung | **−80 %** |
| Skalierungsgeschwindigkeit | „wenige Sekunden" statt 10+ Minuten (klassische DB-basierte Registries) |

Bedient Produktions-Spitzenlast in den meisten Fällen **ohne** Scale-out. Kernlehre: weniger Abhängigkeiten bedeuten weniger Fehlerquellen — ein Designprinzip, das direkt erklärt, warum Serverless-Container so schnell und zuverlässig aus der Registry bezogen werden können (siehe auch Abschnitt 13, Lazy Container Filesystem).

---

## 15. Versionless Apache Spark: Automatische Upgrades und Release Stability System

**Hintergrund:** Abschnitt 1 dieser Datei nennt Serverless bereits als „versionless product" mit automatischen, schrittweisen Runtime-Upgrades. Ein Databricks-Engineering-Blogpost erläutert den technischen Mechanismus dahinter im Detail.

**Architektur:** Nutzer laufen auf einer **Environment-Version** (enthält Spark Connect, Python, Abhängigkeiten; jede Version erhält **3 Jahre Support**, analog zu DBR-LTS-Releases — deckt sich mit Abschnitt 4 dieser Datei). Da der Client über eine **stabile, versionierte API** (basierend auf **Spark Connect**) vom Spark-Server entkoppelt ist, kann Databricks den Server unabhängig upgraden, ohne dass Nutzer-Code sich ändern muss.

**Release Stability System (RSS) — KI-gestützte Absicherung:** erkennt und behebt Fehlschläge automatisch über Workload-Fingerprinting, historische Run-Metadaten, ML-basierte Fehlerklassifizierung und Anomalie-Erkennungs-Pipelines. Schlägt ein Workload auf einer neuen Server-Version fehl, erstellt das RSS automatisch einen **Pinning-Eintrag** und führt den Job erneut auf der letzten bekannt funktionierenden Version aus; Engineering-Teams erhalten Alerts zur Fehlerbehebung, der Workload bleibt gepinnt, bis ein Fix ausgerollt ist.

**Ergebnisse im Maßstab:** über **2 Milliarden** Spark-Workloads automatisch über **25 Databricks-Runtime-Releases** hinweg upgraded; nur **0,000006 %** benötigten ein Rollback, alle davon im Schnitt innerhalb von **12 Tagen** behoben.

**Einordnung:** Erklärt technisch, warum Serverless Notebooks/Jobs ohne manuelle Runtime-Pflege „einfach funktionieren" — direkte Ergänzung zu Abschnitt 1 (Übersicht) und Abschnitt 4 (Environment-Versionen).