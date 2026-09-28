# Classic Compute konfigurieren

Dieses Dokument fasst die Databricks-Referenzseite "Configure classic compute for pipelines" zusammen. Verifiziert per `WebFetch` gegen die AWS-Seite (`docs.databricks.com/aws/en/ldp/configure-compute`) und wörtlich vollständig extrahiert von der inhaltlich übereinstimmenden Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/configure-compute`).

## Abschnittsübersicht

1. [Wann Classic Compute?](#wann-classic)
2. [Compute für die Pipeline auswählen](#compute-auswaehlen)
3. [Compute Policy wählen](#compute-policy)
4. [Compute-Tags konfigurieren](#compute-tags)
5. [Instance-Typen wählen](#instance-typen)
6. [Update- und Maintenance-Cluster getrennt konfigurieren](#separate-cluster)
7. [Compute-Shutdown verzögern](#shutdown-delay)
8. [Single-Node-Compute erstellen](#single-node)
9. [Liquid Clustering in Lakeflow Pipelines](#liquid-clustering)
10. [Quellen](#quellen)

---

## <a id="wann-classic">1. Wann Classic Compute?</a>

Databricks empfiehlt Serverless für neue Pipelines. Classic Compute wird gewählt, wenn bestimmte Instanztypen, benutzerdefinierte Compute-Policies, Init-Skripte, ein extern auf dem Cluster installierter JDBC-Treiber oder ein Workspace außerhalb einer Serverless-fähigen Region benötigt werden.

Um eine Pipeline zu erstellen, die auf Classic Compute läuft, benötigen Nutzer zunächst die Berechtigung, Classic Compute bereitzustellen — entweder uneingeschränkte Erstellungsberechtigung oder Zugriff auf eine Compute Policy. Serverless-Pipelines benötigen **keine** Compute-Erstellungsberechtigungen; standardmäßig können alle Workspace-Nutzer Serverless-Pipelines verwenden.

**Hinweis aus der Doku:** Da die Pipeline-Runtime den Lebenszyklus der Pipeline-Compute verwaltet und eine angepasste Version von Databricks Runtime ausführt, lassen sich manche Compute-Einstellungen in einer Pipeline-Konfiguration **nicht** manuell setzen, etwa die Spark-Version oder Cluster-Namen.

## <a id="compute-auswaehlen">2. Compute für die Pipeline auswählen</a>

So wird Classic Compute für eine Pipeline im Lakeflow Pipelines Editor konfiguriert:

1. Auf **Settings** klicken.
2. Im Abschnitt **Compute** der Pipeline-Einstellungen das Stift-Symbol anklicken.
3. Ist **Serverless** angehakt, die Checkbox deaktivieren.
4. Weitere Änderungen an den Compute-Einstellungen vornehmen und **Save** klicken.

## <a id="compute-policy">3. Compute Policy wählen</a>

Workspace-Admins können Compute Policies konfigurieren, um Nutzern Zugriff auf Classic-Compute-Ressourcen für Pipelines zu geben. Compute Policies sind optional.

Bei Verwendung der Pipelines-API muss `"apply_policy_default_values": true` in der `clusters`-Definition gesetzt werden, damit die Policy-Default-Werte korrekt angewendet werden:

```json
{
  "clusters": [
    {
      "label": "default",
      "policy_id": "<policy-id>",
      "apply_policy_default_values": true
    }
  ]
}
```

## <a id="compute-tags">4. Compute-Tags konfigurieren</a>

Benutzerdefinierte Tags lassen sich zu den Classic-Compute-Ressourcen der Pipeline hinzufügen. Tags erlauben die Überwachung der Kosten von Compute-Ressourcen für verschiedene Gruppen innerhalb der Organisation. Databricks wendet diese Tags auf Cloud-Ressourcen und auf in den Usage-System-Tabellen erfasste Nutzungsprotokolle an. Tags lassen sich über die **Cluster tags**-UI-Einstellung oder durch Bearbeiten der JSON-Konfiguration der Pipeline hinzufügen.

## <a id="instance-typen">5. Instance-Typen wählen</a>

Standardmäßig wählt die Pipeline die Instanztypen für Driver- und Worker-Knoten selbst. Diese lassen sich optional konfigurieren — etwa um die Pipeline-Performance zu verbessern oder Speicherprobleme zu beheben.

Vorgehen im Lakeflow Pipelines Editor:

1. Auf **Settings** klicken.
2. Im Abschnitt **Compute** der Pipeline-Einstellungen das Stift-Symbol anklicken.
3. Im Abschnitt **Advanced settings** die Instanztypen für **Worker type** und **Driver type** auswählen.

## <a id="separate-cluster">6. Update- und Maintenance-Cluster getrennt konfigurieren</a>

Jede Declarative Pipeline besitzt zwei zugehörige Compute-Ressourcen: einen **Update-Cluster**, der Pipeline-Updates verarbeitet, und einen **Maintenance-Cluster**, der tägliche Pflegeaufgaben ausführt (einschließlich Predictive Optimization). Standardmäßig gelten die Compute-Konfigurationen für beide Cluster. Dieselben Einstellungen für beide Cluster zu verwenden verbessert die Zuverlässigkeit von Maintenance-Läufen, da so sichergestellt wird, dass erforderliche Konfigurationen — etwa Datenzugriffs-Credentials für einen Storage-Speicherort — auch auf den Maintenance-Cluster angewendet werden.

Um Einstellungen nur auf einen der beiden Cluster anzuwenden, wird das Feld `label` zum Einstellungs-JSON-Objekt hinzugefügt. Mögliche Werte:

- `maintenance`: gilt nur für den Maintenance-Cluster.
- `updates`: gilt nur für den Update-Cluster.
- `default`: gilt für beide Cluster. Dies ist der Standardwert, falls `label` weggelassen wird.

Bei widersprüchlichen Einstellungen überschreibt die mit `updates` oder `maintenance` gelabelte Einstellung die mit `default` gelabelte Einstellung.

**Hinweis aus der Doku:** Der tägliche Maintenance-Cluster wird nur in bestimmten Fällen verwendet: Pipelines, die im Hive-Metastore gespeichert sind; Pipelines in Workspaces, die die Serverless-Compute-Nutzungsbedingungen nicht akzeptiert haben; Pipelines in Workspaces, bei denen der Private Link zu Serverless nicht korrekt konfiguriert ist.

### Beispiel: Einstellung nur für den Update-Cluster definieren

```json
{
  "clusters": [
    {
      "label": "default",
      "autoscale": {
        "min_workers": 1,
        "max_workers": 5,
        "mode": "ENHANCED"
      }
    },
    {
      "label": "updates",
      "spark_conf": {
        "key": "value"
      }
    }
  ]
}
```

**Hinweis aus der Doku:** Um die Kosten bei Classic Compute zu kontrollieren, sollte Enhanced Autoscaling (`"mode": "ENHANCED"`) aktiviert und realistische `min_workers`- und `max_workers`-Grenzen passend zum jeweiligen Workload gesetzt werden, statt einer für Spitzenlast dimensionierten festen Worker-Anzahl (siehe `Autoscaling.md`).

### Beispiel: Instanztypen nur für den Update-Cluster konfigurieren

```json
{
  "clusters": [
    {
      "label": "updates",
      "node_type_id": "Standard_D12_v2",
      "driver_node_type_id": "Standard_D3_v2",
      "...": "..."
    }
  ]
}
```

## <a id="shutdown-delay">7. Compute-Shutdown verzögern</a>

Über die Einstellung `pipelines.clusterShutdown.delay` in der Pipeline-Konfiguration lässt sich das Cluster-Shutdown-Verhalten steuern. Das folgende Beispiel setzt den Wert auf 60 Sekunden:

```json
{
  "configuration": {
    "pipelines.clusterShutdown.delay": "60s"
  }
}
```

Der Standardwert für `pipelines.clusterShutdown.delay` hängt vom Update-Ausführungsverhalten ab: **0 Sekunden** für Updates, die automatisches Retry- und Restart-Verhalten nutzen, und **2 Stunden** für Ad-hoc-Updates mit Fast-Start-, auf Debugging ausgerichtetem Verhalten.

**Hinweis aus der Doku:** Da Pipeline-Compute-Ressourcen automatisch herunterfahren, wenn sie nicht genutzt werden, kann keine Compute Policy verwendet werden, die `autotermination_minutes` setzt — das führt zu einem Fehler.

## <a id="single-node">8. Single-Node-Compute erstellen</a>

Ein Single-Node-Compute besitzt einen Driver-Knoten, der sowohl als Master als auch als Worker fungiert. Gedacht für Workloads mit geringen Datenmengen oder ohne Verteilung.

Um Single-Node-Compute zu erstellen, wird `num_workers` auf 0 gesetzt:

```json
{
  "clusters": [
    {
      "num_workers": 0
    }
  ]
}
```

## <a id="liquid-clustering">9. Liquid Clustering in Lakeflow Pipelines</a>

Liquid Clustering lässt sich in Lakeflow Pipelines **direkt auf der Streaming-Table- bzw. Materialized-View-Definition** aktivieren, über die `CLUSTER BY`-Klausel — ein separater `OPTIMIZE`-Befehl ist dafür nicht nötig, da die Pipeline-Runtime das Clustering beim Schreiben übernimmt. Die allgemeinen Grundlagen zu Liquid Clustering (Konzept, Vorteile gegenüber Partitionierung/Z-Ordering, `OPTIMIZE FULL`, Predictive Optimization) sind ausführlich in [Liquid Clustering.md](../../../../Performance%20Optimization/Foundation%20Design/Liquid%20Clustering.md) behandelt; die vollständige formale `CLUSTER BY`-Syntax für `CREATE STREAMING TABLE` (inklusive `AUTO`, `NONE`, Wechselwirkung mit `PARTITIONED BY`) findet sich in [CREATE STREAMING TABLE.md](../14%20Developer%20Reference/SQL-Referenz/CREATE%20STREAMING%20TABLE.md).

**Zwei Varianten, direkt auf der Tabellendefinition:**

```sql
-- Databricks wählt die Clustering-Spalten automatisch anhand der Query-Historie
CREATE OR REFRESH STREAMING TABLE my_table
CLUSTER BY AUTO
AS SELECT * FROM STREAM source_table;

-- Explizit angegebene Clustering-Spalten
CREATE OR REFRESH STREAMING TABLE my_table
CLUSTER BY (region, order_date)
AS SELECT * FROM STREAM source_table;
```

**Nicht-Databricks-Quelle: privates Kursmaterial** (`Kursmetrial_Databricks/5_Advanced Techniques with Spark Declarative Pipelines/_Abschnitte/_1 Lecture - Introduction to Multi Flows, Expectation and Liquid Clustering in SDP/D. Liquid Clustering in Spark Declarative Pipelines.md`): Entscheidungshilfe für die beiden Varianten:

- **`CLUSTER BY AUTO`** — geeignet, wenn die Query-Muster noch unbekannt sind oder sich weiterentwickeln; Databricks beobachtet die tatsächliche Nutzung und wählt/passt die Clustering-Keys eigenständig an. Zu Beginn ist noch kein Key gesetzt — Databricks muss zunächst Queries beobachten, bevor Keys gewählt werden.
- **`CLUSTER BY (columns)`** — geeignet bei bekannten, stabilen Filterspalten; liefert volle Kontrolle und ein vorhersehbares Layout, etwa für regulatorisch oder performancekritisch wichtige Tabellen.
- **Hybrid möglich:** explizite Spalten als Startpunkt setzen und zusätzlich Auto-Clustering für die langfristige Weiterentwicklung aktivieren.

Diese beiden Fälle entsprechen exakt den in [CREATE STREAMING TABLE.md](../14%20Developer%20Reference/SQL-Referenz/CREATE%20STREAMING%20TABLE.md) dokumentierten `CLUSTER BY`-Optionen `AUTO` und benannte Spalten; die dortige Referenz beschreibt zusätzlich die dritte Option `NONE` sowie den gegenseitigen Ausschluss mit `PARTITIONED BY`.

### Quellen

- Kursmaterial (siehe Pfadangabe oben)
- https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-streaming-table
- https://docs.databricks.com/aws/en/tables/clustering

---

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/configure-compute
- https://learn.microsoft.com/en-us/azure/databricks/ldp/configure-compute (wörtliche Vollzitat-Quelle, inhaltlich mit AWS-Seite abgeglichen)
