# Phase 10: High Availability und Disaster Recovery gestalten

Teil der [Production Planning](Uebersicht.md)-Reihe — letzte Phase. Behandelt Control- und Compute-Plane-HA, DR-Überlegungen je Architektur-Ebene, DR-Design-Patterns, RTO-/RPO-Anforderungen und DR-Testing-Strategie.

## Abschnittsübersicht

1. [High-Availability-Strategie gestalten](#ha-strategie)
2. [Disaster-Recovery-Strategie gestalten](#dr-strategie)
3. [DR-Design-Patterns](#dr-patterns)
4. [RTO- und RPO-Anforderungen](#rto-rpo)
5. [DR-Testing-Strategie gestalten](#dr-testing)
6. [Empfehlungen](#empfehlungen)
7. [Ergebnisse der Phase](#ergebnisse)
8. [Quelle](#quelle)

---

## <a id="ha-strategie">1. High-Availability-Strategie gestalten</a>

### Control-Plane-HA

Die Databricks-Control-Plane umfasst zahlreiche Dienste, von „Frontend-Hosting und Authentifizierung bis Cluster-Management und Endpoint-Deployment." Seit Anfang 2025 arbeiten die Kerndienste multi-zonal.

**Kerneigenschaften:** „Automatisches Failover": Dienste failovern automatisch zu gesunden Zonen; „15-Minuten-RTO": Failover ist typischerweise innerhalb von 15 Minuten abgeschlossen; „0 RPO": kein Datenverlust bei zonalen Ausfällen; „Multi-Zone-Abdeckung": gilt für Cloud-Regionen mit mehreren Availability Zones.

**Hinweis:** Regionen mit nur einer Zone behandeln zonale Ausfälle als regionale Ausfälle.

### Compute-Plane-HA

**Classic Compute:** Workspace-Subnetze über mindestens 2 Availability Zones deployen (3 empfohlen); Databricks verteilt Cluster-Knoten automatisch über Zonen; Job-Retries mit exponentiellem Backoff für transiente Fehler konfigurieren; Availability-Zone-Gesundheit überwachen und Workloads bei Beeinträchtigung umverteilen.

**Serverless Compute:** „Serverless Compute bietet automatisch Multi-Zone-Failover" — keine zusätzliche Konfiguration nötig, Workloads werden bei Zonenausfällen automatisch umverteilt.

**Best Practices:** Serverless Compute für automatisches Multi-Zone-Failover nutzen; bei Classic Compute sicherstellen, dass Subnetze mehrere Availability Zones umfassen; automatische Job-Retries für transiente Fehler konfigurieren; Failover-Verfahren regelmäßig testen; Zonen-Gesundheitsmetriken überwachen und Kapazitätsplanung anpassen.

## <a id="dr-strategie">2. Disaster-Recovery-Strategie gestalten</a>

### DR-Überlegungen je Ebene

- **Clients:** Fähigkeit, auf Failover-Workspace-URLs zu wechseln; DNS- oder Load-Balancer-Konfiguration für automatisches Failover aktualisieren.
- **Code und Workspace-Objekte:** IaC/Terraform für Plattforminfrastruktur-Deployment nutzen; Versionskontrolle für allen Code inkl. Notebooks; Deployment an beiden Standorten via CI/CD; Deployment in die sekundäre Region automatisieren.
- **Identitäten:** Nutzer, Service Principals, Gruppen verwalten; SCIM-Synchronisation auf Account-Ebene nutzen; Identitätsföderation sichert konsistenten regionsübergreifenden Zugriff.
- **Unity Catalog:** Terraform oder Skripte zum Deployment/Kopieren der Infrastruktur nutzen; Metadaten (Tabellendefinitionen, ACLs etc.) via Terraform/Skripte kopieren; OpenSharing-Konfiguration via Terraform/Skripte kopieren; Metastores in Primär- und Sekundärregion deployen.
- **Daten:** External/Managed Data — geo-redundante Replikation; Delta-Tabellen — Delta Deep Clone für regionsübergreifende Replikation; Landing Zones — Replikation in die Sekundärregion.
- **Streaming-Endpoints:** Checkpoint-Informationen über Regionen hinweg synchronisieren; Dual Writes oder Checkpoint-Replikation konfigurieren.

## <a id="dr-patterns">3. DR-Design-Patterns</a>

**Active-Passive-DR:** Primärregion bedient den gesamten Produktionsverkehr; Sekundärregion im Standby für Failover; Daten werden periodisch repliziert (stündlich, täglich); manuelles oder automatisiertes Failover bei Primärausfall.

**Active-Active-DR:** „Beide Regionen bedienen Produktionsverkehr"; Daten werden kontinuierlich oder nahezu in Echtzeit repliziert; Load Balancing über Regionen hinweg; höhere Kosten, aber bessere Performance und RTO.

**Backup and Restore:** regelmäßige Backups in die Sekundärregion; manueller Restore-Prozess bei Primärausfall; niedrigste Kosten, aber höchste RTO und RPO; geeignet für unkritische Workloads.

## <a id="rto-rpo">4. RTO- und RPO-Anforderungen</a>

**Recovery Time Objective (RTO):** akzeptable Dauer des Geschäftsausfalls; bestimmt Anforderungen an die Failover-Automatisierung; beeinflusst Infrastrukturinvestitionen.

**Recovery Point Objective (RPO):** „Wie viel Datenverlust ist akzeptabel?"; bestimmt die Replikationsfrequenz; beeinflusst Backup- und Replikationsstrategie.

**Beispielanforderungen:**

- **Kritische Workloads:** RTO < 1 Stunde, RPO < 15 Minuten (Active-Active oder Active-Passive mit kontinuierlicher Replikation).
- **Wichtige Workloads:** RTO < 4 Stunden, RPO < 1 Stunde (Active-Passive mit stündlicher Replikation).
- **Standard-Workloads:** RTO < 24 Stunden, RPO < 24 Stunden (Backup and Restore).

## <a id="dr-testing">5. DR-Testing-Strategie gestalten</a>

**Testing-Muster:** vierteljährliche DR-Tests (vollständiges Failover in die Sekundärregion, Validierung aller Systeme); monatliche Runbook-Validierung (Überprüfung und Aktualisierung der Verfahren); kontinuierliche automatisierte Tests (regelmäßiges Testen einzelner Komponenten); Tabletop-Übungen (Simulation von DR-Szenarien mit Stakeholdern).

**Best Practices:** detaillierte DR-Runbooks mit Schritt-für-Schritt-Verfahren dokumentieren; außerhalb von Spitzenzeiten testen; Datenintegrität nach Failover validieren; tatsächliche RTO und RPO während der Tests messen; Verfahren anhand der Testergebnisse aktualisieren; Betriebsteams in DR-Verfahren schulen.

## <a id="empfehlungen">6. Empfehlungen</a>

**Empfohlene Praktiken:**

- IaC (Terraform) nutzen, um Infrastruktur in beiden Regionen zu deployen.
- Classic Compute über mehrere Availability Zones für HA deployen.
- Serverless Compute für automatisches Multi-Zone-Failover nutzen.
- Geo-redundante Replikation für Rohdaten und Quellen implementieren.
- Delta Deep Clone nutzen, um kritische Tabellen über Regionen hinweg zu replizieren.
- SCIM-Synchronisation für konsistentes Identitätsmanagement nutzen.
- RTO- und RPO-Anforderungen für alle kritischen Workloads dokumentieren.
- DR-Failover-Verfahren wo möglich automatisieren.
- DR-Verfahren regelmäßig testen (mindestens vierteljährlich).
- Detaillierte DR-Runbooks dokumentieren.

**Anhand der Anforderungen zu bewerten:**

- Active-Active-DR für geschäftskritische Workloads mit strikten RTO-Anforderungen erwägen.
- DR-Investition gegen Geschäftskritikalität und RTO-/RPO-Anforderungen abwägen.
- Multi-Cloud-DR für höchste Resilienz erwägen (höchste Komplexität und Kosten).

## <a id="ergebnisse">7. Ergebnisse der Phase</a>

Nach Abschluss dieser Phase — und damit der gesamten [Production-Planning](Uebersicht.md)-Reihe — sollten vorliegen: entworfene High-Availability-Strategie (Multi-Zone-Deployment für Classic Compute); Verständnis der Control-Plane-HA-Eigenschaften; entworfene Disaster-Recovery-Strategie; definierte RTO-/RPO-Anforderungen für kritische Workloads; gewählte DR-Design-Patterns; definierte DR-Testing-Strategie mit regelmäßigem Testplan; definierter IaC-Ansatz für Primär- und Sekundärregion; entworfene Datenreplikationsstrategie; entworfene Identitätsmanagement-Strategie; dokumentierte DR-Runbooks mit detaillierten Verfahren.

## <a id="quelle">8. Quelle</a>

- https://docs.databricks.com/aws/en/lakehouse-architecture/deployment-guide/ha-dr

**Stand:** 2026-08-21.
