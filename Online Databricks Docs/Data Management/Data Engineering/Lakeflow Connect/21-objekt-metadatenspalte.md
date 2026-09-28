# Die Objekt-Metadatenspalte (_object_metadata)

Die Spalte `_object_metadata` (Public Preview) macht Cloud-Objekt-Eigenschaften für jede von einer dateibasierten Datenquelle gelesene Datei zugänglich. Sie erfordert Databricks Runtime 18.2 oder höher und funktioniert mit allen Eingabedateiformaten aus Cloud Object Storage.

Im Unterschied zur Spalte `_metadata` (Dateipfad und -größe) liefert `_object_metadata` umfangreichere, über Cloud-APIs abgerufene Speicherschicht-Eigenschaften – u. a. MIME-Typ, ETag, benutzerdefinierte Schlüssel-Wert-Metadaten, systemdefinierte Metadaten und Objekt-Tags.

## Schema-Felder

Die Spalte `_object_metadata` ist eine STRUCT mit folgenden nullbaren Feldern:

| Feld | Typ | Zweck |
| --- | --- | --- |
| `mime_type` | STRING | Content-Type (z. B. `application/parquet`) |
| `etag` | STRING | Versionierungs-Kennung des Objekts |
| `user_metadata` | VARIANT | Benutzerdefinierte Schlüssel-Wert-Paare |
| `system_metadata` | VARIANT | Vom Cloud-Anbieter definierte Schlüssel-Wert-Paare |
| `tags` | VARIANT | Benutzerdefinierte Objekt-Tags |

## Batch-Dateien lesen

```python
path = "<path-to-load-from>"
df = spark.read.format("csv").load(path)
display(df.select("*", "_metadata", "_object_metadata"))
```

## Streaming mit Auto Loader

```python
dsw = (spark.readStream
    .format("cloudFiles")
    .option("cloudFiles.format", "text")
    .load(path)
    .selectExpr("*", "_metadata as md", "_object_metadata as obj_md")
    .writeStream
    .format("delta")
    .start(table))
```

## Gezielt einzelne Felder selektieren

Um Schemafehler zu vermeiden, sollten gezielt einzelne Felder statt der gesamten Struktur selektiert werden:

```python
df.select("_object_metadata.user_metadata", "_object_metadata.tags", "_object_metadata.etag")
```

## COPY INTO mit Metadaten

```sql
%sql
COPY INTO my_delta_table
FROM (SELECT *, _object_metadata FROM '<path>')
FILEFORMAT = CSV
```

## VARIANT-Werte extrahieren

```sql
%sql
SELECT _object_metadata.user_metadata:my_key::STRING AS my_key
FROM csv.`<path>`
```

## Wichtige Hinweise

Unterstützt werden Amazon S3, Azure DFS, Azure Blob und GCP. Zusätzliche API-Aufrufe pro Datei können bei sehr vielen kleinen Dateien zu höherer Latenz führen. Die Tag-Unterstützung variiert: S3 und Azure Blob Storage werden unterstützt, andere Anbieter liefern leere Objekte zurück. Für S3 ist die Berechtigung `s3:GetObjectTagging` erforderlich. Bei Databricks-verwaltetem Speicher sind System-Metadaten, Benutzer-Metadaten und Tags nicht verfügbar und werden auf `null` gesetzt.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/object-metadata-column  
**Stand:** 2026-08-07
