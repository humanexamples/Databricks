# Phase 1: Account- und Identitätsstrategie gestalten

Teil der [Production Planning](Uebersicht.md)-Reihe. Behandelt administrative Grenzen, Rollenstrategien, Identitätsmanagement und Single Sign-On für produktionsreife Databricks-Deployments.

## Abschnittsübersicht

1. [Administrative Grenzen verstehen](#grenzen)
2. [Administrative Rollenstrategie gestalten](#rollen)
3. [Identitätsstrategie gestalten](#identitaet)
4. [Cross-Domain-Identitätsanforderungen](#cross-domain)
5. [Single-Sign-On-Strategie gestalten](#sso)
6. [Automatic Identity Management](#auto-identity)
7. [Just-in-Time Provisioning](#jit)
8. [Empfehlungen](#empfehlungen)
9. [Ergebnisse der Phase](#ergebnisse)
10. [Quelle](#quelle)

---

## <a id="grenzen">1. Administrative Grenzen verstehen</a>

Vier bewusst getrennte administrative Ebenen:

- **Account-Ebene:** Mandantenweite Administration und gemeinsame Dienste, einschließlich Identitätsföderation, Workspace-Management und Billing.
- **Workspace-Ebene:** Operative Grenze für Team-Workloads mit workspace-spezifischen Kontrollen.
- **Data-Governance-Ebene:** Verwaltet über Unity Catalog für zentrale Governance im gesamten Account.
- **Compute-Plane-Ebene:** Steuert Workload-Ausführung und Netzwerkpfad-Governance.

**Kernprinzip des geschichteten Sicherheitsmodells:** „Keine einzelne Ebene ist für sich genommen ausreichend. Administratoren sollten vermeiden, Schutzmaßnahmen nur auf eine Grenze zu konzentrieren" — Kontrollen sollten über Account-, Workspace-, Data-Governance- und Compute-Plane-Ebene hinweg implementiert werden, um Flexibilität bei gleichzeitiger Absicherung zu bieten.

## <a id="rollen">2. Administrative Rollenstrategie gestalten</a>

### Globale Admin-Rollen

| Rolle | Geltungsbereich | Verantwortlichkeiten |
|---|---|---|
| Account Admin | Account-weit | Einstellungen, Billing, Identitätskonfiguration, Workspace-Erstellung, Unity-Catalog-Metastores, Cloud-Ressourcen |
| Workspace Admin | Einzelner Workspace | Identitäten, Zugriffskontrolle, Einstellungen, Features, Compute-Policies |

### Feature-spezifische Admin-Rollen

| Rolle | Geltungsbereich | Verantwortlichkeiten |
|---|---|---|
| Metastore Admin | Unity-Catalog-Metastore | Storage von Unity-Catalog-Objekten verwalten, Daten zentral über Workspaces hinweg verwalten |
| Marketplace Admin | Account-weit | Marketplace-Provider-Profil und -Listings verwalten |
| Billing Admin | Account-weit | Budgets einsehen, Serverless-Nutzungsrichtlinien verwalten |

### Design-Patterns für administrative Rollen

- **Zentralisierte Administration** — geeignet für kleine Organisationen.
- **Föderierte Administration** — geeignet für große Organisationen.
- **Getrennte Zuständigkeiten (Segregated Duties)** — geeignet für regulierte Branchen.

### Best Practices

- „Account-Admin-Rechte auf zwei bis drei vertrauenswürdige Personen beschränken."
- Workspace Admins für das Tagesgeschäft einsetzen.
- Metastore-Admin-Rollen entsprechend dem Governance-Modell vergeben.
- Audit-Logging über alle Ebenen hinweg aktivieren.
- Verantwortlichkeiten und Eskalationsverfahren dokumentieren.
- Gruppen statt einzelner Nutzer für Admin-Rollen verwenden.
- Trennung der Zuständigkeiten zwischen administrativen Accounts durchsetzen.

## <a id="identitaet">3. Identitätsstrategie gestalten</a>

### Identitätstypen

- **Users:** „Nutzeridentitäten, die von Databricks erkannt und über E-Mail-Adressen repräsentiert werden."
- **Service Principals:** Identitäten für Jobs, automatisierte Tools, Skripte, Apps, CI/CD-Plattformen.
- **Groups:** Sammlungen von Identitäten zur Verwaltung des Zugriffs auf Workspaces und Daten.

### Vorteile der Identitätsföderation

- Zentrale Verwaltung von Nutzern, Gruppen und Service Principals auf Account-Ebene.
- Vereinfachte Administration, da Zuweisung über mehrere Workspaces hinweg möglich ist.
- „Einheitliche Governance: eine Single Source of Truth für Identitätsmanagement über alle Workspaces hinweg."
- Automatisierte Provisionierung über Automatic Identity Management oder SCIM.

**Wichtiger Hinweis:** „Databricks aktiviert Identitätsföderation standardmäßig für alle neuen Workspaces, und sie kann nicht deaktiviert werden."

## <a id="cross-domain">4. Cross-Domain-Identitätsanforderungen berücksichtigen</a>

**Behandelte Szenarien:**

- E-Mail-Domain vs. Zugriffsdomain (unterschiedliche Adressen für Kommunikation vs. Authentifizierung).
- Fusionierte Organisationen mit konsolidierten Databricks-Accounts.
- Multi-Brand-Unternehmen mit separaten Domains auf einer gemeinsamen Plattform.

**Best Practices:**

- E-Mail-Adressen korrekt in SCIM-Attribut-Mappings abbilden.
- Authentifizierungs-Flows für alle Domains vor dem Produktivbetrieb testen.
- Domain-Mapping-Konfigurationen dokumentieren.
- Sicherstellen, dass der Identity Provider Multi-Domain-Szenarien unterstützt.

## <a id="sso">5. Single-Sign-On-Strategie gestalten</a>

### Protokollwahl

| Protokoll | Anwendungsfall | Unterstützte Provider |
|---|---|---|
| OIDC (OpenID Connect) | Moderne Authentifizierung, API-Integration, für neue Deployments empfohlen | Microsoft Entra ID, Okta, Google Workspace, OneLogin |
| SAML 2.0 | Enterprise-SSO, Legacy-Systeme | Microsoft Entra ID, Okta, PingFederate, ADFS |

**Design-Überlegungen:** Multifaktor-Authentifizierung im Identity Provider aktivieren; Notfallzugriff für Ausfälle des Identity Providers einplanen.

**AWS-spezifische Option:** Für Organisationen ohne unternehmensweiten Identity Provider unterstützt Databricks „Sign in with Google" und „Sign in with Microsoft" als Social-SSO-Optionen (OAuth 2.0/OpenID Connect). Einmalige Passcodes per E-Mail sind ebenfalls verfügbar.

**Best Practices:** SSO mit MFA nutzen, um Authentifizierung zu zentralisieren und Passwort-Risiken zu reduzieren; SSO-Konfiguration mit Testnutzern vor der Durchsetzung testen; Attribut-Mappings für E-Mail, Vor- und Nachname korrekt konfigurieren; Durchsetzung erst nach gründlichem Testen aktivieren; Wartungsfenster und Failover des Identity Providers einplanen; Notfallzugriff konfigurieren, um Aussperrungen zu vermeiden.

## <a id="auto-identity">6. Nutzer über Automatic Identity Management provisionieren</a>

**Fähigkeiten:** direkte Synchronisation von Nutzern, Service Principals, Gruppen und verschachtelten Gruppen; der Identity Provider dient als Source of Truth mit automatischer Änderungsübernahme; „vereinfachte Konfiguration: reduziert den administrativen Aufwand gegenüber SCIM"; erweiterte Features inkl. verschachtelter Gruppen und Service Principals aus Microsoft Entra ID.

**Best Practices:** Automatic Identity Management als Standard für Identitätssynchronisation nutzen; verschachtelte Gruppen zur Vereinfachung der Berechtigungsverwaltung nutzen; Service Principals statt Nutzerkonten für automatisierte Workloads verwenden; die Gruppenstruktur des Identity Providers dokumentieren.

**Alternative:** Wird der Identity Provider von Automatic Identity Management nicht unterstützt, SCIM verwenden.

## <a id="jit">7. Just-in-Time Provisioning verstehen</a>

**JIT-Ablauf:**

1. Nutzer authentifiziert sich über den SSO-Identity-Provider.
2. Databricks prüft auf einen bestehenden Account.
3. Existiert kein Account, provisioniert Databricks einen neuen Account anhand der Attribute des Identity Providers.
4. Der Nutzer erhält sofortigen Zugriff auf zugewiesene Workspaces.

**Vorteile:** automatisiertes Onboarding ohne manuelle Kontoerstellung; reduzierter administrativer Aufwand; konsistente Provisionierung aus dem Identity Provider; verbesserte Nutzererfahrung durch sofortigen Zugriff.

**Design-Überlegungen:** Methoden der Workspace-Zuweisung planen (manuell vs. automatisiert gruppenbasiert); Standardberechtigungen für neu provisionierte Nutzer definieren; sicherstellen, dass der Identity Provider akkurate Attribute liefert.

**Wichtiger Hinweis:** „JIT Provisioning ist standardmäßig für Accounts aktiviert, die nach dem 1. Mai 2025 erstellt wurden."

## <a id="empfehlungen">8. Empfehlungen zu Account und Identität</a>

**Empfohlene Praktiken:**

- Authentifizierung via SSO auf Account-Ebene mit dem Identity Provider.
- MFA im Identity Provider nutzen.
- SCIM oder Automatic Identity Management zur Synchronisation verwenden.
- JIT Provisioning für automatisiertes Onboarding aktivieren.
- Account-Admin-Nutzer auf 2–3 vertrauenswürdige Personen beschränken.
- Trennung der Zuständigkeiten durchsetzen.
- Workspace Admins entsprechend der Organisationsstruktur einschränken.
- OAuth-Authentifizierung für Service Principals nutzen.
- Service Principals für administrative Aufgaben und Produktions-Workloads verwenden.
- Administrative Operationen mit Terraform o. ä. automatisieren.
- Administrative Rollen, Verantwortlichkeiten und Eskalationsverfahren dokumentieren.
- Gruppen statt einzelner Nutzer für Admin-Rollen verwenden.

**Anhand der Anforderungen zu bewerten:** Cross-Domain-Identitätsanforderungen berücksichtigen, falls zutreffend; Granularität administrativer Rollen gegen operative Komplexität abwägen; Notfallzugriffsverfahren berücksichtigen; Wartung und Failover des Identity Providers einplanen.

## <a id="ergebnisse">9. Ergebnisse der Phase</a>

Nach Abschluss dieser Phase sollten vorliegen:

- Entworfene administrative Rollenstrategie.
- Definierte Identitätsföderationsstrategie mit Account-first-Provisionierung.
- Entworfene SSO-Strategie mit Protokollwahl und MFA-Anforderungen.
- Definierte Nutzerprovisionierungsstrategie.
- Identifizierte Cross-Domain-Identitätsanforderungen.
- Dokumentierte administrative Verantwortlichkeiten und Eskalationsverfahren.
- Service-Principal-Strategie für automatisierte Workloads.

**Nächste Phase:** Phase 2 — Workspace-Strategie gestalten (siehe [02 Workspace-Strategie.md](02%20Workspace-Strategie.md)).

## <a id="quelle">10. Quelle</a>

- https://docs.databricks.com/aws/en/lakehouse-architecture/deployment-guide/account-setup

**Stand:** 2026-08-21.
