# Phase 9: Observability-Strategie gestalten

Teil der [Production Planning](Uebersicht.md)-Reihe. Behandelt System-Tabellen, Job-/Pipeline-Monitoring, Spark-Performance-Monitoring, Datenqualitäts-Monitoring, Model-Monitoring und Third-Party-Integrationen.

## Abschnittsübersicht

1. [System-Tabellen-Strategie](#system-tabellen)
2. [Job- und Pipeline-Monitoring](#job-pipeline)
3. [Spark-Performance-Monitoring](#spark-performance)
4. [Datenqualitäts-Monitoring](#datenqualitaet)
5. [Model-Monitoring-Strategie](#model-monitoring)
6. [Third-Party-Integration](#third-party)
7. [Ergebnisse der Phase](#ergebnisse)
8. [Quelle](#quelle)

---

## <a id="system-tabellen">1. System-Tabellen-Strategie gestalten</a>

System-Tabellen dienen als „ein von Databricks gehosteter analytischer Speicher der operativen Daten des Accounts." Kernfähigkeiten:

- Billing- und Nutzungsverfolgung.
- Audit-Logs für Workspace-Aktivitäten.
- Query-History-Analyse.
- Job-Run-Monitoring.
- Data-Lineage-Verfolgung.
- Cluster-Event-Monitoring.

**Anwendungsfälle:** Kostenoptimierung, Sicherheitsüberwachung, Performance-Analyse, Kapazitätsplanung und Data Governance.

**Best Practices:** System-Tabellen über alle Metastores hinweg aktivieren; Dashboards und Alerts erstellen; regelmäßig auf Optimierungspotenzial abfragen; mit Audit-Logs kombinieren; Metriken/Schwellenwerte dokumentieren; ungenutzte Ressourcen identifizieren.

**Beispiel-Monitoring-Queries:** teuerste Queries; fehlgeschlagene Jobs nach Workspace/Nutzer; seit über 24 Stunden ungenutzte Cluster; häufig genutzte Tabellen/Volumes; Lineage kritischer Produktionstabellen.

## <a id="job-pipeline">2. Job- und Pipeline-Monitoring</a>

**Betonte Muster:** „Echtzeit-Alerting" für kritische Fehlschläge; Trendanalyse über Workflow- und Pipelines-Monitoring; Anomalieerkennung über SQL-Alerts; SLA-Monitoring gegen erwartete Laufzeiten; Abhängigkeitsverfolgung für vorgelagerte Fehlschläge.

Pipeline-spezifische Überlegungen betreffen Lakeflow-Observability, Checkpoints für inkrementelle Verarbeitung, Datenaktualitäts-Fenster und Fehlerbehandlungsstrategien.

## <a id="spark-performance">3. Spark-Performance-Monitoring</a>

### Query Profile (Serverless/SQL Warehouses)

Fähigkeiten: Ausführungspläne visualisieren, teure Operationen identifizieren, Data Skew analysieren, Optimierungsempfehlungen einsehen.

### Spark UI (Classic Compute)

Ermöglicht: Stage-Ausführung überwachen, Data Skew über Task-Dauer-Varianz identifizieren, Speicher-/Spill-Metriken verfolgen, Executor-Metriken einsehen, Shuffle-Muster analysieren.

## <a id="datenqualitaet">4. Datenqualitäts-Monitoring gestalten</a>

Lakehouse Monitoring bietet Time-Series-Monitore, Snapshot-Monitore, statistisches Profiling, Data-Drift-Erkennung und Anomalie-Alerting.

**Monitoring-Muster:** Fokus auf geschäftskritische Tabellen in der Gold-Schicht; Schema-Compliance-Validierung in der Silver-Schicht; Ingestion-Verifikation in der Bronze-Schicht; Echtzeit-Alerting-Fähigkeiten; Pipeline-Latenz-Verfolgung.

## <a id="model-monitoring">5. Model-Monitoring-Strategie gestalten</a>

Model-Serving-Observability verfolgt Endpoint-Gesundheit, Invocation-Metriken, Inference-Tabellen, Modellversions-Nutzung und Fehlerraten.

**Muster:** Echtzeit-Anomalie-Alerting; SLA-Compliance-Monitoring; Inference-Analyse zur Drift-Erkennung; A/B-Testing über Versionen hinweg; automatisierte Rollback-Verfahren.

## <a id="third-party">6. Third-Party-Integrationsstrategie gestalten</a>

Genannte Optionen: Datadog, Prometheus, AWS CloudWatch und AWS-CloudTrail-Integration für zentralisierte Observability.

## <a id="ergebnisse">7. Ergebnisse der Phase</a>

Nach Abschluss dieser Phase sollten vorliegen: dokumentierte System-Tabellen-Strategie; konfigurierte Job-/Pipeline-Alerts; Spark-Monitoring-Ansatz; Datenqualitäts-Monitoring für kritische Tabellen; Model-Monitoring-Design; Third-Party-Integrationspläne; dokumentierte SLAs; operative Runbooks.

**Nächste Phase:** Phase 10 — High Availability und Disaster Recovery gestalten (siehe [10 High Availability und Disaster Recovery.md](10%20High%20Availability%20und%20Disaster%20Recovery.md)).

## <a id="quelle">8. Quelle</a>

- https://docs.databricks.com/aws/en/lakehouse-architecture/deployment-guide/observability

**Stand:** 2026-08-21.
