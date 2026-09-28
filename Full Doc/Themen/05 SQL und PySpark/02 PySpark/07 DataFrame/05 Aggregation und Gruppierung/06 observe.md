# `DataFrame.observe()`

Definiert (benannte) Metriken, die auf dem DataFrame beobachtet werden. Die Methode gibt einen „beobachteten“ DataFrame zurück, der dasselbe Ergebnis wie die Eingabe liefert, mit folgenden Garantien:

- Die definierten Aggregate (Metriken) werden auf allen Daten berechnet, die an dieser Stelle durch das Dataset fließen.
- Der Wert der definierten Aggregatspalten wird gemeldet, sobald ein Abschlusspunkt erreicht ist.

## Signatur

```python
observe(observation: Union["Observation", str], *exprs: Column)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `observation` | `Observation` oder `str` | Ein `str`, um den Namen anzugeben, oder eine `Observation`-Instanz, über die die Metrik abgerufen wird. |
| `exprs` | `Column` | Spaltenausdrücke (`Column`). |

## Rückgabewert

`DataFrame`: Der beobachtete DataFrame.

## Hinweise

Ist `observation` eine `Observation`, unterstützt die Methode nur Batch-Queries. Ist `observation` ein String, funktioniert sie für Batch- und Streaming-Queries. Continuous Execution wird derzeit noch nicht unterstützt.

## Beispiel

```python
from pyspark.sql import Observation, functions as sf
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
observation = Observation("my metrics")
observed_df = df.observe(observation,
    sf.count(sf.lit(1)).alias("count"), sf.max("age"))
observed_df.count()
# 2
observation.get
# {'count': 2, 'max(age)': 5}
```

## Quellen

- DataFrame.observe: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/observe

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
