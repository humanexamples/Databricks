# `DataFrame.isStreaming` (Eigenschaft)

Gibt `True` zurück, wenn dieser `DataFrame` eine oder mehrere Quellen enthält, die kontinuierlich Daten liefern, sobald sie eintreffen. Ein `DataFrame`, der aus einer Streaming-Quelle liest, muss als `StreamingQuery` über die Methode `start` des `DataStreamWriter` ausgeführt werden. Methoden, die eine einzelne Antwort liefern, etwa `count` oder `collect`, lösen bei vorhandener Streaming-Quelle eine `AnalysisException` aus.

## Rückgabewert

`bool`

## Beispiel

```python
df = spark.readStream.format("rate").load()
df.isStreaming
# True
```

Siehe auch [`writeStream`](04%20writeStream.md).

## Quellen

- DataFrame.isStreaming: https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe/isStreaming

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
