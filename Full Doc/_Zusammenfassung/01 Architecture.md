



# 01 Architecture — Gesamtzusammenfassung

Konsolidierte Übersicht aller 12 Inhaltsdateien dieses Ordners (`01 Medallion Architecture.md` sowie alle 11 Dateien der zehnteiligen Reihe im Unterordner `02 Production Planning/`) mit **allen** enthaltenen Code-Beispielen. Jede Originaldatei bleibt die primäre, ausführliche Quelle — dieses Dokument dient als kompakter Überblick plus vollständige Code-Referenz an einem Ort.

**Hinweis zum Code-Anteil:** Der Ordner "01 Architecture" ist überwiegend konzeptionell (Enterprise-Architektur- und Governance-Planung, kein Hands-on-Tutorial). Nur 2 der 12 Dateien enthalten Fenced-Code-/Diagramm-Blöcke: "01 Medallion Architecture.md" (5 SQL-Blöcke) und "03 Unity Catalog Architektur.md" (1 ASCII-Strukturdiagramm). Alle übrigen Dateien sind reine Fließtext-/Tabellen-Konzeptüberblicke — dort jeweils explizit vermerkt.

## Inhalt

1. [Medallion Architecture](#1-medallion-architecture)
2. [Production Planning — Überblick](#2-production-planning--überblick)
3. [Phase 1: Account und Identität](#3-phase-1-account-und-identität)
4. [Phase 2: Workspace-Strategie](#4-phase-2-workspace-strategie)
5. [Phase 3: Unity-Catalog-Architektur](#5-phase-3-unity-catalog-architektur)
6. [Phase 4: Netzwerkarchitektur](#6-phase-4-netzwerkarchitektur)
7. [Phase 5: Storage-Architektur](#7-phase-5-storage-architektur)
8. [Phase 6: Delta-Lake-Architektur](#8-phase-6-delta-lake-architektur)
9. [Phase 7: Infrastructure as Code](#9-phase-7-infrastructure-as-code)
10. [Phase 8: Compute-Konfiguration](#10-phase-8-compute-konfiguration)
11. [Phase 9: Observability-Strategie](#11-phase-9-observability-strategie)
12. [Phase 10: High Availability und Disaster Recovery](#12-phase-10-high-availability-und-disaster-recovery)

---

## 1. Medallion Architecture

Die Medallion Architecture (Multi-Hop-Architektur) organisiert Lakehouse-Daten in drei progressiv verfeinerten Schichten **Bronze ⇒ Silver ⇒ Gold**, um Struktur und Qualität inkrementell zu verbessern und dabei ACID-Eigenschaften über alle Transformationsschritte hinweg zu garantieren.

- **Bronze:** Rohdaten-Ingestion mit minimaler Validierung, Single Source of Truth, Felder möglichst als `STRING`/`VARIANT`/`BINARY` speichern, um Schemaänderungen nicht zu verlieren. Nicht für direkten Analysten-Zugriff gedacht.
- **Silver:** Schema Enforcement, Dedupe, Null-Handling, Type Casting, Joins — validierte, angereicherte, nicht-aggregierte Datensätze; überwiegend als Streaming Reads aus Bronze/Silver gebaut.
- **Gold:** dimensional modellierte, stark aggregierte, geschäftsorientierte Datensätze für BI/ML, für Query-Performance optimiert (häufig via Materialized Views).
- Die Architektur ist **empfohlene Best Practice, keine Pflicht**.
- Ingestion-Frequenz-Optionen mit Kosten-/Latenz-Trade-off: Continuous Incremental Ingestion (Streaming, `spark.readStream`, höhere Kosten/niedrigere Latenz), Triggered Incremental Ingestion (`Trigger.Available`, geplante/dateiausgelöste Trigger), Batch Ingestion mit manuellen inkrementellen Updates (`spark.read`, Partition-Overwrite, höchste Latenz).
- **Resiliente Pipeline-Muster:** Bronze akzeptiert alle Felder als `STRING` mit `schemaEvolutionMode => 'rescue'`, damit kein Typ-Mismatch die Pipeline stoppt; Silver nutzt `TRY_CAST` + NULL-tolerantes `CASE WHEN`-Constraint-Muster. `schemaHints` deklariert künftige Spalten proaktiv; `_rescued_data` fängt alles Unerwartete als JSON auf. **Kritisch:** Constraints auf per Schema Evolution hinzugefügten Spalten müssen NULL-tolerant sein, sonst schlagen alle historischen Datensätze fehl.
- **Guiding Principles des Databricks Well-Architected Framework** (übergeordneter Rahmen): (1) Daten kuratieren und als vertrauenswürdige Produkte anbieten (Ingest/Curated/Final Layer), (2) Daten-Silos eliminieren und Datenbewegung minimieren, (3) Wertschöpfung durch Self-Service demokratisieren (Data-as-Product), (4) organisationsweite Daten-/KI-Governance-Strategie (Datenqualität, Data Catalog, Access Control), (5) offene Schnittstellen und Formate fördern (Interoperabilität, kein Vendor-Lock-in), (6) für Skalierung bauen, Storage/Compute entkoppeln.



### Gold-Layer-Aggregationsbeispiel

```sql
CREATE OR REPLACE MATERIALIZED VIEW main.example_output.weekly_bookings AS
SELECT date_trunc('week', check_in) AS week,
       property_id,
       status,
       count(*) AS total_bookings,
       sum(total_amount) AS total_revenue
FROM samples.wanderbricks.bookings
GROUP BY week, property_id, status
```

### Resiliente Pipeline-Muster: Bronze als STRING + rescue

```sql
CREATE OR REFRESH STREAMING TABLE bronze_events
COMMENT "Bronze: all fields as STRING, schema rescue enabled"
AS SELECT *
FROM STREAM read_files(
  '/path/to/source',
  format => 'json',
  schemaEvolutionMode => 'rescue'
)
```

### Silver: TRY_CAST mit NULL-tolerantem Constraint

```sql
CREATE OR REFRESH STREAMING TABLE silver_events (
  CONSTRAINT valid_amount EXPECT (
    CASE WHEN amount IS NOT NULL
    THEN amount >= 0 ELSE TRUE END
  ) ON VIOLATION DROP ROW
)
AS SELECT *,
  TRY_CAST(amount_str AS DOUBLE) AS amount
FROM STREAM bronze_events
```

### schemaHints — künftige Spalten vorab deklarieren

```sql
CREATE OR REFRESH STREAMING TABLE bronze_events
AS SELECT *
FROM STREAM read_files(
  '/path/to/source',
  format => 'json',
  schemaHints => 'loyalty_tier STRING, region_code STRING',
)
-- Alte Datensätze: loyalty_tier = NULL (akzeptabel)
-- Neue Datensätze: loyalty_tier automatisch befüllt


# Alle bekannten und zukünftigen Spalten via Wildcard (*) als String erzwingen
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json") # oder "csv"
  .option("cloudFiles.inferColumnTypes", "false") # Keine automatische Typ-Erkennung
  .option("cloudFiles.schemaHints", "* string")   # Wildcard: ALLE Spalten String
  .option("mergeSchema", "true")                  # Erlaubt Schema-Evolution
  .load("/pfad/zu/den/daten"))
```

```sql
# Alle bekannten und zukünftigen Spalten via Wildcard (*) als String erzwingen
CREATE OR REFRESH STREAMING TABLE bronze_events
COMMENT "Bronze: all fields as STRING, schema rescue enabled"
AS SELECT *
FROM STREAM read_files(
  'abfss://container@storage.dfs.core.windows.net/pfad/zu/daten',
  format => 'json', -- oder 'csv'
  dataTypeHints => '* string' -- Der Wildcard-Hint erzwingt STRING 
)
```



### _rescued_data — letzte Verteidigungslinie

`_rescued_data` Spalte bei `read_files()` (Batch, SQL) und Auto Laoder (`cloudFiles` / `STREAM read_files`) automatisch eingefügt.

Aber bei `spark.sreadStream()`, `spark.read()` muss die Spalte via .option("rescuedDataColumn", "...") eingefügt werden.

Auch bei `COPY INTO` muss die Spalte mit   `FORMAT_OPTIONS ('rescuedDataColumn' = '...')`  eingefügt werden.

```sql
-- Gerettete Felder im Nachhinein untersuchen
SELECT
  event_id,
  _rescued_data:unexpected_field  AS unexpected_field,
  _rescued_data:new_column        AS new_column
FROM bronze_events
WHERE _rescued_data IS NOT NULL
```

---

## 2. Production Planning — Überblick

Strukturierter, zehnphasiger Ansatz zur Planung einer produktionsreifen Enterprise-Databricks-Plattform, Teil des Databricks Well-Architected Framework. Zielgruppe: Cloud-Architekten, Platform Engineers, Data Architects, Security-Teams, Account-Administratoren. Voraussetzungen: aktive Cloud-Accounts mit Admin-Rechten, Databricks-Account-Console-Zugriff, dokumentierte Security-/Compliance-Anforderungen, Netzwerkplanung (CIDR-Bereiche), Identity-Provider-Details.

Die zehn (sich teils überlappenden) Phasen: (1) Account und Identität, (2) Workspace-Strategie, (3) Unity Catalog, (4) Netzwerk, (5) Storage, (6) Delta Lake, (7) IaC, (8) Compute, (9) Observability, (10) High Availability/DR. Implementierung erfolgt nach dem Design über **Terraform** (Infrastruktur) und **Databricks Asset Bundles** (Workloads) mit CI/CD-Automatisierung.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 3. Phase 1: Account und Identität

Vier administrative Ebenen (Account, Workspace, Data Governance, Compute Plane) — Kernprinzip: keine einzelne Ebene reicht für sich, Kontrollen müssen über alle Ebenen verteilt sein. Globale Admin-Rollen: **Account Admin** (account-weit: Billing, Identität, Workspace-Erstellung, Metastores) und **Workspace Admin** (einzelner Workspace). Feature-Rollen: Metastore Admin, Marketplace Admin, Billing Admin. Design-Patterns: zentralisiert, föderiert, getrennte Zuständigkeiten.

Identitätstypen: Users, Service Principals, Groups — Identitätsföderation ist für alle neuen Workspaces **standardmäßig aktiviert und nicht deaktivierbar**. SSO-Protokolle: OIDC (empfohlen für neue Deployments) vs. SAML 2.0 (Legacy/Enterprise); AWS bietet zusätzlich Social-SSO (Google/Microsoft) und E-Mail-Einmalpasscodes. Automatic Identity Management synchronisiert Nutzer/Gruppen/Service Principals direkt vom Identity Provider (einfacher als SCIM); Alternative bei fehlender Unterstützung: SCIM. **JIT Provisioning** ist seit dem 1. Mai 2025 standardmäßig für neue Accounts aktiviert und provisioniert Nutzer automatisch bei erster SSO-Authentifizierung.

Empfehlung: Account-Admin-Rechte auf 2–3 vertrauenswürdige Personen beschränken, SSO+MFA, Gruppen statt Einzelnutzer für Admin-Rollen, OAuth für Service Principals.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 4. Phase 2: Workspace-Strategie

Ein Workspace ist die operative Grenze in einer Cloud-Region für Team-Workloads (Notebooks, Jobs, Dashboards, Repos, Cluster-Policies, Secrets). Zwei Deployment-Modelle: **Serverless Workspaces** (Databricks-verwalteter Storage, sofort verfügbares Compute, empfohlener Start) vs. **Classic Workspaces** (eigener Cloud-Account, volle VPC-Kontrolle, nötig für On-Premises-Konnektivität/spezielle Compliance).

Gründe für mehrere Workspaces: Datenschutz, Geschäftsbereichs-Trennung, unterschiedliche Feature-Zugriffe, SDLC-Trennung, geografische Verteilung, Ressourcengrenzen. **AWS-Ressourcengrenzen je Account:** Premium-Tier 10 Standard/50 Hard Limit; Enterprise-Tier 1.000 Classic-/2.000 Serverless-Workspace-Hard-Limit. Nachteile aufgeteilter Workspaces: keine Notebook-Kollaboration über Workspaces hinweg, administrativer Mehraufwand, teure Netzwerkinfrastruktur je Workspace, eingeschränkte Cross-Workspace-Features.

**Security Modes:** Standard Mode (Multi-User-Cluster, SQL/Python/Scala, granulare View-/Attribut-/Tabellen-ACLs, kein ML-DBR) vs. Dedicated Mode (ML DBR + alle Sprachen, aber Single-User/-Group je Cluster). Namenskonvention: `{organisation}-{umgebung}-{region}-{zweck}`, max. 50 Zeichen. Beispiel-Deployment-Muster: Single-Tenant/Single-Region, Multi-Region (DSGVO), Multi-Business-Unit, Environment-basiert.

Empfehlung: SDLC-Trennung in eigene Workspaces (mind. Dev/Prod), Terraform-Automatisierung, standardmäßig Serverless; vermeiden: Team-/Kleinprojekt-Workspaces (stattdessen Catalogs/Schemas), 50–100+ Workspaces ohne Automatisierung.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 5. Phase 3: Unity-Catalog-Architektur

**Governance-Betriebsmodelle:** Zentralisiert (regulierte Branchen), Dezentralisiert (agile Startups), Föderiert (empfohlener Start für die meisten Organisationen — balanciert Kontrolle/Agilität), Hybrid (Fintechs). Unity Catalog aktiviert sich automatisch für Accounts nach dem 8. November 2023.

**Metastore:** regionaler Top-Level-Container für Metadaten/Governance — **ein Metastore je Region**, jeder Workspace genau einem Metastore zugewiesen. Vier Isolationsebenen: Admin Isolation, Workspace Binding, Storage Isolation, Unity-Catalog-Zugriffskontrolle. Design-Patterns: Single Cloud/Single Region, Single Cloud/Multi-Region (D2D-OpenSharing), Multi-Cloud/Multi-Region. **Kritische Warnung:** geteilte Tabellen nie als External Tables in mehr als einem Metastore registrieren (Schema-Mismatches, Delta-Commit-Konsistenzprobleme) — stattdessen D2D-OpenSharing nutzen.

**Catalog-Struktur-Patterns:** Environment-basiert (`sales_dev`/`sales_prod`, Standard für die meisten Organisationen), Domain-basiert (Data Mesh), Hybrid, Data-Lifecycle-basiert (`raw`/`curated`/`analytics`). Empfehlung: 3–10 Catalogs je Metastore, keine Catalogs für einzelne Teams (stattdessen Schemas).

**Storage Credentials:** Cross-Account-IAM-Rollen mit Trust-Policies für Zugriff auf kundenverwalteten Cloud-Storage (nicht nötig für Managed Tables/Volumes). **External Locations:** verknüpfen Storage Credential + Cloud-Storage-Pfad-Präfix, auf höchstmöglichem gemeinsamen Präfix anlegen.

**Berechtigungsmodell:** Data Curators (Eigentümerschaft/Schreibrechte), Data Consumers (`SELECT`), Data Engineers (Dev/Staging Lese-/Schreibzugriff), Analysts (Prod-Analytics Lesezugriff) — Rechte an Gruppen vergeben, Least Privilege, Audit über `system.access.audit`.

**Hub-and-Spoke-Pattern:** zentraler Hub-Catalog für organisationsweite Assets, domänenspezifische Spoke-Catalogs, getrennte Storage Credentials je Catalog, Managed Tables bevorzugt, Volumes für Rohdaten, External Tables nur zum Teilen mit Nicht-OpenSharing-Systemen. Metastore-Storage ist inzwischen optional und nicht mehr empfohlen.

### Hub-and-Spoke-Beispielstruktur

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

---

## 6. Phase 4: Netzwerkarchitektur

Drei Kommunikationskanäle: Inbound (Nutzerzugriff UI/API), Outbound (Serverless-Verbindungen zu Kundenressourcen), Classic-Konnektivität (Compute → Control Plane). Classic Compute nutzt kundenverwaltete Netzwerksegmentierung/Routing/Egress-Kontrollen; Serverless Compute nutzt Plattformkontrollen/Account-Konfigurationen.

**Secure Cluster Connectivity (SCC):** kehrt die Verbindungsrichtung um — Cluster initiieren Verbindung zum SCC-Relay in der Control Plane. Vorteile: keine öffentlichen IPs auf Compute-Knoten, keine Inbound-Ports nötig. Standardmäßig für alle neuen Workspaces aktiviert.

**IP Access Lists:** beschränken Zugriff auf bekannte IPs (VPN, Büro), auf Workspace- oder Account-Ebene konfigurierbar; bestehende Sessions brechen bei IP-Wechsel weg.

**Data-Exfiltration-Schutz:** Netzwerksegmentierung, Egress-Filterung, Private Link, Deaktivieren von Export-/Download-Features.

**Private Link:** private Konnektivität ohne öffentliches Internet — Front-End (Workspace-UI/API) und Back-End (Compute → Control Plane) Private Link, für hochsensible Umgebungen beide aktivieren.

**Serverless-Konnektivität (NCC):** Network Connectivity Configurations liefern stabile IPs für Firewall-Allowlisting; getrennte NCCs je Umgebung/Geschäftsbereich.

**AWS-VPC-Architektur:** mind. 2 Subnetze über unterschiedliche AZs, je Subnetz-Netzmaske /17 bis /26 (Kapazitätstabelle: /17→16.381 Knoten, /21→2.045, /26→29). Routentabellen: S3 via Gateway-VPC-Endpoint (kostenlos, bevorzugt), Internet via NAT-Gateway. Interface-Endpoints für STS/Kinesis in separaten Subnetzen. NAT-Gateways je AZ für HA. Optionale Netzwerk-Firewall für Exfiltration-Schutz. Hub-and-Spoke: zentrale Hub-VPC mit Endpoints/Firewall/Gateways, Spoke-VPCs mit Workspace-Subnetzen über Transit Gateway.

**Gestuftes Risikomodell:** Workspace-Ebene regelt "wer was darf", Netzwerk-Ebene regelt "wohin verbunden werden darf" — höhere Risiko-Workloads erhalten restriktivere Netzwerkumgebungen.

Keine eigenen Code-Beispiele in dieser Datei (nur eine Tabelle zu Subnetz-Kapazitäten) — reiner Konzeptüberblick.

---

## 7. Phase 5: Storage-Architektur

Zwei Storage-Arten: Databricks-verwalteter Storage (Default) vs. kundenverwalteter Storage. **Workspace-Storage** dient als Default-Catalog-Storage und für interne Plattformdaten (MLflow, Registry, Lakeflow, Cloud Fetch) — nicht für Produktionskundendaten nutzen; DBFS-Migration: strukturierte Daten → Managed Tables, unstrukturierte Daten → Volumes.

**Unity-Catalog-Storage-Objekttypen:** Managed Objects (Managed-Storage-Location auf Metastore-/Catalog-/Schema-Ebene, untergeordnet überschreibt übergeordnet), External Objects (Storage Credential + Cloud-Container), Foreign Objects (Verbindung zu externem Datensystem). AWS: pro Metastore optional ein Default-S3-Bucket plus beliebig viele Catalog-/Schema-/External-Buckets, Zugriff über Cross-Account-IAM-Trust-Rollen.

**Isolationsmuster:** nach Umgebung, Geschäftsbereich oder Datendomäne — jeweils mit getrennten Containern/Credentials.

**Verschlüsselung:** Standard = Cloud-Provider-Verschlüsselung + Databricks-verwalteter Schlüssel. Kundenverwaltete Schlüssel (CMK) für (1) Control-Plane/Managed-Services und (2) Compute-/Data-Plane — Pflicht für stark regulierte Umgebungen, optional für sensible Produktionsdaten in Standard-Enterprise-Deployments.

**Netzwerksicherheit:** S3-Bucket-Policies auf bestimmte VPCs/Endpoints beschränken, VPC-Endpoints für private Konnektivität, Storage-Logging aktivieren.

**Hub-and-Spoke-Storage:** analog zu Abschnitt 5 — Hub-Storage für geteilte Daten, Spoke-Storage je Geschäftsbereich, getrennte Credentials, Managed Tables bevorzugt, Volumes für Rohdaten.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 8. Phase 6: Delta-Lake-Architektur

Ergänzt die Medallion-Grunddefinitionen (Abschnitt 1) um Produktionsplanungs-Details. Layer-spezifische Best Practices: **Bronze** — alle Quellfelder erhalten, Volumes zum Landen, inkrementelle Ingestion, Partitionierung nach Ingestion-Datum. **Silver** — Qualitätsprüfungen, Managed Tables, Partitionierung nach Geschäftsdimension, Aktualitäts-SLAs. **Gold** — getrennte Tabellen je Geschäftsbereich, Dynamic Views für Sicherheit, Predictive Optimization, Lineage-Dokumentation.

**Landing Zone** (zusätzliche Vorstufe vor Bronze bei größeren Organisationen): Cloud-Object-Storage + Unity-Catalog-Volumes, Schreibzugriff für Drittsysteme, Event-Benachrichtigungen zum Pipeline-Trigger.

**Ingestion-Methoden:** Lakeflow Connect (verwalteter Databricks-Dienst), Partner-Tools (z. B. Fivetran), Custom-Pipelines (Lakeflow/Notebooks). **Ingestion-Muster:** Batch (günstig, hohe Latenz), Streaming (Auto Loader, niedrige Latenz, höhere Kosten), CDC (effizient für große, häufig aktualisierte Tabellen).

**Table Management:** Managed Tables für alle neuen Lakehouse-Daten (Standard); External Tables nur bei regulatorischem Pfad-Zwang.

**Hub-and-Spoke-Medallion:** zentraler Data Hub mit eigenen Bronze/Silver/Gold-Schichten speist Domänen, die wiederum eigene Medallion-Schichten besitzen.

**Data Governance:** Datenqualität über Constraints, Primary/Foreign Keys, Expectations, Lakehouse Monitoring — strengere Regeln in Silver/Gold als in Bronze. Unterscheidung "Data Copy" (unschädlich, Wegwerf-Kopie) vs. "Data Silo" (schädlich, sobald operative Abhängigkeiten entstehen) — Unity-Catalog-Views/OpenSharing statt Kopieren nutzen. Unity Catalog erfasst automatisch Lineage für Table-zu-Table-, Notebook-/Job- und System-Abhängigkeiten.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick (verweist auf `Medallion Architecture.md` für die dortigen SQL-Beispiele, siehe Abschnitt 1 oben).

---

## 9. Phase 7: Infrastructure as Code

**Terraform** (empfohlen für Lakehouse-Infrastruktur): verwaltet Account- und Workspace-Ressourcen konsistent über AWS/Azure/GCP; Best Practices: modulare Muster, Remote-State mit Locking, Umgebungstrennung über State-Dateien, `.tfvars`-Parametrisierung, CI/CD-Plan-Reviews, konsistentes Tagging.

**Databricks Asset Bundles** (empfohlen für Daten-/KI-Ressourcen): deployt Jobs, Pipelines, Notebooks, ML-Modelle; Multi-Umgebungs-Deployments, Git-Integration (GitHub Actions, Azure DevOps, GitLab CI). Klare Trennung: Terraform für Infrastruktur, Bundles für Workloads.

**AWS CloudFormation:** historisch für Workspace-Deployment genutzt, heute nicht mehr bevorzugt (stattdessen Terraform).

**Deployment-Pfade (AWS):** Express-Setup (Serverless-Workspace + Trial ohne bestehenden AWS-Account) vs. bestehender AWS-Account (Databricks-direkt oder AWS-Marketplace-Billing).

**Administratives Workspace-Bootstrap:** ein administrativer Workspace je Region — nötig für Unity-Catalog-API-Zugriff, zentrales Admin-Dashboard/Security Analysis Tool, Automatisierungs-Hub.

**Deployment-Muster:** (1) Workspace-Deployment-Muster — wiederverwendbare Terraform-Module je Persona (Data-Engineering-, Analytics-, ML-, Produktions-Workspace); (2) Environment-Promotion-Muster (Dev → Staging → Prod mit Freigabe-Gates); (3) Wiederverwendbare-Module-Muster (Workspace-, Unity-Catalog-, Cluster-Policy-, Netzwerk-Modul).

Vermeiden: manuelle Workspace-Erstellung in Produktion, lokaler Terraform-State, Deployment ohne Plan-Review, "Snowflake"-Sonderkonfigurationen.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 10. Phase 8: Compute-Konfiguration

**Grundempfehlung:** Serverless Compute zuerst — keine Konfiguration nötig, immer verfügbar, sekundenschnelle Autoskalierung. Classic Compute nur bei fehlender Serverless-Unterstützung.

**Cluster-Sizing:** Überlegungen zu Workload-Typ, Datenvolumen, Performance, Autoscaling, Instance-Typ. Größenmuster: klein (2–8 Knoten, Dev/Test), mittel (8–32, Produktions-ETL/Analytics), groß (32+, Batch/ML-Training). Best Practice: mit Baseline starten und iterieren, Spot-Instanzen für fehlertolerante Workloads.

**SQL-Warehouse-Sizing:** Auto-Scaling basiert auf Query-Durchsatz, Queue-Größe, vorhergesagtem Bedarf (2-Minuten-Fenster). **Größe (XS–XL)** bestimmt Rechenleistung je Query (klein = einfache Dashboards, groß = komplexe Queries auf riesigen Datensätzen). **Anzahl** bestimmt Concurrency (Faustregel: ~10 gleichzeitige Queries je Cluster). Merksatz: "Größe erhöhen, um einzelne Queries schneller zu machen. Anzahl erhöhen, um mehr Nutzer gleichzeitig zu bedienen." Start mit Serverless-SQL-Warehouses empfohlen.

**Cluster-Policies:** für alle Organisationen empfohlen — beschränken Instance-Typen/Versionen/Größen, vereinfachen UI, begrenzen Kosten, erzwingen Compliance-Tags. Muster: Development-, Production-, ML-, Spot-Policy.

**Usage Policies:** Tags auf Serverless-Compute-Aktivität, propagieren in `system.billing.usage.custom_tags` — zur Kostenzuordnung nach Abteilung/Projekt/Umgebung.

**Monitoring:** vorgefertigte Nutzungs-Dashboards importieren, Trends nach Workspace/Nutzer/Compute-Typ, Alerts bei Budgetüberschreitung, monatliches Finance-Review.

**Zugriffskontrolle:** Standard-Installation erlaubt allen Nutzern Objekterstellung, sofern Admin die Zugriffskontrolle nicht aktiviert. Muster: Permissive, Restricted, Segregated.

**Workspace-Einstellungen (vor Produktivbetrieb prüfen):** Access/Visibility Control (Standard: aktiviert), Table Access Control (Standard: deaktiviert — stattdessen Unity Catalog empfohlen), Enforce User Isolation (Standard: deaktiviert — aktivieren gegen "No Isolation"-Cluster), Container Services (Standard: deaktiviert), Repos Git Allow Lists (Standard: deaktiviert), Exfiltration-Schutz (Download-/Export-/Clipboard-Features deaktivieren), Interactive Notebook Results Storage (aktivieren für eigenen Storage-Account).

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 11. Phase 9: Observability-Strategie

**System-Tabellen:** von Databricks gehosteter analytischer Speicher operativer Account-Daten — Billing/Nutzung, Audit-Logs, Query-History, Job-Runs, Lineage, Cluster-Events. Anwendungsfälle: Kostenoptimierung, Security-Monitoring, Performance-Analyse, Kapazitätsplanung, Governance. Beispiel-Monitoring-Queries (konzeptionell genannt): teuerste Queries, fehlgeschlagene Jobs, seit >24h ungenutzte Cluster, häufig genutzte Tabellen/Volumes, Lineage kritischer Produktionstabellen.

**Job-/Pipeline-Monitoring:** Echtzeit-Alerting bei kritischen Fehlschlägen, Trendanalyse, SQL-Alert-basierte Anomalieerkennung, SLA-Monitoring, Abhängigkeitsverfolgung. Pipeline-spezifisch: Lakeflow-Observability, Checkpoints, Aktualitätsfenster, Fehlerbehandlung.

**Spark-Performance-Monitoring:** Query Profile (Serverless/SQL Warehouses) für Ausführungspläne/Skew/Optimierungsempfehlungen; Spark UI (Classic Compute) für Stage-Ausführung, Skew über Task-Dauer, Speicher-/Spill-/Executor-/Shuffle-Metriken.

**Datenqualitäts-Monitoring:** Lakehouse Monitoring mit Time-Series-/Snapshot-Monitoren, statistischem Profiling, Drift-Erkennung — Fokus auf Gold-Tabellen (Geschäftskritikalität), Schema-Compliance in Silver, Ingestion-Verifikation in Bronze.

**Model-Monitoring:** Endpoint-Gesundheit, Invocation-Metriken, Inference-Tabellen, Modellversions-Nutzung, Fehlerraten; Muster: Echtzeit-Alerting, SLA-Compliance, Drift-Erkennung, A/B-Testing, automatisierte Rollbacks.

**Third-Party-Integration:** Datadog, Prometheus, AWS CloudWatch, AWS CloudTrail.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.

---

## 12. Phase 10: High Availability und Disaster Recovery

**Control-Plane-HA:** seit Anfang 2025 arbeiten Kerndienste multi-zonal — automatisches Failover, **15-Minuten-RTO**, **0 RPO** bei zonalen Ausfällen (gilt für Regionen mit mehreren AZs; Single-AZ-Regionen behandeln zonale Ausfälle als regionale Ausfälle).

**Compute-Plane-HA:** Classic Compute — Subnetze über mind. 2 (empfohlen 3) AZs deployen, automatische Knotenverteilung, Job-Retries mit exponentiellem Backoff. Serverless Compute — automatisches Multi-Zone-Failover ohne Zusatzkonfiguration.

**DR-Überlegungen je Ebene:** Clients (Failover-URLs, DNS/Load-Balancer-Update), Code/Workspace-Objekte (IaC + Git + CI/CD in beiden Regionen), Identitäten (SCIM-Sync, Identitätsföderation), Unity Catalog (Terraform/Skripte für Metastore, Metadaten, OpenSharing in Primär-/Sekundärregion), Daten (geo-redundante Replikation, **Delta Deep Clone** für regionsübergreifende Tabellenreplikation), Streaming-Endpoints (Checkpoint-Synchronisation/Dual Writes).

**DR-Design-Patterns:** Active-Passive (periodische Replikation, manuelles/automatisiertes Failover), Active-Active (beide Regionen produktiv, kontinuierliche Replikation, Load Balancing, höhere Kosten/besseres RTO), Backup and Restore (günstigste, aber höchste RTO/RPO — für unkritische Workloads).

**RTO/RPO-Beispielanforderungen:** kritische Workloads RTO < 1h / RPO < 15 Min (Active-Active/-Passive mit kontinuierlicher Replikation); wichtige Workloads RTO < 4h / RPO < 1h (Active-Passive, stündliche Replikation); Standard-Workloads RTO < 24h / RPO < 24h (Backup and Restore).

**DR-Testing:** vierteljährliche vollständige Failover-Tests, monatliche Runbook-Validierung, kontinuierliche automatisierte Komponententests, Tabletop-Übungen. Best Practice: außerhalb der Spitzenzeiten testen, tatsächliche RTO/RPO messen, Teams schulen.

Keine eigenen Code-Beispiele in dieser Datei — reiner Konzeptüberblick.
