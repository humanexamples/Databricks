[← Übersicht](00%20Uebersicht.md)

# Muster: Korrigierte Dateien mit gleichem Namen

**Ausgangslage:** Eine Datei wurde schon geladen. Später kommt eine korrigierte Version **mit demselben Namen**.

**Problem:** `COPY INTO` überspringt sie, denn bereits geladene Dateien werden auch dann übersprungen, wenn sie geändert wurden.

**Lösungsidee in drei Schritten:**
1. In Bronze bei jeder Zeile Dateiname und Änderungszeit mitspeichern.
2. Korrigierte Dateien gezielt mit `force` nachladen. Bronze bekommt dadurch beide Versionen.
3. In Silver pro Datei oder pro Schlüssel nur die neueste Version behalten.

---

## Schritt 1: Bronze mit Herkunft laden

```sql
CREATE TABLE IF NOT EXISTS main.bronze.sales;

COPY INTO main.bronze.sales
FROM (
  SELECT *,
         _metadata.file_name              AS src_file,
         _metadata.file_modification_time AS src_file_ts,
         current_timestamp()              AS ingest_ts
  FROM '/Volumes/main/raw/landing/sales'
)
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true', 'mergeSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');
```

---

## Schritt 2: Korrigierte Dateien nachladen

### Fall A: Du kennst die Dateinamen

```sql
COPY INTO main.bronze.sales
FROM (
  SELECT *,
         _metadata.file_name              AS src_file,
         _metadata.file_modification_time AS src_file_ts,
         current_timestamp()              AS ingest_ts
  FROM '/Volumes/main/raw/landing/sales'
)
FILEFORMAT = CSV
FILES = ('sales_2026-09-01.csv')          -- höchstens 1000 Namen
FORMAT_OPTIONS ('header' = 'true')
COPY_OPTIONS ('force' = 'true');
```

### Fall B: Du kennst die Dateinamen nicht

Du nimmst den neuesten Änderungszeitpunkt, der schon in Bronze steht. Mit `modifiedAfter` + `force` werden dann alle Dateien geladen, die **danach** geändert wurden, egal ob neu oder korrigiert.

```python
landing = "/Volumes/main/raw/landing/sales"

last_ts = spark.sql("""
    SELECT date_format(max(src_file_ts), "yyyy-MM-dd'T'HH:mm:ss")
    FROM main.bronze.sales
""").first()[0]

# Erster Lauf (Bronze leer): ohne Zeitfilter laden
modified_after = f", 'modifiedAfter' = '{last_ts}'" if last_ts else ""

spark.sql(f"""
    COPY INTO main.bronze.sales
    FROM (SELECT *,
                 _metadata.file_name              AS src_file,
                 _metadata.file_modification_time AS src_file_ts,
                 current_timestamp()              AS ingest_ts
          FROM '{landing}')
    FILEFORMAT = CSV
    FORMAT_OPTIONS ('header' = 'true'{modified_after})
    COPY_OPTIONS ('force' = 'true')
""")
```

Worauf du achten musst:
- Die korrigierte Datei muss beim Ablegen einen **neuen Änderungszeitpunkt** bekommen. Wird beim Kopieren der alte Zeitstempel beibehalten, wird sie übersehen.
- `modifiedAfter` erwartet das Format `YYYY-MM-DDTHH:mm:ss`, also ohne Sekundenbruchteile. Eine Datei, die in derselben Sekunde wie der Stand geändert wurde, kann deshalb ein zweites Mal geladen werden. Solche Duplikate fängt Schritt 3 in Silver ab.
- `modifiedAfter` nimmt nur Dateien, die **nach** dem Zeitpunkt geändert wurden.
- **Nie `force` ohne Filter** verwenden. Sonst wird bei jedem Lauf der ganze Ordner noch einmal angehängt.

### Fall C: Geladene Dateien wegräumen

Nach jedem Lauf verschiebst du die geladenen Dateien in einen Archiv-Ordner. Im Landing-Ordner liegt dann nur, was noch nicht geladen ist. Eine korrigierte Datei landet dort einfach wieder. Mit `force` wird sie beim nächsten Lauf geladen, und du brauchst keinen Zeitfilter.

```python
landing = "/Volumes/main/raw/landing/sales"
archive = "/Volumes/main/raw/archive/sales"

spark.sql(f"""
    COPY INTO main.bronze.sales
    FROM (SELECT *, _metadata.file_name AS src_file,
                 _metadata.file_modification_time AS src_file_ts,
                 current_timestamp() AS ingest_ts
          FROM '{landing}')
    FILEFORMAT = CSV
    FORMAT_OPTIONS ('header' = 'true')
    COPY_OPTIONS ('force' = 'true')
""")

for f in dbutils.fs.ls(landing):
    dbutils.fs.mv(f.path, f"{archive}/{f.name}")
```

Das setzt voraus, dass während eines Laufs keine neuen Dateien ankommen. Sonst würde eine noch nicht geladene Datei mit ins Archiv verschoben.

---

## Schritt 3: In Silver die neueste Version behalten

### Variante 1: Die korrigierte Datei ersetzt die alte komplett

```sql
CREATE OR REPLACE TABLE main.silver.sales AS
SELECT * FROM main.bronze.sales
QUALIFY src_file_ts = max(src_file_ts) OVER (PARTITION BY src_file);
```

```
Bronze:  sales_01.csv | 09-01 08:00 | 3 Zeilen   ← alte Version
         sales_01.csv | 09-26 14:30 | 3 Zeilen   ← Korrektur
Silver:  sales_01.csv | 09-26 14:30 | 3 Zeilen   ← nur die Korrektur
```

### Variante 2: Es gibt einen fachlichen Schlüssel (z. B. `order_id`)

```sql
MERGE INTO main.silver.sales t
USING (
  SELECT * FROM main.bronze.sales
  QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY src_file_ts DESC) = 1
) s
ON t.order_id = s.order_id
WHEN MATCHED AND s.src_file_ts > t.src_file_ts THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

`main.silver.sales` braucht dafür die Spalte `src_file_ts`.

### Variante 3: Direkt in Bronze ersetzen

Das ist nur sinnvoll, wenn in Bronze **keine** Historie gebraucht wird.

```sql
DELETE FROM main.bronze.sales WHERE src_file = 'sales_2026-09-01.csv';
-- danach COPY INTO mit FILES = ('sales_2026-09-01.csv') und force = true
```

---

## Alternative: Auto Loader

Mit `cloudFiles.allowOverwrites = true` (Standard `false`) dürfen Änderungen an Dateien im Eingabeordner bestehende Daten überschreiben. Dann brauchst du keine eigene Logik, um die Dateien zu finden. Schritt 3 in Silver bleibt aber nötig. Siehe [../Datei Ingestion Varianten/03 Gleiche Datei wird ueberschrieben.md](../Datei%20Ingestion%20Varianten/03%20Gleiche%20Datei%20wird%20ueberschrieben.md).

Zusätzlich: Soll nur eine Teilmenge neu geladen werden, geht das mit `COPY INTO` leichter als mit Auto Loader. `COPY INTO` kann dafür auch parallel zu einem laufenden Auto-Loader-Stream eingesetzt werden. Siehe [../Datei Ingestion Varianten/09 Korrektur, Teilmenge neu laden.md](../Datei%20Ingestion%20Varianten/09%20Korrektur,%20Teilmenge%20neu%20laden.md).
