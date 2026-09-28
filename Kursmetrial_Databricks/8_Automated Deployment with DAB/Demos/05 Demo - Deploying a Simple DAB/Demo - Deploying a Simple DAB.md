Erstellen Sie einen einfachen Databricks-Job, untersuchen Sie seine YAML-Konfiguration und durchlaufen Sie den vollständigen Lebenszyklus eines **Declarative Automation Bundle (DAB)**: validieren, bereitstellen, ausführen, ändern, erneut bereitstellen und entfernen. 


Dieses Notebook benötigt **All-Purpose-Compute** (Dedicated). Serverless wird für dieses Notebook nicht unterstützt.



Während der Entwicklung ist es einfacher, den Job, den Sie mit **Declarative Automation Bundles** automatisch bereitstellen möchten, zunächst manuell zu erstellen, um die für das Deployment nötige YAML-Konfiguration zu erhalten.

Führen Sie die folgende Zelle aus und bestätigen Sie, dass der Job erstellt wurde.

Um Zeit zu sparen, verwenden wir die Databricks-Academy-Klasse **`DAJobConfig`**, die mit dem Databricks SDK erstellt wurde, um **unseren Job für diese Demonstration automatisch anzulegen**. In einem typischen Entwicklungszyklus würden Sie den Job manuell erstellen.

```python
# **Job erstellen**
job_tasks = [
    {
        'task_name': 'create_bronze_table',
        'notebook_path': '/05 - Deploying a Simple DAB/src/create_bronze_table',
        'depends_on': None
    },
    {
        'task_name': 'create_silver_table',
        'notebook_path': '/05 - Deploying a Simple DAB/src/create_silver_table',
        'depends_on': [{'task_key': 'create_bronze_table'}]
    }
]

myjob = DAJobConfig(job_name=f'demo05_simple_dab_{my_catalog}',
                    job_tasks=job_tasks,
                    job_parameters=[
                      {'name':'display_target', 'default':'development'},
                      {'name':'catalog_name', 'default':catalog_dev}
                    ])
```

---

### B3. Die YAML-Konfiguration des Jobs ansehen

Beachten Sie, dass Databricks die Job-Konfiguration in mehreren Formaten erzeugen kann.

| Format | Was Sie tun können |
|---|---|
| **YAML** | - Den Job als YAML-Konfiguration ansehen<br>- Auf **Copy** klicken, um die Konfiguration direkt in `.yaml`-Dateien eines Declarative Automation Bundle einzufügen<br>- Auf **Edit** klicken, um die Job-Konfiguration in YAML statt über die UI zu ändern |
| **Python** | - Zwischen dem Format **Databricks SDK** und **Declarative Automation Bundles** wählen<br>- Auf **Copy** klicken, um wiederverwendbaren Python-Code zu erzeugen<br>- Die Version **Databricks SDK** verwenden, um Jobs in Notebooks oder lokalen Entwicklungsumgebungen zu erstellen<br>- Die Version **Bundles** verwenden, um Jobs in Python-basierten Bundle-Konfigurationen zu definieren |
| **JSON** | - Auf **Copy** klicken, um die vollständige Job-Konfiguration im JSON-Format abzurufen<br>- Das JSON mit der Databricks CLI, den Databricks SDKs oder der Databricks REST API verwenden, um Jobs zu erstellen, zu aktualisieren oder abzurufen |

---

#### Der Ressourcenteil in der YAML-Datei:
```yaml
...
resources:
  jobs:
    demo05_simple_dab_labuser15933383_1787966030:
      name: demo05_simple_dab_labuser15933383_1787966030
      tasks:
        - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_bronze_table.ipynb
            source: WORKSPACE
        - task_key: create_silver_table
          depends_on:
            - task_key: create_bronze_table
          notebook_task:
            notebook_path: ./src/create_silver_table.ipynb
            source: WORKSPACE
      parameters:
        - name: display_target
          default: development
        - name: catalog_name
          default: labuser1234_1_dev
...
```


---

```bash
%sh

# Schritt 1: Bundle validieren, falls databricks.yml vorhanden
databricks bundle validate

# Schritt 2: Bundle bereitstellen
databricks bundle deploy -t development

# Schritt 3: Den Job ausführen
databricks bundle run -t development demo05_simple_dab_labuser15933383_1787966030

# Schritt 4: Den bereitgestellten Job entfernen
# Standardmäßig werden Sie aufgefordert, das endgültige Löschen der zuvor bereitgestellten 
# Jobs, Pipelines und Artefakte zu bestätigen. Um diese Abfragen zu überspringen und automatisch 
# endgültig zu löschen, fügen Sie dem Befehl bundle destroy die Option --auto-approve hinzu.
databricks bundle destroy --auto-approve
```
