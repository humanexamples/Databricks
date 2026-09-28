# Berechtigungen für Lakeflow Declarative Pipelines — Referenz

Dieses Dokument fasst zusammen, wie Databricks den Zugriff auf Lakeflow Declarative Pipelines (LDP) über Identitäten, Berechtigungen (Permissions/ACLs) und Unity-Catalog-Privilegien steuert. Jede faktische Aussage wurde per `WebFetch` gegen die offizielle Databricks-Online-Dokumentation verifiziert; für die Kernaussagen wurde zusätzlich die Azure/Microsoft-Learn-Spiegelseite abgerufen und mit der AWS-Fassung abgeglichen. Die vollständige ACL-Berechtigungstabelle für Pipelines stammt von der separaten Referenzseite "Access control lists", auf die die Berechtigungs-Seite selbst verweist.

## Abschnittsübersicht

1. [Grundlagen: Identitäten, Berechtigungen und Privilegien](#grundlagen)
2. [Welche Identität wird für Pipeline-Updates verwendet? (Run-as-Identität)](#run-as)
3. [Wer kann ein Pipeline-Update ausführen?](#wer-run)
4. [Wer kann eine Pipeline und ihre Ausgabe sehen?](#wer-view)
5. [Pipeline-Berechtigungen konfigurieren](#konfigurieren)
6. [Lakeflow-Pipelines-ACL-Tabelle](#acl-tabelle)
7. [Den Pipeline-Owner ändern](#owner-aendern)
8. [Nicht-Admins Zugriff auf die Treiber-Logs erlauben](#driver-logs)
9. [Credentials aus einem Secret Scope referenzieren](#secrets)
10. [Sensible Daten in der Pipeline-Ausgabe schützen](#pii)
11. [Quellen](#quellen)

---

## <a id="grundlagen">1. Grundlagen: Identitäten, Berechtigungen und Privilegien</a>

Identitäten, Berechtigungen und Privilegien bestimmen, wer Pipelines ausführen, verwalten und abfragen kann sowie wer auf die von ihnen erzeugten Daten zugreifen darf.

Databricks empfiehlt, für alle neuen Pipelines Unity Catalog zu verwenden. Standardmäßig können materialisierte Sichten (Materialized Views) und Streaming Tables, die von mit Unity Catalog konfigurierten Pipelines erstellt werden, nur vom Pipeline-Owner abgefragt werden.

Publizieren die Pipelines Datasets in den Legacy Hive Metastore, gilt ein eigener Dokumentationsabschnitt ("Use Lakeflow pipelines with legacy Hive metastore"). Für allgemeine Best Practices zur Identitätskonfiguration verweist die Doku auf die Seite "Identity best practices".

---

## <a id="run-as">2. Welche Identität wird für Pipeline-Updates verwendet? (Run-as-Identität)</a>

Pipelines verarbeiten Updates unter der Identität des **Run-as-Nutzers** ("run-as user"). Standardmäßig ist der Run-as-Nutzer der Pipeline-Ersteller, er kann aber auf einen anderen Nutzer oder ein Service Principal geändert werden.

Databricks empfiehlt ausdrücklich, den Run-as-Nutzer auf ein Service Principal zu setzen, damit Pipeline-Updates nicht an das Konto einer einzelnen Person gebunden sind.

Diesem Service Principal sollten nur die Unity-Catalog-Privilegien gewährt werden, die die Pipeline tatsächlich benötigt, statt breiter Account-weiter Zugriffsrechte. Beispiel aus der Doku: `USE CATALOG` auf dem Zielkatalog gewähren, `USE SCHEMA` sowie das passende `CREATE`-Privileg (`CREATE MATERIALIZED VIEW` oder `CREATE TABLE`) auf dem Ausgabe-Schema, und `SELECT` auf den Quellen der Pipeline. Für die vollständige Liste der zum Publizieren nach Unity Catalog erforderlichen Privilegien verweist die Doku auf den Abschnitt "Requirements" der Unity-Catalog-Integrationsseite.

---

## <a id="wer-run">3. Wer kann ein Pipeline-Update ausführen?</a>

Pipeline-Updates können von jedem Nutzer oder Service Principal mit den Berechtigungen `CAN RUN`, `CAN MANAGE` oder `IS OWNER` ausgeführt werden.

---

## <a id="wer-view">4. Wer kann eine Pipeline und ihre Ausgabe sehen?</a>

Um eine Pipeline zu öffnen und ihre Details einzusehen, benötigt ein Nutzer mindestens die Berechtigung `CAN VIEW` auf der Pipeline.

Um die Pipeline einzusehen, die eine Streaming Table oder eine materialisierte Sicht erzeugt, benötigt ein Nicht-Admin-Nutzer zusätzlich zu seinen Pipeline-Berechtigungen auch das `REFRESH`-Privileg auf dieser Streaming Table bzw. materialisierten Sicht. Ohne das `REFRESH`-Privileg zeigt die Pipeline-URL **"Pipeline not available"** an.

---

## <a id="konfigurieren">5. Pipeline-Berechtigungen konfigurieren</a>

Um Berechtigungen zu verwalten, ist die Berechtigung `CAN MANAGE` oder `IS OWNER` auf der Pipeline erforderlich. Pipelines nutzen Access Control Lists (ACLs), um Berechtigungen zu steuern.

Vorgehen laut Doku:

1. In der Seitenleiste auf **Jobs & Pipelines** klicken.
2. Den **Namen** einer Pipeline auswählen.
3. Auf **Share** klicken. Der Dialog **Permissions Settings** öffnet sich.
4. Auf **Select User, Group or Service Principal…** klicken und einen Nutzer, eine Gruppe oder ein Service Principal auswählen.
5. Eine Berechtigung aus dem Berechtigungs-Dropdown-Menü auswählen.
6. Auf **Add** klicken.
7. Auf **Save** klicken.

---

## <a id="acl-tabelle">6. Lakeflow-Pipelines-ACL-Tabelle</a>

Für die vollständige Liste der Pipeline-Berechtigungsstufen und der damit jeweils verbundenen Fähigkeiten verweist die Berechtigungs-Seite auf die allgemeine Referenzseite "Access control lists" (Abschnitt "Lakeflow pipelines ACLs"). Diese Tabelle wurde dort separat abgerufen und zweifach (AWS- sowie Azure-Spiegelseite, inhaltlich identisch) gegengeprüft:

| Fähigkeit | NO PERMISSIONS | CAN VIEW | CAN RUN | CAN MANAGE | IS OWNER |
|---|---|---|---|---|---|
| Pipeline-Details ansehen und Pipeline auflisten | | ✓ | ✓ | ✓ | ✓ |
| Spark-UI und Treiber-Logs einsehen | | ✓ | ✓ | ✓ | ✓ |
| Ein Pipeline-Update starten und stoppen | | | ✓ | ✓ | ✓ |
| Pipeline-Cluster direkt stoppen | | | ✓ | ✓ | ✓ |
| Pipeline-Einstellungen bearbeiten | | | | ✓ | ✓ |
| Die Pipeline löschen | | | | ✓ | ✓ |
| Runs und Experiments bereinigen (purge) | | | | ✓ | ✓ |
| Berechtigungen ändern | | | | ✓ | ✓ |

**Hinweis zur Herkunft dieser Tabelle:** Sie steht nicht auf der Berechtigungs-Seite selbst, sondern auf der separaten, produktübergreifenden ACL-Referenzseite ("Access control lists"), die für jeden Objekttyp im Workspace (Alerts, Compute, Dashboards, Jobs, Notebooks, Pipelines usw.) eine eigene Tabelle führt.

---

## <a id="owner-aendern">7. Den Pipeline-Owner ändern</a>

Standardmäßig ist der Pipeline-Owner zugleich der Run-as-Nutzer, unter dem Pipeline-Updates laufen. Eine Änderung des Owners ändert auch die Identität, unter der künftige Updates ausgeführt werden.

Soll nur die Ausführungsidentität geändert werden, ohne den Owner zu ändern, ist stattdessen der Run-as-Nutzer zu setzen (siehe Abschnitt 2).

**Um den Owner einer Pipeline zu ändern, muss man sowohl Metastore-Admin als auch Workspace-Admin sein.** Die Änderung erfolgt über die UI oder die REST API.

### Über die UI

1. In der Seitenleiste auf **Jobs & Pipelines** klicken.
2. Den **Namen** der Pipeline auswählen.
3. Auf **Share** klicken. Der Dialog **Permissions Settings** öffnet sich.
4. Den aktuellen Owner entfernen, dann den neuen Owner auswählen. Der Owner kann ein Nutzer oder ein Service Principal sein — Databricks empfiehlt ein Service Principal.
5. Auf **Save** klicken.

### Über die REST API

Ist die Owner-Steuerung in der UI nicht verfügbar (etwa bei manchen intern verwalteten Pipelines), erfolgt die Änderung über die REST-API-Operation **Set pipeline permissions**. Dabei wird der `user_name` (bzw. `service_principal_name` für ein Service Principal) des neuen Owners mit der Berechtigungsstufe `IS_OWNER` angegeben:

```json
{
  "access_control_list": [
    {
      "user_name": "new.owner@example.com",
      "permission_level": "IS_OWNER"
    }
  ]
}
```

### Wenn niemand sowohl Metastore- als auch Workspace-Admin ist

Ist in der Organisation niemand gleichzeitig Metastore-Admin und Workspace-Admin, muss der Databricks-Ansprechpartner kontaktiert werden, um den Pipeline-Owner zu ändern.

---

## <a id="driver-logs">8. Nicht-Admins Zugriff auf die Treiber-Logs erlauben</a>

Standardmäßig können nur der Pipeline-Owner und Workspace-Admins die Treiber-Logs des Clusters einsehen, der eine Unity-Catalog-aktivierte Pipeline ausführt. Der Zugriff auf die Treiber-Logs lässt sich für jeden Nutzer mit `CAN MANAGE`-, `CAN VIEW`- oder `CAN RUN`-Berechtigung freigeben, indem folgender Spark-Konfigurationsparameter dem `configuration`-Objekt in den Pipeline-Einstellungen hinzugefügt wird:

```json
{
  "configuration": {
    "spark.databricks.acl.needAdminPermissionToViewLogs": "false"
  }
}
```

---

## <a id="secrets">9. Credentials aus einem Secret Scope referenzieren</a>

API-Schlüssel, Datenbank-Passwörter oder Tokens sollten niemals im Pipeline-Quellcode hartkodiert werden. Stattdessen sollten sie in einem Secret Scope gespeichert und zur Laufzeit referenziert werden:

```python
api_token = dbutils.secrets.get(scope="orders-pipeline-secrets", key="external_api_token")
```

Databricks redigiert automatisch Secret-Werte (`[REDACTED]`) überall dort, wo sie sonst in Notebook- oder Log-Ausgaben ausgegeben würden; zusätzlich lässt sich mit einer Secret-ACL einschränken, wer einen Scope lesen darf.

---

## <a id="pii">10. Sensible Daten in der Pipeline-Ausgabe schützen</a>

Für Spalten mit personenbezogenen Daten (PII) empfiehlt Databricks, Unity-Catalog-Governance auf die von der Pipeline erzeugten Tabellen anzuwenden, statt eigene Maskierungslogik im Pipeline-Code zu schreiben:

- **Column Masks** redigieren oder hashen den Wert einer Spalte abhängig von der Gruppenzugehörigkeit des abfragenden Nutzers.
- **Row Filters** schränken ein, welche Zeilen ein Nutzer sehen kann.

Das Anwenden dieser Kontrollen auf der Unity-Catalog-Tabelle schützt personenbezogene Daten konsistent für jeden Konsumenten der Tabelle — einschließlich Dashboards, Ad-hoc-Abfragen und nachgelagerter Jobs — und nicht nur innerhalb der Pipeline selbst. Als weiterer Schritt wird empfohlen, PII auf klar benannte, dedizierte Spalten oder Tabellen/Schemas zu beschränken, damit Zugriffsrechte und Audits einfacher nachvollziehbar bleiben.

---

## <a id="quellen">Quellen</a>

- [Manage identities, permissions, and privileges for pipelines (AWS)](https://docs.databricks.com/aws/en/ldp/privileges) — abgerufen 2026-08-19
- [Manage identities, permissions, and privileges for pipelines (Azure/Microsoft Learn, Gegenprüfung)](https://learn.microsoft.com/en-us/azure/databricks/ldp/privileges) — abgerufen 2026-08-19
- [Access control lists — Abschnitt "Lakeflow pipelines ACLs" (AWS)](https://docs.databricks.com/aws/en/security/auth/access-control/) — abgerufen 2026-08-19
- [Access control lists — Abschnitt "Lakeflow pipelines ACLs" (Azure/Microsoft Learn, Gegenprüfung)](https://learn.microsoft.com/en-us/azure/databricks/security/auth/access-control/) — abgerufen 2026-08-19
