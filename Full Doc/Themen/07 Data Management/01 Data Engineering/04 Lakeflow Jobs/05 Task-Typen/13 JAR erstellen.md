# Eine Databricks-kompatible JAR erstellen

## Kernanforderungen

1. **Versionsabgleich:** dieselben JDK-, Scala- und Spark-Versionen wie das Compute verwenden.
2. **Abhängigkeitsverwaltung:** benötigte Bibliotheken in der JAR bündeln oder auf dem Compute installieren.
3. **Spark-Session-Nutzung:** `SparkSession.builder().getOrCreate()` zum Zugriff auf die Session aufrufen.
4. **Allowlist-Konfiguration:** Standard Compute erfordert das Hinzufügen der JAR zur Allowlist.

## Architekturunterschiede

Serverless und Standard Compute nutzen die Spark-Connect-Architektur (Isolation, Governance, kein direkter Spark-Context-/RDD-Zugriff). Dedicated Compute nutzt die klassische Spark-Architektur mit vollem API-Zugriff.

## Versionen ermitteln

- **Serverless:** Tabellen zu Serverless Environment Version 4+.
- **Standard/Dedicated:** Abschnitt „System Environment" der Databricks-Runtime-Release-Notes.

## Beispiel-Build-Konfiguration (Databricks Runtime 17.3 LTS)

- Scala-Version: 2.13.16
- JDK: 17
- Maven-Compiler-Source/Target: 17

## Abhängigkeiten

Empfohlen: Databricks Connect mit `provided`-Scope nutzen, um Spark nicht mit einzupacken. Laufzeit-bereitgestellte Bibliotheken als `provided` markieren; Anwendungsabhängigkeiten mit sbt-assembly oder Maven Shade Plugin bündeln.

## Erforderliche Code-Muster

Spark-Session über `SparkSession.builder().getOrCreate()` abrufen. Für Aufräumarbeiten `try`-`finally`-Blöcke statt Shutdown Hooks nutzen, da Databricks Container-Lebenszeiten verwaltet und Hooks ggf. nicht ausgeführt werden.

## Serverless-Logging

SLF4J-Logging über die `log4j-slf4j2-impl`-Bridge konfigurieren (passend zur Log4j-Version der Serverless-Umgebung) — entweder in der Fat JAR oder als separate Abhängigkeit.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/jar-create
