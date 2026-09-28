*Verschoben aus `_read_files.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

### XML-spezifische Optionen (Auswahl, gemeinsam mit `spark.read`)

| Option | Werte / Standard |
|---|---|
| `rowTag` | Pflichtoption |
| `mode` | `PERMISSIVE` / `DROPMALFORMED` / `FAILFAST` |
| `inferSchema` | `true` |
| `samplingRatio` | — |
| `rescuedDataColumn` | — |
| `singleVariantColumn` | — |

---

*Verschoben aus `_spark_read.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

| Option | Standardwert | Beschreibung |
|---|---|---|
| `rowTag` | **Pflichtoption**, kein Default | *"This is a required option."* |
| `mode` | dokumentiert ohne genannten expliziten Default | `PERMISSIVE`, `DROPMALFORMED`, `FAILFAST`. |
| `inferSchema` | **`true`** | Abweichend von CSV (`false`)! *"If `true`, attempts to infer an appropriate type for each resulting DataFrame column."* (Bestätigt über zwei unabhängige Abrufe.) |
| `samplingRatio` | `1.0` | Anteil der Zeilen, der für die Schema-Inferenz gesampelt wird. |
| `rescuedDataColumn` | keiner | Bei `spark.read` **nicht** standardmäßig aktiv — muss explizit gesetzt werden. |

```python
# XML mit Pflichtoption rowTag
df = spark.read.format("xml").option("rowTag", "book").load("s3://bucket/books.xml")
```
