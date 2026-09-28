# Lakehouse Replay

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/lakehouse-replay>
> **Public Preview**

Lakehouse Replay verbessert die Qualität der Databricks Runtime, indem es automatisch **read-only-Workloads** gegen kommende Runtime-Versionen testet, bevor diese in Produktion gehen.

## Was es ist

> *"automatically replays a small subset of read-only workloads from your workspace against upcoming runtime versions"*

Automatisierte Regressionserkennung zur Verbesserung der Runtime-Stabilität. Fokus auf Serverless-Compute-Umgebungen; die erkannten Regressionen kommen **allen** Databricks-Runtime-Releases zugute (Classic und Serverless).

## Funktionsweise (Shadow Execution, 4 Stufen)

1. Produktions-Workloads laufen normal in der eigenen Umgebung
2. Eine kleine Stichprobe **sicherer, read-only** Workloads wird automatisch ausgewählt
3. Spark-Pläne der ausgewählten Workloads laufen auf von Databricks verwaltetem **Shadow Compute** mit Kandidaten-Runtime-Versionen erneut
4. Diskrepanzen lösen eine Untersuchung vor dem Release aus

Shadow Compute arbeitet unabhängig — *"no impact on your production workloads or jobs."*

## Unterstützte Workload-Typen

- Read-only-SQL- und DataFrame-Workloads auf Serverless Compute
- Serverless SQL Warehouses und Notebooks
- Serverless Jobs
- Unity-Catalog-Delta-Table-Reads

> Für DataFrame-Workloads: *"Lakehouse Replay replays only the Spark plan submitted to the production cluster. Preceding Python cells are not executed."*

## Datensicherheit und Datenschutz

- **Keine Datenextraktion:** *"Lakehouse Replay compares only execution status and runtime metrics to detect discrepancies."*
- **Berechtigungserhalt:** replayte Workloads laufen unter der ursprünglichen Nutzeridentität mit Unity-Catalog-Berechtigungen.
- **Isolierte Ausführung:** Shadow Compute kann nicht auf externe APIs, Datenbanken oder andere Workspaces zugreifen.

## Abrechnung

Compute-Kosten für die Replay-Ausführung trägt Databricks. Minimale Object-Storage-API-Gebühren können anfallen (replayte Workloads lesen Daten über dieselben Storage-Pfade).

## Audit-Logging

Lakehouse-Replay-Aktivität erscheint in der Audit-Log-Systemtabelle unter dem Service-Identifier `lakehouseReplay`.

## Erste Schritte

**Keine Konfiguration erforderlich.** Workspace-Admins aktivieren das Feature über die **Previews**-Seite des Workspace. Sampling erfolgt automatisch und probabilistisch — *"Most workloads are replayed within one hour of the original execution."*

## FAQ

- **Muss ich etwas tun?** Nein — kein Setup, keine Konfiguration, keine Wartung.
- **Beeinflusst es Produktions-Workloads?** Nein — Shadow Compute arbeitet getrennt.
- **Woran erkenne ich, ob meine Workloads replayt werden?** Replayte Workloads erscheinen **nicht** in der Job- oder Query-History; nur in den Audit-Logs.
- **Was passiert bei einem fehlgeschlagenen Replay?** Wenn Produktion erfolgreich ist, Shadow-Ausführung aber fehlschlägt, untersucht Databricks und behebt bestätigte Regressionen vor dem Release.
- **Welche Regressionen werden erkannt?** Ausführungsfehler — Workloads, die in Produktion erfolgreich sind, aber auf kommenden Runtime-Versionen fehlschlagen.
- **Wie häufig wird replayt?** Probabilistisch, abhängig von Workspace-Traffic und Workload-Typ.
