# Tutorial: Python-Wheel-Datei in Lakeflow Jobs nutzen

Beispiel: eigene Python-Wheel-Datei erstellen und in einem Job ausführen.

## Voraussetzungen

- Python 3
- Pakete `wheel` und `setuptools`:

```bash
pip install wheel setuptools
```

## Schritt 1: Lokales Verzeichnis anlegen

Z. B. `databricks_wheel_test`.

## Schritt 2: Beispiel-Python-Skript erstellen

Speichern unter `my_test_code/__main__.py`:

```python
"""The entry point of the Python Wheel"""
import sys

def main():
  # This method will print the provided arguments
  print('Hello from my func')
  print('Got arguments:')
  print(sys.argv)

if __name__ == '__main__':
  main()
```

## Schritt 3: Metadaten-Datei erstellen

Speichern unter `my_test_code/__init__.py`:

```python
__version__ = "0.0.1"
__author__ = "Databricks"
```

## Schritt 4: Python-Wheel-Datei erstellen

`setup.py` im Root-Verzeichnis. **Hinweis:** Der Teil vor `=` in `entry_points` (hier `run`) ist der Name des Entry Points, der bei der Konfiguration des Python-Wheel-Tasks verwendet wird.

```python
from setuptools import setup, find_packages
import my_test_code

setup(
  name='my_test_package',
  version=my_test_code.__version__,
  author=my_test_code.__author__,
  url='https://databricks.com',
  author_email='john.doe@databricks.com',
  description='my test wheel',
  packages=find_packages(include=['my_test_code']),
  entry_points={
    'group_1': 'run=my_test_code.__main__:main'
  },
  install_requires=[
    'setuptools'
  ]
)
```

Paketieren:

```bash
python3 setup.py bdist_wheel
```

Erzeugt `dist/my_test_package-0.0.1-py3.none-any.whl`.

## Schritt 5: Job erstellen

1. **Jobs & Pipelines** → **Create** → **Job**.
2. Kachel **Python wheel** (ggf. über **Add another task type** suchen).
3. Job optional umbenennen.
4. Task-Namen vergeben.
5. Typ **Python wheel**.
6. **Package name**: `my_test_package`.
7. **Entry point**: `run`.
8. **Compute**: bestehenden Job-Cluster wählen oder **Add new job cluster**.
9. Wheel-Datei angeben: unter **Environment and Libraries** → Stift neben **Default** → **Add dependency** → Ordner-Icon → Wheel-Datei per Drag & Drop → **Confirm**.
10. Unter **Parameters**: **Positional arguments** (JSON-Array, z. B. `["first argument","first value","second argument","second value"]`) oder **Keyword arguments** (Key/Value über **Add**).
11. **Save task**.

## Schritt 6: Job ausführen

**Run Now** → Tab **Runs** → Link in Spalte **Start time** → Ausgabe im **Output**-Panel prüfen, inkl. übergebener Argumente.

## Quelle

- https://docs.databricks.com/aws/en/jobs/how-to/use-python-wheels-in-workflows
