## Share

Innerhalb eines [Metastores](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#metastore) ist ein **Share** ein sicherbares Objekt in OpenSharing, das eine logische Gruppierung von Daten-Assets (Tabellen, Views und Volumes) repräsentiert. Ein [Provider](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#provider) kann den Share anschließend externen [Recipients](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#recipient) zur Verfügung stellen.

Das `SELECT`-Privileg auf einem Share wird einem Recipient gewährt (nicht einzelnen Nutzern), damit dieser die Assets im Share lesen kann. Um einen Share anzulegen, benötigt ein Nutzer das `CREATE SHARE`-Privileg auf dem Unity-Catalog-Metastore.

Weitere Informationen zu Shares siehe [Shares für OpenSharing anlegen](https://docs.databricks.com/aws/en/opensharing/create-share).

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### CREATE SHARE
Legt einen neuen Share an, optional mit `IF NOT EXISTS` und einem beschreibenden Kommentar.
```sql
CREATE SHARE IF NOT EXISTS customer_share COMMENT 'This is customer share';
```
Quelle: [CREATE SHARE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-share)

### ALTER SHARE
Fügt Tabellen zu einem Share hinzu (inkl. Umbenennung, Partitionsfilter und Steuerung der Zeitreise-Historie) und verwaltet Umbenennung/Owner des Shares.
```sql
ALTER SHARE some_share
  ADD TABLE my_schema.my_tab
    COMMENT 'some comment'
    PARTITION(c1_int = 5, c2_date LIKE '2021%')
    AS shared_schema.shared_tab;

ALTER SHARE share ADD TABLE table1 WITH HISTORY;
ALTER SHARE share ADD TABLE table2 WITHOUT HISTORY;

ALTER SHARE some_share RENAME TO new_share;
ALTER SHARE some_share OWNER TO `alf@melmak.et`;
```
Quelle: [ALTER SHARE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-share)

### DROP SHARE
Entfernt einen Share; mit `IF EXISTS` fehlerfrei auch dann, wenn er nicht existiert.
```sql
DROP SHARE IF EXISTS vaccine;
```
Quelle: [DROP SHARE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-share)

### SHOW SHARES / SHOW SHARES IN PROVIDER
Listet Shares im Metastore bzw. gefiltert nach einem bestimmten Provider auf.
```sql
SHOW SHARES;
SHOW SHARES LIKE 'vaccine';
SHOW SHARES IN PROVIDER some_provider;
```
Quellen: [SHOW SHARES](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-shares), [SHOW SHARES IN PROVIDER](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-shares-in-provider)

### SHOW ALL IN SHARE
Zeigt alle Objekte (Tabellen, Partitionen, Aliase) innerhalb eines Shares an.
```sql
CREATE SHARE IF NOT EXISTS customer_share COMMENT 'This is customer share';
ALTER SHARE customer_share ADD TABLE my_schema.tab1 AS their_schema.tab1;
ALTER SHARE customer_share ADD TABLE other_schema.tab2 PARTITION (c1 = 5), (c1 = 7);
SHOW ALL IN SHARE customer_share;
```
Quelle: [SHOW ALL IN SHARE](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-all-in-share)

### GRANT / REVOKE / SHOW GRANTS ON SHARE
Vergibt bzw. entzieht einem Recipient das `SELECT`-Privileg auf einem Share und zeigt bestehende Berechtigungen an.
```sql
GRANT SELECT ON SHARE vaccines TO RECIPIENT jab_me_now_corp;
REVOKE SELECT ON SHARE vaccines FROM RECIPIENT jab_me_now_corp;
SHOW GRANTS ON SHARE shared_date;
```
Quellen: [GRANT ON SHARE](https://docs.databricks.com/aws/en/sql/language-manual/security-grant-share), [REVOKE ON SHARE](https://docs.databricks.com/aws/en/sql/language-manual/security-revoke-share), [SHOW GRANTS ON SHARE](https://docs.databricks.com/aws/en/sql/language-manual/security-show-grant-on-share)

### Gesamtablauf (OpenSharing)
Typischer End-to-End-Ablauf: Provider umbenennen, verfügbare Shares einsehen und einen Katalog aus einem geteilten Share erstellen.
```sql
ALTER PROVIDER `Center for Disease Control` RENAME TO cdc;
SHOW SHARES IN PROVIDER cdc;
CREATE CATALOG cdcdata USING SHARE cdc.vaccinedata;
```
Quelle: [Delta Sharing – SQL-Referenz](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-sharing)
