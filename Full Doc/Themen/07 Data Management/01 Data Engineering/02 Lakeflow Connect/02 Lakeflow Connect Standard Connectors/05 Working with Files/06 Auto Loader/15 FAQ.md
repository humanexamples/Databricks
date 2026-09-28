# Auto Loader — FAQ

Quelle: [Auto Loader FAQ](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/faq.html) (Gegenprüfung: [Azure-Spiegelseite](https://learn.microsoft.com/en-us/azure/databricks/ingestion/cloud-object-storage/auto-loader/faq)).

Deutsche Zusammenfassung der wörtlich abgerufenen Antworttexte:

1. **Verarbeitet Auto Loader eine Datei erneut, wenn sie angehängt oder überschrieben wird?** Mit der Standardeinstellung (`cloudFiles.allowOverwrites` = `false`) werden Dateien genau einmal verarbeitet (siehe [09 Datei-Tracking und Checkpoints.md](09%20Datei-Tracking%20und%20Checkpoints.md)).
2. **Wie bestimmt Auto Loader, ob eine Datei bereits aufgenommen wurde?** Auto Loader nimmt jede Datei normalerweise nur einmal auf, basierend auf ihrem Dateipfad. Wird `allowOverwrites` auf `true` gesetzt, verwendet Auto Loader zusätzlich den letzten Änderungszeitpunkt der Datei.
3. **Sollte diese Quelle auch verwendet werden, wenn Dateien in regelmäßigen Intervallen eintreffen (z. B. einmal täglich)?** In diesem Fall lässt sich ein `Trigger.AvailableNow` einrichten (verfügbar ab Databricks Runtime 10.4 LTS).
4. **Wie inferiert Auto Loader das Schema?** Beim erstmaligen Definieren des DataFrames listet Auto Loader das Quellverzeichnis auf und wählt die neuesten (nach Dateiänderungszeitpunkt) 50 GB an Daten oder 1000 Dateien.
5. **Wie verhält sich Auto Loader, wenn das Quellverzeichnis leer ist?** Auto Loader verlangt die Angabe eines Schemas, da keine Daten vorhanden sind.
6. **Wann inferiert Auto Loader das Schema — entwickelt es sich nach jedem Micro-Batch automatisch weiter?** Das Schema wird bei der erstmaligen Definition des DataFrames inferiert. Während jedes Micro-Batches werden Schema-Änderungen dynamisch ausgewertet.
7. **Welchen Performance-Einfluss hat die Schema-Inferenz?** Bei sehr großen Quellverzeichnissen ist für die initiale Schema-Inferenz mit einigen Minuten zu rechnen.
8. **Eine fehlerhafte Datei hat mein Schema drastisch verändert — wie mache ich eine Schema-Änderung rückgängig?** Der Databricks-Support sollte kontaktiert werden.
9. **Was passiert, wenn ich beim Neustart des Streams den Checkpoint-Speicherort ändere?** Eine Änderung des Checkpoint-Speicherorts bedeutet effektiv, dass der vorherige Stream aufgegeben und ein neuer Stream gestartet wird.
10. **Muss ich Event-Notification-Dienste vorab selbst anlegen?** Nein — wählt man den File-Notification-Modus und stellt die erforderlichen Berechtigungen bereit, kann Auto Loader die File-Notification-Dienste selbst anlegen.
11. **Können mehrere Streaming-Abfragen aus unterschiedlichen Eingabeverzeichnissen desselben Buckets/Containers laufen?** Ja, solange es sich nicht um Eltern-Kind-Verzeichnisse handelt — `prod-logs/` und `prod-logs/usage/` würden nicht funktionieren.
12. **Kann diese Funktion genutzt werden, wenn bereits File Notifications auf meinem Bucket/Container existieren?** Ja, solange das Eingabeverzeichnis nicht mit dem bestehenden Notification-Präfix in Konflikt steht.
13. **Kann eine SQS-Queue zwischen Auto Loader und anderen Anwendungen geteilt werden?** Databricks empfiehlt das nicht.
14. **Wie bestätige ich, dass File Events korrekt eingerichtet sind?** Über die Schaltfläche **Test Connection** auf der External-Location-Seite; bei korrekter Einrichtung erscheint ein grünes Häkchen.
15. **Kann eine vollständige Verzeichnisauflistung beim Erststart vermieden werden?** Nein. Selbst wenn `includeExistingFiles` auf `false` gesetzt ist, führt Auto Loader eine Verzeichnisauflistung durch, um nach dem Stream-Start erstellte Dateien zu erkennen.
16. **Muss `cloudFiles.backfillInterval` gesetzt werden, um verpasste Dateien zu vermeiden?** Nein. Databricks empfahl dies früher für den klassischen File-Notification-Modus, weil Cloud-Speicher-Benachrichtigungssysteme zu verpassten oder verspätet eintreffenden Dateien führen konnten.
17. **Bei fehlkonfigurierter File-Events-Queue verpasste Dateien — wie stellt Auto Loader sicher, dass sie nachträglich aufgenommen werden?** Auto Loader liest weiterhin aus dem File-Events-Cache und nimmt automatisch alle während der Fehlkonfiguration verpassten Dateien auf.
18. **Wie behebe ich einen `CF_MANAGED_FILE_EVENTS_INVALID_CONTINUATION_TOKEN`-Fehler?** Die Optionen `.option("cloudFiles.listOnStart", "true")` und `.option("cloudFiles.validateOptions", false)` auf der Streaming-Abfrage setzen.
19. **Wie räume ich die von Auto Loader angelegten Event-Notification-Ressourcen auf?** Über den Cloud Resource Manager lassen sich Ressourcen auflisten und abbauen; alternativ manuell löschen (siehe [06 File Notification Mode.md](06%20File%20Notification%20Mode.md)).
20. **Wie überwache ich meine Auto-Loader-Pipeline?** Auto Loader stellt wichtige Metriken über `StreamingQueryListener` sowie den dateibezogenen Ingestion-Zustand über `cloud_files_state()` bereit (siehe [13 Observability.md](13%20Observability.md)).
