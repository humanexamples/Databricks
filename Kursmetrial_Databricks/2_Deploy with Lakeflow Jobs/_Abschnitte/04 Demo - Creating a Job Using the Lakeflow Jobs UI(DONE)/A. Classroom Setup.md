## A. Classroom-Setup

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren. Dabei werden außerdem mithilfe der `USE`-Anweisungen Ihr Standardkatalog auf **dbacademy** und das Schema auf Ihren unten angezeigten spezifischen Schemanamen gesetzt.

```
USE CATALOG dbacademy;
USE SCHEMA dbacademy.<your unique schema name>;
```

**HINWEIS:** Das Objekt `DA` wird nur in Databricks-Academy-Kursen verwendet und ist außerhalb dieser Kurse nicht verfügbar. Es referenziert dynamisch die Informationen, die zum Ausführen des Kurses benötigt werden.

**HINWEIS:** Wenn Sie **Serverless**-Compute verwenden möchten, stellen Sie sicher, dass Sie die **neueste Version (Version > 1)** nutzen. Andernfalls funktioniert das Setup nicht korrekt.

- [Select an environment version](https://docs.databricks.com/aws/en/compute/serverless/dependencies#-select-an-environment-version). 

```text
%run ./Includes/Classroom-Setup-04
```
