[← Übersicht](00%20Uebersicht.md)

# Betrieb: Parallelität, Transaktionen, Historie, VACUUM, CLONE

## COPY INTO parallel ausführen

Mehrere `COPY INTO` auf dieselbe Tabelle dürfen gleichzeitig laufen. Sie funktionieren nur, wenn jeder Aufruf **andere Dateien** lädt. Sonst gibt es einen Transaktionskonflikt.

```sql
-- Session A
COPY INTO main.bronze.events FROM '/Volumes/main/raw/landing/events/region=eu' FILEFORMAT = JSON;
-- Session B, gleichzeitig
COPY INTO main.bronze.events FROM '/Volumes/main/raw/landing/events/region=us' FILEFORMAT = JSON;
```

**Nicht für mehr Performance parallelisieren.** Ein einzelner `COPY INTO` mit vielen Dateien ist meist schneller als viele parallele Aufrufe mit je einer Datei.

Parallel ist sinnvoll, wenn …
- mehrere Datenlieferanten sich nicht auf einen gemeinsamen Aufruf abstimmen können, oder
- ein sehr großes Verzeichnis Unterordner für Unterordner geladen wird. Bei sehr vielen Dateien empfiehlt Databricks aber Auto Loader.

Passende Fehler:
- `COPY_INTO_DUPLICATED_FILES_COPY_NOT_ALLOWED`: Ein paralleler `COPY INTO` hat dieselben Dateien schon committet. Später erneut versuchen.
- `COPY_INTO_NON_BLIND_APPEND_NOT_ALLOWED`: Ein `COPY INTO`, das nicht nur anhängt, darf nicht parallel zu anderen Transaktionen laufen.

---

## COPY INTO in Transaktionen

`COPY INTO` ist in Transaktionen erlaubt, zum Beispiel in einem `BEGIN ATOMIC ... END`-Block. Dafür brauchst du ein SQL Warehouse, Serverless Compute oder Databricks Runtime 18.0+. Schreibt die Transaktion in mehrere Tabellen, müssen alle Unity-Catalog-Managed-Tables mit aktivierten Catalog Commits sein.

```sql
BEGIN ATOMIC
  COPY INTO main.bronze.orders
  FROM '/Volumes/main/raw/landing/orders'
  FILEFORMAT = CSV
  FORMAT_OPTIONS ('header' = 'true');

  INSERT INTO main.ops.load_log VALUES ('orders', current_timestamp());
END;
```

**Einschränkung:** Eine Transaktion mit `COPY INTO` schlägt fehl, wenn gleichzeitig ein anderer `COPY INTO` in dieselbe Tabelle schreibt und zuerst committet. Der Fehler heißt `TRANSACTION_CONCURRENT_COPY_INTO`. Dann die Transaktion wiederholen.

---

## Ergebnis und Historie

`COPY INTO` erscheint in der Tabellenhistorie mit den gleichen Metriken wie `WRITE`, CTAS und RTAS:

- `numFiles`: Anzahl der geschriebenen Dateien
- `numOutputBytes`: Größe der geschriebenen Daten in Bytes
- `numOutputRows`: Anzahl der geschriebenen Zeilen

Mit `ignoreCorruptFiles` kommt `numSkippedCorruptFiles` dazu. In der Ergebnisspalte des Befehls heißt sie `num_skipped_corrupt_files`.

```sql
DESCRIBE HISTORY main.bronze.orders;
-- Spalte operationMetrics: numFiles, numOutputBytes, numOutputRows (ggf. numSkippedCorruptFiles)
```

---

## VACUUM räumt COPY-INTO-Metadaten auf (ab Databricks Runtime 15.2)

`COPY INTO` legt Metadaten-Dateien an, um zu speichern, welche Dateien geladen wurden. Ab Databricks Runtime 15.2 entfernt `VACUUM` die nicht mehr referenzierten Metadaten-Dateien. Am Verhalten von `COPY INTO` ändert das nichts.

```sql
VACUUM main.bronze.orders;
```

Klappt das Aufräumen nicht, obwohl `VACUUM` die Datendateien gelöscht hat, kommt der Fehler `DELTA_VACUUM_COPY_INTO_STATE_FAILED`.

---

## CLONE und COPY-INTO-Metadaten

- **Deep Clone** kopiert Daten, Schema, Partitionierung, Eigenschaften und zusätzlich die Stream- und `COPY INTO`-Metadaten.
- **Shallow Clone** kopiert die `COPY INTO`-Metadaten nicht.

```sql
CREATE TABLE main.bronze.orders_backup DEEP CLONE main.bronze.orders;
```

Auch bei der Migration von Hive nach Unity Catalog ist `CLONE` meist besser als CTAS. Mit `CLONE` musst du Partitionierung, Format, Constraints, Stream- und `COPY INTO`-Metadaten nicht selbst angeben.

---

## Deletion Vectors

Ist die Workspace-Einstellung zum automatischen Aktivieren von Deletion Vectors an, schaltet `COPY INTO` sie auf der Zieltabelle ein. Das passiert auf SQL Warehouses und ab Databricks Runtime 14.0. Danach kann Databricks Runtime 11.3 LTS und älter die Tabelle nicht mehr lesen.

---

## Weitere Einsatzorte

- Databricks SQL (SQL-Editor, SQL Warehouse)
- Notebooks (SQL, Python, R, Scala)
- Lakeflow Jobs
