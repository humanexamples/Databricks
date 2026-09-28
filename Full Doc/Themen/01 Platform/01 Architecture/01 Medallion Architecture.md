# Medallion Architecture

Die Medallion Architecture beschreibt eine Reihe von Datenschichten, die die Qualität der im Lakehouse gespeicherten Daten kennzeichnen — Databricks empfiehlt diesen mehrschichtigen Ansatz für den Aufbau von Enterprise-Datenprodukten. Ergänzt um die sechs übergeordneten "Guiding Principles" der Databricks-Lakehouse-Architektur, die den konzeptionellen Rahmen liefern, in den die Medallion Architecture eingebettet ist.

## Abschnittsübersicht

1. [Was ist die Medallion Architecture?](#was-ist)
2. [Bronze Layer](#bronze)
3. [Silver Layer](#silver)
4. [Gold Layer](#gold)
5. [Beispielarchitektur](#beispiel)
6. [Ingestion-Frequenz-Optionen](#ingestion-frequenz)
7. [Empfehlung, keine Pflicht](#empfehlung)
8. [Resiliente Pipeline-Muster für Bronze und Silver](#resilienz)
9. [Guiding Principles der Lakehouse-Architektur](#guiding-principles)
10. [Quellen](#quellen)

---

## <a id="was-ist">1. Was ist die Medallion Architecture?</a>

„Die Medallion Architecture beschreibt eine Reihe von Datenschichten, die die Qualität der im Lakehouse gespeicherten Daten kennzeichnen." Es handelt sich um ein Daten-Design-Pattern zur logischen Organisation von Daten (auch als **Multi-Hop-Architektur** bezeichnet), dessen Ziel es ist, Struktur und Qualität der Daten inkrementell und progressiv zu verbessern, während sie jede Schicht durchlaufen. Die drei Stufen verlaufen von **Bronze ⇒ Silver ⇒ Gold**.

Das Design „garantiert Atomicity, Consistency, Isolation und Durability, während Daten mehrere Schichten aus Validierungen und Transformationen durchlaufen, bevor sie in einem für effiziente Analysen optimierten Layout gespeichert werden."

### Quelle

- https://docs.databricks.com/aws/en/lakehouse/medallion

---

## <a id="bronze">2. Bronze Layer (Rohdaten-Ingestion)</a>

**Zweck:** Rohdaten-Ingestion mit minimaler Validierung.

**Kerneigenschaften:**

- „Enthält und bewahrt den Rohzustand der Datenquelle in ihren ursprünglichen Formaten."
- „Wird inkrementell angehängt und wächst über die Zeit."
- Gedacht für den Konsum durch Workloads, die Daten für Silver-Tabellen anreichern — **nicht** für den direkten Zugriff durch Analysten.
- Dient als **Single Source of Truth**, die die Datentreue bewahrt.
- Ermöglicht Reprocessing und Auditing, da die gesamte Historie erhalten bleibt.

**Datenquellen:** Cloud Object Storage (S3, GCS, ADLS), Message Buses (Kafka, Kinesis) und föderierte Systeme.

**Validierungsansatz:** In der Bronze-Schicht wird nur minimale Datenvalidierung durchgeführt. Databricks empfiehlt, Felder als `STRING`, `VARIANT` oder `BINARY` zu speichern, um Datenverlust durch unerwartete Schemaänderungen zu vermeiden. Metadaten-Spalten (z. B. `_metadata.file_name`) können ergänzt werden.

**Zielgruppen:** Data Engineers, Data Operations, Compliance- und Audit-Teams.

### Quelle

- https://docs.databricks.com/aws/en/lakehouse/medallion

---

## <a id="silver">3. Silver Layer (validierte Daten)</a>

**Zweck:** Datenbereinigung, Validierung und Deduplizierung.

**Typische Datenqualitäts-Operationen:**

- Schema Enforcement
- Behandlung von Null- und fehlenden Werten
- Datendeduplizierung
- Auflösung von unsortiert bzw. verspätet eintreffenden Daten
- Datenqualitätsprüfungen und -durchsetzung
- Schema Evolution
- Type Casting
- Joins

**Aufbau:** Zum Aufbau der Silver-Schicht werden Daten aus einer oder mehreren Bronze- oder Silver-Tabellen gelesen und in Silver-Tabellen geschrieben. Databricks rät von direkten Ingestion-Writes ab, da dadurch „Fehlschläge durch Schemaänderungen oder korrupte Datensätze in den Datenquellen" entstehen. Die meisten Reads sollten als Streaming Reads konfiguriert werden; Batch Reads sollten auf kleine Datensätze beschränkt bleiben.

**Datendarstellung:** Die Silver-Schicht repräsentiert validierte, bereinigte und angereicherte Versionen der Daten und sollte stets mindestens eine validierte, nicht-aggregierte Repräsentation jedes Datensatzes enthalten.

**Datenmodellierung:** In der Silver-Schicht beginnt typischerweise die Datenmodellierung, einschließlich der Entscheidung, wie stark verschachtelte oder semi-strukturierte Daten dargestellt werden — über `VARIANT`-Datentypen, JSON-Strings oder durch Erstellen von Structs, Maps und Arrays.

**Zielgruppen:** Data Engineers; Data Analysts (nutzen Silver für verfeinerte Datensätze mit erhaltenem Detailgrad); Data Scientists (bauen Modelle und führen fortgeschrittene Analysen durch).

### Quelle

- https://docs.databricks.com/aws/en/lakehouse/medallion

---

## <a id="gold">4. Gold Layer (angereicherte Analyse-Daten)</a>

**Zweck:** Dimensionale Modellierung, Aggregation und geschäftsorientierte Analysen.

**Eigenschaften:** Die Gold-Schicht repräsentiert stark veredelte Sichten der Daten, die nachgelagerte Analysen, Dashboards, ML und Anwendungen antreiben. Die Daten sind „oft stark aggregiert und für bestimmte Zeiträume oder geografische Regionen gefiltert" und „enthalten semantisch sinnvolle Datensätze, die auf Geschäftsfunktionen und -bedürfnisse abbilden."

**Merkmale der Gold-Schicht:**

- Besteht aus aggregierten, für Analysen und Reporting zugeschnittenen Daten.
- Richtet sich nach Geschäftslogik und -anforderungen.
- Ist für Performance bei Queries und Dashboards optimiert.

**Geschäftsausrichtung:** Organisationen legen häufig mehrere Gold-Schichten für unterschiedliche Domänen an (z. B. HR, Finance, IT).

**Aggregationsbeispiel:**

```sql
CREATE OR REPLACE MATERIALIZED VIEW main.example_output.weekly_bookings AS
SELECT date_trunc('week', check_in) AS week,
       property_id,
       status,
       count(*) AS total_bookings,
       sum(total_amount) AS total_revenue
FROM samples.wanderbricks.bookings
GROUP BY week, property_id, status
```

Organisationen legen häufig Materialized Views wie `weekly_bookings` an, die diese Daten vorab aggregieren, damit Analysten und andere Nutzer nicht wiederholt dieselben, häufig genutzten Aggregationen neu erstellen müssen.

**Performance-Optimierung:** Die Optimierung von Gold-Tabellen für Performance ist eine Best Practice, da diese Datensätze häufig abgefragt werden.

**Zielgruppen:** Business Analysts und BI-Entwickler; Data Scientists und ML Engineers; Führungskräfte und Entscheidungsträger; operative Teams.

### Quelle

- https://docs.databricks.com/aws/en/lakehouse/medallion

---

## <a id="beispiel">5. Beispielarchitektur</a>

Die Doku illustriert eine Medallion Architecture für den Geschäftsbetrieb anhand dreier Schemas innerhalb eines `ops`-Catalogs:

**Bronze (`ops.bronze`):** Nimmt Rohdaten aus Cloud Storage, Kafka und Salesforce auf. Hier findet keine Datenbereinigung oder Validierung statt.

**Silver (`ops.silver`):** Verarbeitungs- und Join-Operationen finden statt:

- Kunden- und Transaktionsdaten werden bereinigt (Nullwerte entfernt, ungültige Datensätze isoliert) zum Dataset `customer_transactions` für Data Scientists.
- Salesforce-Accounts- und Opportunity-Datensätze werden zu `account_opportunities` gejoint.
- Rohe Lead-Daten werden zu `leads_cleaned` bereinigt.

**Gold (`ops.gold`):** Geschäftsorientierte, aggregierte Datensätze:

- `customer_spending`: Durchschnittliche und Gesamtausgaben je Kunde.
- `account_performance`: Tägliche Performance-Metriken.
- `sales_pipeline_summary`: End-to-End-Informationen zur Sales-Pipeline.
- `business_summary`: Stark aggregierte Daten für Führungskräfte.

### Quelle

- https://docs.databricks.com/aws/en/lakehouse/medallion

---

## <a id="ingestion-frequenz">6. Ingestion-Frequenz-Optionen</a>

Drei Ansätze für die Ingestion-Frequenz, mit Kosten-/Latenz-Trade-off:

| Ansatz | Kosten | Latenz | Methoden |
|---|---|---|---|
| **Continuous Incremental Ingestion** | höher | niedriger | Streaming Table via `spark.readStream` aus Cloud Storage oder Message Bus; Pipeline läuft kontinuierlich; Structured-Streaming-Code mit kontinuierlichem Job-Trigger orchestriert |
| **Triggered Incremental Ingestion** | niedriger | höher | Streaming Table, ausgelöst durch geplante Trigger oder File-Arrival-Trigger; `Trigger.Available` in Notebooks |
| **Batch Ingestion mit manuellen inkrementellen Updates** | niedriger | am höchsten (wegen seltener Läufe) | Nutzt `spark.read` statt Structured Streaming; Partition-Overwrite-Strategie; erfordert umfangreiche vorgelagerte Architektur und datumsbasierte Partitionierung |

### Quelle

- https://docs.databricks.com/aws/en/lakehouse/medallion

---

## <a id="empfehlung">7. Empfehlung, keine Pflicht</a>

„Der Medallion Architecture zu folgen ist eine empfohlene Best Practice, aber keine Pflicht." Das Design garantiert Atomicity, Consistency, Isolation und Durability, während Daten mehrere Schichten aus Validierungen und Transformationen durchlaufen, bevor sie in einem für effiziente Analysen optimierten Layout gespeichert werden.

### Quelle

- https://docs.databricks.com/aws/en/lakehouse/medallion

---

## <a id="resilienz">8. Resiliente Pipeline-Muster für Bronze und Silver</a>

Aus privater Kursnotiz — zwei konkrete Entwurfsmuster, um die in Abschnitt 2–3 beschriebenen Bronze-/Silver-Eigenschaften ("minimale Validierung" bzw. "Schema Enforcement") robust umzusetzen, ohne dass Typkonflikte oder unerwartete Schemaänderungen die Pipeline zum Absturz bringen. Die eingesetzten Mechanismen (`schemaEvolutionMode`, `schemaHints`, `_rescued_data`, `TRY_CAST`) sind an anderer Stelle in diesem Projekt bereits ausführlich dokumentiert (siehe Querverweise) — hier liegt der Fokus auf dem übergeordneten Entwurfsmuster für resiliente Medallion-Pipelines.

### 8.1 Alles als STRING ingestieren (Bronze)

„Das resilienteste Bronze-Schicht-Design lehnt niemals einen Datensatz wegen eines Typ-Mismatches ab." Indem alle eingehenden Felder als `STRING` gespeichert werden, wird akzeptiert, was auch immer die Quelle sendet — Integers, Decimals, gemischte Typen — und die Typdurchsetzung wird auf Silver verschoben, wo `TRY_CAST` Fehlschläge geordnet abfängt.

**Bronze — alles akzeptieren:** Alle Felder werden als `STRING` inferiert. Typ-Mismatches lassen die Pipeline nie fehlschlagen — eine Ganzzahl in einem String-Feld ist einfach ein String.

```sql
CREATE OR REFRESH STREAMING TABLE bronze_events
COMMENT "Bronze: all fields as STRING, schema rescue enabled"
AS SELECT *
FROM STREAM read_files(
  '/path/to/source',
  format => 'json',
  schemaEvolutionMode => 'rescue'
)
```

**Silver — Typen sicher durchsetzen:** `TRY_CAST` gibt bei einem Cast-Fehlschlag `NULL` zurück, statt die Pipeline anzuhalten. Das NULL-tolerante Constraint-Muster übernimmt danach den Rest.

```sql
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

### 8.2 Schema-Evolution-Werkzeuge auf der Bronze-Schicht

Zwei eingebaute Mechanismen decken den gesamten Lebenszyklus einer Schemaänderung ab — `schemaHints` für Spalten, von denen bereits bekannt ist, dass sie kommen werden, und `_rescued_data` als letzte Verteidigungslinie für alles Unerwartete.

**`schemaHints` — künftige Spalten schon heute deklarieren:** Spalten deklarieren, die in *künftigen* Dateien erwartet werden, bevor sie eintreffen. Erscheint die neue Spalte, wird sie automatisch befüllt. Datensätze von vor der Schema-Evolution tragen `NULL` — gleichzeitig rückwärts- und vorwärtskompatibel.

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

**`_rescued_data` — letzte Verteidigungslinie:** Jedes Feld außerhalb des deklarierten Schemas — unerwartete Spalten, Typ-Mismatches — wird als JSON in `_rescued_data` erfasst. Nichts wird stillschweigend verworfen; die Spalte lässt sich jederzeit für Untersuchung oder Wiederherstellung abfragen.

```sql
-- Gerettete Felder im Nachhinein untersuchen
SELECT
  event_id,
  _rescued_data:unexpected_field  AS unexpected_field,
  _rescued_data:new_column        AS new_column
FROM bronze_events
WHERE _rescued_data IS NOT NULL
```

**⚠️ Kritisches Zusammenspiel:** Wird eine Spalte per Schema Evolution hinzugefügt, tragen alle Datensätze, die *vor* der Evolution ingestiert wurden, `NULL` für diese Spalte. Jeder für diese Spalte geschriebene Constraint **muss das NULL-tolerante `CASE WHEN`-Muster** nutzen (siehe Beispiel in Abschnitt 8.1) — andernfalls schlägt jeder historische Datensatz am Constraint fehl, was zu massenhaften Falsch-Verstößen in der Pipeline-UI führt.

**Vertiefte Referenz zu den eingesetzten Mechanismen:**

- `_rescued_data` im Detail: [Lakeflow Connect/.../Diagnose- und Herkunftsspalten/_rescued_data.md](../../Data%20Management/Data%20Engineering/Lakeflow%20Connect/Lakeflow%20Connect%20Standard%20Connectors/Working%20with%20Files/Diagnose-%20und%20Herkunftsspalten/_rescued_data.md)
- `schemaHints` und weitere Schema-Aspekte: [Lakeflow Connect/.../_schema_Aspekte.md](../../Data%20Management/Data%20Engineering/Lakeflow%20Connect/Lakeflow%20Connect%20Standard%20Connectors/Working%20with%20Files/_schema_Aspekte.md)
- Umgang mit fehlerhaften/nicht parsbaren Zeilen allgemein: [Lakeflow Connect/.../Diagnose- und Herkunftsspalten/Rescuing Malformed Rows.md](../../Data%20Management/Data%20Engineering/Lakeflow%20Connect/Lakeflow%20Connect%20Standard%20Connectors/Working%20with%20Files/Diagnose-%20und%20Herkunftsspalten/Rescuing%20Malformed%20Rows.md)

### Quelle

- Private Kursnotiz.

---

## <a id="guiding-principles">9. Guiding Principles der Lakehouse-Architektur</a>

„Guiding Principles sind Level-Null-Regeln, die die Architektur definieren und beeinflussen." Ein organisationsweiter Konsens über diese Prinzipien ist notwendig, um erfolgreich eine Databricks-Plattform aufzubauen. Sechs Kernprinzipien, Teil des Databricks Well-Architected Framework:

### 9.1 Daten kuratieren und als vertrauenswürdige Datenprodukte anbieten

Daten sollen „wie ein Produkt mit klarer Definition, Schema und Lebenszyklus behandelt werden" — das sichert semantische Konsistenz und fortlaufende Qualitätsverbesserung über die Schichten hinweg. Drei-Schichten-Ansatz (analog zu Bronze/Silver/Gold aus Abschnitt 1–4):

- **Ingest Layer:** Quelldaten werden in die erste Schicht des Lakehouse aufgenommen und dort persistiert — das ermöglicht den Wiederaufbau nachgelagerter Schichten bei Bedarf.
- **Curated Layer:** Enthält „bereinigte, verfeinerte, gefilterte und aggregierte Daten" — eine verlässliche Grundlage für Analysen und Reports über organisatorische Rollen hinweg.
- **Final Layer:** Um konkrete Geschäftsbedürfnisse herum aufgebaut, bietet „Datenprodukte für andere Geschäftsbereiche oder Projekte" mit angewendeten Sicherheits- und Performance-Optimierungen.

Pipelines müssen sicherstellen, dass Daten „jederzeit akkurat, vollständig, zugänglich und konsistent sind, selbst bei gleichzeitigen Lese- und Schreibvorgängen." Qualitätsvalidierung erfolgt beim Eintritt in die Curated Layer, mit anschließenden Verbesserungen durch ETL-Prozesse.

### 9.2 Daten-Silos eliminieren und Datenbewegung minimieren

Das Prinzip warnt vor mehreren Datensatz-Kopien, bei denen Geschäftsprozesse von unterschiedlichen Versionen abhängen — das führt zu „Daten-Silos, die aus der Synchronisation geraten, was zu geringerer Qualität führt." Wichtige Unterscheidung: Wegwerf-Kopien sind für Experimente akzeptabel, operative Silos sind problematisch, sobald nachgelagerte Abhängigkeiten bestehen. Versuche, synchronisierte Kopien zu pflegen, scheitern typischerweise und resultieren in „höheren Kosten und einem erheblichen Vertrauensverlust der Nutzer." Lösung für externes Daten-Sharing: ein „Enterprise-Sharing-Mechanismus, der direkten Zugriff auf die Daten auf sichere Weise erlaubt", statt Kopien anzulegen.

### 9.3 Wertschöpfung durch Self-Service demokratisieren

„Der beste Data Lake kann keinen ausreichenden Wert liefern, wenn Nutzer nicht einfach auf die Plattform oder Daten für ihre BI-/ML-/AI-Aufgaben zugreifen können." Organisationen müssen „die Zugangshürden zu Daten und Plattformen für alle Geschäftsbereiche senken" — über schlanke Prozesse und Self-Service-Ansätze. Im Data-as-Product-Modell wird Daten „von einer Geschäftseinheit oder einem Geschäftspartner wie ein Produkt angeboten und gepflegt und von anderen Parteien mit passender Berechtigungskontrolle konsumiert" — ohne Abhängigkeit von zentralen Teams und langsamen Anfrage-Workflows. Erfolg erfordert „eine moderne Daten- und KI-Plattform, die die Infrastruktur und Tools zum Aufbau von Datenprodukten liefert, ohne den Aufwand zu duplizieren."

### 9.4 Eine organisationsweite Daten- und KI-Governance-Strategie verfolgen

Drei Governance-Dimensionen:

- **Datenqualität:** „Die wichtigste Voraussetzung für korrekte und aussagekräftige Reports, Analyseergebnisse und Modelle." Umsetzungsansätze: Data Contracts, SLA-Einhaltung, Schema-Stabilität und kontrollierte Evolution.
- **Data Catalog:** Essenziell für Auffindbarkeit, besonders in Self-Service-Modellen. Hauptziele: einheitliche Benennung von Geschäftskonzepten organisationsweit sicherstellen; „Data Lineage präzise nachverfolgen, damit Nutzer erklären können, wie diese Daten zu ihrer aktuellen Form gekommen sind"; hochwertige Metadaten pflegen, die „genauso wichtig wie die Daten selbst" sind.
- **Access Control:** Die Plattform muss „Sicherheit als First-Class-Citizen" behandeln, mit granularen Berechtigungen einschließlich „spalten- und zeilenbasierter Zugriffskontrolle, rollen- oder attributbasierter Zugriffskontrolle." Organisationen sollten „von Anfang an Audit-Logs" implementieren, unabhängig vom anfänglichen Strenge-Level.

### 9.5 Offene Schnittstellen und offene Formate fördern

Offene Ansätze sind „entscheidend für die Interoperabilität zwischen dem Lakehouse und anderen Tools" — sie verhindern Vendor-Lock-in und ermöglichen den Aufbau eines Partner-Ökosystems. Vorteile offener Standards:

- „Erhöht die Langlebigkeit und Portabilität der Daten, sodass sie mit mehr Anwendungen und für mehr Anwendungsfälle genutzt werden können."
- Ermöglicht Partnern, „die offenen Schnittstellen schnell zu nutzen, um ihre Tools in die Databricks-Plattform zu integrieren."
- Offene Datenformate sorgen dafür, dass „die Gesamtkosten deutlich niedriger ausfallen", da direkter Cloud-Storage-Zugriff ohne proprietäre Plattform-Egress-Kosten möglich ist.

### 9.6 Für Skalierung bauen und auf Performance und Kosten optimieren

„Daten wachsen unweigerlich weiter und werden komplexer" — das erfordert Infrastruktur, die variable Workloads aus ETL-Prozessen, Geschäftsreports und ML-Modelltraining bewältigen kann. Skalierungsansätze:

- Horizontale Skalierung (Anzahl der Knoten anpassen).
- Vertikale Skalierung (Knotengröße anpassen).
- Ressourcen sollten „einfach bedarfsgesteuert" verfügbar sein, mit Kosten begrenzt auf den „tatsächlichen Verbrauch."

**Entkopplung von Storage und Compute:** „Es gibt keine klare Beziehung zwischen dem Datenvolumen und den Workloads, die diese Daten nutzen" — das macht entkoppelte Infrastruktur vorteilhaft für die unabhängige Optimierung von Storage- und Compute-Ressourcen.

### Quelle

- https://docs.databricks.com/aws/en/lakehouse-architecture/guiding-principles

---

## <a id="quellen">10. Quellen</a>

- Medallion Lakehouse Architecture: https://docs.databricks.com/aws/en/lakehouse/medallion
- Guiding principles (Databricks Well-Architected Framework): https://docs.databricks.com/aws/en/lakehouse-architecture/guiding-principles
- Abschnitt 8 (Resiliente Pipeline-Muster): private Kursnotiz — die eingesetzten Mechanismen sind zusätzlich in den dortigen Querverweisen doc-verifiziert.

**Stand:** 2026-08-21.
