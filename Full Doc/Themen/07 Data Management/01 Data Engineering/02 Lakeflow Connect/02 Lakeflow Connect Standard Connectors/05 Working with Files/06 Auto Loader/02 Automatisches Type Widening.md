# Auto Loader — Automatisches Type Widening

Quelle: [Automatic type widening with Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/type-widening) (Public Preview).

Auto Loader reduziert den Pflegeaufwand von Pipelines, indem es komplexe Schema-Änderungen automatisch handhabt. Mit dem Schema-Evolution-Modus `addNewColumnsWithTypeWidening` erweitert Auto Loader zusätzlich zum Hinzufügen neuer Spalten automatisch kompatible Datentypänderungen (z. B. `int` zu `long` oder `float` zu `double`), ohne dass Daten neu geschrieben werden müssen oder Nutzereingriff nötig ist.

---

## Unterstützte Typänderungen

| Quelltyp | Mögliche Zieltypen |
|---|---|
| `byte` | `short`, `int`, `long`, `decimal`, `double` |
| `short` | `int`, `long`, `decimal`, `double` |
| `int` | `long`, `decimal`, `double` |
| `long` | `decimal` |
| `float` | `double` |
| `decimal` | `decimal` mit größerer Präzision und Skala |
| `date` | `timestampNTZ` (nur für Parquet-Dateien) |

Type Widening gilt laut Doku für alle Formate mit Schema-Evolution-Unterstützung — sowohl Textformate (JSON, CSV, XML) als auch Binärformate (Avro, Parquet).

---

## Voraussetzungen

**Databricks Runtime 16.4 oder höher.** Ist die Schreib-Senke eine Delta-Lake-Tabelle, muss Type Widening zusätzlich auf dieser Tabelle aktiviert sein:

```sql
-- Für bestehende Tabellen:
ALTER TABLE <table_name> SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true')

-- Bei Neuanlage:
CREATE TABLE T(c1 INT) TBLPROPERTIES('delta.enableTypeWidening' = 'true')
```

---

## Aktivierung über `addNewColumnsWithTypeWidening`

```python
query = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("cloudFiles.inferColumnTypes", True)
  .option("cloudFiles.schemaLocation", "<schemaPath>")
  .option("cloudFiles.schemaEvolutionMode", "addNewColumnsWithTypeWidening")
  .load("<inputPath>")
  .writeStream
  .option("mergeSchema", "true")
  .option("checkpointLocation", "<checkpointPath>")
  .trigger(availableNow=True)
  .toTable("table_name"))
```

---

## Präzision bei Erweiterung auf `decimal`

Beim Erweitern eines beliebigen numerischen Typs auf `decimal` erweitert Auto Loader auf ein `decimal` mit einer Präzision, die mindestens der Ausgangs-Präzision entspricht.

| Typ | Ausgangs-Präzision |
|---|---|
| `byte` | 10 |
| `short` | 10 |
| `int` | 10 |
| `long` | 20 |

**Beispiel aus der Doku:** Wird eine Spalte vom Typ `int` gelesen und tritt in einer Datei `decimal(5, 2)` für dieselbe Spalte auf, erweitert Auto Loader auf `decimal(12, 2)`.

---

## Verhalten je Modus bei typ-erweiterbarer Änderung

Wird eine Spalte `id` zunächst als `INT` inferiert und erscheint anschließend ein Wert außerhalb des `INT`-Bereichs (z. B. `2147483648`):

| Modus | Verhalten |
|---|---|
| `addNewColumns` (Standard) | Datentyp entwickelt sich **nicht** weiter; Stream schlägt wegen der Typänderung nicht fehl; Spalte mit dem abweichenden Wert wird für diese Zeile `NULL`, der Originalwert landet in der Rescued-Data-Spalte. |
| `rescue` | Schema entwickelt sich nicht weiter, kein Fehlschlag; abweichender Wert wird `NULL` + in Rescued-Data-Spalte gerettet. |
| `failOnNewColumns` | Wie `addNewColumns` bei Typänderungen (kein Fehlschlag, Rettung in Rescued-Data-Spalte); Fehlschlag ausschließlich bei **neuen** Spalten. |
| `none` | Keine Schema-Evolution, keine Rettung (außer `rescuedDataColumn` separat gesetzt). |
| `addNewColumnsWithTypeWidening` | Stream schlägt (bewusst) fehl. Neue Spalten werden zum Schema hinzugefügt, und unterstützte Datentypänderungen werden erweitert; die Spalte wird beim Neustart auf den passenden Zieltyp erweitert (`INT` → `BIGINT`), der Wert bleibt erhalten statt gerettet zu werden. |

---

## Einschränkungen

- Die Option `prefersDecimal` kann bei Verwendung von `addNewColumnsWithTypeWidening` nicht auf `false` gesetzt werden (Standard `true`).
- `date`-zu-`timestampNTZ`-Widening wird nur für Parquet-Dateien unterstützt.
