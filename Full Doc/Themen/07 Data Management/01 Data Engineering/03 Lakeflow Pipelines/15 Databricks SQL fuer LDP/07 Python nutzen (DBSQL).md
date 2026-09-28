# Python für Standalone Pipelines nutzen (Databricks SQL)

Dieses Dokument beschreibt, wie Standalone Materialized Views und Streaming Tables aus einem Python-Notebook heraus erstellt und verwaltet werden — im Unterschied zur dekorator-basierten Python-API (`pyspark.pipelines`) vollständiger Lakeflow-Pipelines.

## Abschnittsübersicht

1. [Grundkonzept](#grundkonzept)
2. [Voraussetzungen](#voraussetzungen)
3. [Materialized View erstellen](#mv-erstellen)
4. [Streaming Table erstellen](#st-erstellen)
5. [Refreshen](#refreshen)
6. [Parametrisierte Anweisungen](#parametrisiert)
7. [Einschränkungen](#einschraenkungen)
8. [Quellen](#quellen)

---

## <a id="grundkonzept">1. Grundkonzept</a>

Standalone Materialized Views und Streaming Tables lassen sich aus einem Python-Notebook heraus erstellen und refreshen, indem `spark.sql()`-Aufrufe mit den bekannten SQL-DDL-Anweisungen genutzt werden ("create and refresh standalone materialized views and streaming tables from a notebook using Python"). Dies unterscheidet sich von der Python-API vollständiger Lakeflow-Pipelines, die über Dekoratoren aus `pyspark.pipelines` (`@dp.table`, `@dp.materialized_view` usw.) arbeitet (siehe Best-Practices-Dateien in "16 Best Practices/").

## <a id="voraussetzungen">2. Voraussetzungen</a>

- Ein Notebook, das an Serverless General Compute angehängt ist
- **Databricks Runtime 18.1 oder höher**
- Das Feature befindet sich im Beta-Status mit regionalen Verfügbarkeitseinschränkungen

## <a id="mv-erstellen">3. Materialized View erstellen</a>

```python
spark.sql("""
  CREATE OR REPLACE MATERIALIZED VIEW mv1
  AS SELECT
    date,
    sum(sales) AS sum_of_sales
  FROM base_table1
  GROUP BY date
""")
```

## <a id="st-erstellen">4. Streaming Table erstellen</a>

```python
spark.sql("""
  CREATE OR REFRESH STREAMING TABLE sales
  AS SELECT product, price FROM STREAM raw_data
""")
```

## <a id="refreshen">5. Refreshen</a>

```python
spark.sql("REFRESH MATERIALIZED VIEW mv1")
spark.sql("REFRESH STREAMING TABLE sales")
```

Die Doku merkt an, dass Refreshes auf Serverless General Compute synchron ablaufen.

## <a id="parametrisiert">6. Parametrisierte Anweisungen</a>

Named Parameter Marker (z. B. `:parameter_name`), übergeben über das `args`-Argument von `spark.sql()`, ermöglichen parametrisierte Statements. Für Objektnamen (z. B. Tabellen-/View-Namen) ist der `IDENTIFIER()`-Wrapper erforderlich:

```python
mv_name = "main.sales.regional_sales"
min_sales = 1000
spark.sql("""
  CREATE OR REPLACE MATERIALIZED VIEW IDENTIFIER(:mv)
  AS SELECT
    region,
    sum(sales) AS sum_of_sales
  FROM base_table1
  WHERE sales > :min_sales
  GROUP BY region
""", args={
  "mv": mv_name,
  "min_sales": min_sales,
})
```

## <a id="einschraenkungen">7. Einschränkungen</a>

- Asynchrone Refreshes werden auf Serverless General Compute nicht unterstützt.
- Keine Kostenzuordnung pro Tabelle ("Per-table cost attribution is unavailable").
- Benutzerdefinierte Warehouse-Tags werden nicht an diese Pipelines weitergegeben.

Diese Einschränkungen decken sich mit den in "Compute.md", Abschnitt 4 ("Notebook (Beta)") aufgeführten Punkten.

---

## <a id="quellen">8. Quellen</a>

1. Use Python with standalone pipelines (AWS): https://docs.databricks.com/aws/en/ldp/dbsql/using-python
