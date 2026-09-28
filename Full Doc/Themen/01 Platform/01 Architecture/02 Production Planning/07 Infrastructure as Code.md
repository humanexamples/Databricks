# Phase 7: Infrastructure-as-Code-Ansatz planen

Teil der [Production Planning](Uebersicht.md)-Reihe. Behandelt die Wahl der IaC-Tools (Terraform, Databricks Asset Bundles, Cloud-native Tools), das Bootstrap eines administrativen Workspace und wiederkehrende Deployment-Muster.

## Abschnittsübersicht

1. [IaC-Tool-Wahl](#tool-wahl)
2. [Cloud-native IaC-Tools](#cloud-nativ)
3. [Deployment-Ansatz](#deployment-ansatz)
4. [Administratives Workspace-Bootstrap](#bootstrap)
5. [Deployment-Muster](#muster)
6. [Empfehlungen](#empfehlungen)
7. [Ergebnisse der Phase](#ergebnisse)
8. [Quelle](#quelle)

---

## <a id="tool-wahl">1. IaC-Tool-Wahl</a>

### Terraform (empfohlen für Lakehouse-Infrastruktur)

Terraform ist das primäre Drittanbieter-IaC-Tool mit offiziellem Databricks-Provider-Support.

**Kernfähigkeiten:** verwaltet Databricks-Account-Ressourcen (Workspaces, Netzwerke, Storage-Konfigurationen); verwaltet Workspace-Ebenen-Ressourcen (Cluster, Jobs, Notebooks); funktioniert konsistent über AWS, Azure und GCP hinweg; unterstützt durch umfangreiches Ökosystem und offizielle Databricks-Anleitung.

**Deployment-Muster:** Account-Ebenen-Infrastruktur (Workspaces, Netzwerke, Storage Credentials, Metastores); Workspace-Konfiguration (Cluster-Policies, Instance Pools, Einstellungen); Unity-Catalog-Ressourcen (Catalogs, Schemas, External Locations); Notebooks, Repositories und Secrets-Management.

**Best Practices:** modulare Muster für organisationsweite Wiederverwendung erstellen; State in Remote-Backends mit State-Locking speichern; Umgebungen über getrennte State-Dateien isolieren; Konfigurationen über Variablen und `.tfvars` parametrisieren; Plan-Reviews in CI/CD vor dem Apply implementieren; konsistentes Ressourcen-Tagging für Governance anwenden; dokumentierte Modul-Registries pflegen.

### Databricks Asset Bundles (empfohlen für Daten-/KI-Ressourcen)

First-Party-Databricks-Tool zur konsistenten Paketierung von Daten- und KI-Ressourcen.

**Primäre Fähigkeiten:** deployt Jobs, Pipelines, Notebooks und ML-Modelle; verwaltet Multi-Umgebungs-Deployments (Dev, Staging, Prod); integriert mit Git für Source Control; unterstützt GitHub Actions, Azure DevOps und GitLab CI.

**Ideale Anwendungsfälle:** Data-Engineering-Workflows und Lakeflow-Pipelines; ML-Workflows und Model Serving; Notebook- und SQL-Query-Deployment; umgebungsspezifisches Konfigurationsmanagement; automatisierte Promotion-Workflows.

**Best Practices:** Bundles für Daten- und KI-Workloads reservieren; Terraform ausschließlich für Infrastruktur nutzen; Templates für gängige Muster nutzen; alle Bundle-Definitionen versioniert in Git verwalten; umgebungsspezifische Konfigurationen implementieren.

## <a id="cloud-nativ">2. Cloud-native IaC-Tools</a>

### AWS CloudFormation

Verwaltet AWS-spezifische Infrastruktur wie S3-Buckets, IAM-Rollen und VPCs.

**Status:** Historisch für Workspace-Deployment genutzt, ist diese Methode „nicht mehr die bevorzugte Methode zum Starten eines Databricks-Workspace" — stattdessen Terraform für Databricks-Ressourcen nutzen.

## <a id="deployment-ansatz">3. Deployment-Ansatz</a>

### Subscription- und Account-Einrichtung

Zwei AWS-Pfade:

- **Express-Setup-Pfad:** liefert einen Serverless-Workspace und eine kostenlose Testversion ohne bestehenden AWS-Account.
- **Bestehender-AWS-Account-Optionen:** Anmeldung über Databricks (selbstverwaltete Rechnungsstellung) oder über den AWS Marketplace (AWS-verwaltete Rechnungsstellung).

## <a id="bootstrap">4. Administratives Workspace-Bootstrap</a>

Die Erstellung eines administrativen Workspace je Region dient kritischen Funktionen:

**Primäre Zwecke:** Unity-Catalog-API-Zugriff erfordert einen vorhandenen Workspace; zentrales administratives Dashboard und Ausführung des Security Analysis Tool; dient als Automatisierungs-Hub für Terraform- und Bundles-Deployment.

**Best Practices:** Zugriff auf Plattform-Administratoren beschränken; Automatisierungs-Tools innerhalb dieses Workspace deployen; für Unity-Catalog-Verwaltung und System-Table-Abfragen nutzen; Zugriffsbeschränkungen klar dokumentieren.

## <a id="muster">5. Deployment-Muster</a>

### Muster 1: Workspace-Deployment-Muster

Wiederverwendbare Terraform-Module, abgebildet auf organisatorische Personas.

**Beispielmuster:** Data-Engineering-Workspace (Classic Compute, kundenverwaltete VPC, Lakeflow aktiviert); Analytics-Workspace (Serverless Compute, SQL Warehouses, BI-Integration); ML-Workspace (GPU-Cluster, ML-Runtime, MLflow aktiviert); Produktions-Workspace (Hochverfügbarkeit, Private Link, kundenverwaltete Schlüssel).

Vorteile: reduziert Konfigurationsfehler und beschleunigt die Provisionierung.

### Muster 2: Environment-Promotion-Muster

Etabliert Workflows, die Workloads von Development über Staging zu Production bewegen.

**Ablauf:** 1. In den Dev-Workspace deployen (Bundles mit Dev-Konfiguration). 2. Zu Staging promoten mit Integrationstests. 3. Zu Production promoten nach Freigabe-Gates.

### Muster 3: Wiederverwendbare-Module-Muster

Aufbau von Modul-Bibliotheken als standardisierte Bausteine.

**Beispielmodule:** Workspace-Modul (deployt mit Netzwerk, Storage, Unity Catalog); Unity-Catalog-Modul (erstellt Catalogs mit Schemas und Grants); Cluster-Policy-Modul (definiert Policies für Teams/Anwendungsfälle); Netzwerk-Modul (VPC/VNet mit Subnetzen, NAT, Firewall-Regeln).

## <a id="empfehlungen">6. Empfehlungen</a>

**Empfohlene Praktiken:**

- IaC-Tools für alle Workspace-Starts nutzen.
- Terraform für Infrastruktur einsetzen; Bundles für Workloads.
- State in Remote-Backends mit Locking speichern.
- Deployments in CI/CD-Pipelines integrieren.
- Konsistentes Ressourcen-Tagging pflegen.
- Alle Deployment-Muster dokumentieren.

**Zu vermeidende Praktiken:**

- Manuelle Workspace-Erstellung in Produktionsumgebungen.
- Terraform-State lokal speichern.
- Deployment ohne Plan-Review.
- Vermischung von IaC- und manuellen Konfigurationsansätzen.
- Erstellung einzigartiger „Snowflake"-Konfigurationen.

## <a id="ergebnisse">7. Ergebnisse der Phase</a>

Nach Abschluss dieser Phase sollten etabliert sein: IaC-Tool-Strategie; Design des administrativen Workspace; Deployment-Muster; Pläne für die Terraform-Modul-Bibliothek; CI/CD-Integrationsansatz; Remote-State-Management-Strategie; konsistente Tagging-Standards.

**Nächste Phase:** Phase 8 — Compute-Konfiguration gestalten (siehe [08 Compute-Konfiguration.md](08%20Compute-Konfiguration.md)).

## <a id="quelle">8. Quelle</a>

- https://docs.databricks.com/aws/en/lakehouse-architecture/deployment-guide/iac

**Stand:** 2026-08-21.
