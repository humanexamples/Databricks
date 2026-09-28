# 04 Data Guides — Gesamtzusammenfassung

Konsolidierte Übersicht aller 7 Original-Markdown-Dateien im Ordner `04 Data Guides\` (Magic Commands sowie der Unterordner `02 Work with files\` mit den Themen Workspace Files, Unity Catalog Volumes und DBFS) mit **allen** enthaltenen Code-Beispielen und einer kurzen, einfachen Einführung pro Thema. Jede Originaldatei bleibt die primäre, ausführliche Quelle — dieses Dokument dient als kompakter Überblick plus vollständige Code-Referenz an einem Ort.

**Verifikationsstatus:** Die Originaldateien zitieren durchgängig offizielle Databricks-Doku-Quellen (`docs.databricks.com`) und sind bereits größtenteils per `WebFetch` gegengeprüft. Für dieses Dokument wurden die Themen zusätzlich gegen aktuelle **Databricks-Blog-Artikel** (`databricks.com/blog`) abgeglichen — Ergebnisse siehe Abschnitt 8 „Verifikationsprotokoll" am Ende dieser Datei.

## Inhalt

1. [Magic Commands in Databricks-Notebooks](#1-magic-commands-in-databricks-notebooks)
2. [Datei-Speicheroptionen und Workspace Files](#2-datei-speicheroptionen-und-workspace-files)
3. [Workspace Files als Code-Module](#3-workspace-files-als-code-module)
4. [Unity Catalog Volumes](#4-unity-catalog-volumes)
5. [DBFS Grundlagen](#5-dbfs-grundlagen)
6. [`dbutils.fs` — Befehlsreferenz](#6-dbutilsfs--befehlsreferenz)
7. [Mounts und Migration](#7-mounts-und-migration)
8. [Verifikationsprotokoll (Databricks-Blog-Abgleich)](#8-verifikationsprotokoll-databricks-blog-abgleich)

---

## 1. Magic Commands in Databricks-Notebooks

**Einfach erklärt:** Magic Commands sind spezielle Befehle am Zellenanfang (mit `%` eingeleitet), die das Standardverhalten einer Notebook-Zelle ändern — z. B. um Shell-Befehle auszuführen, ein anderes Notebook einzubinden oder die Zellsprache umzuschalten. Am wichtigsten für den Alltag: `%sh` (Shell/Bash) und `%run` (Notebook-Verkettung).

### `%sh` — Shell-/Bash-Befehle ausführen

Läuft ausschließlich auf dem Spark-**Treiber** (Driver), nicht auf den Worker-Knoten — für Shell-Befehle auf allen Knoten ist stattdessen ein Init-Skript nötig.

```python
%sh ls -la
```

**Fehlerbehandlung mit `-e`:** Ohne `-e` schlägt die Zelle bei einem fehlerhaften Shell-Befehl nicht automatisch fehl.

```python
%sh -e some-command-that-might-fail
```

### `%run` — Ein anderes Notebook ausführen

`%run` muss allein in einer Zelle stehen — der Befehl führt das referenzierte Notebook vollständig inline im aktuellen Ausführungskontext aus; Funktionen und Variablen aus dem ausgeführten Notebook stehen danach im aufrufenden Notebook zur Verfügung.

```python
# Running ipynb Files
%run ./Classroom-Setup-Common
```

```python
%run /path/to/notebook
```

### Weitere Magic Commands (Kurzübersicht)

| Befehl | Zweck |
|---|---|
| `%python`, `%r`, `%scala`, `%sql` | Zellsprache umschalten; Code in der jeweiligen Sprache ausführen. Bei `%sql` sind Ergebnisse in Python-/SQL-Zellen als `_sqldf` verfügbar. |
| `%md` | Zellsprache auf Markdown umschalten; rendert Text, Bilder, Formeln, LaTeX. |
| `%fs` | Dateisystem-Befehle (Kurzform für `dbutils.fs`) — siehe Abschnitt 6. |
| `%pip` | Installiert Python-Pakete (Notebook-scoped). |
| `%uv pip` | Installiert/verwaltet Python-Pakete (Notebook-scoped) mit `uv` und Standard-pip-Subcommands. |
| `%skip` | Überspringt die Zellausführung — die Zelle läuft nicht mit, wenn das Notebook ausgeführt wird. |
| `%tensorboard` | Zeigt die TensorBoard-UI inline an. Nur auf Databricks Runtime ML verfügbar. |
| `%%profile` | Profiled die Python-Code-Ausführung; zeigt einen hierarchischen Call-Tree mit Timing-Informationen. |
| `%%oprofile` | Profiled die Objekterzeugung während der Zellausführung. |
| `%set_cell_max_output_size_in_mb` | Setzt die maximale Zellen-Output-Größe (Bereich: 1–20 MB). |

Quellen: https://docs.databricks.com/aws/en/notebooks/notebooks-code · https://docs.databricks.com/aws/en/dev-tools/databricks-utils

---

## 2. Datei-Speicheroptionen und Workspace Files

**Einfach erklärt:** Databricks bietet fünf Wege, Dateien zu speichern — von den empfohlenen **Unity Catalog Volumes** über **Workspace Files** (für Notebooks/Code/kleine Testdateien) bis zu den veralteten **DBFS-Mounts**. Dieser Abschnitt erklärt zuerst die Optionen im Überblick, dann Workspace Files im Detail.

### Fünf Datei-Speicheroptionen im Überblick

| Option | Empfehlung |
|---|---|
| **Unity Catalog Volumes** | empfohlen für nicht-tabellarische Daten im Cloud-Storage |
| **Workspace Files** | für Notebooks, Quellcode und kleine Datendateien |
| **Cloud Object Storage** | direkter S3-Zugriff über URIs |
| **DBFS Mounts und DBFS Root** | veraltet — nicht für neue Implementierungen empfohlen |
| **Ephemeral Storage** | temporärer Driver-Node-Storage — verschwindet bei Cluster-Neustart |

### Pfad-Formate: URI-Style vs. POSIX-Style

- **URI-Style-Pfade:** enthalten ein Schema (z. B. `s3://`, `file:/`) — erforderlich für Cloud-Storage.
- **POSIX-Style-Pfade:** relativ zum Driver-Root (`/`) — benötigt für FUSE-abhängige ML-Frameworks.

### Was sind Workspace Files?

Workspace Files sind die Dateien, die im Databricks-Workspace-Dateisystem gespeichert und verwaltet werden. Sie befinden sich im Databricks-Workspace-Dateibaum, der auch mit Git-Repositories verbundene Ordner (**Databricks Git-Ordner**) einschließen kann.

### Unterstützte Dateitypen

Notebooks (`.ipynb`), Quellcode (`.py`, `.sql`, `.r`, `.scala`), SQL-Queries (`.dbquery.ipynb`), Dashboards (`.lvdash.json`), Alerts (`.dbalert.json`), Python-Module (`.py`), Konfigurationsdateien (`.yaml`, `.yml`), Markdown (`.md`), Text-/Datendateien (`.txt`, `.csv`), Bibliotheken (`.whl`, `.jar`), Log-Dateien (`.log`). Genie Agents und Experiments können **keine** Workspace Files sein.

### Wichtige Einschränkungen

- **Dateigröße:** maximal **500 MB** — größere Operationen schlagen fehl.
- **Zugriffsberechtigungen:** laufen nach 36 Stunden für interaktives Compute und nach 30 Tagen für Jobs ab.
- Executors können nicht in Workspace Files schreiben.
- Symlinks nur auf Ziele innerhalb von `/Workspace` beschränkt.
- Notebooks als Workspace Files nur ab Databricks Runtime 16.2+ unterstützt.

### Workspace Files über die UI erstellen, importieren und bearbeiten

Erstellen über **Create** > **File** in einem beliebigen Verzeichnis. Import über das Kebab-Menü (**Import**, Drag-and-drop oder Browse) oder direktes Drag-and-Drop in den Workspace. Nur Notebooks können von einer URL importiert werden; ZIP-Dateien werden automatisch extrahiert; `.whl`-Dateien lassen sich zur Bibliotheksnutzung importieren. Jede Datei im Workspace-Browser lässt sich anklicken und mit Autocomplete/Multicursor bearbeiten — Änderungen werden automatisch gespeichert.

### Programmatisch mit Workspace Files arbeiten

Erfordert Databricks Runtime 11.3 LTS+ (Notebook-Unterstützung ab Runtime 16.2). Pfad-Formate: Git-Ordner `file:/Workspace/Repos/<user>/<repo>/path/to/file`, persönliches Verzeichnis `file:/Workspace/Users/<user>/path/to/file`.

**Datendateien lesen — über pandas (CSV):**

```python
import pandas as pd

df = pd.read_csv("./data/winequality-red.csv")
```

**Über Spark mit vollständig qualifizierten Pfaden:**

```python
import os

spark.read.format("csv").load(f"file:{os.getcwd()}/my_data.csv")
```

**Dateien erstellen und bearbeiten:**

```python
import os

os.mkdir('dir1')
with open('dir1/new_file.txt', "w") as f:
    f.write("new content")
with open('dir1/new_file.txt', "a") as f:
    f.write(" continued")
```

**Löschen:**

```python
os.remove('dir1/new_file.txt')
os.rmdir('dir1')
```

**Kopieren und Verschieben:**

```python
import shutil

shutil.copy("my-dashboard.lvdash.json", "my-dashboard-copy.lvdash.json")
shutil.move("test-query.dbquery", "shared-queries/")
```

Quellen: https://docs.databricks.com/aws/en/files/ · https://docs.databricks.com/aws/en/files/workspace · https://docs.databricks.com/aws/en/files/workspace-basics · https://docs.databricks.com/aws/en/files/workspace-interact

---

## 3. Workspace Files als Code-Module

**Einfach erklärt:** Workspace Files lassen sich nicht nur als Dateien verwalten, sondern auch als echte Python-Module importieren, als Cluster-Init-Skripte nutzen und mit integrierten Unit-Tests versehen. Besonders wichtig: Das Arbeitsverzeichnis-Verhalten hat sich mit Databricks Runtime 14.0 grundlegend geändert.

### Workspace Files als Python-Module importieren

Um Module aus einem anderen Verzeichnis zu importieren, wird das Verzeichnis über einen relativen Pfad zu `sys.path` hinzugefügt:

```python
import sys
import os

sys.path.append(os.path.abspath('..'))
```

Danach lassen sich Funktionen aus Workspace-File-Modulen wie aus Standardbibliotheken importieren:

```python
from sample import power
power.powerOfTwo(3)
```

**Für R-Module:**

```r
source("sample.R")
power.powerOfTwo(3)
```

**Verhaltenshinweise je Runtime-Version:**

| Runtime | Verhalten |
|---|---|
| **14.0+** | Standard-Arbeitsverzeichnis wird automatisch auf das Verzeichnis gesetzt, das das Notebook enthält |
| **13.3 LTS+** | Verzeichnisse im Python-`sys.path` oder Python-Pakete werden automatisch an alle Cluster-Executors verteilt |
| **11.3 LTS+** | das aktuelle Arbeitsverzeichnis des Notebooks wird automatisch zum Python-Pfad hinzugefügt |

### Autoreload für die Entwicklung

```python
%load_ext autoreload
%autoreload 2
```

**Wichtige Einschränkung:** Autoreload wirkt nur auf den Spark-Driver-Prozess, nicht auf Executor-Prozesse — bei der Entwicklung von Modulen für Worker-Knoten (etwa UDFs) sollte Autoreload nicht genutzt werden. Ab Runtime 16.0+ unterstützt Autoreload gezieltes Neuladen von Modulen bei Funktionsänderungen und schlägt automatisch vor, aktiviert zu werden, wenn ein importiertes Modul geändert wurde.

### Cluster-Init-Skripte als Workspace Files

Databricks empfiehlt, Init-Skripte ab Databricks Runtime 11.3 LTS in Workspace Files zu speichern, sofern Unity Catalog nicht genutzt wird. Für frühere Versionen (9.1 LTS, 10.4 LTS) gelten Einschränkungen — u. a. wird das Referenzieren anderer Dateien aus Init-Skripten heraus nicht unterstützt. Zugriff wird über ACLs gesteuert — standardmäßig haben nur der hochladende Nutzer und Workspace-Admins Berechtigungen.

### Python-Unit-Tests im Workspace

Databricks erkennt Testdateien automatisch nach Pytest-Konventionen (`test_*.py`, `*_test.py`) und bietet ein integriertes Testing-Panel mit Ausführungssteuerung, Inline-Run-Buttons und Ergebnis-Tracking.

**Erkennungsregeln:** eigenständige Funktionen mit Präfix `test_` außerhalb jeder Klasse; Methoden mit Präfix `test_` innerhalb von `Test_`-präfigierten Klassen (ohne `__init__`); `@staticmethod`/`@classmethod`-Methoden innerhalb von `Test_`-Klassen.

```python
class TestClass():
    def test_1(self):
        assert True

    def test_3(self):
        assert 4 == 3

def test_foo():
    assert "foo" == "bar"
```

### Arbeitsverzeichnis-Verhalten ab Databricks Runtime 14.0

**Vorher (DBR 13.3 LTS und darunter):** Für Code außerhalb von `/Workspace/Repos` zeigte das Arbeitsverzeichnis (CWD) auf ephemeren Storage (gelöscht bei Cluster-Terminierung). Für Code in `/Workspace/Repos` hing das Verhalten von Admin-Konfiguration und Runtime-Version ab.

**Nachher (DBR 14.0+):** Das CWD ist immer das Verzeichnis, das das ausgeführte Notebook oder Skript enthält — unabhängig davon, ob sich der Code in `/Workspace/Repos` befindet. Dadurch erzeugen Standard-Dateioperationen jetzt **persistente** Workspace Files statt (wie zuvor) ephemere, bei Cluster-Terminierung verlorene Daten.

**Aktuelles Arbeitsverzeichnis abrufen:**

```python
import os

cwd = os.getcwd()
```

**Zum Legacy-Verhalten (ephemerer Storage) zurückkehren:**

```python
import os

os.chdir("/tmp")
```

Quellen: https://docs.databricks.com/aws/en/files/workspace-modules · https://docs.databricks.com/aws/en/files/workspace-modules#autoreload-for-python-modules · https://docs.databricks.com/aws/en/files/workspace-init-scripts · https://docs.databricks.com/aws/en/files/python-unit-tests · https://docs.databricks.com/aws/en/files/cwd-dbr-14

---

## 4. Unity Catalog Volumes

**Einfach erklärt:** Unity Catalog Volumes sind Databricks' empfohlener Weg, um **nicht-tabellarische** Daten (Bilder, PDFs, Rohdaten, Archive, Bibliotheken) mit zentraler Governance zu speichern — der Nachfolger von Workspace Files und DBFS für alles, was über kleine Entwicklungsdateien hinausgeht. Volumes sind Unity-Catalog-Objekte, die eine logische Schicht über dem Cloud-Object-Storage bilden, sodass Dateien governt, organisiert und verwaltet werden können.

### Managed vs. External Volumes

| Typ | Beschreibung |
|---|---|
| **Managed Volumes** | die Plattform verwaltet Storage-Lebenszyklus und Cloud-Speicherort |
| **External Volumes** | Nutzer kontrollieren Speicherort und Lebenszyklusverwaltung selbst |

### Zugriffsmethoden

- **Browser-Oberfläche:** Catalog Explorer zum Hochladen/Herunterladen/Durchsuchen; **„My Files"** (Beta) — ein Volume pro Nutzer für schnelle Dateispeicherung ohne eigene Catalog-Infrastruktur.
- **Programmatisch:** Apache Spark, pandas, SQL-Queries.
- **Kommandozeile:** `dbutils.fs`-Utilities, Magic Commands, Bash-Shell.

### Integrations-Anwendungsfälle

Daten-Ingestion (`COPY INTO`, Auto Loader, Spark-APIs), Compute-Log-Zustellung, File-Arrival-Trigger, Cluster-Bibliotheken, Init-Skripte, MLflow-Experiment-Artefakt-Speicherung.

### Speicherempfehlungen: Volumes vs. Workspace Files

**In Unity Catalog Volumes speichern:** strukturierte Daten (Parquet, ORC), semi-strukturierte Daten (CSV, TXT, JSON), unstrukturierte Inhalte (Bilder, Audio, PDFs), Rohdaten zur Exploration, Log-Dateien, große Archive (ZIPs), Build-Artefakte/Bibliotheken (Wheels, JARs), workspace-übergreifende Konfigurationsdateien.

**Als Workspace Files speichern:** Databricks-Objekte (Notebooks, Queries), Quellcode (vorzugsweise in Git-Ordnern), projektspezifische Konfigurationsdateien in Git-Repos, kleine Dateien unter 500 MB.

| Aspekt | Workspace Files | Unity Catalog Volumes |
|---|---|---|
| **Zugänglichkeit** | nur ein Workspace | über alle Workspaces zugänglich |
| **Max. Upload/Download** | 500 MB | 5 GB |
| **Berechtigungsmodell** | Workspace-ACLs | Unity-Catalog-verwaltet, workspace-übergreifend |
| **Tabellenerstellung** | nicht unterstützt | unterstützt über `COPY INTO`, Auto Loader |
| **External Storage** | nicht unterstützt | unterstützt External Volumes |
| **UDF-Unterstützung** | nicht unterstützt | unterstützt über FUSE |

### Dateien in Volumes schreiben

Über Apache Spark lassen sich Dateien nach folgendem Pfadmuster in Unity-Catalog-Volumes schreiben:

```
/Volumes/<catalog>/<schema>/<volume>/<path>/<file-name>
```

### ZIP-Dateien entpacken

Primäre Methode: der `unzip`-Bash-Befehl über den `%sh`-Magic-Command. Parquet-Dateien (meist `.snappy.parquet`) müssen dank eingebauter Spark-Codec-Unterstützung in der Regel nicht manuell entpackt werden.

**Vollständiges Beispiel: Herunterladen, Entpacken, in Volume verschieben, lesen:**

```bash
%sh curl https://resources.lendingclub.com/LoanStats3a.csv.zip --output /tmp/LoanStats3a.csv.zip
unzip /tmp/LoanStats3a.csv.zip
```

```python
%sh mv /tmp/LoanStats3a.csv /Volumes/my_catalog/my_schema/my_volume/LoanStats3a.csv
```

```python
df = spark.read.format("csv").option("skipRows", 1).option("header", True).load("/Volumes/my_catalog/my_schema/my_volume/LoanStats3a.csv")
display(df)
```

Quellen: https://docs.databricks.com/aws/en/files/volumes · https://docs.databricks.com/aws/en/files/files-recommendations · https://docs.databricks.com/aws/en/files/write-data · https://docs.databricks.com/aws/en/files/unzip-files

---

## 5. DBFS Grundlagen

**Einfach erklärt:** Das Databricks File System (DBFS) ist der historische, inzwischen **veraltete** Weg, wie Databricks mit Cloud-Storage interagiert. Der Begriff umfasst zwei Komponenten: **DBFS Root** (ein für alle Workspace-Nutzer zugänglicher Standard-Speicherort) und **DBFS Mounts** (siehe Abschnitt 7). Neue Konten werden ohne Zugriff auf diese Features bereitgestellt.

### Deprecation-Status und empfohlene Alternativen

Sowohl DBFS Root als auch DBFS Mounts sind veraltet. Databricks empfiehlt stattdessen: **Unity Catalog Volumes**, **External Locations**, **Workspace Files**.

- **DBFS Root:** von der Speicherung von Produktionsdaten, Bibliotheken oder Skripten wird abgeraten.
- **DBFS Mounts:** erlauben Zugriff auf Cloud-Object-Storage als lokale Dateisystem-Ressourcen über gespeicherte Hadoop-Konfigurationen — veraltet zugunsten von Unity-Catalog-Volumes.

### DBFS Root im Detail

DBFS Root dient als Standard-Speicherort für Managed Tables im Hive Metastore. Da **alle Workspace-Nutzer** darauf zugreifen können, rät Databricks ausdrücklich davon ab, Produktionsdaten oder sensible Informationen dort zu speichern. Empfehlungen für den Übergangsbetrieb: Nutzeraufklärung, Audit-Logging/S3-Object-Level-Logging aktivieren, Customer-Managed Keys für Verschlüsselung einsetzen, auf Volumes/External Locations/Workspace Files migrieren.

### Standardmäßige Root-Verzeichnisse

| Verzeichnis | Zweck |
|---|---|
| **`/Volumes`** | pfadbasierter Zugriff auf Unity-Catalog-Volumes-Daten — die empfohlene moderne Alternative |
| **`/databricks-datasets`** | Open-Source-Datensätze von Databricks für Tutorials, Demos, Exploration |
| **`/user/hive/warehouse`** | Standard-Speicherort für Managed-Table-Daten im `hive_metastore` |
| **`/FileStore`** | über die UI hochgeladene Daten/Bibliotheken sowie generierte Plot-Bilder — primär Legacy-Verhalten |
| **`/databricks-results`** | Dateien beim Herunterladen vollständiger Query-Ergebnisse aus Notebooks |
| **`/databricks/init`** | Legacy-Global-Init-Skripte — veraltet, nicht mehr nutzen |

Keine weiteren Code-Beispiele in dieser Datei.

Quellen: https://docs.databricks.com/aws/en/dbfs/ · https://docs.databricks.com/aws/en/dbfs/dbfs-root · https://docs.databricks.com/aws/en/dbfs/root-locations

---

## 6. `dbutils.fs` — Befehlsreferenz

**Einfach erklärt:** `dbutils.fs` ist Databricks' Dateisystem-API für Notebooks — mit Befehlen zum Auflisten, Kopieren, Verschieben, Löschen und Lesen/Schreiben von Dateien. `%fs` ist eine abgekürzte Magic-Command-Syntax dafür, die aber nur für einzeilige, einfache Aufrufe reicht; für Aufrufe mit mehreren Argumenten (z. B. `recurse=True`) ist `dbutils.fs` direkt nötig.

### `%fs` — Kurzform für `dbutils.fs`

```python
%fs ls /path
```

### Verfügbare `dbutils.fs`-Befehle

| Befehl | Syntax | Beschreibung |
|---|---|---|
| `ls` | `ls(dir: String): Seq` | Listet den Inhalt eines Verzeichnisses auf (Pfad, Name, Größe, Änderungszeit). |
| `cp` | `cp(from: String, to: String, recurse: boolean = false): boolean` | Kopiert eine Datei oder ein Verzeichnis, ggf. über Dateisystemgrenzen hinweg. `recurse` kopiert Verzeichnisse samt Inhalt. |
| `mv` | `mv(from: String, to: String, recurse: boolean = false): boolean` | Verschiebt eine Datei oder ein Verzeichnis — intern eine Kopie gefolgt von einem Löschvorgang. |
| `rm` | `rm(dir: String, recurse: boolean = false): boolean` | Löscht eine Datei oder ein Verzeichnis. Bei nicht-leerem Verzeichnis ohne `recurse` wird ein Fehler geworfen. |
| `mkdirs` | `mkdirs(dir: String): boolean` | Legt das angegebene Verzeichnis inklusive aller nötigen übergeordneten Verzeichnisse an. |
| `head` | `head(file: String, max_bytes: int = 65536): String` | Gibt bis zur angegebenen maximalen Byte-Anzahl einer Datei als UTF-8-String zurück. |
| `put` | `put(file: String, contents: String, overwrite: boolean = false): boolean` | Schreibt den angegebenen String UTF-8-kodiert in eine Datei. |

```python
# Beispiele mit dbutils.fs direkt (äquivalent zu den %fs-Kurzformen)
dbutils.fs.ls("/Volumes/main/schema/volume/")
dbutils.fs.cp("/source/path", "/target/path", recurse=True)
dbutils.fs.mkdirs("/Volumes/main/schema/volume/new_folder")
dbutils.fs.rm("/Volumes/main/schema/volume/old_file.csv")
```

```python
# Äquivalente Kurzform über %fs (nur einzeilige, einfache Aufrufe)
%fs ls /Volumes/main/schema/volume/
%fs mkdirs /Volumes/main/schema/volume/new_folder
```

Für `mount`/`unmount` siehe Abschnitt 7 — diese Befehle sind speziell für Cloud-Storage-Mounts.

Quellen: https://docs.databricks.com/aws/en/notebooks/notebooks-code · https://docs.databricks.com/aws/en/dev-tools/databricks-utils

---

## 7. Mounts und Migration

**Einfach erklärt:** DBFS Mounts verbanden Workspaces mit Cloud-Object-Storage über vertraute Dateipfade unter `/mnt` — ein bequemes, aber inzwischen veraltetes Muster, das mit Serverless Compute **inkompatibel** ist. Dieser Abschnitt zeigt die Mount-Syntax für Referenzzwecke, das Zusammenspiel von DBFS mit Unity Catalog, und wie sich DBFS Root und Mounts kontrolliert deaktivieren lassen.

### DBFS und Unity Catalog: Best Practices

**In Legacy-Systemen:** Aktionen auf `hive_metastore`-Tabellen nutzen Legacy-Datenzugriffsmuster mit Managed Tables im DBFS Root. **Dedicated Access Mode:** Compute hat vollen DBFS-Zugriff. **Standard Access Mode:** direkte Dateiinteraktion verlangt `ANY FILE`-Berechtigungen — Databricks warnt davor, diese breit zu vergeben, da sie Legacy-Table-ACLs im `hive_metastore` umgehen und Zugriff auf alle DBFS-verwalteten Daten gewähren.

**Kritische Best Practices:** DBFS nicht mit External Locations kombinieren (kein Storage-Wiederverwenden zwischen DBFS-Mounts und UC-External-Volumes); Managed Storage mit neuen Storage-Accounts/eigenen Identity-Policies absichern; DBFS Root niemals als External Location laden (Sicherheitsrisiko); Cluster-Hadoop-Konfigurationen gelten nicht für Unity-Catalog-Filesystem-Zugriff; Eltern-/Kind-Pfade nicht über unterschiedliche Zugriffsmethoden in derselben Zelle ansprechen.

### Was sind DBFS Mounts?

DBFS Mounts erzeugen Verknüpfungen zwischen Workspaces und Cloud-Object-Storage über vertraute `/mnt`-Dateipfade — sie speichern Speicherort-URIs, Treiber-Spezifikationen und Sicherheits-Credentials.

### `dbutils.fs.mount`-Syntax

```python
dbutils.fs.mount(
  source: str,
  mount_point: str,
  encryption_type: Optional[str] = "",
  extra_configs: Optional[dict[str:str]] = None
)
```

### Storage unmounten

```python
dbutils.fs.unmount("/mnt/<mount-name>")
```

**Warnung:** Mounts nicht während aktiver Lese-/Schreibvorgänge ändern. `dbutils.fs.refreshMounts()` auf anderen Clustern ausführen, um Updates zu propagieren.

### S3-Bucket-Mounting-Methoden

**Instance-Profile-Authentifizierung:**

```python
aws_bucket_name = "<aws-bucket-name>"
mount_name = "<mount-name>"
dbutils.fs.mount(f"s3a://{aws_bucket_name}", f"/mnt/{mount_name}")
display(dbutils.fs.ls(f"/mnt/{mount_name}"))
```

**AWS-Keys-Authentifizierung:**

```python
access_key = dbutils.secrets.get(scope = "aws", key = "aws-access-key")
secret_key = dbutils.secrets.get(scope = "aws", key = "aws-secret-key")
encoded_secret_key = secret_key.replace("/", "%2F")
dbutils.fs.mount(f"s3a://{access_key}:{encoded_secret_key}@{aws_bucket_name}",
                  f"/mnt/{mount_name}")
```

**Wichtig:** Bei Key-basierten Mounts erhalten alle Workspace-Nutzer Lese-/Schreibzugriff auf alle Bucket-Objekte.

**AssumeRole-Policy:**

```python
dbutils.fs.mount("s3a://<s3-bucket-name>", "/mnt/<s3-bucket-name>",
  extra_configs = {
    "fs.s3a.credentialsType": "AssumeRole",
    "fs.s3a.stsAssumeRole.arn": "arn:aws:iam::<bucket-owner-acct-id>:role/MyRoleB",
    "fs.s3a.canned.acl": "BucketOwnerFullControl",
    "fs.s3a.acl.default": "BucketOwnerFullControl"
  })
```

**S3-Verschlüsselungsoptionen — SSE-S3:**

```python
dbutils.fs.mount(s"s3a://$AccessKey:$SecretKey@$AwsBucketName",
                  s"/mnt/$MountName", "sse-s3")
```

**SSE-KMS:**

```python
# Standard-KMS-Key
dbutils.fs.mount(s"s3a://$AccessKey:$SecretKey@$AwsBucketName",
                  s"/mnt/$MountName", "sse-kms")

# Spezifischer KMS-Key
dbutils.fs.mount(s"s3a://$AccessKey:$SecretKey@$AwsBucketName",
                  s"/mnt/$MountName", "sse-kms:$KmsKey")
```

**Databricks Commit Service für S3:**

```python
dbutils.fs.unmount("/mnt/<mount-name>")
dbutils.fs.mount("s3a://<bucket-name>/", "/mnt/<mount-name>",
  extra_configs = {
    "fs.s3a.credentialsType": "AssumeRole",
    "fs.s3a.stsAssumeRole.arn": "<role-arn>"
})
```

### Azure ADLS/Blob Storage mounten

```python
configs = {
  "fs.azure.account.auth.type": "OAuth",
  "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
  "fs.azure.account.oauth2.client.id": "<application-id>",
  "fs.azure.account.oauth2.client.secret": dbutils.secrets.get(scope="<scope-name>",
                                                                  key="<service-credential-key-name>"),
  "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/<directory-id>/oauth2/token"
}
dbutils.fs.mount(
  source = "abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/",
  mount_point = "/mnt/<mount-name>",
  extra_configs = configs)
```

### DBFS Root und Mounts deaktivieren

**Als Workspace-Admin:** 1. Anmelden. 2. Nutzerprofil-Icon → **Settings**. 3. **Workspace admin** → **Security**. 4. **Disable DBFS root and mounts** aktivieren. 5. Bis zu 20 Minuten auf Propagierung warten. 6. Alle laufenden Cluster und SQL-Warehouses manuell neu starten.

**Was danach nicht mehr funktioniert:** Lese-/Schreibzugriff auf DBFS Root/Mounts (Fehler „Public DBFS root is disabled"); DBFS-Browser/Uploads; Jobs/Notebooks/Skripte mit DBFS-Pfaden; statische Notebook-Datei-Einbettung über `/files` (500-Fehler); Mount-/Unmount-Operationen; FileStore-Operationen; Runtime-Versionen unter 13.3 LTS.

**Was weiterhin funktioniert:** Unity Catalog Volumes (über `dbfs:/Volumes`-Präfix), System-Pfade wie `dbfs:/databricks-datasets/`, interne Workspace-Systemdaten. Vor der Deaktivierung: alle Workflows migrieren, Runtime auf 13.3 LTS+ aktualisieren, Observability-Skripte zur Identifikation verbleibender DBFS-Nutzung einsetzen.

Quellen: https://docs.databricks.com/aws/en/dbfs/unity-catalog · https://docs.databricks.com/aws/en/dbfs/mounts · https://docs.databricks.com/aws/en/dbfs/disable-dbfs-root-mounts

---

## 8. Verifikationsprotokoll (Databricks-Blog-Abgleich)

Abgleich der in diesem Ordner dokumentierten Themen gegen aktuelle **Databricks-Blog-Artikel** (`databricks.com/blog`), durchgeführt am 2026-09-24:

| Thema | Blog-Quelle | Ergebnis |
|---|---|---|
| Unity Catalog Volumes (Abschnitt 4) | [Announcing the General Availability of Unity Catalog Volumes](https://www.databricks.com/blog/announcing-general-availability-unity-catalog-volumes) | ✅ Bestätigt: Volumes sind GA auf AWS, Azure und GCP, konzipiert speziell für nicht-tabellarische KI-Daten (PDFs, Bilder, Video, Audio) — z. B. für RAG- und Computer-Vision-Anwendungsfälle. Deckt sich vollständig mit der Originaldatei. Ergänzend aus einer früheren Recherche in diesem Projekt (Data + AI Summit 2026): Ein neuer **FILE-Volume-Typ** (Beta) governt unstrukturierte Daten jetzt direkt *innerhalb* von Managed-Delta-/Iceberg-Tabellen — über die in der Originaldatei beschriebenen klassischen Managed/External-Volumes hinaus. Nicht in der Originaldatei erwähnt. |
| DBFS-Deprecation (Abschnitte 5 und 7) | [Disable access to DBFS root and mounts](https://docs.databricks.com/aws/en/dbfs/disable-dbfs-root-mounts) (kein dedizierter Blog-Artikel gefunden, nur Doku + Community-Thread) | ✅ Bestätigt: „Both DBFS root and DBFS mounts are deprecated and not recommended by Databricks" — deckt sich wortgleich mit den Originaldateien. Zusätzlich gefunden: Es gibt inzwischen eine **Account-Level-Einstellung** „Disable legacy features", mit der Workspace-Admins DBFS bereits für neue Workspaces von vornherein deaktivieren können — nicht nur nachträglich pro bestehendem Workspace wie in Abschnitt 7 beschrieben. Kein dedizierter Blog-Artikel zu diesem Thema auffindbar, da es sich um eine reine Migrations-/Deprecation-Doku-Seite handelt, die typischerweise nicht separat im Blog beworben wird. |
| Workspace Files, Git-Ordner, Notebooks | Keine dedizierten Blog-Artikel gefunden — nur aktuelle Doku-Seiten (`files/workspace`, `repos/`) | ⚠️ Kein Blog-Artikel speziell zu Workspace Files gefunden; die Kerninhalte (Dateitypen, 500-MB-Limit, Git-Ordner-Integration) sind aber inhaltlich deckungsgleich mit der aktuellen Doku — keine Widersprüche. Workspace Files sind ein reifes, etabliertes Feature ohne größere 2026er-Ankündigungen. |
| Magic Commands (`%sh`, `%run`, `%fs`) | Keine dedizierten Blog-Artikel gefunden — Kernfunktionalität ist Teil der Notebook-Dokumentation, nicht separat beworben | ✅ Keine Hinweise auf Änderungen; Verhalten von `%sh` (nur Driver-Node) und `%run` (Inline-Ausführung) ist seit Jahren stabil und deckt sich mit der aktuellen Doku. |

### Gesamtfazit

Alle 7 Originaldateien sind inhaltlich weiterhin korrekt und aktuell — kein Blog-Artikel widerspricht den dokumentierten Kernaussagen. Der DBFS-Deprecation-Status und die Volumes-Empfehlung sind gut belegt und stimmen exakt mit der aktuellen Blog-/Doku-Kommunikation von Databricks überein. Einzige nennenswerte Ergänzung: Der neue **FILE-Volume-Typ (Beta)** für unstrukturierte Daten direkt in Managed-Tabellen sowie die **„Disable legacy features"-Einstellung auf Account-Ebene** fehlen in den Originaldateien und könnten bei Gelegenheit ergänzt werden. Für Workspace Files und Magic Commands gibt es keine dedizierten Blog-Ankündigungen, da es sich um reife, seit Langem stabile Kernfunktionen handelt.
