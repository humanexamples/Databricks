# Jobs mit Git-Quellcode

Remote-Git-Repositories als Quelle für Lakeflow-Jobs, inkl. Sparse Checkout für große Repositories und Konfliktvermeidung durch Release-Branch-Strategien. Teil der [Testing](../Uebersicht.md)-Reihe. Ergänzt [Developers/Git Folders (Repos)](../../Developers/Git%20Folders%20%28Repos%29/) um die job-spezifische Nutzung von Git als Code-Quelle.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Wichtige Einschränkung](#einschraenkung)
3. [Konfigurationsschritte](#konfiguration)
4. [Rollenbasierte Ausführung](#rollen)
5. [Sparse Checkout für große Repositories](#sparse-checkout)
6. [API-Implementierung](#api)
7. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

Tasks in Lakeflow Jobs können Quellcode direkt aus Remote-Git-Repositories abrufen. Das Feature unterstützt Notebooks, Python-Skripte, SQL-Dateien und dbt-Projekte. Wichtig: „Alle Tasks eines Jobs müssen denselben Commit im Remote-Repository referenzieren" — sichert Konsistenz über einen einzelnen Job-Lauf hinweg.

**Unterstützte Task-Typen:** Notebooks, Python-Skripte, SQL-Dateien, Data-Build-Tool-(dbt)-Projekte.

## <a id="einschraenkung">2. Wichtige Einschränkung</a>

Tasks, die für Remote-Git-Repositories konfiguriert sind, können nicht in Workspace-Dateien schreiben. Stattdessen müssen temporäre Daten in ephemeren Storage auf dem Driver-Knoten geleitet werden, dauerhafte Daten in Volumes oder Tabellen.

## <a id="konfiguration">3. Konfigurationsschritte</a>

Zugriff auf den Git-Konfigurationsdialog über das **Job details**-Panel unter **Git**, oder während des Task-Setups. Anzugebende Details:

1. **Git-Repository-URL** — die Remote-Repository-Adresse.
2. **Git-Provider** — aus dem Dropdown wählen.
3. **Git-Referenz** — Branch, Tag oder Commit-Identifier angeben.
4. **Referenz-Typ** — festlegen, ob es sich um einen Branch, Tag oder Commit-Hash handelt.

Nur genau ein Referenz-Typ ist anzugeben: **Branch**-Beispiel `main`; **Tag**-Beispiel `release-1.0.0`; **Commit**-Beispiel `e0056d01`.

Bei fehlenden Credentials: Git-Integration vor dem Fortfahren konfigurieren (siehe [Developers/Git Folders (Repos)/02 Git-Integration konfigurieren.md](../../Developers/Git%20Folders%20%28Repos%29/02%20Git-Integration%20konfigurieren.md)).

## <a id="rollen">4. Rollenbasierte Ausführung</a>

Bei aktivierter rollenbasierter Zugriffskontrolle (RBAC) können Jobs als bestimmte Gruppe laufen. Der Job klont das Repository dann mit „dem Git-Credential der Rolle" — erfordert vorheriges Setup dieses Credentials durch einen Manager.

## <a id="sparse-checkout">5. Sparse Checkout für große Repositories</a>

### Wann einsetzen

Nur aktivieren, wenn beide Bedingungen zutreffen:

- Repository übersteigt etwa 2.500 Dateien.
- Der Ziel-Branch aktualisiert sich selten (etwa ein Commit pro Stunde oder seltener).

Sparse Checkout bei schnell wechselnden, durch automatisierte CI/CD-Workflows beeinflussten Branches vermeiden.

### Caching-Mechanismus

Databricks cacht Checkouts anhand von vier Kriterien: Workspace, Repository-URL, exakter Commit-Hash, Fingerabdruck des Sparse-Checkout-Patterns (bestimmte Ordnerpfade). Cache-Einträge bleiben bis zu einer Woche gültig. Jedes einzigartige Sparse-Pattern erzeugt einen eigenen Cache-Eintrag — potenziell erhöhte Systemlast, wenn viele Nutzer eigene Patterns definieren.

### Import-Rate-Berechnung

**Dateien pro Stunde = Job-Läufe pro Stunde × Cache-Miss-Rate × importierte Dateien je Miss**

Schwellenwerte:

- **Unter 150.000 Dateien/Stunde:** Normalbetrieb.
- **150.000–300.000 Dateien/Stunde:** verschlechterte Performance, manche Jobs können Verzögerungen oder Fehlschläge erleben.
- **Über 300.000 Dateien/Stunde:** Jobs schließen nicht zuverlässig ab.

### Best-Practice-Empfehlungen

**Pattern-Standardisierung:** „drei oder weniger gemeinsam genutzte Checkout-Patterns organisationsweit nutzen, um Cache-Treffer zu maximieren." Individuelle Team-Patterns vermeiden, da jedes zusätzlichen Overhead verursacht.

**Commit-Management:** Jobs auf stabile Release-Branches ausrichten statt auf häufig aktualisierte Branches wie `main`. „Merges in geplante Release-Fenster bündeln, damit mehrere Läufe denselben gecachten Commit teilen."

**Lastmanagement:** große Binärdateien und generierte Artefakte aus der Versionskontrolle entfernen. Trigger-Frequenz für unkritische Jobs reduzieren oder Jobs mit identischen Checkouts konsolidieren.

### Release-Branch-Strategie

Einen langlebigen Branch erstellen (z. B. `release-candidate`), der sich automatisch nach festem Zeitplan aktualisiert. Verbessert Cache-Trefferquote, da mehrere Läufe innerhalb eines Zeitfensters denselben Commit referenzieren.

**Trade-offs:** Jobs laufen gegen Code, der bis zu einer Stunde hinter dem Main-Branch liegt. Schlägt der Release-Schnitt fehl, laufen Jobs gegen den vorherigen Commit weiter (Alerting hierfür empfohlen).

**GitHub-Actions-Beispiel** für stündliche Release-Branch-Schnitte (`.github/workflows/cut-release-branch.yml`):

```yaml
name: Cut Hourly Release Candidate
on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:
jobs:
  update-branch:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout main branch
        uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 0
      - name: Update release-candidate branch
        run: |
          git push origin HEAD:release-candidate --force
```

Nach dem Committen dieser Datei und einmaligem manuellem Auslösen: Jobs auf `release-candidate` ausrichten.

## <a id="api">6. API-Implementierung</a>

Sparse Checkout über die Jobs API aktivieren, mit einem `sparse_checkout`-Block innerhalb von `git_source`:

```json
{
  "git_source": {
    "git_url": "https://github.com/example/my-repo",
    "git_provider": "gitHub",
    "git_branch": "release-candidate",
    "sparse_checkout": {
      "patterns": ["src/models", "src/utils"]
    }
  }
}
```

Jeder Pattern-String repräsentiert einen relativ zum Repository-Root angegebenen Verzeichnispfad; alle Dateien innerhalb der angegebenen Verzeichnisse werden eingeschlossen.

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/jobs/git

**Stand:** 2026-08-21.
