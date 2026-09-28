# 3_3_Spill

Diese Lektion behandelt, was Spill in Spark ist, welche Arten und Beispiele es gibt und wie man es abmildern kann.

Spill beschreibt, **was passiert, wenn so viele Daten vorhanden sind, dass sie nicht alle in den RAM passen, sodass ein Teil davon auf die Festplatte ausgelagert werden muss.** Werden diese Daten später wieder benötigt, müssen sie von der Festplatte zurück in den RAM geladen werden. Diese Situation tritt auf, wenn das Datenvolumen die verfügbare, dem Cluster zugewiesene RAM-Kapazität übersteigt. Infolgedessen muss das System auf Disk Reads und Writes zurückgreifen, die deutlich langsamer sind, um RAM freizugeben und die Berechnungen fortsetzen zu können. Geschieht dies nicht und geht dem System der Speicher aus, kann dies zu einem Out-of-Memory-Fehler führen und den gesamten Job zum Scheitern bringen

- Spill ist der Begriff für das Verschieben von Daten aus dem RAM auf die Festplatte und später wieder zurück in den RAM
- Dies tritt auf, wenn eine bestimmte Partition schlicht zu groß ist, um in den RAM zu passen
- In diesem Fall ist Spark gezwungen, [potenziell] teure Disk Reads und Writes durchzuführen, um lokalen RAM freizugeben
- All das nur, um den gefürchteten OOM-Fehler zu vermeiden

------

**Spill - Beispiele**

Einige häufige Situationen, die einen Spill verursachen können

- Wenn max partition bytes zu hoch eingestellt wird, was zu **übergroßen Partitionen** führt, die nicht in den RAM passen und auf die Festplatte geschrieben werden müssen. **Der Standardwert beträgt 128 MB, aber eine Erhöhung kann leicht zu großen Partitionen pro Worker führen.**
- Eine weitere Ursache ist das **Explodieren selbst eines kleinen Arrays**, wodurch schnell mehr Daten entstehen können, als der verfügbare RAM bewältigen kann.
- Auch Joins - insbesondere **Cross Joins** - zwischen Tabellen können zu einer enormen Anzahl neuer Zeilen führen und dabei möglicherweise das Speicherlimit überschreiten.
- Probleme können auch durch **Joins auf skew-behafteten Keys** entstehen, wodurch **bestimmte Partitionen deutlich größer werden als andere**.
- **Group by auf Spalten mit niedriger Kardinalität**, die Verwendung von **count distinct**, **collect set** oder **zu niedrig eingestellte Shuffle Partitions** können ebenfalls Spills auslösen.
- Selbst die **falsche Verwendung von repartition** kann zu hohem Speicherbedarf führen.

Zusammenfassend kann alles, was das Datenvolumen über das hinaus erhöht, was der RAM Ihres Clusters bewältigen kann, zu einem Spill führen und damit zu langsameren, disk-basierten Berechnungen.

Einige häufige Situationen, die einen Spill verursachen können

- Wenn `spark.sql.files.maxPartitionBytes` zu hoch eingestellt ist (Standard ist 128 MB)
- Das `explode()` selbst eines kleinen Arrays
- Der `join()` oder `crossJoin()` zweier Tabellen, der viele neue Zeilen erzeugt
- Der `join()` oder `crossJoin()` zweier Tabellen über einen skew-behafteten Key
- Der `groupBy()`, bei dem die Spalte eine niedrige Kardinalität hat
- `countDistinct()` und `size(collect_set())`
- `spark.sql.shuffle.partitions` zu niedrig eingestellt oder falsche Verwendung von `repartition()`

------

**Spill - Memory & Disk**

Spill - In der Spark UI

- Spill wird nur auf der Detailseite einer einzelnen Stage dargestellt ...
  - Summary Metrics
  - Aggregated Metrics by Executor
  - Die Tasks-Tabelle
- Oder in den entsprechenden Query-Details
- Dadurch ist es schwer zu erkennen, da man danach suchen muss
- Wenn kein Spill vorliegt, erscheinen die entsprechenden Spalten in der Spark UI erst gar nicht - das bedeutet, wenn die Spalte vorhanden ist, gibt es irgendwo einen Spill

In der Spark UI wird Spill durch zwei Werte dargestellt:

- **Spill (Memory)**: Für die Partition, die gespillt wurde, ist dies die Größe dieser Daten, wie sie im Speicher vorlagen
- **Spill (Disk)**: Ebenso ist dies für die gespillte Partition die Größe der Daten, wie sie auf der Festplatte vorlagen

Die beiden Werte werden immer zusammen angezeigt

Die Größe auf der Festplatte ist stets kleiner, aufgrund der natürlichen Kompression, die durch die Serialisierung der Daten vor dem Schreiben auf die Festplatte entsteht

------

**Spill - Mitigations**

Um Spills zu vermeiden, besteht eine Möglichkeit darin, einen Cluster mit mehr RAM pro Core bereitzustellen, um einen größeren Speicherraum für die Verarbeitung der Daten zu schaffen. Auch die Behebung von Data Skew ist wichtig; wenn eine Partition deutlich größer ist als andere, kann eine Verkleinerung ihr helfen, leichter in den Speicher zu passen. Die Verwaltung der Größe von Spark-Partitionen ist ein weiterer wichtiger Ansatz, der in der Demo gezeigt wird. Das Vermeiden teurer Operationen wie explode, wo möglich, kann das Risiko von Spills verringern. Zusätzlich kann eine vorzeitige Reduzierung der Datenmenge - durch den Ausschluss unnötiger Spalten oder das Herausfiltern nicht benötigter Zeilen - dabei helfen, die Arbeitslast innerhalb des verfügbaren Speichers zu halten und Spills während der Verarbeitung zu verhindern.

- Cluster mit mehr RAM pro Core bereitstellen
- Data Skew beheben
- Größe der Spark-Partitionen verwalten
- Teure Operationen wie explode() vermeiden
- Datenmenge nach Möglichkeit vorzeitig reduzieren
