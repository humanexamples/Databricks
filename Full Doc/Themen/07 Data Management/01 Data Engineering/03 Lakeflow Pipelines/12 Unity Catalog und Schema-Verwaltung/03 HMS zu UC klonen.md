# Eine Unity-Catalog-Pipeline durch Klonen einer Hive-Metastore-Pipeline erstellen

Da bestehende Hive-Metastore-Pipelines nicht direkt auf Unity Catalog aktualisiert werden können (siehe `Unity Catalog.md`, Abschnitt Einschränkungen), stellt Databricks über die REST-API einen Klon-Mechanismus bereit, der eine Hive-Metastore-Pipeline in eine neue Unity-Catalog-Pipeline überführt — inklusive Daten, Metadaten und Checkpoints. Jede Aussage wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/clone-hms-to-uc` verifiziert.

## Abschnittsübersicht

1. [Grundprinzip](#grundprinzip)
2. [Vor dem Beginn (Voraussetzungen)](#voraussetzungen)
3. [Klonen über die REST-API](#rest-api)
4. [Klonen aus einem Databricks-Notebook](#notebook)
5. [Einschränkungen](#einschraenkungen)
6. [Quellen](#quellen)

---

## <a id="grundprinzip">1. Grundprinzip</a>

Die Klon-Operation dupliziert Quellcode und Konfiguration der Quell-Pipeline und passt dabei automatisch die Definitionen von Materialized Views und Streaming Tables an, damit sie den Unity-Catalog-Anforderungen entsprechen. Der Vorgang migriert bestehende Daten, Metadaten und Checkpoints — Streaming Tables können also an der zuvor erreichten Verarbeitungsposition fortsetzen. Nach Abschluss des Klonens arbeiten Original- und geklonte Pipeline unabhängig voneinander.

---

## <a id="voraussetzungen">2. Vor dem Beginn (Voraussetzungen)</a>

**Pipeline-Konfiguration:**

- Die Ziel-Pipeline muss Tabellen in ein festgelegtes Schema veröffentlichen.
- Alle Referenzen auf Hive-Metastore-Tabellen und -Views im Quellcode müssen vollständig qualifiziert sein — mit dem Katalog-Bezeichner `hive_metastore`, dem Schema-Namen und dem Tabellennamen, z. B. `hive_metastore.sales.customers`.

**Betriebliche Einschränkungen:**

- Der Quellcode der Quell-Pipeline (inklusive verknüpfter Notebooks und in Git gespeicherter Module) kann während des Klonens nicht bearbeitet werden.
- Die Quell-Pipeline muss beim Start des Klon-Vorgangs inaktiv sein; laufende Updates müssen zuvor abgeschlossen oder beendet werden.

**Speicherpfade:**

- Geben Hive-Metastore-Tabellen einen expliziten Speicherort an (Python-Parameter `path` bzw. SQL-Klausel `LOCATION`), muss beim Klon-Request die Konfiguration `"pipelines.migration.ignoreExplicitPath": "true"` übergeben werden.

**Auto-Loader-Kompatibilität:**

- Nutzt die Quell-Pipeline Auto Loader mit `cloudFiles.schemaLocation`, und läuft die ursprüngliche Pipeline nach dem Klonen weiter, benötigen **beide** Pipelines die Einstellung `mergeSchema: true`.

---

## <a id="rest-api">3. Klonen über die REST-API</a>

### cURL-Aufruf

```bash
curl -X POST \
  --header "Authorization: Bearer <personal-access-token>" \
  <databricks-instance>/api/2.0/pipelines/<pipeline-id>/clone \
  --data @clone-pipeline.json
```

- `<personal-access-token>`: Databricks Personal Access Token.
- `<databricks-instance>`: Workspace-Instanz, z. B. `dbc-a1b2345c-d6e7.cloud.databricks.com`.
- `<pipeline-id>`: eindeutige ID der zu klonenden Hive-Metastore-Pipeline (in der Pipelines-UI auffindbar).

### JSON-Konfigurationsdatei (`clone-pipeline.json`)

```json
{
  "catalog": "<target-catalog-name>",
  "target": "<target-schema-name>",
  "name": "<new-pipeline-name>",
  "clone_mode": "MIGRATE_TO_UC",
  "configuration": {
    "pipelines.migration.ignoreExplicitPath": "true"
  }
}
```

- `catalog`: Name des bestehenden Unity-Catalog-Katalogs, in den die neue Pipeline veröffentlicht.
- `target`: optionaler Schema-Name; wird er weggelassen, wird der Schema-Name der Quell-Pipeline übernommen.
- `name`: optionaler Name der neuen Pipeline; standardmäßig wird der Quellname mit angehängtem `[UC]` verwendet.
- `clone_mode`: einziger unterstützter Wert ist `"MIGRATE_TO_UC"`.
- `configuration`: optionale Override-Einstellungen für die neue Pipeline.

Die API-Antwort liefert die ID der neu erstellten Pipeline.

---

## <a id="notebook">4. Klonen aus einem Databricks-Notebook</a>

### Vorgehen

1. Neues Notebook erstellen.
2. Das folgende Python-Skript in die erste Zelle einfügen.
3. Platzhalterwerte anpassen.
4. Notebook ausführen.

```python
import requests

# Your Databricks workspace URL, with no trailing spaces
WORKSPACE = "<databricks-instance>"

# The pipeline ID of the Hive metastore pipeline to clone
SOURCE_PIPELINE_ID = "<pipeline-id>"

# The target catalog name in Unity Catalog
TARGET_CATALOG = "<target-catalog-name>"

# (Optional) The name of a target schema in Unity Catalog. If empty, the same schema name as the Hive metastore pipeline is used
TARGET_SCHEMA = "<target-schema-name>"

# (Optional) The name of the new pipeline. If empty, the following is used for the new pipeline name: f"{originalPipelineName} [UC]"
CLONED_PIPELINE_NAME = "<new-pipeline-name>"

# This is the only supported clone mode
CLONE_MODE = "MIGRATE_TO_UC"

# Specify override configurations
OVERRIDE_CONFIGS = {"pipelines.migration.ignoreExplicitPath": "true"}

def get_token():
    ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
    return getattr(ctx, "apiToken")().get()

def check_source_pipeline_exists():
    data = requests.get(
        f"{WORKSPACE}/api/2.0/pipelines/{SOURCE_PIPELINE_ID}",
        headers={"Authorization": f"Bearer {get_token()}"},
    )
    assert data.json()["pipeline_id"] == SOURCE_PIPELINE_ID, "The provided source pipeline does not exist!"

def request_pipeline_clone():
    payload = {
      "catalog": TARGET_CATALOG,
      "clone_mode": CLONE_MODE,
    }
    if TARGET_SCHEMA != "":
      payload["target"] = TARGET_SCHEMA
    if CLONED_PIPELINE_NAME != "":
      payload["name"] = CLONED_PIPELINE_NAME
    if OVERRIDE_CONFIGS:
      payload["configuration"] = OVERRIDE_CONFIGS
    data = requests.post(
        f"{WORKSPACE}/api/2.0/pipelines/{SOURCE_PIPELINE_ID}/clone",
        headers={"Authorization": f"Bearer {get_token()}"},
        json=payload,
    )
    response = data.json()
    return response

check_source_pipeline_exists()
request_pipeline_clone()
```

---

## <a id="einschraenkungen">5. Einschränkungen</a>

**Automatisierung und Klon-Umfang:**

- Declarative Automation Bundles können den Klon-Vorgang nicht ausführen.
- Es werden ausschließlich Migrationen von Hive Metastore nach Unity Catalog unterstützt (nicht die umgekehrte Richtung).
- Klone müssen innerhalb desselben Workspace wie die Quell-Pipeline verbleiben.

**Unterstützte Streaming-Quellen für den Klon:**

- Delta-Quellen.
- Auto Loader (alle Auto-Loader-Datenquellen werden unterstützt).
- Apache Kafka via Structured Streaming (`kafka.group.id` kann dabei nicht verwendet werden).
- Amazon Kinesis via Structured Streaming (`consumerMode` kann dabei nicht auf `efo` gesetzt werden).

**Auto Loader im File-Notification-Modus:**

Nutzt die Quell-Pipeline den File-Notification-Modus, empfiehlt Databricks, die Ausführung der Quell-Pipeline nach dem Klonen einzustellen, um verpasste File-Notification-Ereignisse zu vermeiden. Wird der Betrieb der Quelle dennoch fortgesetzt, kann zur Wiederherstellung die Auto-Loader-Option `cloudFiles.backfillInterval` genutzt werden.

**Wartung und Time Travel:**

- Wartungsaufgaben pausieren während des Klonens für **beide** Pipelines.
- Time-Travel-Abfragen mit `timestamp_expression` sind für Versionen, die ursprünglich in Hive-Metastore-Managed-Objekten geschrieben wurden, in den geklonten Unity-Catalog-Tabellen **nicht definiert**.
- Time Travel mit `version`-Klausel funktioniert unabhängig vom Ursprung der Version korrekt.

**Weitere Hinweise:** Für zusätzliche Einschränkungen verweist die Doku auf die allgemeine Unity-Catalog-Pipeline-Dokumentation und die generelle Unity-Catalog-Dokumentation.

---

## <a id="quellen">6. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/clone-hms-to-uc

**Stand:** 2026-08-19
