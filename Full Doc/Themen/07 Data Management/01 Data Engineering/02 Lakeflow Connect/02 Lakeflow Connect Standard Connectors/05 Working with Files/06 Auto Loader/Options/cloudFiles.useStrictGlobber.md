# cloudFiles.useStrictGlobber

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `false` |
| **Gültige Werte** | `true`, `false` |
| **`read_files`-Parameter** | `useStrictGlobber` |
| **Seit** | Databricks Runtime 12.2 LTS und höher |

## Beschreibung

> „Whether to use a strict globber that matches the default globbing behavior of other file sources in Apache Spark. See [Common data loading patterns] for more details."

Bei `true` verhält sich die Glob-Auswertung wie bei anderen Apache-Spark-Dateiquellen (statt des lockereren Auto-Loader-Standardverhaltens).

## Beispiel

```python
.option("cloudFiles.useStrictGlobber", "true")
```

## Siehe auch

- [../14 Common Data Loading Patterns.md](../14%20Common%20Data%20Loading%20Patterns.md) — Glob-Muster
