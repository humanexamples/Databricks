[← Übersicht](00%20Uebersicht.md)

# Fall 10 – Mehrere Quellordner → eine Zieltabelle (Multiplex)

**A) Mehrere Append-Flows auf dieselbe Streaming Table (SQL)**

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.orders_bronze;

CREATE FLOW f_bright_home AS INSERT INTO catalog.schema.orders_bronze BY NAME
SELECT *, _metadata.file_name AS source_file
FROM STREAM read_files('/Volumes/catalog/schema/landing/bright_home/', format => 'csv', header => true);

CREATE FLOW f_lumina AS INSERT INTO catalog.schema.orders_bronze BY NAME
SELECT *, _metadata.file_name AS source_file
FROM STREAM read_files('/Volumes/catalog/schema/landing/lumina/', format => 'csv', header => true);
```

**B) Python-Pipeline mit `@dp.append_flow`**

```python
from pyspark import pipelines as dp

dp.create_streaming_table("orders_bronze")

for src in ["bright_home", "lumina", "northstar"]:
    @dp.append_flow(target="orders_bronze", name=f"f_{src}")
    def _flow(src=src):
        return (spark.readStream.format("cloudFiles")
                .option("cloudFiles.format", "csv").option("header", "true")
                .load(f"/Volumes/catalog/schema/landing/{src}/"))
```

**C) Ein gemeinsamer Wurzelpfad mit `recursiveFileLookup`** – wenn alle Unterordner dasselbe Format/Schema haben:

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.orders_bronze
AS SELECT *, _metadata.file_path AS file_path
FROM STREAM read_files('/Volumes/catalog/schema/landing/', format => 'csv',
                       header => true, recursiveFileLookup => true);
```

**D) Glob-Pfad** für gezielte Struktur:

```sql
... FROM STREAM read_files('/Volumes/catalog/schema/landing/*/orders/*.json', format => 'json')
```

---
[← Vorheriger Fall](09%20Korrektur%2C%20Teilmenge%20neu%20laden.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](11%20Schema%20aendert%20sich%20ueber%20die%20Zeit.md)
