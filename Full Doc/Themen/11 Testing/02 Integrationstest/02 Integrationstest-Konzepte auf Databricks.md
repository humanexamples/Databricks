# Integrationstest-Konzepte auf Databricks

Databricks hat keine einzelne, dedizierte "Integrationstest"-Dokumentationsseite — die Konzepte sind über mehrere offizielle Doku-Seiten und Blogartikel verteilt. Diese Datei bündelt sie zu einem zusammenhängenden Bild: was auf Databricks als Integrationstest gilt, welche Werkzeuge dafür existieren, und wie sich das von Unit Testing (siehe [01 Unit Test](../01%20Unit%20Test/)) abgrenzt. Teil der [Testing](../Uebersicht.md)-Reihe. Synthese aus bereits an anderer Stelle dokumentierten, doc-/blog-verifizierten Quellen — vollständige Details jeweils in den verlinkten Dateien.

## Abschnittsübersicht

1. [Abgrenzung zu Unit Testing](#abgrenzung)
2. [Drei-Ebenen-Testmodell aus den Developer Best Practices](#drei-ebenen)
3. [Lakeflow-Pipelines-„Unit"-Testing ist funktional Integrationstest](#ldp-testing)
4. [Workflow-basierte Integrationstests (DLT-DevOps-Blog)](#workflow-basiert)
5. [DLT-Expectations als leichtgewichtige Integrationstest-Alternative](#expectations)
6. [Integrationstests in MLOps-Pipelines (Staging-Stufe)](#mlops-staging)
7. [Data Contract Tests und Regression Tests (DataOps)](#dataops-tests)
8. [Bundle-Validierung als Vorstufe zum Integrationstest](#bundle-validate)
9. [Zusammenfassung: Werkzeugkasten je Integrationstest-Typ](#werkzeugkasten)
10. [Quelle](#quelle)

---

## <a id="abgrenzung">1. Abgrenzung zu Unit Testing</a>

Unit Testing prüft „in sich geschlossene Code-Einheiten wie Funktionen" isoliert — siehe [01 Unit Test/01 Notebook-Testing Grundlagen.md](../01%20Unit%20Test/01%20Notebook-Testing%20Grundlagen.md). Integrationstests prüfen dagegen das **Zusammenspiel mehrerer Komponenten** — mehrere Transformationsschritte, eine ganze Pipeline, oder eine Pipeline zusammen mit der Anwendung, die sie konsumiert. Auf Databricks taucht dieser Unterschied in mehreren Quellen konsistent auf, allerdings ohne einheitliche Terminologie — offizielle Doku-Seiten nennen Pipeline-Kettentests „Unit Testing" (siehe Abschnitt 3), während Blogartikel und die Developer-Best-Practices-Seite den Begriff „Integration Testing" für dieselbe Ebene verwenden.

## <a id="drei-ebenen">2. Drei-Ebenen-Testmodell aus den Developer Best Practices</a>

Die offizielle Developer-Best-Practices-Seite (siehe [05 Andere Themen/04 Allgemeine Developer Best Practices.md](../05%20Andere%20Themen/04%20Allgemeine%20Developer%20Best%20Practices.md), Abschnitt „Testing und Observability") definiert drei Testing-Ebenen entlang des Bundle-Promotion-Pfads:

1. **Unit Tests** — Geschäftslogik mit `pytest` abdecken, blockierend bei Pull-Request-Fehlschlägen.
2. **Bundle-Validierung** — `bundle validate` lokal und `bundle deploy` in Nicht-Produktions-Workspaces in CI (siehe Abschnitt 8 dieser Datei).
3. **Integrationstests** — in Staging, mit Abschlussprüfungen und Datenqualitäts-Assertions.

Diese dritte Ebene ist der eigentliche Integrationstest im engeren Sinne: die vollständig deployte Pipeline/den vollständig deployten Job in einer produktionsnahen Umgebung laufen lassen und das Gesamtergebnis prüfen — nicht mehr einzelne Funktionen isoliert.

## <a id="ldp-testing">3. Lakeflow-Pipelines-„Unit"-Testing ist funktional Integrationstest</a>

Das offizielle Beta-Testing-Framework für Lakeflow Declarative Pipelines (siehe [01 Lakeflow Pipelines Unit Testing.md](01%20Lakeflow%20Pipelines%20Unit%20Testing.md)) heißt offiziell „Unit Testing", deckt aber laut eigener Beschreibung explizit „Ketten abhängiger Transformationen (Bronze → Silver → Gold-Muster)" ab — also das Zusammenspiel mehrerer Tabellen/Schritte, nicht nur eine isolierte Funktion. Die `test_pipeline.run(test_spark, set([...]))`-API kann gezielt eine gesamte Kette von Tabellen gemeinsam ausführen und validieren (siehe dort Abschnitt 11, Aggregations-Beispiel mit `test_counts`/`test_counts_full_dataframe`, das Rohdaten → Users-Tabelle → Counts-Aggregation gemeinsam testet). Funktional ist dies also der Integrationstest-Anwendungsfall dieses Kapitels, terminologisch aber als „Unit Testing" benannt — daher die Doppel-Einordnung in diesem Projekt (Datei liegt unter „Integrationstest", der Name der Databricks-Funktion bleibt aber „Unit Testing").

## <a id="workflow-basiert">4. Workflow-basierte Integrationstests (DLT-DevOps-Blog)</a>

Der Blogartikel „DevOps für Delta Live Tables" (siehe [03 CI-CD/02 Blog - CI-CD Praxisbeispiele und Software-Engineering-Kultur.md](../03%20CI-CD/02%20Blog%20-%20CI-CD%20Praxisbeispiele%20und%20Software-Engineering-Kultur.md), Abschnitt 1) beschreibt zwei konkrete Integrationstest-Ansätze für DLT/Lakeflow-Pipelines, bevor das offizielle Testing-Framework aus Abschnitt 3 existierte:

**Workflow-basierte Integrationstests:** Implementierung als Databricks Workflow mit mehreren sequenziellen Tasks — (1) Testdaten für die Pipeline-Ausführung aufsetzen, (2) die DLT-Pipeline gegen diese Testdaten ausführen, (3) die produzierten Ergebnisse validieren. Erfordert Zusatzcode für Setup und Validierung, liefert aber vollständige Pipeline-Validierung.

**Empfehlung des Artikels:** DLT-native Expectations mit Fail-Operatoren (siehe Abschnitt 5) statt des Workflow-Ansatzes, da letzterer zusätzliche Compute-Ressourcen und Zusatzcode benötigt.

## <a id="expectations">5. DLT-Expectations als leichtgewichtige Integrationstest-Alternative</a>

```python
@dlt.table
@dlt.expect("valid_types", "type IN ('A', 'B', 'C')")
def silver_validation():
    return dlt.read("silver_layer")
```

Vorteile laut Blogartikel: keine zusätzlichen Compute-Ressourcen nötig, integriert sich in die bestehende Pipeline-Ausführung, Ergebnisse werden ins DLT-Event-Log protokolliert, lässt sich zu wiederverwendbaren Expectation-Bibliotheken ausbauen. Dies ist der pragmatische Mittelweg zwischen reinem Unit Testing und vollem Integrationstest — Datenqualität wird kontinuierlich während des normalen Pipeline-Laufs geprüft, statt in einem separaten Testlauf.

**Vollständiges Praxisbeispiel:** [03 SDP-Integrationstest-Patterns (Praxisbeispiel).md](03%20SDP-Integrationstest-Patterns%20%28Praxisbeispiel%29.md) demonstriert diesen Ansatz mit vollständigem Code — umgebungsparametrisierte `@dp.expect_all_or_fail`-Prüfungen (dev/stage/prod) über eigene `TEST_`-Materialized-Views, sowie als Alternative das Job-Tasks-Muster aus Abschnitt 4 als konkretes, lauffähiges Beispiel.

## <a id="mlops-staging">6. Integrationstests in MLOps-Pipelines (Staging-Stufe)</a>

Der offizielle MLOps-Workflow (siehe [05 Andere Themen/02 MLOps-Workflow.md](../05%20Andere%20Themen/02%20MLOps-Workflow.md), Abschnitt 4 „Staging-Stufe") definiert Integrationstests als eigenen CI-Schritt: „CI-Prozesse führen anschließend Integrationstests aus, die alle Pipelines (Feature Engineering, Modelltraining, Inferenz, Monitoring) durchlaufen, um korrektes Zusammenspiel zu verifizieren." Die Staging-Umgebung soll Production dabei so genau wie möglich widerspiegeln; für Echtzeit-Inferenz muss Serving-Infrastruktur temporär erstellt und getestet werden. Um Testfidelity gegen Ausführungsgeschwindigkeit/Kosten abzuwägen, können Modelle auf kleinen Datensubsets mit weniger Iterationen trainiert werden, statt vollständiger Skalierung.

## <a id="dataops-tests">7. Data Contract Tests und Regression Tests (DataOps)</a>

Der DataOps-Blogartikel (siehe [05 Andere Themen/05 Blog - MLOps, DataOps und KI-gestuetzte Entwicklung.md](../05%20Andere%20Themen/05%20Blog%20-%20MLOps%2C%20DataOps%20und%20KI-gestuetzte%20Entwicklung.md), Abschnitt „Was ist DataOps?") nennt drei Testtypen, von denen zwei genuine Integrationstest-Charakteristik haben:

- **Data Contract Tests** — erzwingen Schema, Nullability-Constraints und Wertebereichs-Vereinbarungen **zwischen** Pipeline-Stufen (also an der Schnittstelle zweier Komponenten — das definierende Merkmal eines Integrationstests).
- **Regression Tests** — führen die **vollständige Pipeline** gegen repräsentative Stichproben aus und vergleichen Output-Metriken mit erwarteten Baselines.

(Der dritte Typ, Unit Tests für einzelne Transformationslogik, gehört zu [01 Unit Test](../01%20Unit%20Test/).)

## <a id="bundle-validate">8. Bundle-Validierung als Vorstufe zum Integrationstest</a>

`databricks bundle validate` (siehe [Developers/Databricks Asset Bundles/01 Grundlagen.md](../../Developers/Databricks%20Asset%20Bundles/01%20Grundlagen.md), Abschnitt 6.3) prüft nur die YAML-Konfiguration auf syntaktische/strukturelle Korrektheit — kein tatsächlicher Datenfluss. Die Developer-Best-Practices-Seite (siehe Abschnitt 2 dieser Datei) reiht dies explizit zwischen Unit Tests und Integrationstests ein: „`bundle validate` lokal und `bundle deploy` in Nicht-Produktions-Workspaces in CI" — bevor die eigentlichen Integrationstests in Staging laufen.

## <a id="werkzeugkasten">9. Zusammenfassung: Werkzeugkasten je Integrationstest-Typ</a>

| Anwendungsfall | Werkzeug/Ansatz | Siehe |
|---|---|---|
| Kette abhängiger Lakeflow-Pipeline-Tabellen | `TestPipeline.run()` mit mehreren Tabellennamen | [01 Lakeflow Pipelines Unit Testing.md](01%20Lakeflow%20Pipelines%20Unit%20Testing.md) |
| Datenqualität kontinuierlich während des Pipeline-Laufs | DLT/LDP-Expectations (`@dlt.expect`) | Abschnitt 5 dieser Datei |
| Vollständige Pipeline in eigenem Testlauf | Workflow mit Setup-/Run-/Validate-Tasks | Abschnitt 4 dieser Datei |
| ML-Pipeline-Zusammenspiel (Feature Engineering → Training → Inferenz → Monitoring) | Staging-CI-Schritt im MLOps-Workflow | Abschnitt 6 dieser Datei |
| Schema-/Wertebereich-Verträge zwischen Pipeline-Stufen | Data Contract Tests (Great Expectations, Soda Core, dbt-Tests) | Abschnitt 7 dieser Datei |
| Konfigurations-/Struktur-Korrektheit vor dem eigentlichen Test | `databricks bundle validate` | Abschnitt 8 dieser Datei |
| Umgebungsparametrisierte SDP-Expectations (dev/stage/prod) + Job-Tasks-Alternative, mit vollständigem Code | `@dp.expect_all_or_fail`, `TEST_`-Materialized-Views | [03 SDP-Integrationstest-Patterns (Praxisbeispiel).md](03%20SDP-Integrationstest-Patterns%20%28Praxisbeispiel%29.md) |

## <a id="quelle">10. Quelle</a>

Diese Datei ist eine Synthese ohne eigene neue Primärquelle — alle Aussagen sind in den verlinkten Dateien dieses Projekts einzeln quellenbelegt (offizielle Databricks-Dokumentation bzw. Databricks-Blog, siehe dortige Quellenangaben).

**Stand:** 2026-08-21.
