## Provider

Innerhalb eines [Metastores](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#metastore) ist ein **Provider** ein sicherbares Objekt in OpenSharing, das eine externe Organisation repräsentiert, die Daten mit deiner Organisation geteilt hat. Provider-Objekte werden im Unity-Catalog-Metastore des Recipients angelegt. Das `USE PROVIDER`-Privileg erlaubt einem Nutzer, alle Provider und deren Shares einzusehen, und — kombiniert mit `CREATE CATALOG` — einen geteilten Katalog einzubinden, ohne die Metastore-Admin-Rolle zu benötigen.

Um einen Provider anzulegen, benötigt ein Nutzer das `CREATE PROVIDER`-Privileg auf dem Unity-Catalog-Metastore.

Weitere Informationen zu Providern siehe [Was ist OpenSharing?](https://docs.databricks.com/aws/en/opensharing/).

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### ALTER PROVIDER
Benennt einen Provider um bzw. überträgt dessen Eigentümerschaft. Zugangsdaten (Credentials) werden dadurch nicht aktualisiert.
```sql
ALTER PROVIDER `Center for Disease Control` RENAME TO cdc;
ALTER PROVIDER cdc OWNER TO `alf@melmak.et`;
```
Quelle: [ALTER PROVIDER](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-provider)

### DROP PROVIDER
Entfernt einen Provider; mit `IF EXISTS` fehlerfrei auch dann, wenn er nicht existiert.
```sql
DROP PROVIDER IF EXISTS other_corp;
```
Quelle: [DROP PROVIDER](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-provider)

### DESCRIBE PROVIDER
Zeigt Metadaten eines Providers an (u. a. Authentifizierungstyp, Ersteller, Cloud-Region).
```sql
DESCRIBE PROVIDER other_org;
```
Quelle: [DESCRIBE PROVIDER](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-provider)

### SHOW PROVIDERS
Listet alle sichtbaren Provider auf, optional gefiltert per Musterabgleich.
```sql
SHOW PROVIDERS;
SHOW PROVIDERS LIKE 'other_org';
```
Quelle: [SHOW PROVIDERS](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-providers)
