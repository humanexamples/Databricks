## Schema

Innerhalb eines [Catalogs](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#catalog) ist ein **Schema** (auch Datenbank genannt) die zweite Ebene der Objekthierarchie für deine Daten-Assets. Schemas sind [Container-Objekte](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#container-objects). Ein Schema enthält Tabellen, Views, Volumes und Funktionen.

Häufig ist vom *Drei-Ebenen-Namespace* (also `catalog`.`schema`.`table`) für Daten in Unity Catalog die Rede. Das Schema bildet dabei die zweite Ebene dieses Drei-Ebenen-Namespace.

Die folgende Tabelle fasst wichtige Details zu Schemas zusammen:

| Detail | Beschreibung |
| :----------------------------- | :----------------------------------------------------------- |
| Vererbung | Auf einem Schema vergebene Privilegien gelten automatisch für alle aktuellen und künftigen Tabellen, Views, Volumes und Funktionen darin. `SELECT` auf einem Schema zu vergeben erlaubt einem Nutzer beispielsweise, jede Tabelle in diesem Schema zu lesen (mit den passenden `USE CATALOG`- und `USE SCHEMA`-[Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges)). Siehe [Privilegienvererbung](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#inheritance). Wegen dieser Vererbung können Schema-Level-Privilegien weitreichend sein — vor der Vergabe an Nutzer sollte geprüft werden, welche Objekte das Schema enthält. |
| Nutzungsprivileg (`USE SCHEMA`) | Das `USE SCHEMA`-[Nutzungsprivileg](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges) ist Voraussetzung, bevor ein Nutzer mit irgendeinem Objekt in einem Schema interagieren kann — zusätzlich zu `USE CATALOG` auf dem übergeordneten Katalog des Schemas. Ein `USE SCHEMA`-Grant allein gewährt noch keinen Zugriff auf Daten im Schema. |

Weitere Informationen zu Schemas siehe [Schemas](https://docs.databricks.com/aws/en/schemas/).

```python
USE SCHEMA mySchema;
```

```python
-- Mit der Anweisung SHOW SCHEMAS IN die verfügbaren Schemas eines Katalogs anzeigen.
SHOW SCHEMAS IN mycatalog;
```

```python
-- Mit der Anweisung DESCRIBE SCHEMA EXTENDED Informationen zu einem Schema einsehen
DESCRIBE SCHEMA EXTENDED IDENTIFIER(DA.schema_name);
```

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

Hinweis: `DATABASE` ist im Language Manual lediglich ein Alias für `SCHEMA` (`ALTER/CREATE/DROP/DESCRIBE DATABASE`, `SHOW DATABASES`, `USE DATABASE`) — inhaltlich identisch, aber `SCHEMA` wird von Databricks bevorzugt. Die folgenden Beispiele nutzen daher konsequent die `SCHEMA`-Syntax.

### ALTER SCHEMA

Ändert Eigenschaften eines bestehenden Schemas, z. B. Owner, Tags, Predictive Optimization oder den Managed-Storage-Ort.

```sql
-- Schema-Eigenschaften setzen
ALTER SCHEMA inventory SET DBPROPERTIES ('Edited-by' = 'John', 'Edit-date' = '01/01/2001');

-- Besitzer übertragen
ALTER SCHEMA inventory OWNER TO `alf@melmak.et`;

-- Tags setzen
ALTER SCHEMA test SET TAGS ('tag1' = 'val1', 'tag2' = 'val2');

-- 7-Tage-Wiederherstellungsfrist für gelöschte Managed Tables (überschreibt Katalog-Einstellung)
ALTER SCHEMA my_catalog.my_schema SET RETAIN DROPPED TO 7 DAYS;
```

Quelle: [ALTER SCHEMA](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-schema)

### ALTER SCHEMA … SET MANAGED LOCATION

Ändert den Managed-Storage-Pfad eines Schemas, z. B. bei der Migration eines föderierten Schemas.

```sql
ALTER SCHEMA my_catalog.my_schema SET MANAGED LOCATION 'abfss://container@account.dfs.core.windows.net/managed/';
```

Quelle: [ALTER SCHEMA SET MANAGED LOCATION](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-schema-set-managed-location)

### CREATE SCHEMA

Legt ein neues Schema an, optional mit Kommentar, eigenem Managed-Storage-Ort oder Aufbewahrungsfrist für gelöschte Tabellen.

```sql
CREATE SCHEMA IF NOT EXISTS customer_sc COMMENT 'This is customer schema';

-- Eigener Managed-Storage-Ort (nur in Unity Catalog unterstützt)
CREATE SCHEMA customer_sc MANAGED LOCATION 's3://depts/finance';

-- 14-Tage-Wiederherstellungsfrist für gelöschte Managed Tables
CREATE SCHEMA customer_sc RETAIN DROPPED FOR 14 DAYS;
```

Quelle: [CREATE SCHEMA](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-schema)

### DROP SCHEMA

Löscht ein Schema; `CASCADE` löscht auch alle enthaltenen Objekte, `RESTRICT` (Standard) verlangt ein leeres Schema.

```sql
DROP SCHEMA inventory_schema CASCADE;
DROP SCHEMA IF EXISTS inventory_schema CASCADE;
```

Quelle: [DROP SCHEMA](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-schema)

### DESCRIBE SCHEMA

Zeigt Metadaten eines Schemas an; `EXTENDED` liefert zusätzlich gesetzte Properties.

```sql
DESCRIBE SCHEMA employees;

ALTER SCHEMA employees SET DBPROPERTIES ('Create-by' = 'Kevin', 'Create-date' = '09/01/2019');
DESCRIBE SCHEMA EXTENDED employees;
```

Quelle: [DESCRIBE SCHEMA](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-schema)

### SHOW SCHEMAS

Listet die Schemas eines Katalogs auf, optional gefiltert per `LIKE`-Muster.

```sql
SHOW SCHEMAS;
SHOW SCHEMAS LIKE 'pay*';
SHOW SCHEMAS IN some_catalog;
```

Quelle: [SHOW SCHEMAS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-schemas)

### USE SCHEMA

Setzt das aktive Schema der Session; unqualifizierte Referenzen auf Tabellen, Views und Funktionen werden dann aus diesem Schema aufgelöst.

```sql
USE SCHEMA userschema;

USE CATALOG main;
USE SCHEMA my_schema;
SELECT current_catalog(), current_schema();
```

Quelle: [USE SCHEMA](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-use-schema) (Alias-Seiten: [ALTER DATABASE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-database), [CREATE DATABASE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-database), [DROP DATABASE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-database), [DESCRIBE DATABASE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-database), [SHOW DATABASES](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-databases), [USE DATABASE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-usedb))
