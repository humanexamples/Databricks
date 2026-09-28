# Die Datei-Metadatenspalte (_metadata)

Die Spalte `_metadata` liefert Dateimetadaten für Eingabedateien über alle Formate hinweg. Diese versteckte Spalte muss in Leseabfragen explizit selektiert werden, um im resultierenden DataFrame enthalten zu sein.

**Wichtiger Hinweis:** Enthält die Datenquelle bereits eine Spalte namens `_metadata`, liefern Abfragen die Quellspalte zurück statt der Dateimetadaten.

## Unterstützte Metadatenfelder

| Feld | Typ | Beschreibung | Beispiel | Min. Runtime |
| --- | --- | --- | --- | --- |
| `file_path` | STRING | Pfad der Eingabedatei | `file:/tmp/f0.csv` | 10.5 |
| `file_name` | STRING | Dateiname mit Endung | `f0.csv` | 10.5 |
| `file_size` | LONG | Dateigröße in Bytes | 628 | 10.5 |
| `file_modification_time` | TIMESTAMP | Zeitpunkt der letzten Änderung | `2021-12-20 20:05:21` | 10.5 |
| `file_block_start` | LONG | Start des gelesenen Blocks in Bytes | 0 | 13.0 |
| `file_block_length` | LONG | Länge des gelesenen Blocks in Bytes | 628 | 13.0 |

## Best Practices

**Empfehlung:** Nur die tatsächlich benötigten Felder aus der Spalte selektieren – das verhindert Fehler durch Schema Evolution, wenn neue Felder hinzukommen.

**Bei Auto Loader:** Enthalten die Quelldaten bereits eine Spalte `_metadata`, sollte sie in `source_metadata` umbenannt werden, um weiterhin auf die Dateimetadaten der Zieltabelle zugreifen zu können.

**Bei Streaming:** Bei Verwendung von `foreachBatch` sollte die Metadatenspalte im streamenden Lese-DataFrame referenziert werden, bevor die Funktion aufgerufen wird – nicht innerhalb der Funktion.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/file-metadata-column  
**Stand:** 2026-08-07
