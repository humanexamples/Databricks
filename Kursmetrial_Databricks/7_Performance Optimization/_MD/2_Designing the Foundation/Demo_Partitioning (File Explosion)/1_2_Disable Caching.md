# 1_2_Disable Caching

Führen Sie die folgende Zelle aus, um eine Spark-Konfigurationsvariable zu setzen, die das Disk Caching deaktiviert.

Das Deaktivieren des Disk Caching verhindert, dass Databricks Dateien aus dem Cloud Storage nach der ersten Query zwischenspeichert. Dadurch wird die Wirkung der Optimierungen deutlicher sichtbar, da sichergestellt ist, dass die Dateien bei jeder Query stets aus dem Cloud Storage geladen werden.

Weitere Informationen finden Sie unter Optimize performance with caching on Databricks: [AWS](https://docs.databricks.com/aws/en/optimizations/disk-cache) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/optimizations/disk-cache) | [GCP](https://docs.databricks.com/gcp/en/optimizations/disk-cache).

**HINWEIS:** Dies funktioniert nicht in Serverless. Verwenden Sie Classic Compute, um das Caching zu deaktivieren. Bei Verwendung von Serverless wird ein Fehler zurückgegeben.

```py
spark.conf.set('spark.databricks.io.cache.enabled', False)
```

