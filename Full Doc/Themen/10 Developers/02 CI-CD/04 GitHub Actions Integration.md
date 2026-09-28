# GitHub Actions Integration

„GitHub Actions lösen Läufe der CI/CD-Flows aus GitHub-Repositories aus und erlauben es, Build-, Test- und Deployment-Pipelines zu automatisieren." Aktuell in Public Preview auf Databricks. Behandelt drei Beispiel-Workflows: Git-Folder-Sync, Bundle-Deployment, JAR-Build. Teil der [CI/CD](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Verfügbare Databricks-GitHub-Action](#action)
2. [Workflow 1: Git-Folder-Update](#git-folder-update)
3. [Workflow 2: Bundle-Pipeline-Update](#bundle-pipeline)
4. [Workflow 3: JAR-Build und Bundle-Deployment](#jar-build)
5. [Strukturelemente und Befehlsmuster](#struktur)
6. [Authentifizierungsmethoden](#authentifizierung)
7. [Quelle](#quelle)

---

## <a id="action">1. Verfügbare Databricks-GitHub-Action</a>

**`databricks/setup-cli`** — eine Composite Action, die die Databricks CLI in einem GitHub-Actions-Workflow einrichtet.

## <a id="git-folder-update">2. Workflow 1: Git-Folder-Update</a>

**Zweck:** aktualisiert einen Workspace-Git-Folder, wenn sich ein Remote-Branch aktualisiert.

**Voraussetzungen:** Service Principal mit GitHub-Actions-Federation-Policy; konfigurierte Workload Identity Federation; das Subject der Federation-Policy muss exakt übereinstimmen (Format `repo:org/repo:environment:Prod`); Umgebungsvariablen `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`.

```yaml
name: Sync Git Folder
concurrency: prod_environment
on:
  push:
    branches:
      - git-folder-cicd-example
permissions:
  id-token: write
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    name: 'Update git folder'
    environment: Prod
    env:
      DATABRICKS_AUTH_TYPE: github-oidc
      DATABRICKS_HOST: ${{ vars.DATABRICKS_HOST }}
      DATABRICKS_CLIENT_ID: ${{ secrets.DATABRICKS_CLIENT_ID }}
    steps:
      - uses: actions/checkout@v3
      - uses: databricks/setup-cli@main
      - name: Update git folder
        run: databricks repos update /Workspace/<git-folder-path> --branch git-folder-cicd-example
```

## <a id="bundle-pipeline">3. Workflow 2: Bundle-Pipeline-Update</a>

**Zweck:** validiert, deployt und führt bestimmte Jobs in einem Bundle für Dev- und Prod-Umgebungen aus.

**Voraussetzungen:** benutzerdefinierte Umgebungsvariable `DATABRICKS_BUNDLE_ENV`; Bundle-Konfigurationsdatei im Repository-Root mit definiertem Job `sample_job` und Targets `dev`/`prod`; GitHub-Secret `SP_TOKEN` mit einem Databricks-Access-Token des Service Principal; der Service Principal muss dem Ziel-Workspace zugeordnet sein.

**Service-Principal-Setup:** Databricks-Service-Principal erstellen → OAuth Secret generieren → Account-/Workspace-Access-Token manuell mit Secret und Client-ID generieren → Access Token als GitHub-Secret `SP_TOKEN` hinterlegen.

**Dev-Deployment:**

```yaml
name: 'Dev deployment'
concurrency: 1
on:
  pull_request:
    types:
      - opened
      - synchronize
    branches:
      - main
jobs:
  deploy:
    name: 'Deploy bundle'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: databricks/setup-cli@main
      - run: databricks bundle deploy
        working-directory: .
        env:
          DATABRICKS_TOKEN: ${{ secrets.SP_TOKEN }}
          DATABRICKS_BUNDLE_ENV: dev

  pipeline_update:
    name: 'Run pipeline update'
    runs-on: ubuntu-latest
    needs:
      - deploy
    steps:
      - uses: actions/checkout@v3
      - uses: databricks/setup-cli@main
      - run: databricks bundle run sample_job --refresh-all
        working-directory: .
        env:
          DATABRICKS_TOKEN: ${{ secrets.SP_TOKEN }}
          DATABRICKS_BUNDLE_ENV: dev
```

**Production-Deployment:** identisch, mit `on: push: branches: [main]` statt `pull_request`, sowie `DATABRICKS_BUNDLE_ENV: prod`.

**Beispiel-Bundle-Konfiguration:**

```yaml
bundle:
  name: pipeline_update

include:
  - resources/*.yml

variables:
  catalog:
    description: The catalog to use
  schema:
    description: The schema to use

resources:
  jobs:
    sample_job:
      name: sample_job
      parameters:
        - name: catalog
          default: ${var.catalog}
        - name: schema
          default: ${var.schema}
      tasks:
        - task_key: refresh_pipeline
          pipeline_task:
            pipeline_id: ${resources.pipelines.sample_pipeline.id}
      environments:
        - environment_key: default
          spec:
            environment_version: '4'

  pipelines:
    sample_pipeline:
      name: sample_pipeline
      catalog: ${var.catalog}
      schema: ${var.schema}
      serverless: true
      root_path: '../src/sample_pipeline'
      libraries:
        - glob:
            include: ../src/sample_pipeline/transformations/**
      environment:
        dependencies:
          - --editable ${workspace.file_path}

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: <dev-workspace-url>
    variables:
      catalog: my_catalog
      schema: ${workspace.current_user.short_name}

  prod:
    mode: production
    workspace:
      host: <production-workspace-url>
      root_path: /Workspace/Users/someone@example.com/.bundle/${bundle.name}/${bundle.target}
    variables:
      catalog: my_catalog
      schema: prod
    permissions:
      - user_name: someone@example.com
        level: CAN_MANAGE
```

## <a id="jar-build">4. Workflow 3: JAR-Build und Bundle-Deployment</a>

**Zweck:** baut Java-JAR-Dateien, lädt sie in Volumes hoch, validiert und deployt Bundles.

**Voraussetzungen:** Bundle-Konfiguration im Repository-Root; Umgebungsvariable `DATABRICKS_TOKEN` (Workspace-Access-Token); `DATABRICKS_HOST` (Workspace-URL); Maven-Projekt mit `pom.xml`.

```yaml
name: Build JAR and deploy with bundle

on:
  pull_request:
    branches:
      - main
  push:
    branches:
      - main

jobs:
  build-test-upload:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Java
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Cache Maven dependencies
        uses: actions/cache@v4
        with:
          path: ~/.m2/repository
          key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
          restore-keys: |
            ${{ runner.os }}-maven-

      - name: Build and test JAR with Maven
        run: mvn clean verify

      - name: Databricks CLI Setup
        uses: databricks/setup-cli@v0.9.0

      - name: Upload JAR to a volume
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
        run: |
          databricks fs cp target/my-app-1.0.jar dbfs:/Volumes/artifacts/my-app-${{ github.sha }}.jar --overwrite

  validate:
    needs: build-test-upload
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Databricks CLI Setup
        uses: databricks/setup-cli@v0.9.0
      - name: Validate bundle
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
        run: databricks bundle validate

  deploy:
    needs: validate
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      - name: Databricks CLI Setup
        uses: databricks/setup-cli@v0.9.0
      - name: Deploy bundle
        env:
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
        run: databricks bundle deploy --target prod
```

## <a id="struktur">5. Strukturelemente und Befehlsmuster</a>

**Gängige GitHub-Actions-Elemente:** `on:` (Trigger), `jobs:` (sequenzielle/parallele Ausführungseinheiten), `needs:` (Job-Abhängigkeiten), `if:` (bedingte Ausführung), `concurrency:` (stellt einzelne Workflow-Ausführung sicher), `permissions:` (nötig für Workload Identity Federation, `id-token`/`contents`), `env:`, `steps:`, `working-directory:`.

**Wichtige Befehle:** `databricks repos update` (aktualisiert Git-verbundene Ordner); `databricks bundle deploy`; `databricks bundle run`; `databricks bundle validate`; `databricks fs cp`; `--refresh-all` (aktualisiert alle abhängigen Objekte beim Run).

## <a id="authentifizierung">6. Authentifizierungsmethoden</a>

1. **Workload Identity Federation** (empfohlen für Git-Folder-Workflows): nutzt OIDC-Tokens von GitHub, erfordert `id-token: write`-Berechtigung.
2. **Service-Principal-Tokens** (für Bundles): nutzt `DATABRICKS_TOKEN` mit OAuth-Credentials des Service Principal.
3. **Umgebungsvariablen:** `DATABRICKS_AUTH_TYPE`, `DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_TOKEN`.

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/ci-cd/github

**Stand:** 2026-08-21.
