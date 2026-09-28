[← Übersicht](00%20Uebersicht.md)

# Fall 5 – Periodische Voll-Snapshots (jede Lieferung = kompletter aktueller Stand)

**A) `create_auto_cdc_from_snapshot_flow` – ein Snapshot pro Pipeline-Lauf** (Python, Lakeflow Declarative Pipelines)

```python
from pyspark import pipelines as dp

@dp.view(name="source")
def source():
    return spark.read.table("catalog.schema.snapshot")   # oder read_files auf den neuesten Ordner

dp.create_streaming_table("catalog.schema.target")
dp.create_auto_cdc_from_snapshot_flow(
    target             = "catalog.schema.target",
    source             = "source",
    keys               = ["userId"],
    stored_as_scd_type = 2)          # 1 = überschreiben, 2 = Historie
```

**B) `create_auto_cdc_from_snapshot_flow` – mehrere versionierte Snapshots** (Snapshot-Funktion, die je Aufruf den nächsten Snapshot + Version liefert)

```python
from pyspark import pipelines as dp
from typing import Optional, Tuple
from pyspark.sql import DataFrame

def next_snapshot_and_version(latest_version: Optional[int]) -> Optional[Tuple[DataFrame, int]]:
    base = "/Volumes/catalog/schema/snapshots/"
    versions = sorted(
        int(f.name.replace("snapshot_", "").replace(".csv", ""))
        for f in dbutils.fs.ls(base)
        if f.name.startswith("snapshot_") and f.name.endswith(".csv")
    )
    candidates = versions if latest_version is None else [v for v in versions if v > latest_version]
    if not candidates:
        return None
    v = candidates[0]
    df = spark.read.format("csv").option("header", True).load(f"{base}snapshot_{v}.csv")
    return (df, v)

dp.create_streaming_table("catalog.schema.target_versioned")
dp.create_auto_cdc_from_snapshot_flow(
    target             = "catalog.schema.target_versioned",
    source             = next_snapshot_and_version,
    keys               = ["userId"],
    stored_as_scd_type = 2)
```

> Snapshots müssen in **aufsteigender** Version verarbeitet werden; out-of-order-Snapshots werden ignoriert.

**C) Manuell mit `MERGE` (SCD Type 1)** – ohne Pipelines, reiner SQL-Job:

```sql
CREATE OR REPLACE TEMP VIEW snap AS
SELECT * FROM read_files('/Volumes/catalog/schema/landing/latest/', format => 'csv', header => true);

MERGE INTO catalog.schema.target t
USING snap s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *
WHEN NOT MATCHED BY SOURCE THEN DELETE;   -- im Ziel entfernen, was im Snapshot fehlt
```

**D) Manuell SCD Type 2 mit `MERGE`** – Gültigkeitsspalten (`valid_from`, `valid_to`, `is_current`) selbst pflegen; Standardmuster mit zwei `MERGE`-Schritten oder `MERGE … WHEN MATCHED AND t.hash <> s.hash`.

**E) Voll-Ersetzen** (keine Historie, kein Key-Abgleich nötig):

```sql
CREATE OR REPLACE TABLE catalog.schema.target AS
SELECT * FROM read_files('/Volumes/catalog/schema/landing/latest/', format => 'csv', header => true);
```

---
[← Vorheriger Fall](04%20Datei%20waechst.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](06%20Change-Events%20in%20Dateien.md)
