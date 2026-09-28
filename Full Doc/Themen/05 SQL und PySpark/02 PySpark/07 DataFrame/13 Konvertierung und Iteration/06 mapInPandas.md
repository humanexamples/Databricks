# `DataFrame.mapInPandas()`

Verarbeitet einen Iterator von Batches des aktuellen DataFrames mit einer nativen Python-Funktion, die auf pandas-DataFrames als Ein- und Ausgabe arbeitet, und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
mapInPandas(func: "PandasMapIterFunction", schema: Union[StructType, str], barrier: bool = False, profile: Optional[ResourceProfile] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `func` | Funktion | Native Python-Funktion, die einen Iterator von `pandas.DataFrame` entgegennimmt und einen Iterator von `pandas.DataFrame` ausgibt. |
| `schema` | `DataType` oder `str` | Rückgabetyp von `func` in PySpark – entweder ein `pyspark.sql.types.DataType`-Objekt oder ein DDL-formatierter Typ-String. |
| `barrier` | `bool`, optional, Standard `False` | Barrier-Mode-Ausführung verwenden: Alle Python-Worker der Stage werden gleichzeitig gestartet. |
| `profile` | `ResourceProfile`, optional | Optionales `ResourceProfile` für `mapInPandas`. |

## Rückgabewert

`DataFrame`

## Beispiel

```python
df = spark.createDataFrame([(1, 21), (2, 30)], ("id", "age"))

def filter_func(iterator):
    for pdf in iterator:
        yield pdf[pdf.id == 1]

df.mapInPandas(filter_func, df.schema).show()
# +---+---+
# | id|age|
# +---+---+
# |  1| 21|
# +---+---+

def mean_age(iterator):
    for pdf in iterator:
        yield pdf.groupby("id").mean().reset_index()

df.mapInPandas(mean_age, "id: bigint, age: double").show()
# +---+----+
# | id| age|
# +---+----+
# |  1|21.0|
# |  2|30.0|
# +---+----+

df.mapInPandas(filter_func, df.schema, barrier=True).collect()
# [Row(id=1, age=21)]
```

Siehe auch [`mapInArrow`](07%20mapInArrow.md).

## Quellen

- DataFrame.mapInPandas: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/mapInPandas

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
