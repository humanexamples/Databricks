# Notebook-Testing Grundlagen

Unit-Testing-Grundlagen für Notebooks (Scope, Organisationsansätze je Sprache, Testing-Frameworks) sowie praktische Testmuster (unittest, Widgets für Test-/Normal-Modus, Testcode auslagern via `%run`, Testen mit Git Folders). Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Scope und Einschränkungen](#scope)
2. [Organisationsansätze je Sprache](#organisation)
3. [Gut entworfene Funktionen](#funktionen)
4. [Testing-Frameworks](#frameworks)
5. [Best Practice: nicht gegen Produktionsdaten testen](#produktionsdaten)
6. [Ausführung und Integration](#ausfuehrung)
7. [Praktisches Testmuster: unittest direkt im Notebook](#unittest-direkt)
8. [Praktisches Testmuster: Widgets für Test-/Normal-Modus](#widgets)
9. [Code und Ergebnisse ausblenden](#ausblenden)
10. [Geplante automatisierte Tests](#geplant)
11. [Testcode über `%run` auslagern](#run-auslagern)
12. [Testen mit Git Folders](#git-folders)
13. [Quelle](#quelle)

---

## <a id="scope">1. Scope und Einschränkungen</a>

Unit Testing ist „ein Ansatz zum frühen und häufigen Testen in sich geschlossener Code-Einheiten wie Funktionen." Diese Methodik hilft, Probleme schneller zu erkennen und falsche Annahmen über das Codeverhalten aufzudecken.

Der Leitfaden fokussiert auf grundlegendes Unit Testing mit Funktionen über Python, R, Scala und SQL hinweg. **Ausdrücklich ausgeschlossen:** fortgeschrittene Konzepte wie das Testen von Klassen, Interfaces, Stubs, Mocks und Test Harnesses. Andere Testmethodiken — Integrationstests, Systemtests, Abnahmetests und nicht-funktionale Tests (Performance, Usability) — liegen außerhalb dieses Dokumentationsbereichs.

## <a id="organisation">2. Organisationsansätze je Sprache</a>

### Python und R

Databricks empfiehlt, Funktionen und Tests **außerhalb von Notebooks** zu speichern:

- Funktionen lassen sich in Notebooks und externen Umgebungen wiederverwenden.
- Test-Frameworks sind für externe Ausführung optimiert.
- Der Workspace bietet Tools, um Python-Unit-Tests zu entdecken und nachzuverfolgen.

Alternative Ansätze: Funktionen und Tests in getrennte Notebooks aufteilen, oder beides in einem einzelnen Notebook belassen — beides mit Trade-offs bei Wiederverwendbarkeit und Wartung.

### Scala

Empfohlene Strategie: Funktionen in einem Notebook, Unit Tests in einem separaten Notebook — da externe Speicherung nicht unterstützt wird.

### SQL

Funktionen als SQL User-Defined Functions (UDFs) innerhalb von Schemas speichern und aus SQL-Notebooks heraus aufrufen.

## <a id="funktionen">3. Gut entworfene Funktionen</a>

Funktionen sollten:

- „ein einziges, vorhersehbares Ergebnis zurückgeben und von einem einzigen Datentyp sein."
- boolesche Werte (true/false) für Existenzprüfungen zurückgeben.
- nicht-negative Ganzzahlen für Zeilenanzahlen zurückgeben.
- vermeiden, je nach Bedingung mehrere Datentypen zurückzugeben.

## <a id="frameworks">4. Testing-Frameworks</a>

| Sprache | Framework | Konvention |
|---|---|---|
| Python | pytest | Dateien mit Präfix `test_` |
| R | testthat | Dateien mit Präfix `test` |
| Scala | ScalaTest (FunSuite-Stil) | — |
| SQL | `SELECT`-Statements mit bedingter Logik | — |

Für Python zusätzlich die offiziellen `pyspark.testing.utils`-Hilfsfunktionen (`assertDataFrameEqual`, `assertSchemaEqual`) sowie ein vollständiges Praxisbeispiel mit pytest-Fixtures siehe [07 PySpark-Testing-Utilities und Praxisbeispiel.md](07%20PySpark-Testing-Utilities%20und%20Praxisbeispiel.md).

## <a id="produktionsdaten">5. Best Practice: nicht gegen Produktionsdaten testen</a>

Wichtige Empfehlung: „Es ist Best Practice, Unit Tests **nicht** gegen Funktionen auszuführen, die mit Produktionsdaten arbeiten." Stattdessen synthetische Testdaten erstellen, die die Produktionsstruktur widerspiegeln, oder Views für sicherere Testszenarien nutzen.

## <a id="ausfuehrung">6. Ausführung und Integration</a>

Tests lassen sich manuell ausführen oder zeitplanen. Ergebnisse erscheinen in den Cluster-Driver-Logs. CI/CD-Integration ist möglich, z. B. über GitHub Actions für automatisiertes Testen bei Code-Änderungen (siehe [Developers/CI-CD](../../Developers/CI-CD/)).

## <a id="unittest-direkt">7. Praktisches Testmuster: unittest direkt im Notebook</a>

Die primäre Methode nutzt Pythons eingebautes `unittest`-Modul:

```python
def reverse(s):
    return s[::-1]

import unittest

class TestHelpers(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('abc'), 'cba')

r = unittest.main(argv=[''], verbosity=2, exit=False)
assert r.result.wasSuccessful(), 'Test failed; see logs above'
```

Testfehlschläge erscheinen im Output-Bereich der Zelle. Die Assertion stellt sicher, dass die Test-Suite erfolgreich abgeschlossen wurde.

## <a id="widgets">8. Praktisches Testmuster: Widgets für Test-/Normal-Modus</a>

Databricks Widgets erlauben das Umschalten zwischen Test- und Produktionsausführung innerhalb eines einzelnen Notebooks:

```python
dbutils.widgets.dropdown("Mode", "Test", ["Test", "Normal"])

def reverse(s):
    return s[::-1]

if dbutils.widgets.get('Mode') == 'Test':
    assert reverse('abc') == 'cba'
    print('Tests passed')
else:
    print(reverse('desrever'))
```

Erzeugt ein Dropdown-Menü, mit dem Nutzer ohne Code-Änderungen zwischen Modi wechseln können.

## <a id="ausblenden">9. Code und Ergebnisse ausblenden</a>

Über das Zellen-Aktionsmenü lässt sich „Hide Code" oder „Hide Result" wählen. Wichtig: „Fehler werden angezeigt, selbst wenn Ergebnisse ausgeblendet sind" — Fehlschläge bleiben also unabhängig von den Anzeigeeinstellungen sichtbar.

## <a id="geplant">10. Geplante automatisierte Tests</a>

„Um Tests periodisch und automatisch auszuführen, können geplante Notebooks genutzt werden." Diese Jobs können bei Fehlschlag Benachrichtigungs-E-Mails versenden, was passives Monitoring der Test-Suites ermöglicht.

## <a id="run-auslagern">11. Testcode über `%run` auslagern</a>

Testcode in dedizierten Notebooks isoliert halten:

**`shared-code-notebook`:**

```python
def reverse(s):
    return s[::-1]
```

**`shared-code-notebook-test` (Zelle 1):**

```python
%run ./shared-code-notebook
```

**`shared-code-notebook-test` (Zelle 2):**

```python
import unittest

class TestHelpers(unittest.TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('abc'), 'cba')

r = unittest.main(argv=[''], verbosity=2, exit=False)
assert r.result.wasSuccessful(), 'Test failed; see logs above'
```

## <a id="git-folders">12. Testen mit Git Folders</a>

Für Code in Git-Repositories lassen sich Tests direkt aus Notebooks oder über das Web Terminal ausführen — das ahmt lokale Entwicklungs-Workflows nach. Das ermöglicht CI/CD-artige Automatisierung, die Tests bei jedem Commit über eine GitHub-Actions-Integration auslöst (siehe [Developers/Git Folders (Repos)](../../Developers/Git%20Folders%20%28Repos%29/) und [Developers/CI-CD](../../Developers/CI-CD/)).

## <a id="quelle">13. Quelle</a>

- https://docs.databricks.com/aws/en/notebooks/testing
- https://docs.databricks.com/aws/en/notebooks/test-notebooks

**Stand:** 2026-08-21.
