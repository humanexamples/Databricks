# Git Folder Serverless

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/notebooks/git-folder-serverless>
> **Beta**

Stellt **eine** Serverless-Compute-Ressource bereit, die von allen Assets in einem Git-Ordner (Notebooks und Dateien) **gemeinsam** genutzt wird. Damit entfällt das Starten separater Compute-Ressourcen pro Notebook beim Arbeiten über mehrere Dateien.

## Voraussetzungen

- Das Projekt muss in einem **Git-Ordner** organisiert sein.
- Der Git-Ordner muss über den **Git-Folder-Editor** geöffnet werden.
- Existiert eine Root-`pyproject.toml`, muss deren `environment_version` auf **5 oder höher** stehen.

## Gemeinsames Compute und gemeinsame Umgebung

Alle Notebooks und Dateien im selben Git-Ordner hängen an **einer** Git-Folder-Serverless-Compute-Ressource und verwenden die über `pyproject.toml` verwaltete Umgebung.

- Nur Assets **innerhalb** des zugehörigen Git-Ordners können auf die geteilte Compute-Ressource zugreifen.
- In einem Notebook definierte Python-Variablen sind in einem **anderen** Notebook **nicht** verfügbar.
- Aus angehängten Notebooks/Dateien geöffnete Web-Terminals laufen auf **derselben** Compute-Ressource.

## Aktivierung im Editor

1. Im Workspace-Seitenbereich zum Git-Ordner navigieren
2. **Open in editor** klicken
3. Ein Notebook oder eine Datei im Ordner öffnen
4. Compute-Dropdown öffnen
5. **Git Folder Serverless** auswählen
6. Notebook/Datei ausführen, um die Compute-Ressource zu initialisieren

## Umgebungsverwaltung über `pyproject.toml`

Anders als bei Standard-Serverless-Notebooks (Abhängigkeiten pro Notebook) zentralisiert Git Folder Serverless die Python-Abhängigkeiten in einer Root-`pyproject.toml`.

### Abhängigkeiten über Notebook-Befehle hinzufügen

1. Notebook öffnen, das an Git Folder Serverless angehängt ist
2. Prüfen, dass `pyproject.toml` im Git-Ordner-Root existiert; ggf. über das Environment-Seitenpanel erstellen
3. `%uv add <package>` ausführen:
   ```
   %uv add cowsay
   ```
4. `%uv sync` ausführen, um die Änderungen anzuwenden und `uv.lock` zu aktualisieren/erzeugen:
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

Anschließend oben im Datei-Editor **Apply** klicken. Die aktualisierte Umgebung wird für alle Notebooks/Dateien der geteilten Compute-Ressource verfügbar.

## Zusammenarbeit über Git

- **Single-User-Modell:** *"Only the user who starts a Git Folder Serverless compute resource can run workloads on it."* Andere Nutzer werden blockiert.
- Databricks empfiehlt, dass Mitarbeitende *"clone the repository into a Git folder in their personal workspace folder"* — jede Person erhält eine eigene Compute-Ressource und Umgebung. Austausch über Branches/Commits/Pushes/Pulls.

## Einschränkungen

- Compute-Sharing ist durch die **Serverless Usage Policy** begrenzt: Notebooks/Dateien im selben Git-Ordner mit **unterschiedlichen** Usage Policies erhalten **separate** Compute-Ressourcen statt einer gemeinsamen.

## Verwandte Themen

- [02 Notebooks.md](02%20Notebooks.md) · [04 Umgebung und Abhaengigkeiten.md](04%20Umgebung%20und%20Abhaengigkeiten.md)
- Doku: *Create and manage Git folders*, *Run shell commands in the web terminal*
