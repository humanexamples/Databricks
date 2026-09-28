# Spark-Ausführungsarchitektur

Grundbegriffe der Spark-/Databricks-Ausführungsarchitektur — Driver, Cluster Manager, Worker Node, Executor, Cores, Job, Stage, Task — sowie ein kurzer Überblick zu Adaptive Query Execution (AQE) und generellen Code-Optimierungsempfehlungen. Diese Datei dient als **Einstiegspunkt vor** den bereits vorhandenen, tieferen Referenzen [Shuffles.md](../Code%20Optimization/Shuffles.md) und [Data Skew.md](../Code%20Optimization/Data%20Skew.md), die diese Grundbegriffe bereits voraussetzen, aber nicht selbst einführen. Basierend auf einer privaten Kursnotiz sowie der offiziellen Apache-Spark- und Databricks-Dokumentation (jeweils am Ende jedes Abschnitts referenziert).

## Abschnittsübersicht

1. [Job, Stage, Task](#grundbegriffe)
2. [Spark-Cluster-Architektur: Driver, Cluster Manager, Worker, Executor](#architektur)
3. [Databricks-spezifische Besonderheit: ein Executor pro Worker Node](#databricks-executor)
4. [Cores/Slots und Ausführungsfluss: Client → Driver → Executor-Cores → Tasks](#ausfuehrungsfluss)
5. [Single-Node-Compute](#single-node)
6. [Adaptive Query Execution (AQE) im Überblick](#aqe)
7. [Generelle Code-Optimierungsempfehlungen](#code-optimierung)
8. [Zusammenfassung](#zusammenfassung)

---

## <a id="grundbegriffe">1. Job, Stage, Task</a>

Nach offizieller Apache-Spark-Terminologie:

- **Job:** „A parallel computation consisting of multiple tasks that gets spawned in response to a Spark action" (z. B. `save()`, `collect()`). Jede parallelisierte Action erzeugt also einen eigenen Job.
- **Stage:** „Each job gets divided into smaller sets of tasks called stages that depend on each other (similar to the map and reduce stages in MapReduce)." Stages sind eine geordnete Menge von Schritten, die gemeinsam einen Job erfüllen — eine neue Stage entsteht in der Regel dort, wo ein Shuffle nötig wird (siehe [Shuffles.md](../Code%20Optimization/Shuffles.md), Abschnitt „Wide vs. Narrow Transformations").
- **Task:** „A unit of work that will be sent to one executor." Tasks sind die kleinste Ausführungseinheit in Spark; sie werden vom Driver erzeugt und jeweils einer Datenpartition zugewiesen.

Diese drei Begriffe erscheinen so auch in den Driver-Logs sowie in der Spark UI (Jobs-Tab → Stages-Tab → Tasks-Tabelle).

### Quellen

- https://spark.apache.org/docs/latest/cluster-overview.html
- Private Kursnotiz (Einordnung als „Ausführungshierarchie" einer Spark-Anwendung)

---

## <a id="architektur">2. Spark-Cluster-Architektur: Driver, Cluster Manager, Worker, Executor</a>

Nach offizieller Apache-Spark-Dokumentation laufen Spark-Anwendungen als unabhängige Prozessmengen auf einem Cluster, koordiniert durch das `SparkContext`-Objekt im Hauptprogramm.

- **Driver-Programm:** „The process running the `main()` function of the application and creating the `SparkContext`." Der Driver ist damit die Instanz, die
  - Informationen über die Spark-Anwendung vorhält,
  - auf das Nutzerprogramm reagiert, und
  - Arbeit über die Executors hinweg analysiert, verteilt und einplant (`SparkContext sends tasks to the executors to run`).
  - Der Driver muss über das Netzwerk von den Worker-Knoten aus erreichbar sein und sollte — da er Tasks im Cluster einplant — möglichst nah an den Worker-Knoten laufen, idealerweise im selben lokalen Netzwerk.
  - **In einem Databricks-Cluster gibt es unabhängig von der Anzahl der Executors immer nur genau einen Driver.**
- **Cluster Manager:** „An external service for acquiring resources on the cluster" (z. B. Spark Standalone, Hadoop YARN, Kubernetes) — verteilt Ressourcen über mehrere Anwendungen hinweg. Der `SparkContext` kann sich mit verschiedenen Cluster-Manager-Typen verbinden.
- **Worker Node:** „Any node that can run application code in the cluster" — ein physischer bzw. virtueller Knoten, auf dem Anwendungscode ausgeführt werden kann.
- **Executor:** „A process launched for an application on a worker node, that runs tasks and keeps data in memory or disk storage across them. Each application has its own executors." Executors sind also Prozesse, die auf einem Worker Node laufen, Berechnungen durchführen, Daten für die Anwendung vorhalten und über die Lebensdauer der Anwendung hinweg bestehen bleiben (Ausführung mehrerer Tasks in parallelen Threads).
  - Jeder Executor hält einen Teil der zu verarbeitenden Daten — eine **Spark-Partition** (eine Sammlung von Zeilen, physisch auf einer Maschine im Cluster). Das ist strikt von Festplattenpartitionen zu unterscheiden, die sich auf den Speicherplatz einer Festplatte beziehen.
  - Jeder Executor ist für zwei Dinge zuständig: den vom Driver zugewiesenen Code auszuführen und den Status der Berechnung an den Driver zurückzumelden.

### Quellen

- https://spark.apache.org/docs/latest/cluster-overview.html
- Private Kursnotiz (Driver/Worker-Node/Executor-Beschreibung, Spark-Partition-Begriff)

---

## <a id="databricks-executor">3. Databricks-spezifische Besonderheit: ein Executor pro Worker Node</a>

**Abweichung vom generischen Apache-Spark-Modell:** Während Open-Source-Spark grundsätzlich mehrere Executors pro physischem Knoten zulässt (konfigurierbar über den jeweiligen Cluster-Manager), legt Databricks dieses Verhältnis fest auf 1:1 fest:

> „Databricks runs one executor per worker node. Therefore, the terms executor and worker are used interchangeably in the context of the Databricks architecture."

Das heißt: In Databricks-Dokumentation und -UI werden „Worker" und „Executor" häufig synonym verwendet, weil es strukturell immer nur einen Executor je Worker-Knoten gibt. Die *interne* Parallelität innerhalb eines Workers entsteht stattdessen über die Anzahl der **Cores/Slots** dieses einen Executors (siehe Abschnitt 4), nicht über mehrere Executor-Prozesse auf demselben Knoten.

- Der Driver-Knoten hält den Zustand aller angehängten Notebooks, verwaltet den `SparkContext`, interpretiert alle ausgeführten Befehle und führt den Apache-Spark-Master aus, der mit den Executors koordiniert.
- „In multi-node compute, worker nodes run the Spark executors and other services required for a properly functioning compute resource."
- Um überhaupt einen Spark-Job auszuführen, wird mindestens ein Worker-Knoten benötigt — bei null Workern lassen sich nur Nicht-Spark-Befehle auf dem Driver-Knoten ausführen, Spark-Befehle schlagen fehl.

### Quelle

- https://docs.databricks.com/aws/en/compute/configure

---

## <a id="ausfuehrungsfluss">4. Cores/Slots und Ausführungsfluss: Client → Driver → Executor-Cores → Tasks</a>

Aus einer privaten Kursnotiz übernommen — der grundlegende Ausführungsfluss einer Spark-Anwendung lässt sich vereinfacht so beschreiben: Ein Client stellt eine Query. Der Driver erstellt daraus „Arbeitsanweisungen" für kleine, handliche Speicherpartitionen (Memory Partitions), die dann von den Cores der Executors parallel als Tasks (Arbeitseinheiten) erzeugt und ausgeführt werden.

**Cores** (auch als **Slots** oder **Threads** bezeichnet) sind die Ebene, auf der Spark innerhalb eines Executors parallelisiert:

- Spark parallelisiert auf zwei Ebenen: erstens die Aufteilung der Arbeit auf mehrere Executors, zweitens die Aufteilung innerhalb eines Executors auf dessen Cores/Slots.
- Jeder Executor besitzt eine bestimmte Anzahl an Slots; jedem Slot kann ein Task zugewiesen werden. Zu einem gegebenen Zeitpunkt können manche Slots mit Tasks belegt und andere frei sein.
- Offiziell konfigurierbar über `spark.executor.cores` (Anzahl Cores/Threads pro Executor).

**Diagramm-Beschreibung (Nicht-Databricks-Quelle: privates Kursmaterial):** Client → Driver → mehrere Worker-Knoten mit je einem Executor → mehrere Cores pro Executor, auf denen parallel Tasks laufen, die jeweils eine Partition der Daten verarbeiten.

Ein Cluster besteht dabei aus einer oder mehreren virtuellen Maschineninstanzen, über die Rechenlast verteilt wird. Im Regelfall besteht ein Cluster aus einem Driver-Knoten und einem oder mehreren Worker-Knoten; Databricks bietet zusätzlich ein Single-Node-Modell an (siehe Abschnitt 5), typischerweise für Entwicklung oder Tests mit kleinen Workloads begrenzt.

### Quellen

- Private Kursnotiz (Diagramm-Beschreibung, Cores/Slots-Erklärung)
- https://docs.databricks.com/aws/en/compute/configure

---

## <a id="single-node">5. Single-Node-Compute</a>

Im Single-Node-Modell entfällt die Trennung von Driver und Worker-Knoten vollständig:

- Der Driver „acts as both master and worker, with no worker nodes".
- Er „spawns one executor thread per logical core in the compute resource, minus 1 core for the driver" — d. h. die Anzahl der Executor-Threads entspricht der Anzahl logischer Kerne der Maschine minus einem Kern, der für den Driver-Prozess selbst reserviert bleibt.

Single-Node-Compute eignet sich laut Kursnotiz typischerweise für Entwicklung oder Tests mit kleinen Workloads, nicht für Produktions-Workloads mit hohem Parallelitätsbedarf.

### Quelle

- https://docs.databricks.com/aws/en/compute/configure

---

## <a id="aqe">6. Adaptive Query Execution (AQE) im Überblick</a>

**Definition:** „Adaptive query execution (AQE) is query re-optimization that occurs during query execution" — AQE nutzt exakte Laufzeitstatistiken (insbesondere nach Shuffle- und Broadcast-Exchanges), um den Ausführungsplan einer Query während der Laufzeit neu zu optimieren, statt sich ausschließlich auf Compile-Zeit-Schätzungen zu verlassen.

**Vier Kernfähigkeiten** (die ersten drei bereits mit Spark 3.0 eingeführt, die vierte kam später hinzu):

1. **Dynamischer Join-Strategie-Wechsel:** wandelt Sort-Merge-Joins zur Laufzeit in Broadcast-Hash-Joins um, wenn sich eine Join-Seite als kleiner erweist als ursprünglich geschätzt.
2. **Dynamisches Coalescing von Shuffle-Partitionen:** fasst nach einem Shuffle zu kleine Partitionen zu angemessen großen zusammen (Details in [Shuffles.md](../Code%20Optimization/Shuffles.md), Abschnitt 5.1).
3. **Dynamische Optimierung von Skew-Joins:** teilt schiefe (skewed) Partitionen in gleichmäßig große Teilaufgaben auf (Details in [Data Skew.md](../Code%20Optimization/Data%20Skew.md)).
4. **Empty-Relation-Erkennung/-Propagation:** erkennt zur Laufzeit leere Zwischenergebnisse und propagiert diese Information durch den restlichen Query-Plan, sodass nachgelagerte Operationen auf offensichtlich leeren Daten übersprungen werden können.

**Versionsstand:** Neu eingeführt in Spark 3.0 (zunächst standardmäßig **deaktiviert**, konfigurierbar über `spark.sql.adaptive.enabled`), seit **Spark 3.2 standardmäßig aktiviert**. In Databricks ist AQE ebenfalls standardmäßig aktiviert.

### Job-Optimierung mit vs. ohne AQE

**Mit AQE:** Der Ausführungsplan wird laufend anhand tatsächlicher Datenstatistiken angepasst — dynamische Partitionsanpassung, Join-Umordnung und weitere Optimierungen laufen während der Job-Ausführung.

**Ohne AQE** durchläuft eine DataFrame-Operation einen rein statischen Optimierungspfad:

1. **Logical Plan:** DataFrame-Operationen werden als logischer Plan repräsentiert, der die Abfolge der Operationen festlegt.
2. **Catalyst-Optimierung:** Catalyst, Sparks Optimizer, übersetzt den logischen Plan unter Berücksichtigung von Optimierungsregeln und Kostenmodellen in einen physischen Plan.
3. **Physical Plan:** Der physische Plan legt fest, wie die Berechnungen auf dem Cluster ausgeführt werden, und übersetzt DataFrame-Operationen in RDD-Transformationen und -Actions.

Ohne Laufzeitstatistiken bleibt dieser Plan während der gesamten Ausführung fix — Fehleinschätzungen aus der Compile-Zeit (z. B. bei Datengröße oder Skew) werden nicht mehr korrigiert.

### Quellen

- https://docs.databricks.com/aws/en/optimizations/aqe
- https://www.databricks.com/blog/2020/05/29/adaptive-query-execution-speeding-up-spark-sql-at-runtime.html
- https://www.databricks.com/blog/2021/10/19/introducing-apache-spark-3-2.html
- Private Kursnotiz (Gegenüberstellung „mit/ohne AQE", Logical-/Physical-Plan-Beschreibung)

---

## <a id="code-optimierung">7. Generelle Code-Optimierungsempfehlungen</a>

Aus einer privaten Kursnotiz übernommen, durch offizielle Doku ergänzt — drei grundlegende Empfehlungen, die vor spezifischeren Techniken (Shuffle-Tuning, Skew-Behandlung, Partitionierung) stehen sollten:

1. **DataFrame- oder SQL-APIs statt RDD-APIs verwenden.** RDD-Operationen umgehen Catalyst und profitieren nicht von dessen Planungs- und Optimierungsfähigkeiten (Prädikat-Pushdown, Spaltenbeschneidung, Join-Reordering usw.), die DataFrame- und SQL-Operationen automatisch erhalten.
2. **In Produktions-Jobs unnötige Actions vermeiden.** Operationen, die außerhalb von reinem Lesen/Schreiben eine Action auslösen — etwa `count()`, `display()`, `collect()` — erzwingen jeweils eine vollständige Ausführung des bis dahin aufgebauten Plans und sollten nur eingesetzt werden, wenn ihr Ergebnis tatsächlich gebraucht wird.
3. **Keine Berechnung erzwingen, die ausschließlich auf dem Driver-Knoten läuft** — etwa durch single-threaded Python/pandas-Code. Solcher Code nutzt nur einen einzigen Kern auf einer einzigen Maschine (dem Driver) und verzichtet vollständig auf die verteilte Ausführung über Executors und deren Cores hinweg. Stattdessen empfiehlt sich **Pandas API on Spark** (`import pyspark.pandas as ps`), um pandas-artige Syntax bei gleichzeitig verteilter Ausführung zu nutzen: „pandas does not scale out to big data" — Pandas API on Spark schließt genau diese Lücke, indem es pandas-äquivalente APIs bereitstellt, die auf Apache Spark laufen. Verfügbar seit Apache Spark 3.2 (enthalten ab Databricks Runtime 10.0; für ältere Runtimes existierte das Vorgängerprojekt Koalas).

### Quellen

- Private Kursnotiz
- https://docs.databricks.com/aws/en/pandas/pandas-on-spark

---

## <a id="zusammenfassung">8. Zusammenfassung</a>

Eine Spark-/Databricks-Anwendung wird vom **Driver** koordiniert, der Arbeit als **Jobs** (pro Action) einplant, die in **Stages** (getrennt durch Shuffles) und darin wiederum in **Tasks** (kleinste Arbeitseinheit, je eine Partition) zerlegt werden. Ausgeführt werden diese Tasks auf den **Cores/Slots** der **Executors**, die auf **Worker-Knoten** laufen — wobei Databricks abweichend von generischem Spark stets genau einen Executor pro Worker-Knoten betreibt. **AQE** ergänzt diese statische Planung um Laufzeit-Reoptimierung (Join-Strategie, Partition-Coalescing, Skew-Handling, Empty-Relation-Propagation). Die drei generellen Code-Empfehlungen — DataFrame/SQL statt RDD, unnötige Actions vermeiden, keine Driver-lastige Pandas-Nutzung — bilden die Grundlage, auf der die spezifischeren Techniken in [Shuffles.md](../Code%20Optimization/Shuffles.md), [Data Skew.md](../Code%20Optimization/Data%20Skew.md) und den übrigen Dateien in diesem Ordner aufbauen.
