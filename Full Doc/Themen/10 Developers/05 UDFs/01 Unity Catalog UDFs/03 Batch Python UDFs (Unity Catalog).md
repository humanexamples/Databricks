# Batch Python UDFs in Unity Catalog

Referenz zu Batch-Unity-Catalog-Python-UDFs (`PARAMETER STYLE PANDAS`): Verarbeitung von Zeilen-Batches statt Einzelzeilen, mit 1:1-Input/Output-Parität.

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [Batch-Unity-Catalog-Python-UDF erstellen](#erstellen)
3. [Batch-UDF-Handler-Funktion](#handler)
4. [Custom Dependencies installieren](#dependencies)
5. [Batch-UDFs mit einem oder mehreren Parametern](#parameter)
6. [Performance durch Trennung teurer Operationen optimieren](#performance)
7. [Environment Isolation](#isolation)
8. [Service Credentials in Batch-UDFs](#credentials)
9. [Task-Kontext abrufen](#task-context)
10. [`DETERMINISTIC` setzen](#deterministic)
11. [Limitierungen](#limitierungen)
12. [Quellen](#quellen)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

Batch-Unity-Catalog-Python-UDFs erfordern **Databricks Runtime 16.3 oder höher**.

---

## <a id="erstellen">2. Batch-Unity-Catalog-Python-UDF erstellen</a>

- `PARAMETER STYLE PANDAS`: legt fest, dass die UDF Daten in Batches über Pandas-Iteratoren verarbeitet.
- `HANDLER 'handler_function'`: legt die Handler-Funktion fest, die zur Verarbeitung der Batches aufgerufen wird.

```sql
%sql
CREATE OR REPLACE TEMPORARY FUNCTION calculate_bmi_pandas(weight_kg DOUBLE, height_m DOUBLE)
RETURNS DOUBLE
LANGUAGE PYTHON
DETERMINISTIC
PARAMETER STYLE PANDAS
HANDLER 'handler_function'
AS $$
import pandas as pd
from typing import Iterator, Tuple

def handler_function(batch_iter: Iterator[Tuple[pd.Series, pd.Series]]) -> Iterator[pd.Series]:
  for weight_series, height_series in batch_iter:
    yield weight_series / (height_series ** 2)
$$;
```

```sql
SELECT person_id, calculate_bmi_pandas(weight_kg, height_m) AS bmi
FROM (
  SELECT 1 AS person_id, CAST(70.0 AS DOUBLE) AS weight_kg, CAST(1.75 AS DOUBLE) AS height_m UNION ALL
  SELECT 2 AS person_id, CAST(80.0 AS DOUBLE) AS weight_kg, CAST(1.80 AS DOUBLE) AS height_m
);
```

---

## <a id="handler">3. Batch-UDF-Handler-Funktion</a>

Batch-Unity-Catalog-Python-UDFs benötigen eine Handler-Funktion, die Batches verarbeitet und Ergebnisse per `yield` zurückgibt. Der Name der Handler-Funktion wird bei der Erstellung der UDF über das Schlüsselwort `HANDLER` angegeben.

Die Handler-Funktion:

1. akzeptiert ein Iterator-Argument, das über eine oder mehrere `pandas.Series` iteriert — jede `pandas.Series` enthält die Eingabeparameter der UDF für einen Batch.
2. iteriert über den Generator und verarbeitet die Daten.
3. gibt einen Generator-Iterator zurück.

Batch-Unity-Catalog-Python-UDFs müssen dieselbe Anzahl Zeilen zurückgeben wie eingegeben wurde. Die Handler-Funktion stellt das sicher, indem sie pro Batch eine `pandas.Series` mit derselben Länge wie die Eingabe-Series per `yield` zurückgibt.

---

## <a id="dependencies">4. Custom Dependencies installieren</a>

Die Funktionalität von Batch-Unity-Catalog-Python-UDFs lässt sich über die Definition benutzerdefinierter Abhängigkeiten für externe Bibliotheken erweitern (siehe [SQL und Python UDFs (Unity Catalog) — Custom Dependencies](01%20SQL%20und%20Python%20UDFs%20%28Unity%20Catalog%29.md#dependencies)).

---

## <a id="parameter">5. Batch-UDFs mit einem oder mehreren Parametern</a>

Ein Parameter:

```sql
%sql
CREATE OR REPLACE TEMPORARY FUNCTION one_parameter_udf(value INT)
RETURNS STRING
LANGUAGE PYTHON
DETERMINISTIC
PARAMETER STYLE PANDAS
HANDLER 'handler_func'
AS $$
import pandas as pd
from typing import Iterator
def handler_func(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
  for value_batch in batch_iter:
    d = {"min": value_batch.min(), "max": value_batch.max()}
    yield pd.Series([str(d)] * len(value_batch))
$$;
SELECT one_parameter_udf(id), count(*) from range(0, 100000, 3, 8) GROUP BY ALL;
```

Zwei Parameter:

```sql
%sql
CREATE OR REPLACE TEMPORARY FUNCTION two_parameter_udf(p1 INT, p2 INT)
RETURNS INT
LANGUAGE PYTHON
DETERMINISTIC
PARAMETER STYLE PANDAS
HANDLER 'handler_function'
AS $$
import pandas as pd
from typing import Iterator, Tuple

def handler_function(batch_iter: Iterator[Tuple[pd.Series, pd.Series]]) -> Iterator[pd.Series]:
  for p1, p2 in batch_iter: # same order as arguments above
    yield p1 + p2
$$;
SELECT two_parameter_udf(id , id + 1) from range(0, 100000, 3, 8);
```

---

## <a id="performance">6. Performance durch Trennung teurer Operationen optimieren</a>

Code außerhalb der Handler-Funktion (z. B. auf Modulebene der UDF) wird nur einmal pro Isolation Environment ausgeführt, nicht pro Batch — teure einmalige Berechnungen sollten daher aus der Handler-Funktion herausgezogen werden:

```sql
%sql
CREATE OR REPLACE TEMPORARY FUNCTION expensive_computation_udf(value INT)
RETURNS INT
LANGUAGE PYTHON
DETERMINISTIC
PARAMETER STYLE PANDAS
HANDLER 'handler_func'
AS $$
def compute_value():
  # expensive computation...
  return 1

expensive_value = compute_value()
def handler_func(batch_iter):
  for batch in batch_iter:
    yield batch * expensive_value
$$;
SELECT expensive_computation_udf(id), count(*) from range(0, 100000, 3, 8) GROUP BY ALL
```

---

## <a id="isolation">7. Environment Isolation</a>

**Hinweis:** Shared Isolation Environments erfordern Databricks Runtime 17.1 oder höher. In früheren Versionen laufen alle Batch-Unity-Catalog-Python-UDFs im Strict-Isolation-Modus.

Batch-Unity-Catalog-Python-UDFs mit demselben Owner und derselben Session können standardmäßig eine Isolation Environment teilen. Das verbessert die Performance und reduziert den Speicherverbrauch, da weniger separate Umgebungen gestartet werden müssen.

### Strict Isolation

Die meisten UDFs benötigen keine Strict Isolation — Standard-Datenverarbeitungs-UDFs profitieren von der standardmäßig geteilten Isolation Environment und laufen schneller bei geringerem Speicherverbrauch.

Um sicherzustellen, dass eine UDF stets in einer eigenen, vollständig isolierten Umgebung läuft, wird die `STRICT ISOLATION`-Characteristic-Klausel hinzugefügt. Diese sollte bei UDFs verwendet werden, die:

- Input als Code mit `eval()`, `exec()` oder ähnlichen Funktionen ausführen
- Dateien ins lokale Dateisystem schreiben
- globale Variablen oder den Systemzustand verändern
- Umgebungsvariablen verändern

```sql
CREATE OR REPLACE TEMPORARY FUNCTION eval_string(input STRING)
RETURNS STRING
LANGUAGE PYTHON
PARAMETER STYLE PANDAS
HANDLER 'handler_func'
STRICT ISOLATION
AS $$
import pandas as pd
from typing import Iterator

def handler_func(batch_iter: Iterator[pd.Series]) -> Iterator[pd.Series]:
  for code_series in batch_iter:
    def eval_func(code):
      try:
        return str(eval(code))
      except Exception as e:
        return f"Error: {e}"
    yield code_series.apply(eval_func)
$$;
```

---

## <a id="credentials">8. Service Credentials in Batch-Unity-Catalog-Python-UDFs</a>

```sql
CREATE OR REPLACE TEMPORARY FUNCTION example_udf(data STRING)
RETURNS STRING
LANGUAGE PYTHON
PARAMETER STYLE PANDAS
HANDLER 'handler_function'
CREDENTIALS (
  `credential-name` DEFAULT,
  `complicated-credential-name` AS short_name,
  `simple-cred`,
  cred_no_quotes
)
AS $$
# Python code here
$$;
```

### Service-Credentials-Berechtigungen

Der Ersteller der UDF muss über die `ACCESS`-Berechtigung auf dem Unity-Catalog-Service-Credential verfügen. Für UDF-Aufrufer genügt es hingegen, ihnen die `EXECUTE`-Berechtigung auf der UDF zu erteilen — Aufrufer benötigen keinen Zugriff auf das zugrunde liegende Service Credential, da die UDF mit den Credential-Berechtigungen des Erstellers ausgeführt wird.

Bei temporären Funktionen ist der Ersteller stets identisch mit dem Aufrufer. UDFs, die im No-PE-Scope laufen (auch als "dedicated clusters" bezeichnet), verwenden stattdessen die Berechtigungen des Aufrufers.

### Default Credentials und Aliase

```python
from databricks.service_credentials import getServiceCredentialsProvider
import boto3

# Assuming credential definition: CREDENTIALS(`aws-cred` AS testcred)
boto3_session = boto3.Session(botocore_session=getServiceCredentialsProvider('testcred'))
s3 = boto3_session.client('s3')
```

### Service-Credential-Beispiel — AWS-Lambda-Funktion

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

  # Propagate TaskContext information to lambda context:
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

```sql
SELECT main.test.call_lambda_func(data, false)
FROM VALUES
('abc'),
('def')
AS t(data)
```

---

## <a id="task-context">9. Task-Kontext abrufen</a>

Über die `TaskContext`-PySpark-API lassen sich Kontextinformationen wie die Identität des Nutzers, Cluster-Tags, die Spark-Job-ID u. a. abrufen. Siehe [UDF Task Context.md](../03%20UDF%20Task%20Context.md).

---

## <a id="deterministic">10. `DETERMINISTIC` setzen, wenn die Funktion konsistente Ergebnisse liefert</a>

`DETERMINISTIC` sollte der Funktionsdefinition hinzugefügt werden, wenn sie für dieselben Eingaben stets dieselben Ausgaben liefert. Das erlaubt Query-Optimierungen, die Performance zu verbessern.

Standardmäßig werden Batch-Unity-Catalog-Python-UDTFs als nicht-deterministisch angenommen, sofern nicht explizit anders deklariert. Beispiele für nicht-deterministische Funktionen: Erzeugen von Zufallswerten, Abfragen der aktuellen Uhrzeit/des aktuellen Datums oder externe API-Aufrufe.

---

## <a id="limitierungen">11. Limitierungen</a>

- Um Batch-Unity-Catalog-Python-UDF-Aufrufe auf serverlosem Notebook- oder Job-Compute durchzuführen, muss Serverless Egress Control konfiguriert sein.

---

## <a id="quellen">12. Quellen</a>

- Batch Python user-defined functions (UDFs) in Unity Catalog: https://docs.databricks.com/aws/en/udf/python-batch-udf

**Stand:** 2026-08-22.
