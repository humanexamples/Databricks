# Dynamische Wertreferenzen

Variablen, die bei der Konfiguration von Jobs und Tasks verfügbar sind — Job-Metadaten (ID, Name, Run-ID), erzeugte Informationen (Job-ID, Run-ID, Startzeit), Repair-Versuche, Task-Ergebniszustände sowie nutzerkonfigurierte Job-/Task-Parameter.

## Syntax und Regeln

Dynamische Wertreferenzen nutzen doppelte geschweifte Klammern (`{{ }}`) und werden beim Job-Lauf durch String-Literale ersetzt. Beispiel: `{"job_run_id": "job_{{job.run_id}}"}` mit Run-ID `550315892394120` ergibt `job_550315892394120`.

**Wichtige Einschränkungen:**

- Der Inhalt der doppelten geschweiften Klammern wird **nicht** als Ausdruck ausgewertet — keine Operationen/Funktionen innerhalb von `{{ }}` möglich.
- Syntaxfehler werden stillschweigend als Literal-String übernommen.
- Ungültige Referenzen aus bekannten Namespaces (z. B. `{{job.notebook_url}}`) erzeugen Fehlermeldungen.

## Kategorien

**Job-Referenzen:** `{{job.id}}`, `{{job.name}}`, `{{job.run_id}}`, `{{job.repair_count}}`, `{{job.start_time.<argument>}}`, `{{job.parameters.<name>}}`, `{{job.trigger.type}}`

**Task-Referenzen:** `{{task.name}}`, `{{task.run_id}}`, `{{task.execution_count}}`, `{{task.notebook_path}}`, `{{tasks.<task_name>.run_id}}`, `{{tasks.<task_name>.result_state}}`

**Workspace-Referenzen:** `{{workspace.id}}`, `{{workspace.url}}`

**Backfill-Referenzen:** `{{backfill.day}}`, `{{backfill.iso_date}}`, `{{backfill.month}}`, `{{backfill.year}}`

## Datum/Zeit-Argumente

Zeitbasierte Variablen unterstützen: `iso_weekday`, `is_weekday`, `iso_date`, `iso_datetime`, `year`, `month`, `day`, `hour`, `minute`, `second`, `timestamp_ms`.

## SQL-Ausgabe referenzieren

Nachgelagerte Tasks können die Ausgabe eines vorgelagerten SQL-Tasks referenzieren: `{{tasks.<task_name>.output.rows}}`, `{{tasks.<task_name>.output.first_row}}`, `{{tasks.<task_name>.output.first_row.<column_alias>}}`. Ausgaben sind auf 1.000 Zeilen und 48 KB begrenzt, 7 Tage aufbewahrt.

## Veraltete Referenzen

Ältere Variablen wie `{{job_id}}`, `{{run_id}}`, `{{start_date}}`, `{{task_retry_count}}` sind zugunsten der neuen namespaced Syntax veraltet.

## Quelle

- https://docs.databricks.com/aws/en/jobs/dynamic-value-references
