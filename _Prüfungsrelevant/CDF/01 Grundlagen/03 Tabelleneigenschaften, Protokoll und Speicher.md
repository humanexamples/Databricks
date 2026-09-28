[← Übersicht](../00%20Uebersicht.md)

# Tabelleneigenschaften, Protokoll und Speicher

> Quellen: [Table properties reference](https://docs.databricks.com/aws/en/tables/table-properties) · [Feature compatibility and protocols](https://docs.databricks.com/aws/en/tables/features/feature-compatibility) · [VACUUM](https://docs.databricks.com/aws/en/tables/operations/vacuum) · [Use change data feed on Databricks](https://docs.databricks.com/aws/en/tables/features/change-data-feed) · [Incremental refresh for materialized views](https://docs.databricks.com/aws/en/ldp/incremental-refresh) · [Lakeflow Connect FAQ](https://docs.databricks.com/aws/en/ingestion/lakeflow-connect/faq) · [CONFIG_NOT_AVAILABLE](https://docs.databricks.com/aws/en/error-messages/config-not-available-error-class) · [DBR 15.4 LTS](https://docs.databricks.com/aws/en/release-notes/runtime/15.4lts) · [DBSQL Release Notes 2024](https://docs.databricks.com/aws/en/sql/release-notes/2024)

## Relevante Tabelleneigenschaften

Delta-Tabellen verwenden das Präfix `delta.`, Iceberg-Tabellen `iceberg.`.

| Eigenschaft | Bedeutung | Typ | Default |
|---|---|---|---|
| `enableChangeDataFeed` | `true` schaltet (Legacy-)CDF ein | `Boolean` | `false` |
| `enableRowTracking` (nur Delta) | vergibt stabile Row IDs und Row Commit Versions pro Zeile; Grundlage für **Automatic CDF**. Ab DBR 14.0. Iceberg-v3-Tabellen haben Row Tracking automatisch. | `Boolean` | `false` |
| `deletedFileRetentionDuration` | Mindestdauer, bevor logisch gelöschte Dateien physisch gelöscht werden. Databricks empfiehlt 7 Tage oder mehr. | `CalendarInterval` | `interval 1 week` |
| `logRetentionDuration` | wie lange die Tabellenhistorie (Log) aufbewahrt wird | `CalendarInterval` | `interval 30 days` |

> **Wichtig:** Jede Operation, die Tabelleneigenschaften setzt, **kollidiert mit parallelen Schreibvorgängen** und lässt diese fehlschlagen. Eigenschaften nur ändern, wenn niemand gleichzeitig schreibt.

### Auf Serverless: Tabelleneigenschaft statt Spark-Config

Auf Serverless ist das Setzen von CDF über eine Session-Konfiguration nicht möglich (Fehler `CONFIG_NOT_AVAILABLE`). Die Fehlermeldung empfiehlt: CDF über eine **Tabelleneigenschaft** oder als **Option im DataFrame-Write** ein- bzw. ausschalten.

---

## Protokollversion

| Feature | Delta `minWriterVersion` | Delta `minReaderVersion` | Iceberg `format-version` | Feature-Typ |
|---|---|---|---|---|
| Change data feed | **4** | **1** | N/A | **Writer** |
| Row tracking | 7 | 1 | 3 | Writer |
| Column mapping | 5 | 2 | N/A | Reader and writer |
| Deletion vectors | 7 | 3 | 3 | Reader and writer |

- CDF ist ein reines **Writer-Feature**: Es verlangt nur von **schreibenden** Clients Unterstützung, lesende Clients sind nicht betroffen.
- CDF wird in **allen unterstützten Databricks-Runtime-Versionen** vollständig unterstützt.

---

## Aufbewahrung: CDF ist kurzlebig

- CDF-Datensätze sind **transient** und nur innerhalb eines **Retention-Fensters** abrufbar.
- Das Transaktionslog entfernt regelmäßig alte Tabellenversionen **und** die zugehörigen CDF-Versionen. Ist eine Version entfernt, kann ihr CDF nicht mehr gelesen werden.
- CDF zeichnet nur Änderungen **ab der Aktivierung** auf und ist **nicht als dauerhafte Historie** gedacht. Für ein dauerhaftes Archiv den Feed in eine eigene Tabelle schreiben → [Streaming, Abschnitt „Dauerhafte Historie“](../02%20Lesen/02%20Streaming%20-%20readStream%20und%20Optionen.md).

### `VACUUM` und das Verzeichnis `_change_data`

- Die Daten des (Legacy-)CDF liegen im Verzeichnis **`_change_data`** und werden von **`VACUUM` entfernt**.
- Standard-Retention für Datendateien nach `VACUUM`: **7 Tage**.
- Log-Dateien werden nicht von `VACUUM` gelöscht, sondern automatisch nach Checkpoints (Standard 30 Tage).
- Nach `VACUUM` sind Versionen älter als die Retention nicht mehr abfragbar.

Fehler bei zu alten Versionen: `DELTA_CHANGE_DATA_FILE_NOT_FOUND` („… the change data file is out of the retention period and has been deleted by the `VACUUM` statement“) → [07](../07%20Einschraenkungen%20und%20Fehlermeldungen.md).

---

## Performance-Verbesserung bei `replaceWhere`

Laut Release Notes (DBR 15.4 LTS, Databricks SQL 2024, Serverless): Selective Overwrites mit **`replaceWhere`** auf Tabellen mit CDF schreiben **keine separaten Change-Data-Dateien** mehr für eingefügte Daten. Sie nutzen eine versteckte Spalte `_change_type` in den Parquet-Datendateien und vermeiden so **Write Amplification**.

---

## CDF zusammen mit anderen Tabelleneigenschaften

### Empfehlung für Quellen von Materialized Views

Für die beste inkrementelle Aktualisierung von Materialized Views empfiehlt Databricks auf **allen Quelltabellen** Deletion Vectors, Row Tracking und Change Data Feed:

```sql
ALTER TABLE <table-name> SET TBLPROPERTIES (
  delta.enableDeletionVectors = true,
  delta.enableRowTracking = true,
  delta.enableChangeDataFeed = true);
```

Für inkrementelles Refresh sind Delta-Quellen **mit Row Tracking** Voraussetzung; CDF wird zusätzlich **für bessere Performance** empfohlen. → [06 Weitere Einsatzgebiete](../06%20Weitere%20Einsatzgebiete.md)

### Lakeflow-Connect-Zieltabellen

Laut FAQ ist CDF auf **allen Zieltabellen** von Lakeflow Connect **bereits aktiviert**. Nachgelagerte Pipelines können deren Änderungen also direkt lesen.

---
[← Vorherige Datei](02%20Schema%20und%20Metadatenspalten.md) · [Übersicht](../00%20Uebersicht.md) · [Weiter: Batch-Reads →](../02%20Lesen/01%20Batch%20-%20table_changes%20und%20readChangeFeed.md)
