# `unittest` — Python-Standardbibliothek-Referenz

Vollständige Referenz für Pythons eingebautes Test-Framework `unittest` (von JUnit inspiriert), bereits kurz als „Option 2" der drei offiziellen PySpark-Testing-Ansätze in [07 PySpark-Testing-Utilities und Praxisbeispiel.md](07%20PySpark-Testing-Utilities%20und%20Praxisbeispiel.md), Abschnitt 6.1 eingeführt — hier die vollständige API-Referenz. Teil der [Testing](../Uebersicht.md)-Reihe, Kapitel [01 Unit Test](../01%20Unit%20Test/).

## Abschnittsübersicht

1. [Kernkonzepte](#kernkonzepte)
2. [Minimalbeispiel](#minimalbeispiel)
3. [`TestCase`: Setup und Teardown](#setup-teardown)
4. [`TestCase`: Assert-Methoden](#assert-methoden)
5. [Weitere `TestCase`-Methoden](#weitere-methoden)
6. [Testcode organisieren](#organisieren)
7. [Tests überspringen und erwartete Fehlschläge](#skip)
8. [Test-Discovery](#discovery)
9. [Kommandozeile](#cli)
10. [`TestSuite`, `TestLoader`, `TestResult`, `TextTestRunner`](#klassen)
11. [Async-Tests: `IsolatedAsyncioTestCase`](#async)
12. [`FunctionTestCase` (Legacy)](#functiontestcase)
13. [Zusammenfassungstabelle](#zusammenfassung)
14. [Quelle](#quelle)

---

## <a id="kernkonzepte">1. Kernkonzepte</a>

| Begriff | Bedeutung |
|---|---|
| **Test Fixture** | die Vorbereitung, die für einen oder mehrere Tests nötig ist (Setup + Cleanup) — z. B. temporäre Datenbanken, Verzeichnisse, Serverprozesse |
| **Test Case** | eine einzelne Testeinheit, die eine bestimmte Antwort auf bestimmte Eingaben prüft — implementiert über die `TestCase`-Klasse |
| **Test Suite** | eine Sammlung von Testfällen und/oder weiteren Test-Suiten, die gemeinsam ausgeführt werden sollen |
| **Test Runner** | orchestriert die Testausführung und liefert die Ergebnisse (grafisch, textuell oder als Rückgabewert) |

## <a id="minimalbeispiel">2. Minimalbeispiel</a>

```python
import unittest

class TestStringMethods(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # prüft, dass s.split scheitert, wenn der Separator kein String ist
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()
```

**Ausgabe (normal):**

```
...
----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

**Ausgabe (verbose, mit `-v`):**

```
test_isupper (__main__.TestStringMethods.test_isupper) ... ok
test_split (__main__.TestStringMethods.test_split) ... ok
test_upper (__main__.TestStringMethods.test_upper) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.001s

OK
```

## <a id="setup-teardown">3. `TestCase`: Setup und Teardown</a>

### Pro Testmethode: `setUp()`/`tearDown()`

```python
import unittest

class WidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.widget = Widget('The widget')

    def tearDown(self):
        self.widget.dispose()

    def test_default_widget_size(self):
        self.assertEqual(self.widget.size(), (50, 50),
                         'incorrect default size')

    def test_widget_resize(self):
        self.widget.resize(100, 150)
        self.assertEqual(self.widget.size(), (100, 150),
                         'wrong size after resize')
```

- `setUp()` läuft vor **jeder** Testmethode, `tearDown()` danach — auch wenn der Test fehlgeschlagen ist.
- Löst `setUp()` eine Exception aus, wird `tearDown()` **nicht** aufgerufen.
- Testmethoden laufen standardmäßig in **alphabetischer Reihenfolge** nach Namen.

### Pro Klasse: `setUpClass()`/`tearDownClass()`

```python
class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # läuft einmal, bevor alle Tests der Klasse starten
        pass

    @classmethod
    def tearDownClass(cls):
        # läuft einmal, nachdem alle Tests der Klasse abgeschlossen sind
        pass
```

Muss mit `@classmethod` dekoriert sein; läuft **einmal je Klasse**, nicht je Testmethode — sinnvoll für teure Setup-Operationen (z. B. Datenbankverbindungen, SparkSession — siehe Praxisbeispiel in Datei 07, Abschnitt 6.1).

## <a id="assert-methoden">4. `TestCase`: Assert-Methoden</a>

Alle Assert-Methoden akzeptieren zusätzlich ein optionales `msg`-Argument für eine eigene Fehlermeldung: `self.assertEqual(a, b, msg="Custom error message")`.

### Basis-Assertions

| Methode | Prüft | Neu in |
|---|---|---|
| `assertEqual(a, b)` | `a == b` | — |
| `assertNotEqual(a, b)` | `a != b` | — |
| `assertTrue(x)` | `bool(x) is True` | — |
| `assertFalse(x)` | `bool(x) is False` | — |
| `assertIs(a, b)` | `a is b` | 3.1 |
| `assertIsNot(a, b)` | `a is not b` | 3.1 |
| `assertIsNone(x)` | `x is None` | 3.1 |
| `assertIsNotNone(x)` | `x is not None` | 3.1 |
| `assertIn(a, b)` | `a in b` | 3.1 |
| `assertNotIn(a, b)` | `a not in b` | 3.1 |
| `assertIsInstance(a, b)` | `isinstance(a, b)` | 3.2 |
| `assertNotIsInstance(a, b)` | `not isinstance(a, b)` | 3.2 |
| `assertIsSubclass(a, b)` | `issubclass(a, b)` | 3.14 |
| `assertNotIsSubclass(a, b)` | `not issubclass(a, b)` | 3.14 |

### Exceptions und Warnings testen

```python
# assertRaises() als Callable
self.assertRaises(ValueError, int, 'xyz')

# als Context-Manager
with self.assertRaises(ValueError):
    int('xyz')

# Exception-Objekt inspizieren
with self.assertRaises(ValueError) as cm:
    int('xyz')
the_exception = cm.exception
self.assertEqual(the_exception.args[0], "...")

# assertRaisesRegex()
self.assertRaisesRegex(ValueError, "invalid literal for.*XYZ'$", int, 'XYZ')
with self.assertRaisesRegex(ValueError, 'literal'):
    int('XYZ')

# assertWarns()
with self.assertWarns(SomeWarning):
    do_something()
with self.assertWarns(SomeWarning) as cm:
    do_something()
self.assertIn('myfile.py', cm.filename)
self.assertEqual(320, cm.lineno)

# assertWarnsRegex()
self.assertWarnsRegex(DeprecationWarning,
                      r'legacy_function\(\) is deprecated',
                      legacy_function, 'XYZ')
with self.assertWarnsRegex(RuntimeWarning, 'unsafe frobnicating'):
    frobnicate('/etc/passwd')
```

### Logging testen

```python
# assertLogs()
with self.assertLogs('foo', level='INFO') as cm:
    logging.getLogger('foo').info('first message')
    logging.getLogger('foo.bar').error('second message')
self.assertEqual(cm.output, ['INFO:foo:first message',
                             'ERROR:foo.bar:second message'])

# assertNoLogs() — Gegenstück: prüft, dass NICHTS geloggt wird
with self.assertNoLogs('foo', level='ERROR'):
    pass
```

### Numerische Vergleiche

| Methode | Prüft |
|---|---|
| `assertAlmostEqual(a, b, places=7)` | `round(a-b, places) == 0` |
| `assertNotAlmostEqual(a, b, places=7)` | `round(a-b, places) != 0` |
| `assertGreater(a, b)` | `a > b` |
| `assertGreaterEqual(a, b)` | `a >= b` |
| `assertLess(a, b)` | `a < b` |
| `assertLessEqual(a, b)` | `a <= b` |

```python
self.assertAlmostEqual(2.5, 2.50001, places=4)
self.assertAlmostEqual(2.5, 2.6, delta=0.2)   # alternativ über absolute Toleranz
```

Analoges Konzept in PySpark: `assertDataFrameEqual(..., rtol=...)` (siehe Datei 07, Abschnitt 4.1) bzw. `assert_approx_df_equality(...)` in chispa (siehe [09 chispa — PySpark-Testbibliothek.md](09%20chispa%20%E2%80%94%20PySpark-Testbibliothek.md), Abschnitt 6).

### Strings, Regex, Container, Attribute

| Methode | Prüft |
|---|---|
| `assertRegex(s, r)` | `r.search(s)` |
| `assertNotRegex(s, r)` | `not r.search(s)` |
| `assertStartsWith(a, b)` | `a.startswith(b)` |
| `assertNotStartsWith(a, b)` | `not a.startswith(b)` |
| `assertEndsWith(a, b)` | `a.endswith(b)` |
| `assertNotEndsWith(a, b)` | `not a.endswith(b)` |
| `assertCountEqual(a, b)` | gleiche Elemente unabhängig von der Reihenfolge |
| `assertHasAttr(a, b)` | `hasattr(a, b)` |
| `assertNotHasAttr(a, b)` | `not hasattr(a, b)` |

```python
self.assertRegex('Fail: invalid literal for int() with base 10: xyz',
                 r'invalid literal for int\(\)')
self.assertCountEqual([1, 2, 2], [2, 1, 2])   # besteht: gleiche Elemente, andere Reihenfolge
```

### Typspezifische Gleichheitsmethoden

Werden automatisch von `assertEqual()` genutzt, sobald beide Argumente vom passenden Typ sind:

| Methode | Vergleicht |
|---|---|
| `assertMultiLineEqual(a, b)` | Strings (mehrzeilig) |
| `assertSequenceEqual(a, b)` | Sequenzen |
| `assertListEqual(a, b)` | Listen |
| `assertTupleEqual(a, b)` | Tupel |
| `assertSetEqual(a, b)` | Sets/Frozensets |
| `assertDictEqual(a, b)` | Dicts |

```python
self.assertMultiLineEqual("line1\nline2", "line1\nline2")
self.assertListEqual([1, 2, 3], [1, 2, 3])
self.assertDictEqual({'a': 1}, {'a': 1})
```

## <a id="weitere-methoden">5. Weitere `TestCase`-Methoden</a>

### `skipTest()` und `subTest()`

```python
def test_maybe_skipped(self):
    if not external_resource_available():
        self.skipTest("external resource not available")
```

```python
class NumbersTest(unittest.TestCase):
    def test_even(self):
        """Test that numbers between 0 and 5 are all even."""
        for i in range(0, 6):
            with self.subTest(i=i):
                self.assertEqual(i % 2, 0)
```

`subTest()` erlaubt es, einzelne Iterationen innerhalb eines Tests zu unterscheiden — **alle** Subtests laufen weiter, selbst wenn eines fehlschlägt; jeder Fehlschlag wird einzeln gemeldet, beliebig verschachtelbar.

### Cleanup-Mechanismen

```python
def test_with_cleanup(self):
    resource = acquire_resource()
    self.addCleanup(resource.release)
    # resource nutzen
```

- Cleanup-Funktionen laufen in **umgekehrter Reihenfolge** (LIFO).
- Werden nach `tearDown()` aufgerufen — bzw. nach `setUp()`, falls dieses fehlschlägt.
- Mehrere Cleanup-Funktionen möglich.

```python
def test_with_context_manager(self):
    temp_file = self.enterContext(tempfile.NamedTemporaryFile())
    # temp_file nutzen
```

**Klassen-Ebenen-Cleanup:**

```python
@classmethod
def setUpClass(cls):
    cls.resource = expensive_setup()
    cls.addClassCleanup(expensive_teardown, cls.resource)
```

### Sonstige Attribute und Methoden

```python
TestCase.failureException   # Standard: AssertionError
TestCase.longMessage = True # eigene msg wird an Standardmeldung angehängt (Default)
TestCase.maxDiff = 80*8     # maximale Diff-Länge in Fehlermeldungen

test_case.countTestCases()      # gibt 1 zurück (für TestCase)
test_case.defaultTestResult()   # liefert eine TestResult-Instanz
test_case.id()                  # eindeutiger Test-Identifier
test_case.shortDescription()    # erste Docstring-Zeile oder None
test_case.fail(msg=None)        # Test bedingungslos fehlschlagen lassen
test_case.run(result=None)      # Test ausführen
test_case.debug()               # Test ausführen, ohne Ergebnisse zu sammeln
```

## <a id="organisieren">6. Testcode organisieren</a>

```python
import unittest

class DefaultWidgetSizeTestCase(unittest.TestCase):
    def test_default_widget_size(self):
        widget = Widget('The widget')
        self.assertEqual(widget.size(), (50, 50))
```

**Wichtig:** Testmethoden müssen mit `test` beginnen, laufen alphabetisch, und jede erhält eine **frische** `TestCase`-Instanz.

**Test-Suite manuell zusammenstellen:**

```python
def suite():
    suite = unittest.TestSuite()
    suite.addTest(WidgetTestCase('test_default_widget_size'))
    suite.addTest(WidgetTestCase('test_widget_resize'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
```

**Vorteile separater Testmodule** (laut offizieller Doku): eigenständig lauffähig, Testcode getrennt vom Produktivcode, weniger Versuchung, Tests an den zu testenden Code anzupassen statt umgekehrt, Tests ändern sich seltener als der Quellcode, erleichtert Refactoring, C-Modul-Tests müssen ohnehin getrennt sein, und Änderungen an der Teststrategie wirken sich nicht auf den Quellcode aus.

## <a id="skip">7. Tests überspringen und erwartete Fehlschläge</a>

### Skip-Decorators

```python
class MyTestCase(unittest.TestCase):

    @unittest.skip("demonstrating skipping")
    def test_nothing(self):
        self.fail("shouldn't happen")

    @unittest.skipIf(mylib.__version__ < (1, 3),
                     "not supported in this library version")
    def test_format(self):
        pass

    @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    def test_windows_support(self):
        pass
```

**Ganze Klasse überspringen:**

```python
@unittest.skip("showing class skipping")
class MySkippedTestCase(unittest.TestCase):
    def test_not_run(self):
        pass
```

**Bedingtes Überspringen in `setUp()`:**

```python
def setUp(self):
    if not external_resource_available():
        self.skipTest("external resource not available")
```

**Eigener Skip-Decorator:**

```python
def skipUnlessHasattr(obj, attr):
    if hasattr(obj, attr):
        return lambda func: func
    return unittest.skip("{!r} doesn't have {!r}".format(obj, attr))
```

**Direkt per Exception:** `raise unittest.SkipTest("reason")`.

**Verhalten bei übersprungenen Tests:** `setUp()`/`tearDown()` laufen **nicht**, ebenso wenig `setUpClass()`/`tearDownClass()` (Klassenebene) oder `setUpModule()`/`tearDownModule()` (Modulebene).

### Erwartete Fehlschläge

```python
class ExpectedFailureTestCase(unittest.TestCase):
    @unittest.expectedFailure
    def test_fail(self):
        self.assertEqual(1, 0, "broken")
```

Schlägt der Test fehl oder wirft er einen Fehler: zählt als **Erfolg**. Besteht der Test: zählt als **Fehlschlag** („unexpected success").

## <a id="discovery">8. Test-Discovery</a>

```bash
cd project_directory
python -m unittest discover
```

Äquivalent zu: `python -m unittest`.

| Option | Standard | Bedeutung |
|---|---|---|
| `-s, --start-directory` | `.` | Startverzeichnis für die Suche |
| `-p, --pattern` | `test*.py` | Dateinamensmuster |
| `-t, --top-level-directory` | — | oberstes Projektverzeichnis |

```bash
python -m unittest discover -s project_directory
python -m unittest discover -p "*_test.py"
python -m unittest discover -t myproject

# Positionsargumente sind äquivalent zu den Flags:
python -m unittest discover -s project_directory -p "*_test.py"
python -m unittest discover project_directory "*_test.py"

# Paketname als Startverzeichnis
python -m unittest discover myproject.subpackage.test
```

**Voraussetzungen für Discovery:**

- Testdateien müssen gültige Python-Modulnamen sein.
- Testdateien müssen vom obersten Verzeichnis aus importierbar sein.
- Pfade werden in Modulnamen umgewandelt: `foo/bar/baz.py` → `foo.bar.baz`.
- Start- und Unterverzeichnisse müssen reguläre Packages mit `__init__.py` sein (oder Namespace-Packages ab 3.14+).

**`load_tests`-Protokoll:** Test-Module/-Packages können das Laden von Tests individuell anpassen:

```python
def load_tests(loader, tests, pattern):
    # eigene Lade-Logik
    return tests
```

## <a id="cli">9. Kommandozeile</a>

```bash
python -m unittest test_module1 test_module2         # bestimmte Module
python -m unittest test_module.TestClass              # bestimmte Klasse
python -m unittest test_module.TestClass.test_method  # bestimmte Methode
python -m unittest tests/test_something.py            # per Dateipfad
python -m unittest -v test_module                     # verbose
python -m unittest -h                                 # Hilfe
```

| Option | Bedeutung |
|---|---|
| `-b, --buffer` | puffert stdout/stderr während der Tests; Ausgabe erscheint nur bei Fehlschlag |
| `-c, --catch` | Strg+C wartet, bis der aktuelle Test fertig ist, bevor Ergebnisse gemeldet werden |
| `-f, --failfast` | bricht beim ersten Fehler/Fehlschlag ab |
| `-k` | führt nur Tests aus, die dem Muster entsprechen (mehrfach nutzbar) |
| `--locals` | zeigt lokale Variablen in Tracebacks |
| `--durations N` | zeigt die N langsamsten Tests (`N=0` für alle) |

**`-k`-Pattern-Matching:**

```bash
python -m unittest -k foo
# matcht z. B. foo_tests.SomeTest.test_something
# matcht z. B. bar_tests.SomeTest.test_foo
# matcht NICHT bar_tests.FooTest.test_something
```

Mit Wildcard (`*`): `fnmatch.fnmatchcase()`; ohne Wildcard: case-sensitive Substring-Matching gegen den vollqualifizierten Testmethodennamen.

## <a id="klassen">10. `TestSuite`, `TestLoader`, `TestResult`, `TextTestRunner`</a>

**`TestSuite`** — Sammlung von Testfällen/-suiten:

```python
suite = unittest.TestSuite()
suite.addTest(test)          # einzelnen Test/eine Suite hinzufügen
suite.addTests(tests)        # mehrere aus einem Iterable hinzufügen
suite.run(result)            # Tests ausführen, Ergebnisse in result sammeln
suite.debug()                # ohne Ergebnis-Sammlung ausführen
suite.countTestCases()       # Anzahl Tests
```

**`TestLoader`** — lädt Tests aus Modulen/Klassen/Funktionen:

```python
loader = unittest.TestLoader()
suite = loader.loadTestsFromTestCase(MyTestCase)
suite = loader.loadTestsFromModule(my_module)
suite = loader.loadTestsFromName('mymodule.MyTestCase.test_method')
suite = loader.discover('.')

# oder den Standard-Loader nutzen
suite = unittest.defaultTestLoader.discover('.')
```

Konfigurierbare Attribute: `testMethodPrefix` (Standard `'test'`), `sortTestMethodsUsing`, `suiteClass` (Standard `TestSuite`), `testNamePatterns`.

**`TestResult`** — sammelt Testergebnisse:

```python
result.errors               # [(TestCase, traceback), ...]
result.failures             # [(TestCase, traceback), ...]
result.skipped              # [(TestCase, reason), ...]
result.expectedFailures     # [(TestCase, traceback), ...]
result.unexpectedSuccesses  # [TestCase, ...]
result.collectedDurations   # [(test_name, elapsed_time), ...] (ab 3.12)
result.testsRun             # Gesamtanzahl ausgeführter Tests
result.wasSuccessful()      # True, wenn alle Tests bestanden haben
```

Konfiguration: `buffer`, `failfast`, `tb_locals`, `shouldStop`.

**`TextTestRunner`** — einfacher Runner mit Textausgabe:

```python
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(test_suite)
```

Parameter: `stream` (Standard `sys.stderr`), `descriptions=True`, `verbosity=1`, `failfast=False`, `buffer=False`, `resultclass=None`, `warnings=None`, `tb_locals=False`, `durations=None`.

## <a id="async">11. Async-Tests: `IsolatedAsyncioTestCase`</a>

Für asynchrone Testfunktionen (ab Python 3.8):

```python
from unittest import IsolatedAsyncioTestCase

events = []

class Test(IsolatedAsyncioTestCase):
    def setUp(self):
        events.append("setUp")

    async def asyncSetUp(self):
        self._async_connection = await AsyncConnection()
        events.append("asyncSetUp")

    async def test_response(self):
        events.append("test_response")
        response = await self._async_connection.get("https://example.com")
        self.assertEqual(response.status_code, 200)
        self.addAsyncCleanup(self.on_cleanup)

    def tearDown(self):
        events.append("tearDown")

    async def asyncTearDown(self):
        await self._async_connection.close()
        events.append("asyncTearDown")

    async def on_cleanup(self):
        events.append("cleanup")
```

**Ausführungsreihenfolge:** `["setUp", "asyncSetUp", "test_response", "asyncTearDown", "tearDown", "cleanup"]`.

Weitere Methoden: `addAsyncCleanup(function, *args, **kwargs)`, `async enterAsyncContext(cm)`, `loop_factory`-Attribut zum Überschreiben der Standard-Event-Loop-Policy.

## <a id="functiontestcase">12. `FunctionTestCase` (Legacy)</a>

Umhüllt Legacy-Testfunktionen mit dem `TestCase`-Interface:

```python
def testSomething():
    something = makeSomething()
    assert something.name is not None

testcase = unittest.FunctionTestCase(
    testSomething,
    setUp=makeSomethingDB,
    tearDown=deleteSomethingDB
)
```

**Hinweis:** Für neuen Code nicht empfohlen — stattdessen reguläre `TestCase`-Unterklassen verwenden.

## <a id="zusammenfassung">13. Zusammenfassungstabelle</a>

| Feature | Nutzung |
|---|---|
| Basis-Test | `TestCase` erweitern, `test_*`-Methoden definieren |
| Setup/Teardown | `setUp()`, `tearDown()` (je Test) |
| Klassen-Setup | `setUpClass()`, `tearDownClass()` (je Klasse) |
| Assertions | 60+ `assert*()`-Methoden |
| Test überspringen | `@skip()`, `@skipIf()`, `@skipUnless()`, `skipTest()` |
| Erwarteter Fehlschlag | `@expectedFailure` |
| Subtests | `with self.subTest(...)` |
| Test-Discovery | `python -m unittest discover` |
| Tests ausführen | `python -m unittest module.TestClass.test_method` |
| Eigener Runner | `TextTestRunner()` |
| Test-Suite | `TestSuite()` mit `addTest()` |
| Test-Loader | `TestLoader()` bzw. `defaultTestLoader` |
| Async-Tests | `IsolatedAsyncioTestCase` |
| Cleanup | `addCleanup()`, `enterContext()` |

### Quelle

- https://docs.python.org/3/library/unittest.html

**Stand:** 2026-09-01.
