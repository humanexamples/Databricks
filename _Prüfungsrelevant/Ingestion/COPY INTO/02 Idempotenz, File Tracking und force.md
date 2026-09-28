[← Übersicht](00%20Uebersicht.md)

# Idempotenz, File Tracking und `force`

## Grundregel

`COPY INTO` merkt sich, welche Dateien schon in die Zieltabelle geladen wurden. Diese Dateien werden bei späteren Läufen **übersprungen**. Das gilt **auch dann, wenn eine Datei nach dem Laden verändert wurde.**

```sql
COPY INTO my_json_data
FROM 's3://my-bucket/jsonData'
FILEFORMAT = JSON
FILES = ('f1.json', 'f2.json', 'f3.json', 'f4.json', 'f5.json');

-- Der zweite Lauf kopiert nichts, weil der erste die Daten schon geladen hat
COPY INTO my_json_data
FROM 's3://my-bucket/jsonData'
FILEFORMAT = JSON
FILES = ('f1.json', 'f2.json', 'f3.json', 'f4.json', 'f5.json');
```

Deshalb kannst du denselben Befehl als Job regelmäßig laufen lassen. Er lädt jedes Mal **nur neue Dateien**.

```
Lauf 1:  a.csv, b.csv          → beide geladen
Lauf 2:  a.csv, b.csv, c.csv   → nur c.csv geladen
Lauf 3:  a.csv (überschrieben) → nichts geladen, a.csv ist schon bekannt
```

Der Zustand „schon geladen“ liegt im **Delta-Log der Zieltabelle**. Zwei verschiedene Zieltabellen, die aus demselben Ordner laden, haben also jeweils ihren eigenen Stand.

---

## `force = true` – Idempotenz abschalten

Mit `force` werden Dateien geladen, egal ob sie schon geladen wurden.

```sql
COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true')
COPY_OPTIONS ('force' = 'true');
```

**Wichtig: `force` überschreibt nichts.** `COPY INTO` hängt immer an. Mit `force` werden die Zeilen einer bereits geladenen Datei **noch einmal angehängt**.

```sql
-- sales_01.csv (3 Zeilen) wurde schon geladen, jetzt kommt eine korrigierte Version
COPY INTO main.bronze.sales
FROM (SELECT *, _metadata.file_name AS src_file,
             _metadata.file_modification_time AS src_file_ts
      FROM '/Volumes/main/raw/landing/sales')
FILEFORMAT = CSV
FILES = ('sales_01.csv')
FORMAT_OPTIONS ('header' = 'true')
COPY_OPTIONS ('force' = 'true');

SELECT src_file, src_file_ts, count(*) FROM main.bronze.sales GROUP BY ALL;
-- sales_01.csv | 2026-09-01 08:00 | 3   ← alte Version bleibt
-- sales_01.csv | 2026-09-26 14:30 | 3   ← neue Version zusätzlich
```

**Vorsicht:** `force` ohne `FILES`, `PATTERN` oder `modifiedAfter` lädt **alle** Dateien im Ordner noch einmal. Jeder Lauf erzeugt dann Duplikate.

Gezielt einsetzen:

```sql
-- Nur bestimmte Dateien
... FILES = ('sales_01.csv', 'sales_02.csv')
    COPY_OPTIONS ('force' = 'true');

-- Nur Dateien, die nach einem Zeitpunkt geändert wurden
... FORMAT_OPTIONS ('header' = 'true', 'modifiedAfter' = '2026-09-26T00:00:00')
    COPY_OPTIONS ('force' = 'true');
```

---

## Zeitfilter: `modifiedAfter` und `modifiedBefore`

Diese allgemeinen Reader-Optionen gelten für alle Dateiformate, auch in `COPY INTO`. Sie filtern Dateien nach ihrem Änderungszeitpunkt. Der Wert ist ein Zeitstempel-String im Format `YYYY-MM-DDTHH:mm:ss`.

```sql
COPY INTO main.bronze.orders
FROM '/Volumes/main/raw/landing/orders'
FILEFORMAT = CSV
FORMAT_OPTIONS (
  'header'         = 'true',
  'modifiedAfter'  = '2026-09-01T00:00:00',   -- nur Dateien, die danach geändert wurden
  'modifiedBefore' = '2026-09-02T00:00:00'    -- und vor diesem Zeitpunkt
);
```

Ohne `force` gilt das File Tracking trotzdem weiter. Die Zeitfilter schränken nur ein, welche Dateien überhaupt betrachtet werden.

---

## Beschädigte Dateien werden nicht getrackt

Mit `ignoreCorruptFiles = true` (ab Databricks Runtime 11.3 LTS) werden beschädigte Dateien übersprungen. Sie gelten danach **nicht** als geladen. Sobald du die Datei reparierst, lädt der nächste Lauf sie automatisch.

```sql
COPY INTO my_table
FROM '/path/to/files'
FILEFORMAT = JSON
FORMAT_OPTIONS ('ignoreCorruptFiles' = 'true');
-- Ergebnisspalte num_skipped_corrupt_files = Anzahl übersprungener Dateien
```

Welche Dateien beschädigt sind, zeigt ein Lauf im `VALIDATE`-Modus:

```sql
COPY INTO my_table
FROM '/path/to/files'
FILEFORMAT = JSON
VALIDATE ALL
FORMAT_OPTIONS ('ignoreCorruptFiles' = 'true');
```

Die Zahl steht auch in der Tabellenhistorie unter `operationMetrics.numSkippedCorruptFiles`:

```sql
DESCRIBE HISTORY my_table;
```

---

## Fehlende Dateien

`ignoreMissingFiles` ist bei `COPY INTO` standardmäßig **`true`**, bei Auto Loader dagegen `false`. Wird eine Datei zwischen dem Auflisten und dem Lesen gelöscht, läuft `COPY INTO` also weiter.

---

## Wo der Zustand liegt und wie er aufgeräumt wird

- Der Zustand „welche Dateien sind geladen“ gehört zur Zieltabelle. Beim Laden nutzt `COPY INTO` einen RocksDB-State-Store. Seit einer Databricks-SQL-Version von 2024 wird dieser State asynchron geladen. Das beschleunigt den Start bei Tabellen mit sehr vielen schon geladenen Dateien.
- Ab Databricks Runtime 15.2 räumt `VACUUM` nicht mehr referenzierte Metadaten-Dateien auf, die `COPY INTO` für das Tracking angelegt hat. Am Verhalten von `COPY INTO` ändert das nichts.

```sql
VACUUM main.bronze.orders;
```

- Ein **Deep Clone** kopiert neben Daten und Schema auch die `COPY INTO`-Metadaten der Quelltabelle. Ein Shallow Clone kopiert sie nicht.

```sql
CREATE TABLE main.bronze.orders_copy DEEP CLONE main.bronze.orders;     -- mit COPY-INTO-Metadaten
CREATE TABLE main.bronze.orders_sc   SHALLOW CLONE main.bronze.orders;  -- ohne
```

---

## Vergleich mit Auto Loader

- **`COPY INTO`:** Das Tracking hängt an der Zieltabelle. Eine geänderte Datei mit demselben Namen wird **nie** automatisch neu geladen. Dafür gibt es `force`.
- **Auto Loader:** Das Tracking liegt im Checkpoint (RocksDB). Mit `cloudFiles.allowOverwrites = true` (Standard `false`) dürfen Änderungen an Dateien im Eingabeordner bestehende Daten überschreiben.

Siehe auch [../File Tracking.md](../File%20Tracking.md) und [11 Muster – Korrigierte Dateien](11%20Muster%20-%20Korrigierte%20Dateien%20mit%20gleichem%20Namen.md).
