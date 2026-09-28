# Databricks SDK für Python

Werkzeug zur Automatisierung von Databricks-Operationen und zur Beschleunigung der Entwicklung — implementiert die Databricks-„Unified Authentication" (siehe [Authenticate developer tools/12 Unified Authentication.md](Authenticate%20developer%20tools/12%20Unified%20Authentication.md)) für einen einheitlichen Auth-Ansatz über mehrere Databricks-Tools und -SDKs hinweg. **Status:** Beta, aber für den Produktiveinsatz freigegeben.

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [Installation](#installation)
3. [Authentifizierung](#authentifizierung)
4. [Code-Beispiele](#beispiele)
5. [Databricks Utilities über das SDK nutzen](#dbutils)
6. [Testen mit Mocking](#testing)
7. [Lokal vs. im Notebook ausführen](#ausfuehrung)
8. [Wichtige Konfigurationshinweise](#konfiguration)
9. [Weiterführende Ressourcen](#ressourcen)
10. [Quelle](#quelle)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

**Lokale Entwicklungsmaschine:**

- Konfigurierte Databricks-Authentifizierung.
- Python 3.8 oder höher installiert.
- Empfohlen: Python-Version, die der Ziel-Compute-Ressource entspricht (die offiziellen Beispiele richten sich an Databricks Runtime 13.3 LTS mit Python 3.10).
- Empfohlen: eine Python-Virtual-Environment via `venv` oder Poetry anlegen.

**Notebook:**

- Databricks-Cluster mit installiertem SDK (ab Runtime 13.3 LTS standardmäßig vorhanden).
- Für Runtime 12.2 LTS und darunter: manuelle Installation nötig (vgl. dieselbe Voraussetzung für `pytest.main` in [07 PySpark-Testing-Utilities und Praxisbeispiel.md](../11%20Testing/01%20Unit%20Test/07%20PySpark-Testing-Utilities%20und%20Praxisbeispiel.md), Abschnitt 6).

## <a id="installation">2. Installation</a>

**Lokal, mit venv:**

```bash
pip3 install databricks-sdk
pip3 install databricks-sdk==0.1.6   # bestimmte Version
pip3 install --upgrade databricks-sdk
pip3 show databricks-sdk             # Version prüfen
```

**Lokal, mit Poetry:**

```bash
poetry add databricks-sdk
poetry add databricks-sdk==0.1.6     # bestimmte Version
poetry add databricks-sdk@latest     # aktualisieren
poetry show databricks-sdk           # Version prüfen
```

**Im Databricks-Notebook:**

```python
%pip install databricks-sdk --upgrade
```

```python
dbutils.library.restartPython()
```

```python
%pip show databricks-sdk | grep -oP '(?<=Version: )\S+'
```

## <a id="authentifizierung">3. Authentifizierung</a>

### Option 1 — Default Authentication (empfohlen)

Ein Databricks-Konfigurationsprofil mit den nötigen Feldern anlegen (bzw. die entsprechenden Umgebungsvariablen setzen), dann den Client **ohne Argumente** instanziieren:

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
```

### Option 2 — Hartkodierte Credentials (nicht empfohlen)

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient(
  host = 'https://...',
  token = '...')
```

### Unterstützte Authentifizierungsarten

| Methode | Verfügbar ab |
|---|---|
| Personal-Access-Token-Authentifizierung | alle SDK-Versionen |
| OAuth Machine-to-Machine (M2M) | alle SDK-Versionen |
| OAuth User-to-Machine (U2M) | SDK-Version 0.1.9+ |
| Standard-Notebook-Authentifizierung | SDK-Version 0.6.0+ (die meisten Runtimes); 0.20.0+ für Runtime 15.1 |

**Einschränkungen der Standard-Notebook-Authentifizierung:**

- Funktioniert **nur** auf dem Cluster-Driver-Knoten, nicht auf Worker-/Executor-Knoten.
- Funktioniert **nicht** mit Databricks-Konfigurationsprofilen.
- **Nicht unterstützt** mit Databricks Container Services.
- **Nicht unterstützt** für Account-Ebenen-API-Aufrufe (dafür ist der `AccountClient` mit expliziten Credentials nötig, siehe Abschnitt 4).

## <a id="beispiele">4. Code-Beispiele</a>

**Cluster auflisten:**

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
for c in w.clusters.list():
  print(c.cluster_name)
```

**Cluster erstellen:**

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
print("Attempting to create cluster. Please wait...")
c = w.clusters.create_and_wait(
  cluster_name = 'my-cluster',
  spark_version = '12.2.x-scala2.12',
  node_type_id = 'i3.xlarge',
  autotermination_minutes = 15,
  num_workers = 1)
print(f"The cluster is now ready at " \
      f"{w.config.host}#setting/clusters/{c.cluster_id}/configuration\n")
```

**Cluster dauerhaft löschen:**

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
c_id = input('ID of cluster to delete (for example, 1234-567890-ab123cd4): ')
w.clusters.permanent_delete(cluster_id = c_id)
```

**Job erstellen** (vgl. das äquivalente Beispiel für die CLI/`databricks jobs create` in [03 Jobs automatisieren.md](../07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/01%20Uebersicht/03%20Jobs%20automatisieren.md)):

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import Task, NotebookTask, Source
w = WorkspaceClient()
job_name = input("Some short name for the job (for example, my-job): ")
description = input("Some short description for the job (for example, My job): ")
existing_cluster_id = input("ID of the existing cluster in the workspace to run the job on (for example, 1234-567890-ab123cd4): ")
notebook_path = input("Workspace path of the notebook to run (for example, /Users/someone@example.com/my-notebook): ")
task_key = input("Some key to apply to the job's tasks (for example, my-key): ")
print("Attempting to create the job. Please wait...\n")
j = w.jobs.create(
  name = job_name,
  tasks = [
    Task(
      description = description,
      existing_cluster_id = existing_cluster_id,
      notebook_task = NotebookTask(
        base_parameters = dict(""),
        notebook_path = notebook_path,
        source = Source("WORKSPACE")
      ),
      task_key = task_key
    )
  ])
print(f"View the job at {w.config.host}/#job/{j.job_id}\n")
```

**Job mit Serverless Compute erstellen:**

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import NotebookTask, Source, Task
w = WorkspaceClient()
j = w.jobs.create(
  name = "My Serverless Job",
  tasks = [
    Task(
      notebook_task = NotebookTask(
      notebook_path = "/Users/someone@example.com/MyNotebook",
      source = Source("WORKSPACE")
      ),
      task_key = "MyTask",
   )
  ])
```

**Unity-Catalog-Volume-Dateien verwalten:**

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
# Volume-, Ordner- und Dateidetails definieren.
catalog = 'main'
schema = 'default'
volume = 'my-volume'
volume_path = f"/Volumes/{catalog}/{schema}/{volume}"
volume_folder = 'my-folder'
volume_folder_path = f"{volume_path}/{volume_folder}"
volume_file = 'data.csv'
volume_file_path = f"{volume_folder_path}/{volume_file}"
upload_file_path = './data.csv'

# Leeren Ordner in einem Volume anlegen.
w.files.create_directory(volume_folder_path)

# Datei in ein Volume hochladen (Methode 1: empfohlen bei Daten aus lokaler Datei)
w.files.upload_from(volume_file_path, upload_file_path, overwrite=True)

# Datei in ein Volume hochladen (Methode 2: empfohlen bei In-Memory-Daten)
with open(upload_file_path, "rb") as f:
    w.files.upload(volume_file_path, io.BytesIO(f.read()), overwrite=True)

# Volume-Inhalt auflisten.
for item in w.files.list_directory_contents(volume_path):
  print(item.path)

# Ordnerinhalt im Volume auflisten.
for item in w.files.list_directory_contents(volume_folder_path):
  print(item.path)

# Datei aus Volume herunterladen (Methode 1: empfohlen für lokalen Storage)
w.files.download_to(volume_file_path, local_download_path)

# Datei aus Volume herunterladen (Methode 2: empfohlen bei In-Memory-Daten)
resp = w.files.download(volume_file_path)
chunk_size = 8192
with resp.contents as f:
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        print(f"Read {len(chunk)} characters")

# Datei aus Volume löschen.
w.files.delete(volume_file_path)

# Ordner aus Volume löschen.
w.files.delete_directory(volume_folder_path)
```

**Account-Ebenen-Gruppen auflisten** (nutzt `AccountClient` statt `WorkspaceClient` — erfordert explizite Credentials, siehe Abschnitt 3):

```python
from databricks.sdk import AccountClient
a = AccountClient()
for g in a.groups.list():
  print(g.display_name)
```

## <a id="dbutils">5. Databricks Utilities über das SDK nutzen</a>

Vergleiche die volle `dbutils`-Referenz in [06 Databricks Utils](06%20Databricks%20Utils/00%20Uebersicht.md).

**Über `WorkspaceClient`** (unterstützt alle Authentifizierungsarten):

```python
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
d = w.dbutils.fs.ls('/')
for f in d:
  print(f.path)
```

**Direkter Import** (nur mit Standard-Notebook-Authentifizierung):

```python
from databricks.sdk.runtime import *
d = dbutils.fs.ls('/')
for f in d:
  print(f.path)
```

**Verfügbare Befehlsgruppen:**

| Kontext | Verfügbare Command Groups |
|---|---|
| Lokale Entwicklung | `dbutils.fs`, `dbutils.secrets`, `dbutils.widgets`, `dbutils.jobs` |
| Notebooks | alle Command Groups (`dbutils.notebook` dabei auf zwei Verschachtelungsebenen begrenzt) |

## <a id="testing">6. Testen mit Mocking</a>

Beispiel-Hilfsfunktion in `helpers.py`:

```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.compute import ClusterDetails

def create_cluster(
  w: WorkspaceClient,
  cluster_name: str,
  spark_version: str,
  node_type_id: str,
  autotermination_minutes: int,
  num_workers: int) -> ClusterDetails:
  response = w.clusters.create(
    cluster_name = cluster_name,
    spark_version = spark_version,
    node_type_id = node_type_id,
    autotermination_minutes = autotermination_minutes,
    num_workers = num_workers
  )
  return response
```

Testdatei `test_helpers.py` — mockt den `WorkspaceClient` über `unittest.mock.create_autospec` (zu `unittest` siehe [11 unittest — Python-Standardbibliothek-Referenz.md](../11%20Testing/01%20Unit%20Test/11%20unittest%20%E2%80%94%20Python-Standardbibliothek-Referenz.md)):

```python
from databricks.sdk import WorkspaceClient
from helpers import *
from unittest.mock import create_autospec

def test_create_cluster():
  # Einen Mock-WorkspaceClient erstellen.
  mock_workspace_client = create_autospec(WorkspaceClient)
  # Den cluster_id-Rückgabewert des Mocks setzen.
  mock_workspace_client.clusters.create.return_value.cluster_id = '123abc'
  # Die tatsächliche Funktion mit dem Mock aufrufen.
  response = create_cluster(
    w = mock_workspace_client,
    cluster_name = 'Test Cluster',
    spark_version = '<spark-version>',
    node_type_id = '<node-type-id>',
    autotermination_minutes = 15,
    num_workers = 1
  )
  # Erwarteten Rückgabewert prüfen.
  assert response.cluster_id == '123abc'
```

Ausführen mit:

```bash
pytest
```

(vollständige pytest-Referenz siehe [08 pytest — Grundlagen und Referenz.md](../11%20Testing/01%20Unit%20Test/08%20pytest%20%E2%80%94%20Grundlagen%20und%20Referenz.md)).

## <a id="ausfuehrung">7. Lokal vs. im Notebook ausführen</a>

**Lokal, mit venv:**

```bash
python3.10 main.py
```

**Lokal, mit Poetry:**

```bash
poetry run python3.10 main.py
```

**Im Databricks-Notebook:** Zellen mit Python-Code erstellen, die `WorkspaceClient()` ohne Argumente für Default Authentication nutzen.

## <a id="konfiguration">8. Wichtige Konfigurationshinweise</a>

- **Während der Beta-Phase:** Abhängigkeiten auf konkrete Minor-Versionen in `requirements.txt` bzw. `pyproject.toml` pinnen.
- Default Authentication prüft Umgebungsvariablen bzw. Konfigurationsprofile.
- Private-Link-Redirects, die zu einer Login-Seiten-Fehlermeldung führen, deuten auf eine Authentifizierungs-Fehlkonfiguration hin.
- Sicherstellen, dass der Databricks-Host korrekt gesetzt ist und keine Firewall den API-Traffic blockiert.
- Account-Ebenen-Operationen erfordern explizite Credentials (nicht mit Notebook-Authentifizierung nutzbar) — siehe `AccountClient`-Beispiel in Abschnitt 4.

## <a id="ressourcen">9. Weiterführende Ressourcen</a>

- Offizielle SDK-Dokumentation: https://databricks-sdk-py.readthedocs.io
- Code-Beispiel-Repository: https://github.com/databricks/databricks-sdk-py/tree/main/examples
- Workspace-API-Referenz: https://databricks-sdk-py.readthedocs.io/en/latest/workspace/index.html
- Account-API-Referenz: https://databricks-sdk-py.readthedocs.io/en/latest/account/index.html
- Weiterführende Doku-Verweise (Logging, Long-Running Operations, Paginated Responses, OAuth Single Sign-On) sowie die Databricks-Labs-Plugins für pytest (Integrationstests) und pylint (Code-Qualität) — jeweils ohne eigene URL auf der Quellseite genannt.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/sdk-python

**Stand:** 2026-09-01.
