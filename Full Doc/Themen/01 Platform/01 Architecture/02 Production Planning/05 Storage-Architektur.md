# Phase 5: Storage-Architektur gestalten

Teil der [Production Planning](Uebersicht.md)-Reihe. Behandelt Workspace-Storage, Unity-Catalog-Storage-Objekttypen, Storage-Isolationsmuster, Authentifizierung, Verschlüsselung, Netzwerksicherheit und Hub-and-Spoke-Storage.

## Abschnittsübersicht

1. [Zwei Storage-Arten](#storage-arten)
2. [Workspace-Storage-Architektur](#workspace-storage)
3. [Unity-Catalog-Storage-Architektur](#uc-storage)
4. [Storage-Isolationsmuster](#isolation)
5. [Multi-Region-Storage-Design](#multi-region)
6. [Zugriffs- und Authentifizierungsstrategie](#auth)
7. [Verschlüsselungsstrategie](#verschluesselung)
8. [Storage-Netzwerksicherheit](#netzwerksicherheit)
9. [Hub-and-Spoke-Storage-Design](#hub-spoke)
10. [Empfehlungen](#empfehlungen)
11. [Ergebnisse der Phase](#ergebnisse)
12. [Quelle](#quelle)

---

## <a id="storage-arten">1. Zwei Storage-Arten</a>

- **Databricks-verwalteter Storage (Default Storage):** Storage im von Databricks besessenen Cloud-Account.
- **Kundenverwalteter Storage:** Storage im eigenen Cloud-Account des Kunden.

## <a id="workspace-storage">2. Workspace-Storage-Architektur</a>

### Kernzwecke

Der Workspace-Storage-Account/-Bucket dient mehreren Funktionen:

- Default-Unity-Catalog-Catalog-Storage für den Workspace.
- Interne Plattformdaten (MLflow-Experimente, Registry-Modelle, Lakeflow-Pipelines, Cloud Fetch).

### Best Practices

- Unity-Catalog-External-Locations nutzen, um den Default-Workspace-Storage zu überschreiben.
- Web-App-Uploads einschränken, sofern nicht zwingend nötig.
- Den Workspace-Root-Bucket nicht für Produktionskundendaten nutzen.
- Risiken und Workarounds im Zusammenhang mit Root-Bucket-Nutzung verstehen.

### DBFS-Migrationsstrategie

Für bestehende Deployments:

- **Strukturierte Daten:** DBFS-Tabellen zu Unity-Catalog-Managed-Tables migrieren.
- **Unstrukturierte Daten:** Dateien zu Unity-Catalog-Volumes für POSIX-artigen Zugriff migrieren.
- **Workspace Files:** Workspace-Storage weiterhin für Notebooks, Bibliotheken, Cluster-Logs nutzen.

## <a id="uc-storage">3. Unity-Catalog-Storage-Architektur</a>

### Storage-Objekttypen

- **Managed Objects:** Managed-Storage-Locations spezifizieren Cloud-Object-Storage-Locations für Managed Tables und Volumes, zuordenbar auf Metastore-, Catalog- oder Schema-Ebene. Untergeordnete Locations überschreiben übergeordnete Definitionen.
- **External Objects:** speichern Daten in External Locations, die ein Storage Credential mit einem Cloud-Container (S3-Bucket, Azure-Container, GCS-Bucket) verknüpfen.
- **Foreign Objects:** „Ein Foreign Catalog spezifiziert eine Verbindung zu einem externen Datensystem für den Zugriff auf entfernte Tabellen und Schemas."

### AWS-Storage-Architektur

Ein Unity-Catalog-Metastore umfasst: null oder ein S3-Bucket für Default-Managed-Table-Storage; null oder mehr Buckets auf Catalog-/Schema-Ebene; null oder mehr S3-Buckets für External Tables. Cross-Account-IAM-Rollen mit Trust-Beziehungen ermöglichen Databricks, Rollen für den Datenzugriff zu übernehmen.

## <a id="isolation">4. Storage-Isolationsmuster</a>

- **Nach Umgebung:** getrennte Container für Development, Staging und Production verhindern versehentlichen Zugriff auf Produktionsdaten.
- **Nach Geschäftsbereich:** vollständige Datentrennung erfordert getrennte Container und Storage Credentials je Geschäftsbereich.
- **Nach Datendomäne:** Data-Mesh-Architekturen profitieren von domänenspezifischen Containern mit dedizierten Credentials.

## <a id="multi-region">5. Multi-Region-Storage-Design</a>

Wichtige Überlegungen: Storage in derselben Region wie den Metastore deployen (Performance); Databricks-managed OpenSharing für regionsübergreifendes Sharing nutzen; Häufigkeit und Volumen des regionsübergreifenden Zugriffs bewerten; Egress-Kosten berücksichtigen.

**Kritische Warnung:** „Geteilte Tabellen nicht als External Tables in mehr als einem Metastore registrieren."

## <a id="auth">6. Zugriffs- und Authentifizierungsstrategie</a>

### AWS-Authentifizierungsarchitektur

1. IAM-Rollen mit Trust-Policies erstellen, die Databricks erlauben, Rollen zu übernehmen.
2. IAM-Policies anhängen, die S3-Berechtigungen für bestimmte Buckets/Präfixe gewähren.
3. IAM-Rollen-ARNs als Storage Credentials registrieren.
4. External Locations unter Nutzung der Storage Credentials erstellen.

### Best Practices

Getrennte IAM-Rollen für unterschiedliche Buckets/Domänen nutzen; Least-Privilege-Berechtigungen anwenden; AWS CloudTrail für Audit-Logging aktivieren; Bucket-Policies als zusätzliche Sicherheitsebene nutzen.

## <a id="verschluesselung">7. Verschlüsselungsstrategie</a>

### Optionen

- **Databricks-verwaltete Schlüssel (Standard):** „Standardmäßig werden Daten im Ruhezustand mit der Verschlüsselung des Cloud-Providers und einem Databricks-verwalteten Schlüssel verschlüsselt."
- **Kundenverwaltete Schlüssel:** zwei Hauptzwecke — (1) Control-Plane- und Managed-Services-Verschlüsselung (AI Search, Query-Ergebnisse, Code, Secrets); (2) Compute- und Data-Plane-Verschlüsselung für bestimmte Dienste.

### Muster

- **Stark regulierte Umgebungen:** kundenverwaltete Schlüssel sowohl für Control Plane als auch Compute-/Data-Plane-Verschlüsselung nutzen.
- **Standard-Enterprise-Deployments:** Databricks-verwaltete Schlüssel für die meisten Workloads nutzen, kundenverwaltete Schlüssel für Produktionsumgebungen mit sensiblen Daten reservieren.
- **Multi-Tenant-Deployments:** separate kundenverwaltete Schlüssel je Geschäftsbereich oder Umgebung erwägen.

## <a id="netzwerksicherheit">8. Storage-Netzwerksicherheit</a>

**Muster:** S3-Bucket-Policies nutzen, die den Zugriff auf bestimmte VPCs oder VPC-Endpoints beschränken.

**Best Practices:** Storage-Zugriff auf bestimmte virtuelle Netzwerke/Subnetze beschränken; VPC-Endpoints für private Konnektivität nutzen; Storage-Service-Logging für Zugriffs-Auditing aktivieren; Netzwerkregeln konfigurieren, bevor breite Berechtigungen vergeben werden.

## <a id="hub-spoke">9. Hub-and-Spoke-Storage-Design</a>

- **Hub-Storage:** organisationsweite, gemeinsam genutzte Daten (Kundenstammdaten, Referenzdaten, kuratierte Datensätze).
- **Spoke-Storage:** domänenspezifische Daten im Besitz von Geschäftsbereichen.
- **Storage-Trennung:** Hub- und Domänen-Catalogs nutzen dedizierten Storage mit getrennten Credentials.
- **Managed Tables:** bevorzugt für strukturierte Lakehouse-Daten.
- **Volumes:** für Landing-, Roh- oder unstrukturierte Daten.
- **External Tables:** zum Teilen von Daten mit Nicht-OpenSharing-Systemen.

**Best Practices:** Hub-Storage für organisationsweit gemeinsam genutzte Daten; Spoke-Storage für geschäftsbereichsspezifische Daten; getrennte Storage Credentials und External Locations; Databricks-managed OpenSharing für Hub-zu-Spoke-Sharing; Daten-Eigentümerschaft und Lineage dokumentieren.

**Hinweis:** Metastore-Storage ist inzwischen optional und wird nicht empfohlen.

## <a id="empfehlungen">10. Empfehlungen</a>

**Empfohlene Praktiken:**

- Unity-Catalog-Managed-Tables nutzen, ohne Bucket-Ebenen-Storage-Zugriff zu gewähren.
- Storage-Locations explizit auf Catalog-/Schema-Ebene definieren.
- Storage nach Umgebung mit unterschiedlichen Containern trennen.
- Volumes für Unity-Catalog-gesicherte POSIX-artige Dateipfade nutzen.
- Legacy-Muster wie Cloud-Storage-Mounting und Instance Profiles vermeiden.
- Kundenverwaltete Verschlüsselungsschlüssel für mehr Kontrolle bewerten.
- Databricks-managed OpenSharing für Cross-Cloud-/-Region-Sharing nutzen.

**Zu vermeidende Praktiken:**

- Root-Bucket (DBFS) für Kundendatenspeicherung.
- Produktionsdaten auf DBFS.
- External-Table-Registrierung über Regionen/Metastores hinweg.
- Direkter Storage-Ebenen-Zugriff für Nutzer.
- Verlass auf Default-Metastore-Ebenen-Storage-Locations.

## <a id="ergebnisse">11. Ergebnisse der Phase</a>

Nach Abschluss dieser Phase sollten dokumentiert sein: Workspace-Storage-Architektur (kundenverwaltet vs. Databricks-verwaltet); Unity-Catalog-Storage-Architektur (Managed vs. External vs. Foreign Objects); Storage-Isolationsstrategie (Umgebung, Geschäftsbereich oder Domäne); Authentifizierungsstrategie (IAM-Rollen, Access Connectors oder Service Accounts); gewählte Verschlüsselungsstrategie; Storage-Netzwerksicherheitsmuster; Multi-Region-Storage-Überlegungen (falls zutreffend); bewertetes Hub-and-Spoke-Design; DBFS-Migrationsstrategie für bestehende Deployments.

**Nächste Phase:** Phase 6 — Delta-Lake-Architektur gestalten (siehe [06 Delta Lake Architektur.md](06%20Delta%20Lake%20Architektur.md)).

## <a id="quelle">12. Quelle</a>

- https://docs.databricks.com/aws/en/lakehouse-architecture/deployment-guide/storage

**Stand:** 2026-08-21.
