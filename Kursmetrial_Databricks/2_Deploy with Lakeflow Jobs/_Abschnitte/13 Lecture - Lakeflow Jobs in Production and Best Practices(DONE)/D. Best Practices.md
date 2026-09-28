## D. Best Practices

Compute- & Kostenoptimierung
![Compute and cost optimization icon](./Includes/images/icons/compute_cost_optimization.png)

Verwenden Sie in der Produktion Job- oder **Serverless-Cluster**
Vermeiden Sie interaktive Cluster für Produktions-Workloads
**Aktivieren Sie Photon** für eine schnellere und günstigere Ausführung
**Verwenden Sie Cluster wieder**, um Startzeit und Kosten zu reduzieren

Fokus: effizientes Produktions-Compute mit geringerem Start-Overhead und niedrigeren Kosten.

Orchestrierung & Modularität
![Orchestration and modularity icon](./Includes/images/icons/orchestration_modularity.png)

**Zerlegen Sie komplexe Pipelines** in modulare Jobs/Run Jobs
Verwenden Sie **Multi-Task-Jobs** für eine parallele und skalierbare Ausführung
Wenden Sie bedingte Logik mit Run-If-, If/Else- und For-Each-Tasks an
Begrenzen Sie Jobs auf eine **handhabbare Anzahl von Tasks** für die Wartbarkeit; das Limit liegt bei 1000 Tasks

Fokus: modulares Design, das auch bei wachsenden Workflows wartbar bleibt.

Monitoring & Governance
![Monitoring and governance icon](./Includes/images/icons/monitoring_governance.png)

Verwenden Sie **Service Principals** als Job-Eigentümer und für den Datenzugriff
Konfigurieren Sie Alerts für **Fehler, Verzögerungen und Abschlüsse**
Nutzen Sie **Repair & Run**, um Kosten für die erneute Verarbeitung zu senken
Parametrisieren Sie Tasks für **Wiederverwendbarkeit und Flexibilität**

Fokus: zuverlässige Verantwortlichkeiten, Alerting, Wiederherstellung und wiederverwendbare Ausführungsmuster.

##### Zusätzliche Hinweise
**Praktiken zur Compute- & Kostenoptimierung:**

- **Produktions-Compute:** Verwenden Sie in Produktionsumgebungen immer Job-Cluster oder Serverless Compute, um Kosteneffizienz und Ressourcenisolation sicherzustellen
- **Interaktive Cluster vermeiden:** Reservieren Sie interaktive Cluster ausschließlich für Entwicklung und Ad-hoc-Analysen, um Kostenüberschreitungen und Ressourcenkonflikte in der Produktion zu vermeiden
- **Photon aktivieren:** Aktivieren Sie die Photon-Beschleunigung für alle geeigneten Workloads, um deutliche Performance-Verbesserungen und Kostensenkungen zu erzielen
- **Cluster wiederverwenden:** Gestalten Sie Workflows so, dass Cluster nach Möglichkeit über Tasks hinweg wiederverwendet werden, um den Start-Overhead zu verringern und die Kosteneffizienz zu verbessern

**Praktiken zu Orchestrierung & Modularität:**

- **Modulare Architektur:** Zerlegen Sie komplexe Pipelines mithilfe des Run-Job-Task-Musters in logische, wartbare Module, um Wartbarkeit und Zusammenarbeit im Team zu verbessern
- **Multi-Task-Design:** Nutzen Sie Multi-Task-Jobs für parallele Ausführung und eine bessere Ressourcennutzung, während der Workflow übersichtlich bleibt
- **Fortgeschrittene Logik:** Setzen Sie anspruchsvolle Geschäftslogik mit Run-If-, If/Else- und For-Each-Tasks um, um komplexe reale Szenarien zu bewältigen
- **Task-Limits:** Halten Sie einzelne Jobs unter 1000 Tasks, um Handhabbarkeit und Performance zu wahren, und nutzen Sie modulares Design für größere Workflows

**Praktiken zu Monitoring & Governance:**

- **Nutzung von Service Principals:** Verwenden Sie Service Principals statt persönlicher Konten als Job-Eigentümer und für den Datenzugriff, um Kontinuität und eine ordnungsgemäße Zugriffskontrolle sicherzustellen
- **Umfassendes Alerting:** Konfigurieren Sie Alerts für Fehler, Verzögerungen und Abschlüsse mit geeigneten Eskalations- und Benachrichtigungsstrategien
- **Optimierte Wiederherstellung:** Nutzen Sie die Repair-&-Run-Funktionen, um Kosten und Wiederherstellungszeit bei Fehlern zu minimieren
- **Parametrisierung:** Gestalten Sie Tasks mit sinnvoller Parametrisierung für maximale Wiederverwendbarkeit und Flexibilität über Umgebungen und Anwendungsfälle hinweg

