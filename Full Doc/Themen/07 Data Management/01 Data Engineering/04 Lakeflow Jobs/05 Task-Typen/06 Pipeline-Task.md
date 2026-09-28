# Pipeline-Task

Lakeflow Jobs definiert Beziehungen zwischen Tasks prozedural; Lakeflow Pipelines definieren Beziehungen zwischen Datasets und Transformationen deklarativ. Eine Pipeline lässt sich als Task in einem Job zeitplanen — über Jobs-UI, Lakeflow-Pipelines-UI oder SQL.

Ein Pipeline-Task läuft je nach Job-Zeitplan unterschiedlich:

- **Triggered/Scheduled Job:** startet ein einzelnes Update und stoppt nach dessen Abschluss.
- **Continuous Job:** läuft die Pipeline kontinuierlich — der Job-Zeitplan bestimmt den Ausführungsmodus, auch wenn der eigene Pipeline-Mode der Pipeline auf „triggered" steht.

## Konfiguration über die Jobs-UI

1. Neuen Task anlegen, Typ **Pipeline**.
2. Im **Pipeline**-Dropdown bestehende Pipeline wählen.
3. Optional Full Refresh der Pipeline auslösen.
4. Optional Parameter-Overrides im **Parameters**-Feld setzen.
5. Optional Retries, Laufdauer-/Streaming-Backlog-Schwellen oder Benachrichtigungen konfigurieren.

Über **New ingestion pipeline** im Add-Task-Panel bzw. Type-Dropdown lässt sich auch direkt eine neue Ingestion-Pipeline anlegen.

## Kontinuierlich mit einem Continuous Job ausführen

Der eingebaute **Pipeline mode** muss nicht auf continuous gesetzt werden — der Job-Zeitplan bestimmt den Ausführungsmodus und hat Vorrang. Gilt nur für Lakeflow Pipelines; eigenständige Materialized Views/Streaming Tables laufen immer getriggert. Eine in einem Continuous Job laufende Pipeline kann Serverless-Performance-Modi wie Standard nutzen, die der eingebaute Continuous-Modus der Pipeline nicht unterstützt.

Databricks empfiehlt, kontinuierliche Pipelines über einen Continuous Job statt über die eingebaute Continuous-Einstellung der Pipeline laufen zu lassen — dabei den Pipeline Mode auf **triggered** (Standard) belassen.

**Beispiel — Declarative Automation Bundles:**

```yaml
# resources/continuous_job.yml
resources:
  jobs:
    continuous_pipeline_job:
      name: continuous_pipeline_job
      performance_target: STANDARD
      continuous:
        pause_status: UNPAUSED
      email_notifications:
        on_failure:
          - your_email@example.com
      tasks:
        - task_key: refresh_pipeline
          pipeline_task:
            pipeline_id: ${resources.pipelines.example_pipeline.id}
```

Migration einer bestehenden Continuous-Pipeline zu einem Continuous Job: `continuous`-Feld aus der Pipeline-Definition entfernen — der Job übernimmt die kontinuierliche Ausführung.

## Database Table Sync Pipeline

Ein Pipeline-Task, der die Pipeline für eine Lakebase-Synced-Table pflegt — zum zeitgesteuerten Refresh oder bei Änderung der Unity-Catalog-Quelltabelle, damit operative Anwendungen aktuelle Daten aus Lakebase Postgres lesen. Erscheint im Type-Dropdown unter „Ingestion and Transformation". Im **Pipeline**-Feld die zur Synced Table gehörige Pipeline wählen (Lakebase Autoscaling oder Lakebase Provisioned, je nach Angebot).

## Ingestion Pipeline

Ein Pipeline-Task, der eine Ingestion-Pipeline ausführt. Über **Ingestion pipeline** im Type-Dropdown startet der **Add data**-Assistent, der einen Pipeline-Task für eine Ingestion-Pipeline erstellt — die erste Seite fragt nach der Datenquelle.

## Parameter (Beta)

Job- oder Task-Parameter lassen sich über dynamische Wertreferenzen im Pipeline-Task nutzen; Overrides über Key-Value-Paare im **Parameters**-Feld des Tasks.

## Concurrency-Grenzen

Eine Pipeline kann immer nur ein Update gleichzeitig ausführen:

- Ein Job mit `max_concurrent_runs > 1`, der einen Pipeline-Task enthält, wird auf einen gleichzeitigen Lauf begrenzt (Hinweis in der Job-UI).
- Ein in einem For-each-Task verpackter Pipeline-Task ist unabhängig von der konfigurierten Loop-Concurrency auf eine gleichzeitige Iteration begrenzt.

## Pipeline über die Pipeline-UI zeitplanen

Erzeugt einen Job mit einem einzelnen Pipeline-Task:

1. **Jobs & Pipelines** → Pipeline-Namen anklicken.
2. **Schedule** klicken (bzw. **Add schedule**, falls bereits Zeitpläne existieren).
3. Trigger-Typ wählen: **Scheduled** (zeitbasiert, mit Advanced-/Cron-Optionen) oder **Continuous**.
4. Eindeutigen Job-Namen vergeben.
5. Optional **Performance optimized** deaktivieren für Standard Performance Mode.
6. Optional E-Mail-Benachrichtigungen bei Start/Erfolg/Fehlschlag unter **More options**.
7. **Create**.

Bei kontinuierlichem Zeitplan startet Databricks den Lauf automatisch; **Stop** auf der Pipeline-Seite oder Pausieren des Zeitplans beendet ihn (und bricht das aktive Update ab). Ist die Pipeline in mehreren Zeitplänen enthalten, zeigt der Schedule-Button deren Anzahl (z. B. „Schedule (5)").

## Zeitplan für Materialized View/Streaming Table in Databricks SQL

In Databricks SQL definierte Materialized Views und Streaming Tables unterstützen zeitbasierte Zeitpläne direkt über `CREATE`/`ALTER`.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/pipeline
