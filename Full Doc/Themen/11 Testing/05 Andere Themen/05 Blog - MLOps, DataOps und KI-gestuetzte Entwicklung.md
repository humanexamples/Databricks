# Blog: MLOps, DataOps und KI-gestützte Entwicklung

Kuratierte Zusammenfassung von vier Databricks-Blogartikeln: ein früher Notebook-/MLflow-Deployment-Ansatz, MLOps vs. DevOps, DataOps-Strategie, und ein aktuelles Benchmarking von KI-Coding-Agents auf Databricks' eigener Codebase. Teil der [Testing](../Uebersicht.md)-Reihe. Blog-Inhalte, keine normative Referenzdokumentation.

## Abschnittsübersicht

1. [Deployment und Testing mit Notebooks und MLflow (2020)](#mlflow-deployment)
2. [MLOps vs. DevOps](#mlops-vs-devops)
3. [Was ist DataOps?](#dataops)
4. [Benchmarking von Coding Agents auf Databricks' Multi-Millionen-Zeilen-Codebase](#coding-agents)
5. [Quelle](#quelle)

---

## <a id="mlflow-deployment">1. Deployment und Testing mit Notebooks und MLflow (2020)</a>

Gemeinsam mit Iterable entwickelter CI/CD-Ansatz, der Databricks-Notebooks mit MLflow und der Databricks CLI integriert — ohne separaten Build-Server. Folgt GitHub-Flow-Prinzipien: Feature-Branches → Notebooks via GitHub-Integration synchronisiert → Staging-Test → Merge in Master → Production.

**Driver-Notebook:** orchestriert den gesamten Prozess, akzeptiert Parameter (Umgebung, MLflow-Experiment-ID, Quellcode-Version), initialisiert Access Tokens für Workspace und Quellcode-Repository.

**Token-Management über Databricks Secrets:**

```
databricks secrets create-scope --scope cicd-test
databricks secrets put --scope cicd-test --key token
```

Abruf: `dbutils.secrets.get(scope="cicd-test", key="token")` — Tokens erscheinen als „[REDACTED]" in Notebooks.

**Deploy-Tracking via MLflow:** statt separater Datenbank/Deployment-UI protokolliert die MLflow-Tracking-API Deployment-Metadaten (Umgebung, App-Name, Notizen) als Run-Parameter.

**Triggering:** eine Delta-Tabelle dient als Source of Truth, die deployte Git-Hashes auf Umgebungen abbildet:

```
dbutils.notebook.run(PATH_PREFIX + s"${git_hash}/notebook", ...)
```

Ermöglicht gleichzeitiges Testen von Version B in Staging, während Version A in Production läuft.

**Testing:** zentralisiert über ein Driver-Notebook, das eine Liste von Test-Notebooks definiert, durchläuft und Ergebnisse mit dem jeweiligen Git-Commit verknüpft in MLflow protokolliert. Eine `TestTracker`-ScalaTest-Fixture überschreibt `withFixture`, um Testdauer und Metadaten automatisch zu protokollieren.

**Vorteile:** keine externe Build-Infrastruktur nötig, automatisiertes Test-Logging, durchsuchbare Testergebnisse, zentrale Deployment-Übersicht, Modell-Performance-Tracking für Drift-/Degradations-Erkennung.

## <a id="mlops-vs-devops">2. MLOps vs. DevOps</a>

Kerndistinktion: DevOps automatisiert Software-Delivery für traditionelle Anwendungen; MLOps erweitert diese Prinzipien, um Code, Daten und Modelle gleichzeitig zu regeln. „88 % der KI-Initiativen scheitern, ohne Produktionsreife zu erreichen" — ohne dedizierte MLOps-Praktiken, da Modelle degradieren, während sich reale Daten unabhängig von Code-Änderungen verschieben.

### Kernunterschiede

| Aspekt | DevOps | MLOps |
|---|---|---|
| Primärer Fokus | Quellcode und Konfiguration | Code, Datensätze, Feature-Tabellen, Modell-Artefakte, Inferenz-Outputs |
| Versionierung | Git-basierte Code-Repositories | Git (Code) + DVC/Delta Lake (Daten) + Model Registries (Modelle) |
| Quality Gates | Unit-/Integrationstests | Datenvalidierung, Modell-Performance-Schwellenwerte, Vorhersage-Genauigkeitsprüfungen |

**Model Drift** ist der schärfste Kontrast: Software bleibt unabhängig von neuen Eingabedaten funktionsfähig, ML-Modelle jedoch degradieren, „während sich reale Datenverteilungen verschieben — Modell-Performance erodiert, selbst wenn der zugrunde liegende Code unverändert bleibt."

**Continuous Training (CT)** ist eine ML-spezifische Anforderung: automatisches Retraining, wenn sich Datenverteilungen verschieben oder die Performance degradiert — ein Konzept ohne Entsprechung im traditionellen DevOps.

### Rollen

**Data Scientists** entwerfen Experimente, entwickeln Trainings-Pipelines, etablieren Monitoring-Metriken. **ML Engineers** fungieren als Brücke zwischen Modellentwicklung und Produktionsbetrieb — bauen CI/CD-Pipelines, etablieren automatisierte Test-Frameworks. **IT-Operations-Teams** provisionieren GPU-/TPU-Ressourcen, pflegen Sicherheitsgrenzen zwischen Dev-/Prod-Catalogs.

### Best-Practice-Roadmap

Progressive Einführung: Datenvalidierung/Schema-Checks zu bestehenden CI/CD-Pipelines hinzufügen, bevor volles Modelltraining automatisiert wird. Dreidomänen-Versionierung: Git (Code), DVC/Delta Lake (Daten), Model Registries (Artefakte mit Versionsnummern, Aliassen, Lineage).

**Wann MLOps vs. DevOps wählen:** MLOps-Investition lohnt sich für geschäftskritische, häufig neu zu trainierende ML-Modelle (Fraud Detection, Empfehlungen). Standard-DevOps genügt für Anwendungen ohne ML-Komponenten. Die meisten Enterprise-Produkte kombinieren beides (Hybrid-Ansatz).

## <a id="dataops">3. Was ist DataOps?</a>

„DataOps ist eine kollaborative Datenmanagement-Praxis, die DevOps-Prinzipien — Continuous Integration, automatisiertes Testen und schnelle Auslieferung — auf den End-to-End-Datenlebenszyklus anwendet." Statt Stabilität zu priorisieren, fördert DataOps eine „Ship-and-iterate"-Kultur.

**Marktwachstum:** DataOps-Plattform-Markt von 3,9 Mrd. USD (2023) auf projizierte 10,9 Mrd. USD (2028); Unternehmen mit etablierten DataOps-Praktiken berichten bis zu 99 % weniger Data-Downtime-Vorfälle.

### Kernprozesse

**Ingestion/Integration:** Standardisierung von Quell-Onboarding, automatisierte Schema-Validierung bei der Ingestion, idempotente Ingestion-Jobs für sichere Wiederholungen.

**Transformation über Medallion-Layer:** Bronze (Rohdaten) → Silver (bereinigt, mit Basis-Deduplizierung) → Gold (kuratiert, mit Geschäftslogik/Aggregationen) — jeder Layer-Übergang ist ein explizites Quality Gate.

**CI/CD:** Pipeline-Änderungen folgen Software-Entwicklungsdisziplin — Versionskontrolle, automatisierte Tests, gestufte Promotion, Peer Review. „Bei einem Produktionsfehlschlag liefert die Versionskontrolle die sofortige Antwort auf 'was hat sich geändert?'"

**Automatisiertes Testen — drei Typen:** Unit Tests (Transformationslogik), Data Contract Tests (Schema/Nullability/Wertebereich zwischen Pipeline-Stufen), Regression Tests (volle Pipelines gegen repräsentative Stichproben).

**Statistical Process Control (SPC):** aus der Fertigung übernommene Control-Chart-Methodik statt statischer Schwellenwerte — Kontrollgrenzen bei zwei/drei Standardabweichungen vom Mittelwert, reduziert False-Positive-Alerts bei erhaltener Sensitivität für echte Abweichungen.

### Rollen

DataOps erweitert die traditionelle Data-Engineering-Rolle über Build-Time hinaus: Pipeline-SLAs besitzen, automatisierte Tests schreiben/pflegen, auf Datenqualitäts-Vorfälle reagieren, an Pipeline-Code-Reviews teilnehmen.

**Governance und Observability:** Unity Catalog liefert automatisiertes Spalten- und Tabellen-Lineage über SQL, Python, R und Scala hinweg — beantwortet „Welche nachgelagerten Datensätze sind betroffen, wenn ich diese Tabelle ändere?" und „Woher stammt diese Zahl im Dashboard?"

### Metriken

**Pipeline Success Rate** (Ziel: über 95 %); **MTTD** (Mean Time to Detect) und **MTTR** (Mean Time to Resolve) — reife DataOps-Praktiken erreichen MTTD unter einer Stunde, MTTR unter vier Stunden. **Datenqualitätsmetriken:** Completeness, Freshness, Schema Validity, Feature Drift.

### DataOps vs. DevOps

Kritischer Unterschied: Software hat deterministische Ein-/Ausgaben, Daten nicht — „das Ziel ist nicht ein fehlerfreier Datenfeed (unmöglich im großen Maßstab), sondern Abweichungen zu erkennen und zu beheben, bevor sie Datenkonsumenten beeinträchtigen." Deshalb der starke Fokus auf SPC und kontinuierliches Monitoring, ohne direkte DevOps-Entsprechung.

## <a id="coding-agents">4. Benchmarking von Coding Agents auf Databricks' Multi-Millionen-Zeilen-Codebase</a>

Databricks entwickelte einen internen Coding-Benchmark, um KI-Agenten anhand echter Engineering-Aufgaben aus der eigenen Produktions-Codebase zu bewerten.

**Kernerkenntnisse:**

1. **Nur eine Tool-Mischung liefert Frontier-Performance** — Modelle clustern in drei Fähigkeitsstufen; teure, hochintelligente Modelle für komplexe Probleme, mittlere Optionen für Routineaufgaben.
2. **Offene Modelle sind produktionsreif** — GLM 5.2 statistisch gleichauf mit Opus 4.8 bei Qualität, aber 1,28 USD statt 1,94 USD je Task.
3. **Token-Preise täuschen bei der Kostenanalyse:** Sonnet 5 ist 1,7x günstiger je Token als Opus 4.8, kostete aber je Task mehr (2,09 USD vs. 1,94 USD), da Sonnet 5 „länger arbeitete und mehr las, um dorthin zu gelangen" (1,9x mehr Tokens).
4. **Harness-Wahl beeinflusst die Effizienz drastisch:** identische Modelle in unterschiedlichen Harnesses zeigten 2x Kostenunterschiede bei gleicher Qualität — der „Pi"-Harness sandte „3x weniger Kontext je Turn."

**Benchmark-Methodik:** Pull Requests aus der eigenen Codebase gefiltert nach Aktualität, menschlicher Autorenschaft (keine Bots/Service-Accounts), Testabdeckung, Selbstständigkeit und Stack-Diversität (Scala, Rust, TypeScript, Protobuf, Bazel).

**Qualitätssicherung:** „Git History Sealing" — die Arbeitskopie wird während jedes Laufs vollständig vom Repository getrennt, um zu verhindern, dass Agenten über die Git-Historie die korrekte Implementierung finden. Tatsächliche Testausführung statt LLM-Richter bestimmt Erfolg — „belohnt sonst richtig klingen statt richtig sein."

**Warum kein öffentlicher Benchmark:** öffentliche Task-Lösungen „sickern mit der Zeit in Trainingsdaten", und bestehende Benchmarks repräsentieren nicht Databricks' 10-Sprachen-Polyglot-Codebase.

## <a id="quelle">5. Quelle</a>

- https://www.databricks.com/blog/2020/01/16/automate-deployment-and-testing-with-databricks-notebook-mlflow.html
- https://www.databricks.com/blog/mlops-vs-devops
- https://www.databricks.com/blog/what-is-dataops
- https://www.databricks.com/blog/benchmarking-coding-agents-databricks-multi-million-line-codebase

**Stand:** 2026-08-21.
