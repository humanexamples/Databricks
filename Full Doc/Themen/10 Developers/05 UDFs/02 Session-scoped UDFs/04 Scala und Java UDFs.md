# Session-scoped Scala- und Java-UDFs

Referenz zu session-scoped Scala-/Java-UDFs: inline Scala-UDFs in Notebooks, Java-UDFs aus einer JAR über `spark.udf.registerJavaFunction`, typisierte Dataset-APIs und die Kompatibilitätsmatrix nach Databricks-Runtime-Version.

## Abschnittsübersicht

1. [Den passenden Ansatz wählen](#ansatz)
2. [Voraussetzungen](#voraussetzungen)
3. [Eine Funktion als UDF registrieren](#registrieren)
4. [Die UDF in Spark SQL aufrufen](#sql-aufruf)
5. [UDF mit DataFrames verwenden](#dataframes)
6. [Dateien mit UDF (Beta)](#files)
7. [Eine Java-UDF aus einer JAR registrieren](#java-jar)
8. [Auswertungsreihenfolge und Null-Prüfung](#null-checking)
9. [Typisierte Dataset-APIs](#typed-apis)
10. [Scala-UDF-Feature-Kompatibilität nach Databricks-Runtime](#kompatibilitaet)
11. [Quellen](#quellen)

---

## <a id="ansatz">1. Den passenden Ansatz wählen</a>

| Ansatz | Beschreibung |
|---|---|
| **Inline Scala-UDF** | UDF direkt in einem Notebook als Scala-Funktion oder Lambda definieren. Session-scoped. Nicht unterstützt auf serverlosem Compute. |
| **Java-UDF aus einer JAR** | Eine vorkompilierte UDF-Klasse aus einer JAR über `spark.udf.registerJavaFunction` registrieren. Session-scoped. Unterstützt auf serverlosem Compute. |
| **Unity-Catalog-governed Scala- oder Java-UDF** | UDF in Unity Catalog registrieren für Governance, Wiederverwendung und Auffindbarkeit. Unterstützt auf serverlosem Compute. Siehe [Scala und Java UDFs (Unity Catalog)](../01%20Unity%20Catalog%20UDFs/02%20Scala%20und%20Java%20UDFs%20%28Unity%20Catalog%29.md). |

---

## <a id="voraussetzungen">2. Voraussetzungen</a>

- Scala-UDFs auf Unity-Catalog-fähigem Compute mit Standard Access Mode erfordern Databricks Runtime 14.2 oder höher.
- ARM-Instance-Support für Scala-UDFs auf Unity-Catalog-fähigen Clustern erfordert Databricks Runtime 15.2 oder höher.
- Die Registrierung einer Java-UDF aus einer JAR über `spark.udf.registerJavaFunction` erfordert Databricks Runtime 18 LTS oder höher (siehe [Eine Java-UDF aus einer JAR registrieren](#java-jar)).

Versions-Matching:

- **Klassisches Compute:** Scala- und Spark-Version der Databricks-Runtime-Version müssen übereinstimmen (siehe Abschnitt "System environment" der Databricks-Runtime-Release-Notes zu Versionen und Kompatibilität). Beispiel: Databricks Runtime 18 LTS verwendet Scala 2.13.16 und Apache Spark 4.0.
- **Serverloses Compute:** Scala-Version der Environment Version muss übereinstimmen (siehe Environment Versions).

---

## <a id="registrieren">3. Eine Funktion als UDF registrieren</a>


---

## <a id="sql-aufruf">4. Die UDF in Spark SQL aufrufen</a>


```sql
%sql select id, square(id) as id_squared from test
```

---

## <a id="dataframes">5. UDF mit DataFrames verwenden</a>


---

## <a id="files">6. Dateien mit UDF (Beta)</a>

Dieses Feature ist im **Beta**-Status. Workspace-Admins können den Zugriff über die Previews-Seite steuern.

Der Scala-Typ für eine Datei ist `FileRef`, verwendbar als Parameter- oder Rückgabetyp einer UDF, sowohl als Top-Level-Typ als auch verschachtelt.

Um den Inhalt einer Datei innerhalb einer UDF zu lesen, wird eine der folgenden Methoden auf einer `FileRef` aufgerufen:

- `asLocalFile()`: liefert eine `java.io.File`, die an jede Bibliothek übergeben werden kann, die einen Pfad akzeptiert.
- `open()`: liefert einen `java.io.InputStream` zum Lesen der Bytes der Datei. Der Aufrufer muss ihn schließen.

Um innerhalb einer UDF eine neue `FileRef` zu erzeugen, wird eine der folgenden statischen Methoden aufgerufen:

- `FileRef.create(uri)`: erstellt einen Verweis auf die Datei unter `uri`.
- `FileRef.fromBytes(bytes, destinationPath, contentType)`: lädt Bytes an den Volume-Pfad `destinationPath` als externe Datei hoch und gibt einen Verweis zurück.
- `FileRef.fromLocalFile(localFile, destinationPath, contentType)`: lädt eine lokale Datei an den Volume-Pfad `destinationPath` als externe Datei hoch und gibt einen Verweis zurück.

Eine `FileRef` aus einer UDF zurückzugeben, die in eine `FILE MANAGED`-Spalte schreibt, wird nicht unterstützt.

---

## <a id="java-jar">7. Eine Java-UDF aus einer JAR registrieren</a>

### Schritt 1: Projekt anlegen

Scala:

```bash
sbt new scala/scala-seed.g8
```



Java (Maven):

```bash
mvn archetype:generate \
  -DgroupId=com.example \
  -DartifactId=my-udf \
  -DarchetypeArtifactId=maven-archetype-quickstart \
  -DinteractiveMode=false
```

```xml
<properties>
  <maven.compiler.source>17</maven.compiler.source>
  <maven.compiler.target>17</maven.compiler.target>
  <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>

<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-shade-plugin</artifactId>
      <version>3.5.0</version>
      <executions>
        <execution>
          <phase>package</phase>
          <goals>
            <goal>shade</goal>
          </goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

### Schritt 2: Die UDF-Klasse schreiben

```java
package com.example;

import org.apache.spark.sql.api.java.UDF1;

public class MyIntegerUDF implements UDF1<Integer, Integer> {
  @Override
  public Integer call(Integer x) {
    return x + 1;
  }
}
```

### Schritt 3: Das Fat-JAR bauen

```bash
sbt clean assembly
```

```bash
mvn clean package
```

### Schritt 4: Die JAR in ein Unity-Catalog-Volume hochladen

```sql
CREATE VOLUME IF NOT EXISTS my_catalog.my_schema.udf_jars
COMMENT 'Storage for UDF JAR files';
```

1. Im Databricks-Workspace auf **Catalog** klicken, um den Catalog Explorer zu öffnen.
2. Katalog, dann Schema mit dem Volume auswählen.
3. Auf den Volume-Namen klicken.
4. **Upload to this volume** klicken und die JAR-Datei auswählen.
5. **Upload** klicken.
6. Nach dem Upload auf den Namen der JAR-Datei klicken, dann **Copy path** klicken, um den Volume-Pfad zu kopieren, z. B. `/Volumes/my_catalog/my_schema/udf_jars/my-udf-assembly-0.1.0-SNAPSHOT.jar`. Dieser Pfad wird im nächsten Schritt benötigt.

### Schritt 5: Die UDF registrieren und aufrufen

```python
# Add the JAR containing your UDF class to the session
spark.addArtifact("/Volumes/my_catalog/my_schema/udf_jars/my-udf-assembly-0.1.0-SNAPSHOT.jar")

# Register the UDF class, providing the SQL function name,
# the fully qualified class name, and the return type
from pyspark.sql.types import IntegerType

spark.udf.registerJavaFunction(
    "my_udf",
    "com.example.MyIntegerUDF",
    IntegerType(),
)

# Call the UDF from Spark SQL
spark.sql("SELECT my_udf(21)").show()
```

```text
+----------+
| my_udf(21)|
+----------+
|        22|
+----------+
```

---

## <a id="null-checking">8. Auswertungsreihenfolge und Null-Prüfung</a>

Spark SQL garantiert nicht, in welcher Reihenfolge Subexpressions ausgewertet werden:


Zwei Lösungswege:

- Die UDF selbst null-aware machen und die Null-Prüfung innerhalb der UDF durchführen.
- `IF`- oder `CASE WHEN`-Ausdrücke verwenden, um die Null-Prüfung durchzuführen und die UDF in einem bedingten Zweig aufzurufen.


---

## <a id="typed-apis">9. Typisierte Dataset-APIs</a>

**Hinweis:** Dieses Feature wird auf Unity-Catalog-fähigen Clustern mit Standard Access Mode ab Databricks Runtime 15.4 unterstützt.

Typisierte Dataset-APIs erlauben es, Transformationen wie `map`, `filter` und Aggregationen auf Datasets mit einer benutzerdefinierten Funktion auszuführen. Das folgende Beispiel nutzt die `map()`-API, um eine Zahl in einer Ergebnisspalte in einen mit Präfix versehenen String umzuwandeln:


Dieses Beispiel nutzt `map()`, dasselbe Muster gilt aber auch für andere typisierte Dataset-APIs wie `filter()`, `mapPartitions()`, `foreach()`, `foreachPartition()`, `reduce()` und `flatMap()`.

---

## <a id="kompatibilitaet">10. Scala-UDF-Feature-Kompatibilität nach Databricks-Runtime</a>

| Feature | Minimale Databricks-Runtime-Version |
|---|---|
| Scalar UDFs | Databricks Runtime 14.2 |
| `Dataset.map`, `Dataset.mapPartitions`, `Dataset.filter`, `Dataset.reduce`, `Dataset.flatMap` | Databricks Runtime 15.4 |
| `KeyValueGroupedDataset.flatMapGroups`, `KeyValueGroupedDataset.mapGroups` | Databricks Runtime 15.4 |
| (Streaming) `foreachWriter` Sink | Databricks Runtime 15.4 |
| (Streaming) `foreachBatch` | Databricks Runtime 16.1 |
| (Streaming) `KeyValueGroupedDataset.flatMapGroupsWithState` | Databricks Runtime 16.2 |
| `spark.udf.registerJavaFunction` (Java-UDF aus einer JAR) | Databricks Runtime 18 LTS |

---

## <a id="quellen">11. Quellen</a>

- Session-scoped Scala and Java UDFs: https://docs.databricks.com/aws/en/udf/scala

**Stand:** 2026-08-22.
