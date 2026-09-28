# CI/CD — Überblick

„Continuous Integration und Continuous Delivery (CI/CD) bezeichnet den Prozess, Software in kurzen, häufigen Zyklen über Automatisierungs-Pipelines zu entwickeln und auszuliefern." CI/CD ist im Data Engineering und in der Data Science zunehmend notwendig geworden — Teams liefern zuverlässiger, indem Build, Test und Deployment automatisiert werden.

## Themen in diesem Kapitel

1. **Grundlagen und Empfehlungen** — die siebenstufige CI/CD-Pipeline, empfohlene Tools, Databricks Asset Bundles als primärer Ansatz vs. Alternativen. Siehe [01 Grundlagen und Empfehlungen.md](01%20Grundlagen%20und%20Empfehlungen.md).
2. **CI/CD-Workflows und Best Practices** — sechs Kernprinzipien, der empfohlene Bundles-Workflow, sowie rollenspezifische Ansätze für ML, SQL und Dashboards. Siehe [02 CI-CD-Workflows und Best Practices.md](02%20CI-CD-Workflows%20und%20Best%20Practices.md).
3. **Azure DevOps Integration** — vollständiges Setup mit Build- und Release-Pipeline. Siehe [03 Azure DevOps Integration.md](03%20Azure%20DevOps%20Integration.md).
4. **GitHub Actions Integration** — Git-Folder-Sync, Bundle-Deployment, JAR-Build-Workflows. Siehe [04 GitHub Actions Integration.md](04%20GitHub%20Actions%20Integration.md).
5. **Jenkins Integration** — vollständiges Pipeline-Setup mit `Jenkinsfile`. Siehe [05 Jenkins Integration.md](05%20Jenkins%20Integration.md).

## Verwandte Kapitel

- [Git Folders (Repos)](../Git%20Folders%20%28Repos%29/) — Git-Integration im Workspace, inkl. eigenem CI/CD-Kapitel zu Produktions-Ordnern.
- [Databricks Asset Bundles](../Databricks%20Asset%20Bundles/) — die von Databricks empfohlene CI/CD-Methodik im Detail.
- [Terraform](../Terraform/) — Infrastructure as Code als Alternative/Ergänzung zu Bundles.

**Stand:** 2026-08-21.
