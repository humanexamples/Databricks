In dieser Demonstration stellen Sie denselben Job aus einem einzigen Bundle in zwei Umgebungen (`development` und `production`) bereit. 

```yaml
bundle:                   # Erforderlich
  name: demo08_bundle     # Erforderlich


#################################################################
## Zusätzliche YAML-Konfigurationen, die in das Deployment aufgenommen werden #
## - Das Array include gibt eine Liste von Pfaden mit Konfigurationsdateien an, die in das Bundle aufgenommen werden.
#################################################################
include:
  - "./resources/demo_08_job.job.yml"       # Vollständige Job-Konfiguration im Ordner resources


variables:
  my_lab_user_name:
    description: Add your lab user name
    default: ${workspace.current_user.short_name}      #<----- Ermittelt Ihren Lab-Benutzernamen dynamisch

# Ändern Sie die folgenden Variablen nicht. Sie verwenden den Standardwert der Variablen my_lab_user_name und erzeugen die nötigen Variablen. Sehen Sie sich die folgenden Variablen an.
  catalog_dev:
    description: Development catalog for the project. Append _1_dev to the user name.
    default: ${var.my_lab_user_name}_1_dev
    
  catalog_prod:
    description: Production catalog for the project. Append _3_prod to the user name.
    default: ${var.my_lab_user_name}_3_prod

  target_catalog:
    description: Target catalog to use for deployment - default is 'dev'.
    default: ${var.catalog_dev}
    
  raw_data_path:
    description: Path to source CSV files to ingest (dev/stage/prod) - default is 'dev'.
    default: /Volumes/${var.target_catalog}/default/health

  my_cluster_id:
    description: Get the lab cluster ID using a lookup variable.
    lookup:
      cluster: labuser15933383_1788034912




##############################################################################################
# ZIELUMGEBUNGEN FÜR DAS DEPLOYMENT
# - Dies sind die Ziele (Targets) für Deployments und Workflow-Runs. 
# - Genau eines dieser Ziele darf auf "default: true" gesetzt sein.
##############################################################################################
targets:

  development:
    mode: development
    default: true
    workspace:
      # host: https://dbc-d9be2316-40bd.cloud.databricks.com/
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

    # Im Development-Modus Ihren kleinen Lab-Cluster für die Tasks verwenden. Dadurch wird der Cluster jedem Task im Ressourcen-Mapping des Jobs demo_08_job hinzugefügt.
    resources:
      jobs:
        demo_08_job:
          tasks:
            - task_key: create_bronze_table
              existing_cluster_id: ${var.my_cluster_id}
            - task_key: create_silver_table
              existing_cluster_id: ${var.my_cluster_id}


  production:
    mode: production
    workspace:
      # host: https://dbc-d9be2316-40bd.cloud.databricks.com/
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

    ## In der Produktionsumgebung Variablenwerte ändern, um den Produktionskatalog username_3_prod zu verwenden
    variables:
        target_catalog: ${var.catalog_prod}

```

```python
%sh
# Schritt 1
databricks bundle validate

# Schritt 2
# Mit databricks bundle validate --output json können Sie die vollständig aufgelöste Bundle- 
# Konfiguration als JSON anzeigen. Das ist nützlich, um zu bestätigen, dass Variablenersetzungen wie 
# erwartet aufgelöst wurden.
databricks bundle validate --output json

# Schritt 3
# Das Bundle bereitstellen
databricks bundle deploy -t development

# Schritt 4
# Den Job ausführen
databricks bundle run -t production demo_08_job

# Schritt 5
# Die Bundles entfernen
databricks bundle destroy --auto-approve
databricks bundle destroy -t production --auto-approve
```

------



------

 Bestätigen Sie, dass die Zelle die Version **v0.298.0** zurückgibt.

```bash
databricks -v
```

## B. Die Entwicklungs- und Produktionsdaten erkunden

1. Sehen Sie sich eine Vorschau der Entwicklungsdaten in Ihrem Katalog **labuser_UNIQUE_ID_1_dev** an. Beachten Sie Folgendes:
 - Sie enthalten 7.500 Zeilen (ohne die Kopfzeile).
 - Die PII-Daten sind maskiert.

 **HINWEIS:** In diesem Szenario sind die Beispieldaten in der Entwicklungsumgebung eine Teilmenge der Produktionsdaten, die zum Testen verwendet wird. Wir testen später gegen diesen Datensatz.

```python
spark.sql(f'''
SELECT *
FROM text.`/Volumes/{catalog_dev}/default/health`
''').display()
```

2. Sehen Sie sich eine Vorschau der Produktionsdaten in Ihrem Katalog **labuser_UNIQUE_ID_3_prod** an. Beachten Sie Folgendes:
 - Sie enthalten 70.695 Zeilen.
 - Die PII-Daten sind verfügbar.

 **HINWEIS:** In unserem Szenario wird dem Volume **health** im Prod-Katalog täglich eine CSV-Datei hinzugefügt. Wenn Sie das Volume **health** im Produktionskatalog untersuchen, finden Sie bereits 3 befüllte Tage.

```python
spark.sql(f'''
SELECT count(*) AS Total
FROM text.`/Volumes/{catalog_prod}/default/health`
''').display()
```

```python
spark.sql(f'''
SELECT *
FROM text.`/Volumes/{catalog_prod}/default/health`
''').display()
```

## C. Ein DAB in mehreren Umgebungen bereitstellen (Development und Production)

In diesem Beispiel verwenden wir denselben Job aus der Demonstration **05 - Deploying a Simple DAB**. Dies sind die gewünschten Konfigurationen der einzelnen Umgebungen (Kataloge):

#### Konfigurationsanforderungen für das Development-Ziel:
- Den Wert **labuser_UNIQUE_ID_1_dev** als Entwicklungskatalog zum Lesen und Schreiben verwenden.
- Den Job mit dem **kleinen Lab-Cluster** ausführen, da die Entwicklungsdaten klein und statisch sind.
- Die Entwicklungsumgebung zur **Standard**umgebung machen.

#### Konfigurationsanforderungen für das Production-Ziel:
- Den Wert **labuser_UNIQUE_ID_3_prod** als Produktionskatalog verwenden, um auf die Produktionsdaten zuzugreifen.
- Den Job mit Serverless Compute ausführen, da die Daten kontinuierlich wachsen, sodass sich Databricks Serverless an den Compute-Bedarf anpasst.

**Deployment-Modi (`development` / `production`)**: [AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/deployment-modes) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/deployment-modes) | [GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/deployment-modes)

### C1. Die Job-YAML-Datei unter `resources` erkunden
1. Öffnen Sie die Datei **./resources/demo_08_job.job.yml** in einem neuen Tab und erkunden Sie die Job-Konfiguration.

 a. Der Job-Schlüssel lautet `demo_08_job`.

 b. Die Vorlage für den Job-Namen lautet `${bundle.target}_demo08_dab_${workspace.current_user.userName}`. Durch die Ersetzung beim Deployment erhalten Sie einen Namen, der die Zielumgebung und den Benutzer enthält.

 c. Der Job verwendet die Notebooks `../src/create_bronze_table.ipynb` und `../src/create_silver_table.ipynb`.

 d. Scrollen Sie in der YAML-Datei nach unten und beachten Sie, dass die Parameter dieses Jobs Variablen verwenden:
 ```yaml
      parameters:
      - name: display_target
        default: ${bundle.target}
      - name: catalog_name
        default: ${var.target_catalog}
 ```

 e. Es ist kein Cluster angegeben, daher läuft dieser Job standardmäßig auf Serverless Compute.

 f. Lassen Sie diesen Tab geöffnet.

2. Führen Sie den folgenden Code aus, um Ihren Lab-Benutzernamen zu erhalten. Sie benötigen ihn im nächsten Abschnitt.

```python
print(my_catalog)
```

### C2. Die Datei `databricks.yml` erkunden und ändern

1. Navigieren Sie in Ihrem anderen Tab zur Datei **./databricks.yml** im Hauptordner der Demonstration und erkunden Sie das Bundle. Beachten Sie Folgendes:

 a. Dieses Bundle heißt `demo_08_bundle`.

 b. Dieses Bundle enthält ein übergeordnetes Mapping `include`:
 - Es gibt den Pfad zur Datei **./resources/demo_08_job.job.yml** an.
 - Diese YAML-Datei definiert den Job, der beim Deployment in das Mapping `resources` übernommen wird, wie Sie im vorherigen Schritt gesehen haben.
 - **HINWEIS:** Wenn Ihr Projekt wächst, ist es Best Practice, die Ressourcen des DAB in YAML-Dateien pro Ressource zu modularisieren.

 c. Dieses DAB enthält außerdem ein übergeordnetes Mapping `variables`. Sehen wir uns die definierten Variablen an:

 - Die Variable `my_lab_user_name` verwendet die Ersetzung `${workspace.current_user.short_name}`. Damit wird Ihr Benutzername für das Lab ermittelt und der korrekte Wert an die übrigen Variablen für jeden Katalog weitergegeben.

 - Die Variable `catalog_dev` verwendet die Variable `my_lab_user_name` und hängt `_1_dev` an Ihren Benutzernamen an, um auf Ihren Entwicklungskatalog zu verweisen.

 - Die Variable `catalog_prod` verwendet die Variable `my_lab_user_name` und hängt `_3_prod` an Ihren Benutzernamen an, um auf Ihren Produktionskatalog zu verweisen.

 - Die Variable `target_catalog` verweist standardmäßig auf Ihren Dev-Katalog.
 - Diese Variable wird in den Job-Parametern referenziert, die in **./resources/demo_08_job.job.yml** definiert sind:


 ```yaml
      parameters:
      - name: display_target
        default: ${bundle.target}
      - name: catalog_name
        default: ${var.target_catalog}
 ```


 - Die Variable `raw_data_path` verweist über `target_catalog` auf das Volume **health**, standardmäßig also auf das Volume **health** in Ihrem Dev-Katalog.

**Variablen und Ersetzungen (`${var.…}`, `${bundle.…}`, Lookups)**: [AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/variables) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/variables) | [GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/variables)

**
 TO DO – Den Cluster-Lookup in **databricks.yml** festlegen
 **

Die Variable `cluster_id` verwendet einen **Lookup**, um beim Deployment einen Clusternamen in eine Cluster-ID aufzulösen. Suchen Sie die Variable in **databricks.yml** und aktualisieren Sie den Wert `cluster:` mit dem Namen **Ihres** Lab-Clusters.

```yaml
variables:
  cluster_id:
    description: Look up your lab cluster's ID by name.
    lookup:
      cluster: <your-cluster-name>     # <-- hier Ihren Clusternamen einfügen
```

Im Databricks-Academy-Lab entspricht Ihr Clustername dem Wert, den die obige Zelle ausgibt (Ihr Lab-Benutzername).

Lassen Sie den Tab mit Ihrer Datei **databricks.yml** geöffnet.

2. Erkunden Sie in der Datei **databricks.yml** das Mapping `targets` der ersten Ebene. Beachten Sie Folgendes:

 a. Beim Deployment in das Ziel `development`:

 - Es ist auf `mode: development` gesetzt.

 - Es ist das **Standard**ziel.

 - Der `root_path`, unter dem die Dateien abgelegt werden, endet mit dem Zielnamen `development`.

 - Compute wird für jeden Task im Mapping `resources` überschrieben. Die (zuvor definierte) Lookup-Variable `my_cluster_id` liefert die ID des kleinen Lab-Clusters. Wir tun dies, weil die Entwicklungsdaten klein sind und kein großes Compute benötigen.

 b. Beim Deployment in das Ziel `production`:

 - Es ist auf `mode: production` gesetzt.

 - Die Variable `target_catalog` wird vom Standardwert `${var.catalog_dev}` auf `${var.catalog_prod}` überschrieben. Dadurch liest und schreibt der bereitgestellte Job im Produktionskatalog.

 - Der `root_path`, unter dem die Dateien abgelegt werden, endet mit dem Zielnamen `production`.

 - Der Job läuft auf **Serverless**, da wir das in der Ressourcen-YAML definierte Compute nicht überschreiben.

**
 Information
 **

- Falls verfügbar, könnten Sie den `host` angeben und festlegen, in welchen Databricks-Workspace bereitgestellt wird. In diesem Lab haben wir nur einen Workspace, daher isolieren wir die Umgebungen über den **Katalog**.

- Dieses Beispiel überschreibt für das Ziel `production` nur einige Konfigurationen. Viele weitere Einstellungen können überschrieben werden, siehe die Dokumentation **Bundle settings**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/settings) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/settings) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/settings)

3. Validieren Sie das Bundle für diese Demonstration und bestätigen Sie, dass die Validierung erfolgreich ist.

 **HINWEIS:** Wenn das Bundle nicht validiert wird, lesen Sie den Fehler und beheben Sie das Problem. Häufige Ursachen:

 - Fehlende Dateiendungen bei den Notebook-Pfaden in der Datei **demo_08_job.job.yml**.

 - Nicht oder falsch definierte bzw. referenzierte Variablen in der Datei **databricks.yml**.

```bash
databricks bundle validate
```

**
 Fehlerbehebung
 **

Wenn Sie nach dem Validieren Ihres Bundles den folgenden Fehler sehen, ist das Format Ihres Notebooks möglicherweise falsch.

`Error: notebook src/create_bronze_table.ipynb not found`. 

Prüfen Sie das Format Ihres Notebooks und passen Sie es entsprechend an.

4. Mit `databricks bundle validate --output json` können Sie die vollständig aufgelöste Bundle-Konfiguration als JSON anzeigen. Das ist nützlich, um zu bestätigen, dass Variablenersetzungen wie erwartet aufgelöst wurden.

Einige häufig verwendete Ersetzungen:

- `${bundle.name}`

- `${bundle.target}` (dem veralteten `${bundle.environment}` vorzuziehen)

- `${workspace.host}`

- `${workspace.current_user.short_name}`

- `${workspace.current_user.userName}`

- `${workspace.file_path}`

- `${workspace.root_path}`

- `${resources.jobs.<job-name>.id}`

- `${resources.models.<model-name>.name}`

- `${resources.pipelines.<pipeline-name>.name}`

Zum Beispiel in der folgenden JSON-Ausgabe:

- `bundle.target` wird zu `development` aufgelöst. Das YAML verwendet `${bundle.target}`, um darauf zu verweisen.
- Suchen Sie `workspace` > `current_user` > `short_name`. Dies gibt Ihren Lab-Benutzernamen zurück.

```bash
databricks bundle validate --output json
```

### C3. In der Entwicklungsumgebung bereitstellen

1. Löschen Sie die Tabellen **health_bronze_demo_08** und **health_silver_demo_08**, falls sie in unserem Entwicklungskatalog existieren, damit wir überprüfen können, dass unser Bundle sie beim Deployment erstellt.

 Führen Sie den Code aus und bestätigen Sie, dass die Tabellen nicht in Ihrem **_1_dev**-Katalog sind. Die Ausgabe unten zeigt alle Tabellen im Schema **default** außer **health_bronze_demo_08** und **health_silver_demo_08**.

```python
del_table(catalog_dev, 'default', 'health_bronze_demo_08')
del_table(catalog_dev, 'default', 'health_silver_demo_08')

spark.sql(f'''SHOW TABLES IN {catalog_dev}.default''').display()
```

2. Stellen wir das Bundle mit den spezifischen Konfigurationen in der **Development**-Umgebung bereit.

 **HINWEIS:** Wenn Sie `-t development` nicht angeben, wird standardmäßig in diese Umgebung bereitgestellt, da für das Development-Ziel in der Datei **databricks.yml** die Konfiguration `default: True` verwendet wird. Es ist jedoch besser, dies explizit anzugeben.

```bash
databricks bundle deploy -t development
```

3. Wenn die obige Zelle abgeschlossen ist (nach etwa einer Minute), sehen Sie sich den bereitgestellten Job namens `[dev username] development_demo08_dab_<username>` an.

 Prüfen Sie im Job Folgendes:

 - Wählen Sie die Job-Tasks aus und bestätigen Sie, dass jeder Task den in der Konfiguration angegebenen Lab-Compute-Cluster verwendet.

 - Suchen Sie im rechten Detailbereich den Abschnitt **Job parameters**. Beachten Sie die Werte:

 **Job parameters**
 - `catalog_name` – Ihr Katalog `labuser_UNIQUE_ID_1_dev`
 - `display_target` – `development`

 Denken Sie daran, dass wir den Job im Modus `development` bereitgestellt haben und dass er die in **databricks.yml** definierten Standardwerte der Variablen verwendet, um in Ihrem Entwicklungskatalog zu lesen und zu schreiben.

#### Checkpoint
![Dev](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/multiple-env-demo/dev-deployment.png)

4. Führen Sie den Job in der Entwicklungsumgebung aus.

 **HINWEIS:** Während der Job läuft, nehmen wir uns einen Moment Zeit für konkrete Fragen.

```bash
databricks bundle run -t development demo_08_job
```

**
 Ausführen über den Job-Schlüssel
 **

Wenn Sie einen Job über die Befehlszeile ausführen, müssen Sie den Job-Schlüssel aus der Job-YAML-Datei übergeben. 

In unserem Szenario steht beispielsweise Folgendes in unserer Job-YAML-Datei:

```YAML
  resources:
    jobs:
      demo_08_job:    #<---- Job-Schlüssel
        name: ${bundle.target}_demo08_dab_${workspace.current_user.userName}
        ...
```

Daher führen wir `databricks bundle run -t development demo_08_job` aus.

5. Führen Sie die folgende Zelle aus, um nach Abschluss des Jobs (nach etwa 2 Minuten) die verfügbaren Tabellen im Entwicklungskatalog anzuzeigen.

 Beachten Sie, dass die zwei neuen Tabellen erstellt wurden:

 - **health_bronze_demo_08**
 - **health_silver_demo_08**

```python
spark.sql(f'SHOW TABLES IN {catalog_dev}.default').display()
```

6. Zählen Sie die Zeilen in der Tabelle **health_bronze_demo_08** im Katalog **user_name_1_dev**. 

 Beachten Sie, dass sie 7.500 Zeilen enthält, da wir die Entwicklungsdaten verwenden.

 Das bestätigt, dass unser Job korrekt im **Entwicklungs**katalog gelesen und geschrieben hat.

```python
spark.sql(f'''
    SELECT count(*) 
    FROM {catalog_dev}.default.health_bronze_demo_08''').display()
```

### C4. In der Produktionsumgebung bereitstellen
Nachdem wir bestätigt haben, dass der Job in der Entwicklungsumgebung gelaufen ist, stellen wir denselben Job in der Produktionsumgebung bereit.

**HINWEIS:** In einer echten Produktion führen Sie den Job typischerweise mit einem Service Principal aus. 
 - Siehe die Dokumentation **Set a bundle run identity**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/run-as) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/run-as) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/run-as)

Zu Demonstrationszwecken führen wir den Produktions-Job einfach als Benutzer aus.

1. Bevor wir in die Produktion bereitstellen, prüfen (und löschen ggf.) wir die Tabellen im Katalog `<username>_3_prod`. 

 Beachten Sie, dass die folgenden Tabellen im Produktionskatalog nicht vorhanden sind:
 - **health_bronze_demo_08**
 - **health_silver_demo_08**

```python
del_table(catalog_prod, 'default', 'health_bronze_demo_08')
del_table(catalog_prod, 'default', 'health_silver_demo_08')

spark.sql(f'SHOW TABLES IN {catalog_prod}.default').display()
```

2. Sehen wir uns die **Produktions**konfigurationen an. 

 Beachten Sie Folgendes:

```YAML
  production:
    mode: production
    workspace:
      # host: https://dbc-d9be2316-40bd.cloud.databricks.com/
      root_path: /Workspace/Users/${workspace.current_user.userName}/.bundle/${bundle.name}/${bundle.target}

    ## In der Produktionsumgebung Variablenwerte ändern, um den Produktionskatalog username_3_prod zu verwenden
    variables:
        target_catalog: ${var.catalog_prod}
```

**
 Information
 **

- Hier ändern wir die Variable `target_catalog` so, dass sie auf unsere Variable `catalog_prod` verweist, die unseren Produktionskatalog referenziert. Dies überschreibt den Standard-Job-Parameter in der Datei **./resources/demo_08_job.job.yml**.

- Wir fügen keine Überschreibungen für den Cluster hinzu, den unser Job verwenden soll. Da wir keine Überschreibungen angeben, wird der Standard aus der Datei **./resources/demo_08_job.job.yml** verwendet, also Serverless Compute.

3. Stellen wir das Bundle mit den angegebenen Konfigurationen in der **Produktions**umgebung bereit.

```bash
databricks bundle deploy -t production
```

4. Wenn die obige Zelle abgeschlossen ist (nach etwa einer Minute), sehen Sie sich den bereitgestellten Job namens `production_demo08_dab_<username>` an.

 Prüfen Sie im Job Folgendes:

 - Wählen Sie die Job-Tasks aus und bestätigen Sie, dass jeder Task Serverless Compute verwendet.

 - Suchen Sie im rechten Detailbereich den Abschnitt **Job parameters**. Beachten Sie die Werte:

 **Job parameters**
 - `catalog_name` – Ihr Katalog `labuser_UNIQUE_ID_3_prod`
 - `display_target` – `production`

 Denken Sie daran, dass wir den Job im Modus `production` bereitgestellt haben und dass er die in **databricks.yml** angegebene Konfiguration verwendet, um im Produktionskatalog zu lesen und zu schreiben und Serverless Compute zu nutzen.

#### Checkpoint
![Dev](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/multiple-env-demo/prod-deployment.png)

5. Führen Sie den Produktions-Job mit der Databricks CLI aus.

```bash
databricks bundle run -t production demo_08_job
```

6. Während der Job läuft, sehen wir uns an, wo die Databricks-Assets gebündelt wurden.

 a. Klicken Sie in der Hauptnavigationsleiste mit der rechten Maustaste auf **Workspace** und wählen Sie *Open in a New Tab*.

 b. Navigieren Sie zu **Workspace > Users > Ihr Benutzername**.

 c. Öffnen Sie den Ordner **.bundle**. Hier sollten Sie die Namen der Bundles sehen, die Sie bereitgestellt haben (**demo05_bundle** und **demo_08_bundle**).

 d. Öffnen Sie das bereitgestellte **demo_08_bundle** (den Bundle-Namen, den wir in der Datei **databricks.yml** für diese Demonstration angegeben haben).

 e. Hier sehen wir, dass wir in die Ziele **development** und **production** bereitgestellt haben. 

 f. Wählen Sie den Ordner **production**.
 - Sie sehen die Ordner **artifacts**, **files** und **state**.

 g. Wählen Sie den Ordner **files**.
 - Beachten Sie, dass alle bereitgestellten Dateien für das Deployment im Produktionsmodus an diesem Ort im Workspace hinzugefügt wurden.

 h. Schließen Sie diesen Tab.

7. Inzwischen sollte der **Produktions**-Job abgeschlossen sein. 

 Navigieren Sie zum Job und bestätigen Sie, dass er erfolgreich ausgeführt wurde.

8. Führen Sie den folgenden Code aus, um die Tabellen in Ihrem Katalog `labuser_UNIQUE_ID_3_prod` anzuzeigen. 

 Beachten Sie, dass der Produktions-Job die Produktionstabellen erstellt hat:
 - **health_bronze_demo_08**
 - **health_silver_demo_08**

```python
spark.sql(f'SHOW TABLES IN {catalog_prod}.default').display()
```

9. Zählen Sie die Zeilen in der Tabelle **health_bronze_demo_08** im Katalog **labuser_UNIQUE_ID_3_prod**. 

 Beachten Sie, dass sie über 70.692 Zeilen enthält, da aus den Produktionsdaten gelesen und in den Produktionskatalog geschrieben wird.

```python
spark.sql(f'''
          SELECT count(*) 
          FROM {catalog_prod}.default.health_bronze_demo_08'''
          ).display()
```

## D. Die Bundles entfernen
Da wir mit diesem Bundle fertig sind, löschen wir es abschließend mit dem Befehl `databricks bundle destroy`.

 Standardmäßig werden Sie aufgefordert, das endgültige Löschen der zuvor bereitgestellten Jobs, Pipelines und Artefakte zu bestätigen. Um diese Abfragen zu überspringen und automatisch endgültig zu löschen, fügen Sie dem Befehl bundle destroy die Option `--auto-approve` hinzu.

1. Löschen Sie die Bundles!

```bash
databricks bundle destroy --auto-approve
databricks bundle destroy -t production --auto-approve
```

**Warnung!**

Das Entfernen eines Bundles löscht die zuvor bereitgestellten Jobs, Pipelines und Artefakte des Bundles endgültig. Diese Aktion kann nicht rückgängig gemacht werden.

Weitere Informationen finden Sie in der Dokumentation **Destroy the bundle**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/work-tasks#step-6-destroy-the-bundle) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/work-tasks#step-6-destroy-the-bundle) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/work-tasks#step-6-destroy-the-bundle)

## Fazit

In dieser Demonstration haben Sie dasselbe Bundle in zwei Zielen bereitgestellt und gesehen, wie Sie verhindern, dass Dev und Prod auseinanderdriften:

1. Den Job modularisiert, indem seine Definition in **./resources/demo_08_job.job.yml** verschoben und über das Mapping `include` eingebunden wurde.
2. Wiederverwendbare **Variablen** (`my_lab_user_name`, `catalog_dev`, `catalog_prod`, `target_catalog`, `raw_data_path`) und eine **Lookup**-Variable (`my_cluster_id`) definiert, die einen Clusternamen in eine Cluster-ID auflöst.
3. `databricks bundle validate --output json` verwendet, um das vollständig aufgelöste Bundle zu untersuchen und die Ersetzungen zu bestätigen.
4. Das Bundle in den Zielen `development` und `production` bereitgestellt und ausgeführt, wobei jedes Ziel Katalog und Compute nach Bedarf überschreibt.
5. Aufgeräumt, indem beide Ziele mit `databricks bundle destroy --auto-approve` und `databricks bundle destroy -t production --auto-approve` entfernt wurden.

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
