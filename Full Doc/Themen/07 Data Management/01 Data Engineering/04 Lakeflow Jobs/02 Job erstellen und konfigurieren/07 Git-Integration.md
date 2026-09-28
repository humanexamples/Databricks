# Git mit Lakeflow Jobs nutzen

Task-Typen mit Remote-Git-Unterstützung: Notebooks, Python-Skripte, SQL-Dateien, dbt-Projekte. Alle Tasks eines Jobs referenzieren denselben Commit — bei Laufbeginn erstellt Databricks einen Snapshot des angegebenen Branches/Commits, sodass alle Tasks dieselbe Codeversion nutzen. Die Run-Details zeigen die zugehörige Commit-SHA.

**Wichtig:** Mit Remote-Git konfigurierte Tasks können nicht in Workspace-Dateien schreiben — temporäre Daten müssen auf ephemeren Speicher am Driver-Node, persistente Daten in ein Volume oder eine Tabelle geschrieben werden.

## Git-Repository vs. Git-Ordner

Git-Ordner (ein mit einem Repository synchronisierter Workspace-Ordner) erfordern manuelles Synchronisieren. Ein direkt referenziertes Remote-Git-Repository zieht dagegen bei jedem Job-Lauf automatisch den neuesten Stand. Empfehlung: Git-Ordner nur für schnelle Iteration/Tests in der Entwicklung; für Staging/Produktion Remote-Git-Repositories verwenden.

## Git-Provider konfigurieren

Im Job-Details-Panel unter **Git** → **Add Git settings**, oder direkt in der Task-Konfiguration:

- Repository-URL
- Git-Provider aus Dropdown
- Git-Referenz: **branch**, **tag** oder **commit** (nur eines von beiden angeben) — z. B. `main`, `release-1.0.0`, `e0056d01`

## Als Rolle ausführen (RBAC)

Bei aktiviertem RBAC lässt sich die Run-As-Identität eines Jobs auf eine Gruppe (Rolle) setzen — der Job klont dann mit dem Git-Credential dieser Rolle.

## Sparse Checkout für große Repositories

Importiert nur bestimmte Verzeichnisse statt des gesamten Repositories — reduziert Checkout-Zeit und Ressourcenverbrauch. Falsch konfiguriert kann es jedoch Cache-Fragmentierung verursachen und die Ausführungszeiten workspaceweit verschlechtern.

### Caching-Mechanismus

Databricks cacht jeden Git-Checkout anhand von vier Werten: Workspace, Repository-URL, exakter Commit-Hash, Fingerprint des Sparse-Checkout-Musters. Ein Cache-Eintrag ist bis zu **eine Woche** gültig. Jedes eindeutige Muster erzeugt einen eigenen Fingerprint und damit einen eigenen Cache-Eintrag — 20 Nutzer mit je einem individuellen Zusatzordner erzeugen 20 Cache-Keys und importieren den gemeinsamen Ordnerbaum 20-mal.

### Wann Sparse Checkout sinnvoll ist

Beide Kriterien sollten zutreffen:

- **Größe:** Repository ist groß (z. B. über 2.500 Dateien).
- **Stabiles Ziel:** Zielbranch wird selten aktualisiert (z. B. ca. ein Commit pro Stunde oder seltener).

Zusätzlich empfohlen: **Standardisierung** (max. drei gemeinsame Checkout-Muster je Repository) und/oder **Micro-Targeting** (jedes Muster zielt auf wenige Dateien, idealerweise unter 200).

### Importrate berechnen

```
Files Per Hour = Job Runs Per Hour × Cache Miss Rate × Files Imported Per Miss
```

Beispiel: 180 Läufe/Stunde × 10 % Miss-Rate × 6.000 Dateien/Miss = 108.000 Dateien/Stunde.

| Dateien importiert pro Stunde | Erwartete Auswirkung |
|---|---|
| unter 150.000 | Normalbetrieb |
| 150.000–300.000 | Verschlechterte Performance, ggf. Verzögerungen/Fehlschläge |
| über 300.000 | Jobs schließen nicht mehr zuverlässig ab |

### Best Practices

- **Muster standardisieren:** max. drei genehmigte Sparse-Muster je Repository veröffentlichen; keine individuellen Team-Muster zulassen.
- **Commit-Churn steuern:** Jobs auf einen stabilen Release-Branch zeigen lassen statt auf `main`/`master`, da jeder neue Commit den Cache invalidiert.
- **Last steuern:** große Binärdateien und generierte Artefakte aus der Versionskontrolle entfernen; Trigger-Frequenz redundanter Jobs senken.

### Release-Branch zur Commit-Churn-Reduktion

1. Langlebigen Branch anlegen (z. B. `release-candidate`).
2. Automatisiert nach festem Zeitplan (z. B. stündlich) mit `main` aktualisieren.
3. Git-gestützte Jobs auf `release-candidate` zeigen lassen.

| Abwägung | Beschreibung |
|---|---|
| Commit-Verzögerung | Jobs laufen bis zu eine Stunde hinter `main` — für die meisten Batch-Workloads akzeptabel |
| Fehlerfenster | Schlägt der Release-Cut-Job fehl, bleibt der Branch für diese Stunde unverändert; Alerting auf den Cut-Job empfohlen |

**Beispiel — GitHub Actions für stündlichen Release-Cut:**

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

### Sparse Checkout über die Jobs API aktivieren

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

Jeder String in `patterns` ist ein Verzeichnispfad relativ zum Repository-Root; alle Dateien darin werden ausgecheckt.

## Quelle

- https://docs.databricks.com/aws/en/jobs/git
