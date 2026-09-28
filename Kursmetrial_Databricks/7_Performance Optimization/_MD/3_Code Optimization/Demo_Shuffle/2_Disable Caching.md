# 2_Disable Caching

Führen Sie die folgende Zelle aus, um eine Spark-Konfigurationsvariable zu setzen, die das Disk Caching deaktiviert.

Das Deaktivieren des Disk Caching verhindert, dass Databricks Cloud-Storage-Dateien nach der ersten Abfrage speichert. Dadurch wird die Wirkung der Optimierungen deutlicher sichtbar, da sichergestellt wird, dass die Dateien bei jeder Abfrage stets aus dem Cloud Storage geladen werden.

Weitere Informationen finden Sie unter Optimize performance with caching on Databricks: [AWS](https://docs.databricks.com/aws/en/optimizations/disk-cache) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/optimizations/disk-cache) | [GCP](https://docs.databricks.com/gcp/en/optimizations/disk-cache).

**HINWEIS:** Dies funktioniert nicht bei Serverless. Bitte verwenden Sie Classic Compute, um das Caching zu deaktivieren. Wenn Sie Serverless verwenden, wird ein Fehler zurückgegeben.

```python
spark.conf.set('spark.databricks.io.cache.enabled', False)
```

