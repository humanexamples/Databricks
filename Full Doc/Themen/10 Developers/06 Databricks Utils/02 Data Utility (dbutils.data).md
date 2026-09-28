# Data Utility (`dbutils.data`)

Befehl zum Verstehen und Untersuchen von Datasets über automatisch berechnete Zusammenfassungsstatistiken. Teil der [Databricks Utils](00%20Uebersicht.md)-Reihe.

## Status und Verfügbarkeit

**Public Preview.** Erfordert **Databricks Runtime 9.0 oder höher**. Verfügbar in Python, R und Scala.

## Befehl: `summarize`

**Signatur:**

```
summarize(df: Object, precise: boolean): void
```

„Berechnet und zeigt Zusammenfassungsstatistiken eines Apache-Spark- oder pandas-DataFrames an."

| Parameter | Bedeutung |
|---|---|
| `df` | zu analysierender Spark- oder pandas-DataFrame |
| `precise` | Boolean (ab Databricks Runtime 10.4 LTS); Standard `false` |

**Genauigkeitsmodi:**

- **`precise=false`** (Standard, nutzt Approximationen für kürzere Laufzeit):
  - Distinct-Value-Counts bei hochkardinalen kategorialen Spalten: bis zu ~5 % relativer Fehler.
  - Häufigkeits-Counts bei mehr als 10.000 verschiedenen Werten: bis zu 0,01 % Fehler.
  - Histogramme und Perzentil-Schätzungen: bis zu 0,01 % relativer Fehler.
- **`precise=true`** (höhere Genauigkeit, höhere Laufzeitkosten):
  - Alle Statistiken außer Histogrammen und Perzentilen numerischer Spalten sind exakt.
  - Histogramme und Perzentil-Schätzungen: bis zu 0,0001 % relativer Fehler.

**Wichtiger Vorbehalt:** „Dieser Befehl analysiert den vollständigen Inhalt des DataFrames. Die Ausführung bei sehr großen DataFrames kann sehr teuer sein."

## Beispiel

```python
df = spark.read.format('csv').load(
  '/databricks-datasets/Rdatasets/data-001/csv/ggplot2/diamonds.csv',
  header=True,
  inferSchema=True)
dbutils.data.summarize(df)
```

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/databricks-utils#data-utility-dbutilsdata

**Stand:** 2026-08-26.
