# `DataStreamWriter.foreach()`

Verarbeitet die Ausgabe der Streaming-Query mit einem selbst bereitgestellten Writer. Die Verarbeitungslogik kann als Funktion angegeben werden, die eine Zeile (`Row`) entgegennimmt, oder als Objekt mit einer `process(row)`-Methode und optionalen Methoden `open(partition_id, epoch_id)` und `close(error)`.

## Signatur

```python
foreach(f)
```

## Parameter

| Parameter | Typ | Beschreibung |
| --- | --- | --- |
| `f` | `callable` oder Objekt | Eine Funktion, die eine `Row` entgegennimmt, **oder** ein Objekt mit einer `process(row)`-Methode und optionalen Methoden `open` und `close`. |

## Rückgabewert

`DataStreamWriter`

## Hinweise

Das bereitgestellte Objekt muss serialisierbar sein. Jegliche Initialisierung für das Schreiben von Daten (z. B. das Öffnen einer Verbindung) sollte innerhalb von `open()` erfolgen, **nicht** im Konstruktor.

## Beispiele

### Als Funktion

```python
import time
df = spark.readStream.format("rate").load()

def print_row(row):
    print(row)

q = df.writeStream.foreach(print_row).start()
time.sleep(3)
q.stop()
```

### Als Writer-Objekt (mit `open`/`process`/`close`)

```python
class RowPrinter:
    def open(self, partition_id, epoch_id):
        print("Opened %d, %d" % (partition_id, epoch_id))
        return True

    def process(self, row):
        print(row)

    def close(self, error):
        print("Closed with error: %s" % str(error))

q = df.writeStream.foreach(RowPrinter()).start()
time.sleep(3)
q.stop()
```

## Quellen

- DataStreamWriter.foreach: https://docs.databricks.com/aws/en/pyspark/reference/classes/datastreamwriter/foreach

**Stand:** 2026-09-07, per `WebFetch` verifiziert.
