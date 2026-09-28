# Spark UI — Prüfungsfragen und Spickzettel

## 1. Spickzettel: Woran erkenne ich …?

| Problem | Wo? | Signal | Lösung |
|---|---|---|---|
| **Skew** | Stage-Detailseite → **Summary Metrics** → Duration | **Max > 1,5 × 75. Perzentil** | AQE Skew Join, Liquid Clustering, Salting |
| **Spill** | Stage-Detailseite (oben + Summary Metrics) | Spalten **Spill (Memory)/(Disk)** vorhanden | mehr Shuffle-Partitionen (`auto`), mehr RAM/Core |
| **I/O-gebunden** | Stage-Spalten Input/Output/Shuffle | größte Spalte ÷ Worker-Cores ÷ Sekunden **≈ 3 MB/s** | Delta, Liquid Clustering, Photon, Disk Cache, DFP, größerer Cluster |
| **Kleine Dateien lesen** | SQL-DAG → Scan → *number of files read* | **zehntausende** Dateien, Dateien **< 8 MB** | `OPTIMIZE`, Predictive Optimization, weniger Partitionen |
| **Kleine Dateien schreiben** | SQL-DAG → Write-Knoten | viele Dateien, wenig Daten | Optimized Writes, Predictive Optimization |
| **Daten-Rewrite** | SQL-DAG → Writer bzw. Merge-Knoten | viel mehr geschrieben als erwartet | MERGE optimieren, Deletion Vectors |
| **Langsame UDF** | SQL-DAG | `BatchEvalPython`/`ArrowEvalPython`, wenige Tasks | native Funktionen; sonst `repartition(num_cores)` |
| **Exploding Join** | SQL-DAG | wenige Zeilen rein, Größenordnungen mehr raus | Duplikate/Join-Reihenfolge prüfen |
| **Cartesian Join** | SQL-DAG | `CartesianProduct` / Nested Loop Join | Join-Bedingung prüfen |
| **Nur ein Task** | Stage-Liste → Tasks | `1/1` | Gzip, `multiLine`, Schema-Inferenz, `coalesce(1)` vermeiden |
| **Lücken** | Event Timeline | Lücken ≥ 1 min | Serverless, `withColumn`-Schleifen ersetzen, Driver entlasten |
| **Viele kleine Jobs** | Event Timeline | viele Jobs à wenige Sekunden, Daten < 10 GB | Parallelisieren: Lakeflow Pipelines, Multi-Task-Jobs, SQL Warehouse |
| **Driver überlastet** | Compute → **Metrics** → Server load distribution | ein **roter** Block (Driver) | Driver **verdoppeln**, Nebenläufigkeit senken, verteilen |
| **Executors entfernt** | Event Timeline (rot) → Event log → Executors | Autoscaling / Spot / OOM | Autoscaling ist ok; Spot-Typ wechseln; Speicher |
| **Speicherproblem** | Failed Tasks, `ExecutorLostFailure` | besser mit doppeltem RAM/Core | Shuffle-Partitionen, Broadcast, UDF, Window ohne `PARTITION BY`, Skew, State |
| **AQE aktiv?** | SQL-DAG | `AdaptiveSparkPlan`, `isFinalPlan=true` | — |
| **AQE-Skew wirkt** | SQL-DAG | `SortMergeJoin` mit `isSkew=true` | — |
| **Photon greift?** | SQL-DAG / Query Profile | orange (Spark UI) / lila (Query Profile) | UDFs/RDDs vermeiden |
| **Streaming-Rückstau** | Streaming-Reiter → Processing Time | Verarbeitung > 80 % des Batch-Intervalls | mehr Ressourcen, Trigger-Intervall, Parallelität |

---

## 2. Typische Fallen

| Aussage | Richtig? |
|---|---|
| Serverless-Notebooks haben ein Spark UI | ❌ Query Profile / Query Insights |
| Zeiten im SQL-DAG sind Wanduhr-Zeiten | ❌ kumulativ über alle Tasks |
| Fehlen die Spill-Spalten, ist das ein Anzeigefehler | ❌ dann gibt es **keinen** Spill |
| Entfernte Executors sind immer ein Fehler | ❌ Autoscaling ist erwartet |
| `EXPLAIN` zeigt den finalen AQE-Plan | ❌ nur den Initial Plan |
| AQE ändert die Join-Reihenfolge | ❌ |
| AQE optimiert Skew auch bei Broadcast Joins | ❌ nur SMJ/Shuffle Hash |
| Broadcast-Hint ist mit AQE überflüssig | ❌ statischer Broadcast ist meist schneller |
| Nach Neustart eines beendeten Clusters sieht man die alten Jobs im Spark UI | ❌ nur die des neu gestarteten Compute |
| Für das Spark UI eines Jobs reicht CAN VIEW | ❌ CAN MANAGE RUN oder höher |
| Executor-Logs gibt es auch im Standard Access Mode | ❌ |

---

## 3. Übungsfragen

**1. Wo beginnt man laut Databricks die Diagnose im Spark UI?**
A) Environment · B) **Jobs → Event Timeline** ✅ · C) Storage · D) Executors

**2. Summary Metrics einer Stage: 75. Perzentil 20 s, Max 45 s. Was liegt vermutlich vor?**
A) Spill · B) **Skew** ✅ · C) Small Files · D) Driver-Überlastung
*(Max > 1,5 × 75. Perzentil)*

**3. Auf der Stage-Seite gibt es keine Spill-Spalten. Was bedeutet das?**
A) Spill wird nur im SQL-DAG gezeigt · B) **Die Stage hat keinen Spill** ✅ · C) Photon verbirgt Spill · D) AQE hat Spill entfernt

**4. Ein Scan-Knoten liest 80.000 Dateien für 5 GB. Beste Maßnahme?**
A) Mehr Shuffle-Partitionen · B) Broadcast-Hint · C) **`OPTIMIZE` / Predictive Optimization, Partitionierung überdenken** ✅ · D) Driver vergrößern

**5. Eine lange Stage hat genau einen Task. Welche Ursache passt NICHT?**
A) Gzip-Datei · B) `coalesce(1)` · C) `multiLine`-JSON · D) **zu viele Shuffle-Partitionen** ✅

**6. Wie analysiert man die Performance einer Abfrage auf Serverless-Compute?**
A) Spark UI · B) **Query Profile** ✅ · C) Ganglia · D) Executor-Logs

**7. Welche Berechtigung braucht man mindestens, um das Spark UI eines Clusters zu sehen?**
A) CAN MANAGE · B) CAN RESTART · C) **CAN ATTACH TO** ✅ · D) keine

**8. Große Lücken in der Timeline, Worker idle, Driver-Block in den Metriken rot. Erste Empfehlung?**
A) Mehr Worker · B) **Driver-Größe verdoppeln** ✅ · C) Spot-Instanzen · D) AQE ausschalten

**9. Welcher Plan-Hinweis zeigt, dass AQE Shuffle-Partitionen zusammengefasst hat?**
A) `isSkew=true` · B) **`CustomShuffleReader` / `AQEShuffleRead` mit `Coalesced`** ✅ · C) `LocalTableScan` · D) `BroadcastExchange`

**10. Ab wann gilt eine Partition für AQE als schief (Defaults)?**
A) > 64 MB · B) > 2 × Median · C) **> 5 × Median UND > 256 MB** ✅ · D) > 30 MB

**11. Faustregel für Streaming-Batches?**
A) Verarbeitung ≤ 50 % · B) **≤ 80 % des Batch-Intervalls** ✅ · C) = Batch-Intervall · D) egal

**12. Viele Jobs à 2 Sekunden auf < 10 GB Daten. Was hilft am meisten?**
A) Größere Worker · B) **Operationen parallelisieren (Lakeflow Pipelines, Multi-Task-Jobs, SQL Warehouse)** ✅ · C) Mehr Shuffle-Partitionen · D) Z-Order

## Quellen

Siehe Dateien [01](01%20Aufbau%2C%20Zugriff%20und%20Logs.md)–[05](05%20Query%20Profile%2C%20Serverless%20und%20Jobs.md) in diesem Ordner.
