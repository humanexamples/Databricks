# Phase 4: Netzwerkarchitektur gestalten

Teil der [Production Planning](Uebersicht.md)-Reihe. Behandelt Konnektivitätsmuster, Secure Cluster Connectivity, IP-Zugriffskontrolle, Data-Exfiltration-Schutz, Private Link, Serverless-Konnektivität (NCC) und die AWS-spezifische VPC-Architektur.

## Abschnittsübersicht

1. [Grundlegende Netzwerkkonzepte](#konzepte)
2. [Virtual-Private-Network-Konfiguration](#vpc-konfiguration)
3. [Secure Cluster Connectivity (SCC)](#scc)
4. [IP-Zugriffskontroll-Strategie](#ip-access)
5. [Data-Exfiltration-Schutz](#exfiltration)
6. [Private-Link-Strategie](#private-link)
7. [Serverless-Konnektivität (NCC)](#ncc)
8. [AWS-Netzwerkarchitektur](#aws-netzwerk)
9. [Netzwerksicherheitskontrollen nach Risiko](#risiko-kontrollen)
10. [Empfehlungen](#empfehlungen)
11. [Ergebnisse der Phase](#ergebnisse)
12. [Quelle](#quelle)

---

## <a id="konzepte">1. Grundlegende Netzwerkkonzepte</a>

Databricks-Networking verwaltet drei Kommunikationskanäle:

- **Inbound-Konnektivität:** Nutzerzugriff auf Admin-Console und Workspaces über UI und APIs.
- **Outbound-Konnektivität:** Serverless-Compute-Verbindungen zu Kundenressourcen.
- **Classic-Konnektivität:** sichere Verbindungen von Classic Compute zur Control Plane.

Die Netzwerksicherheitsumsetzung unterscheidet sich je Compute-Modell: Classic Compute nutzt „kundenverwaltete Cloud-Netzwerke, daher wird die Netzwerkhaltung primär über kundenverwaltete Segmentierung, Routing, private Konnektivität und Egress-Kontrollen umgesetzt." Serverless Compute setzt auf „Plattformkontrollen und Account-Ebenen-Konfigurationen, um Konnektivität zu regeln."

## <a id="vpc-konfiguration">2. Virtual-Private-Network-Konfiguration</a>

**Classic Workspaces:** Für maximale Kontrolle rät Databricks, Classic Workspaces in kundenverwalteten VPCs zu deployen — das ermöglicht „die größte Kontrolle über Netzwerktopologie, Subnetzbereiche und Security Groups."

**Serverless Compute:** Databricks verwaltet das Networking der Compute Plane. Wesentliche Features: sicheres Ingress/Egress und Network Connectivity Configurations (NCC) zur Definition von Egress-Regeln.

## <a id="scc">3. Secure Cluster Connectivity (SCC)</a>

SCC kehrt die Beziehung zwischen Control Plane und Compute um: „Jeder Cluster initiiert eine Verbindung zum SCC-Relay in der Control Plane und etabliert damit einen sicheren Kommunikationstunnel."

**Vorteile:** keine öffentlichen IP-Adressen auf Compute-Knoten; keine Inbound-Ports auf Security Groups erforderlich; vereinfachte Sicherheitshaltung; reduzierte Angriffsfläche.

**Best Practices:** für alle neuen Workspaces aktivieren (Standardeinstellung); als Baseline-Sicherheitsansatz nutzen; kompatibel mit Private Link und fortgeschrittenem Networking.

## <a id="ip-access">4. IP-Zugriffskontroll-Strategie</a>

IP Access Lists beschränken Verbindungen auf bekannte, vertrauenswürdige Adressen aus Unternehmens-VPNs oder Büronetzwerken. „Bestehende Nutzersitzungen funktionieren nicht mehr, wenn der Nutzer zu einer nicht erlaubten IP-Adresse wechselt."

**Listen-Ebenen:** Workspace-Ebene (einzelne Workspaces); Account-Ebene (alle Workspaces und die Account-Console).

**Muster:** nur Unternehmens-VPN-Zugriff; bestimmte Bürostandorte; Cloud-Provider-Netzwerke; Hybrid-Ansätze.

**Best Practices:** mit Account-Ebenen-Listen für Konsistenz starten; Workspace-Ebenen-Listen für spezifische Bedürfnisse nutzen; IP-Bereiche und Zwecke dokumentieren; Remote-Work-Szenarien einplanen; vor vollständiger Durchsetzung testen.

## <a id="exfiltration">5. Data-Exfiltration-Schutz</a>

Schutz umfasst „Absicherung des Netzwerks, Einschränkung des Routings und Hinzufügen einer Netzwerk-Firewall zur Beschränkung des Outbound-Zugriffs."

**Muster:** Netzwerksegmentierung (isolierte VPCs); Egress-Filterung (Netzwerk-Firewalls); private Konnektivität (Private Link); Einschränkung von Workspace-Features (Exports, Downloads deaktivieren).

**Best Practices:** Schutzmaßnahmen entsprechend der Datensensitivität bewerten; Private Link für sensible Umgebungen nutzen; Firewalls nur für benötigte Ziele konfigurieren; datenexfiltrierende Features deaktivieren.

## <a id="private-link">6. Private-Link-Strategie</a>

Private Link ermöglicht „private Konnektivität von den virtuellen Netzwerken der Cloud-Provider und On-Premises-Netzwerken zu den Diensten der Cloud-Provider, ohne Exposition gegenüber dem öffentlichen Internet."

**Architektur:** Front-End Private Link (Workspace-UI-/API-Zugriff); Back-End Private Link (Compute zu Control Plane).

**Best Practices:** für Workspaces mit hochsensiblen Daten deployen; sowohl Front-End als auch Back-End für maximale Isolation aktivieren; DNS-Konfiguration einplanen; Konnektivität vor Produktivbetrieb testen.

## <a id="ncc">7. Serverless-Konnektivität (NCC)</a>

Account-Admins konfigurieren Network Connectivity Configurations (NCC) in der Account-Console. „Wird eine NCC an einen Workspace angehängt, nutzt Serverless Compute in diesem Workspace die Netzwerkkonfiguration der NCC, um sichere ausgehende Verbindungen aufzubauen."

**Fähigkeiten:** stabile IPs für Firewall-Allowlisting.

**Best Practices:** getrennte NCCs je Umgebung; getrennte NCCs zur Geschäftsbereichs-Isolation; zur Kontrolle des Serverless-Egress nutzen; NCC-IP-Bereiche auf Storage-Firewalls allowlisten.

## <a id="aws-netzwerk">8. AWS-Netzwerkarchitektur</a>

### Basis-VPC-Konfiguration

**Subnetz-Anforderungen:** mindestens zwei Subnetze über unterschiedliche Availability Zones; dedizierte Subnetze für EC2-Instanzen (Spark-Cluster, SQL-Warehouses); Databricks weist jedem Knoten zwei IP-Adressen zu (Management- und Anwendungsverkehr).

**Subnetz-Größe:** jedes Workspace-Subnetz benötigt eine Netzmaske zwischen /17 und /26.

**Kapazitätstabelle:**

| VPC-CIDR | Subnetz-CIDR | Max. Knoten je Subnetz/AZ |
|---|---|---|
| ≥ /16 | /17 | 16.381 |
| ≥ /20 | /21 | 2.045 |
| ≥ /25 | /26 | 29 |

**Routentabellen-Konfiguration:** S3-Dienst (Gateway-VPC-Endpoint); Internetzugriff (`0.0.0.0/0` via NAT-Gateway).

**Interface-Typ-VPC-Endpoints:** für STS- und Kinesis-Dienste in separaten, kleineren Subnetzen (eines je AZ) deployen. Security Groups müssen Ingress von Databricks-Cluster-Security-Groups erlauben.

**S3-Endpoint-Hinweis:** Interface-Typ-S3-Endpoints sind teuer (Datentransfergebühren). „Sofern nicht aus Compliance-Gründen zwingend erforderlich, den kostenlosen Gateway-S3-VPC-Endpoint bevorzugen."

**NAT-Gateway-Konfiguration:** in separaten Subnetzen deployen. Für Hochverfügbarkeit eines je Availability Zone platzieren, mit Internetzugriff via Internet Gateway.

**Netzwerk-Firewall (optional):** in dedizierten Subnetzen (eines je AZ) für Data-Exfiltration-Schutz deployen. Routentabellen so konfigurieren, dass Cluster-Traffic durch die Firewall-Endpoints geleitet wird.

### Gemeinsame Nutzung von Netzwerkressourcen

Mehrere Workspaces können sich eine einzelne VPC teilen. Gemeinsam genutzte Ressourcen: NAT-Gateway, Netzwerk-Firewall und VPC-Endpoint-Subnetze. Jeder Workspace benötigt separate Cluster-Deployment-Subnetze.

**Hub-and-Spoke-Architektur:** eine zentrale Hub-VPC enthält Endpoints, Firewalls und Gateways. Spoke-VPCs (im selben oder in unterschiedlichen AWS-Accounts) hosten Workspace-Subnetze und verbinden sich über ein Transit Gateway.

## <a id="risiko-kontrollen">9. Netzwerksicherheitskontrollen nach Risiko</a>

Organisationen können Workspace- und Netzwerkkontrollen kombinieren, um „klare operative Grenzen zu etablieren, während gemeinsame Governance- und Plattformdienste weiterverwendet werden."

**Gestuftes Workspace-Modell:** Workloads mit höherem Risiko nutzen restriktivere Konnektivitätsumgebungen (enge VPC-/VNet-Konfiguration, genehmigte Egress-Ziele). Workloads mit geringerem Risiko laufen in weniger restriktiven Umgebungen für höhere Entwicklergeschwindigkeit.

**Kontroll-Ebenen:** Workspace-Ebene definiert, „wer was innerhalb des Workspace tun darf"; Netzwerk-Ebene definiert, „wohin Workloads sich verbinden dürfen."

## <a id="empfehlungen">10. Empfehlungen</a>

**Empfohlene Praktiken:**

- In kundenverwaltete virtuelle Netzwerke deployen.
- Mindestens /26 für Subnetze nutzen; in den meisten Fällen ist /23 erforderlich.
- Serverless-NCC an kundenverwaltete Einstellungen anpassen.
- IP Access Lists anwenden.
- Hub-and-Spoke bei mehreren Workspaces nutzen.
- Hochverfügbarkeit über Availability Zones hinweg einplanen.

**Anhand der Anforderungen zu bewerten:**

- Zusätzliche Data-Exfiltration-Schutzmaßnahmen (bei strikten Sicherheitsrichtlinien).
- Private Link für sensible Workloads.
- Netzwerk-Firewalls für Egress-Kontrolle.

## <a id="ergebnisse">11. Ergebnisse der Phase</a>

Nach Abschluss dieser Phase sollten vorliegen: Netzwerkarchitektur-Design (kundenverwaltete VPC); Secure-Cluster-Connectivity-Strategie; IP-Zugriffskontroll-Strategie; bewerteter Data-Exfiltration-Schutz; Private-Link-Strategie (falls compliance-relevant); Serverless-Konnektivitäts-Design (NCC); cloud-spezifische Netzwerkarchitektur; bewertetes Hub-and-Spoke-Modell; risikoangepasste Netzwerksicherheitskontrollen; berechnete Subnetzgrößen.

**Nächste Phase:** Phase 5 — Storage-Architektur gestalten (siehe [05 Storage-Architektur.md](05%20Storage-Architektur.md)).

## <a id="quelle">12. Quelle</a>

- https://docs.databricks.com/aws/en/lakehouse-architecture/deployment-guide/network

**Stand:** 2026-08-21.
