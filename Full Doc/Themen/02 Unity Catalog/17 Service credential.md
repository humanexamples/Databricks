## Service Credential

Innerhalb eines [Metastores](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#metastore) ist ein **Service Credential** ein sicherbares Objekt, das Authentifizierungsinformationen für den Zugriff auf externe Cloud-Dienste speichert — im Unterschied zu [Storage Credentials](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#storage-credential), die den Zugriff auf Cloud-Speicher regeln.

Um ein Service Credential anzulegen, benötigt ein Nutzer das `CREATE SERVICE CREDENTIAL`-Privileg auf dem Unity-Catalog-Metastore.

Das `ACCESS`-Privileg erlaubt einem Nutzer, das Service Credential zu verwenden, um auf einen externen Dienst zuzugreifen. `CREATE CONNECTION` auf einem Service Credential (kombiniert mit `CREATE CONNECTION` auf dem Metastore) erlaubt einem Nutzer, mit diesem Credential eine Connection zu einer externen Datenbank anzulegen.

Weitere Informationen zu Service Credentials siehe [Service Credentials anlegen](https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-services/service-credentials).

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### ALTER SERVICE CREDENTIAL

```sql
-- Service Credential umbenennen
ALTER SERVICE CREDENTIAL street_cred RENAME TO good_cred;

-- Eigentümer ändern
ALTER SERVICE CREDENTIAL street_cred OWNER TO `alf@melmak.et`;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-credential

### DROP SERVICE CREDENTIAL

```sql
DROP SERVICE CREDENTIAL secrets;

-- Ohne Fehler, falls das Credential nicht existiert
DROP SERVICE CREDENTIAL IF EXISTS secrets;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-credential

### DESCRIBE SERVICE CREDENTIAL

```sql
DESCRIBE SERVICE CREDENTIAL secrets;
```

Gibt Name, Owner, Erstellungsdatum/-nutzer und die Credential-Details zurück (analog zu Storage Credentials).

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-credential

### SHOW SERVICE CREDENTIALS

```sql
SHOW SERVICE CREDENTIALS;
```

Listet alle im Metastore zugänglichen Service Credentials samt Kommentar auf. Ohne `STORAGE`/`SERVICE`-Filter liefert `SHOW CREDENTIALS` beide Typen zusammen.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-credentials
