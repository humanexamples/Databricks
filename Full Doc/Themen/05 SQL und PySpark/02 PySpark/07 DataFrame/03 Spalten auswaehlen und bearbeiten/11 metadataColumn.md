# `DataFrame.metadataColumn()`

Wählt eine Metadatenspalte anhand ihres logischen Spaltennamens aus und gibt sie als `Column` zurück.

*Hinzugefügt in Databricks Runtime 16.1*

## Signatur

```python
metadataColumn(colName: str)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `colName` | `str` | Name der Metadatenspalte. |

## Rückgabewert

`Column`

## Hinweise

Auf eine Metadatenspalte kann auf diese Weise auch dann zugegriffen werden, wenn die zugrunde liegende Datenquelle eine Datenspalte mit gleichem Namen definiert.

## Beispiel

Die offizielle Referenz enthält für diese Methode kein Beispiel.

## Quellen

- DataFrame.metadataColumn: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/metadataColumn

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
