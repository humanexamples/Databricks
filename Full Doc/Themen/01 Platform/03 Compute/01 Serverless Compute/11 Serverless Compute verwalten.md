# Serverless Compute verwalten (Admin)

> Quelle: <https://docs.databricks.com/aws/en/compute/serverless/manage-serverless-compute>

Jeder Workspace erhält automatisch **zwei** Serverless-Compute-Objekte, die Workspace-Admins zur Steuerung von Zugriff und Ausgaben konfigurieren:

- **Default Interactive Compute** — steuert den Zugriff auf Notebooks und Databricks Connect
- **Default Automated Compute** — steuert den Zugriff auf Jobs und Spark Declarative Pipelines (Lakeflow)

Standardmäßig haben **alle** Workspace-Nutzer „Can Use" auf beiden Objekten. Die Default-Objekte können **nicht umbenannt oder gelöscht** werden.

## Zugriff verwalten

### Berechtigungsstufen

| Berechtigung | Fähigkeiten |
|---|---|
| **Can Use** | Workloads auf der Compute-Ressource ausführen |
| **Can Manage** | Workloads ausführen **und** Berechtigungseinstellungen ändern |

Workspace-Admins haben standardmäßig „Can Manage" und können das delegieren.

### Interaktiven Serverless-Zugriff einschränken

1. **Compute** in der Workspace-Sidebar → Tab **Serverless**
2. Kebab-Menü neben **Default Interactive Compute** → **Edit permissions**
3. Gruppe **All Users** entfernen
4. Zugriff nur autorisierten Nutzern/Gruppen/Service-Principals gewähren

Verlieren Nutzer den interaktiven Zugriff: bestehende Notebook-Verbindungen schlagen fehl, die **Serverless**-Option verschwindet aus dem Compute-Picker, Databricks Connect gibt Fehler zurück.

### Automatisierten Serverless-Zugriff einschränken

Analog über **Default Automated Compute**. Nutzer, die den Zugriff verlieren, erleben Job- und Pipeline-Fehler. **Vorher aktive Workloads auditieren.**

**Pre-Revocation-Audit-Query:**

```sql
SELECT *
FROM system.billing.usage
WHERE usage_date >= date_add(now(), -30)
  AND billing_origin_product IN ('JOBS', 'DLT')
  AND identity_metadata.run_as = '<user_email>';
```

Die Spalte `usage_metadata` prüfen, um betroffene Job-IDs und Pipeline-IDs zu identifizieren.

### Serverless-Nutzung auditieren

Billing-Datensätze enthalten ein Feld `serverless_compute_id` in `usage_metadata`:

```sql
SELECT
  usage_metadata.serverless_compute_id,
  identity_metadata.run_as,
  SUM(usage_quantity) AS total_dbus
FROM system.billing.usage
WHERE billing_origin_product IN ('JOBS', 'DLT', 'INTERACTIVE')
  AND usage_metadata.serverless_compute_id IS NOT NULL
  AND usage_date >= date_add(now(), -30)
GROUP BY 1, 2
ORDER BY 3 DESC;
```

### Unterstützte / nicht unterstützte Access-Control-Features

- **Interactive (Default Interactive Compute):** Notebooks + Serverless-GPU-Notebooks, Databricks Connect
- **Automated (Default Automated Compute):** Jobs + Serverless-GPU-Jobs, Spark Declarative Pipelines (Lakeflow)
- **Nicht** über diese Access Controls steuerbar: Databricks SQL (DBSQL), Batch Inference (`ai_query()`), Model Serving, Foundation Model API Provisioned Throughput, Lakebase, Databricks Apps, Agent Evaluation / Synthetic Data, Vector Search Indexing, Predictive Optimization, Lakehouse Monitoring, Fine-Grained Access Control auf Dedicated Compute.

### Access-Control-Limitierungen

> ⚠️ **Wichtig:** Bei Service-Störungen kann die Zugriffsprüfung **permissiv** fehlschlagen und ggf. nicht autorisierte Workload-Ausführung erlauben. Dieses Feature dient **nur der Governance**, **nicht** als Spend-Cap. Databricks übernimmt keine Verantwortung für Kosten während solcher Vorfälle.

- Default-Compute-Objekte können nicht umbenannt/gelöscht werden.
- Nutzer, die „Can Use" verlieren, erleben Job-/Pipeline-Fehler.
- **Background Compute** (systeminitiierte Jobs) umgeht die Serverless-Access-Controls.

## Rate Limits auf Serverless Compute — Private Preview

Rate Limits beschränken die Ausgaben automatisierter Workloads, indem sie Autoscaling-Parameter deckeln. Admins können **custom** Automated-Compute-Objekte mit individuellen Rate Limits anlegen.

- Gelten **nur** für automatisierte Workloads (Jobs, Spark Declarative Pipelines); interaktive Workloads bleiben unbeschränkt.
- Betreffen **nur** das Spark-Executor-Autoscaling — Driver, REPL-VMs, GPUs und MV-/Streaming-Table-Refreshes bleiben unberührt.
- Jeder Job/jede Pipeline auf einem Compute-Objekt erhält eigenständige Durchsetzung; mehrere Jobs auf demselben Objekt greifen jeweils auf den vollen Cap zu, Tasks innerhalb eines Jobs teilen sich einen Cap.

### Voraussetzungen

- Workspace-Admin **oder** unbeschränkte Cluster-Creation-Rechte
- Databricks Runtime **17.3.1+** (automatisch für Jobs; Opt-in-Preview-Channel für Lakeflow Pipelines)

### Rate-limited Serverless Compute erstellen

1. **Compute** → Tab **Serverless** → **Create serverless compute**
2. Name vergeben
3. **Size** von Small bis 2X-Large wählen (**Default** = Workspace-Standard)
4. **Create**

Das Objekt erscheint als Typ **Automated**. Nutzern „Can Use"/„Can Manage" gewähren. Größen von Default-Objekten sind nicht änderbar.

### Rate-Limit-Größen

| Größe | Ungefährer stündlicher DBU-Cap |
|---|---|
| Small | ~60 DBUs |
| Medium | ~120 DBUs |
| Large | ~240 DBUs |
| X-Large | ~480 DBUs |
| 2X-Large | ~960 DBUs |

**Default:** Medium (Premium-Tier) bzw. Large (Enterprise-Tier). Werte sind Richtwerte; tatsächlicher Verbrauch schwankt.

### Workloads auf Rate-limited Compute

- **Jobs:** Serverless Compute in den Job-**Compute**-Einstellungen wählen oder die Compute-ID über die Jobs-API referenzieren (**Copy compute ID** im **Serverless**-Tab).
- **Spark Declarative Pipelines:** Automated Compute im Lakeflow-Editor als Serverless Compute festlegen.
- Workloads ohne angegebenes Compute-Objekt → **Default Automated Compute**; fehlt der Zugriff, schlägt die Ausführung fehl.
- Throttling-Effekte erscheinen in der Query-History bzw. im Lakeflow-Pipeline-Interface.

### Rate-Limit-Constraints

- Nur Spark-Executor-Autoscaling wird beschränkt.
- Stündliche DBU-Caps sind Schätzungen; tatsächlicher Verbrauch kann Ziele überschreiten.
- 2X-Large-Workloads können unterperformen (physische Cluster-Größe cappt bei 256 Executors).
- Identische Workloads können bei unterschiedlichen Rate-Limit-Größen unterschiedlichen DBU-Verbrauch akkumulieren.
- Default-Compute-Objekte können keine Rate-Limit-Zuweisung erhalten.

## Verwandte Themen

- [01 Uebersicht.md](01%20Uebersicht.md) · [09 Einschraenkungen.md](09%20Einschraenkungen.md)
- Serverless Usage Policies / Networking (NCC, Egress Control): siehe die Governance-/Networking-Doku bzw. das Account-Team.
