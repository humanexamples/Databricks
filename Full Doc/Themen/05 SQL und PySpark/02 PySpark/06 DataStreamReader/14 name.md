# `DataStreamReader.name()`

Vergibt einen Namen für die Streaming-Quelle (für Checkpoint-Evolution).

## Signatur

```python
name(source_name)
```

## Beschreibung

*"Assigns a name to the streaming source for checkpoint evolution."*

Ermöglicht die Weiterentwicklung von Streaming-Queries: benannte Quellen können umgeordnet oder ergänzt werden, ohne die Checkpoint-Kompatibilität zu brechen. Ist die Quellen-Evolution aktiviert, **müssen alle Quellen benannt werden**.

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `source_name` | `str` | Der Name dieser Streaming-Quelle. Darf nur ASCII-Buchstaben (a–z, A–Z), Ziffern (0–9) und Unterstriche (`_`) enthalten. |

## Voraussetzung

Erfordert aktivierte Streaming-Quellen-Evolution über die Konfiguration `spark.sql.streaming.enableSourceEvolution`.

## Rückgabewert

`DataStreamReader`

## Beispiele

```python
# Mehrere Quellen benennen und vereinigen
df1 = spark.readStream.format("rate").name("source1").load()
df2 = spark.readStream.format("rate").name("source2").load()
query = df1.union(df2).writeStream.format("console").start()
```

```python
# Gültige Namen
spark.readStream.format("rate").name("mySource").load()
spark.readStream.format("rate").name("my_source_123").load()

# Ungültiger Name — löst AnalysisException aus
spark.readStream.format("rate").name("my-source").load()
```

## Quellen

- DataStreamReader.name: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamreader/name

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
