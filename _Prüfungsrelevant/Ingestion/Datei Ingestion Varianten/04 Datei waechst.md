[← Übersicht](00%20Uebersicht.md)

# Fall 4 – Datei wächst (wird an dieselbe Datei angehängt)

Wird von Databricks nicht sauber unterstützt.

**A) `cloudFiles.allowOverwrites = true`** – Auto Loader liest bei jeder Änderung die **gesamte** Datei neu (nicht nur den Zuwachs) → immer per Upsert/Dedup nachbearbeiten (siehe [Fall 3, Abschnitt 3](03%20Gleiche%20Datei%20wird%20ueberschrieben.md#s3)).

**B) Empfohlene Alternative: Quelle auf rotierende Dateien umstellen** (`log_00001.json`, `log_00002.json`, …) → dann Standard-Append ([Fall 2](02%20Append-only.md)).

**C) Streaming direkt aus der Quelle** statt aus Dateien (Kafka, Kinesis, Zerobus), falls die Quelle das erlaubt.

---
[← Vorheriger Fall](03%20Gleiche%20Datei%20wird%20ueberschrieben.md) · [Übersicht](00%20Uebersicht.md) · [Nächster Fall →](05%20Periodische%20Voll-Snapshots.md)
