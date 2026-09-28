# Tabellen mit benutzerdefinierten Metadaten anreichern

Databricks empfiehlt, Kommentare für Tabellen und Spalten anzulegen. Dafür gibt es auch KI-generierte Vorschläge. Unity Catalog unterstützt zusätzlich das Taggen von Daten und das Protokollieren eigener Commit-Nachrichten im Transaktionsprotokoll.

## Benutzerdefinierte Commit-Metadaten setzen

Über die DataFrameWriter-Option `userMetadata` können Sie eigene Strings als Metadaten in einem Commit hinterlegen. Das funktioniert mit jedem Schreibmodus, zum Beispiel `append` und `overwrite`. Diese Metadaten lassen sich später über `DESCRIBE HISTORY` auslesen.

SQL-Beispiel (Delta-Tabellen):

```sql
%sql
SET spark.databricks.delta.commitInfo.userMetadata=overwrite-comment
INSERT OVERWRITE target_table SELECT * FROM data_source
```

SQL-Beispiel (Iceberg-Tabellen):

```sql
%sql
SET spark.databricks.iceberg.commitInfo.userMetadata=overwrite-comment
INSERT OVERWRITE target_table SELECT * FROM data_source
```

Python-Beispiel:

```python
df.write \
    .mode("overwrite") \
    .option("userMetadata", "overwrite-comment") \
    .saveAsTable("target_table")
df.write \
    .mode("append") \
    .option("userMetadata", "append-comment") \
    .saveAsTable("target_table")
```

## Hinweise zu den Compute-Typen

Bei klassischem Compute unterstützen SparkSession-Konfigurationsschlüssel die Commit-Metadaten. Sind beide Wege gleichzeitig angegeben, hat die DataFrameWriter-Option Vorrang.

Bei Serverless Compute müssen Sie direkt die DataFrameWriter-Option verwenden. SparkSession-Konfigurationsschlüssel werden dort nicht unterstützt.

---
**Quelle:** https://docs.databricks.com/aws/en/tables/operations/custom-metadata  
**Stand:** 2026-08-06
