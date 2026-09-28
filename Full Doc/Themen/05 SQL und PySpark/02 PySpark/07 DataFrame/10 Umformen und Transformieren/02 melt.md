# `DataFrame.melt()`

Wandelt einen DataFrame vom Wide- ins Long-Format um (Unpivot), wobei optional Identifier-Spalten erhalten bleiben. Das ist die Umkehrung von `groupBy(...).pivot(...).agg(...)` – mit Ausnahme der Aggregation, die sich nicht umkehren lässt.

`melt` ist ein Alias für [`unpivot`](01%20unpivot.md).

## Signatur

```python
melt(ids: Union["ColumnOrName", List["ColumnOrName"], Tuple["ColumnOrName", ...]], values: Optional[Union["ColumnOrName", List["ColumnOrName"], Tuple["ColumnOrName", ...]]], variableColumnName: str, valueColumnName: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `ids` | `str`, `Column`, `tuple`, `list`, optional | Spalte(n), die als Identifier verwendet werden. Eine einzelne Spalte bzw. ein Spaltenname oder eine Liste/ein Tupel für mehrere Spalten. |
| `values` | `str`, `Column`, `tuple`, `list`, optional | Spalte(n), die „entpivotiert“ werden. Eine einzelne Spalte bzw. ein Spaltenname oder eine Liste/ein Tupel für mehrere Spalten. Ist nichts oder eine leere Angabe gesetzt, werden alle Spalten verwendet, die nicht in `ids` stehen. |
| `variableColumnName` | `str` | Name der Variablenspalte. |
| `valueColumnName` | `str` | Name der Wertespalte. |

## Rückgabewert

`DataFrame`: Entpivotierter DataFrame.

## Hinweise

Unterstützt Spark Connect.

## Beispiel

Die offizielle Referenzseite für `melt` enthält kein eigenes Beispiel; siehe das Beispiel unter [`unpivot`](01%20unpivot.md).

## Quellen

- DataFrame.melt: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/melt

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
