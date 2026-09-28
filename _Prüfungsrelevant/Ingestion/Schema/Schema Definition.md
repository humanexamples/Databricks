# Schema Definition (`StructType` / `.schema()`)

## Worum geht es?

Statt das Schema von Databricks **ableiten** zu lassen ([Schema Inference.md](Schema%20Inference.md)), gibt man es **explizit** vor. Dafür gibt es zwei gleichwertige Schreibweisen: den **DDL-String** (z. B. `"id INT, ts TIMESTAMP, event STRING"`) — kurz, gut geeignet für SQL (`read_files(schema => '...')`) und schnelle Notebooks — sowie **`StructType`/`StructField`** als programmatische Variante (siehe unten) — wiederverwendbar, testbar, aus Code oder Config generierbar, mit feingranularer Kontrolle über `nullable` und `metadata`.

**Warum explizit?**

- **Kein Inferenz-Lesevorgang** → schneller, deterministisch (siehe [Schema Inference.md](Schema%20Inference.md), Abschnitt „Batch").
- **Vertrag / Datenqualität:** abweichende Felder werden nicht stillschweigend übernommen, sondern landen in der Rescued-Data-Spalte ([Rescued Data.md](Rescued%20Data.md)).
- **Streaming (Auto Loader):** ein angegebenes Schema setzt `schemaEvolutionMode` standardmäßig auf `none` — neue Spalten werden ignoriert statt den Stream zu stoppen ([Schema Evolution.md](Schema%20Evolution.md), Abschnitt C).

---

## `StructType` / `StructField` aufbauen

```python
from pyspark.sql.types import (
    StructType, StructField,
    StringType, IntegerType, LongType, DoubleType, BooleanType,
    TimestampType, DateType, DecimalType,
    ArrayType, MapType,
)

schema = StructType([
    StructField("id",        LongType(),      nullable=False),
    StructField("event",     StringType(),    nullable=True),
    StructField("amount",    DecimalType(10, 2)),
    StructField("ts",        TimestampType()),
])
```

- `StructField(name, dataType, nullable=True, metadata=None)` — `nullable` ist der dritte Parameter, Default `True`.
- `metadata` ist ein Dict (z. B. `{"comment": "Primärschlüssel"}`), nützlich u. a. für Spaltenkommentare.
- Kurzform mit DDL-String (identisches Ergebnis):

```python
schema = "id LONG, event STRING, amount DECIMAL(10,2), ts TIMESTAMP"
```

### Verschachtelte Typen

```python
schema = StructType([
    StructField("user", StructType([
        StructField("name", StringType()),
        StructField("age",  IntegerType()),
    ])),
    StructField("tags",   ArrayType(StringType())),
    StructField("orders", ArrayType(StructType([
        StructField("order_id", StringType()),
        StructField("total",    DoubleType()),
    ]))),
    StructField("props",  MapType(StringType(), StringType())),
])
```

DDL-Äquivalent:

```
user STRUCT<name: STRING, age: INT>,
tags ARRAY<STRING>,
orders ARRAY<STRUCT<order_id: STRING, total: DOUBLE>>,
props MAP<STRING, STRING>
```

---

## `.schema()` beim Lesen anwenden

### Batch (`spark.read`)

```python
df = (spark.read
      .schema(schema)                 # StructType ODER DDL-String
      .json("/Volumes/cat/sch/vol/events"))

# format-agnostisch:
df = spark.read.format("csv").option("header", "true").schema(schema).load(path)
```

- `.schema()` akzeptiert **sowohl** ein `StructType` **als auch** einen DDL-String.
- Ohne `.schema()` → Inferenz. Mit `.schema()` → keine Inferenz.
- `spark.read` rettet abweichende Werte **nicht** automatisch — `rescuedDataColumn` explizit setzen ([Rescued Data.md](Rescued%20Data.md)).

### Streaming / Auto Loader

```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .schema(schema)                 # kein schemaLocation nötig, wenn Schema fix
      .load("/Volumes/cat/sch/vol/events"))
```

- Mit festem `.schema()` ist `cloudFiles.schemaLocation` nicht erforderlich.
- Default `schemaEvolutionMode` = `none`; für Evolution trotz Schema explizit z. B. `addNewColumns` + `schemaLocation` setzen ([Schema Evolution.md](Schema%20Evolution.md)).

### SQL / `read_files`

`read_files` kennt nur den **DDL-String** über den `schema`-Parameter (kein `StructType`):

```sql
SELECT * FROM read_files('/Volumes/cat/sch/vol/events', format => 'json',
  schema => 'id LONG, event STRING, ts TIMESTAMP');
```

Siehe [Schema Inference.md](Schema%20Inference.md).

**Ist eine Schema-Angabe hier eigentlich Pflicht oder optional?** Bei den meisten Lesewegen optional (Inferenz als Fallback) — nur bei `spark.readStream()` ohne Auto Loader und bei `COPY INTO` gelten Besonderheiten. Vollständige Übersicht: [Schema-Pflicht.md](Schema-Pflicht.md).

---

## Schema wiederverwenden, ableiten, umwandeln

```python
df.printSchema()                 # Baumdarstellung
df.schema                        # StructType-Objekt
df.schema.simpleString()         # "struct<id:bigint,event:string,...>"
df.schema.json()                 # JSON-Repräsentation

# JSON <-> StructType (z. B. Schema in Datei/Config ablegen)
import json
StructType.fromJson(json.loads(df.schema.json()))

# DDL-String -> StructType
from pyspark.sql.types import _parse_datatype_string
_parse_datatype_string("id LONG, event STRING")

# Schema einer Beispiel-Datei einmalig ableiten und dann fest verdrahten
inferred = spark.read.option("inferSchema", "true").json(sample_path).schema
print(inferred.simpleString())   # Ergebnis kopieren und als festes Schema übernehmen
```

Muster: Schema **einmal** per Inferenz bestimmen, prüfen, als `StructType`/DDL in den Code (oder eine Config-Datei) übernehmen → ab dann deterministisch und ohne Inferenz-Kosten.

---

## Anwenden auf einen bestehenden DataFrame

`.schema()` gibt es nur am Reader. Einen bereits gelesenen DataFrame an ein Zielschema angleichen:

```python
from pyspark.sql.functions import col

df_typed = df.select([
    col(f.name).cast(f.dataType).alias(f.name) for f in schema.fields
])
```

Bei `createDataFrame` kann `StructType` direkt übergeben werden:

```python
spark.createDataFrame(rows, schema)
```

---

## Verwandte Themen

- [Schema-Pflicht.md](Schema-Pflicht.md) · [Schema Inference.md](Schema%20Inference.md) · [Schema Enforcement.md](Schema%20Enforcement.md) · [Schema Evolution.md](Schema%20Evolution.md) · [Rescued Data.md](Rescued%20Data.md)
- Deep-Dive im Projekt: [07 Data Management/01 Data Engineering/02 Lakeflow Connect/02 Lakeflow Connect Standard Connectors/05 Working with Files/_read_files.md](07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/_read_files.md)
