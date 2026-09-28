## Catalog

Innerhalb eines [Metastores](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#metastore) ist ein **Catalog** die erste und oberste Ebene für deine Daten-Assets. Kataloge sind [Container-Objekte](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#container-objects). Ein Katalog enthält Schemas, die wiederum Tabellen, Views, Volumes und Funktionen enthalten.

Häufig ist vom "Drei-Ebenen-Namespace" (`catalog`.`schema`.`table`) für Daten in Unity Catalog die Rede. Der Katalog bildet dabei die erste Ebene dieses Drei-Ebenen-Namespace.

Die folgende Tabelle fasst wichtige Details zu Katalogen zusammen:

| Detail | Beschreibung |
| :------------------------------ | :----------------------------------------------------------- |
| Vererbung | Auf einem Katalog vergebene Privilegien gelten automatisch für alle aktuellen und künftigen Schemas, Tabellen, Views, Volumes und Funktionen darin. `SELECT` auf einem Katalog zu vergeben erlaubt einem Nutzer beispielsweise, jede Tabelle in diesem Katalog zu lesen (mit den passenden `USE CATALOG`- und `USE SCHEMA`-[Nutzungsprivilegien](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges)). Siehe [Privilegienvererbung](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#inheritance). Wegen dieser Vererbung sind Katalog-Level-Privilegien weitreichend — bei der Vergabe an Nutzer ist Vorsicht geboten. |
| Nutzungsprivileg (`USE CATALOG`) | Das `USE CATALOG`-[Nutzungsprivileg](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/permissions-concepts#usage-privileges) ist Voraussetzung, bevor ein Nutzer mit irgendeinem Objekt in einem Katalog interagieren kann — unabhängig davon, welche Privilegien er auf untergeordneten Objekten besitzt. |
| Das `BROWSE`-Privileg | Wird einem Nutzer `BROWSE` auf einem Katalog gewährt, kann er Metadaten für alle Objekte im Katalog entdecken und einsehen — inklusive untergeordneter Schemas, Tabellen, Views, Volumes und Funktionen —, ohne dass Datenzugriff gewährt wird. `BROWSE` lässt sich nur auf Katalog-Ebene vergeben. Databricks empfiehlt, `BROWSE` an die Gruppe `All account users` zu vergeben, damit Nutzer Daten entdecken und bei Bedarf Zugriff anfragen können. |
| Workspace-Bindung | Standardmäßig ist ein Katalog von allen mit demselben Metastore verbundenen Workspaces aus zugänglich. Das lässt sich einschränken, indem der Katalog an bestimmte Workspaces gebunden wird, optional als schreibgeschützt. Workspace-Bindung hat Vorrang vor einzelnen Privilegienvergaben — selbst ein Nutzer mit explizitem `SELECT`-Grant kann nicht auf ein Objekt in einem Katalog zugreifen, der nicht an seinen Workspace gebunden ist. Siehe [Workspace-Catalog-Bindung](https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/workspace-catalog-binding). |

```python
USE CATALOG dbacademy;
```

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### ALTER CATALOG

Mit `ALTER CATALOG` lassen sich u. a. Owner, Tags, Predictive Optimization und die Aufbewahrungsdauer gelöschter Objekte eines Katalogs ändern.

```sql
-- Besitzer des Katalogs übertragen
ALTER CATALOG some_cat OWNER TO `alf@melmak.et`;

-- Tags setzen bzw. entfernen
ALTER CATALOG test SET TAGS ('tag1' = 'val1', 'tag2' = 'val2');
ALTER CATALOG test UNSET TAGS ('tag1', 'tag2');

-- Predictive Optimization aktivieren
ALTER CATALOG main ENABLE PREDICTIVE OPTIMIZATION;

-- 30-Tage-Wiederherstellungsfrist für gelöschte Managed Tables setzen
ALTER CATALOG my_catalog RETAIN DROPPED TO 30 DAYS;
```

Quelle: [ALTER CATALOG](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-catalog)

### ALTER CATALOG … DROP CONNECTION

Wandelt einen föderierten (Foreign) Katalog (z. B. aus HMS-Föderation) in einen Standard-Unity-Catalog um, indem die zugrunde liegende Connection entfernt wird.

```sql
-- Konvertierung nur, wenn keine Foreign Tables/Views mehr existieren (Standard)
ALTER CATALOG hms_federated_catalog DROP CONNECTION;

-- Erzwungene Konvertierung inkl. Löschen verbleibender Foreign Tables
ALTER CATALOG hms_federated_catalog DROP CONNECTION FORCE;
```

Quelle: [ALTER CATALOG … DROP CONNECTION](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-catalog-drop-connection)

### CREATE CATALOG

Legt einen neuen Katalog an, optional mit Kommentar, abweichendem Managed-Storage-Pfad oder als Foreign Catalog über eine Connection.

```sql
-- Katalog anlegen (nur falls nicht bereits vorhanden)
CREATE CATALOG IF NOT EXISTS customer_cat COMMENT 'This is customer catalog';

-- Katalog mit eigenem Managed-Storage-Ort
CREATE CATALOG customer_cat MANAGED LOCATION 's3://depts/finance';

-- Foreign Catalog über eine bestehende Connection (z. B. PostgreSQL)
CREATE FOREIGN CATALOG postgresql_catalog
  USING CONNECTION postgresql_connection
  OPTIONS (database = 'postgresdb');
```

Quelle: [CREATE CATALOG](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-catalog)

### DROP CATALOG

Löscht einen Katalog. `CASCADE` löscht auch alle enthaltenen Schemas, `RESTRICT` (Standard) verlangt, dass der Katalog leer ist.

```sql
-- Katalog inklusive aller Schemas löschen
DROP CATALOG vaccine CASCADE;

-- Katalog nur löschen, falls er existiert und leer ist
DROP CATALOG IF EXISTS vaccine RESTRICT;
```

Quelle: [DROP CATALOG](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-catalog)

### DESCRIBE CATALOG

Zeigt Metadaten zu einem Katalog an; mit `EXTENDED` zusätzlich Angaben wie Ersteller und Änderungszeitpunkt.

```sql
DESCRIBE CATALOG main;
DESCRIBE CATALOG EXTENDED main;
```

Quelle: [DESCRIBE CATALOG](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-catalog)

### SHOW CATALOGS

Listet alle sichtbaren Kataloge auf, optional gefiltert per `LIKE`-Muster.

```sql
SHOW CATALOGS;

-- Nur Kataloge, deren Name mit "pay" beginnt
SHOW CATALOGS LIKE 'pay*';
```

Quelle: [SHOW CATALOGS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-catalogs)

### USE CATALOG

Setzt den aktuellen Katalog für die Session. Dabei wird das aktuelle Schema automatisch auf `default` zurückgesetzt.

```sql
USE CATALOG hive_metastore;

-- Katalog über eine String-Variable setzen
DECLARE mycat = 'main';
USE CATALOG IDENTIFIER(mycat);
```

Quelle: [USE CATALOG](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-use-catalog)
