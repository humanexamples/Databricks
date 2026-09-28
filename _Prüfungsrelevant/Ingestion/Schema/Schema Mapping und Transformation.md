# Schema Mapping und Transformation

**Schema Mapping/Transformation** = Spalten umbenennen, Typen anpassen, verschachtelte Strukturen umformen. Ein **generischer Data-Engineering-Begriff**, keine Databricks-exklusive Funktion — jede ETL-Plattform kennt das Konzept. Relevant für die Prüfung ist, **mit welchen konkreten PySpark-/SQL-/Lakeflow-Mechanismen** Databricks das umsetzt.

- Gegenstück zu [Schema-on-Read vs. Schema-on-Write.md](Schema-on-Read%20vs.%20Schema-on-Write.md) (wann ein Schema festgelegt wird) und [Schema Evolution.md](Schema%20Evolution.md) (wie sich ein Tabellenschema über Zeit ändert) — Mapping/Transformation ist der **einmalige, gezielte Umbau** einer Struktur innerhalb einer Transformation, kein automatischer Anpassungsmechanismus.

---

## Umbenennen (Renaming / Aliasing)

```sql
SELECT col_name AS new_name FROM source_table;
```

```python
df.withColumnRenamed("old_name", "new_name")
```

Für dauerhaftes Umbenennen einer **bestehenden Tabellenspalte** (Metadaten-Änderung statt Transformation): `ALTER TABLE ... RENAME COLUMN`:

```sql
ALTER TABLE my_table RENAME COLUMN old_name TO new_name;
```

---

## Typ-Mapping (Casting)

```sql
SELECT CAST(price AS DECIMAL(10,2)) AS price FROM source_table;
```

```python
df.withColumn("price", col("price").cast("decimal(10,2)"))
```

Cast-Regeln, ANSI-Modus und die vollständige Funktionsreferenz sind **nicht** Gegenstand dieser Datei — siehe die SQL-Cast-Funktionsreferenz an anderer Stelle im Projekt. Für Safe-Cast-Verhalten beim Schreiben in Delta-Tabellen siehe [Schema Enforcement.md](Schema%20Enforcement.md).

Für dauerhaftes Ändern des Datentyps einer **bestehenden Tabellenspalte** (Metadaten-Änderung, kein Rewrite der Daten): **Type Widening** (Delta Lake, DBR 15.4 LTS+) — erlaubt nur **verbreiternde** Typänderungen (z. B. `INT` → `BIGINT`, `FLOAT` → `DOUBLE`), keine beliebige Typkonvertierung. Erfordert die Tabelleneigenschaft `delta.enableTypeWidening`:

```sql
ALTER TABLE my_table SET TBLPROPERTIES ('delta.enableTypeWidening' = 'true');
ALTER TABLE my_table ALTER COLUMN price TYPE DOUBLE;
```

---

## Restrukturierung verschachtelter/semi-strukturierter Daten

### Structs flach klopfen (Dot-Notation)

```sql
SELECT address.street, address.city FROM source_table;
```

### Arrays in Zeilen auflösen

**`LATERAL VIEW`** wendet eine **Generator-Funktion** (z. B. `explode`, `posexplode`) auf jede Zeile an und verbindet deren Ergebnis(se) — je Element ein oder mehrere Werte — als **neue Zeile** mit den übrigen Spalten der Ursprungszeile. Eine Zeile mit einem Array aus `n` Elementen wird so zu `n` Ausgabezeilen (klassisches „Array in Zeilen auflösen"/UNNEST-Muster).

```sql
SELECT id, exploded_value FROM source_table LATERAL VIEW explode(items) AS exploded_value;
-- posexplode liefert zusätzlich die Position:
SELECT id, pos, exploded_value FROM source_table LATERAL VIEW posexplode(items) AS pos, exploded_value;
```

Der `table_alias` zwischen Generator-Funktion und `AS` ist **optional** (Namespace für die generierten Spalten, hier ungenutzt) — beide Formen sind äquivalent gültig:

```sql
SELECT id, exploded_value FROM source_table LATERAL VIEW explode(items) virtual_table AS exploded_value;
```

**Deprecated seit DBR 12.2 LTS:** Laut Doku ist der Aufruf von `explode` sowohl über `LATERAL VIEW` als auch direkt in der `SELECT`-Liste (`SELECT id, explode(items) AS x FROM t`) deprecated — funktioniert weiterhin, aber empfohlen ist die Table-Reference-Syntax im `FROM`:

```sql
-- t = Alias für die von explode(items) erzeugte "virtuelle Tabelle" 
-- (nötig, um sie referenzieren zu können, z. B. in einem nachfolgenden 
-- LATERAL-Join oder mit t.spalte).
SELECT id, exploded_value FROM source_table, LATERAL explode(items) AS t(exploded_value);
```

```python
df.select("id", explode("items").alias("item"))
df.select("id", posexplode("items").alias("pos", "item"))
```

### STRING ↔ strukturiert (Round-Trip)

```sql
-- STRING -> strukturiert
SELECT from_json(raw_json, 'struct<id:INT,name:STRING>') AS parsed FROM source_table;
-- strukturiert -> STRING
SELECT to_json(parsed) AS raw_json FROM source_table;
```

---

## Im Lakeflow-Declarative-Pipelines-Kontext: Bronze → Silver

Das `SELECT` innerhalb eines `CREATE STREAMING TABLE ... AS SELECT` bzw. einer `@dp.table`-Python-Funktion **ist** der Schema-Mapping-Schritt von Bronze nach Silver — Umbenennen, Casten und Flachklopfen in einer Abfrage:

```sql
CREATE STREAMING TABLE silver_orders
AS SELECT
  order_id,
  customer.id AS customer_id,
  CAST(order_ts AS TIMESTAMP) AS order_timestamp,
  CAST(amount AS DECIMAL(10,2)) AS amount
FROM STREAM bronze_orders;
```

```python
@dp.table
def silver_orders():
    return (
        spark.readStream.table("bronze_orders")
        .withColumn("customer_id", col("customer.id"))
        .withColumn("order_timestamp", col("order_ts").cast("timestamp"))
        .withColumn("amount", col("amount").cast("decimal(10,2)"))
        .select("order_id", "customer_id", "order_timestamp", "amount")
    )
```

---

## Abgrenzung: `schemaHints` ist **kein** Schema Mapping

`schemaHints` (siehe [Schema Inference.md](Schema%20Inference.md)) überschreibt beim **Lesen** den von der Inferenz ermittelten Datentyp einer Spalte — z. B. um eine als `STRING` inferierte Spalte als `DOUBLE` zu erzwingen. Das ist **kein** Mapping/Transformation im Sinne dieser Datei:

- `schemaHints` **benennt nichts um** und **restrukturiert nichts** — es pinnt nur einen Typ während der Inferenz fest.
- Schema Mapping/Transformation (diese Datei) ist ein **nachgelagerter** `SELECT`/Transformationsschritt, der auf bereits eingelesenen Daten operiert.

Beide Konzepte werden leicht verwechselt, weil beide „Schema" und „Typ" betreffen — sie greifen aber an unterschiedlichen Stellen der Pipeline.

---

## Wichtige Abgrenzung: Nicht auf Reader-Ebene möglich

Umbenennen/Restrukturieren ist **nicht** auf der Ebene des Rohdaten-Readers möglich: Weder `read_files` noch Auto Loader (`cloudFiles`) bieten eine „Spalte umbenennen"-Option beim Einlesen.

- Mapping/Renaming ist **immer** ein nachgelagerter `SELECT`/Transformationsschritt **nach** dem Rohdaten-Read — niemals Teil des Ingestion-Reads selbst.
- Diese Trennung ist ein konkreter, prüfungsrelevanter Unterschied: Der Reader liefert das Schema (inferiert oder vorgegeben), die Transformation formt es um.
