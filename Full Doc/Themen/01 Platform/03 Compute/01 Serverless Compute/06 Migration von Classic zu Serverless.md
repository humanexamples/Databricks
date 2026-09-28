# Migration von Classic Compute zu Serverless Compute

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/migration>

Serverless übernimmt Provisionierung, Skalierung, Runtime-Upgrades und Optimierung automatisch. Die meisten Classic-Workloads lassen sich mit **minimalen oder keinen** Code-Änderungen migrieren. Ausnahmen: `df.cache()` u. Ä. werden noch nicht unterstützt; Workloads, die **R- oder Scala-Notebooks** benötigen, können nicht migriert werden (erfordern Classic Compute).

## Migrationsschritte (6)

1. **Voraussetzungen prüfen** — Workspace, Networking, Cloud-Storage
2. **Code aktualisieren** — nötige Code-/Konfigurationsänderungen
3. **Workloads testen** — Kompatibilität und Korrektheit vor der Migration
4. **Performance-Modus wählen**
5. **Phasenweise migrieren** — inkrementell, beginnend mit Low-Risk-Workloads
6. **Kosten überwachen** — DBU-Verbrauch verfolgen, Alerts einrichten

## Bevor du beginnst

| Voraussetzung | Aktion |
|---|---|
| Workspace für Unity Catalog aktiviert | Ggf. von Hive Metastore migrieren; Workspace auf Unity Catalog upgraden |
| Networking konfiguriert | VPC-Peering durch NCCs, Private Link oder Firewall-Regeln ersetzen |
| Cloud-Storage-Zugriff | Legacy-Datenzugriffsmuster durch Unity-Catalog-External-Locations ersetzen; DBFS-Mounts mit Instance Profiles migrieren |

## Code aktualisieren

### Datenzugriff

| Classic-Muster | Serverless-Ersatz |
|---|---|
| DBFS-Pfade (`dbfs:/...`) | Unity-Catalog-Volumes |
| Hive-Metastore-Tabellen | Unity-Catalog-Tabellen (oder HMS Federation) |
| IAM Instance Profiles | Unity-Catalog-External-Locations |
| Custom JDBC-JARs | Lakehouse Federation |

```python
# Classic
df = spark.read.csv("dbfs:/mnt/datalake/data.csv", header=True)
df.write.parquet("dbfs:/mnt/output/results")
df = spark.table("my_database.my_table")

# Serverless
df = spark.read.csv("/Volumes/main/sales/raw_data/data.csv", header=True)
df.write.parquet("/Volumes/main/analytics/output/results")
df = spark.table("main.my_database.my_table")  # three-level namespace
```

> **Warnung:** *"DBFS access is limited on serverless. Update all `dbfs:/` paths to Unity Catalog volumes before migrating."*

### APIs und Code

| Classic-Muster | Serverless-Ersatz |
|---|---|
| RDD-APIs (`sc.parallelize`, `rdd.map`) | DataFrame-APIs |
| `df.cache()`, `df.persist()` | Caching-Aufrufe entfernen (noch nicht unterstützt) |
| `spark.sparkContext`, `sqlContext` | direkt `spark` (SparkSession) verwenden |
| Hive-Variablen (`${var}`) | SQL `DECLARE VARIABLE` oder Python-f-Strings |
| Nicht unterstützte Spark-Configs | entfernen; Serverless tunt automatisch |

```python
from pyspark.sql import functions as F

# Classic RDD parallelization → DataFrame creation
# Classic: rdd = sc.parallelize([1, 2, 3]); rdd.map(lambda x: x * 2).collect()
df = spark.createDataFrame([(1,), (2,), (3,)], ["value"])
result = df.select((F.col("value") * 2).alias("value")).collect()

# Classic flatMap → explode
# Classic: sc.parallelize(["hello world"]).flatMap(lambda l: l.split(" ")).collect()
df = spark.createDataFrame([("hello world",)], ["line"])
words = df.select(F.explode(F.split("line", " ")).alias("word")).collect()

# Classic groupByKey → DataFrame groupBy
# Classic: rdd.groupByKey().mapValues(list).collect()
df = spark.createDataFrame([("a", 1), ("b", 2), ("a", 3)], ["key", "value"])
grouped = df.groupBy("key").agg(F.collect_list("value").alias("values")).collect()

# mapPartitions → applyInPandas
import pandas as pd
def process_group(pdf: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({"total": [pdf["id"].sum()]})
result = (spark.range(100).repartition(4)
    .groupBy(F.spark_partition_id())
    .applyInPandas(process_group, schema="total long").collect())

# sc.textFile → spark.read.text
df = spark.read.text("/Volumes/catalog/schema/volume/file.txt")
```

```python
from pyspark.sql.functions import broadcast

# sc.broadcast → broadcast join
result = main_df.join(broadcast(lookup_df), "key")

# sc.accumulator → DataFrame aggregation
total = df.agg(F.sum("amount")).collect()[0][0]

# sqlContext.sql → spark.sql
result = spark.sql("SELECT * FROM main.db.table")

# df.cache() → remove caching calls
# Materialize expensive intermediate results to Delta as a workaround:
df = spark.read.parquet(path)
result = df.filter("status = 'active'")
expensive_df.write.format("delta").mode("overwrite").saveAsTable("main.scratch.temp")
result = spark.table("main.scratch.temp")
```

### Libraries und Environments

| Classic-Muster | Serverless-Ersatz |
|---|---|
| Init-Skripte | Serverless-Environments |
| Compute-scoped Libraries | Notebook-scoped oder Environment-Libraries |
| Maven/JAR-Libraries | JAR-Task-Support für Jobs; PyPI für Notebooks |
| Docker-Container | Serverless-Environments |

Python-Pakete in `requirements.txt` pinnen (reproduzierbare Umgebungen).

### Streaming

| Spark-Trigger | Unterstützt | Hinweise |
|---|---|---|
| `Trigger.AvailableNow()` | Ja | empfohlen |
| `Trigger.Once()` | Ja | deprecated; `AvailableNow()` verwenden |
| `Trigger.ProcessingTime(interval)` | Nein | `INFINITE_STREAMING_TRIGGER_NOT_SUPPORTED` |
| `Trigger.Continuous(interval)` | Nein | auf Lakeflow-Pipelines Continuous Mode migrieren |
| Default (kein `.trigger()`) | Nein | immer explizit `.trigger(availableNow=True)` setzen |

```python
# Classic (nicht unterstützt — Default-Trigger ist ProcessingTime)
query = df.writeStream.format("delta").outputMode("append").start()

# Serverless (expliziter AvailableNow-Trigger)
query = (df.writeStream.format("delta").outputMode("append")
    .trigger(availableNow=True)
    .option("checkpointLocation", checkpoint_path)
    .start(output_path))
query.awaitTermination()

# Mit OOM-Prävention für große Quellen
query = (spark.readStream.format("delta")
    .option("maxFilesPerTrigger", 100)
    .option("maxBytesPerTrigger", "10g")
    .load(input_path)
    .writeStream.format("delta")
    .trigger(availableNow=True)
    .option("checkpointLocation", checkpoint_path)
    .start(output_path))
```

## Workloads testen

1. **Schneller Kompatibilitätstest:** Workload auf Classic Compute mit **Standard Access Mode** und **Databricks Runtime 14.3+** ausführen. Erfolg → bereit für Serverless-Migration ohne Code-Änderungen.
2. **A/B-Vergleich** (empfohlen für Produktion): gleiche Workload auf Classic (Kontrolle) und Serverless (Experiment); Output-Tabellen diffen, iterieren bis identisch.
3. **Temporäre Configs:** unterstützte Spark-Configs während des Tests temporär setzen, nach Stabilisierung entfernen.

## Performance-Modus wählen

| Modus | Verfügbarkeit | Start | Am besten für |
|---|---|---|---|
| Standard | Jobs, Lakeflow Pipelines | 4–6 Minuten | kostensensitives Batch |
| Performance-optimized | Notebooks, Jobs, Lakeflow Pipelines | Sekunden | interaktiv, latenzsensitiv |

## Phasenweise migrieren

1. **Neue Workloads:** alle neuen Notebooks/Jobs auf Serverless starten
2. **Low-Risk-Workloads:** PySpark/SQL-Workloads bereits auf Standard Access Mode + Runtime 14.3+
3. **Komplexe Workloads:** solche mit Code-Änderungen (RDD-Rewrites, DBFS-Updates, Trigger-Fixes)
4. **Restliche Workloads:** periodisch neu bewerten, wenn Fähigkeiten wachsen

## Kosten überwachen

Serverless-Abrechnung basiert auf **DBU-Verbrauch**, nicht Cluster-Uptime. Kostenerwartungen mit repräsentativen Workloads validieren, bevor im großen Stil migriert wird.

## Verwandte Themen

- [05 Best Practices.md](05%20Best%20Practices.md) · [07 Streaming.md](07%20Streaming.md) · [09 Einschraenkungen.md](09%20Einschraenkungen.md) · [04 Umgebung und Abhaengigkeiten.md](04%20Umgebung%20und%20Abhaengigkeiten.md)
- Doku: *Spark Connect vs. classic Spark*, *Supported Spark configurations*, *Serverless network security*
