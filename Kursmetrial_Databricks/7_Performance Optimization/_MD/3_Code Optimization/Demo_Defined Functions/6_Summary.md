# 6_Zusammenfassung

Die tatsächlichen Zeiten hängen von einer Reihe von Faktoren ab, im Durchschnitt schneidet die SQL UDF jedoch besser ab als ihr Python-Äquivalent — oft sogar deutlich besser. Der Grund dafür ist, dass SQL UDFs die eingebauten APIs und Funktionen von Spark nutzen, anstatt sich auf externe Abhängigkeiten oder Python UDFs zu verlassen.

Wenn Sie eine UDF in Ihrem Spark-Job verwenden, führt die Umstellung Ihres Codes auf native Spark APIs oder Funktionen, wo immer möglich, zu den besten Performance- und Effizienzgewinnen.

Wenn Sie aufgrund starker Abhängigkeiten von externen Bibliotheken UDFs verwenden müssen, sollten Sie Ihren Code parallelisieren und Ihren DataFrame entsprechend der Anzahl der CPU-Cores in Ihrem Cluster repartitionieren, um das beste Maß an Parallelisierung zu erreichen.

Wenn Sie Python UDFs verwenden, sollten Sie stattdessen **Apache Arrow**-optimierte Python UDFs in Betracht ziehen, da sie die Effizienz des Datenaustauschs zwischen der Spark Runtime und dem UDF-Prozess verbessern. [Mehr über Arrow-optimierte Python UDFs erfahren](https://www.databricks.com/blog/arrow-optimized-python-udfs-apache-sparktm-35).