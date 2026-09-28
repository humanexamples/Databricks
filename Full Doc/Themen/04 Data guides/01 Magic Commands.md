# Magic Commands in Databricks-Notebooks

Fasst die wichtigsten Magic Commands in Databricks-Notebooks zusammen — allen voran `%sh` (Shell-Befehle) und `%run` (Notebook-Verkettung), ergänzt um eine Kurzübersicht der übrigen Magic Commands. Für die dateisystembezogene Magic Command `%fs`/`dbutils.fs` siehe [Work with files/DBFS/dbutils.fs — Befehlsreferenz.md](Work%20with%20files/DBFS/dbutils.fs%20%E2%80%94%20Befehlsreferenz.md).

## `%sh` — Shell-/Bash-Befehle ausführen

Bestätigt: *"Execute shell commands. Runs only on driver node."*

```python
%sh ls -la
```

**Wichtige Einschränkung:** `%sh` läuft ausschließlich auf dem Apache-Spark-**Treiber** (Driver), nicht auf den Worker-Knoten. Um Shell-Befehle auf allen Knoten auszuführen, ist stattdessen ein **Init-Skript** nötig.

**Fehlerbehandlung mit `-e`:** Bestätigt: *"To fail the cell if the shell command has a non-zero exit status, add the -e option."* Ohne `-e` schlägt die Zelle bei einem fehlerhaften Shell-Befehl nicht automatisch fehl.

```python
%sh -e some-command-that-might-fail
```

## `%run` — Ein anderes Notebook ausführen

Bestätigt: *"Execute another notebook, importing its functions and variables."*

```python
# Running ipynb Files
%run ./Classroom-Setup-Common
```

```python
%run /path/to/notebook
```

**Wichtige Einschränkung:** `%run` muss allein in einer Zelle stehen — der Befehl führt das referenzierte Notebook vollständig inline im aktuellen Ausführungskontext aus; Funktionen und Variablen aus dem ausgeführten Notebook stehen danach im aufrufenden Notebook zur Verfügung.

## Weitere Magic Commands (Kurzübersicht, gleiche Quelle)

Zur Einordnung von `%sh`/`%run` im Gesamtbild — alle Magic Commands stammen von derselben Doku-Seite:

| Befehl | Zweck |
|---|---|
| `%python`, `%r`, `%scala`, `%sql` | Zellsprache umschalten; Code in der jeweiligen Sprache ausführen. Bei `%sql` sind Ergebnisse in Python-/SQL-Zellen als `_sqldf` verfügbar. |
| `%md` | Zellsprache auf Markdown umschalten; rendert Text, Bilder, Formeln, LaTeX. |
| `%fs` | Dateisystem-Befehle (Kurzform für `dbutils.fs`) — siehe [Work with files/DBFS/dbutils.fs — Befehlsreferenz.md](Work%20with%20files/DBFS/dbutils.fs%20%E2%80%94%20Befehlsreferenz.md). |
| `%pip` | Installiert Python-Pakete (Notebook-scoped). |
| `%uv pip` | Installiert/verwaltet Python-Pakete (Notebook-scoped) mit `uv` und Standard-pip-Subcommands. |
| `%skip` | Überspringt die Zellausführung — die Zelle läuft nicht mit, wenn das Notebook ausgeführt wird. |
| `%tensorboard` | Zeigt die TensorBoard-UI inline an. Nur auf Databricks Runtime ML verfügbar. |
| `%%profile` | Profiled die Python-Code-Ausführung; zeigt einen hierarchischen Call-Tree mit Timing-Informationen. |
| `%%oprofile` | Profiled die Objekterzeugung während der Zellausführung. |
| `%set_cell_max_output_size_in_mb` | Setzt die maximale Zellen-Output-Größe (Bereich: 1–20 MB). |

## Quellen

- Develop code in Databricks notebooks (Magic Commands): https://docs.databricks.com/aws/en/notebooks/notebooks-code
- Databricks Utilities (`dbutils.fs`): https://docs.databricks.com/aws/en/dev-tools/databricks-utils

**Stand:** 2026-08-17, alle Angaben per `WebFetch` verifiziert; auffällige/spezifische Details (`-e`-Flag-Verhalten) zusätzlich mit einem zweiten, unabhängigen Abruf gegengeprüft.
