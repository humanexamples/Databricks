# cloudFiles.partitionColumns

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | kommagetrennte Liste von Spaltennamen |
| **`read_files`-Parameter** | `partitionColumns` |
| **Seit** | alle Versionen |

## Beschreibung

> „A comma-separated list of Hive-style partition columns that you would like inferred from the directory structure of the files. Hive-style partition columns are key-value pairs combined by an equality sign such as `<base-path>/a=x/b=1/c=y/file.format`. In this example, the partition columns are `a`, `b`, and `c`."

Bei Schema-Inferenz werden diese Spalten automatisch hinzugefügt, sofern `<base-path>` als Ladepfad angegeben ist. Bei explizitem Schema erwartet Auto Loader die Spalten im Schema. `""` ignoriert Partitionsspalten. Wichtig: Auto Loader berücksichtigt Partitionsspalten **nicht** bei der Schema-Evolution — neue Partitionsspalten müssen hier explizit aufgeführt werden.

## Beispiel

```python
.option("cloudFiles.partitionColumns", "event,date,hour")
```

## Siehe auch

- [../01 Schema-Inferenz und -Evolution.md](../01%20Schema-Inferenz%20und%20-Evolution.md) — Abschnitt Partitionsspalten
