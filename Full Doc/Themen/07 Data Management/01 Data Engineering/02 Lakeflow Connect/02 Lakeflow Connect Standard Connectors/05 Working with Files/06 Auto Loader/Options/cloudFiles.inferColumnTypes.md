# cloudFiles.inferColumnTypes

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `false` |
| **Gültige Werte** | `true`, `false` |
| **`read_files`-Parameter** | `inferColumnTypes` (dort ist der Standard `true` — Gegenteil von Auto Loader!) |
| **Seit** | alle Versionen |

## Beschreibung

> „Whether to infer exact column types when leveraging schema inference. By default, columns are inferred as strings when inferring JSON and CSV datasets."

Bei `false` (Standard) inferiert Auto Loader alle Spalten in JSON/CSV/XML als `string`, um Schema-Evolution-Probleme durch Typkonflikte zu vermeiden. Bei `true` wählt Auto Loader Datentypen anhand von Stichprobendaten (Verhalten des Apache-Spark-`DataFrameReader`). Bei typisierten Formaten (Parquet, Avro) ohne Wirkung.

## Beispiel

```python
.option("cloudFiles.inferColumnTypes", True)
```

## Siehe auch

- [../01 Schema-Inferenz und -Evolution.md](../01%20Schema-Inferenz%20und%20-Evolution.md)
- [cloudFiles.schemaHints.md](cloudFiles.schemaHints.md)
