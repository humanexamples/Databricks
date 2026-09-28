# Schema-Inferenz und -Evolution in Auto Loader

Auto Loader kann das Schema geladener Daten automatisch erkennen. Dadurch lassen sich Tabellen initialisieren, ohne das Datenschema explizit deklarieren zu müssen.

## Unterstützte Dateiformate

Schema-Inferenz und -Evolution werden unterstützt für:

- JSON (alle Versionen)
- CSV (alle Versionen)
- XML (ab Databricks Runtime 14.3 LTS)
- Avro (ab Databricks Runtime 10.4 LTS)
- Parquet (ab Databricks Runtime 11.3 LTS)

ORC, Text und Binaryfile werden nur eingeschränkt oder gar nicht unterstützt.

## Konfiguration

Schema-Inferenz wird aktiviert, indem für die Option `cloudFiles.schemaLocation` ein Zielverzeichnis angegeben wird:

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "parquet")
  .option("cloudFiles.schemaLocation", "<path-to-schema>")
  .load("<path-to-source-data>")
  .writeStream
  .option("checkpointLocation", "<path-to-checkpoint>")
  .start("<path-to-target>"))
```

## Funktionsweise der Schema-Inferenz

Auto Loader liest eine Stichprobe der ersten 50 GB bzw. 1.000 Dateien (je nachdem, was zuerst erreicht wird), um das Schema abzuleiten. Bei Formaten ohne kodierte Typen (JSON, CSV, XML) werden alle Spalten standardmäßig als String interpretiert. Bei typisierten Formaten (Parquet, Avro) führt Auto Loader die einzelnen Datei-Schemas zusammen.

Typ-Inferenz aktivieren:

```python
.option("cloudFiles.inferColumnTypes", "true")
```

## Schema-Evolution-Modi

Die Option `cloudFiles.schemaEvolutionMode` unterstützt:

| Modus | Verhalten |
| --- | --- |
| `addNewColumns` (Standard) | Stream schlägt fehl, nachdem neue Spalten hinzugekommen sind; ein Neustart setzt die Verarbeitung fort. |
| `addNewColumnsWithTypeWidening` | Fügt neue Spalten hinzu und erweitert kompatible Typen (z. B. int→long). |
| `rescue` | Das Schema wird nie erweitert; neue Spalten werden in `_rescued_data` erfasst. |
| `failOnNewColumns` | Der Stream schlägt dauerhaft fehl; erfordert ein Schema-Update oder das Entfernen der Datei. |
| `none` | Neue Spalten werden ignoriert; keine Schema-Evolution. |

## Rescued-Data-Spalte

Auto Loader erzeugt eine Spalte `_rescued_data`, die enthält:

- im Schema fehlende Spalten
- Typkonflikte
- Abweichungen in Groß-/Kleinschreibung

Dieses JSON-Blob enthält die geretteten Spalten sowie den Quelldateipfad und stellt sicher, dass durch Schema-Inkonsistenzen keine Daten verloren gehen.

## Schema Hints

Mit Schema Hints lassen sich abgeleitete Typen überschreiben, ohne ein vollständiges Schema angeben zu müssen:

```python
.option("cloudFiles.schemaHints", "tags map<string,string>, version int")
```

Schema Hints unterstützen verschachtelte Felder, Arrays und Maps – so lässt sich der Typ bekannter Spalten präzise festlegen.

## Umgang mit Partitionen

Auto Loader leitet Partitionen aus Hive-artigen Verzeichnisstrukturen ab (z. B. `event=click/date=2021-04-01/`). Zusätzliche Partitionen lassen sich angeben über:

```python
.option("cloudFiles.partitionColumns", "event,date,hour")
```

Widersprüchliche oder fehlende Partitionsstrukturen werden ignoriert.

<cell_type>markdown</cell_type>---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/schema  
**Stand:** 2026-08-09
