Sie sind dafür verantwortlich, Databricks-Projekte in Ihrer Organisation mit **Declarative Automation Bundles (DABs)** bereitzustellen. 

Sie haben das Projekt in **09L - Deploy a Simple DAB** für das Deployment in eine einzelne Entwicklungsumgebung konfiguriert. 

Ihre nächste Aufgabe ist es, das Bundle so zu erweitern, dass **derselbe** Job mit unterschiedlichen Konfigurationen pro Ziel in **beiden** Umgebungen – Development und Production – bereitgestellt werden kann. Das erreichen Sie mit **Bundle-Variablen** und **Überschreibungen auf Zielebene**.



```bash
# Einen CLI-Befehl ausführen, um zu bestätigen, dass die Version der Databricks CLI **v0.298.0** ist.
%sh
databricks -v

databricks bundle validate

databricks bundle validate --output json

databricks bundle deploy -t development
databricks bundle run -t development demo_08_job

databricks bundle deploy -t production
databricks bundle run -t production demo_08_job

databricks bundle destroy --auto-approve
databricks bundle destroy -t production --auto-approve
```

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









------



------

**
 FEHLERBEHEBUNG BEI FEHLERN DER DATABRICKS CLI:
 **

 - Wenn ein Authentifizierungsfehler der Databricks CLI auftritt, war die Authentifizierung nicht erfolgreich. Bestätigen Sie, dass Sie das Notebook mit Ihrem **All-Purpose-Compute** ausgeführt haben.

 - Wenn der unten gezeigte Fehler auftritt, enthält Ihre Datei **databricks.yml** aufgrund einer Änderung Syntaxfehler. Auch für CLI-Befehle, die nichts mit DABs zu tun haben, ist die Datei **databricks.yml** weiterhin erforderlich, da sie wichtige Authentifizierungsdetails wie Host und Profil enthalten kann, die von den CLI-Befehlen verwendet werden.

![CLI Invalid YAML](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/databricks_cli_error_invalid_yaml.png)

## E. Aufgabe 1 – Ihren Lab-Benutzernamen ermitteln

Sie benötigen Ihren Lab-Benutzernamen in der nächsten Aufgabe, um eine Bundle-Variable zu befüllen. Führen Sie die folgende Zelle aus, um ihn auszugeben.

```python
print(my_catalog)
```

## F. Aufgabe 2 – Die Ressourcen-YAML-Datei aktualisieren

Öffnen Sie in einem neuen Tab die Datei **./resources/lab09_nyc.job.yml** und führen Sie Folgendes aus:

**Schritt 2.1** – Setzen Sie den Job-`name` so, dass Ihr Benutzername dynamisch angehängt wird: `name: lab09_dab_${workspace.current_user.userName}`

**Schritt 2.2** – Fügen Sie unter `parameters` die Ersetzung `${bundle.target}` als Standardwert für `display_target` hinzu
 - So spiegelt der Parameter automatisch wider, in welches Ziel das Bundle bereitgestellt wurde.

**TIPP:** Dokumentation zu Variablen und Ersetzungen:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/variables) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/variables) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/variables)

##### LÖSUNG

<details>
 <summary>FÜR DIE LÖSUNG AUFKLAPPEN (Ressourcen-YAML)</summary>

```yaml
resources:
  jobs:
    lab09_dab:
      name: lab09_dab_${workspace.current_user.userName}   # <--- Ihren Benutzernamen anhängen
      tasks:
        - task_key: create_nyc_tables
          notebook_task:
            notebook_path: ../src/our_project_code.sql
            source: WORKSPACE
      parameters:
        - name: display_target
          default: ${bundle.target}                        # <--- Ersetzung bundle.target
```
</details>

## G. Aufgabe 3 – **databricks.yml** aktualisieren

Öffnen Sie im selben Tab die Datei **databricks.yml**. Erkunden Sie zunächst das Bundle und führen Sie dann die vier folgenden Teilschritte aus.

**Was Ihnen in der vorhandenen Datei auffallen sollte:**

- Das Bundle heißt `demo09_lab_bundle`.
- Das Mapping `include` ist **leer** (das beheben Sie in 3.1).
- Das Mapping `variables` definiert mehrere Variablen (eine davon setzen Sie in 3.2).
- Das Mapping `targets` enthält ein Ziel `dev` und ein Ziel `prod` (in 3.3 und 3.4 fügen Sie jedem eine Parameter-Überschreibung hinzu).

### Schritt 3.1 – Die Ressourcendatei zu `include` hinzufügen

Fügen Sie **./resources/lab09_nyc.job.yml** zum Mapping `include` hinzu, damit der in Aufgabe 2 bearbeitete Job in das Bundle aufgenommen wird.
 - **TIPP:** Dokumentation zum Mapping `include`:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/settings#include) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/settings#include) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/settings#include)

### Schritt 3.2 – Die Variable `user_name` setzen

Setzen Sie den Wert der Variablen `user_name` auf Ihren Lab-Benutzernamen (aus Aufgabe 1). 
 - Die Variable `user_name` speist die Variablen `catalog_dev` und `catalog_prod`; wenn sie stimmt, sind auch alle Referenzen korrekt.

### Schritt 3.3 – `catalog_name` für das Ziel `dev` überschreiben

 - Fügen Sie unter dem Ziel `dev` einen Job-Parameter namens `catalog_name` hinzu, dessen Standardwert `${var.catalog_dev}` ist.

### Schritt 3.4 – `catalog_name` für das Ziel `prod` überschreiben

 - Fügen Sie unter dem Ziel `prod` einen Job-Parameter namens `catalog_name` hinzu, dessen Standardwert `${var.catalog_prod}` ist.

**Warum das funktioniert:** Derselbe Job läuft je nach Ziel, in das Sie bereitstellen, gegen den Dev- oder den Prod-Katalog – ohne dass die Job-Definition dupliziert werden muss.

**HINWEIS:** Ein vollständiges Beispiel für **databricks.yml** finden Sie im Ordner **solutions**, falls Sie nicht weiterkommen.

## H. Aufgabe 4 – Das Bundle validieren

Validieren Sie Ihre Bundle-Konfigurationsdatei **databricks.yml** mit der Databricks CLI. Führen Sie die Zelle aus und bestätigen Sie, dass die Validierung erfolgreich ist. Bei einem Fehler korrigieren Sie die Datei **databricks.yml** und führen die Zelle erneut aus.

**TIPP:** Dokumentation zu den CLI-Befehlen `databricks bundle`:
[AWS](https://docs.databricks.com/aws/en/dev-tools/cli/bundle-commands) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/cli/bundle-commands) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/cli/bundle-commands)

```python
# <FILL-IN>
```

**
 Fehlerbehebung
 **

Wenn Sie nach dem Validieren Ihres Bundles den folgenden Fehler sehen, ist das Format Ihres Notebooks möglicherweise falsch.

`Error: notebook src/xxx not found`. 

Prüfen Sie das Format Ihres Notebooks und passen Sie es entsprechend an.

##### LÖSUNG

<details>
 <summary>FÜR DEN LÖSUNGSCODE AUFKLAPPEN</summary>

```
<!-------------------ADD SOLUTION CODE BELOW------------------->
databricks bundle validate
<!-------------------END SOLUTION CODE------------------->
```

</details>

## I. Aufgabe 5 – In das Ziel `dev` bereitstellen

Stellen Sie das Bundle mit der Databricks CLI in der Entwicklungsumgebung bereit.

Nach Abschluss der Zelle:

- Prüfen Sie manuell, ob der Job erfolgreich erstellt wurde. Der Job-Name lautet **[dev ] lab09_dab_**.
- Prüfen Sie die **Job parameters** und bestätigen Sie:
 - `catalog_name` verweist auf Ihren Katalog `labuser_UNIQUE_ID_1_dev`
 - `display_target` ist `dev`

**HINWEIS:** Das Deployment dauert etwa eine Minute.

**TIPP:** Dokumentation zu den CLI-Befehlen `databricks bundle`:
[AWS](https://docs.databricks.com/aws/en/dev-tools/cli/bundle-commands) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/cli/bundle-commands) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/cli/bundle-commands)

```python
# <FILL-IN>
```

#### Checkpoint – Dev-Deployment
![Dev](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/multiple-env-lab/dev-deployment.png)

##### LÖSUNG

<details>
 <summary>FÜR DEN LÖSUNGSCODE AUFKLAPPEN</summary>

```
<!-------------------ADD SOLUTION CODE BELOW------------------->
databricks bundle deploy -t dev
<!-------------------END SOLUTION CODE------------------->
```

</details>

## J. Aufgabe 6 – Den `dev`-Job ausführen

Führen Sie den bereitgestellten Job gegen das Ziel `dev` aus.

**HINWEIS:** Dies dauert 1–2 Minuten.

**TIPP:** Verwenden Sie den **Job-Schlüssel** aus dem Mapping `resources` (Ihr Name wird abweichen):

```yaml
resources:
  jobs:
    lab09_dab:    # <--- Das ist der Job-Schlüssel
      name: lab09_dab_${workspace.current_user.userName}
```

```python
# <FILL-IN>
```

##### LÖSUNG

<details>
 <summary>FÜR DEN LÖSUNGSCODE AUFKLAPPEN</summary>

```
<!-------------------ADD SOLUTION CODE BELOW------------------->
databricks bundle run -t dev lab09_dab
<!-------------------END SOLUTION CODE------------------->
```

</details>

## K. Aufgabe 7 – Die `dev`-Tabellen überprüfen

Führen Sie nach Abschluss des Jobs die folgenden Zellen aus, um Folgendes zu bestätigen:

- Die Tabellen **nyctaxi_bronze** und **nyctaxi_silver** existieren beide in Ihrem Katalog **labuser_UNIQUE_ID_1_dev**.
- Die Tabelle **nyctaxi_bronze** enthält **100 Zeilen**.

```python
spark.sql(f'SHOW TABLES IN {catalog_dev}.default').display()
```

```python
check_nyctaxi_bronze_table(user_catalog = catalog_dev, total_count=100)
```

## L. Aufgabe 8 – In das Ziel `prod` bereitstellen

Stellen Sie das Bundle mit der Databricks CLI in der Produktionsumgebung bereit.

Nach Abschluss der Zelle:

- Prüfen Sie manuell, ob der Job erfolgreich erstellt wurde. Der Name des Produktions-Jobs lautet **lab09_dab_** (im Modus `production` ohne Präfix `[dev …]`).
- Prüfen Sie die **Job parameters** und bestätigen Sie:
 - `catalog_name` verweist auf Ihren Katalog `labuser_UNIQUE_ID_3_prod`
 - `display_target` ist `prod`

**HINWEIS:** Das Deployment dauert etwa eine Minute.

**TIPP:** Dokumentation zu den CLI-Befehlen `databricks bundle`:
[AWS](https://docs.databricks.com/aws/en/dev-tools/cli/bundle-commands) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/cli/bundle-commands) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/cli/bundle-commands)

**HINWEIS:** In einer echten Produktion führen Sie den Job typischerweise mit einem Service Principal aus. Siehe die Dokumentation **Set a bundle run identity**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/run-as) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/run-as) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/run-as). In diesem Lab führen wir den Produktions-Job als Benutzer aus.

```python
# <FILL-IN>
```

#### Checkpoint – Prod-Deployment
![Dev](https://files.training.databricks.com/binder/prod_main/automated-deployment-with-declarative-automation-bundles-en_us-2.4.0/images/20260828T161456Z/Automated Deployment with Declarative Automation Bundles/Includes/images/multiple-env-lab/prod-deployment.png)

##### LÖSUNG

<details>
 <summary>FÜR DEN LÖSUNGSCODE AUFKLAPPEN</summary>

```
<!-------------------ADD SOLUTION CODE BELOW------------------->
databricks bundle deploy -t prod
<!-------------------END SOLUTION CODE------------------->
```

</details>

## M. Aufgabe 9 – Den `prod`-Job ausführen

Führen Sie den bereitgestellten Job gegen das Ziel `prod` aus.

**HINWEIS:** Dies dauert 1–2 Minuten.

```python
# <FILL-IN>
```

##### LÖSUNG

<details>
 <summary>FÜR DEN LÖSUNGSCODE AUFKLAPPEN</summary>

```
<!-------------------ADD SOLUTION CODE BELOW------------------->
databricks bundle run -t prod lab09_dab
<!-------------------END SOLUTION CODE------------------->
```

</details>

## N. Aufgabe 10 – Die `prod`-Tabellen überprüfen

Führen Sie nach Abschluss des Jobs die folgenden Zellen aus, um Folgendes zu bestätigen:

- Die Tabellen **nyctaxi_bronze** und **nyctaxi_silver** existieren beide in Ihrem Katalog **labuser_UNIQUE_ID_3_prod**.
- Die Tabelle **nyctaxi_bronze** enthält **21.932 Zeilen**.

```python
spark.sql(f'SHOW TABLES IN {catalog_prod}.default').display()
```

```python
check_nyctaxi_bronze_table(user_catalog = catalog_prod, total_count=21932)
```

## O. Weiterführende Informationen

Dies war ein einfaches Beispiel für das Deployment eines DAB in mehreren Umgebungen. Wenn Sie weitermachen, lohnt es sich, zwei Bereiche zu erkunden:

- **Weitere Möglichkeiten, den Wert einer Variablen zu setzen.** 
 - In diesem Lab haben Sie Werte in **databricks.yml** gesetzt. 
 - Sie können Werte auch über die Databricks CLI, Umgebungsvariablen oder ein `.databrickscfg`-Profil übergeben. 
 - Dokumentation **Set a variable's value**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/variables#set-a-variables-value) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/variables#set-a-variables-value) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/variables#set-a-variables-value)

- **Cluster-Einstellungen pro Umgebung überschreiben.** 
 - Ein gängiges Produktionsmuster ist es, in Dev kleine Cluster und in Prod größere Cluster oder Serverless zu verwenden. 
 - Dokumentation **Override cluster settings in bundles**:
[AWS](https://docs.databricks.com/aws/en/dev-tools/bundles/cluster-override) |
[Azure](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/bundles/cluster-override) |
[GCP](https://docs.databricks.com/gcp/en/dev-tools/bundles/cluster-override)

## Fazit

Gute Arbeit. In diesem Lab haben Sie ein Bundle für eine einzelne Umgebung so erweitert, dass derselbe Job in zwei Umgebungen bereitgestellt wird, ohne die Job-Definition zu duplizieren:

1. Den Job nach **./resources/lab09_nyc.job.yml** verschoben und über das Mapping `include` eingebunden.
2. Die Bundle-Variable `user_name` gesetzt, damit die Katalogvariablen pro Ziel korrekt aufgelöst werden.
3. Unter den Zielen `dev` und `prod` jeweils eine Überschreibung des Job-Parameters `catalog_name` hinzugefügt.
4. Das Bundle mit `databricks bundle validate`, `databricks bundle deploy -t <target>` und `databricks bundle run -t <target> lab09_dab` gegen beide Ziele validiert, bereitgestellt und ausgeführt.
5. Überprüft, dass die Tabelle **nyctaxi_bronze** in jeder Umgebung die erwartete Zeilenanzahl hat (100 in Dev, 21.932 in Prod).

© 2026 Databricks, Inc. Alle Rechte vorbehalten. Apache, Apache Spark, Spark, das Spark-Logo, Apache Iceberg, Iceberg und das Apache-Iceberg-Logo sind Marken der [Apache Software Foundation](https://www.apache.org/).

[Datenschutzrichtlinie](https://databricks.com/privacy-policy) | [Nutzungsbedingungen](https://databricks.com/terms-of-use) | [Support](https://help.databricks.com/)
