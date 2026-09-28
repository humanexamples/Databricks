# COPY INTO – Übersicht

Der SQL-Befehl `COPY INTO` lädt Daten aus Dateispeicherorten in Delta-Tabellen. Er ist wiederholbar (retriable) und idempotent: Dateien aus der Quelle, die bereits geladen wurden, werden bei erneuten Läufen übersprungen.

## Funktionsumfang

- Konfigurierbare Datei-/Ordnerfilter für Cloud-Speicher (S3, ADLS, ABFS, GCS und Unity-Catalog-Volumes)
- Unterstützung vieler Formate: CSV, JSON, XML, Avro, ORC, Parquet, Text- und Binärdateien
- Standardmäßig exakt einmalige Verarbeitung jeder Datei ("exactly-once")
- Schema-Inferenz, -Mapping, -Merging und -Evolution der Zieltabelle

## Wichtige Hinweise

Databricks empfiehlt, dass SQL-Nutzer für eine skalierbarere und robustere Dateiaufnahme stattdessen Streaming Tables verwenden.

Warnung: Deletion Vectors werden respektiert. Sind sie auf SQL-Warehouses oder ab Databricks Runtime 14.0 aktiviert, blockieren sie Abfragen auf Databricks Runtime 11.3 LTS und darunter.

## Voraussetzungen

Ein Account-Administrator muss den Datenzugriff für die Ingestion konfigurieren, bevor Nutzer mit `COPY INTO` Daten laden können.

## Zwei Lade-Ansätze

- **Schemalose Tabellen**: leere Platzhaltertabellen anlegen und das Schema beim Laden inferieren, indem `mergeSchema` auf `true` gesetzt wird.
- **Vordefiniertes Schema**: Tabellenstruktur zuerst festlegen, danach mit `COPY INTO` laden.

### Beispiel: Schemalose Tabelle

```sql
%sql
CREATE TABLE IF NOT EXISTS <catalog>.<schema>.booking_updates_schemaless;

COPY INTO <catalog>.<schema>.booking_updates_schemaless
FROM '/Volumes/<catalog>/<schema>/<volume>/wanderbricks/booking_updates'
FILEFORMAT = JSON
FORMAT_OPTIONS ('mergeSchema' = 'true', 'multiLine' = 'true')
COPY_OPTIONS ('mergeSchema' = 'true');
```

### Beispiel: Tabelle mit vordefiniertem Schema

```sql
%sql
DROP TABLE IF EXISTS <catalog>.<schema>.booking_updates_upload;

CREATE TABLE <catalog>.<schema>.booking_updates_upload (
  booking_id BIGINT,
  user_id BIGINT,
  status STRING,
  total_amount DOUBLE
);

COPY INTO <catalog>.<schema>.booking_updates_upload
FROM '/Volumes/<catalog>/<schema>/<volume>/wanderbricks/booking_updates'
FILEFORMAT = JSON
FORMAT_OPTIONS ('multiLine' = 'true');

SELECT * FROM <catalog>.<schema>.booking_updates_upload;
```

## Metadaten-Bereinigung

Ab Databricks Runtime 15.2 kann `VACUUM` verwendet werden, um von `COPY INTO` erzeugte, nicht mehr referenzierte Metadatendateien zu bereinigen.

## Weiterführende Ressourcen

- Daten mit Unity-Catalog-Volumes oder External Locations laden
- Gängige Ladeschemata mit `COPY INTO`
- SQL-Sprachreferenz für `COPY INTO` (ab Databricks Runtime 7.x)

---
**Quelle:** https://docs.databricks.com/aws/en/ingestion/cloud-object-storage/copy-into/  
**Stand:** 2026-08-07
