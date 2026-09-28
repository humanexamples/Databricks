# Auto Loader — Best Practices

Quelle: [Auto Loader best practices](https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/best-practices).

---

## Die richtige Ausführungs-Umgebung wählen

> *"Lakeflow pipelines extend Structured Streaming with autoscaling, data quality checks, schema evolution handling, and monitoring through the event log."*

Databricks empfiehlt diesen Ansatz für die meisten produktiven Ingestion-Workloads.

---

## Die richtige Planung und den richtigen Trigger-Typ wählen

Databricks empfiehlt für die meisten Anwendungsfälle einen **File-Arrival-Trigger mit aktivierten File Events** — das erreicht niedrige Latenz bei niedrigen Kosten.

| Trigger-Typ | Latenz | Kosten | Am besten für |
|---|---|---|---|
| **Continuous** | Sub-Sekunde | Am höchsten | Nur wenn Sub-Sekunden-Latenz eine harte Anforderung ist (Continuous Compute ist teurer). |
| **File-Arrival-Trigger** | Niedrig bis mittel | Am niedrigsten | Unregelmäßige Muster beim Eintreffen von Dateien; benötigt File Events. |
| **Scheduled** | Minuten bis Stunden | Mittel | Großzügige Latenzanforderungen (zeitbasierter Zeitplan, z. B. stündlich). |

> **Begriffliche Abgrenzung:** Dies sind **Lakeflow-Pipeline**-Trigger-Konfigurationen — nicht zu verwechseln mit dem Structured-Streaming-eigenen `.trigger()`-Parameter (`processingTime` / `once` / `availableNow` / `continuous`), der auf einer anderen Ebene liegt (siehe [14 Common Data Loading Patterns.md](14%20Common%20Data%20Loading%20Patterns.md)).

---

## Den richtigen Datei-Erkennungsmodus wählen

File Events bündeln Cloud-Speicher-Ressourcen, indem sie ein Abonnement und eine Queue **pro External Location** statt pro Stream verwenden.

| Modus | Setup | Skalierbarkeit | Kosten | Einsatzempfehlung |
|---|---|---|---|---|
| **File Events** | Niedrig (einmalige Berechtigungseinrichtung) | Millionen Dateien pro Stunde | Am niedrigsten | Standard für die meisten Workloads |
| **Klassischer File Notification Mode** | Hoch (über 21 Cloud-Konfigurationsoptionen laut Doku) | Millionen Dateien pro Stunde | Mittel | Wenn File Events nicht verfügbar sind |
| **Directory Listing** | Keine | Begrenzt durch Verzeichnisgröße | Am höchsten (`LIST`-API-Kosten) | Kleine Verzeichnisse, einmalige Backfills, oder Sicherheitsrichtlinien, die andere Modi ausschließen |

Der entscheidende Unterschied: File Events liefern Benachrichtigungen über neue Dateien direkt, sodass die Ingestion-Zeit unabhängig von der Anzahl der Objekte im Verzeichnis niedrig bleibt.

### File Events aktivieren, bzw. wann sie nicht genutzt werden können

File Events erfordern eine einmalige Cloud-Berechtigungsvergabe und eine External Location, die für den Managed-File-Events-Dienst konfiguriert ist. Fehlt diese Konfiguration, oder verhindern organisatorische Sicherheitsrichtlinien die Aktivierung, bleibt nur Directory Listing oder der klassische Modus.

```python
.option("cloudFiles.useManagedFileEvents", "true")
```

---

## Schema-Evolution steuern

| Szenario | Empfehlung |
|---|---|
| Bekanntes, festes Schema | `.schema()` für explizite Definition verwenden |
| Unbekannt, nur additive Änderungen | `schemaEvolutionMode` = `addNewColumns` |
| Unbekannt, mit Typänderungen | `schemaEvolutionMode` = `addNewColumnsWithTypeWidening` |
| Strikter Schema-Vertrag | `schemaEvolutionMode` = `failOnNewColumns` |
| Unvorhersehbar / beliebig | Als `Variant`-Typ aufnehmen |

Details: [01 Schema-Inferenz und -Evolution.md](01%20Schema-Inferenz%20und%20-Evolution.md), [02 Automatisches Type Widening.md](02%20Automatisches%20Type%20Widening.md).

### Schema Hints für bekannte Feldtypen nutzen

```python
.option("cloudFiles.schemaHints", "id long, amount double")
```

### Als Variant-Typ aufnehmen bei unvorhersehbaren Schemata

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("singleVariantColumn", "data")
  .load("/Volumes/analytics/bronze/events"))
```

---

## Schlechte Daten und Datenqualität handhaben

### `_rescued_data` und `_corrupt_record` aktivieren

`_rescued_data` erfasst Felder, die nicht mit dem aktuellen Schema übereinstimmen; Auto Loader fügt die Spalte automatisch hinzu.

```python
.option("cloudFiles.schemaHints", "_corrupt_record string")
.option("columnNameOfCorruptRecord", "_corrupt_record")
```

### Lakeflow-Pipelines-Expectations zum Monitoring

Expectations setzen, die prüfen, dass `_rescued_data` und `_corrupt_record` unter Normalbedingungen `NULL` sind.

```python
import dlt

@dlt.table
@dlt.expect("no rescued data", "_rescued_data IS NULL")
@dlt.expect("no corrupt records", "_corrupt_record IS NULL")
def bronze_table():
    return (spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/Volumes/analytics/bronze/events"))
```

### Beschädigte Daten isolieren

Zeilen mit `_corrupt_record IS NOT NULL` in eine dedizierte Quarantäne-Senke isolieren. Das verhindert, dass beschädigte Daten in nachgelagerte Schichten propagieren.

### Daten mit Quelldatei-Metadaten annotieren

Die Spalte `_metadata` in Auto-Loader-Ingestion-Abfragen einbeziehen — mindestens `file_path` und `file_modification_time`.

```python
.select("*", "_metadata.file_path", "_metadata.file_modification_time")
```

---

## Kosten und Performance optimieren

Drei Hauptkostentreiber: Cloud-`LIST`-API-Aufrufe, ungenutzte (idle) Compute-Ressourcen und langfristiges Speicherwachstum.

- **File Events zur Kostenoptimierung:** liefern inkrementelle Datei-Erkennung, wodurch vollständige Verzeichnisauflistungen entfallen.
- **File-Arrival-Trigger:** starten die Pipeline nur, wenn neue Dateien eintreffen — keine Kosten für ungenutzte Compute-Ressourcen.
- **Archivierung mit `cleanSource`:** `cloudFiles.cleanSource` = `"delete"` oder `"move"` reduziert Speicher- und Verzeichnisauflistungskosten (siehe [10 Clean Source (Quelldateien aufräumen).md](10%20Clean%20Source%20%28Quelldateien%20aufräumen%29.md)).
- Neueste Databricks Runtime oder Serverless Compute verwenden.

---

## Checkpoint-Management

- Auf Checkpoint-Speicherorte niemals Cloud-Objekt-Lifecycle-Richtlinien anwenden — werden Checkpoint-Dateien gelöscht, wird der Stream-Zustand beschädigt.
- Für jeden Stream und jedes Quellverzeichnis separate Checkpoints verwenden.
- Für langlebige, hochvolumige Streams `cloudFiles.maxFileAge` erwägen (konservativ, mindestens 90 Tage empfohlen).

---

## Volumes für optimale Datei-Erkennung mit File Events

Für bessere Performance mit File Events für jeden Pfad bzw. jedes Unterverzeichnis ein eigenes External Volume anlegen (`/Volumes/catalog/schema/volume` statt `s3://bucket/path`).
