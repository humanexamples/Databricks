# Selektives Überschreiben mit Delta Lake

## Übersicht der Optionen

| Option | Anwendungsfall | Compute-Typen | Mindestversion |
|---|---|---|---|
| `REPLACE WHERE` | Atomares Überschreiben von Zeilen nach festem Prädikat (z. B. `colA = 5`) | Alle | SQL: DBR 12.2 LTS+; Python/Scala: DBR 9.1 LTS+ |
| `REPLACE USING` | Dynamisches Überschreiben per Spaltengleichheit | Alle | SQL: DBR 16.3+; Python/Scala: DBR 18.2+ |
| `REPLACE ON` | Dynamisches Überschreiben per boolescher Bedingung (z. B. NULL-sicherer Vergleich) | Alle | SQL: DBR 17.1+; Python/Scala: DBR 18.2+ |
| `partitionOverwriteMode` | Legacy dynamische Partitionsüberschreibung (nicht empfohlen für neue Workloads) | SQL: nur Classic; Python/Scala: alle | DBR 11.3 LTS+ |

> Empfehlung: `REPLACE USING` oder `REPLACE WHERE` für die meisten Fälle. `REPLACE ON` nur bei komplexen/NULL-sicheren Vergleichsbedingungen.

## `REPLACE WHERE`

Prüft vor dem atomaren Ersetzen, dass alle Zeilen dem Prädikat entsprechen. Auf Classic Compute abschaltbar (überschreibt Treffer, fügt Nicht-Treffer ein). Leere Quellabfrage kann Tabellenzeilen löschen.

```python
(replace_data.write
  .mode("overwrite")
  .option("replaceWhere", "start_date >= '2017-01-01' AND end_date <= '2017-01-31'")
  .saveAsTable("myTable"))
# Ergebnis: nur Zeilen im Januar-2017-Fenster werden ersetzt, alle anderen bleiben unverändert
```

```sql
INSERT INTO TABLE myTable REPLACE 
WHERE start_date >= '2017-01-01' AND 
      end_date <= '2017-01-31' 
SELECT * FROM replace_data
```

## `REPLACE USING`

Compute-unabhängiges atomares Überschreiben (SQL-Warehouses, Serverless, Classic). Ersetzt Zeilen mit übereinstimmenden Spalten; andere Daten bleiben unverändert. Leere Quellabfrage → bestehende Zeilen bleiben erhalten.

```python
(sourceDataDF.write
  .mode("overwrite")
  .option("replaceUsing", "event_id, start_date")
  .saveAsTable("myTable"))
```

```sql
INSERT INTO TABLE myTable
  REPLACE USING (event_id, start_date)
  SELECT * FROM source_data
```

## `REPLACE ON`

Frei definierte Bedingung statt Gleichheitsprüfung, z. B. `<=>` für NULL-sicheren Vergleich. Leere Quellabfrage → bestehende Zeilen bleiben erhalten.

```python
(sourceDataDF.alias("s")
  .write
  .mode("overwrite")
  .option("targetAlias", "t")
  .option("replaceOn", "s.event_id <=> t.event_id AND s.start_date <=> t.start_date")
  .saveAsTable("myTable"))
```

```sql
INSERT INTO TABLE myTable AS t
  REPLACE ON (s.event_id <=> t.event_id AND s.start_date <=> t.start_date)
  (SELECT * FROM source_data) AS s
```

## `partitionOverwriteMode` (Legacy)

Ersetzt alle Daten in den betroffenen Partitionen. Einschränkungen bei Schemaänderungen und gleichzeitig genutzten Optionen — für neue Workloads nicht empfohlen.

```sql
SET spark.sql.sources.partitionOverwriteMode=dynamic;
INSERT OVERWRITE TABLE default.people10m SELECT * FROM morePeople;
-- Ergebnis: nur die Partitionen, die in morePeople vertreten sind, werden ersetzt
```

```python
(df.write
  .mode("overwrite")
  .option("partitionOverwriteMode", "dynamic")
  .saveAsTable("default.people10m"))
```

**Stand:** 2026-09-14.
