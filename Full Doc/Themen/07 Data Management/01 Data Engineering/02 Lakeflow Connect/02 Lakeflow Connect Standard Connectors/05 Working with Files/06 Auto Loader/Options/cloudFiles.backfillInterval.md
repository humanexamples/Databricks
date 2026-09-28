# cloudFiles.backfillInterval

| | |
|---|---|
| **Kategorie** | Common Auto Loader option |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | Dauer-String (z. B. `1 day`, `1 week`) |
| **`read_files`-Parameter** | `backfillInterval` |
| **Seit** | alle Versionen |

## Beschreibung

> „Auto Loader can trigger asynchronous backfills at a given interval. […] Do not use when `cloudFiles.useManagedFileEvents` is set to `true`."

Löst asynchrone Backfills (vollständige Verzeichnisauflistung zur Sicherstellung der Vollständigkeit) in festem Intervall aus. Regelmäßige Backfills verursachen **keine** Duplikate. Früher für den klassischen File-Notification-Modus empfohlen; bei File Events nicht nötig (Backfills werden dort automatisch gehandhabt) und **nicht erlaubt**.

## Beispiel

```python
.option("cloudFiles.backfillInterval", "1 week")
```

## Siehe auch

- [../09 Datei-Tracking und Checkpoints.md](../09%20Datei-Tracking%20und%20Checkpoints.md)
- [cloudFiles.useManagedFileEvents.md](cloudFiles.useManagedFileEvents.md)
