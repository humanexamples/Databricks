# `DataFrame.writeTo()`

Erstellt einen Builder für die Schreibkonfiguration für v2-Quellen.

## Signatur

```python
writeTo(table: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `table` | `str` | Name der Zieltabelle. |

## Rückgabewert

`DataFrameWriterV2`: Writer, mit dem anschließend festgelegt wird, wie die Daten gespeichert werden.

## Hinweise

Mit diesem Builder werden Schreiboperationen konfiguriert und ausgeführt – z. B. Anhängen an Tabellen oder Erstellen bzw. Ersetzen bestehender Tabellen (`append()`, `create()`, `createOrReplace()`, `overwrite()` …).

## Beispiel

```python
df = spark.createDataFrame(
    [(14, "Tom"), (23, "Alice"), (16, "Bob")], ["age", "name"])
df.writeTo("catalog.db.table").append()
df.writeTo(
    "catalog.db.table"
).partitionedBy("col").createOrReplace()
```

Siehe auch [`write`](01%20write.md), [`mergeInto`](03%20mergeInto.md).

## Quellen

- DataFrame.writeTo: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/writeTo

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
