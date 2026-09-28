# State lesen — Referenz

Dieses Dokument beschreibt, wie sich Zustandsdaten ("state data") und Zustandsmetadaten von Structured-Streaming-Queries mittels DataFrame-Operationen oder SQL-Table-Value-Functions abfragen lassen. Diese Funktionen dienen dazu, Zustandsinformationen zustandsbehafteter Structured-Streaming-Queries zu beobachten — nützlich für Monitoring und Debugging. Verifiziert per `WebFetch` gegen die GCP-Original-URL sowie ergänzend gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/structured-streaming/read-state`), die eine vollständige, wörtliche Wiedergabe des Roh-Inhalts lieferte.

## Abschnittsübersicht
1. [Überblick](#ueberblick)
2. [Voraussetzungen](#voraussetzungen)
3. [Structured-Streaming-State-Store lesen](#state-store-lesen)
4. [Structured-Streaming-Zustandsänderungen lesen](#zustandsaenderungen-lesen)
5. [Structured-Streaming-Zustandsmetadaten lesen](#zustandsmetadaten-lesen)
6. [Beispiel: eine Seite eines Stream-Stream-Joins abfragen](#beispiel-join-seite)
7. [Beispiel: State Store für Stream mit mehreren zustandsbehafteten Operatoren abfragen](#beispiel-mehrere-operatoren)
8. [Quellen](#quellen)

---

## <a id="ueberblick">1. Überblick</a>

Zum Lesen des Zustands muss Leseberechtigung auf den Checkpoint-Pfad der jeweiligen Streaming-Query bestehen. Die in diesem Dokument beschriebenen Funktionen bieten ausschließlich Lesezugriff auf Zustandsdaten und -metadaten. Zustandsinformationen können nur mit Batch-Read-Semantik abgefragt werden.

**Hinweis:** Zustandsinformationen können nicht für Lakeflow-Pipelines, Streaming-Tabellen oder Materialized Views abgefragt werden. Ebenso lassen sich Zustandsinformationen nicht mittels Serverless Compute oder mit Compute im Standard-Access-Modus abfragen.

## <a id="voraussetzungen">2. Voraussetzungen</a>

- Eine der folgenden Compute-Konfigurationen verwenden:
  - Databricks Runtime 16.3 und höher auf Compute mit Standard-Access-Modus.
  - Databricks Runtime 14.3 LTS und höher auf Compute mit Dedicated- oder No-Isolation-Access-Modus.
- Leseberechtigung auf den von der Streaming-Query verwendeten Checkpoint-Pfad.

## <a id="state-store-lesen">3. Structured-Streaming-State-Store lesen</a>

Zustandsspeicher-Informationen ("state store information") für Structured-Streaming-Queries lassen sich für jede unterstützte Databricks-Runtime-Version lesen. Dazu wird folgende Syntax verwendet:

### Python

```python
df = (spark.read
  .format("statestore")
  .load("/checkpoint/path"))
```

### SQL

```sql
SELECT * FROM read_statestore('/checkpoint/path')
```

### State-Reader-API-Optionen und Schema

Eine vollständige Liste der `statestore`-Format-Optionen findet sich in der Referenz "State store" innerhalb der Spark-API-Optionen.

Die Ausgabedaten besitzen folgendes Schema:

| Spalte | Typ | Beschreibung |
| --- | --- | --- |
| `key` | Struct (weiterer Typ vom State-Key abgeleitet) | Der Key für einen Datensatz des zustandsbehafteten Operators im State-Checkpoint. |
| `value` | Struct (weiterer Typ vom State-Value abgeleitet) | Der Wert für einen Datensatz des zustandsbehafteten Operators im State-Checkpoint. |
| `partition_id` | Integer | Die Partition des State-Checkpoints, die den Datensatz des zustandsbehafteten Operators enthält. |

In Databricks Runtime 16.4 LTS und höher besitzen die Ausgabedaten, wenn die Option `readChangeFeed` auf `true` gesetzt ist, folgendes Schema:

| Spalte | Typ | Beschreibung |
| --- | --- | --- |
| `batch_id` | Long | Die Batch-ID, zu der die Zustandsänderung gehört. |
| `change_type` | String | Der Typ der durch den Batch angewendeten Änderung: `update` für Inserts und Updates, `delete` für Löschungen. |
| `key` | Struct (weiterer Typ vom State-Key abgeleitet) | Der Key für einen Datensatz des zustandsbehafteten Operators im State-Checkpoint. |
| `value` | Struct (weiterer Typ vom State-Value abgeleitet) | Der Wert für einen Datensatz des zustandsbehafteten Operators im State-Checkpoint. `null` bei Datensätzen, deren `change_type` `delete` ist. |
| `partition_id` | Integer | Die Partition des State-Checkpoints, die den Datensatz des zustandsbehafteten Operators enthält. |

Siehe dazu auch die Referenz zur `read_statestore`-Table-Valued-Function.

## <a id="zustandsaenderungen-lesen">4. Structured-Streaming-Zustandsänderungen lesen</a>

Verfügbar ab Databricks Runtime 16.4 LTS. Um nachzuvollziehen, wie sich der Zustand über mehrere Micro-Batches hinweg ändert — statt den vollständigen Zustand zu einem einzelnen Micro-Batch zu betrachten — wird `readChangeFeed` auf `true` gesetzt und `changeStartBatchId` angegeben. Optional kann zusätzlich `changeEndBatchId` angegeben werden. Eine vollständige Liste der Optionen findet sich in der Referenz "State store" innerhalb der Spark-API-Optionen.

Beispiel: Zustandsänderungen von Batch `2` bis zum aktuellsten committeten Batch lesen:

### Python

```python
df = (spark.read
  .format("statestore")
  .option("readChangeFeed", True)
  .option("changeStartBatchId", 2)
  .load("<checkpointLocation>")
)
```

### SQL

```sql
SELECT * FROM read_statestore(
    '<checkpointLocation>',
    readChangeFeed => true,
    changeStartBatchId => 2
);
```

Das Ausgabeschema enthält zusätzlich die Spalten `batch_id` und `change_type`. Das vollständige Schema findet sich im Abschnitt [State-Reader-API-Optionen und Schema](#state-store-lesen).

## <a id="zustandsmetadaten-lesen">5. Structured-Streaming-Zustandsmetadaten lesen</a>

Verfügbar ab Databricks Runtime 14.3 LTS. Zustandsmetadaten-Informationen für Structured-Streaming-Queries lassen sich wie folgt lesen:

### Python

```python
df = (spark.read
  .format("state-metadata")
  .load("<checkpointLocation>"))
```

### SQL

```sql
SELECT * FROM read_state_metadata('/checkpoint/path')
```

Die zurückgegebenen Daten besitzen folgendes Schema:

| Spalte | Typ | Beschreibung |
| --- | --- | --- |
| `operatorId` | Integer | Die Integer-ID des zustandsbehafteten Streaming-Operators. |
| `operatorName` | String | Name des zustandsbehafteten Streaming-Operators. |
| `stateStoreName` | String | Name des State Store des Operators. |
| `numPartitions` | Integer | Anzahl der Partitionen des State Store. |
| `minBatchId` | Long | Die minimale Batch-ID, für die Zustand abgefragt werden kann. |
| `maxBatchId` | Long | Die maximale Batch-ID, für die Zustand abgefragt werden kann. |

**Hinweis:** Die von `minBatchId` und `maxBatchId` bereitgestellten Batch-ID-Werte spiegeln den Zustand zum Zeitpunkt wider, zu dem der Checkpoint geschrieben wurde. Alte Batches werden im Rahmen der Micro-Batch-Ausführung automatisch bereinigt, sodass der hier angegebene Wert nicht garantiert weiterhin verfügbar ist.

Siehe dazu auch die Referenz zur `read_state_metadata`-Table-Valued-Function.

## <a id="beispiel-join-seite">6. Beispiel: eine Seite eines Stream-Stream-Joins abfragen</a>

Mit folgender Syntax lässt sich die linke Seite eines Stream-Stream-Joins abfragen:

### Python

```python
left_df = (spark.read
  .format("statestore")
  .option("joinSide", "left")
  .load("/checkpoint/path"))
```

### SQL

```sql
SELECT * FROM read_statestore(
    '/checkpoint/path',
    joinSide => 'left'
);
```

## <a id="beispiel-mehrere-operatoren">7. Beispiel: State Store für Stream mit mehreren zustandsbehafteten Operatoren abfragen</a>

Dieses Beispiel nutzt den State-Metadata-Reader, um Metadaten-Details einer Streaming-Query mit mehreren zustandsbehafteten Operatoren zu ermitteln, und verwendet die Metadaten-Ergebnisse anschließend als Optionen für den State-Reader.

Der State-Metadata-Reader akzeptiert ausschließlich den Checkpoint-Pfad als Option, wie im folgenden Syntaxbeispiel gezeigt:

### Python

```python
df = (spark.read
  .format("state-metadata")
  .load("<checkpointLocation>"))
```

### SQL

```sql
SELECT * FROM read_state_metadata('/checkpoint/path')
```

Die folgende Tabelle zeigt eine Beispielausgabe der State-Store-Metadaten:

| operatorId | operatorName | stateStoreName | numPartitions | minBatchId | maxBatchId |
| --- | --- | --- | --- | --- | --- |
| 0 | stateStoreSave | default | 200 | 0 | 13 |
| 1 | dedupeWithinWatermark | default | 200 | 0 | 13 |

Um Ergebnisse für den Operator `dedupeWithinWatermark` zu erhalten, wird der State-Reader mit der Option `operatorId` abgefragt, wie im folgenden Beispiel gezeigt:

### Python

```python
left_df = (spark.read
  .format("statestore")
  .option("operatorId", 1)
  .load("/checkpoint/path"))
```

### SQL

```sql
SELECT * FROM read_statestore(
    '/checkpoint/path',
    operatorId => 1
);
```

---

## <a id="quellen">8. Quellen</a>
- Read Structured Streaming state information (Original, GCP): https://docs.databricks.com/gcp/en/structured-streaming/read-state
- Read Structured Streaming state information (Mirror, verifiziert/vollständig abgerufen, Azure): https://learn.microsoft.com/en-us/azure/databricks/structured-streaming/read-state

**Stand:** 2026-08-22.
