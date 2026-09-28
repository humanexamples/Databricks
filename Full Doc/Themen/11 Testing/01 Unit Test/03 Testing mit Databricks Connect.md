# Testing mit Databricks Connect

Lokales Testen von PySpark-Code mit pytest über Databricks Connect (Databricks Runtime 13.3 LTS+) — Code läuft lokal, die SparkSession verbindet sich mit einem Remote-Cluster. Teil der [Testing](../Uebersicht.md)-Reihe.

## Abschnittsübersicht

1. [Überblick](#ueberblick)
2. [Wichtige Voraussetzungen](#voraussetzungen)
3. [Beispiel-Projektstruktur](#projektstruktur)
4. [Ausführung](#ausfuehrung)
5. [Quelle](#quelle)

---

## <a id="ueberblick">1. Überblick</a>

Testverfahren für Databricks Connect mit Databricks Runtime 13.3 LTS und höher, unter Nutzung des `pytest`-Frameworks.

## <a id="voraussetzungen">2. Wichtige Voraussetzungen</a>

**Wichtiger Kompatibilitätshinweis:** „Databricks Connect und PySpark schließen sich gegenseitig aus." Diese dürfen in der Entwicklungsumgebung nicht in Konflikt stehen.

**Konfigurationsanforderung:** Beim Ausführen von Tests über das Terminal „funktioniert pytest nur mit dem `DEFAULT`-Konfigurationsprofil." Dieses Profil muss die Compute-Ressource angeben — entweder einen Cluster oder Serverless Compute.

## <a id="projektstruktur">3. Beispiel-Projektstruktur</a>

### Datei 1: `nyctaxi_functions.py`

```python
from databricks.connect import DatabricksSession
from pyspark.sql import DataFrame, SparkSession

def get_spark() -> SparkSession:
  spark = DatabricksSession.builder.getOrCreate()
  return spark

def get_nyctaxi_trips() -> DataFrame:
  spark = get_spark()
  df = spark.read.table("samples.nyctaxi.trips")
  return df
```

`get_spark()` instanziiert eine `SparkSession` über Databricks Connect; `get_nyctaxi_trips()` liest eine Tabelle aus dem `samples`-Catalog.

### Datei 2: `main.py`

```python
from nyctaxi_functions import *

df = get_nyctaxi_trips()
df.show(5)
```

### Datei 3: `test_nyctaxi_functions.py`

```python
import pyspark.sql.connect.session
from nyctaxi_functions import *

def test_get_spark():
  spark = get_spark()
  assert isinstance(spark, pyspark.sql.connect.session.SparkSession)

def test_get_nyctaxi_trips():
  df = get_nyctaxi_trips()
  assert df.count() > 0
```

Der erste Test prüft, dass `get_spark()` eine korrekte `SparkSession`-Instanz zurückgibt. Der zweite Test bestätigt, dass `get_nyctaxi_trips()` Daten abruft, indem geprüft wird, dass der DataFrame mindestens eine Zeile enthält.

## <a id="ausfuehrung">4. Ausführung</a>

`pytest` vom Projekt-Root aus ausführen:

```
$ pytest
=================== test session starts ====================
platform darwin -- Python 3.11.7, pytest-8.1.1, pluggy-1.4.0
rootdir: <project-rootdir>
collected 2 items
test_nyctaxi_functions.py .. [100%]
======================== 2 passed ==========================
```

## <a id="quelle">5. Quelle</a>

- https://docs.databricks.com/aws/en/dev-tools/databricks-connect/python/testing

**Stand:** 2026-08-21.
