# nutter — Databricks-Notebook-Testing-Framework

Microsofts Open-Source-Framework zum Testen von Databricks-Notebooks als Ganzes (im Gegensatz zu pytest/unittest, die einzelne Python-Funktionen testen) — nutzt intern `dbutils.notebook.run()` (siehe [05 Notebook Workflows als Testing-Orchestrierung (Legacy-Beispiel).md](05%20Notebook%20Workflows%20als%20Testing-Orchestrierung%20%28Legacy-Beispiel%29.md)), um ein zu testendes Notebook auszuführen und anschließend Assertions gegen dessen Ergebnisse zu prüfen. Teil der [Testing](../Uebersicht.md)-Reihe, Kapitel [01 Unit Test](../01%20Unit%20Test/).

## Abschnittsübersicht

1. [Überblick und Architektur](#ueberblick)
2. [Die `NutterFixture`-Klasse](#nutterfixture)
3. [Lifecycle-Methoden](#lifecycle)
4. [Tests im Notebook ausführen](#im-notebook)
5. [Installation](#installation)
6. [Umgebungsvariablen](#umgebung)
7. [CLI-Befehle](#cli)
8. [Fortgeschrittene Muster](#fortgeschritten)
9. [Ausführungsreihenfolge](#reihenfolge)
10. [CLI-Flags-Referenz](#flags)
11. [Azure-DevOps-Integration](#azure-devops)
12. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick und Architektur</a>

Nutter besteht aus zwei Komponenten:

1. **Nutter Runner** — serverseitige Bibliothek, auf dem Databricks-Cluster installiert.
2. **Nutter CLI** — clientseitiges Werkzeug für Entwickler-Laptops und Build-Agents.

Ermöglicht sowohl lokale Entwicklungs-Workflows als auch Integration in CI/CD-Pipelines wie Azure DevOps (siehe Abschnitt 11 sowie [03 Azure DevOps Integration.md](../../10%20Developers/02%20CI-CD/03%20Azure%20DevOps%20Integration.md)).

## <a id="nutterfixture">2. Die `NutterFixture`-Klasse</a>

Tests werden implementiert, indem eine Klasse `NutterFixture` erweitert:

```python
from runtime.nutterfixture import NutterFixture, tag
class MyTestFixture(NutterFixture):
    def run_test_name(self):
        dbutils.notebook.run('notebook_under_test', 600, args)

    def assertion_test_name(self):
        some_tbl = sqlContext.sql('SELECT COUNT(*) AS total FROM sometable')
        first_row = some_tbl.first()
        assert (first_row[0] == 1)
```

## <a id="lifecycle">3. Lifecycle-Methoden</a>

Jeder Testfall folgt einer Namenskonvention mit den Präfixen `before_`, `run_`, `assertion_` und `after_` — Nutter entdeckt und führt sie in dieser Reihenfolge aus:

| Präfix | Pflicht? | Zweck |
|---|---|---|
| `before_(testname)` | optional | Setup vor dem Run |
| `run_(testname)` | optional | führt das zu testende Notebook aus |
| `assertion_(testname)` | **erforderlich** | prüft die Testergebnisse |
| `after_(testname)` | optional | Cleanup nach den Assertions |

Zusätzlich auf Fixture-Ebene (nicht pro Testfall):

- **`before_all()`** — läuft vor allen Tests der Fixture.
- **`after_all()`** — läuft nach allen Tests der Fixture.

## <a id="im-notebook">4. Tests im Notebook ausführen</a>

```python
result = MyTestFixture().execute_tests()
print(result.to_string())
result.exit(dbutils)
```

**Wichtig:** `result.exit(dbutils)` gibt die Ergebnisse an die CLI zurück — nach diesem Aufruf werden nachfolgende `print`-Ausgaben nicht mehr angezeigt.

## <a id="installation">5. Installation</a>

**Cluster (Runner):** Installation als Cluster-Bibliothek über PyPI (Databricks-Cluster-Bibliotheks-UI).

**CLI:**

```bash
pip install nutter
```

Installation innerhalb einer virtuellen Umgebung wird empfohlen.

## <a id="umgebung">6. Umgebungsvariablen</a>

**Linux:**

```bash
export DATABRICKS_HOST=<HOST>
export DATABRICKS_TOKEN=<TOKEN>
```

**Windows PowerShell:**

```powershell
$env:DATABRICKS_HOST="HOST"
$env:DATABRICKS_TOKEN="TOKEN"
```

## <a id="cli">7. CLI-Befehle</a>

### `list` — Test-Notebooks auflisten

```bash
nutter list /dataload
nutter list /dataload --recursive
```

Listet Test-Notebooks nach der Namenskonvention `test_*` auf; `--recursive` bezieht Unterverzeichnisse mit ein.

### `run` — einzelnes Notebook

```bash
nutter run dataload/test_sourceLoad --cluster_id 0123-12334-tonedabc \
  --notebook_params "{\"example_key_1\": \"example_value_1\"}"
```

### `run` — mehrere Notebooks per Pattern

```bash
nutter run dataload/src* --cluster_id 0123-12334-tonedabc \
  --notebook_params "{\"example_key_1\": \"example_value_1\"}"
```

Patterns matchen den Test-Notebook-Namen **ohne** das `test_`-Präfix.

### `run` — rekursiv

```bash
nutter run dataload/ --cluster_id 0123-12334-tonedabc --recursive
```

### Parallele Ausführung

```bash
nutter run dataload/ --cluster_id 0123-12334-tonedabc \
  --recursive --max_parallel_tests 2
```

## <a id="fortgeschritten">8. Fortgeschrittene Muster</a>

### Mehrere Assertions ohne `run_`-Methode

```python
class MultiTestFixture(NutterFixture):
    def before_all(self):
        dbutils.notebook.run('notebook_under_test', 600, args)

    def assertion_test_case_1(self):
        ...

    def assertion_test_case_2(self):
        ...
```

### Paralleler Fixture-Runner

Mehrere Fixtures gleichzeitig ausführen:

```python
from runtime.runner import NutterFixtureParallelRunner

parallel_runner = NutterFixtureParallelRunner(num_of_workers=2)
parallel_runner.add_test_fixture(CustomerTestFixture())
parallel_runner.add_test_fixture(CountryTestFixture())

result = parallel_runner.execute()
print(result.to_string())
```

### Geteilter State zwischen Tests

Instanzvariablen, die im Konstruktor definiert werden, bleiben über alle Testfälle der Fixture hinweg erhalten:

```python
class TestFixture(NutterFixture):
    def __init__(self):
        self.file = '/data/myfile'
        NutterFixture.__init__(self)
```

## <a id="reihenfolge">9. Ausführungsreihenfolge</a>

„Nachdem die Testfälle geladen wurden, nutzt Nutter ein sortiertes Dictionary, um sie nach Namen zu ordnen" — Tests laufen also in alphabetischer Reihenfolge (analog zu `unittest`, siehe [11 unittest — Python-Standardbibliothek-Referenz.md](11%20unittest%20%E2%80%94%20Python-Standardbibliothek-Referenz.md), Abschnitt 3).

## <a id="flags">10. CLI-Flags-Referenz</a>

**`run`-Befehl:**

| Flag | Bedeutung |
|---|---|
| `--timeout` | Ausführungs-Timeout in Sekunden (Standard: 120) |
| `--junit_report` | erzeugt einen JUnit-XML-Report |
| `--tags_report` | erzeugt einen CSV-Report mit Test-Tags |
| `--max_parallel_tests` | maximale Anzahl gleichzeitiger Testausführungen |
| `--recursive` | führt Tests in der gesamten Ordnerhierarchie aus |
| `--poll_wait_time` | Polling-Intervall in Sekunden (Standard: 5) |
| `--notebook_params` | übergibt Parameter, abrufbar via `dbutils.widgets.get('key')` |

**`list`-Befehl:**

| Flag | Bedeutung |
|---|---|
| `--recursive` | listet Tests in der gesamten Ordnerhierarchie |

## <a id="azure-devops">11. Azure-DevOps-Integration</a>

Beispiel-Pipeline-Schritte: Nutter installieren, Tests ausführen, JUnit-Ergebnisse veröffentlichen:

```yaml
- script: |
    pip install nutter
  displayName: 'Install Nutter'

- script: |
    nutter run /Shared/ $CLUSTER --recursive --junit_report
  displayName: 'Execute Nutter'
  env:
      CLUSTER: $(clusterID)
      DATABRICKS_HOST: $(databricks_host)
      DATABRICKS_TOKEN: $(databricks_token)

- task: PublishTestResults@2
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: '**/test-*.xml'
```

Die CLI beendet sich bei Testfehlschlägen mit einem Exit-Code ungleich null — dadurch erkennt die Pipeline Fehlschläge automatisch. Vertiefende Azure-DevOps-Pipeline-Beispiele (nicht nutter-spezifisch): [03 Azure DevOps Integration.md](../../10%20Developers/02%20CI-CD/03%20Azure%20DevOps%20Integration.md).

### Quelle

- https://github.com/microsoft/nutter

**Stand:** 2026-09-01.
