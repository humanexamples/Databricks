# `DataFrameWriter.mode()`

Legt das Verhalten beim Schreiben fest, falls die Zieldaten (Pfad oder Tabelle) bereits existieren.

## Signatur

```python
mode(saveMode)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `saveMode` | `str` | Der Speichermodus. Zulässige Werte: `'append'`, `'overwrite'`, `'error'`/`'errorifexists'` (Standard), `'ignore'`. |

## Bedeutung der einzelnen Werte

Wörtlich aus der offiziellen API-Referenz (gegengeprüft gegen die AWS- und die inhaltsgleiche Azure-Spiegelseite):

| Wert | Verhalten, falls die Zieldaten (Pfad oder Tabelle) bereits existieren |
| --- | --- |
| `'append'` | „append to existing data" — die neuen Daten werden an die bestehenden Daten angehängt. |
| `'overwrite'` | „overwrite existing data" — die bestehenden Daten werden durch die neuen Daten ersetzt. |
| `'error'` / `'errorifexists'` (**Standard**) | „throw an exception if data exists" — es wird eine Exception ausgelöst, sofern am Ziel bereits Daten vorhanden sind; ohne explizit gesetzten `mode()` ist dies das Verhalten. |
| `'ignore'` | „silently skip if data exists" — der Schreibvorgang wird stillschweigend übersprungen, wenn am Ziel bereits Daten vorhanden sind (kein Fehler, aber auch kein Schreiben). |

## Rückgabewert

`DataFrameWriter`

## Beispiel

```python
import tempfile
with tempfile.TemporaryDirectory(prefix="mode") as d:
    # Overwrite the path with a new Parquet file
    spark.createDataFrame(
        [{"age": 100, "name": "Alice"}]
    ).write.mode("overwrite").format("parquet").save(d)
    # Append another DataFrame into the Parquet file
    spark.createDataFrame(
        [{"age": 120, "name": "Sue"}]
    ).write.mode("append").format("parquet").save(d)
    # Read the Parquet file as a DataFrame.
    spark.read.parquet(d).show()
    # +---+-------------+
    # |age|         name|
    # +---+-------------+
    # |120| Sue          |
    # |100| Alice       |
    # +---+-------------+
```

## Quellen

- DataFrameWriter.mode: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframewriter/mode
- Azure-Spiegelseite (Gegenprüfung der Werte-Beschreibungen, wortgleich): https://learn.microsoft.com/en-us/azure/databricks/pyspark/reference/classes/dataframewriter/mode

**Stand:** 2026-09-11, per `WebFetch` gegen zwei unabhängige Quellen verifiziert.
