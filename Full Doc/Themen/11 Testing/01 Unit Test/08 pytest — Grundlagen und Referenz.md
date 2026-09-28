# pytest — Grundlagen und Referenz

Vollständige Dokumentation des Test-Frameworks `pytest`, das in diesem Projekt als bevorzugtes Test-Framework für PySpark-Code verwendet wird (siehe [07 PySpark-Testing-Utilities und Praxisbeispiel.md](07%20PySpark-Testing-Utilities%20und%20Praxisbeispiel.md)). Teil der [Testing](../Uebersicht.md)-Reihe, Kapitel [01 Unit Test](../01%20Unit%20Test/).

## Abschnittsübersicht

1. [Was ist pytest?](#was-ist)
2. [Kernfunktionen](#kernfunktionen)
3. [Minimalbeispiel](#minimalbeispiel)
4. [Dokumentationsstruktur](#doku-struktur)
5. [Weiterführende Ressourcen](#ressourcen)
6. [Quelle](#quelle)

---

## <a id="was-ist">1. Was ist pytest?</a>

„Das `pytest`-Framework macht es einfach, kleine, gut lesbare Tests zu schreiben, und skaliert dabei bis hin zu komplexem funktionalem Testing für Anwendungen und Bibliotheken."

## <a id="kernfunktionen">2. Kernfunktionen</a>

- **Detaillierte Fehlerinfos bei fehlgeschlagenen `assert`-Statements** — „ohne sich `self.assert*`-Namen merken zu müssen" (Abgrenzung zu `unittest`, siehe [11 unittest — Python-Standardbibliothek-Referenz.md](11%20unittest%20%E2%80%94%20Python-Standardbibliothek-Referenz.md)).
- **Auto-Discovery** von Testmodulen und -funktionen — keine manuelle Registrierung nötig.
- **Modulare Fixtures** zur Verwaltung von Test-Ressourcen (z. B. einer SparkSession, siehe die Praxisbeispiele in Datei 07).
- **Unterstützung für `unittest`-Testsuiten** — bestehende `unittest`-Tests laufen auch unter pytest.
- **Kompatibilität:** Python 3.10+ oder PyPy 3.
- **Über 1.300 externe Plugins** verfügbar.

## <a id="minimalbeispiel">3. Minimalbeispiel</a>

```python
def inc(x):
    return x + 1

def test_answer():
    assert inc(3) == 5
```

Bei Ausführung mit `pytest` schlägt dieser Test mit einer detaillierten Ausgabe fehl, die die genaue Abweichung zeigt: `assert 4 == 5`.

## <a id="doku-struktur">4. Dokumentationsstruktur</a>

Die offizielle pytest-Doku gliedert sich in vier Hauptbereiche:

1. **Get Started** — Einstieg und Installation.
2. **How-to guides** — Nutzung, Fixtures, Assertions, Plugins u. a.
3. **Reference guides** — API-Dokumentation, Konfiguration, Plugin-Verzeichnis.
4. **Explanation** — konzeptionelle Themen wie Fixtures, CI-Praktiken, Testaufbau.

## <a id="ressourcen">5. Weiterführende Ressourcen</a>

Die Landing Page verlinkt zusätzlich auf den GitHub-Issue-Tracker für Bug-Reports sowie auf Open Collective und Tidelift für Spenden bzw. Enterprise-Support.

**Im Projekt bereits praktisch demonstriert:**

- pytest-Fixtures für die SparkSession, `assertDataFrameEqual`/`assertSchemaEqual` im pytest-Kontext, `pytest.main()`-Ausführung im Notebook: siehe [07 PySpark-Testing-Utilities und Praxisbeispiel.md](07%20PySpark-Testing-Utilities%20und%20Praxisbeispiel.md), Abschnitte 3, 7–8.
- pytest in der VS-Code-Extension: siehe [04 pytest in der VS-Code-Extension.md](04%20pytest%20in%20der%20VS-Code-Extension.md).
- pytest in CI/CD-Pipelines (Azure DevOps): siehe [03 Azure DevOps Integration.md](../../10%20Developers/02%20CI-CD/03%20Azure%20DevOps%20Integration.md).

### Quelle

- https://docs.pytest.org/en/stable/

**Stand:** 2026-09-01.
