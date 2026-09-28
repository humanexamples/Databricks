# `DataFrame.mapInArrow()`

Verarbeitet einen Iterator von Batches des aktuellen DataFrames mit einer nativen Python-Funktion, die auf `pyarrow.RecordBatch`-Objekten als Ein- und Ausgabe arbeitet, und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
mapInArrow(func: "ArrowMapIterFunction", schema: Union[StructType, str], barrier: bool = False, profile: Optional[ResourceProfile] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `func` | Funktion | Native Python-Funktion, die einen Iterator von `pyarrow.RecordBatch` entgegennimmt und einen Iterator von `pyarrow.RecordBatch` ausgibt. |
| `schema` | `DataType` oder `str` | Rückgabetyp von `func` in PySpark – entweder ein `pyspark.sql.types.DataType`-Objekt oder ein DDL-formatierter Typ-String. |
| `barrier` | `bool`, optional, Standard `False` | Barrier-Mode-Ausführung verwenden: Alle Python-Worker der Stage werden gleichzeitig gestartet. |
| `profile` | `ResourceProfile`, optional | Optionales `ResourceProfile` für `mapInArrow`. |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import pyarrow as pa
df = spark.createDataFrame([(1, 21), (2, 30)], ("id", "age"))
def filter_func(iterator):
    for batch in iterator:
        pdf = batch.to_pandas()
        yield pa.RecordBatch.from_pandas(pdf[pdf.id == 1])
df.mapInArrow(filter_func, df.schema).show()
# +---+---+
# | id|age|
# +---+---+
# |  1| 21|
# +---+---+

df.mapInArrow(filter_func, df.schema, barrier=True).collect()
# [Row(id=1, age=21)]
```

Siehe auch [`mapInPandas`](06%20mapInPandas.md).

## Quellen

- DataFrame.mapInArrow: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/mapInArrow

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
