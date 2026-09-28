# Eigentümerschaft übertragen (`OWNER TO`)

```sql
ALTER <securable-type> <securable-name> OWNER TO <principal>;
```

**Beispiel für eine Table:**

```sql
ALTER TABLE mycatalog.myschema.orders OWNER TO `accounting`;
```

**Beispiel für einen Catalog** (`ALTER CATALOG`-Sprachreferenz, dort als `[ SET ] OWNER TO principal` innerhalb des vollständigen Syntaxblocks):

```sql
ALTER CATALOG some_cat OWNER TO 'alf@melmak.et';
```

**Beispiel für ein Schema:**

```sql
ALTER SCHEMA main.bronze OWNER TO `data-engineers`;
```

**Beispiel für ein Volume** (eigene Syntaxvariante mit `SET OWNER TO` statt nur `OWNER TO`, laut `ALTER VOLUME`-Referenz):

```sql
ALTER VOLUME main.bronze.landing_files SET OWNER TO `data-engineers`;
```

## Unterstützte Objekttypen

Catalogs, Schemas, Tables, Views, Volumes, External Locations und Storage Credentials unterstützen die Eigentumsübertragung. Ausdrücklich **nicht** unterstützt: `METASTORE` wird in diesem Befehl nicht als Securable-Objekt unterstützt.

## Wer darf übertragen?

Die Objekt-Ownership kann übertragen werden, wenn man einer der folgenden ist:

- der aktuelle Owner,
- ein Metastore-Admin,
- der Owner des Containers (der Catalog für ein Schema, das Schema für eine Table),
- ein Nutzer mit dem `MANAGE`-Privileg auf dem Objekt.

## Einschränkung bei Views/Functions/Models

Um Privilege Escalation zu verhindern, kann **nur ein Metastore-Admin** die Ownership einer View, Function oder eines Models an einen beliebigen Nutzer, Service Principal oder eine beliebige Gruppe im Account übertragen. Aktuelle Owner und Nutzer mit dem `MANAGE`-Privileg dürfen die Ownership nur an ihren eigenen Nutzernamen oder an eine Gruppe übertragen, deren Mitglied sie sind.

Bei **Shares** gilt ebenfalls eine Sonderregel: Nur ein Metastore-Admin kann die Share-Eigentümerschaft übertragen.

## Quellen

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-alter-catalog
