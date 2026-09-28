## F. Einen Run reparieren

Wenn Ihr Master-Job beim letzten Task fehlschlägt, gehen Sie wie folgt vor, um den Run zu reparieren:

1. Wechseln Sie zu Ihrem Job **Lab_15_<-your schema name->**.
2. Suchen Sie im Abschnitt **Runs** den fehlgeschlagenen Run.
3. Klicken Sie im Graph-Bereich auf den fehlgeschlagenen Task.
![Lesson15_failed_task](../../Includes/images/lab_mo/Lesson15_failed_task.png)

4. Dadurch wird die Seite mit dem Skript-Snapshot geöffnet. Klicken Sie auf **Repair run**.
5. Suchen Sie rechts den Abschnitt **Job parameters** und aktualisieren Sie den Parameter:
   * Schlüssel: **should_fail**
   * Wert: **false**
6. Klicken Sie auf **Repair Run**, um den Run erneut zu versuchen.

![Lesson15_corrected_task](../../Includes/images/lab_mo/Lesson15_corrected_task.png)

## G. Ihren Job ansehen

Sobald Ihr Run erfolgreich war, sollte Ihr endgültiger Master-Run wie unten aussehen
![Lesson15_master_job](../../Includes/images/lab_mo/Lesson15_master_job.png)

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
