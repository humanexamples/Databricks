# SDP-Integrationstest-Patterns (Praxisbeispiel)

Zwei praktische Muster für Integrationstests mit Spark Declarative Pipelines (SDP, der aktuelle Name für Lakeflow Declarative Pipelines/DLT): (1) Expectations-basierte Tests direkt in der Pipeline, umgebungsparametrisiert für dev/stage/prod, und (2) Job-Tasks-basierte Integrationstests als separate Schritte nach der Pipeline-Ausführung. Teil der [Testing](../Uebersicht.md)-Reihe, Kapitel [02 Integrationstest](../02%20Integrationstest/). Ergänzt [02 Integrationstest-Konzepte auf Databricks.md](02%20Integrationstest-Konzepte%20auf%20Databricks.md) (Abschnitt 5, DLT-Expectations) um ein vollständiges, ausführbares Beispiel.

## Abschnittsübersicht

1. [Methode 1: SDP mit Expectations](#methode-1)
2. [Vollständiges Codebeispiel: `integration_tests_sdp.py`](#codebeispiel)
3. [Methode 2: Lakeflow Jobs mit Tasks](#methode-2)

---

## <a id="methode-1">1. Methode 1: SDP mit Expectations</a>

**Szenario:** Eine SDP ingestiert CSV-Dateien aus dem jeweiligen Catalog (dev, stage, prod) basierend auf einer Pipeline-Konfigurationsvariable — unabhängig von der Zielumgebung wird **dieselbe** SDP mit derselben Transformationslogik (inkl. benutzerdefinierter Funktionen) ausgeführt ("Shared SDP Code"). Daten aus dem Ziel-Catalog werden in `health_bronze` ingestiert, in `health_silver` bereinigt und schließlich in einer Materialized View `chol_age_agg` (Gold-Tabelle) je Umgebung aggregiert.

**Kernidee:** Da für dev und stage statische, bekannte Testdaten verwendet werden, ist das erwartete Ergebnis im Voraus bekannt — das erlaubt es, den gemeinsam genutzten SDP-Code mit **Expectations** zu testen. Zusätzliche Materialized Views ("Test-Materialized-Views") werden während der dev-/stage-Läufe erstellt, die z. B. Zeilenanzahlen zählen, um korrekte Ingestion zu bestätigen — in der Praxis würden deutlich gezieltere Tests ergänzt.

**SDK-Beispiel zum Erstellen und Starten der Pipeline:**

```python
pipeline = DeclarativePipelineCreator(
                            pipeline_name=f"sdk_health_etl_{DA.catalog_dev}", 
                            catalog_name = DA.catalog_name,
                            schema_name = 'default',
                            root_path_folder_name='src',
                            source_folder_names=[
                                'src/sdp/**', 
                                'tests/integration_test/**'],
                            configuration = {
                                'target': 'development',
                                'raw_data_path':f'/Volumes/{DA.catalog_name}/default/health'
                            })

pipeline.create_pipeline()

pipeline.start_pipeline()
```

Die `source_folder_names` binden sowohl den eigentlichen SDP-Quellcode (`src/sdp/**`) als auch die Integrationstest-Dateien (`tests/integration_test/**`) in dieselbe Pipeline ein — die Testlogik läuft also als Teil des regulären Pipeline-Updates.

## <a id="codebeispiel">2. Vollständiges Codebeispiel: `integration_tests_sdp.py`</a>

Vollständiges Beispiel-Notebook, das Methode 1 umsetzt. Nutzt zwei Testfunktionen — eine für Zeilenanzahl-Prüfungen (parametrisiert je Umgebung), eine für Wertebereichs-Prüfungen an der Gold-Tabelle — und führt je nach Ziel-Umgebung eine passende Teilmenge davon aus.

```python
from pyspark import pipelines as dp

## Zielumgebungs-Konfigurationsvariable in der Variable target speichern
target = spark.conf.get("target")

## Basierend auf dem deployten Target die spezifischen Validierungsmetriken für die Tabellen ermitteln.
target_integration_tests_validation = {
    'development': {
        'health_bronze': {
            'total_rows': 7500
        },
        'health_silver': {
            'total_rows': 7500
        }
    },
    'stage': {
        'health_bronze': {
            'total_rows': 35000
        },
        'health_silver': {
            'total_rows': 35000
        }
    }
}

## Erwartete Werte für die Gesamtzeilenanzahl der Tabellen je nach Target (development oder stage) speichern
if target in ('development', 'stage'):
    total_expected_bronze = target_integration_tests_validation[target]['health_bronze']['total_rows']
    total_expected_silver = target_integration_tests_validation[target]['health_silver']['total_rows']


def test_count_table_total_rows(table_name, total_count, target):
    '''
    Zählt die Zeilen der angegebenen Tabelle und vergleicht sie mit den erwarteten Werten für
    development/stage-Daten. Schlägt das Update fehl, wenn die Anzahl nicht übereinstimmt.
    '''
    @dp.table(
        name=f"TEST_{target}_{table_name}_total_rows_verification",
        comment=f"Confirms all rows were ingested from the {target} raw data to {table_name}"
    )
    @dp.expect_all_or_fail({"valid count": f"total_rows = {total_count}"}) 
    def count_table_total_rows():
        return spark.sql(f"""
            SELECT COUNT(*) AS total_rows FROM {table_name}
        """)


def test_gold_table_columns():
    '''
    Prüft die eindeutigen Werte in den Spalten Age_Group und HighCholest_Group der Gold-Tabelle
    chol_age_agg — bestätigt, dass die distinkten Werte dieser Spalten korrekt sind.
    ''' 
    check_silver_calc_columns = {
        "valid age group": "Age_Group in ('0-9', '10-19', '20-29', '30-39', '40-49', '50+', 'Unknown')",
        "valid cholest group": "HighCholest_Group in ('Normal', 'Above Average', 'High', 'Unknown')"
    }

    @dp.table(comment="Check age group and high cholest group in the gold table")
    @dp.expect_all_or_fail(check_silver_calc_columns)
    def test_calculated_columns_age_cholesterol():
        return (dp
                .read("chol_age_agg")
                .select("Age_Group", "HighCholest_Group")
            )


## Die angegebenen Tests je nach Zielumgebung ausführen (development, stage oder production)
if target in ('development','stage'):  ## Dynamischer Integrationstest für dev-/stage-Tabellen
    test_count_table_total_rows('health_bronze',  total_expected_bronze, target)
    test_count_table_total_rows('health_silver',  total_expected_silver, target)
    test_gold_table_columns()
elif target == 'production':  ## In Production nur die Gold-Tabelle testen
    test_gold_table_columns()
```

**Wichtige Muster:**

- **Umgebungsparametrisierung über `target`:** dieselbe Testdatei passt sich über die Pipeline-Konfigurationsvariable `target` (development/stage/production) automatisch an — in Production werden bewusst nur die Gold-Tabellen-Wertebereichsprüfungen ausgeführt (keine Zeilenanzahl-Prüfungen, da Produktionsdatenmengen nicht statisch/bekannt sind), in dev/stage laufen alle Prüfungen gegen bekannte, statische Testdatenmengen.
- **`@dp.expect_all_or_fail(...)`:** löst bei Verstoß einen harten Fehlschlag des Pipeline-Updates aus (im Gegensatz zu `@dp.expect`, das nur protokolliert, ohne das Update zu stoppen — siehe [02 Integrationstest-Konzepte auf Databricks.md](02%20Integrationstest-Konzepte%20auf%20Databricks.md), Abschnitt 5).
- **`TEST_`-Namenskonvention:** Test-Materialized-Views werden klar als `TEST_{target}_{table_name}_total_rows_verification` benannt — leicht von den eigentlichen Datenprodukt-Tabellen zu unterscheiden.
- Die Zeilenanzahl-Erwartungswerte liegen in einer einfachen verschachtelten Dictionary-Struktur — eine von mehreren möglichen Umsetzungen für "Portable and Reusable Expectations".

## <a id="methode-2">3. Methode 2: Lakeflow Jobs mit Tasks</a>

Statt Expectations direkt in der SDP zu nutzen, lässt sich Integrationstest auch als eigener Job mit mehreren sequenziellen Tasks umsetzen:

1. **Unit Tests ausführen** — testet einzelne Funktionen isoliert. Schlägt ein Unit Test fehl, schlägt der gesamte Job fehl (Fail-Fast).
2. **SDP ausführen** — dieselbe SDP wie zuvor, aber **ohne** Expectations (die Datenqualitätsprüfung erfolgt in diesem Muster separat, nicht in der Pipeline selbst).
3. **Integrationstests ausführen** — als Notebooks, die als eigene Tasks im Lakeflow Job konfiguriert sind. Benötigt die korrekten Parameter für die Zielumgebung (dev/stage/prod). Mögliche Prüfungen: Zeilenanzahl in Tabellen zählen, Existenz von Tabellen verifizieren, erwartete Spalten/distinkte Werte prüfen, Wertebereiche von Spalten kontrollieren, Duplikate ausschließen, und mehr.
4. **Visualisierung erstellen** — abschließend, nachdem Unit Tests, Pipeline und Integrationstests erfolgreich durchgelaufen sind.

**Vorteil gegenüber Methode 1:** Trennung von Datenverarbeitung (Pipeline) und Testlogik (separate Job-Tasks) — Tests lassen sich unabhängig von der Pipeline warten, erweitern und im Job-UI einzeln nachvollziehen (jeder Task zeigt individuell Erfolg/Fehlschlag).

**Vorteil von Methode 1:** Tests laufen als Teil des Pipeline-Updates selbst, ohne zusätzlichen Orchestrierungs-Job — Ergebnisse landen automatisch im Pipeline-Event-Log (siehe [02 Integrationstest-Konzepte auf Databricks.md](02%20Integrationstest-Konzepte%20auf%20Databricks.md), Abschnitt 5, zu denselben Vorteilen bei DLT-Expectations allgemein).
