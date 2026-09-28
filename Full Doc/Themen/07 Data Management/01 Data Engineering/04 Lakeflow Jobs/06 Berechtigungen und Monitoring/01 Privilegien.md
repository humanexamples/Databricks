# Identitäten, Berechtigungen und Privilegien für Jobs

Lakeflow Jobs nutzt zwei Berechtigungssysteme: **Job-Privilegien** (wer Jobs sehen, ausführen, verwalten darf) und **Run-as-Privilegien** (welche Identität auf Daten und Ressourcen zugreift).

## Secrets in Logs

Secrets bleiben standardmäßig in Spark-Driver-Logs von Classic Compute sichtbar. Nur Nutzer mit `CAN MANAGE` können die Logs einsehen, sofern nicht `spark.databricks.acl.needAdminPermissionToViewLogs` auf `false` gesetzt ist. Für Legacy „No Isolation Shared" Access Mode gelten abweichende Regeln.

## Job-Privilegien vs. Run-as-Nutzer

Job-Privilegien steuern den Zugriff auf den Job selbst. Getrennt davon führt der Job Tasks mit den Rechten eines festgelegten **Run-as**-Nutzers aus — der Ersteller kann Run-as auf einen anderen Nutzer setzen, sodass der Job auf Ressourcen zugreifen kann, die der Ersteller selbst nicht hat.

## Standard-Privilegien

- Job-Ersteller erhalten `IS OWNER`.
- Workspace-Admins erhalten `CAN MANAGE`.
- Der Job-Ersteller ist standardmäßig der Run-as-Nutzer.

Workspace-Admins können Eigentümerschaft und Run-as-Konfiguration standardmäßig ändern; die Einstellung `RestrictWorkspaceAdmins` erlaubt Account-Admins, das einzuschränken.

## Unity-Catalog-Interaktion

Jobs laufen als Run-as-Identität und werden gegen folgende Berechtigungen ausgewertet: Unity-Catalog-verwaltete Assets (Tabellen, Volumes, Modelle, Views), Legacy-Hive-Metastore-ACLs, Workspace-Asset-ACLs (Compute, Notebooks, Queries), Databricks Secrets.

**Zeitpunkt der Prüfung:** Job-Privilegien werden bei Aktionen am Job geprüft; Run-as-Privilegien während der Ausführung — teils erst bei Task-Start, teils fortlaufend. **Wichtig:** Nicht alle Run-as-Privilegien werden zu Laufbeginn geprüft — werden Run-as-Rechte während eines laufenden Jobs entzogen, kann der Job vor Abschluss fehlschlagen.

## SQL-Tasks und Berechtigungen

Nur File-Tasks respektieren den Run-as-Nutzer vollständig. SQL-Queries folgen den Sharing-Einstellungen der Query:

- **Run as owner:** läuft mit der Identität des Query-Eigentümers.
- **Run as viewer:** läuft mit der Run-as-Identität des Jobs.

**Beispiel:** Nutzer A besitzt Query `my_query` mit „Run as owner". Nutzer B plant sie in Job `my_job` mit Service Principal `prod_sp` als Run-as. Der Job läuft als Nutzer A. Ändert A das Sharing auf „Run as viewer", läuft der Job als `prod_sp`.

## Run-as-Nutzer konfigurieren

Nutzer mit `CAN MANAGE` oder `IS OWNER` können Run-as ändern — auf sich selbst oder einen Service Principal mit „Service Principal User"-Entitlement.

1. **Jobs & Pipelines** → Job öffnen.
2. Stift-Icon neben **Run as** im Job-Details-Panel.
3. Nutzer/Service Principal suchen und wählen.
4. **Save**.

## Run-as auf eine Gruppe setzen (Public Preview)

Alle Tasks laufen dann mit den Rechten der Gruppe; Workspace-Assets gehören der Gruppe. Audit-Logs zeigen `identity_metadata.run_as` als Gruppe und `identity_metadata.run_by` als Jobs-Service-Application-Service-Principal.

**Voraussetzung:** Gruppenmitgliedschaft oder `Assume`-Privileg auf der Gruppe.

## Best Practices für Produktions-Jobs

1. **Service Principals als Run-as verwenden** — verhindert Fehlschläge, wenn Ersteller den Workspace verlassen oder Rechte verlieren.
2. **Unity-Catalog-kompatibles Compute nutzen** — Serverless und SQL-Warehouses nutzen immer Unity Catalog; Classic Compute nach Möglichkeit im Standard Access Mode.
3. **Job-Privilegien einschränken:** `CAN VIEW` für Beobachter, `CAN MANAGE RUN` für Nutzer, die Läufe auslösen, `CAN MANAGE`/`IS OWNER` nur für vertrauenswürdige Nutzer, die Produktionscode ändern.

## Job-Berechtigungen

| Berechtigung | Umfang |
|---|---|
| `IS OWNER` | standardmäßige Run-as-Identität; überschreibbar |
| `CAN MANAGE` | Job-Definition, Konfiguration, Tasks, Berechtigungen bearbeiten; Zeitplan pausieren/fortsetzen |
| `CAN MANAGE RUN` | Läufe auslösen und abbrechen |
| `CAN VIEW` | Lauf-Ergebnisse, Details, Historie, Status einsehen |

Jede Berechtigung schließt die darunterliegenden ein. Nur ein Job-Eigentümer möglich; Gruppen können nicht `IS OWNER` erhalten. Über „Run Now" ausgelöste Läufe übernehmen die Rechte des Run-as-Nutzers, nicht des auslösenden Nutzers. Job-Zugriffskontrolle gilt für die Jobs-&-Pipelines-UI, nicht für Notebook-Workflows oder API-eingereichte Jobs (außer `access_control_list` ist explizit gesetzt).

## Berechtigungen konfigurieren

1. **Jobs & Pipelines** → Job öffnen.
2. **Edit permissions** im Job-Details-Panel.
3. Nutzer/Gruppen/Service Principals suchen → **Add** → **Save**.

## Job-Eigentümer verwalten

Nur Workspace-Admins können den Eigentümer ändern; genau ein Eigentümer ist Pflicht (Nutzer oder Service Principal).

## Notebook-Tasks und API-Zugriff

Notebook-Task-Ausgabe über die UI erfordert Notebook-Zugriff. Derselbe Lauf über die API zeigt die Ausgabe dem API-Aufrufer auch mit nur Job-Level-Zugriff.

## Quelle

- https://docs.databricks.com/aws/en/jobs/privileges
