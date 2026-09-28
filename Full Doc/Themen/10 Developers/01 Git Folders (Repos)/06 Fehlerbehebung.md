# Fehlerbehebung

Bekannte Fehler und deren Ursachen/Lösungen für Git Folders — Authentifizierungsfehler, Repository-State-Probleme und unerwartetes Verhalten. Teil der [Git Folders (Repos)](01%20Grundlagen.md)-Reihe.

## Abschnittsübersicht

1. [Authentifizierungsfehler](#auth-fehler)
2. [Repository-State-Fehler](#state-fehler)
3. [Unerwartetes Verhalten](#unerwartet)
4. [Wiederherstellbarkeit von Dateien](#wiederherstellung)
5. [Support kontaktieren](#support)
6. [Quelle](#quelle)

---

## <a id="auth-fehler">1. Authentifizierungsfehler</a>

### Ungültige Credentials

**Ursachen/Lösungen:** Git-Integrationseinstellungen unter Settings > Linked accounts auf Username und Token prüfen; korrekte Git-Provider-Auswahl bestätigen; sicherstellen, dass PAT/App-Passwort die nötigen Repository-Rechte hat; bei aktiviertem SSO Tokens für SSO autorisieren; Credentials über die Kommandozeile testen:

```bash
git clone https://<username>:<token>@github.com/<org>/<repo>.git
```

### SSL-Verbindungsfehler

**Fehlermeldung:** „Secure connection to [link] could not be established because of SSL problems"

**Ursache:** Netzwerkkonnektivitätsproblem oder TLS-Zertifikatsproblem der Git-Infrastruktur der Organisation.

**Vor Support-Kontakt zu sammeln:** Git-Server-URL; ob der Server ein selbstsigniertes oder privates CA-Zertifikat nutzt; ob der Fehler weitere Workspace-Nutzer betrifft.

## <a id="state-fehler">2. Repository-State-Fehler</a>

### Detached-HEAD-Zustand

**Was es ist:** Der Repository-HEAD zeigt direkt auf einen Commit statt auf einen Branch — Git kann Änderungen dann auf keinem Branch nachverfolgen.

**Wann es auftritt:** bei Löschung des Remote-Branches versucht Databricks eine Wiederherstellung, indem uncommittete Änderungen auf den Default-Branch angewendet werden — bei Konflikten entsteht ein Detached HEAD; oder wenn ein Nutzer/Service Principal über die Update-Repo-API einen Tag auscheckt.

**Wiederherstellung:** „Create branch" klicken, um vom aktuellen Commit einen neuen Branch zu erstellen, ODER „Select branch", um einen bestehenden Branch auszuchecken. Änderungen committen und pushen, um sie zu erhalten, oder über das Kebab-Menü unter „Changes" verwerfen.

### Inkonsistenter Repository-State

**Fehlermeldung:** „There was a problem with deleting folders. The repo could be in an inconsistent state and re-cloning is recommended."

**Lösung:** Repository löschen und neu klonen, um den State zurückzusetzen.

### Notebook-Namenskonflikte

**Fehlermeldungen:** „Cannot perform Git operation due to conflicting names"; „A folder cannot contain a notebook with the same name as a notebook, file, or folder (excluding file extensions)."

**Ursache:** unterschiedliche Dateiendungen bei identischem Namen erzeugen Konflikte (z. B. `notebook.ipynb` und `notebook.py`).

**Lösung:** das konfliktbehaftete Notebook, die Datei oder den Ordner lokal oder im Remote-Repository umbenennen.

## <a id="unerwartet">3. Unerwartetes Verhalten</a>

### Timeout-Fehler

**Ursache:** Klonen großer Repositories oder Branch-Checkout-Operationen überschreiten Zeitlimits.

**Wichtiger Hinweis:** Operationen können nach dem Timeout im Hintergrund abgeschlossen werden.

**Schritte:** einige Minuten warten, dann den Git Folder aktualisieren, um zu prüfen, ob die Operation abgeschlossen ist; bei hoher Workspace-Last nach Lastabnahme erneut versuchen; bei großen Repositories Sparse Checkout nutzen, um nur benötigte Dateien einzubeziehen.

### 404-Fehler

**Wann es auftritt:** beim Öffnen von Nicht-Notebook-Dateien.

**Lösung:** einige Minuten warten und erneut versuchen — es besteht eine kurze Verzögerung zwischen Workspace-Aktivierung und der Übernahme der Konfiguration durch die Webapp.

### Notebooks erscheinen ohne Nutzeränderungen als geändert

**Ursache:** unterschiedliche Zeilenenden zwischen Systemen — Databricks nutzt Linux-Style (LF), Windows nutzt CRLF.

**Diagnose:** die Datei `.gitattributes` prüfen.

**Lösungen:** die Einstellung `* text eol=crlf` entfernen, sofern kein Windows genutzt wird; auf Windows-Systemen die Einstellung zu `* text=auto` ändern (Git speichert intern Linux-Zeilenenden, checkt aber plattformspezifisch aus).

**Bei bereits mit Windows-Zeilenenden committeten Dateien:**

1. Ausstehende Änderungen bereinigen.
2. `.gitattributes` entsprechend aktualisieren.
3. Änderung committen.
4. `git add --renormalize` ausführen und alle Änderungen committen/pushen.

## <a id="wiederherstellung">4. Wiederherstellbarkeit von Dateien</a>

| Aktion | Wiederherstellbar? | Wiederherstellungsmethode |
|---|---|---|
| Löschen über den Workspace-Browser | Ja | Trash-Ordner |
| Neue Datei über den Git-Dialog verwerfen | Ja | Trash-Ordner |
| Geänderte Datei über den Git-Dialog verwerfen | Nein | — |
| Hard Reset bei uncommitteten Änderungen | Nein | — |
| Hard Reset bei neuen uncommitteten Dateien | Nein | — |
| Branch-Wechsel über den Git-Dialog | Ja | Remote-Git-Repo |
| Commit-/Push-Operationen über den Git-Dialog | Ja | Remote-Git-Repo |
| PATCH-Operationen auf `/repos/id` über die API | Ja | Remote-Git-Repo |

## <a id="support">5. Support kontaktieren</a>

Bei der Fehlermeldung anzugeben: exakter Fehlermeldungstext; Name des Git-Providers und Sichtbarkeitsstatus des Repositories (privat/öffentlich); ob das Problem alle oder nur bestimmte Nutzer betrifft; bereits versuchte Troubleshooting-Schritte.

## <a id="quelle">6. Quelle</a>

- https://docs.databricks.com/aws/en/repos/errors-troubleshooting

**Stand:** 2026-08-21.
