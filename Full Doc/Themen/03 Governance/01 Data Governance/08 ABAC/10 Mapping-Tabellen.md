# Mapping-Tabellen für dynamische Zugriffskontrolle

Muster zur Verwaltung von Row- und Column-Level-Zugriff über eine **einzige Lookup-Tabelle** — statt über zahlreiche Gruppen (z. B. 16+ Gruppen für Region-Abteilungs-Kombinationen). Zugriffsänderungen erfolgen über einfache Zeilen-Updates statt über Policy-Änderungen.

## Mapping-Tabelle

```sql
CREATE OR REPLACE TABLE abac_tutorial.mapping_demo.user_access (
  user_email STRING,
  region STRING,
  department STRING,
  pii_access STRING,
  expires_on DATE);

INSERT INTO abac_tutorial.mapping_demo.user_access VALUES
  (current_user(),      'us_east', 'engineering', 'masked', '2099-12-31'),
  ('bob@example.com',   'us_west', 'sales',       'full',   '2099-12-31'),
  ('carol@example.com', 'eu',      'engineering', 'none',   '2099-12-31'),
  ('david@example.com', 'apac',    'marketing',   'masked', '2099-12-31');
```

Das Feld `expires_on` ermöglicht automatischen Zugriffsentzug ohne manuellen Eingriff.

## Row-Filter-UDF

```sql
CREATE OR REPLACE FUNCTION abac_tutorial.mapping_demo.access_filter(
  region_val STRING,
  dept_val STRING)
RETURNS BOOLEAN
RETURN EXISTS (
  SELECT 1 FROM abac_tutorial.mapping_demo.user_access
  WHERE user_email = current_user()
    AND region = region_val
    AND department = dept_val
    AND expires_on >= current_date());
```

## Column-Mask-UDF (bedingte Maskierung)

Maskiert PII abhängig von der Freigabestufe des Nutzers **und** der Priorität der Zeile — als `confidential` markierte Bestellungen werden unabhängig von der Freigabestufe des Nutzers vollständig geschwärzt:

```sql
CREATE OR REPLACE FUNCTION abac_tutorial.mapping_demo.pii_mask(
  val STRING,
  pii_type STRING,
  order_pri STRING)
RETURNS STRING
RETURN CASE
  WHEN order_pri = 'confidential' THEN '***REDACTED***'
  WHEN EXISTS (
    SELECT 1 FROM abac_tutorial.mapping_demo.user_access
    WHERE user_email = current_user() AND pii_access = 'full'
  ) THEN val
  WHEN EXISTS (
    SELECT 1 FROM abac_tutorial.mapping_demo.user_access
    WHERE user_email = current_user() AND pii_access = 'masked'
  ) THEN
    CASE pii_type
      WHEN 'email' THEN CONCAT(LEFT(val, 1), '***@', SUBSTRING_INDEX(val, '@', -1))
      WHEN 'name'  THEN CONCAT(LEFT(val, 1), '***')
      ELSE CONCAT(LEFT(val, 1), '***')
    END
  ELSE '***REDACTED***'
END;
```

## Policies

```sql
CREATE POLICY user_access_filter
ON SCHEMA abac_tutorial.mapping_demo
ROW FILTER abac_tutorial.mapping_demo.access_filter
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag('region') AS r, has_tag('department') AS d
USING COLUMNS (r, d);

CREATE POLICY pii_mask_name
ON SCHEMA abac_tutorial.mapping_demo
COLUMN MASK abac_tutorial.mapping_demo.pii_mask
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'name') AS m,
  has_tag('priority') AS pri
ON COLUMN m
USING COLUMNS ('name', pri);

CREATE POLICY pii_mask_email
ON SCHEMA abac_tutorial.mapping_demo
COLUMN MASK abac_tutorial.mapping_demo.pii_mask
TO `account users`
FOR TABLES
MATCH COLUMNS has_tag_value('pii', 'email') AS m,
  has_tag('priority') AS pri
ON COLUMN m
USING COLUMNS ('email', pri);
```

## Vorteile

- **Skalierbarkeit:** neue Regionen/Abteilungen erfordern nur neue Tabellenzeilen, keine neuen Gruppen.
- **Wartbarkeit:** Zugriffsänderungen aktualisieren Mapping-Tabellen-Einträge, nicht Policies oder UDFs.
- **Flexibilität:** Nutzer können über mehrere Zeilen Zugriff auf mehrere Region-Abteilungs-Kombinationen erhalten.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/mapping-tables
