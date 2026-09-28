# Tutorial: ABAC mit SQL konfigurieren

Dasselbe Szenario wie in `Tutorial (UI).md`, hier vollständig über SQL statt Catalog Explorer.

## Voraussetzungen

- Databricks Runtime 16.4+ oder Serverless Compute.
- Account- oder Workspace-Admin-Rechte für Governed Tags.
- `MANAGE` auf Ziel-Catalog/-Schema, `EXECUTE` auf den UDFs.

## Schritt 1: Governed Tags erstellen

- Tag `pii` mit Werten `ssn`, `address`, `email`.
- Tag `consent` nur als Schlüssel (ohne feste Werte).

## Schritt 2: Kundentabelle erstellen

```sql
CREATE CATALOG IF NOT EXISTS abac_tutorial;
USE CATALOG abac_tutorial;
CREATE SCHEMA IF NOT EXISTS customers;
CREATE OR REPLACE TABLE profiles (
    first_name STRING,
    last_name STRING,
    email STRING,
    phone_number STRING,
    home_address STRING,
    ssn_number STRING,
    has_consent BOOLEAN);
```

## Schritt 3: Governed Tags auf Spalten anwenden

`ssn_number`, `home_address` und `email` werden mit `pii` getaggt, `has_consent` mit `consent` — jeweils über `ALTER TABLE`.

## Schritt 4: UDF zur EU-Adresserkennung

```sql
CREATE OR REPLACE FUNCTION is_not_eu_address(address STRING)
RETURNS BOOLEAN
RETURN (SELECT CASE
    WHEN LOWER(address) LIKE '%eu%'
      OR LOWER(address) LIKE '%e.u.%'
      OR LOWER(address) LIKE '%europe%'
    THEN FALSE
    ELSE TRUE
END);
```

## Schritt 5: Row-Filter-Policy

```sql
CREATE POLICY hide_eu_customers
ON SCHEMA abac_tutorial.customers
ROW FILTER is_not_eu_address
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'address') AS addr_col
USING COLUMNS (addr_col);
```

## Schritt 6: Testen

Die Query liefert nur Nicht-EU-Kunden; EU-Kunden werden ausgeblendet.

## Schritt 7: SSN-Maskierungs-UDF

```sql
CREATE OR REPLACE FUNCTION redact_ssn(ssn STRING)
RETURNS STRING
RETURN '***-**-****';
```

## Schritt 8: Column-Mask-Policy

```sql
CREATE POLICY redact_ssn_policy
ON SCHEMA abac_tutorial.customers
COLUMN MASK redact_ssn
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'ssn') AS ssn_col
ON COLUMN ssn_col;
```

## Erweiterung: Zustimmungsabhängige E-Mail-Maskierung

```sql
CREATE OR REPLACE FUNCTION mask_email_by_consent(email STRING, consent BOOLEAN)
RETURNS STRING
RETURN CASE
  WHEN consent = TRUE THEN email
  ELSE CONCAT(LEFT(email, 1), '***@', SUBSTRING_INDEX(email, '@', -1))
END;
```

```sql
CREATE POLICY mask_email_by_consent_policy
ON SCHEMA abac_tutorial.customers
COLUMN MASK mask_email_by_consent
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'email') AS email_col,
  has_tag('consent') AS consent_col
ON COLUMN email_col
USING COLUMNS (consent_col);
```

Diese Policy zeigt die E-Mail nur an, wenn `has_consent = TRUE` ist — sonst wird sie teilweise maskiert.

## Aufräumen

Am Ende des Tutorials werden Policies, Funktionen und Tabellen wieder per SQL entfernt (`DROP POLICY`, `DROP FUNCTION`, `DROP TABLE`).

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/tutorial-sql
