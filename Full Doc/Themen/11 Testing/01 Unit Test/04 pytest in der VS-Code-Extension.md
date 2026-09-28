# pytest in der VS-Code-Extension

Zwei Wege, Python-Code über die Databricks-IDE-Extension zu testen: pytest gegen einen Remote-Cluster, oder Databricks Connect für lokales Testen mit Spark-APIs. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Methode 1: pytest](#pytest)
3. [Methode 2: Databricks Connect](#databricks-connect)
4. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

Die Databricks-IDE-Extension ermöglicht das Testen von Python-Code über zwei primäre Ansätze: pytest für Remote-Cluster-Testing, und Databricks Connect für lokales Testen mit Spark-APIs.

## <a id="pytest">2. Methode 1: pytest</a>

### Zweck und Umfang

„pytest lässt sich auf lokalem Code ausführen, der keine Verbindung zu einem Cluster in einem Remote-Databricks-Workspace benötigt." Die Extension unterstützt aber auch die Ausführung von pytest gegen Remote-Workspace-Code. Gut geeignet für „Funktionen, die PySpark-DataFrames im lokalen Speicher entgegennehmen und zurückgeben."

### Schritt 1 — Testdateien erstellen

Eine Python-Testdatei (Beispiel: `spark_test.py`) mit pytest-Fixtures und Testfunktionen anlegen. Die Fixture-Komponente etabliert eine SparkSession: „eine SparkSession (den Einstiegspunkt zur Spark-Funktionalität) auf dem Cluster im Remote-Databricks-Workspace erstellen — Unit Tests haben standardmäßig keinen Zugriff auf diese SparkSession." Ein Beispieltest prüft Tabelleninhalte, ob „die angegebene Zelle in der Tabelle den angegebenen Wert enthält."

### Schritt 2 — pytest-Runner erstellen

Eine zweite Python-Datei (Beispiel: `pytest_databricks.py`) orchestriert die Testausführung:

- „pytest durchsucht alle Dateien mit dem Endungsmuster '_test.py' nach Tests."
- Innerhalb der Dateien „führt pytest jede Funktion aus, deren Name mit 'test_' beginnt."
- Der Runner ermittelt „den Pfad zum Verzeichnis dieser Datei im Workspace."
- Überspringt „das Schreiben von `.pyc`-Dateien in den Bytecode-Cache auf dem Cluster."

### Schritt 3 — Custom Run Configuration konfigurieren

Über das VS-Code-Run-Menü eine eigene Run-Konfiguration erstellen. Die `launch.json` erfordert Anpassungen:

- Konfiguration von „Run on Databricks" auf einen eigenen Bezeichner umbenennen.
- `program`-Wert auf den Pfad der Runner-Datei ändern.
- `args` auf die Testdatei-Speicherorte anpassen.

Beispiel: `"program": "${workspaceFolder}/pytest_databricks.py"` und `"args": ["."]`.

### Schritt 4 — Tests ausführen

Vor der Ausführung sicherstellen, dass pytest über den Libraries-Tab der Workspace-Einstellungen auf dem Cluster installiert ist. Dann: View > Run-Menü, Konfiguration wählen, grünen „Start Debugging"-Pfeil anklicken.

Die Ausgabe erscheint in der Debug Console mit „collected 1 item" und Testergebnissen, markiert mit Punkten (bestanden) oder `F` (fehlgeschlagen).

## <a id="databricks-connect">3. Methode 2: Databricks Connect</a>

### Konfiguration

Setup-Verfahren für die Databricks-Connect-Integration mit der Extension befolgen, um lokales Spark-API-Testing zu ermöglichen (siehe [03 Testing mit Databricks Connect.md](03%20Testing%20mit%20Databricks%20Connect.md)).

### Testerstellung

Testdateien (Beispiel: `main_test.py`) mit Standard-pytest-Syntax erstellen:

```python
def test_find_all_taxis():
    taxis = main.find_all_taxis()
    assert taxis.count() > 5
```

### Launch-Konfiguration

Eine debugpy-basierte Launch-Konfiguration erfordert das Feld `"databricks": true`, um die Databricks-Connect-Funktionalität zu aktivieren — erlaubt lokalem Code den Zugriff auf Remote-Cluster-Ressourcen.

### Ausführung

Über View > Testing-Menü zugreifen, dann Debug-Icons neben den Testdateien anklicken. „Das bloße Ausführen des Tests löst die angepasste Debug-Konfiguration nicht aus, und der Code hätte keinen Zugriff auf Databricks Connect" — der Debug-Ansatz stellt die korrekte Konnektivität sicher.

## <a id="quelle">4. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/vscode-ext/pytest

**Stand:** 2026-08-21.
