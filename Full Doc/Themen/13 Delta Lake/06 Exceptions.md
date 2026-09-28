# Exceptions — Python-Referenz (Delta Lake)

## Abschnittsübersicht
1. [Zweck](#zweck)
2. [`DeltaConcurrentModificationException` (Basisklasse)](#basis)
3. [`ConcurrentWriteException`](#concurrentwrite)
4. [`MetadataChangedException`](#metadatachanged)
5. [`ProtocolChangedException`](#protocolchanged)
6. [`ConcurrentAppendException`](#concurrentappend)
7. [`ConcurrentDeleteReadException`](#concurrentdeleteread)
8. [`ConcurrentDeleteDeleteException`](#concurrentdeletedelete)
9. [`ConcurrentTransactionException`](#concurrenttransaction)
10. [Quellen](#quellen)

## <a id="zweck">1. Zweck</a>
Das Modul `delta.exceptions` enthält die Exception-Klassen, die Delta Lake wirft, wenn zwei oder mehr Transaktionen gleichzeitig auf dieselbe Delta-Tabelle schreiben und dabei in Konflikt geraten (optimistische Nebenläufigkeitskontrolle). Diese Klassen werden in der Praxis nicht selbst instanziiert, sondern beim Schreiben (z. B. `DataFrame.write`, `DeltaTable.merge`, `.update()`, `.delete()`) von der Delta-Engine geworfen und im eigenen Code per `try/except` abgefangen.

Alle acht Klassen haben dieselbe Konstruktor-Signatur:
```python
ExceptionKlasse(
    message: str | None = None,
    errorClass: str | None = None,
    messageParameters: dict[str, str] | None = None,
    contexts: list | None = None,
)
```
Da man sie so gut wie nie selbst erzeugt, ist diese Signatur für die Praxis nebensächlich — relevant ist, welches Konfliktszenario jede Klasse anzeigt und wie man darauf reagiert (z. B. Retry).

## <a id="basis">2. `DeltaConcurrentModificationException` (Basisklasse)</a>
- Laut Doku: "The basic class for all Delta commit conflict exceptions." Sie ist die gemeinsame Basisklasse, von der alle sieben folgenden spezifischeren Konflikt-Exceptions erben.
- Praktischer Nutzen: Wenn man nicht zwischen den einzelnen Konfliktarten unterscheiden will, reicht es, generisch auf diese Basisklasse zu prüfen — sie fängt jede Art von Delta-Commit-Konflikt ab.
```python
from delta.exceptions import DeltaConcurrentModificationException
import time

def schreiben_mit_retry(schreib_funktion, max_versuche=3):
    for versuch in range(1, max_versuche + 1):
        try:
            schreib_funktion()
            return
        except DeltaConcurrentModificationException as e:
            print(f"Konflikt bei Versuch {versuch}: {e}")
            if versuch == max_versuche:
                raise
            time.sleep(2 ** versuch)  # exponentielles Backoff

schreiben_mit_retry(lambda: (
    delta_table.update(condition="id = 42", set={"status": "'erledigt'"})
))
```

## <a id="concurrentwrite">3. `ConcurrentWriteException`</a>
- Konflikt: Eine andere Transaktion hat bereits neue Daten geschrieben (committed), nachdem die aktuelle Transaktion die Tabelle gelesen hat — die aktuelle Transaktion basiert also auf einem veralteten Tabellenstand.
```python
from delta.exceptions import ConcurrentWriteException

try:
    (spark.range(100)
        .write.format("delta").mode("append")
        .save("/mnt/delta/events"))
except ConcurrentWriteException as e:
    print(f"Ein anderer Schreibvorgang war schneller, erneut versuchen: {e}")
```

## <a id="metadatachanged">4. `MetadataChangedException`</a>
- Konflikt: Zwischen dem Lesezeitpunkt und dem Commit-Zeitpunkt der aktuellen Transaktion hat sich das Metadata-Objekt der Tabelle geändert — z. B. hat eine parallele Transaktion per `ALTER TABLE` das Schema geändert oder Tabelleneigenschaften angepasst.
```python
from delta.exceptions import MetadataChangedException

try:
    (spark.read.format("delta").load("/mnt/delta/events")
        .write.format("delta").mode("overwrite")
        .option("mergeSchema", "true")
        .save("/mnt/delta/events"))
except MetadataChangedException as e:
    print(f"Tabellen-Metadaten wurden parallel geändert: {e}")
```

## <a id="protocolchanged">5. `ProtocolChangedException`</a>
- Konflikt: Zwischen Lese- und Commit-Zeitpunkt hat sich die Protokollversion der Tabelle geändert, z. B. weil eine parallele Transaktion ein Tabellen-Feature-Upgrade (Reader/Writer-Version) durchgeführt hat.
```python
from delta.exceptions import ProtocolChangedException

try:
    delta_table.delete(condition="event_date < '2020-01-01'")
except ProtocolChangedException as e:
    print(f"Protokollversion der Tabelle wurde parallel geändert: {e}")
```

## <a id="concurrentappend">6. `ConcurrentAppendException`</a>
- Konflikt: Eine parallele Transaktion hat Dateien hinzugefügt, die von der aktuellen Transaktion beim Lesen mit erfasst worden wären (z. B. zwei `MERGE`/`UPDATE`-Vorgänge, die sich überlappende Partitionen anfassen).
```python
from delta.exceptions import ConcurrentAppendException

try:
    (delta_table.alias("t")
        .merge(neue_daten.alias("s"), "t.id = s.id")
        .whenMatchedUpdateAll()
        .whenNotMatchedInsertAll()
        .execute())
except ConcurrentAppendException as e:
    print(f"Parallel hinzugefügte Dateien überschneiden sich mit dieser Transaktion: {e}")
```

## <a id="concurrentdeleteread">7. `ConcurrentDeleteReadException`</a>
- Konflikt: Die aktuelle Transaktion liest Daten, die zwischenzeitlich von einer parallelen Transaktion gelöscht wurden — die gelesenen Zeilen existieren beim Commit nicht mehr.
```python
from delta.exceptions import ConcurrentDeleteReadException

try:
    (delta_table.alias("t")
        .merge(updates.alias("s"), "t.id = s.id")
        .whenMatchedUpdateAll()
        .execute())
except ConcurrentDeleteReadException as e:
    print(f"Gelesene Zeilen wurden parallel gelöscht: {e}")
```

## <a id="concurrentdeletedelete">8. `ConcurrentDeleteDeleteException`</a>
- Konflikt: Die aktuelle Transaktion versucht, Zeilen zu löschen, die bereits von einer parallelen Transaktion gelöscht wurden (zwei gleichzeitige `DELETE`-Vorgänge auf denselben Datensätzen).
```python
from delta.exceptions import ConcurrentDeleteDeleteException

try:
    delta_table.delete(condition="status = 'abgelaufen'")
except ConcurrentDeleteDeleteException as e:
    print(f"Zeilen wurden bereits parallel gelöscht: {e}")
```

## <a id="concurrenttransaction">9. `ConcurrentTransactionException`</a>
- Konflikt: Zwei parallele Transaktionen verwenden dieselbe idempotente Transaktions-ID (z. B. bei Streaming-Writern mit `txnAppId`/`txnVersion`) und versuchen beide, diese zu aktualisieren — Delta lässt nur einen Gewinner zu.
```python
from delta.exceptions import ConcurrentTransactionException

try:
    (streaming_df.write.format("delta")
        .option("txnAppId", "app-1")
        .option("txnVersion", "1")
        .mode("append")
        .save("/mnt/delta/events"))
except ConcurrentTransactionException as e:
    print(f"Idempotente Transaktion wurde parallel bereits verwendet: {e}")
```

## <a id="quellen">10. Quellen</a>
- `delta.exceptions` — vollständige Modulreferenz: https://docs.delta.io/api/latest/python/spark/

**Stand:** 2026-09-21.
