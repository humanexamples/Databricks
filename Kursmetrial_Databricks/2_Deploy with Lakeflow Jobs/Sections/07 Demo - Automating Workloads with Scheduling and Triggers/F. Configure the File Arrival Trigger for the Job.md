## F. Den File Arrival Trigger für den Job konfigurieren

In diesem Schritt richten wir einen File Arrival Trigger ein, der ein festgelegtes Volume auf neue Datendateien überwacht. Ziel ist es, den Job automatisch zu starten, sobald am angegebenen Speicherort eine neue Datei erkannt wird, und so eine nahtlose und zeitnahe Datenverarbeitung zu ermöglichen.

**HINWEIS:**  Databricks Volumes sind Unity-Catalog-Objekte, die ein logisches Speichervolume an einem Cloud-Object-Storage-Speicherort darstellen. Volumes bieten Funktionen zum Abrufen, Speichern, Verwalten (Governance) und Organisieren von Dateien. Sie können Volumes verwenden, um Dateien in jedem Format zu speichern und darauf zuzugreifen – strukturierte, semistrukturierte und unstrukturierte Daten.

1. Führen Sie die folgende Zelle aus, um ein Volume namens **trigger_storage_location** zu erstellen. Dieses Volume dient als Speicherort, der auf neue Dateien überwacht wird.  

   Es wird im Katalog **dbacademy** in Ihrem eindeutigen Schema **labuser** erstellt.

```sql
%sql
CREATE VOLUME IF NOT EXISTS trigger_storage_location
```

2. Führen Sie die folgenden Schritte aus, um Ihr neues Volume **trigger_storage_location** in Ihrem Schema **dbacademy.labuser** anzuzeigen:

   a. Klicken Sie in der linken Navigationsleiste auf das Symbol **Catalog** ![Catalog Icon](../../Includes/images/icons/catalog_icon.png).

   b. Suchen Sie den Katalog **dbacademy** und klappen Sie ihn auf.

   c. Klappen Sie Ihr Schema **labuser** auf.

   d. Klappen Sie **Volumes** auf und bestätigen Sie, dass das Volume **trigger_storage_location** angezeigt wird.

   e. Klappen Sie das Volume **trigger_storage_location** auf und prüfen Sie, dass es **keine** Dateien enthält.

3. Sie können auch die Anweisung `SHOW VOLUMES` verwenden, um die verfügbaren Volumes in Ihrem Schema (Ihrer Datenbank) anzuzeigen.

```sql
%sql
SHOW VOLUMES;
```

4. Führen Sie die folgende Zelle aus, um den Pfad zu diesem Volume mithilfe des für diesen Kurs erstellten benutzerdefinierten Objekts `DA` zu erhalten.

**HINWEIS:** Sie können auch Ihr Volume im Katalog auswählen, auf die drei Punkte klicken und dann *Copy volume path* wählen, um den Volume-Pfad zu erhalten.

```python
your_volume_path = (f"/Volumes/{DA.catalog_name}/{DA.schema_name}/trigger_storage_location/")
print(your_volume_path)
```

5. Führen Sie die folgenden Schritte aus, um den **File Arrival**-Trigger für Ihren Job zu konfigurieren:

   a. Wechseln Sie zurück zum Browser-Tab mit Ihrem Job.

   b. **Klicken Sie** in Ihrem Job im Bereich Job details **auf Add Trigger** und wählen Sie unter Trigger type den Trigger-Typ File Arrival.

   c. Fügen Sie den obigen Pfad in das Feld **Storage location** ein

   d. Klicken Sie auf **Test Trigger**, um den korrekten Pfad zu überprüfen

- **HINWEIS:** Sie sollten **Success** sehen. Falls nicht, prüfen Sie, ob Sie die obige Zelle ausgeführt und die gesamte Zellenausgabe in **Storage location** kopiert haben

   e. Klappen Sie die **Advanced**-Optionen auf. Beachten Sie, dass Sie verschiedene Trigger-Optionen festlegen können.

   f. Klicken Sie auf **Save**

**HINWEIS:**  Es gibt ein Limit von 1000 Dateien, die mit einem File Arrival Trigger ausgelöst werden können. 

Referenz: https://docs.databricks.com/aws/en/jobs/file-arrival-triggers#limitations
