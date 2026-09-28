[← Übersicht](00%20Uebersicht.md)

# Fall 8 – Späte / unsortierte Dateien (Datei von gestern kommt heute an)

**A) Auto Loader** verarbeitet sie normal, sobald sie erscheinen – Ankunftsreihenfolge ist egal, da pro Pfad getrackt wird.

**B) Fachliche Reihenfolge** über eine Business-Spalte statt Ankunftszeit:
- in `AUTO CDC INTO`: `SEQUENCE BY event_timestamp`
- bei manuellem `MERGE`: `row_number() OVER (PARTITION BY id ORDER BY event_timestamp DESC)`

**C) `AUTO CDC FROM SNAPSHOT`**: out-of-order-Snapshots (niedrigere Version als bereits verarbeitet) werden **ignoriert** – Versionsvergabe muss monoton sein (siehe [Fall 5](05%20Periodische%20Voll-Snapshots.md)).

**D) Später-als-Toleranz beim Streaming** über Watermark, falls aggregiert wird:

```python
.withWatermark("event_timestamp", "3 days")
```

---
[← Vorheriger Fall](07%20Backfill%20zusaetzlich%20zum%20Stream.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](09%20Korrektur%2C%20Teilmenge%20neu%20laden.md)
