# Databricks Utils (`dbutils`) — Überblick

Databricks Utilities (`dbutils`) sind in Notebooks und Jobs vorinstallierte Hilfsfunktionen für Dateisystemzugriff, Secrets, Widgets, Notebook-Verkettung, Job-Task-Kommunikation und weitere Aufgaben.

## Sub-Utilities in diesem Kapitel

1. **Credentials** (`dbutils.credentials`) — IAM-Rollen für S3-Zugriff wechseln, nur mit Credential Passthrough. Siehe [01 Credentials Utility (dbutils.credentials).md](01%20Credentials%20Utility%20%28dbutils.credentials%29.md).
2. **Data** (`dbutils.data`) — Zusammenfassungsstatistiken für DataFrames (`summarize`), Public Preview. Siehe [02 Data Utility (dbutils.data).md](02%20Data%20Utility%20%28dbutils.data%29.md).
3. **File System** (`dbutils.fs`) — DBFS-Dateioperationen (`ls`, `cp`, `mv`, `rm`, `mount` u. a.). Siehe [03 File System Utility (dbutils.fs).md](03%20File%20System%20Utility%20%28dbutils.fs%29.md).
4. **Jobs** (`dbutils.jobs`) — `taskValues` zum Austausch von Werten zwischen Job-Tasks, nur Python. Siehe [04 Jobs Utility (dbutils.jobs).md](04%20Jobs%20Utility%20%28dbutils.jobs%29.md).
5. **Library** (`dbutils.library`) — größtenteils deprecated, `restartPython` als einziger aktiver Befehl. Siehe [05 Library Utility (dbutils.library).md](05%20Library%20Utility%20%28dbutils.library%29.md).
6. **Notebook** (`dbutils.notebook`) — Notebooks verketten und beenden (`run`, `exit`). Siehe [06 Notebook Utility (dbutils.notebook).md](06%20Notebook%20Utility%20%28dbutils.notebook%29.md).
7. **Secrets** (`dbutils.secrets`) — sichere Credential-Ablage und -Abruf. Siehe [07 Secrets Utility (dbutils.secrets).md](07%20Secrets%20Utility%20%28dbutils.secrets%29.md).
8. **Widgets** (`dbutils.widgets`) — Notebook-Parametrisierung über Eingabeelemente. Siehe [08 Widgets Utility (dbutils.widgets).md](08%20Widgets%20Utility%20%28dbutils.widgets%29.md).

## Nicht in diesem Kapitel behandelt

Die offizielle Referenzseite listet zusätzlich `meta` (Compiler-Hooks, experimentell), `preview` (Utilities in Preview) und `api` (Application Builds) — diese wurden nicht angefragt und sind hier nicht dokumentiert.

## Verwandte Kapitel

- [DBFS](../../04%20Data%20guides/02%20Work%20with%20files/04%20DBFS/) — vertiefte `dbutils.fs`-Befehlsreferenz und Mount-Details.
- [Lakeflow Jobs — Parameter](../../07%20Data%20Management/01%20Data%20Engineering/04%20Lakeflow%20Jobs/07%20Parameter/) — praktische Nutzung von Task Values und Widgets in Jobs.
- [Databricks Asset Bundles](../03%20Databricks%20Asset%20Bundles/) — Bibliotheksverwaltung als moderne Alternative zu `dbutils.library`.
- [Databricks SDK für Python](../07%20Databricks%20SDK%20fuer%20Python.md), Abschnitt 5 — `dbutils` programmatisch über `WorkspaceClient().dbutils` bzw. `databricks.sdk.runtime` nutzen.

### Quelle

- https://docs.databricks.com/aws/en/dev-tools/databricks-utils

**Stand:** 2026-08-26.
