# Jobs mit vielen Tasks

Databricks erlaubt Jobs mit bis zu **1.000 Tasks**. Ab mehr als 100 Tasks können folgende Probleme auftreten:

## Fehler: „Only 100 tasks allowed"

Ressourcen mit mehr als 100 Tasks benötigen API 2.2 oder höher — SDK/CLI aktualisieren:

| SDK/Sprache | Mindestversion |
|---|---|
| Go | 0.60.0 |
| Python | 0.45.0 |
| Java | 0.42.0 |
| Databricks CLI | 0.244.0 |

## Fehler: „Only 150 execution contexts allowed"

Bei diesem Fehler müssen Tasks auf mehrere Cluster verteilt werden.

## Performance der Matrix-Ansicht

Bei großen Task-Mengen (z. B. 500 Tasks über 100 Job-Läufe) kann die UI langsamer werden oder nur noch Zusammenfassungen statt Einzeldetails zeigen. Filtern auf kürzere Zeiträume verbessert die Performance.

## Quelle

- https://docs.databricks.com/aws/en/jobs/large-jobs
