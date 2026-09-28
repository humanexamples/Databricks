# Mounts und Migration

DBFS Mounts verbanden Workspaces mit Cloud-Object-Storage über vertraute Dateipfade unter `/mnt` — ein bequemes, aber inzwischen veraltetes Muster. Dieses Dokument behandelt die Mount-Syntax für Referenzzwecke, das Zusammenspiel von DBFS mit Unity Catalog, und wie sich DBFS Root und Mounts kontrolliert deaktivieren lassen. Basierend auf offiziellen Databricks-Doku-Seiten (jeweils am Ende jedes Abschnitts referenziert). Baut auf [DBFS Grundlagen.md](DBFS%20Grundlagen.md) auf. Für die übrigen, allgemeinen `dbutils.fs`-Befehle (`ls`, `cp`, `mv`, `rm`, `mkdirs`, `head`, `put`) und die `%fs`-Kurzform siehe [dbutils.fs — Befehlsreferenz.md](dbutils.fs%20%E2%80%94%20Befehlsreferenz.md).

## Abschnittsübersicht

1. [DBFS und Unity Catalog: Best Practices](#unity-catalog)
2. [Was sind DBFS Mounts?](#was-sind-mounts)
3. [`dbutils.fs.mount`-Syntax](#mount-syntax)
4. [Storage unmounten](#unmount)
5. [S3-Bucket-Mounting-Methoden](#s3-mounting)
6. [Azure ADLS/Blob Storage mounten](#azure-mounting)
7. [DBFS Root und Mounts deaktivieren](#deaktivieren)
8. [Zusammenfassung](#zusammenfassung)

---

## <a id="unity-catalog">1. DBFS und Unity Catalog: Best Practices</a>

### 1.1 Grundsätzliche Empfehlung

„Sowohl DBFS Root als auch DBFS Mounts sind veraltet und werden von Databricks nicht empfohlen." Die Plattform empfiehlt stattdessen Unity Catalog Volumes, External Locations oder Workspace Files (siehe [Unity Catalog Volumes.md](../Unity%20Catalog%20Volumes.md) und [Datei-Speicheroptionen und Workspace Files.md](../Datei-Speicheroptionen%20und%20Workspace%20Files.md)).

### 1.2 Wie DBFS in Unity-Catalog-Umgebungen funktioniert

- **In Legacy-Systemen:** Aktionen auf `hive_metastore`-Tabellen nutzen Legacy-Datenzugriffsmuster, mit Managed Tables, die im DBFS Root gespeichert sind.
- **Dedicated Access Mode:** Compute-Ressourcen haben vollen DBFS-Zugriff, einschließlich aller Root-Dateien und gemounteter Daten.
- **Standard Access Mode:** Zugriff erfordert explizite Berechtigungen. Direkte Dateiinteraktion verlangt `ANY FILE`-Berechtigungen — Databricks warnt davor, diese breit zu vergeben, da sie „Legacy-Table-ACLs im `hive_metastore` umgeht und Zugriff auf alle von DBFS verwalteten Daten gewährt."

### 1.3 Kritische Best Practices

1. **DBFS nicht mit External Locations kombinieren:** Cloud-Object-Storage-Volumes nicht zwischen DBFS-Mounts und UC-External-Volumes wiederverwenden, besonders nicht workspace- oder kontoübergreifend.
2. **Managed Storage absichern:** neue Storage-Accounts/Buckets nutzen, eigene Identity-Policies definieren, Zugriff exklusiv auf Databricks-verwaltete Unity-Catalog-Ressourcen beschränken.
3. **DBFS Root niemals als External Location laden:** das Laden von DBFS-Root-Storage als UC-External-Location stellt ein Sicherheitsrisiko dar.
4. **Cluster-Konfigurationen werden ignoriert:** Hadoop-Filesystem-Einstellungen gelten nicht für den Unity-Catalog-Filesystem-Zugriff.
5. **Pfad-Zugriffs-Einschränkung:** Pfade mit Eltern-/Kind-Beziehung können innerhalb einer einzelnen Notebook-Zelle nicht über unterschiedliche Zugriffsmethoden angesprochen werden.

### Quelle

- https://docs.databricks.com/aws/en/dbfs/unity-catalog

---

## <a id="was-sind-mounts">2. Was sind DBFS Mounts?</a>

DBFS Mounts erzeugen Verknüpfungen zwischen Workspaces und Cloud-Object-Storage, die Interaktion über vertraute Dateipfade unter `/mnt` ermöglichen. Mounts speichern Speicherort-URIs, Treiber-Spezifikationen und Sicherheits-Credentials, sodass Nutzer ohne Cloud-Kenntnisse nahtlos auf Daten zugreifen können.

**Deprecation-Hinweis:** DBFS Mounts sind ein veraltetes Muster, das mit Serverless Compute inkompatibel ist. Neue Konten haben keinen Zugriff mehr auf dieses Feature. Databricks empfiehlt die Migration zu Unity-Catalog-External-Locations.

### Quelle

- https://docs.databricks.com/aws/en/dbfs/mounts

---

## <a id="mount-syntax">3. `dbutils.fs.mount`-Syntax</a>

```python
dbutils.fs.mount(
  source: str,
  mount_point: str,
  encryption_type: Optional[str] = "",
  extra_configs: Optional[dict[str:str]] = None
)
```

Parameter: `source` (Object-Storage-URI), `mount_point` (lokaler `/mnt`-Pfad), optionaler `encryption_type`, zusätzliche Konfigurationen als Dictionary.

### Quelle

- https://docs.databricks.com/aws/en/dbfs/mounts

---

## <a id="unmount">4. Storage unmounten</a>

```python
dbutils.fs.unmount("/mnt/<mount-name>")
```

**Warnung:** Mounts nicht während aktiver Lese-/Schreibvorgänge ändern. `dbutils.fs.refreshMounts()` auf anderen Clustern ausführen, um Updates zu propagieren.

### Quelle

- https://docs.databricks.com/aws/en/dbfs/mounts

---

## <a id="s3-mounting">5. S3-Bucket-Mounting-Methoden</a>

### 5.1 Instance-Profile-Authentifizierung

```python
aws_bucket_name = "<aws-bucket-name>"
mount_name = "<mount-name>"
dbutils.fs.mount(f"s3a://{aws_bucket_name}", f"/mnt/{mount_name}")
display(dbutils.fs.ls(f"/mnt/{mount_name}"))
```

### 5.2 AWS-Keys-Authentifizierung

```python
access_key = dbutils.secrets.get(scope = "aws", key = "aws-access-key")
secret_key = dbutils.secrets.get(scope = "aws", key = "aws-secret-key")
encoded_secret_key = secret_key.replace("/", "%2F")
dbutils.fs.mount(f"s3a://{access_key}:{encoded_secret_key}@{aws_bucket_name}",
                  f"/mnt/{mount_name}")
```

**Wichtig:** Bei Key-basierten Mounts erhalten alle Workspace-Nutzer Lese-/Schreibzugriff auf alle Bucket-Objekte.

### 5.3 AssumeRole-Policy

```python
dbutils.fs.mount("s3a://<s3-bucket-name>", "/mnt/<s3-bucket-name>",
  extra_configs = {
    "fs.s3a.credentialsType": "AssumeRole",
    "fs.s3a.stsAssumeRole.arn": "arn:aws:iam::<bucket-owner-acct-id>:role/MyRoleB",
    "fs.s3a.canned.acl": "BucketOwnerFullControl",
    "fs.s3a.acl.default": "BucketOwnerFullControl"
  })
```

### 5.4 S3-Verschlüsselungsoptionen

**SSE-S3-Verschlüsselung:**

```python
dbutils.fs.mount(s"s3a://$AccessKey:$SecretKey@$AwsBucketName",
                  s"/mnt/$MountName", "sse-s3")
```

**SSE-KMS-Verschlüsselung:**

```python
# Standard-KMS-Key
dbutils.fs.mount(s"s3a://$AccessKey:$SecretKey@$AwsBucketName",
                  s"/mnt/$MountName", "sse-kms")

# Spezifischer KMS-Key
dbutils.fs.mount(s"s3a://$AccessKey:$SecretKey@$AwsBucketName",
                  s"/mnt/$MountName", "sse-kms:$KmsKey")
```

### 5.5 Databricks Commit Service für S3

```python
dbutils.fs.unmount("/mnt/<mount-name>")
dbutils.fs.mount("s3a://<bucket-name>/", "/mnt/<mount-name>",
  extra_configs = {
    "fs.s3a.credentialsType": "AssumeRole",
    "fs.s3a.stsAssumeRole.arn": "<role-arn>"
})
```

### Quelle

- https://docs.databricks.com/aws/en/dbfs/mounts

---

## <a id="azure-mounting">6. Azure ADLS/Blob Storage mounten</a>

```python
configs = {
  "fs.azure.account.auth.type": "OAuth",
  "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
  "fs.azure.account.oauth2.client.id": "<application-id>",
  "fs.azure.account.oauth2.client.secret": dbutils.secrets.get(scope="<scope-name>",
                                                                  key="<service-credential-key-name>"),
  "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/<directory-id>/oauth2/token"
}
dbutils.fs.mount(
  source = "abfss://<container-name>@<storage-account-name>.dfs.core.windows.net/",
  mount_point = "/mnt/<mount-name>",
  extra_configs = configs)
```

### Quelle

- https://docs.databricks.com/aws/en/dbfs/mounts

---

## <a id="deaktivieren">7. DBFS Root und Mounts deaktivieren</a>

### 7.1 Deaktivierung als Workspace-Admin

1. Im Databricks-Workspace anmelden.
2. Nutzerprofil-Icon (oben rechts) → **Settings** wählen.
3. Zu **Workspace admin** → **Security** navigieren.
4. **Disable DBFS root and mounts** auf „Disabled: DBFS root and mounts cannot be used" setzen.
5. Bis zu 20 Minuten auf die Propagierung warten.
6. Alle laufenden Cluster und SQL-Warehouses manuell neu starten.

**Wichtiger Hinweis:** „Es kann bis zu 20 Minuten dauern, bis die Deaktivierung von DBFS Root und Mounts vollständig propagiert ist" — Cluster müssen danach neu gestartet werden, damit die Änderungen wirksam werden.

### 7.2 Was bei Deaktivierung nicht mehr funktioniert

- Sämtlicher Lese-/Schreibzugriff auf DBFS Root und Mounts schlägt fehl, mit Fehlern wie „Public DBFS root is disabled".
- DBFS-Browser und Upload-Optionen werden unzugänglich.
- Jobs, Notebooks und Skripte, die diese Pfade referenzieren, schlagen fehl.
- Statische Notebook-Datei-Einbettung über `/files` liefert 500-Fehler.
- Mount-/Unmount-Operationen werden blockiert.
- FileStore-Operationen werden blockiert.
- Databricks-Runtime-Versionen unter 13.3 LTS werden deaktiviert.

### 7.3 Was weiterhin funktioniert

- Unity Catalog Volumes (über das `dbfs:/Volumes`-Präfix).
- System-Pfade wie `dbfs:/databricks-datasets/`.
- Interne Workspace-Systemdaten (Notebook-Revisionen, Job-Details, Spark-Logs).
- Bereits vorhandene DBFS-Daten bleiben intakt, sind aber bis zur Reaktivierung unzugänglich.

### 7.4 Voraussetzungen vor der Deaktivierung

- Alle Workflows zu Unity Catalog Volumes, External Locations oder Workspace Files migrieren.
- Alle Jobs und Cluster auf Databricks Runtime 13.3 LTS oder höher aktualisieren.
- Observability-Skripte in Betracht ziehen, um verbleibende DBFS-Nutzung zu identifizieren.

### Quelle

- https://docs.databricks.com/aws/en/dbfs/disable-dbfs-root-mounts

---

## <a id="zusammenfassung">8. Zusammenfassung</a>

- DBFS und Unity Catalog lassen sich zwar kombinieren (`ANY FILE`-Berechtigung für direkten Dateizugriff im Standard Access Mode), Databricks rät jedoch grundsätzlich davon ab, DBFS-Root-Storage als External Location wiederzuverwenden.
- **DBFS Mounts** verbinden Cloud-Storage über `/mnt`-Pfade mit dem Workspace — `dbutils.fs.mount()`/`unmount()` unterstützen Instance-Profile-, AWS-Key- und AssumeRole-Authentifizierung für S3 sowie OAuth für Azure ADLS/Blob Storage, jeweils mit optionalen SSE-S3-/SSE-KMS-Verschlüsselungsoptionen.
- Mounts sind mit Serverless Compute **inkompatibel** und werden vollständig durch Unity-Catalog-External-Locations ersetzt.
- **DBFS Root und Mounts lassen sich als Workspace-Admin über die Security-Einstellungen vollständig deaktivieren** — nach einer bis zu 20-minütigen Propagierungszeit und Cluster-Neustarts brechen alle darauf angewiesenen Legacy-Workflows, während Unity-Catalog-Volumes und interne Systempfade unbeeinträchtigt weiterlaufen. Vor der Deaktivierung sollte die vollständige Migration auf Unity Catalog Volumes, External Locations und Workspace Files sowie ein Runtime-Upgrade auf 13.3 LTS+ abgeschlossen sein.
