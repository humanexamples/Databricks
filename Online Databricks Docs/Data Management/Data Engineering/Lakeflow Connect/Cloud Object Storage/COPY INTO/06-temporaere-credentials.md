# COPY INTO mit temporären Zugangsdaten

Diese Seite beschreibt, wie `COPY INTO` mit temporären Zugangsdaten Daten aus externem Cloud-Object-Storage in Delta-Lake-Tabellen lädt, wenn Cluster oder SQL-Warehouse keine direkten Berechtigungen besitzen.

## Zugangsdaten- und Verschlüsselungsoptionen

Hinweis: Zugangsdaten- und Verschlüsselungsoptionen sind ab Databricks Runtime 10.4 LTS verfügbar.

`COPY INTO` unterstützt folgende Arten von Zugangsdaten:

- **Azure-SAS-Tokens** für den Zugriff auf ADLS und Azure Blob Storage. Tokens für Azure Blob Storage wirken auf Container-Ebene, Tokens für ADLS können auf Verzeichnis- oder Container-Ebene wirken. Databricks empfiehlt SAS-Tokens auf Verzeichnisebene. Tokens müssen die Rechte "Read" und "List" enthalten.
- **AWS-STS-Tokens** für den Zugriff auf S3. Tokens sollten die Rechte `s3:GetObject*`, `s3:ListBucket` und `s3:GetBucketLocation` besitzen.

Warnung: Um Missbrauch oder Offenlegung von Zugangsdaten zu vermeiden, sollten Ablaufzeiten so kurz wie möglich gewählt werden – gerade lang genug, um die Aufgabe abzuschließen.

`COPY INTO` unterstützt außerdem das Laden verschlüsselter Daten aus AWS S3, indem Verschlüsselungstyp und Entschlüsselungsschlüssel angegeben werden.

## Daten mit temporären Zugangsdaten laden

Beispiel für S3 mit AWS-Zugangsdaten:

```sql
%sql
COPY INTO my_json_data
FROM 's3://my-bucket/jsonData' WITH (
  CREDENTIAL (AWS_ACCESS_KEY = '...', AWS_SECRET_KEY = '...', AWS_SESSION_TOKEN = '...'))
FILEFORMAT = JSON
```

Beispiel für ADLS mit einem Azure-SAS-Token:

```sql
%sql
COPY INTO my_json_data
FROM 'abfss://container@storageAccount.dfs.core.windows.net/jsonData' WITH (
  CREDENTIAL (AZURE_SAS_TOKEN = '...'))
FILEFORMAT = JSON
```

## Verschlüsselte Daten laden

Beispiel für das Laden verschlüsselter Daten aus S3:

```sql
%sql
COPY INTO my_json_data
FROM 's3://my-bucket/jsonData' WITH (
  ENCRYPTION (TYPE = 'AWS_SSE_C', MASTER_KEY = '...'))
FILEFORMAT = JSON
```

## JSON-Daten mit separaten Zugangsdaten für Quelle und Ziel laden

Dieses Beispiel lädt JSON-Daten aus S3 in eine externe Delta-Tabelle und verwendet dabei unterschiedliche Zugangsdaten für Lese- und Schreibvorgang:

```sql
%sql
COPY INTO my_json_data WITH (CREDENTIAL target_credential)
  FROM 's3://my-bucket/jsonData' WITH (CREDENTIAL source_credential)
  FILEFORMAT = JSON
  FILES = ('f.json')
```

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/temporary-credentials  
**Stand:** 2026-08-07
