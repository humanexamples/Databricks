# `GRANT`, `REVOKE`, `SHOW GRANTS` — vollständige Syntax



## `GRANT`

```sql
GRANT privilege_types ON securable_object TO principal

privilege_types { ALL PRIVILEGES | privilege_type [, ...] }
```

**`ALL PRIVILEGES`:** Gewährt alle auf das `securable_object` anwendbaren Privilegien. In Unity Catalog wird `ALL PRIVILEGES` **zum Zeitpunkt der Berechtigungsprüfung** auf alle dann verfügbaren Privilegien erweitert — es werden nicht einzeln alle zum Zeitpunkt der Vergabe anwendbaren Privilegien gewährt. Um versehentliche Datenexfiltration oder Privilege Escalation zu vermeiden, umfasst `ALL PRIVILEGES` **nicht** die Privilegien `EXTERNAL USE SCHEMA`, `EXTERNAL USE LOCATION`, `MANAGE` oder `READ METADATA`.

Nutzer-, Service-Principal- und Gruppennamen mit Sonderzeichen müssen in Backticks (`` ` ``) eingeschlossen werden (siehe [Prinzipal-Typen.md](Prinzipal-Typen.md)).

```sql
GRANT CREATE ON SCHEMA my_schema TO `alf@melmak.et`;
GRANT ALL PRIVILEGES ON TABLE forecasts TO finance;
GRANT SELECT ON TABLE sample_data TO `alf@melmak.et`;

-- Privileg an einen Service Principal vergeben
GRANT SELECT ON TABLE t TO `fab9e00e-ca35-11ec-9d64-0242ac120002`;
```

**Hinweis:** Der `samples`-Catalog lässt sich nicht per `GRANT` verändern — er ist für alle Workspaces verfügbar, aber schreibgeschützt.

### `GRANT ... ON SHARE` (Delta Sharing) — eigene Syntax

```sql
GRANT SELECT ON SHARE <share-name> TO RECIPIENT <recipient-name>;
REVOKE SELECT ON SHARE <share-name> FROM RECIPIENT <recipient-name>;
```

`SELECT` ist das einzige Privileg, das einem Recipient auf einem Share gewährt werden kann. Um diesen Befehl selbst ausführen zu dürfen, braucht ein Prinzipal entweder Metastore-Admin-Rechte, oder in Kombination (`USE SHARE` **und** `SET SHARE PERMISSION`, oder alternativ Share-Owner) **und** (`USE RECIPIENT`, oder alternativ Recipient-Owner). Für `REVOKE` genügt bereits Metastore-Admin, `USE SHARE`-Inhaber oder Share-Owner.

## `REVOKE`

```sql
REVOKE privilege_types ON securable_object FROM principal

privilege_types { ALL PRIVILEGES | privilege_type [, ...] }
```

```sql
REVOKE ALL PRIVILEGES ON SCHEMA default FROM `alf@melmak.et`;
REVOKE SELECT ON TABLE t FROM aliens;
```

**Idempotenz:** Ein `REVOKE` gelingt auch dann, wenn das angegebene Privileg vorher nie erteilt wurde — es stellt lediglich sicher, dass die Berechtigung danach nicht mehr besteht, unabhängig vom vorherigen Zustand.

**Sonderfall `ALL PRIVILEGES`:** Ein `REVOKE ALL PRIVILEGES` entfernt sowohl den `ALL PRIVILEGES`-Grant selbst als auch alle davon implizierten Einzelrechte — **nicht** aber `EXTERNAL USE SCHEMA`, `EXTERNAL USE LOCATION`, `MANAGE` oder `READ METADATA`, da diese ohnehin nie Teil von `ALL PRIVILEGES` waren.

## `SHOW GRANTS`

```sql
SHOW GRANTS [ principal ] ON securable_object
```

`GRANT` kann alternativ auch anstelle von `GRANTS` verwendet werden (`SHOW GRANT ...` funktioniert ebenso wie `SHOW GRANTS ...`).

`SHOW GRANTS` zeigt **alle** Privilegien (geerbte, verweigerte und gewährte), die sich auf das Securable-Objekt auswirken — nicht nur explizit gesetzte, sondern auch geerbte Berechtigungen.

**Berechtigungsvoraussetzungen:** Workspace-Administrator oder Owner des Objekts sein; oder die `READ METADATA`- oder `MANAGE`-Berechtigung auf dem Objekt besitzen, zuzüglich der erforderlichen Usage-Privilegien auf dessen übergeordneten Containern; oder der in `principal` angegebene Nutzer selbst sein.

Rückgabespalten: `principal`, `actionType`, `objectType`, `objectKey`.

```sql
SHOW GRANTS `alf@melmak.et` ON SCHEMA my_schema;
-- principal      actionType  objectType  objectKey
-- alf@melmak.et  USE         DATABASE    my_schema

SHOW GRANTS ON SHARE some_share;
-- recipient  actionType  objectType  objectKey
-- A_Corp     SELECT
-- B.com      SELECT

SHOW GRANTS ON CONNECTION mysql_connection;
-- principal      actionType              objectType  objectKey
-- alf@melmak.et  CREATE FOREIGN CATALOG  CONNECTION  mysql_connection
-- alf@melmak.et  USE CONNECTION          CONNECTION  mysql_connection
```

Auf Metastore-Ebene entfällt der Objektname:

```sql
SHOW GRANTS [ principal ] ON METASTORE;
```

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### `DENY` — Privileg explizit verweigern

`DENY` hat dieselbe Syntax wie `GRANT`, kehrt aber dessen Wirkung um: Ein `DENY` schlägt jeden geerbten oder direkt gewährten `GRANT` — es ist die stärkste Regel in der Privilegien-Hierarchie.

```sql
DENY privilege_types ON securable_object TO principal

privilege_types { ALL PRIVILEGES | privilege_type [, ...] }
```

```sql
-- Alf das Recht verweigern, `t` abzufragen
DENY SELECT ON TABLE t TO `alf@melmak.et`;

-- DENY wieder aufheben
REVOKE SELECT ON TABLE t FROM `alf@melmak.et`;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/security-deny

### `sql-ref-privileges` — Beispiele mit weiteren Privilegtypen

Die allgemeine Privilegien-Referenz zeigt `GRANT`/`REVOKE` zusätzlich mit `USE SCHEMA` und `READ METADATA` sowie mit der Sondergruppe `` `account users` ``:

```sql
GRANT SELECT ON TABLE t TO `alf@melmak.et`;
REVOKE USE SCHEMA ON SCHEMA some_schema FROM `account users`;
GRANT READ METADATA ON SCHEMA some_schema TO `auditors`;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-privileges

### `SHOW GRANTS` — zusätzliches Beispiel

Neben den bereits oben gezeigten Beispielen belegt die Doku-Seite dieselben drei Fälle (Schema, Share, Connection) als Kernbeispiele der Syntax — inklusive des Hinweises, dass `GRANT` als Synonym für `GRANTS` funktioniert:

```sql
SHOW GRANTS `alf@melmak.et` ON SCHEMA my_schema;
SHOW GRANTS ON SHARE some_share;
SHOW GRANTS ON CONNECTION mysql_connection;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/security-show-grant

## Quellen

- https://docs.databricks.com/aws/en/sql/language-manual/security-grant
- https://docs.databricks.com/aws/en/sql/language-manual/security-revoke
- https://docs.databricks.com/aws/en/sql/language-manual/security-deny
- https://docs.databricks.com/aws/en/sql/language-manual/security-show-grant
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-privileges
- https://docs.databricks.com/aws/en/delta-sharing/grant-access
