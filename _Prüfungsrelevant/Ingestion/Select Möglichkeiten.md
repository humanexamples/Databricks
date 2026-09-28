

# Select-Möglichkeiten bei der Ingestion

> Quellen: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options), [File metadata column](https://docs.databricks.com/aws/en/ingestion/file-metadata-column), [COPY INTO — Sprachreferenz](https://docs.databricks.com/aws/en/sql/language-manual/delta-copy-into), [Read and write Parquet files](https://docs.databricks.com/aws/en/query/formats/parquet) · siehe auch [Metadata.md](Metadata.md), [Rescued Data.md](Rescued%20Data.md)

## `.select()` vs. `.selectExpr()`

Der zentrale Unterschied liegt darin, wie ein **String**-Argument interpretiert wird:

| | `.select(...)` | `.selectExpr(...)` |
|---|---|---|
| String-Argument | wird als **wörtlicher Spaltenname** behandelt | wird als vollständige **SQL-Expression** geparst |
| Alias/Umbenennen per String | ❌ nicht möglich (`"col as new"` wird als ein Spaltenname `"col as new"` gesucht) | ✅ `"col as new"` |
| Berechnete Ausdrücke per String | ❌ nur über `Column`-Objekte (`col()`, `expr()`) | ✅ `"round(x, 2) as x_rounded"` |
| Wildcard | `.select("*")` | `.selectExpr("*")` |

```python
from pyspark.sql.functions import col, expr

# .select() – Spaltennamen oder Column-Objekte
df.select("c_custkey", "c_acctbal")
df.select(col("c_custkey"), col("c_acctbal"))

# Umbenennen mit .select() braucht ein Column-Objekt:
df.select(col("c_custkey").alias("key"))

# .selectExpr() – SQL-Ausdrücke als String, inkl. Alias
df.selectExpr("c_custkey as key", "round(c_acctbal) as account_rounded")
```

Beide Wege sind funktional gleichwertig — `selectExpr` ist meist nur die kompaktere Schreibweise, um Alias/Ausdruck direkt als String zu formulieren, ohne `col()`/`alias()`/`expr()` zu importieren.

---

## Praxisfall: `_metadata` bei Auto Loader umbenennen

Bei Auto Loader **muss** `_metadata` umbenannt werden, sobald die Quelldaten selbst eine Spalte namens `_metadata` enthalten — sonst ist die Datei-Metadaten-Spalte in der Zieltabelle nicht erreichbar (siehe [Metadata.md](Metadata.md#fallstricke)):

```python
(spark.readStream.format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .load("abfss://…/csvData")
  .selectExpr("*", "_metadata as source_metadata")   # Alias per String → selectExpr
  .writeStream.option("checkpointLocation", cp).start(targetTable))
```

Mit `.select()` wäre dafür ein `Column`-Objekt nötig:

```python
.select("*", col("_metadata").alias("source_metadata"))
```

> **Streaming-Sonderfall:** Wird zusätzlich `foreachBatch` verwendet, muss `_metadata` **vor** dem `foreachBatch`-Aufruf selektiert werden — innerhalb der Batch-Funktion referenziert, ist die Spalte nicht mehr enthalten (Details: [Metadata.md](Metadata.md#fallstricke)).

---

## Explizite Selektion versteckter Spalten (`_metadata`, `_object_metadata`)

`_metadata` und `_object_metadata` sind **versteckte** Spalten und erscheinen bei keinem Zugriffsweg (`spark.read`, `read_files`, Auto Loader, `COPY INTO`) automatisch über `SELECT *` / `.select("*")` — sie müssen ausdrücklich referenziert werden:

```python
df = (spark.read.format("csv").schema(schema)
      .load("/Volumes/<c>/<s>/<v>/data/*")
      .select("*", "_metadata"))
```

Einzelne Felder per Punktnotation gezielt selektieren (empfohlen, da künftige Runtime-Versionen neue Felder zur Struktur hinzufügen können):

```python
.select("_metadata.file_name", "_metadata.file_size")
```

Details und Feldlisten: [Metadata.md](Metadata.md).

---

## `SELECT * EXCEPT (...)` — Spalten gezielt ausschließen

Databricks SQL erlaubt, einzelne Spalten aus einem Wildcard-Ergebnis auszuschließen — nützlich z. B. bei `format => 'binaryFile'`, um die große `content`-Spalte wegzulassen:

```sql
SELECT * EXCEPT (content), _metadata.file_name, _metadata.file_size
FROM read_files('/Volumes/my_catalog/my_schema/my_volume', format => 'binaryFile');
```

---

## `COPY INTO`: Spaltenauswahl/-transformation vor dem Laden

`COPY INTO` erlaubt anstelle eines reinen Pfads auch eine `SELECT`-Klausel, um vor dem Kopieren gezielt Spalten oder Ausdrücke auszuwählen — auch **Window-Funktionen** sind erlaubt, **`GROUP BY`/Aggregationen mit Gruppierung dagegen nicht** (nur globale Aggregate):

```sql
COPY INTO workspace.default.orders_bronze
FROM (
  SELECT order_id, customer_id, amount, _metadata.file_name AS source_file
  FROM '/Volumes/raw/orders/'
)
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');
```

Details: [06 DML Statements/_copy_into.md](../06%20DML%20Statements/_copy_into.md), Abschnitt 3.

---

## Nur benötigte Spalten lesen statt `SELECT *`

Parquet (das zugrunde liegende Speicherformat von Delta Lake) ist spaltenorientiert: *"It allows query engines to read only the columns needed and skip irrelevant row groups."* Eine **explizite Spaltenauswahl** anstelle von `SELECT *` nutzt das aus — nicht benötigte Spalten werden dann gar nicht erst von der Storage-Schicht gelesen (Column Pruning). Bei zeilenorientierten Formaten (CSV, JSON) muss die Zeile beim Parsen trotzdem vollständig verarbeitet werden — der Vorteil einer gezielten Auswahl liegt dort eher in kleineren nachgelagerten DataFrames als in reduziertem I/O.

---

## Verwandte Themen

- [Metadata.md](Metadata.md) — vollständige `_metadata`-/`_object_metadata`-Feldliste, Namenskonflikt-Regeln, `foreachBatch`-Fallstrick
- [Rescued Data.md](Rescued%20Data.md) — `_rescued_data` ist (anders als `_metadata`) eine **reguläre** Schema-Spalte und erscheint bei `SELECT *`, sobald sie aktiviert ist
- [File Filter.md](File%20Filter.md) — Filter **welche Dateien** gelesen werden, nicht **welche Spalten** einer Datei
- Deep-Dive: [.../05 Diagnose- und Herkunftsspalten/_metadata.md](07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/05%20Diagnose-%20und%20Herkunftsspalten/_metadata.md)
