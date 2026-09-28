# Grant-Rezepte für häufige Szenarien

Vollständige, kopierbare `GRANT`-Kombinationen für wiederkehrende Zugriffs-Anforderungen — jeweils unter Berücksichtigung der `USE CATALOG`/`USE SCHEMA`-Kette aus [Schluesselprivilegien im Detail.md](Schluesselprivilegien%20im%20Detail.md).

## a) Nutzer/Gruppe soll eine Tabelle nur lesen können

```sql
GRANT USE CATALOG ON CATALOG main TO `data-consumers`;
GRANT USE SCHEMA ON SCHEMA main.default TO `data-consumers`;
GRANT SELECT ON TABLE main.default.department TO `data-consumers`;
```

Alternative, kompakter über Vererbung: `SELECT` auf dem gesamten Schema statt auf einer einzelnen Tabelle vergeben — gilt dann automatisch für alle aktuellen und künftigen Tabellen/Views darin:

```sql
GRANT USE CATALOG ON CATALOG main TO `data-consumers`;
GRANT USE SCHEMA ON SCHEMA main.default TO `data-consumers`;
GRANT SELECT ON SCHEMA main.default TO `data-consumers`;
```

*Quelle: Tutorial-Beispiel `GRANT SELECT ON TABLE default.department TO \`data-consumers\`;`*

## b) Nutzer/Gruppe soll neue Tabellen in einem Schema anlegen können

```sql
GRANT CREATE TABLE ON SCHEMA main.default TO `finance-team`;
GRANT USE SCHEMA ON SCHEMA main.default TO `finance-team`;
GRANT USE CATALOG ON CATALOG main TO `finance-team`;
```

## c) Nutzer/Gruppe soll Dateien aus einem Volume lesen bzw. lesen+schreiben können

```sql
-- Nur Lesezugriff
GRANT READ VOLUME ON VOLUME unstructured_data_lab.raw.files_volume
TO `<user-or-group-name>`;

-- Lese- und Schreibzugriff
GRANT READ VOLUME, WRITE VOLUME ON VOLUME unstructured_data_lab.raw.files_volume
TO `<user-or-group-name>`;

-- Alle Privilegien auf dem Volume
GRANT ALL PRIVILEGES ON VOLUME unstructured_data_lab.raw.files_volume
TO `<user-or-group-name>`;
```

Zusätzlich (analog zu a/b) auf den Elternobjekten nötig:

```sql
GRANT USE CATALOG ON CATALOG unstructured_data_lab TO `<user-or-group-name>`;
GRANT USE SCHEMA ON SCHEMA unstructured_data_lab.raw TO `<user-or-group-name>`;
```

Aktuelle Rechte auf dem Volume anzeigen:

```sql
SHOW GRANTS ON VOLUME unstructured_data_lab.raw.files_volume;
```

*Quelle: Tutorial „Work with unstructured data in volumes".*

## d) Ein Volume selbst anlegen können (managed oder external)

```sql
-- Voraussetzung für ein managed Volume
GRANT USE CATALOG ON CATALOG main TO `data-engineers`;
GRANT USE SCHEMA ON SCHEMA main.bronze TO `data-engineers`;
GRANT CREATE VOLUME ON SCHEMA main.bronze TO `data-engineers`;

CREATE VOLUME main.bronze.landing_files;
```

```sql
-- Zusätzlich für ein external Volume
GRANT CREATE EXTERNAL VOLUME ON EXTERNAL LOCATION my_ext_location TO `data-engineers`;

CREATE EXTERNAL VOLUME main.bronze.landing_files_ext
LOCATION 's3://my-bucket/landing/';
```

*Quelle: Tabelle „Required permissions" auf der Volumes-Utility-Commands-Seite.*

## e) Per `read_files`/`COPY INTO` aus einer External Location oder einem Volume laden

Voraussetzung: `READ VOLUME`-Privileg auf einem Volume **oder** `READ FILES`-Privileg auf einer External Location, plus `USE SCHEMA` auf dem Schema der Ziel-Table und `USE CATALOG` auf dem übergeordneten Catalog.

```sql
-- Laden aus einem Volume
GRANT USE CATALOG ON CATALOG quickstart_catalog TO `data-engineers`;
GRANT USE SCHEMA ON SCHEMA quickstart_catalog.quickstart_schema TO `data-engineers`;
GRANT READ VOLUME ON VOLUME quickstart_catalog.quickstart_schema.quickstart_volume TO `data-engineers`;

COPY INTO quickstart_catalog.quickstart_schema.landing_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data'
FILEFORMAT = PARQUET;
```

```sql
-- Laden aus einer External Location
GRANT USE CATALOG ON CATALOG quickstart_catalog TO `data-engineers`;
GRANT USE SCHEMA ON SCHEMA quickstart_catalog.quickstart_schema TO `data-engineers`;
GRANT READ FILES ON EXTERNAL LOCATION my_ext_location TO `data-engineers`;

COPY INTO my_json_data
FROM 'abfss://container@storageAccount.dfs.core.windows.net/jsonData'
FILEFORMAT = JSON;
```

**Wichtige Einschränkung zur External-Location-Vererbung:** Berechtigungen auf einer External Location gewähren keine Privilegien auf Verzeichnissen oberhalb oder parallel zum angegebenen Pfad — sie gelten nur für den definierten Pfad und dessen Unterverzeichnisse.

Für `read_files` gilt dieselbe Grundregel:

```sql
GRANT READ FILES, WRITE FILES ON EXTERNAL LOCATION <location-name> TO <principal>;

SELECT * FROM read_files('s3://<bucket>/<path>', format => 'csv');
```

*Quelle: „Load data using COPY INTO with Unity Catalog volumes or external locations".*

## f) Neue externe Tabelle direkt an einem Cloud-Speicherpfad anlegen

```sql
GRANT USE CATALOG ON CATALOG main TO `data-engineers`;
GRANT USE SCHEMA ON SCHEMA main.bronze TO `data-engineers`;
GRANT CREATE TABLE ON SCHEMA main.bronze TO `data-engineers`;
GRANT CREATE EXTERNAL TABLE ON EXTERNAL LOCATION my_ext_location TO `data-engineers`;
```

## g) Ein „Data Engineer"-Rollenprofil: Bronze-Tabellen aus Cloud-Speicher bauen

**Methodik-Hinweis:** Für dieses zusammengesetzte Rollenprofil existiert **keine einzelne Doku-Seite**, die genau diese Kombination als „Minimalausstattung für einen Data Engineer" vorschreibt. Das folgende Beispiel ist eine eigene Zusammensetzung aus den einzeln verifizierten atomaren Anforderungen der Rezepte (b), (d) und (e) — kein wörtliches Doku-Zitat, sondern eine Ableitung.

```sql
-- 1. Zugriff auf Ziel-Catalog/-Schema (Bronze-Layer)
GRANT USE CATALOG ON CATALOG main TO `data-engineers`;
GRANT USE SCHEMA ON SCHEMA main.bronze TO `data-engineers`;

-- 2. Tabellen im Bronze-Schema anlegen und befüllen dürfen
GRANT CREATE TABLE ON SCHEMA main.bronze TO `data-engineers`;
GRANT SELECT, MODIFY ON SCHEMA main.bronze TO `data-engineers`;

-- 3a. Rohdaten aus einem Volume lesen (empfohlener Weg)
GRANT READ VOLUME ON VOLUME main.landing.raw_files TO `data-engineers`;

-- 3b. Alternativ: Rohdaten direkt aus einer External Location lesen
-- GRANT READ FILES ON EXTERNAL LOCATION my_ext_location TO `data-engineers`;
```

## h) Rechte wieder entziehen (`REVOKE`)

Gleiche Syntax wie `GRANT`, nur mit `FROM` statt `TO`:

```sql
REVOKE CREATE TABLE ON SCHEMA main.default FROM `finance-team`;
REVOKE WRITE VOLUME ON VOLUME main.bronze.landing_files FROM `data-engineers`;
REVOKE ALL PRIVILEGES ON SCHEMA default FROM `alf@melmak.et`;
```

Ein `REVOKE` schlägt nicht fehl, selbst wenn die Berechtigung vorher nie erteilt wurde (siehe [GRANT, REVOKE und SHOW GRANTS.md](GRANT%2C%20REVOKE%20und%20SHOW%20GRANTS.md)).

## Quellen

- https://docs.databricks.com/aws/en/getting-started/create-table
- https://docs.databricks.com/aws/en/data-governance/unity-catalog/manage-privileges/
- https://docs.databricks.com/aws/en/volumes/utility-commands
- https://docs.databricks.com/aws/en/volumes/unstructured-data-tutorial
- https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/unity-catalog
