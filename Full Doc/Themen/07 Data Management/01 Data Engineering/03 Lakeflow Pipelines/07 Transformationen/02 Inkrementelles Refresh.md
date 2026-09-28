# Inkrementelles Refresh für Materialized Views — Referenz

Dieses Dokument beschreibt inkrementelles Refresh für Materialized Views in Lakeflow-Declarative-Pipelines (LDP): Es erkennt Änderungen in Quelldaten und berechnet nur die betroffenen Ergebnisse neu, statt die gesamte Query neu auszuführen. Verifiziert per `WebFetch` gegen die Azure-Spiegelseite (`learn.microsoft.com/en-us/azure/databricks/ldp/incremental-refresh`), die eine vollständige, wörtliche Wiedergabe des Roh-Markdowns lieferte; die Kernaussagen (Serverless-Pflicht, `REFRESH POLICY`-Werte) wurden zusätzlich per Zweitabruf gegen die AWS-Seite (`docs.databricks.com/aws/en/ldp/incremental-refresh`) wörtlich gegengeprüft.

## Abschnittsübersicht

1. [Grundprinzip](#grundprinzip)
2. [Refreshes laufen auf Serverless Compute](#serverless)
3. [Refresh-Semantik für Materialized Views](#semantik)
4. [Datenquellen-Überlegungen für Materialized Views](#datenquellen)
5. [Materialized Views optimieren](#optimieren)
6. [Refresh-Typen für Materialized Views](#refresh-typen)
7. [Unterstützung für inkrementelles Refresh nach SQL-Konstrukt](#unterstuetzung)
8. [Incrementalization Insights](#insights)
9. [Refresh-Typ eines Updates bestimmen](#refresh-typ-bestimmen)
10. [Refresh Policy](#refresh-policy)
11. [Quellen](#quellen)

---

## <a id="grundprinzip">1. Grundprinzip</a>

Inkrementelles Refresh auf einer Materialized View erkennt Änderungen in den Quelldaten und berechnet nur die betroffenen Ergebnisse neu, statt die gesamte Query neu auszuführen. Bei Updates auf Materialized Views über Serverless Pipelines lassen sich viele Queries inkrementell refreshen — das spart Rechenkosten, indem Änderungen in den Datenquellen der Materialized View erkannt und das Ergebnis inkrementell berechnet wird.

## <a id="serverless">2. Refreshes laufen auf Serverless Compute</a>

Refresh-Operationen laufen auf Serverless Pipelines, unabhängig davon, ob die Operation eigenständig oder mit Lakeflow-Pipelines definiert wurde.

- Für eigenständige Materialized Views muss der Workspace nicht für Serverless Lakeflow Pipelines aktiviert sein — der Refresh nutzt automatisch eine Serverless Pipeline.
- Für über Lakeflow-Pipelines definierte Materialized Views muss die Pipeline auf Serverless konfiguriert sein.

## <a id="semantik">3. Refresh-Semantik für Materialized Views</a>

Materialized Views garantieren zu Batch-Queries äquivalente Ergebnisse. Beispiel-Aggregat-Query:

```sql
SELECT account_id,
  COUNT(txn_id) txn_count,
  SUM(txn_amount) account_revenue
FROM transactions_table
GROUP BY account_id
```

Wird diese Query über ein beliebiges Databricks-Produkt ausgeführt, wird das Ergebnis mit Batch-Semantik berechnet — alle Datensätze der Quelltabelle `transactions_table` werden in einer Operation gescannt und aggregiert.

**Hinweis:** Manche Databricks-Produkte cachen Ergebnisse automatisch innerhalb oder über Sessions hinweg, wenn sich Datenquellen seit der letzten Ausführung nicht geändert haben. Automatisches Caching unterscheidet sich von Materialized Views.

Das folgende Beispiel wandelt diese Batch-Query in eine Materialized View um:

```sql
CREATE OR REPLACE MATERIALIZED VIEW transaction_summary AS
SELECT account_id,
  COUNT(txn_id) txn_count,
  SUM(txn_amount) account_revenue
FROM transactions_table
GROUP BY account_id
```

```python
@dp.materialized_view()
def transaction_summary():
  return (spark.read.table("transactions_table")
    .groupBy("account_id")
    .agg(
      count("*").alias("txn_count"),
      sum("txn_amount").alias("account_revenue")
    )
  )
```

Wird eine Materialized View refresht, ist das berechnete Ergebnis identisch zur Batch-Query-Semantik. Diese Query ist ein Beispiel für eine Materialized View, die inkrementell refresht werden kann — die Refresh-Operation unternimmt einen Best-Effort-Versuch, beim Berechnen der Ergebnisse nur neue oder geänderte Daten in der Quelle `transactions_table` zu verarbeiten.

## <a id="datenquellen">4. Datenquellen-Überlegungen für Materialized Views</a>

Eine Materialized View lässt sich gegen jede Datenquelle definieren, aber nicht alle Datenquellen eignen sich gut dafür.

**Wichtig:** Materialized Views unternehmen einen Best-Effort-Versuch, Ergebnisse für unterstützte Operationen inkrementell zu refreshen. Manche Änderungen in Datenquellen erfordern einen Full Refresh. Es lässt sich eine Refresh Policy definieren, die fehlschlägt, statt einen Full Refresh durchzuführen.

Alle Datenquellen für Materialized Views sollten robust gegenüber Full-Refresh-Semantik sein, selbst wenn die definierende Query inkrementelles Refresh unterstützt.

- Für Queries, bei denen ein Full Refresh kostenprohibitiv wäre, sollten Streaming Tables verwendet werden, um Exactly-once-Verarbeitung zu garantieren — z. B. bei sehr großen Tabellen.
- Eine Materialized View sollte **nicht** gegen eine Datenquelle definiert werden, deren Datensätze nur einmal verarbeitet werden sollen — dort sind Streaming Tables vorzuziehen. Beispiele:
  - Datenquellen ohne Datenhistorie, etwa Kafka.
  - Ingestion-Operationen, etwa Queries, die Auto Loader zur Ingestion aus Cloud-Objektspeicher nutzen.
  - Jede Datenquelle, bei der Daten nach Verarbeitung gelöscht/archiviert werden sollen, Informationen aber in nachgelagerten Tabellen erhalten bleiben müssen — z. B. eine nach Datum partitionierte Tabelle, bei der Datensätze älter als ein bestimmter Schwellenwert gelöscht werden sollen.
- Nicht alle Datenquellen unterstützen inkrementelles Refresh. Folgende Datenquellen unterstützen es:
  - Delta-Tabellen, einschließlich Unity-Catalog-Managed-Tables und External Tables auf Basis von Delta Lake.
  - Materialized Views.
  - Streaming Tables, einschließlich der Ziele von `AUTO CDC ... INTO`-Operationen.
  - Unity-Catalog-Managed-Iceberg-Tables (v2 und v3) — Iceberg v3 wird für die beste Unterstützung inkrementellen Refreshs empfohlen. Foreign Iceberg Tables werden nicht unterstützt.
- Manche Operationen für inkrementelles Refresh benötigen aktiviertes Row Tracking auf den abgefragten Datenquellen — Row Tracking ist ein nur von Delta-Tabellen unterstütztes Delta-Lake-Feature (dazu zählen Materialized Views, Streaming Tables und Unity-Catalog-Managed-Tables).
- Datenquellen mit definierten Row Filters oder Column Masks unterstützen kein inkrementelles Refresh.

## <a id="optimieren">5. Materialized Views optimieren</a>

Für optimale Performance empfiehlt Databricks, folgende Features auf allen Quelltabellen einer Materialized View zu aktivieren:

- Deletion Vectors
- Row Tracking
- Change Data Feed

Diese Features lassen sich bei der Erstellung setzen oder später über `ALTER TABLE` (ausgeführt von Databricks SQL):

```sql
ALTER TABLE <table-name> SET TBLPROPERTIES (
  delta.enableDeletionVectors = true,
  delta.enableRowTracking = true,
  delta.enableChangeDataFeed = true);
```

## <a id="refresh-typen">6. Refresh-Typen für Materialized Views</a>

Beim Update einer Materialized View lässt sich zwischen Refresh und Full Refresh wählen:

- Ein **Refresh** versucht ein inkrementelles Refresh, führt aber bei Bedarf eine vollständige Neuberechnung der Daten durch. Inkrementelles Refresh ist nur verfügbar, wenn das verbundene Compute Serverless ist.
- Ein **Full Refresh** berechnet immer alle Eingaben der Materialized View neu und setzt alle Checkpoints zurück.

### Default Refresh

Der Standard-Refresh einer Materialized View auf Serverless versucht ein *inkrementelles Refresh*. Dabei werden Änderungen in den zugrunde liegenden Daten seit dem letzten Refresh verarbeitet und an die Tabelle angehängt. Je nach Basistabellen und enthaltenen Operationen lassen sich nur bestimmte Arten von Materialized Views inkrementell refreshen. Ist ein inkrementelles Refresh nicht möglich oder das verbundene Compute Classic statt Serverless, wird eine vollständige Neuberechnung durchgeführt.

**Hinweis:** Databricks wendet ein Full oder inkrementelles Refresh an — die Entscheidung basiert darauf, welche Option kosteneffektiver ist und ob eine Query inkrementelles Refresh unterstützt (steuerbar über Refresh Policy, Abschnitt 10).

Die Ausgabe eines inkrementellen Refreshs und einer vollständigen Neuberechnung ist identisch. Databricks führt eine Kostenanalyse durch, um zwischen inkrementellem Refresh und vollständiger Neuberechnung die günstigere Option zu wählen.

Nur über Serverless Pipelines aktualisierte Materialized Views können inkrementelles Refresh nutzen — Materialized Views ohne Serverless Pipelines werden immer vollständig neu berechnet.

Werden Materialized Views mit einem SQL Warehouse oder Serverless Lakeflow Pipelines angelegt, refresht Databricks sie inkrementell, sofern ihre Queries unterstützt werden. Nutzt eine Query nicht unterstützte Ausdrücke, führt Databricks stattdessen eine vollständige Neuberechnung durch, was die Kosten erhöhen kann.

### Full Refresh

Ein Full Refresh überschreibt die Ergebnisse in der Materialized View, indem Tabelle und Checkpoints geleert und alle in der Quelle verfügbaren Daten erneut verarbeitet werden.

Für Materialized Views, die mit Databricks SQL definiert wurden:

```sql
REFRESH MATERIALIZED VIEW mv_name FULL
```

Für in Lakeflow-Pipelines definierte Materialized Views lässt sich ein Full Refresh wahlweise auf ausgewählte Datasets oder alle Datasets einer Pipeline anwenden.

**Wichtig:** Läuft ein Full Refresh gegen eine Datenquelle, in der Datensätze wegen Retention-Schwellenwert oder manueller Löschung entfernt wurden, spiegeln sich diese entfernten Datensätze nicht in den berechneten Ergebnissen wider. Alte Daten sind unter Umständen nicht wiederherstellbar, wenn sie in der Quelle nicht mehr verfügbar sind. Dies kann auch das Schema für Spalten ändern, die in den Quelldaten nicht mehr existieren.

## <a id="unterstuetzung">7. Unterstützung für inkrementelles Refresh nach SQL-Konstrukt</a>

Die folgende Tabelle listet die Unterstützung für inkrementelles Refresh nach SQL-Keyword bzw. -Klausel. Um eine bestimmte Query auf Inkrementalisierbarkeit zu testen, lässt sich `EXPLAIN CREATE MATERIALIZED VIEW` verwenden.

**Wichtig:** Manche mit Stern (\*) markierten Keywords/Klauseln benötigen aktiviertes Row Tracking auf den abgefragten Datenquellen.

| SQL-Keyword/-Klausel | PySpark-DataFrame-Äquivalent | Unterstützung für inkrementelles Refresh |
|---|---|---|
| `SELECT`-Ausdrücke\* | `df.select()` oder `df.selectExpr()` | Ja — Ausdrücke einschließlich deterministischer Built-in-Funktionen und unveränderlicher UDFs werden unterstützt. |
| `GROUP BY` | `df.groupBy().agg()` | Ja |
| `WITH` | Verkettung von DataFrame-Variablen | Ja — Common Table Expressions werden unterstützt. |
| `WITH RECURSIVE` | N/A | Nein — Materialized Views mit rekursiven CTEs sind für inkrementelles Refresh nicht geeignet und fallen auf vollständige Neuberechnung zurück. |
| `UNION ALL`\* | `df.union` oder `df.unionAll` | Ja |
| `FROM` | `df = spark.read...` | Unterstützte Basistabellen: Delta-Tabellen, Unity-Catalog-Managed-Iceberg-Tables, Materialized Views, Streaming Tables. |
| `WHERE`, `HAVING`\* | `df.filter()`, `df.where()`, `df.groupBy().filter()` | Filterklauseln wie `WHERE` und `HAVING` werden unterstützt. |
| `INNER JOIN`\* | `df.join()` | Ja |
| `LEFT OUTER JOIN`\* | `df.join(... how="left")` | Ja |
| `FULL OUTER JOIN`\* | `df.join(... how="full")` | Ja |
| `RIGHT OUTER JOIN`\* | `df.join(... how="right")` | Ja |
| `OVER` | `df.over(window.partitionBy)`-Funktionen | Ja — `PARTITION_BY`-Spalten müssen für die Inkrementalisierung von Fensterfunktionen angegeben werden. |
| `QUALIFY` | `df.over(w).filter(...)` | Ja |
| `EXPECTATIONS` | `@dp.expect` | Ja — Materialized Views mit Expectations lassen sich inkrementell refreshen. Nicht unterstützt jedoch, wenn die Materialized View aus einer View mit Expectations liest, oder wenn die Materialized View eine `DROP`-Expectation hat und `NOT NULL`-Spalten im Schema enthält. |
| UDFs | UDFs | Databricks versucht zu erkennen, wenn sich das Verhalten einer UDF ändert, und führt dann ein Full Refresh durch. UDFs, die andere Funktionen/Bibliotheken aufrufen, können ihr Verhalten jedoch auf Weisen ändern, die Databricks nicht erkennt — in diesem Fall liegt die Verantwortung für ein Full Refresh beim Anwender. |
| Nicht-deterministische Funktionen | Nicht-deterministische Funktionen | Nicht-deterministische Zeitfunktionen werden in `WHERE`-Klauseln unterstützt, etwa `current_date()`, `current_timestamp()`, `now()`. Andere nicht-deterministische Funktionen werden nicht unterstützt. |
| Nicht-deterministische Datentypen | Nicht-deterministische Datentypen | Aggregationen, die Gleitkommawerte summieren (`SUM`, `AVG`, Kovarianz), können bei `FLOAT`/`DOUBLE`-Spalten nicht-deterministische Ergebnisse liefern und erzwingen ein Full Refresh. Diese Spalten in `DECIMAL` casten (z. B. `SUM(CAST(revenue AS DECIMAL(18,2)))`), um inkrementelles Refresh zu ermöglichen. |
| Nicht unterstützte Quellen | Nicht unterstützte Quellen | Quellen wie Volumes, External Locations und Foreign Catalogs werden nicht unterstützt. Foreign Iceberg Tables werden nicht unterstützt. Unity-Catalog-Managed-Iceberg-Tables werden unterstützt. |

## <a id="insights">8. Incrementalization Insights</a>

Im Pipeline-Editor oder beim Monitoring eines Pipeline-Updates enthält das **Tables**-Panel eine Spalte **Incrementalization**, die zeigt, wie jede Materialized View im letzten Update verarbeitet wurde:

| Status | Beschreibung |
|---|---|
| **Incremental** | Die Materialized View wurde inkrementell refresht. |
| **Full recompute** | Die Materialized View wurde vollständig neu berechnet. |
| **No change** | Keine Änderungen an den Quelldaten erkannt — die Materialized View wurde nicht aktualisiert. |

Erkennt Databricks ein Problem, das ein inkrementelles Refresh verhindert hat (oder künftig verhindern könnte), und hat eine empfohlene Lösung, erscheint neben dem Status ein Lightbulb-Icon-Insight. Ein Klick öffnet das **Issues**-Panel, gefiltert nach dieser Materialized View. Jeder Insight erklärt die Ursache und empfiehlt eine Lösung. Verbreitete Lösungen:

- Row Tracking oder Deletion Vectors auf den Quelltabellen aktivieren.
- Einen nicht unterstützten Operator in der Materialized-View-Definition umschreiben.
- Die Pipeline auf Serverless Compute konfigurieren.

Insights können auch bei Status **No change** oder bei einem Dry Run erscheinen, sodass Probleme behoben werden können, bevor sie ein Update beeinträchtigen. Ein Insight kann auch zur relevanten Codezeile führen. Das Fehlen eines Insights garantiert nicht, dass eine Materialized View inkrementell refresht werden kann.

Genie Code lässt sich auch fragen, warum eine Materialized View nicht inkrementell refresht, und kann die Probleme erklären und beheben.

## <a id="refresh-typ-bestimmen">9. Refresh-Typ eines Updates bestimmen</a>

Zur Optimierung der Refresh-Performance nutzt Databricks ein Kostenmodell, um die Refresh-Technik auszuwählen:

| Technik | Inkrementelles Refresh? | Beschreibung |
|---|---|---|
| `FULL_RECOMPUTE` | Nein | Die Materialized View wurde vollständig neu berechnet. |
| `NO_OP` | Nicht zutreffend | Die Materialized View wurde nicht aktualisiert, da keine Änderungen an der Basistabelle erkannt wurden. |
| Eine von: `ROW_BASED`, `PARTITION_OVERWRITE`, `WINDOW_FUNCTION`, `APPEND_ONLY`, `GROUP_AGGREGATE`, `GENERIC_AGGREGATE` | Ja | Die Materialized View wurde inkrementell mit der angegebenen Technik refresht. |

Zur Ermittlung der verwendeten Technik wird das Lakeflow-Pipeline-Event-Log abgefragt, wobei `event_type` gleich `planning_information` ist:

```sql
SELECT
  timestamp,
  message
FROM
  event_log(TABLE(<fully-qualified-table-name>))
WHERE
  event_type = 'planning_information'
ORDER BY
  timestamp desc;
```

`<fully-qualified-table-name>` wird durch den vollqualifizierten Namen der Materialized View (inkl. Katalog und Schema) ersetzt.

Beispielausgabe:

| timestamp | message |
|---|---|
| `2025-03-21T22:23:16.497+00:00` | `Flow 'sales' has been planned to be executed as ROW_BASED.` |

## <a id="refresh-policy">10. Refresh Policy</a>

Standardmäßig wählt Databricks automatisch die kosteneffektivste Refresh-Strategie (inkrementell oder vollständig) basierend auf Query-Struktur, Datenänderungsvolumen und Kostenmodellierung des Systems — ohne manuelle Konfiguration.

Manche Workloads benötigen jedoch vorhersehbareres oder explizit gesteuertes Refresh-Verhalten. Dafür lässt sich eine `REFRESH POLICY` in der Materialized-View-Definition angeben. Eine Refresh Policy steuert, ob Databricks inkrementelles Refresh durchführt, wann auf ein Full Refresh zurückgefallen wird, und ob ein Refresh statt einer vollständigen Neuberechnung fehlschlagen soll.

Über `REFRESH POLICY` lässt sich konfigurieren:

- **`AUTO`** (Standard) — automatische, kostenbasierte Auswahl. Databricks wählt inkrementell oder vollständig basierend auf Effizienz und Query-Fähigkeiten. Für die meisten Anwender empfohlen.
- **`INCREMENTAL`** — bevorzugt inkrementelles Refresh. Databricks führt inkrementelles Refresh durch, wo immer möglich, und fällt auf ein Full Refresh zurück, wenn der Query-Plan inkrementelles Refresh nicht mehr unterstützt.
- **`INCREMENTAL STRICT`** — verlangt strikt inkrementelles Refresh. Inkrementelles Refresh ist im Normalbetrieb erforderlich — ist Inkrementalisierung nicht möglich, schlägt der Refresh bzw. die Create-Operation fehl.
- **`FULL`** — führt immer vollständige Refreshes durch. Databricks führt nie inkrementelles Refresh durch, selbst wenn die Query inkrementalisierbar wäre.

```sql
-- Create a materialized view with an incremental refresh policy
CREATE MATERIALIZED VIEW IF NOT EXISTS my_mv
REFRESH POLICY INCREMENTAL
AS SELECT a, sum(b) FROM my_catalog.example.my_table GROUP BY a;
```

```python
from pyspark import pipelines as dp

@dp.materialized_view(
  refresh_policy = 'incremental_strict'
)
def my_mv():
  return spark.read("main.default.source_table")
```

Die optimale Refresh Policy hängt von den Workload-Eigenschaften ab:

- **`AUTO`** eignet sich für die meisten Workloads — balanciert Kosten und Performance und passt sich automatisch bei geändertem Query-Verhalten an.
- **`INCREMENTAL`** ist nützlich, wenn inkrementelles Refresh Vorteile bietet, es aber akzeptabel ist, dass Databricks Full Refreshes durchführt, wenn Inkrementalisierung vorübergehend nicht verfügbar ist (z. B. wenn Row Tracking auf einer Quelltabelle deaktiviert wird).
- **`INCREMENTAL STRICT`** sollte verwendet werden, wenn inkrementelles Refresh zur Einhaltung von Kosten-, Performance- oder SLA-Vorgaben erforderlich ist und unerwartete Full Refreshes inakzeptabel sind — empfohlen, wenn Anwender lieber ein fehlschlagendes Update zum Debuggen bevorzugen, statt mit einem Full Refresh fortzufahren.
- **`FULL`** eignet sich, wenn inkrementelles Refresh wenig Nutzen bietet, das Dataset klein ist, oder sich die Query-Struktur häufig auf eine Weise ändert, die Inkrementalisierung verhindert.

---

## <a id="quellen">11. Quellen</a>

- Incremental refresh for materialized views (Azure-Spiegelseite, vollständig als Rohtext abgerufen): https://learn.microsoft.com/en-us/azure/databricks/ldp/incremental-refresh
- Incremental refresh for materialized views (AWS, Zweitabruf zur Gegenprüfung von Serverless-Pflicht und `REFRESH POLICY`-Werten): https://docs.databricks.com/aws/en/ldp/incremental-refresh

**Stand:** 2026-08-19.
