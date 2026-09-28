# Auto Loader — Directory Listing Mode

Quelle: [Configure Auto Loader streams in directory listing mode](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/directory-listing-mode).

Im Directory-Listing-Modus identifiziert Auto Loader neue Dateien, indem es das Eingabeverzeichnis auflistet. Dieser Ansatz ist optimiert, um Dateien in Cloud-Speicher effizienter zu entdecken als andere Apache-Spark-Optionen, und benötigt nur Zugriffsberechtigungen auf den Cloud-Speicher selbst.

---

## Wie Directory Listing funktioniert

Auto Loader reduziert die Anzahl der API-Aufrufe auf die Anzahl der Dateien im Speicher geteilt durch die Anzahl der von jedem API-Aufruf zurückgegebenen Ergebnisse, was die Cloud-Kosten deutlich reduziert.

Für eine nach Datum/Uhrzeit hierarchisch organisierte Struktur (`/some/path/YYYY/MM/DD/HH/fileName`, Dateien alle 5 Minuten) schätzt die Doku den API-Aufwand naiver Auflistung so ab: 1 (Basisverzeichnis) + 365 (pro Tag) × 24 (pro Stunde) = **8761 Aufrufe**. Auto Loader reduziert dies drastisch, indem es abgeflachte Antworten vom Speicher erhält.

### Ergebnisse pro API-Aufruf laut Doku

| Objektspeicher | Ergebnisse pro API-Aufruf |
|---|---|
| S3 | 1000 |
| ADLS | 5000 |
| GCS | 1024 |

---

## Lexikalische Reihenfolge der Dateien

Neu hochgeladene Dateien sollten für optimale Performance ein Präfix haben, das lexikografisch größer ist als das bestehender Dateien. Beispiele:

- **Versionierte Dateien:** Delta-Lake-Transaktionslogs (`00000000000000000000.json`, `00000000000000000001.json`).
- **Datumspartitionierte Dateien:** Formate wie `2021/12/01/10:11:23-randomString.json` (mit links mit Nullen aufgefüllten Datums-/Zeitkomponenten).

Ab Databricks Runtime 9.1 erkennt Auto Loader automatisch, ob Dateien in lexikalischer Reihenfolge eintreffen, und reduziert dadurch die Anzahl der API-Aufrufe.

---

## Incremental Listing (veraltet)

Incremental Listing ist veraltet; Databricks empfiehlt stattdessen den File-Notification-Modus mit File Events.

Ist `cloudFiles.useIncrementalListing` auf `"auto"` gesetzt, erkennt Auto Loader automatisch, ob ein gegebenes Verzeichnis für Incremental Listing geeignet ist, indem es Dateipfade zuvor abgeschlossener Verzeichnisauflistungen prüft und vergleicht. Um die Datenvollständigkeit sicherzustellen, löst Auto Loader automatisch eine vollständige Verzeichnisauflistung aus, nachdem **7 aufeinanderfolgende inkrementelle Auflistungen** abgeschlossen wurden. Über `cloudFiles.backfillInterval` (siehe [09 Datei-Tracking und Checkpoints.md](09%20Datei-Tracking%20und%20Checkpoints.md)) lässt sich diese Häufigkeit zusätzlich steuern.

---

## Pfad-Änderung ohne neuen Checkpoint

Ab **Databricks Runtime 11.3 LTS** lässt sich der Eingabepfad im Directory-Listing-Modus ändern, ohne einen neuen Checkpoint-Pfad zu benötigen — nützlich z. B. für tägliche Ingestion-Jobs mit unterschiedlich datumsorganisierten Verzeichnissen. Im File-Notification-Modus wird dies **nicht** unterstützt.
