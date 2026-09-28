[← Übersicht](00%20Uebersicht.md)

# Fall 11 – Schema ändert sich über die Zeit (neue Spalten, Typänderungen)

**A) Auto Loader – neue Spalten automatisch aufnehmen** (`addNewColumns`, Default bei aktiver Inferenz). Der Stream stoppt bei neuer Spalte einmal und muss neu gestartet werden (im Job automatisch):

```python
.option("cloudFiles.schemaLocation", checkpoint)
.option("cloudFiles.schemaEvolutionMode", "addNewColumns")
```

**B) Unerwartete Felder auffangen statt Stopp** (`rescue`):

```python
.option("cloudFiles.schemaEvolutionMode", "rescue")   # Extra-Daten landen in _rescued_data
```

Weitere Modi: `none` (ignorieren), `failOnNewColumns` (hart abbrechen). Details: [../Schema Evolution.md](../Schema%20Evolution.md), [../Rescued Data.md](../Rescued%20Data.md).

**C) Typen fixieren / Hinweise geben**:

```python
.option("cloudFiles.inferColumnTypes", "true")
.option("cloudFiles.schemaHints", "order_id BIGINT, order_total DECIMAL(10,2)")
```

**D) `COPY INTO` mit Schema-Evolution**:

```sql
COPY INTO catalog.schema.bronze
FROM '/Volumes/catalog/schema/landing/'
FILEFORMAT = PARQUET
COPY_OPTIONS ('mergeSchema' = 'true');
```

**E) Alles als `VARIANT`** – maximal robust gegen Schemaänderungen:

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.bronze_variant
AS SELECT * FROM STREAM read_files('/Volumes/catalog/schema/landing/', format => 'json',
                                   schemaEvolutionMode => 'none')
-- oder gezielt: SELECT parse_json(value) AS data FROM STREAM read_files(..., format => 'text')
```

**F) `MERGE WITH SCHEMA EVOLUTION`** beim Upsert:

```sql
MERGE WITH SCHEMA EVOLUTION INTO catalog.schema.target t
USING incoming s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

---
[← Vorheriger Fall](10%20Mehrere%20Quellordner%20%28Multiplex%29.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](12%20Zeitfenster-%20und%20gefilterte%20Ingestion.md)
