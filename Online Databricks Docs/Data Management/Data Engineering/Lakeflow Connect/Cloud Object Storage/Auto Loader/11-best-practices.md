# Auto Loader Best Practices

Lakeflow-Pipelines erweitern Structured Streaming um Autoskalierung, Datenqualitätsprüfungen, Behandlung von Schema Evolution und Monitoring über das Event-Log. Databricks empfiehlt diesen Ansatz für die meisten Produktiv-Workloads – Structured Streaming bietet dagegen maximale Kontrolle, Managed Connectors die einfachste Einrichtung.

## Zeitplanung und Trigger-Typen

Je nach Latenzanforderung gibt es drei Optionen:

- **Continuous:** für Anforderungen im Sub-Sekundenbereich; höchste Kosten
- **File-Arrival-Trigger:** empfohlen für niedrige bis mittlere Latenz; läuft nur, wenn Dateien eintreffen
- **Scheduled:** zeitgesteuerte Ausführung; geeignet, wenn Minuten bis Stunden Latenz toleriert werden

## Dateierkennungsmodi im Vergleich

| Modus | Komplexität | Skalierbarkeit | Kosten | Am besten geeignet für |
| --- | --- | --- | --- | --- |
| File Events (empfohlen) | Niedrig | Millionen/Stunde | Am niedrigsten | Standard für die meisten Workloads |
| Klassischer File Notification | Hoch | Millionen/Stunde | Mittel | Wenn File Events nicht verfügbar sind |
| Directory Listing | Keine | Begrenzt | Am höchsten | Kleine Verzeichnisse, Backfills |

### File Events aktivieren

File Events erfordern eine einmalige Cloud-Berechtigungsfreigabe sowie eine für den Managed-File-Events-Dienst konfigurierte External Location:

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.useManagedFileEvents", "true")
  .load("/path/to/data/dir"))
```

## Umgang mit Schema Evolution

| Szenario | Empfehlung |
| --- | --- |
| Bekanntes, festes Schema | Explizites `.schema()` verwenden |
| Unbekannt, nur additive Änderungen | `schemaEvolutionMode: addNewColumns` |
| Unbekannt, mit Typänderungen | `schemaEvolutionMode: addNewColumnsWithTypeWidening` |
| Strikte Anforderungen | `schemaEvolutionMode: failOnNewColumns` |
| Unvorhersehbares Schema | Als `Variant`-Typ einlesen |

**Schema-Hints-Beispiel:**

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.schemaHints", "id long, amount double")
  .load("/path/to/data/dir"))
```

**Type Widening:**

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.schemaEvolutionMode",
    "addNewColumnsWithTypeWidening")
  .load("/path/to/data/dir"))
```

**Ingestion als Variant:**

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("singleVariantColumn", "data")
  .load("/path/to/data/dir"))
```

## Umgang mit Datenqualität

**Rescue-Spalten aktivieren:**

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.schemaHints", "_corrupt_record string")
  .option("columnNameOfCorruptRecord", "_corrupt_record")
  .load("/path/to/data/dir"))
```

Databricks empfiehlt `columnNameOfCorruptRecord` gegenüber `badRecordsPath`, um mögliche Race Conditions zu vermeiden.

**Lakeflow Expectations:**

```python
@dlt.table
@dlt.expect("no rescued data", "_rescued_data IS NULL")
@dlt.expect("no corrupt records", "_corrupt_record IS NULL")
def bronze_table():
    return (spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .load("/path/to/data/dir"))
```

**Fehlerhafte Daten isolieren:**

```python
@dlt.table
def corrupt_records_sink():
    return dlt.read_stream("bronze_table").where(
        "_corrupt_record IS NOT NULL")

@dlt.view
def clean_table():
    return dlt.read_stream("bronze_table").where(
        "_corrupt_record IS NULL")
```

**Metadaten anfügen:**

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .load("/path/to/data/dir")
  .select("*", "_metadata.file_path",
    "_metadata.file_modification_time"))
```

## Kosten- und Performance-Optimierung

Wichtige Strategien:

- **File Events nutzen**, um vollständige Verzeichnisscans zu vermeiden
- **File-Arrival-Trigger**, um Leerlaufkosten für Compute zu vermeiden
- **`cloudFiles.cleanSource`**, um Speicher- und Listing-Kosten zu senken

```python
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "json")
  .option("cloudFiles.cleanSource", "delete")
  .load("/path/to/data/dir"))
```

**Warnung:** `cloudFiles.cleanSource` nicht aktivieren, wenn mehrere Auto-Loader-Streams oder andere Clients aus demselben Quellverzeichnis lesen.

## Checkpoint-Verwaltung

- Auf Checkpoint-Speicherorte niemals Cloud-Lifecycle-Richtlinien anwenden.
- Separate Checkpoints pro Stream/Verzeichnis verwenden.
- Bei langlebigen Streams `cloudFiles.maxFileAge` in Betracht ziehen (mindestens 90 Tage empfohlen).

## Volumes für File Events nutzen

Für jeden Pfad bzw. jedes Unterverzeichnis, aus dem Auto Loader lädt, ein externes Volume anlegen. Auto Loader Volume-Pfade übergeben (z. B. `/Volumes/catalog/schema/volume`) statt Cloud-Pfade.

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/auto-loader/best-practices  
**Stand:** 2026-08-07
