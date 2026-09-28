# Jobs bei Tabellen-Updates auslösen

Table-Update-Trigger lösen einen Job-Lauf automatisch aus, wenn sich Quelltabellen ändern — ohne dauerhaft laufende Cluster oder manuelles Monitoring.

## Funktionsweise

Überwacht werden können eine oder mehrere Tabellen, wahlweise mit Auslösung bei **jedem** Update oder erst, wenn **alle** überwachten Tabellen aktualisiert wurden. Unterstützte Typen: Unity-Catalog-Delta- und Iceberg-Managed-Tables, External Tables auf Delta-Basis, Materialized Views, Streaming Tables sowie Unity-Catalog-Views/Metric-Views, die von unterstützten Tabellen abhängen. Keine Zusatzkosten über die üblichen Cloud-Gebühren für Tabellenauflistung und Speicherzugriff hinaus.

## Trigger hinzufügen

1. **Jobs & Pipelines** → Ziel-Job auswählen.
2. Rechtes Panel **Schedules & Triggers** → **Add trigger**.
3. Trigger-Typ **Table update**.
4. Zu überwachende Tabellen angeben.
5. Bei mehreren Tabellen: Auslösung bei jedem Update oder erst bei allen konfigurieren.
6. Optional erweiterte Einstellungen:
   - **Minimum time between triggers (seconds):** Mindestwartezeit nach Abschluss des vorherigen Laufs.
   - **Wait after last change (seconds):** verzögert die Ausführung nach Tabellen-Updates; weitere Änderungen setzen den Timer zurück.
7. **Test trigger** zur Prüfung.
8. Speichern.

Sind beide erweiterten Optionen gesetzt, wartet der Trigger zuerst das Mindestintervall ab, danach die angegebene Zeit nach der letzten Änderung. Beispiel: 120 Sekunden Minimum + 60 Sekunden Wait-after-Change → Ausführung frühestens nach 120 Sekunden, selbst wenn Updates bereits innerhalb der ersten 60 Sekunden eintreffen.

## OpenSharing und System-Tabellen (Beta)

Table-Update-Trigger können auch über OpenSharing geteilte Daten und System-Tabellen überwachen (Tabellen, Views, Metric Views, Materialized Views, Streaming Tables, System-Tabellen). Nur Databricks-zu-Databricks-Sharing wird unterstützt (nicht Databricks-zu-Open); Betas müssen auf Recipient- und Provider-Seite aktiviert sein (bei System-Tabellen nur Recipient-seitig); der Trigger-Ersteller benötigt `SELECT` auf die geteilten Objekte/System-Tabellen.

## File-Events-Optimierung

Aktivierte File Events auf externen Speicherorten verbessern Performance und Skalierbarkeit deutlich — einmalige Konfiguration, nutzt Cloud-Provider-Änderungsbenachrichtigungen. Tabellen im Metastore-Root-Speicher müssen zuvor in External Locations konvertiert werden.

## Job-Parameter

| Referenz | Bedeutung |
|---|---|
| `{{job.trigger.table_update.updated_tables}}` | JSON-Liste geänderter Tabellen seit dem letzten Lauf |
| `{{job.trigger.table_update.<catalog.schema.table>.commit_timestamp.iso_datetime}}` | jüngster Commit-Zeitstempel, der den Job ausgelöst hat |
| `{{job.trigger.table_update.<catalog.schema.table>.version}}` | jüngste Commit-Version, die den Job ausgelöst hat |

## Benachrichtigungen

E-Mail- oder System-Ziel-Benachrichtigungen lassen sich konfigurieren, wenn die Trigger-Auswertung fehlschlägt.

## Einschränkungen

- Maximal 10 Managed-/Delta-Tabellen pro Trigger.
- Ohne File Events: maximal 1.000 Jobs mit Table-Update-Triggern pro Workspace.
- Maximal 1.000 OpenSharing-/System-Tabellen-Trigger pro Workspace.
- Unity-Catalog-View-Trigger: Views mit `read_files`, Abhängigkeit von Nicht-UC-Tabellen oder Federated Tables werden nicht unterstützt; abhängige Tabellen zählen zum 10-Tabellen-Limit; maximal 10 abhängige Views pro überwachter View.

## Quelle

- https://docs.databricks.com/aws/en/jobs/trigger-table-update
