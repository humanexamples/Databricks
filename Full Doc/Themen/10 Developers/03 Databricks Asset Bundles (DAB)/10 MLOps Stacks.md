# MLOps Stacks

Ein produktionsreifes ML-Projekt-Framework auf Basis von Bundles und der Databricks CLI. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Was MLOps Stacks sind](#was-sind)
2. [Voraussetzungen](#voraussetzungen)
3. [Sechs-Schritte-Umsetzung](#schritte)
4. [Anpassung](#anpassung)
5. [Quelle](#quelle)

---

## <a id="was-sind">1. Was MLOps Stacks sind</a>

„Ein MLOps Stack ist ein MLOps-Projekt auf Databricks, das von Haus aus produktionsreife Best Practices befolgt" — aufgebaut auf Bundles und der Databricks CLI.

## <a id="voraussetzungen">2. Voraussetzungen</a>

- Workspace-Dateien im Ziel-Workspace aktiviert.
- Databricks CLI ≥ 0.212.2 (`databricks -v`) — Versionen 0.18 und darunter sind inkompatibel.

## <a id="schritte">3. Sechs-Schritte-Umsetzung</a>

### Schritt 1 — Authentifizierung

Für die Entwicklung empfiehlt die Doku OAuth User-to-Machine (U2M):

```bash
databricks auth login --host <workspace-url>
```

Für jeden Ziel-Workspace ausführen, vorgeschlagenen Profilnamen übernehmen/anpassen, browserbasierten Login abschließen, Token-Status mit `databricks auth token` prüfen. Für Produktions-Deployments empfiehlt die Doku stattdessen „OAuth Machine-to-Machine (M2M)" für vollautomatisierte Workflows.

### Schritt 2 — Bundle-Projekt erstellen

```bash
databricks bundle init mlops-stacks
```

Drei Setup-Optionen:

- **CICD_and_Project** (Standard) — richtet sowohl ML-Code als auch CI/CD-Infrastruktur ein.
- **Project_Only** — fokussiert auf ML-Code-Komponenten für Data Scientists.
- **CICD_Only** — adressiert CI/CD-Infrastruktur für ML Engineers.

Die Initialisierung generiert Starter-Dateien mit rollenspezifischen Anleitungen (Data Scientists, MLOps Engineers, Erstnutzer).

### Schritt 3 — Validierung

```bash
databricks bundle validate
```

Vom Projekt-Root ausführen (wo `databricks.yml` liegt). Fehler müssen vor dem Fortfahren behoben werden.

### Schritt 4 — Deployment

```bash
databricks bundle deploy -t <target-name>
```

Zielname z. B. `dev`, `test`, `staging` oder `prod`.

### Schritt 5 — Ausführung

```bash
databricks bundle run -t <target-name> <job-name>
```

Deployte Jobs sofort ausführen, andernfalls laufen sie nach ihrem vordefinierten Zeitplan.

### Schritt 6 — Aufräumen (optional)

```bash
databricks bundle destroy -t <target-name>
```

Nach Bestätigungsabfrage.

## <a id="anpassung">4. Anpassung</a>

Anpassungs-Mappings für Experiments, Jobs, Modelle und Pipelines „entsprechen dem Request-Payload der jeweiligen `create [resource]`-Operation" der zugehörigen REST-API-Referenzen, ausgedrückt in YAML.

## <a id="quelle">5. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/mlops-stacks

**Stand:** 2026-08-21.
