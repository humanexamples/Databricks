# Adaptive Query Execution (AQE)

Adaptive Query Execution (AQE) ist eine Neuoptimierung von Abfragen, die während der Ausführung stattfindet. Diese Seite erklärt Funktionsweise, Konfiguration und häufige Fragen.

## Warum eine Neuoptimierung zur Laufzeit?

Databricks hat am Ende eines Shuffle- oder Broadcast-Austauschs (in AQE als Query Stage bezeichnet) die aktuellsten und genauesten Statistiken. Dadurch kann Databricks eine bessere physische Strategie wählen. Es kann eine optimale Partitionsgröße und -anzahl nach dem Shuffle festlegen. Es kann auch Optimierungen durchführen, die früher Hints benötigten, zum Beispiel bei Skew-Joins.

Das ist besonders nützlich, wenn keine Statistiken erfasst wurden oder diese veraltet sind. Es hilft auch dort, wo statisch abgeleitete Statistiken ungenau sind, etwa mitten in einer komplexen Abfrage oder nach Datenschiefe (Data Skew).

## Fähigkeiten

AQE ist standardmäßig aktiviert und bietet vier Hauptfunktionen:

- Wandelt Sort-Merge-Joins dynamisch in Broadcast-Hash-Joins um.
- Fasst kleine Partitionen nach einem Shuffle-Austausch dynamisch zusammen. Sehr kleine Tasks haben einen schlechteren I/O-Durchsatz und leiden stärker unter Scheduling- und Setup-Overhead. Das Zusammenfassen kleiner Tasks spart Ressourcen und verbessert den Cluster-Durchsatz.
- Erkennt Datenschiefe bei Sort-Merge-Joins und Shuffle-Hash-Joins. Sie teilt schiefe Tasks bei Bedarf mit Replikation in annähernd gleich große Tasks auf.
- Erkennt leere Relationen dynamisch und propagiert sie durch den Plan.

## Anwendungsbereich

AQE gilt für alle Abfragen, die:

- nicht streamend sind,
- mindestens einen Exchange enthalten (meist bei Join, Aggregation oder Window),
- eine Subquery oder beides.

Nicht jede Abfrage, auf die AQE angewendet wird, wird tatsächlich neu optimiert. Die Neuoptimierung kann zu einem anderen Plan führen als dem statisch kompilierten, muss aber nicht. Ob sich der Plan geändert hat, sehen Sie im nächsten Abschnitt.

## Query-Pläne prüfen

### Spark UI

**AdaptiveSparkPlan-Knoten:** Abfragen, auf die AQE angewendet wird, enthalten einen oder mehrere `AdaptiveSparkPlan`-Knoten, meist als Root-Knoten jeder Haupt- oder Subquery. Vor und während der Ausführung zeigt das Flag `isFinalPlan` des zugehörigen Knotens `false`. Nach Abschluss der Ausführung wechselt es zu `true`.

**Sich entwickelnder Plan:** Das Plandiagramm entwickelt sich während der Ausführung weiter. Es zeigt jeweils den aktuell ausgeführten Plan. Bereits ausgeführte Knoten mit verfügbaren Metriken ändern sich nicht mehr. Noch nicht ausgeführte Knoten können sich durch Neuoptimierungen ändern.

### DataFrame.explain()

**AdaptiveSparkPlan-Knoten:** Wie in der Spark UI enthalten Abfragen einen oder mehrere `AdaptiveSparkPlan`-Knoten. Das Flag `isFinalPlan` verhält sich genauso.

**Aktueller und initialer Plan:** Unter jedem `AdaptiveSparkPlan`-Knoten finden Sie sowohl den initialen Plan (vor jeder AQE-Optimierung) als auch den aktuellen beziehungsweise finalen Plan. Der aktuelle Plan entwickelt sich mit fortschreitender Ausführung weiter.

**Laufzeitstatistiken:** Jede Shuffle- und Broadcast-Stufe enthält Datenstatistiken. Vor und während der Ausführung sind die Statistiken Compile-Time-Schätzungen, das Flag `isRuntime` ist `false`, zum Beispiel:

```
Statistics(sizeInBytes=1024.0 KiB, rowCount=4, isRuntime=false);
```

Nach Abschluss der Stufe sind es zur Laufzeit erfasste Statistiken. Das Flag `isRuntime` wird `true`, zum Beispiel:

```
Statistics(sizeInBytes=658.1 KiB, rowCount=2.81E+4, isRuntime=true)
```

### SQL EXPLAIN

**AdaptiveSparkPlan-Knoten:** Auch hier erscheinen ein oder mehrere `AdaptiveSparkPlan`-Knoten.

**Kein aktueller Plan:** Da `SQL EXPLAIN` die Abfrage nicht ausführt, entspricht der aktuelle Plan immer dem initialen Plan. Er zeigt nicht, was AQE letztlich ausführen würde.

## Wirksamkeit erkennen

Der Query-Plan ändert sich, wenn eine oder mehrere AQE-Optimierungen greifen. Das zeigt sich im Unterschied zwischen aktuellem beziehungsweise finalem Plan und initialem Plan, an bestimmten Knoten:

- Dynamischer Wechsel von Sort-Merge-Join zu Broadcast-Hash-Join: unterschiedliche physische Join-Knoten zwischen aktuellem/finalem Plan und initialem Plan.
- Dynamisches Zusammenfassen von Partitionen: Knoten `CustomShuffleReader` mit der Eigenschaft `Coalesced`.
- Dynamische Behandlung von Skew-Joins: Knoten `SortMergeJoin` mit dem Feld `isSkew` gleich `true`.
- Dynamisches Erkennen leerer Relationen: Ein Teil des Plans, oder der gesamte Plan, wird durch den Knoten `LocalTableScan` mit leerem Relationsfeld ersetzt.

## Konfiguration

### AQE aktivieren und deaktivieren

- Eigenschaft: `spark.databricks.optimizer.adaptive.enabled`
- Typ: Boolean
- Beschreibung: Aktiviert oder deaktiviert Adaptive Query Execution.
- Standardwert: `true`

### Auto-optimiertes Shuffle aktivieren

- Eigenschaft: `spark.sql.shuffle.partitions`
- Typ: Integer
- Beschreibung: Standardanzahl der Partitionen beim Shuffling für Joins oder Aggregationen. Der Wert `auto` aktiviert Auto-optimiertes Shuffle. Die Anzahl wird dann automatisch anhand von Query-Plan und Eingabedatenmenge bestimmt.
- Standardwert: 200

Bei Structured Streaming kann diese Konfiguration zwischen Neustarts einer Abfrage aus demselben Checkpoint-Verzeichnis nicht geändert werden.

### Dynamischer Wechsel von Sort-Merge-Join zu Broadcast-Hash-Join

- Eigenschaft: `spark.databricks.adaptive.autoBroadcastJoinThreshold`
- Typ: Byte String
- Beschreibung: Schwellenwert, der zur Laufzeit den Wechsel zu Broadcast-Join auslöst.
- Standardwert: 30MB

### Dynamisches Zusammenfassen von Partitionen

- Eigenschaft: `spark.sql.adaptive.coalescePartitions.enabled`
  - Typ: Boolean
  - Beschreibung: Aktiviert oder deaktiviert das Zusammenfassen von Partitionen.
  - Standardwert: `true`
- Eigenschaft: `spark.sql.adaptive.advisoryPartitionSizeInBytes`
  - Typ: Byte String
  - Beschreibung: Zielgröße nach dem Zusammenfassen. Die zusammengefassten Partitionsgrößen liegen nahe an, aber nicht über dieser Zielgröße.
  - Standardwert: 64MB
- Eigenschaft: `spark.sql.adaptive.coalescePartitions.minPartitionSize`
  - Typ: Byte String
  - Beschreibung: Mindestgröße der Partitionen nach dem Zusammenfassen. Die zusammengefassten Partitionsgrößen liegen nicht unter diesem Wert.
  - Standardwert: 1MB
- Eigenschaft: `spark.sql.adaptive.coalescePartitions.minPartitionNum`
  - Typ: Integer
  - Beschreibung: Mindestanzahl an Partitionen nach dem Zusammenfassen. Nicht empfohlen, da eine explizite Einstellung `spark.sql.adaptive.coalescePartitions.minPartitionSize` überschreibt.
  - Standardwert: 2x Anzahl der Cluster-Kerne

### Dynamische Behandlung von Skew-Joins

- Eigenschaft: `spark.sql.adaptive.skewJoin.enabled`
  - Typ: Boolean
  - Beschreibung: Aktiviert oder deaktiviert die Behandlung von Skew-Joins.
  - Standardwert: `true`
- Eigenschaft: `spark.sql.adaptive.skewJoin.skewedPartitionFactor`
  - Typ: Integer
  - Beschreibung: Faktor, der mit der Median-Partitionsgröße multipliziert wird, um zu bestimmen, ob eine Partition schief ist.
  - Standardwert: 5
- Eigenschaft: `spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes`
  - Typ: Byte String
  - Beschreibung: Schwellenwert, der mitbestimmt, ob eine Partition schief ist.
  - Standardwert: 256MB

Eine Partition gilt als schief, wenn beide Bedingungen zutreffen: (Partitionsgröße > `skewedPartitionFactor` * Median-Partitionsgröße) und (Partitionsgröße > `skewedPartitionThresholdInBytes`).

### Dynamisches Erkennen und Propagieren leerer Relationen

- Eigenschaft: `spark.databricks.adaptive.emptyRelationPropagation.enabled`
- Typ: Boolean
- Beschreibung: Aktiviert oder deaktiviert die dynamische Propagierung leerer Relationen.
- Standardwert: `true`

## Häufig gestellte Fragen (FAQ)

### Warum wurde eine kleine Join-Tabelle nicht per Broadcast verteilt?

Liegt die Größe der zu broadcastenden Relation unter dem Schwellenwert, wird aber trotzdem kein Broadcast durchgeführt, prüfen Sie Folgendes:

- Prüfen Sie den Join-Typ. Broadcast wird für bestimmte Join-Typen nicht unterstützt. Zum Beispiel kann die linke Relation eines `LEFT OUTER JOIN` nicht per Broadcast verteilt werden.
- Die Relation kann viele leere Partitionen enthalten. Dann sind die meisten Tasks beim Sort-Merge-Join ohnehin schnell fertig, oder die Situation lässt sich durch Skew-Join-Handling optimieren. AQE vermeidet den Wechsel zu Broadcast-Hash-Join, wenn der Anteil nicht-leerer Partitionen unter `spark.sql.adaptive.nonEmptyPartitionRatioForBroadcastJoin` liegt.

### Sollte ich trotz aktiviertem AQE weiterhin einen Broadcast-Join-Hint verwenden?

Ja. Ein statisch geplanter Broadcast-Join ist meist performanter als ein dynamisch von AQE geplanter. AQE wechselt unter Umständen erst nach dem Shuffle beider Join-Seiten zu Broadcast, dann sind die tatsächlichen Relationsgrößen erst bekannt. Kennen Sie Ihre Abfrage gut, ist ein Broadcast-Hint weiterhin sinnvoll. AQE respektiert Query-Hints wie die statische Optimierung. Zusätzlich wendet AQE dynamische Optimierungen an, die von den Hints nicht betroffen sind.

### Was ist der Unterschied zwischen dem Skew-Join-Hint und der AQE-Skew-Join-Optimierung? Was sollte ich nutzen?

Databricks empfiehlt, sich auf die AQE-Skew-Join-Behandlung zu verlassen statt auf den Skew-Join-Hint. AQE-Skew-Join-Handling läuft vollautomatisch und liefert meist bessere Ergebnisse als der Hint.

### Warum hat AQE meine Join-Reihenfolge nicht automatisch angepasst?

Dynamisches Join-Reordering ist nicht Teil von AQE.

### Warum hat AQE meine Datenschiefe nicht erkannt?

Zwei Größenbedingungen müssen gleichzeitig erfüllt sein, damit AQE eine Partition als schief erkennt:

- Die Partitionsgröße ist größer als `spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes` (Standard 256MB).
- Die Partitionsgröße ist größer als die mediane Größe aller Partitionen, multipliziert mit dem Skew-Partition-Faktor `spark.sql.adaptive.skewJoin.skewedPartitionFactor` (Standard 5).

Zusätzlich ist die Skew-Behandlung bei bestimmten Join-Typen eingeschränkt. Bei `LEFT OUTER JOIN` kann zum Beispiel nur Skew auf der linken Seite optimiert werden.

## Legacy

Den Begriff „Adaptive Execution" gibt es bereits seit Spark 1.6. Das neue AQE in Spark 3.0 unterscheidet sich davon grundlegend. Funktional deckte Spark 1.6 nur das dynamische Zusammenfassen von Partitionen ab. Technisch-architektonisch ist das neue AQE ein Framework für dynamische Planung und Neuplanung von Abfragen auf Basis von Laufzeitstatistiken. Es unterstützt die hier beschriebenen Optimierungen und lässt sich um weitere Optimierungen erweitern.

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/aqe  
**Stand:** 2026-08-06
