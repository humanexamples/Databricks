# `DataFrame.semanticHash()`

Gibt einen Hashcode des logischen Query-Plans dieses DataFrames zurück.

## Signatur

```python
semanticHash()
```

## Rückgabewert

`int`: Hashwert.

## Hinweise

- Anders als beim Standard-Hashcode wird der Hash auf dem vereinfachten Query-Plan berechnet, wobei kosmetische Unterschiede wie Attributnamen toleriert werden.
- Dies ist eine Developer-API.

## Beispiel

```python
spark.range(10).selectExpr("id as col0").semanticHash()
# 1855039936
spark.range(10).selectExpr("id as col1").semanticHash()
# 1855039936
```

Siehe auch [`sameSemantics`](07%20sameSemantics.md).

## Quellen

- DataFrame.semanticHash: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/semanticHash

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
