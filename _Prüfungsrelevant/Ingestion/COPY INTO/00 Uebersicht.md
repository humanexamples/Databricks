# COPY INTO – Übersicht

`COPY INTO` ist ein SQL-Befehl. Er lädt Dateien aus einem Speicherort in eine **bestehende Delta-Tabelle**.

Die drei wichtigsten Eigenschaften:

- **Idempotent:** Bereits geladene Dateien werden beim nächsten Lauf übersprungen.
- **Wiederholbar (retryable):** Schlägt ein Lauf fehl, startest du ihn einfach neu.
- **Inkrementell:** Jeder Lauf lädt nur die Dateien, die neu dazugekommen sind.

```sql
CREATE TABLE IF NOT EXISTS main.bronze.orders;

COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true', 'inferSchema' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');

-- Zweiter Lauf direkt danach: lädt nichts, alle Dateien sind schon bekannt.
```

## Was COPY INTO kann

- Datei- und Ordnerfilter für S3, ADLS, ABFS, GCS und Unity-Catalog-Volumes
- Formate: CSV, JSON, XML, Avro, ORC, Parquet, Text, Binärdateien, außerdem Excel
- Standardmäßig genau einmal pro Datei (exactly-once)
- Schema-Inferenz, Spalten-Mapping und Schema-Evolution der Zieltabelle
- Nutzbar in Databricks SQL, in Notebooks und in Lakeflow Jobs

## Wann COPY INTO, wann Auto Loader?

**Dateimenge:**
- Tausende Dateien über die Zeit → `COPY INTO` reicht.
- Millionen Dateien oder mehr → Auto Loader. Er braucht weniger Operationen, um Dateien zu finden, und kann in mehrere Batches aufteilen. Bei großen Mengen ist er deshalb günstiger und effizienter.

**Häufige Schemaänderungen:** Auto Loader kann Schemas besser ableiten und weiterentwickeln.

**Ausgewählte Dateien neu laden:** Das geht mit `COPY INTO` leichter. Bei Auto Loader ist es schwerer, gezielt eine Teilmenge erneut zu verarbeiten. Du kannst aber `COPY INTO` für die Teilmenge laufen lassen, während parallel ein Auto-Loader-Stream läuft.

```sql
-- Nur zwei erneut hochgeladene Dateien nachladen
COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
FILES = ('orders_2026-09-01.csv', 'orders_2026-09-02.csv')
FORMAT_OPTIONS ('header' = 'true')
COPY_OPTIONS ('force' = 'true');
```

**Empfehlung für SQL-Nutzer:** Streaming Tables (`CREATE STREAMING TABLE`) skalieren besser und sind robuster. Sie sind die empfohlene Alternative zu `COPY INTO`. Auch in der Referenz der Format-Optionen wird `COPY INTO` als „legacy“ bezeichnet.

```sql
-- Empfohlene Alternative: Streaming Table mit Auto Loader
CREATE OR REFRESH STREAMING TABLE main.bronze.orders_st
AS SELECT * FROM STREAM read_files(
  '/Volumes/main/raw/landing/orders',
  format => 'csv',
  header => true
);
```

## Nicht verwechseln

- **`copy_file()` / `try_copy_file()`** sind SQL-Funktionen ab Databricks Runtime 18 (Beta). Sie kopieren **eine einzelne Datei** an einen anderen Pfad und geben eine `FILE`-Referenz zurück. Mit dem Laden in eine Tabelle haben sie nichts zu tun.

```sql
SELECT copy_file(
  to_file('/Volumes/source/data/input.csv'),
  destination => '/Volumes/target/data/output.csv',
  if_file_exists_mode => 'skip'      -- 'error' (Standard) | 'overwrite' | 'skip'
);

-- try_copy_file liefert NULL statt eines Fehlers, wenn die Quelldatei fehlt
SELECT try_copy_file(deleted_file, destination => '/Volumes/archive/reports/report.pdf');
```

- **`LOAD DATA`** ist ein eigener Befehl (Hive-Stil). Er verweist nur auf `COPY INTO` als verwandten Befehl.

## Dateien in diesem Ordner

- [01 Syntax und Parameter](01%20Syntax%20und%20Parameter.md)
- [02 Idempotenz, File Tracking und force](02%20Idempotenz,%20File%20Tracking%20und%20force.md)
- [03 Zieltabelle und Schema](03%20Zieltabelle%20und%20Schema.md)
- [04 Dateiformate und Format-Optionen](04%20Dateiformate%20und%20Format-Optionen.md)
- [05 Metadatenspalten](05%20Metadatenspalten.md)
- [06 Datenzugriff/](06%20Datenzugriff/)
  - [01 Volumes und External Locations](06%20Datenzugriff/01%20Volumes%20und%20External%20Locations.md)
  - [02 Temporaere Credentials und Verschluesselung](06%20Datenzugriff/02%20Temporaere%20Credentials%20und%20Verschluesselung.md)
  - [03 Admin-Konfiguration und Instance Profile](06%20Datenzugriff/03%20Admin-Konfiguration%20und%20Instance%20Profile.md)
- [07 Tutorials](07%20Tutorials.md)
- [08 Weitere Quellen (SharePoint, OneDrive, Google Drive, Zerobus)](08%20Weitere%20Quellen%20%28SharePoint,%20OneDrive,%20Google%20Drive,%20Zerobus%29.md)
- [09 Betrieb (Parallelitaet, Transaktionen, Historie, VACUUM, CLONE)](09%20Betrieb%20%28Parallelitaet,%20Transaktionen,%20Historie,%20VACUUM,%20CLONE%29.md)
- [10 Fehlermeldungen](10%20Fehlermeldungen.md)
- [11 Muster - Korrigierte Dateien mit gleichem Namen](11%20Muster%20-%20Korrigierte%20Dateien%20mit%20gleichem%20Namen.md)
