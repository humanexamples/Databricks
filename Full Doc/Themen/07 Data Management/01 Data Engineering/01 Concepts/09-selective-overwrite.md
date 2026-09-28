# Selektives Überschreiben mit Delta Lake

Delta Lake bietet vier unterschiedliche Methoden, um Daten selektiv zu überschreiben, statt eine ganze Tabelle neu zu schreiben.

## Übersicht der Optionen

| Option | Anwendungsfall | Unterstützte Compute-Typen | Mindestversion |
| --- | --- | --- | --- |
| `REPLACE WHERE` | Atomares Überschreiben von Zeilen, die einem festen Prädikat entsprechen (z. B. `colA = 5`) | Alle Compute-Typen | SQL: DBR 12.2 LTS+; Python/Scala: DBR 9.1 LTS+ |
| `REPLACE USING` | Dynamisches Überschreiben per Spaltengleichheit | Alle Compute-Typen | SQL: DBR 16.3+; Python/Scala: DBR 18.2+ |
| `REPLACE ON` | Dynamisches Überschreiben per boolescher Bedingung (z. B. NULL-sicherer Vergleich) | Alle Compute-Typen | SQL: DBR 17.1+; Python/Scala: DBR 18.2+ |
| `partitionOverwriteMode` | Alte dynamische Partitionsüberschreibung (für neue Workloads nicht empfohlen) | SQL: nur Classic; Python/Scala: alle Typen | DBR 11.3 LTS+ |

**Empfehlung:** Databricks empfiehlt für die meisten Anwendungsfälle `REPLACE USING` oder `REPLACE WHERE`. `REPLACE ON` sollte nur genutzt werden, wenn komplexe oder NULL-sichere Vergleichsbedingungen benötigt werden.

## REPLACE WHERE

Überprüft vor dem atomaren Ersetzen, dass alle Zeilen dem Prädikat entsprechen. Auf Classic Compute lässt sich diese Prüfung deaktivieren, um übereinstimmende Zeilen zu überschreiben und gleichzeitig nicht übereinstimmende Zeilen einzufügen. Bei einer leeren Quellabfrage kann diese Methode Tabellenzeilen löschen.

```python
(replace_data.write
  .mode("overwrite")
  .option("replaceWhere", "start_date >= '2017-01-01' AND end_date <= '2017-01-31'")
  .saveAsTable("events"))
```

```sql
%sql
INSERT INTO TABLE events REPLACE WHERE start_date >= '2017-01-01' AND end_date <= '2017-01-31' SELECT * FROM replace_data
```

## REPLACE USING

Ermöglicht compute-unabhängiges atomares Überschreiben über SQL-Warehouses, Serverless und Classic Compute hinweg. Ersetzt Zeilen, bei denen die angegebenen Spalten übereinstimmen; andere Daten bleiben unverändert. Bei einer leeren Quellabfrage bleiben bestehende Zeilen erhalten.

```python
(sourceDataDF.write
  .mode("overwrite")
  .option("replaceUsing", "event_id, start_date")
  .saveAsTable("events"))
```

```sql
%sql
INSERT INTO TABLE events
  REPLACE USING (event_id, start_date)
  SELECT * FROM source_data
```

## REPLACE ON

Verwendet statt einer Gleichheitsprüfung frei definierte Bedingungen, z. B. um NULL-Werte mit dem Operator `<=>` als gleich zu behandeln. Bei einer leeren Quellabfrage bleiben bestehende Zeilen ebenfalls erhalten.

```python
(sourceDataDF.alias("s")
  .write
  .mode("overwrite")
  .option("targetAlias", "t")
  .option("replaceOn", "s.event_id <=> t.event_id AND s.start_date <=> t.start_date")
  .saveAsTable("events"))
```

```sql
%sql
INSERT INTO TABLE events AS t
  REPLACE ON (s.event_id <=> t.event_id AND s.start_date <=> t.start_date)
  (SELECT * FROM source_data) AS s
```

## partitionOverwriteMode (Legacy)

Ersetzt alle Daten in den betroffenen Partitionen. Unterliegt Einschränkungen bei Schemaänderungen und gleichzeitig genutzten Optionen – für neue Workloads nicht empfohlen.

```sql
%sql
SET spark.sql.sources.partitionOverwriteMode=dynamic;
INSERT OVERWRITE TABLE default.people10m SELECT * FROM morePeople;
```

```python
(df.write
  .mode("overwrite")
  .option("partitionOverwriteMode", "dynamic")
  .saveAsTable("default.people10m"))
```

---
**Quelle:** https://docs.databricks.com/aws/en/delta/selective-overwrite  
**Stand:** 2026-08-07
