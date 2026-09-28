## E. Ihren Job über die Jobs-UI planen

Gehen Sie wie folgt vor, um Ihren Databricks-Job zu planen:

1. **Ihren Job öffnen:** Wechseln Sie zu dem Job, den Sie gerade erstellt haben.

2. **Zum Tab Tasks wechseln:** Stellen Sie sicher, dass Sie den Tab **Tasks** in Ihrem Job sehen.

3. **Job Details aufklappen:**  Suchen Sie auf der rechten Seite der Jobs-UI den Bereich **Job Details**.  
   - **HINWEIS:** Wenn der Bereich eingeklappt ist, klicken Sie auf das Pfeilsymbol, um ihn aufzuklappen.

4. **Einen Zeitplan hinzufügen:**  Klicken Sie im Abschnitt **Schedules & Triggers** auf **Add trigger**. Sie sehen drei Planungsoptionen:  
   - **Scheduled** (zu bestimmten Zeiten ausführen)

   - **Continuous** (ausführen, sobald der vorherige Run beendet ist)

   - **Table Update** (automatisch ausführen, sobald eine oder mehrere angegebene Tabellen aktualisiert werden)

   - **File arrival** (ausführen, wenn Dateien an einem Speicherort eintreffen)

5. **Einen geplanten Run einrichten:**  
   - Wählen Sie **Scheduled**.

   - Klicken Sie auf den Abschnitt **Advanced**, um weitere Optionen zu sehen.

6. **Den Zeitplan konfigurieren:**  
   - Legen Sie fest, dass der Job **jeden Tag** zu einer Uhrzeit Ihrer Wahl läuft.

   - Achten Sie darauf, Ihre spezifische Zeitzone auszuwählen.

   - **Tipp:** Legen Sie den Zeitplan so fest, dass er zwei Minuten nach Ihrer aktuellen Uhrzeit startet, damit Sie nicht lange auf den Job-Run warten müssen.

**HINWEIS:** Durch das Planen Ihres Jobs wird sichergestellt, dass er automatisch zu den von Ihnen festgelegten Zeiten ausgeführt wird. Sie können Ihren Job-Run auch starten, indem Sie oben in Ihrem Job auf **Run Now** klicken.

## F. Ihren Job validieren

Prüfen Sie, ob die Tabelle **high_risk_borrowers_silver** in Ihrem Schema existiert.

Führen Sie außerdem den folgenden Befehl aus, um die Daten von **high_risk_borrowers_silver** zu überprüfen

```sql
%sql
SELECT count(*) FROM high_risk_borrowers_silver
```

Stellen Sie sicher, dass die Anzahl der Kreditnehmer mit hohem Risiko **143** beträgt; dies sollte der Gesamtzeilenzahl in der Tabelle **high_risk_borrowers_silver** entsprechen.
