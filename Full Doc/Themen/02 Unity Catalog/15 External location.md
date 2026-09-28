## External Location

Innerhalb eines [Metastores](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#metastore) ist eine **External Location** ein sicherbares Objekt, das ein [Storage Credential](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#storage-credential) mit einem Cloud-Speicherpfad koppelt. Sie regelt den Zugriff auf einen bestimmten Pfad im Cloud-Speicher.

Um eine External Location anzulegen, benötigt ein Nutzer das `CREATE EXTERNAL LOCATION`-Privileg auf dem Unity-Catalog-Metastore.

Nach dem Anlegen einer External Location benötigen Nutzer das `READ FILES`-Privileg, um Dateien direkt aus dem Speicherpfad zu lesen, und das `WRITE FILES`-Privileg, um Dateien zu schreiben. Databricks empfiehlt jedoch, den Zugriff auf Cloud-Speicher über [Volumes](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#volume) und die Privilegien `READ VOLUME`/`WRITE VOLUME` zu verwalten, statt `READ FILES` und `WRITE FILES` direkt auf External Locations zu vergeben.

Weitere Informationen zu External Locations siehe [Überblick über External Locations](https://docs.databricks.com/aws/en/connect/unity-catalog/cloud-storage/#external-locations).

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### CREATE EXTERNAL LOCATION

```sql
CREATE EXTERNAL LOCATION s3_remote URL 's3://us-east-1/location'
    WITH (STORAGE CREDENTIAL s3_remote_cred)
    COMMENT 'Default source for AWS exernal data';
```

Koppelt einen Cloud-Speicherpfad (`URL`) mit einem Storage Credential. Namen mit Sonderzeichen (z. B. Bindestrichen) müssen in Backticks stehen.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-location

### ALTER EXTERNAL LOCATION

```sql
-- Umbenennen
ALTER EXTERNAL LOCATION descend_loc RENAME TO decent_loc;

-- URL ändern (auch wenn die Location aktiv genutzt wird)
ALTER EXTERNAL LOCATION best_loc SET URL 's3://us-east-1-prod/best_location' FORCE;

-- Storage Credential wechseln
ALTER EXTERNAL LOCATION best_loc SET STORAGE CREDENTIAL street_cred;

-- Eigentümer ändern
ALTER EXTERNAL LOCATION best_loc OWNER TO `alf@melmak.et`;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-location

### DROP EXTERNAL LOCATION

```sql
DROP EXTERNAL LOCATION IF EXISTS some_location;
```

Erfordert `MANAGE`-Privileg oder Eigentümerschaft; mit `IF EXISTS` wird kein Fehler geworfen, falls die Location nicht existiert.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-location

### DESCRIBE EXTERNAL LOCATION / SHOW EXTERNAL LOCATIONS

```sql
DESCRIBE EXTERNAL LOCATION best_loco;

SHOW EXTERNAL LOCATIONS;
```

`DESCRIBE` zeigt Name, URL, Credential, Owner und Zeitstempel einer einzelnen Location; `SHOW` listet alle im Metastore zugänglichen External Locations.

Quellen: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-location, https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-locations

### REFRESH FOREIGN

```sql
REFRESH FOREIGN CATALOG some_catalog;
REFRESH FOREIGN SCHEMA some_catalog.some_schema;
REFRESH FOREIGN TABLE some_catalog.some_schema.some_table;

-- DBFS-Pfad einer föderierten Tabelle neu auflösen
REFRESH FOREIGN TABLE hms_fed_catalog.schema.table RESOLVE DBFS LOCATION;
```

Aktualisiert Metadaten für über Catalog Federation angebundene Catalogs/Schemas/Tabellen (z. B. Hive-Metastore-Federation).

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-refresh-foreign

### REFRESH FULL

```sql
-- Streaming Table vollständig neu verarbeiten (Truncate + Neuaufbau)
REFRESH STREAMING TABLE cat.db.st_name FULL;
```

Erzwingt bei Streaming Tables bzw. Materialized Views eine vollständige Neuverarbeitung aller Quelldaten statt eines inkrementellen Refresh — relevant, wenn sich die zugrunde liegende External Location oder deren Inhalt grundlegend geändert hat.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-refresh-full
