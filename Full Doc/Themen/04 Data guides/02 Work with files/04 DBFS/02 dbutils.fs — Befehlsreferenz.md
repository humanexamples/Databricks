# `dbutils.fs` — Befehlsreferenz (inkl. `%fs`-Kurzform)

Referenz für die allgemeinen `dbutils.fs`-Dateisystem-Befehle und ihre `%fs`-Magic-Command-Kurzform in Databricks-Notebooks. Ergänzt [DBFS Grundlagen.md](DBFS%20Grundlagen.md) (Überblick über DBFS) und [Mounts und Migration.md](Mounts%20und%20Migration.md) (`dbutils.fs.mount()`/`unmount()` speziell für Cloud-Storage-Mounts) um die übrigen, allgemeinen Dateisystem-Operationen.

## `%fs` — Kurzform für `dbutils.fs`

Bestätigt: *"Execute dbutils filesystem commands. Shorthand for `dbutils.fs` commands."*

```python
%fs ls /path
```

`%fs` ist eine abgekürzte Syntax für `dbutils.fs`-Aufrufe — man kann Dateisystem-Operationen ausführen, ohne `dbutils.fs` explizit aufzurufen. Die Kurzform eignet sich nur für einzeilige, einfache Aufrufe; für Aufrufe mit mehreren Argumenten (z. B. `recurse=True`) ist `dbutils.fs` direkt nötig.

## Verfügbare `dbutils.fs`-Befehle (zweifach verifiziert)

| Befehl | Syntax | Beschreibung |
|---|---|---|
| `ls` | `ls(dir: String): Seq` | Listet den Inhalt eines Verzeichnisses auf (Pfad, Name, Größe, Änderungszeit). |
| `cp` | `cp(from: String, to: String, recurse: boolean = false): boolean` | Kopiert eine Datei oder ein Verzeichnis, ggf. über Dateisystemgrenzen hinweg. `recurse` kopiert Verzeichnisse samt Inhalt. |
| `mv` | `mv(from: String, to: String, recurse: boolean = false): boolean` | Verschiebt eine Datei oder ein Verzeichnis, ggf. über Dateisystemgrenzen hinweg — intern eine Kopie gefolgt von einem Löschvorgang. |
| `rm` | `rm(dir: String, recurse: boolean = false): boolean` | Löscht eine Datei oder ein Verzeichnis. Bei einem nicht-leeren Verzeichnis ohne `recurse` wird ein Fehler geworfen. |
| `mkdirs` | `mkdirs(dir: String): boolean` | Legt das angegebene Verzeichnis an, falls es nicht existiert — inklusive aller nötigen übergeordneten Verzeichnisse. |
| `head` | `head(file: String, max_bytes: int = 65536): String` | Gibt bis zu der angegebenen maximalen Byte-Anzahl einer Datei als UTF-8-String zurück. |
| `put` | `put(file: String, contents: String, overwrite: boolean = false): boolean` | Schreibt den angegebenen String UTF-8-kodiert in eine Datei. |

**Für `mount`/`unmount`** siehe [Mounts und Migration.md](Mounts%20und%20Migration.md), Abschnitt 3 — diese Befehle sind speziell für Cloud-Storage-Mounts und dort ausführlich behandelt.

```python
# Beispiele mit dbutils.fs direkt (äquivalent zu den %fs-Kurzformen)
dbutils.fs.ls("/Volumes/main/schema/volume/")
dbutils.fs.cp("/source/path", "/target/path", recurse=True)
dbutils.fs.mkdirs("/Volumes/main/schema/volume/new_folder")
dbutils.fs.rm("/Volumes/main/schema/volume/old_file.csv")
```

```python
# Äquivalente Kurzform über %fs (nur einzeilige, einfache Aufrufe)
%fs ls /Volumes/main/schema/volume/
%fs mkdirs /Volumes/main/schema/volume/new_folder
```

## Quellen

- Develop code in Databricks notebooks (Magic Commands): https://docs.databricks.com/aws/en/notebooks/notebooks-code
- Databricks Utilities (`dbutils.fs`): https://docs.databricks.com/aws/en/dev-tools/databricks-utils

**Stand:** 2026-08-17, alle Angaben per `WebFetch` verifiziert; auffällige/spezifische Details (Syntaxsignaturen) zusätzlich mit einem zweiten, unabhängigen Abruf gegengeprüft.
