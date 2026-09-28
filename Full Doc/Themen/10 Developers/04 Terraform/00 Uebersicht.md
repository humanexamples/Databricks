# Terraform — Überblick

Der Databricks-Terraform-Provider erlaubt Infrastructure-as-Code-Verwaltung für Databricks-Workspaces und zugehörige Cloud-Ressourcen über HashiCorp Terraform — automatisiert Deployment und Verwaltung von Datenplattformen über AWS, Azure und GCP hinweg.

## Themen in diesem Kapitel

1. **Grundlagen** — Kernfähigkeiten, Einstiegsvoraussetzungen, Beispielkonfiguration, Testing-Ansätze. Siehe [01 Grundlagen.md](01%20Grundlagen.md).
2. **Workspace bereitstellen und verwalten** — Secrets, Notebooks, Jobs, Cluster, Berechtigungen, Storage, IP-Access-Lists. Siehe [02 Workspace bereitstellen und verwalten.md](02%20Workspace%20bereitstellen%20und%20verwalten.md).
3. **Cluster, Notebook und Job bereitstellen** — vollständiges End-to-End-Beispiel inkl. Beispiel-Notebooks. Siehe [03 Cluster, Notebook und Job bereitstellen.md](03%20Cluster%2C%20Notebook%20und%20Job%20bereitstellen.md).
4. **Unity Catalog automatisieren** — Voraussetzungen und Umgebungsvariablen für UC-Setup via Terraform. Siehe [04 Unity Catalog automatisieren.md](04%20Unity%20Catalog%20automatisieren.md).
5. **Service Principals bereitstellen** — Service Principal samt optionalem Access Token per Terraform anlegen. Siehe [05 Service Principals bereitstellen.md](05%20Service%20Principals%20bereitstellen.md).
6. **CDKTF** — Terraform-CDK mit Python (nicht mehr empfohlen, aber dokumentiert). Siehe [06 CDKTF.md](06%20CDKTF.md).
7. **Fehlerbehebung** — Provider-Installationsfehler und Logging. Siehe [07 Fehlerbehebung.md](07%20Fehlerbehebung.md).

## Verwandte Kapitel

- [Databricks Asset Bundles](../Databricks%20Asset%20Bundles/) — die Direct Deployment Engine der Bundles basiert teils auf denselben Konzepten wie der klassische Terraform-Provider.
- [Git Folders (Repos)/04 CI-CD und Automatisierung.md](../Git%20Folders%20%28Repos%29/04%20CI-CD%20und%20Automatisierung.md) — nutzt Terraform zur Automatisierung von Git-Credentials.
- [CI-CD](../CI-CD/) — Terraform als eines der empfohlenen CI/CD-Tools.

**Stand:** 2026-08-21.
