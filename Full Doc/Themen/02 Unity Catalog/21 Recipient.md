## Recipient

Innerhalb eines [Metastores](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#metastore) ist ein **Recipient** ein sicherbares Objekt in OpenSharing, das eine externe Organisation oder Nutzergruppe repräsentiert, mit der ein Provider Daten teilt. Recipient-Objekte werden im Unity-Catalog-Metastore des Providers angelegt. Auf einem Recipient-Objekt selbst lassen sich keine Privilegien vergeben. Der Zugriff auf geteilte Daten wird gesteuert, indem `SELECT` auf einem [Share](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#share) an den Recipient vergeben wird.

Um einen Recipient anzulegen, benötigt ein Nutzer das `CREATE RECIPIENT`-Privileg auf dem Unity-Catalog-Metastore.

Weitere Informationen zu Recipients siehe [Daten-Recipients für OpenSharing anlegen (Databricks-zu-Databricks-Sharing)](https://docs.databricks.com/aws/en/opensharing/create-recipient).

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### CREATE RECIPIENT
Legt einen Recipient an — entweder für Databricks-zu-Databricks-Sharing über eine Metastore-ID oder für externe Organisationen (Token-basiert), optional mit Kommentar und benutzerdefinierten Properties.
```sql
CREATE RECIPIENT other_databricks_org
USING ID 'azure:westus:f12dcb34-5678-9d4c-1234-c5ac67f8b90a';

CREATE RECIPIENT recipient_name
COMMENT 'description'
PROPERTIES (property_key = 'property_value');
```
Quelle: [CREATE RECIPIENT](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-recipient)

### ALTER RECIPIENT
Benennt einen Recipient um, überträgt die Eigentümerschaft oder setzt Properties (z. B. für Partitionsfilterung je Recipient).
```sql
ALTER RECIPIENT `Center for Disease Control` RENAME TO cdc;
ALTER RECIPIENT cdc OWNER TO `alf@melmak.et`;
ALTER RECIPIENT cdc SET PROPERTIES ( 'country' = 'US' );
```
Quelle: [ALTER RECIPIENT](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-recipient)

### DROP RECIPIENT
Entfernt einen Recipient wieder aus dem Metastore.
```sql
CREATE RECIPIENT other_corp COMMENT 'OtherCorp.com';
DESCRIBE RECIPIENT other_corp;
DROP RECIPIENT other_corp;
```
Quelle: [DROP RECIPIENT](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-recipient)

### DESCRIBE RECIPIENT / SHOW RECIPIENTS
Zeigt Metadaten eines einzelnen Recipients (u. a. Aktivierungslink, Token) bzw. listet alle Recipients im Metastore auf.
```sql
CREATE RECIPIENT other_org;
DESCRIBE RECIPIENT other_org;

SHOW RECIPIENTS;
SHOW RECIPIENTS LIKE 'other_org';
```
Quellen: [DESCRIBE RECIPIENT](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-recipient), [SHOW RECIPIENTS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-recipients)

### SET RECIPIENT
Setzt den aktuellen Recipient in der Session, um `CURRENT_RECIPIENT()` beim Testen von partitionsgefilterten Views zu simulieren (nur für Provider nutzbar).
```sql
CREATE RECIPIENT nasdaq PROPERTIES ('country' = 'US');
CREATE VIEW my_view AS
  SELECT * FROM my_table
  WHERE country = CURRENT_RECIPIENT('country');
SET RECIPIENT nasdaq;
SELECT * FROM my_view;
```
Quelle: [SET RECIPIENT](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-set-recipient)

### SHOW GRANTS TO RECIPIENT
Zeigt an, auf welche Shares ein Recipient Zugriff hat.
```sql
SHOW GRANTS TO RECIPIENT a_corp;
```
Quelle: [SHOW GRANTS TO RECIPIENT](https://docs.databricks.com/aws/en/sql/language-manual/security-show-grant-to-recipient)
