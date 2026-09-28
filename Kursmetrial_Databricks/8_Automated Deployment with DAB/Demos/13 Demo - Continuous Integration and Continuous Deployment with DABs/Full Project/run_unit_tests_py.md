# 13 Demo - Continuous Integration and Continuous Deployment with DABs/Full Project/run_unit_tests.py

*(Databricks-Notebook, konvertiert nach Markdown)*

### Pytest importieren

```python
!pip install pytest==8.3.4

dbutils.library.restartPython()
```

### Autoreload für Python-Module

Wenn Sie bei der Entwicklung von Python-Code mehrere Dateien bearbeiten, können Sie die Erweiterung autoreload aktivieren, damit importierte Module automatisch neu geladen werden und Befehlsausführungen diese Änderungen übernehmen. Verwenden Sie die folgenden Befehle in einer beliebigen Notebook-Zelle oder Python-Datei, um die Erweiterung autoreload zu aktivieren.

Dokumentation: [Autoreload for Python modules](https://docs.databricks.com/en/files/workspace-modules.html#autoreload-for-python-modules)

```python
# MAGIC %load_ext autoreload
# MAGIC %autoreload 2
```

### Die Unit-Tests ausführen

```python
## Die Module `pytest` und `sys` importieren.
import pytest
import sys

from src.helpers import project_functions

sys.dont_write_bytecode = True

retcode = pytest.main(["./tests/unit_tests/test_spark_helper_functions.py", "-v", "-p", "no:cacheprovider"])

# Die Zellenausführung fehlschlagen lassen, wenn Tests fehlschlagen.
assert retcode == 0, "The pytest invocation failed. See the log for details."
```
