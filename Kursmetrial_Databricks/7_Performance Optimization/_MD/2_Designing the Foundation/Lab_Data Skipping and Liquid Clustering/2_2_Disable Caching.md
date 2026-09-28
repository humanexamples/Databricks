# 2_2_Disable Caching

Führen Sie die folgende Zelle aus, um eine Spark-Konfigurationsvariable zu setzen, die das Disk Caching deaktiviert.

Das Deaktivieren des Disk Caching **verhindert, dass Databricks Cloud-Storage-Dateien nach dem ersten Query zwischenspeichert. Dadurch wird der Effekt der Optimierungen deutlicher sichtbar, da die Dateien bei jedem Query stets aus dem Cloud Storage geladen werden.**

Weitere Informationen finden Sie unter [Optimize performance with caching on Databricks](https://docs.databricks.com/en/optimizations/disk-cache.html#optimize-performance-with-caching-on-databricks).

**HINWEIS:** Dies funktioniert nicht in Serverless. Bitte verwenden Sie Classic Compute, um das Caching zu deaktivieren. Wenn Sie Serverless verwenden, wird ein Fehler zurückgegeben.

```python
# Die Spark-Konfigurationsvariable "io.cache" auf "False" setzen
spark.conf.set('spark.databricks.io.cache.enabled', False)
```

