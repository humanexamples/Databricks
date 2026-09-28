# Prinzipal-Typen: Nutzer, Gruppen, Service Principals

Ein `<principal>` in `GRANT`/`REVOKE`-Statements ist ein Nutzer, ein Service Principal oder eine Gruppe, dem/der die Privilegien gewährt werden.

## Backtick-Regel

Nutzer-, Service-Principal- und Gruppennamen mit Sonderzeichen müssen in Backticks (`` ` ``) eingeschlossen werden — z. B. bei E-Mail-Adressen (enthalten `@` und `.`) oder Gruppennamen mit Bindestrich:

```sql
GRANT SELECT ON TABLE sample_data TO `alf@melmak.et`;
GRANT CREATE TABLE ON SCHEMA main.default TO `finance-team`;
```

## Service Principals

Werden über ihren `applicationId`-Wert referenziert. Im Doku-Beispiel wird die Service-Principal-ID selbst in Backticks gesetzt, weil sie Bindestriche enthält:

```sql
-- Privileg an den Service Principal fab9e00e-ca35-11ec-9d64-0242ac120002 vergeben
GRANT SELECT ON TABLE t TO `fab9e00e-ca35-11ec-9d64-0242ac120002`;
```

## Gruppen

Werden syntaktisch identisch wie Nutzer behandelt — einfacher Name ohne Backticks, sofern keine Sonderzeichen enthalten sind:

```sql
GRANT ALL PRIVILEGES ON TABLE forecasts TO finance;
```

Sonst mit Backticks, wie bei `` `finance-team` `` oder `` `data-consumers` ``.

## Vertiefung: Weitere SQL-Beispiele aus dem Language Manual

### Prinzipal-Syntax (`sql-ref-principal`)

Die formale Syntax für `<principal>` fasst alle vier Formen zusammen:

```sql
{ `<user>@<domain-name>` | `<sp-application-id>` | group_name | users | `account users` }
```

Beispiele, die die verschiedenen Prinzipal-Formen zeigen — inklusive der Sondergruppe `` `account users` `` (alle Nutzer des Accounts) und Ownership-Transfer auf eine Gruppe:

```sql
-- Privileg an die Sondergruppe "alle Account-Nutzer" entziehen
REVOKE SELECT ON TABLE t FROM `account users`;

-- Eigentümerschaft eines Schemas auf eine Gruppe übertragen
ALTER SCHEMA some_schema OWNER TO `some-group`;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-principal

### `CREATE GROUP`

```sql
CREATE GROUP group_principal
  [ WITH
    [ USER user_principal [, ...] ]
    [ GROUP subgroup_principal [, ...] ]
  ]
```

```sql
-- Leere Gruppe anlegen
CREATE GROUP humans;

-- Gruppe mit zwei Nutzern als Mitglieder anlegen
CREATE GROUP tv_aliens WITH USER `alf@melmak.et`, `thor@asgaard.et`;

-- Gruppe mit einem Nutzer UND einer Untergruppe anlegen (verschachtelte Gruppen)
CREATE GROUP aliens WITH USER `hilo@jannus.et` GROUP tv_aliens;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/security-create-group

### `ALTER GROUP` — Mitglieder hinzufügen/entfernen

```sql
ALTER GROUP parent_principal { ADD | DROP }
  { GROUP group_principal [, ...] | USER user_principal [, ...] } [...]
```

```sql
ALTER GROUP aliens ADD GROUP tv_aliens;
ALTER GROUP aliens DROP USER `alf@melmak.et`;
ALTER GROUP tv_aliens ADD USER `alf@melmak.et`;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/security-alter-group

### `DROP GROUP`

```sql
DROP GROUP group_principal
```

```sql
DROP GROUP aliens;
```

Quelle: https://docs.databricks.com/aws/en/sql/language-manual/security-drop-group

## Quelle

- https://docs.databricks.com/aws/en/sql/language-manual/security-grant
