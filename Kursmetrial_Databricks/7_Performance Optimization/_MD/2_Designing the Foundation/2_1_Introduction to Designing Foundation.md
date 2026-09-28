## 2_1_Einführung in das Design der Grundlagen

In dieser Lektion behandeln wir grundlegende Konzepte zur Gestaltung einer Foundation, häufige Performance-Engpässe und Strategien zur Vermeidung des Small-File-Problems.

**Grundlegende Konzepte**

Anzahl gelesener Bytes

- Je mehr Daten gelesen werden müssen, um eine Query zu beantworten, desto länger dauert die Query. Die Daten werden **von einer Festplatte gelesen, über das Netzwerk übertragen usw.** Wenn Sie also auf viele Daten zugreifen müssen, um eine Query zu beantworten, wird dies wahrscheinlich **einige Zeit oder Rechenleistung kosten**.

Query-Komplexität / Berechnung

- **Je komplexer** die Query, die Berechnung oder die erforderlichen Aggregationen und Joins sind, **desto länger dauert die Query**.

Anzahl der zugegriffenen Dateien

- Je mehr Dateien eine Query aufrufen muss, desto langsamer ist die Query. Jeder Dateizugriff bringt einen gewissen Overhead mit sich, und wenn die Datenbank auf viele Dateien zugreifen muss, verbringt sie unter Umständen mehr Zeit mit dem **Overhead des Öffnens und Schließens von Dateien** als mit der eigentlichen Datenverarbeitung. Dieses Prinzip gilt insbesondere für Datenbanken, die ihre Daten über mehrere Dateien verteilt speichern, wie Databricks, aber auch andere Datenbanken haben oft ein Äquivalent (Dateisystem-Blöcke usw.).

Parallelismus

- In MPP-Systemen (Massively Parallel Processing) wie Databricks ist die Fähigkeit, Berechnungen parallel auszuführen, wichtig, um die Ausführungszeit einer Query zu verringern.

Warum manche Schemas und Queries schneller laufen als andere

- Anzahl gelesener Bytes
- Query-Komplexität/Berechnung
- Anzahl der zugegriffenen Dateien
- Parallelismus

------

**Häufige Performance-Engpässe**

- **1. Small-File-Problem**: Wenn Daten über viele winzige Dateien verteilt sind, verlangsamt das Öffnen und Übertragen dieser Dateien über das Netzwerk die Queries und kann sogar das I/O-Throttling des Cloud-Anbieters auslösen. Die Lösung ist die Verwendung von **Auto Optimize**.
  - **Optimize Write**: Diese Komponente arbeitet dynamisch innerhalb desselben Spark-Jobs und passt die Größe der Apache-Spark-Partitionen basierend auf den tatsächlichen Daten an. Ziel ist es, für jede Tabellenpartition 128 MB große Dateien zu erzeugen. Dieser Ansatz löst nicht nur das „Small-File-Problem“, sondern optimiert auch die Verteilung der Daten innerhalb des Spark-Jobs.
  - **Auto Compact**: Nach Abschluss des Spark-Jobs treibt Auto Compact die Optimierung noch weiter voran. Dabei wird ein neuer Job gestartet, der prüft, ob eine zusätzliche Komprimierung der Dateien möglich ist, mit dem Ziel, eine einheitliche Dateigröße von 128 MB zu erreichen. Dieser nachgelagerte Verarbeitungsschritt stellt sicher, dass die Daten effizient organisiert und kompakt bleiben.
  - Die Verwendung von Auto Optimize zusammen mit einer intelligenten Partitionsverwaltung hilft dabei, große dateibasierte Datenmengen effizient zu verarbeiten und gleichzeitig das „Small-File-Problem“ zu vermeiden
  - Automatische Vermeidung des Small-File-Problems zur Bewältigung dieser häufigen Performance-Herausforderung in Data Lakes

- Zu viele kleine Dateien erhöhen den Overhead beim Lesen erheblich
- Zu wenige große Dateien verringern den Parallelismus beim Lesen
- Over-Partitioning ist ein häufiges Problem
- Databricks passt **die Größe von Delta-Lake-Tabellen automatisch an**
- Databricks komprimiert kleine Dateien beim Schreiben automatisch mit **Auto-Optimize**

- **2. Data Skew**: wenn eine Partition deutlich größer ist als andere oder wenn Transformationen ein Ungleichgewicht erzeugen. Da die Verarbeitung auf den langsamsten Executor wartet, kann eine einzelne große Partition den gesamten Job verzögern.

- **3. Verarbeitung von mehr Daten als nötig**: Im Gegensatz zu traditionellen Data Lakes, die häufig komplette Datensätze neu schreiben, können wir nur die benötigten Dateien verarbeiten und mit **Techniken wie Data Skipping** die Performance weiter verbessern.

![image-20260710215158788](../../../../assets/image-20260710215158788.png)

------

In dieser Lektion werden wir Folgendes untersuchen:

- Data Skipping,
- Z-Ordering,
- Herausforderungen beim Partitioning,
- und wie Liquid Clustering mit Predictive Optimization die Query-Performance in Databricks Delta Lake verbessert.
