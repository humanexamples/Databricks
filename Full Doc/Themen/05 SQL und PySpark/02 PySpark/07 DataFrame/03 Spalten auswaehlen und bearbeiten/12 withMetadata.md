# `DataFrame.withMetadata()`

Gibt einen neuen DataFrame zurück, in dem eine bestehende Spalte mit Metadaten aktualisiert ist.

## Signatur

```python
withMetadata(columnName: str, metadata: Dict[str, Any])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `columnName` | `str` | Name der bestehenden Spalte, deren Metadaten aktualisiert werden. |
| `metadata` | `dict` | Neue Metadaten, die `df.schema[columnName].metadata` zugewiesen werden. |

## Rückgabewert

`DataFrame`: DataFrame mit aktualisierten Spalten-Metadaten.

## Beispiel

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
df_meta = df.withMetadata('age', {'foo': 'bar'})
df_meta.schema['age'].metadata
# {'foo': 'bar'}
```

## Quellen

- DataFrame.withMetadata: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/withMetadata

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
