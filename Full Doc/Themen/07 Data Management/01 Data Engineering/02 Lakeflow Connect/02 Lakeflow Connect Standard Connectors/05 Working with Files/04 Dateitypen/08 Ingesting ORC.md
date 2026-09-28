*Verschoben aus `_read_files.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

### ORC-spezifische Optionen (Auswahl, gemeinsam mit `spark.read`)

| Option | Werte / Standard |
|---|---|
| `mergeSchema` | `false` |

---

*Verschoben aus `_spark_read.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

| Option | Standardwert | Beschreibung |
|---|---|---|
| `mergeSchema` | `false` | Wie bei Parquet. |

```python
df = spark.read.option("mergeSchema", True).orc("s3://bucket/orc-data")
```
