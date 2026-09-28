# cloudFiles.project

| | |
|---|---|
| **Kategorie** | File Notification Mode option (klassisch, GCS) |
| **Seite** | `spark.readStream` (`DataStreamReader`) |
| **Standardwert** | None |
| **Datentyp** | String |
| **`read_files`-Parameter** | `project` |

## Beschreibung

Die Google-Cloud-Projekt-ID, in der der GCS-Bucket und die Pub/Sub-Ressourcen liegen. Erforderlich, wenn Auto Loader die Benachrichtigungsdienste selbst einrichtet (`cloudFiles.useNotifications = true`).

> Hinweis: Der Cloud Resource Manager (`CloudFilesGCPResourceManager`) verwendet stattdessen den Options-Namen `cloudFiles.projectId`.

*(Beschreibung sinngemäß nach der Spark API options reference; GCS-Tabelle beim Abruf abgeschnitten.)*

## Beispiel

```python
.option("cloudFiles.project", "my-gcp-project")
```

## Siehe auch

- [../06 File Notification Mode.md](../06%20File%20Notification%20Mode.md)
