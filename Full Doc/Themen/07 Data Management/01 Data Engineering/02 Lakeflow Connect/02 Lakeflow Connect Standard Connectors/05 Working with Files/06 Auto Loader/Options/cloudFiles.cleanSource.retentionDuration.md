# cloudFiles.cleanSource.retentionDuration

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | `30 days` |
| **Datentyp** | CalendarInterval-String (z. B. `14 days`, `2 weeks`, `1 month`) |
| **`read_files`-Parameter** | `cleanSource.retentionDuration` |
| **Seit** | Databricks Runtime 16.4 und höher |

## Beschreibung

> „Amount of time to wait before processed files become candidates for cleanup with clean source."

Minimum bei `DELETE`: mindestens 7 Tage; bei `MOVE` kein Minimum. Nur wirksam bei gesetztem [cloudFiles.cleanSource](cloudFiles.cleanSource.md) (`DELETE` oder `MOVE`).

## Beispiel

```python
.option("cloudFiles.cleanSource.retentionDuration", "14 days")
```

## Siehe auch

- [../10 Clean Source (Quelldateien aufräumen).md](../10%20Clean%20Source%20%28Quelldateien%20aufräumen%29.md)
