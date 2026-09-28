# `cloudFiles.project`

Google-Cloud-Projekt-ID des GCS-Buckets.

## Beschreibung

Die Google-Cloud-Projekt-ID, in der der GCS-Bucket und die Pub/Sub-Ressourcen liegen. Erforderlich, wenn Auto Loader im klassischen File-Notification-Modus (`cloudFiles.useNotifications = true`) die Benachrichtigungsdienste selbst einrichten soll. Zu beachten: Der Cloud Resource Manager (`CloudFilesGCPResourceManager`) verwendet für denselben Zweck stattdessen den Options-Namen `cloudFiles.projectId`.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.project", "my-gcp-project")
      .load("gs://my-bucket/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
