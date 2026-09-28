# Phase 2: Workspace-Strategie gestalten

Teil der [Production Planning](Uebersicht.md)-Reihe. Behandelt Deployment-Modelle, Gründe für die Aufteilung in mehrere Workspaces, Ressourcengrenzen, Security Modes und Namenskonventionen.

## Abschnittsübersicht

1. [Was ist ein Workspace?](#konzept)
2. [Deployment-Modelle](#deployment-modelle)
3. [Gründe für die Aufteilung in mehrere Workspaces](#split-gruende)
4. [Ressourcengrenzen](#ressourcengrenzen)
5. [Nachteile aufgeteilter Workspaces](#split-nachteile)
6. [Security Modes](#security-modes)
7. [Namenskonvention](#namenskonvention)
8. [Beispiel-Deployments](#beispiele)
9. [Strategische Empfehlungen](#empfehlungen)
10. [Ergebnisse der Phase](#ergebnisse)
11. [Quelle](#quelle)

---

## <a id="konzept">1. Was ist ein Workspace?</a>

Ein Databricks-Workspace ist „die operative Grenze in einer Cloud-Region, in der Teams Workloads entwickeln und ausführen." Er umfasst Kollaborations-Artefakte (Notebooks, Jobs, Dashboards, Repositories) sowie workspace-gebundene Konfigurationen (Berechtigungen, Cluster-Policies, Secrets). Datenpersistenz erfolgt typischerweise in externen Cloud-Diensten, nicht innerhalb des Workspace selbst.

## <a id="deployment-modelle">2. Deployment-Modelle</a>

**Serverless Workspaces:**

- Cloud-Storage, verwaltet von Databricks im eigenen Account, in derselben Region.
- Vorkonfiguriertes, sofort verfügbares Serverless Compute.
- Keine Infrastruktur-Provisionierung nötig.
- Automatische Skalierung basierend auf Workload-Bedarf.

**Classic Workspaces:**

- Storage- und Compute-Ressourcen im eigenen Cloud-Account provisioniert.
- Volle Kontrolle über VPC/VNet-Konfiguration.
- Serverless Compute lässt sich zusätzlich zu klassischem Compute nutzen.

**Empfehlung:** Mit Serverless Workspaces starten (operative Effizienz), erst auf Classic wechseln, wenn benutzerdefinierte Netzwerkkonfigurationen, On-Premises-Konnektivität oder spezifische Compliance-Vorgaben nötig sind.

## <a id="split-gruende">3. Gründe für die Aufteilung in mehrere Workspaces</a>

- **Datenschutz:** Isolierung stark regulierter Workloads zur Vereinfachung sensibler Datenkontrollen.
- **Geschäftsbereichs-Trennung:** Verhindert Asset-Sharing zwischen Organisationseinheiten, die vollständige Isolation benötigen.
- **Plattform-Feature-Zugriff:** Trennung von Teams mit unterschiedlichen Feature-Sets und Zugriffsebenen.
- **SDLC-Umgebungen:** Trennung von Development, Staging und Production bei striktem Isolationsbedarf oder zum Testen von Workspace-Einstellungen vor dem Produktivbetrieb.
- **Geografische Verteilung:** Unterstützung von Multi-Country-Betrieb mit regionalen Datenresidenz-Anforderungen, reduzierte Latenz für lokale Analysen.
- **Ressourcenbeschränkungen:** Verteilung von Workloads über Accounts hinweg bei Erreichen von Cloud-Provider- oder Workspace-Ebenen-Ressourcengrenzen.

## <a id="ressourcengrenzen">4. Ressourcengrenzen</a>

AWS-Workspace-Höchstgrenzen je Databricks-Account:

- **Premium-Tier:** 10 Standard, 50 Hard Limit.
- **Enterprise-Tier:** 1.000 Classic-Workspace-Hard-Limit, 2.000 Serverless-Workspace-Hard-Limit.

Kritische zugrunde liegende AWS-Infrastrukturgrenzen betreffen die Anzahl an Accounts und VPCs je Region.

## <a id="split-nachteile">5. Nachteile aufgeteilter Workspaces</a>

- Keine Notebook-Kollaboration über Workspaces hinweg (Unity Catalog ermöglicht dennoch Daten-Sharing; GitHub erleichtert Code-Sharing).
- Erheblicher administrativer Mehraufwand bei der Verwaltung von 100+ Workspaces, Risiko verwaister Deployments.
- Vollständige Automatisierung für Einrichtung und Wartung zwingend erforderlich (Terraform, Cloud-Tools oder REST-APIs).
- Teure Netzwerkinfrastruktur, wenn jeder Workspace auf Netzwerkebene abgesichert wird.
- Eingeschränkte Cross-Workspace-Unterstützung für bestimmte Fähigkeiten wie Serverless-Egress-Kontrollen und KI-Features.

## <a id="security-modes">6. Security Modes</a>

- **Standard Mode:** Unterstützt mehrere Nutzer pro Cluster, geeignet für ETL und Datenexploration. Ermöglicht SQL, Python und Scala mit granularer Zugriffskontrolle (view-basiert sowie attribut-/tabellenbasiert). Kein ML-DBR-Support.
- **Dedicated Mode:** Unterstützt ML DBR und alle Programmiersprachen. Beschränkt auf Single-User- bzw. Single-Group-Zugriff je Cluster-Zuweisung.

## <a id="namenskonvention">7. Namenskonvention</a>

Empfohlenes Muster: `{organisation}-{umgebung}-{region}-{zweck}`

Beispiele: `acme-prod-us-west-analytics`, `acme-dev-shared`, `acme-prod-eu-west-gdpr`, `acme-staging-us-east-dataeng`.

Best Practices: Kleinbuchstaben mit Bindestrichen; Umgebungskennzeichnung einschließen; Regionsangabe bei Multi-Region-Setups; Geschäftsbereichs-/Zweck-Kennzeichnung; maximal 50 Zeichen Länge; Dokumentation in Runbooks.

## <a id="beispiele">8. Beispiel-Deployments</a>

- **Single-Tenant, Single-Region:** Ein Produktions-Workspace, ein Development-Workspace, alle Ressourcen in einer einzelnen Region.
- **Multi-Region:** Getrennte US- und EU-Produktions-Workspaces (DSGVO-Konformität), gemeinsam genutzter Development-Workspace, regionale Unity-Catalog-Metastores mit D2D-OpenSharing.
- **Multi-Business-Unit:** Eigener Workspace je Geschäftsbereich, gemeinsam genutzter Development-Workspace, zentraler Unity-Catalog-Metastore mit Catalog-Ebenen-Trennung.
- **Environment-basiert:** Getrennte Production-, Staging- und Development-Workspaces mit eigenen Netzwerken und Storage.

## <a id="empfehlungen">9. Strategische Empfehlungen</a>

**Empfohlene Ansätze:**

- SDLC-Umgebungen in getrennte Workspaces aufteilen (mindestens Dev und Prod).
- Automatisierungs-Tools wie Terraform für wiederholbare Muster nutzen.
- Standardmäßig Serverless-Workspaces verwenden, Classic nur für spezifische Anforderungen.
- Split-Strategie und Namenskonventionen dokumentieren.
- Einen administrativen Workspace je Region für die Unity-Catalog-Verwaltung etablieren.

**Zu vermeidende Muster:**

- Individuelle Team- oder Kleinprojekt-Workspaces (stattdessen Unity-Catalog-Catalogs/Schemas nutzen).
- 50–100+ Workspaces ohne robuste Begründung und Automatisierung deployen.
- Unnötige Workspace-Fragmentierung trotz fehlendem Isolationsbedarf.
- Ad-hoc-Workspace-Erstellung unter Umgehung der Namenskonventionen.

## <a id="ergebnisse">10. Ergebnisse der Phase</a>

Nach Abschluss dieser Phase sollten feststehen: Wahl des Deployment-Modells; an die Organisationsstruktur angepasste Workspace-Split-Strategie; Verständnis der Ressourcengrenzen mit Abhilfemaßnahmen; Dokumentation der Namenskonvention; Verständnis der Security Modes; dokumentierte Beispiel-Deployment-Architektur; Automatisierungsstrategie für die Provisionierung.

**Nächste Phase:** Phase 3 — Unity-Catalog-Architektur gestalten (siehe [03 Unity Catalog Architektur.md](03%20Unity%20Catalog%20Architektur.md)).

## <a id="quelle">11. Quelle</a>

- https://docs.databricks.com/aws/en/lakehouse-architecture/deployment-guide/workspace-strategy

**Stand:** 2026-08-21.
