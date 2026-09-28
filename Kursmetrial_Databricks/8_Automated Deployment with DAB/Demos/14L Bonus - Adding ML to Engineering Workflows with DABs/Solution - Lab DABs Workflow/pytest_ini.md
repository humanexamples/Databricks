# 14L Bonus - Adding ML to Engineering Workflows with DABs/Solution - Lab DABs Workflow/pytest.ini

```ini
[pytest]

# Die Einstellung pythonpath = . in pytest.ini stellt sicher, dass beim Ausführen von pytest das aktuelle Verzeichnis zum Python-Modulsuchpfad hinzugefügt wird.
# So kann pytest Code aus dem Projekt-Root oder benachbarten Verzeichnissen importieren, ohne dass sys.path manuell geändert werden muss.
pythonpath = .  

# Die Zeile addopts weist pytest an, Ihre Tests immer über das importlib-System von Python statt über die ältere Methode des Pfad-Einfügens zu importieren. Das macht Test-Importe vorhersehbarer, insbesondere wenn Ihr Projekt in einer Umgebung mit ungewöhnlichen Pfaden (wie dem Databricks-Workspace) läuft.
addopts = --import-mode=importlib

## Für dieses einfache Projekt Warnungen zu veralteten Funktionen ignorieren
filterwarnings = ignore::DeprecationWarning
```
