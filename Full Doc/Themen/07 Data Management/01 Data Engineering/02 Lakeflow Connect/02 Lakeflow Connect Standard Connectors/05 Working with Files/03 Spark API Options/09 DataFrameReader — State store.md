# DataFrameReader options — State store

Bereich: **DataFrameReader options › State store** — Optionen des State-Store-Datenquellen-Readers (`spark.read.format("statestore")`), um den internen Zustand einer Structured-Streaming-Abfrage zu inspizieren.

Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).

| Option | Standard | Typ | Beschreibung | Seit |
|---|---|---|---|---|
| `batchId` | jüngste Batch-ID | Ganzzahl | „The target batch to read from." | |
| `operatorId` | `0` | Ganzzahl | „The target operator to read from." | |
| `storeName` | `DEFAULT` | String | „The target state store name to read from." | |
| `joinSide` | None | enum | „The target side to read from for a stream-stream join." | |
| `snapshotStartBatchId` | None | Ganzzahl | „The batch ID of the snapshot to use as the starting point when reading state." | DBR 15.4 LTS+ |
| `snapshotPartitionId` | None | Ganzzahl | „If specified, the query only reads this partition." | DBR 15.4 LTS+ |
| `readChangeFeed` | `false` | boolean | „When `true`, returns state changes across a specified range of batches." | DBR 16.4 LTS+ |
| `changeStartBatchId` | None | Ganzzahl | „The starting batch ID for the change feed range." | DBR 16.4 LTS+ |
| `changeEndBatchId` | jüngste Batch-ID | Ganzzahl | „The ending batch ID for the change feed range." | DBR 16.4 LTS+ |
| `stateVarName` | None | String | „The state variable name to read." | DBR 16.4 LTS+ |
| `readRegisteredTimers` | `false` | boolean | „When `true`, reads registered timers used by the `transformWithState` operator." | DBR 16.4 LTS+ |
| `flattenCollectionTypes` | `true` | boolean | „When `true`, flattens the records returned for map and list state variables." | DBR 16.4 LTS+ |

## Beispiel

```python
state_df = (spark.read.format("statestore")
  .option("batchId", 12)
  .option("operatorId", 0)
  .load("/Volumes/analytics/bronze/_checkpoint"))
```

## Siehe auch

- [`../04 Dateitypen/09 State Store.md`](../04%20Dateitypen/09%20State%20Store.md)
