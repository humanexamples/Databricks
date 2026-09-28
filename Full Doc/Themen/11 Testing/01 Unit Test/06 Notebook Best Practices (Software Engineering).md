# Notebook Best Practices (Software Engineering)

Professionelle Entwicklungspraktiken für Databricks-Notebooks: Versionskontrolle, Code-Modularität, Dependency-Management, Teststrategie, automatisierte Job-Ausführung und CI/CD-Integration — anhand eines durchgängigen COVID-Analyse-Beispiels. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Versionskontroll-Integration](#versionskontrolle)
2. [Code-Modularität und -Sharing](#modularitaet)
3. [Dependency-Management](#dependencies)
4. [Teststrategie](#teststrategie)
5. [Automatisierte Job-Ausführung](#jobs)
6. [CI/CD-Integration](#cicd)
7. [Empfohlene Repository-Struktur](#repo-struktur)
8. [Implementierungsvoraussetzungen](#voraussetzungen)
9. [Workflow-Zusammenfassung](#workflow)
10. [Quelle](#quelle)

---

## <a id="versionskontrolle">1. Versionskontroll-Integration</a>

Die grundlegende Praxis besteht darin, Databricks-Notebooks mit Remote-Git-Repositories zu verbinden. Nutzer richten Git Folders im Databricks-Workspace ein, die mit GitHub synchronisieren und kollaborative Entwicklung sowie Änderungsverfolgung ermöglichen. Der Workflow nutzt Branches für unabhängige Arbeit — „eine Software-Engineering-Best-Practice", die Entwicklern erlaubt, getrennt vom Produktions-`main`-Branch an Dateien zu arbeiten (siehe [Developers/Git Folders (Repos)](../../Developers/Git%20Folders%20%28Repos%29/)).

## <a id="modularitaet">2. Code-Modularität und -Sharing</a>

Statt monolithischer Notebooks zu pflegen, betont der Leitfaden das Extrahieren wiederverwendbarer Funktionen in gemeinsam genutzte Module. Das bietet mehrere Vorteile: „ermöglicht die Nutzung dieser Funktionen mit anderen ähnlichen Notebooks" und hilft, „vorhersehbarere und konsistentere Notebook-Ergebnisse sicherzustellen."

**Beispiel:** ein Modul `covid_analysis/transforms.py` mit vier Funktionen:

- `filter_country()` — filtert Daten nach Ländercode.
- `pivot_and_clean()` — reorganisiert Daten und behandelt fehlende Werte.
- `clean_spark_cols()` — standardisiert Spaltenbenennungskonventionen.
- `index_to_col()` — konvertiert Index-Daten zu Spalten.

## <a id="dependencies">3. Dependency-Management</a>

Professionelle Praxis erfordert explizite Abhängigkeitsdeklaration. Eine `requirements.txt`-Datei spezifiziert exakte Paketversionen, was Reproduzierbarkeit verbessert: „Für bessere Kompatibilität lassen sich diese Versionen mit den auf dem All-Purpose-Cluster installierten Versionen abgleichen."

## <a id="teststrategie">4. Teststrategie</a>

Das separate Testen von gemeinsam genutztem Code (getrennt vom Notebook selbst) ist eine kritische Best Practice: „Schlägt der gemeinsam genutzte Code fehl, würde vermutlich auch das Notebook selbst fehlschlagen. Fehler im gemeinsam genutzten Code sollten zuerst erkannt werden, bevor das Haupt-Notebook letztlich fehlschlägt."

Die Testimplementierung nutzt pytest mit Fixtures und Mock-Daten. Die Testdateistruktur folgt pytest-Konventionen: `test_*.py` oder `*_test.py`. Beispiel-Testfunktionen validieren:

- Filteroperationen liefern die erwarteten Ländercodes.
- fehlende Werte werden korrekt behandelt.
- Spaltenbenennungskonventionen werden angewendet.
- Index-zu-Spalte-Konvertierungen funktionieren wie beabsichtigt.

## <a id="jobs">5. Automatisierte Job-Ausführung</a>

Statt manueller Notebook-Läufe automatisieren Databricks Jobs die Ausführung. Jobs können on-demand oder zeitgesteuert laufen, mit Task-Abhängigkeiten, die sequenzielle Ausführung sicherstellen. Jobs referenzieren committete Repository-Versionen statt Workspace-Arbeitskopien, was Konsistenz sicherstellt.

## <a id="cicd">6. CI/CD-Integration</a>

GitHub-Actions-Workflows ermöglichen automatisiertes Testen, wenn Änderungen ins Repository gemerged werden. Wichtige Sicherheitsempfehlung: „Aus Sicherheitsgründen rät Databricks davon ab, den persönlichen Access Token des Databricks-Workspace-Nutzers an GitHub weiterzugeben. Stattdessen empfiehlt Databricks, GitHub einen Databricks-Access-Token zu geben, der einem Databricks-Service-Principal zugeordnet ist" (siehe [Developers/CI-CD](../../Developers/CI-CD/) und [Developers/Git Folders (Repos)/04 CI-CD und Automatisierung.md](../../Developers/Git%20Folders%20%28Repos%29/04%20CI-CD%20und%20Automatisierung.md)).

Das Beispiel triggert das Notebook `run_unit_tests` bei Pull Requests und liefert unmittelbares Feedback zu Code-Änderungen.

## <a id="repo-struktur">7. Empfohlene Repository-Struktur</a>

```
├── covid_analysis/
│   └── transforms.py
├── notebooks/
│   ├── covid_eda_modular
│   ├── covid_eda_raw (optional)
│   └── run_unit_tests
├── requirements.txt
└── tests/
    ├── testdata.csv
    └── transforms_test.py
```

## <a id="voraussetzungen">8. Implementierungsvoraussetzungen</a>

- ein Remote-Git-Repository (GitHub empfohlen).
- ein Databricks-Workspace.
- ein All-Purpose-Cluster für Entwicklung und Job-Ausführung.
- GitHub-Credentials und Personal Access Tokens mit `repo`- und `workflow`-Berechtigungen.

## <a id="workflow">9. Workflow-Zusammenfassung</a>

Der vollständige Workflow durchläuft: Git-Konnektivität etablieren, initiale Notebooks importieren und ausführen, gemeinsam genutzten Code in Module extrahieren, gemeinsam genutzte Funktionalität testen, Ausführung über Jobs automatisieren und optional CI/CD für kontinuierliches Testen bei Code-Änderungen implementieren.

## <a id="quelle">10. Quelle</a>

- https://docs.databricks.com/aws/en/notebooks/best-practices
- https://www.databricks.com/blog/2022/06/25/software-engineering-best-practices-with-databricks-notebooks.html (inhaltsgleiche Blog-Fassung)

**Stand:** 2026-08-21.
