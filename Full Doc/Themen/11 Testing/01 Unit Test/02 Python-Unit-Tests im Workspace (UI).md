# Python-Unit-Tests im Workspace (UI)

Die in den Workspace integrierten Tools zum Entdecken, Ausführen und Nachverfolgen von Python-Unit-Tests: Testing-Sidebar, Inline-Ausführungscontrols und Ergebnis-Panel. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Gültige Python-Testdateien](#testdateien)
3. [Tests-Sidebar-Panel](#sidebar)
4. [Tests über Inline-Icons ausführen](#inline)
5. [Inline-Fehleranzeige](#fehleranzeige)
6. [Testergebnisse-Panel](#ergebnisse)
7. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

Databricks bietet integrierte Tools, um Python-Unit-Tests direkt im Workspace zu entdecken, auszuführen und nachzuverfolgen — mit einer Testing-Sidebar, Inline-Ausführungscontrols und einem dedizierten Ergebnis-Panel.

## <a id="testdateien">2. Gültige Python-Testdateien</a>

Databricks folgt pytest-Namenskonventionen zur Erkennung von Testdateien, -klassen und -methoden.

**Erkannte Dateinamensmuster:** `test_*.py`, `*_test.py`.

**Erkennungskonventionen:**

- mit „test" beginnende Funktionen/Methoden außerhalb einer Klasse.
- mit „test" beginnende Funktionen/Methoden innerhalb von mit „Test" beginnenden Klassen (ohne `__init__`-Methode).
- mit `@staticmethod` oder `@classmethod` dekorierte Methoden innerhalb von „Test"-Klassen.

**Beispielstruktur:**

```python
class TestClass():    
    def test_1(self):        
        assert True    
    def test_3(self):        
        assert 4 == 3

def test_foo():    
    assert "foo" == "bar"
```

**Hinweis:** Das Tests-Icon erscheint nur, wenn die Datei im Editor-Tab aktiv ist und nicht im Read-only-Modus angezeigt wird.

## <a id="sidebar">3. Tests-Sidebar-Panel</a>

Ein Klick auf das Tests-Icon in der linken Sidebar öffnet das Testing-Panel. In Pipelines, Databricks Asset Bundles oder Git-Folder-Bereichen mit angehängten Clustern umfasst die Test-Erkennung alle Dateien im Ordner — andernfalls ist sie auf die aktuelle Datei beschränkt.

**Verfügbare Aktionen in der Sidebar:**

- **Run all tests** (Doppel-Play-Icon).
- **Run all failed tests** (Refresh mit X-Icon).
- **Refresh tests** (Refresh-Icon).
- Test-Status über Bestanden-(Häkchen-Kreis)/Fehlgeschlagen-(X-Kreis)-Indikatoren überwachen.
- Tests nach Name oder Status über Suchleiste/Filter-Icon filtern.
- einzelne Tests durch Hovern und Klick auf das Play-Icon ausführen.

## <a id="inline">4. Tests über Inline-Icons ausführen</a>

Beim Ansehen einer Python-Testdatei erscheinen Run-Buttons inline neben jedem entdeckten Testfall. Ein Klick auf das Play-Icon führt genau diesen Test aus — das Icon aktualisiert sich anschließend, um Bestanden-/Fehlgeschlagen-Status widerzuspiegeln.

## <a id="fehleranzeige">5. Inline-Fehleranzeige</a>

Schlägt ein Unit Test fehl, erscheint ein Inline-Fehlerindikator auf der verursachenden Zeile. Ein Klick auf den Indikator öffnet ein Modal mit der vollständigen Fehlermeldung.

## <a id="ergebnisse">6. Testergebnisse-Panel</a>

Für gültige Python-Testdateien erscheint ein dedizierter „Testing"-Tab im unteren Panel, mit:

- vollständiger Zusammenfassung des letzten Testlaufs.
- Ergebnissen einzelner Testfälle.

**Optionen beim Hovern über einen Testfall:** zum Test navigieren (File-Code-Icon), Test ausführen (Play-Icon).

## <a id="quelle">7. Quelle</a>

- https://docs.databricks.com/aws/en/files/python-unit-tests

**Stand:** 2026-08-21.
