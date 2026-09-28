## Storage Credential

Innerhalb eines [Metastores](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#metastore) ist ein **Storage Credential** ein sicherbares Objekt, das die zum Zugriff auf einen bestimmten Cloud-Speicherpfad benötigten Authentifizierungsinformationen speichert. Die gespeicherte Authentifizierungsmethode hängt vom Cloud-Anbieter ab: eine IAM-Rolle bei AWS, ein Service Principal bei Azure oder ein Service Account bei GCP.

Storage Credentials werden am häufigsten als Baustein für [External Locations](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#external-location) verwendet, die ein Storage Credential mit einem bestimmten Cloud-Speicherpfad koppeln. Ein Storage Credential lässt sich auch direkt verwenden, um External Tables anzulegen.

Um ein Storage Credential anzulegen, benötigt ein Nutzer das `CREATE STORAGE CREDENTIAL`-Privileg auf dem Unity-Catalog-Metastore.

Weitere Informationen zu Storage Credentials siehe [Überblick über Storage Credentials](https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-storage/#storage-credentials).

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### ALTER STORAGE CREDENTIAL

Storage Credentials lassen sich umbenennen oder deren Eigentümer ändern:

```sql
-- Storage Credential umbenennen
ALTER STORAGE CREDENTIAL street_cred RENAME TO good_cred;

-- Eigentümer ändern
ALTER STORAGE CREDENTIAL street_cred OWNER TO `alf@melmak.et`;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-credential

### DROP STORAGE CREDENTIAL

```sql
-- Löschen erzwingen, auch wenn abhängige External Locations existieren
DROP STORAGE CREDENTIAL street_cred FORCE;

-- Ohne Fehler, falls das Credential nicht existiert
DROP STORAGE CREDENTIAL IF EXISTS street_cred;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-credential

### DESCRIBE STORAGE CREDENTIAL

```sql
DESCRIBE STORAGE CREDENTIAL good_cred;
```

Gibt Name, Owner, Erstellungsdatum/-nutzer und die Credential-Details zurück.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-credential

### SHOW STORAGE CREDENTIALS

```sql
SHOW STORAGE CREDENTIALS;
```

Listet alle im Metastore zugänglichen Storage Credentials samt Kommentar auf.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-credentials
