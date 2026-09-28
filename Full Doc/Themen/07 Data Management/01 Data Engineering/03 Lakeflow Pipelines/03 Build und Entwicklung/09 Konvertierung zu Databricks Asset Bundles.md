# Konvertierung einer Pipeline in ein Bundle-Projekt — Referenz

Dieses Dokument fasst zusammen, wie sich eine bestehende Lakeflow Declarative Pipeline (LDP) in ein Declarative-Automation-Bundles-Projekt (DAB, früher Databricks Asset Bundles) konvertieren lässt. Jede faktische Aussage wurde per `WebFetch` gegen die offizielle Databricks-Online-Dokumentation verifiziert. Die AWS-Seite lieferte zunächst zusammengefasste Auszüge; zur Gegenprüfung und für den vollständigen, wörtlich zitierbaren Text (inklusive aller CLI-Befehle und YAML-Beispiele) wurde zusätzlich die Azure/Microsoft-Learn-Spiegelseite vollständig im Roh-Markdown-Format abgerufen. Beide Fassungen stimmten inhaltlich und in allen Code-Beispielen überein; produktbezogene Unterschiede ("Databricks" vs. "Azure Databricks") wurden im Fließtext neutral als "Databricks" wiedergegeben.

## Abschnittsübersicht

1. [Überblick über den Konvertierungsprozess](#ueberblick)
2. [Voraussetzungen](#voraussetzungen)
3. [Schritt 1: Ordner für das Bundle-Projekt einrichten](#schritt1)
4. [Schritt 2: Pipeline-Konfiguration generieren](#schritt2)
5. [Schritt 3: Die Bundle-Projektdateien überprüfen](#schritt3)
6. [Schritt 4: Die Bundle-Pipeline an die bestehende Pipeline binden](#schritt4)
7. [Schritt 5: Die Pipeline mit dem neuen Bundle deployen](#schritt5)
8. [Über Umgebungen hinweg mit Targets befördern](#targets)
9. [CI/CD einrichten](#cicd)
10. [Troubleshooting](#troubleshooting)
11. [Tipps für den Erfolg](#tipps)
12. [Weiterführende Ressourcen](#weiterfuehrend)
13. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick über den Konvertierungsprozess</a>

Eine bestehende Pipeline lässt sich in ein Declarative-Automation-Bundles-Projekt konvertieren. Bundles erlauben es, die Data-Processing-Konfiguration in einer einzigen, source-controllten YAML-Datei zu definieren und zu verwalten, was die Wartung erleichtert und automatisiertes Deployment in Ziel-Umgebungen ermöglicht.

![Konvertierungsprozess: Existing ETL pipeline → Create bundle project → Generate bundle config → Review settings → Bind pipeline → Deploy bundle](images/convert-dlt-pipeline-dabs-process.png)

Die Schritte zur Konvertierung einer bestehenden Pipeline in ein Bundle sind:

1. Sicherstellen, dass Zugriff auf eine zuvor konfigurierte Pipeline besteht, die in ein Bundle konvertiert werden soll.
2. Einen Ordner erstellen bzw. vorbereiten (vorzugsweise in einer source-controllten Hierarchie), um das Bundle zu speichern.
3. Über die Databricks CLI eine Konfiguration für das Bundle aus der bestehenden Pipeline generieren.
4. Die generierte Bundle-Konfiguration überprüfen, um sicherzustellen, dass sie vollständig ist.
5. Das Bundle mit der ursprünglichen Pipeline verknüpfen (binden).
6. Die Pipeline über die Bundle-Konfiguration in einen Ziel-Workspace deployen.

## <a id="voraussetzungen">2. Voraussetzungen</a>

Bevor begonnen wird, muss Folgendes vorhanden sein:

- Die Databricks CLI, installiert auf der lokalen Entwicklungsmaschine. Databricks-CLI-Version **0.218.0 oder höher** ist erforderlich, um Declarative Automation Bundles zu nutzen.
- Die ID einer bestehenden deklarativen Pipeline, die über ein Bundle verwaltet werden soll.
- Autorisierung für den Databricks-Workspace, in dem die bestehende Pipeline läuft.
- Für den vollständigen Satz an Privilegien, die zum Erstellen, Ausführen, Refreshen und Anzeigen von Pipelines und ihrer Ausgabe erforderlich sind, verweist die Doku auf die Seite zur Verwaltung von Identitäten, Berechtigungen und Privilegien für Pipelines.

## <a id="schritt1">3. Schritt 1: Ordner für das Bundle-Projekt einrichten</a>

Es muss Zugriff auf ein Git-Repository bestehen, das in Databricks als Git-Folder konfiguriert ist. Das Bundle-Projekt wird in diesem Repository erstellt, wodurch Source Control angewendet und das Projekt über einen Git-Folder im entsprechenden Databricks-Workspace anderen Kollaborateuren verfügbar gemacht wird.

1. Zum Root des geklonten Git-Repositorys auf der lokalen Maschine wechseln.
2. An geeigneter Stelle in der Ordnerhierarchie einen Ordner speziell für das Bundle-Projekt erstellen. Beispiel:

   ```bash
   mkdir -p ~/source/my-pipelines/ingestion/events/my-bundle
   ```
3. Das aktuelle Arbeitsverzeichnis in diesen neuen Ordner wechseln. Beispiel:

   ```bash
   cd ~/source/my-pipelines/ingestion/events/my-bundle
   ```
4. Ein neues Bundle initialisieren:

   ```bash
   databricks bundle init
   ```

   Die Prompts beantworten. Nach Abschluss existiert eine Projekt-Konfigurationsdatei namens `databricks.yml` im neuen Home-Ordner des Projekts. Diese Datei ist erforderlich, um die Pipeline von der Kommandozeile aus zu deployen.

## <a id="schritt2">4. Schritt 2: Pipeline-Konfiguration generieren</a>

Aus diesem neuen Verzeichnis im Ordnerbaum des geklonten Git-Repositorys heraus wird der Databricks-CLI-Befehl `bundle generate` ausgeführt, wobei die ID der Pipeline als `<pipeline-id>` übergeben wird:

```bash
databricks bundle generate pipeline --existing-pipeline-id <pipeline-id> --profile <profile-name>
```

Wenn der `generate`-Befehl ausgeführt wird, erstellt er eine Bundle-Konfigurationsdatei für die Pipeline im `resources`-Ordner des Bundles und lädt alle referenzierten Artefakte in den `src`-Ordner herunter. Das Flag `--profile` (bzw. `-p`) ist optional; wird jedoch ein bestimmtes Databricks-Konfigurationsprofil (definiert in der `.databrickscfg`-Datei, die bei der Installation der Databricks CLI erstellt wurde) anstelle des Standardprofils benötigt, wird es in diesem Befehl angegeben.

**Tipp aus der Doku:** Existiert bereits ein Spark-Declarative-Pipelines-(SDP-)Projekt (es besitzt eine `spark-pipeline.yml`-Datei), kann dieses Pipeline-Projekt in den `src`-Ordner des Bundles kopiert werden; anschließend wird der Befehl `databricks pipelines generate` verwendet, um dafür eine Bundle-Konfiguration zu generieren.

## <a id="schritt3">5. Schritt 3: Die Bundle-Projektdateien überprüfen</a>

Wenn der Befehl `bundle generate` abgeschlossen ist, hat er zwei neue Ordner erstellt:

- `resources` ist das Projekt-Unterverzeichnis, das Projekt-Konfigurationsdateien enthält.
- `src` ist der Projektordner, in dem Quelldateien wie Queries und Notebooks gespeichert werden.

Der Befehl erstellt außerdem einige zusätzliche Dateien:

- `*.pipeline.yml` im `resources`-Unterverzeichnis. Diese Datei enthält die spezifische Konfiguration und Einstellungen für die Pipeline.
- Quelldateien wie SQL-Queries im `src`-Unterverzeichnis, kopiert aus der bestehenden Pipeline.

```
├── databricks.yml                            # Project configuration file created with the bundle init command
├── resources/
│   └── {your-pipeline-name.pipeline}.yml     # Pipeline configuration
└── src/
    └── {source folders and files...}         # Your pipeline's declarative queries
```

## <a id="schritt4">6. Schritt 4: Die Bundle-Pipeline an die bestehende Pipeline binden</a>

Die Pipeline-Definition im Bundle muss mit der bestehenden Pipeline verknüpft ("gebunden") werden, um sie bei Änderungen aktuell zu halten. Dazu wird der Databricks-CLI-Befehl `bundle deployment bind` ausgeführt:

```bash
databricks bundle deployment bind <pipeline-name> <pipeline-ID> --profile <profile-name>
```

`<pipeline-name>` ist der Name der Pipeline. Dieser Name sollte demselben vorangestellten String-Wert des Dateinamens der Pipeline-Konfiguration im neuen `resources`-Verzeichnis entsprechen. Beispiel: Existiert eine Pipeline-Konfigurationsdatei namens `ingestion_data_pipeline.pipeline.yml` im `resources`-Ordner, muss `ingestion_data_pipeline` als Pipeline-Name angegeben werden.

`<pipeline-ID>` ist die ID der Pipeline — dieselbe, die bereits als Teil der Voraussetzungen kopiert wurde.

## <a id="schritt5">7. Schritt 5: Die Pipeline mit dem neuen Bundle deployen</a>

Nun wird das Pipeline-Bundle über den Databricks-CLI-Befehl `bundle deploy` in den Ziel-Workspace deployt:

```bash
databricks bundle deploy --target <target-name> --profile <profile-name>
```

Das Flag `--target` ist erforderlich und muss auf einen String gesetzt werden, der einem konfigurierten Ziel-Workspace-Namen entspricht, etwa `development` oder `production`.

Ist dieser Befehl erfolgreich, liegt die Pipeline-Konfiguration nun in einem externen Projekt vor, das in andere Workspaces geladen und ausgeführt sowie einfach mit anderen Databricks-Nutzern im Account geteilt werden kann.

## <a id="targets">8. Über Umgebungen hinweg mit Targets befördern</a>

Ein Bundle definiert benannte Deployment-Umgebungen namens *Targets* in `databricks.yml`, von denen jede auf einen eigenen Workspace, Katalog und eigene Variablenwerte zeigt. Targets sind das Mittel, um dieselbe Pipeline durch Dev, Staging und Produktion zu befördern und dabei identischen Quellcode in jede aufeinanderfolgende Umgebung zu deployen, ohne ihn zu bearbeiten:

```yaml
bundle:
  name: orders_pipeline

variables:
  catalog:
    description: Unity Catalog to write to
    default: dev_catalog

targets:
  dev:
    mode: development
    default: true
    variables:
      catalog: dev_catalog

  prod:
    mode: production
    variables:
      catalog: prod_catalog
    run_as:
      service_principal_name: '12345678-90ab-cdef-1234-567890abcdef'
```

Der auf jedem Target gesetzte `mode` verändert dessen Deployment-Verhalten:

- `mode: development` markiert ein Target als persönliches Scratch-Deployment. Ressourcen erhalten ein `[dev username]`-Präfix, und Schedules sind standardmäßig pausiert, sodass die eigene Arbeit niemand anderen beeinträchtigt.
- `mode: production` deaktiviert diese Sicherheits-Standardwerte. In Kombination mit `run_as` erlaubt dies, die Pipeline als Service Principal statt als individueller Account auszuführen, sodass Läufe nicht abbrechen, wenn jemand das Team verlässt oder die Rolle wechselt. Databricks empfiehlt einen Service Principal für Staging und Produktion. `service_principal_name` nimmt die Application ID des Service Principals entgegen, nicht dessen Anzeigenamen. Die Application ID lässt sich auf der Seite des Service Principals in den Workspace-Admin-Einstellungen abrufen.

Um zu befördern, wird dasselbe Bundle nacheinander in jedes Target deployt, wobei bei jedem Schritt verifiziert wird:

```bash
databricks bundle validate --target prod
databricks bundle deploy --target prod
databricks bundle run orders_pipeline --target prod
```

Statt Katalognamen oder Quellpfade pro Umgebung im Transformationscode fest zu codieren, werden die Werte aus dem Target übergeben, sodass derselbe Quellcode überall unverändert läuft. Wie die Werte gesetzt werden, hängt von der Quellsprache ab. Pipeline-Parameter gelten nur für SQL-Quellcode. Für Python-Quellcode wird das Pipeline-Feld `configuration` verwendet und die Werte werden mit `spark.conf.get()` gelesen:

```yaml
resources:
  pipelines:
    orders_pipeline:
      name: orders-pipeline
      # For SQL source code. Reference as ${source_catalog}.
      parameters:
        source_catalog: ${var.catalog}
        source_schema: raw
      # For Python source code. Read with spark.conf.get("source_catalog").
      configuration:
        source_catalog: ${var.catalog}
        source_schema: raw
```

## <a id="cicd">9. CI/CD einrichten</a>

Da eine konvertierte Pipeline vollständig als Bundle definiert ist (YAML plus Quelldateien in Git), bedeutet die Einrichtung von Continuous Integration und Continuous Delivery (CI/CD) dafür, die Bundle-Befehle aus einem CI-System wie GitHub Actions oder Azure DevOps auszuführen. Bei jedem Pull Request führt eine gute Baseline aus:

1. `pytest` gegen die unit-testbaren Transformationsfunktionen.
2. `databricks bundle validate --target <env>`, um Konfigurationsfehler zu erkennen.
3. Optional ein `databricks bundle run` in einem Scratch-Target, um Expectations gegen Beispieldaten zu prüfen.

Der folgende GitHub-Actions-Workflow deployt bei einem Merge nach `main` nach Staging, unter Verwendung von OpenID Connect (OIDC) Federation statt eines gespeicherten Tokens:

```yaml
# .github/workflows/deploy.yml
name: Deploy pipeline bundle

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    env:
      DATABRICKS_AUTH_TYPE: github-oidc
      DATABRICKS_HOST: ${{ vars.DATABRICKS_HOST }}
      DATABRICKS_CLIENT_ID: ${{ vars.DATABRICKS_CLIENT_ID }} # Service principal application ID
    steps:
      - uses: actions/checkout@v4

      - name: Install Databricks CLI
        uses: databricks/setup-cli@main

      - name: Validate bundle
        run: databricks bundle validate --target staging

      - name: Deploy bundle
        run: databricks bundle deploy --target staging
```

Der Produktions-Deploy sollte hinter einer manuellen Freigabe abgesichert werden (zum Beispiel ein zweiter Job, der eine GitHub-Environment-Freigabe erfordert, oder eine separate Stage in Azure DevOps), sodass eine Person jede Beförderung explizit freigibt. Der Produktions-Job führt `databricks bundle deploy --target prod` mit einem auf den Produktions-Workspace beschränkten Service Principal aus.

## <a id="troubleshooting">10. Troubleshooting</a>

| Problem | Lösung |
|---|---|
| Fehler "`databricks.yml` not found" beim Ausführen von `bundle generate` | Aktuell erstellt der Befehl `bundle generate` die Bundle-Konfigurationsdatei (`databricks.yml`) nicht automatisch. Die Datei muss mit `databricks bundle init` oder manuell erstellt werden. |
| Bestehende Pipeline-Einstellungen stimmen nicht mit den Werten in der generierten Pipeline-YAML-Konfiguration überein | Die Pipeline-ID erscheint nicht in der Bundle-Konfigurations-YML-Datei. Werden weitere fehlende Einstellungen bemerkt, können diese manuell nachgetragen werden. |

## <a id="tipps">11. Tipps für den Erfolg</a>

- Immer Versionskontrolle verwenden. Wer keine Databricks-Git-Folder nutzt, sollte Projekt-Unterverzeichnisse und -Dateien in einem Git- oder einem anderen versionskontrollierten Repository bzw. Dateisystem speichern.
- Die Pipeline in einer Nicht-Produktionsumgebung (etwa einer "development"- oder "test"-Umgebung) testen, bevor sie in eine Produktionsumgebung deployt wird. Es lässt sich leicht versehentlich eine Fehlkonfiguration einführen.

## <a id="weiterfuehrend">12. Weiterführende Ressourcen</a>

Laut der AWS-Fassung der Seite verweist der Abschnitt "Additional resources" auf:

- "What are Declarative Automation Bundles?"
- "Develop pipelines with Declarative Automation Bundles"

---

## <a id="quellen">13. Quellen</a>

Beide Fassungen der Seite wurden am 19.08.2026 per `WebFetch` abgerufen. Die AWS-Fassung lieferte zunächst zusammengefasste, aber inhaltlich mit der Azure-Fassung übereinstimmende Auszüge (insbesondere für Requirements, Troubleshooting, Tips for success und Additional resources); der vollständige, wörtlich zitierbare Roh-Markdown-Text inklusive aller CLI-Befehle und YAML-Beispiele stammt aus dem Abruf der Azure/Microsoft-Learn-Spiegelseite. Alle Code-Beispiele und Zahlenangaben (insbesondere die CLI-Mindestversion 0.218.0 sowie der `service_principal_name`-Beispielwert) stimmten zwischen beiden Fassungen exakt überein.

- Convert a pipeline into a bundle project (AWS): https://docs.databricks.com/aws/en/ldp/convert-to-dab
- Convert a pipeline into a bundle project (Azure-Spiegelseite, für vollständigen Wortlaut und Gegenprüfung genutzt): https://learn.microsoft.com/en-us/azure/databricks/ldp/convert-to-dab

**Bilder:** Das Diagramm unter "Conversion process overview" wurde am 20.08.2026 erfolgreich von der Azure-Spiegelseite heruntergeladen (`_static/images/dlt/convert-dlt-pipeline-dabs-process.png`) und liegt lokal unter `images/convert-dlt-pipeline-dabs-process.png` — eingebettet in Abschnitt 1.

Keine inhaltlichen Lücken: Alle Kernaussagen (CLI-Version, Befehle, YAML-Beispiele, Troubleshooting-Tabelle, Tipps) sowie das Übersichtsdiagramm wurden zwischen AWS- und Azure-Fassung übereinstimmend verifiziert.
