# Pipeline-Properties-Referenz

Referenz für die JSON/YAML-Konfigurationseinstellungen von Lakeflow Declarative Pipelines, Tabellen-Properties und Trigger-Intervalle sowie nicht vom Nutzer setzbare Cluster-Attribute. Jede Aussage wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/properties` verifiziert; alle Default-Werte wurden zusätzlich über die Azure-Spiegelseite `learn.microsoft.com/en-us/azure/databricks/ldp/properties` wörtlich gegengeprüft.

## Abschnittsübersicht

1. [Einordnung: Lakeflow Pipelines und Apache Spark Declarative Pipelines](#einordnung)
2. [Wie Properties gesetzt werden](#setzen)
3. [Pipeline-Konfigurationen](#pipeline-konfigurationen)
4. [Pipeline-Tabellen-Properties](#tabellen-properties)
5. [Pipeline-Trigger-Intervall](#trigger-intervall)
6. [Nicht vom Nutzer setzbare Cluster-Attribute](#cluster-attribute)
7. [Quellen- und Query-Optionen](#quellen-optionen)
8. [Quellen](#quellen)

---

## <a id="einordnung">1. Einordnung: Lakeflow Pipelines und Apache Spark Declarative Pipelines</a>

Lakeflow Pipelines bauen auf Apache Spark Declarative Pipelines (SDP) auf. Die Pipeline-Konfiguration ist größtenteils eine Obermenge der SDP-Projekt-Spezifikation. Unterschiede in der Nutzung von Properties zwischen SDP und Lakeflow Pipelines sind in den folgenden Tabellen vermerkt.

---

## <a id="setzen">2. Wie Properties gesetzt werden</a>

Die meisten Pipeline-Properties lassen sich auf folgende Arten setzen:

- **Pipeline-JSON oder -YAML:** Property zur Pipeline-Spezifikation hinzufügen — entweder in der Pipeline-Settings-UI oder in einer Declarative-Automation-Bundles-Konfigurationsdatei. Pipeline-Level-Einstellungen wie `catalog`, `channel` und `edition` werden so gesetzt.
- **Das `configuration`-Objekt:** Spark-Konfigurationseigenschaften (mit dem Präfix `pipelines.`) lassen sich für die gesamte Pipeline setzen, indem sie zum `configuration`-Objekt der Pipeline-Spezifikation hinzugefügt werden.
- **SQL:** In einer SQL-Quelldatei wird eine Spark-Konfigurationseigenschaft für die nachfolgenden Datasets per `SET` gesetzt.
- **Python:** In einer Python-Quelldatei wird eine Spark-Konfigurationseigenschaft für ein einzelnes Dataset über das `spark_conf`-Argument des Dataset-Decorators gesetzt.

Das Setzen einer Property in SQL oder Python wirkt auf Dataset-Ebene und überschreibt den Pipeline-Level-Wert aus dem `configuration`-Objekt. Nicht jede Property unterstützt jede Methode: Pipeline-Level-Einstellungen lassen sich nur in der Spezifikation setzen, Spark-Konfigurationseigenschaften sowohl auf Pipeline- als auch auf Dataset-Ebene.

---

## <a id="pipeline-konfigurationen">3. Pipeline-Konfigurationen</a>

| Property | Typ | Default | Beschreibung |
|---|---|---|---|
| `id` | string | systemvergeben | Global eindeutige, vom System vergebene ID der Pipeline; unveränderlich. Nur Lakeflow-Pipelines (SDP vergibt keine Pipeline-ID). |
| `name` | string | erforderlich | Nutzerfreundlicher Name der Pipeline, sichtbar in der UI. Auch in SDP als erforderliches Feld `name`. |
| `configuration` | object | optional | Optionale Liste an Einstellungen, die der Spark-Konfiguration des Clusters hinzugefügt werden, der die Pipeline ausführt. Elemente als `key:value`-Paare. Auch in SDP als `configuration`. |
| `parameters` | object | optional | Beta-Feature: Map aus Key-Value-Paaren, die der Pipeline-Quellcode über Named-Parameter-Syntax referenzieren kann (z. B. `:source_catalog`). Keys erlauben alphanumerische Zeichen, `_`, `-`, `.`; Werte sind stets Strings. Überschreibbar beim Update-Start, am Pipeline-Task oder per Pushdown von Job-Parametern. Nur aus SQL referenzierbar. Nur Lakeflow-Pipelines. |
| `libraries` | array of objects | erforderlich | Array aus Code-Dateien mit Pipeline-Code und benötigten Artefakten. In SDP als `libraries`, dort als Liste von Source-File-Glob-Mustern statt eines Arrays von Code-File-Objekten. |
| `clusters` | array of objects | automatisch gewählt | Array an Spezifikationen für die Cluster, die die Pipeline ausführen. Ist nichts angegeben, wählt die Pipeline automatisch eine Standard-Cluster-Konfiguration. Nur Lakeflow-Pipelines (SDP verwaltet keine Compute). |
| `development` | boolean | `false` | Flag, ob die Pipeline im `development`- oder `production`-Modus läuft. Nur Lakeflow-Pipelines. |
| `notifications` | array of objects | optional | Optionales Array an Spezifikationen für E-Mail-Benachrichtigungen bei Abschluss eines Updates, Fehlschlag mit wiederholbarem oder nicht wiederholbarem Fehler, oder Fehlschlag eines Flows. Nur Lakeflow-Pipelines. |
| `continuous` | boolean | `false` | Flag, ob die Pipeline kontinuierlich läuft. Nur Lakeflow-Pipelines. |
| `catalog` | string | nicht gesetzt (legacy Hive) | Name des Standardkatalogs der Pipeline, in den alle Datasets und Metadaten veröffentlicht werden. Setzen dieses Werts aktiviert Unity Catalog für die Pipeline. Bleibt er ungesetzt, veröffentlicht die Pipeline in den legacy Hive Metastore am in `storage` angegebenen Speicherort. Im Legacy Publishing Mode gibt er den Katalog an, der das Zielschema enthält, in das alle Datasets der aktuellen Pipeline veröffentlicht werden. Auch in SDP als `catalog`. |
| `schema` | string | erforderlich | Name des Standardschemas der Pipeline, in das standardmäßig alle Datasets und Metadaten veröffentlicht werden. In SDP als `database` verfügbar, das auch den Alias `schema` akzeptiert. |
| `target` (legacy) | string | — | Veralteter Alternativname zu `schema` für das Standardschema der Pipeline; `schema` wird bevorzugt. Nur Lakeflow-Pipelines. |
| `storage` (legacy) | string | `dbfs:/pipelines/` | Speicherort auf DBFS oder Cloud-Storage, an dem Ausgabedaten und für die Pipeline-Ausführung benötigte Metadaten abgelegt werden. Nach der Pipeline-Erstellung unveränderlich. In SDP als erforderliches Feld `storage`; bei Lakeflow-Pipelines ein Legacy-Setting. |
| `channel` | string | `current` | Version der Pipeline-Runtime: `preview` zum Testen kommender Runtime-Änderungen, `current` für die aktuelle Runtime-Version. Optionales Feld. Databricks empfiehlt `current` für Produktions-Workloads. Nur Lakeflow-Pipelines. |
| `edition` | string | `ADVANCED` | Product Edition: `CORE` für Streaming-Ingest-Workloads, `PRO` für Streaming-Ingest- und CDC-Workloads, `ADVANCED` für Streaming-Ingest-, CDC- und Expectations-Workloads. Optionales Feld. Nur Lakeflow-Pipelines. |
| `photon` | boolean | `false` | Flag, ob Photon (die Hochleistungs-Spark-Engine) zur Ausführung genutzt wird. Photon-aktivierte Pipelines werden zu einem anderen Satz abgerechnet. Optionales Feld. Nur Lakeflow-Pipelines. |
| `serverless` | boolean | — | Flag, ob die Pipeline Serverless Compute nutzt. Nur Lakeflow-Pipelines. |
| `event_log` | object | optional | Konfiguration für das Event-Log-Ziel der Pipeline als Objekt mit den Feldern `name`, `catalog`, `schema`, das das Event Log in eine Unity-Catalog-Tabelle veröffentlicht. Nur Lakeflow-Pipelines. |
| `tags` | object | optional | Optionale Map benutzerdefinierter Tags für die Pipeline. Maximal 25 Tags können hinzugefügt werden. Nur Lakeflow-Pipelines. |
| `budget_policy_id` | string | automatisch aufgelöst | ID der Serverless-Budget-Policy zur Kostenzuordnung. Erscheint in der JSON/YAML-Konfiguration nur, wenn explizit gesetzt; ansonsten löst Databricks automatisch eine Standard-Policy auf (in der UI sichtbar, aber nicht in JSON/YAML geschrieben). Nur Lakeflow-Pipelines. |
| `root_path` | string | optional | Root-Pfad der Pipeline. Ist er gesetzt, wird dieses Verzeichnis beim Ausführen von Python-Quelldateien zu `sys.path` hinzugefügt, damit Module relativ dazu importiert werden können. Nur Lakeflow-Pipelines. |
| `environment` | object | optional | Environment-Spezifikation zur Installation von Python-Abhängigkeiten für die Pipeline. Nur Lakeflow-Pipelines. |
| `pipelines.maxFlowRetryAttempts` | int | **2** | Tritt bei einem Pipeline-Update ein wiederholbarer Fehler auf, ist dies die maximale Anzahl an Wiederholungsversuchen für einen Flow, bevor das Update fehlschlägt. Begrenzt Retries eines einzelnen, für wiederholbare Fehler anfälligen Flows, damit dieser nicht ein gesamtes Update blockiert. Default: zwei Retry-Versuche — bei einem wiederholbaren Fehler versucht die Pipeline-Runtime den Flow insgesamt dreimal auszuführen (den ursprünglichen Versuch eingeschlossen). Nur Lakeflow-Pipelines. |
| `pipelines.numUpdateRetryAttempts` | int | **5 (getriggert) / unbegrenzt (kontinuierlich)** | Tritt bei einem Update ein wiederholbarer Fehler auf, ist dies die maximale Anzahl an Wiederholungsversuchen für das gesamte Update, bevor es endgültig fehlschlägt (der Retry läuft als vollständiges Update). Gilt nur für Pipelines mit automatischem Retry- und Restart-Verhalten (siehe `Updates.md`) — nicht für Ad-hoc-Updates aus dem Editor oder ein `Validate`-Update. Nur Lakeflow-Pipelines. |

---

## <a id="tabellen-properties">4. Pipeline-Tabellen-Properties</a>

Zusätzlich zu den von Delta Lake unterstützten Tabellen-Properties lassen sich folgende Properties setzen:

| Property | Default | Beschreibung |
|---|---|---|
| `pipelines.autoOptimize.zOrderCols` | keiner | Optionaler String mit kommaseparierter Liste von Spaltennamen, nach denen die Tabelle Z-Order-sortiert wird, z. B. `pipelines.autoOptimize.zOrderCols = "year,month"`. Databricks empfiehlt stattdessen Liquid Clustering (`CLUSTER BY AUTO` bzw. `cluster_by_auto=True` in Python), damit Databricks Clustering-Spalten automatisch wählt und pflegt. Nur Lakeflow-Pipelines. |
| `pipelines.reset.allowed` | `true` | Steuert, ob für diese Tabelle ein Full Refresh erlaubt ist. Auch in SDP als `pipelines.reset.allowed`. |
| `pipelines.autoOptimize.managed` | `true` | Aktiviert/deaktiviert automatisch geplante Optimierung dieser Tabelle. Für von Predictive Optimization verwaltete Pipelines wird diese Property nicht genutzt. Nur Lakeflow-Pipelines. |

**`pipelines.reset.allowed` — Full-Table-Refresh-Schutz:** Dieser Schutz ist besonders wichtig, wenn die Rohdatenquelle Dateien nach einer bestimmten Zeitspanne automatisch entfernt (z. B. über eine Lifecycle-Richtlinie im Objektspeicher). Ohne diese Einstellung würden Daten, die im Quellverzeichnis nicht mehr vorhanden sind, bei einem **Run pipeline with full table refresh** nicht erneut in die Zieltabelle eingelesen — ein Full Refresh löscht die Tabelle zunächst vollständig und liest anschließend nur noch das aus der Quelle nach, was dort tatsächlich noch existiert. Mit `pipelines.reset.allowed = false` bleiben bereits eingelesene, aus der Quelle inzwischen entfernte Daten in der Tabelle erhalten. Siehe auch [Transform-Grundlagen.md](../07%20Transformationen/01%20Transform-Grundlagen.md), Abschnitt 7, für das analoge Szenario bei manuell gelöschten/aktualisierten Datensätzen.

---

## <a id="trigger-intervall">5. Pipeline-Trigger-Intervall</a>

Ein Trigger-Intervall lässt sich für die gesamte Pipeline oder als Teil einer Dataset-Deklaration angeben.

**Property:** `pipelines.trigger.interval`

**Default, abhängig vom Flow-Typ:**

- **5 Sekunden** für Streaming-Abfragen.
- **1 Minute** für Complete-Abfragen, wenn alle Eingabedaten aus Delta-Quellen stammen.
- **10 Minuten** für Complete-Abfragen, wenn Datenquellen ggf. nicht-Delta sind.

**Format:** Zahl plus Zeiteinheit. Gültige Zeiteinheiten: `second`/`seconds`, `minute`/`minutes`, `hour`/`hours`, `day`/`days` (Singular oder Plural verwendbar).

Beispielwerte:

```json
{"pipelines.trigger.interval" : "1 hour"}
{"pipelines.trigger.interval" : "10 seconds"}
{"pipelines.trigger.interval" : "30 second"}
{"pipelines.trigger.interval" : "1 minute"}
{"pipelines.trigger.interval" : "10 minutes"}
{"pipelines.trigger.interval" : "10 minute"}
```

Databricks empfiehlt, `pipelines.trigger.interval` auf einzelnen Tabellen zu setzen, da Streaming- und Batch-Abfragen unterschiedliche Defaults haben. Ein Setzen auf Pipeline-Ebene ist nur sinnvoll, wenn die Verarbeitung Updates für den gesamten Pipeline-Graphen steuern muss.

**In Python (auf einer Tabelle, via `spark_conf`):**

```python
@dp.table(
  spark_conf={"pipelines.trigger.interval" : "10 seconds"}
)
def <function-name>():
    return (<query>)
```

**In SQL (für nachfolgende Datasets, via `SET`):**

```sql
SET pipelines.trigger.interval=10 seconds;

CREATE OR REFRESH MATERIALIZED VIEW TABLE_NAME
AS SELECT ...
```

**Für die gesamte Pipeline (im `configuration`-Objekt):**

```json
{
  "configuration": {
    "pipelines.trigger.interval": "10 seconds"
  }
}
```

---

## <a id="cluster-attribute">6. Nicht vom Nutzer setzbare Cluster-Attribute</a>

Da Pipelines den Cluster-Lebenszyklus verwalten, werden viele Cluster-Einstellungen vom System gesetzt und können weder in einer Pipeline-Konfiguration noch in einer von einer Pipeline genutzten Cluster-Policy manuell konfiguriert werden. Gilt nur für Lakeflow-Pipelines (SDP verwaltet keine Compute, daher sind diese Attribute dort nicht relevant).

| Attribut | Begründung |
|---|---|
| `cluster_name` | Wird vom System gesetzt; kann nicht überschrieben werden. |
| `data_security_mode`, `access_mode` | Werden automatisch vom System gesetzt. |
| `spark_version` | Läuft auf einer angepassten Databricks-Runtime-Version, die kontinuierlich aktualisiert wird; die Spark-Version ist an die Runtime-Version gebunden und kann nicht überschrieben werden. |
| `autotermination_minutes` | Da die Pipeline die Auto-Termination- und Wiederverwendungslogik selbst verwaltet, kann die Auto-Termination-Zeit nicht überschrieben werden. |
| `runtime_engine` | Steuerbar nur indirekt über das Aktivieren von Photon; ein direktes Setzen ist nicht möglich. |
| `effective_spark_version` | Wird automatisch vom System gesetzt. |
| `cluster_source` | Wird vom System gesetzt und ist nur lesbar. |
| `docker_image` | Da die Pipeline den Cluster-Lebenszyklus verwaltet, sind benutzerdefinierte Container nicht kompatibel. |
| `workload_type` | Wird vom System gesetzt und kann nicht überschrieben werden. |

---

## <a id="quellen-optionen">7. Quellen- und Query-Optionen</a>

Manche Datenaufnahme- und Verarbeitungsverhalten werden auf der Datenquelle bzw. Abfrage selbst konfiguriert statt als Pipeline-Property — dazu zählen Schema-Evolution, Schema Hints und -Inferenz, Ingestion-Rate-Limits und Datei-Filterung. Konfiguriert wird dies über die Optionen von `read_files` und Auto Loader. Für Schema-Evolution mit `from_json` gibt es eine eigene Dokumentationsseite.

---

## <a id="quellen">8. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/properties
- https://learn.microsoft.com/en-us/azure/databricks/ldp/properties (Gegenprüfung: alle Default-Werte, Trigger-Intervalle)

**Stand:** 2026-08-19
