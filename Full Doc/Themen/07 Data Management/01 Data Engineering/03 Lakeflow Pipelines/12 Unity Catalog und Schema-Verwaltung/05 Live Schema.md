# LIVE-Schema (Legacy)

Das virtuelle `LIVE`-Schema ist eine veraltete Funktionalität, die an den **Legacy Publishing Mode** von Lakeflow Declarative Pipelines gebunden ist. Sie funktioniert weiterhin für bestehende, damit erstellte Pipelines, Databricks empfiehlt aber ausdrücklich die Migration zum aktuellen Default Publishing Mode (siehe `Migration zu DPM.md`). Jede Aussage wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/live-schema` verifiziert.

## Abschnittsübersicht

1. [Was ist das virtuelle LIVE-Schema?](#was-ist-live)
2. [Legacy Publishing Mode für Pipelines](#legacy-mode)
3. [Quellcode vom LIVE-Schema aktualisieren](#quellcode-aktualisieren)
4. [Event Log für Unity-Catalog-Legacy-Publishing-Mode-Pipelines](#event-log)
5. [Quellen](#quellen)

---

## <a id="was-ist-live">1. Was ist das virtuelle LIVE-Schema?</a>

Das `LIVE`-Schema ist ein Programmierkonzept in Pipelines, das eine virtuelle Grenze für alle in einer Pipeline erstellten oder aktualisierten Datasets definiert. Es funktioniert unabhängig von veröffentlichten Schemas und erlaubt die Ausführung von Pipeline-Logik, ohne dass Datasets in ein Schema veröffentlicht werden müssen.

Im Legacy Mode referenzieren Entwickler andere Pipeline-Datasets über eine Syntax wie `SELECT * FROM LIVE.bronze_table`. Der Default Publishing Mode ignoriert diese Syntax stillschweigend — unqualifizierte Bezeichner referenzieren stattdessen das konfigurierte Pipeline-Schema.

**Support-Hinweis:** Die Unterstützung für das legacy `LIVE`-Virtual-Schema und den Legacy Publishing Mode ist für die Entfernung in einer zukünftigen Version vorgesehen.

### Migrationswege

Zwei Wege stehen zur Verfügung:

1. **Tabellen verschieben** (Materialized Views, Streaming Tables) von Legacy-Pipelines zu Pipelines im Default Mode (siehe `Tabellen verschieben.md`).
2. **Default Publishing Mode direkt in bestehenden Legacy-Pipelines aktivieren** (siehe `Migration zu DPM.md`).

Beide Migrationswege sind **unumkehrbar** — Tabellen können nicht zurück in den Legacy Mode wechseln. Die UI kennzeichnet Legacy-Pipelines im **Summary**-Feld. Neue Pipelines können über die Konfigurations-UI nicht mehr im Legacy Publishing Mode erstellt werden — nur Tabellen von vor dem 5. Februar 2025 nutzen standardmäßig noch diesen Modus.

---

## <a id="legacy-mode">2. Legacy Publishing Mode für Pipelines</a>

Die Doku beschreibt eine Matrix zur Speicherort- und Metadaten-Handhabung im Legacy Publishing Mode, abhängig von Kombinationen aus Speicherort und Zielschema:

**Hive-Metastore-Szenarien:**

- Kein Speicherort/kein Zielschema angegeben: Metadaten und Daten liegen im DBFS-Root; keine Metastore-Registrierung.
- Speicherort angegeben, kein Zielschema: Daten liegen am angegebenen Speicherort; keine Metastore-Registrierung.
- Kein Speicherort, Zielschema angegeben: Daten liegen im DBFS-Root; Tabellen werden im angegebenen Hive-Schema veröffentlicht.
- Sowohl Speicherort als auch Zielschema angegeben: Daten liegen am angegebenen Speicherort; Tabellen werden im Hive-Schema veröffentlicht.

**Unity-Catalog-Szenarien:**

- Katalog angegeben, kein Zielschema: Daten liegen im Standard-Speicherort des Katalogs; keine Registrierung.
- Sowohl Katalog als auch Schema angegeben: Daten liegen im Standard-Speicherort von Schema/Katalog; Tabellen werden im Unity-Catalog-Schema veröffentlicht.

---

## <a id="quellcode-aktualisieren">3. Quellcode vom LIVE-Schema aktualisieren</a>

Die zentrale Migrationsüberlegung betrifft unqualifizierte Tabellenreferenzen: Der Legacy Mode löste diese standardmäßig gegen den Default-Katalog und das Default-Schema des Workspace auf (z. B. `main.default.raw_data`). Der Default Mode nutzt stattdessen den in der Pipeline konfigurierten Katalog und das konfigurierte Schema.

**Beispiel für nötige Anpassung:**

Legacy-Code:

```sql
CREATE MATERIALIZED VIEW silver_table
AS SELECT * FROM raw_data
```

Aktualisierter Code:

```sql
CREATE MATERIALIZED VIEW silver_table
AS SELECT * FROM main.default.raw_data
```

Diese Anpassung stellt sicher, dass Legacy-Code nach der Migration wie beabsichtigt weiterläuft.

---

## <a id="event-log">4. Event Log für Unity-Catalog-Legacy-Publishing-Mode-Pipelines</a>

Für Legacy-Pipelines, die nach Unity Catalog veröffentlichen, liefert die Table Valued Function (TVF) `event_log` den Zugriff auf Events.

**Nach Pipeline-ID:**

```sql
SELECT * FROM event_log("04c78631-3dd7-4856-b2a6-7d84e9b2638b")
```

**Nach Tabellen-Zugehörigkeit:**

```sql
SELECT * FROM event_log(TABLE(my_catalog.my_schema.table1))
```

Die TVF erfordert Zugriff über ein SQL Warehouse oder einen Shared Cluster. Pipeline-Owner können Views erstellen, um wiederholte Abfragen zu vereinfachen:

```sql
CREATE VIEW event_log_raw AS SELECT * FROM event_log("<pipeline-ID>");
```

**Wichtige Einschränkungen:** Nur Pipeline-Owner können die TVF aufrufen; sie kann nicht mehrere Pipelines gleichzeitig abfragen; erstellte Views können nicht mit anderen Nutzern geteilt werden.

Um das jüngste Pipeline-Update zu isolieren:

```sql
CREATE OR REPLACE TEMP VIEW latest_update AS
SELECT origin.update_id AS id
FROM event_log_raw
WHERE event_type = 'create_update'
ORDER BY timestamp DESC
LIMIT 1;
```

Für Hive-Metastore-Pipelines gelten separate Event-Log-Mechanismen (siehe `Hive Metastore.md`).

---

## <a id="quellen">5. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/live-schema

**Stand:** 2026-08-19
