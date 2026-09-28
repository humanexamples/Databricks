# Prozedural vs. Deklarativ, Batch vs. Streaming, Tabellen vs. Views

## Prozedural vs. deklarative Datenverarbeitung

- **Prozedural:** legt explizit fest, *wie* etwas erledigt wird (Schritt-für-Schritt-Reihenfolge, Kontrollstrukturen, feingranulares Ressourcenmanagement). Unterform der imperativen Programmierung. Einsatz: individuelle ETL-Logik, Low-Level-Performance-Tuning, Altsysteme. In Databricks: Apache Spark, Lakeflow Jobs.
- **Deklarativ:** beschreibt *was* erreicht werden soll — das System optimiert selbst die Ausführung. Einsatz: SQL-Transformationen, skalierbare verteilte Workloads. In Databricks: Lakeflow-Pipelines (Apache Spark Declarative Pipelines / SDP).
- Entscheidung: prozedural bei feingranularer Kontrolle/komplexen manuell optimierten Geschäftsregeln; deklarativ bei Fokus auf einfache Entwicklung, Wartung und eingebauter Optimierung.

```python
# Prozedural: explizite Schritt-für-Schritt-Logik in PySpark
df = spark.read.table("bronze.orders")
df = df.filter("status = 'valid'")
df = df.withColumn("amount_eur", col("amount_usd") * 0.92)
df.write.mode("overwrite").saveAsTable("silver.orders")
```

```sql
-- Deklarativ: beschreibt nur das Zielergebnis, Lakeflow entscheidet über die Ausführung
CREATE OR REFRESH STREAMING TABLE silver.orders AS
SELECT *, amount_usd * 0.92 AS amount_eur
FROM STREAM bronze.orders
WHERE status = 'valid'
```

## Batch vs. Streaming Datenverarbeitung

Beide teilen sich dieselbe Engine (Apache Spark / Structured Streaming) — Quellen sind flexibel für beide Methoden nutzbar.

- **Batch:** verarbeitet bei jedem Lauf alle aktuell verfügbaren Daten, ohne frühere Läufe zu berücksichtigen (meist Neuverarbeitung über logische Partitionierung begrenzt).
- **Streaming:** merkt sich bereits verarbeitete Daten, verarbeitet nur neue.

| Ansatz | Stärken | Herausforderungen |
|---|---|---|
| Batch | Einfache Logik; präzise Ergebnisse über alle Daten | Ineffiziente Neuverarbeitung; höhere Latenz (Stunden–Minuten) |
| Streaming | Nur neue Daten; Latenz im Sekunden-/Millisekundenbereich | Komplexe zustandsbehaftete Operationen; Genauigkeitsprobleme bei verspäteten Daten |

**Empfehlung nach Medallion-Schicht:**
- Bronze: Streaming (zustandslose Append-Operationen).
- Silver: Batch mit inkrementellem Refresh bevorzugt; Streaming optional bei Latenz-Priorität.
- Gold: Batch mit inkrementellem Refresh.

> Verspätete Daten: Batch berechnet automatisch neu; Streaming braucht zusätzliche Zustandsverwaltungs-Logik.

## Tabellen und Views

Vier Datenobjekte, unterschieden nach Speicherung/Aktualisierung:

```sql
-- Tabelle: strukturierter Datensatz, physisch gespeichert (Default: Unity-Catalog-Managed)
CREATE TABLE main.sales.orders (id INT, amount DOUBLE);

-- View: speichert keine Daten, nur die Abfrage
CREATE VIEW main.sales.orders_view AS SELECT id, amount FROM main.sales.orders WHERE amount > 0;

-- Materialisierte View: wie View, aber Ergebnis wird vorausberechnet + gespeichert -> schnellere Reads, mehr Speicher
CREATE MATERIALIZED VIEW main.sales.orders_mv AS SELECT id, sum(amount) AS total FROM main.sales.orders GROUP BY id;

-- Streaming-Tabelle: Unity-Catalog-verwaltete Tabelle, Verarbeitungslogik über Flows definiert
CREATE STREAMING TABLE main.sales.orders_stream AS SELECT * FROM STREAM main.sales.orders_raw;
```

- Tabellen unterstützen `INSERT`/`UPDATE`/`DELETE`/`MERGE INTO`.
- Views kapseln Geschäftslogik über eine oder mehrere zugrunde liegende Tabellen, ohne eigene Daten.
- Materialisierte Views und Streaming-Tabellen erstell-/pflegbar über Databricks SQL oder Lakeflow-Pipelines.
- **Kernunterschied Materialized View vs. Streaming Table:** Materialisierte Views = **Batch-Semantik**, Streaming-Tabellen = **Streaming-Semantik**. Wahl abhängig von Workload-Anforderungen.

**Stand:** 2026-09-14.
