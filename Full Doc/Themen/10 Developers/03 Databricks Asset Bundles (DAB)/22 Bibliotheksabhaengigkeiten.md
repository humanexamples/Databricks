# Bibliotheksabhängigkeiten (`libraries`)

Alle unterstützten Bibliothekstypen für das `libraries`-Mapping auf Task- bzw. Pipeline-Ebene: Wheel, JAR, PyPI, Maven, `requirements.txt` sowie moderne `uv`/`pyproject.toml`-basierte Verwaltung. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Python-Wheel-Dateien](#whl)
2. [JAR-Dateien](#jar)
3. [PyPI-Pakete](#pypi)
4. [Maven-Pakete](#maven)
5. [`requirements.txt`](#requirements)
6. [`uv` und `pyproject.toml`](#uv)
7. [Wichtige Hinweise](#hinweise)
8. [Quelle](#quelle)

---

## <a id="whl">1. Python-Wheel-Dateien</a>

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          libraries:
            - whl: ./my-wheel-0.1.0.whl
            - whl: /Workspace/Shared/Libraries/my-wheel-0.0.1-py3-none-any.whl
            - whl: /Volumes/main/default/my-volume/my-wheel-0.1.0.whl
```

**Unterstützte Quellorte:** lokale Pfade, Workspace-Dateien, Unity-Catalog-Volumes.

Siehe auch [21 Private Artefakte.md](21%20Private%20Artefakte.md) für Wheels aus privaten Paketquellen sowie [03 Python- und Scala-Artefakte.md](03%20Python-%20und%20Scala-Artefakte.md) für das Bauen eigener Wheels.

## <a id="jar">2. JAR-Dateien</a>

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          libraries:
            - jar: /Volumes/main/default/my-volume/my-java-library-1.0.jar
```

**Unterstützte Quellorte:** Unity-Catalog-Volumes, Cloud-Object-Storage, lokale Dateipfade.

## <a id="pypi">3. PyPI-Pakete</a>

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          libraries:
            - pypi:
                package: wheel==0.41.2
            - pypi:
                package: numpy==1.25.2
                repo: https://pypi.org/simple/
```

Ohne `repo`-Angabe wird der Standard-`pip`-Index (`https://pypi.org/simple`) verwendet.

## <a id="maven">4. Maven-Pakete</a>

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          libraries:
            - maven:
                coordinates: com.databricks:databricks-sdk-java:0.8.1
            - maven:
                coordinates: com.databricks:databricks-dbutils-scala_2.13:0.1.4
                repo: https://mvnrepository.com/
                exclusions:
                  - org.scala-lang:scala-library:2.13.0-RC*
```

Koordinaten im Gradle-Stil; `repo` optional; ohne Angabe werden sowohl das Maven-Central-Repository als auch das Spark-Packages-Repository durchsucht.

## <a id="requirements">5. `requirements.txt`</a>

```yaml
resources:
  jobs:
    my_job:
      tasks:
        - task_key: my_task
          libraries:
            - requirements: ./local/path/requirements.txt
```

Unterstützte Pfade: lokal, Workspace, Unity-Catalog-Volume.

## <a id="uv">6. `uv` und `pyproject.toml`</a>

Für Python-Dependency-Management empfiehlt die Doku **`uv`**, mit Abhängigkeiten in `pyproject.toml`:

```toml
[project]
name = "test"
version = "0.0.1"
requires-python = ">=3.10,<3.13"
dependencies = [
    "numpy==1.25.2"
]
```

Einbindung in Bundle-Ressourcen (Beispiel: Pipeline):

```yaml
resources:
  pipelines:
    test_uv_etl:
      name: test_uv_etl
      libraries:
        - glob:
            include: ../src/test_uv_etl/transformations/**
      environment:
        dependencies:
          - --editable ${workspace.file_path}
```

Artefakt-Build über `uv`:

```yaml
artifacts:
  python_artifact:
    type: whl
    build: uv build --wheel
```

## <a id="hinweise">7. Wichtige Hinweise</a>

- **DBFS-Root deprecated:** Bibliotheken im DBFS-Root abzulegen ist ab Databricks Runtime 15.1 deprecated und standardmäßig deaktiviert — stattdessen Workspace-Dateien, Unity-Catalog-Volumes oder Paket-Repositories nutzen.
- **Bibliotheksunterstützung hängt von Cluster-Konfiguration und -Quelle ab.**
- **Pipelines:** Abhängigkeiten werden während der Entwicklung gecacht — Abhängigkeiten stattdessen in den `environment`-Abschnitt der `pipeline.yml` eintragen statt in `libraries`.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/library-dependencies

**Stand:** 2026-08-26.
