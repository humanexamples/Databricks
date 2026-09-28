*Verschoben aus `_read_files.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

### Avro-spezifische Optionen (Auswahl, gemeinsam mit `spark.read`)

| Option | Werte / Standard |
|---|---|
| `avroSchema` | — |
| `avroSchemaEvolutionMode` | `none` / `restart` — `restart` löst bei Schema-Änderung eine `UnknownFieldException` aus |
| `mergeSchema` | — |
| `mode` | Standardwert hier `FAILFAST`, abweichend von CSV/JSON |
| `rescuedDataColumn` | — |

**Wichtig:** Anders als bei CSV und JSON (Standard `PERMISSIVE`) ist der Standard-`mode` bei **Avro** `FAILFAST` — ein nicht parsbarer Avro-Datensatz führt also standardmäßig zu einer Exception, sofern `mode` nicht explizit auf `PERMISSIVE` oder `DROPMALFORMED` gesetzt wird.

---

*Verschoben aus `_spark_read.md`, Abschnitt 3 (Vollständige Optionsreferenz):*

| Option | Standardwert | Beschreibung |
|---|---|---|
| `mode` | **`FAILFAST`** | Abweichend von CSV/JSON! Parser-Modus für korrupte Datensätze — `FAILFAST` wirft standardmäßig eine Exception. (Bestätigt über zwei unabhängige Abrufe.) |
| `avroSchema` | keiner | Explizites Avro-Schema (Avro-Schema-String). |
| `avroSchemaEvolutionMode` | `none` | *"How to handle schema evolution when using a schema registry. `none` ignores schema changes and continues the job. `restart` raises an `UnknownFieldException` when schema changes are detected and requires a job restart."* Laut Doku Teil der **Batch**-Avro-Optionen (`spark.read.format("avro")`), nicht nur Streaming. |
| `mergeSchema` | `false` | Wie bei Parquet/ORC. |
| `rescuedDataColumn` | keiner | Bei `spark.read` **nicht** standardmäßig aktiv — muss explizit gesetzt werden. |

```python
# Avro mit explizitem PERMISSIVE-Modus (Standard wäre sonst FAILFAST!)
df = spark.read.format("avro").option("mode", "PERMISSIVE").load("s3://bucket/avro-data")
```
