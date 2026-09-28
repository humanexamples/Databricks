[← Übersicht](00%20Uebersicht.md)

# Metadatenspalten in COPY INTO

Es gibt zwei versteckte Spalten, die man im `SELECT` von `COPY INTO` abfragen kann. Sie erscheinen nur, wenn man sie ausdrücklich auswählt.

---

## `_metadata` – Infos zur Datei

`_metadata` ist ein `STRUCT` mit diesen Feldern:

- `file_path` (`STRING`): der volle Pfad, z. B. `file:/tmp/f0.csv`
- `file_name` (`STRING`): Dateiname mit Endung, z. B. `f0.csv`
- `file_size` (`LONG`): Größe in Bytes
- `file_modification_time` (`TIMESTAMP`): letzte Änderung der Datei
- `file_block_start` (`LONG`, ab Databricks Runtime 13.0): Start des gelesenen Blocks
- `file_block_length` (`LONG`, ab Databricks Runtime 13.0): Länge des gelesenen Blocks

Die ersten vier Felder gibt es ab Databricks Runtime 10.5.

**Ganzes Struct übernehmen:**

```sql
COPY INTO my_delta_table
FROM (
  SELECT *, _metadata FROM 's3://my-bucket/csvData'
)
FILEFORMAT = CSV;
```

**Besser: einzelne Felder auswählen.** Später können neue Felder zu `_metadata` hinzukommen. Wählst du nur einzelne Felder, vermeidest du dadurch Fehler bei der Schema-Evolution.

```sql
COPY INTO main.bronze.orders
FROM (
  SELECT *,
         _metadata.file_name              AS src_file,
         _metadata.file_modification_time AS src_file_ts
  FROM '/Volumes/main/raw/landing/orders'
)
FILEFORMAT = CSV
FORMAT_OPTIONS ('header' = 'true');
```

**Namenskonflikt:** Hat die Datei selbst eine Spalte namens `_metadata`, bekommst du diese Spalte zurück und nicht die Datei-Metadaten.

---

## `_object_metadata` – Infos aus dem Cloud-Speicher (Public Preview)

`_object_metadata` gibt es ab Databricks Runtime 18.2 für alle Formate beim Lesen aus Cloud Object Storage. Die Werte kommen über die Cloud-APIs. Alle Felder können `NULL` sein.

- `mime_type` (`STRING`): z. B. `text/csv`
- `etag` (`STRING`): hilfreich, um Änderungen oder Versionen zu erkennen
- `user_metadata` (`VARIANT`): selbst gesetzte Schlüssel-Wert-Paare am Objekt
- `system_metadata` (`VARIANT`): vom Cloud-Anbieter gesetzte Werte
- `tags` (`VARIANT`): die Tags des Objekts

```sql
COPY INTO my_delta_table
FROM (
  SELECT *, _object_metadata FROM '<path-to-load-from>'
)
FILEFORMAT = CSV;
```

**Namenskonflikt:** Hat die Datei eine Spalte `_object_metadata`, schreibst du `__object_metadata` mit einem zusätzlichen Unterstrich. Kollidiert auch das, hängst du einen weiteren Unterstrich an.

---

## Wozu das in der Praxis dient

Mit Dateiname und Änderungszeit kannst du später in Silver erkennen, welche Zeilen aus welcher Datei-Version stammen. Siehe [11 Muster – Korrigierte Dateien](11%20Muster%20-%20Korrigierte%20Dateien%20mit%20gleichem%20Namen.md).

```sql
SELECT src_file, src_file_ts, count(*) AS rows
FROM main.bronze.orders
GROUP BY ALL
ORDER BY src_file, src_file_ts;
```
