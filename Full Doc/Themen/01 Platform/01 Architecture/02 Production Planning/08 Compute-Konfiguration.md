# Phase 8: Compute-Konfiguration gestalten

Teil der [Production Planning](Uebersicht.md)-Reihe. Behandelt Cluster- und SQL-Warehouse-Sizing, Cluster- und Usage-Policies, Kostenüberwachung, Zugriffskontrolle und Workspace-Einstellungen aus Admin-/Governance-Perspektive. Für die technische Instance-Auswahl und Performance-Tuning-Details siehe [Performance Optimization/The Right Cluster](../../../Performance%20Optimization/The%20Right%20Cluster/).

## Abschnittsübersicht

1. [Grundempfehlung: Serverless zuerst](#grundempfehlung)
2. [Cluster-Sizing-Strategie](#cluster-sizing)
3. [SQL-Warehouse-Sizing-Strategie](#sql-warehouse-sizing)
4. [Cluster-Policy-Strategie](#cluster-policies)
5. [Usage-Policy-Strategie](#usage-policies)
6. [Nutzung und Kosten überwachen](#monitoring)
7. [Zugriffskontroll-Strategie](#access-control)
8. [Workspace-Einstellungen überprüfen](#workspace-settings)
9. [Empfehlungen](#empfehlungen)
10. [Ergebnisse der Phase](#ergebnisse)
11. [Quelle](#quelle)

---

## <a id="grundempfehlung">1. Grundempfehlung: Serverless zuerst</a>

Databricks empfiehlt Serverless Compute als primäre Option: „Serverless erfordert keine Konfiguration, ist immer verfügbar und skaliert automatisch mit den Workloads in Sekunden." Classic Compute nur manuell konfigurieren, wenn Serverless den Anwendungsfall nicht unterstützt.

## <a id="cluster-sizing">2. Cluster-Sizing-Strategie gestalten</a>

### Überlegungen

- **Workload-Typ:** Batch-Verarbeitung benötigt größere Cluster; interaktive Workloads profitieren von Autoscaling.
- **Datenvolumen:** Cluster nach erwartetem Datenvolumen und Parallelitätsanforderungen dimensionieren.
- **Performance-Anforderungen:** Balance zwischen Kosten und Query-Latenz.
- **Autoscaling:** für Workloads mit variablem Bedarf aktivieren.
- **Instance-Typen:** nach CPU-, Speicher- und I/O-Anforderungen wählen.

### Größenmuster

- **Kleine Cluster (2–8 Knoten):** Development, Testing, kleine Datensätze.
- **Mittlere Cluster (8–32 Knoten):** Produktions-ETL und Analytics-Workloads.
- **Große Cluster (32+ Knoten):** großangelegte Batch-Verarbeitung und ML-Training.

**Best Practices:** mit einer Baseline-Konfiguration starten und anhand von Performance-Metriken iterieren; Autoscaling für variable Workloads nutzen; Cluster-Auslastungsmetriken (CPU, Speicher, I/O) zum Right-Sizing überwachen; Spot-/Preemptible-Instanzen für fehlertolerante Workloads zur Kostenreduktion nutzen; Sizing-Entscheidungen und Performance-Baselines dokumentieren.

## <a id="sql-warehouse-sizing">3. SQL-Warehouse-Sizing-Strategie gestalten</a>

Databricks SQL nutzt einen Auto-Scaling-Mechanismus, der Cluster basierend auf drei Faktoren hinzufügt oder entfernt:

- **Query-Durchsatz:** Wie viele Queries laufen aktuell?
- **Queue-Größe:** Wie viele Queries warten auf einen Slot?
- **Vorhergesagter Bedarf:** die geschätzte Workload für die nächsten zwei Minuten.

„Databricks fügt Cluster hinzu, wenn berechnet wird, dass die aktuelle Hardware die bestehenden und anstehenden Queries nicht schnell genug verarbeiten kann."

### Die richtige Größe wählen (XS bis XL)

Die „T-Shirt-Größe" des Clusters bestimmt die verfügbare Rechenleistung je Query.

- **Kleine Stufen (XS, S):** am besten für einfache, schnelle Queries — am kosteneffektivsten für einfache Dashboards.
- **Große Stufen (L, XL):** nötig für komplexe, aufwendige Queries auf riesigen Datensätzen, um Performance-Engpässe zu vermeiden.

### Die richtige Anzahl wählen (Concurrency)

Die Anzahl der Compute-Ressourcen bestimmt, wie viele gleichzeitige Nutzer unterstützt werden.

- **Faustregel:** etwa 10 gleichzeitige Queries je Cluster einplanen.
- **Hohe Concurrency:** viele Nutzer mit kleinen Queries → viele kleine Cluster.
- **Niedrige Concurrency:** wenige Nutzer mit großen Queries → wenige große Cluster.

**Zusammenfassung:** „Größe erhöhen, um einzelne Queries schneller zu machen. Anzahl erhöhen, um mehr Nutzer gleichzeitig zu bedienen."

**Best Practices:** mit Serverless-SQL-Warehouses starten (kein Sizing nötig); bei Classic-SQL-Warehouses mit mittlerer Größe starten und anhand der Query-Muster anpassen; Query-Performance und Queueing-Metriken überwachen; mehrere Warehouses für unterschiedliche Anwendungsfälle nutzen (Ad-hoc vs. Reporting); Performance-SLAs für unterschiedliche Nutzergruppen dokumentieren.

## <a id="cluster-policies">4. Cluster-Policy-Strategie gestalten</a>

„Mit Cluster-Policies können Databricks-Admins viele Aspekte der hochgefahrenen Cluster kontrollieren. Cluster-Policies werden für alle Organisationen empfohlen."

**Anwendungsfälle:** Nutzer auf vorgeschriebene Einstellungen beschränken (verfügbare Instance-Typen, Databricks-Versionen, Instanzgrößen); Benutzeroberfläche vereinfachen, indem Werte fixiert/versteckt werden; Kosten begrenzen (maximale Kosten je Cluster); Compliance durchsetzen (externe Metastores oder bestimmte Cluster-Tags vorschreiben).

**Muster:** Development-Policy (kleine, kosteneffiziente Cluster); Production-Policy (größere, leistungsfähigere Cluster mit bestimmten Instance-Typen und Tags); ML-Policy (GPU-fähige Cluster mit ML-Runtimes); Spot-/Preemptible-Policy (Spot-Instanzen für fehlertolerante Workloads).

**Best Practices:** getrennte Policies je Team/Anwendungsfall erstellen; Cluster-Policies zur Durchsetzung von Kostenkontrollen und Ressourcengrenzen nutzen; Tags auf allen Clustern zur Kostenzuordnung verlangen; UI durch Ausblenden unnötiger Konfigurationsoptionen vereinfachen; Zweck und Einschränkungen der Cluster-Policies dokumentieren.

## <a id="usage-policies">5. Usage-Policy-Strategie gestalten</a>

„Usage Policies bestehen aus Tags, die auf jede Serverless-Compute-Aktivität eines der Policy zugewiesenen Nutzers angewendet werden. Die Tags werden in den Rechnungsdatensätzen protokolliert, wodurch sich ausgewählte Serverless-Nutzung bestimmten Budgets zuordnen lässt."

**Anwendungsfälle:** Serverless-Compute-Kosten bestimmten Abteilungen/Projekten zuordnen; Kosten je Umgebung (Dev, Staging, Prod) nachverfolgen; Ausgaben gegen Budgetgrenzen überwachen; Kostenberichte je Geschäftsbereich/Kostenstelle erzeugen.

**Best Practices:** Usage Policies je Abteilung/Projekt erstellen; konsistente Tagging-Schemata über alle Compute-Ressourcen hinweg nutzen; Budgetnutzung über System-Tabellen und Dashboards überwachen; Alerts für Budgetschwellenwerte einrichten; Budgetzuweisungen vierteljährlich überprüfen und anpassen.

**Technisches Detail:** „Nachdem eine Policy auf ein Notebook, einen Job oder eine Pipeline angewendet wurde, propagiert Databricks alle Tags der Policy in die `custom_tags`-Spalte der System-Tabelle `system.billing.usage`."

## <a id="monitoring">6. Nutzung und Kosten überwachen</a>

„Vorgefertigte Nutzungs-Dashboards in Workspaces importieren, um Account- und Workspace-Ebenen-Nutzung zu überwachen."

**Best Practices:** vorgefertigte Nutzungs-Dashboards importieren und anpassen; Nutzungstrends nach Workspace, Nutzer und Compute-Typ überwachen; Alerts für ungewöhnliche Ausgabenmuster einrichten; Nutzungsberichte monatlich mit Finance-Teams überprüfen; System-Tabellen für individuelle Nutzungsanalysen verwenden.

## <a id="access-control">7. Zugriffskontroll-Strategie gestalten</a>

„Bei einer Standard-Databricks-Installation können alle Nutzer Workspace-Objekte erstellen und ändern, sofern ein Administrator die Workspace-Zugriffskontrolle nicht aktiviert."

**Muster:** Permissive (Standard) — alle Nutzer können Cluster, Jobs, Notebooks erstellen; Restricted — Nutzer benötigen explizite Berechtigungen für Workspace-Objekte; Segregated — unterschiedliche Teams haben Zugriff auf unterschiedliche Workspace-Ressourcen.

**Best Practices:** Workspace-Zugriffskontrolle für Produktionsumgebungen aktivieren; Gruppen statt einzelner Nutzer zur Berechtigungsverwaltung nutzen; Least-Privilege-Zugriff implementieren; Workspace-Berechtigungen regelmäßig überprüfen und auditieren; Zugriffskontrollrichtlinien im Runbook dokumentieren.

## <a id="workspace-settings">8. Workspace-Einstellungen überprüfen</a>

„Die Workspace-Settings-Seite in der Admin-Console enthält eine große Anzahl wichtiger Einstellungen, von denen viele nicht über APIs abgedeckt sind (und daher nicht automatisiert werden können)." Alle diese Einstellungen sollten überprüft werden, bevor ein Workspace produktionsreif gemacht wird.

**Externe Ressource:** den Security-Best-Practices-Leitfaden herunterladen (`https://www.databricks.com/trust/security-features/best-practices`) und die dortigen Vorschläge entsprechend umsetzen.

### Kritische zu prüfende Einstellungen

- **Access/Visibility Control:** standardmäßig aktiviert. Steuert Sichtbarkeit von Workspace, Cluster, Pool und Jobs.
- **Table Access Control:** standardmäßig deaktiviert. Erwägen, dies deaktiviert zu lassen und stattdessen Unity Catalog für granulare Tabellen-ACLs zu nutzen.
- **Enforce User Isolation:** standardmäßig deaktiviert. Aktivieren, um „No Isolation"-Cluster zu vermeiden.
- **Container Services:** standardmäßig deaktiviert. Aktivieren, um benutzerdefinierte Docker-Container zu erlauben.
- **Repos Git Allow Lists:** standardmäßig deaktiviert. Erwägen zu aktivieren, um zugängliche Repositories einzuschränken.
- **Exfiltration-Schutzmaßnahmen:** erwägen, folgende Features zur Vermeidung von Datenexfiltration zu deaktivieren: Download-Button für Notebook-Ergebnisse, Datenupload über die UI, Notebook-Export, Notebook-Table-Clipboard-Feature, MLflow-Run-Artifact-Download.
- **Interactive Notebook Results Storage:** aktivieren, um Ergebnisse im eigenen Account zu speichern.

**Best Practices:** alle Workspace-Einstellungen vor dem Produktivbetrieb überprüfen; Features entsprechend Sicherheits-/Compliance-Anforderungen aktivieren; exfiltrationsermöglichende Features für sensible Workspaces deaktivieren; Workspace-Einstellungen und Begründung im Runbook dokumentieren; IaC (Terraform) zur Verwaltung von Workspace-Einstellungen nutzen, wo möglich.

## <a id="empfehlungen">9. Empfehlungen</a>

**Empfohlene Praktiken:**

- Serverless Compute als primäre Option für SQL, Notebooks, Jobs und Lakeflow-Pipelines nutzen.
- Initiale Konfiguration für Cluster und SQL Warehouses erstellen, dann anhand realistischer Lasten verfeinern.
- Kosten-/Performance-Trade-off beim Kapazitätsdesign berücksichtigen.
- Cluster-Policies nutzen, um Berechtigungen einzuschränken und angemessene Clustergrößen durchzusetzen.
- Usage Policies nutzen, um Serverless-Kosten Abteilungen/Projekten zuzuordnen.
- Nutzung über System-Tabellen und vorgefertigte Dashboards überwachen.
- Workspace-Zugriffskontrolle für Produktionsumgebungen aktivieren.
- Workspace-Einstellungen vor dem Produktivbetrieb sorgfältig überprüfen.

**Zu vermeidende Praktiken:**

- Cluster in der Produktion manuell ohne Cluster-Policies erstellen.
- Unbegrenzte Clustergrößen oder Instance-Typen ohne Kontrollen erlauben.
- Testen mit realistischen Workloads vor der Finalisierung der Clustergrößen überspringen.
- Exfiltrationsermöglichende Features ohne Sicherheits-Review aktivieren.
- Ohne Überprüfung aller Workspace-Einstellungen in Produktion deployen.

## <a id="ergebnisse">10. Ergebnisse der Phase</a>

Nach Abschluss dieser Phase sollten vorliegen: definierte Compute-Strategie (Serverless vs. Classic je Workload); entworfene Cluster-Sizing-Strategie für Classic-Compute-Workloads; entworfene SQL-Warehouse-Sizing-Strategie; entworfene Cluster-Policy-Strategie mit Policies je Team/Anwendungsfall; entworfene Usage-Policy-Strategie für Serverless-Kostenzuordnung; definierter Nutzungsüberwachungsansatz mit Dashboards und Alerts; entworfene Zugriffskontroll-Strategie; überprüfte und dokumentierte Workspace-Einstellungen; definierte Kostenoptimierungsstrategie (z. B. Spot-Instanzen, Autoscaling, Right-Sizing).

**Nächste Phase:** Phase 9 — Observability-Strategie gestalten (siehe [09 Observability-Strategie.md](09%20Observability-Strategie.md)).

## <a id="quelle">11. Quelle</a>

- https://docs.databricks.com/aws/en/lakehouse-architecture/deployment-guide/compute

**Stand:** 2026-08-21.
