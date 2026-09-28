# Unit-Tests für PySpark

## Testfunktionen von pyspark.testing.utils

**`pyspark.testing.utils`** stellt Hilfsfunktionen bereit, die Unit-Testing in PySpark erleichtern.

- **`assertDataFrameEqual`** – `assertDataFrameEqual(actual, expected[, ...])`
- **`assertSchemaEqual`** – `assertSchemaEqual(actual, expected)`

Es gibt verschiedene weitere Methoden, um Ihre Unit-Tests zu testen; wir konzentrieren uns auf die PySpark Testing Utils.

## Beispiel für einen Unit-Test

**1. Sie haben die folgende Funktion, um eine Spalte zu erstellen**

```python
from pyspark.sql.functions import col, when

def add_new_col(df, new, s_col):
 return (df
         .withColumn(new,
            when(col(s_col) == 0, 'Normal')
            .otherwise('Unknown')))
```

```python
def test_add_new_col():
   data = [(0,), (1,), (-1,),(None,)]
   columns = ["value"]
   df = spark.createDataFrame(data, columns)

   actual_df = add_new_col(df, "new_value", "value")

   expected_data = [(0, 'Normal'), (1, 'Unknown'),
                    (-1, 'Unknown'), (None, 'Unknown')]
   expected_df = spark.createDataFrame(expected_data,
                                       ["value", "new_value"])

   assertDataFrameEqual(actual_df, expected_df)
```

---

## E. Unit-Testing-Framework – pytest

**Pytest** ist ein beliebtes Test-Framework für Python, das es einfach macht, unkomplizierte und skalierbare Testfälle zu schreiben.

- **Verwendet eine einfache Syntax** – Minimale Syntax, definieren Sie einfach Funktionen, die mit `test_` beginnen.
- **Bietet Assertions** – Verwenden Sie `assert`-Anweisungen, um bei Fehlschlägen detaillierte Fehlermeldungen zu liefern.
- **Automatische Erkennung** – Findet und führt alle Tests automatisch mit einer einfachen Konfiguration aus.
- **Reiches Ökosystem** – Erweitern Sie die Funktionalität mit Plugins für Coverage, parallele Tests und mehr.
