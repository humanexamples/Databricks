# CI/CD Best Practices

Die sechs offiziellen Kernprinzipien für CI/CD auf Databricks — Versionskontrolle, automatisiertes Testen, Infrastructure as Code, Umgebungstrennung, werkzeugpassende Tool-Wahl, Monitoring/Rollback — sowie die Sicherheitsempfehlung Workload Identity Federation. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Sechs Kernprinzipien](#kernprinzipien)
2. [Sicherheitsempfehlung: Workload Identity Federation](#wif)
3. [Quelle](#quelle)

---

## <a id="kernprinzipien">1. Sechs Kernprinzipien</a>

1. **Alles versionieren:** „Notebooks, Skripte, Infrastruktur-Definitionen (IaC) und Job-Konfigurationen in Git speichern." Branching-Strategien wie Gitflow für Development-, Staging- und Production-Umgebungen nutzen.
2. **Testen automatisieren:** Unit Tests mit pytest (Python) und ScalaTest (Scala) implementieren; Workflows mit „Databricks CLI bundle validate" validieren; Integrationstests für Data Pipelines mit Tools wie chispa einsetzen.
3. **Infrastructure as Code:** Cluster und Jobs über „Databricks Asset Bundles YAML oder Terraform" definieren, umgebungsspezifische Einstellungen parametrisieren statt hartzukodieren (siehe [Developers/Databricks Asset Bundles](../../Developers/Databricks%20Asset%20Bundles/) und [Developers/Terraform](../../Developers/Terraform/)).
4. **Umgebungen isolieren:** getrennte Workspaces für Development, Staging und Production pflegen, „MLflow Model Registry für Modellversionierung über Umgebungen hinweg" nutzen.
5. **Tools passend zum Cloud-Ökosystem wählen:** Azure nutzt Azure DevOps; AWS nutzt GitHub Actions; GCP nutzt Cloud Build.
6. **Überwachen und Rollbacks automatisieren:** Erfolgsraten von Deployments verfolgen, automatisierte Rollback-Mechanismen für fehlgeschlagene Deployments implementieren.

Diese Punkte decken sich inhaltlich mit den bereits ausführlich behandelten CI/CD-Workflows unter [Developers/CI-CD/02 CI-CD-Workflows und Best Practices.md](../../Developers/CI-CD/02%20CI-CD-Workflows%20und%20Best%20Practices.md) — dort auch der vierstufige Bundles-CI/CD-Workflow (Kompilieren/Testen → Upload → Validieren → Deployen) im Detail.

## <a id="wif">2. Sicherheitsempfehlung: Workload Identity Federation</a>

Zusätzliche Sicherheitsempfehlung: Databricks empfiehlt „Workload Identity Federation für die CI/CD-Authentifizierung" — eliminiert die Notwendigkeit, Secrets zu speichern (siehe auch [Developers/Databricks Asset Bundles/07 Deployment-Modi und Authentifizierung.md](../../Developers/Databricks%20Asset%20Bundles/07%20Deployment-Modi%20und%20Authentifizierung.md) für OAuth-M2M-Details).

## <a id="quelle">3. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/ci-cd/best-practices

**Stand:** 2026-08-21.
