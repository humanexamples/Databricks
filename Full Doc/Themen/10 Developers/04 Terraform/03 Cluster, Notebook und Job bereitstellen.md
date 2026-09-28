# Cluster, Notebook und Job bereitstellen

Vollständiges End-to-End-Beispiel: Cluster (Unity-Catalog-kompatibel und All-Purpose), Notebook und Job in einem bestehenden Workspace über den Databricks-Terraform-Provider bereitstellen — inkl. dreier vollständiger Beispiel-Notebooks. Teil der [Terraform](Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Cluster-Konfiguration](#cluster)
2. [Notebook-Konfiguration](#notebook)
3. [Beispiel-Notebooks](#notebook-beispiele)
4. [Job-Konfiguration](#job)
5. [Konfigurationen ausführen](#ausfuehren)
6. [Ergebnisse erkunden](#ergebnisse)
7. [Aufräumen](#aufraeumen)

---

## <a id="cluster">1. Cluster-Konfiguration</a>

**`cluster.tf`, Unity-Catalog-kompatibel:**

```hcl
variable "cluster_name" {}
variable "cluster_autotermination_minutes" {}
variable "cluster_num_workers" {}
variable "cluster_data_security_mode" {}

data "databricks_node_type" "smallest" {
  local_disk = true
}

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

resource "databricks_cluster" "this" {
  cluster_name            = var.cluster_name
  node_type_id            = data.databricks_node_type.smallest.id
  spark_version           = data.databricks_spark_version.latest_lts.id
  autotermination_minutes = var.cluster_autotermination_minutes
  num_workers             = var.cluster_num_workers
  data_security_mode      = var.cluster_data_security_mode
}

output "cluster_url" {
  value = databricks_cluster.this.url
}
```

**`cluster.auto.tfvars`, Unity-Catalog-kompatibel:**

```hcl
cluster_name                    = "My Cluster"
cluster_autotermination_minutes = 60
cluster_num_workers             = 1
cluster_data_security_mode      = "SINGLE_USER"
```

**All-Purpose-Cluster** (ohne `data_security_mode`-Variable):

```hcl
variable "cluster_name" {
  description = "A name for the cluster."
  type        = string
  default     = "My Cluster"
}

variable "cluster_autotermination_minutes" {
  description = "Minutes before automatic termination due to inactivity."
  type        = number
  default     = 60
}

variable "cluster_num_workers" {
  description = "The number of workers."
  type        = number
  default     = 1
}

data "databricks_node_type" "smallest" {
  local_disk = true
}

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
}

resource "databricks_cluster" "this" {
  cluster_name            = var.cluster_name
  node_type_id            = data.databricks_node_type.smallest.id
  spark_version           = data.databricks_spark_version.latest_lts.id
  autotermination_minutes = var.cluster_autotermination_minutes
  num_workers             = var.cluster_num_workers
}

output "cluster_url" {
  value = databricks_cluster.this.url
}
```

**`cluster.auto.tfvars`, All-Purpose:**

```hcl
cluster_name                    = "My Cluster"
cluster_autotermination_minutes = 60
cluster_num_workers             = 1
```

## <a id="notebook">2. Notebook-Konfiguration</a>

**`notebook.tf`:**

```hcl
variable "notebook_subdirectory" {
  description = "Subdirectory name for storing the notebook."
  type        = string
  default     = "Terraform"
}

variable "notebook_filename" {
  description = "The notebook's filename."
  type        = string
}

variable "notebook_language" {
  description = "The language of the notebook."
  type        = string
}

resource "databricks_notebook" "this" {
  path     = "${data.databricks_current_user.me.home}/${var.notebook_subdirectory}/${var.notebook_filename}"
  language = var.notebook_language
  source   = "./${var.notebook_filename}"
}

output "notebook_url" {
  value = databricks_notebook.this.url
}
```

## <a id="notebook-beispiele">3. Beispiel-Notebooks</a>

### Python ETL Quick Start (`notebook-getting-started-etl-quick-start.py`)

```python
# Databricks notebook source
from pyspark.sql.functions import col, current_timestamp

file_path = "/databricks-datasets/structured-streaming/events"
username = spark.sql("SELECT regexp_replace(session_user(), '[^a-zA-Z0-9]', '_')").first()[0]
table_name = f"{username}_etl_quickstart"
checkpoint_path = f"/tmp/{username}/_checkpoint/etl_quickstart"

spark.sql(f"DROP TABLE IF EXISTS {table_name}")
dbutils.fs.rm(checkpoint_path, True)

(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", checkpoint_path)
  .load(file_path)
  .select("*", col("_metadata.file_path").alias("source_file"), current_timestamp().alias("processing_time"))
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .trigger(availableNow=True)
  .toTable(table_name))

# COMMAND ----------
df = spark.read.table(table_name)

# COMMAND ----------
display(df)
```

`notebook.auto.tfvars`: `notebook_subdirectory = "Terraform"`, `notebook_filename = "notebook-getting-started-etl-quick-start.py"`, `notebook_language = "PYTHON"`.

### SQL Quick Start (`notebook-getting-started-quickstart.sql`)

```sql
-- Databricks notebook source
-- MAGIC %python
-- MAGIC diamonds = (spark.read
-- MAGIC   .format("csv")
-- MAGIC   .option("header", "true")
-- MAGIC   .option("inferSchema", "true")
-- MAGIC   .load("/databricks-datasets/Rdatasets/data-001/csv/ggplot2/diamonds.csv")
-- MAGIC )
-- MAGIC
-- MAGIC diamonds.write.format("delta").save("/mnt/delta/diamonds")

-- COMMAND ----------
DROP TABLE IF EXISTS diamonds;
CREATE TABLE diamonds USING DELTA LOCATION '/mnt/delta/diamonds/'

-- COMMAND ----------
SELECT color, avg(price) AS price FROM diamonds GROUP BY color ORDER BY COLOR
```

`notebook.auto.tfvars`: `notebook_filename = "notebook-getting-started-quickstart.sql"`, `notebook_language = "SQL"`.

### Python Lakehouse E2E (`notebook-getting-started-lakehouse-e2e.py`)

```python
# Databricks notebook source
external_location = "<your_external_location>"
catalog = "<your_catalog>"

dbutils.fs.put(f"{external_location}/foobar.txt", "Hello world!", True)
display(dbutils.fs.head(f"{external_location}/foobar.txt"))
dbutils.fs.rm(f"{external_location}/foobar.txt")
display(spark.sql(f"SHOW SCHEMAS IN {catalog}"))

# COMMAND ----------
from pyspark.sql.functions import col

username = spark.sql("SELECT regexp_replace(session_user(), '[^a-zA-Z0-9]', '_')").first()[0]
database = f"{catalog}.e2e_lakehouse_{username}_db"
source = f"{external_location}/e2e-lakehouse-source"
table = f"{database}.target_table"
checkpoint_path = f"{external_location}/_checkpoint/e2e-lakehouse-demo"

spark.sql(f"SET c.username='{username}'")
spark.sql(f"SET c.database={database}")
spark.sql(f"SET c.source='{source}'")
spark.sql("DROP DATABASE IF EXISTS ${c.database} CASCADE")
spark.sql("CREATE DATABASE ${c.database}")
spark.sql("USE ${c.database}")

dbutils.fs.rm(source, True)
dbutils.fs.rm(checkpoint_path, True)

class LoadData:
  def __init__(self, source):
    self.source = source

  def get_date(self):
    try:
      df = spark.read.format("json").load(source)
    except:
        return "2016-01-01"
    batch_date = df.selectExpr("max(distinct(date(tpep_pickup_datetime))) + 1 day").first()[0]
    if batch_date.month == 3:
      raise Exception("Source data exhausted")
    return batch_date

  def get_batch(self, batch_date):
    return (
      spark.table("samples.nyctaxi.trips")
        .filter(col("tpep_pickup_datetime").cast("date") == batch_date)
    )

  def write_batch(self, batch):
    batch.write.format("json").mode("append").save(self.source)

  def land_batch(self):
    batch_date = self.get_date()
    batch = self.get_batch(batch_date)
    self.write_batch(batch)

RawData = LoadData(source)

# COMMAND ----------
RawData.land_batch()

# COMMAND ----------
from pyspark.sql.functions import col, current_timestamp

(spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaLocation", checkpoint_path)
  .load(source)
  .select("*", col("_metadata.file_path").alias("source_file"), current_timestamp().alias("processing_time"))
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .trigger(availableNow=True)
  .option("mergeSchema", "true")
  .toTable(table))

# COMMAND ----------
df = spark.read.table(table)

# COMMAND ----------
display(df)
```

`notebook.auto.tfvars`: `notebook_filename = "notebook-getting-started-lakehouse-e2e.py"`, `notebook_language = "PYTHON"`.

## <a id="job">4. Job-Konfiguration</a>

**`job.tf`:**

```hcl
variable "job_name" {
  description = "A name for the job."
  type        = string
  default     = "My Job"
}

variable "task_key" {
  description = "A name for the task."
  type        = string
  default     = "my_task"
}

resource "databricks_job" "this" {
  name = var.job_name
  task {
    task_key = var.task_key
    existing_cluster_id = databricks_cluster.this.cluster_id
    notebook_task {
      notebook_path = databricks_notebook.this.path
    }
  }
  email_notifications {
    on_success = [ data.databricks_current_user.me.user_name ]
    on_failure = [ data.databricks_current_user.me.user_name ]
  }
}

output "job_url" {
  value = databricks_job.this.url
}
```

**`job.auto.tfvars`:**

```hcl
job_name = "My Job"
task_key = "my_task"
```

## <a id="ausfuehren">5. Konfigurationen ausführen</a>

```bash
terraform validate
terraform plan
terraform apply
```

Bei der Bestätigungsabfrage `yes` eingeben. Das Deployment, insbesondere die Cluster-Provisionierung, kann mehrere Minuten dauern.

## <a id="ergebnisse">6. Ergebnisse erkunden</a>

1. **Cluster:** `cluster_url` aus der `terraform apply`-Ausgabe im Browser öffnen.
2. **Notebook:** `notebook_url` öffnen — ggf. ist vor der Nutzung eine Anpassung nötig.
3. **Job:** `job_url` öffnen.
4. **Job ausführen:** **Run now** auf der Job-Seite klicken; nach Abschluss den neuesten Eintrag in **Completed runs (past 60 days)** über die **Start time**-Spalte öffnen; das **Output**-Panel zeigt die Notebook-Ausführungsergebnisse.

## <a id="aufraeumen">7. Aufräumen</a>

```bash
terraform plan
terraform destroy
```

Bei der Löschbestätigung `yes` eingeben — Terraform entfernt alle angegebenen Ressourcen aus dem Workspace.
