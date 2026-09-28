# Schema Evolution, CDC-Grundbegriffe, Join und Aggregation

## Schema Evolution

Anpassung an strukturelle Änderungen über die Zeit: neue Spalten, umbenannte/entfernte Felder, Type Widening (z. B. `INT` → `DOUBLE`), andere Typumwandlungen. Vier unabhängige Kategorien: **Connectors**, **Format-Parser**, **Engines**, **Datasets**.

| Kategorie | Unterstützung |
|---|---|
| Auto Loader | Spaltenänderungen + Type Widening über `cloudFiles.schemaEvolutionMode`; neue Spalten/Umbenennungen erfordern manuellen Neustart |
| Delta-Connector | neue Spalten via `mergeSchema` automatisch; Umbenennen/Löschen mit bestimmten Spark-Configs |
| SaaS-/CDC-Connectors | Neustart bei Schemaänderungen automatisch; Typänderungen erfordern vollständigen Refresh |
| Kafka/Kinesis/Pub/Sub/Pulsar | keine native Unterstützung — delegiert an Format-Parser |
| `from_json` | keine native Unterstützung; automatische Evolution in Lakeflow-Pipelines |
| `from_avro`/`from_protobuf` | über Confluent Schema Registry |
| `from_csv`/`from_xml` | keine Unterstützung |
| Streaming-Tabellen | Merge-Schema-Evolution standardmäßig aktiv; Type Widening explizit aktivieren |
| Materialisierte Views | jede Schemaänderung löst vollständige Neuberechnung aus |
| Delta-Tabellen | Merge-Schema, Column Mapping, Type Widening; andere Typänderungen erfordern Neuschreiben (`overwriteSchema`) |
| Views | Modus `SCHEMA EVOLUTION` für automatische Anpassung ohne explizite Spaltenliste |

Relevante Optionen: `cloudFiles.schemaEvolutionMode`, `rescuedDataColumn`, `schemaHints`, `addNewColumnsWithTypeWidening`, `mergeSchema`, `spark.databricks.delta.streaming.allowSourceColumnRename`, `spark.databricks.delta.streaming.allowSourceColumnDrop`, `delta.enableTypeWidening`, `schemaLocationKey`, `spark.databricks.delta.schema.autoMerge.enabled`, `avroSchemaEvolutionMode`, `overwriteSchema`, `SCHEMA EVOLUTION`, `SCHEMA TYPE EVOLUTION`.

### Beispiel: Kafka-zu-Delta-Ingestion mit Avro-Schema-Evolution

```python
from pyspark.sql.functions import col
from pyspark.sql.avro.functions import from_avro

reader = (spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers", BOOTSTRAP)
  .option("subscribe", TOPIC)
  .option("startingOffsets", "earliest"))

raw_df = reader.load()

decoded = from_avro(
    data=col("value"),
    jsonFormatSchema=None,
    subject=f"{TOPIC}-value",
    schemaRegistryAddress=SCHEMA_REG,
    options={
      "confluent.schema.registry.basic.auth.credentials.source": "USER_INFO",
      "confluent.schema.registry.basic.auth.user.info": f"{SR_USER}:{SR_PASS}",
      "avroSchemaEvolutionMode": "restart",
      "mode": "FAILFAST"
    }).alias("payload")

bronze_df = raw_df.select(decoded, "timestamp").select("payload.*", "timestamp")

(bronze_df.writeStream
  .format("delta")
  .option("checkpointLocation", CHECKPOINT)
  .option("ignoreChanges", "true")
  .outputMode("append")
  .option("mergeSchema", "true")
  .trigger(availableNow=True)
  .toTable(BRONZE_TABLE))
```

## Change Data Capture (CDC) — Grundbegriffe

CDC erfasst nur Änderungen an Quellsystemen, statt jedes Mal den Gesamtdatensatz zu verarbeiten (ändert sich 1 Zeile einer 50-zeiligen Tabelle, enthält der CDC-Feed nur diesen `UPDATE`).

- **SCD Typ 1** (nur aktueller Stand): überschreibt alte Daten. Ideal für inkrementelle Materialized-View-Updates ohne volle Neuberechnung.
- **SCD Typ 2** (Historie): Zeitstempel-Metadaten `__START_AT`/`__END_AT`; aktive Datensätze haben `__END_AT = NULL`. Für Auditierbarkeit, Regulatorik, Stichtagsberichte.
- **AUTO CDC**: verarbeitet Change-Feeds aus CDC-fähigen relationalen DBs oder Delta-Tabellen mit Change Data Feed; behandelt außer der Reihe eintreffende Datensätze automatisch über monoton steigende Sequenzierungsspalten.
- **AUTO CDC FROM SNAPSHOT**: für Quellen ohne CDC — vergleicht aufeinanderfolgende Snapshots, erzeugt einen synthetischen Change-Feed, gleiche SCD-Logik wie AUTO CDC.
- Vorteile: geringeres Verarbeitungsvolumen; Rekonstruktion von Datensätzen zu Zeitpunkten (Audit/Trend); stabile Surrogatschlüssel für Joins.

## Joins

ANSI-Standard-Join-Syntax, unterschiedliche Join-Arten je Verarbeitungsmodus.

**Batch-Joins** — zustandslos, sofortiges Ergebnis:

```sql
-- Inner Join: nur Zeilen mit Treffer auf beiden Seiten
SELECT id, name, employee.deptno, deptname
FROM employee
INNER JOIN department ON employee.deptno = department.deptno;

-- Semi Join: nur Spalten aus employee, nur Zeilen mit Treffer in department
SELECT * FROM employee
SEMI JOIN department ON employee.deptno = department.deptno;

-- Anti Join: nur Zeilen aus employee OHNE Treffer in department
SELECT * FROM employee
ANTI JOIN department ON employee.deptno = department.deptno;

-- Cross Join: kartesisches Produkt (keine ON-Bedingung)
SELECT id, name, employee.deptno, deptname
FROM employee
CROSS JOIN department;
```

- **Stream-Stream-Joins:** zustandsbehaftet, Ergebnisse werden iterativ aktualisiert. Unterstützt: Inner, Left/Right/Full Outer, Left-Semi. Watermarks für beide Seiten empfohlen.
- **Stream-Static-Joins:** zustandslos, verbinden jeweils aktuellste Delta-Tabellen-Version mit einem Stream. Achtung: ändert sich die statische Tabelle zwischen Läufen, kann erneute Verarbeitung derselben Streaming-Daten zu unterschiedlichen Ergebnissen führen.

```python
checkpoint_path = f"/Volumes/{catalog}/{schema}/checkpoints/bookings_with_user_info"
streamingDF = spark.readStream.table("samples.wanderbricks.bookings")
staticDF = spark.read.table("samples.wanderbricks.users")
query = (streamingDF.join(staticDF, "user_id", "inner")
  .writeStream.option("checkpointLocation", checkpoint_path)
  .trigger(availableNow=True).table(f"{catalog}.{schema}.bookings_with_user_info"))
```

- Skew-Joins werden automatisch optimiert. Range-Join-Hints verbessern Ungleichheits-Joins (z. B. Timestamps, Clustering-IDs).

## Aggregation

Vier Ansätze:

- **Batch-Aggregate:** Standard für Ad-hoc-SQL/DataFrame-Verarbeitung; Latenz/Kosten steigen mit Datenmenge — bei häufiger Nutzung materialisierte Views einsetzen.
- **Stateful Aggregates:** für Streaming-Workloads; **Watermarks zwingend** — ohne sie wächst der Zustand unbegrenzt (Performance-/Speicherprobleme).
- **Inkrementelle Aggregate:** Materialisierte Views überwachen Quelländerungen und wenden beim Refresh nur nötige Updates an — Ergebnis entspricht einer vollständigen Batch-Neuberechnung.
- **Approximate Aggregates:** `approx_count_distinct`, `approx_percentile`, `approx_top_k`; zusätzlich `TABLESAMPLE` für Stichproben.
- Data Profiling nutzt aggregierte Statistiken für Qualitätstrends/Anomalie-Alarme über die Zeit.

### `GROUP BY` — `GROUPING SETS`, `ROLLUP`, `CUBE`

```sql
-- Mehrere Gruppierungskombinationen in einem Durchlauf (äquivalent zu UNION mehrerer Queries)
SELECT city, car_model, sum(quantity) AS sum
FROM dealer
GROUP BY GROUPING SETS ((city, car_model), (city), (car_model), ())
ORDER BY city;

-- ROLLUP: hierarchische Zwischensummen (Kurzform für gängige GROUPING SETS)
SELECT city, car_model, sum(quantity) AS sum
FROM dealer
GROUP BY city, car_model WITH ROLLUP
ORDER BY city, car_model;

-- GROUP BY ALL: gruppiert automatisch nach allen nicht-aggregierten SELECT-Spalten
SELECT car_model, count(DISTINCT city) AS count
FROM dealer GROUP BY ALL;
```

`CUBE` liefert (anders als `ROLLUP`) alle möglichen Kombinationen der Gruppierungsspalten.

### `HAVING` — Filtern nach Aggregatwerten

Filtert (im Gegensatz zu `WHERE`) nach dem Gruppieren; kann sich auf eine nicht in `SELECT` stehende Aggregatfunktion oder auf den Alias eines Aggregats beziehen.

```sql
-- Filtert nach einer Aggregatfunktion, die im SELECT gar nicht auftaucht
SELECT city, sum(quantity) AS sum FROM dealer GROUP BY city
HAVING max(quantity) > 15;

-- Filtert über den Alias des Aggregats aus der SELECT-Liste
SELECT city, sum(quantity) AS sum FROM dealer GROUP BY city
HAVING sum > 15;

-- HAVING ohne GROUP BY: bezieht sich auf ein einziges globales Aggregat
SELECT sum(quantity) AS sum FROM dealer HAVING sum(quantity) > 10;
```

**Stand:** 2026-09-14.
