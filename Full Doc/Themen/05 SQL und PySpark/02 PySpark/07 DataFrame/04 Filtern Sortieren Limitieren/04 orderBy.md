# `DataFrame.orderBy()`

`orderBy` ist ein Alias für [`sort`](03%20sort.md).

## Signatur

```python
orderBy(*cols: Union[int, str, Column, List[Union[int, str, Column]]], **kwargs: Any)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `cols` | `int`, `str`, `list` oder `Column`, optional | Liste von `Column`s, Spaltennamen oder Spaltenordinalzahlen, nach denen sortiert wird. |
| `ascending` | `bool` oder `list`, optional, Standard `True` | Boolean oder Liste von Booleans: aufsteigend vs. absteigend sortieren. |

## Rückgabewert

`DataFrame`: Sortierter DataFrame.

## Beispiel

Die offizielle Referenzseite für `orderBy` enthält kein eigenes Beispiel; siehe die Beispiele unter [`sort`](03%20sort.md).

## Quellen

- DataFrame.orderBy: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/orderBy

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
