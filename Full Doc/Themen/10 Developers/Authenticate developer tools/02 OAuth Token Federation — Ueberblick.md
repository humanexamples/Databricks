# Zugriff auf Databricks über OAuth Token Federation authentifizieren

Überblicksseite zu OAuth Token Federation für den Zugriff auf Account- und Workspace-Ressourcen mit Tokens des eigenen Identity Providers (IdP). Teil der Reihe [Authentifizierung für Entwicklerwerkzeuge](00%20Uebersicht.md).

## Abschnittsübersicht

1. [Was ist Databricks OAuth Token Federation?](#was)
2. [Warum wird es für Workloads dringend empfohlen?](#warum)
3. [Welche Federation-Typen werden unterstützt?](#typen)
4. [Wie konfiguriere ich OAuth Token Federation?](#konfig)
5. [Weiterführende Ressourcen](#ressourcen)
6. [Quelle](#quelle)

---

## <a id="was">1. Was ist Databricks OAuth Token Federation?</a>

OAuth Token Federation ermöglicht den sicheren Zugriff auf Databricks-APIs mit Tokens deiner vertrauenswürdigen Identity Provider (IdPs). Laut Doku „entfällt damit die Notwendigkeit, Databricks-Secrets wie Personal Access Tokens und Databricks-OAuth-Client-Secrets zu verwalten und zu rotieren."

Der Mechanismus: Benutzer und Service Principals tauschen **JWTs (JSON Web Tokens)** ihres Identity Providers gegen **Databricks-OAuth-Tokens**, die dann für den Zugriff auf Databricks-APIs verwendet werden.

## <a id="warum">2. Warum wird es für Workloads dringend empfohlen?</a>

OAuth Token Federation ist eine einfachere und sicherere Methode zur Authentifizierung, besonders für automatisierte Workloads:

- Der Workload authentifiziert sich bei Databricks als **Service Principal** im Databricks-Account.
- Verwendet werden **Workload-Identity-Tokens**, die von der Automatisierungsumgebung ausgestellt werden.
- Die **Databricks-SDKs und die Databricks CLI** holen diese Workload-Identity-Tokens automatisch und tauschen sie gegen Databricks-OAuth-Tokens.
- Das eliminiert das Verwalten und Rotieren von Databricks-Secrets.

## <a id="typen">3. Welche Federation-Typen werden unterstützt?</a>

Databricks unterstützt zwei Typen von Token Federation:

- **Account-weite Token Federation (Account-wide token federation)** — ermöglicht **allen Benutzern und Service Principals** im Databricks-Account den Zugriff auf Databricks-APIs mit Tokens des IdP. Zentralisiert die Token-Ausgabe-Policies im IdP und wird typischerweise **zusammen mit SCIM** eingesetzt, sodass Benutzer aus dem IdP in den Databricks-Account synchronisiert werden.

- **Workload Identity Federation** — erlaubt automatisierten Workloads **außerhalb** von Databricks den Zugriff auf Databricks-APIs **ohne Databricks-Secrets**. Die Anwendung (Workload) authentifiziert sich als Databricks-Service-Principal mit Tokens, die von der Workload-Laufzeitumgebung ausgestellt werden.

## <a id="konfig">4. Wie konfiguriere ich OAuth Token Federation?</a>

1. Entscheide, ob du **Account-weite Token Federation** oder **Workload Identity Federation** verwendest.
2. Erstelle eine **Federation Policy**. Du benötigst:
   - deine **Account-ID** (für Account-weite Token Federation),
   - die **ID des Service Principals** (für Workload Identity Federation),
   - Informationen des Werkzeugs / Providers, der die föderierten Tokens ausstellt.
3. Konfiguriere das Werkzeug bzw. den Identity Provider so, dass es sich mit föderierten Tokens bei Databricks authentifiziert. Beispiele für gängige CI/CD-IdPs: siehe [04 Workload Identity Federation in CI-CD aktivieren.md](04%20Workload%20Identity%20Federation%20in%20CI-CD%20aktivieren.md).

Details zur Policy-Erstellung: [03 Federation Policy konfigurieren.md](03%20Federation%20Policy%20konfigurieren.md).

## <a id="ressourcen">5. Weiterführende Ressourcen</a>

- [12 Unified Authentication.md](12%20Unified%20Authentication.md)
- [10 OAuth U2M — Benutzerzugriff.md](10%20OAuth%20U2M%20%E2%80%94%20Benutzerzugriff.md)
- Autorisierung von Service-Principal-Zugriff mit OAuth (OAuth M2M)

## <a id="quelle">6. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/auth/oauth-federation

**Stand:** 2026-08-28.
