View parquet data

```sql
SELECT * 
FROM parquet.`/Volumes/dbacademy_ecommerce/v01/raw/users-historical`;
```

```sql
CREATE TABLE historical_users_bronze_ctas_rf 
SELECT * 
FROM read_files(
        '/Volumes/dbacademy_ecommerce/v01/raw/users-historical',
        format => 'parquet'
      );
```

---

*Verschoben aus `_read_files.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

### Parquet-spezifische Optionen (Auswahl, gemeinsam mit `spark.read`)

| Option | Werte / Standard |
|---|---|
| `mergeSchema` | `false` |
| `datetimeRebaseMode` / `int96RebaseMode` | `LEGACY` / `EXCEPTION` / `CORRECTED` |
| `rescuedDataColumn` | — |

---

*Verschoben aus `_spark_read.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

| Option | Standardwert | Beschreibung |
|---|---|---|
| `mergeSchema` | `false` | *"Whether to infer the schema across multiple files and to merge the schema of each file."* |
| `datetimeRebaseMode` | `LEGACY` | Steuert Umrechnung von `DATE`/`TIMESTAMP` zwischen julianischem und proleptisch-gregorianischem Kalender. |
| `int96RebaseMode` | `LEGACY` | Analog für `INT96`-Zeitstempel. |
| `readerCaseSensitive` | `true` | Steuert Groß-/Kleinschreibungs-Verhalten, wenn `rescuedDataColumn` aktiv ist. |
| `rescuedDataColumn` | keiner | Bei `spark.read` **nicht** standardmäßig aktiv — muss explizit gesetzt werden. |

```python
# Parquet mit Schema-Merge über mehrere Dateien hinweg
df = spark.read.option("mergeSchema", True).parquet("s3://bucket/parquet-data")
```

