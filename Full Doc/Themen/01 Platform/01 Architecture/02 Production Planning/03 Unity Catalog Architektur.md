# Phase 3: Unity-Catalog-Architektur gestalten

Teil der [Production Planning](Uebersicht.md)-Reihe. Behandelt Governance-Betriebsmodelle, Metastore-Design, Catalog-Struktur, Storage-Credential- und External-Location-Strategie, Berechtigungsmodell und das Hub-and-Spoke-Muster. Für die konkrete Einrichtungs-Syntax (Metastore anlegen, `GRANT`/`REVOKE` etc.) siehe [Governance/Data Governance](../../../Governance/Data%20Governance/) — dieses Dokument behandelt die vorgelagerten Architektur-Entscheidungen.

## Abschnittsübersicht

1. [Governance-Betriebsmodell wählen](#governance-modell)
2. [Metastore-Architektur gestalten](#metastore)
3. [Catalog-Struktur gestalten](#catalog-struktur)
4. [Storage-Credential-Strategie gestalten](#storage-credentials)
5. [External-Location-Strategie gestalten](#external-locations)
6. [Berechtigungsmodell gestalten](#berechtigungsmodell)
7. [Hub-and-Spoke-Design-Pattern](#hub-spoke)
8. [Empfehlungen](#empfehlungen)
9. [Ergebnisse der Phase](#ergebnisse)
10. [Quelle](#quelle)

---

## <a id="governance-modell">1. Governance-Betriebsmodell wählen</a>

Unity Catalog aktiviert sich automatisch für Accounts, die nach dem 8. November 2023 erstellt wurden — inklusive automatischer Metastore-Erstellung und Workspace-Zuweisung.

Vier Governance-Modelle:

| Attribut | Zentralisiert | Dezentralisiert | Föderiert | Hybrid |
|---|---|---|---|---|
| **Definition** | Eine zentrale Autorität kontrolliert alle Daten-/KI-Policies | Geschäftsbereiche verwalten Policies unabhängig | Zentrale Guidelines + lokale Autonomie | Kerndaten zentral, Domänen dezentral |
| **Entscheidungsfindung** | Top-down durch zentrales Team | Unabhängig durch Geschäftsbereiche | Zentral setzt Grenzen; lokal entscheidet innerhalb | Zentral für Kerndaten; Einheiten entscheiden domänenspezifisch |
| **Daten-Eigentümerschaft** | Zentrales Team besitzt alle Assets | Einzelne Teams besitzen ihre Daten | Mehrere Teams teilen sich Eigentümerschaft | Zentral besitzt geteilte Daten; Einheiten besitzen Domänendaten |
| **Skalierbarkeit** | Kann mit wachsender Organisation zum Flaschenhals werden | Unabhängige Skalierung möglich; Koordination schwierig | Skaliert bei erhaltener Koordination | Kern skaliert zentral; Einheiten skalieren unabhängig |
| **Compliance & Sicherheit** | Konsistente Durchsetzung mit starker Aufsicht | Durchsetzung variiert; potenzielle Sicherheitslücken | Zentral setzt Standards; lokale Durchsetzung | Kerndaten streng compliant; Domänen flexibel |
| **Operative Effizienz** | Effizient, aber bürokratisch/langsame Freigaben | Schnelle Anpassung; doppelter Aufwand/Silos | Balance aus Effizienz/Flexibilität; Koordinationsaufwand | Kernbetrieb kann Flaschenhals sein; Einheiten effizient |
| **Anwendungsfall** | Regulierte Branchen (Finanzen, Gesundheit) | Agile Unternehmen/Startups/Innovation | Große Enterprises/Multinationals | Fintechs, die Compliance/Innovation balancieren |

**Best Practices:** Für die meisten Organisationen mit föderierter Governance starten (balanciert Kontrolle und Agilität); zentralisierte Governance für stark regulierte Branchen nutzen (z. B. Finanzen, Gesundheit, Behörden); Rollen und Verantwortlichkeiten je Modell klar dokumentieren; Governance-Modell an bestehende Organisationsstrukturen ausrichten; Modell regelmäßig überprüfen und mit der Reifung der Datenplattform anpassen.

**Auswirkung:** Die Wahl des Governance-Modells beeinflusst das Metastore-Design — zentralisierte Modelle können einen einzelnen Metastore-Admin zuweisen; dezentralisierte Modelle verwalten Berechtigungen über CI/CD-Automatisierung statt einzelnen Administratoren zu delegieren.

## <a id="metastore">2. Metastore-Architektur gestalten</a>

**Definition:** „Ein Unity-Catalog-Metastore ist der regionale Top-Level-Container für Metadaten und Governance." Jeder Metastore speichert Metadaten für schützbare Objekte (Tables, Views, Volumes, External Locations, Shares) und Zugriffsberechtigungen, betrieben als Multi-Tenant-Dienst in der Databricks Control Plane.

**Wichtige Einschränkung:** „Unity Catalog erlaubt einen einzelnen Metastore je Region und erlaubt die Nutzung dieses Metastores nur in seiner zugewiesenen Region. Jeder Workspace muss genau einem Metastore zugewiesen sein."

### Metastore-Admin-Rolle

Optionale Konfiguration, abhängig vom Governance-Modell — wird bei automatischer Unity-Catalog-Aktivierung nicht gesetzt.

- **Erforderlich, wenn:** Storage von Unity-Catalog-Objekten auf Metastore-Ebene verwaltet wird oder Daten zentral über mehrere regionale Workspaces hinweg verwaltet werden.
- **Zentralisiertes Modell:** einzelnen Metastore-Admin oder eine dedizierte Gruppe zuweisen.
- **Dezentralisiertes Modell:** Berechtigungen über automatisierte Deployment-Pipelines verwalten.

**Empfehlung:** „Wird ein Metastore-Admin genutzt, wird dringend empfohlen, die Rolle einer dedizierten Gruppe statt einem einzelnen Nutzer zuzuweisen."

### Isolationsmechanismen

Vier Isolationsebenen:

1. **Admin Isolation (Delegation des Managements):** designierte Personen/Teams verwalten Daten nach Zweck/Eigentümerschaft.
2. **Workspace Binding:** Daten sind nur in designierten Umgebungen zugänglich — ein Catalog kann an mehrere Workspaces gebunden werden, ein Workspace an mehrere Catalogs, Credentials und External Locations desselben Metastores.
3. **Storage Isolation:** Daten sind physisch im Storage getrennt.
4. **Unity-Catalog-Zugriffskontrolle:** Nutzer greifen auf Daten/Metadaten gemäß vereinbarter Zugriffsregeln zu.

### Metastore-Design-Patterns

- **Single Cloud, Single Region:** ein Metastore in der Region, alle regionalen Workspaces diesem zugewiesen.
- **Single Cloud, Multi-Region:** ein Metastore je Region derselben Cloud; Databricks-managed (D2D) OpenSharing teilt Daten zwischen Metastores über Regionen hinweg.
- **Multi-Cloud, Multi-Region:** ein Metastore je Region und Cloud; D2D-OpenSharing teilt Daten über Clouds/Regionen hinweg.
- **Alternative Muster:** ein Metastore je Geschäftsbereich (bei vollständigem Isolationsbedarf ohne Daten-Sharing); ein Metastore je Umgebung (seltener, für strikte Umgebungsisolation von Dev/Staging/Prod).

### Multi-Region-Überlegungen

„Wird Databricks in mehreren Regionen genutzt, muss in jeder Region ein eigener Unity-Catalog-Metastore deployt werden."

**Kritische Warnung:** „Geteilte Tabellen nicht als External Tables in mehr als einem Metastore registrieren." Risiko: Änderungen an Schema, Tabelleneigenschaften und Kommentaren durch Schreibvorgänge auf Metastore A registrieren sich nicht bei Metastore B — Schema-Mismatches und getrennte Eigenschaften entstehen, Tabellen müssen neu angelegt werden. Kann Delta-Commit-Konsistenzprobleme verursachen. Für Cross-Metastore-Daten-Sharing D2D-OpenSharing nutzen.

**Best Practices:** Standardmäßig einen Metastore je Region deployen; Databricks-managed OpenSharing für regionsübergreifendes Tabellen-Sharing nutzen; Häufigkeit/Volumen regionsübergreifenden Datenzugriffs bewerten, ggf. Synchronisationspipeline bei zu hohen Kosten einrichten; Metastore-Root-Storage in derselben Region wie den Metastore ablegen (Performance).

### Metastore-Best-Practices (allgemein)

„Einen Metastore je Region als Standardmuster für operative Einfachheit nutzen." Workspaces derselben Region demselben Metastore zuweisen; Catalogs innerhalb des Metastores zur Trennung nach Umgebung/Domäne nutzen; einen administrativen Workspace je Region zur Verwaltung von Unity-Catalog-Ressourcen anlegen; Metastore-Zuweisungen und regionale Grenzen im Runbook dokumentieren.

**Hinweis für neue Accounts:** Für nach dem 8. November 2023 erstellte Accounts werden Metastores automatisch erstellt und zugewiesen.

## <a id="catalog-struktur">3. Catalog-Struktur gestalten</a>

Catalogs sind die erste Organisationsebene innerhalb des Metastores und enthalten Schemas, die wiederum Tables, Views, Volumes und Functions enthalten.

### Design-Patterns

- **Environment-basiert:** getrennte Catalogs je SDLC-Umgebung (`dev`, `staging`, `prod`) — unterstützt Promotion-Workflows und verhindert versehentliche Produktionsänderungen. Beispiele: `sales_dev`, `sales_prod`.
- **Domain-basiert:** getrennte Catalogs je Geschäftsdomäne (`sales`, `marketing`, `finance`, `engineering`) — passt zu Data-Mesh-Architekturen und Domänen-Eigentümerschaft.
- **Hybrid:** kombiniert Environment- und Domain-Muster (`sales_prod`, `sales_dev`, `finance_prod`, `finance_dev`) — bietet sowohl Isolation als auch klare Eigentümerschaft.
- **Data-Lifecycle-basiert:** getrennte Catalogs je Datenreife-Stufe (`raw`, `curated`, `analytics`) — folgt Medallion-Architektur-Prinzipien auf Catalog-Ebene.

### Sandbox-/Entwicklungsbereiche

„Viele Teams brauchen Sandbox-Bereiche, um temporäre Datensätze für den internen Gebrauch anzulegen." Individuen oder Teams eigene, sandboxed Schemas bereitstellen, in denen sie Tabellen anlegen können, diese aber nicht außerhalb des eigenen Teams teilen können, da sie weder Schema noch Catalog besitzen.

### Namenskonvention

Eine Namenskonvention wählen, die zu bestimmten Konfigurationen passt — z. B. nach SDLC-Umgebung (Dev, Test, Prod), Medallion-Layer (Bronze, Silver, Gold) oder Geschäftsbereich (Billing, Customer, Sales). Das Architekturteam legt die genaue Konvention fest.

### Best Practices

„Environment-basierte Catalogs als Standard für die meisten Organisationen nutzen." Domain-basierte Catalogs für Data-Mesh-/föderierte Governance-Modelle nutzen; Anzahl der Catalogs begrenzen, um administrativen Aufwand zu reduzieren (typischerweise 3–10 je Metastore); konsistente Namenskonvention über alle Catalogs hinweg; Catalog-Zwecke und Daten-Eigentümerschaft in Catalog-Kommentaren dokumentieren; Catalog-Grants nutzen, um Schema-/Tabellenerstellung innerhalb jedes Catalogs zu kontrollieren; „keine separaten Catalogs für einzelne Teams oder Projekte anlegen (stattdessen Schemas nutzen)."

## <a id="storage-credentials">4. Storage-Credential-Strategie gestalten</a>

**Definition:** Storage Credentials sind Authentifizierungsobjekte, die Unity Catalog erlauben, im Namen von Nutzern auf Cloud-Storage zuzugreifen — sicherer Zugriff auf kundenverwalteten Storage, ohne langlebige Credentials zu teilen.

**Wann benötigt:** External Locations auf Cloud-Storage (S3, ADLS Gen2, GCS) anlegen; Zugriff auf kundenverwalteten Storage für External Tables/Volumes; Lesen von Daten aus nicht durch Unity Catalog verwaltetem Cloud-Storage.

**Wann NICHT benötigt:** Zugriff auf Unity-Catalog-Managed-Tables und -Volumes (Databricks-verwalteter Storage); Nutzung des Standard-Storage in Serverless-Workspaces.

### AWS-Architektur

Storage Credentials nutzen Cross-Account-IAM-Rollen mit Trust-Policies, die Databricks erlauben, die Rolle zu übernehmen. Die IAM-Rolle muss S3-Berechtigungen (z. B. `s3:GetObject`, `s3:PutObject`, `s3:ListBucket`) für bestimmte S3-Buckets/-Präfixe gewähren.

**Authentifizierungsablauf:**

1. Unity Catalog übernimmt die IAM-Rolle über die Trust-Beziehung.
2. AWS validiert die Trust-Policy und gibt temporäre Credentials zurück.
3. Unity Catalog nutzt die temporären Credentials für S3-Zugriff im Namen des Nutzers.
4. Zugriff wird basierend auf den an die Rolle angehängten IAM-Policies gewährt/verweigert.

### Design-Patterns und Best Practices

Getrennte IAM-Rollen für unterschiedliche Storage-Buckets/Datendomänen (z. B. `uc-prod-sales-role`, `uc-dev-engineering-role`); Least-Privilege-Berechtigungen (nur Zugriff auf bestimmte S3-Präfixe); ein Storage Credential je Umgebung (Dev, Staging, Prod); ein Storage Credential je Geschäftsbereich bei erforderlicher Datentrennung; AWS CloudTrail zur Audit-Prüfung des S3-Zugriffs aktivieren; Bucket-Policies als zusätzliche Sicherheitsebene nutzen.

## <a id="external-locations">5. External-Location-Strategie gestalten</a>

**Definition:** „External Locations bilden Storage Credentials auf spezifische Cloud-Storage-Pfade ab und erlauben Unity Catalog, Zugriff auf außerhalb von Unity-Catalog-verwaltetem Storage liegende Daten zu regeln. Jede External Location kombiniert ein Storage Credential mit einem Cloud-Storage-URL-Präfix."

**Anwendungsfälle:** Zugriff auf bestehende Daten im Cloud-Storage von vor der Unity-Catalog-Einführung; External Tables, die auf von anderen Systemen verwaltete Datendateien verweisen; Daten-Sharing mit externen Systemen, die direkten Dateizugriff benötigen; Speicherung großer unstrukturierter Daten (Videos, Bilder, PDFs) in Unity-Catalog-Volumes.

**Design-Patterns:** External Locations auf dem höchstmöglichen gemeinsamen Pfad-Präfix anlegen, um die Anzahl der Locations zu minimieren; External Locations an Catalog-/Schema-Grenzen ausrichten (z. B. eine je Catalog); nach Umgebung trennen (Dev, Staging, Prod); nach Geschäftsbereich/Datendomäne trennen, wo erforderlich.

**Best Practices:** External Locations für Daten nutzen, die in bestimmten Cloud-Storage-Pfaden verbleiben müssen; wo möglich Unity-Catalog-Managed-Tables statt External Locations nutzen (einfachere Governance und Optimierung); beschreibende Namen verwenden, die Storage-Pfad/Zweck angeben (z. B. `s3-sales-data-prod`, `adls-finance-reports-dev`); Zugriff auf External Locations nur an Nutzer vergeben, die External Tables anlegen müssen; Zweck und Daten-Eigentümerschaft der External Location dokumentieren.

## <a id="berechtigungsmodell">6. Berechtigungsmodell gestalten</a>

**Beispiel-Berechtigungsmodell:**

- **Data Curators:** verwalten alle Datenassets (Eigentümerschaft, Erstellungs-, Änderungs-, Löschrechte).
- **Data Consumers:** Nur-Lese-Zugriff auf die meisten Datenassets (`SELECT`-Rechte).
- **Data Engineers:** Lese-/Schreibzugriff auf Development- und Staging-Umgebungen.
- **Analysts:** Nur-Lese-Zugriff auf Produktions-Analytics-Daten.

**Berechtigungsdelegation:** „Der Metastore-Administrator etabliert und setzt Berechtigungsrichtlinien durch, indem er Zugriffsrechte an Nutzer oder Gruppen entsprechend ihrer Verantwortlichkeiten zuweist und delegiert." Beispiel: Data Curators erhalten Eigentümerschaft/Schreibrechte; Consumers erhalten Leserechte über Gruppenzugehörigkeit. Das sichert konsistente Governance, vereinfacht die Wartung und unterstützt Compliance.

**Best Practices:** Rechte an Gruppen statt einzelne Nutzer vergeben; Least-Privilege-Zugriff nutzen; Zugriffskontrollrichtlinien dokumentieren und regelmäßig mit Security-Teams überprüfen; Catalog-/Schema-Grants für grobkörnige Zugriffskontrolle nutzen; Table-/View-Grants für feingranulare Zugriffskontrolle nutzen; Dynamic Views sowie Row-/Column-Filter für sensible Daten nutzen; Zugriff über System-Tabellen (`system.access.audit`) auditieren.

## <a id="hub-spoke">7. Hub-and-Spoke-Design-Pattern</a>

„Das Hub-and-Spoke-Design-Pattern ist eine gängige Architektur für Enterprise-Unity-Catalog-Deployments. Dieses Muster zentralisiert gemeinsam genutzte Datenassets in einem Hub-Catalog und erlaubt gleichzeitig domänenspezifische Daten in Spoke-Catalogs."

**Eigenschaften:**

- **Hub-Catalog:** enthält organisationsweite, gemeinsam genutzte Datenassets (Kundenstammdaten, Referenzdaten, zentral kuratierte Datensätze).
- **Spoke-Catalogs:** enthalten domänenspezifische Daten im Besitz der Geschäftsbereiche (Sales-Analytics, Marketing-Kampagnen).
- **Storage-Trennung:** Hub- und Domänen-Catalogs nutzen dedizierten Storage mit getrennten Storage Credentials.
- **Präferenz für Managed Tables:** „Für strukturierte Daten im Lakehouse Managed Tables nutzen."
- **Volumes für Rohdaten:** „Volumes nutzen, um auf Landing-, Roh- oder unstrukturierte Daten zuzugreifen (die außerhalb des Lakehouse liegen können, da Drittparteien üblicherweise direkten Zugriff auf diese Storage-Locations benötigen)."
- **External Tables zum Teilen:** „External Tables nutzen, um Daten außerhalb des Lakehouse zu teilen (mit anderen Systemen, die kein OpenSharing nutzen können oder direkten Zugriff auf die Storage-Location benötigen)."

**Beispielstruktur:**

```
Metastore (Region: us-east-1)
├── Hub-Catalog (prod_hub)
│   ├── Storage Credential: hub-prod-credential
│   ├── External Location: s3://company-hub-prod/
│   └── Schemas: customers, products, reference_data
├── Sales-Domänen-Catalog (sales_prod)
│   ├── Storage Credential: sales-prod-credential
│   ├── External Location: s3://company-sales-prod/
│   └── Schemas: transactions, forecasts, reports
└── Engineering-Domänen-Catalog (engineering_prod)
    ├── Storage Credential: engineering-prod-credential
    ├── External Location: s3://company-engineering-prod/
    └── Schemas: telemetry, monitoring, logs
```

**Best Practices:** Hub-Catalog für organisationsweit gemeinsam genutzte, von mehreren Domänen konsumierte Daten nutzen; Spoke-Catalogs für domänenspezifische, im Besitz von Geschäftsbereichen befindliche Daten nutzen; getrennte Storage Credentials/External Locations für Hub und jeden Spoke; Databricks-managed OpenSharing nutzen, um Daten von Hub zu Spokes zu teilen; Daten-Eigentümerschaft und Lineage für Hub und Spokes dokumentieren.

**Hinweis:** Metastore-Storage ist inzwischen optional und wird nicht mehr empfohlen.

## <a id="empfehlungen">8. Empfehlungen</a>

**Empfohlene Praktiken:**

- SDLC-Umgebungen im Unity-Catalog-Metastore auf Catalog-Ebene des dreistufigen Namespace trennen.
- Isolationsebenen von Unity Catalog nutzen, um Workloads, Teams, Geschäftsbereiche zu trennen.
- Databricks-managed OpenSharing nutzen, um Tabellen über Clouds und Regionen hinweg zu teilen.
- Bei Cross-Region-Setups Häufigkeit und Volumen des regionsübergreifenden Datenzugriffs bewerten; bei zu hohen Kosten eine Synchronisationspipeline zwischen Regionen einrichten.
- Unity-Catalog-Managed-Tables nutzen und keinen Storage-Ebenen-Zugriff auf Buckets gewähren.
- Volumes für Unity-Catalog-gesicherte POSIX-artige Dateipfade nutzen.
- Legacy-Datenzugriffsmuster wie Cloud-Storage-Mounting und Instance Profiles wo möglich vermeiden.
- Bewerten, ob kundenverwaltete Verschlüsselungsschlüssel für Managed Services/Storage nötig sind.

**Zu vermeidende Praktiken:**

- Keine anderen Access Modes als Standard oder Dedicated für Unity-Catalog-aktivierte Workspaces nutzen.
- Keine Produktionsdaten auf DBFS speichern.
- Keine External Tables über Regionen (Metastores) hinweg registrieren.
- Den Root-Bucket (DBFS) nicht zur Speicherung von Kundendaten nutzen — Risiken und Workarounds des Root-Buckets verstehen.

## <a id="ergebnisse">9. Ergebnisse der Phase</a>

Nach Abschluss dieser Phase sollten vorliegen: gewähltes Governance-Modell; entworfene Metastore-Architektur (i. d. R. eine je Region); entworfene Unity-Catalog-Storage-Architektur (Managed vs. External vs. Foreign Objects); definierte Catalog-Struktur (Environment-, Domain- oder Hybrid-basiert); Storage-Credential-Strategie mit getrennten Credentials je Umgebung/Domäne; External-Location-Strategie; Berechtigungsmodell mit klaren Rollen (Curators, Consumers, Engineers, Analysts); bewertetes Hub-and-Spoke-Design für Enterprise-Deployments.

**Nächste Phase:** Phase 4 — Netzwerkarchitektur gestalten (siehe [04 Netzwerkarchitektur.md](04%20Netzwerkarchitektur.md)).

**Implementierungsanleitung:** Für schrittweise Umsetzung siehe die Dokumentation „What is Unity Catalog?" sowie [Governance/Data Governance](../../../Governance/Data%20Governance/) in diesem Projekt für die konkrete GRANT-/Setup-Syntax.

## <a id="quelle">10. Quelle</a>

- https://docs.databricks.com/aws/en/lakehouse-architecture/deployment-guide/unity-catalog

**Stand:** 2026-08-21.
