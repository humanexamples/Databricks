[← Übersicht](../00%20Uebersicht.md)

# Temporäre Credentials und Verschlüsselung

Dieser Weg ist gedacht, wenn der Cluster oder das SQL Warehouse **keine Leserechte** auf die Quelldateien hat. Du gibst die Zugangsdaten dann direkt im Befehl mit. Credential- und Verschlüsselungsoptionen gibt es ab Databricks Runtime 10.4 LTS.

---

## Welche temporären Credentials gibt es?

**AWS STS-Token für S3:**
- Optionen: `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_SESSION_TOKEN`
- Nötige Rechte: `s3:GetObject*`, `s3:ListBucket`, `s3:GetBucketLocation`

**Azure SAS-Token für ADLS und Azure Blob Storage:**
- Option: `AZURE_SAS_TOKEN`
- Der Token braucht die Rechte **Read** und **List**.
- Bei Blob Storage gilt der Token für den ganzen Container. Bei ADLS kann er auch auf ein Verzeichnis beschränkt sein. Databricks empfiehlt Token auf Verzeichnisebene.

**Sicherheit:** Die Gültigkeit sollte nur so lang sein, wie die Aufgabe dauert.

---

## Mit temporären Credentials laden

**S3**

```sql
COPY INTO my_json_data
FROM 's3://my-bucket/jsonData' WITH (
  CREDENTIAL (AWS_ACCESS_KEY = '...', AWS_SECRET_KEY = '...', AWS_SESSION_TOKEN = '...')
)
FILEFORMAT = JSON;
```

**ADLS**

```sql
COPY INTO my_json_data
FROM 'abfss://container@storageAccount.dfs.core.windows.net/jsonData' WITH (
  CREDENTIAL (AZURE_SAS_TOKEN = '...')
)
FILEFORMAT = JSON;
```

Quell-Credentials gehen nur mit den Schemata `s3`, `s3n`, `s3a`, `wasbs` und `abfss`. Bei anderen Schemata kommt der Fehler `COPY_INTO_CREDENTIALS_NOT_ALLOWED_ON`.

---

## Verschlüsselte Daten laden (S3, SSE-C)

Du gibst die Art der Verschlüsselung und den Schlüssel an.

```sql
COPY INTO my_json_data
FROM 's3://my-bucket/jsonData' WITH (
  ENCRYPTION (TYPE = 'AWS_SSE_C', MASTER_KEY = '...')
)
FILEFORMAT = JSON;
```

Verschlüsselung geht nur mit `s3`, `s3n`, `s3a` und `abfss`. Unter Azure geht sie nur mit ADLS Gen2 (`abfss://`).

---

## Benannte Credentials für Quelle und Ziel

Ein Befehl kann zwei verschiedene gespeicherte Credentials nutzen: eine zum **Schreiben** in eine externe Delta-Tabelle und eine zum **Lesen** aus S3.

```sql
COPY INTO my_json_data WITH (CREDENTIAL target_credential)
  FROM 's3://my-bucket/jsonData' WITH (CREDENTIAL source_credential)
  FILEFORMAT = JSON
  FILES = ('f.json');
```

Eine benannte Credential brauchst du nur, wenn der Pfad **nicht** in einer External Location liegt.

---

## Typische Syntaxfehler

- **`COPY_INTO_SYNTAX_ERROR.CREDENTIAL_SYNTAX`**: Credentials müssen an der Quelle mit `WITH (CREDENTIAL ...)` stehen.
- **`COPY_INTO_SYNTAX_ERROR.ENCRYPTION_SYNTAX`**: Die Verschlüsselung muss an der Quelle mit `WITH (ENCRYPTION ...)` stehen.
- **`COPY_INTO_CREDENTIALS_REQUIRED`**: In der Credential fehlen Pflichtschlüssel. Die Meldung nennt die erwarteten Schlüssel.

```sql
-- richtig: Credential direkt an der Quelle
FROM 's3://my-bucket/jsonData' WITH (CREDENTIAL (AWS_ACCESS_KEY = '...', AWS_SECRET_KEY = '...', AWS_SESSION_TOKEN = '...'))
```

---

## Temporäre Credentials erzeugen (AWS, Kurzfassung)

Das erledigt meist ein Cloud-Admin.

**1. IAM-Policy mit reinem Lesezugriff anlegen**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadOnlyAccessToTrips",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": ["arn:aws:s3:::<s3-bucket>", "arn:aws:s3:::<s3-bucket>/<folder>/*"]
    }
  ]
}
```

**2. IAM-User anlegen:** mit programmatischem Zugriff und dieser Policy. Access Key ID und Secret Access Key sicher ablegen.

**3. Named Profile in der AWS CLI anlegen und testen:**

```bash
aws s3 ls s3://<s3-bucket>/<folder>/ --profile <named-profile>
```

**4. Session-Token holen:**

```bash
aws sts get-session-token --profile <named-profile>
```

Die Werte `AccessKeyId`, `SecretAccessKey` und `SessionToken` aus der Ausgabe kommen in `CREDENTIAL (...)`.
