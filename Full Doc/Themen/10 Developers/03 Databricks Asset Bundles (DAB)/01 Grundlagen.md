# Grundlagen

Was Declarative Automation Bundles (früher Databricks Asset Bundles) sind, ihre Kernkomponenten, Einsatzszenarien und der sechsstufige Entwicklungs-Lebenszyklus. Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Was Bundles sind](#was-sind)
2. [Kernkomponenten](#komponenten)
3. [Wann Bundles einsetzen](#einsatz)
4. [Funktionsweise](#funktionsweise)
5. [Installationsvoraussetzungen](#voraussetzungen)
6. [Der sechsstufige Lebenszyklus](#lebenszyklus)
7. [Quelle](#quelle)

---

## <a id="was-sind">1. Was Bundles sind</a>

Bundles erlauben es, „Databricks-Ressourcen wie Jobs und Pipelines als Quelldateien zu beschreiben" — eine vollständige End-to-End-Projektdefinition, gebündelt als ein einziges deploybares Projekt.

## <a id="komponenten">2. Kernkomponenten</a>

Ein Bundle enthält: benötigte Cloud-Infrastruktur und Workspace-Konfigurationen; Quelldateien (Notebooks, Python-Dateien) mit der Geschäftslogik; Definitionen für Databricks-Ressourcen (Jobs, Pipelines, Dashboards, Model-Serving-Endpoints, MLflow-Experimente, registrierte Modelle); Unit- und Integrationstests.

## <a id="einsatz">3. Wann Bundles einsetzen</a>

- Team-basierte Entwicklung von Daten-, Analytics- und ML-Projekten.
- Schnellere Iteration bei ML-Problemen unter Nutzung produktionsreifer Praktiken.
- Etablierung organisationsweiter Standards über eigene Templates.
- Branchen mit regulatorischen Compliance-Anforderungen an versionierte Code-/Infrastruktur-Historie.

## <a id="funktionsweise">4. Funktionsweise</a>

Bundle-Metadaten nutzen YAML-Dateien, die Artefakte, Ressourcen und Konfiguration spezifizieren. Die Databricks CLI validiert, deployt und führt Bundles aus. Projekte lassen sich manuell erstellen oder aus Templates ableiten — Databricks liefert Standard-Templates, eigene Templates sind für teamspezifische Implementierungen möglich (siehe [04 Templates.md](04%20Templates.md)).

## <a id="voraussetzungen">5. Installationsvoraussetzungen</a>

- Workspace-Dateien müssen im Databricks-Workspace aktiviert sein (Standard ab Runtime 11.3 LTS+).
- Databricks CLI Version 0.218.0 oder höher installiert.
- CLI für Workspace-Zugriff konfiguriert (OAuth-U2M-Authentifizierung empfohlen, siehe [07 Deployment-Modi und Authentifizierung.md](07%20Deployment-Modi%20und%20Authentifizierung.md)).

**Einstieg:** Projekte über `databricks bundle init` initialisieren, das Template-Auswahl und Konfigurationsfragen präsentiert. Die Entwicklung setzt sich fort über die Definition von Einstellungen in `databricks.yml` und Ressourcen-Konfigurationsdateien, gefolgt von Validierung und Deployment.

## <a id="lebenszyklus">6. Der sechsstufige Lebenszyklus</a>

1. **Create** — Bundle-Grundgerüst aus einem Projekt-Template initialisieren.
2. **Develop** — Konfigurationsdateien lokal erstellen, die Infrastruktur und Workspace-Einstellungen definieren.
3. **Validate** — Einstellungen gegen Schemas prüfen, um Deploybarkeit sicherzustellen.
4. **Deploy** — Bundle in den Ziel-Workspace pushen (Dev, Staging, Production).
5. **Run** — Workflow-Ressourcen wie Jobs oder Pipelines ausführen.
6. **Destroy** — Bundle-Ressourcen dauerhaft entfernen, wenn nicht mehr benötigt.

### 6.1 Drei Wege, ein Bundle zu erstellen

**Standard-Template:**

```bash
databricks bundle init
```

Zeigt verfügbare Templates aus den offiziellen Databricks-Repositories (`databricks/cli`, `databricks/mlops-stacks`).

**Eigenes Template:**

```bash
databricks bundle init <project-template-local-path-or-url>
```

**Manuelle Erstellung:** ein Projektverzeichnis lokal oder mit Git anlegen, YAML-Konfigurationsdateien erstellen — `databricks.yml` ist die einzige Pflichtdatei. Weitere Konfigurationsdateien müssen im `include`-Mapping referenziert werden (siehe [09 Manuelle Bundle-Erstellung und Ressourcen-Migration.md](09%20Manuelle%20Bundle-Erstellung%20und%20Ressourcen-Migration.md)).

**IDE-Unterstützung für manuelle Erstellung:** drei IDEs bieten YAML-/JSON-Schema-Support:

- **Visual Studio Code:** YAML-Extension aus dem Marketplace installieren; Schema generieren: `databricks bundle schema > bundle_config_schema.json`; Kommentar in `databricks.yml` ergänzen: `# yaml-language-server: $schema=bundle_config_schema.json`.
- **PyCharm Professional & IntelliJ IDEA Ultimate:** Schema-Datei über den `bundle schema`-Befehl generieren; benutzerdefiniertes JSON-Schema-Mapping in den IDE-Einstellungen konfigurieren — liefert Echtzeit-Syntaxprüfung und Code-Vervollständigung.

### 6.2 Konfiguration befüllen

Konfigurationsdateien spezifizieren Workspace-Details, Artefaktnamen, Dateipfade, Job- und Pipeline-Einstellungen — typischerweise mit Dev-, Staging- und Production-Deployment-Targets. Zwei Automatisierungsbefehle helfen: `bundle generate` (generiert automatisch Konfiguration für bestehende Workspace-Ressourcen) und `bundle deployment bind` (verknüpft generierte Konfiguration mit Ressourcen zur Synchronisation) — siehe [09 Manuelle Bundle-Erstellung und Ressourcen-Migration.md](09%20Manuelle%20Bundle-Erstellung%20und%20Ressourcen-Migration.md).

### 6.3 Validieren

```bash
databricks bundle validate
```

Erfolgreiche Validierung liefert „eine Zusammenfassung der Bundle-Identität und eine Bestätigungsmeldung." `databricks bundle schema` gibt das Schema separat aus.

### 6.4 Deployen

Voraussetzung: Workspace-Dateien im Remote-Workspace aktiviert.

```bash
databricks bundle deploy
```

Deployment erfolgt in den in der Konfiguration deklarierten Ziel-Workspace. Die Bundle-Identität setzt sich aus Name, Target und Deployer-Identität zusammen — identische Kombinationen über unterschiedliche Bundles hinweg verursachen Interferenzen. Hinweis: `BUNDLE_ROOT` kann gesetzt werden, um Befehle außerhalb des Bundle-Verzeichnisses auszuführen.

### 6.5 Ausführen

```bash
databricks bundle run hello_job
databricks bundle run -t dev hello_job
```

Der Ressourcen-Key entspricht Top-Level-YAML-Elementen. Ohne Key-Angabe wählt der Nutzer aus verfügbaren Ressourcen. Ohne `-t`-Option greift das Default-Target.

### 6.6 Zerstören

**Warnung:** „Das Zerstören eines Bundles löscht dessen zuvor deployte Jobs, Pipelines und Artefakte dauerhaft. Diese Aktion kann nicht rückgängig gemacht werden."

```bash
databricks bundle destroy
databricks bundle destroy --auto-approve
```

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/bundles/
- https://docs.databricks.com/aws/en/dev-tools/bundles/work-tasks

**Stand:** 2026-08-21.
