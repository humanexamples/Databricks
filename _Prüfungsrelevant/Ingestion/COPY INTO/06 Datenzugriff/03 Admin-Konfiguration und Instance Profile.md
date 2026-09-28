[← Übersicht](../00%20Uebersicht.md)

# Admin-Konfiguration und Instance Profile

Bevor Nutzer `COPY INTO` ausführen können, muss ein Admin den Zugriff auf den Cloud-Speicher einrichten.

## Die vier Wege, den Zugriff einzurichten

1. **Unity-Catalog-Volume anlegen** (empfohlen). Die Nutzer brauchen `READ VOLUME`.
2. **External Location mit Storage Credential** anlegen. Die Nutzer brauchen `READ FILES`.
3. **Compute mit AWS Instance Profile** konfigurieren. Dafür sind Workspace-Admin-Rechte nötig.
4. **Temporäre Credentials** (Access Key ID, Secret Key, Session Token) erzeugen und an die Nutzer weitergeben.

Welcher Befehl danach zu welchem Weg passt:

- Weg 1 und 2 → [01 Volumes und External Locations](01%20Volumes%20und%20External%20Locations.md)
- Weg 3 → unten und im Tutorial [07 Tutorials](../07%20Tutorials.md)
- Weg 4 → [02 Temporäre Credentials](02%20Temporaere%20Credentials%20und%20Verschluesselung.md)

---

## COPY INTO mit Instance Profile

Das SQL Warehouse nutzt ein Instance Profile, das S3 lesen darf. Im Befehl stehen dann keine Credentials.

Voraussetzungen:
- ein SQL Warehouse mit diesem Instance Profile
- das Recht **Can manage** auf dem SQL Warehouse
- die vollständige S3-URI

**Zugriff testen:**

```sql
select * from csv.`s3://<bucket>/<folder>/`
```

**Laden:**

```sql
COPY INTO <catalog-name>.<schema-name>.<table-name>
FROM 's3://<s3-bucket>/<folder>/'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');
```

---

## Aufräumen

- das AWS-CLI-Profil aus `~/.aws/credentials` entfernen (Windows: `%USERPROFILE%\.aws\credentials`)

```
[<named-profile>]
aws_access_key_id = <access-key-id>
aws_secret_access_key = <secret-access-key>
```

- IAM-User und IAM-Policy in der IAM-Konsole löschen
- den S3-Bucket leeren und löschen, falls er nicht mehr gebraucht wird
- das SQL Warehouse stoppen, damit keine Kosten entstehen

---

## Hinweis zu S3 und AWS GuardDuty

`COPY INTO` schreibt wie Delta Lake, Structured Streaming und Auto Loader über den **S3 Commit Service** der Databricks Control Plane. Den braucht es, weil S3 keine Operation „nur schreiben, wenn das Objekt noch nicht existiert“ hat. Schreiben mehrere Cluster gleichzeitig, sichert der Dienst die Commits zentral ab.

Wer Daten über IAM Instance Profiles liest und AWS GuardDuty nutzt, kann deshalb Warnungen zum Abfluss von Instance-Credentials sehen. Das ist normales Databricks-Verhalten. Commits auf Tabellen, die Unity Catalog verwaltet, lösen diese Warnungen nicht aus.
