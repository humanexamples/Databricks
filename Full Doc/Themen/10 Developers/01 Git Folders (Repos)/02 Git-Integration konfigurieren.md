# Git-Integration konfigurieren

Behandelt Voraussetzungen, das Hinzufügen von Git-Credentials (individuell und für Gruppen), Commit-Identität, Netzwerkkonnektivität und Sicherheitsfeatures für Git Folders — sowie die provider-spezifischen Schritte zur Token-Erstellung. Teil der [Git Folders (Repos)](01%20Grundlagen.md)-Reihe.

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [Git-Credentials hinzufügen](#credentials-hinzufuegen)
3. [Git-Credential für eine Gruppe (Rolle)](#gruppen-credential)
4. [Mehrere Credentials je Nutzer](#mehrere-credentials)
5. [Commit-Identität konfigurieren](#commit-identitaet)
6. [Netzwerkkonnektivität konfigurieren](#netzwerk)
7. [Sicherheitsfeatures](#sicherheit)
8. [Provider-spezifische Token-Erstellung](#provider-tokens)
9. [Quelle](#quelle)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

- Git Folders im Workspace aktiviert (Standardeinstellung).
- Zugriff auf ein Git-Provider-Konto (GitHub, GitLab, Azure DevOps, Bitbucket, AWS CodeCommit).
- Personal Access Token (PAT) oder OAuth-Credentials für private Repos oder Schreiboperationen.
- Hinweis: „Öffentliche Remote-Repositories lassen sich ohne Git-Credentials klonen."

## <a id="credentials-hinzufuegen">2. Git-Credentials hinzufügen</a>

**Schritte:**

1. Nutzername oben in der Leiste anklicken → **Settings**.
2. **Linked accounts** anklicken.
3. **Add Git credential** anklicken.
4. Git-Provider aus dem Dropdown wählen.
5. Bei OAuth-Providern den Authentifizierungs-Flow abschließen.
6. Bei PAT-basierten Providern: E-Mail im Feld „Git provider email" eintragen.
7. PAT im Feld „Token" einfügen.
8. Bei aktiviertem GitHub-SAML-SSO: Token für SSO autorisieren.
9. **Save** anklicken.

Alternative: Verwaltung über die Databricks Repos API.

## <a id="gruppen-credential">3. Git-Credential für eine Gruppe (Rolle)</a>

**Voraussetzungen:** `Manage`-Berechtigung auf der Gruppe; Workspace nutzt rollenbasierte Zugriffskontrolle (RBAC).

**Schritte:** Settings > Identity and access > Groups → Gruppe öffnen → Tab „Git integration" → Git-Provider wählen → PAT eingeben oder via OAuth verbinden → Git-Username und Git-E-Mail für die Gruppe setzen → Save.

**Kapazität:** Jede Gruppe kann bis zu 10 Git-Credentials je Workspace haben.

**Token-Berechtigungen für Gruppen:** Databricks empfiehlt Read-only-Tokens für Gruppen-Credentials — diese verhindern Push, Branch-Löschung und Commit-Autorenschaft unter der Gruppenidentität. Schreibzugriff nur gewähren, wenn Nutzer als Gruppe committen/pushen müssen. Hinweis: „Da die Workspace-UI Commit und Push in einer einzigen Aktion durchführt, erfordert das Committen als Gruppe Schreibzugriff."

**Zugrundeliegendes Git-Konto:** Best Practice ist, das Gruppen-Credential mit einem dedizierten Service-/Bot-Konto zu hinterlegen (z. B. ein GitHub Machine User oder ein GitLab Deploy Token), statt mit dem Token eines einzelnen Nutzers — vermeidet Kopplung des Git-Zugriffs an den Lebenszyklus einer Einzelperson und erlaubt unabhängige Token-Rotation.

**Azure DevOps:** „Die Git-Integration unterstützt keine Microsoft-Entra-ID-Tokens — es muss ein Azure-DevOps-Personal-Access-Token verwendet werden."

## <a id="mehrere-credentials">4. Mehrere Credentials je Nutzer</a>

Nutzer können mehrere Credentials für unterschiedliche Provider/Konten speichern, ohne wechseln zu müssen.

**Credential für Git Folders auswählen:** Git Folder öffnen → Tab „Git settings" → unter „Git credential" das Credential aus dem Dropdown wählen → Save.

**Standard-Credentials:** Jeder Git-Provider unterstützt genau ein Standard-Credential je Nutzer. Databricks nutzt das Standard-Credential automatisch für Jobs, Repos-API-Operationen und Git-Folder-Operationen (wenn kein spezifisches Credential gewählt wurde). Das erste erstellte Credential für einen Provider wird automatisch zum Standard. Ändern über: User Settings > Linked accounts → Kebab-Menü neben dem Credential → „Set as default".

**Einschränkungen:** Jobs, die ein Nicht-Standard-Credential für einen Provider benötigen, müssen einen Service Principal verwenden; die Databricks-GitHub-App erlaubt nur ein verknüpftes Credential; jeder Nutzer kann maximal 10 Git-Credentials haben.

## <a id="commit-identitaet">5. Commit-Identität konfigurieren</a>

Bestimmt, wie Commits beim Git-Provider erscheinen (Attribution, Profilbild, Contribution-Tracking).

**Funktionsweise:** Die E-Mail des Credentials wird zur Autoren-E-Mail (`GIT_AUTHOR_EMAIL`/`GIT_COMMITTER_EMAIL`) aller Commits; der Username wird zum Committer-Namen (`GIT_AUTHOR_NAME`/`GIT_COMMITTER_NAME`). Ohne angegebene E-Mail nutzt Databricks den Git-Username als E-Mail, was korrekte Commit-Attribution verhindern kann. Wurden Credentials vor Einführung der E-Mail-Konfiguration erstellt, ist das E-Mail-Feld standardmäßig der Username — sollte auf die echte E-Mail-Adresse aktualisiert werden.

**Bei aktiver Rolle (RBAC):** persönliche Commits nutzen das persönliche Git-Credential (Attribution an den Nutzer); Commits als Rolle nutzen das Rollen-Credential (Attribution an die Rollenidentität beim Git-Provider).

**Verknüpfte GitHub-Credentials:** Die Databricks-GitHub-App konfiguriert E-Mail und Git-Identität automatisch; bei falscher Identität: benötigte Berechtigungen genehmigen oder Konto neu verknüpfen.

## <a id="netzwerk">6. Netzwerkkonnektivität konfigurieren</a>

„Git Folders benötigen Netzwerkkonnektivität zum Git-Provider. Die meisten Konfigurationen funktionieren ohne zusätzliches Setup über das Internet." Zusätzliches Setup ist nötig bei: IP-Allowlists beim Git-Provider; selbstgehosteten Git-Servern (GitHub Enterprise, Bitbucket Server, GitLab Self-Managed); privat gehosteten Netzwerken.

Hinweis: „Git Folders mit Git-CLI-Zugriff führen UI-basierte Git-Operationen auf Serverless Compute aus" — Workspace-Admins müssen sicherstellen, dass Serverless Compute den Git-Provider erreichen kann.

**IP-Allowlists konfigurieren:** die Databricks-Control-Plane-NAT-IP-Adresse der Region ermitteln (Seite „Databricks clouds and regions") und diese IP zur Allowlist des Git-Servers hinzufügen.

**Private Git-Server:** siehe [05 Administration und private Netzwerke.md](05%20Administration%20und%20private%20Netzwerke.md) oder das Databricks-Account-Team kontaktieren.

## <a id="sicherheit">7. Sicherheitsfeatures</a>

**Git-Credentials verschlüsseln:** AWS KMS mit kundenverwalteten Schlüsseln zur Verschlüsselung von Git-PATs nutzen.

**Git-URL-Allowlists:** Workspace-Admins können zugängliche Remote-Repositories einschränken, um Code-Exfiltration zu verhindern und die Nutzung genehmigter Repositories durchzusetzen.

Einrichtung: Settings > Development → Option „Git URL allow list permission" wählen:

- **Disabled (keine Einschränkungen)**
- **Restrict Clone, Commit & Push to Allowed Git Repositories** — beschränkt alle Operationen auf Allowlist-URLs.
- **Only Restrict Commit & Push to Allowed Git Repositories** — beschränkt nur Schreiboperationen; Clone/Pull unbeschränkt.

Kommagetrennte Liste von URL-Präfixen eintragen (case-insensitives Präfix-Matching, keine Wildcards). Beispiele: `https://github.com` (alle GitHub-Repositories), `https://github.com/CompanyName` (nur diese Organisation), `https://dev.azure.com/CompanyName`.

**Warnung:** keine URLs mit Nutzernamen oder Auth-Tokens eintragen — diese könnten global repliziert werden und Nutzer blockieren. Eine neue Liste überschreibt die bestehende Allowlist; Änderungen brauchen bis zu 15 Minuten.

**Zugriffskontrolle:** nur im Premium-Plan oder höher verfügbar. Berechtigungsstufen: `NO PERMISSIONS`, `CAN READ` (nur ansehen), `CAN RUN` (ansehen + ausführen), `CAN EDIT` (ansehen + ausführen + ändern), `CAN MANAGE` (volle Kontrolle inkl. Teilen/Löschen) — gelten für den gesamten Inhalt des Git Folders.

**Audit Logging:** protokolliert Erstellen/Aktualisieren/Löschen von Git Folders, Auflisten von Git Folders im Workspace, Synchronisation zwischen Git Folders und Remote-Repository.

**Secrets Detection:** Git Folders scannen Code automatisch vor Commits auf exponierte Credentials (z. B. AWS Access Key IDs mit `AKIA`-Präfix und weitere sensible Muster).

## <a id="provider-tokens">8. Provider-spezifische Token-Erstellung</a>

### GitHub

**Databricks-GitHub-App (empfohlen):** nutzt OAuth 2.0 mit verschlüsseltem Repository-Traffic, erneuert Tokens automatisch, beschränkt Zugriff auf bestimmte Repositories. GitHub Enterprise Server erfordert stattdessen PATs; Enterprise Managed Users können keine GitHub Apps installieren und müssen PATs nutzen.

Setup: User Settings > Linked accounts → „Add Git credential" → Provider GitHub → „Link Git account" → Databricks-GitHub-App autorisieren → App auf gewünschten Repositories installieren (optional auf bestimmte Repos beschränken). Access Tokens laufen nach 8 Stunden ab, Refresh Tokens nach 6 Monaten Inaktivität — verschlüsselbar mit kundenverwalteten Schlüsseln.

**Classic Personal Access Token:** GitHub Settings → Developer settings → Personal access tokens → Tokens (classic) → neues Token mit Scope `repo` generieren (zusätzlich `workflow` bei Nutzung von GitHub Actions) → in Databricks Settings > Linked accounts einfügen. Bei SSO: Token muss für SAML autorisiert werden.

**Fine-Grained Personal Access Token:** GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens → neues Token mit Name/Beschreibung erstellen → Repository-Zugriff und Berechtigungen wählen (Contents: „Read and write", Resource Owner: die GitHub-Organisation, Standard-Ablauf: 30 Tage) → in Databricks Settings > Linked accounts einfügen.

### GitLab

Gilt für GitLab.com und GitLab Self-Managed: Nutzer-Icon → „Preferences" → „Personal access tokens" → „Add new token" → Namen und Scopes wählen → Token erstellen und in Databricks Settings > Linked accounts einfügen. Alternative: Project Access Tokens für feingranularen Zugriff auf bestimmte Projekte.

### AWS CodeCommit

Voraussetzung: der zugehörige IAM-Nutzer benötigt Lese-/Schreibrechte auf dem Repository. HTTPS-Git-Credentials gemäß AWS-CodeCommit-Doku erstellen, das Passwort (nicht den Username) kopieren und in Databricks Settings > Linked accounts einfügen.

### Azure DevOps Services

**Personal Access Token** — Anwendungsfall: Databricks und Azure-DevOps-Repository in unterschiedlichen Microsoft-Entra-ID-Tenants. Netzwerkanforderung: Der Microsoft-Entra-ID-Service-Endpoint muss sowohl vom privaten als auch vom öffentlichen Subnetz des Databricks-Workspace erreichbar sein.

Schritte: bei dev.azure.com anmelden → User-Settings-Icon → „Personal Access Tokens" → neues Token erstellen (Organisation wählen, Ablaufdatum setzen, Scope „Full access" oder passende Berechtigungen) → Token kopieren → in Databricks Settings > Linked accounts einfügen → im Feld „Git provider username or email" die für die DevOps-Organisation genutzte E-Mail-Adresse eintragen.

### Bitbucket

Unterstützt: Bitbucket Cloud und Bitbucket Data Center.

**API Token (empfohlen):** benötigte Scopes `read:repository:bitbucket` und `write:repository:bitbucket`. Scoped API Token gemäß Bitbucket-Doku generieren, in Databricks Settings > Linked accounts hinzufügen.

**Access Token:** für CI/CD konzipiert, empfohlen für Service Principals — bietet scoped Authentifizierung für Repositories, Projekte oder Workspaces.

**App Password (Deprecation):** „Atlassian phast App Passwords für Bitbucket aus, vollständige Abschaffung zum 9. Juni 2026 geplant" — Migration zu API-Tokens empfohlen. Bei Nutzung: den Bitbucket-Username im Feld „Git provider username" eintragen.

### Weitere Git-Provider

Für nicht gelistete Provider kann der Versuch, GitHub auszuwählen und einen PAT des jeweiligen Providers einzugeben, funktionieren — ist aber nicht garantiert.

### Service Principals

Service Principals lassen sich für Git-Credentials konfigurieren und sind „die empfohlene Wahl für Jobs, CI/CD-Pipelines und andere automatisierte Workflows" (siehe [04 CI-CD und Automatisierung.md](04%20CI-CD%20und%20Automatisierung.md)).

## <a id="quelle">9. Quelle</a>

- https://docs.databricks.com/aws/en/repos/repos-setup
- https://docs.databricks.com/aws/en/repos/get-access-tokens-from-git-provider

**Stand:** 2026-08-21.
