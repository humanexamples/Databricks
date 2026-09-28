# Methoden der inkrementellen Verarbeitung in Databricks

**Batch kann inkrementell sein:**
 Mit Batch-Verarbeitung verfolgt die Engine nicht, welche Daten bereits in der Quelle verarbeitet wurden. Alle aktuell in der Quelle verfügbaren Daten werden zum Zeitpunkt der Verarbeitung verarbeitet. Das klingt zunächst nicht inkrementell – **aber**: In der Praxis wird eine Batch-Datenquelle typischerweise logisch partitioniert, zum Beispiel nach Tag oder Region, um die Neuverarbeitung von Daten zu begrenzen. Zusätzlich existiert mit **Incremental Refresh für Materialized Views** eine offiziell dokumentierte Methode, die *innerhalb* der Batch-Semantik inkrementell arbeitet: Ein inkrementeller Refresh erkennt Änderungen in den Quelldaten und berechnet nur die betroffenen Ergebnisse neu, statt die gesamte Query neu auszuführen.

**Streaming ist von Natur aus inkrementell:**
 Bei Streaming-Verarbeitung merkt sich die Engine, welche Daten bereits verarbeitet wurden, und verarbeitet in nachfolgenden Läufen nur neue Daten.

| Methode                          | Zweck                                          | Semantik    | Kernaussage                                                  |
| -------------------------------- | ---------------------------------------------- | ----------- | ------------------------------------------------------------ |
| Auto Loader                      | Neue Dateien aus Cloud-Storage laden           | Streaming   | Verarbeitet neue Dateien inkrementell und effizient, sobald sie ankommen; Dateimetadaten werden in RocksDB am Checkpoint-Ort gespeichert (Exactly-once); kann nach Fehlern vom letzten Checkpoint fortsetzen |
| COPY INTO                        | Neue Dateien aus Cloud-Storage laden           | Batch       | Wiederholbare und idempotente Operation — bereits geladene Dateien werden bei erneuten Läufen übersprungen, auch bei zwischenzeitlicher Änderung |
| Auto Loader vs. COPY INTO        | Wahl-Kriterium                                 | —           | Bei Tausenden Dateien: COPY INTO. Bei Millionen+ Dateien: Auto Loader (weniger Operationen zur Dateierkennung, Aufteilung in Batches) |
| Structured Streaming (Batch)     | Verarbeitungs-Engine                           | Batch       | Engine verfolgt nicht, was bereits verarbeitet wurde — alle verfügbaren Daten werden neu verarbeitet |
| Structured Streaming (Streaming) | Verarbeitungs-Engine                           | Streaming   | Engine merkt sich den Verarbeitungsstand — nur neue Daten werden in Folgeläufen verarbeitet |
| Change Data Feed (CDF)           | Änderungen an Delta-/Iceberg-Tabellen erkennen | —           | Verfolgt zeilenbasierte Änderungen zwischen Tabellenversionen; erfasst Insert/Update/Delete |
| CDF – Kombination                | Nutzungsempfehlung                             | —           | Databricks empfiehlt CDF in Kombination mit Structured Streaming |
| MERGE INTO                       | Änderungen in Zieltabelle anwenden             | Batch (DML) | Merged Updates, Insertions und Deletions aus Quelle in Ziel-Delta-Tabelle; für Deduplizierung, Upserts, SCD Typ 2 |
| Append Flow                      | Neue Records ins Ziel schreiben                | Streaming   | Häufigster Flow-Typ: neue Records werden bei jedem Update geschrieben; entspricht Append-Modus in Structured Streaming |
| Auto CDC Flow                    | CDC-Daten in Ziel einpflegen                   | Streaming   | Verarbeitet Query mit CDC-Daten; nur Streaming-Tables als Ziel möglich |
| Update Flow (Preview)            | Geänderte Aggregate ausgeben                   | Streaming   | Gibt globale, nicht-watermarked Aggregate an Sink aus; nur Python |
| Streaming Table                  | Rohdaten inkrementell speichern                | Streaming   | Unity-Catalog-verwaltete Tabelle, Verarbeitungslogik über Flows definiert |
| Materialized View                | Aggregierte Ergebnisse aktuell halten          | Batch       | Nutzt Batch-Semantik; speichert Query-Ergebnis vorab         |
| Incremental Refresh              | Nur geänderte Daten neu berechnen              | Batch       | Berechnet nur betroffene Ergebnisse neu; erfordert Serverless; Ergebnis identisch zu vollständiger Batch-Query |

------





### [Auto Loader](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/)

- Verarbeitet neue Dateien inkrementell und effizient, sobald sie im Cloud-Storage ankommen.
- Skaliert auf Milliarden von Dateien; Kosten skalieren mit der Anzahl der Dateien, nicht der Verzeichnisse.
- Dateimetadaten werden in einem Key-Value-Store (RocksDB) am Checkpoint-Ort gespeichert → **Exactly-once-Verarbeitung**, auch nach Fehlern (Resume von letztem Checkpoint).
- Unterstützt Schema-Inferenz und -Evolution inkl. Benachrichtigung bei Schema-Drift.
- Databricks empfiehlt Auto Loader für inkrementelle Ingestion in Lakeflow-Pipelines.

**Beispiel:**
```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .load("/mnt/rohdaten/events"))
```

---

### [COPY INTO](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage) / [Sprachreferenz](https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into)
- Empfohlen bei Dateien im Bereich von **Tausenden**.
- Bei **Millionen+** Dateien: Auto Loader nutzen (weniger Operationen zur Dateierkennung, Aufteilung in mehrere Batches).
- Erneutes Laden einer Teilmenge von Dateien ist mit COPY INTO einfacher als mit Auto Loader.

**Beispiel:**
```sql
COPY INTO meine_tabelle
FROM '/mnt/rohdaten/verkaeufe'
FILEFORMAT = PARQUET
COPY_OPTIONS ('mergeSchema' = 'true')
```

---

### [Structured Streaming](https://docs.databricks.com/aws/en/data-engineering/batch-vs-streaming)
- **Batch:** Engine merkt sich nicht, was bereits verarbeitet wurde — alle verfügbaren Daten werden neu verarbeitet.
- **Streaming:** Engine merkt sich den Verarbeitungsstand und verarbeitet in Folgeläufen nur neue Daten.
- Cloud-Object-Storage und Delta Lake können als Streaming-Quellen behandelt werden.

**Beispiel:**
```python
df = spark.readStream.format("delta").table("bronze.verkaeufe")
(df.writeStream
   .format("delta")
   .option("checkpointLocation", "/mnt/checkpoints/silver_verkaeufe")
   .table("silver.verkaeufe"))
```

---

### [Change Data Feed (CDF)](https://docs.databricks.com/aws/en/delta/delta-change-data-feed)
- Verfolgt zeilenbasierte Änderungen zwischen Versionen einer Delta- (oder Iceberg v3-)Tabelle.
- Erfasst Inserts, Updates, Deletes inkl. Metadaten-Spalten.
- Nutzen: inkrementelle ETL-Pipelines, Audit-Trails, Datenreplikation.
- Databricks empfiehlt CDF in Kombination mit **Structured Streaming**.

**Beispiel:**
```sql
ALTER TABLE kunden SET TBLPROPERTIES (delta.enableChangeDataFeed = true);
SELECT * FROM table_changes('kunden', 5);
```

---

### [MERGE INTO](https://docs.databricks.com/aws/en/sql/language-manual/delta-merge-into) / [Anleitung](https://docs.databricks.com/aws/en/delta/merge)
- Führt Upserts (Insert + Update + Delete) aus einer Quelle in eine Ziel-Delta-Tabelle durch.
- Nutzbar für Deduplizierung, Change-Data-Capture-Upserts, SCD-Typ-2-Operationen.
- Nur für Delta-Lake-Tabellen unterstützt.

**Beispiel:**
```sql
MERGE INTO silver.kunden t
USING bronze.kunden_updates s
ON t.kunden_id = s.kunden_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
```

---

### [Lakeflow Pipeline Flows](https://docs.databricks.com/aws/en/ldp/flows)
- Ein Flow ist eine Query, die Daten inkrementell lädt/verarbeitet.
- **Streaming-Produkte:** Lakeflow Connect, Append Flow, Apply-Change-Flow (Auto CDC), Streaming Table, Sink.
- **Batch-Produkte:** Materialized View Flow, Materialized View (inkl. Incremental Refresh).

**Beispiel:**
```python
import dlt

@dlt.table
def bronze_events():
    return (spark.readStream
            .format("cloudFiles")
            .option("cloudFiles.format", "json")
            .load("/mnt/events"))
```

---

### [Incremental Refresh (Materialized Views)](https://docs.databricks.com/aws/en/data-engineering/batch-vs-streaming)
- Batch-basierte Methode: nur geänderte Daten fließen in die Neuberechnung ein.
- Empfohlen für Silver- und Gold-Layer.

**Beispiel:**
```sql
CREATE MATERIALIZED VIEW gold_umsatz_pro_tag AS
SELECT datum, SUM(betrag) AS umsatz
FROM silver.verkaeufe
GROUP BY datum;
```

---

