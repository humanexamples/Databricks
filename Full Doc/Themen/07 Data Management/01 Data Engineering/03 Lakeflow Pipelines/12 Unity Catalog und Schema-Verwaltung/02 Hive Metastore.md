# Hive Metastore (Legacy) in Lakeflow Declarative Pipelines

Dieses Dokument beschreibt, wie Lakeflow Declarative Pipelines (LDP) Daten in den **legacy Hive Metastore** veröffentlichen — eine Alternative zu Unity Catalog für Workspaces, die (noch) keinen Unity Catalog nutzen. Jede Aussage wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/hive-metastore` verifiziert.

## Abschnittsübersicht

1. [Einordnung](#einordnung)
2. [Streaming Tables und Materialized Views im Hive Metastore abfragen](#abfragen)
3. [Pipeline zur Veröffentlichung im Hive Metastore konfigurieren](#konfigurieren)
4. [Speicherort angeben](#speicherort)
5. [Cloud-Storage-Konfiguration](#cloud-storage)
6. [Event Log für Hive-Metastore-Pipelines](#event-log)
7. [Beispiel-Notebooks für Workspaces ohne Unity Catalog](#beispiel-notebooks)
8. [Quellen](#quellen)

---

## <a id="einordnung">1. Einordnung</a>

Databricks empfiehlt für neue Pipelines Unity Catalog (siehe `Unity Catalog.md`). Dieses Dokument behandelt die Funktionalität des aktuellen Standard-Publishing-Modus beim Veröffentlichen in den legacy Hive Metastore und grenzt sich damit von älteren Legacy-Publishing-Modi ab, die von vor dem 5. Februar 2025 erstellten Pipelines verwendet werden.

---

## <a id="abfragen">2. Streaming Tables und Materialized Views im Hive Metastore abfragen</a>

Nach Abschluss eines Pipeline-Updates lassen sich Schema, Tabellen und Daten aus verschiedenen Umgebungen abfragen, u. a. Databricks SQL, Notebooks und anderen Lakeflow-Pipelines. Veröffentlichte Pipeline-Tabellen sind aus jeder Umgebung mit entsprechendem Schema-Zugriff abfragbar.

**Wichtige Einschränkung:** Es werden ausschließlich Tabellen und ihre zugehörigen Metadaten veröffentlicht — **Views werden nicht in den Metastore veröffentlicht.**

---

## <a id="konfigurieren">3. Pipeline zur Veröffentlichung im Hive Metastore konfigurieren</a>

Um in den legacy Hive Metastore zu veröffentlichen, wird beim Erstellen der Pipeline unter den Advanced Options (ggf. über „See more" erreichbar) die Option **„Use Hive Metastore"** ausgewählt. Beim Veröffentlichen in den Hive Metastore ist die Angabe eines Standard-Zielschemas (Default Target Schema) verpflichtend.

---

## <a id="speicherort">4. Speicherort angeben</a>

Für Pipelines, die in den Hive Metastore veröffentlichen, kann ein Speicherort (Storage Location) festgelegt werden. Der Hauptgrund dafür ist, den Speicherort der von der Pipeline geschriebenen Daten im Objektspeicher zu kontrollieren. Databricks empfiehlt, **stets** einen Speicherort anzugeben, um ein Schreiben in das DBFS-Root zu vermeiden. Da Lakeflow-Pipelines Tabellen, Daten, Checkpoints und Metadaten vollständig selbst verwalten, erfolgt der Zugriff auf die Datasets in der Praxis meist über die im Metastore registrierten Tabellen und nicht über den direkten Zugriff auf den Speicherort.

---

## <a id="cloud-storage">5. Cloud-Storage-Konfiguration</a>

Der Zugriff auf S3-Speicher wird über AWS Instance Profiles konfiguriert. Zwei Konfigurationswege stehen zur Verfügung:

**Weg 1 — über die UI:**

1. Pipeline im Lakeflow Pipelines Editor öffnen.
2. Auf **Settings** klicken.
3. Im Compute-Abschnitt im Dropdown **Instance profile** das gewünschte Instance Profile auswählen.

**Weg 2 — über die JSON-Konfiguration:**

Im JSON-Editor der Pipeline-Einstellungen das Instance Profile in der Cluster-Konfiguration eintragen:

```json
{
  "clusters": [
    {
      "aws_attributes": {
        "instance_profile_arn": "arn:aws:..."
      }
    }
  ]
}
```

Alternativ lässt sich das Instance Profile auch über eine Cluster-Policy für Lakeflow-Pipelines konfigurieren (Databricks Knowledge-Base-Beispiel verfügbar).

---

## <a id="event-log">6. Event Log für Hive-Metastore-Pipelines</a>

Für Pipelines, die Tabellen in den Hive Metastore veröffentlichen, liegt das Event Log unter `/system/events` relativ zum konfigurierten Speicherort. Ist der Speicherort z. B. `/Users/username/data`, liegt das Event Log unter `/Users/username/data/system/events` in DBFS. Ist kein Speicherort konfiguriert, liegt das Event Log standardmäßig unter `/pipelines/<pipeline-id>/system/events` in DBFS — Beispiel: `/pipelines/91de5e48-35ed-11ec-8d3d-0242ac130003/system/events`.

### Sicht auf das Event Log erstellen

```sql
CREATE OR REPLACE TEMP VIEW event_log_raw
AS SELECT * FROM delta.`<event-log-path>`;
```

`<event-log-path>` ist dabei durch den tatsächlichen Event-Log-Speicherort zu ersetzen.

### Letztes Update ermitteln

Jeder Pipeline-Lauf wird als „Update" bezeichnet. Das jeweils letzte Update lässt sich wie folgt ermitteln:

```sql
CREATE OR REPLACE TEMP VIEW latest_update AS
SELECT origin.update_id AS id
FROM event_log_raw
WHERE event_type = 'create_update'
ORDER BY timestamp DESC
LIMIT 1;
```

Das Event Log lässt sich über Databricks-Notebooks oder den SQL-Editor abfragen; die genannten temporären Views dienen dabei als Grundlage für Beispiel-Abfragen.

---

## <a id="beispiel-notebooks">7. Beispiel-Notebooks für Workspaces ohne Unity Catalog</a>

Databricks stellt importierbare Beispiel-Notebooks für Workspaces ohne Unity Catalog bereit — sowohl in Python als auch in SQL. Nach dem Import werden die jeweiligen Notebook-Pfade im Feld **Source code** bei der Pipeline-Konfiguration mit der Storage-Option „Hive Metastore" angegeben.

---

## <a id="quellen">8. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/hive-metastore

**Stand:** 2026-08-19
