# Metaprogrammierung mit Python

## Abschnittsübersicht

1. [Grundkonzept](#grundkonzept)
2. [Vollständiges Beispiel: Fire-Department-Pipeline](#beispiel)
3. [Warum das funktioniert](#warum)
4. [Quellen](#quellen)

---

## <a id="grundkonzept">1. Grundkonzept</a>

Metaprogrammierung in Lakeflow-Pipelines nutzt innere Python-Funktionen (*"Metaprogramming in Lakeflow pipelines uses Python inner functions"*). Da diese Funktionen von der Pipeline-Laufzeit lazy (verzögert) ausgewertet werden, lässt sich ein `@dp.table`-Dekorator innerhalb einer Factory-Funktion verschachteln (*"you can wrap `@dp.table` decorators inside a factory function"*) und die Factory-Funktion anschließend mehrfach mit unterschiedlichen Parametern aufrufen — so entstehen mehrere gleichartige Flows/Tabellen, ohne Code zu duplizieren.

---

## <a id="beispiel">2. Vollständiges Beispiel: Fire-Department-Pipeline</a>

Das Doku-Tutorial demonstriert das Muster anhand einer Pipeline, die Einsatzdaten der Feuerwehr nach Einsatztyp aufteilt (Alarms, Structure Fire, Medical Incident) und für jeden Typ eigene Tabellen erzeugt:

```python
import functools
from pyspark import pipelines as dp
from pyspark.sql.functions import *

@dp.table(
  name="raw_fire_department",
  comment="raw table for fire department response")
@dp.expect_or_drop("valid_received", "received IS NOT NULL")
@dp.expect_or_drop("valid_response", "responded IS NOT NULL")
@dp.expect_or_drop("valid_neighborhood", "neighborhood != 'None'")
def get_raw_fire_department():
  return (
    spark.read.format('csv')
      .option('header', 'true')
      .option('multiline', 'true')
      .load('/databricks-datasets/timeseries/Fires/Fire_Department_Calls_for_Service.csv')
      .withColumnRenamed('Call Type', 'call_type')
      .withColumnRenamed('Received DtTm', 'received')
      .withColumnRenamed('Response DtTm', 'responded')
      .withColumnRenamed('Neighborhooods - Analysis Boundaries', 'neighborhood')
      .select('call_type', 'received', 'responded', 'neighborhood')
  )

all_tables = []
def generate_tables(call_table, response_table, filter):
  @dp.table(
    name=call_table,
    comment="top level tables by call type"
  )
  def create_call_table():
    return spark.sql("""
      SELECT
        unix_timestamp(received,'M/d/yyyy h:m:s a') as ts_received,
        unix_timestamp(responded,'M/d/yyyy h:m:s a') as ts_responded,
        neighborhood
      FROM raw_fire_department
      WHERE call_type = '{filter}'
    """.format(filter=filter))
  @dp.table(
    name=response_table,
    comment="top 10 neighborhoods with fastest response time"
  )
  def create_response_table():
    return spark.sql("""
      SELECT
        neighborhood,
        AVG((ts_received - ts_responded)) as response_time
      FROM {call_table}
      GROUP BY 1
      ORDER BY response_time
      LIMIT 10
    """.format(call_table=call_table))
  all_tables.append(response_table)

generate_tables("alarms_table", "alarms_response", "Alarms")
generate_tables("fire_table", "fire_response", "Structure Fire")
generate_tables("medical_table", "medical_response", "Medical Incident")

@dp.table(
  name="best_neighborhoods",
  comment="which neighbor appears in the best response time list the most")
def summary():
  target_tables = [dp.read(t) for t in all_tables]
  unioned = functools.reduce(lambda x, y: x.union(y), target_tables)
  return (
    unioned.groupBy(col("neighborhood"))
      .agg(count("*").alias("score"))
      .orderBy(desc("score"))
  )
```

---

## <a id="warum">3. Warum das funktioniert</a>

Die Doku fasst das Muster so zusammen: *"a single factory function generates all of them"* — eine einzige Factory-Funktion (`generate_tables`) erzeugt alle drei Paare aus Call- und Response-Tabelle. Zentral dafür:

- **Innere Funktionen werden lazy registriert:** Der Dekorator führt die Funktion nicht sofort aus, sondern registriert sie bei der Pipeline-Laufzeit.
- **Closures fangen Parameter ein:** Jeder Aufruf von `generate_tables(...)` kapselt seine eigenen, isolierten Parameterwerte (`call_table`, `response_table`, `filter`) — anders als bei der in [Python-Entwicklung.md](Python-Entwicklung.md) Abschnitt 5 beschriebenen Closure-Falle in `for`-Schleifen, da hier jeder Aufruf einen eigenen Funktionsbereich (Scope) der äußeren Funktion `generate_tables` erhält.
- **Reduziert Redundanz:** Erspart nahezu identische Tabellendefinitionen für jeden Call-Typ.

Die abschließende Tabelle `best_neighborhoods` liest alle in `all_tables` gesammelten Response-Tabellen über `dp.read(t)`, vereinigt sie per `functools.reduce` mit `union`, und ermittelt so, welches Neighborhood am häufigsten in den "schnellste Reaktionszeit"-Listen der drei Call-Typen erscheint.

---

## <a id="quellen">4. Quellen</a>

- Tutorial: Create multiple flows with different parameters (Grundkonzept, vollständiges Fire-Department-Beispiel): https://docs.databricks.com/aws/en/ldp/developer/ldp-metaprogramming

**Stand:** 2026-08-19.
