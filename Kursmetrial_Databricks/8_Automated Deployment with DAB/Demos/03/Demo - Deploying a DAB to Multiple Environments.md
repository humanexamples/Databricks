![DB Academy](../Includes/images/common/db-academy.png)

# [Video-Tutorial](https://customer-academy.databricks.com/learn/courses/3724/automated-deployment-with-declarative-automation-bundles/lessons/33987/demo-deploying-a-dab-to-multiple-environments)

# 03 - Bereitstellen eines Declarative Automation Bundle (DAB) in mehreren Umgebungen

## Übersicht

In dieser Demonstration stellen Sie denselben Job aus einem einzigen Bundle in zwei Umgebungen (`development` und `production`) bereit. Sie arbeiten mit **Bundle-Variablen**, **Lookup-Variablen**, dem **`include`**-Mapping zur Modularisierung von Ressourcendateien sowie dem **`targets`**-Mapping, um umgebungsspezifische Einstellungen (Catalog, Compute, Mode) zu überschreiben.

Das Beispiel baut auf dem einfachen Bundle aus der vorherigen Demonstration auf. Die wichtigsten neuen Konzepte hier sind: Variablen einmal definieren und wiederverwenden, Ressourcen in eigene YAML-Dateien aufteilen und Werte auf Target-Ebene überschreiben, sodass sich Entwicklung und Produktion unterscheiden können, ohne Job-Definitionen zu duplizieren.

## Lernziele

Am Ende dieser Demonstration können Sie:

1. **Bundle-Variablen definieren und referenzieren** in `databricks.yml`, einschließlich einer **Lookup**-Variable, die einen Cluster-Namen in eine Cluster-ID auflöst.
2. **Ressourcen modularisieren**, indem Sie eine Job-Definition in eine eigene YAML-Datei unter `resources/` verschieben und diese über das `include`-Mapping referenzieren.
3. **Werte pro Target überschreiben**, indem Sie `mode`, `variables` und Overrides auf Task-Ebene für `development` und `production` unterschiedlich setzen.
4. **Ein vollständig aufgelöstes Bundle prüfen** mit `databricks bundle validate --output json`, um zu sehen, was tatsächlich bereitgestellt wird.
5. **Dasselbe Bundle bereitstellen, ausführen und löschen** für zwei Targets mit `databricks bundle deploy -t <target>`, `databricks bundle run -t <target> <job_key>` und `databricks bundle destroy --auto-approve`.

## ERFORDERLICH - WÄHLEN SIE EINE COMPUTE-UMGEBUNG

**Wählen Sie All-Purpose Compute**

Dieses Notebook erfordert **All-Purpose Compute** (Dedicated). Serverless wird für dieses Notebook nicht unterstützt.

Führen Sie die folgenden Schritte aus, um einen All-Purpose-Compute-Cluster anzuhängen:

1. Navigieren Sie oben rechts in diesem Notebook und klicken Sie auf das Dropdown-Menü, um Ihren `labuser_USERNAME`-Cluster auszuwählen.
- Standardmäßig verwendet das Notebook möglicherweise **Serverless**.

2. Wenn Ihr Cluster verfügbar ist, wählen Sie ihn aus und fahren Sie mit der nächsten Zelle fort. Wenn der Cluster nicht angezeigt wird:

- Wählen Sie im Dropdown-Menü **More** aus.

- Wählen Sie im Popup **Attach to an existing compute resource** das erste Dropdown-Menü aus. Dort sehen Sie einen eindeutigen Cluster-Namen. Wählen Sie diesen Cluster aus.

⚠️ **HINWEIS:** Wenn der Cluster den Status **terminated** anzeigt (roter Punkt in der Cluster-Auswahl), muss er gestartet werden, bevor Sie ihn anhängen können. Klicken Sie auf den Cluster und dann auf **Start**, und warten Sie einige Minuten, bis ein grüner Punkt angezeigt wird.

## ERFORDERLICH - DATEN-SETUP

**Daten-Setup**

Denken Sie daran, dass Ihre Umgebung mit dem Notebook **0 - REQUIRED - Course Setup and Authentication** eingerichtet wurde.

Wenn Sie Ihr Lab beenden oder Ihre Lab-Sitzung abläuft, wird Ihre Umgebung zurückgesetzt. Sie müssen das Notebook **0 - REQUIRED - Course Setup and Authentication** erneut ausführen, um die Catalogs und Daten für Ihre Umgebung neu zu erstellen.

## A. Einrichtung der Lernumgebung

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren.

```text
%run ../Includes/Classroom-Setup-03
```

1. Führen Sie den folgenden Databricks-CLI-Befehl aus, um zu bestätigen, dass die Databricks CLI authentifiziert ist.

```bash
%sh
databricks catalogs list
```

**
FEHLERBEHEBUNG BEI DATABRICKS-CLI-FEHLERN:
**

  - Wenn ein Databricks-CLI-Authentifizierungsfehler auftritt, bedeutet dies, dass die Authentifizierung nicht erfolgreich war. Stellen Sie sicher, dass Sie das Notebook mit Ihrem **All-Purpose Compute** ausgeführt haben.

  - Wenn der folgende Fehler auftritt, bedeutet dies, dass Ihre Datei **databricks.yml** durch eine Änderung Syntaxprobleme aufweist. Selbst bei Nicht-DAB-CLI-Befehlen ist die Datei **databricks.yml** weiterhin erforderlich, da sie wichtige Authentifizierungsdetails wie Host und Profile enthalten kann, die von den CLI-Befehlen verwendet werden.

![CLI Invalid YAML](../Includes/images/databricks_cli_error_invalid_yaml.png)

2. Führen Sie den Befehl `databricks -v` aus, um die Version der Databricks CLI anzuzeigen. 

Bestätigen Sie, dass die Zelle die Version **v0.298.0** zurückgibt.

```bash
%sh
databricks -v
```

## B. Erkunden der Entwicklungs- und Produktionsdaten

1. Sehen Sie sich die Entwicklungsdaten in Ihrem Catalog **labuser_UNIQUE_ID_1_dev** an. Beachten Sie Folgendes:
   - Er enthält 7.500 Zeilen (ohne die Kopfzeile).
   - Die PII-Daten sind maskiert.

**HINWEIS:** In diesem Szenario ist der Beispieldatensatz in der Entwicklungsumgebung eine Teilmenge der Produktionsdaten, die zu Testzwecken verwendet wird. Wir werden später gegen diesen Datensatz testen.

```python
spark.sql(f'''
SELECT COUNT(*) AS Total_DEV
FROM text.`/Volumes/{catalog_dev}/default/health`
LIMIT 5
''').display()

spark.sql(f'''
SELECT *
FROM text.`/Volumes/{catalog_dev}/default/health`
LIMIT 5
''').display()
```

2. Sehen Sie sich die Produktionsdaten in Ihrem Catalog **labuser_UNIQUE_ID_3_prod** an. Beachten Sie Folgendes:
   - Er enthält 70.695 Zeilen.
   - Die PII-Daten sind verfügbar.

**HINWEIS:** In unserem Szenario wird dem **health**-Volume im Produktions-Catalog täglich eine CSV-Datei hinzugefügt. Wenn Sie das **health**-Volume im Produktions-Catalog untersuchen, finden Sie bereits Daten für 3 Tage.

```python
spark.sql(f'''
SELECT count(*) AS Total_PROD
FROM text.`/Volumes/{catalog_prod}/default/health`
''').display()

spark.sql(f'''
SELECT *
FROM text.`/Volumes/{catalog_prod}/default/health`
LIMIT 5
''').display()
```

## C. Bereitstellen eines DAB in mehreren Umgebungen (Entwicklung und Produktion)

In diesem Beispiel verwenden wir denselben Job aus Demonstration 01. Hier sind die gewünschten Konfigurationen für jede Umgebung (Catalog):

#### Konfigurationsanforderungen für das Entwicklungs-Target:
- Verwenden Sie den Wert **labuser_UNIQUE_ID_1_dev** als Entwicklungs-Catalog zum Lesen und Schreiben.
- Führen Sie den Job mit dem **kleinen Lab-Cluster** aus, da die Entwicklungsdaten klein und statisch sind.
- Machen Sie die Entwicklungsumgebung zur **Standard**-Umgebung.

#### Konfigurationsanforderungen für das Produktions-Target:
- Verwenden Sie den Wert **labuser_UNIQUE_ID_3_prod** als Produktions-Catalog, um auf die Produktionsdaten zuzugreifen.
- Führen Sie den Job mit Serverless-Compute aus, da die Daten kontinuierlich wachsen und Databricks Serverless sich so an den Compute-Bedarf anpassen kann.

**Deployment-Modi (`development` / `production`)**: [AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/deployment-modes) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/deployment-modes) | [GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/deployment-modes)

### C1. Erkunden der Job-YAML-Datei unter `resources`
1. Öffnen Sie die Datei **./resources/demo_03_job.job.yml** in einem neuen Tab und erkunden Sie die Job-Konfiguration.

   a. Der Job-Key-Name lautet `demo03_job`.

   b. Die Job-Namensvorlage lautet `${bundle.target}_demo3_dab_${workspace.current_user.userName}`. Die Substitution zum Zeitpunkt der Bereitstellung ergibt einen Namen, der die Zielumgebung und den Benutzer enthält.

   c. Der Job verwendet die Notebooks `../src/create_bronze_table.ipynb` und `../src/create_silver_table.ipynb`.

   d. Scrollen Sie in der YAML-Datei nach unten und beachten Sie, dass die Parameter dieses Jobs Variablen verwenden:
   ```yaml
      parameters:
      - name: display_target
        default: ${bundle.target}
      - name: catalog_name
        default: ${var.target_catalog}
    ```

   e. Es ist kein Cluster angegeben, daher läuft dieser Job standardmäßig auf Serverless-Compute.

   f. Lassen Sie diesen Tab geöffnet.

2. Führen Sie den folgenden Code aus, um Ihren Lab-Benutzernamen zu ermitteln. Sie benötigen diesen für den nächsten Abschnitt.

```python
print(my_catalog)
```

### C2. Erkunden und Bearbeiten der Datei `databricks.yml`

1. Navigieren Sie in Ihrem anderen Tab zur Datei **./databricks.yml** im Hauptordner der Demonstration und erkunden Sie das Bundle. Beachten Sie Folgendes:

   a. Dieses Bundle heißt `demo03_bundle`.

   b. Dieses Bundle enthält ein `include`-Mapping auf oberster Ebene:
- Dieses gibt den Pfad zur Datei **./resources/demo_03_job.job.yml** an.
- Diese YAML-Datei definiert den Job, der zum Zeitpunkt der Bereitstellung in das `resources`-Mapping eingefügt wird, wie Sie im vorherigen Schritt gesehen haben.
- **HINWEIS:** Mit zunehmendem Umfang Ihres Projekts empfiehlt es sich, die Ressourcen des DAB in einzelne YAML-Dateien pro Ressource zu modularisieren.

   c. Dieses DAB enthält außerdem ein `variables`-Mapping auf oberster Ebene. Sehen wir uns die definierten Variablen an:

- Die Variable `my_lab_user_name` verwendet die Substitution `${workspace.current_user.short_name}`. Diese ermittelt Ihren Benutzernamen für das Lab und gibt den korrekten Wert an die übrigen Variablen für jeden Catalog weiter.

- Die Variable `catalog_dev` verwendet die Variable `my_lab_user_name` und hängt `_1_dev` an Ihren Benutzernamen an, um auf Ihren Entwicklungs-Catalog zu verweisen.

- Die Variable `catalog_prod` verwendet die Variable `my_lab_user_name` und hängt `_3_prod` an Ihren Benutzernamen an, um auf Ihren Produktions-Catalog zu verweisen.

- Die Variable `target_catalog` verweist standardmäßig auf Ihren Entwicklungs-Catalog.
- Diese Variable wird in den Job-Parametern referenziert, die in **./resources/demo_03_job.job.yml** definiert sind:

```yaml
      parameters:
      - name: display_target
        default: ${bundle.target}
      - name: catalog_name
        default: ${var.target_catalog}
    ```

- Die Variable `raw_data_path` verweist über `target_catalog` auf das **health**-Volume, das standardmäßig auf das **health**-Volume in Ihrem Entwicklungs-Catalog zeigt.

**Variablen und Substitutionen (`${var.…}`, `${bundle.…}`, Lookups)**: [AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/variables) | [Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/variables) | [GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/variables)

**
TO DO - Legen Sie den Cluster-Lookup in **databricks.yml** fest
**

Die Variable `cluster_id` verwendet einen **Lookup**, um zum Zeitpunkt der Bereitstellung einen Cluster-Namen in eine Cluster-ID aufzulösen. Suchen Sie die Variable in **databricks.yml** und aktualisieren Sie den Wert `cluster:` mit dem Namen **Ihres** Lab-Clusters.

```yaml
variables:
  cluster_id:
    description: Look up your lab cluster's ID by name.
    lookup:
      cluster: <your-cluster-name>     # <-- hier Ihren Clusternamen einfügen
```

Im Databricks Academy Lab entspricht Ihr Cluster-Name dem Wert, der von der obigen Zelle ausgegeben wird (Ihr Lab-Benutzername).

Lassen Sie den Tab mit Ihrer Datei **databricks.yml** geöffnet.

2. Erkunden Sie in der Datei **databricks.yml** das `targets`-Mapping der ersten Ebene. Beachten Sie Folgendes:

   a. Beim Bereitstellen in das Target `development`:

- Es ist `mode: development` gesetzt.

- Es ist das **Standard**-Target.

- Der `root_path`, in dem die Dateien abgelegt werden, endet mit dem Target-Namen `development`.

- Das Compute wird für jede Task im `resources`-Mapping überschrieben. Die zuvor definierte Lookup-Variable `my_cluster_id` liefert die ID des kleinen Lab-Clusters. Wir tun dies, weil die Entwicklungsdaten klein sind und kein großes Compute benötigen.

   b. Beim Bereitstellen in das Target `production`:

- Es ist `mode: production` gesetzt.

- Die Variable `target_catalog` wird vom Standardwert `${var.catalog_dev}` auf `${var.catalog_prod}` überschrieben. Dadurch liest und schreibt der bereitgestellte Job in den Produktions-Catalog.

- Der `root_path`, in dem die Dateien abgelegt werden, endet mit dem Target-Namen `production`.

- Der Job läuft auf **Serverless**, da wir das in der Ressourcen-YAML definierte Compute nicht überschreiben.

**
Information
**

- Falls verfügbar, könnten Sie den `host` angeben und auswählen, in welchen Databricks-Workspace bereitgestellt werden soll. In diesem Lab haben wir nur einen Workspace, daher isolieren wir die Umgebungen über den **Catalog**.

- Dieses Beispiel überschreibt nur wenige Konfigurationen für das Target `production`. Viele weitere Einstellungen können überschrieben werden, siehe die Dokumentation **Bundle settings**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/settings) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/settings) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/settings)

3. Validieren Sie das Bundle für diese Demonstration und bestätigen Sie, dass die Validierung erfolgreich ist.

**HINWEIS:** Wenn das Bundle nicht validiert werden kann, lesen Sie die Fehlermeldung und beheben Sie das Problem. Häufige Ursachen:

- Fehlende Dateiendungen bei den Notebook-Pfaden in der Datei **demo_03_job.job.yml**.

- Variablen, die in der Datei **databricks.yml** nicht korrekt definiert oder referenziert wurden.

```bash
%sh
databricks bundle validate
```

**
Fehlerbehebung
**

Wenn nach der Validierung Ihres Bundles der folgende Fehler angezeigt wird, könnte das Format Ihres Notebooks fehlerhaft sein.

`Error: notebook src/create_bronze_table.ipynb not found`. 

Überprüfen Sie das Format Ihres Notebooks und passen Sie es entsprechend an. 

4. Sie können `databricks bundle validate --output json` ausführen, um die vollständig aufgelöste Bundle-Konfiguration als JSON anzuzeigen. Dies ist hilfreich, um zu bestätigen, dass die Variablensubstitutionen wie erwartet aufgelöst wurden.

Einige häufig verwendete Substitutionen:

- `${bundle.name}`

- `${bundle.target}`  (wird gegenüber dem veralteten `${bundle.environment}` bevorzugt)

- `${workspace.host}`

- `${workspace.current_user.short_name}`

- `${workspace.current_user.userName}`

- `${workspace.file_path}`

- `${workspace.root_path}`

- `${resources.jobs.<job-name>.id}`

- `${resources.models.<model-name>.name}`

- `${resources.pipelines.<pipeline-name>.name}`

Zum Beispiel im folgenden JSON-Output:

- `bundle.target` löst sich zu `development` auf. Die YAML-Datei verwendet `${bundle.target}`, um darauf zu verweisen.
- Suchen Sie nach `workspace` > `current_user` > `short_name`. Dieser Wert liefert Ihren Lab-Benutzernamen.

```bash
%sh
databricks bundle validate --output json
```

### C3. Bereitstellen in der Entwicklungsumgebung

1. Löschen Sie die Tabellen **health_bronze_demo03** und **health_silver_demo03**, falls sie in unserem Entwicklungs-Catalog vorhanden sind, damit wir überprüfen können, dass unser Bundle sie bei der Bereitstellung erstellt.

Führen Sie den Code aus und bestätigen Sie, dass die Tabellen nicht in Ihrem Catalog **_1_dev** vorhanden sind. Die untenstehende Ausgabe zeigt alle Tabellen an, die im Schema **default** vorhanden sind, mit Ausnahme von **health_bronze_demo03** und **health_silver_demo03**.

```python
# die Tabellen löschen, falls sie existieren
del_table(catalog_dev, 'default', 'health_bronze_demo03')
del_table(catalog_dev, 'default', 'health_silver_demo03')

spark.sql(f'''SHOW TABLES IN {catalog_dev}.default''').display()
```

2. Stellen wir das Bundle mithilfe der spezifischen Konfigurationen in der Umgebung **Entwicklung** bereit.

**HINWEIS:** Wenn Sie `-t development` nicht angeben, wird standardmäßig in diese Umgebung bereitgestellt, da für das Entwicklungs-Target in der Datei **databricks.yml** die Konfiguration `default: True` verwendet wird. Es ist jedoch besser, dies explizit anzugeben.

```bash
%sh
databricks bundle deploy -t development
```

3. Wenn die obige Zelle abgeschlossen ist (nach etwa einer Minute), sehen Sie sich den bereitgestellten Job mit dem Namen `[dev username] development_demo3_dab_<username>` an.

Überprüfen Sie im Job Folgendes:

- Wählen Sie die Job-Tasks aus und bestätigen Sie, dass jede Task den in der Konfiguration angegebenen Lab-Compute-Cluster verwendet.

- Suchen Sie im rechten Detailbereich den Abschnitt **Job parameters**. Notieren Sie sich die Werte:

**Job parameters**
- `catalog_name` - Ihr Catalog `labuser_UNIQUE_ID_1_dev`
- `display_target` – `development`

Denken Sie daran, dass wir den Job im Modus `development` bereitgestellt haben und dieser die in **databricks.yml** definierten Standardwerte der Variablen verwendet, um aus Ihrem Entwicklungs-Catalog zu lesen und in diesen zu schreiben.

#### Checkpoint
![Dev](../Includes/images/multiple-env-demo/dev-deployment.png)

4. Führen Sie den Job in der Entwicklungsumgebung aus.

**HINWEIS:** Während der Job ausgeführt wird, nehmen wir uns einen Moment Zeit, um etwaige Fragen zu klären.

```bash
%sh
databricks bundle run -t development demo03_job
```

**
Ausführen mithilfe des Job-Keys
**

Wenn Sie einen Job über die Befehlszeile ausführen, müssen Sie den Job-Key aus der Job-YAML-Datei übergeben. 

In unserem Szenario haben wir beispielsweise Folgendes in unserer Job-YAML-Datei:

```YAML
  resources:
    jobs:
      demo03_job:    #<---- Job key
        name: ${bundle.target}_demo3_dab_${workspace.current_user.userName}
        ...
```

Wir führen also `databricks bundle run -t development demo03_job` aus.

5. Führen Sie die folgende Zelle aus, um die verfügbaren Tabellen im Entwicklungs-Catalog anzuzeigen, nachdem der Job abgeschlossen ist (nach etwa 2 Minuten).

Beachten Sie, dass die beiden neuen Tabellen erstellt wurden:

- **health_bronze_demo03**
- **health_silver_demo03**

```python
spark.sql(f'SHOW TABLES IN {catalog_dev}.default').display()
```

6. Zählen Sie die Anzahl der Zeilen in der Tabelle **health_bronze_demo03** im Catalog **user_name_1_dev**. 

Beachten Sie, dass sie 7.500 Zeilen enthält, da wir die Entwicklungsdaten verwenden.

Dies bestätigt, dass unser Job korrekt aus dem **Entwicklungs**-Catalog gelesen und in diesen geschrieben hat.

```python
spark.sql(f'''
    SELECT count(*) 
    FROM {catalog_dev}.default.health_bronze_demo03''').display()
```

### C4. Bereitstellen in der Produktionsumgebung
Nachdem wir bestätigt haben, dass der Job in der Entwicklungsumgebung ausgeführt wurde, stellen wir denselben Job nun in der Produktionsumgebung bereit.

**HINWEIS:** In einer echten Produktionsumgebung führen Sie den Job in der Regel mit einem Service Principal aus. 
  - Siehe die Dokumentation **Set a bundle run identity**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/run-as) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/run-as) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/run-as)

Zu Demonstrationszwecken führen wir den Produktions-Job hier einfach als Benutzer aus.

1. Bevor wir in Produktion bereitstellen, überprüfen wir die Tabellen im Catalog `<username>_3_prod` (und löschen sie gegebenenfalls). 

Beachten Sie, dass die folgenden Tabellen im Produktions-Catalog nicht vorhanden sind:
- **health_bronze_demo03**
- **health_silver_demo03**

```python
del_table(catalog_prod, 'default', 'health_bronze_demo03')
del_table(catalog_prod, 'default', 'health_silver_demo03')

spark.sql(f'SHOW TABLES IN {catalog_prod}.default').display()
```

2. Sehen wir uns die Konfigurationen für **production** an. 

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

- Hier ändern wir die Variable `target_catalog`, sodass sie auf unsere Variable `catalog_prod` verweist, die wiederum auf unseren Produktions-Catalog verweist. Dies überschreibt den Standard-Job-Parameter in der Datei **./resources/demo_03_job.job.yml**.

- Wir fügen keine Overrides bezüglich des für unseren Job zu verwendenden Clusters hinzu. Da wir keine Overrides angeben, wird der in der Datei **./resources/demo_03_job.job.yml** festgelegte Standard verwendet, welcher Serverless-Compute nutzt.

3. Stellen wir das Bundle mithilfe der angegebenen Konfigurationen in der Umgebung **Produktion** bereit.

```bash
%sh
databricks bundle deploy -t production
```

4. Wenn die obige Zelle abgeschlossen ist (nach etwa einer Minute), sehen Sie sich den bereitgestellten Job mit dem Namen `production_demo3_dab_<username>` an.

Überprüfen Sie im Job Folgendes:

- Wählen Sie die Job-Tasks aus und bestätigen Sie, dass jede Task Serverless-Compute verwendet.

- Suchen Sie im rechten Detailbereich den Abschnitt **Job parameters**. Notieren Sie sich die Werte:

**Job parameters**
- `catalog_name` - Ihr Catalog `labuser_UNIQUE_ID_3_prod`
- `display_target` – `production`

Denken Sie daran, dass wir den Job im Modus `production` bereitgestellt haben und dieser die in **databricks.yml** angegebene Konfiguration verwendet, um aus dem Produktions-Catalog zu lesen, in diesen zu schreiben und Serverless-Compute zu nutzen.

#### Checkpoint
![Dev](../Includes/images/multiple-env-demo/prod-deployment.png)

5. Führen Sie den Produktions-Job mithilfe der Databricks CLI aus.

```bash
%sh
databricks bundle run -t production demo03_job
```

6. Während der Job ausgeführt wird, sehen wir uns an, wo die Databricks-Assets gebündelt wurden.

a. Klicken Sie in der Hauptnavigationsleiste mit der rechten Maustaste auf **Workspace** und wählen Sie *Open in a New Tab* aus.

b. Navigieren Sie zu **Workspace > Users > Ihr Benutzername**.

c. Öffnen Sie den Ordner **.bundle**. Hier sollten Sie die Namen der von Ihnen bereitgestellten Bundles sehen (**demo01_bundle** und **demo03_bundle**).

d. Öffnen Sie das bereitgestellte **demo03_bundle** (der Bundle-Name, den wir für diese Demonstration in der Datei **databricks.yml** angegeben haben).

e. Hier sehen wir, dass wir in die Targets **development** und **production** bereitgestellt haben. 

f. Wählen Sie den Ordner **production** aus.
- Sie sehen die Ordner **artifacts**, **files** und **state**.

g. Wählen Sie den Ordner **files** aus.
- Beachten Sie, dass alle von uns bereitgestellten Dateien für die Bereitstellung im Produktions-Modus an diesem Ort im Workspace hinzugefügt wurden.

h. Schließen Sie diesen Tab.

7. Zu diesem Zeitpunkt sollte der **production**-Job abgeschlossen sein. 

Navigieren Sie zum Job und bestätigen Sie, dass er erfolgreich ausgeführt wurde.

8. Führen Sie den folgenden Code aus, um die Tabellen in Ihrem Catalog `labuser_UNIQUE_ID_3_prod` anzuzeigen. 

Beachten Sie, dass der Produktions-Job die folgenden Produktionstabellen erstellt hat:
- **health_bronze_demo03**
- **health_silver_demo03**

```python
spark.sql(f'SHOW TABLES IN {catalog_prod}.default').display()
```

9. Zählen Sie die Anzahl der Zeilen in der Tabelle **health_bronze_demo03** im Catalog **labuser_UNIQUE_ID_3_prod**. 

  Beachten Sie, dass sie über 70.692 Zeilen enthält, da aus den Produktionsdaten gelesen und in den Produktions-Catalog geschrieben wird.

```python
spark.sql(f'''
          SELECT count(*) 
          FROM {catalog_prod}.default.health_bronze_demo03'''
          ).display()
```

## D. Löschen der Bundles
Da wir mit diesem Bundle nun fertig sind, löschen wir es abschließend mit dem Befehl `databricks bundle destroy`.

  Standardmäßig werden Sie aufgefordert, die endgültige Löschung der zuvor bereitgestellten Jobs, Pipelines und Artefakte zu bestätigen. Um diese Bestätigungsabfragen zu überspringen und die endgültige Löschung automatisch durchzuführen, fügen Sie dem Befehl bundle destroy die Option `--auto-approve` hinzu.

1. Löschen Sie die Bundles!

```bash
%sh
databricks bundle destroy --auto-approve
databricks bundle destroy -t production --auto-approve
```

**Achtung!**

Das Löschen eines Bundles entfernt die zuvor bereitgestellten Jobs, Pipelines und Artefakte des Bundles endgültig. Diese Aktion kann nicht rückgängig gemacht werden.

Weitere Informationen finden Sie in der Dokumentation **Destroy the bundle**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/work-tasks#step-6-destroy-the-bundle) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/work-tasks#step-6-destroy-the-bundle) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/work-tasks#step-6-destroy-the-bundle)

## Fazit

In dieser Demonstration haben Sie dasselbe Bundle in zwei Targets bereitgestellt und gesehen, wie sich Entwicklung und Produktion vor einem Auseinanderdriften bewahren lassen:

1. Den Job modularisiert, indem seine Definition in **./resources/demo_03_job.job.yml** verschoben und über das `include`-Mapping eingebunden wurde.
2. Wiederverwendbare **Variablen** (`my_lab_user_name`, `catalog_dev`, `catalog_prod`, `target_catalog`, `raw_data_path`) sowie eine **Lookup**-Variable (`my_cluster_id`) definiert, die einen Cluster-Namen in eine Cluster-ID auflöst.
3. `databricks bundle validate --output json` verwendet, um das vollständig aufgelöste Bundle zu prüfen und die Substitutionen zu bestätigen.
4. Das Bundle sowohl in `development` als auch in `production` bereitgestellt und ausgeführt, wobei jedes Target den Catalog und das Compute nach Bedarf überschrieben hat.
5. Aufgeräumt, indem beide Targets mit `databricks bundle destroy --auto-approve` und `databricks bundle destroy -t production --auto-approve` gelöscht wurden.

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
