[← Übersicht](00%20Uebersicht.md)

# Fall 6 – Dateien enthalten Change-Events (insert/update/delete mit Sequenz)

**A) `AUTO CDC INTO` – SQL, SCD Type 1**

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.users_current;

CREATE FLOW apply_cdc AS AUTO CDC INTO catalog.schema.users_current
FROM STREAM read_files('/Volumes/catalog/schema/landing/cdc/', format => 'json')
KEYS (userId)
APPLY AS DELETE WHEN operation = 'DELETE'
APPLY AS TRUNCATE WHEN operation = 'TRUNCATE'
SEQUENCE BY sequenceNum
COLUMNS * EXCEPT (operation, sequenceNum)
STORED AS SCD TYPE 1;
```

**B) `AUTO CDC INTO` – SQL, SCD Type 2**

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.users_history;

CREATE FLOW apply_cdc AS AUTO CDC INTO catalog.schema.users_history
FROM STREAM read_files('/Volumes/catalog/schema/landing/cdc/', format => 'json')
KEYS (userId)
APPLY AS DELETE WHEN operation = 'DELETE'
SEQUENCE BY sequenceNum
COLUMNS * EXCEPT (operation, sequenceNum)
STORED AS SCD TYPE 2;
```

**C) `create_auto_cdc_flow` – Python**

```python
from pyspark import pipelines as dp
from pyspark.sql.functions import col, expr

@dp.view
def users_cdf():
    return (spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "json")
            .load("/Volumes/catalog/schema/landing/cdc/"))

dp.create_streaming_table("users_current")
dp.create_auto_cdc_flow(
    target             = "users_current",
    source             = "users_cdf",
    keys               = ["userId"],
    sequence_by        = col("sequenceNum"),
    apply_as_deletes   = expr("operation = 'DELETE'"),
    except_column_list = ["operation", "sequenceNum"],
    stored_as_scd_type = 1)
```

**D) Manuell mit `foreachBatch` + `MERGE`** – siehe [Dedup-/Upsert-Muster, Abschnitt B](99%20Dedup%20und%20Upsert%20Muster.md).

---
[← Vorheriger Fall](05%20Periodische%20Voll-Snapshots.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](07%20Backfill%20zusaetzlich%20zum%20Stream.md)
