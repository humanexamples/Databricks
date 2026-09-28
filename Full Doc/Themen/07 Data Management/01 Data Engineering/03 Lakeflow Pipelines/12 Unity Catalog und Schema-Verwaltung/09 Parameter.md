# Pipelines parametrisieren

Pipeline-Parameter sind veränderliche Key-Value-Paare, die es erlauben, denselben Pipeline-Quellcode über verschiedene Umgebungen oder Datasets hinweg wiederzuverwenden, ohne den Quellcode zu bearbeiten. Jede Aussage wurde per `WebFetch` gegen `docs.databricks.com/aws/en/ldp/parameters` verifiziert.

## Abschnittsübersicht

1. [Was sind Pipeline-Parameter?](#was-sind-parameter)
2. [Parameter definieren](#definieren)
3. [Parameter im SQL-Quellcode referenzieren](#referenzieren)
4. [Parameter zum Update-Zeitpunkt überschreiben](#ueberschreiben)
5. [Parameter-Priorität](#prioritaet)
6. [Pipeline-Parameter in Lakeflow Jobs](#jobs)
7. [Einschränkungen und bekannte Probleme](#einschraenkungen)
8. [Parameter über das Configuration-Feld referenzieren](#configuration-feld)
9. [Quellen](#quellen)

---

## <a id="was-sind-parameter">1. Was sind Pipeline-Parameter?</a>

**Wichtig:** Dieses Feature befindet sich in der Beta-Phase. Workspace-Admins können den Zugriff darauf über die Previews-Seite steuern.

Parameter lassen sich:

- als Standardwerte in den Pipeline-Einstellungen deklarieren,
- beim Starten eines Updates aus der Pipeline-UI, der Start-Update-API oder dem Dialog „Run with different settings" überschreiben,
- am Pipeline-Task in einem Job überschreiben, optional mit Pushdown von Job-Level-Parametern,
- aus SQL-Quellcode über die Named-Parameter-Syntax referenzieren.

Parameterwerte sind ausschließlich Strings. Gültige Zeichen für Keys sind alphanumerische Zeichen, Unterstriche (`_`), Bindestriche (`-`) und Punkte (`.`).

### Parameter vs. Configuration

| Parameter | Configuration |
|---|---|
| Werte, die sich zwischen Updates ändern (Zielkatalog, Quellpfad) | Spark-Konfiguration, die das Pipeline-Verhalten steuert (z. B. `pipelines.enzyme.enabled`) |
| Werte, die von Job-/Task-Ebene durchgereicht werden | Statische, strukturelle Pipeline-Eigenschaften |
| Referenzierung über SQL-Named-Parameter-Syntax | Referenzierung über `${key}`-Syntax in SQL oder `spark.conf.get("key")` in Python |

---

## <a id="definieren">2. Parameter definieren</a>

Drei Wege stehen zur Verfügung:

**Über die Pipeline-UI:**

1. In der Seitenleiste **Jobs and Pipelines** öffnen.
2. Pipeline auswählen und auf **Settings** klicken.
3. Im Abschnitt **Parameters** auf **Edit** klicken.
4. Key/Value-Paare hinzufügen und speichern.

**Über JSON/REST-API:**

```json
{
  "name": "Sales pipeline",
  "parameters": {
    "source_catalog": "dev_catalog",
    "source_schema": "sales",
    "start_date": "2026-01-01"
  }
}
```

**Über YAML / Declarative Automation Bundles:**

```yaml
resources:
  pipelines:
    my_pipeline:
      name: Sales pipeline
      parameters:
        source_catalog: dev_catalog
        source_schema: sales
        start_date: '2026-01-01'
```

---

## <a id="referenzieren">3. Parameter im SQL-Quellcode referenzieren</a>

Die Standard-Referenzierung nutzt einen Doppelpunkt vor dem Parameternamen:

```sql
CREATE OR REFRESH MATERIALIZED VIEW transaction_summary AS
SELECT account_id,
  COUNT(txn_id) AS txn_count,
  SUM(txn_amount) AS account_revenue
FROM :source_catalog.sales.transactions
WHERE txn_date >= :start_date
GROUP BY account_id
```

Für Positionen, die Bezeichner (Katalog, Schema, Tabellenname) erwarten, wird die Funktion `IDENTIFIER()` genutzt:

```sql
USE CATALOG IDENTIFIER(:source_catalog);
USE SCHEMA IDENTIFIER(:source_schema);
CREATE OR REFRESH MATERIALIZED VIEW daily_sales AS
SELECT date(timestamp) AS date,
  SUM(price) AS total_sales
FROM transactions
GROUP BY date;
```

Fehlende Parameterwerte führen zum Fehlschlagen des Updates; nicht referenzierte Parameter werden ignoriert.

---

## <a id="ueberschreiben">4. Parameter zum Update-Zeitpunkt überschreiben</a>

Drei Wege, Parameter zu überschreiben:

- **Pipeline-UI:** Auf „Run with different settings" klicken und den Abschnitt **Parameters** anpassen.
- **Pipeline-Task in einem Job:** Overrides im Parameters-Feld des Tasks setzen.
- **API:** Eine Parameter-Map im Start-Update-Request übergeben.

Databricks erfasst die für ein konkretes Update genutzten Parameter in der Update-Historie und zeigt sie in der Spalte **Run parameters** an.

---

## <a id="prioritaet">5. Parameter-Priorität</a>

Von höchster zu niedrigster Priorität:

1. Job-Run-Parameter (Overrides für einen einzelnen Lauf)
2. Job-Parameter (Standardwerte des übergeordneten Jobs)
3. Pipeline-Task-Parameter (Werte am Pipeline-Task)
4. Pipeline-Parameter (Standardwerte in den Pipeline-Einstellungen)

---

## <a id="jobs">6. Pipeline-Parameter in Lakeflow Jobs</a>

Wird eine Pipeline als Pipeline-Task in einem Job geplant, können Tasks die Standardwerte der Pipeline überschreiben. Parameterwerte können dynamische Werte-Referenzen nutzen, um zur Job-Laufzeit ermittelte Werte einzufügen, z. B. `{{job.trigger.time.iso_date}}` oder `{{job.parameters.region}}`.

Referenzen auf Werte vorgelagerter Tasks: `{{tasks.<task_name>.values.<value_name>}}`.

Job-Parameter kaskadieren automatisch zu Pipeline-Tasks und lassen sich dort über die Named-Parameter-Syntax im Pipeline-Quellcode referenzieren.

---

## <a id="einschraenkungen">7. Einschränkungen und bekannte Probleme</a>

### Concurrency-Einschränkung

Pipelines werden sequenziell ausgeführt (maximal ein Update gleichzeitig). Databricks begrenzt die Concurrency auf 1, wenn:

- ein Job einen Pipeline-Task mit `max_concurrent_runs` größer als eins enthält,
- der Pipeline-Task in einem For-Each-Task eingebettet ist.

### Datumsfilterung und Inkrementalität

Eine Filterung auf **beiden Seiten** eines Datumsbereichs macht die inkrementelle Verarbeitung auf Materialized Views ungültig und löst bei jedem Update einen Full Refresh aus.

Problematischer Ansatz (Full Refresh):

```sql
CREATE OR REFRESH MATERIALIZED VIEW recent_orders AS
SELECT * FROM orders
WHERE order_date >= :start_date AND order_date < :end_date;
```

Bevorzugter Ansatz (inkrementell):

```sql
CREATE OR REFRESH MATERIALIZED VIEW recent_orders AS
SELECT * FROM orders
WHERE order_date >= :start_date;
```

### Sprachunterstützung

Named Parameters funktionieren ausschließlich in SQL; für Python ist der Weg über das Configuration-Feld nötig (siehe Abschnitt 8).

---

## <a id="configuration-feld">8. Parameter über das Configuration-Feld referenzieren</a>

Das Configuration-Feld ist der ältere Parametrisierungsmechanismus und funktioniert weiterhin parallel zu Pipeline-Parametern. Dieser Ansatz unterstützt Python-Quellcode und erlaubt das Auslesen über `spark.conf.get()`.

```sql
-- SQL-Beispiel
CREATE OR REFRESH MATERIALIZED VIEW customer_events
AS SELECT * FROM source_table WHERE date > '${mypipeline.start_date}';
```

```python
# Python-Beispiel
from pyspark import pipelines as dp
from pyspark.sql.functions import col

@dp.table
def customer_events():
  start_date = spark.conf.get("mypipeline.start_date")
  return spark.read.table("source_table").where(col("date") > start_date)
```

Configuration-Werte werden über den Configuration-Abschnitt der Pipeline-Einstellungen oder das `configuration`-Feld im Pipeline-JSON gesetzt. Namenskollisionen mit reservierten Pipeline-/Spark-Werten sind zu vermeiden.

---

## <a id="quellen">9. Quellen</a>

- https://docs.databricks.com/aws/en/ldp/parameters

**Stand:** 2026-08-19
