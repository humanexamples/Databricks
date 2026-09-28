## G. Task Parameters setzen
Das Task-Notebook für diese Demo muss den Namen des Katalogs und des Schemas kennen, mit denen wir arbeiten. Dies können wir mit **Task parameters** konfigurieren (Sie können auch **Job Parameters** verwenden; diese werden an alle Tasks weitergegeben). 

  Das bietet Flexibilität und ermöglicht die Wiederverwendung von Code.

1. Führen Sie die folgende Zelle aus, um Ihre **Katalog**- und **Schema**-Namen anzuzeigen. Diese benötigen wir beim Setzen der Parameter.

```python
print(f"catalog : {DA.catalog_name}")
print(f"schema : {DA.schema_name}")
```

2. Führen Sie die folgenden Schritte aus, um **die Task Parameters zu setzen**:

   a. Kehren Sie zu Ihrem Task **ingesting_customers** zurück. Klicken Sie im Bereich **Task details** unter **Parameters** auf **Add**.

   b. Setzen Sie die folgenden Schlüssel-Wert-Paare:
   - **catalog** (Schlüssel) =  **dbacademy** (Wert) 
   - **schema** (Schlüssel) = Ihr **labuser**-Schemaname aus der obigen Zellenausgabe (Wert) 

   c. Klicken Sie auf **Save task**.

3.  Klicken Sie, um das Notebook [Task Files/Lesson 07 Files/7.1 - Creating customers table]($./Task Files/Lesson 07 Files/7.1 - Creating customers table) zu öffnen. Dieses Notebook wird im Task **ingesting_customers** verwendet. Beachten Sie im Notebook Folgendes:

- Die Variable `my_catalog` erhält ihren Wert aus dem Parameter `catalog`, den wir im Task gesetzt haben, und zwar mit:
- `my_catalog = dbutils.widgets.get('catalog')`

- Die Variable `my_schema` erhält ihren Wert aus dem Parameter `schema`, den wir im Task gesetzt haben, und zwar mit: 
- `my_schema = dbutils.widgets.get('schema')`

- Die Variable `my_volume_path` verwendet die gesetzten Parameter, um auf Ihr Volume **trigger_storage_location** zu verweisen:
- `f"/Volumes/{my_catalog}/{my_schema}/trigger_storage_location/"`

4.  Schließen Sie das Notebook **Creating customer table**

![Lesson03_TriggerJob.png](./Includes/images/demo_scheduler/Lesson07_TriggerJob.png)

   Ihr File Arrival Trigger und der Task ingesting_customers sollten wie im obigen Screenshot aussehen.

## H. Eine Datei in das Volume legen
Führen Sie die folgende Zelle aus, um eine neue Datei in Ihrem Volume **trigger_storage_location** abzulegen. 

Beim File Arrival Trigger werden nur neue Dateien ingestiert und verarbeitet. Geänderte Dateien lösen den Run nicht erneut aus. Um erneut auszulösen, müssen Sie den Dateinamen manuell ändern.

**HINWEIS:** Dies ist eine für den Kurs erstellte benutzerdefinierte Funktion, die Daten zu Ihrem Volume hinzufügt, um das Laden von Daten in Cloud-Speicher zu simulieren.

```python
DA.copy_data()
```
