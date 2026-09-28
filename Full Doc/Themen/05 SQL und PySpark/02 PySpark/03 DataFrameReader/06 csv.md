# `DataFrameReader.csv()`

Lädt eine CSV-Datei (oder mehrere) und gibt das Ergebnis als DataFrame zurück.

## Signatur

```python
csv(path, schema=None, **options)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `path` | `str` oder `list` | Ein oder mehrere Eingabepfade, oder eine RDD von Strings, die CSV-Zeilen enthält. |
| `schema` | `StructType` oder `str`, optional | Eingabeschema als `StructType`-Objekt oder DDL-formatierter String (z. B. `'col0 INT, col1 DOUBLE'`). |

## Rückgabewert

`DataFrame`

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="csv") as d:
    df = spark.createDataFrame([{"age": 100, "name": "Alice"}])
    df.write.mode("overwrite").format("csv").save(d)
    spark.read.csv(d, schema=df.schema, nullValue="Alice").show()
    # +---+----+
    # |age|name|
    # +---+----+
    # |100|NULL|
    # +---+----+
```

Wichtige `**options` (z. B. `header`, `inferSchema`, `sep`, `encoding`) werden per `.option()`/`.options()` gesetzt — siehe [03 option.md](03%20option.md) und [04 options.md](04%20options.md). Vollständige CSV-Optionstabelle: [07 Data Management/.../05 Working with Files/03 Spark API Options/03 DataFrameReader — CSV.md](../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/03%20Spark%20API%20Options/03%20DataFrameReader%20%E2%80%94%20CSV.md).

## Quellen

- DataFrameReader.csv: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframereader/csv

**Stand:** 2026-08-25, per `WebFetch` verifiziert.
