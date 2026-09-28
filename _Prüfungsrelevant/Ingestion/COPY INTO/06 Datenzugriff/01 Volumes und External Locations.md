[← Übersicht](../00%20Uebersicht.md)

# Datenzugriff über Unity-Catalog-Volumes und External Locations

## Die vier Zugriffswege

1. **Unity-Catalog-Volume** – von Databricks empfohlen
2. **External Location** mit Storage Credential – unterstützt, aber nicht empfohlen
3. **Instance Profile** auf dem Compute – siehe [03 Admin-Konfiguration](03%20Admin-Konfiguration%20und%20Instance%20Profile.md)
4. **Temporäre Credentials** im Befehl – siehe [02 Temporäre Credentials](02%20Temporaere%20Credentials%20und%20Verschluesselung.md)

---

## Benötigte Rechte

- `READ VOLUME` auf dem Volume **oder** `READ FILES` auf der External Location
- `USE SCHEMA` auf dem Schema der Zieltabelle
- `USE CATALOG` auf dem übergeordneten Katalog

```sql
GRANT USE CATALOG ON CATALOG quickstart_catalog TO `data_engineers`;
GRANT USE SCHEMA  ON SCHEMA  quickstart_catalog.quickstart_schema TO `data_engineers`;
GRANT READ VOLUME ON VOLUME  quickstart_catalog.quickstart_schema.quickstart_volume TO `data_engineers`;
```

---

## Aus einem Volume laden

Das Recht auf ein Volume gilt für **alle Unterordner** darin.

```sql
COPY INTO landing_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data'
FILEFORMAT = PARQUET;

COPY INTO json_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data/json'
FILEFORMAT = JSON;
```

Das Präfix `dbfs:` funktioniert auch (`dbfs:/Volumes/...`). Empfohlen ist aber die Form `/Volumes/...`.

---

## Über eine External Location laden

Du gibst die Cloud-URL an. Credentials sind nicht nötig, weil die External Location den Zugriff regelt.

```sql
COPY INTO my_json_data
FROM 's3://landing-bucket/json-data'
FILEFORMAT = JSON;
```

**Die Rechte werden nur nach unten vererbt.** Angenommen, die External Location ist `s3://landing-bucket/raw-data`.

Das geht, weil es derselbe Ordner oder ein Unterordner ist:

```sql
COPY INTO landing_table FROM 's3://landing-bucket/raw-data'      FILEFORMAT = PARQUET;
COPY INTO json_table    FROM 's3://landing-bucket/raw-data/json' FILEFORMAT = JSON;
```

Das geht **nicht**, weil der Ordner darüber oder daneben liegt:

```sql
COPY INTO parent_table  FROM 's3://landing-bucket'           FILEFORMAT = PARQUET;  -- darüber
COPY INTO sibling_table FROM 's3://landing-bucket/json-data' FILEFORMAT = JSON;     -- daneben
```

---

## Dreiteiliger Name für die Zieltabelle

```sql
COPY INTO quickstart_catalog.quickstart_schema.landing_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data'
FILEFORMAT = PARQUET;
```

Oder du setzt vorher Katalog und Schema:

```sql
USE CATALOG quickstart_catalog;
USE SCHEMA quickstart_schema;

COPY INTO landing_table
FROM '/Volumes/quickstart_catalog/quickstart_schema/quickstart_volume/raw_data'
FILEFORMAT = PARQUET;
```

---

## Managed oder External Volume?

**External Volume** empfiehlt sich für:
- Landing-Bereiche für Rohdaten aus fremden Systemen
- Staging-Orte für die Ingestion mit Auto Loader, `COPY INTO` oder CTAS
- allgemein, wenn Daten beim Laden an einen anderen Ort **kopiert** werden

**Managed Volume** empfiehlt sich für:
- die meisten Anwendungsfälle, weil es die Unity-Catalog-Governance voll nutzt
- wenn du Tabellen aus Dateien im Volume erzeugen willst, **ohne** `COPY INTO` oder CTAS auszuführen

Weitere Hinweise:
- Lege External Volumes am besten aus **einer** External Location innerhalb **eines** Schemas an.
- Willst du Daten ohne Kopie an Ort und Stelle abfragen, nimm eine **External Table** statt eines Volumes.

```sql
-- External Volume als Landing Zone
CREATE EXTERNAL VOLUME main.raw.landing
LOCATION 's3://landing-bucket/raw-data';

COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');
```

---

## Beispiel mit ADLS (abfss)

```sql
CREATE TABLE <database-name>.<table-name>;

COPY INTO <database-name>.<table-name>
FROM 'abfss://container@storageAccount.dfs.core.windows.net/path/to/folder'
FILEFORMAT = CSV
COPY_OPTIONS ('mergeSchema' = 'true');
```
