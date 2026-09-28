# chispa — PySpark-Testbibliothek

Community-Bibliothek (nicht offiziell von Databricks/Apache Spark) mit Assertion-Funktionen für PySpark-DataFrames, die im Fehlerfall besonders lesbare, farblich hervorgehobene Diffs liefert — eine Alternative bzw. Ergänzung zu den offiziellen `pyspark.testing.utils`-Funktionen (siehe [07 PySpark-Testing-Utilities und Praxisbeispiel.md](07%20PySpark-Testing-Utilities%20und%20Praxisbeispiel.md)). Teil der [Testing](../Uebersicht.md)-Reihe, Kapitel [01 Unit Test](../01%20Unit%20Test/).

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Installation](#installation)
3. [Spalten-Gleichheit](#spalten-gleichheit)
4. [DataFrame-Gleichheit](#dataframe-gleichheit)
5. [Vergleichsoptionen](#vergleichsoptionen)
6. [Näherungsweise Gleichheit (Floats)](#naeherung)
7. [Eigenes Ausgabeformat](#formatierung)
8. [Voraussetzungen und Entwicklung](#voraussetzungen)
9. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

„Chispa" ist Spanisch für „Funke" (spark). Die Bibliothek hilft, hochwertigen PySpark-Code zu schreiben, indem Testfehlschläge durch formatierte Ausgaben leichter debugbar werden.

## <a id="installation">2. Installation</a>

```bash
pip install chispa
```

Oder mit Poetry:

```bash
poetry add chispa --group dev
```

## <a id="spalten-gleichheit">3. Spalten-Gleichheit</a>

`assert_column_equality` vergleicht zwei Spalten innerhalb desselben DataFrames:

```python
from chispa import assert_column_equality

def test_remove_non_word_characters_short():
    data = [
        ("jo&&se", "jose"),
        ("**li**", "li"),
        ("#::luisa", "luisa"),
        (None, None)
    ]
    df = (spark.createDataFrame(data, ["name", "expected_name"])
        .withColumn("clean_name", remove_non_word_characters(F.col("name"))))
    assert_column_equality(df, "clean_name", "expected_name")
```

Schlägt der Test fehl, gibt die Funktion „beschreibende Fehlermeldungen" mit farblich hervorgehobenen, abweichenden Zeilen aus.

## <a id="dataframe-gleichheit">4. DataFrame-Gleichheit</a>

`assert_df_equality` vergleicht zwei vollständige DataFrames:

```python
from chispa import assert_df_equality

def test_remove_non_word_characters_long():
    source_data = [
        ("jo&&se",),
        ("**li**",),
        ("#::luisa",),
        (None,)
    ]
    source_df = spark.createDataFrame(source_data, ["name"])

    actual_df = source_df.withColumn(
        "clean_name",
        remove_non_word_characters(F.col("name"))
    )

    expected_data = [
        ("jo&&se", "jose"),
        ("**li**", "li"),
        ("#::luisa", "luisa"),
        (None, None)
    ]
    expected_df = spark.createDataFrame(expected_data, ["name", "clean_name"])

    assert_df_equality(actual_df, expected_df)
```

## <a id="vergleichsoptionen">5. Vergleichsoptionen</a>

`assert_df_equality` akzeptiert mehrere optionale Parameter zur Feinsteuerung des Vergleichs:

| Option | Wirkung |
|---|---|
| `ignore_row_order=True` | Zeilenreihenfolge wird beim Vergleich ignoriert |
| `ignore_column_order=True` | Spaltenreihenfolge wird ignoriert |
| `ignore_columns=[...]` | angegebene Spalten werden vom Vergleich ausgeschlossen |
| `ignore_nullable=True` | Nullability-Unterschiede im Schema werden ignoriert |
| `ignore_metadata=True` | Schema-Metadaten-Unterschiede werden übergangen |
| `transforms=[...]` | wendet Vorverarbeitungsschritte auf beide DataFrames an, bevor verglichen wird |
| `underline_cells=True` | hebt abweichende Zellen in der Ausgabe zusätzlich hervor |
| `allow_nan_equality=True` | behandelt `NaN == NaN` als gleich |

```python
assert_df_equality(df1, df2, ignore_row_order=True)
assert_df_equality(df1, df2, ignore_column_order=True)
assert_df_equality(df1, df2, ignore_columns=["clean_name"])
assert_df_equality(df1, df2, ignore_nullable=True)
```

## <a id="naeherung">6. Näherungsweise Gleichheit (Floats)</a>

Für Floating-Point-Spalten: `assert_approx_column_equality` (einzelne Spalte) bzw. `assert_approx_df_equality` (ganzes DataFrame), jeweils mit explizitem Toleranzwert als letztem Argument — analog zum `rtol`-Parameter von `assertDataFrameEqual` (siehe Datei 07, Abschnitt 4.1), hier aber als absolute Toleranz.

```python
def test_approx_col_equality_same():
    data = [
        (1.1, 1.1),
        (2.2, 2.15),
        (3.3, 3.37),
        (None, None)
    ]
    df = spark.createDataFrame(data, ["num1", "num2"])
    assert_approx_column_equality(df, "num1", "num2", 0.1)
```

```python
def test_approx_df_equality_same():
    data1 = [(1.1, "a"), (2.2, "b"), (3.3, "c"), (None, None)]
    df1 = spark.createDataFrame(data1, ["num", "letter"])

    data2 = [(1.05, "a"), (2.13, "b"), (3.3, "c"), (None, None)]
    df2 = spark.createDataFrame(data2, ["num", "letter"])

    assert_approx_df_equality(df1, df2, 0.1)
```

## <a id="formatierung">7. Eigenes Ausgabeformat</a>

Über `FormattingConfig` lässt sich die Fehlerausgabe (Farben, Stile) anpassen:

```python
from chispa import FormattingConfig

formats = FormattingConfig(
    mismatched_rows={"color": "light_yellow"},
    matched_rows={"color": "cyan", "style": "bold"},
    mismatched_cells={"color": "purple"},
    matched_cells={"color": "blue"},
)

assert_basic_rows_equality(df1.collect(), df2.collect(), formats=formats)
```

Alternativ über Enums statt Strings:

```python
from chispa import FormattingConfig, Color, Style

formats = FormattingConfig(
    mismatched_rows={"color": Color.LIGHT_YELLOW},
    matched_rows={"color": Color.CYAN, "style": Style.BOLD},
    mismatched_cells={"color": Color.PURPLE},
    matched_cells={"color": Color.BLUE},
)
```

**Empfehlung:** Für projektweite Wiederverwendung `formats` als Fixture in `conftest.py` definieren.

## <a id="voraussetzungen">8. Voraussetzungen und Entwicklung</a>

- **Python:** `>=3.10,<4.0`.
- **Getestet gegen PySpark:** 3.5.x, 4.0.x, 4.1.x.
- **Python-Versionen:** 3.10, 3.11, 3.12.
- **Entwicklung:** Dependency-Management über Poetry:
  ```bash
  poetry install
  poetry run pytest tests
  ```

### Quelle

- https://github.com/MrPowers/chispa

**Stand:** 2026-09-01.
