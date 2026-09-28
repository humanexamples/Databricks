# Jenkins Integration

Vollständiges Setup einer CI/CD-Pipeline mit Jenkins über die Databricks CLI und Databricks Asset Bundles — achtstufige `Jenkinsfile`-Pipeline für Build, Test und Deployment eines Python-Wheels samt Notebooks. Teil der [CI/CD](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Initiales Setup](#setup)
2. [Jenkins-Pipeline erstellen](#pipeline-erstellen)
3. [Globale Umgebungsvariablen](#env-vars)
4. [Jenkinsfile: Pipeline-Stufen](#jenkinsfile)
5. [Bundle-Konfiguration](#bundle-config)
6. [Python-Wheel-Bibliotheksstruktur](#wheel-struktur)
7. [Notebook- und Hilfsdateien](#notebooks)
8. [Git-Repository-Vorbereitung](#gitignore)
9. [Pipeline-Ausführung](#ausfuehrung)
10. [Quelle](#quelle)

---

## <a id="setup">1. Initiales Setup</a>

Auf der lokalen Entwicklungsmaschine zu installieren:

- **Databricks CLI** (Version 0.205 oder höher) — „Jenkins nutzt die Databricks CLI, um die Test- und Ausführungsanweisungen dieses Beispiels an den Workspace weiterzugeben."
- **Jenkins** — für das jeweilige Betriebssystem herunterladen und konfigurieren (Linux, macOS, Windows).
- **jq** — Kommandozeilen-JSON-Prozessor zum Parsen der Ausgabe.
- **Python-Wheel-Build-Tools** — installieren via `pip install --upgrade wheel`.

## <a id="pipeline-erstellen">2. Jenkins-Pipeline erstellen</a>

1. Jenkins-Dashboard öffnen, „New Item" wählen.
2. Pipeline-Namen vergeben (Beispiel: `jenkins-demo`).
3. Projekttyp „Pipeline" wählen.
4. Pipeline-Einstellungen konfigurieren: Definition auf „Pipeline script from SCM" setzen; Git als SCM-Provider wählen; Repository-URL des Git-Providers eintragen; Branch im Format `*/<branch-name>` angeben; Script-Pfad auf `Jenkinsfile` setzen; Option „Lightweight checkout" deaktivieren; Konfiguration speichern.

## <a id="env-vars">3. Globale Umgebungsvariablen</a>

Drei Umgebungsvariablen in der Jenkins-Systemkonfiguration setzen (Dashboard → Manage Jenkins → System → Global properties):

- **`DATABRICKS_HOST`** — Databricks-Workspace-URL, beginnend mit `https://`.
- **`DATABRICKS_CLIENT_ID`** — Client-/Application-ID des Service Principal.
- **`DATABRICKS_CLIENT_SECRET`** — OAuth Secret des Service Principal.

## <a id="jenkinsfile">4. Jenkinsfile: Pipeline-Stufen</a>

Vor der Umsetzung zu ersetzende Platzhalter: `<user-name>`/`<repo-name>` (Git-Provider-Zugangsdaten), `<release-branch-name>`, `<databricks-cli-installation-path>`, `<jq-installation-path>`, `<job-prefix-name>`.

**Stage 1 — Checkout:** ruft die neuesten Artefakte aus dem Drittanbieter-Git-Repository in das Jenkins-Arbeitsverzeichnis ab (typischerweise `~/.jenkins/workspace/<pipeline-name>`).

**Stage 2 — Validate Bundle:** `databricks bundle validate -t ${BUNDLETARGET}` — prüft die syntaktische Korrektheit des Bundles.

**Stage 3 — Deploy Bundle:** `databricks bundle deploy -t ${BUNDLETARGET}` — baut eine Python-Wheel-Datei über `setup.py`; deployt Wheel-Datei, Python-Dateien und Notebooks in den Workspace (Standardpfad: `/Workspace/Users/<username>/.bundle/<bundle-name>/<target-name>`).

**Stage 4 — Run Unit Tests:** `databricks bundle run -t ${BUNDLETARGET} run-unit-tests` — nutzt das pytest-Framework.

**Stage 5 — Run Notebook:** `databricks bundle run -t ${BUNDLETARGET} run-dabdemo-notebook` — testet das gebaute Wheel.

**Stage 6 — Evaluate Notebook Runs:** `databricks bundle run -t ${BUNDLETARGET} evaluate-notebook-runs` — Erfolgs-/Fehlschlag-Bewertung.

**Stage 7 — Import Test Results:** `databricks workspace export-dir` — überträgt Testergebnisse vom Workspace auf die lokale Maschine.

**Stage 8 — Publish Test Results:** veröffentlicht Ergebnisse über das Jenkins-JUnit-Plugin zur Visualisierung und Berichterstattung.

## <a id="bundle-config">5. Bundle-Konfiguration (`databricks.yml`)</a>

Im Repository-Root anzulegen, mit folgenden Kernabschnitten:

- **Bundle-Metadaten:** eindeutigen Bundle-Namen setzen (`<bundle-name>`); Variablen für `job_prefix`, `spark_version`, `node_type_id` definieren.
- **Artifacts:** `dabdemo-wheel` vom Typ `whl`, verweist auf `./Libraries/python/dabdemo`.
- **Resources — Jobs:** drei Job-Definitionen erforderlich:
  1. **`run-unit-tests`** — `notebook_task` verweist auf `./run_unit_tests.py`, inkl. pytest-Bibliothek.
  2. **`run-dabdemo-notebook`** — `notebook_task` verweist auf `./dabdemo_notebook.py`, inkl. Wheel-Bibliotheksreferenz.
  3. **`evaluate-notebook-runs`** — `spark_python_task` verweist auf `./evaluate_notebook_runs.py`, inkl. `unittest-xml-reporting`.
- **Targets:** `dev`-Target mit `mode: development`.

## <a id="wheel-struktur">6. Python-Wheel-Bibliotheksstruktur</a>

```
Libraries/
└── python/
    └── dabdemo/
        ├── dabdemo/
        │   ├── __init__.py
        │   ├── __main__.py
        │   ├── addcol.py
        │   └── test_addcol.py
        └── setup.py
```

- **`addcol.py`:** enthält die Kernfunktion `with_status(df)`, die „einer Apache-Spark-DataFrame eine neue Spalte hinzufügt, befüllt mit einem Literal."
- **`test_addcol.py`:** enthält die pytest-kompatible Testklasse `TestAppendCol` mit der Methode `test_with_status()`, die das Verhalten der Funktion gegen Mock-Daten validiert.
- **`__init__.py`:** definiert `__version__` und `__author__`, konfiguriert den Python-Pfad für Modul-Importe.
- **`__main__.py`:** liefert einen Einstiegspunkt mit `main()`-Funktion und Modulpfad-Konfiguration.
- **`setup.py`:** definiert Paketkonfiguration (Name, Version, Autor, Abhängigkeiten, Entry Points) für den Wheel-Build.

## <a id="notebooks">7. Notebook- und Hilfsdateien</a>

**`run_unit_tests.py`:** erstellt das Ausgabeverzeichnis für Testergebnisse; führt pytest gegen den Bibliothekscode aus; erzeugt einen JUnit-XML-Report; Assertions prüfen erfolgreiche Testausführung.

**`dabdemo_notebook.py`:** startet die Python-Umgebung nach der Wheel-Installation neu; importiert `with_status` aus dem Wheel; erstellt einen Beispiel-DataFrame; wendet die Transformation an; zeigt Ergebnisse an.

**`evaluate_notebook_runs.py`:** enthält zwei `unittest`-`TestCase`-Methoden — `test_performance()` (prüft Ausführungsdauer unter 100.000 ms) und `test_job_run()` (bestätigt, dass der Job-Status „Erfolg" entspricht); gibt XML-Ergebnisse in das Workspace-Validierungsverzeichnis aus.

## <a id="gitignore">8. Git-Repository-Vorbereitung</a>

Vor dem Push zur `.gitignore` hinzufügen:

```
.databricks/
.vscode/
Libraries/python/dabdemo/build/
Libraries/python/dabdemo/__pycache__/
Libraries/python/dabdemo/dabdemo.egg-info/
Validation/
```

Verhindert das Committen von Bundle-Arbeitsdateien, Python-Artefakten und generierten Validierungsberichten.

## <a id="ausfuehrung">9. Pipeline-Ausführung</a>

Manueller Start über das Jenkins-Dashboard: Pipeline-Namen anklicken → „Build Now" in der Sidebar wählen → Ausführung über die neueste Run-Nummer überwachen → „Console Output" für detaillierte Logs und Ergebnisse einsehen.

## <a id="quelle">10. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/ci-cd/jenkins

**Stand:** 2026-08-21.
