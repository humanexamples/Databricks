# Task Values: Informationen zwischen Tasks weitergeben

Task Values nutzen die Databricks-Utilities-Subutility `taskValues`, um beliebige Werte zwischen Tasks eines Jobs zu übergeben. Ein Key-Value-Paar wird mit `dbutils.jobs.taskValues.set()` in einem Task gesetzt und in nachgelagerten Tasks über Task-Namen und Key referenziert.

**Hinweis:** `dbutils.jobs.taskValues.set()`/`.get()` sind Python-Funktionen und funktionieren nur in Python-Notebooks. Über dynamische Wertreferenzen lassen sich Task Values jedoch in allen parameterfähigen Tasks referenzieren.

## Task Values setzen

Schlüssel müssen Strings und (bei mehreren Werten) eindeutig sein. Nur JSON-valide Werte, maximal **48 KiB**.

**Statischer String:**

```python
dbutils.jobs.taskValues.set(key = "fave_food", value = "beans")
```

**Query-Ergebnisse:**

```python
from pyspark.sql.functions import col
order_num = dbutils.widgets.get("order_num")
query = (spark.read.table("orders")
  .orderBy(col("updated"), ascending=False)
  .select(col("order_status"))
  .where(col("order_num") == order_num))
dbutils.jobs.taskValues.set(key = "record_count", value = query.count())
dbutils.jobs.taskValues.set(key = "order_status", value = query.take(1)[0][0])
```

**Listen:**

```python
prod_list = list(spark.read.table("products").select("prod_id").distinct().toPandas()["prod_id"])
dbutils.jobs.taskValues.set(key = "prod_list", value = prod_list)
```

## Task Values referenzieren

Empfohlen: dynamische Wertreferenz `{{tasks.<task_name>.values.<value_name>}}` — z. B. für `prod_list` aus Task `product_inventory`: `{{tasks.product_inventory.values.prod_list}}`.

**Alternative — `dbutils.jobs.taskValues.get()`:**

```python
order_status = dbutils.jobs.taskValues.get(taskKey = "order_lookup", key = "order_status", debugValue = "Delivered")
```

Benötigt den Namen des vorgelagerten Tasks, optional einen `debugValue` für interaktives Testen.

## Ansehen

Task-Value-Ausgaben erscheinen im **Output**-Panel der Task-Run-Details.

## Quelle

- https://docs.databricks.com/aws/en/jobs/task-values
