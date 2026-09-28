# cloudFiles.pathRewrites

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, AWS S3) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | JSON-Map-String |
| **`read_files`-Parameter** | `pathRewrites` |
| **Seit** | alle Versionen |

## Beschreibung

> „Required only if you specify a `queueUrl` that receives file notifications from multiple S3 buckets and you want to use mount points configured for accessing data in these containers. Use this option to rewrite the prefix of the `bucket/key` path with the mount point. Only prefixes can be rewritten. For example, for the configuration `{"<databricks-mounted-bucket>/path": "dbfs:/mnt/data-warehouse"}`, the path `s3://<databricks-mounted-bucket>/path/2017/08/fileA.json` is rewritten to `dbfs:/mnt/data-warehouse/2017/08/fileA.json`. Do not use when `cloudFiles.useManagedFileEvents` is set to `true`."

## Beispiel

```python
.option("cloudFiles.pathRewrites", '{"<databricks-mounted-bucket>/path": "dbfs:/mnt/data-warehouse"}')
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
- [cloudFiles.queueUrl.md](cloudFiles.queueUrl.md)
