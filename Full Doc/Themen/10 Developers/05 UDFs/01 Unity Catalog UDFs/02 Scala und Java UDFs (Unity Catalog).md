# Scala und Java UDFs in Unity Catalog

Referenz zu governed Scala-/Java-UDFs in Unity Catalog: JAR-Build lokal oder im Notebook, Registrierung, Aufruf, Governance, Performance-Optimierung und lokales Testen.

## Abschnittsübersicht

1. [Eigenschaften](#eigenschaften)
2. [Voraussetzungen](#voraussetzungen)
3. [Die UDF-JAR bauen](#bauen)
4. [Im Notebook bauen](#notebook-bauen)
5. [Die UDF in Unity Catalog registrieren](#registrieren)
6. [Die UDF in SQL und Notebooks aufrufen](#aufrufen)
7. [Governance und Sharing](#governance)
8. [Die UDF aktualisieren](#aktualisieren)
9. [Performance-Optimierung](#performance)
10. [Limitierungen](#limitierungen)
11. [Best Practices](#best-practices)
12. [UDFs lokal testen](#testen)
13. [Weiterführende Ressourcen](#weiterfuehrend)

---

## <a id="eigenschaften">1. Eigenschaften</a>

Scala-/Java-UDFs in Unity Catalog sind:

- **Governed:** verwaltet über Unity-Catalog-Berechtigungen und Zugriffskontrollen.
- **Reusable:** teamübergreifend, notebook-, job- und SQL-Warehouse-übergreifend nutzbar.
- **Discoverable:** sichtbar in Catalog Explorer und System Tables.
- **Isolated:** laufen in Sandboxes mit einmaligen Cold-Start-Kosten pro Session — nachfolgende Aufrufe sind schnell.

---

## <a id="voraussetzungen">2. Voraussetzungen</a>

- **Scala:** 2.13.16. Scala 2.12 wird nicht unterstützt.
- **JDK:** 17.
- **Packaging:** ein Fat-JAR, das alle von der UDF verwendeten Drittanbieter-Abhängigkeiten enthält.

Berechtigungen:

- **UDF erstellen:** `USAGE` und `CREATE FUNCTION` auf dem Schema, sowie `USAGE` auf dem Katalog.
- **UDF ausführen:** `EXECUTE` auf der Funktion sowie `USAGE` auf Schema und Katalog.
- **Zugriff auf die JAR-Datei:** `READ VOLUME` auf dem Volume, in dem die JAR gespeichert ist.

---

## <a id="bauen">3. Die UDF-JAR bauen</a>

Zwei Wege stehen zur Wahl: **lokal bauen** oder **im Notebook bauen**.

### Umgebung einrichten (lokal)

Scala (sbt):

```bash
brew install openjdk@17
brew install sbt
```

```bash
java -version   # Should show Java 17
sbt --version   # Should show sbt version
```

Java (Maven):

```bash
brew install openjdk@17
brew install maven
```

```bash
java -version   # Should show Java 17
mvn --version   # Should show Maven version
```

### Projekt anlegen

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
```

```xml
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

### Die UDF schreiben

- **Scala:** Der Handler wird als Methode auf einem `object` (nicht einer `class`) definiert. Der `HANDLER`-Wert löst zu einer Methode auf einem Scala-`object` auf.
- **Java:** Der Handler wird als `public static`-Methode definiert.
- **Signatur:** Parametertypen, -reihenfolge und Rückgabetyp der Methode müssen der Argumentliste und dem `RETURNS`-Typ der `CREATE FUNCTION`-Anweisung entsprechen.
- **Nur skalar:** Der Handler muss genau einen skalaren Wert zurückgeben. Tabellen-Rückgabetypen werden nicht unterstützt.
- **Self-contained:** Der Handler darf nur mit seinen Eingabeargumenten arbeiten. Er kann keine Spark-APIs verwenden oder von Spark-Core-Paketen abhängen (siehe [Limitierungen](#limitierungen)).

Einfaches Beispiel, Scala:


Komplexeres Beispiel mit Drittanbieter-Abhängigkeit (Scala):



Einfaches Beispiel, Java:

```java
package com.example;

public class MyUDF {
    public static int addOne(int x) {
        return x + 1;
    }
}
```

Komplexeres Beispiel mit Drittanbieter-Abhängigkeit (Java):

```xml
<dependencies>
    <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-lang3</artifactId>
        <version>3.12.0</version>
    </dependency>
</dependencies>
```

```java
package com.example;

import org.apache.commons.lang3.StringUtils;
import java.util.Map;
import java.util.HashMap;

public class CurrencyUDF {
    private static final Map<String, Double> rates = new HashMap<>();

    static {
        rates.put("USD", 1.0);
        rates.put("EUR", 1.1);
        rates.put("GBP", 1.3);
        rates.put("JPY", 0.007);
    }

    public static double convertToUSD(double price, String currency) {
        if (currency == null) {
            throw new IllegalArgumentException("Currency must not be null");
        }

        String normalizedCurrency = StringUtils.upperCase(currency);

        if (!rates.containsKey(normalizedCurrency)) {
            throw new IllegalArgumentException("Unsupported currency: " + currency);
        }

        return price * rates.get(normalizedCurrency);
    }
}
```

### Das Fat-JAR bauen

```bash
sbt clean assembly
```

```bash
mvn clean package
```

### Die JAR in ein Unity-Catalog-Volume hochladen

```sql
CREATE VOLUME IF NOT EXISTS my_catalog.my_schema.udf_jars
COMMENT 'Storage for UDF JAR files';
```

```sql
GRANT READ VOLUME ON VOLUME my_catalog.my_schema.udf_jars TO `user@example.com`;
```

1. Im Databricks-Workspace auf **Catalog** klicken, um den Catalog Explorer zu öffnen.
2. Katalog, dann Schema mit dem Volume auswählen.
3. Auf den Volume-Namen klicken.
4. **Upload to this volume** klicken und die JAR-Datei auswählen.
5. **Upload** klicken.
6. Nach dem Upload auf den Namen der JAR-Datei klicken.
7. **Copy path** klicken, um den Volume-Pfad in die Zwischenablage zu kopieren, z. B. `/Volumes/my_catalog/my_schema/udf_jars/my-udf-assembly-0.1.0-SNAPSHOT.jar` (Scala) oder `/Volumes/my_catalog/my_schema/udf_jars/my-udf-1.0-SNAPSHOT.jar` (Java). Dieser Pfad wird bei der Registrierung der UDF benötigt.

---

## <a id="notebook-bauen">4. Im Notebook bauen</a>

Alternative zum lokalen Build: JDK-Kompilierung, JAR-Packaging und Upload direkt aus einem Python-Notebook heraus, z. B. für einfache Java-Handler ohne externe Build-Toolchain:

```python
import os
import subprocess
import shutil

build_dir = "/tmp/udf_build"
package_dir = f"{build_dir}/src/com/databricks/udf"
classes_dir = f"{build_dir}/classes"
os.makedirs(package_dir, exist_ok=True)
os.makedirs(classes_dir, exist_ok=True)

# The UDF handler: a public static method on a plain Java class.
# The doubled backslashes produce a single backslash in the Java source (\\s+).
udf_code = """package com.databricks.udf;
public class StringCleanUDF {
    public static String clean(String input) {
        if (input == null) return null;
        return input.trim().replaceAll("\\\\s+", " ").toLowerCase();
    }
}
"""
with open(f"{package_dir}/StringCleanUDF.java", "w") as f:
    f.write(udf_code)

# Compile with JDK 17 to match Environment Version 4.
subprocess.run(
    ["javac", "--release", "17", "-d", classes_dir, f"{package_dir}/StringCleanUDF.java"],
    check=True,
)

# Package the compiled class into a JAR.
jar_path = f"{build_dir}/string_clean_udf.jar"
subprocess.run(["jar", "cf", jar_path, "-C", classes_dir, "."], check=True)

# Copy the JAR to a Unity Catalog volume.
volume_path = "/Volumes/my_catalog/my_schema/udf_jars/string_clean_udf.jar"
os.makedirs(os.path.dirname(volume_path), exist_ok=True)
shutil.copy2(jar_path, volume_path)

print(f"JAR uploaded to: {volume_path}")
```

---

## <a id="registrieren">5. Die UDF in Unity Catalog registrieren</a>

Scala:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.add_one(x INT)
RETURNS INT
LANGUAGE SCALA
DETERMINISTIC
ENVIRONMENT (
  java_dependencies = '["/Volumes/my_catalog/my_schema/udf_jars/my-udf-assembly-0.1.0-SNAPSHOT.jar"]',
  environment_version = '4'
)
HANDLER 'com.example.MyUDF.addOne';
```

Java:

```sql
CREATE OR REPLACE FUNCTION my_catalog.my_schema.add_one(x INT)
RETURNS INT
LANGUAGE JAVA
DETERMINISTIC
ENVIRONMENT (
  java_dependencies = '["/Volumes/my_catalog/my_schema/udf_jars/my-udf-1.0-SNAPSHOT.jar"]',
  environment_version = '4'
)
HANDLER 'com.example.MyUDF.addOne';
```

---

## <a id="aufrufen">6. Die UDF in SQL und Notebooks aufrufen</a>

```sql
-- Simple select
SELECT my_catalog.my_schema.add_one(5) AS result;

-- With table data
SELECT
  id,
  price,
  currency,
  my_catalog.my_schema.convert_to_usd(price, currency) AS price_usd
FROM my_catalog.my_schema.transactions;

-- Filtering
SELECT *
FROM my_catalog.my_schema.products
WHERE my_catalog.my_schema.convert_to_usd(price, currency) > 100;

-- Aggregation
SELECT
  category,
  SUM(my_catalog.my_schema.convert_to_usd(price, currency)) AS total_usd
FROM my_catalog.my_schema.sales
GROUP BY category;
```

---

## <a id="governance">7. Governance und Sharing</a>

### Berechtigungen erteilen

Über Catalog Explorer:

1. In der Seitenleiste auf **Catalog** klicken.
2. Katalog, dann Schema mit der Funktion auswählen.
3. Auf den Funktionsnamen klicken.
4. Im Tab **Permissions** auf **Grant** klicken.
5. Prinzipale auswählen und die Berechtigung `EXECUTE` zuweisen.
6. **Confirm** klicken.

Über SQL:

```sql
-- Grant to a specific user
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.add_one TO `user@example.com`;

-- Grant to a group
GRANT EXECUTE ON FUNCTION my_catalog.my_schema.add_one TO `data-engineers`;
```

### Berechtigungen entziehen

1. In der Seitenleiste auf **Catalog** klicken.
2. Katalog, dann Schema mit der Funktion auswählen.
3. Auf den Funktionsnamen klicken.
4. Im Tab **Permissions** die Checkbox neben dem betroffenen Prinzipal auswählen. **Revoke** klicken.
5. In der Benachrichtigung erneut **Revoke** klicken.

```sql
-- Revoke from specific user
REVOKE EXECUTE ON FUNCTION my_catalog.my_schema.add_one FROM `user@example.com`;

-- Revoke from a group
REVOKE EXECUTE ON FUNCTION my_catalog.my_schema.add_one FROM `data-engineers`;
```

### UDFs auffinden

```sql
SELECT
  routine_catalog,
  routine_schema,
  routine_name,
  routine_definition,
  created
FROM system.information_schema.routines
WHERE routine_catalog = 'my_catalog'
  AND routine_schema = 'my_schema';
```

---

## <a id="aktualisieren">8. Die UDF aktualisieren</a>

1. Code lokal ändern.
2. Die JAR mit neuer Versionsnummer neu bauen. Scala: `sbt clean assembly` (z. B. `my-udf-assembly-0.2.0-SNAPSHOT.jar`); Java: `mvn clean package` (z. B. `my-udf-2.0-SNAPSHOT.jar`).
3. Die neue JAR in das Unity-Catalog-Volume hochladen.
4. Mit `CREATE OR REPLACE FUNCTION` unter demselben Funktionsnamen die UDF aktualisieren. Sicherstellen, dass in `java_dependencies` auf die neueste JAR verwiesen wird.

---

## <a id="performance">9. Performance-Optimierung</a>

### Cold-Start-Latenz

Der erste UDF-Aufruf in einer Session initialisiert die isolierte Sandbox, was zusätzliche Latenz verursacht. Nachfolgende Aufrufe in derselben Session sind schneller. Dies sollte bei Benchmarks oder beim Design latenzsensitiver Workloads berücksichtigt werden.

### Teure Berechnungen cachen

Scala:


Java:

```java
package example;

import java.util.Map;
import java.util.HashMap;

public class CachedUDF {
    // Computed once and cached
    private static Map<String, Double> expensiveData;

    static {
        // Load data from somewhere expensive
        expensiveData = new HashMap<>();
        expensiveData.put("key1", 1.0);
        expensiveData.put("key2", 2.0);
    }

    public static double lookup(String key) {
        return expensiveData.getOrDefault(key, 0.0);
    }
}
```

### `DETERMINISTIC` nutzen, wenn angebracht

Eine UDF sollte als `DETERMINISTIC` markiert werden, wenn sie für dieselbe Eingabe immer dieselbe Ausgabe liefert. Das erlaubt dem Query-Optimizer, Ergebnisse zu cachen und die Performance zu verbessern.

---

## <a id="limitierungen">10. Limitierungen</a>

- Es werden nur skalare UDFs unterstützt. User-Defined Aggregate Functions (UDAFs) und User-Defined Table Functions (UDTFs) werden nicht unterstützt.
- UDFs laufen in einer isolierten Sandbox ohne aktive Spark-Session. Spark-APIs (`SparkSession`, `SparkContext`, `spark.sql(...)`, `DataFrame`- und `Dataset`-Operationen) stehen nicht zur Verfügung.
- UDFs können nicht von Spark-Core-Paketen abhängen.
- UDFs haben zur Laufzeit keinen Zugriff auf Workspace-Dateien oder Unity-Catalog-Volumes.

---

## <a id="best-practices">11. Best Practices</a>

- JAR-Dateien versionieren, z. B. `my-udf-0.1.0.jar`, `my-udf-0.2.0.jar`.
- SQL-Typ-Mappings vor dem Deployment validieren (siehe Language Mappings).
- `READ VOLUME`- und `EXECUTE`-Berechtigungen nur an Nutzer vergeben, die die UDF tatsächlich ausführen müssen. Für teamübergreifend genutzte UDFs Gruppen-Ownership verwenden.

---

## <a id="testen">12. UDFs lokal testen</a>

Scala (ScalaTest):



```bash
sbt test
```

Java (JUnit 5):

```java
package com.example;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class MyUDFTest {
    @Test
    public void testAddOne() {
        assertEquals(6, MyUDF.addOne(5));
    }

    @Test
    public void testAddOneWithNegativeNumbers() {
        assertEquals(0, MyUDF.addOne(-1));
    }
}
```

```xml
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.10.0</version>
    <scope>test</scope>
</dependency>
```

```bash
mvn test
```

---

## <a id="weiterfuehrend">13. Weiterführende Ressourcen</a>

- Session-scoped Scala and Java UDFs (siehe [Scala und Java UDFs (Session-scoped)](../02%20Session-scoped%20UDFs/04%20Scala%20und%20Java%20UDFs.md))
- SQL and Python user-defined functions (UDFs) in Unity Catalog (siehe [SQL und Python UDFs (Unity Catalog)](01%20SQL%20und%20Python%20UDFs%20%28Unity%20Catalog%29.md))
- What are user-defined functions (UDFs)? (siehe [00 Overview.md](../00%20Overview.md))
