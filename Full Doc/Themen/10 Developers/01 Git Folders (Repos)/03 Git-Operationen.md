# Git-Operationen im Alltag

Behandelt Klonen, Branch-Management, Commit/Push/Pull, Merge- und Rebase-Operationen, Sparse Checkout sowie Team-Kollaborationsmuster mit Git Folders. Teil der [Git Folders (Repos)](01%20Grundlagen.md)-Reihe.

## Abschnittsübersicht

1. [Klonen](#klonen)
2. [Git-CLI-Zugriff (Public Preview)](#cli-zugriff)
3. [Branch-Operationen](#branches)
4. [Commit und Push](#commit-push)
5. [Pull](#pull)
6. [Merge](#merge)
7. [Merge-Konflikte lösen](#merge-konflikte)
8. [Rebase](#rebase)
9. [Reset](#reset)
10. [Sparse Checkout](#sparse-checkout)
11. [Team-Kollaboration](#kollaboration)
12. [Rollenbasiertes Committen](#rollen-commit)
13. [Löschen](#loeschen)
14. [API-Verwaltung](#api)
15. [Quelle](#quelle)

---

## <a id="klonen">1. Klonen</a>

**Über die UI:** **Create > Git folder** in der Workspace-Sidebar. Der Dialog benötigt: Repository-URL (Format `https://example.com/organization/project.git`), Git-Provider-Auswahl, Ordnername für den Workspace-Storage, optional Sparse-Checkout-Modus für große Repositories.

**Über das Web Terminal:**

```bash
cd /Workspace/Users/<your-email>/<project>
git clone <remote-url>
```

Voraussetzung: `CAN MANAGE`-Berechtigung auf den übergeordneten Ordnern sowie konfigurierte Workspace-Git-Credentials.

## <a id="cli-zugriff">2. Git-CLI-Zugriff (Public Preview)</a>

CLI-fähige Git Folders erlauben das Ausführen von Standard-Git-Befehlen wie `git stash`, `git rebase -i` und Force Pushes auf Serverless Compute.

**Voraussetzungen:** Serverless Compute (Environment Version 5+) oder Classic Compute (Databricks Runtime 17.0+); Preview-Feature muss vom Workspace-Admin aktiviert werden; Netzwerkkonnektivität zum Git-Provider muss geprüft sein; Repository-Größenlimit von 10.000 Dateien während der Public Preview.

**Einschränkung:** „Git-URL-Allowlists gelten für Git-Operationen, die über die Databricks-UI ausgeführt werden, werden aber nicht für Git-Befehle durchgesetzt, die direkt über die Git-CLI ausgeführt werden."

## <a id="branches">3. Branch-Operationen</a>

**Erstellen:** im Git-Dialog **Create Branch** wählen, Namen angeben, Basis-Branch festlegen, **Create** klicken.

**Wechseln:** über das Branch-Dropdown. „Uncommittete Änderungen auf dem aktuellen Branch werden übernommen und erscheinen als uncommittete Änderungen auf dem neuen Branch, sofern sie nicht mit Code auf dem neuen Branch kollidieren." **Warnung:** Beim Wechseln können Workspace-Assets gelöscht werden, wenn der neue Branch diese nicht enthält — beim Zurückwechseln neu erstellte Assets erhalten neue IDs und URLs.

## <a id="commit-push">4. Commit und Push</a>

Commit-Nachricht eingeben, **Commit & Push** klicken, um das Remote-Repository zu aktualisieren. Wichtige Einschränkung: „Notebook-Outputs sind standardmäßig nicht in Commits enthalten, wenn Notebooks im Source-File-Format (`.py`, `.scala`, `.sql`, `.r`) gespeichert sind."

## <a id="pull">5. Pull</a>

Ruft Remote-Änderungen ab und aktualisiert Notebooks automatisch. Wichtig: „Git-Operationen, die vorgelagerte Änderungen pullen, löschen den Notebook-State."

## <a id="merge">6. Merge</a>

Die UI implementiert `git merge`, um Commit-Historien zusammenzuführen. Für Standard-Merges ist kein Force Push nötig.

## <a id="merge-konflikte">7. Merge-Konflikte lösen</a>

Die Git-Folders-UI zeigt konfliktbehaftete Dateien mit Auflösungsoptionen: manuelle Bearbeitung der konfliktbehafteten Zeilen; **Keep all current changes**; **Take all incoming changes**; Abbrechen-Funktion zum Neustart. Konflikt-Marker entfernen und **Mark As Resolved** wählen.

## <a id="rebase">8. Rebase</a>

Wendet `git rebase` an, um Commits auf dem Ziel-Branch erneut anzuwenden (lineare Historie). Die UI führt nach dem Rebase `git commit` und `git push --force` aus. **Vorsicht:** „Rebase schreibt die Commit-Historie um, was Versionierungsprobleme für Mitarbeiter verursachen kann, die im selben Repo arbeiten."

## <a id="reset">9. Reset</a>

Entspricht funktional `git reset --hard` kombiniert mit `git push --force` — ersetzt Branch-Inhalt und -Historie durch den Zustand eines anderen Branches. **Kritische Warnung:** „Beim Reset gehen alle uncommitteten und committeten Änderungen sowohl in der lokalen als auch der Remote-Version des Branches verloren."

## <a id="sparse-checkout">10. Sparse Checkout</a>

Klont nur eine Teilmenge der Verzeichnisse über Cone-Patterns — adressiert Repository-Größenlimits. Standard-Pattern umfasst Root-Dateien, keine Unterverzeichnisse. Syntax-Beispiel: `parent/child/grandchild` bezieht rekursiv das `grandchild`-Verzeichnis plus Dateien in den Elternpfaden ein.

**Wichtige Einschränkung:** „Ausschluss-Verhalten (`!`) wird in der Git-Cone-Pattern-Syntax nicht unterstützt."

**Pattern-Änderungen:** Entfernen von Ordnern löscht diese, sofern keine uncommitteten Änderungen bestehen; Hinzufügen von Ordnern bezieht diese ohne zusätzliches Pull ein; uncommittete Änderungen verhindern Pattern-Ausschlüsse.

## <a id="kollaboration">11. Team-Kollaboration</a>

Empfohlener Workflow: „Jedes Teammitglied hat seinen eigenen, auf das Remote-Git-Repository gemappten Git Folder, in dem es auf einem eigenen Entwicklungs-Branch arbeitet."

**Kritische Einschränkung:** „Nur ein Nutzer führt Git-Operationen auf jedem Git Folder aus. Führen mehrere Nutzer Git-Operationen auf demselben Ordner aus, kann das Branch-Management-Probleme verursachen."

Sharing-Konfiguration umfasst die Option **Copy link to create Git folder**, mit der Mitarbeiter in ihren eigenen Workspace-Ordner klonen können.

## <a id="rollen-commit">12. Rollenbasiertes Committen</a>

Zwei Ansätze beim Committen unter einer aktiven Rolle:

- **User-Identity-Ansatz:** mit persönlichen Credentials committen; Ordner entsprechend teilen — erfordert Zugänglichkeit des Ordners unter beiden Identitäten.
- **Role-Identity-Ansatz:** Klonen, Autorenschaft und Committen als Rolle — erfordert ein Rollen-Credential mit Schreibzugriff. Trade-off: Attribution auf Rollenebene statt individueller Identifikation.

## <a id="loeschen">13. Löschen</a>

Rechtsklick auf den Git Folder → **Move to Trash** → Aktion bestätigen für dauerhaftes Entfernen.

## <a id="api">14. API-Verwaltung</a>

Programmatische Git-Folder-Verwaltung über die „Repos API reference" in der Databricks-Dokumentation.

## <a id="quelle">15. Quelle</a>

- https://docs.databricks.com/aws/en/repos/git-operations-with-repos

**Stand:** 2026-08-21.
