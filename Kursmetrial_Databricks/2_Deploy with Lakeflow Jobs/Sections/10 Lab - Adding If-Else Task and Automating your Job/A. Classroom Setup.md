## A. Classroom-Setup

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren. Dabei werden außerdem mithilfe der `USE`-Anweisungen Ihr Standardkatalog auf **dbacademy** und das Schema auf Ihren unten angezeigten spezifischen Schemanamen gesetzt.

```
USE CATALOG dbacademy;
USE SCHEMA dbacademy.<your unique schema name>;
```

**HINWEIS:** Das Objekt `DA` wird nur in Databricks-Academy-Kursen verwendet und ist außerhalb dieser Kurse nicht verfügbar. Es referenziert dynamisch die Informationen, die zum Ausführen des Kurses benötigt werden.

**HINWEIS:** Wenn Sie Serverless V1 verwenden, wird eine Warnung ausgegeben. Sie können die Warnung ignorieren.

```text
%run ./Includes/Classroom-Setup-10L
```
