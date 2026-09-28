## I. Ein Dashboard zu Ihrem Job hinzufügen

In diesem Abschnitt integrieren wir ein vorab erstelltes Dashboard in Ihren Job. Das Dashboard wurde für Sie vorbereitet und ist als JSON-Eingabedatei gespeichert, sodass Sie es nicht von Grund auf neu erstellen müssen.

#### I1. Ihr Retail-Dashboard konfigurieren
Gehen Sie wie folgt vor, um Ihr Dashboard anzuzeigen und zu konfigurieren:

1. Navigieren Sie zu **Lesson 12 Files**: [Task Files/Lesson 12 Files]($./Task Files/Lesson 12 Files), um die Eingabedatei zu finden.
2. Suchen Sie die Datei **input_file**. Diese Datei hilft beim Generieren einer benutzerspezifischen Dashboard-JSON-Datei.
3. Führen Sie den folgenden Befehl aus, um das Dashboard automatisch aus der Eingabedatei zu erstellen.

```python
DA.dashboard_creation_from_input()
```

4. Klicken Sie links auf das Ordnersymbol ![folder_icon.png](./Includes/images/icons/folder_icon.png); Sie sehen Ihr Dashboard zusammen mit anderen Lab-/Demo-Notebooks.
5. Stellen Sie sicher, dass der Dashboard-Name mit dem in der obigen Zellenausgabe angezeigten übereinstimmt. Klicken Sie auf das Dashboard, um es zu öffnen.
6. Klicken Sie oben links auf **Edit draft**, um Ihr Dashboard anzuzeigen und zu ändern.
7. Stellen Sie oben rechts sicher, dass **shared_warehouse** als Compute ausgewählt ist. Verwenden Sie nicht "unknown warehouse". Warten Sie, bis das SQL Warehouse gestartet ist, damit Ihr Dashboard dargestellt werden kann.
8. Klicken Sie links auf den Tab **Data**. Prüfen Sie, dass die folgenden Tabellen ausgewählt sind:
   - `customers_orders_ny_gold`
   - `customers_orders_va_gold`
   - `customers_sales_summary_gold`
9. Führen Sie im Abfragefeld Abfragen auf jede Tabelle aus, um Erkenntnisse zu gewinnen. Stellen Sie sicher, dass Ihr Katalog auf **dbacademy** und Ihr Schema auf Ihr spezifisches **labuser**-Schema gesetzt ist.
10. Klicken Sie auf **Publish**. Hier finden Sie Optionen zum Freigeben von Dashboard-Berechtigungen. Ihr Dashboard wurde durch den obigen Befehl automatisch veröffentlicht. Wenn Sie jedoch Änderungen vornehmen, müssen Sie das Dashboard erneut veröffentlichen, um es zu aktualisieren.

**Hinweis:** Das Veröffentlichen des Dashboards ist erforderlich, um es in Ihren Job-Tasks zu verwenden.

So stellen Sie sicher, dass Ihr Dashboard mit den richtigen Daten- und Compute-Ressourcen verbunden ist.

#### I2. Einen Dashboard-Task zu Ihrem Job hinzufügen
Dieses Dashboard wurde im Classroom-Setup-Skript für Sie vorab erstellt. Das Erstellen von Dashboards liegt außerhalb des Umfangs dieses Kurses.

1. Klicken Sie in Ihrem Job auf **Add task** und wählen Sie **Dashboard**. Konfigurieren Sie den Task wie folgt:

| Einstellung    | Anweisungen                                                                  |
|----------------|------------------------------------------------------------------------------|
| Task name      | Geben Sie **refreshing_retail_dashboard** ein                                |
| Type           | Stellen Sie sicher, dass **Dashboard** ausgewählt ist                        |
| Dashboard      | Wählen Sie Ihr Dashboard aus der Liste der verfügbaren Dashboards. Der Name Ihres Dashboards wird in der Ausgabezelle des Befehls zur Dashboard-Erstellung angezeigt.                                                |
| SQL warehouse  | Wählen Sie im Dropdown Ihr **Warehouse**                                     |
| Subscribers    | Wählen Sie im Dropdown eine E-Mail-Adresse, um Dashboard-Snapshots zu erhalten. In unserer Lernumgebung können Sie keine weiteren E-Mail-Adressen hinzufügen.                    |
| Depends on     | Wählen Sie **transforming_customers_sales_table** und **transforming_customers_orders_data** |
| Dependencies   | Auf **All Succeeded** setzen                                                 |

2. Klicken Sie auf **Save task**.

![Lesson12_dashboard_task.png](./Includes/images/demo_monitoring/Lesson12_dashboard_task.png)

3. Klicken Sie auf **Run Now** und warten Sie, bis der Run abgeschlossen ist.

**HINWEIS:** Stellen Sie sicher, dass der Datenbereich Ihres Dashboards alle Gold-Tabellen enthält (Tabellen mit dem Suffix `gold` aus Ihrem Schema) und dass Ihr Dashboard mit Ihrem SQL Warehouse verbunden ist.

#### I3. Das Retail-Dashboard analysieren
Prüfen Sie nach Abschluss des Runs Ihre E-Mails. Sie sollten eine E-Mail von Databricks mit dem Retail_Dashboard erhalten haben.
