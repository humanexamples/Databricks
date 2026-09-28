[← Übersicht](00%20Uebersicht.md)

# Fall 7 – Backfill großer Altbestände zusätzlich zum laufenden Stream

**A) Auto Loader lädt vorhandene Dateien automatisch mit** (`cloudFiles.includeExistingFiles` = `true`, Default). Der erste Lauf zieht den kompletten Bestand, danach nur Neues.

**B) Garantierte Vollständigkeit im Notification-Modus – asynchroner Backfill**

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", checkpoint)
  .option("cloudFiles.useNotifications", "true")
  .option("cloudFiles.backfillInterval", "1 week")   # periodisches Voll-Listing gegen verpasste Events
  .load("/Volumes/catalog/schema/landing/")
  .writeStream.option("checkpointLocation", checkpoint)
  .trigger(processingTime="1 minute")
  .toTable("catalog.schema.bronze"))
```

**C) Getrennte Backfill-Ladung** in dieselbe Zieltabelle (einmaliger `COPY INTO` oder CTAS aus dem Archivpfad), danach Auto Loader nur auf den Landing-Pfad.

**D) Durchsatz beim Backfill steuern**: `cloudFiles.maxFilesPerTrigger` (Default `1000`), `cloudFiles.maxBytesPerTrigger`.

---
[← Vorheriger Fall](06%20Change-Events%20in%20Dateien.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](08%20Spaete%2C%20unsortierte%20Dateien.md)
