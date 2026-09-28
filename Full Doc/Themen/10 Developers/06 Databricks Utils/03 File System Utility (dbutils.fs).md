# File System Utility (`dbutils.fs`)

Befehle für den Zugriff auf das Databricks-Dateisystem (DBFS). Eine ausführlichere Befehlsreferenz mit weiteren Beispielen zu `ls`/`cp`/`mv`/`rm`/`mkdirs`/`head`/`put` sowie der `%fs`-Magic-Command-Kurzform existiert bereits unter [dbutils.fs — Befehlsreferenz.md](../../04%20Data%20guides/02%20Work%20with%20files/04%20DBFS/02%20dbutils.fs%20%E2%80%94%20Befehlsreferenz.md); Mount-Operationen sind ausführlich in [Mounts und Migration.md](../../04%20Data%20guides/02%20Work%20with%20files/04%20DBFS/03%20Mounts%20und%20Migration.md) behandelt. Diese Seite fasst **alle** offiziell dokumentierten Befehle des Moduls vollständig zusammen. Teil der [Databricks Utils](00%20Uebersicht.md)-Reihe.

## Hinweis zur Python-Syntax

„Die Python-Implementierung aller `dbutils.fs`-Methoden nutzt `snake_case` statt `camelCase`" bei Keyword-Argumenten.

## Befehlsübersicht

| Befehl | Signatur | Beschreibung |
|---|---|---|
| `cp` | `cp(from: String, to: String, recurse: boolean = false): boolean` | kopiert eine Datei/ein Verzeichnis, ggf. über Dateisystemgrenzen hinweg |
| `head` | `head(file: String, max_bytes: int = 65536): String` | gibt bis zu `max_bytes` einer Datei als UTF-8-Text zurück |
| `ls` | `ls(dir: String): Seq` | listet Verzeichnisinhalt auf (Pfad, Name, Größe, Änderungszeit als `FileInfo`-Objekte) |
| `mkdirs` | `mkdirs(dir: String): boolean` | legt das Verzeichnis samt fehlender übergeordneter Verzeichnisse an |
| `mount` | `mount(source: String, mountPoint: String, encryptionType: String = "", owner: String = null, extraConfigs: Map = Map.empty[String, String]): boolean` | hängt ein Quellverzeichnis an einem Mount-Punkt in DBFS ein |
| `mounts` | `mounts: Seq` | zeigt Informationen zu allen aktuell eingehängten Mounts (`MountInfo`-Objekte) |
| `mv` | `mv(from: String, to: String, recurse: boolean = false): boolean` | verschiebt eine Datei/ein Verzeichnis (intern: Kopie + Löschung) |
| `put` | `put(file: String, contents: String, overwrite: boolean = false): boolean` | schreibt einen String UTF-8-kodiert in eine Datei |
| `refreshMounts` | `refreshMounts: boolean` | weist alle Cluster-Maschinen an, ihren Mount-Informations-Cache zu aktualisieren |
| `rm` | `rm(dir: String, recurse: boolean = false): boolean` | löscht eine Datei/ein Verzeichnis; Fehler bei nicht-leerem Verzeichnis ohne `recurse` |
| `unmount` | `unmount(mountPoint: String): boolean` | entfernt einen DBFS-Mount-Punkt |
| `updateMount` | `updateMount(source: String, mountPoint: String, encryptionType: String = "", owner: String = null, extraConfigs: Map = Map.empty[String, String]): boolean` | ändert einen bestehenden Mount-Punkt, statt einen neuen anzulegen — ab Databricks Runtime 10.4 LTS |

## Beispiele

```python
dbutils.fs.cp("/Volumes/main/default/my-volume/data.csv",
              "/Volumes/main/default/my-volume/new-data.csv")
# Out[4]: True

dbutils.fs.head("/Volumes/main/default/my-volume/data.csv", 25)
# Out[12]: 'Year,First Name,County,Se'

dbutils.fs.ls("/Volumes/main/default/my-volume/")
# Out[13]: [FileInfo(path='dbfs:/Volumes/main/default/my-volume/data.csv',
#           name='data.csv', size=2258987, modificationTime=1711357839000)]

dbutils.fs.mkdirs("/Volumes/main/default/my-volume/my-data")
# Out[15]: True

dbutils.fs.mv("/Volumes/main/default/my-volume/rows.csv",
              "/Volumes/main/default/my-volume/my-data/")
# Out[2]: True

dbutils.fs.put("/Volumes/main/default/my-volume/hello.txt",
               "Hello, Databricks!", True)
# Out[6]: True

dbutils.fs.rm("/Volumes/main/default/my-volume/my-data/", True)
# Out[8]: True

# Mounting (siehe Mounts und Migration.md für Auth-Details)
aws_bucket_name = "my-bucket"
mount_name = "s3-my-bucket"
dbutils.fs.mount("s3a://%s" % aws_bucket_name, "/mnt/%s" % mount_name)

dbutils.fs.mounts()
# Out[11]: [MountInfo(mountPoint='/mnt/databricks-results',
#           source='databricks-results', encryptionType='sse-s3')]

dbutils.fs.refreshMounts()

dbutils.fs.updateMount("s3a://%s" % aws_bucket_name, "/mnt/%s" % mount_name)

dbutils.fs.unmount("/mnt/<mount-name>")
```

## Wichtige Hinweise

- **`mount` gilt als Auslaufmodell:** „Databricks empfiehlt, von `dbutils.fs.mount` wegzukommen, da es nicht mit der Serverless-Compute-Architektur kompatibel ist." Dasselbe gilt für `mounts` (Serverless-inkompatibel).
- **Niemals** einen Mount-Punkt ändern, während andere Jobs ihn lesen oder beschreiben.
- **`%fs`-Magic-Command:** Kurzform für `dbutils.fs`, z. B. `%fs ls /Volumes/main/default/my-volume/` — nur für einzeilige, einfache Aufrufe geeignet.
- **Workspace-Dateien:** dafür stattdessen Shell-Befehle wie `%sh ls` nutzen.
- **Einschränkung:** `dbutils`-Aufrufe innerhalb von Executors können zu unerwarteten Ergebnissen oder Fehlern führen.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/databricks-utils#file-system-utility-dbutilsfs

**Stand:** 2026-08-26.
