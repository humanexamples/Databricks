*Verschoben aus `_read_files.md`, Abschnitt 3 (Vollständige Optionsreferenz) — Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).*

**Hinweis:** Anders als die übrigen Dateien in diesem Ordner ist "State Store" kein Dateiformat zum Einlesen von Rohdaten, sondern eine Datenquelle zum Abfragen des internen Zustands (State) einer laufenden Structured-Streaming-Query — z. B. zum Debuggen von zustandsbehafteten Operatoren (Aggregationen, Joins, `transformWithState`).

### State-Store-Optionen

| Option | Standardwert | Gültige Werte | Beschreibung |
|---|---|---|---|
| `batchId` | letzte Batch-ID | positive Ganzzahlen oder `0` | Der abzufragende Ziel-Batch. Dient zur Abfrage eines früheren Zustands der Query. |
| `operatorId` | `0` | positive Ganzzahlen oder `0` | Der abzufragende Ziel-Operator. Relevant, wenn die Query mehrere zustandsbehaftete Operatoren hat. |
| `storeName` | `DEFAULT` | beliebiger String | Name des abzufragenden Ziel-State-Stores. |
| `joinSide` | keiner | `left`, `right` | Die abzufragende Seite bei einem Stream-Stream-Join. |
| `snapshotStartBatchId` | keiner | positive Ganzzahlen oder `0` | Batch-ID des Snapshots als Startpunkt beim Lesen des Zustands. |
| `snapshotPartitionId` | keiner | positive Ganzzahlen oder `0` | Falls angegeben, liest die Query nur diese Partition. |
| `readChangeFeed` | `false` | `true`, `false` | Bei `true` werden Zustandsänderungen über einen angegebenen Batch-Bereich zurückgegeben. |
| `changeStartBatchId` | keiner | positive Ganzzahlen oder `0` | Start-Batch-ID für den Change-Feed-Bereich. |
| `changeEndBatchId` | letzte Batch-ID | positive Ganzzahlen oder `0` | End-Batch-ID für den Change-Feed-Bereich. |
| `stateVarName` | keiner | beliebiger String | Name der abzufragenden State-Variable. |
| `readRegisteredTimers` | `false` | `true`, `false` | Bei `true` werden registrierte Timer des `transformWithState`-Operators gelesen. |
| `flattenCollectionTypes` | `true` | `true`, `false` | Bei `true` werden die für Map- und List-State-Variablen zurückgegebenen Datensätze abgeflacht. |
