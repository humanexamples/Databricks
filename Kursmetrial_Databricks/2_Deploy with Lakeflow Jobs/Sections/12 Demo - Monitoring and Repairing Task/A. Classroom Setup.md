## A. Classroom-Setup

Führen Sie die folgende Zelle aus, um Ihre Arbeitsumgebung für diesen Kurs zu konfigurieren. Dabei werden außerdem mithilfe der `USE`-Anweisungen Ihr Standardkatalog auf **dbacademy** und das Schema auf Ihren unten angezeigten spezifischen Schemanamen gesetzt.

```
USE CATALOG dbacademy;
USE SCHEMA dbacademy.<your unique schema name>;
```

**HINWEIS:** Das Objekt **DA** wird nur in Databricks-Academy-Kursen verwendet und ist außerhalb dieser Kurse nicht verfügbar. 

```text
%run ./Includes/Classroom-Setup-12
```
