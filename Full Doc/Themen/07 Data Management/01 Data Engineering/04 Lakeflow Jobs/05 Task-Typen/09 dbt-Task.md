# dbt-Task

Konfiguriert und führt dbt-Projekte auf Databricks aus. Beim Lauf injiziert Databricks das `DBT_ACCESS_TOKEN` für den im **Run As**-Feld konfigurierten Principal.

## Voraussetzungen

Der **Run As**-Principal benötigt:

- `CAN USE` auf dem SQL-Warehouse, das den von dbt generierten SQL-Code ausführt.
- die von den dbt-Modellen benötigten Unity-Catalog-Privilegien (z. B. `USE CATALOG`/`USE SCHEMA` auf Ziel-Catalog/-Schema, `SELECT`/`MODIFY` auf gelesenen/geschriebenen Objekten).

## Konfiguration

1. Tab **Tasks** → **Add task**.
2. Task-Namen eingeben, Typ **dbt**.
3. **Source**: **Workspace** (dbt-Projekt in Workspace-Ordnern) oder **Git provider** (Remote-Repository).
4. **Project directory** über den Dateibrowser wählen bzw. Git-Informationen eingeben.
5. **dbt commands** — Standard: `dbt deps`, `dbt seed`, `dbt run` (sequenziell, anpassbar).
6. **SQL warehouse** wählen (nur Serverless/Pro).
7. **Warehouse catalog** (Standard: Workspace-Default) und **Warehouse schema** (Standard: `default`) angeben.
8. **dbt CLI compute** wählen, auf dem dbt Core läuft (Serverless oder Classic Jobs Compute mit Single-Node-Cluster empfohlen).
9. `dbt-databricks`-Version festlegen: bei Serverless über **Environment and Libraries**; sonst über **Dependent libraries** (Standard `dbt-databricks>=1.0.0,<2.0.0`) — Version zum Pinnen löschen und neu setzen.
10. Optional Retries, Laufdauer-/Streaming-Backlog-Schwellen oder Benachrichtigungen.
11. **Save task**.

**Empfehlung:** dbt-Tasks auf eine feste `dbt-databricks`-Version pinnen, damit Entwicklung und Produktion dieselbe Version nutzen.

## dbt-Kommandos

Das Feld **dbt commands** akzeptiert dbt-CLI-Befehle.

### Optionen übergeben

Die dbt-Node-Selection-Syntax erlaubt `--select`/`--exclude` bei `run`/`build`, plus weitere Konfigurations-Flags.

### Variablen übergeben

Über `--vars`, als einfach-quotiertes JSON mit doppelt-quotierten Keys/Values:

```
dbt run --vars '{"volume_path": "/Volumes/path/to/data", "date": "2024/08/16"}'
```

### Parametrisierte Beispiele

| Parametername | Wert |
|---|---|
| `volume_path` | `/Volumes/path/to/data` |
| `table_name` | `my_table` |
| `select_clause` | `--select "tag:nightly"` |
| `dbt_refresh` | `--full-refresh` |

```
dbt run '{"volume_path": "{{job.parameters.volume_path}}"}'
dbt run --select "{{job.parameters.table_name}}"
dbt run {{job.parameters.select_clause}}
dbt run {{job.parameters.dbt_refresh}}
dbt run '{"volume_path": "{{job.parameters.volume_path}}"}' {{job.parameters.dbt_refresh}}
```

Dynamische Parameter/Task Values:

```
dbt run --vars '{"date": "{{job.start_time.iso_date}}"}'
dbt run --vars '{"sales_count": "{{tasks.sales_task.values.sales_count}}"}'
```

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/dbt
