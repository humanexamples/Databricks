# Jobs bei neuen Dateien auslösen

File-Arrival-Trigger lösen einen Job aus, wenn neue Dateien in externen Speicherorten (S3, Azure Storage, GCS) eintreffen — nützlich bei unregelmäßigem statt planbarem Dateneingang.

## Funktionsweise

Das System prüft ca. **einmal pro Minute** auf neue Dateien (Cloud-Speicher-Performance kann diese Frequenz beeinflussen). Keine Zusatzkosten über die üblichen Cloud-Gebühren für Dateiauflistung hinaus.

Überwacht werden können:

- der Root eines Unity-Catalog External Location oder Volume,
- Unterpfade davon.

Beispiel gültiger Pfade für ein Volume `/Volumes/mycatalog/myschema/myvolume/`:

```
/Volumes/mycatalog/myschema/myvolume/
/Volumes/mycatalog/myschema/myvolume/mydirectory/
```

Trigger prüfen rekursiv alle Unterverzeichnisse.

### Mit File Events

Für optimale Performance File Events auf der External Location aktivieren — Databricks nutzt dann einen internen Dienst, der Ingestion-Metadaten über Cloud-Provider-Änderungsbenachrichtigungen verfolgt. Bestehende Trigger profitieren innerhalb von Minuten, neue innerhalb von Sekunden.

## Voraussetzungen

- Unity Catalog im Workspace aktiviert.
- Speicherort ist ein Volume oder eine Unity-Catalog-External-Location.
- `READ`-Berechtigung auf dem Speicherort und `CAN MANAGE` auf dem Job.
- Empfohlen: External Locations für Managed File Events aktivieren (erfordert `MANAGE`-Privileg oder Eigentümerschaft der External Location).

## Trigger hinzufügen

1. **Jobs & Pipelines** in der Sidebar.
2. Optional Filter **Jobs**/**Owned by me**.
3. Job-Namen anklicken.
4. **Add trigger** im Job-Details-Panel.
5. Trigger-Typ **File arrival**.
6. Speicherort-URL (Root oder Unterpfad) eingeben.
7. Optional erweiterte Optionen zur Ratenbegrenzung.
8. **Test connection**.
9. **Save**.

## Lauffrequenz steuern

- **Minimum time between triggers (seconds):** Cooldown — maximal ein Lauf pro Zeitraum.
- **Wait after last change (seconds):** Debouncing — wartet, bis für die angegebene Dauer keine neuen Dateien mehr eintreffen; jede neue Ankunft setzt den Timer zurück.

Beide Optionen sind unabhängig oder kombiniert nutzbar.

**Beispiele:**

- Maximal alle 15 Minuten: `Minimum time between triggers in seconds: 900`
- Auf vollständigen Batch warten: `Wait after last change in seconds: 60`
- Beides kombiniert: `900` + `60`

## Dateien mit Auto Loader verarbeiten

**Beispiel 1 — in Delta-Tabelle laden:**

```python
file_location = "[REPLACE]" # dieselbe URL wie im File-Arrival-Trigger
checkpoint_location = "[REPLACE]" # separate URL außerhalb von file_location
sink_table = "[REPLACE]"

streamingQuery = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "json") \
  .option("cloudFiles.schemaLocation", checkpoint_location) \
  .option("cloudFiles.useManagedFileEvents","true") \
  .load(file_location) \
  .writeStream \
  .option("checkpointLocation", checkpoint_location) \
  .trigger(availableNow = True) \
  .toTable(sink_table)
```

**Beispiel 2 — benutzerdefinierte Verarbeitung mit `foreachBatch`:**

```python
file_location = "[REPLACE]"
checkpoint_location = "[REPLACE]"

def process_batch(batch_df, batch_id):
  file_url = batch_df.select("path").collect()[0].path
  # [REPLACE] eigene Verarbeitungslogik für neu eingetroffene Dateien

streamingQuery = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "binaryFile") \
  .option("cloudFiles.useManagedFileEvents","true") \
  .load(file_location) \
  .drop("content") \
  .writeStream \
  .foreachBatch(process_batch) \
  .option("checkpointLocation", checkpoint_location) \
  .start()
```

`foreachBatch` garantiert nur At-least-once-Verarbeitung.

## Einschränkungen

**Allgemein:**

- Nur neue Dateien lösen Läufe aus — Überschreiben bestehender Dateien nicht.
- Pfade dürfen keine External Tables oder Managed Locations enthalten.
- Keine Wildcards (`*`, `?`) in Pfaden.

**Mit File Events:**

- Keine Mengenbegrenzung für Dateien.
- Trigger können bei sehr vielen irrelevanten Datei-Updates timeouten.
- Unterpfad-Trigger können bei häufigen Root-Level-Änderungen fehlerhaft reagieren — Workaround: eigenes Unity-Catalog-Volume direkt auf das Zielverzeichnis mappen.
- Geänderte Dateien mit Metadaten außerhalb des Rolling-Retention-Zeitraums gelten als neue Ankünfte — Vermeidung durch unveränderliche Dateien oder Auto-Loader-Fortschrittsverfolgung.

**Ohne File Events:**

- Maximal 50 Jobs mit File-Arrival-Triggern pro Workspace.
- Speicherort auf 10.000 Dateien begrenzt (Unterpfad, nicht Root).

### Nicht existierende Pfade (S3, GCS)

Existiert der konfigurierte Pfad nicht (mehr), wertet der Trigger weiterhin fehlerfrei aus — S3/GCS unterscheiden nicht zwischen nicht-existent, gelöscht und leer. Kein Fehlschlag, keine Fehlerbenachrichtigung, einfach kein Auslösen, bis Dateien hinzukommen.

## Quelle

- https://docs.databricks.com/aws/en/jobs/file-arrival-triggers
