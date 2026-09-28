# Overwrite oder Append bei der Ingestion

## Was bedeuten „Append“ und „Overwrite“?

Beide Begriffe beschreiben, was mit den Daten in der **Zieltabelle** passiert, wenn neue Daten kommen.

- **Append:** Die neuen Zeilen kommen **zu den bestehenden dazu**. Nichts wird gelöscht.
- **Overwrite:** Bestehende Daten werden **ersetzt**, ganz oder teilweise.

```
Vorher:        Ziel = {A, B}      Neue Daten = {C}
Append:        Ziel = {A, B, C}
Overwrite:     Ziel = {C}
```

**Append** ist der Normalfall bei der inkrementellen Ingestion in Bronze. Jede neue Datei bringt neue Zeilen.

```sql
INSERT INTO main.bronze.orders SELECT * FROM staging_orders;
```

Es gibt drei Arten von Overwrite:

**1. Komplett überschreiben:** Die ganze Tabelle wird geleert und neu befüllt.

```sql
INSERT OVERWRITE main.bronze.orders SELECT * FROM staging_orders;
```

**2. Selektiv überschreiben:** Nur ein Teil der Tabelle wird ersetzt, der Rest bleibt.

```sql
INSERT INTO main.bronze.orders
REPLACE WHERE order_date = '2026-09-01'
SELECT * FROM staging_orders WHERE order_date = '2026-09-01';
```

**3. Schema überschreiben:** Beim kompletten Überschreiben wird auch das Schema ersetzt.

```python
df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable("main.bronze.orders")
```

**Abgrenzung:** Diese Datei behandelt nur das **Ziel**, also was mit den Daten in der Tabelle passiert. Welche Dateien überhaupt gelesen werden, ist das Thema von [File Tracking.md](File%20Tracking.md).

---

## Übersicht: Was kann welche Methode?

**Beides (Append und Overwrite):**
- `INSERT INTO` hängt an. `INSERT OVERWRITE` und `INSERT INTO ... REPLACE ...` überschreiben.
- DataFrame-`write` hängt mit `mode("append")` an und überschreibt mit `mode("overwrite")`.
- Structured Streaming bzw. Auto Loader hängt mit `outputMode("append")` an (Standard). Mit `outputMode("complete")` wird überschrieben, aber nur bei Aggregationen.

**Nur Append:**
- `COPY INTO` hängt immer an. Es hat keine Overwrite-Option, auch `force` überschreibt nicht.
- Streaming Tables sind für Append-only-Ingestion gedacht. Ein normaler Refresh hängt nur neue Daten an. Ersetzen geht nur über einen **Full Refresh**.

**Nur Overwrite:**
- CTAS mit `CREATE OR REPLACE TABLE ... AS SELECT` ersetzt die Tabelle immer komplett. Anhängen geht damit nicht.

**Weder noch:**
- `MERGE INTO` aktualisiert, fügt ein und löscht Zeilen einzeln (Upsert).

**Alle Overwrite-Möglichkeiten im Überblick:**
- CTAS mit `CREATE OR REPLACE TABLE ... AS SELECT` ersetzt die Tabelle komplett.
- `INSERT OVERWRITE` ersetzt die Tabelle komplett oder einzelne Partitionen.
- `INSERT INTO ... REPLACE WHERE / REPLACE USING / REPLACE ON` ersetzt selektiv.
- DataFrame-`write.mode("overwrite")` ersetzt komplett, mit `replaceWhere`, `replaceUsing` oder `replaceOn` auch selektiv.
- Streaming Tables und Lakeflow-Pipelines: Ein **Full Refresh** leert die Tabelle und verarbeitet alles neu.
- Structured Streaming bzw. Auto Loader mit `outputMode("complete")` ersetzt die Tabelle nach jedem Batch. Das geht **nur bei Aggregationen**.


---

## Die Methoden im Einzelnen

### 1. CTAS – `CREATE OR REPLACE TABLE ... AS SELECT`

Die Tabelle wird durch das Ergebnis der Abfrage ersetzt. Tabellenhistorie, erteilte Rechte, Row Filter und Column Masks **bleiben erhalten**.

```sql
CREATE OR REPLACE TABLE main.bronze.orders AS
SELECT * FROM staging_orders;
```

**Append gibt es bei CTAS nicht.** Für weitere Daten nimmst du danach `INSERT INTO`:

```sql
INSERT INTO main.bronze.orders
SELECT * FROM staging_orders_new;
```

`CREATE OR REPLACE TABLE IF NOT EXISTS` ist nicht erlaubt, denn `IF NOT EXISTS` und `REPLACE` schließen sich aus.

Weil Delta die Historie behält, kannst du einen Fehler rückgängig machen:

```sql
RESTORE TABLE main.bronze.orders TO VERSION AS OF 5;
```

---

### 2. `INSERT INTO` und `INSERT OVERWRITE`

- **Ohne Partitionsangabe** wird die Tabelle vor der ersten Zeile geleert.
- **Mit Partitionsangabe** werden nur die passenden Partitionen geleert.

```sql
-- ganze Tabelle ersetzen
INSERT OVERWRITE main.bronze.orders
SELECT * FROM staging_orders;

-- nur eine Partition ersetzen (Tabelle ist nach order_date partitioniert)
INSERT OVERWRITE main.bronze.orders PARTITION (order_date = '2026-09-01')
SELECT order_id, amount FROM staging_orders WHERE order_date = '2026-09-01';
```

Das Gegenstück `INSERT INTO` hängt an. Alle eingefügten Zeilen kommen zu den bestehenden dazu.

```sql
INSERT INTO main.bronze.orders SELECT * FROM staging_orders;
```

---

### 3. Selektiv überschreiben mit `INSERT INTO ... REPLACE`

**`REPLACE WHERE`** (SQL ab Databricks Runtime 12.2 LTS): Es werden genau die Zeilen ersetzt, die auf eine Bedingung passen. Die Tabelle muss dafür nicht partitioniert sein.

```sql
INSERT INTO TABLE main.default.events
REPLACE WHERE start_date >= '2017-01-01' AND end_date <= '2017-01-31'
SELECT * FROM main.default.replace_data;
```

Jede neue Zeile muss die Bedingung erfüllen. Sonst schlägt der Befehl fehl und schreibt nichts. **Achtung:** Ist die Quelle leer, kann `REPLACE WHERE` Zeilen löschen.

**`REPLACE USING`** (SQL ab Databricks Runtime 16.3, dynamisches Überschreiben ab 17.2): Zeilen werden ersetzt, wenn die genannten Spalten gleich sind. Neue Schlüssel werden eingefügt.

```sql
INSERT INTO TABLE main.default.events
REPLACE USING (event_id, start_date)
SELECT * FROM main.default.source_data;
```

**`REPLACE ON`** (SQL ab Databricks Runtime 17.1): Wie `REPLACE USING`, aber mit einer eigenen Bedingung, zum Beispiel NULL-sicher mit `<=>`.

```sql
INSERT INTO TABLE main.default.events AS t
REPLACE ON (s.event_id <=> t.event_id AND s.start_date <=> t.start_date)
(SELECT * FROM main.default.source_data) AS s;
```

Bei leerer Quelle löschen `REPLACE USING` und `REPLACE ON` nichts. Databricks empfiehlt meist `REPLACE USING` oder `REPLACE WHERE`. Ausführlicher: [../Data Transformation and Modeling/04 DML und Kernkonzepte/04 Selective Overwrite.md](../Data%20Transformation%20and%20Modeling/04%20DML%20und%20Kernkonzepte/04%20Selective%20Overwrite.md).

---

### 4. DataFrame-API `df.write` (Batch)

Über `mode` legst du fest, ob überschrieben oder angehängt wird.

```python
# df = ein beliebiger DataFrame mit den neuen Daten
df.write.mode("overwrite").saveAsTable("main.bronze.orders")   # ersetzen
df.write.mode("append").saveAsTable("main.bronze.orders")      # anhängen
```

Mit `mode("overwrite")` und `replaceWhere` wird selektiv überschrieben:

```python
(df.write
   .mode("overwrite")
   .option("replaceWhere", "order_date = '2026-09-01'")
   .saveAsTable("main.bronze.orders"))
```

Mit `replaceUsing` (Python/Scala ab Databricks Runtime 18.2) wird dynamisch überschrieben:

```python
(df.write
   .mode("overwrite")
   .option("replaceUsing", "event_id, start_date")
   .saveAsTable("main.default.events"))
```

Mit `overwriteSchema` werden auch Schema und Partitionierung ersetzt. Das braucht man zum Beispiel, um einen Spaltentyp zu ändern oder eine Spalte zu löschen.

```python
(df.write
   .mode("overwrite")
   .option("overwriteSchema", "true")
   .saveAsTable("main.bronze.orders"))
```

Einschränkungen:
- `overwriteSchema = true` geht nicht zusammen mit dem dynamischen Partitions-Overwrite.
- `replaceOn` und `replaceUsing` gehen nicht zusammen mit `replaceWhere`, `partitionOverwriteMode` oder `overwriteSchema`.

**Legacy:** `partitionOverwriteMode = dynamic` ersetzt nur die Partitionen, in die geschrieben wird. Das ist Public Preview, ab Databricks Runtime 11.3 LTS und nur auf Classic Compute. Databricks empfiehlt stattdessen `REPLACE USING`.

---

### 5. `COPY INTO` – nur Append

`COPY_OPTIONS` kennt nur `force` und `mergeSchema`. `COPY INTO` **hängt immer an**. Dank File Tracking hängt jeder Lauf nur Zeilen aus **neuen** Dateien an. Das Append ist also idempotent.

```sql
COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');
-- 2. Lauf ohne neue Dateien: nichts wird angehängt
```

**Die Copy-Option `force`** (in `COPY_OPTIONS`, Typ Boolean, Standard `false`): Bei `'force' = 'true'` ist die **Idempotenz abgeschaltet**. Dann werden alle Dateien geladen, auch solche, die schon geladen wurden. Das heißt, sie werden **zusätzlich** angehängt. Überschrieben wird trotzdem nichts.

```sql
COPY_OPTIONS ('force' = 'true')    -- Idempotenz aus: auch bereits geladene Dateien laden
COPY_OPTIONS ('force' = 'false')   -- Standard: bereits geladene Dateien überspringen
```

Wer ersetzen will, leert die Tabelle vorher:

```sql
TRUNCATE TABLE main.bronze.orders;

COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true')
COPY_OPTIONS ('force' = 'true');   -- sonst werden bereits geladene Dateien übersprungen
```

Oder man nimmt statt `COPY INTO` gleich `INSERT OVERWRITE` bzw. CTAS. Siehe [COPY INTO/02 Idempotenz, File Tracking und force.md](COPY%20INTO/02%20Idempotenz,%20File%20Tracking%20und%20force.md).

---

### 6. Structured Streaming (auch Auto Loader)

Für das Ziel ist egal, woher der Stream kommt, zum Beispiel aus Auto Loader. `stream_df` steht unten für einen beliebigen Streaming-DataFrame. Ein Stream kennt kein `mode("overwrite")`. Stattdessen gibt es den **Output Mode**. Delta-Tabellen unterstützen `append` und `complete`, aber nicht `update`.

**`append` (Standard):** Neue Zeilen werden angehängt. Das ist der normale Fall bei der Ingestion.

```python
(stream_df.writeStream
   .outputMode("append")          # Standard, kann auch weggelassen werden
   .option("checkpointLocation", "/Volumes/main/raw/_checkpoints/orders")
   .toTable("main.bronze.orders"))
```

**`complete`:** Die ganze Tabelle wird nach **jedem Batch** ersetzt. Das geht nur mit Streaming-Aggregationen und kann bei großen Daten langsam werden. Databricks empfiehlt dafür eher Materialized Views.

```python
(stream_df.groupBy("customer_id").count()
 .writeStream
   .outputMode("complete")
   .option("checkpointLocation", "/Volumes/main/raw/_checkpoints/orders_by_customer")
   .toTable("main.silver.orders_by_customer"))
```

**Eigenes Overwrite in `foreachBatch`:** Jeder Micro-Batch kann das Ziel mit SQL ersetzen.

```python
def overwrite_target(batch_df, _):
    batch_df.createOrReplaceTempView("incoming")
    batch_df.sparkSession.sql("INSERT OVERWRITE main.bronze.orders SELECT * FROM incoming")

(stream_df.writeStream
   .foreachBatch(overwrite_target)
   .option("checkpointLocation", "/Volumes/main/raw/_checkpoints/orders")
   .start())
```

---

### 7. Streaming Tables und Lakeflow-Pipelines – Append, Overwrite nur per Full Refresh

Streaming Tables sind für **Append-only-Ingestion** gedacht. Ein normaler Refresh verarbeitet nur neue Datensätze und hängt sie an. Ein **Full Refresh** leert die Streaming Table, setzt die Checkpoints zurück und verarbeitet alle Daten aus der Quelle mit der aktuellen Definition neu.

```sql
CREATE OR REFRESH STREAMING TABLE main.bronze.orders_st
AS SELECT * FROM STREAM main.raw.orders_raw;

REFRESH STREAMING TABLE main.bronze.orders_st;        -- Append: nur neue Datensätze
REFRESH STREAMING TABLE main.bronze.orders_st FULL;   -- leeren und alles neu laden
```

**Vorsicht:** Liegen Quelldaten nicht mehr vor (z. B. bei Kafka mit kurzer Aufbewahrung oder bei gelöschten Dateien), gehen sie durch den Full Refresh verloren. Databricks empfiehlt Full Refreshes nur, wenn nötig.

Selektiv geht es nur bei einer Streaming Table, deren Flow mit `FLOW REPLACE WHERE` angelegt wurde. Dort ersetzt `REFRESH ... WHERE` einmalig die Bedingung. Nur die passenden Zeilen werden gelöscht und neu berechnet. Bei anderen Streaming Tables gibt `WHERE` einen Fehler.

```sql
-- orders_rw wurde mit FLOW REPLACE WHERE angelegt
REFRESH STREAMING TABLE main.bronze.orders_rw WHERE order_date = '2026-09-01';
```

**Materialized Views** liefern bei normalem Refresh und Full Refresh dasselbe Ergebnis. Sie spiegeln immer den aktuellen Stand der Abfrage wider.

---

### 8. `MERGE INTO` – weder Append noch Overwrite

`MERGE` ersetzt nicht die ganze Tabelle. Es ändert Zeilen **einzeln**: aktualisieren, einfügen und bei Bedarf löschen.

```sql
MERGE INTO main.silver.orders t
USING main.bronze.orders_latest s
ON t.order_id = s.order_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

Siehe [Datei Ingestion Varianten/99 Dedup und Upsert Muster.md](Datei%20Ingestion%20Varianten/99%20Dedup%20und%20Upsert%20Muster.md).

---

## Append: worauf achten

**1. Duplikate:** Append ist nur sicher, wenn jede Zeile genau einmal kommt. `COPY INTO`, Auto Loader und Streaming Tables sorgen selbst dafür, dass nichts doppelt angehängt wird. Bei `INSERT INTO` und `write.mode("append")` bist du selbst verantwortlich.

```sql
-- Nicht idempotent: zweimal ausgeführt = jede Zeile doppelt
INSERT INTO main.bronze.orders SELECT * FROM staging_orders;
INSERT INTO main.bronze.orders SELECT * FROM staging_orders;
```

**2. Neue Spalten beim Append:** Bringen die neuen Daten zusätzliche Spalten mit, schaltest du die Schema-Evolution pro Schreibvorgang ein.

```sql
-- SQL ab Databricks Runtime 18.1
INSERT WITH SCHEMA EVOLUTION INTO main.bronze.orders
SELECT * FROM staging_orders;

-- COPY INTO
COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');
```

```python
# DataFrame-API, Batch oder Streaming
df.write.mode("append").option("mergeSchema", "true").saveAsTable("main.bronze.orders")
```

Databricks empfiehlt, die Schema-Evolution pro Schreibvorgang einzuschalten (`WITH SCHEMA EVOLUTION` bzw. `mergeSchema`) statt über eine Spark-Konfiguration.

**3. Korrigierte Daten:** Append ersetzt nichts. Kommt eine korrigierte Version, stehen alte und neue Zeilen nebeneinander. Die Auflösung passiert später, zum Beispiel in Silver mit `MERGE` oder mit `QUALIFY row_number()`. Siehe [COPY INTO/11 Muster - Korrigierte Dateien mit gleichem Namen.md](COPY%20INTO/11%20Muster%20-%20Korrigierte%20Dateien%20mit%20gleichem%20Namen.md).

---

## Wann Append, wann Overwrite?

- **Append:** laufend neue, unveränderliche Dateien, typisch für Bronze. Die Historie bleibt erhalten.
- **Komplett überschreiben:** Jede Lieferung ist der vollständige aktuelle Stand (Voll-Snapshot), und Historie wird nicht gebraucht.
- **Selektiv überschreiben:** Ein bestimmter Bereich wird neu geliefert, etwa ein Tag oder ein Monat. Dann `REPLACE WHERE` oder `REPLACE USING`.
- **Weder noch (Upsert):** Einzelne Zeilen ändern sich per Schlüssel. Dann `MERGE INTO`.

---

## Häufige Verwechslungen

- **`force = true` (COPY INTO)** heißt nicht „Ziel überschreiben“. Es heißt „Datei trotz File Tracking noch einmal laden“. Das Ergebnis ist Append, und es entstehen Duplikate.
- **`CREATE OR REFRESH STREAMING TABLE`** heißt nicht „Daten ersetzen“. Ein normaler Refresh verarbeitet neue Daten. Ersetzen tut erst `REFRESH ... FULL`.
- **`INSERT OVERWRITE` bei leerer Quelle** leert die Tabelle. `REPLACE WHERE` kann bei leerer Quelle ebenfalls Zeilen löschen, `REPLACE USING` und `REPLACE ON` tun es nicht.
- **Versehentlich überschrieben?** Mit Delta Time Travel lässt sich das rückgängig machen: `RESTORE TABLE ... TO VERSION AS OF n`.

---

## Verwandte Themen

- [File Tracking.md](File%20Tracking.md): welche Dateien gelesen werden (Quellseite)
- [COPY INTO/00 Uebersicht.md](COPY%20INTO/00%20Uebersicht.md)
- [Datei Ingestion Varianten/03 Gleiche Datei wird ueberschrieben.md](Datei%20Ingestion%20Varianten/03%20Gleiche%20Datei%20wird%20ueberschrieben.md)
- [Datei Ingestion Varianten/05 Periodische Voll-Snapshots.md](Datei%20Ingestion%20Varianten/05%20Periodische%20Voll-Snapshots.md)
- [../Data Transformation and Modeling/04 DML und Kernkonzepte/04 Selective Overwrite.md](../Data%20Transformation%20and%20Modeling/04%20DML%20und%20Kernkonzepte/04%20Selective%20Overwrite.md)
