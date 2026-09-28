# FAQ

Häufige Fragen zu Declarative Automation Bundles (früher Databricks Asset Bundles). Teil der [Databricks Asset Bundles](Uebersicht.md)-Reihe.

## <a id="frage-1">1. Warum wurden Databricks Asset Bundles in Declarative Automation Bundles umbenannt?</a>

Die Namensänderung spiegelt den tatsächlichen Anwendungsfall und die Fähigkeiten des Features genauer wider. Der frühere Begriff „Assets" erzeugte Mehrdeutigkeit, da Databricks dieses Wort in mehreren Kontexten nutzt. Wichtig: „Diese Namensänderung ist nicht-brechend — der `bundle`-CLI-Befehl und alle" bestehenden Konfigurationen bleiben unverändert.

## 2. Wie nutze ich Bundles als Teil meiner CI/CD-Pipeline auf Databricks?

Bundles ermöglichen die programmatische Verwaltung mehrerer Asset-Typen:

- **Notebooks:** Versionskontrolle, Validierung und automatisiertes Testen von Databricks-Notebooks innerhalb von CI/CD-Workflows.
- **Bibliotheken:** Verwaltung und Versionskontrolle von Bibliotheksabhängigkeiten mit automatisiertem Testen.
- **Workflows:** Nutzung von Jobs zur Zeitplanung und Automatisierung von Tasks über Notebooks oder Spark-Jobs.
- **Data Pipelines:** Einbindung von Pipeline-Deklarationen in die CI/CD-Automatisierung.
- **Infrastruktur:** Definition und Provisionierung von Clustern, Workspaces und Storage mit Validierung und Testing.

## 3. Warum brauche ich getrennte Development- und Production-Zielumgebungen?

Getrennte Umgebungen bieten mehrere Vorteile: sie „isolieren Entwicklungsänderungen sicher, sodass sie die Produktion nicht versehentlich beeinträchtigen"; verhindern Code-Duplizierung durch umgebungsspezifische Anpassung; vereinfachen CI/CD durch maßgeschneiderte Konfiguration; ermöglichen Workflow-Wiederverwendung über Teams und Umgebungen hinweg.

## 4. Wie mache ich meine Bundles organisationsweit konsistent?

Bundle-Templates nutzen, um standardisierte Struktur zu etablieren, Setup-Fehler zu reduzieren und Best Practices durchzusetzen. Organisationen können Standard-Templates nutzen oder eigene, maßgeschneiderte erstellen (siehe [04 Templates.md](04%20Templates.md)).

## 5. Es gibt viel Wiederholung über meine Bundles hinweg (z. B. dieselben Cluster-Definitionen) — wie gehe ich damit am besten um?

Benutzerdefinierte Variablen adressieren Wiederholung und kontextspezifische Einstellungen am effektivsten über Bundle-Konfigurationen hinweg.

## 6. Was sind Best Practices bei der Nutzung von Bundles im Deployment-Flow?

Databricks empfiehlt acht Kernpraktiken:

1. Von manuellen zu automatisierten, Git-integrierten Deployment-Workflows wechseln.
2. Bundles mit `databricks bundle validate` innerhalb von CI/CD validieren.
3. Deploy-Schritte für Review und bewusste Änderungen trennen.
4. Umgebungen (Dev, Staging, Prod) über Overrides parametrisieren.
5. Integrationstests nach dem Deployment ausführen, um Probleme frühzeitig zu erkennen.
6. GitHub Actions, Azure DevOps oder GitLab CI nutzen, um Deployments auszulösen (siehe [CI-CD](../CI-CD/)).
7. Deployment-Tracking pflegen, das jedes Deployment mit einem bestimmten Commit verknüpft.
8. Deployment-Versionen und -Orte systematisch überwachen.

## 7. Kann ich bestehende Jobs, Pipelines, Dashboards und andere Databricks-Objekte in mein Bundle übernehmen?

Ja. `databricks bundle generate` nutzen, um Konfigurationsdateien für bestehende Ressourcen zu erstellen, dann `databricks bundle deployment bind`, um Bundle-Ressourcen mit Workspace-Ressourcen zu verknüpfen (siehe [09 Manuelle Bundle-Erstellung und Ressourcen-Migration.md](09%20Manuelle%20Bundle-Erstellung%20und%20Ressourcen-Migration.md)). Dieser Ansatz ermöglicht das „Onboarding bestehender Workflows in eine strukturierte, versionierte Entwicklung" und löst dabei Pfad-Referenzen auf, um Fehler zu vermeiden.

## 8. Wie teste ich mein Bundle iterativ?

Iteratives Testen umfasst vier Schritte: vor dem Deployment validieren; inkrementell deployen; nur benötigte Komponenten ausführen; wiederholt bearbeiten. Diese Methodik „beschleunigt Testen und Debugging, reduziert Kontextwechsel, ermöglicht sicherere und schnellere Iteration" und erzwingt gleichzeitig Disziplin, während Projekte sich der Produktion nähern.

## Quelle

- https://docs.databricks.com/aws/en/dev-tools/bundles/faqs

**Stand:** 2026-08-21.
