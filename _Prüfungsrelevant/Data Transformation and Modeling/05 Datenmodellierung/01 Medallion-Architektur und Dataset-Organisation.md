# Medallion-Architektur und Dataset-Organisation

## Was ist die Medallion Architecture?

Daten-Design-Pattern (auch **Multi-Hop-Architektur**) zur logischen Organisation von Daten in Qualitätsschichten: **Bronze ⇒ Silver ⇒ Gold**. Jede Schicht verbessert Struktur/Qualität inkrementell; Atomicity/Consistency/Isolation/Durability über alle Validierungs-/Transformationsschritte hinweg.

## Bronze Layer (Rohdaten-Ingestion)

- Zweck: Rohdaten-Ingestion, minimale Validierung.
- Bewahrt Rohzustand im Ursprungsformat; wächst inkrementell per Append.
- **Nicht** für direkten Analysten-Zugriff — nur Input für Silver-Anreicherung. Single Source of Truth; ermöglicht Reprocessing/Auditing (volle Historie erhalten).
- Quellen: Cloud Object Storage (S3, GCS, ADLS), Message Buses (Kafka, Kinesis), föderierte Systeme.
- Validierung: minimal. Felder als `STRING`/`VARIANT`/`BINARY` speichern, um Datenverlust bei unerwarteten Schemaänderungen zu vermeiden. Metadaten-Spalten (z. B. `_metadata.file_name`) optional ergänzbar.
- Zielgruppen: Data Engineers, Data Ops, Compliance/Audit.

## Silver Layer (validierte Daten)

- Zweck: Bereinigung, Validierung, Deduplizierung.
- Typische DQ-Operationen: Schema Enforcement, NULL-/Missing-Value-Handling, Deduplizierung, Auflösung verspäteter/unsortierter Daten, DQ-Checks, Schema Evolution, Type Casting, Joins.
- Liest aus Bronze-/Silver-Tabellen, schreibt nach Silver — **nicht** direkt aus der Quelle ingestieren (Risiko: Fehlschläge durch Schemaänderungen/korrupte Datensätze). Reads bevorzugt als Streaming Reads; Batch Reads nur für kleine Datensätze.
- Enthält validierte, bereinigte, angereicherte, **nicht-aggregierte** Repräsentation jedes Datensatzes.
- Hier beginnt Datenmodellierung — inkl. Entscheidung über Verschachtelungsgrad (`VARIANT`, JSON-Strings, oder Structs/Maps/Arrays).
- Zielgruppen: Data Engineers, Data Analysts, Data Scientists.

## Gold Layer (angereicherte Analyse-Daten)

- Zweck: dimensionale Modellierung, Aggregation, geschäftsorientierte Analysen.
- Stark veredelt, treibt Dashboards/ML/Anwendungen; oft aggregiert und nach Zeitraum/Region gefiltert; semantisch an Geschäftsfunktionen ausgerichtet.
- Für Query-/Dashboard-Performance optimiert. Organisationen legen oft mehrere Gold-Schichten pro Domäne an (HR, Finance, IT).
- Zielgruppen: Business Analysts/BI, Data Scientists/ML Engineers, Führungskräfte, operative Teams.

```sql
CREATE OR REPLACE MATERIALIZED VIEW main.example_output.weekly_bookings AS
SELECT date_trunc('week', check_in) AS week,
       property_id,
       status,
       count(*) AS total_bookings,
       sum(total_amount) AS total_revenue
FROM samples.wanderbricks.bookings
GROUP BY week, property_id, status
-- Ergebnis: vorab aggregierte, wöchentliche Buchungskennzahlen je property_id/status —
-- Analysten müssen die Aggregation nicht wiederholt selbst berechnen
```

## Beispielarchitektur (`ops`-Catalog)

- **Bronze (`ops.bronze`):** Rohdaten aus Cloud Storage, Kafka, Salesforce — keine Bereinigung/Validierung.
- **Silver (`ops.silver`):** `customer_transactions` (bereinigt, NULLs entfernt, ungültige Datensätze isoliert), `account_opportunities` (Join von Salesforce Accounts/Opportunities), `leads_cleaned`.
- **Gold (`ops.gold`):** `customer_spending`, `account_performance` (tägliche Metriken), `sales_pipeline_summary`, `business_summary` (Führungskräfte-Aggregate).

## Ingestion-Frequenz-Optionen

| Ansatz | Kosten | Latenz | Methoden |
|---|---|---|---|
| Continuous Incremental Ingestion | höher | niedriger | Streaming Table via `spark.readStream`; Pipeline läuft kontinuierlich, orchestriert per Structured-Streaming-Code mit kontinuierlichem Job-Trigger |
| Triggered Incremental Ingestion | niedriger | höher | Streaming Table, ausgelöst durch geplante/File-Arrival-Trigger; `Trigger.Available` in Notebooks |
| Batch Ingestion mit manuellen inkrementellen Updates | niedriger | am höchsten | `spark.read` statt Structured Streaming; Partition-Overwrite-Strategie; braucht umfangreiche vorgelagerte Architektur + datumsbasierte Partitionierung |

> Medallion Architecture ist empfohlene Best Practice, keine Pflicht.

## Resiliente Pipeline-Muster für Bronze und Silver

**Alles als STRING ingestieren (Bronze):** lehnt nie einen Datensatz wegen Typ-Mismatch ab — Typdurchsetzung wird auf Silver verschoben (`TRY_CAST` fängt Fehlschläge geordnet ab).

```sql
-- Bronze: alle Felder als STRING inferieren, Typ-Mismatches lassen die Pipeline nie fehlschlagen
CREATE OR REFRESH STREAMING TABLE bronze_events
COMMENT "Bronze: all fields as STRING, schema rescue enabled"
AS SELECT *
FROM STREAM read_files(
  '/path/to/source',
  format => 'json',
  schemaEvolutionMode => 'rescue'
)
```

```sql
-- Silver: TRY_CAST gibt bei Cast-Fehlschlag NULL zurück statt die Pipeline anzuhalten
CREATE OR REFRESH STREAMING TABLE silver_events (
  CONSTRAINT valid_amount EXPECT (
    CASE WHEN amount IS NOT NULL
    THEN amount >= 0 ELSE TRUE END
  ) ON VIOLATION DROP ROW
)
AS SELECT *,
  TRY_CAST(amount_str AS DOUBLE) AS amount
FROM STREAM bronze_events
```

**Schema-Evolution-Werkzeuge auf Bronze:**

- `schemaHints` — künftige Spalten vorab deklarieren; erscheint die Spalte, wird sie automatisch befüllt; Altdatensätze bekommen `NULL` (rückwärts- und vorwärtskompatibel).

```sql
CREATE OR REFRESH STREAMING TABLE bronze_events
AS SELECT *
FROM STREAM read_files(
  '/path/to/source',
  format => 'json',
  schemaHints => 'loyalty_tier STRING, region_code STRING',
)
-- Alte Datensätze: loyalty_tier = NULL (akzeptabel)
-- Neue Datensätze: loyalty_tier automatisch befüllt
```

- `_rescued_data` — letzte Verteidigungslinie: jedes Feld außerhalb des Schemas (unerwartete Spalten, Typ-Mismatches) landet als JSON darin, nichts wird still verworfen.

```sql
SELECT
  event_id,
  _rescued_data:unexpected_field  AS unexpected_field,
  _rescued_data:new_column        AS new_column
FROM bronze_events
WHERE _rescued_data IS NOT NULL
```

> **Gotcha:** Neue Spalte per Schema Evolution hinzugefügt → alle vorher ingestierten Datensätze tragen `NULL` dafür. Jeder Constraint auf dieser Spalte **muss** das NULL-tolerante `CASE WHEN`-Muster nutzen — sonst schlagen alle historischen Datensätze am Constraint fehl (Massen-Falsch-Verstöße in der Pipeline-UI).

## Guiding Principles der Lakehouse-Architektur (Databricks Well-Architected Framework)

1. **Daten kuratieren und als vertrauenswürdige Datenprodukte anbieten** — Daten wie ein Produkt behandeln (Definition, Schema, Lebenszyklus). Drei-Schichten-Analogie zu Bronze/Silver/Gold: Ingest Layer (Persistenz der Rohdaten, ermöglicht Wiederaufbau), Curated Layer (bereinigt/verfeinert/aggregiert, verlässliche Analysebasis), Final Layer (um Geschäftsbedürfnisse gebaute Datenprodukte mit Security/Performance-Optimierung). Qualitätsvalidierung beim Eintritt in Curated Layer.
2. **Daten-Silos eliminieren, Datenbewegung minimieren** — mehrere Kopien geraten aus der Synchronisation und mindern die Qualität. Wegwerf-Kopien für Experimente okay, operative Silos mit Downstream-Abhängigkeiten problematisch. Für externes Sharing: Enterprise-Sharing-Mechanismus statt Kopien.
3. **Wertschöpfung durch Self-Service demokratisieren** — niedrige Zugangshürden zu Daten/Plattform für alle Geschäftsbereiche; Data-as-Product-Modell: eine Einheit bietet/pflegt Daten, andere konsumieren mit passender Berechtigung.
4. **Organisationsweite Daten-/KI-Governance-Strategie** — drei Dimensionen: Datenqualität (Data Contracts, SLAs, kontrollierte Schema-Evolution), Data Catalog (Auffindbarkeit, Lineage, Metadaten), Access Control (granulare Spalten-/Zeilen-Berechtigungen, RBAC/ABAC, Audit-Logs von Anfang an).
5. **Offene Schnittstellen und offene Formate fördern** — verhindert Vendor-Lock-in, ermöglicht Partner-Ökosystem; Vorteile: Langlebigkeit/Portabilität, schnelle Tool-Integration, niedrigere Kosten (kein proprietärer Egress).
6. **Für Skalierung bauen, auf Performance/Kosten optimieren** — horizontale (Knotenanzahl) und vertikale (Knotengröße) Skalierung; Ressourcen bedarfsgesteuert, Kosten am Verbrauch orientiert. Entkopplung von Storage und Compute: unabhängige Optimierung, da kein festes Verhältnis Datenvolumen↔Workload besteht.

## Datasets über Lakeflow-Pipelines hinweg organisieren

- **Parallelitätsgrenze:** ein getriggertes Pipeline-Update führt **max. 16 Dataset-Updates parallel** aus — darüber hinausgehende Datasets reihen sich ein statt parallel zu laufen, auch wenn Compute verfügbar wäre.
- **Gleiche Pipeline:** Datasets einer Abhängigkeitskette/logischen Domäne (z. B. Bronze/Silver/Gold für Bestellungen — zusammenhängender DAG lässt sich als Einheit planen/checkpointen/full-refreshen, Lineage bleibt lesbar); gleiche Frische-Anforderung/Kadenz; Gesamtgröße bequem unter der Parallelitätsgrenze.
- **Separate Pipeline:** unterschiedliche Domänen/Teams (getrennte Ownership → getrennte Pipelines, damit ein Fehlschlag nicht das andere Team blockiert); Layer, die unabhängig skaliert/geplant werden sollen (empfohlen: Ingestion/Bronze von Transformation/Silver+Gold trennen); unterschiedliche Latenzprofile (Low-Latency-Stream ≠ Pipeline mit täglichem Batch-Aggregat); Datasets über der Parallelitätsgrenze.
- **Faustregel:** weder ein Monolith noch eine Pipeline pro Tabelle. Gruppierung nach *Domäne + geteilte Kadenz + Abhängigkeit*, Trennung an *Ownership, Layer, Latenz* — Anzahl unabhängig aktualisierbarer Datasets bequem unter 16 halten. Im Zweifel mehrere mittelgroße domänenorientierte Pipelines statt eines Monolithen (leichter später zusammenzuführen als einen produktiven Monolithen aufzuteilen).
- **Einschränkungen:** 16er-Parallelitätsgrenze pro Update; Aufteilung auf mehrere Pipelines kostet End-to-End-Sichtbarkeit — dagegen System-Tabellen (`system.lakeflow.pipelines`, `system.lakeflow.job_run_timeline`) nutzen und die Teile über einen Lakeflow Job orchestrieren.

**Stand:** 2026-09-14.
