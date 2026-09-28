# Quiz

1. **Welches Format verwenden Declarative Automation Bundles (DABs), um Code gemeinsam mit Konfigurationen zu versionieren?**

   - XML
   - YAML ✅
   - Python
   - JSON

2. **Welche Komponente muss angegeben werden, wenn Sie mit databricks bundle run einen Job innerhalb eines bereitgestellten Bundles ausführen?**

   - Notebook-Pfad
   - Bundle-Name
   - Zielumgebung
   - Name des Job-Schlüssels ✅

3. **Welche Strategie ermöglicht es, Entwicklungsumgebungen mit Unity Catalog in Databricks zu isolieren?**

   - Separate Jobs verwenden
   - Separate Kataloge/Workspaces verwenden ✅
   - Separate Workflows verwenden
   - Separate Dashboards verwenden

4. **Welches Deployment-Tool erfordert das manuelle Erstellen von HTTP-Anfragen?**

   - Declarative Automation Bundles
   - Databricks CLI
   - Databricks SDK
   - Databricks REST API ✅

5. **Welchen Vorteil bietet die lokale Verwendung der Databricks CLI im Vergleich zu Databricks-Notebooks?**

   - Interaktiveres Debugging ✅
   - Automatische Rollback-Funktionen
   - Höhere Compute-Zuweisung
   - Einfachere Zusammenarbeit am Code

6. **Als welcher Identitätstyp wird eine deklarative Pipeline beim Deployment in eine Staging-Umgebung typischerweise ausgeführt?**

   - Anonymer Benutzer
   - Workspace-Administrator
   - Run as Service Principal ✅
   - Single-Node-Benutzer

7. **Welches Suffix des CLI-Befehls ist erforderlich, um ein Bundle in einer bestimmten Umgebung namens development bereitzustellen?**

   - -w development
   - -c development
   - -e development
   - -t development ✅

8. **Welches Mapping der obersten Ebene wird verwendet, um Databricks-Objekte wie Lakeflow Jobs und MLflow zu definieren?**

   - permissions
   - targets
   - artifacts
   - resources ✅

9. **Mit welchem Befehl der Databricks CLI wird ein neues Bundle auf Basis eines Templates erstellt?**

   - databricks bundle create
   - databricks bundle template
   - databricks bundle generate
   - databricks bundle init ✅

10. **Welche Eigenschaft von Konfigurationsdateien stellen Standard-Variablenersetzungen sicher?**

- Unveränderlichkeit
- Isolation der Umgebungen
- Trennung nach Cloud-Anbietern
- Wiederverwendbarkeit ✅

11. **An welchen Teil des gesamten CI/CD-Workflows schließt sich der Deployment-Schritt mit der Databricks CLI unmittelbar an?**

- Entwickeln
- Testen/Versionskontrolle ✅??
- Build
- Überwachen

12. **Welche Möglichkeit bietet die Definition eines Lookups für eine benutzerdefinierte Variable?**

- Sicherstellen, dass der Wert global eindeutig ist
- Den Variablentyp in einen komplexen Typ umwandeln
- Die ID bzw. den Wert des Objekts dynamisch abrufen ✅??
- Den Wert der Variablen verschlüsseln

13. **Welches Entwicklertool führt Apache-Spark-Code aus einer lokalen Umgebung remote auf einem Databricks-Cluster aus?**

- Databricks CLI
- Databricks VSCode Extension
- DBFS Fuse
- Databricks Connect V2 ✅

14. **Welcher Mechanismus stellt sicher, dass verschiedene Umgebungen (dev/prod) dasselbe Bundle verwenden, aber auf unterschiedliche Kataloge verweisen können?**

- Separate Notebooks verwenden
- Unity Catalog deaktivieren
- Katalognamen im Code fest codieren
- Variablen-Überschreibungen pro Zielumgebung ✅

15. **Was vereinfacht die Databricks VSCode Extension in Bezug auf Entwicklungsressourcen?**

- Einrichtung mit Ressourcen-Explorern und CLI ✅
- Überwachung von Kennzahlen zum Pipeline-Zustand
- Begrenzungen der Clustergröße
- Automatisierte Erstellung von YAML-Dateien

16. **Für welche Art von Tests werden Expectations in Delta Live Tables (DLT) hauptsächlich verwendet?**

- Integrationstests ✅
- Systemtests
- Unit-Tests
- Smoke-Tests

17. **Unter welchem Mapping werden bei der Definition einer komplexen Variablen für einen Cluster Konfigurationseinstellungen wie spark_version aufgeführt?**

- type
- default ✅
- name
- description

18. **Was ist die Hauptfunktion von Declarative Automation Bundles (DABs)?**

- Best Practices des Software-Engineerings für Daten-/KI-Projekte ermöglichen ✅
- Eine grafische Oberfläche für Entwickler bereitstellen
- Nur Konfigurationen von SQL Warehouses definieren
- Nur die Abrechnung von Clustern verwalten

19. Mit welchem Befehl prüfen Sie Bundle-Konfigurationsdateien auf Warnungen zu Ressourceneigenschaften?

- databricks bundle get
- databricks bundle run
- databricks bundle validate ✅
- databricks bundle deploy

20. Welche Funktion kann benutzerdefinierten Templates hinzugefügt werden, um die Benutzerinteraktion bei der Initialisierung zu erleichtern?

- Remote-Ausführung von Spark
- Benutzerabfragen (User Prompts) ✅??
- Automatische Validierung des Deployments
- Integriertes Debugging
