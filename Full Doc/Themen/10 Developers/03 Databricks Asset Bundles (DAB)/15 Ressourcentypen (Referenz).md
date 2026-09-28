# Ressourcentypen (Referenz)

Referenz der über `resources` in `databricks.yml` definierbaren Ressourcentypen, mit den jeweils wichtigsten Feldern und Besonderheiten. Ergänzt die Kurzübersicht in [05 Konfiguration (databricks.yml).md](05%20Konfiguration%20%28databricks.yml%29.md), Abschnitt 3. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Compute und Orchestrierung](#compute)
2. [Daten und Analytics](#daten)
3. [Unity-Catalog-Ressourcen](#unity-catalog)
4. [ML und Serving](#ml)
5. [Lakebase/Postgres](#lakebase)
6. [Suche und KI](#suche-ki)
7. [Alerts und Instance Pools](#alerts)
8. [Gemeinsame Merkmale aller Ressourcen](#gemeinsam)
9. [Quelle](#quelle)

---

## <a id="compute">1. Compute und Orchestrierung</a>

| Ressource | Wichtige Felder | Besonderheiten |
|---|---|---|
| **`clusters`** | `spark_version`, `node_type_id`, `num_workers`, `autoscale`, `autotermination_minutes` | Cloud-spezifische Attribute für AWS/Azure/GCP; flexible Node-Type-Konfiguration inkl. Fallback-Optionen für den Driver-Node; Init-Scripts über DBFS, S3, Workspace-Dateien oder Volumes |
| **`jobs`** | siehe [16 Job-Task-Typen.md](16%20Job-Task-Typen.md) | Python-Unterstützung (PyDABs) verfügbar, siehe [03 Python- und Scala-Artefakte.md](03%20Python-%20und%20Scala-Artefakte.md) |
| **`pipelines`** | Spark-Declarative-Pipelines-Definition | Python-Unterstützung verfügbar |

## <a id="daten">2. Daten und Analytics</a>

| Ressource | Wichtige Felder | Besonderheiten |
|---|---|---|
| **`dashboards`** (Lakeview) | `display_name`, `file_path`, `warehouse_id`, `embed_credentials` | Parametrisierung über `dataset_catalog`/`dataset_schema`; Dateiendung `.lvdash.json`; **Konfliktverhalten:** Weicht das lokale Dashboard-JSON vom Remote-Stand im Workspace ab, schlägt das Deployment fehl — Überschreiben nur explizit über `--force` |
| **`sql_warehouses`** | dedizierte SQL-Analytics-Compute | — |
| **`quality_monitors`** | Data-Quality-Automatisierung | — |

## <a id="unity-catalog">3. Unity-Catalog-Ressourcen</a>

| Ressource | Wichtige Felder | Besonderheiten |
|---|---|---|
| **`catalogs`** | `name`, `comment`, `storage_root`, `connection_name` | Unterstützt CMK-Verschlüsselung über `managed_encryption_settings`; **erfordert die Direct Deployment Engine** (siehe [11 Direct Deployment Engine.md](11%20Direct%20Deployment%20Engine.md)) — mit der Terraform-Engine nicht definierbar |
| **`schemas`** | Organisation von Objekten innerhalb eines Catalogs | Python-Unterstützung verfügbar |
| **`volumes`** | unstrukturierte Datenablage | Python-Unterstützung verfügbar |
| **`external_locations`** | Anbindung an Cloud-Storage | Teil der Unity-Catalog-Governance |
| **`registered_models`** | Modell-Lebenszyklus | Unity-Catalog-Integration |
| **`secrets`** | sichere Credential-Ablage | von den (legacy) `secret_scopes` zu unterscheiden |
| **`secret_scopes`** (Legacy) | Workspace-Ebenen-Secrets | — |

## <a id="ml">4. ML und Serving</a>

| Ressource | Wichtige Felder | Besonderheiten |
|---|---|---|
| **`experiments`** | MLflow-Experiment-Tracking | — |
| **`model_serving_endpoints`** | REST-API-Objektreferenz | Echtzeit-Modell-Inferenz; **kein `run_as`-Support** (siehe [18 Run As.md](18%20Run%20As.md)) |
| **`apps`** | `name`, `source_code_path`, `compute_size`, `description` | Konfiguration über `app.yaml` oder im Bundle (`command`, `env`); Git-Repository-Integration; Ressourcen-Bindung für Jobs, Experiments, Databases, Secrets, Warehouses; Telemetrie-Export-Ziele; **Namensregel:** nur Kleinbuchstaben, Ziffern und Bindestriche |

## <a id="lakebase">5. Lakebase/Postgres</a>

| Ressource | Beschreibung |
|---|---|
| **`synced_database_tables`** | Lakebase-Tabellensynchronisation |
| **`database_instances`** | Lakebase-Provisionierung |
| **`database_catalogs`** | registriert Lakebase-Datenbanken als UC-Catalogs — Felder `database_name`, `database_instance_name` |
| **`postgres`-Endpoints, -Projects, -Catalogs, -Databases, -Branches, -Roles, Synced Tables** | vollständige Postgres-kompatible Stack-Verwaltung mit Project-/Catalog-/Database-Hierarchie |

## <a id="suche-ki">6. Suche und KI</a>

| Ressource | Beschreibung |
|---|---|
| **Vector-Search-Endpoints** | als „AI-Search-Endpoint"-Objekt bezeichnet; semantische Such-Infrastruktur |
| **Vector-Search-Indexes** | Index-Verwaltung für Embeddings |
| **Genie Spaces** | KI-Agent-Konfiguration mit natürlichsprachlicher Schnittstelle |

## <a id="alerts">7. Alerts und Instance Pools</a>

| Ressource | Wichtige Felder | Besonderheiten |
|---|---|---|
| **`alerts`** | `display_name`, `query_text`, `warehouse_id`, `schedule`; Auswertung über `comparison_operator`, `source`, `threshold`, `notification` | unterstützt Aggregationsfunktionen (SUM, COUNT, STDDEV usw.); Cron-Zeitplan mit Zeitzone; unterstützt `run_as` für Nutzer/Service Principals |
| **Instance Pools** | vorkonfigurierte Compute-Node-Gruppen | — |

## <a id="gemeinsam">8. Gemeinsame Merkmale aller Ressourcen</a>

- **Lifecycle-Einstellungen:** steuern das Verhalten einer Ressource beim Deployen bzw. Zerstören, ressourcenübergreifend einheitlich.
- **Permissions:** auf die meisten Ressourcen anwendbar — Details inkl. ressourcenspezifischer Berechtigungsstufen in [19 Berechtigungen (Permissions).md](19%20Berechtigungen%20%28Permissions%29.md).
- **Grants** (Unity Catalog): prinzipal-basierte Privilegienvergabe.
- **Python-Unterstützung:** verfügbar für Jobs, Pipelines, Schemas, Volumes und weitere — Implementierungen im Databricks-GitHub-Repository.

**Praktische Hinweise:**

- JSON-Schema-Validierung ist im Databricks-CLI-GitHub-Repository verfügbar.
- `databricks bundle generate` erzeugt YAML aus bestehenden Ressourcen (siehe [09 Manuelle Bundle-Erstellung und Ressourcen-Migration.md](09%20Manuelle%20Bundle-Erstellung%20und%20Ressourcen-Migration.md)).
- `databricks bundle validate` gibt Warnungen für unbekannte Properties aus.
- Für bestimmte Ressourcen (u. a. Catalogs) ist die Direct Deployment Engine zwingend erforderlich.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/resources

**Stand:** 2026-08-26.
