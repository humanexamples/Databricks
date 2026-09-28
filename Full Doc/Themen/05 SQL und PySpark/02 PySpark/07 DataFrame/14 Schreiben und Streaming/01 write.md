# `DataFrame.write` (Eigenschaft)

Schnittstelle zum Speichern des Inhalts eines nicht-streamenden `DataFrame` in externe Speichersysteme.

## Rückgabewert

`DataFrameWriter` – Details siehe [../04 DataFrameWriter/00 Uebersicht.md](../../04%20DataFrameWriter/00%20Uebersicht.md).

## Beispiele

```python
df = spark.createDataFrame([(2, "Alice"), (5, "Bob")], schema=["age", "name"])
type(df.write)
# <class '...readwriter.DataFrameWriter'>
```

Den DataFrame als Tabelle schreiben:

```python
df.write.saveAsTable("tab2")
```

Siehe auch [`writeTo`](02%20writeTo.md), [`writeStream`](04%20writeStream.md).

## Quellen

- DataFrame.write: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/write

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
