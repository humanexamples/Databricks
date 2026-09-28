[← Übersicht](00%20Uebersicht.md)

# Fall 9 – Korrigierte Dateien / Teilmenge neu laden

**A) `COPY INTO` mit `FILES`** – genau die benannten Dateien neu einspielen:

```sql
COPY INTO catalog.schema.bronze
FROM '/Volumes/catalog/schema/landing/'
FILEFORMAT = JSON
FILES = ('orders_2026-08-30.json', 'orders_2026-08-31.json')
COPY_OPTIONS ('force' = 'true');
```

**B) `COPY INTO` mit `PATTERN` + `force`** – ganze Gruppe neu:

```sql
COPY INTO catalog.schema.bronze
FROM '/Volumes/catalog/schema/landing/'
FILEFORMAT = JSON
PATTERN = 'orders_2026-08-*.json'
COPY_OPTIONS ('force' = 'true');
```

**C) Auto Loader**: keine selektive Neuverarbeitung. Wege:
- korrigierte Datei **unter neuem Namen** ablegen (sauberste Lösung), oder
- `cloudFiles.allowOverwrites = true` und die Datei am gleichen Pfad ersetzen, danach Upsert.

**D) Ziel-Partition gezielt überschreiben** (wenn nach Datum partitioniert):

```sql
INSERT OVERWRITE catalog.schema.bronze
SELECT * FROM read_files('/Volumes/catalog/schema/landing/', format => 'json',
                         modifiedAfter => '2026-08-30', modifiedBefore => '2026-09-01');
```

**E) `REPLACE WHERE`** für einen gezielten Bereich:

```sql
INSERT INTO catalog.schema.bronze REPLACE WHERE order_date >= '2026-08-30' AND order_date < '2026-09-01'
SELECT * FROM read_files('/Volumes/.../corrected/', format => 'json');
```

---
[← Vorheriger Fall](08%20Spaete%2C%20unsortierte%20Dateien.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](10%20Mehrere%20Quellordner%20%28Multiplex%29.md)
