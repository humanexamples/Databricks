# `cloudFiles.resourceTag`

Vergibt Key-Value-Tags an die von Auto Loader angelegten Cloud-Ressourcen.

## Beschreibung

> *"A series of key-value tag pairs to help associate and identify related resources, for example: `cloudFiles.option("cloudFiles.resourceTag.myFirstKey", "myFirstValue").option("cloudFiles.resourceTag.mySecondKey", "mySecondValue")`. Do not use when `cloudFiles.useManagedFileEvents` is set to `true`. Instead set resource tags using the cloud provider console."*

Anders als die meisten Optionen ist der Key hier Teil des Options-Namens selbst (`cloudFiles.resourceTag.<eigener-key>`), nicht der Wert. In Prosa wird die Option oft im Plural als "resourceTags" bezeichnet, die Options-Referenz nennt aber `cloudFiles.resourceTag` (Singular) als Basisnamen. Gilt nur im klassischen File-Notification-Modus; beim File-Events-Modus werden Tags stattdessen direkt über die Konsole des Cloud-Anbieters gesetzt.

## Beispiel

```python
df = (spark.readStream.format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      .option("cloudFiles.useNotifications", "true")
      .option("cloudFiles.resourceTag.team", "data-eng")
      .option("cloudFiles.resourceTag.env", "prod")
      .load("/Volumes/analytics/bronze/events"))
```

## Quellen

- Auto Loader options: https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/options

**Stand:** 2026-09-15
