

  Einen Job mit einem einzelnen Notebook und einer SQL-Abfrage erstellen und die Lakeflow-Jobs-UI erkunden.

```python
DA.print_job_config(job_name_extension='Demo_04_Retail_Job', 
                    file_paths='/Task Files/Lesson 04 Files',
                    Files=[
                        '4.1 - Creating orders table'
                    ])
```

### D2. Den Job erstellen und benennen

Führen Sie die folgenden Schritte aus, um Ihren Job zu erstellen und zu benennen.

1. Klicken Sie in der Seitenleiste mit der rechten Maustaste auf die Schaltfläche **Jobs and Pipelines** und wählen Sie *Open Link in New Tab*.

2. Vergewissern Sie sich im neuen Tab, dass Sie sich im Tab **Jobs & Pipelines** befinden.

3. Klicken Sie auf die Schaltfläche **Create** und wählen Sie im Dropdown-Menü **Job**.

4. In der oberen linken Ecke des Bildschirms sehen Sie einen Standard-Job-Namen, der auf dem aktuellen Datum und der Uhrzeit basiert (zum Beispiel *New Job Jul 29, 2025, 11:46 AM*).

5. Ändern Sie den **Job Name** in den Namen, der in der vorherigen Zelle angegeben wurde (zum Beispiel: **Demo_01_Retail_Job_labuser123**).

6. Lassen Sie den Job geöffnet und fahren Sie mit den nächsten Schritten fort.

**HINWEIS:** Wenn Sie auf einen empfohlenen Task (wie **Notebook**) klicken, werden Sie auf eine andere Seite weitergeleitet als im folgenden Screenshot gezeigt.

![Lesson04_Jobs_UI.png](./Includes/images/demo_creating_a_job/Lesson04_Jobs_UI.png)

### D3. Den Notebook-Task erstellen

Führen Sie die folgenden Schritte aus, um einen Notebook-Task hinzuzufügen.

1. In der Lakeflow-Jobs-UI sehen Sie möglicherweise einige Task-Vorschläge, z. B. **Notebook** oder **SQL File**.

2. Wählen Sie den Task-Typ **Notebook**.

3. Konfigurieren Sie den Task mit den folgenden Einstellungen:

| Einstellung     | Anweisungen |
|-----------------|--------------|
| **Task name**   | Geben Sie **ingesting_orders** ein |
| **Type**        | Wählen Sie **Notebook** |
| **Source**      | Wählen Sie **Workspace** |
| **Path**        | Verwenden Sie den Datei-Navigator, um **Notebook #1** zu suchen und auszuwählen:; **./Task Files/Lesson 04 Files/4.1 - Creating orders table** |
| **Compute**     | Wählen Sie im Dropdown-Menü einen **Serverless**-Cluster.; (Wir verwenden in diesem Kurs für alle Jobs Serverless-Cluster. Außerhalb dieses Kurses können Sie bei Bedarf einen anderen Cluster angeben.) ; ; **HINWEIS**: Wenn Sie Ihren All-Purpose-Cluster ausgewählt haben, erhalten Sie möglicherweise eine Warnung, dass dies als All-Purpose-Compute abgerechnet wird. Produktions-Jobs sollten immer auf neuen Job-Clustern geplant werden, die für den Workload passend dimensioniert sind, da diese zu einem deutlich niedrigeren Tarif abgerechnet werden.
 |
| **Create task** | Klicken Sie auf **Create task** |

4. Lassen Sie die Lakeflow-Jobs-UI geöffnet; im nächsten Schritt fügen Sie einen weiteren Task hinzu.
##### Für eine bessere Performance aktivieren Sie bitte den Performance Optimized Mode in den Job Details. Andernfalls kann es 6 bis 8 Minuten dauern, bis die Ausführung startet.

#### Einrichtung des Notebook-Tasks

![Lesson04_Notebook_task.png](./Includes/images/demo_creating_a_job/Lesson04_Notebook_task.png)

### D4. Den SQL-Query-Task erstellen

Führen Sie diese Schritte aus, um eine SQL-Datei als Task hinzuzufügen:

1. Klicken Sie in der Lakeflow-Jobs-UI auf **Add task**.

2. Wählen Sie den Task-Typ **SQL query**.

3. Konfigurieren Sie den Task mit den folgenden Einstellungen:

| Einstellung       | Anweisungen |
|-------------------|--------------|
| **Task name**     | Geben Sie **ingesting_sales** ein |
| **Type**          | Wählen Sie **SQL** |
| **SQL task**      | Wählen Sie **Query** |
| **SQL query**     | Wählen Sie im Dropdown die SQL-Datei:; **4.2 - Creating sales table - SQL Query** |
| **SQL warehouse** | Wählen Sie im Dropdown-Menü Ihr SQL Warehouse |
| **Depends on**    | Hier sollte kein Task ausgewählt sein.; (Heben Sie die Auswahl von **ingesting_orders** auf, falls es ausgewählt ist.) |
| **Create task**   | Klicken Sie auf **Create task** |

#### Einrichtung des SQL-Tasks

![Lesson04_task1_sql.png](./Includes/images/demo_creating_a_job/Lesson04_task1_sql.png)

### D5. Die Job-Details erkunden und ändern

1. Navigieren Sie zur Seite Job Details. Im rechten Bereich finden Sie die folgenden Details auf Job-Ebene:

- **Job Details:** Informationen wie Job-ID, Ersteller und mehr.
- **Schedulers and Triggers:** Verschiedene Planungsoptionen und Trigger für den Job anzeigen und konfigurieren.
- **Job Parameters:** Optionen zum Deklarieren von Parametern, die für den gesamten Job gelten.

#### Für eine bessere Performance aktivieren Sie bitte den Performance Optimized Mode in den Job Details.

##### Performance Optimized Mode
- Ermöglicht einen schnellen Compute-Start und eine höhere Ausführungsgeschwindigkeit.

##### Standard Mode
- Das Deaktivieren der Performance-Optimierung führt zu Startzeiten ähnlich wie bei der Classic-Infrastruktur und kann Ihre Kosten senken.

## E. Den Job ausführen

1. Suchen Sie in der oberen rechten Ecke das Kebab-Menü (drei Punkte) neben der Schaltfläche **Run now**. Dort sehen Sie Optionen wie **Edit as YAML**, **Clone job**, **View as code** und **Delete job**.

2. Klicken Sie auf **View as code**, um Ihren Job in drei Formaten zu sehen: YAML, Python (SDK und DABS) und JSON.

3. Kehren Sie zur Hauptseite des Jobs zurück und klicken Sie oben rechts auf die Schaltfläche **Run now**, um den Job zu starten.

**HINWEIS:** Nach dem Starten des Jobs können Sie auf den Link klicken, um den laufenden Run anzusehen. Im nächsten Abschnitt lernen Sie eine weitere Möglichkeit kennen, vergangene und aktuelle Job-Runs anzuzeigen.

## F. Den Job-Run überprüfen

1. Klicken Sie auf der Seite Job Details oben links auf den Tab **Runs** (derzeit sollten Sie sich im Tab **Tasks** befinden).

2. Im Tab Runs Ihres Jobs sehen Sie detaillierte Informationen zu jedem Run.
   Oben befindet sich ein zeitbasiertes Balkendiagramm, bei dem:

   - die X-Achse jeden Run darstellt.
   - die Y-Achse die Dauer jedes Tasks innerhalb dieses Runs zeigt.
3. Farbcodierung
   -    Legende: grün = erfolgreich
   -    rot = fehlgeschlagen
   -    gelb = wartend/Wiederholung, 
   -    pink = übersprungen,
   -    grau = ausstehend/abgebrochen/Timeout.

Unter dem Diagramm finden Sie eine tabellarische Matrixansicht, die dieselben Informationen im Detail darstellt. Diese Tabelle beginnt mit dem Zeitstempel und enthält Felder wie run_id, Run-Status, Dauer und weitere relevante Details zu jedem Run.

![Lesson04_view_runs.png](./Includes/images/demo_creating_a_job/Lesson04_view_runs.png)

4. Öffnen Sie die Ausgabedetails, indem Sie auf den Zeitstempel in der Spalte **Start time** klicken:

   - Wenn **der Job noch läuft**, sehen Sie im rechten Bereich den aktiven Zustand mit dem **Status** **Pending** oder **Running**.

   - Wenn **der Job abgeschlossen ist**, sehen Sie im rechten Bereich die vollständigen Ausführungsergebnisse mit dem **Status** **Succeeded** oder **Failed**.

## G. Ihre neuen Tabellen ansehen
1. Wählen Sie im linken Bereich **Catalog**. Navigieren Sie dann in den Katalog **dbacademy**.

2. Klappen Sie Ihren eindeutigen Schemanamen auf.

3. Beachten Sie, dass sich in Ihrem Schema die Tabellen **sales_bronze** und **orders_bronze** befinden.

## H. Ihre neuen Tabellen abfragen

```sql
%sql
-- Tabelle sales_bronze abfragen
SELECT * 
FROM sales_bronze
LIMIT 5;
```

```sql
%sql
-- Tabelle orders_bronze abfragen
SELECT * 
FROM orders_bronze
LIMIT 50;
```

## Zusätzliche Ressourcen

- [Lakeflow Jobs Documentation](https://docs.databricks.com/aws/en/jobs/)

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
