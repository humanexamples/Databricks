# Auto Loader — File Notification Mode

Es gibt zwei Varianten des File-Notification-Modus. Beide ermöglichen inkrementelle Datei-Erkennung im großen Maßstab (Millionen Dateien pro Stunde); der Unterschied liegt in Verwaltungsaufwand und Ressourcenzuteilung.

- **File Events (empfohlen):** Databricks richtet Abonnements und File Events im Cloud-Speicherkonto ein, ohne dass zusätzliche Zugangsdaten bereitgestellt werden müssen — eine gemeinsame Benachrichtigungswarteschlange **pro External Location** statt einer separaten Queue pro Stream.
- **Klassischer Modus:** Datei-Benachrichtigungs-Warteschlangen werden für jeden Auto-Loader-Stream separat verwaltet.

---

## Abschnitte

1. [File Events (empfohlen)](#file-events)
2. [Klassischer File-Notification-Modus](#klassischer-modus)
3. [Cloud-Ressourcen im klassischen Modus](#cloud-ressourcen)
4. [Berechtigungen je Cloud](#berechtigungen)
5. [Cross-Account-Ingestion (AWS)](#cross-account)
6. [Cloud Resource Manager: manuelles Einrichten und Aufräumen](#resource-manager)
7. [Troubleshooting](#troubleshooting)

---

## <a id="file-events">1. File Events (empfohlen)</a>

### Voraussetzungen

- Ein für Unity Catalog aktivierter Workspace.
- Berechtigung, Storage-Credential- und External-Location-Objekte in Unity Catalog anzulegen.
- Compute auf **Databricks Runtime 14.3 LTS oder höher**.
- File Events müssen auf der External Location aktiviert sein.

### Aktivierung

Über die Option `cloudFiles.useManagedFileEvents => true`, nachdem File Events auf der External Location aktiviert wurden:

```python
autoLoaderStream = (spark.readStream
  .format("cloudFiles")
  # ... weitere Optionen ...
  .option("cloudFiles.useManagedFileEvents", True)
  # ... weitere Optionen ...
  )
```

```sql
CREATE OR REFRESH STREAMING LIVE TABLE <table-name>
AS SELECT <select clause expressions>
  FROM STREAM read_files('abfss://path/to/external/location/or/volume',
                   format => '<format>',
                   useManagedFileEvents => 'True'
                   -- ... weitere Parameter ...
                   );
```

### Bei File Events nicht unterstützte Einstellungen

| Einstellung | Grund |
|---|---|
| `useIncremental` | Die Entscheidung zwischen der Effizienz von File Notifications und der Einfachheit von Directory Listing entfällt. |
| `useNotifications` | Es gibt nur eine Queue und ein Storage-Event-Abonnement pro External Location. |
| `cloudFiles.fetchParallelism` | Auto Loader mit File Events bietet keine manuelle Parallelitäts-Optimierung an. |
| `cloudFiles.backfillInterval` | Databricks handhabt Backfills automatisch für External Locations, die für File Events aktiviert sind. |
| `cloudFiles.pathRewrites` | Diese Option gilt nur, wenn externe Datenspeicherorte in DBFS gemountet werden — was veraltet ist. |
| `resourceTags` | Ressourcen-Tags sollten stattdessen über die Cloud-Konsole gesetzt werden. |

### Einschränkung: 7-Tage-Regel

Läuft Auto Loader mit File Events selten, kann der File-Events-Cache ablaufen, und Auto Loader fällt auf Directory Listing zurück, um Dateien zu erkennen und den Cache zu aktualisieren. Um dieses Szenario zu vermeiden, sollte Auto Loader **mindestens einmal alle sieben Tage** aufgerufen werden. Zusätzlich unterstützt Auto Loader mit File Events keine Pfad-Rewrites ("path rewrites").

### Best Practices für File Events

- **Volumes für optimale Datei-Erkennung:** Für bessere Performance ein eigenes External Volume für jeden Pfad bzw. jedes Unterverzeichnis anlegen, aus dem geladen wird. Volume-Pfade (`/Volumes/catalog/schema/volume`) statt Cloud-Speicher-URLs verwenden.
- **File-Arrival-Trigger statt Continuous:** Für ereignisgetriebene Pipelines einen File-Arrival-Trigger in Erwägung ziehen.
- **Trigger-Intervall bei Continuous-Triggern:** Werden dennoch Continuous-Trigger verwendet, das Trigger-Intervall auf **1 Minute oder höher** konfigurieren.
- File Events auf der External Location aktivieren, bevor die Streams konfiguriert werden.

---

## <a id="klassischer-modus">2. Klassischer File-Notification-Modus</a>

Im klassischen Modus etabliert Auto Loader dedizierte Benachrichtigungs- und Queue-Dienste für jeden einzelnen Stream. Auto Loader konsumiert Nachrichten aus der Benachrichtigungswarteschlange während der Dateiverarbeitung und löscht jede Nachricht aus der Warteschlange, nachdem die zugehörige Datei gelesen wurde.

---

## <a id="cloud-ressourcen">3. Cloud-Ressourcen im klassischen Modus</a>

| Cloud-Speicher | Subscription-Dienst | Queue-Dienst | Präfix | Limit |
|---|---|---|---|---|
| Amazon S3 | AWS SNS | AWS SQS | `databricks-auto-ingest` | 100 pro S3-Bucket |
| ADLS | Azure Event Grid | Azure Queue Storage | `databricks` | 500 pro Storage Account |
| GCS | Google Pub/Sub | Google Pub/Sub | `databricks-auto-ingest` | 100 pro GCS-Bucket |
| Azure Blob Storage | Azure Event Grid | Azure Queue Storage | `databricks` | 500 pro Storage Account |

Das Limit gibt an, wie viele **gleichzeitige** File-Notification-Pipelines gestartet werden können. Werden mehr benötigt, empfiehlt sich entweder File Events oder ein Fan-out-Dienst (AWS Lambda, Azure Functions, Google Cloud Functions). Dieser verteilt Benachrichtigungen aus einer einzelnen Queue, die einen ganzen Container/Bucket überwacht, in verzeichnisspezifische Queues.

### Cloud-spezifische Datei-Ereignisse

- **S3:** Amazon S3 liefert ein `ObjectCreated`-Ereignis, wenn eine Datei in einen S3-Bucket hochgeladen wird — unabhängig davon, ob dies per Put oder Multi-Part-Upload geschah.
- **ADLS:** Auto Loader lauscht auf das `FlushWithClose`-Ereignis zur Verarbeitung einer Datei. Unterstützt zudem `RenameFile` (erfordert einen API-Aufruf zum Ermitteln der Dateigröße) und `RenameDirectory` (ab Runtime 9.0, erfordert Directory-Listing-API-Aufrufe).
- **GCS:** Google Cloud Storage liefert ein `OBJECT_FINALIZE`-Ereignis, wenn eine Datei hochgeladen wird — dies schließt Überschreibungen und Datei-Kopien ein. Fehlgeschlagene Uploads erzeugen kein Ereignis.

**Zustellungs-Vorbehalt:** Cloud-Provider garantieren keine 100%ige Zustellung aller Datei-Ereignisse unter sehr seltenen Bedingungen und geben keine strikten SLAs für die Latenz der Datei-Ereignisse.

---

## <a id="berechtigungen">4. Erforderliche Berechtigungen je Cloud</a>

Es gibt vollständige IAM-Policy-JSONs pro Cloud-Provider. Hier die wesentlichen Bausteine:

- **Azure (ADLS/Blob Storage):** Ab Databricks Runtime 16.1 kann ein Databricks-Service-Credential verwendet werden; alternativ eine Microsoft-Entra-ID-App mit Service Principal. Benötigte eingebaute Rollen: **Contributor** (Einrichtung von Queues und Event-Subscriptions), **Storage Queue Data Contributor** (Queue-Operationen wie Abrufen/Löschen von Nachrichten), **EventGrid EventSubscription Contributor** (Event-Grid-Subscription-Operationen). Custom-Role-Berechtigungen umfassen Event-Grid-Subscription-Operationen (write/read/delete) und Queue-Service-/Message-Operationen (read/write/delete/process).
- **AWS (S3):** Eine vollständige Setup-Policy erlaubt u. a. `s3:GetBucketNotification`, `s3:PutBucketNotification`, `sns:ListSubscriptionsByTopic`, `sns:CreateTopic`, `sns:Subscribe`, `sqs:CreateQueue`, `sqs:DeleteMessage`, `sqs:ReceiveMessage`, `sqs:GetQueueUrl`, `sqs:GetQueueAttributes` auf Ressourcen mit dem Präfix `databricks-auto-ingest-*`. Nach der Ersteinrichtung lässt sich auf eine reduzierte "Use"-Policy umstellen, die keine Erstellungs-/Teardown-Rechte mehr benötigt.
- **GCS:** Erforderlich sind `list`- und `get`-Berechtigungen auf dem GCS-Bucket und allen Objekten sowie die Rolle **Pub/Sub Publisher** für das GCS-Service-Konto. Für den vollen Funktionsumfang wird zusätzlich eine benutzerdefinierte Rolle mit `pubsub.subscriptions.create/delete/get`, `pubsub.topics.create/delete/update` und `pubsub.topics.attachSubscription/detachSubscription` benötigt. Das GCS-Service-Konto findet sich in der Google Cloud Console unter *Cloud Storage > Settings* im Abschnitt *Cloud Storage Service Account*.

---

## <a id="cross-account">5. Cross-Account-Ingestion (AWS)</a>

Auto Loader kann Daten über AWS-Konten hinweg laden, indem eine IAM-Rolle per `AssumeRole` übernommen wird. Dafür muss die Spark-Konfiguration des Clusters entsprechend gesetzt werden:

```ini
fs.s3a.credentialsType AssumeRole
fs.s3a.stsAssumeRole.arn arn:aws:iam::<bucket-owner-acct-id>:role/MyRoleB
fs.s3a.acl.default BucketOwnerFullControl
```

Eine gesonderte, allgemeine Multi-Cloud-Konfiguration (eine Ingestion, die mehrere Cloud-Provider gleichzeitig kombiniert) ist nicht dokumentiert — nur die kontoübergreifende (Cross-Account) Konfiguration innerhalb von AWS. Ebenfalls nicht dokumentiert: KMS-Verschlüsselung speziell für File-Notification-Warteschlangen.

---

## <a id="resource-manager">6. Cloud Resource Manager: manuelles Einrichten und Aufräumen</a>

Auto Loader baut die im klassischen Modus angelegten Cloud-Ressourcen **nicht automatisch** wieder ab. Um File-Notification-Ressourcen abzubauen, muss der Cloud Resource Manager verwendet werden; alternativ lassen sich die Ressourcen manuell löschen.

Der Cloud Resource Manager wird über eine dedizierte API angesprochen (`CloudFilesAWSResourceManager`, `CloudFilesAzureResourceManager` bzw. `CloudFilesGCPResourceManager`), typischerweise mit einem Databricks-Service-Credential oder alternativ mit direkten Zugangsdaten:

```python
# AWS, über Databricks-Service-Credential
manager = spark._jvm.com.databricks.sql.CloudFilesAWSResourceManager \
  .newManager() \
  .option("cloudFiles.region", "<region>") \
  .option("path", "<path-to-specific-bucket-and-folder>") \
  .option("databricks.serviceCredential", "<service-credential-name>") \
  .create()

# AWS, über Access Key/Secret
manager = spark._jvm.com.databricks.sql.CloudFilesAWSResourceManager \
  .newManager() \
  .option("cloudFiles.region", "<region>") \
  .option("cloudFiles.awsAccessKey", "<aws-access-key>") \
  .option("cloudFiles.awsSecretKey", "<aws-secret-key>") \
  .option("cloudFiles.roleArn", "<role-arn>") \
  .option("cloudFiles.roleExternalId", "<role-external-id>") \
  .option("cloudFiles.roleSessionName", "<role-session-name>") \
  .option("cloudFiles.stsEndpoint", "<sts-endpoint>") \
  .option("path", "<path-to-specific-bucket-and-folder>") \
  .create()
```

```python
# Azure, über Databricks-Service-Credential
manager = spark._jvm.com.databricks.sql.CloudFilesAzureResourceManager \
  .newManager() \
  .option("cloudFiles.resourceGroup", "<resource-group>") \
  .option("cloudFiles.subscriptionId", "<subscription-id>") \
  .option("databricks.serviceCredential", "<service-credential-name>") \
  .option("path", "<path-to-specific-container-and-folder>") \
  .create()

# GCP, über Databricks-Service-Credential
manager = spark._jvm.com.databricks.sql.CloudFilesGCPResourceManager \
  .newManager() \
  .option("cloudFiles.projectId", "<project-id>") \
  .option("databricks.serviceCredential", "<service-credential-name>") \
  .option("path", "<path-to-specific-bucket-and-folder>") \
  .create()
```

Nach dem Anlegen des Managers stehen drei Methoden zur Verfügung:

```python
# Queue und Topic einrichten
manager.setUpNotificationServices("<resource-suffix>")

# Angelegte Notification-Services auflisten
from pyspark.sql import DataFrame
df = DataFrame(manager.listNotificationServices(), spark)

# Notification-Services für einen bestimmten Stream abbauen
manager.tearDownNotificationServices("<stream-id>")
```

Die Setup-/List-/Teardown-APIs sind für S3, ADLS und Azure Blob Storage in allen Runtime-Versionen verfügbar, für GCS ab Databricks Runtime 9.1.

---

## <a id="troubleshooting">7. Troubleshooting (klassischer Modus)</a>

- **`Failed to create event grid subscription`:** Im Azure-Portal unter der Subscription den Abschnitt *Resource Providers* öffnen und den Provider `Microsoft.EventGrid` registrieren.
- **`403 Forbidden ... does not have authorization to perform action 'Microsoft.EventGrid/eventSubscriptions/[read|write]'`:** Prüfen, ob dem Service Principal die Rolle **Contributor** für Event Grid und das Storage-Konto zugewiesen ist.
- **Event-Grid-Client umgeht den Proxy:** Ab Databricks Runtime 15.2 verwenden Event-Grid-Verbindungen in Auto Loader standardmäßig die Proxy-Einstellungen aus den System-Properties. Auf Databricks Runtime 13.3 LTS, 14.3 LTS und 15.0–15.2 lässt sich dies manuell aktivieren:

  ```
  spark.databricks.cloudFiles.eventGridClient.useSystemProperties true
  ```

- **`com.databricks.sql.util.UnexpectedHttpStatus: Too many requests. Please wait a moment and try again.`:** Tritt typischerweise auf, wenn mehrere Auto-Loader-Streams aus unterschiedlichen Unterpfaden derselben External Location lesen, ohne Unity-Catalog-Volumes zu verwenden. Lösung: separate Volumes pro Unterpfad.
