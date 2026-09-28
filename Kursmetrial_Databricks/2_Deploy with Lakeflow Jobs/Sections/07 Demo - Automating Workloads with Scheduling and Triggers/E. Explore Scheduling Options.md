## E. Planungsoptionen erkunden

Führen Sie die folgenden Schritte aus, um Planungsoptionen und Trigger in Lakeflow Jobs zu erkunden.

1. Kehren Sie zu Ihrem Job zurück.

2. Stellen Sie sicher, dass Sie sich im Tab **Tasks** Ihres Jobs befinden.

3. Suchen Sie auf der rechten Seite der Jobs-UI den Abschnitt **Job Details**.  
   - **HINWEIS:** Wenn der Seitenbereich eingeklappt ist, klicken Sie auf das nach links zeigende Pfeilsymbol, um ihn aufzuklappen.

4. Klicken Sie im Abschnitt **Schedules & Triggers** auf die Schaltfläche **Add trigger**, um die Optionen zu erkunden. Es gibt drei Optionen (zusätzlich zu manuell):

   - **Scheduled** — Sie sehen zwei Zeitplantypen: **Simple** und **Advanced** 
- Simple: Bietet Optionen zum Planen periodischer Job-Runs auf täglicher, stündlicher oder wöchentlicher Basis.
- Advanced: Mit dieser Option können Sie Jobs mit CRON-Syntax für ein präzises Timing planen.

   - **Table Update** – Auf Plattformen wie Azure Databricks kann ein Trigger eingerichtet werden, der automatisch ausgeführt wird, sobald eine oder mehrere angegebene Tabellen aktualisiert werden.

   - **Continuous** — läuft wiederholt mit einem kurzen Intervall zwischen den Runs.

   - **File arrival** — überwacht einen externen Speicherort oder ein Volume auf neue Dateien. Beachten Sie die **Advanced**-Einstellungen, in denen Sie die Zeit zwischen den Prüfungen und die Verzögerung nach dem Eintreffen einer neuen Datei bis zum Start eines Runs anpassen können.

5. Lassen Sie den Bereich **Schedules & Triggers** geöffnet und kehren Sie zu den folgenden Anweisungen zurück.
