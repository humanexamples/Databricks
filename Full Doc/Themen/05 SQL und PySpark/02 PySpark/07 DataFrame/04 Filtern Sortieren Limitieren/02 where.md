# `DataFrame.where()`

`where` ist ein Alias für [`filter`](01%20filter.md).

## Signatur

```python
where(condition: Union[Column, str])
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `condition` | `Column` oder `str` | Eine `Column` vom Typ `BooleanType` oder ein String mit SQL-Ausdrücken. |

## Rückgabewert

`DataFrame`: Neuer DataFrame mit den Zeilen, die die Bedingung erfüllen.

## Beispiel

Die offizielle Referenzseite für `where` enthält kein eigenes Beispiel; siehe die Beispiele unter [`filter`](01%20filter.md).

## Quellen

- DataFrame.where: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/where

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
