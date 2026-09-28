# Berechtigungen (Permissions)

Das `permissions`-Mapping auf Top-Level und Ressourcenebene, ressourcenspezifische Berechtigungsstufen und die Präzedenzregeln, wenn mehrere Ebenen gleichzeitig Berechtigungen definieren. Das einleitende Beispiel dazu findet sich bereits in [08 Zusammenarbeit und gemeinsame Dateien.md](08%20Zusammenarbeit%20und%20gemeinsame%20Dateien.md), Abschnitt 5 — hier die vollständige Referenz. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Grundregel: keine Überlappung](#grundregel)
2. [Top-Level-Permissions-Mapping](#top-level)
3. [Ressourcenspezifische Permissions](#ressourcenspezifisch)
4. [Berechtigungsstufen je Ressourcentyp](#stufen-tabelle)
5. [Präzedenz bei mehreren Ebenen](#praezedenz)
6. [Target-spezifische Ressourcen-Permissions](#target-spezifisch)
7. [Sicherheitshinweis: Immutable Folder](#sicherheit)
8. [Quelle](#quelle)

---

## <a id="grundregel">1. Grundregel: keine Überlappung</a>

„Berechtigungen dürfen sich nicht überlappen. Mit anderen Worten: Berechtigungen für einen Nutzer, eine Gruppe oder einen Service Principal dürfen nicht gleichzeitig im Top-Level-`permissions`-Mapping **und** innerhalb des `resources`-Mappings definiert werden."

## <a id="top-level">2. Top-Level-Permissions-Mapping</a>

Gilt über alle unterstützten Ressourcen hinweg — von Databricks als bevorzugter Ansatz für breite Berechtigungsverwaltung empfohlen.

**Am Top-Level erlaubte Stufen:** `CAN_VIEW`, `CAN_MANAGE`, `CAN_RUN` — **nicht** jede ressourcenspezifische Stufe aus Abschnitt 4 ist hier verfügbar.

```yaml
bundle:
  name: my-bundle
resources:
  jobs:
    my-job:
      # ...
targets:
  dev:
    permissions:
      - user_name: someone@example.com
        level: CAN_RUN
```

## <a id="ressourcenspezifisch">3. Ressourcenspezifische Permissions</a>

Für granulare Kontrolle lassen sich Berechtigungen direkt innerhalb einzelner Ressourcendefinitionen setzen (Dashboards, Experiments, Jobs, Models, Pipelines und weitere).

**Pflichtfelder je Eintrag:** genau eines aus `user_name`, `group_name`, `service_principal_name`, plus `level`.

## <a id="stufen-tabelle">4. Berechtigungsstufen je Ressourcentyp</a>

| Ressource | Erlaubte Stufen |
|---|---|
| Alerts | `CAN_EDIT`, `CAN_MANAGE`, `CAN_READ`, `CAN_RUN` |
| Apps | `CAN_MANAGE`, `CAN_USE` |
| Clusters | `CAN_ATTACH_TO`, `CAN_MANAGE`, `CAN_RESTART` |
| Dashboards | `CAN_EDIT`, `CAN_MANAGE`, `CAN_RUN`, `CAN_READ` |
| Database Instances | `CAN_MANAGE`, `CAN_USE`, `CAN_CREATE` |
| Genie Agents | `CAN_EDIT`, `CAN_MANAGE`, `CAN_RUN`, `CAN_VIEW` |
| Experiments | `CAN_EDIT`, `CAN_MANAGE`, `CAN_READ`, `CAN_RUN` |
| Jobs | `CAN_MANAGE`, `CAN_MANAGE_RUN`, `CAN_VIEW`, `IS_OWNER` |
| Models | `CAN_EDIT`, `CAN_MANAGE`, `CAN_MANAGE_STAGING_VERSIONS`, `CAN_MANAGE_PRODUCTION_VERSIONS`, `CAN_READ` |
| Pipelines | `CAN_MANAGE`, `CAN_RUN`, `CAN_VIEW`, `IS_OWNER` |
| Secret Scopes | `READ`, `WRITE`, `MANAGE` |
| SQL Warehouses | `CAN_MANAGE`, `CAN_USE`, `CAN_VIEW`, `CAN_MONITOR`, `IS_OWNER` |

## <a id="praezedenz">5. Präzedenz bei mehreren Ebenen</a>

Existieren Berechtigungen an mehreren Stellen, gilt folgende Reihenfolge (höchste zu niedrigster Priorität):

1. Ressourcen-Permissions **im Target-Deployment**
2. Target-Level-Permissions im Deployment
3. Ressourcen-Permissions im Top-Level-Bundle
4. Top-Level-Bundle-Permissions

**Beispiel:**

```yaml
bundle:
  name: my-bundle
permissions:
  - group_name: test-group
    level: CAN_VIEW
resources:
  jobs:
    my-job:
      permissions:
        - group_name: test-group
          level: CAN_MANAGE_RUN
targets:
  dev:
    resources:
      jobs:
        my-job:
          permissions:
            - group_name: test-group
              level: CAN_MANAGE   # gewinnt für dev
  prod:
    # kein Override -> CAN_MANAGE_RUN gilt
```

**Kombinationsregel:** Definieren Bundle-Level und Target-Level Berechtigungen für **unterschiedliche** Prinzipale auf derselben Ressource, werden beide Berechtigungssätze zusammengeführt und gelten gemeinsam für die deployte Ressource.

## <a id="target-spezifisch">6. Target-spezifische Ressourcen-Permissions</a>

```yaml
targets:
  <target-id>:
    resources:
      pipelines:
        <pipeline-id>:
          permissions:
            - user_name: <name>
              level: <permission-level>
```

## <a id="sicherheit">7. Sicherheitshinweis: Immutable Folder</a>

Um zu verhindern, dass Nicht-Admins deployte Assets nachträglich verändern, empfiehlt die Doku das Deployment in einen **unveränderlichen, schreibgeschützten Ordner** über die `immutable_folder`-Konfigurationsoption (siehe auch die Immutable-Deployment-Option der Direct Engine in [11 Direct Deployment Engine.md](11%20Direct%20Deployment%20Engine.md)).

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/permissions

**Stand:** 2026-08-26.
