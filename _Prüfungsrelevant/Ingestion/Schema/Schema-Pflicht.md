# Schema-Pflicht

**Wann ist eine Schema-Angabe zwingend notwendig?** Übersicht über alle relevanten Lesewege: Bei den meisten ist eine explizite Schema-Angabe **optional** (Inferenz als Fallback, siehe [Schema Inference.md](Schema%20Inference.md)) — nur in wenigen, klar abgrenzbaren Fällen ist sie **zwingend**.

Bei **`read_files()`** im Batch-Modus (SQL) ist die Schema-Angabe optional: Das Schema wird automatisch aus allen Dateien inferiert (außer bei `BINARYFILE`/`TEXT`, wo es ohnehin fest vorgegeben ist). Bei **`STREAM read_files(...)`** (SQL, intern Auto Loader) und bei **Auto Loader** selbst (Python `cloudFiles` oder SQL) ist sie ebenfalls optional — mit einer Ausnahme: Ist das Quellverzeichnis beim allerersten Start leer, wird ein Schema zwingend benötigt, weil ohne vorhandene Daten nichts inferiert werden kann. `STREAM read_files` nutzt intern dieselbe `cloudFiles`-Quelle, daher verhält es sich in Python und SQL identisch.

Bei **`spark.readStream()` ohne `cloudFiles`** — der klassischen Structured-Streaming-File-Source — ist eine Schema-Angabe dagegen **zwingend erforderlich**, und zwar als Standardverhalten: Spark verbietet Schema-Inferenz für Streaming-Quellen grundsätzlich, um über Neustarts und Failures hinweg ein konsistentes Schema zu garantieren.

Bei **`spark.read()`** im Batch-Modus ist die Schema-Angabe optional: Für JSON, Parquet, Avro, ORC und Delta ist Inferenz immer möglich; bei CSV nur mit der Option `inferSchema=true` (ohne sie werden alle Spalten als `string` gelesen — kein Fehler, nur ungetypt).

Bei **`COPY INTO`** ist die Situation anders gelagert: Der Befehl selbst besitzt gar keinen `schema`-Parameter, da er immer in eine bereits vorhandene Delta-Tabelle schreibt. Die Zieltabelle muss also existieren — entweder mit vorab per `CREATE TABLE` festgelegtem Schema, oder als schemalose Platzhaltertabelle, deren Schema erst über `mergeSchema` aus den Quelldaten abgeleitet wird.

## `spark.readStream()` ohne Auto Loader — der einzige Fall mit echtem Zwang

```python
# Wirft standardmäßig einen Fehler ohne .schema(...):
# "Schema must be specified when creating a streaming source DataFrame"
df = spark.readStream.format("json").load("/Volumes/cat/sch/vol/events")

# Explizites Schema macht es lauffähig
df = spark.readStream.format("json").schema(schema).load("/Volumes/cat/sch/vol/events")

# Alternative (laut Doku nur für Ad-hoc-Fälle gedacht, nicht für Produktion):
spark.conf.set("spark.sql.streaming.schemaInference", "true")
```

Betrifft **nur** die generische `spark.readStream.format("json"/"csv"/"parquet"/...)`-Dateiquelle — sobald `cloudFiles` (Auto Loader) verwendet wird, entfällt dieser Zwang (siehe oben).

## `COPY INTO` — Schema kommt nie direkt aus der Anweisung selbst

```sql
-- Weg 1: Zieltabelle vorab MIT Schema anlegen
CREATE TABLE my_table (id INT, event STRING, ts TIMESTAMP);
COPY INTO my_table FROM '/path' FILEFORMAT = JSON;

-- Weg 2: Schemalose Platzhaltertabelle anlegen, Schema erst beim ersten COPY INTO ableiten
CREATE TABLE IF NOT EXISTS my_table;
COPY INTO my_table FROM '/path' FILEFORMAT = JSON
  COPY_OPTIONS ('mergeSchema' = 'true');
```

## Auto Loader / `STREAM read_files` — Schema-Zwang nur bei leerem Verzeichnis

Ist das Quellverzeichnis beim allerersten Start leer, verlangt Auto Loader (und damit auch `STREAM read_files`, das intern Auto Loader nutzt) zwingend ein Schema — es gibt keine Daten, aus denen inferiert werden könnte.

---

## Verwandte Themen

- [Schema Definition.md](Schema%20Definition.md) · [Schema Inference.md](Schema%20Inference.md) · [Schema Enforcement.md](Schema%20Enforcement.md) · [Schema Evolution.md](Schema%20Evolution.md)
- [Schema-on-Read vs. Schema-on-Write.md](Schema-on-Read%20vs.%20Schema-on-Write.md)
