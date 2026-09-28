# Konfiguration (databricks.yml)

Alle Top-Level-Mappings der Bundle-Konfigurationsdatei `databricks.yml`. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Grundstruktur](#grundstruktur)
2. [Top-Level-Mappings](#mappings)
3. [Ressourcentypen](#ressourcentypen)
4. [Target-Konfiguration](#targets)
5. [Variablensubstitutionen und benutzerdefinierte Variablen](#variablen)
   - 5.1 [Vordefinierte Substitutionen](#substitutionen)
   - 5.2 [Einfache benutzerdefinierte Variablen](#einfache-variablen)
   - 5.3 [Komplexe Variablen](#komplexe-variablen)
   - 5.4 [Lookup-Variablen](#lookup-variablen)
   - 5.5 [Variablenwerte setzen: Overrides und Priorität](#variablen-overrides)
   - 5.6 [Unterschiede im Überblick](#variablen-vergleich)
6. [Praktische Beispiele](#beispiele)
7. [Modularisierung](#modularisierung)
8. [Deployment-Befehle](#befehle)
9. [Workspace-Pfade im Detail](#workspace-pfade)
10. [Quelle](#quelle)

---

## <a id="grundstruktur">1. Grundstruktur</a>

„Ein Bundle muss genau eine Konfigurationsdatei namens `databricks.yml` im Root des Bundle-Projektordners enthalten." Die Datei nutzt YAML-Syntax und kann über das `include`-Mapping weitere Konfigurationsdateien referenzieren.

**Pflichtelemente der einfachsten Bundle-Konfiguration:** `bundle.name` (erforderlicher Bezeichner) und `targets` (mindestens ein Ziel-Deployment).

## <a id="mappings">2. Top-Level-Mappings</a>

| Mapping | Inhalt |
|---|---|
| `bundle` | Kern-Metadaten: Name, CLI-Version, Cluster-ID, Deployment-Einstellungen, Git-Konfiguration (Origin-URL, Branch-Tracking) |
| `run_as` | Identität für die Bundle-Ausführung — Nutzername oder Service-Principal-Name |
| `include` | referenziert zusätzliche Konfigurationsdateien oder Glob-Patterns |
| `scripts` | definiert ausführbare Skripte mit eindeutigen Namen und Inhalt |
| `sync` | steuert Datei-Synchronisation über Include-/Exclude-Patterns und spezifische Pfade |
| `artifacts` | verwaltet Build-Artefakte (Build-Befehle, Versionierung, Executables, Dateien, Pfade, Typdefinitionen) |
| `variables` | benutzerdefinierte Konfigurationsvariablen mit Beschreibung, Default, Lookup-Mappings, Typangabe (insb. `complex`) — Details zu allen Variablentypen und vordefinierten Substitutionen in Abschnitt 5 |
| `workspace` | Workspace-Konnektivität: Artefakt-Pfade, Host-URL, Auth-Profil, Ressourcen-Pfade, Root-Pfad, State-Pfad |
| `permissions` | ressourcenweite Zugriffskontrolle je Berechtigungsstufe für Gruppen, Nutzer, Service Principals — Details und Präzedenzregeln in [19 Berechtigungen (Permissions).md](19%20Berechtigungen%20%28Permissions%29.md) |
| `resources` | definiert Infrastruktur-Ressourcen über zahlreiche Kategorien (siehe Abschnitt 3 sowie die vollständige Referenz in [15 Ressourcentypen (Referenz).md](15%20Ressourcentypen%20%28Referenz%29.md)) |
| `targets` | Deployment-Umgebungen — genau ein Target muss `default: true` gesetzt haben |

## <a id="ressourcentypen">3. Ressourcentypen</a>

Alerts, Apps, Catalogs, Clusters, Dashboards, Database Catalogs, Database Instances, Experiments, Jobs, Model-Serving-Endpoints, Pipelines, Postgres-Branches/-Endpoints/-Projects, Quality Monitors, Registered Models, Schemas, Secret Scopes, SQL Warehouses, Synced Database Tables, Volumes.

## <a id="targets">4. Target-Konfiguration</a>

Targets erlauben umgebungsspezifische Overrides für Artifacts, Bundle-Einstellungen, Permissions, Resources, Sync-Verhalten, Variablen und Workspace-Konfiguration. Jedes Target kann einen `mode` und Preset-Werte angeben (siehe [07 Deployment-Modi und Authentifizierung.md](07%20Deployment-Modi%20und%20Authentifizierung.md)).

## <a id="variablen">5. Variablensubstitutionen und benutzerdefinierte Variablen</a>

Bundles unterstützen zwei verwandte, aber unterschiedliche Mechanismen, um Werte dynamisch aufzulösen statt sie hart zu kodieren: **vordefinierte Substitutionen** (systemseitig bereitgestellt) und **benutzerdefinierte Variablen** (im `variables`-Mapping deklariert, in drei Ausprägungen: einfach, komplex, Lookup). Beide werden mit derselben `${...}`-Syntax referenziert.

### <a id="substitutionen">5.1 Vordefinierte Substitutionen</a>

Eingebaute Werte, die abhängig vom Deployment-Kontext dynamisch ermittelt werden — sie werden **nicht** im `variables`-Mapping deklariert, sondern referenzieren bereits vorhandene System-Properties und (ggf. bereits deployte) Ressourcen.

**Syntax:** `${<Kategorie>.<Feld>}`

**Von der offiziellen Doku genannte Beispiele:**

- `${bundle.name}`
- `${bundle.target}` (ersetzt das inzwischen veraltete `${bundle.environment}`)
- `${workspace.host}`
- `${workspace.current_user.userName}`
- `${workspace.current_user.short_name}`
- `${workspace.current_user.domain_friendly_name}`
- `${workspace.file_path}`
- `${workspace.root_path}`
- `${resources.jobs.<job-name>.id}`
- `${resources.pipelines.<pipeline-name>.name}`
- `${resources.models.<model-name>.name}`

**Beispiel:**

```yaml
workspace:
  root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/my-envs/${bundle.target}
```

### <a id="einfache-variablen">5.2 Einfache benutzerdefinierte Variablen</a>

Im `variables`-Mapping deklarierte String-Variablen mit optionalem Default. „Eine benutzerdefinierte Variable wird als Typ **string** angenommen, sofern sie nicht als komplexe Variable definiert wird."

**Syntax:**

```yaml
variables:
  <variable-name>:
    description: <Text>
    default: <Wert>
```

**Beispiel** (aus der offiziellen Doku):

```yaml
variables:
  my_cluster_id:
    description: The ID of an existing cluster.
    default: 1234-567890-abcde123
```

**Referenz:** `${var.<variable-name>}`

### <a id="komplexe-variablen">5.3 Komplexe Variablen</a>

Variablen, die statt eines Skalarwerts ein strukturiertes Objekt (Map) enthalten — z. B. eine vollständige Cluster-Definition.

**Syntax:** `type: complex` setzen; `default` ist dann ein Objekt statt eines Einzelwerts. „Die Bundle-Validierung schlägt fehl, wenn `type` auf `complex` gesetzt ist und der für die Variable definierte `default` ein Einzelwert ist."

**Beispiel** (aus der offiziellen Doku) — die komplexe Variable wird **als Ganzes** referenziert und einem `new_cluster`-Mapping zugewiesen; die Doku zeigt keinen Zugriff auf einzelne Felder per Punktnotation:

```yaml
variables:
  my_cluster:
    description: 'My cluster definition'
    type: complex
    default:
      spark_version: '13.2.x-scala2.11'
      node_type_id: 'Standard_DS3_v2'
      num_workers: 2
      spark_conf:
        spark.speculation: true
        spark.databricks.delta.retentionDurationCheck.enabled: false

resources:
  jobs:
    my_job:
      job_clusters:
        - job_cluster_key: my_cluster_key
          new_cluster: ${var.my_cluster}
      tasks:
        - task_key: hello_task
          job_cluster_key: my_cluster_key
```

### <a id="lookup-variablen">5.4 Lookup-Variablen</a>

Statt IDs bestehender Workspace-Objekte hart zu kodieren, lässt sich eine Variable per `lookup` definieren: Der Wert wird beim Deployment anhand des angegebenen Namens im Workspace aufgelöst und in die tatsächliche ID des Objekts umgewandelt.

**Warum Lookup statt einer einfachen Variable mit der ID als `default`?** „Wenn für eine Variable ein Lookup definiert ist, wird die ID des Objekts mit dem angegebenen Namen als Wert der Variable verwendet. Das stellt sicher, dass immer die korrekt aufgelöste ID des Objekts für die Variable verwendet wird." Eine einfache Variable liefert dagegen genau den Wert, der ihr per `default`/Override zugewiesen wurde — die Doku beschreibt für sie keinerlei Abgleich mit tatsächlich im Workspace existierenden Objekten.

**Unterstützte Objekttypen:** `alert`, `cluster`, `cluster_policy`, `dashboard`, `instance_pool`, `job`, `metastore`, `notification_destination`, `pipeline`, `query`, `service_principal`, `warehouse`.

**Syntax:**

```yaml
variables:
  <variable-name>:
    lookup:
      <object-type>: '<object-name>'
```

**Beispiel** (aus der offiziellen Doku):

```yaml
variables:
  my_cluster_id:
    description: An existing cluster
    lookup:
      cluster: '12.2 shared'

resources:
  jobs:
    my_job:
      name: 'My Job'
      tasks:
        - task_key: TestTask
          existing_cluster_id: ${var.my_cluster_id}
```

**Einschränkungen:** Ein Fehler tritt auf, wenn kein Objekt mit dem angegebenen Namen existiert, oder wenn mehr als ein Objekt mit diesem Namen existiert — der Name muss also im relevanten Bereich eindeutig sein.

**Praxisbeispiel aus dem Kurs — Nicht-Databricks-Quelle: privates Kursmaterial** (`Kursmetrial_Databricks/8_Automated Deployment with Declarative Automation Bundles/03 - Deploying a DAB to Multiple Environments/databricks.yml`): Lookup einer Lab-Cluster-ID anhand des Cluster-Namens, anschließend referenziert als `existing_cluster_id` in den Job-Tasks eines `development`-Targets:

```yaml
variables:
  my_cluster_id:
    description: Get the lab cluster ID using a lookup variable.
    lookup:
      cluster: labuser15933383_1784728005   # Cluster-Name statt hartkodierter ID

targets:
  development:
    mode: development
    default: true
    resources:
      jobs:
        demo03_job:
          tasks:
            - task_key: create_bronze_table
              existing_cluster_id: ${var.my_cluster_id}
            - task_key: create_silver_table
              existing_cluster_id: ${var.my_cluster_id}
```

### <a id="variablen-overrides">5.5 Variablenwerte setzen: Overrides und Priorität</a>

Fünf Wege, einer benutzerdefinierten Variable (einfach, komplex oder Lookup) einen Wert zuzuweisen — in absteigender Priorität:

1. **CLI-Flag** beim Aufruf von `validate`/`deploy`/`run`: `--var="<key>=<value>"`
2. **Umgebungsvariable** nach dem Muster `BUNDLE_VAR_<variable-name>`
3. **Variable-Overrides-Datei** `.databricks/bundle/<target>/variable-overrides.json`
4. **Target-Level-Konfiguration** im `targets`-Mapping:
   ```yaml
   targets:
     dev:
       variables:
         my_cluster_id: 1234-567890-abcde123
         my_notebook_path: ./hello.py
     prod:
       variables:
         my_cluster_id: 2345-678901-bcdef234
         my_notebook_path: ./hello.py
   ```
5. **`default`-Wert** in der `variables`-Deklaration (niedrigste Priorität)

**Wichtiger Hinweis:** „Unabhängig davon, welchen Ansatz du zum Setzen der Variablenwerte wählst, verwende denselben Ansatz sowohl bei der Deployment- als auch bei der Run-Phase. Andernfalls können zwischen dem Zeitpunkt eines Deployments und einem darauf basierenden Job- oder Pipeline-Lauf unerwartete Ergebnisse auftreten."

### <a id="variablen-vergleich">5.6 Unterschiede im Überblick</a>

| Typ | Deklariert in `variables`? | Wert | Wann aufgelöst | Referenzsyntax |
|---|---|---|---|---|
| Vordefinierte Substitution | Nein — systemseitig bereitgestellt | Skalar, aus Kontext/bereits deployten Ressourcen | Deployment-/Config-Zeit | `${bundle.name}`, `${workspace.host}`, `${resources.jobs.<name>.id}`, … |
| Einfache benutzerdefinierte Variable | Ja | String (Default-Typ ohne `type`-Angabe) | Deployment-Zeit, per `default` oder Override (Abschnitt 5.5) | `${var.<name>}` |
| Komplexe Variable | Ja, mit `type: complex` | Strukturiertes Objekt/Map, `default` darf kein Einzelwert sein | Deployment-Zeit; als Ganzes referenziert, nicht feldweise | `${var.<name>}` |
| Lookup-Variable | Ja, mit `lookup:`-Mapping | ID eines bestehenden, per Name gesuchten Workspace-Objekts | Deployment-Zeit, per Namenssuche im Workspace | `${var.<name>}` |

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/variables

## <a id="beispiele">6. Praktische Beispiele</a>

Grundkonfigurationen demonstrieren Job-Definitionen mit Notebook-Tasks, bestehenden Cluster-IDs und Task-Keys. Multi-Umgebungs-Setups zeigen, wie Produktions-Targets Development-Einstellungen über unterschiedliche Workspace-URLs und Cluster-Konfigurationen überschreiben.

„Es ist nicht nötig, das `notebook_task`-Mapping innerhalb des `prod`-Mappings zu deklarieren, da es auf das `notebook_task`-Mapping im Top-Level-`resources`-Mapping zurückfällt, sofern es dort nicht explizit überschrieben wird."

## <a id="modularisierung">7. Modularisierung</a>

Komplexe Bundles lassen sich über mehrere Dateien aufteilen: die Haupt-`databricks.yml` mit `include`-Einträgen, separate Ressourcen-Definitionsdateien (z. B. `hello-job.yml`) und target-spezifische Konfigurationsdateien (z. B. `targets.yml`).

## <a id="befehle">8. Deployment-Befehle</a>

```bash
databricks bundle validate
databricks bundle deploy
databricks bundle run
```

Jeweils mit optionalem `-t <target>`-Flag.

## <a id="workspace-pfade">9. Workspace-Pfade im Detail</a>

Aus der vollständigen Bundle-Konfigurationsreferenz — Details zum `workspace`-Mapping (siehe Abschnitt 2), die über die reine Feldliste hinausgehen:

| Pfad-Feld | Zweck |
|---|---|
| `root_path` | Basis-Pfad für alles, was das Bundle im Workspace ablegt; Default: `/Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}` |
| `file_path` | Zielpfad für synchronisierte Quelldateien (Notebooks, Skripte) unterhalb des Root-Pfads |
| `artifact_path` | Zielpfad für gebaute Artefakte (Wheels, JARs) — auf einen Unity-Catalog-Volumes-Pfad gesetzt, lädt das Bundle referenzierte Artefakte automatisch nach Unity Catalog hoch (siehe [21 Private Artefakte.md](21%20Private%20Artefakte.md)) |

**Warnung:** Von `/Shared`-Pfaden für Production wird ausdrücklich abgeraten — dort haben potenziell viele Nutzer Schreibzugriff, was ungewollte Änderungen an deployten Assets ermöglicht (vgl. die Immutable-Folder-Empfehlung in [19 Berechtigungen (Permissions).md](19%20Berechtigungen%20%28Permissions%29.md), Abschnitt 7).

**Immutable Folders (Preview):** Deployt ein Bundle in einen unveränderlichen, schreibgeschützten Snapshot-Ordner, um die Job-Stabilität zu erhöhen — verwandtes Konzept zur Immutable-Deployment-Option der Direct Engine (siehe [11 Direct Deployment Engine.md](11%20Direct%20Deployment%20Engine.md)).

**Zusätzliche Presets** (über die in [07 Deployment-Modi und Authentifizierung.md](07%20Deployment-Modi%20und%20Authentifizierung.md), Abschnitt 3 gezeigten hinaus): `artifacts_dynamic_version` (dynamische Versionierung für Wheel-Artefakte) und `source_linked_deployment`.

**`include`/`exclude`:** filtern Dateien nach `.gitignore`-Syntax.

## <a id="quelle">10. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/settings
- https://docs.databricks.com/aws/en/dev-tools/bundles/reference

**Stand:** 2026-09-11.
