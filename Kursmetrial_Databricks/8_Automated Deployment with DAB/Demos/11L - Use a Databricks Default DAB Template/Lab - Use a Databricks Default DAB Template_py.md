Bisher haben Sie Bundles von Hand erstellt. In diesem Lab verwenden Sie die eingebauten **Bundle-Templates** der Databricks CLI, um ein neues Projekt von Grund auf anzulegen. Templates liefern Ihnen ein funktionsfähiges Bundle mit sinnvollen Standardwerten (Job, Pipeline, Tests, README), das Sie anpassen können, anstatt mit einer leeren **databricks.yml** zu beginnen.

Sie sehen sich die verfügbaren Templates an, erzeugen mit `databricks bundle init` ein `default-python`-Projekt, erkunden die generierte Struktur und validieren sie.

## Lab-Szenario

Sie beginnen ein brandneues Projekt und möchten sich den Boilerplate-Code sparen. Anstatt **databricks.yml** von Hand zu schreiben, verwenden Sie den Befehl `bundle init` der Databricks CLI mit dem Template `default-python`, um ein funktionsfähiges Bundle anzulegen, und validieren es anschließend.

```bash
%sh
# Bevor Sie mit den Lab-Aufgaben beginnen, führen Sie einige kurze Prüfungen durch, um zu bestätigen, dass die 
# Databricks CLI installiert und gegenüber Ihrem Workspace authentifiziert ist.
databricks -v

# Führen Sie die folgende Zelle aus, um zu bestätigen, dass die Databricks CLI gegenüber Ihrem Workspace authentifiziert ist. 
# Ist die Authentifizierung fehlerhaft, gibt die Zelle einen Fehler statt einer Liste von Katalogen zurück.
databricks catalogs list

databricks bundle init --help
```

Verwenden Sie `databricks bundle init <template-name>`, um ein neues Projekt anzulegen. Die folgende Zelle verwendet das Template `default-python`.

**HINWEIS:** Wenn Sie keinen Template-Namen angeben, wechselt `bundle init` in den **interaktiven** Modus und fordert Sie zur Auswahl auf. Der interaktive Modus ist beim Ausführen von `%sh`-Zellen in einem Notebook nicht verfügbar, daher geben wir in diesem Lab immer den Template-Namen an.

```bash
%sh
databricks bundle init default-python

```

Navigieren Sie im Datei-Browser des Workspace zum generierten Ordner **my_project** und sehen Sie sich an, was `bundle init` erzeugt hat:

- **resources/** enthält zusätzliche YAML-Dateien, die vom Bundle eingebunden werden:
 - **my_project.job.yml**
 - **my_project.pipeline.yml**
- **scratch/** enthält ein Explorations-Notebook für Ad-hoc-Analysen.
- **src/** enthält den Produktionscode (ein Python-Notebook und ein Notebook für eine Spark Declarative Pipeline).
- **tests/** enthält Unit- und Integrationstests für das Projekt.
- Das Projekt-Root enthält außerdem eine **pytest.ini**, eine **README.md** und einige Konfigurationsdateien.

```python
# Führen Sie die folgende Zelle aus, um zu bestätigen, dass Sie sich noch nicht in my_project/ befinden
pwd
ls

# Das Projekt bündeln
cd 'my_project'
databricks bundle validate
```

**Warum wir in diesem Lab beim Validieren aufhören:** Die Lab-Umgebung der Databricks Academy schränkt Ihre Möglichkeit ein, Cluster zu erstellen, daher können Job und Pipeline des generierten Bundles hier nicht tatsächlich bereitgestellt und ausgeführt werden. Der vollständige Deployment-Ablauf wurde in früheren Modulen behandelt.

**Möchten Sie Templates lokal verwenden?** Dieses Lab stellt außerdem eine funktionierende VS-Code-Umgebung bereit. Wie Sie ein Template mit VS Code bereitstellen, erfahren Sie unter **08 - Using VS Code with Databricks**.

## Fazit

In diesem Lab haben Sie ein Databricks-Standard-Bundle-Template verwendet, um ein neues Projekt vollständig anzulegen, ohne **databricks.yml** von Hand zu schreiben:

1. Die vier Standard-Templates (`default-python`, `default-sql`, `dbt-sql`, `mlops-stacks`) angesehen.
2. Die Ausgabe von `databricks bundle init --help` gelesen, um die verfügbaren Flags zu verstehen.
3. Mit `databricks bundle init default-python` ein funktionsfähiges Bundle erzeugt.
4. Die resultierende Projektstruktur (`resources/`, `src/`, `scratch/`, `tests/`, **databricks.yml**) erkundet.
5. Das generierte Bundle mit `cd my_project && databricks bundle validate` validiert.

In der Praxis beginnen Sie ein neues Projekt meist mit Templates. Ab hier gilt derselbe Workflow `validate` / `deploy` / `run` / `destroy`, den Sie bereits geübt haben.
