[← Übersicht](../00%20Uebersicht.md)

# CDF im Stream lesen: `readStream` und Optionen

> Quellen: [Use change data feed on Databricks – Incrementally process change data](https://docs.databricks.com/aws/en/tables/features/change-data-feed) · [Delta Lake table streaming reads and writes](https://docs.databricks.com/aws/en/structured-streaming/delta-lake) · [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options) · [System tables](https://docs.databricks.com/aws/en/admin/system-tables/) · [Production considerations for Structured Streaming](https://docs.databricks.com/aws/en/structured-streaming/production)

## Warum Streaming?

Databricks **empfiehlt, CDF zusammen mit Structured Streaming** zu verwenden, um Änderungen inkrementell zu verarbeiten. Nur mit Structured Streaming merkt sich Databricks **automatisch**, bis zu welcher Version der Feed bereits gelesen wurde (im Checkpoint). Im Batch muss man diese Position selbst verwalten.

Für CDC mit SCD Typ 1 oder 2 verweist die Doku auf die AUTO-CDC-APIs → [03/02 CDF und AUTO CDC](../03%20Pipelines%20und%20Muster/02%20CDF%20und%20AUTO%20CDC.md).

## Grundform

```python
(spark.readStream
  .option("readChangeFeed", "true")
  .table("myTable"))
```

```scala
spark.readStream
  .option("readChangeFeed", "true")
  .table("myTable")
```

### Verhalten beim ersten Start

Beim ersten Start liefert der Stream den **aktuellen Snapshot der Tabelle als `INSERT`-Datensätze** und danach alle weiteren Änderungen als Change Data. CDF schreibt Change Data und neue Datenzeilen **gleichzeitig** ins Transaktionslog.

---

## Rate Limits

Beim Lesen von Change Data werden unterstützt:

- `maxFilesPerTrigger`
- `maxBytesPerTrigger`
- `excludeRegex`

Außerhalb des Start-Snapshots gelten Rate Limits **atomar pro Commit**: Ein Batch enthält entweder den **ganzen** Commit oder verschiebt ihn komplett in den nächsten Batch.

---

## Startversion festlegen

Startpunkt per **Version** oder **Zeitstempel**; im Stream optional.

| Situation | Empfehlung |
|---|---|
| Neue Pipeline | Default-Verhalten: alle bestehenden Zeilen beim ersten Start als `INSERT` verarbeiten |
| Ziel enthält bereits alle Änderungen bis Version X | `startingVersion` = X + 1, damit der Quellzustand nicht noch einmal als `INSERT` verarbeitet wird |

### Beispiel: Wiederanlauf nach beschädigtem Checkpoint

Annahmen der Doku:

- CDF war auf der Quelle seit Anlage aktiv.
- Das Ziel hat alle Änderungen **bis einschließlich Version 75** verarbeitet.
- Die Versionshistorie der Quelle ist ab Version 70 verfügbar.

Für den Write-Stream in die bestehende Zieltabelle **muss ein neuer Checkpoint-Pfad** angegeben werden:

```python
(spark.readStream
  .option("readChangeFeed", "true")
  .option("startingVersion", 76)
  .table("source_table")
  .writeStream
  .option("checkpointLocation", "<new-checkpoint-path>")
  .toTable("target_table"))
```

```scala
spark.readStream
  .option("readChangeFeed", "true")
  .option("startingVersion", 76)
  .table("source_table")
  .writeStream
  .option("checkpointLocation", "<new-checkpoint-path>")
  .toTable("target_table")
```

> **Wichtig:** Ist die angegebene Startversion nicht mehr in der Historie vorhanden, **startet der Stream mit neuem Checkpoint nicht**. Managed Tables räumen alte Versionen automatisch auf, daher werden **alle** angegebenen Startversionen irgendwann gelöscht.

---

## Dauerhafte Historie: CDF archivieren

CDF ist **kein dauerhaftes Protokoll** aller Änderungen: Er enthält nur Änderungen ab Aktivierung, und alte Versionen verschwinden mit der Retention. Wer eine dauerhafte Historie braucht, schreibt den Feed **inkrementell in eine eigene Tabelle**. Die Doku nutzt dafür `trigger(availableNow=True)`: Der Stream verarbeitet alles Verfügbare wie einen Batch-Job und stoppt dann. Das eignet sich für Audits oder vollständige Replays.

```python
(spark.readStream
  .option("readChangeFeed", "true")
  .table("source_table")
  .writeStream
  .option("checkpointLocation", <checkpoint-path>)
  .trigger(availableNow=True)
  .toTable("target_table"))
```

```scala
spark.readStream
  .option("readChangeFeed", "true")
  .table("source_table")
  .writeStream
  .option("checkpointLocation", <checkpoint-path>)
  .trigger(Trigger.AvailableNow)
  .toTable("target_table")
```

---

## Streaming-Optionen für Delta-Quellen (Auszug)

Aus der Spark-Optionsreferenz, Abschnitt „Delta Lake“ (`spark.readStream`):

| Option | Default | Werte | Beschreibung |
|---|---|---|---|
| `readChangeFeed` **oder** `readChangeData` | `false` | `true`, `false` | liest den CDF: der Stream liefert Zeilenänderungen mit Metadatenspalten |
| `startingVersion` | neueste verfügbar | positive Zahl, `0` oder `latest` | Version, ab der gelesen wird (inklusive). Nicht mit `startingTimestamp` kombinierbar. **Ignoriert, wenn der Checkpoint schon existiert.** |
| `startingTimestamp` | neueste verfügbar | z. B. `2019-01-01T00:00:00.000Z` oder `2019-01-01` | Zeitstempel, ab dem gelesen wird. Liegt er vor allen Commits, startet der Stream beim frühesten verfügbaren. Nicht mit `startingVersion` kombinierbar. **Ignoriert, wenn der Checkpoint existiert.** |
| `skipChangeCommits` | `false` | `true`, `false` | ignoriert Transaktionen, die bestehende Zeilen löschen oder ändern; verarbeitet nur Appends. Ab DBR 12.2 LTS. |
| `excludeRegex` | – | Java-Regex | Dateien, deren Pfad passt, werden ausgeschlossen |
| `failOnDataLoss` | `true` | `true`, `false` | Stream schlägt fehl, wenn Quelldaten durch Log-Retention gelöscht wurden |
| `ignoreChanges` (deprecated) | `false` | `true`, `false` | bis DBR 11.3 LTS; durch `skipChangeCommits` ersetzt |
| `ignoreDeletes` (deprecated) | `false` | `true`, `false` | ignoriert nur das Löschen ganzer Partitionen |

> **Namensverwechslung vermeiden:** Die **State Data Source** (Lesen von Streaming-State) kennt ebenfalls eine Option `readChangeFeed` (mit `changeStartBatchId`/`changeEndBatchId`, ab DBR 16.4 LTS). Das ist ein **anderes** Feature und hat nichts mit dem Delta-CDF zu tun.

---

## Vier Wege, mit Änderungen an einer Stream-Quelle umzugehen

Structured Streaming akzeptiert von einer Delta-Quelle standardmäßig **nur Appends**. Ein `UPDATE`, `DELETE`, `MERGE INTO` oder `OVERWRITE` auf der Quelle lässt den Stream **mit Fehler abbrechen**. Die Doku nennt vier Ansätze:

| Ansatz | Vorteile | Nachteile |
|---|---|---|
| `skipChangeCommits` | einfach, keine komplexe Logik; gut für Append-only-Verarbeitung oder um einen fehlerhaften Datensatz vorübergehend zu überspringen | gibt Änderungen **nicht** weiter, verarbeitet nur Appends |
| Full Refresh | ebenfalls einfach; gut für kleine Datenmengen mit seltenen Änderungen | teuer bei großen Daten; alle nachgelagerten Tabellen müssen neu verarbeitet werden |
| **Change Data Feed** | verarbeitet **alle** Änderungstypen (Insert, Update, Delete). **Databricks empfiehlt, wann immer möglich aus dem CDF statt direkt aus der Tabelle zu streamen.** | mehr eigene Logik pro Änderungstyp nötig |
| Materialized Views | einfache Alternative mit automatischer Weitergabe von Änderungen | höhere Latenz; nur in Lakeflow Pipelines und Databricks SQL |

Die Doku nennt CDF den **robustesten Ansatz**, weil der Code jeden Änderungstyp explizit behandelt.

### `skipChangeCommits` zum Vergleich

```python
(spark.readStream
  .option("skipChangeCommits", "true")
  .table("source_table")
)
```

```scala
spark.readStream
  .option("skipChangeCommits", "true")
  .table("source_table")
```

Databricks empfiehlt `skipChangeCommits` für die meisten Workloads, die **keinen** CDF nutzen.

> **Column Mapping:** Bis einschließlich DBR 12.2 LTS kann man nicht aus dem CDF einer Tabelle mit Column Mapping streamen, die eine nicht-additive Schemaänderung (Umbenennen/Löschen von Spalten) erlebt hat.

---

## Weitere Hinweise aus der Doku

- **System Tables:** Den CDF von System Tables per `readChangeFeed` zu streamen erfordert **DBR 17.3** oder höher (normales Streaming ab 16.4). System Tables haben 7 Tage `VACUUM`-Retention, ein Stream, der mehr als 7 Tage zurückliegt, kann abbrechen.
- **Niedrige Latenz:** Für operative Streaming-Workloads nennt die Produktions-Doku die **Change Data Feeds von Delta-Lake- und Iceberg-Tabellen** ausdrücklich als latenzarme Quellen, neben Message-Bussen wie Kafka.

---
[← Vorherige Datei](01%20Batch%20-%20table_changes%20und%20readChangeFeed.md) · [Übersicht](../00%20Uebersicht.md) · [Weiter: Pipelines und Muster →](../03%20Pipelines%20und%20Muster/01%20Demo%20-%20Silver%20nach%20Gold%20propagieren.md)
