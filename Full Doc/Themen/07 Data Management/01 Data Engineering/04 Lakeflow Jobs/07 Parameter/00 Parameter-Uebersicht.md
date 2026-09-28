# Jobs parametrisieren — Überblick

Parameter erlauben es, Werte an einen Job und seine Tasks zu übergeben und Werte zwischen Tasks zu referenzieren. Quellcode-Assets, die als Tasks konfiguriert sind, müssen entsprechend angepasst werden, um Parameter zu referenzieren — die Referenzierung unterscheidet sich je Sprache und Task-Typ.

## Grundbegriffe

| Begriff | Bedeutung |
|---|---|
| **Job-Parameter** | Key-Value-Paar auf Job-Ebene, an Tasks weitergereicht (siehe `Job-Parameter.md`) |
| **Task-Parameter** | Key-Value-Paar oder JSON-Array auf Task-Ebene (siehe `Task-Parameter.md`) |
| **Dynamische Wertreferenzen** | Syntax zur Referenzierung von Job-Zuständen, Metadaten und Parametern bei der Task-Konfiguration (siehe `Dynamische Wertreferenzen.md`) |
| **Task Values** | Syntax zum Erfassen und Referenzieren von während des Task-Laufs erzeugten Werten (siehe `Task-Values.md`) |
| **Parameterwerte im Code lesen** | wie Parameterwerte im Task-Code gelesen werden, je Task-Typ (siehe `Parameter-Nutzung.md`) |

**Hinweis:** Für deployment-spezifische Konfiguration eignen sich statt Parametern auch Umgebungsvariablen für Serverless Jobs (siehe `02 Job erstellen und konfigurieren/Umgebungsvariablen.md`).

## Anwendungsfälle

- Erweiterbare Logik in Code-Assets einbauen.
- Läufe bedingt gestalten.
- Gemeinsame Parameter über mehrere Tasks referenzieren.
- In einem Task erzeugte Informationen in einem anderen Task nutzen.
- Metadaten und Zustandsinformationen des Job-Laufs referenzieren.

## Job- vs. Task-Parameter

**Job-Parameter** sind Key-Value-Paare auf Job-Ebene, überschreibbar über „Run now with different parameters" oder die REST-API, und werden mit Key-Value-Parametern an Tasks weitergereicht.

**Task-Parameter** sind Key-Value-Paare oder JSON-Arrays auf Task-Ebene. Jeder Task-Typ übergibt Werte unterschiedlich — Notebook-Tasks nutzen `dbutils.widgets`, Python-Skripte erhalten sie als Kommandozeilenargumente.

**Hinweis:** Jeder Nutzer mit `CAN MANAGE RUN` oder höher kann Job-Parameterwerte für manuelle Läufe überschreiben.

## Workflows mit dynamischen Werten bauen

Statische Task-Parameter lassen sich nur durch Ändern der Task-Definition überschreiben. Dynamische Wertreferenzen ermöglichen Muster wie: Job-Parameter über Tasks hinweg nutzen, Notebook-Query-Ausgaben als Listen erfassen, Verzweigungslogik erstellen, oder Parameter aus anderen Tasks referenzieren.

## Quelle

- https://docs.databricks.com/aws/en/jobs/parameters
