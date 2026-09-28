# `DataFrame.pandas_api()`

Konvertiert den bestehenden DataFrame in einen pandas-on-Spark-DataFrame.

## Signatur

```python
pandas_api(index_col: Optional[Union[str, List[str]]] = None)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `index_col` | `str` oder Liste von `str`, optional | Indexspalte(n) der Tabelle in Spark. |

## Rückgabewert

`PandasOnSparkDataFrame`

## Hinweise

- Wird ein pandas-on-Spark-DataFrame in einen Spark-DataFrame und wieder zurück konvertiert, gehen die Indexinformationen verloren; der ursprüngliche Index wird zu einer normalen Spalte.
- Nur verfügbar, wenn pandas installiert und verfügbar ist.

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])

df.pandas_api()
#    age   name
# 0   14    Tom
# 1   23  Alice
# 2   16    Bob

df.pandas_api(index_col="age")
#       name
# age
# 14     Tom
# 23   Alice
# 16     Bob
```

Siehe auch [`toPandas`](01%20toPandas.md).

## Quellen

- DataFrame.pandas_api: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/pandas_api

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
