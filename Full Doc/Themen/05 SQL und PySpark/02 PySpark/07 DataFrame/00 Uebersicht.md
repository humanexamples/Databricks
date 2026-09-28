# `DataFrame` — Klassenreferenz

Referenz für `pyspark.sql.DataFrame`.

## Beschreibung

*"A distributed collection of data grouped into named columns."*

Auf Deutsch: Eine verteilte Datensammlung, die in benannte Spalten gegliedert ist. Ein DataFrame entspricht einer relationalen Tabelle in Spark SQL und kann über verschiedene Funktionen der `SparkSession` erzeugt werden (z. B. `spark.createDataFrame`, `spark.read`, `spark.table`, `spark.sql`).

> **Wichtig:** Ein DataFrame sollte nicht direkt über den Konstruktor erstellt werden.

*Unterstützt Spark Connect.*

Eigenschaften (ohne Klammern aufgerufen, z. B. `df.columns`) sind in der Spalte „Art“ als **Eigenschaft** markiert, alle anderen Einträge sind Methoden.

## Ordnerstruktur

| Ordner | Thema |
| --- | --- |
| [01 Anzeigen und Inspizieren](01%20Anzeigen%20und%20Inspizieren/) | Daten ausgeben, Schema und Metadaten abfragen, Zeilen zum Driver holen |
| [02 Temporaere Views](02%20Temporaere%20Views/) | DataFrames als (globale) temporäre Views für SQL registrieren |
| [03 Spalten auswaehlen und bearbeiten](03%20Spalten%20auswaehlen%20und%20bearbeiten/) | Projektion, Spalten hinzufügen, umbenennen, entfernen, Schema angleichen |
| [04 Filtern Sortieren Limitieren](04%20Filtern%20Sortieren%20Limitieren/) | Zeilen filtern, sortieren, begrenzen, überspringen |
| [05 Aggregation und Gruppierung](05%20Aggregation%20und%20Gruppierung/) | `groupBy`, Rollup, Cube, Grouping Sets, Metriken |
| [06 Joins](06%20Joins/) | Joins, Cross Joins, Lateral Joins |
| [07 Mengenoperationen und Deduplizierung](07%20Mengenoperationen%20und%20Deduplizierung/) | Union, Intersect, Except, Duplikate entfernen |
| [08 Fehlende Werte](08%20Fehlende%20Werte/) | NULL/NaN entfernen, füllen, ersetzen |
| [09 Statistik und Sampling](09%20Statistik%20und%20Sampling/) | Quantile, Korrelation, Kovarianz, Stichproben |
| [10 Umformen und Transformieren](10%20Umformen%20und%20Transformieren/) | Unpivot, Transpose, verkettete Transformationen |
| [11 Partitionierung und Query-Plan](11%20Partitionierung%20und%20Query-Plan/) | Repartitionierung, Hints, Pläne analysieren und vergleichen |
| [12 Caching und Checkpointing](12%20Caching%20und%20Checkpointing/) | Cache, Persist, Checkpoints |
| [13 Konvertierung und Iteration](13%20Konvertierung%20und%20Iteration/) | pandas/Arrow/RDD, Batch-Funktionen, `foreach`, Plots |
| [14 Schreiben und Streaming](14%20Schreiben%20und%20Streaming/) | Writer, MERGE, Streaming, Watermarks |
| [15 Subqueries und Tabellenargumente](15%20Subqueries%20und%20Tabellenargumente/) | SCALAR-/EXISTS-Subqueries, Tabellenargumente für TVFs |

## 01 Anzeigen und Inspizieren

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`show`](01%20Anzeigen%20und%20Inspizieren/01%20show.md) | Methode | Gibt die ersten `n` Zeilen auf der Konsole aus. |
| [`printSchema`](01%20Anzeigen%20und%20Inspizieren/02%20printSchema.md) | Methode | Gibt das Schema in Baumform aus. |
| [`columns`](01%20Anzeigen%20und%20Inspizieren/03%20columns.md) | Eigenschaft | Namen aller Spalten als Liste. |
| [`dtypes`](01%20Anzeigen%20und%20Inspizieren/04%20dtypes.md) | Eigenschaft | Spaltennamen und Datentypen als Liste. |
| [`schema`](01%20Anzeigen%20und%20Inspizieren/05%20schema.md) | Eigenschaft | Schema als `StructType`. |
| [`count`](01%20Anzeigen%20und%20Inspizieren/06%20count.md) | Methode | Anzahl der Zeilen. |
| [`isEmpty`](01%20Anzeigen%20und%20Inspizieren/07%20isEmpty.md) | Methode | Prüft, ob der DataFrame leer ist. |
| [`collect`](01%20Anzeigen%20und%20Inspizieren/08%20collect.md) | Methode | Alle Datensätze als Liste von `Row`. |
| [`take`](01%20Anzeigen%20und%20Inspizieren/09%20take.md) | Methode | Die ersten `num` Zeilen als Liste von `Row`. |
| [`head`](01%20Anzeigen%20und%20Inspizieren/10%20head.md) | Methode | Die ersten `n` Zeilen. |
| [`first`](01%20Anzeigen%20und%20Inspizieren/11%20first.md) | Methode | Die erste Zeile als `Row`. |
| [`tail`](01%20Anzeigen%20und%20Inspizieren/12%20tail.md) | Methode | Die letzten `num` Zeilen als Liste von `Row`. |
| [`toLocalIterator`](01%20Anzeigen%20und%20Inspizieren/13%20toLocalIterator.md) | Methode | Iterator über alle Zeilen. |
| [`describe`](01%20Anzeigen%20und%20Inspizieren/14%20describe.md) | Methode | Basisstatistiken für numerische und String-Spalten. |
| [`summary`](01%20Anzeigen%20und%20Inspizieren/15%20summary.md) | Methode | Gewählte Statistiken für numerische und String-Spalten. |
| [`inputFiles`](01%20Anzeigen%20und%20Inspizieren/16%20inputFiles.md) | Methode | Best-Effort-Snapshot der zugrunde liegenden Dateien. |
| [`isLocal`](01%20Anzeigen%20und%20Inspizieren/17%20isLocal.md) | Methode | `True`, wenn `collect`/`take` lokal laufen können. |
| [`sparkSession`](01%20Anzeigen%20und%20Inspizieren/18%20sparkSession.md) | Eigenschaft | Die `SparkSession`, die den DataFrame erstellt hat. |
| [`executionInfo`](01%20Anzeigen%20und%20Inspizieren/19%20executionInfo.md) | Eigenschaft | `ExecutionInfo` nach der Ausführung (nur Spark Connect). |

## 02 Temporäre Views

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`createTempView`](02%20Temporaere%20Views/01%20createTempView.md) | Methode | Erstellt eine lokale temporäre View. |
| [`createOrReplaceTempView`](02%20Temporaere%20Views/02%20createOrReplaceTempView.md) | Methode | Erstellt oder ersetzt eine lokale temporäre View. |
| [`createGlobalTempView`](02%20Temporaere%20Views/03%20createGlobalTempView.md) | Methode | Erstellt eine globale temporäre View. |
| [`createOrReplaceGlobalTempView`](02%20Temporaere%20Views/04%20createOrReplaceGlobalTempView.md) | Methode | Erstellt oder ersetzt eine globale temporäre View. |

## 03 Spalten auswählen und bearbeiten

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`select`](03%20Spalten%20auswaehlen%20und%20bearbeiten/01%20select.md) | Methode | Projiziert eine Menge von Ausdrücken. |
| [`selectExpr`](03%20Spalten%20auswaehlen%20und%20bearbeiten/02%20selectExpr.md) | Methode | Projiziert eine Menge von SQL-Ausdrücken. |
| [`drop`](03%20Spalten%20auswaehlen%20und%20bearbeiten/03%20drop.md) | Methode | Entfernt die angegebenen Spalten. |
| [`withColumn`](03%20Spalten%20auswaehlen%20und%20bearbeiten/04%20withColumn.md) | Methode | Fügt eine Spalte hinzu oder ersetzt eine gleichnamige. |
| [`withColumns`](03%20Spalten%20auswaehlen%20und%20bearbeiten/05%20withColumns.md) | Methode | Fügt mehrere Spalten hinzu oder ersetzt gleichnamige. |
| [`withColumnRenamed`](03%20Spalten%20auswaehlen%20und%20bearbeiten/06%20withColumnRenamed.md) | Methode | Benennt eine Spalte um. |
| [`withColumnsRenamed`](03%20Spalten%20auswaehlen%20und%20bearbeiten/07%20withColumnsRenamed.md) | Methode | Benennt mehrere Spalten um. |
| [`toDF`](03%20Spalten%20auswaehlen%20und%20bearbeiten/08%20toDF.md) | Methode | Vergibt neue Spaltennamen. |
| [`alias`](03%20Spalten%20auswaehlen%20und%20bearbeiten/09%20alias.md) | Methode | Setzt einen Alias für den DataFrame. |
| [`colRegex`](03%20Spalten%20auswaehlen%20und%20bearbeiten/10%20colRegex.md) | Methode | Wählt Spalten per regulärem Ausdruck aus. |
| [`metadataColumn`](03%20Spalten%20auswaehlen%20und%20bearbeiten/11%20metadataColumn.md) | Methode | Wählt eine Metadatenspalte über ihren logischen Namen aus. |
| [`withMetadata`](03%20Spalten%20auswaehlen%20und%20bearbeiten/12%20withMetadata.md) | Methode | Aktualisiert die Metadaten einer bestehenden Spalte. |
| [`to`](03%20Spalten%20auswaehlen%20und%20bearbeiten/13%20to.md) | Methode | Gleicht jede Zeile an ein angegebenes Schema an. |

## 04 Filtern, Sortieren, Limitieren

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`filter`](04%20Filtern%20Sortieren%20Limitieren/01%20filter.md) | Methode | Filtert Zeilen anhand einer Bedingung. |
| [`where`](04%20Filtern%20Sortieren%20Limitieren/02%20where.md) | Methode | Alias für `filter`. |
| [`sort`](04%20Filtern%20Sortieren%20Limitieren/03%20sort.md) | Methode | Sortiert nach den angegebenen Spalten. |
| [`orderBy`](04%20Filtern%20Sortieren%20Limitieren/04%20orderBy.md) | Methode | Alias für `sort`. |
| [`sortWithinPartitions`](04%20Filtern%20Sortieren%20Limitieren/05%20sortWithinPartitions.md) | Methode | Sortiert jede Partition nach den angegebenen Spalten. |
| [`limit`](04%20Filtern%20Sortieren%20Limitieren/06%20limit.md) | Methode | Begrenzt die Anzahl der Ergebniszeilen. |
| [`offset`](04%20Filtern%20Sortieren%20Limitieren/07%20offset.md) | Methode | Überspringt die ersten `n` Zeilen. |

## 05 Aggregation und Gruppierung

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`groupBy`](05%20Aggregation%20und%20Gruppierung/01%20groupBy.md) | Methode | Gruppiert nach den angegebenen Spalten für Aggregationen. |
| [`agg`](05%20Aggregation%20und%20Gruppierung/02%20agg.md) | Methode | Aggregiert über den gesamten DataFrame (Kurzform für `df.groupBy().agg()`). |
| [`rollup`](05%20Aggregation%20und%20Gruppierung/03%20rollup.md) | Methode | Mehrdimensionales Rollup. |
| [`cube`](05%20Aggregation%20und%20Gruppierung/04%20cube.md) | Methode | Mehrdimensionaler Cube. |
| [`groupingSets`](05%20Aggregation%20und%20Gruppierung/05%20groupingSets.md) | Methode | Mehrdimensionale Aggregation über Grouping Sets. |
| [`observe`](05%20Aggregation%20und%20Gruppierung/06%20observe.md) | Methode | Definiert (benannte) Metriken, die beobachtet werden. |

## 06 Joins

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`join`](06%20Joins/01%20join.md) | Methode | Joint mit einem anderen DataFrame über einen Join-Ausdruck. |
| [`crossJoin`](06%20Joins/02%20crossJoin.md) | Methode | Kartesisches Produkt mit einem anderen DataFrame. |
| [`lateralJoin`](06%20Joins/03%20lateralJoin.md) | Methode | Lateral Join mit einem anderen DataFrame. |

## 07 Mengenoperationen und Deduplizierung

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`union`](07%20Mengenoperationen%20und%20Deduplizierung/01%20union.md) | Methode | Vereinigung der Zeilen (positionsbasiert, ohne Deduplizierung). |
| [`unionByName`](07%20Mengenoperationen%20und%20Deduplizierung/02%20unionByName.md) | Methode | Vereinigung der Zeilen (namensbasiert). |
| [`intersect`](07%20Mengenoperationen%20und%20Deduplizierung/03%20intersect.md) | Methode | Schnittmenge ohne Duplikate. |
| [`intersectAll`](07%20Mengenoperationen%20und%20Deduplizierung/04%20intersectAll.md) | Methode | Schnittmenge mit Duplikaten. |
| [`subtract`](07%20Mengenoperationen%20und%20Deduplizierung/05%20subtract.md) | Methode | Differenzmenge (`EXCEPT DISTINCT`). |
| [`exceptAll`](07%20Mengenoperationen%20und%20Deduplizierung/06%20exceptAll.md) | Methode | Differenzmenge mit Duplikaten (`EXCEPT ALL`). |
| [`distinct`](07%20Mengenoperationen%20und%20Deduplizierung/07%20distinct.md) | Methode | Gibt die eindeutigen Zeilen zurück. |
| [`dropDuplicates`](07%20Mengenoperationen%20und%20Deduplizierung/08%20dropDuplicates.md) | Methode | Entfernt doppelte Zeilen, optional nur bezogen auf bestimmte Spalten. |
| [`dropDuplicatesWithinWatermark`](07%20Mengenoperationen%20und%20Deduplizierung/09%20dropDuplicatesWithinWatermark.md) | Methode | Entfernt doppelte Zeilen innerhalb des Watermarks (Streaming). |

## 08 Fehlende Werte

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`na`](08%20Fehlende%20Werte/01%20na.md) | Eigenschaft | `DataFrameNaFunctions` zur Behandlung fehlender Werte. |
| [`dropna`](08%20Fehlende%20Werte/02%20dropna.md) | Methode | Entfernt Zeilen mit NULL- oder NaN-Werten. |
| [`fillna`](08%20Fehlende%20Werte/03%20fillna.md) | Methode | Ersetzt NULL-Werte durch einen neuen Wert. |
| [`replace`](08%20Fehlende%20Werte/04%20replace.md) | Methode | Ersetzt einen Wert durch einen anderen. |

## 09 Statistik und Sampling

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`stat`](09%20Statistik%20und%20Sampling/01%20stat.md) | Eigenschaft | `DataFrameStatFunctions` für Statistikfunktionen. |
| [`approxQuantile`](09%20Statistik%20und%20Sampling/02%20approxQuantile.md) | Methode | Approximative Quantile numerischer Spalten. |
| [`corr`](09%20Statistik%20und%20Sampling/03%20corr.md) | Methode | Korrelation zweier Spalten (Pearson). |
| [`cov`](09%20Statistik%20und%20Sampling/04%20cov.md) | Methode | Stichproben-Kovarianz zweier Spalten. |
| [`crosstab`](09%20Statistik%20und%20Sampling/05%20crosstab.md) | Methode | Paarweise Häufigkeitstabelle (Kontingenztabelle). |
| [`freqItems`](09%20Statistik%20und%20Sampling/06%20freqItems.md) | Methode | Häufige Elemente, möglicherweise mit False Positives. |
| [`sample`](09%20Statistik%20und%20Sampling/07%20sample.md) | Methode | Gibt eine Stichprobe zurück. |
| [`sampleBy`](09%20Statistik%20und%20Sampling/08%20sampleBy.md) | Methode | Geschichtete Stichprobe ohne Zurücklegen. |
| [`randomSplit`](09%20Statistik%20und%20Sampling/09%20randomSplit.md) | Methode | Teilt den DataFrame zufällig nach Gewichten auf. |

## 10 Umformen und Transformieren

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`unpivot`](10%20Umformen%20und%20Transformieren/01%20unpivot.md) | Methode | Wide- zu Long-Format. |
| [`melt`](10%20Umformen%20und%20Transformieren/02%20melt.md) | Methode | Alias für `unpivot`. |
| [`transpose`](10%20Umformen%20und%20Transformieren/03%20transpose.md) | Methode | Transponiert den DataFrame anhand einer Indexspalte. |
| [`transform`](10%20Umformen%20und%20Transformieren/04%20transform.md) | Methode | Kompakte Syntax zum Verketten eigener Transformationen. |

## 11 Partitionierung und Query-Plan

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`repartition`](11%20Partitionierung%20und%20Query-Plan/01%20repartition.md) | Methode | Hash-Partitionierung nach Ausdrücken. |
| [`repartitionByRange`](11%20Partitionierung%20und%20Query-Plan/02%20repartitionByRange.md) | Methode | Range-Partitionierung nach Ausdrücken. |
| [`repartitionById`](11%20Partitionierung%20und%20Query-Plan/03%20repartitionById.md) | Methode | Partitionierung nach Partitions-ID-Ausdruck. |
| [`coalesce`](11%20Partitionierung%20und%20Query-Plan/04%20coalesce.md) | Methode | Reduziert auf genau `numPartitions` Partitionen (ohne Shuffle). |
| [`hint`](11%20Partitionierung%20und%20Query-Plan/05%20hint.md) | Methode | Gibt einen Optimierungs-Hint an. |
| [`explain`](11%20Partitionierung%20und%20Query-Plan/06%20explain.md) | Methode | Gibt die (logischen und physischen) Pläne aus. |
| [`sameSemantics`](11%20Partitionierung%20und%20Query-Plan/07%20sameSemantics.md) | Methode | `True`, wenn die logischen Query-Pläne beider DataFrames gleich sind. |
| [`semanticHash`](11%20Partitionierung%20und%20Query-Plan/08%20semanticHash.md) | Methode | Hashcode des logischen Query-Plans. |

## 12 Caching und Checkpointing

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`cache`](12%20Caching%20und%20Checkpointing/01%20cache.md) | Methode | Persistiert mit dem Standard-Storage-Level (`MEMORY_AND_DISK_DESER`). |
| [`persist`](12%20Caching%20und%20Checkpointing/02%20persist.md) | Methode | Setzt das Storage-Level für die Persistierung. |
| [`unpersist`](12%20Caching%20und%20Checkpointing/03%20unpersist.md) | Methode | Hebt die Persistierung auf und entfernt alle Blöcke. |
| [`storageLevel`](12%20Caching%20und%20Checkpointing/04%20storageLevel.md) | Eigenschaft | Aktuelles Storage-Level. |
| [`checkpoint`](12%20Caching%20und%20Checkpointing/05%20checkpoint.md) | Methode | Gibt eine gecheckpointete Version zurück. |
| [`localCheckpoint`](12%20Caching%20und%20Checkpointing/06%20localCheckpoint.md) | Methode | Gibt eine lokal gecheckpointete Version zurück. |

> **Serverless:** `cache`, `persist` und `checkpoint` sind nicht mit Serverless Compute kompatibel; Databricks empfiehlt, Zwischenergebnisse in Delta-Tabellen zu materialisieren.

## 13 Konvertierung und Iteration

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`toPandas`](13%20Konvertierung%20und%20Iteration/01%20toPandas.md) | Methode | Inhalt als `pandas.DataFrame`. |
| [`toArrow`](13%20Konvertierung%20und%20Iteration/02%20toArrow.md) | Methode | Inhalt als `pyarrow.Table`. |
| [`pandas_api`](13%20Konvertierung%20und%20Iteration/03%20pandas_api.md) | Methode | Konvertiert in einen pandas-on-Spark-DataFrame. |
| [`toJSON`](13%20Konvertierung%20und%20Iteration/04%20toJSON.md) | Methode | Konvertiert in ein RDD von JSON-Strings bzw. einen DataFrame. |
| [`rdd`](13%20Konvertierung%20und%20Iteration/05%20rdd.md) | Eigenschaft | Inhalt als RDD von `Row` (nur Classic-Modus). |
| [`mapInPandas`](13%20Konvertierung%20und%20Iteration/06%20mapInPandas.md) | Methode | Verarbeitet Batches mit einer Python-Funktion auf pandas-DataFrames. |
| [`mapInArrow`](13%20Konvertierung%20und%20Iteration/07%20mapInArrow.md) | Methode | Verarbeitet Batches mit einer Python-Funktion auf `pyarrow.RecordBatch`. |
| [`foreach`](13%20Konvertierung%20und%20Iteration/08%20foreach.md) | Methode | Wendet `f` auf jede `Row` an. |
| [`foreachPartition`](13%20Konvertierung%20und%20Iteration/09%20foreachPartition.md) | Methode | Wendet `f` auf jede Partition an. |
| [`plot`](13%20Konvertierung%20und%20Iteration/10%20plot.md) | Eigenschaft | `PySparkPlotAccessor` für Plot-Funktionen. |

## 14 Schreiben und Streaming

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`write`](14%20Schreiben%20und%20Streaming/01%20write.md) | Eigenschaft | `DataFrameWriter` für nicht-streamende DataFrames (→ [DataFrameWriter](../04%20DataFrameWriter/00%20Uebersicht.md)). |
| [`writeTo`](14%20Schreiben%20und%20Streaming/02%20writeTo.md) | Methode | Builder für die Schreibkonfiguration (v2-Quellen). |
| [`mergeInto`](14%20Schreiben%20und%20Streaming/03%20mergeInto.md) | Methode | MERGE von Updates, Inserts und Deletes in eine Zieltabelle. |
| [`writeStream`](14%20Schreiben%20und%20Streaming/04%20writeStream.md) | Eigenschaft | `DataStreamWriter` für Streaming-DataFrames (→ [DataStreamWriter](../05%20DataStreamWriter/00%20Uebersicht.md)). |
| [`isStreaming`](14%20Schreiben%20und%20Streaming/05%20isStreaming.md) | Eigenschaft | `True`, wenn der DataFrame kontinuierlich liefernde Quellen enthält. |
| [`withWatermark`](14%20Schreiben%20und%20Streaming/06%20withWatermark.md) | Methode | Definiert ein Event-Time-Watermark. |

## 15 Subqueries und Tabellenargumente

| Name | Art | Beschreibung |
| --- | --- | --- |
| [`scalar`](15%20Subqueries%20und%20Tabellenargumente/01%20scalar.md) | Methode | `Column` für eine SCALAR-Subquery (genau eine Zeile, eine Spalte). |
| [`exists`](15%20Subqueries%20und%20Tabellenargumente/02%20exists.md) | Methode | `Column` für eine EXISTS-Subquery. |
| [`asTable`](15%20Subqueries%20und%20Tabellenargumente/03%20asTable.md) | Methode | Wandelt den DataFrame in ein `TableArg` für TVFs/UDTFs um. |

## Beispiele

### Grundlegende DataFrame-Operationen

```python
# Create a DataFrame
people = spark.createDataFrame([
    {"deptId": 1, "age": 40, "name": "Alice", "gender": "M", "salary": 50},
    {"deptId": 1, "age": 50, "name": "Bob", "gender": "M", "salary": 100},
    {"deptId": 2, "age": 60, "name": "Sue", "gender": "F", "salary": 150},
    {"deptId": 3, "age": 20, "name": "Tom", "gender": "M", "salary": 200}
])

# Select columns
people.select("name", "age").show()

# Filter rows
people.filter(people.age > 30).show()

# Add a new column
people.withColumn("age_plus_10", people.age + 10).show()
```

### Aggregation und Gruppierung

```python
# Group by and aggregate
people.groupBy("gender").agg({"salary": "avg", "age": "max"}).show()

# Multiple aggregations
from pyspark.sql import functions as F
people.groupBy("deptId").agg(
    F.avg("salary").alias("avg_salary"),
    F.max("age").alias("max_age")
).show()
```

### Joins

```python
# Create another DataFrame
department = spark.createDataFrame([
    {"id": 1, "name": "PySpark"},
    {"id": 2, "name": "ML"},
    {"id": 3, "name": "Spark SQL"}
])

# Join DataFrames
people.join(department, people.deptId == department.id).show()
```

### Komplexe Transformationen

```python
# Chained operations
result = people.filter(people.age > 30) \
    .join(department, people.deptId == department.id) \
    .groupBy(department.name, "gender") \
    .agg({"salary": "avg", "age": "max"}) \
    .sort("max(age)")
result.show()
```

## Quellen

- DataFrame (Klassenreferenz): https://docs.databricks.com/aws/en/pyspark/reference/classes/dataframe

**Stand:** 2026-09-26, gegen die offizielle API-Referenz (docs.databricks.com) verifiziert.
