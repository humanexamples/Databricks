# Spark Tuning-Parameter

Vier grundlegende Tuning-Parameter (Prüfungsobjektiv): `spark.sql.shuffle.partitions`, `spark.default.parallelism`, `spark.executor.memory`/`spark.driver.memory`, `spark.sql.autoBroadcastJoinThreshold` — was sie steuern, ihr Standardwert, Lesen/Setzen, und wie man den Effekt einer Änderung nachmisst.

## 1. `spark.sql.shuffle.partitions`

- Steuert: Anzahl Partitionen nach einem Shuffle bei DataFrame-/SQL-Joins und -Aggregationen (`groupBy`, `join`, `distinct` …).
- **Standardwert: `200`** (verifiziert gegen `spark.apache.org/docs/latest/sql-performance-tuning.html`; identischer Wert `200` auch in der Databricks-AQE-Dokumentation `docs.databricks.com` bestätigt — Databricks überschreibt den Zahlenwert nicht).
- **Gotcha:** Adaptive Query Execution (`spark.sql.adaptive.coalescePartitions.enabled`, auf Databricks standardmäßig aktiv) fasst nach dem Shuffle automatisch kleine Partitionen zusammen — die tatsächlich beobachtete Partitionsanzahl nach einer Aktion kann daher unter 200 liegen, auch wenn der Parameter selbst 200 bleibt. Alternativ: Wert `auto` setzen, dann bestimmt Databricks die Zahl datengetrieben.

```python
# Lesen
spark.conf.get("spark.sql.shuffle.partitions")
# Ergebnis: '200'

# Setzen
spark.conf.set("spark.sql.shuffle.partitions", 8)
```

**Vorher/Nachher am Beispiel eines Shuffles:**

```python
df = spark.range(1000000).withColumnRenamed("id", "key")

spark.conf.set("spark.sql.shuffle.partitions", 200)
result_200 = df.groupBy("key").count()
print(result_200.rdd.getNumPartitions())
# Ergebnis: 200

spark.conf.set("spark.sql.shuffle.partitions", 8)
result_8 = df.groupBy("key").count()
print(result_8.rdd.getNumPartitions())
# Ergebnis: 8
```

**Performance nachmessen (Wall-Clock-Vergleich bei kleinem Datensatz — zu viele Partitionen erzeugen Overhead):**

```python
import time

for n in (200, 8):
    spark.conf.set("spark.sql.shuffle.partitions", n)
    t0 = time.time()
    df.groupBy("key").count().count()
    print(n, "Partitionen:", round(time.time() - t0, 2), "s")
# Ergebnis (Beispiel, kleiner Datensatz, lokal):
# 200 Partitionen: 1.84 s
# 8 Partitionen:   0.41 s
```

- Alternative Messmethode: Anzahl der Tasks der Shuffle-Stage in der Spark UI (**Stages**-Tab) vergleichen — entspricht direkt dem gesetzten Wert.

## 2. `spark.default.parallelism`

- Steuert: Standard-Partitionsanzahl für **RDD**-Operationen ohne expliziten Partitionswert (`sc.parallelize`, RDD-`join`/`reduceByKey`) — **nicht** für DataFrame-/SQL-Shuffles (dort gilt `spark.sql.shuffle.partitions`).
- **Standardwert (kein fester Zahlenwert, hängt vom Cluster-Manager ab — verifiziert gegen `spark.apache.org/docs/latest/configuration.html`):**
  - Für Shuffle-Operationen (`reduceByKey`, `join`): größte Partitionsanzahl der Eltern-RDD.
  - Für `parallelize` ohne Eltern-RDD — **Local Mode:** Anzahl Kerne der lokalen Maschine. **Standalone/YARN/Mesos/Kubernetes:** Gesamtzahl der Executor-Kerne im Cluster, mindestens 2.
- Auf Databricks konkret: `sc.defaultParallelism` richtet sich nach der Anzahl der Worker-Kerne des laufenden Clusters — kein fixer Databricks-eigener Standardwert dokumentiert, folgt der OSS-Regel für Standalone/YARN-artige Cluster.

```python
# Lesen
sc.defaultParallelism
# Ergebnis (Beispiel, 4 Worker-Kerne): 4

spark.conf.get("spark.default.parallelism")
# wirft Fehler, falls nicht explizit gesetzt — kein SQL-Conf-Wert, sondern SparkContext-Property

# Setzen (nur beim Erstellen des SparkContext möglich, nicht zur Laufzeit über spark.conf.set)
# im spark-submit / Cluster-Konfiguration:
# --conf spark.default.parallelism=16
```

**Vorher/Nachher am Beispiel eines RDD ohne expliziten Partitionswert:**

```python
rdd_default = sc.parallelize(range(1000))
print(rdd_default.getNumPartitions())
# Ergebnis: entspricht sc.defaultParallelism, z. B. 4

rdd_explicit = sc.parallelize(range(1000), 16)
print(rdd_explicit.getNumPartitions())
# Ergebnis: 16
```

- Nachmessen: `getNumPartitions()` direkt nach der Erzeugung vergleichen (wie oben) — bei RDD-Jobs zusätzlich Task-Anzahl der Stage in der Spark UI prüfen.

## 3. `spark.executor.memory` / `spark.driver.memory`

- Steuern: JVM-Heap-Speicher pro Executor-Prozess bzw. für den Driver-Prozess.
- **Standardwert: `1g` / `1g`** (verifiziert gegen `spark.apache.org/docs/latest/configuration.html` — reiner OSS-Spark-Standard).
- **Auf Databricks in der Praxis abweichend:** Databricks-Dokumentation (`docs.databricks.com/en/compute/cluster-config-best-practices.html`) rät ausdrücklich davon ab, `spark.executor.memory`/`spark.driver.memory` hart zu kodieren — der tatsächliche Wert wird automatisch aus dem gewählten Node-/Instance-Typ des Clusters abgeleitet. Ein pauschaler Databricks-Standardwert lässt sich daher nicht seriös angeben (hängt vom Instance-Typ ab).

```python
# Lesen
spark.conf.get("spark.executor.memory")
# Ergebnis (Beispiel OSS-Standard, falls nicht clusterseitig überschrieben): '1g'

spark.conf.get("spark.driver.memory")
# Ergebnis: '1g'

# Setzen — NICHT zur Laufzeit über spark.conf.set() möglich (JVM bereits gestartet)!
# Muss vor Cluster-/Session-Start erfolgen, z. B.:
# --conf spark.executor.memory=4g --conf spark.driver.memory=4g
```

**Effekt beobachten (Spill statt Absturz bei zu wenig Executor-Speicher):**

```python
# Cluster mit knapp bemessenem spark.executor.memory, große In-Memory-Aggregation
big_df = spark.range(50_000_000).selectExpr("id", "id % 1000 as key")
big_df.groupBy("key").count().collect()
```

- Nachmessen: Spark UI → **Stages** → Spalte **Spill (Memory)/(Disk)** je Task — sinkt bzw. verschwindet nach Erhöhung von `spark.executor.memory`, gleichzeitig sinkt die Stage-Laufzeit. Executor-Speicherbelegung zusätzlich im **Executors**-Tab (Spalte **Storage Memory**) prüfbar.

## 4. `spark.sql.autoBroadcastJoinThreshold`

- Steuert: maximale Größe (in Bytes) einer Tabelle, ab der der Query-Planer sie automatisch per Broadcast Join statt Sort-Merge-Join verteilt.
- **Standardwert: `10485760` (= 10 MB)** — verifiziert gegen `spark.apache.org/docs/latest/sql-performance-tuning.html`, gegengeprüft mit unabhängiger Spark-Versionsdokumentation (2.4.x/4.x konsistent). **`-1` deaktiviert automatische Broadcast Joins vollständig.**
- **Nicht verwechseln:** Databricks kennt zusätzlich den separaten AQE-Parameter `spark.databricks.adaptive.autoBroadcastJoinThreshold` (Standardwert laut Databricks-Dokumentation `docs.databricks.com/aws/en/optimizations/aqe`: **30 MB**) — steuert die *laufzeitdynamische* Umwandlung eines Sort-Merge-Joins in einen Broadcast-Join durch AQE, ist aber ein anderer Parameter als der hier geprüfte, planungszeitige `spark.sql.autoBroadcastJoinThreshold`.

```python
# Lesen
spark.conf.get("spark.sql.autoBroadcastJoinThreshold")
# Ergebnis: '10485760'

# Setzen (Bytes)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 10 * 1024 * 1024)

# Deaktivieren
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
```

**Vorher/Nachher: Join-Strategie im Query-Plan (`.explain()`):**

```python
small = spark.range(1000).withColumnRenamed("id", "key")   # deutlich < 10 MB
large = spark.range(10_000_000).withColumnRenamed("id", "key")

spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 10 * 1024 * 1024)
large.join(small, "key").explain()
# Ergebnis: Plan enthält "BroadcastHashJoin" / "BroadcastExchange"

spark.conf.set("spark.sql.autoBroadcastJoinThreshold", -1)
large.join(small, "key").explain()
# Ergebnis: Plan enthält stattdessen "SortMergeJoin" (Broadcast deaktiviert)
```

- Nachmessen: neben dem Plan-Wechsel in `.explain()` zusätzlich Laufzeit vergleichen (`%timeit`-Stil) — Broadcast Join spart bei kleiner Seite typischerweise den Shuffle der großen Tabelle und ist messbar schneller; in der Spark UI zeigt sich das als fehlende Shuffle-Read/-Write-Stage für den Join.

---

**Stand:** 2026-09-15.
