# Bundles im Workspace (Web-UI)

Bundles direkt im Browser erstellen, bearbeiten und deployen — ohne YAML-Kenntnisse oder die Databricks CLI lokal nutzen zu müssen. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Überblick und Voraussetzungen](#ueberblick)
2. [Bundle erstellen](#erstellen)
3. [Neue Dateien hinzufügen](#dateien-hinzufuegen)
4. [Ressourcen-Definitionen anlegen](#ressourcen-definitionen)
5. [Bestehende Ressourcen hinzufügen](#bestehende-ressourcen)
6. [Bundle-Ressourcen bearbeiten](#bearbeiten)
7. [Bundle deployen](#deployen)
8. [Dashboards bearbeiten und deployen](#dashboards)
9. [Source-Linked Deployments](#source-linked)
10. [Workflow ausführen](#ausfuehren)
11. [Zusammenarbeit und Produktions-Deployment](#zusammenarbeit)
12. [Tutorial: Erstes Bundle im Workspace](#tutorial)
13. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick und Voraussetzungen</a>

Bundles lassen sich direkt in der Workspace-UI erstellen und verwalten, was „schnellere Iteration und Tests vor dem Umzug in die Produktion" ermöglicht.

**Voraussetzungen:** Workspace-Dateien aktiviert; ein Git Folder für die Bundle-Erstellung; Serverless Compute aktiviert; Kompatibilität mit Serverless-Egress-Kontrolle (mit PyPI-Paket-Einschränkung). Die für das Deployment genutzte Databricks-CLI-Version erscheint im Deploy-Dialog.

**Kein YAML-Wissen nötig:** Die Workspace-UI erlaubt Zusammenarbeit, ohne „YAML lernen oder die Databricks CLI bedienen zu müssen."

**Bundle-Erkennung:** Ordner mit einer `databricks.yml`-Datei im Root werden automatisch als Bundles erkannt.

**Konfigurationsunterstützung:** Fast alle bestehenden Bundle-Konfigurationen funktionieren im Workspace — außer Python für Bundles (siehe [03 Python- und Scala-Artefakte.md](03%20Python-%20und%20Scala-Artefakte.md), Abschnitt 4).

**Cross-Workspace-Deployment:** wird nicht direkt unterstützt — Databricks empfiehlt stattdessen CI/CD-Workflows mit der CLI (siehe [CI-CD](../CI-CD/)).

## <a id="erstellen">2. Bundle erstellen</a>

Im gewünschten Git Folder **Create** > **Bundle** wählen (oder Rechtsklick auf den Git Folder → **Create** > **Bundle**). Im Dialog einen Bundle-Namen eingeben (nur Buchstaben, Zahlen, Bindestriche, Unterstriche). Template wählen:

- eigene Templates (falls im Workspace konfiguriert)
- Empty bundle
- Sample Python notebook bundle
- SQL bundle
- ETL pipeline project (falls der Lakeflow Pipelines Editor aktiviert ist)

Manche Templates benötigen vor dem Deployment zusätzliche Konfiguration. Der Prozess erzeugt eine Git-Konfigurationsdatei, Quelldateien passend zum gewählten Template sowie die essenzielle `databricks.yml`.

## <a id="dateien-hinzufuegen">3. Neue Dateien hinzufügen</a>

Innerhalb des Bundle-Ordners über den **Create**-Button Notebooks, Dateien, Queries oder Dashboards hinzufügen — alternativ über das Kebab-Menü Dateien importieren. Neu hinzugefügte Dateien müssen in `databricks.yml` referenziert oder in eine Job-/Pipeline-Definition eingebunden werden, um am Bundle-Deployment teilzunehmen.

## <a id="ressourcen-definitionen">4. Ressourcen-Definitionen anlegen</a>

Über **Open in editor** neben dem Bundle-Namen den Bundle-Editor öffnen, dann das Deployment-Icon zum **Deployments**-Panel wählen.

**Job-Definitionen:** **Add** > **New job definition** → Job benennen → YAML befüllen:

```yaml
resources:
  jobs:
    run_notebook:
      name: run-notebook
      queue:
        enabled: true
      tasks:
        - task_key: my-notebook-task
          notebook_task:
            notebook_path: ../helloworld.ipynb
```

**Pipeline-Definitionen:** **Add** > **New pipeline definition** → Namen vergeben:

```yaml
resources:
  pipelines:
    test_pipeline:
      name: test_pipeline
      libraries:
        - notebook:
            path: ../test_pipeline.ipynb
      serverless: true
      catalog: main
      target: test_pipeline_${bundle.environment}
```

**ETL-Pipelines:** **Add** > **New ETL pipeline** → Personal-Schema-Präferenz, Default-Catalog, Default-Schema und Programmiersprache konfigurieren. Das System deployt eine Beispiel-Pipeline mit Exploration- und Transformation-Tabellen.

**Dashboard-Definitionen:** **Add** > **New dashboard definition** → Namen vergeben, Warehouse wählen, deployen — erzeugt ein leeres Dashboard samt zugehöriger YAML-Konfiguration.

## <a id="bestehende-ressourcen">5. Bestehende Ressourcen hinzufügen</a>

**Über die Workspace-UI:** im **Deployments**-Panel **Add** → **Add existing job**, **Add existing pipeline** oder **Add existing dashboard** → Ressource aus dem Dropdown wählen. Update-Verhalten festlegen:

- **Update on production deploys** — Änderungen greifen beim Production-Deployment.
- **Update on development deploys** — Änderungen greifen beim Development-Deployment.
- **Don't update** — die Ressource wird nicht verknüpft, stattdessen wird „eine Kopie erstellt".

**Über Konfiguration:** die YAML-Konfiguration einer bestehenden Ressource über deren Einstellungen kopieren und in eine neue Ressourcen-Definitionsdatei im Bundle einfügen — erlaubt es, „das Bundle zu deployen und die Pipeline-Ressource anschließend über die UI auszuführen."

## <a id="bearbeiten">6. Bundle-Ressourcen bearbeiten</a>

Im **Deployments**-Panel auf einen Job oder eine Pipeline unter **Bundle resources** klicken, um ihn direkt zu ändern — die Konfigurations-YAML wird automatisch aktualisiert. Workspace-Benachrichtigungen bestätigen Änderungen; anschließend muss deployt werden, damit sie wirksam werden.

**Einschränkungen beim Bearbeiten:** Variablen-/Substitutions-Updates betreffen nur bestimmte Felder; Job-Berechtigungsänderungen sind deaktiviert; Zeitpläne werden nicht in der Pipelines-/Dashboards-UI angezeigt.

## <a id="deployen">7. Bundle deployen</a>

1. **Bundle-Konfiguration öffnen** — im Workspace zum Bundle navigieren und eine Konfigurationsdatei wie `databricks.yml` wählen.
2. **Deployments-Panel öffnen** — Deployments-Icon anklicken.
3. **Target wählen** — aus den in `databricks.yml` unter `targets` definierten Zielen (siehe [07 Deployment-Modi und Authentifizierung.md](07%20Deployment-Modi%20und%20Authentifizierung.md)).
4. **Validieren und prüfen** — **Deploy** anklicken, um die Validierung zu starten; Validierungsdetails und Bestätigungsdialog prüfen.
5. **Deployment abschließen** — Aktion bestätigen. Der Status erscheint im Project-Output-Fenster, deployte Ressourcen anschließend im **Bundle resources**-Panel.

**Sicherheitshinweis:** „Das Deployen von Bundles und Ausführen von Bundle-Ressourcen führt Code als der aktuelle Nutzer aus." Vor dem Deployment sicherstellen, dass allem Code — inklusive YAML-Konfigurationen, die Befehle ausführen können — vertraut wird.

## <a id="dashboards">8. Dashboards bearbeiten und deployen</a>

1. Ein Dashboard unter **Bundle resources** anklicken, um es zu öffnen.
2. „Edit draft" wählen, um in den Dashboard-Editor zu wechseln.
3. Änderungen vornehmen.
4. **Deploy** anklicken, um zu veröffentlichen (deployt dabei alle Bundle-Ressourcen erneut).
5. „View deployed" anklicken, um die Änderungen zu bestätigen.

**Hinweis:** „Das Bearbeiten von Ressourcen ist im Production-Modus stets deaktiviert." Für zeitgesteuerte Updates geplante Jobs mit Dashboard-Tasks nutzen.

## <a id="source-linked">9. Source-Linked Deployments</a>

Standardmäßig „referenzieren beim Deployment erstellte Ressourcen Quelldateien im Workspace statt ihrer Workspace-Kopien." Deaktivierbar über `source_linked_deployment: false` in der Target-Konfiguration.

## <a id="ausfuehren">10. Workflow ausführen</a>

1. Bundle-Konfigurationsdatei öffnen.
2. Deployments-Icon anklicken.
3. Unter **Bundle resources** das Run-Icon neben der gewünschten Ressource anklicken.

Nicht deployte Ressourcen zeigen kein Run-Icon.

## <a id="zusammenarbeit">11. Zusammenarbeit und Produktions-Deployment</a>

Bundles über den Workspace-Share-Button für die Teamzusammenarbeit teilen. Bundles erben Berechtigungen vom übergeordneten Git Folder. Der Übergang von Dev zu Production erfolgt durch Wechsel der Ziel-Deployment-Einstellung auf `prod`.

## <a id="tutorial">12. Tutorial: Erstes Bundle im Workspace</a>

### Bundle erstellen

1. Zum gewünschten Git Folder im Workspace navigieren.
2. **Create** > **Bundle** wählen (oder Rechtsklick → **Create** > **Bundle**).
3. Bundle-Namen eingeben (nur Buchstaben, Zahlen, Bindestriche, Unterstriche).
4. „Empty project" wählen, **Next** klicken.

Erzeugt ein Bundle mit `.gitignore` und der erforderlichen `databricks.yml`.

### Notebook hinzufügen

1. Kachel **Add notebook** anklicken (oder Kebab-Menü → **Create** > **Notebook**).
2. Notebook in „helloworld" umbenennen.
3. Sprache auf Python setzen.
4. Code einfügen: `print("Hello World!")`.

### Job definieren

1. Deployment-Icon anklicken, um das **Deployments**-Panel zu öffnen.
2. Unter **Bundle resources** **Add**, dann **New job definition**.
3. „run-notebook" im Feld **Job name** eintragen.
4. **Add and deploy**, dann mit **Deploy** bestätigen.
5. Die generierte `run-notebook.job.yml` mit folgender YAML bearbeiten:

```yaml
resources:
  jobs:
    run_notebook:
      name: run-notebook
      queue:
        enabled: true
      tasks:
        - task_key: my-notebook-task
          notebook_task:
            notebook_path: ../helloworld.ipynb
```

### Bundle deployen

1. Im **Deployments**-Panel das Ziel-Workspace „dev" aus dem Dropdown wählen.
2. **Deploy** anklicken.
3. Validierungsdetails prüfen und im Bestätigungsdialog erneut **Deploy** anklicken.

### Job ausführen

Das Play-Icon neben der Job-Ressource unter **Bundle resources** anklicken. Ergebnisse über **Job runs** in der linken Navigation einsehen.

## <a id="quelle">13. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/workspace
- https://docs.databricks.com/aws/en/dev-tools/bundles/workspace-author
- https://docs.databricks.com/aws/en/dev-tools/bundles/workspace-deploy
- https://docs.databricks.com/aws/en/dev-tools/bundles/workspace-tutorial

**Stand:** 2026-08-21.
