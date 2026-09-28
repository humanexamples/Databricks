[← Übersicht](00%20Uebersicht.md)

# Timestamp-basiertes CDC mit Lakeflow Jobs

**Kombination:** Timestamp-CDC (High Watermark) · Control-Tabelle · Lakehouse Federation · `MERGE` · Lakeflow Jobs (Task Values, For-Each-Task, Schedule) · Databricks Asset Bundle

Viele Quellsysteme haben **kein** Transaktionslog, auf das man zugreifen kann, aber eine Spalte `last_modified`. Dann lädt man pro Lauf nur die Zeilen, die seit dem letzten Lauf geändert wurden. Der „letzte Lauf“ wird als **Watermark** in einer Control-Tabelle gespeichert.

```
Job (stündlich)
 ├─ get_tables        liest die Control-Tabelle → Task Value "tables"
 └─ copy_tables       For-Each über "tables" (4 parallel)
      └─ copy_one_table(table_name)
            1. Watermark lesen
            2. Änderungen > Watermark aus der Quelle holen
            3. MERGE ins Ziel
            4. Watermark hochsetzen
```

---

## 1. Control-Tabelle

```sql
CREATE TABLE IF NOT EXISTS catalog.ops.cdc_watermarks (
  table_name     STRING,
  key_column     STRING,
  last_watermark TIMESTAMP
);

INSERT INTO catalog.ops.cdc_watermarks VALUES
  ('customers', 'customer_id', TIMESTAMP'1900-01-01 00:00:00'),
  ('orders',    'order_id',    TIMESTAMP'1900-01-01 00:00:00'),
  ('products',  'product_id',  TIMESTAMP'1900-01-01 00:00:00');
```

Eine neue Tabelle aufnehmen = eine Zeile einfügen. Der Job muss dafür nicht geändert werden.

## 2. Task `get_tables` – Tabellenliste als Task Value

```python
tables = [r.table_name for r in spark.table("catalog.ops.cdc_watermarks").collect()]
dbutils.jobs.taskValues.set(key="tables", value=tables)
```

## 3. Task `copy_one_table` – eine Tabelle inkrementell kopieren

```python
from delta.tables import DeltaTable
from pyspark.sql import functions as F

table = dbutils.widgets.get("table_name")        # kommt aus dem For-Each-Task

cfg     = spark.table("catalog.ops.cdc_watermarks").filter(F.col("table_name") == table).first()
key     = cfg["key_column"]
last_wm = cfg["last_watermark"]

# Quelle: Foreign Catalog über Lakehouse Federation (z. B. PostgreSQL)
source = spark.table(f"erp_postgres.public.{table}")

# Obergrenze ZUERST festlegen, damit Watermark und geladene Daten zusammenpassen
new_wm = (source.filter(F.col("last_modified") > F.lit(last_wm))
                .agg(F.max("last_modified")).first()[0])

if new_wm is None:
    dbutils.notebook.exit(f"{table}: keine Änderungen")

changes = source.filter((F.col("last_modified") > F.lit(last_wm)) &
                        (F.col("last_modified") <= F.lit(new_wm)))

# Soft Deletes der Quelle (Flag-Spalte) werden zu echten Deletes im Ziel
(DeltaTable.forName(spark, f"catalog.silver.{table}").alias("t")
    .merge(changes.alias("s"), f"t.{key} = s.{key}")
    .whenMatchedDelete(condition="s.is_deleted = true")
    .whenMatchedUpdateAll()
    .whenNotMatchedInsertAll(condition="s.is_deleted = false")
    .execute())

# Watermark erst NACH erfolgreichem MERGE hochsetzen
spark.sql(
    "UPDATE catalog.ops.cdc_watermarks SET last_watermark = :wm WHERE table_name = :tbl",
    args={"wm": new_wm, "tbl": table})
```

**Warum die Reihenfolge wichtig ist:** Schlägt das `MERGE` fehl, bleibt die alte Watermark stehen, und der nächste Lauf lädt dieselben Änderungen erneut. Da `MERGE` idempotent ist, entsteht dadurch kein Duplikat.

## 4. Job als Databricks Asset Bundle

```yaml
# resources/cdc_incremental_copy.job.yml
resources:
  jobs:
    cdc_incremental_copy:
      name: cdc_incremental_copy
      schedule:
        quartz_cron_expression: "0 0 * * * ?"     # stündlich
        timezone_id: Europe/Berlin
      tasks:
        - task_key: get_tables
          notebook_task:
            notebook_path: ../src/get_tables.ipynb

        - task_key: copy_tables
          depends_on:
            - task_key: get_tables
          for_each_task:
            inputs: "{{tasks.get_tables.values.tables}}"
            concurrency: 4
            task:
              task_key: copy_one_table
              notebook_task:
                notebook_path: ../src/cdc_copy_table.ipynb
                base_parameters:
                  table_name: "{{input}}"
```

Ohne Compute-Angabe laufen die Notebook-Tasks auf **Serverless Jobs Compute** (sofern im Workspace aktiviert). Deployment: `databricks bundle deploy -t dev`.

---

## Grenzen von Timestamp-basiertem CDC

| Problem | Folge | Abhilfe |
|---|---|---|
| **Hard Deletes** in der Quelle | werden nie erkannt, weil die Zeile einfach fehlt | Soft-Delete-Flag in der Quelle · periodischer Snapshot-Vergleich (`MERGE … WHEN NOT MATCHED BY SOURCE THEN DELETE`) · log-basiertes CDC |
| Zwischenstände | Wird eine Zeile zwischen zwei Läufen dreimal geändert, sieht man nur den letzten Stand | Für lückenlose Historie log-basiertes CDC verwenden |
| `last_modified` wird nicht zuverlässig gepflegt | Änderungen gehen verloren | Trigger in der Quell-DB oder anderes Verfahren |
| Uhrzeit-Versatz / lange Transaktionen | Zeilen mit `last_modified` knapp unter der Watermark werden erst nach ihr committed | kleines Überlappungsfenster (z. B. `last_wm - INTERVAL 5 MINUTES`), Dubletten fängt das `MERGE` ab |

> Für SCD 2 aus Timestamp-CDC: Das `MERGE` hier durch das SCD-2-Muster aus [../SCD/03](../SCD/03%20SCD%20Type%202%20manuell%20mit%20MERGE.md) ersetzen.

---
[← Vorherige Datei](04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md) · [Übersicht](00%20Uebersicht.md) · [Nächste Datei →](06%20CDC%20ohne%20SCD.md)

## Quellen

- [Use a For each task to run another task in a loop](https://docs.databricks.com/aws/en/jobs/for-each)
- [Use task values to pass information between tasks](https://docs.databricks.com/aws/en/jobs/task-values)
- [What is Lakehouse Federation?](https://docs.databricks.com/aws/en/query-federation/)
- [Upsert into a Delta Lake table using merge](https://docs.databricks.com/aws/en/delta/merge)
