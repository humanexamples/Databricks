# Serverless-Umgebung konfigurieren (Abhängigkeiten)

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/dependencies>

Beschreibt das Einrichten und Verwalten von Serverless-Umgebungen für **Notebooks** und **Job-Tasks**: Base Environments, Abhängigkeiten, Memory-/GPU-Optionen, Usage Policies.

## Base Environment auswählen

Das Dropdown **Base environment** im Environment-Seitenpanel bietet:

- **Standard** — Standard-Serverless-Umgebung mit von Databricks bereitgestellten Libraries
- **ML** — enthält Python- und System-Pakete aus der Databricks Runtime for Machine Learning
- **AI** — GPU-optimierte Umgebung mit vorinstallierten ML-Libraries (erfordert Accelerator-Auswahl)
- **More** — Zugriff auf frühere Versionen, benutzerdefinierte YAML-Umgebungen und Workspace-konfigurierte Optionen

> *"Databricks recommends using the latest version to get the most up-to-date notebook features."*

**Schritte:** Environment-Seitenpanel-Icon klicken → Umgebung im Dropdown wählen → **Apply**.

## Abhängigkeiten zu Notebooks hinzufügen

Da Serverless **keine** Compute-Policies und **keine** Init-Skripte unterstützt, werden Abhängigkeiten über das Environment-Seitenpanel installiert:

1. **Environment**-Seitenpanel öffnen
2. Im Abschnitt **Dependencies** die Pfad-/Paket-Spezifikation eingeben
3. **+Add dependency** klicken
4. **Apply** klicken → installiert und startet den Python-Prozess neu

Abhängigkeiten in *"any format that is valid in a requirements.txt file"*; referenzierbar:

- **Workspace-Dateien** (Pfade beginnend mit `/Workspace/`)
- **Unity-Catalog-Volumes** (Format `/Volumes/<catalog>/<schema>/<volume>/<path>.whl`)

> **Warnung:** *"Do not install PySpark or any library that installs PySpark as a dependency on your serverless notebooks. Doing so will stop your session and result in an error."*

### Environment-Caching

> *"Databricks caches your notebook's virtual environment, so dependencies don't reinstall every time you reopen a notebook or resume after inactivity. Job tasks that share the same dependency set also benefit from this cache within a run."*

### Installierte Abhängigkeiten ansehen

Tab **Installed** zeigt alle installierten Pakete; **pip logs**-Link am Panel-Ende öffnet die pip-Logs.

## Custom Environment Specification erstellen

1. In einem Serverless-Notebook Base Environment wählen und gewünschte Abhängigkeiten installieren
2. Kebab-Menü am Panel-Ende → **Export environment**
3. Als Workspace-Datei oder in einem Unity-Catalog-Volume speichern

Zur Nutzung: **Custom** im **Base environment**-Dropdown wählen und zur YAML-Datei navigieren.

## Gemeinsame Tools workspace-weit teilen

Beispielstruktur:

```
helper_utils/
├── helpers/
│   └── __init__.py
├── pyproject.toml
```

`pyproject.toml`:

```toml
[project]
name = "common_utils"
version = "0.1.0"
```

Funktionen zu `__init__.py` hinzufügen und das Paket als Abhängigkeit über den Pfad `/Workspace/helper_utils` installieren.

> **Hinweis:** *"If you change the implementation of a custom Python package used in a job on serverless, you must also update its version number so that jobs can pick up the latest implementation."*

## AI Runtime (Serverless GPU) — Public Preview

1. Compute-Dropdown → **Serverless GPU**
2. Environment-Seitenpanel öffnen
3. Im Feld **Accelerator** **A10** oder **H100** wählen
4. Unter **Base environment** **Standard** oder **AI** wählen
5. **Apply**, dann bestätigen

## High Memory Serverless Compute — Public Preview

Gegen Out-of-Memory-Fehler:

- **Standard**: 16 GB Gesamtspeicher
- **High**: 32 GB Gesamtspeicher

Konfiguration: Environment-Seitenpanel → unter **Memory** **High memory** wählen → **Apply**.

> *"Serverless usage with high memory has a higher DBU emission rate than standard memory."*

## Serverless Usage Policy auswählen — Public Preview

Custom-Tagging für Billing-Attribution. Wenn Policies im Workspace konfiguriert sind: Environment-Seitenpanel → Policy unter **Serverless usage policy** wählen → **Apply**.

> *"If a user is assigned to only one serverless usage policy, that policy applies by default."*

## Umgebung in Source-Datei-Exporte einschließen

Für Python-Notebooks speichert der Toggle **Include in source file exports** Base Environment und Abhängigkeiten im **PEP-723**-Format beim Export von Source-Dateien (für Git-Ordner oder heruntergeladene Notebooks):

```python
# /// script
# [tool.databricks.environment]
# environment_version = "5"
# ///
```

## Environment-Abhängigkeiten zurücksetzen

Der Environment-Cache bleibt über Inaktivitäts-Trennungen bestehen. Zum Leeren und Neuinstallieren: Pfeil neben **Apply** → **Reset to defaults**.

## Umgebung für Job-Tasks konfigurieren

Jeder Job-Task läuft in einer **isolierten** Umgebung. Das Base Environment bestimmt Python-/Scala-Runtime und vorinstallierte Libraries.

- **Notebook-Tasks:** standardmäßig **Notebook Environment** (Notebook-Konfiguration); über ein Job-Level-Environment überschreibbar.
- **Python-Script- und Python-Wheel-Tasks:** erfordern explizite Environment-Konfiguration.
- **DBT-Tasks:** verwenden Job-Level-Environments für die Library-Konfiguration.
- **JAR-Tasks:** unterstützen **keine** Workspace-Base-Environments; YAML-basierte Specs + **Environment version**-Dropdown verwenden.

**Schritte (Python-/Wheel-Tasks):** Task-Konfiguration → **Environment and Libraries** → **+ Add dependency** → in **Configure environment** aus **Base environment** wählen (Databricks-Environments Standard/ML; Workspace-Environments; More) → Abhängigkeiten im requirements.txt-Format → **Confirm**.

## Environment-/Compute-Kompatibilität

- Das gewählte Base Environment muss zum Compute-Typ des Tasks passen (CPU oder GPU).
- *"If you set a hardware accelerator (GPU) at the job level, you must also select a base environment at the job level."*
- Das Ändern des Compute-Typs eines referenzierten Notebooks kann bestehende Task-Kompatibilität brechen.
- *"For API users: if you set the base environment at the job level but the notebook defines the compute type, Databricks validates compatibility at runtime, not at job creation time."*

## Architektur-Kompatibilität

> *"Serverless compute does not guarantee a specific CPU architecture. A notebook or job can run on either `aarch64` or `x86_64`, and the architecture can change between runs."*

Für Wheels mit nativen Extensions: pure-Python-Wheels verwenden **oder** beide Architektur-Varianten mit Platform-Machine-Environment-Markern einschließen.

## Private Package Repositories

Workspace-Admins können Default-pip-Quellen für private/authentifizierte Repositories konfigurieren, sodass Nutzer ohne Angabe von Index-URLs aus internen Quellen installieren können (pre-signed URLs, siehe [01 Uebersicht.md](01%20Uebersicht.md)).

## Git Folder Serverless

Dort teilen Notebooks eine über eine Root-`pyproject.toml` verwaltete Umgebung statt individueller Abhängigkeitslisten — siehe [03 Git-Ordner (Git Folder Serverless).md](03%20Git-Ordner%20(Git%20Folder%20Serverless).md).

## Verwandte Themen

- [02 Notebooks.md](02%20Notebooks.md) · [05 Best Practices.md](05%20Best%20Practices.md) · [06 Migration von Classic zu Serverless.md](06%20Migration%20von%20Classic%20zu%20Serverless.md)
