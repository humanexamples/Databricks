# Tutorial: JARs auf Serverless Compute erstellen und ausführen

**Empfehlung:** Statt JARs manuell zu bauen, Declarative Automation Bundles nutzen — vereinfacht die Projekterstellung mit vorkonfigurierten Scala-, JDK- und Databricks-Connect-Versionen.

## Voraussetzungen

- sbt 1.11.7+ (Scala) bzw. Maven 3.9.0+ (Java).
- JDK-, Scala- und Databricks-Connect-Versionen passend zur Serverless-Umgebung.

**Abhängigkeitsversionen für Serverless Environment 4:** Scala-2.13-Kompilierung, JDK 17 (Class File Version 61), Databricks Connect 17.3, nur öffentliche Spark-APIs (keine RDDs/Internals).

## Einschränkungen

Serverless Compute nutzt Spark Connect — die JAR läuft gegen eine schlanke Client-Bibliothek mit den öffentlichen Spark-APIs, während die Spark-Engine serverseitig läuft. **Nicht verfügbar:** RDD-API und SparkContext/JavaSparkContext, Spark-interne APIs (catalyst, util, sql/util, sql/internal), native Bibliotheken (.so, .dll, JNI).

## Schritt 1: JAR bauen

**Java:** Maven-Projektstruktur → `pom.xml` mit Maven Shade Plugin → Main-Class anlegen → `mvn clean package`.

```java
package com.examples;
import org.apache.spark.sql.SparkSession;
import java.util.stream.Collectors;

public class SparkJar {
  public static void main(String[] args) {
    SparkSession spark = SparkSession.builder().getOrCreate();
    System.out.println(String.join(", ", args));
    System.out.println(spark.version());
    System.out.println(
      spark.range(10).limit(3).collectAsList().stream()
        .map(Object::toString)
        .collect(Collectors.joining(" "))
    );
  }
}
```

## Abhängigkeiten verwalten

Drei Strategien: (1) mitgelieferte Bibliotheken nutzen (Serverless enthält Databricks Connect und gängige Libraries), (2) als Environment Library hinzufügen, falls nicht vorhanden, (3) für externe Datenbanken JDBC-Connections statt eingebetteter Treiber nutzen.

**Mitgelieferte Bibliotheken (Environment 4, Auswahl):** `databricks-connect_2.13` (17.3.2), `scala-library_2.13` (2.13.16), `slf4j-api` (2.0.10), `log4j-core` (2.20.0), `jackson-databind` (2.15.2), `guava` (32.0.1-jre), `databricks-sdk-java` (0.52.0), u. a.

## Schritt 2: Job zum Ausführen erstellen

1. **Jobs & Pipelines** → **Create** → **Job**.
2. Kachel **JAR**.
3. Job- und Task-Namen vergeben.
4. **Main class**: `com.examples.SparkJar`.
5. Compute: **Serverless**.
6. Serverless-Environment konfigurieren (Version 4+).
7. JAR-Datei per Drag & Drop oder Dateibrowser hochladen.
8. Parameter hinzufügen (Beispiel: `["Hello", "World!"]`).
9. **Save task**.

## Schritt 3: Ausführen und prüfen

**Run Now** → Ausgabe erscheint im **Output**-Panel.

## Fehlerbehebung

| Fehler | Ursache | Lösung |
|---|---|---|
| `NoSuchMethodError` (scala.*) | mit Scala 2.12 kompiliert, Serverless nutzt 2.13 | mit `scalaVersion := "2.13.16"` neu kompilieren |
| `NoClassDefFoundError: scala/...` | Scala-2.12-/2.13-Konflikt | 2.13.16 mit `_2.13`-Suffix für Abhängigkeiten |
| `UnsupportedClassVersionError` | mit JDK 18+ kompiliert, Serverless nutzt JDK 17 | `--release 17` verwenden |
| `NoClassDefFoundError` (org/apache/spark/...) | Spark-Internals/RDD-API genutzt | nur öffentliche Spark-API nutzen |
| `ClassNotFoundException` (JDBC-Treiber) | Treiber nicht im Classpath | JDBC-Connection nutzen |
| `ClassNotFoundException` (Drittanbieter) | Bibliothek nicht im Serverless-Classpath | zur JAR/Environment hinzufügen |
| `UnsatisfiedLinkError` | native Bibliothek in der JAR | reines-Java-Äquivalent oder Classic Compute nutzen |
| `NoSuchMethodError` (Drittanbieter) | Versionskonflikt mit mitgelieferten Bibliotheken | mitgelieferte Version nutzen, als „provided" markieren |

## Quelle

- https://docs.databricks.com/aws/en/jobs/how-to/use-jars-in-workflows
