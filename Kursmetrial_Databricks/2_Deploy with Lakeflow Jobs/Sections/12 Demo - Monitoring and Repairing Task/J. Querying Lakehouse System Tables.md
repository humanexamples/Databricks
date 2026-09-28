## J. Lakehouse-Systemtabellen abfragen
Databricks stellt Systemkataloge bereit, die Metadaten zu Abrechnung, Zugriff, Lakehouse-Operationen, Compute-Ressourcen und mehr enthalten. In diesem Kurs konzentrieren wir uns auf das Abfragen von Abrechnungs- und Lakehouse-Operationsdetails.

1. Sehen Sie sich zunächst an, welche Schemas im Katalog `system` vorhanden sind.

```sql
%sql
SHOW SCHEMAS IN system
```

2. Sehen Sie sich als Erstes die verschiedenen Tabellen an, die im Schema `lakeflow` verfügbar sind.

```sql
%sql
SHOW TABLES IN system.lakeflow
```

3. Verknüpfen wir die Tabellen `jobs` und `job_task_run_timeline`, um Erkenntnisse über kürzlich ausgeführte Jobs zu gewinnen.

```sql
%sql
SELECT jobs.workspace_id, 
        jobs.name as job_name,
        jobs.job_id,
        timeline.run_id,
        timeline.period_start_time,
        timeline.period_end_time,
        timeline.task_key,
        timeline.result_state 
FROM system.lakeflow.jobs as jobs
INNER JOIN
system.lakeflow.job_task_run_timeline as timeline
ON jobs.job_id = timeline.job_id
WHERE lower(jobs.name) LIKE 'demo_12_retail_job_%'
ORDER BY timeline.period_start_time
```

Hinweis: Sie können die verschiedenen verfügbaren Systemtabellen abfragen, verknüpfen und filtern, um wertvolle Erkenntnisse zu gewinnen. Dies ist ein umfangreiches Thema und liegt außerhalb des Umfangs dieses Kurses.

### Zusätzliche Ressourcen
Wenn Sie mehr über die Jobs-Systemtabellen erfahren möchten, lesen Sie die folgende Dokumentation:
https://docs.databricks.com/aws/en/admin/system-tables/jobs#jobs

Um die verschiedenen verfügbaren Systemtabellen, ihre Beziehungen und weitere zugehörige Details zu erkunden, siehe:
https://docs.databricks.com/aws/en/admin/system-tables

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
