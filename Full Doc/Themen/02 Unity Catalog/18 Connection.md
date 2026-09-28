## Connection

Innerhalb eines [Metastores](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#metastore) ist eine **Connection** ein sicherbares Objekt, das den Endpunkt und die Zugangsdaten speichert, die zum Zugriff auf ein externes System benötigt werden. Connections unterstützen folgende Szenarien:

- [Query Federation](https://docs.databricks.com/aws/en/query-federation/database-federation)
- [Catalog Federation](https://docs.databricks.com/aws/en/query-federation/catalog-federation)
- [Managed Ingestion](https://docs.databricks.com/aws/en/connect/managed-ingestion)
- [JDBC-Zugriff](https://docs.databricks.com/aws/en/connect/jdbc-connection)
- [HTTP-Dienste](https://docs.databricks.com/aws/en/query-federation/http)

Um eine Connection anzulegen, benötigt ein Nutzer das `CREATE CONNECTION`-Privileg auf dem Unity-Catalog-Metastore. Nutzt die Connection ein [Service Credential](https://docs.databricks.com/aws/en/data-governance/unity-catalog/securable-objects#service-credential), benötigt der Nutzer zusätzlich `CREATE CONNECTION` auf diesem Service Credential.

Das `USE CONNECTION`-Privileg erlaubt einem Nutzer, Connection-Details aufzulisten und einzusehen sowie die Connection für ihr unterstütztes Szenario zu verwenden.

Weitere Informationen siehe [Unity-Catalog-Connections](https://docs.databricks.com/aws/en/connect/uc-connections).

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### CREATE CONNECTION

```sql
-- PostgreSQL-Connection mit Secrets statt Klartext-Zugangsdaten
CREATE CONNECTION postgresql_connection
TYPE POSTGRESQL
OPTIONS (
  host '<hostname>',
  port '5432',
  user secret('secrets.r.us', 'postgresUser'),
  password secret('secrets.r.us', 'postgresPassword')
);

-- HTTP-Connection (z. B. für einen externen REST-Dienst)
CREATE CONNECTION slack_conn
TYPE HTTP
OPTIONS (
  host 'https://slack.com',
  port '443',
  base_path '/api/',
  bearer_token secret('secrets.r.us', 'slackBearerToken')
);
```

Unterstützte `TYPE`-Werte u. a. `DATABRICKS`, `HTTP`, `MYSQL`, `POSTGRESQL`, `REDSHIFT`, `SNOWFLAKE`, `SQLDW`, `SQLSERVER`. Sensible Optionswerte sollten stets über die `secret()`-Funktion statt im Klartext referenziert werden.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-connection

### ALTER CONNECTION

```sql
ALTER CONNECTION mysql_connection SET OWNER TO `alf@melmak.et`;
ALTER CONNECTION mysql_connection RENAME TO `other_mysql_connection`;
ALTER CONNECTION mysql_connection OPTIONS (host 'newmysqlhost.us-west-2.amazonaws.com', port '3306');
```

`OPTIONS(...)` ersetzt dabei die komplette bestehende Optionsliste durch die neue.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-connection

### DROP CONNECTION

```sql
DROP CONNECTION IF EXISTS mysql_connection;
```

Erfordert `MANAGE`-Privileg oder Eigentümerschaft an der Connection.

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-drop-connection

### DESCRIBE CONNECTION / SHOW CONNECTIONS

```sql
DESCRIBE CONNECTION postgresql_connection;

SHOW CONNECTIONS;
```

`DESCRIBE CONNECTION` zeigt Connection- und Credential-Typ, URL, Owner sowie eine Auswahl unkritischer Optionen; `SHOW CONNECTIONS` listet alle zugänglichen Connections im Metastore.

Quellen: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-describe-connection, https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-show-connections
