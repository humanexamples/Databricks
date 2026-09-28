# Column Mapping

„Delta-Lake-Column-Mapping ermöglicht reine Metadaten-Änderungen, um Spalten umzubenennen oder zu löschen, ohne Datendateien neu zu schreiben." Es erlaubt zudem Sonderzeichen in Spaltennamen — einschließlich Leerzeichen und Zeichen wie Kommata, Semikola und geschweifte Klammern —, was direkte Ingestion von CSV- oder JSON-Daten ohne Umbenennung ermöglicht. Basierend auf der offiziellen Databricks-Doku-Seite.

## 1. Kernfähigkeiten

- **Spalten umbenennen** ohne Datei-Neuschreibung.
- **Spalten löschen** ohne Datei-Neuschreibung.
- **Sonderzeichen in Spaltennamen unterstützen**, die Parquet normalerweise einschränkt.

## 2. Voraussetzungen

Delta-Protokolle: Reader-Version 2+, Writer-Version 5+. Databricks Runtime 10.4 LTS oder höher zum Lesen gemappter Tabellen.

## 3. Aktivierung

**Bei neuen Tabellen (`id`-Modus):**

```sql
CREATE TABLE <table-name> (id INT, name STRING)
USING DELTA
TBLPROPERTIES ('delta.columnMapping.mode' = 'id');
```

**Bei bestehenden Tabellen (`name`-Modus):**

```sql
ALTER TABLE <table-name> SET TBLPROPERTIES
('delta.columnMapping.mode' = 'name');
```

## 4. Spaltenoperationen

```sql
-- Umbenennen
ALTER TABLE <table-name> RENAME COLUMN old_col_name TO new_col_name;

-- Eine oder mehrere Spalten löschen
ALTER TABLE table_name DROP COLUMN col_name;
ALTER TABLE table_name DROP COLUMNS (col_name_1, col_name_2, ...);
```

## 5. Column-Mapping-Modi

| Modus | Bedeutung |
|---|---|
| `none` (Standard) | Mapping deaktiviert |
| `name` | ermöglicht reine Metadaten-Änderungen; auf neuen und bestehenden Tabellen nutzbar |
| `id` | ermöglicht reine Metadaten-Änderungen; muss bereits bei Erstellung gesetzt werden |

Databricks empfiehlt den `id`-Modus für Kompatibilität.

**Unterstützte Sonderzeichen im Detail:** Leerzeichen sowie `, ; { } ( ) \n \t =`.

## 6. Mapping entfernen (Downgrade)

Das Entfernen des Column Mappings „schreibt alle Datendateien neu, um physische Spaltennamen durch logische Namen zu ersetzen" — ein potenziell teurer Vorgang.

**Vorbereitung bei größeren Tabellen:**

- Nebenläufige Schreibvorgänge, Streaming-Jobs und ETL-Pipelines pausieren.
- Predictive Optimization deaktivieren.
- Den Vorgang für Zeiten geringer Aktivität einplanen.

```sql
ALTER TABLE <table-name> SET TBLPROPERTIES ('delta.columnMapping.mode' = 'none');
```

**Protokoll-Downgrade:** Ab Databricks Runtime 15.4 LTS unterstützt `DROP FEATURE` das vollständige Downgrade auf Kompatibilität mit Runtime 10.3 (siehe [07 Drop Feature.md](07%20Drop%20Feature.md)).

**Wichtig:** Das Entfernen des Mappings beseitigt die zufälligen Präfixe in Partitionsverzeichnissen partitionierter Tabellen **nicht**.

## 7. Streaming-Überlegungen

Nicht-additive Schema-Änderungen (Umbenennen, Löschen) können Streaming-Lesevorgänge unterbrechen. Lösung: `schemaTrackingLocation` innerhalb des Checkpoint-Verzeichnisses nutzen.

```python
checkpoint_path = "/path/to/checkpointLocation"
(spark.readStream
  .option("schemaTrackingLocation", checkpoint_path)
  .table("delta_source_table")
  .writeStream
  .option("checkpointLocation", checkpoint_path)
  .toTable("output_table"))
```

**Column Mapping auf aktiven Streams aktivieren** erfordert vier Schritte: Stream stoppen → Column Mapping aktivieren → Stream neu starten (initialisiert das Mapping) → erneut neu starten (aktiviert die Schema-Änderungen).

## 8. Weitere Einschränkungen

- Bricht Legacy-Workloads, die sich auf Verzeichnisnamen für Lesevorgänge verlassen.
- Partitionierte Tabellen nutzen zufällige Präfixe statt Spaltennamen für Partitionsverzeichnisse.
- Kann nachgelagerte Change-Data-Feed-Operationen beeinträchtigen.
- Beeinträchtigt Streaming-Lesevorgänge, einschließlich Lakeflow-Pipelines.
- Nebenläufige Schreibvorgänge lösen während der Entfernung eine `ConcurrentModificationException` aus.
- Die Entfernung unterstützt keine Zeilen-Ebenen- oder physische Konfliktauflösung.

## 9. Verwandte Themen

- Iceberg Reads (UniForm) setzt aktiviertes Column Mapping voraus: siehe [14 Iceberg Reads (UniForm).md](14%20Iceberg%20Reads%20%28UniForm%29.md).
- Runtime-Anforderungen und Protokollversion im Gesamtüberblick: siehe [08 Feature Compatibility.md](08%20Feature%20Compatibility.md).

### Quelle

- https://docs.databricks.com/aws/en/tables/features/column-mapping
