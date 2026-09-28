# `DataFrame.freqItems()`

Ermittelt häufige Elemente (frequent items) für Spalten, möglicherweise mit False Positives. Verwendet wird der Frequent-Element-Count-Algorithmus aus <https://doi.org/10.1145/762471.762473> (vorgeschlagen von Karp, Schenker und Papadimitriou). `DataFrame.freqItems` und `DataFrameStatFunctions.freqItems` sind Aliase.

## Signatur

```python
freqItems(cols: Union[List[str], Tuple[str]], support: Optional[float] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `cols` | `list` oder `tuple` | Namen der Spalten, für die häufige Elemente berechnet werden, als Liste oder Tupel von Strings. |
| `support` | `float`, optional | Häufigkeit, ab der ein Element als „häufig“ gilt. Standard ist 1 %. Muss größer als 1e-4 sein. |

## Rückgabewert

`DataFrame`: DataFrame mit den häufigen Elementen.

## Hinweise

Die Funktion ist für die explorative Datenanalyse gedacht; für die Rückwärtskompatibilität des Schemas des Ergebnis-DataFrames gibt es keine Garantie.

## Beispiel

```python
from pyspark.sql import functions as sf
df = spark.createDataFrame([(1, 11), (1, 11), (3, 10), (4, 8), (4, 8)], ["c1", "c2"])
df = df.freqItems(["c1", "c2"])
df.select([sf.sort_array(c).alias(c) for c in df.columns]).show()
# +------------+------------+
# |c1_freqItems|c2_freqItems|
# +------------+------------+
# |   [1, 3, 4]| [8, 10, 11]|
# +------------+------------+
```

## Quellen

- DataFrame.freqItems: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/freqItems

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
