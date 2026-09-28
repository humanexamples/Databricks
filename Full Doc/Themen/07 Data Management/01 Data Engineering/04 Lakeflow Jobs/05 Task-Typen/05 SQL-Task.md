# SQL-Task

Konfiguriert eine SQL-Query, einen SQL-Alert oder eine SQL-Datei als Task. Benötigt Databricks SQL und ein Serverless- oder Pro-SQL-Warehouse. Das SQL-Asset muss an einem für den konfigurierenden Nutzer zugänglichen Ort liegen.

## Konfiguration

1. Tab **Tasks** → Typ **SQL** wählen.
2. Im SQL-Task-Dropdown den Typ wählen:

| Typ | Beschreibung |
|---|---|
| **Query** | eine SQL-Query gegen das angegebene Warehouse ausführen |
| **Alert** | einen SQL-Alert über das angegebene Warehouse auswerten; optional Subscriber für Benachrichtigungen |
| **File** | eine `.sql`-Datei ausführen (mehrere per `;` getrennte Statements möglich) — Quelle **Workspace** oder **Git provider** (relativer Pfad ohne führendes `/` oder `./`, z. B. `etl/bronze/ingest.sql`) |

3. Optional Parameter als Key-Value-Paare.
4. Optional Retries, Laufdauer oder Benachrichtigungen.
5. **Save task**.

## Quelle

- https://docs.databricks.com/aws/en/jobs/tasks/sql
