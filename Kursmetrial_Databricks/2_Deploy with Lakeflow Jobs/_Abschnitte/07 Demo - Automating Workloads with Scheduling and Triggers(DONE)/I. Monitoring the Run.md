## I. Den Run überwachen

Sobald der Trigger konfiguriert ist, überwacht Databricks den Speicherort automatisch auf neue Dateien (standardmäßig jede Minute). Gehen Sie wie folgt vor, um Ihre Job-Runs zu überwachen:

1. **Den Tab Runs öffnen**
   - Klicken Sie in der oberen linken Ecke auf den Tab **Runs**.
   - Suchen Sie den **Trigger status**. Wenn Sie ihn nicht sehen, warten Sie eine Minute und überprüfen Sie bei Bedarf die Einrichtung Ihres **File arrival**-Triggers.

2. **Die Trigger-Auswertung prüfen**
   - Der Trigger wird als ausgewertet angezeigt. Werden keine neuen Dateien gefunden, wird der Job nicht ausgeführt.

3. **Details zum Job-Run ansehen**
   - Nachdem der Job gelaufen ist (in der Regel innerhalb von 1–2 Minuten), klicken Sie auf die **Start time**, um die Run-Details anzuzeigen.

> **Tipp:**  
> Um einen Run manuell mit anderen Parametern auszulösen, gehen Sie zur Job-Konfigurationsseite, klicken Sie auf der Seite **Run output** auf **Edit task**, klicken Sie dann auf den Pfeil nach unten neben **Run now** und wählen Sie **Run now with different settings**.
