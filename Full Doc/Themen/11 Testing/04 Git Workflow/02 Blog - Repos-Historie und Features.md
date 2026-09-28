# Blog: Repos-Historie und Features

Kuratierte Zusammenfassung von vier historischen Databricks-Blogartikeln zur Entwicklung von Databricks Repos (heute „Git Folders"): Produktionsreife für Data Science, GA-Ankündigung, Konfliktauflösung, und OAuth-2.0-Support für Service Principals. Teil der [Testing](../Uebersicht.md)-Reihe. Blog-Inhalte, keine normative Referenzdokumentation — für die aktuelle, vollständige Referenz siehe [Developers/Git Folders (Repos)](../../Developers/Git%20Folders%20%28Repos%29/).

## Abschnittsübersicht

1. [Produktionsreife Data Science mit Repos (2021)](#produktionsreif)
2. [Databricks Repos jetzt allgemein verfügbar (2021)](#ga)
3. [Neue Konfliktauflösung: Merge, Rebase und Pull](#konfliktaufloesung)
4. [OAuth 2.0 Git-Credential-Support für Service Principals (GA)](#oauth)
5. [Quelle](#quelle)

---

## <a id="produktionsreif">1. Produktionsreife Data Science mit Repos (2021)</a>

**Kernproblem:** Data-Science-Teams standen vor der Wahl zwischen Flexibilität für Exploration und der für Produktion nötigen Striktheit — zwang zur Übergabe fertiger Arbeit an Engineering-Teams mit anderen Tech-Stacks, was den gesamten Lösungsaufbau faktisch wiederholte.

**Lösung:** Databricks Repos als Teil des Next-Generation Data Science Workspace — „Repository-Ebenen-Integration mit Git-Providern, die es jedem Mitglied des Datenteams erlaubt, Best Practices zu befolgen." Unterstützte Provider: GitHub, Bitbucket, GitLab, Azure DevOps.

**Enterprise-Fähigkeiten:** Allow Lists (URL-Präfixe für genehmigte Repositories) und Secret Detection (erkennt Klartext-Secrets im Quellcode vor dem Commit).

**Dreistufiger CI/CD-Workflow:** Development (Feature-Branches in persönlichen Ordnern) → Review & Testing (CI/CD aktualisiert Testumgebungen automatisch, führt Validierungstests aus) → Production (nach PR-Merge aktualisiert CI/CD die Produktionsumgebung).

## <a id="ga">2. Databricks Repos jetzt allgemein verfügbar (2021)</a>

Ankündigung vom 7. Oktober 2021: General Availability von Databricks Repos, gleichzeitig ein neues „Files"-Feature in Public Preview.

**Gelöstes Problem:** Data-Engineering- und ML-Praktiker mussten zuvor „durch mehrere Dateien, Schritte und UIs navigieren, um einfach Code zu reviewen und zu committen" — zeitaufwendig und fehleranfällig.

**Files in Repos (Public Preview):** ermöglicht die Arbeit mit Nicht-Notebook-Dateien — Python-Quell-/Bibliotheksdateien, Konfigurationsdateien, Umgebungsspezifikationen, kleine Datendateien — importierbar, lesbar und editierbar „wie in jedem lokalen Dateisystem."

**Hauptvorteile:** Code-Wiederverwendung (Python-/R-Module per Import statt separater Notebooks/Cluster-Libraries); Umgebungsmanagement (`requirements.txt` versioniert neben Code, `%pip install -r requirements.txt`).

## <a id="konfliktaufloesung">3. Neue Konfliktauflösung: Merge, Rebase und Pull</a>

Ankündigung von Git-Merge- und -Rebase-Fähigkeiten mit integrierter Konfliktauflösung direkt in der Repos-UI.

**Merge-Strategie:** bewahrt die vollständige Commit-Historie ohne Umschreiben — empfohlen für Teams, die neu in kollaborativen Git-Workflows sind, da kein Force-Push nötig ist.

**Rebase-Strategie:** erzeugt eine sauberere Projekthistorie durch Umstrukturieren von Commits, schreibt dabei aber die Historie um — kann in bestimmten Szenarien Komplikationen verursachen.

„Jede Operation ist ein Weg, die Commit-Historie eines Branches in einen anderen zu integrieren; der einzige Unterschied ist die dafür genutzte Strategie."

**Konfliktauflösung in der UI:** manuelle Bearbeitung im Code-Editor (Konflikt-Marker entfernen, „Mark as Resolved"); automatisierte Schnellauflösung („Keep all current changes" / „Take all incoming changes", farblich markiert); Abbrechen-Funktion zum vollständigen Zurücksetzen. Nach Auflösung aller Konflikte: „Continue Merge" bzw. „Continue Rebase".

## <a id="oauth">4. OAuth 2.0 Git-Credential-Support für Service Principals (GA)</a>

Ankündigung der allgemeinen Verfügbarkeit von OAuth-2.0-Git-Credential-Support für Service Principals mit GitHub und Azure DevOps — adressiert Sicherheitsbedenken bei Personal Access Tokens (PATs) durch kurzlebige, automatisch erneuerte OAuth-Tokens.

**Probleme mit PATs:** lange Gültigkeitsdauer (Wochen/Monate) erzeugt operative Reibung; Nutzer kopieren PATs oft manuell, was Spuren in Zwischenablagen/Dokumenten hinterlassen kann; GitHub-Classic-PATs gelten „für jedes Repo, auf das der Nutzer Zugriff hat" — potenzielle Privilege Escalation; Azure DevOps unterstützt keine PAT-Generierung für Service Principals.

**OAuth-Vorteile:** automatische Token-Erneuerung (keine manuelle Ablaufverwaltung mehr); Repository-scoped Zugriffskontrollen; kurzlebige Access Tokens (8 Stunden bei GitHub); verbesserte administrative Aufsicht.

**Implementierung:** GitHub über GitHub-App-Verbindung in den Service-Principal-Einstellungen; Azure DevOps über OpenID-Connect-(OIDC)-federated Credentials mit Microsoft Entra ID — reduziert Setup-Zeit „von Stunden auf wenige Minuten."

**Explizit abgelehnte Alternativen:** SSH-Authentifizierung und GPG-Commit-Signierung — würden das Hochladen privater Schlüssel zu Databricks erfordern, „ähnlich dem Speichern eines PAT", mit denselben Sicherheitsnachteilen plus zusätzlichem Risiko bei kompromittierten SSH-Keys.

*Diese Inhalte sind in der aktuellen Form bereits in [Developers/Git Folders (Repos)/02 Git-Integration konfigurieren.md](../../Developers/Git%20Folders%20%28Repos%29/02%20Git-Integration%20konfigurieren.md) (Provider-Setup) und [Developers/Git Folders (Repos)/03 Git-Operationen.md](../../Developers/Git%20Folders%20%28Repos%29/03%20Git-Operationen.md) (Merge/Rebase/Konflikte) referenziert.*

## <a id="quelle">5. Quelle</a>

- https://www.databricks.com/blog/2021/03/16/productionize-data-science-with-repos-on-databricks.html
- https://www.databricks.com/blog/2021/10/07/databricks-repos-is-now-generally-available.html
- https://www.databricks.com/blog/new-support-conflict-resolution-repos-merge-rebase-and-pull
- https://www.databricks.com/blog/oauth-20-git-credential-support-service-principals-now-generally-available

**Stand:** 2026-08-21.
