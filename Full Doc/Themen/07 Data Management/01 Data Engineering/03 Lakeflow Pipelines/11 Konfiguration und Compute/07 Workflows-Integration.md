# Workflows-Integration

Dieses Dokument fasst die Databricks-Referenzseite "Run pipelines in a workflow" zusammen. Verifiziert per `WebFetch` gegen die AWS-Seite (`docs.databricks.com/aws/en/ldp/workflows`) und wörtlich vollständig extrahiert von der inhaltlich übereinstimmenden Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/workflows`) — insbesondere die Angabe zur Multiplikation der Retry-Werte bei Azure Data Factory wurde in beiden Abrufen übereinstimmend wörtlich zitiert.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Pipeline für Orchestrierung vorbereiten](#vorbereitung)
3. [Lakeflow Jobs](#lakeflow-jobs)
4. [Apache Airflow](#airflow)
5. [Azure Data Factory](#adf)
6. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick</a>

Eine Pipeline lässt sich als Teil eines Datenverarbeitungs-Workflows mit Lakeflow Jobs, Apache Airflow oder Azure Data Factory ausführen.

Eine Pipeline löst die Abhängigkeiten zwischen ihren Datasets automatisch auf und handhabt damit einfache, pipeline-interne Orchestrierung selbstständig. Für Orchestrierung, für die eine Pipeline nicht gebaut ist — etwa bedingte Ausführung, Verzweigung basierend auf Task-Ergebnissen, Retries oder die Koordination einer Pipeline mit anderen Arten von Arbeit — sollte statt der Logik innerhalb der Pipeline ein dedizierter Workflow-Orchestrator verwendet werden.

## <a id="vorbereitung">2. Pipeline für Orchestrierung vorbereiten</a>

Orchestrierung funktioniert am besten, wenn jede Pipeline eine klar abgegrenzte Arbeitseinheit abdeckt, die separat geplant, validiert oder ausgeführt werden soll. Pipelines sollten an solchen Grenzen ausgerichtet werden, damit ein Workflow sie als separate Tasks koordinieren kann, einschließlich geeigneter Control-Flow zwischen vor- und nachgelagerten Tasks.

Existiert bereits eine große Pipeline, die separat zu orchestrierende Arbeit kombiniert, sollte sie in kleinere Pipelines aufgeteilt werden, indem Tabellen in eine neue Pipeline verschoben werden.

## <a id="lakeflow-jobs">3. Lakeflow Jobs</a>

Mehrere Tasks lassen sich in Lakeflow Jobs orchestrieren, um einen Datenverarbeitungs-Workflow umzusetzen. Um eine Pipeline in einen Job einzubinden, wird beim Erstellen eines Jobs der **Pipeline**-Task verwendet.

## <a id="airflow">4. Apache Airflow</a>

Apache Airflow ist eine Open-Source-Lösung zur Verwaltung und Planung von Datenworkflows. Airflow stellt Workflows als gerichtete azyklische Graphen (DAGs) von Operationen dar. Ein Workflow wird in einer Python-Datei definiert; Airflow übernimmt Planung und Ausführung.

Um eine Pipeline als Teil eines Airflow-Workflows auszuführen, wird der `DatabricksSubmitRunOperator` verwendet.

### Anforderungen

- Airflow-Version 2.1.0 oder höher.
- Das Databricks-Provider-Paket in Version 2.1.0 oder höher.

### Beispiel

Das folgende Beispiel erstellt einen Airflow-DAG, der ein Update für die Pipeline mit der ID `8279d543-063c-4d63-9926-dae38e35ce8b` auslöst:

```python
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
from airflow.utils.dates import days_ago

default_args = {
  'owner': 'airflow'
}

with DAG('ldp',
         start_date=days_ago(2),
         schedule_interval="@once",
         default_args=default_args
         ) as dag:

  opr_run_now=DatabricksSubmitRunOperator(
    task_id='run_now',
    databricks_conn_id='CONNECTION_ID',
    pipeline_task={"pipeline_id": "8279d543-063c-4d63-9926-dae38e35ce8b"}
  )
```

`CONNECTION_ID` wird durch die ID einer Airflow-Connection zum Workspace ersetzt. Das Beispiel wird im Verzeichnis `airflow/dags` gespeichert; über die Airflow-UI lässt sich der DAG einsehen und auslösen. Die Details des Pipeline-Updates lassen sich über die Pipeline-UI einsehen.

## <a id="adf">5. Azure Data Factory</a>

**Wichtiger, wörtlich zitierter Hinweis:** Lakeflow-Pipelines und Azure Data Factory bieten jeweils Optionen zur Konfiguration der Anzahl von Retries bei einem Fehlschlag. Sind Retry-Werte sowohl für die Pipeline **als auch** für die Azure-Data-Factory-Aktivität konfiguriert, die die Pipeline aufruft, ist die Anzahl der Retries das Produkt aus dem Azure-Data-Factory-Retry-Wert und dem Pipeline-Retry-Wert.

Beispiel aus der Doku: Schlägt ein Pipeline-Update fehl, versucht die Pipeline das Update standardmäßig bis zu **fünf Mal** erneut. Ist der Azure-Data-Factory-Retry auf drei gesetzt und die Pipeline verwendet den Standardwert von fünf Retries, kann eine fehlschlagende Pipeline bis zu **fünfzehn Mal** erneut versucht werden. Um übermäßige Retry-Versuche bei fehlschlagenden Pipeline-Updates zu vermeiden, empfiehlt Databricks, die Anzahl der Retries entweder bei der Pipeline-Konfiguration oder bei der aufrufenden Azure-Data-Factory-Aktivität zu begrenzen.

Die Retry-Konfiguration der Pipeline lässt sich über die Einstellung `pipelines.numUpdateRetryAttempts` ändern.

Azure Data Factory ist ein cloudbasierter ETL-Dienst zur Orchestrierung von Datenintegrations- und -transformations-Workflows. Eine Pipeline lässt sich in einen Workflow einbinden, indem die Pipeline-REST-API über eine Azure-Data-Factory-**Web-Aktivität** aufgerufen wird. Vorgehen zum Auslösen eines Pipeline-Updates aus Azure Data Factory:

1. Eine Data Factory erstellen oder eine bestehende öffnen.
2. **Open Azure Data Factory Studio** öffnen.
3. Über das **New**-Dropdown-Menü **Pipeline** auswählen, um eine neue Azure-Data-Factory-Pipeline zu erstellen.
4. Im **Activities**-Werkzeugkasten unter **General** die **Web**-Aktivität auf die Pipeline-Canvas ziehen. Im Tab **Settings** folgende Werte eintragen:

   - **URL**: `https://<databricks-instance>/api/2.0/pipelines/<pipeline-id>/updates`
   - **Method**: `POST`
   - **Headers**: Name `Authorization`, Value `Bearer <personal-access-token>`
   - **Body**: JSON-Dokument mit zusätzlichen Request-Parametern, etwa `{"full_refresh": "true"}`, um ein Update zu starten und alle Daten der Pipeline erneut zu verarbeiten. Ohne zusätzliche Parameter: leere geschweifte Klammern `{}`.

**Sicherheits-Hinweis aus der Doku:** Bei der Authentifizierung mit automatisierten Tools, Systemen, Skripten und Apps empfiehlt Databricks, Personal Access Tokens von Service Principals statt von Workspace-Nutzern zu verwenden.

Zum Testen der Web-Aktivität wird in der Data-Factory-UI auf **Debug** geklickt; Ausgabe und Status des Laufs — einschließlich Fehler — erscheinen im Tab **Output**.

**Tipp aus der Doku:** Ein häufiges Workflow-Erfordernis ist, einen Task nach Abschluss eines vorherigen Tasks zu starten. Da der `updates`-Request der Pipeline asynchron ist — er kehrt zurück, nachdem das Update gestartet wurde, aber bevor es abgeschlossen ist — müssen Tasks mit einer Abhängigkeit vom Pipeline-Update auf dessen Abschluss warten. Eine Option dafür ist das Hinzufügen einer **Until-Aktivität** nach der auslösenden Web-Aktivität:

1. Eine **Wait-Aktivität** hinzufügen, die eine konfigurierte Anzahl Sekunden auf den Abschluss des Updates wartet.
2. Eine Web-Aktivität nach der Wait-Aktivität hinzufügen, die über den Pipeline-Update-Details-Request den Status des Updates abfragt. Das Feld `state` in der Antwort liefert den aktuellen Status des Updates, einschließlich, ob es abgeschlossen ist.
3. Der Wert des `state`-Felds dient als Abbruchbedingung für die Until-Aktivität. Optional lässt sich eine **Set-Variable-Aktivität** verwenden, um eine Pipeline-Variable basierend auf dem `state`-Wert zu setzen und für die Abbruchbedingung zu nutzen.

---

## <a id="quellen">Quellen</a>

- https://docs.databricks.com/aws/en/ldp/workflows
- https://learn.microsoft.com/en-us/azure/databricks/ldp/workflows (wörtliche Vollzitat-Quelle, inhaltlich mit AWS-Seite abgeglichen)
