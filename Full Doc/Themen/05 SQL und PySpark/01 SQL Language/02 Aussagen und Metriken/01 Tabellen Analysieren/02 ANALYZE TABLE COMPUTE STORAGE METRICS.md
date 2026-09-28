# `ANALYZE TABLE ... COMPUTE STORAGE METRICS`

Berechnet umfassende Storage-Größenmetriken für eine einzelne Tabelle — Gesamt-Bytes, aktive Bytes, vacuumfähige Bytes und Time-Travel-Bytes samt zugehöriger Dateianzahlen. Gedacht für Plattform-Administratoren, die Storage-Muster und Optimierungspotenzial über den Datenbestand hinweg analysieren.

## Syntax

```sql
ANALYZE TABLE table_name COMPUTE STORAGE METRICS
    [ USING INVENTORY LOCATION inventory_path CONF conf_name ]
```

## Parameter

| Parameter/Klausel | Bedeutung |
|---|---|
| `table_name` | Zieltabelle — ohne zeitliche oder Options-Spezifikation, keine Pfadangabe; löst `TABLE_OR_VIEW_NOT_FOUND` aus, falls nicht vorhanden |
| `USING INVENTORY LOCATION inventory_path CONF conf_name` (optional) | liest Metriken aus einem vorab generierten Cloud-Storage-Inventory-Report, statt Dateien direkt zu scannen |
| `LOCATION inventory_path` | vollständiger Cloud-Storage-Pfad zum Inventory-Report inkl. Präfix, z. B. `'s3://your-destination-bucket/your-prefix/'` — muss über eine zugängliche External Location abgesichert sein |
| `CONF conf_name` | Bezeichner der Inventory-Report-Konfiguration — der `Id`-Wert aus dem AWS-CLI-Setup bzw. der Konfigurationsname aus der AWS-Konsole |

## Verhalten ohne `USING INVENTORY`

Standardmäßig scannt der Befehl die Tabellendateien direkt — je nach Tabellengröße kann das Minuten bis mehrere Stunden dauern. Funktioniert sowohl mit Unity-Catalog-Managed- als auch mit External Tables. **Wichtig:** Die Ergebnisse werden zur Laufzeit berechnet, **nicht** in Unity Catalog gespeichert und **nicht** in `DESCRIBE EXTENDED` widergespiegelt — für eine Zeitreihe müssen die Ergebnisse periodisch selbst erfasst und gespeichert werden.

## Ausgabemetriken (8 Zeilen)

| Metrik | Definition |
|---|---|
| `total_bytes` | Summe aus Transaktionslog-, aktiven, vacuumfähigen und Time-Travel-Bytes |
| `num_total_files` | Gesamtzahl Dateien inkl. Delta-Log-, aktiver, vacuumfähiger und Time-Travel-Dateien |
| `active_bytes` | Größe der von der Tabelle aktiv referenzierten Datendateien (entspricht `sizeInBytes`) |
| `num_active_files` | von der aktuellen Tabellenversion aktiv referenzierte Dateien |
| `vacuumable_bytes` | über `VACUUM` oder Predictive Optimization zurückgewinnbare Datenmenge |
| `num_vacuumable_files` | Anzahl vacuumfähiger Dateien |
| `time_travel_bytes` | historische Datenmenge für Rollbacks und Time-Travel-Operationen |
| `num_time_travel_files` | Dateien, die Time-Travel-Funktionalität unterstützen |

## `USING INVENTORY`: Anwendungsfall, Voraussetzungen und Einschränkungen

**Verfügbarkeit:** ab Databricks Runtime 19+. Databricks empfiehlt diese Klausel für Tabellen mit **100.000+ Dateien** oder starker Partitionierung, bei denen ein direkter Scan zu lange dauert.

**Wichtiger Vorbehalt:** „Inventory-Reports nur dort nutzen, wo veraltete Metriken akzeptabel sind." Die Metriken spiegeln den Tabellenzustand des letzten Inventory-Reports wider — potenziell bis zu 24 Stunden alt und damit ggf. abweichend von einem direkten Scan.

**Voraussetzungen:**

1. **Privilegien:** Metastore-Admins haben standardmäßig Zugriff. Andere benötigen: Cloud-Provider-Berechtigungen zum Konfigurieren von Inventory-Reports sowie das Databricks-Privileg `CREATE EXTERNAL LOCATION` auf dem Metastore plus ein Storage Credential, **oder** das `MANAGE`-Privileg auf der External Location.
2. **Konfigurierter Inventory-Report:** AWS-S3-Inventory auf jedem Quell-Bucket mit: Objektversionen = nur aktuelle Version; Häufigkeit = täglich; Ausgabeformat = Apache Parquet; Metadatenfelder müssen **`Size`** und **`LastModifiedDate`** enthalten.
3. **External Location:** Lesezugriff in Databricks auf den Zielpfad des Inventory-Reports — bei Bedarf als External Location registrieren.
4. **Befehls-Privilegien:** `READ FILES`-Privileg auf der die Inventory-Destination absichernden External Location, zusätzlich zu den bestehenden Tabellenprivilegien.

**Generierungsdauer beim Cloud-Provider:** Erster Inventory-Report benötigt 48 Stunden (AWS) bzw. 24 Stunden (Azure, GCP).

**Fehler bei veraltetem Inventory:** Der Befehl sucht nach dem aktuellsten vollständigen Inventory-Report der letzten 14 Tage. Wird keiner gefunden, erscheint der Fehler `ANALYZE_TABLE_COMPUTE_STORAGE_METRICS_INVENTORY_CONTENTS_NOT_VALID` mit einer Meldung, dass zwar Report-Verzeichnisse existieren, aber außerhalb des Lookback-Fensters liegen. Abhilfe: sicherstellen, dass die geplante Inventory-Report-Generierung läuft, und den Befehl nach Erstellung eines neuen Reports erneut ausführen.

**Weitere Einschränkungen von `USING INVENTORY`:**

- Nur auf **Classic Compute** — nicht unterstützt auf Serverless Compute oder SQL-Warehouses.
- Nur für Catalog-Tabellen (Managed und External) — löst `ANALYZE_TABLE_COMPUTE_STORAGE_METRICS_NOT_SUPPORTED` für pfadbasierte Delta-Lake-Tabellen aus.
- Ergebnisse nicht garantiert korrekt, falls Object Versioning auf dem Quell-Bucket/-Container aktiviert ist.
- Erfordert eine erneute Inventory-Konfiguration, falls sich der Storage-Ort der Tabelle ändert.

## Besonderheiten bei bestimmten Tabellentypen

| Tabellentyp | Besonderheit |
|---|---|
| Materialized Views / Streaming Tables | `total_bytes` umfasst Tabelle **und** Metadaten; `active_bytes` schließt vacuumfähige und Time-Travel-Bytes aus |
| Shallow Clones | `total_bytes` umfasst nur die Metadaten und das Delta-Log des Klons (ohne die Dateien der Quelltabelle); `active_bytes` ist **null**, da der Klon auf die Quelldaten verweist |

## Beispiele

**Direkter Scan:**

```sql
ANALYZE TABLE main.my_schema.my_table COMPUTE STORAGE METRICS;
```

Beispielausgabe:

```
metric_name              metric_value  metric_description
total_bytes                5368709120  Total bytes on disk
num_total_files                  1250  Total files on disk
active_bytes                4294967296  Bytes in current snapshot
num_active_files                  1000  Files in current snapshot
vacuumable_bytes             805306368  Bytes eligible for vacuum
num_vacuumable_files               150  Files eligible for vacuum
time_travel_bytes            268435456  Bytes reachable by time travel (excluding active)
num_time_travel_files              100  Files reachable by time travel (excluding active)
```

(5,37 GB gesamt über 1.250 Dateien; 4,29 GB aktiv; 805 MB vacuumfähig; 268 MB Time-Travel.)

**Mit Inventory-Report:**

```sql
ANALYZE TABLE main.my_schema.my_table COMPUTE STORAGE METRICS
USING INVENTORY LOCATION 's3://your-destination-bucket/your-prefix/'
CONF 'databricks-inventory-list-config';
```

**Storage-Metriken für alle Tabellen eines Catalogs** (Python, iteriert über `information_schema.tables`):

```python
tables = spark.sql("""
  SELECT table_catalog, table_schema, table_name
  FROM main.information_schema.tables
  WHERE table_type IN (
    'MANAGED', 'EXTERNAL',
    'STREAMING_TABLE', 'MATERIALIZED_VIEW',
    'MANAGED_SHALLOW_CLONE', 'EXTERNAL_SHALLOW_CLONE'
  )""").collect()
for t in tables:
    full_name = f"{t.table_catalog}.{t.table_schema}.{t.table_name}"
    result = spark.sql(f"""
      ANALYZE TABLE {full_name} COMPUTE STORAGE METRICS
      USING INVENTORY LOCATION 's3://your-destination-bucket/your-prefix/'
      CONF 'databricks-inventory-list-config'
    """)
    result.show()
```

**Quellen:**
- https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-aux-analyze-compute-storage-metrics
- https://docs.databricks.com/aws/en/sql/language-manual/delta-vacuum
- https://docs.databricks.com/aws/en/optimizations/predictive-optimization
