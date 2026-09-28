# Tutorial: Control-Tabelle für einen For-Each-Job nutzen

Statt eine Liste (Märkte, Quelltabellen, Kunden, Datumspartitionen) im Job-Code fest zu hinterlegen, wird sie in einer **Control-Tabelle** gespeichert, die der Job zur Laufzeit liest — die Daten, nicht der Code, bestimmen, was verarbeitet wird.

Beispielszenario: eine Ferienimmobilien-Plattform (Wanderbricks-Beispieldatensatz) führt dieselbe Preisanalyse für jedes Objektsegment (`Ski Resort`, `Urban Year-Round`, …) aus. Eine Control-Tabelle listet die Segmente, ein SQL-Task liest sie, ein For-each-Task führt die Analyse einmal je Segment aus.

## Ablauf

| Task | Typ | Aufgabe |
|---|---|---|
| `read_segments` | SQL | liest die Control-Tabelle, erfasst die Zeilen als JSON-Array |
| `process_segments` | For each | iteriert über das Zeilen-Array, startet den verschachtelten Task je Zeile |
| `run_segment_analysis` | Notebook oder SQL (verschachtelt) | läuft einmal je Zeile, analysiert ein Segment |

Die SQL-Task-Ausgabe (JSON-Array von Zeilenobjekten) fließt über `{{tasks.read_segments.output.rows}}` in das **Inputs**-Feld des For-each-Tasks; dieser übergibt Zeilenfelder als `{{input.property_type}}` und `{{input.min_price}}` an den verschachtelten Task.

## Voraussetzungen

- Workspace mit Recht, Jobs/Notebooks zu erstellen.
- Recht, Tabellen/Schemas in Unity Catalog zu erstellen.
- SQL-Warehouse für SQL-Tasks.
- Zugriff auf den `samples`-Catalog (`samples.wanderbricks.properties`).

## Schritt 1: Control-Tabelle erstellen

```sql
USE CATALOG <catalog-name>;
CREATE SCHEMA IF NOT EXISTS config;
CREATE OR REPLACE TABLE config.property_segments AS
SELECT * FROM VALUES
  ('Urban Year-Round', 150),
  ('Summer Getaway', 200),
  ('Ski Resort', 250)
AS t(property_type, min_price);
```

## Schritt 2: Analyselogik schreiben

**Notebook-Variante** (für prozeduralen Code, mehrere Sprachen, Bibliotheken):

```python
dbutils.widgets.text("property_type", "Ski Resort", "Property type")
dbutils.widgets.text("min_price", "250", "Minimum price")

property_type = dbutils.widgets.get("property_type")
min_price = dbutils.widgets.get("min_price")

result = spark.sql(
    """
    SELECT :property_type AS property_type,
           COUNT(*) AS property_count,
           ROUND(AVG(base_price), 2) AS avg_price
    FROM samples.wanderbricks.properties
    WHERE property_type = :property_type
      AND base_price >= :min_price
    """,
    args={"property_type": property_type, "min_price": min_price},
)
display(result)
```

**Hinweis:** `dbutils.widgets.text()` vor `dbutils.widgets.get()` aufrufen — sonst `InputWidgetNotDefined`-Fehler außerhalb eines Jobs.

**SQL-Variante** (für eine einzelne deklarative Query):

```sql
SELECT :property_type AS property_type,
       COUNT(*) AS property_count,
       ROUND(AVG(base_price), 2) AS avg_price
FROM samples.wanderbricks.properties
WHERE property_type = :property_type
  AND base_price >= :min_price;
```

SQL-Tasks nutzen `:param_name`-Syntax; anders als Notebook-Widgets unterstützen SQL-Named-Parameters keine Standardwerte.

## Schritt 3: Lookup-Query erstellen

```sql
SELECT property_type, min_price FROM <catalog-name>.config.property_segments;
```

Als Query `read_segments` speichern.

## Schritt 4: Job erstellen und konfigurieren

**SQL-Lookup-Task:** Kachel **SQL query** → Task-Name `read_segments` → Query `read_segments` auswählen → SQL-Warehouse setzen → **Create task**.

Die Ausgabe wird als JSON-Array in `tasks.read_segments.output.rows` erfasst:

```json
[
  { "property_type": "Urban Year-Round", "min_price": 150 },
  { "property_type": "Summer Getaway", "min_price": 200 },
  { "property_type": "Ski Resort", "min_price": 250 }
]
```

**For-each-Task:** **Add task** → **For each** → Task-Name `process_segments` → **Depends on** = `read_segments` → **Inputs** = `{{tasks.read_segments.output.rows}}` → **Concurrency** = `2` → verschachtelten Task konfigurieren (Notebook oder SQL aus Schritt 2), Parameter `property_type` = `{{input.property_type}}`, `min_price` = `{{input.min_price}}`.

## Schritt 5: Job ausführen und prüfen

**Run now** → Tab **Runs** → Knoten `process_segments` aufklappen — zeigt eine Zeile je Segment mit Status, Startzeit, Dauer. Einzelne fehlgeschlagene Iterationen lassen sich isoliert erneut ausführen.

## Muster erweitern

Neues Segment hinzufügen — ohne Job-/Notebook-Änderung:

```sql
INSERT INTO <catalog-name>.config.property_segments VALUES ('Historical Place', 100);
```

Weitere Anwendungsfälle: Pro-Kunde-Verarbeitung, Tabellen-Ingestion, Backfill-Verarbeitung nach Datumspartition, Feature-Flag-gesteuerte Ausführung.

Um eine Zeile zu deaktivieren, ohne sie zu löschen: eigene Spalte (z. B. `active`) ergänzen und in der Lookup-Query filtern:

```sql
ALTER TABLE <catalog-name>.config.property_segments ADD COLUMN active BOOLEAN;
UPDATE <catalog-name>.config.property_segments SET active = TRUE;
```

```sql
SELECT property_type, min_price FROM <catalog-name>.config.property_segments WHERE active = TRUE;
```

## Quelle

- https://docs.databricks.com/aws/en/jobs/how-to/foreach-sql-lookup-tutorial
