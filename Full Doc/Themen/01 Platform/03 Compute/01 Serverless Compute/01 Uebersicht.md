# Serverless Compute — Übersicht

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/>

## Was ist Serverless Compute?

Serverless Compute ist ein **von Databricks verwalteter Dienst**, mit dem sich schnell On-Demand-Rechenressourcen für **Notebooks, Workflows und Lakeflow-Pipelines** nutzen lassen — ohne Infrastruktur im eigenen Cloud-Konto zu provisionieren. Databricks allokiert und verwaltet die Ressourcen automatisch: schnellerer Start, schnellere Skalierung, weniger Leerlauf und weniger Verwaltungsaufwand.

> *"Serverless workloads are protected by multiple layers of security and are designed to be enterprise-ready."*

**Vorteile:**

- Automatische Ressourcen-Allokation und -Verwaltung
- Schnellere Start- und Skalierungszeiten
- Minimierte Leerlaufzeit
- Weniger Verwaltung von Compute-Ressourcen
- Enterprise-taugliche Sicherheit mit mehreren Schutzschichten

## Unterstützte Workloads und Features

**Primäre Workloads:**

- Serverless Notebooks (siehe [02 Notebooks.md](02%20Notebooks.md))
- Git Folder Serverless (**Beta**, siehe [03 Git-Ordner (Git Folder Serverless).md](03%20Git-Ordner%20(Git%20Folder%20Serverless).md))
- Serverless Jobs
- Serverless Lakeflow Pipelines
- Streaming auf Serverless Compute (siehe [07 Streaming.md](07%20Streaming.md))
- AI Runtime (**Preview**, Serverless GPU)

**Features auf Serverless-Infrastruktur, die separat konfiguriert werden:**

- Serverless SQL Warehouses
- Databricks Model Training — Forecasting
- Data Quality Monitoring
- Predictive Optimization

## Voraussetzungen und Verfügbarkeit

- *"Serverless compute is available by default in most workspaces and does not require enablement."*
- Workspaces mit aktiviertem **Unity Catalog** haben automatisch Zugriff.
- Workspaces **ohne** Unity Catalog müssen upgraden, um Serverless Compute nutzen zu können.

## FAQ (Kernpunkte)

- **Release-Management:** Serverless ist ein *"versionless product"* — Runtime-Upgrades werden automatisch und schrittweise über alle Nutzer verteilt. Alle Serverless-Workloads laufen auf der **neuesten** Runtime-Version (Details in den Release Notes). Environment-Versionen (nicht Databricks-Runtime-Versionen) für Notebooks/Jobs — siehe [04 Umgebung und Abhaengigkeiten.md](04%20Umgebung%20und%20Abhaengigkeiten.md).
- **Kostenschätzung:** Repräsentative Workloads benchmarken und die Systemtabelle `system.billing.usage` auswerten; ein herunterladbares Cost-Observability-Dashboard ist verfügbar.
- **Abrechnungsverzögerung:** *"there could be up to a 24-hour delay between when you run a workload and its usage being reflected in the billable usage system table."*
- **Unerwartete Abrechnungssätze:** Data Quality Monitoring und Predictive Optimization laufen auf Serverless-Infrastruktur und werden unter der **Serverless-Jobs-SKU** abgerechnet.
- **Private Repositories:** Repos, die Authentifizierung erfordern, benötigen **pre-signed URLs**.
- **Bibliotheken:** Databricks empfiehlt, Libraries für Job-Tasks über **Environments** zu verwalten und zu installieren.
- **Custom Data Sources:** *"only sources that use Lakehouse Federation are supported."*
- **Networking:** Serverless-Ressourcen laufen in einer von Databricks verwalteten **Serverless Compute Plane** (eigene Netzwerkarchitektur/Sicherheit). Siehe [11 Serverless Compute verwalten.md](11%20Serverless%20Compute%20verwalten.md) und die Doku *Serverless network security* (NCCs, Private Link, Firewall).
- **Declarative Automation Bundles:** Serverless lässt sich für Jobs über Bundles konfigurieren.
- **Lokale Entwicklung:** **Databricks Connect** erlaubt das Ausführen von Serverless-Workloads von lokalen Rechnern / Daten-Apps.

## Verwandte Themen

- [09 Einschraenkungen.md](09%20Einschraenkungen.md) — vollständige Liste der Serverless-Limitierungen
- [05 Best Practices.md](05%20Best%20Practices.md) · [06 Migration von Classic zu Serverless.md](06%20Migration%20von%20Classic%20zu%20Serverless.md)
