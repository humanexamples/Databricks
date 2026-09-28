# Umgebungsvariablen für Serverless Jobs (Beta)

Muss von einem Workspace-Admin über die Previews-Seite aktiviert werden.

## Funktionsweise

Umgebungsvariablen-Einträge werden auf **Job-Ebene** mit eindeutigen Schlüsseln definiert, die Inline-Variablen enthalten. Jeder Task wählt genau einen Eintrag über `environment_variables_key` aus. Einträge werden **nie kombiniert**, und ein Eintrag kann nicht von einem anderen erben.

## Voraussetzungen

- Workspace-Admin muss das Feature über die Previews-Seite aktivieren.
- Tasks müssen auf Serverless Environment Version 5 oder höher laufen.

## Einschränkung

UDFs können nicht auf Umgebungsvariablen zugreifen, da sie in der Spark-Ausführungslogik laufen statt im Task-Prozess.

## Konfigurationsgrenzen

| Konfiguration | Grenzwert |
|---|---|
| Umgebungsvariablen-Einträge pro Job | 10 |
| Länge des Eintragsschlüssels | 1–100 Zeichen, Muster `^[\w\-_]+$` |
| Inline-Variablen pro Eintrag | 100 |
| Länge des Inline-Variablennamens | 1–256 Zeichen, Muster `^[A-Za-z_][A-Za-z0-9_]*$` |
| Länge des Inline-Variablenwerts | 512 Zeichen |

## Konfiguration über die API

Über `POST /api/2.2/jobs/create` lässt sich das Feld `environment_variables` setzen, um Einträge für Notebook- und JAR-Tasks zu definieren.

## Variablen im Code lesen

- **Python:** `os.environ["VARIABLE_NAME"]`
- **Scala:** `sys.env("VARIABLE_NAME")`

## Quelle

- https://docs.databricks.com/aws/en/jobs/environment-variables
