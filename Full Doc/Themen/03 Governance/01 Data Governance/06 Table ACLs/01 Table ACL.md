# Table Access Control aktivieren — Legacy

**Hinweis:** Legacy-Governance-Modell für den Hive Metastore. Databricks empfiehlt stattdessen Unity Catalog.

## Zwei Varianten

- **Nur SQL:** Beschränkt Nutzer ausschließlich auf SQL-Befehle, per Spark-Konfiguration `spark.databricks.acl.sqlOnly true`.
- **Python und SQL:** Erlaubt SQL-, Python- und PySpark-Befehle, erzwingt dabei zusätzliche Einschränkungen:
  - Ausführung mit niedrig privilegiertem Nutzer auf Cluster-Knoten.
  - Netzwerkzugriff nur über Ports 80 und 443 (mit Ausnahmen für eingebaute Spark-Funktionen).
  - Konfigurierbare Outbound-Port-Whitelist über `spark.databricks.pyspark.iptable.outbound.whitelisted.ports`.

## Einrichtung auf Workspace-Ebene

1. Zum Tab **Security** in den Workspace-Einstellungen navigieren.
2. Die Option **Table Access Control** aktivieren.
3. Nutzern verbieten, Cluster ohne aktiviertes Table Access Control zu erstellen oder sich damit zu verbinden.

## Wichtige Einschränkung

Selbst wenn Table Access Control für einen Cluster aktiviert ist, haben **Databricks-Workspace-Administratoren weiterhin Zugriff auf Daten auf Dateiebene**.

Nicht unterstützt mit Machine Learning Runtime.

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### Legacy-Privilegien im Hive Metastore (`GRANT`/`REVOKE`)

Im Legacy-Modus (ohne Unity Catalog) funktionieren `GRANT` und `REVOKE` syntaktisch identisch zu Unity Catalog, wirken aber nur auf Hive-Metastore-Objekte (Tabellen/Schemas ohne Catalog-Ebene):

```sql
-- Privileg an einen Nutzer vergeben
GRANT SELECT ON TABLE t TO `alf@melmak.et`;

-- Privileg auf einem Schema entziehen
REVOKE USAGE ON SCHEMA some_schema FROM `alf@melmak.et`;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-privileges-hms

### `MSCK REPAIR ... PRIVILEGES` — verwaiste ACLs aufräumen

Wird ein Objekt gelöscht, ohne dass zuvor alle Berechtigungen darauf entzogen wurden, bleiben verwaiste Zugriffskontrolleinträge zurück. `MSCK REPAIR PRIVILEGES` entfernt diese Legacy-Table-ACL-Reste für alle Nutzer auf einmal:

```sql
MSCK REPAIR object PRIVILEGES

object  { [ SCHEMA | DATABASE ] schema_name |
    FUNCTION function_name |
    TABLE table_name |
    VIEW view_name |
    ANONYMOUS FUNCTION |
    ANY FILE }
```

```sql
MSCK REPAIR SCHEMA gone_from_hive PRIVILEGES;
MSCK REPAIR ANONYMOUS FUNCTION PRIVILEGES;
MSCK REPAIR TABLE default.dropped PRIVILEGES;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/security-msck

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/table-acls/table-acl
