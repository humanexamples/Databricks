# `cloudFiles.pathRewrites`

Schreibt Pfad-Präfixe bei einer Multi-Bucket-Queue auf Mount-Points um.

## Beschreibung

> *"Required only if you specify a `queueUrl` that receives file notifications from multiple S3 buckets and you want to use mount points configured for accessing data in these containers. Use this option to rewrite the prefix of the `bucket/key` path with the mount point. Only prefixes can be rewritten. For example, for the configuration `{"<databricks-mounted-bucket>/path": "dbfs:/mnt/data-warehouse"}`, the path `s3://<databricks-mounted-bucket>/path/2017/08/fileA.json` is rewritten to `dbfs:/mnt/data-warehouse/2017/08/fileA.json`. Do not use when `cloudFiles.useManagedFileEvents` is set to `true`."*

Nur relevant, wenn eine bereits bestehende SQS-Queue (`cloudFiles.queueUrl`) Benachrichtigungen aus **mehreren** S3-Buckets empfängt und man stattdessen konfigurierte Mount-Points zum Datenzugriff nutzen möchte. Es können ausschließlich Pfad-Präfixe umgeschrieben werden, keine beliebigen Teilpfade. Gilt nur im klassischen File-Notification-Modus, nicht im File-Events-Modus.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.queueUrl", "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue")
      .option("cloudFiles.pathRewrites", '{"<databricks-mounted-bucket>/path": "dbfs:/mnt/data-warehouse"}')
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
