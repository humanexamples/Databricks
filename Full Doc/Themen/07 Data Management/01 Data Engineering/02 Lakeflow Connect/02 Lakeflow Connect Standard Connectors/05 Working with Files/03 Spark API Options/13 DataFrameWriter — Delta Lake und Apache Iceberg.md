# DataFrameWriter options — Delta Lake und Apache Iceberg

Bereich: **DataFrameWriter options › Delta Lake and Apache Iceberg** (Batch- und Streaming-Schreiben in Delta-/Iceberg-Tabellen).

Quelle: [Spark API options reference](https://learn.microsoft.com/en-us/azure/databricks/spark/api-options).

| Option | Standard | Typ | Beschreibung | Seit |
|---|---|---|---|---|
| `clusterByAuto` | `false` | `true`, `false` | „Whether to enable automatic liquid clustering, where Azure Databricks selects clustering columns based on query patterns. Only valid with `mode("overwrite")`. Cannot be used with `append` mode." | DBR 16.4+ |
| `mergeSchema` | None | `true`, `false` | „Whether to enable schema evolution for the write operation. New columns in the source DataFrame are added to the target table schema. Applies to batch and streaming appends." | |
| `overwriteSchema` | None | `true`, `false` | „Whether to replace the table schema and partitioning when overwriting. Requires `mode("overwrite")` without `replaceWhere`. Cannot be used with `partitionOverwriteMode`." | |
| `partitionOverwriteMode` | None | `static`, `dynamic` | „The partition overwrite mode. Set this to `dynamic` to overwrite only partitions containing new data, leaving all other partitions unchanged. Legacy mode, not supported on serverless compute or Databricks SQL." | |
| `replaceOn` | None | Boolean-Ausdruck-String | „A boolean expression that matches rows in the target table to replace with rows from the source query. […] Rows in the target that match a source row are deleted and replaced. If the source is empty, no deletions occur." | DBR 17.1+ |
| `replaceUsing` | None | kommagetrennte Spaltenliste | „A comma-separated list of column names used to match rows between the target table and the source query. […] `NULL` values are treated as not equal and won't match." | DBR 16.3+ |
| `replaceWhere` | None | Prädikat-Ausdruck-String | „A predicate expression. Atomically overwrites only the records that match the predicate." | |
| `targetAlias` | None | String | „A string alias for the target table. Use with `replaceOn` or `replaceWhere` to disambiguate column references when the condition references columns from both the target table and the source query." | |
| `txnAppId` | None | String | „A unique string identifying the application for idempotent writes in `foreachBatch` operations. Use together with `txnVersion` to ensure exactly-once writes to multiple Delta Lake tables." | |
| `txnVersion` | None | monoton steigende Ganzzahl | „A monotonically increasing number used as the transaction version for idempotent writes in `foreachBatch` operations. Use together with `txnAppId`." | |
| `optimizeWrite` | None | `true`, `false` | „Whether to enable Auto Optimize Write for this write operation. Overrides the `spark.databricks.delta.optimizeWrite.enabled` configuration." | |
| `userMetadata` | None | String | „A user-defined string appended to the commit metadata for the write operation. Visible in the output of `DESCRIBE HISTORY`." | |

## Beispiel

```python
(df.write.format("delta")
  .mode("overwrite")
  .option("replaceWhere", "event_date >= '2026-09-01'")
  .option("userMetadata", "reprocess-2026-09")
  .saveAsTable("analytics.silver.events"))
```

```python
# Idempotente foreachBatch-Writes in mehrere Delta-Tabellen
def upsert(batch_df, batch_id):
    (batch_df.write.format("delta")
      .option("txnAppId", "events-pipeline")
      .option("txnVersion", batch_id)
      .mode("append").saveAsTable("analytics.silver.events"))
```
