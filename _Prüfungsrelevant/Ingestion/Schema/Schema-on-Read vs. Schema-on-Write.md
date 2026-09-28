# Schema-on-Read vs. Schema-on-Write

**Sehr relevant für Databricks:** Delta Lake/die Lakehouse-Architektur propagiert explizit **Schema-on-Write** — im Gegensatz zum klassischen Data-Lake-Ansatz mit **Schema-on-Read**. Beide Begriffe sind generische Datenarchitektur-Konzepte, keine Databricks-Erfindung, aber Databricks positioniert sich in der eigenen Doku ausdrücklich dazu (siehe Zitate unten).

## Zwei Paradigmen

**Schema-on-Read** bedeutet: Daten landen ungeprüft und in beliebigem Format; die Struktur wird erst zur Abfragezeit abgeleitet oder angewendet — das Schema wird also erst beim Lesen/Interpretieren der Daten angewendet, es gibt beim Landen keine Validierung. Typischer Ort dafür sind Rohdateien in Cloud-Storage, wie im klassischen Data Lake.

**Schema-on-Write** bedeutet das Gegenteil: Das Schema ist vorab fest definiert und wird bei **jedem** Schreibvorgang durchgesetzt. Typischer Ort dafür ist ein Data Warehouse bzw. eine Delta-Tabelle.

Der Unterschied lässt sich am selben Datensatz zeigen — je nachdem, **wann** das Schema ins Spiel kommt:

```python
# Schema-on-Read: Die Datei liegt einfach im Storage, das Schema wird erst beim Lesen bestimmt
df = spark.read.json("/Volumes/analytics/raw/events")   # Struktur erst jetzt bekannt
```
```sql
-- Schema-on-Write: Struktur steht vorher fest, jeder Schreibvorgang wird daran gemessen
CREATE TABLE events (id INT, event STRING, ts TIMESTAMP);
INSERT INTO events VALUES (1, 'click', current_timestamp());  -- muss zum Schema passen
```

## Databricks-Position laut Doku

Für Delta Lake formuliert ein offizieller Databricks-Perspectives-Artikel klar die Schema-on-Write-Seite:

> *"Delta Lake enforces schema on write, rejecting data that violates a table's defined structure before it lands."*

und grenzt das explizit vom Roh-Dateien-Ansatz ab:

> *"That differs from a raw file-based lake, where any file in any format can land without validation, and from a rigid warehouse, where a schema change typically requires a DDL migration and downtime."*

**Quelle beider Zitate:** `developers.databricks.com/perspectives/what-does-schema-enforcement-look-like-in-a-data-lakehouse-platform`.

Für die **Bronze-Schicht** verwendet die offizielle Medallion-Architektur-Doku den Begriff "Schema-on-Read" selbst zwar nicht wörtlich, beschreibt aber inhaltlich genau dieses Verhalten: *"Minimal data validation is performed in the bronze layer"*, und Databricks empfiehlt dort, die meisten Felder als `string`, `VARIANT` oder `binary` zu speichern, *"to protect against unexpected schema changes"* — also bewusst ohne festen Schema-Vertrag beim Landen der Rohdaten. **Quelle:** `docs.databricks.com/aws/en/lakehouse/medallion`, Abschnitt „Ingest raw data to the bronze layer" → „Limit data cleanup or validation" (wortgleich auch im Microsoft-Learn-Spiegel `learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion`). Eine frühere Fassung dieser Datei zitierte hier einen Satz *"Schema-on-read: Flexible schema handling for diverse source systems"*, der sich bei erneuter Prüfung **nicht** auf dieser Seite (weder AWS- noch Microsoft-Learn-Version, vollständig durchsucht) wiederfinden ließ und daher entfernt wurde.

Die exakte Begriffspaarung "Schema-on-Read vs. Schema-on-Write" taucht in der Doku nicht in einem einzigen Satz auf — Databricks belegt beide Seiten des Konzepts an unterschiedlichen Stellen, ohne durchgängig genau diese beiden Fachbegriffe zu verwenden. Der 2019er Einführungs-Blogpost zu Schema Enforcement/Evolution verwendet stattdessen die Formulierung *"schema validation on write"*.

## Delta Lake = Schema-on-Write in der Praxis

Das Schema jeder Delta-Tabelle ist **im Transaction Log** (`_delta_log`) persistiert und wird bei **jedem** Schreibvorgang geprüft und durchgesetzt → [Schema Enforcement.md](Schema%20Enforcement.md). Abweichende Schreibvorgänge werden abgewiesen statt stillschweigend übernommen — das ist der Kern von Schema-on-Write.

```python
spark.sql("CREATE TABLE my_table (id INT, event STRING)")

# Zusätzliche Spalte, die im Tabellenschema nicht existiert
df = spark.createDataFrame([(1, "click", "unexpected")], ["id", "event", "extra_col"])
df.write.mode("append").saveAsTable("my_table")
# -> Fehlschlag: "extra_col" ist nicht Teil des durchgesetzten Tabellenschemas,
#    der Schreibvorgang wird komplett abgewiesen statt teilweise übernommen zu werden
```

## Rohdateien / `read_files` ohne Delta = Schema-on-Read

Solange Daten als reine Dateien (CSV/JSON/Parquet) in Cloud-Storage liegen und direkt per `read_files`/`spark.read` abgefragt werden, existiert **kein persistierter Schema-Vertrag**: Das Schema wird bei jedem Lesevorgang neu inferiert oder explizit per `.schema()` angegeben ([Schema Inference.md](Schema%20Inference.md), [Schema Definition.md](Schema%20Definition.md)) — das ist Schema-on-Read.

```sql
-- Jeder Aufruf inferiert unabhängig neu - es gibt keinen gespeicherten Vertrag,
-- gegen den der Lesevorgang geprüft würde
SELECT * FROM read_files('/Volumes/analytics/raw/events', format => 'json');
```
```python
df = spark.read.json("/Volumes/analytics/raw/events")
df.printSchema()
# Ändert sich der Inhalt der Rohdateien (z. B. neue Spalte in neuen Dateien),
# liefert derselbe Aufruf beim nächsten Mal ein anderes Schema — anders als bei einer
# Delta-Tabelle gibt es hier keinen fixen, über die Zeit stabilen Vertrag.
```

## Hybridrolle: Auto Loader / `read_files` im Medallion-Modell

- **Bronze:** Auto Loader/`STREAM read_files` liest Rohdaten (JSON/CSV/...) und **inferiert** das Schema aus dem Dateiinhalt — inhaltlich Schema-on-Read, auch wenn das Ergebnis am Ende in eine Delta-Tabelle geschrieben wird.
- Sobald die Daten in der Bronze-Delta-Tabelle **gelandet** sind, greift durchgängig Schema-on-Write: jede weitere Lese-/Schreiboperation (Silver, Gold) arbeitet gegen ein festes, durchgesetztes Schema.
- Bronze kommt damit dem Schema-on-Read-Gedanken am nächsten (Eintrittspunkt für Rohdaten wechselnder Struktur), während Silver/Gold strikt unter Delta-Schema-on-Write stehen.

**Bronze — Schema-on-Read in der Praxis:** Die Rohdaten haben beim Landen im Cloud-Storage keinerlei Schema-Vertrag; erst beim Einlesen leitet Auto Loader eines aus dem Dateiinhalt ab. Passend zur oben zitierten Bronze-Empfehlung (*"protect against unexpected schema changes"* durch `string`/`VARIANT`/`binary`-Felder) wird `inferColumnTypes` hier bewusst auf `false` gesetzt, statt exakte Typen zu erzwingen:

```sql
CREATE OR REFRESH STREAMING TABLE bronze_orders
AS SELECT * FROM STREAM read_files(
  '/Volumes/analytics/bronze/orders',
  format => 'json',
  schemaLocation => '/Volumes/analytics/bronze/_schema',
  inferColumnTypes => false   -- explizit nötig: Default bei STREAM read_files ist sonst true
);
```
```python
df = (spark.readStream
      .format("cloudFiles")
      .option("cloudFiles.format", "json")
      .option("cloudFiles.schemaLocation", "/Volumes/analytics/bronze/_schema")
      # cloudFiles.inferColumnTypes hier NICHT nötig — Default ist bei nativem cloudFiles
      # ohnehin schon false (siehe Schema Inference.md)
      .load("/Volumes/analytics/bronze/orders"))

(df.writeStream
   .option("checkpointLocation", "/Volumes/analytics/bronze/_checkpoint")
   .toTable("bronze_orders"))
```

**Silver/Gold — Schema-on-Write ab der ersten Delta-Tabelle:** `bronze_orders` selbst hat jetzt ein festes, im Transaction Log persistiertes Schema. Jede weitere Lese-/Schreiboperation — auch der Übergang nach Silver — arbeitet dagegen, nicht mehr gegen Rohdateien:

```sql
CREATE OR REFRESH STREAMING TABLE silver_orders
AS SELECT
  order_id,
  CAST(order_ts AS TIMESTAMP) AS order_timestamp,
  CAST(amount AS DECIMAL(10,2)) AS amount
FROM STREAM bronze_orders;

-- Ein Schreibversuch mit abweichender Spalte wird abgewiesen statt still übernommen —
-- das ist der Unterschied zur Bronze-Inferenz oben:
INSERT INTO silver_orders (order_id, order_timestamp, unbekannte_spalte)
VALUES ('o1', current_timestamp(), 'x');
-- Fehler: unbekannte_spalte ist nicht Teil des durchgesetzten Silver-Schemas
```

## Trade-off

Bei der **Ingestion-Geschwindigkeit/Flexibilität** liegt Schema-on-Read vorn: beliebige oder wechselnde Quellstrukturen landen ohne Vorab-Modellierung. Schema-on-Write ist hier langsamer/unflexibler, weil das Schema vorab feststehen muss (oder kontrolliert evolviert werden muss).

Bei der **Datenqualität/Konsistenz** ist es umgekehrt: Schema-on-Read ist schwächer, weil sich Fehler erst bei der Abfrage zeigen; Schema-on-Write ist stark, weil Fehler bereits beim Schreiben abgefangen werden.

Im Medallion-Modell findet sich Schema-on-Read typischerweise in **Bronze** (Rohdaten-Eingang), Schema-on-Write dagegen in **Silver/Gold** (kuratierte, verlässliche Daten).

## Verwandte Themen

- [Schema Enforcement.md](Schema%20Enforcement.md) · [Schema Evolution.md](Schema%20Evolution.md) · [Schema Inference.md](Schema%20Inference.md) · [Schema Definition.md](Schema%20Definition.md)
- [Schema Migration.md](Schema%20Migration.md) · [Schema Versioning.md](Schema%20Versioning.md) · [Schema Mapping und Transformation.md](Schema%20Mapping%20und%20Transformation.md) · [Schema Governance.md](Schema%20Governance.md)
