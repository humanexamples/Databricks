# Task-Kontext in einer UDF abrufen (`TaskContext`)

Referenz zur `TaskContext`-PySpark-API, mit der sich Kontextinformationen während der Ausführung einer Batch-Unity-Catalog-Python-UDF oder einer PySpark-UDF (Scalar Python UDF) abrufen lassen — etwa die Identität des ausführenden Nutzers oder Cluster-Tags, um beispielsweise die Nutzeridentität für den Zugriff auf externe Dienste zu verifizieren. Vollständig und wörtlich per direktem HTML-Abruf gegen `docs.databricks.com/aws/en/udf/udf-task-context` verifiziert (WebFetch verweigerte hier die vollständige Wiedergabe unter Verweis auf Urheberrecht; die Zitate stammen daher aus einem direkten Abruf der Seite).

Diese Referenz gilt themenübergreifend für die Batch-Unity-Catalog-Python-UDFs (siehe [Batch Python UDFs (Unity Catalog)](01%20Unity%20Catalog%20UDFs/03%20Batch%20Python%20UDFs%20%28Unity%20Catalog%29.md#task-context)) und die session-scoped Python-Scalar-UDFs (siehe [Python Scalar UDFs](02%20Session-scoped%20UDFs/01%20Python%20Scalar%20UDFs.md#task-context)).

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [TaskContext zum Abrufen von Kontextinformationen nutzen](#nutzung)
3. [`TaskContext`-Eigenschaften](#eigenschaften)
4. [Quellen](#quellen)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

- `TaskContext` wird ab **Databricks Runtime 16.3** unterstützt.
- `TaskContext` wird für folgende UDF-Typen unterstützt: **Batch Unity Catalog Python UDFs** und **Scalar Python UDFs** (in der Doku-Oberfläche als "PySpark UDF" bezeichnet).

---

## <a id="nutzung">2. TaskContext zum Abrufen von Kontextinformationen nutzen</a>

Die Doku zeigt zwei Beispiele über zwei Reiter — einen für **PySpark UDF**, einen für **Batch Unity Catalog Python UDF**.

### PySpark UDF

Das folgende PySpark-UDF-Beispiel gibt den Kontext des Nutzers aus:

```python
@udf
def log_context():
  import json
  from pyspark.taskcontext import TaskContext
  tc = TaskContext.get()

  # Returns current user executing the UDF
  session_user = tc.getLocalProperty("user")

  # Returns cluster tags
  tags = dict(item.values() for item in json.loads(tc.getLocalProperty("spark.databricks.clusterUsageTags.clusterAllTags  ") or "[]"))

  # Returns current version details
  current_version = {
    "dbr_version": tc.getLocalProperty("spark.databricks.clusterUsageTags.sparkVersion"),
    "dbsql_version": tc.getLocalProperty("spark.databricks.clusterUsageTags.dbsqlVersion")
  }

  return {
    "user": session_user,
    "job_group_id": job_group_id,
    "tags": tags,
    "current_version": current_version
  }
```

**Auffälligkeit beim wörtlichen Abgleich:** Im Rückgabe-Dictionary wird die Variable `job_group_id` verwendet, obwohl sie im gezeigten Code-Beispiel selbst nirgends zugewiesen wird (im Gegensatz zu `session_user`, `tags` und `current_version`, die alle zuvor definiert werden). Das ist wörtlich so auf der offiziellen Doku-Seite abgedruckt — vermutlich fehlt dort eine Zeile wie `job_group_id = tc.getLocalProperty("spark.jobGroup.id")` (siehe die entsprechende Property in Abschnitt 3). Diese Unstimmigkeit wird hier bewusst nicht stillschweigend korrigiert, sondern als Ungenauigkeit der Quelle dokumentiert.

### Batch Unity Catalog Python UDF

Das folgende Batch-Unity-Catalog-Python-UDF-Beispiel ruft die Nutzeridentität ab, um über ein Service Credential eine AWS-Lambda-Funktion aufzurufen:

```sql
%sql
CREATE OR REPLACE FUNCTION main.test.call_lambda_func(data STRING, debug BOOLEAN) RETURNS STRING LANGUAGE PYTHON
PARAMETER STYLE PANDAS
HANDLER 'batchhandler'
CREDENTIALS (
  `batch-udf-service-creds-example-cred` DEFAULT
)
AS $$
import boto3
import json
import pandas as pd
import base64
from pyspark.taskcontext import TaskContext


def batchhandler(it):
  # Automatically picks up DEFAULT credential:
  session = boto3.Session()

  client = session.client("lambda", region_name="us-west-2")

  # Can propagate TaskContext information to lambda context:
  user_ctx = {"custom": {"user": TaskContext.get().getLocalProperty("user")}}

  for vals, is_debug in it:
    payload = json.dumps({"values": vals.to_list(), "is_debug": bool(is_debug[0])})

    res = client.invoke(
      FunctionName="HashValuesFunction",
      InvocationType="RequestResponse",
      ClientContext=base64.b64encode(json.dumps(user_ctx).encode("utf-8")).decode(
        "utf-8"
      ),
      Payload=payload,
    )

    response_payload = json.loads(res["Payload"].read().decode("utf-8"))
    if "errorMessage" in response_payload:
      raise Exception(str(response_payload))

    yield pd.Series(response_payload["values"])
$$;
```

Die UDF nach der Registrierung aufrufen:

```sql
SELECT main.test.call_lambda_func(data, false)
FROM VALUES
('abc'),
('def')
AS t(data)
```

---

## <a id="eigenschaften">3. `TaskContext`-Eigenschaften</a>

Die Methode `TaskContext.getLocalProperty()` kennt laut Doku folgende Property-Schlüssel:

| Property-Schlüssel | Beschreibung | Beispielnutzung |
|---|---|---|
| `user` | Der Nutzer, der die UDF aktuell ausführt | `tc.getLocalProperty("user")` → `"alice"` |
| `spark.jobGroup.id` | Die mit der aktuellen UDF verknüpfte Spark-Job-Group-ID | `tc.getLocalProperty("spark.jobGroup.id")` → `"jobGroup-92318"` |
| `spark.databricks.clusterUsageTags.clusterAllTags` | Cluster-Metadaten-Tags als Schlüssel-Wert-Paare, formatiert als String-Repräsentation eines JSON-Dictionarys | `tc.getLocalProperty("spark.databricks.clusterUsageTags.clusterAllTags")` → `[{"Department": "Finance"}]` |
| `spark.databricks.clusterUsageTags.region` | Die Region, in der sich der Workspace befindet | `tc.getLocalProperty("spark.databricks.clusterUsageTags.region")` → `"us-west-2"` |
| `accountId` | Databricks-Account-ID für den laufenden Kontext | `tc.getLocalProperty("accountId")` → `"1234567890123456"` |
| `orgId` | Workspace-ID (auf DBSQL nicht verfügbar) | `tc.getLocalProperty("orgId")` → `"987654321"` |
| `spark.databricks.clusterUsageTags.sparkVersion` | Databricks-Runtime-Version des Clusters (auf Nicht-DBSQL-Umgebungen) | `tc.getLocalProperty("spark.databricks.clusterUsageTags.sparkVersion")` → `"16.3"` |
| `spark.databricks.clusterUsageTags.dbsqlVersion` | DBSQL-Version (auf DBSQL-Umgebungen) | `tc.getLocalProperty("spark.databricks.clusterUsageTags.dbsqlVersion")` → `"2024.35"` |

---

## <a id="quellen">4. Quellen</a>

- Get task context in a UDF: https://docs.databricks.com/aws/en/udf/udf-task-context
- Verwandte Dateien in diesem Projekt: [Batch Python UDFs (Unity Catalog)](01%20Unity%20Catalog%20UDFs/03%20Batch%20Python%20UDFs%20%28Unity%20Catalog%29.md), [Python Scalar UDFs](02%20Session-scoped%20UDFs/01%20Python%20Scalar%20UDFs.md), [Serialization.md](../Performance%20Optimization/Code%20Optimization/Serialization.md) (allgemeine UDF-Performance-Hierarchie)

**Stand:** 2026-08-22.
