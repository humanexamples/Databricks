# Python Scalar UDFs (Session-scoped)

Referenz zu session-scoped Python-Scalar-UDFs, die direkt über die PySpark-API in einer Notebook-/Job-Session registriert werden (`spark.udf.register`, `@udf`).

## Abschnittsübersicht

1. [Voraussetzungen](#voraussetzungen)
2. [Eine Funktion als UDF registrieren](#registrieren)
3. [Die UDF in Spark SQL aufrufen](#sql-aufruf)
4. [UDF mit DataFrames verwenden](#dataframes)
5. [Variant-Typen mit UDFs](#variant)
6. [Dateien mit UDF (Beta)](#files)
7. [Auswertungsreihenfolge und Null-Prüfung](#null-checking)
8. [Service Credentials in Scalar Python UDFs](#credentials)
9. [Task-Ausführungskontext abrufen](#task-context)
10. [Limitierungen](#limitierungen)
11. [Quellen](#quellen)

---

## <a id="voraussetzungen">1. Voraussetzungen</a>

- In Databricks Runtime 12.2 LTS und darunter werden Python-UDFs und Pandas-UDFs auf Unity-Catalog-Compute mit Standard Access Mode nicht unterstützt.
- Scalar-Python-UDFs und Pandas-UDFs werden ab Databricks Runtime 13.3 LTS für alle Access Modes unterstützt.
- Graviton-Instance-Support für Python-UDFs auf Unity-Catalog-fähigen Clustern erfordert Databricks Runtime 15.2 oder höher.

---

## <a id="registrieren">2. Eine Funktion als UDF registrieren</a>

```python
def squared(s):
  return s * s
spark.udf.register("squaredWithPython", squared)
```

Mit explizitem Rückgabetyp:

```python
from pyspark.sql.types import LongType
def squared_typed(s):
  return s * s
spark.udf.register("squaredWithPython", squared_typed, LongType())
```

---

## <a id="sql-aufruf">3. Die UDF in Spark SQL aufrufen</a>

```python
spark.range(1, 20).createOrReplaceTempView("test")
```

```sql
%sql select id, squaredWithPython(id) as id_squared from test
```

---

## <a id="dataframes">4. UDF mit DataFrames verwenden</a>

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import LongType
squared_udf = udf(squared, LongType())
df = spark.table("test")
display(df.select("id", squared_udf("id").alias("id_squared")))
```

Als Dekorator:

```python
from pyspark.sql.functions import udf

@udf("long")
def squared_udf(s):
  return s * s
df = spark.table("test")
display(df.select("id", squared_udf("id").alias("id_squared")))
```

---

## <a id="variant">5. Variant-Typen mit UDFs</a>

Rückgabe eines `Variant`:

```python
from pyspark.sql.types import VariantType

# Return Variant
@udf(returnType = VariantType())
def toVariant(jsonString):
  return VariantVal.parseJson(jsonString)

spark.range(1).select(lit('{"a" : 1}').alias("json")).select(toVariant(col("json"))).display()
```

```text
+---------------+
|toVariant(json)|
+---------------+
|        {"a":1}|
+---------------+
```

Rückgabe eines `Struct<Variant>`:

```python
# Return Struct<Variant>
@udf(returnType = StructType([StructField("v", VariantType(), True)]))
def toStructVariant(jsonString):
  return {"v": VariantVal.parseJson(jsonString)}

spark.range(1).select(lit('{"a" : 1}').alias("json")).select(toStructVariant(col("json"))).display()
```

```text
+---------------------+
|toStructVariant(json)|
+---------------------+
|        {"v":{"a":1}}|
+---------------------+
```

Rückgabe eines `Array<Variant>`:

```python
# Return Array<Variant>
@udf(returnType = ArrayType(VariantType()))
def toArrayVariant(jsonString):
  return [VariantVal.parseJson(jsonString)]

spark.range(1).select(lit('{"a" : 1}').alias("json")).select(toArrayVariant(col("json"))).display()
```

```text
+--------------------+
|toArrayVariant(json)|
+--------------------+
|           [{"a":1}]|
+--------------------+
```

Rückgabe eines `Map<String, Variant>`:

```python
# Return Map<String, Variant>
@udf(returnType = MapType(StringType(), VariantType(), True))
def toArrayVariant(jsonString):
  return {"v1": VariantVal.parseJson(jsonString), "v2": VariantVal.parseJson("[" + jsonString + "]")}

spark.range(1).select(lit('{"a" : 1}').alias("json")).select(toArrayVariant(col("json"))).display()
```

```text
+-----------------------------+
|         toArrayVariant(json)|
+-----------------------------+
|{"v2":[{"a":1}],"v1":{"a":1}}|
+-----------------------------+
```

---

## <a id="files">6. Dateien mit UDF (Beta)</a>

Dieses Feature ist im **Beta**-Status. Workspace-Admins können den Zugriff über die Previews-Seite steuern.

Der PySpark-Typ für eine Datei ist `FileType`. Er kann als Parameter- oder Rückgabetyp einer UDF verwendet werden, sowohl als Top-Level-Typ als auch verschachtelt.

Um den Inhalt einer Datei innerhalb einer UDF zu lesen: `file.as_local_file()` liefert einen lokalen Pfad zum Öffnen, `file.open()` liefert einen Byte-Stream zum Lesen. Für Beispiele in Python, Scala und SQL — einschließlich Bildverarbeitung, Dateityp-Erkennung und Video-Frame-Extraktion — siehe "Process files with UDFs" in der offiziellen Doku.

---

## <a id="null-checking">7. Auswertungsreihenfolge und Null-Prüfung</a>

Spark SQL garantiert nicht, in welcher Reihenfolge Subexpressions ausgewertet werden:

```python
spark.udf.register("strlen", lambda s: len(s), "int")
spark.sql("select s from test1 where s is not null and strlen(s) > 1") # no guarantee
```

Zwei Lösungswege:

- Die UDF selbst null-aware machen und Null-Prüfung innerhalb der UDF durchführen.
- `IF`- oder `CASE WHEN`-Ausdrücke verwenden, um die Null-Prüfung durchzuführen und die UDF in einem bedingten Zweig aufzurufen.

```python
spark.udf.register("strlen_nullsafe", lambda s: len(s) if not s is None else -1, "int")
spark.sql("select s from test1 where s is not null and strlen_nullsafe(s) > 1") // ok
spark.sql("select s from test1 where if(s is not null, strlen(s), null) > 1")   // ok
```

---

## <a id="credentials">8. Service Credentials in Scalar Python UDFs</a>

```python
@udf
def use_service_credential():
    from databricks.service_credentials import getServiceCredentialsProvider
    import boto3

    # Assuming there is a service credential named 'testcred' set up in Unity Catalog
    boto3_session = boto3.Session(botocore_session=getServiceCredentialsProvider('testcred'))
    # Use the S3 session to perform operations
```

### Service-Credentials-Berechtigungen

Analog zu Batch-Unity-Catalog-Python-UDFs: der Ersteller der UDF benötigt `ACCESS`-Berechtigung auf dem Service Credential (siehe [Batch Python UDFs — Service Credentials](../01%20Unity%20Catalog%20UDFs/03%20Batch%20Python%20UDFs%20%28Unity%20Catalog%29.md#credentials)).

### Default Credentials

```python
@udf
def use_service_credential():
    from databricks.service_credentials import getServiceCredentialsProvider
    import boto3

    # The default service credential for the compute is automatically used
    boto3_session = boto3.Session()
    # Use the S3 client to perform operations
```

### Service-Credential-Beispiel — AWS-Lambda-Funktion

Ruft mit dem Default-Credential eine boto3-Session ab, baut eine boto3-Session auf und ruft eine Lambda-Funktion zur Verarbeitung eines Eingabe-Strings auf:

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

@udf(StringType())
def call_lambda_udf(input_str):
    import boto3
    import json
    import base64
    from databricks.service_credentials import getServiceCredentialsProvider
    from pyspark.taskcontext import TaskContext

    # Create a session using the default Unity Catalog service credential
    session = boto3.Session()
    client = session.client("lambda", region_name="us-west-2")

    # Optionally attach Spark TaskContext metadata to the Lambda request
    user_ctx = {"custom": {"user": TaskContext.get().getLocalProperty("user")}}

    # Build the Lambda payload
    payload = json.dumps({
        "values": [input_str],
        "is_debug": False
    })

    # Encode context for Lambda's client context
    encoded_ctx = base64.b64encode(json.dumps(user_ctx).encode("utf-8")).decode("utf-8")

    # Call the Lambda function
    response = client.invoke(
        FunctionName="HashValuesFunction",
        InvocationType="RequestResponse",
        ClientContext=encoded_ctx,
        Payload=payload,
    )

    response_payload = json.loads(response["Payload"].read().decode("utf-8"))

    if "errorMessage" in response_payload:
        raise Exception(response_payload["errorMessage"])

    return response_payload["values"][0]
```

---

## <a id="task-context">9. Task-Ausführungskontext abrufen</a>

Über die `TaskContext`-PySpark-API lassen sich Kontextinformationen wie die Identität des Nutzers, Cluster-Tags, die Spark-Job-ID u. a. abrufen. Siehe [UDF Task Context.md](../03%20UDF%20Task%20Context.md).

---

## <a id="limitierungen">10. Limitierungen</a>

- **Instance Profiles:** PySpark-UDFs auf Clustern mit Standard Access Mode und auf serverlosem Compute unterstützen keine Instance Profiles.

---

## <a id="quellen">11. Quellen</a>

- Python scalar user-defined functions (UDFs): https://docs.databricks.com/aws/en/udf/python

**Stand:** 2026-08-22.
