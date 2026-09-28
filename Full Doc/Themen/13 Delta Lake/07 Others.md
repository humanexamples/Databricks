# Sonstiges — Python-Referenz (Delta Lake)

## Abschnittsübersicht
1. [Zweck](#zweck)
2. [`configure_spark_with_delta_pip()`](#configure)
3. [Bezug zu Databricks-Notebooks](#databricks-bezug)
4. [Quellen](#quellen)

## <a id="zweck">1. Zweck</a>
Das Modul `delta.pip_utils` enthält genau eine Hilfsfunktion, `configure_spark_with_delta_pip()`. Sie richtet sich an alle, die Delta Lake lokal bzw. außerhalb von Databricks per `pip install delta-spark` nutzen: Sie konfiguriert einen `SparkSession.Builder` so, dass Spark die passenden Delta-Lake-JARs automatisch von Maven nachlädt, statt sie manuell über `--packages` angeben zu müssen.

## <a id="configure">2. `configure_spark_with_delta_pip()`</a>
- Nimmt einen bereits vorbereiteten `SparkSession.Builder` entgegen, ergänzt ihn um die korrekten Delta-Lake-Paketkoordinaten (und optional weitere Pakete) und gibt den erweiterten `Builder` zurück, auf dem anschließend `.getOrCreate()` aufgerufen wird.
- Parameter:
  - `spark_session_builder` — der `SparkSession.Builder`, üblicherweise `SparkSession.builder...` mit bereits gesetzten `.appName()`/`.config()`-Aufrufen.
  - `extra_packages` (optional, `List[str] | None`, Default `None`) — zusätzliche Maven-Koordinaten (z. B. für Kafka-Connectoren), die neben den Delta-Lake-Paketen mit eingebunden werden sollen.
- Rückgabewert: der angereicherte `SparkSession.Builder` (noch keine fertige `SparkSession` — dafür ist weiterhin `.getOrCreate()` nötig).
- Seit Version 1.0, Status "Evolving".

Einfaches Beispiel (laut Doku):
```python
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

builder = SparkSession.builder.master("local[*]").appName("test")
spark = configure_spark_with_delta_pip(builder).getOrCreate()
```

Übliches Muster in Kombination mit den Delta-SQL-Extensions und der Catalog-Konfiguration (diese `.config(...)`-Aufrufe stammen aus dem allgemeinen Delta-Lake-Quickstart-Setup, nicht wörtlich aus dem `pip_utils`-Referenzabschnitt selbst — dort sind nur die beiden untenstehenden Kern-Beispiele dokumentiert):
```python
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

builder = (SparkSession.builder
    .appName("MeineLokaleDeltaApp")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"))

spark = configure_spark_with_delta_pip(builder).getOrCreate()
```

Mit zusätzlichen Fremdpaketen (laut Doku):
```python
from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip

builder = SparkSession.builder.appName("test")
meine_pakete = ["org.apache.spark:spark-sql-kafka-0-10_2.12:x.y.z"]
spark = configure_spark_with_delta_pip(builder, extra_packages=meine_pakete).getOrCreate()
```

## <a id="databricks-bezug">3. Bezug zu Databricks-Notebooks</a>
- `configure_spark_with_delta_pip()` wird in Databricks-Notebooks und Lakeflow-Pipelines nicht benötigt und dort auch nicht verwendet: Die Databricks Runtime bringt Delta Lake bereits vollständig vorkonfiguriert mit (passende JARs, SQL-Extensions und Catalog sind bereits gesetzt).
- Das global bereitgestellte `spark`-Objekt in einem Databricks-Notebook wird beim Notebook-Start automatisch von der Runtime erzeugt und bereitgestellt — man muss dort keine `SparkSession` selbst bauen.
- Außerhalb von Databricks (lokale Entwicklung, eigener Cluster, CI-Pipeline mit `pip install delta-spark`) gibt es dieses automatische Setup nicht: Dort ist `configure_spark_with_delta_pip(builder).getOrCreate()` der Äquivalenzschritt, mit dem man sich selbst eine Delta-fähige `SparkSession` erzeugt.

## <a id="quellen">4. Quellen</a>
- `delta.pip_utils` — vollständige Modulreferenz: https://docs.delta.io/api/latest/python/spark/

**Stand:** 2026-09-21.
