# Was sind User-Defined Functions (UDFs)?

User-Defined Functions (UDFs) erlauben es, Code wiederzuverwenden und zu teilen, der die eingebauten Fähigkeiten von Databricks erweitert. UDFs eignen sich für spezifische Aufgaben wie komplexe Berechnungen, Transformationen oder benutzerdefinierte Datenmanipulationen.

## Abschnittsübersicht

1. [Wann eine UDF statt einer Apache-Spark-Funktion?](#wann-udf)
2. [UDF-Typen im Überblick](#udf-typen)
3. [Struktur dieses Ordners](#struktur)
4. [Quellen](#quellen)

---

## <a id="wann-udf">1. Wann eine UDF statt einer Apache-Spark-Funktion?</a>

UDFs eignen sich für Logik, die sich mit eingebauten Apache-Spark-Funktionen nur schwer ausdrücken lässt. Eingebaute Apache-Spark-Funktionen sind für verteilte Verarbeitung optimiert und bieten bessere Performance im großen Maßstab.

Databricks empfiehlt UDFs für Ad-hoc-Queries, manuelle Datenbereinigung, explorative Datenanalyse und Operationen auf kleinen bis mittelgroßen Datensätzen. Typische Anwendungsfälle für UDFs sind Datenverschlüsselung, -entschlüsselung, Hashing, JSON-Parsing und Validierung.

Für Operationen auf großen Datensätzen und für regelmäßig oder kontinuierlich laufende Workloads — einschließlich ETL-Jobs und Streaming-Operationen — sollten Apache-Spark-Methoden verwendet werden.

---

## <a id="udf-typen">2. UDF-Typen im Überblick</a>

Die offizielle Übersichtsseite unterscheidet fünf UDF-Kategorien:

### Scalar UDFs

Verarbeiten eine einzelne Zeile und liefern pro Zeile genau einen Ergebniswert. Sie können Unity-Catalog-governed oder session-scoped sein.

Beispiel: Länge jedes Namens in einer `name`-Spalte berechnen und das Ergebnis in einer neuen Spalte `name_length` ablegen.

```sql
-- SQL-UDF für die Namenslänge erstellen
CREATE OR REPLACE FUNCTION main.test.get_name_length(name STRING)
RETURNS INT
RETURN LENGTH(name);

-- Die UDF in einer SQL-Query verwenden
SELECT name, main.test.get_name_length(name) AS name_length
FROM your_table;
```

Äquivalente Implementierung in einem Databricks-Notebook mit PySpark:

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

@udf(returnType=IntegerType())
def get_name_length(name):
  return len(name)

df = df.withColumn("name_length", get_name_length(df.name))

# Ergebnis anzeigen
display(df)
```

Siehe [SQL und Python UDFs in Unity Catalog](01%20Unity%20Catalog%20UDFs/01%20SQL%20und%20Python%20UDFs%20%28Unity%20Catalog%29.md) und [Python Scalar UDFs](02%20Session-scoped%20UDFs/01%20Python%20Scalar%20UDFs.md).

### Batch Scalar UDFs

Verarbeiten Daten in Batches bei gleichzeitig gewahrter 1:1-Input/Output-Zeilenparität. Das reduziert den Overhead zeilenweiser Operationen bei großskaliger Datenverarbeitung. Batch-UDFs können außerdem Zustand zwischen Batches halten, um effizienter zu arbeiten, Ressourcen wiederzuverwenden und komplexe Berechnungen durchzuführen, die Kontext über mehrere Datenblöcke hinweg benötigen. Sie können Unity-Catalog-governed oder session-scoped sein.

Die folgende Batch-Unity-Catalog-Python-UDF berechnet den BMI während der Verarbeitung von Zeilen-Batches:

```sql
CREATE OR REPLACE FUNCTION main.test.calculate_bmi_pandas(weight_kg DOUBLE, height_m DOUBLE)
RETURNS DOUBLE
LANGUAGE PYTHON
PARAMETER STYLE PANDAS
HANDLER 'handler_function'
AS $$
import pandas as pd
from typing import Iterator, Tuple

def handler_function(batch_iter: Iterator[Tuple[pd.Series, pd.Series]]) -> Iterator[pd.Series]:
  for weight_series, height_series in batch_iter:
    yield weight_series / (height_series ** 2)
$$;

select main.test.calculate_bmi_pandas(cast(70 as double), cast(1.8 as double));
```

Siehe [SQL und Python UDFs in Unity Catalog](01%20Unity%20Catalog%20UDFs/01%20SQL%20und%20Python%20UDFs%20%28Unity%20Catalog%29.md) und [Batch Python UDFs (Unity Catalog)](01%20Unity%20Catalog%20UDFs/03%20Batch%20Python%20UDFs%20%28Unity%20Catalog%29.md).

### Non-Scalar UDFs

Operieren auf ganzen Datensätzen/Spalten mit flexiblem Input/Output-Verhältnis (1:N oder many:many). Session-scoped Batch-Pandas-UDFs können folgende Muster annehmen:

- Series to Series
- Iterator of Series to Iterator of Series
- Iterator of multiple Series to Iterator of Series
- Series to scalar

Beispiel für eine Series-to-Series-Pandas-UDF:

```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

df = spark.createDataFrame([(70, 1.75), (80, 1.80), (60, 1.65)], ["Weight", "Height"])

@pandas_udf("double")
def calculate_bmi_pandas(weight: pd.Series, height: pd.Series) -> pd.Series:
    return weight / (height ** 2)

df.withColumn("BMI", calculate_bmi_pandas(df["Weight"], df["Height"])).display()
```

Siehe [Pandas UDFs](02%20Session-scoped%20UDFs/02%20Pandas%20UDFs.md).

### UDAF (User-Defined Aggregate Function)

Aggregatfunktionen, die mehrere Zeilen zu einem Ergebnis zusammenfassen (z. B. innerhalb eines `GROUP BY`). Siehe [Scala UDAFs](02%20Session-scoped%20UDFs/05%20Scala%20UDAFs.md).

### UDTFs (User-Defined Table Functions)

Geben statt eines skalaren Werts eine ganze Ergebnistabelle zurück. Siehe [Python UDTFs](02%20Session-scoped%20UDFs/03%20Python%20UDTFs.md) und [Python UDTFs (Unity Catalog)](01%20Unity%20Catalog%20UDFs/04%20Python%20UDTFs%20%28Unity%20Catalog%29.md).

---

## <a id="struktur">3. Struktur dieses Ordners</a>

Dieser Ordner spiegelt die offizielle Databricks-Dokumentation unter `docs.databricks.com/aws/en/udf/` und ist in drei Bereiche gegliedert:

- **[01 Unity Catalog UDFs](01%20Unity%20Catalog%20UDFs/)** — UDFs/UDTFs, die als governed Objekte in Unity Catalog registriert werden (SQL/Python, Scala/Java, Batch-Python, Python-UDTFs). Diese sind katalogweit auffindbar, teilbar und über Unity-Catalog-Privilegien steuerbar.
- **[02 Session-scoped UDFs](02%20Session-scoped%20UDFs/)** — UDFs, die über die PySpark-/Scala-API direkt in einer Notebook-/Job-Session registriert werden (`spark.udf.register`, `@udf`, `@pandas_udf`, `@udtf`, `UserDefinedAggregateFunction`). Diese sind nicht katalogweit governed, sondern an die aktuelle `SparkSession` gebunden.
- **[03 UDF Task Context.md](03%20UDF%20Task%20Context.md)** — themenübergreifende Referenz zur `TaskContext`-PySpark-API, die sowohl für Batch-Unity-Catalog-Python-UDFs als auch für PySpark-UDFs gilt.

---

## <a id="quellen">4. Quellen</a>

- What are user-defined functions (UDFs)?: https://docs.databricks.com/aws/en/udf/

**Stand:** 2026-08-22.
