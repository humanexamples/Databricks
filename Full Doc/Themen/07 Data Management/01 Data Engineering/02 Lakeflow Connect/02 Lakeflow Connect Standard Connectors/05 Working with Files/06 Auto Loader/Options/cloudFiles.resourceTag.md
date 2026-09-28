# cloudFiles.resourceTag

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | Key-Value-Tag-Paare (Suffix am Options-Namen) |
| **`read_files`-Parameter** | `resourceTag.<key>` |
| **Seit** | alle Versionen |

## Beschreibung

> „A series of key-value tag pairs to help associate and identify related resources, for example: `cloudFiles.option("cloudFiles.resourceTag.myFirstKey", "myFirstValue").option("cloudFiles.resourceTag.mySecondKey", "mySecondValue")`. Do not use when `cloudFiles.useManagedFileEvents` is set to `true`. Instead set resource tags using the cloud provider console."

Wird oft in Prosa als `resourceTags` (Plural) bezeichnet; die Options-Referenz nennt den Schlüssel `cloudFiles.resourceTag`.

## Beispiel

```python
.option("cloudFiles.resourceTag.team", "data-eng")
.option("cloudFiles.resourceTag.env", "prod")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
