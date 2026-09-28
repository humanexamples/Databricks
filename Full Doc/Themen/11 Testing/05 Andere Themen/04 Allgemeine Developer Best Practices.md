# Allgemeine Developer Best Practices

Die vollständige offizielle Best-Practices-Sammlung für Databricks-Entwickler: Source Control, Workspace-Konfiguration, CI/CD-Empfehlungen, Bundle-Management, allgemeine Entwicklung sowie Testing und Observability. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Source Control](#source-control)
2. [Workspace-Konfiguration](#workspace-konfig)
3. [CI/CD-Empfehlungen](#cicd)
4. [Bundle-Management](#bundle-management)
5. [Allgemeine Entwicklung](#allgemein)
6. [Testing und Observability](#testing-observability)
7. [Quelle](#quelle)

---

## <a id="source-control">1. Source Control</a>

**Alle Dateien versionieren:** Notebooks, Quelldateien (`.py`, `.sql`) und Bundle-Konfigurationsdateien (`databricks.yml` mit umgebungsspezifischen Overrides) gehören unter Versionskontrolle. Build-Artefakte (`.jar`/`.whl`), Credentials/Tokens und lokale Daten mit personenbezogenen Informationen über `.gitignore` ausschließen.

**Ein einzelnes Repository:** Die Doku empfiehlt, ein Repository für allen Code und alle Konfiguration zu pflegen — erleichtert Zusammenarbeit und Wissensaustausch. Einzige Ausnahme: regulierte Branchen, in denen getrennte Repositories Vertraulichkeitsanforderungen dienen.

**Trunk-based-Branching-Strategie:** minimiert Merge-Konflikte und hält den Main-Branch stets deploybar. Workflow: lokal entwickeln, kurzlebige Feature-Branches erstellen, Änderungen in einem Development-Workspace testen, in Main mergen. Automatisiertes CI/CD deployt anschließend in Staging und Production mit begleitender Testausführung.

## <a id="workspace-konfig">2. Workspace-Konfiguration</a>

**Workspace-Umgebungen isolieren:** Teamgröße bestimmt die Umgebungsstruktur — kleine Teams (≤5 Engineers) benötigen Development- und Production-Workspaces; größere Teams (5+) sollten Staging ergänzen. Regulierte Branchen benötigen physisch isolierte Workspaces und Cloud-Accounts. Production-Workspaces sollten Serverless Compute mit Netzwerkrichtlinien oder private Subnetze mit eingeschränktem Egress nutzen.

**Datenspeicher isolieren:** Organisationen sollten einen einzelnen Unity-Catalog-Metastore mit getrennten Catalogs für Development, Staging und Production nutzen. Einzelne Entwickler benötigen persönliche Schemas in Nicht-Produktions-Catalogs. Produktions-Catalogs müssen im `ISOLATED`-Modus ausschließlich an Produktions-Workspaces gebunden sein — verhindert Datenzugriff durch falsch konfigurierte Identitäten in niedrigeren Umgebungen.

**Tabellen- und Spalten-Metadaten als Code behandeln:** Tabellen- und Spaltenkommentare gehören in `.sql`-Dateien neben Bundle-Definitionen, deployt über Metadaten-Jobs. Kommentare sollten Zeilenrepräsentation, Einheiten und gültige Werte in klarer Sprache beschreiben, statt Spaltennamen zu wiederholen.

**Persönliche Schemas konfigurieren:** Bundles sollten während der Entwicklung persönliche Schemas nach Muster `dev_${user_name}` referenzieren — verhindert, dass Entwickler sich gegenseitig Tabellen in gemeinsam genutzten Workspaces überschreiben.

**Serverless Compute nutzen:** vereinfacht Cluster-Management und optimiert Kosten — die bevorzugte Compute-Option.

## <a id="cicd">3. CI/CD-Empfehlungen</a>

**Databricks Asset Bundles für CI/CD:** „Databricks Asset Bundles bieten einen mächtigen, einheitlichen Ansatz zur Verwaltung von Code, Workflows und Infrastruktur innerhalb des Databricks-Ökosystems und werden für CI/CD-Pipelines empfohlen."

**Terraform nur für externe Ressourcen nutzen:** Terraform sollte Cloud-Ebenen-Ressourcen und administrative Aktionen definieren (Workspace-Provisionierung, Networking). Databricks Asset Bundles sollten alle übrigen Databricks-Ressourcen verwalten.

## <a id="bundle-management">4. Bundle-Management</a>

**Kleine Bundles erstellen:** jedes Bundle sollte die Eigentümerschaft eines einzelnen Teams repräsentieren, alle Umgebungen (Dev/Staging/Prod) für dieses Projekt abdecken. Getrennte Bundles für unterschiedliche Produkte/Domänen, Eigentümergrenzen, unterschiedliche Lifecycle-Anforderungen oder unabhängige Promotion-/Rollback-Bedürfnisse.

**`sync.paths` zur Synchronisation gemeinsamer Ordner nutzen:** bei mehreren Bundles in einem Repository ermöglicht `sync.paths` die Synchronisation gemeinsam genutzter Ordner außerhalb des Bundle-Roots (siehe [Developers/Databricks Asset Bundles/08 Zusammenarbeit und gemeinsame Dateien.md](../../Developers/Databricks%20Asset%20Bundles/08%20Zusammenarbeit%20und%20gemeinsame%20Dateien.md)).

**Inter-Bundle-Abhängigkeiten in CI/CD modellieren:** hängt Bundle B von Assets aus Bundle A ab, sollte die Abhängigkeit in der CI/CD-/Orchestrierungsebene existieren, statt beide Bundles zusammenzulegen. Der Abschluss und die Validierung des Deployments von Bundle A sollten der Ausführung von Bundle B vorausgehen.

**Eigene Bundle-Templates:** Organisationen sollten eigene Templates als Standard-Ausgangspunkt für neue Projekte entwickeln, die gemeinsame Konventionen kodieren — Berechtigungen, Tagging, Cluster-Policies, CI/CD-Verdrahtung, Instanz-Baselines (siehe [Developers/Databricks Asset Bundles/04 Templates.md](../../Developers/Databricks%20Asset%20Bundles/04%20Templates.md)).

**Für Rollbacks und Hotfixes planen:** kleine Bundles ermöglichen gezielte Rollbacks. Bei Vorfällen betroffene Bundles auf die letzte bekannt gute Version zurücksetzen. Hotfixes sollten nur dringende, eng begrenzte Probleme adressieren, mit sofortigem Zurückmergen in Main.

## <a id="allgemein">5. Allgemeine Entwicklung</a>

**Service Principals oder OIDC nutzen:** „Service Principals für jegliche Nicht-Development-Automatisierung nutzen, um automatisierte Workflows von individuellen Nutzerkonten zu entkoppeln." Getrennte Service Principals für Deployment (mit minimalem Datenzugriff) und Laufzeit-Operationen (auf spezifische Workload-Anforderungen begrenzt). Regulierte Branchen sollten Workload Identity Federation (OIDC) für CI/CD implementieren, um langlebige Secrets zu eliminieren.

**Databricks-Entwicklertools nutzen:** Workspace-UI mit Git Folders oder lokale IDEs nutzen. Die offizielle Databricks-VS-Code-Extension bietet Zugriff auf Agent Skills, Unity-Catalog-Zugriff und Remote-Entwicklungsfähigkeiten.

**Geschäftslogik in Notebooks minimieren:** Notebooks sollten nur als Explorations- und Visualisierungsebene dienen. Python-Kernlogik gehört in importierbare `.py`-Module innerhalb von `src/` oder `src/py/`, SQL-Queries in `.sql`-Dateien innerhalb von `src/` oder `src/sql/` — referenziert von Jobs und Pipelines statt in Notebooks eingebettet zu sein.

**Kontext dynamisch übergeben:** statische Variablen für Task-Abhängigkeiten vermeiden, stattdessen dynamische Wertreferenzen wie `{{tasks.<task_key>.values.<value_key>}}` nutzen, um Laufzeitkontext zwischen mehrstufigen Job-Tasks zu übergeben.

## <a id="testing-observability">6. Testing und Observability</a>

**Testing-Ebenen implementieren:** drei Testing-Ebenen entsprechen dem Bundle-Fortschritt Richtung Produktion:

1. **Unit Tests** — Geschäftslogik mit `pytest` abdecken, blockierend bei Pull-Request-Fehlschlägen.
2. **Bundle-Validierung** — `bundle validate` lokal und `bundle deploy` in Nicht-Produktions-Workspaces in CI.
3. **Integrationstests** — in Staging mit Abschlussprüfungen und Datenqualitäts-Assertions.

Lakeflow Pipelines sollten die eingebauten Development- und Validierungs-Features nutzen (siehe [02 Integrationstest/01 Lakeflow Pipelines Unit Testing.md](../02%20Integrationstest/01%20Lakeflow%20Pipelines%20Unit%20Testing.md)) statt Ad-hoc-Notebook-Ausführung.

**Logging als Teil des Deployments behandeln:** für deployte Workloads „Metriken und Logging als Teil des Deployment-Vertrags behandeln, statt als etwas, das jedes Projekt unabhängig definiert." Strukturierte Logs konsistent über Jobs und Pipelines hinweg emittieren, Standard-Betriebsmetriken (Run-Status, Dauer, Retry-Anzahl, Durchsatz-/Aktualitäts-Indikatoren) verfolgen, diese Konventionen in gemeinsam genutzten Bibliotheken und Bundle-Templates kodieren.

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/developers/best-practices

**Stand:** 2026-08-21.
