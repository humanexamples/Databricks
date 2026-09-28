# CI/CD-Workflows und Best Practices

Behandelt sechs Kernprinzipien für CI/CD auf Databricks, den empfohlenen vierstufigen Bundles-Workflow sowie rollenspezifische CI/CD-Ansätze für ML, SQL-Entwicklung und Dashboards. Teil der [CI/CD](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Sechs Kernprinzipien](#kernprinzipien)
2. [Databricks Asset Bundles für CI/CD](#bundles-cicd)
3. [CI/CD für Machine Learning](#ml)
4. [CI/CD für SQL-Entwickler](#sql)
5. [CI/CD für Dashboard-Entwickler](#dashboards)
6. [Quelle](#quelle)

---

## <a id="kernprinzipien">1. Sechs Kernprinzipien</a>

1. **Alles versionieren:** „Notebooks, Skripte, Infrastruktur-Definitionen (IaC) und Job-Konfigurationen in Git speichern." Branching-Strategien wie Gitflow für Development-, Staging- und Production-Umgebungen nutzen.
2. **Testen automatisieren:** Unit Tests mit pytest (Python) und ScalaTest (Scala) implementieren; Workflows mit `databricks bundle validate` validieren; Integrationstests für Data Pipelines mit Tools wie chispa einsetzen.
3. **Infrastructure as Code:** Cluster und Jobs über „Databricks Asset Bundles YAML oder Terraform" definieren; umgebungsspezifische Einstellungen parametrisieren statt hartzukodieren.
4. **Umgebungen isolieren:** getrennte Workspaces für Development, Staging und Production pflegen; „MLflow Model Registry für Modellversionierung über Umgebungen hinweg" nutzen.
5. **Tools passend zum Cloud-Ökosystem wählen:** Azure nutzt Azure DevOps; AWS nutzt GitHub Actions; GCP nutzt Cloud Build.
6. **Überwachen und Rollbacks automatisieren:** Erfolgsraten von Deployments verfolgen; automatisierte Rollback-Mechanismen für fehlgeschlagene Deployments implementieren.

**Zusätzliche Sicherheitsempfehlung:** Databricks empfiehlt „Workload Identity Federation für die CI/CD-Authentifizierung" — eliminiert die Notwendigkeit, Secrets zu speichern.

## <a id="bundles-cicd">2. Databricks Asset Bundles für CI/CD</a>

### Zweck und Vorteile

Bundles bündeln Code, Workflows und Infrastruktur „in eine einzige, YAML-definierte Einheit", was Deployment vereinfacht und Konsistenz über Umgebungen hinweg sicherstellt.

### Source-Control-Strategie

Databricks empfiehlt „ein einzelnes Repository für sowohl Code als auch Bundle-Konfiguration", um Workflows zu vereinfachen, sowie „eine Trunk-based-Branching-Strategie, um Merge-Konflikte zu minimieren und sicherzustellen, dass der Main-Branch stets deploybar ist."

### Empfohlener CI/CD-Workflow mit Bundles

**Schritt 1 — Kompilieren und Testen:** ausgelöst bei Pull Requests oder Commits auf den Main-Branch; kompiliert Code und führt Unit Tests aus, erzeugt versionierte Dateien wie `my-app-1.0.jar`.

**Schritt 2 — Kompilierte Dateien hochladen:** kompilierte Dateien in „einem Unity-Catalog-Volume oder einem Artefakt-Repository wie AWS S3 oder Azure Blob Storage" speichern. Versionierungsschema an Git-Commit-Hashes oder semantische Versionierung koppeln, z. B. `dbfs:/mnt/artifacts/my-app-${{ github.sha }}.jar`.

**Schritt 3 — Bundle validieren:** `databricks bundle validate` ausführen, um die Korrektheit der `databricks.yml`-Konfiguration sicherzustellen und Fehlkonfigurationen frühzeitig abzufangen.

**Schritt 4 — Bundle deployen:** `databricks bundle deploy` ausführen, um das Bundle in eine Staging- oder Produktionsumgebung zu deployen — referenziert dabei die hochgeladenen kompilierten Bibliotheken in der Konfigurationsdatei.

## <a id="ml">3. CI/CD für Machine Learning</a>

### Besondere ML-Herausforderungen

- **Multi-Team-Koordination:** Data Scientists, Engineers und MLOps-Teams nutzen unterschiedliche Tools; Databricks vereinheitlicht Prozesse über MLflow, OpenSharing und Databricks Asset Bundles.
- **Daten- und Modellversionierung:** ML-Pipelines müssen Trainingsdaten-Schemas, Feature-Verteilungen und Modell-Artefakte nachverfolgen — Delta Lake liefert ACID-Transaktionen und Time-Travel-Fähigkeit.
- **Reproduzierbarkeit:** Bundles stellen atomares Deployment sicher, das Daten, Code und Infrastruktur über Umgebungen hinweg über YAML-Definitionen kombiniert.
- **Kontinuierliches Retraining:** Jobs ermöglichen automatisierte Retraining-Pipelines; MLflow integriert sich mit Monitoring-Tools für Performance-Tracking.

### MLOps-Stacks-Framework

MLOps Stacks sind „ein produktionsreifes Framework, das Databricks Asset Bundles, vorkonfigurierte CI/CD-Workflows und modulare ML-Projekt-Templates kombiniert."

**Team-Verantwortlichkeiten:**

- **Data Engineers:** bauen ETL-Pipelines und setzen Datenqualität über Lakeflow-Pipelines-YAML und Cluster-Policies durch.
- **Data Scientists:** entwickeln Modelltrainings-Logik und validieren Metriken über MLflow Projects und Notebook-Workflows.
- **MLOps Engineers:** orchestrieren Deployments und überwachen Pipelines über Umgebungsvariablen und Monitoring-Dashboards.

**Beispiel-Kollaborationsworkflow:** Data Engineers committen ETL-Änderungen, die automatisierte Schema-Validierung und Staging-Deployment auslösen. Data Scientists reichen ML-Code ein, der Unit Tests und Staging-Integrationstests durchläuft. MLOps Engineers überprüfen Metriken und promoten Modelle über die MLflow Registry in die Produktion.

## <a id="sql">4. CI/CD für SQL-Entwickler</a>

SQL-Entwickler können Git-Integration für Versionskontrolle und CI/CD-Automatisierung nutzen, ohne tiefe Infrastruktur-Expertise zu benötigen.

**Workflow-Komponenten:**

1. **SQL-Dateien versionieren:** „`.sql`-Dateien in Git-Repositories über Databricks Git Folders oder externe Git-Provider speichern", Branches für umgebungsspezifische Änderungen nutzen.
2. **Deployment automatisieren:** Syntax und Schema während Pull Requests validieren, dann Dateien in Databricks-SQL-Workflows oder -Jobs deployen.
3. **Für Umgebungsisolation parametrisieren:** Variablen in SQL-Dateien nutzen, um umgebungsspezifische Ressourcen dynamisch zu referenzieren:

   ```sql
   CREATE OR REFRESH STREAMING TABLE ${env}_sales_ingest AS 
   SELECT * FROM read_files('s3://${env}-sales-data')
   ```

4. **Zeitplanen und überwachen:** SQL-Tasks in Databricks Jobs nutzen, um Tabellen-Refreshes zu planen, und System-Tabellen zur Überwachung der Refresh-Historie nutzen.

**SQL-Entwicklungsprozess:** Entwickeln (Skripte lokal oder im SQL-Editor schreiben/testen, in Git-Branches committen) → Validieren (bei Pull Requests Syntax/Schema-Kompatibilität über automatisierte CI-Checks prüfen) → Deployen (nach Merge Skripte über CI/CD-Pipelines in Zielumgebungen deployen) → Überwachen (Databricks-Dashboards und -Alerts zur Verfolgung von Query-Performance und Datenaktualität nutzen).

## <a id="dashboards">5. CI/CD für Dashboard-Entwickler</a>

Databricks unterstützt die Integration von Dashboards in CI/CD-Workflows über Databricks Asset Bundles: Dashboards versionskontrollieren (Auditierbarkeit, Teamzusammenarbeit); Deployments zusammen mit Jobs und Pipelines über Umgebungen hinweg automatisieren; manuelle Fehler reduzieren und konsistente Updates sicherstellen; qualitativ hochwertige Analytics-Workflows gemäß CI/CD-Best-Practices pflegen.

**Umsetzung:** Bestehende Dashboards mit `databricks bundle generate` exportieren, um sie als JSON-Dateien zu exportieren und die YAML-Konfiguration zu generieren.

```yaml
resources:
  dashboards:
    sales_dashboard:
      display_name: 'Sales Dashboard'
      file_path: ./dashboards/sales_dashboard.lvdash.json
      warehouse_id: ${var.warehouse_id}
```

Generierte `.lvdash.json`-Dateien in Git-Repositories speichern (Änderungsverfolgung, Zusammenarbeit). Deployment mit `databricks bundle deploy` automatisieren, Variablen wie `${var.warehouse_id}` zur Parametrisierung über Dev/Staging/Prod nutzen.

Die Option `bundle generate --watch` synchronisiert lokale Dashboard-JSON-Dateien kontinuierlich mit Änderungen, die in der Databricks-UI vorgenommen werden; das `--force`-Flag beim Deployment überschreibt bei Bedarf die Remote-Version mit lokalen Änderungen.

## <a id="quelle">6. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/ci-cd/flows

**Stand:** 2026-08-21.
