# 3_4_Serialization

Diese Lektion behandelt Performance-Probleme, die durch Serialisierung in Spark verursacht werden, sowie Techniken, um sie abzumildern.

**Performance-Probleme durch Serialisierung**

Serialisierung ist ein wichtiges Thema der Code-Optimierung, **besonders bei der Arbeit mit User-Defined Functions (UDFs)**. Serialisierung bezeichnet den Prozess, der erforderlich ist, wenn eine UDF erstellt wird - diese Funktion muss serialisiert und an jeden Executor im Cluster verteilt werden.

Während Spark-SQL- und DataFrame-Operationen hochgradig optimiert sind und von Sparks internen Effizienzen profitieren können, gilt dieses Optimierungsniveau nur, wenn diese Operationen direkt verwendet werden.

Wird eine benutzerdefinierte UDF geschrieben, muss diese serialisiert und an alle Executor verteilt werden, was zusätzlichen Aufwand in Bezug auf Zeit und Ressourcen bedeutet. Zusätzlich müssen die Parameter und Rückgabewerte jedes Aufrufs der UDF für jede an die Executor verteilte Datenzeile konvertiert werden, was die Rechenkosten weiter erhöht.
Python-UDFs sind in diesem Zusammenhang am wenigsten optimiert - Python-Code muss gepickled (in ein für Python geeignetes Format serialisiert) werden, und anschließend muss Spark in jedem Executor einen Python-Interpreter starten. Die Konvertierung jeder Zeile zwischen Python und dem DataFrame hin und her fügt eine weitere Schicht an Overhead hinzu, wodurch diese UDFs im Vergleich zu nativen Spark-SQL- oder DataFrame-Ausdrücken deutlich weniger effizient sind.

- Spark-SQL- und DataFrame-Anweisungen sind hochgradig optimiert
- Alle UDFs müssen serialisiert und an jeden Executor verteilt werden
- Die Parameter und der Rückgabewert jeder UDF müssen für jede Datenzeile konvertiert werden, bevor sie an die Executor verteilt werden
- Python-UDFs treffen es noch härter
  - Der Python-Code muss gepickled werden
  - Spark muss in jedem einzelnen Executor einen Python-Interpreter instanziieren
  - Die Konvertierung jeder Zeile von Python zum DataFrame kostet noch mehr

------

**Serialisierungsprobleme mildern**

- Der Catalyst Optimizer kann Code vor und nach der UDF nicht miteinander verbinden
- Die UDF ist eine Black Box, was bedeutet, dass sich Optimierungen auf den Code vor und nach der UDF beschränken, während die UDF selbst und das Zusammenspiel des gesamten Codes ausgeschlossen bleiben
- UDFs erzeugen für den Catalyst Optimizer eine Analysebarriere

- Verwenden Sie keine UDFs
  - Ich fordere Sie heraus, eine Reihe von Transformationen zu finden, die nicht mit den eingebauten, kontinuierlich optimierten, von der Community unterstützten Higher-Order Functions umgesetzt werden können
- Wenn Sie UDFs in Python verwenden müssen (üblich bei Data Scientists), nutzen Sie Vectorized UDFs anstelle der herkömmlichen Python UDFs oder die **Apache Arrow Optimised Python UDFs**
- Wenn Sie UDFs in Scala verwenden müssen, nutzen Sie Typed Transformations anstelle der herkömmlichen Scala UDFs
- Widerstehen Sie der Versuchung, UDFs zu verwenden, um Spark-Code mit bestehender Business-Logik zu integrieren - diese Logik nach Spark zu portieren, zahlt sich fast immer aus