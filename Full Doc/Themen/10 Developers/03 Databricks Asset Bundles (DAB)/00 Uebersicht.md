# Databricks Asset Bundles — Überblick

Databricks Asset Bundles heißen inzwischen offiziell **Declarative Automation Bundles** — „ein Tool, das die Übernahme von Software-Engineering-Best-Practices" für Daten- und KI-Initiativen erleichtert. Sie erlauben es, Databricks-Ressourcen wie Jobs und Pipelines als Quelldateien zu beschreiben und damit eine vollständige End-to-End-Projektdefinition zu erstellen. Namenshinweis: „Diese Namensänderung ist nicht-brechend — der `bundle`-CLI-Befehl und alle bestehenden Konfigurationen bleiben unverändert."

## Themen in diesem Kapitel

1. **Grundlagen** — was Bundles sind, Kernkomponenten, Einsatzszenarien, der sechsstufige Lebenszyklus. Siehe [01 Grundlagen.md](01%20Grundlagen.md).
2. **Tutorials: Jobs, Pipelines, Apps** — vollständige Schritt-für-Schritt-Anleitungen für die drei Standard-Tutorials. Siehe [02 Tutorials - Jobs, Pipelines, Apps.md](02%20Tutorials%20-%20Jobs%2C%20Pipelines%2C%20Apps.md).
3. **Python- und Scala-Artefakte** — Python-Wheel und Scala-JAR bauen, Python als Konfigurationssprache (PyDABs). Siehe [03 Python- und Scala-Artefakte.md](03%20Python-%20und%20Scala-Artefakte.md).
4. **Templates** — Standard-Templates, eigene Templates erstellen und teilen. Siehe [04 Templates.md](04%20Templates.md).
5. **Konfiguration (databricks.yml)** — alle Top-Level-Mappings der Bundle-Konfiguration, inkl. vordefinierter Substitutionen sowie einfacher, komplexer und Lookup-Variablen mit Beispielen. Siehe [05 Konfiguration (databricks.yml).md](05%20Konfiguration%20%28databricks.yml%29.md).
6. **Bundles im Workspace (Web-UI)** — Bundles direkt im Browser erstellen, bearbeiten und deployen. Siehe [06 Bundles im Workspace (Web-UI).md](06%20Bundles%20im%20Workspace%20%28Web-UI%29.md).
7. **Deployment-Modi und Authentifizierung** — `development`/`production`-Modus, Presets, Auth-Methoden. Siehe [07 Deployment-Modi und Authentifizierung.md](07%20Deployment-Modi%20und%20Authentifizierung.md).
8. **Zusammenarbeit und gemeinsame Dateien** — mehrere Bundles teilen sich Konfiguration/Code. Siehe [08 Zusammenarbeit und gemeinsame Dateien.md](08%20Zusammenarbeit%20und%20gemeinsame%20Dateien.md).
9. **Manuelle Bundle-Erstellung und Ressourcen-Migration** — Bundle ohne Template von Grund auf, bestehende Ressourcen einbinden. Siehe [09 Manuelle Bundle-Erstellung und Ressourcen-Migration.md](09%20Manuelle%20Bundle-Erstellung%20und%20Ressourcen-Migration.md).
10. **MLOps Stacks** — produktionsreifes ML-Projekt-Framework auf Basis von Bundles. Siehe [10 MLOps Stacks.md](10%20MLOps%20Stacks.md).
11. **Direct Deployment Engine** — die neue, Terraform-freie Deployment-Engine. Siehe [11 Direct Deployment Engine.md](11%20Direct%20Deployment%20Engine.md).
12. **Air-Gapped-Umgebungen** — Bundles ohne Internetzugriff über Docker nutzen. Siehe [12 Air-Gapped-Umgebungen.md](12%20Air-Gapped-Umgebungen.md).
13. **FAQ** — häufige Fragen und Best Practices. Siehe [13 FAQ.md](13%20FAQ.md).
14. **VS Code Extension** — die Databricks IDE Extension für lokale Bundle-Entwicklung: Authentifizierung, Bundle Resource Explorer, One-Click-Deploy. Siehe [14 VS Code Extension.md](14%20VS%20Code%20Extension.md).
15. **Ressourcentypen (Referenz)** — alle über `resources` definierbaren Ressourcentypen mit Feldern und Besonderheiten. Siehe [15 Ressourcentypen (Referenz).md](15%20Ressourcentypen%20%28Referenz%29.md).
16. **Job-Task-Typen** — Referenz aller Task-Typen für Job-Ressourcen. Siehe [16 Job-Task-Typen.md](16%20Job-Task-Typen.md).
17. **Job-Parameter** — Job-Parameter vs. Bundle-Variablen, Laufzeit-Overrides. Siehe [17 Job-Parameter.md](17%20Job-Parameter.md).
18. **Run As** — Deployment- vs. Ausführungsidentität, Ressourcen-Support, Best Practices. Siehe [18 Run As.md](18%20Run%20As.md).
19. **Berechtigungen (Permissions)** — Top-Level- vs. ressourcenspezifische Permissions, Stufen-Tabelle, Präzedenzregeln. Siehe [19 Berechtigungen (Permissions).md](19%20Berechtigungen%20%28Permissions%29.md).
20. **Overrides zwischen Targets** — Merge-/Override-Regeln für Artifacts, Cluster und Tasks. Siehe [20 Overrides zwischen Targets.md](20%20Overrides%20zwischen%20Targets.md).
21. **Private Artefakte** — Artefakte aus privaten Quellen einbinden. Siehe [21 Private Artefakte.md](21%20Private%20Artefakte.md).
22. **Bibliotheksabhängigkeiten** — Wheel, JAR, PyPI, Maven, `requirements.txt`, `uv`. Siehe [22 Bibliotheksabhaengigkeiten.md](22%20Bibliotheksabhaengigkeiten.md).
23. **Beispiele (bundle-examples Repo)** — Katalog offizieller Bundle-Beispiele nach Anwendungsfall. Siehe [23 Beispiele (bundle-examples Repo).md](23%20Beispiele%20%28bundle-examples%20Repo%29.md).

## Verwandte Kapitel

- [Git Folders (Repos)](../Git%20Folders%20%28Repos%29/) — Versionskontrolle für Bundle-Quellcode.
- [CI-CD](../CI-CD/) — Bundles sind die von Databricks empfohlene CI/CD-Methodik.
- [Terraform](../Terraform/) — der klassische Databricks-Terraform-Provider als Alternative/Unterbau der Bundles-Deployment-Engine.

**Stand:** 2026-09-11.
