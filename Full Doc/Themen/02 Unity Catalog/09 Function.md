## Function

Innerhalb eines [Schemas](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#schema) ist eine **Function** ein sicherbares Objekt in Unity Catalog, das wiederverwendbare, ausführbare Logik repräsentiert. Functions umfassen benutzerdefinierte Funktionen (UDFs), Stored Procedures und registrierte Modelle (in Unity Catalog registrierte MLflow-Modelle).

- **Benutzerdefinierte Funktionen (UDFs)** sind benutzerdefinierte Funktionen in SQL oder Python, die in SQL-Abfragen und Notebooks aufgerufen werden können. Siehe [Was sind benutzerdefinierte Funktionen (UDFs)?](https://docs.databricks.com/aws/en/udf/).
- **Stored Procedures** sind benutzerdefinierte Routinen, die eine Abfolge von SQL-Anweisungen ausführen und Seiteneffekte wie das Einfügen oder Aktualisieren von Daten enthalten können.
- **Registrierte Modelle** sind in Unity Catalog registrierte MLflow-Machine-Learning-Modelle. In Unity Catalog sind registrierte Modelle als eine Art von Function implementiert. Siehe [Modell-Lebenszyklus in Unity Catalog verwalten](https://docs.databricks.com/aws/en/machine-learning/manage-model-lifecycle/).

Die folgende Tabelle fasst wichtige Details zu Functions zusammen:

| Detail | Beschreibung |
| :---------------------- | :----------------------------------------------------------- |
| Nutzungsprivilegien | Um eine Function auszuführen oder ein registriertes Modell zu laden, benötigt ein Nutzer `USE CATALOG` auf dem übergeordneten Katalog und `USE SCHEMA` auf dem übergeordneten Schema ([Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges)), zusätzlich zu `EXECUTE` auf der Function. |
| Das `EXECUTE`-Privileg | Wird einem Nutzer `EXECUTE` auf einer Function gewährt, kann er die Function aufrufen sowie ihre Definition und Metadaten einsehen. Bei registrierten Modellen erlaubt `EXECUTE` zusätzlich, Metadaten aller Modellversionen einzusehen und Modelldateien herunterzuladen. |
| Vererbung | Auf Schema- oder Katalog-Ebene vergebenes `EXECUTE` gilt für alle aktuellen und künftigen Functions in diesem Schema bzw. Katalog. Siehe [Privilegienvererbung](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#inheritance). |

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### CREATE FUNCTION (SQL User-Defined Function)

Legt eine benutzerdefinierte SQL-Skalarfunktion oder Tabellenfunktion an, die `RETURN`-Ausdruck oder -Abfrage kann dabei auch andere UDFs referenzieren.

```sql
-- Einfache Skalarfunktion
CREATE FUNCTION area(x DOUBLE, y DOUBLE) RETURNS DOUBLE RETURN x * y;
SELECT area(3, 4);

-- Funktion mit DEFAULT-Parametern
CREATE FUNCTION roll_dice(num_dice INT DEFAULT 1, num_sides INT DEFAULT 6)
    RETURNS INT
    NOT DETERMINISTIC
    CONTAINS SQL
    COMMENT 'Roll a number of n-sided dice'
    RETURN (rand() * num_sides)::INT + 1;

-- Tabellenfunktion, die eine Ergebnismenge zurückgibt
CREATE FUNCTION weekdays(start DATE, end DATE)
    RETURNS TABLE(day_of_week STRING, day DATE)
    RETURN SELECT extract(DAYOFWEEK_ISO FROM day), day
             FROM (SELECT sequence(weekdays.start, weekdays.end)) AS T(days)
                  LATERAL VIEW explode(days) AS day
             WHERE extract(DAYOFWEEK_ISO FROM day) BETWEEN 1 AND 5;
```

Quelle: [CREATE FUNCTION (SQL Function)](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-sql-function) (Übersicht inkl. externer/JVM-Funktionen: [CREATE FUNCTION](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-function))

### DROP FUNCTION

Löscht eine permanente oder temporäre Function.

```sql
DROP FUNCTION hello;
DROP TEMPORARY FUNCTION IF EXISTS hello;
```

Quelle: [DROP FUNCTION](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-function)

### DESCRIBE FUNCTION

Zeigt Signatur, Implementierungsklasse bzw. Body und Nutzungshinweise einer Function an; `EXTENDED` liefert zusätzlich Beispiele und Details wie Owner und Erstellzeit.

```sql
DESCRIBE FUNCTION abs;
DESCRIBE FUNCTION EXTENDED abs;

-- Für eine selbst erstellte SQL-Funktion
CREATE FUNCTION dice(n INT) RETURNS INT
    NOT DETERMINISTIC
    COMMENT 'An n-sided dice'
    RETURN floor((rand() * n) + 1);
DESCRIBE FUNCTION EXTENDED dice;
```

Quelle: [DESCRIBE FUNCTION](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-function)

### SHOW FUNCTIONS

Listet System- und/oder benutzerdefinierte Functions auf, optional eingeschränkt auf ein Schema oder gefiltert per `LIKE`-Muster bzw. Regex.

```sql
SHOW SYSTEM FUNCTIONS IN salesdb max;
SHOW FUNCTIONS LIKE 't*';
```

Quelle: [SHOW FUNCTIONS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-functions)
