# `REFRESH POLICY`-Klausel (Pipelines) — Referenz

## Abschnittsübersicht

1. [Grundzweck](#grundzweck)
2. [Formale Syntax](#syntax)
3. [Parameter](#parameter)
4. [Verhalten bei Fehlschlag](#fehlschlag)
5. [Doku-eigenes Beispiel](#doku-beispiel)
6. [Quellen](#quellen)

---

## <a id="grundzweck">1. Grundzweck</a>

Die `REFRESH POLICY`-Klausel fügt einer Materialized View eine Refresh Policy hinzu, die steuert, wann ein Refresh inkrementalisiert wird. Sie gehört zum `CREATE MATERIALIZED VIEW`-Statement (siehe `CREATE MATERIALIZED VIEW.md` in diesem Ordner).

Ob eine SQL-Abfrage inkrementalisierbar ist, lässt sich mit dem `EXPLAIN CREATE MATERIALIZED VIEW`-Statement in Databricks SQL prüfen.

---

## <a id="syntax">2. Formale Syntax</a>

```sql
REFRESH POLICY refresh_policy

refresh_policy:
  AUTO | INCREMENTAL | INCREMENTAL STRICT | FULL
```

### Reales Beispiel mit allen Bausteinen der formalen Syntax

Da `refresh_policy` eine einzelne, sich gegenseitig ausschließende Wahl aus vier Werten ist, zeigt das folgende, aus den verifizierten Bausteinen dieses Dokuments zusammengesetzte Beispiel den Einsatz innerhalb eines `CREATE MATERIALIZED VIEW`-Statements — mit `INCREMENTAL` als der Policy, die inkrementelles Refresh am striktesten erzwingt, ohne bei fehlender Inkrementalisierbarkeit sofort zu scheitern:

```sql
CREATE OR REFRESH MATERIALIZED VIEW main.sales.daily_revenue
REFRESH POLICY INCREMENTAL
AS SELECT order_date, SUM(amount) AS revenue
FROM main.sales.orders
GROUP BY order_date;
```

Die drei übrigen, alternativ wählbaren Policy-Werte:

- **`AUTO`** (Standard, wenn `REFRESH POLICY` weggelassen wird) — das System wählt automatisch inkrementelles oder vollständiges Refresh anhand des Kostenmodells.
- **`INCREMENTAL STRICT`** — das System verwendet ausschließlich inkrementelle Refreshes; ein Refresh, der die Policy nicht erfüllen kann, schlägt fehl statt auf ein vollständiges Refresh zurückzufallen.
- **`FULL`** — das System verwendet stets ein vollständiges Refresh.

---

## <a id="parameter">3. Parameter</a>

- **`refresh_policy`** — definiert eine Refresh Policy für die Materialized View. Wird `REFRESH POLICY` weggelassen, ist `AUTO` die Standard-Policy. Die Refresh Policy legt fest, wie ein Refresh die Inkrementalisierung der Materialized View handhabt:
  - **`AUTO`** — das System wählt automatisch inkrementell oder vollständig anhand des Kostenmodells.

    | Zustand | Verhalten |
    |---|---|
    | Inkrementell ist für das Refresh verfügbar. | Nutzt das Kostenmodell, um zu bestimmen, was günstiger ist — inkrementell oder vollständig. |
    | Inkrementell ist für das Refresh nicht verfügbar. | Führt ein vollständiges Refresh durch. |
    | Erstellung oder Reinitialisierung ist erforderlich (z. B. bei Schemaänderung). | Führt ein vollständiges Refresh durch. |
  - **`INCREMENTAL`** — das System verwendet inkrementelle Refreshes, wenn möglich. Bei `CREATE` schlägt das Create-Statement fehl, wenn die Abfrage nicht inkrementalisierbar ist.

    | Zustand | Verhalten |
    |---|---|
    | Inkrementell ist für das Refresh verfügbar. | Führt ein inkrementelles Refresh durch. |
    | Inkrementell ist für das Refresh nicht verfügbar. | Führt ein vollständiges Refresh durch. |
    | Erstellung oder Reinitialisierung ist erforderlich, Inkrementalisierung der Abfrage ist aber möglich. | Führt ein vollständiges Refresh durch. |
    | Erstellung oder Reinitialisierung ist erforderlich, und Inkrementalisierung der Abfrage ist nicht möglich. | Die Operation schlägt fehl. |
  - **`INCREMENTAL STRICT`** — das System verwendet inkrementelle Refreshes. Bei `CREATE` schlägt das Create-Statement fehl, wenn die Abfrage nicht inkrementalisierbar ist.

    | Zustand | Verhalten |
    |---|---|
    | Inkrementell ist für das Refresh verfügbar. | Führt ein inkrementelles Refresh durch. |
    | Inkrementell ist für das Refresh nicht verfügbar. | Das Refresh schlägt fehl. |
    | Erstellung oder Reinitialisierung ist erforderlich, Inkrementalisierung der Abfrage ist aber möglich. | Führt ein vollständiges Refresh durch. |
    | Erstellung oder Reinitialisierung ist erforderlich, und Inkrementalisierung der Abfrage ist nicht möglich. | Die Operation schlägt fehl. |
  - **`FULL`** — das System verwendet stets ein vollständiges Refresh.

    | Zustand | Verhalten |
    |---|---|
    | Inkrementell ist für das Refresh verfügbar. | Führt ein vollständiges Refresh durch. |
    | Inkrementell ist für das Refresh nicht verfügbar. | Führt ein vollständiges Refresh durch. |
    | Erstellung oder Reinitialisierung ist erforderlich. | Führt ein vollständiges Refresh durch. |

---

## <a id="fehlschlag">4. Verhalten bei Fehlschlag</a>

Schlägt ein Refresh fehl, weil es die Refresh Policy nicht erfüllen kann (bei `REFRESH POLICY INCREMENTAL (STRICT)`), liefert das System die Fehlerklasse `MATERIALIZED_VIEW_NOT_INCREMENTALIZABLE` mit detaillierten Informationen zum Grund der fehlenden Inkrementalisierbarkeit:

| Fehlerdetail | Bedeutung |
|---|---|
| `AGGREGATE_NOT_TOP_NODE` | `GROUP BY` mit komplexen Ausdrücken darüber wird nicht unterstützt. |
| `EXPRESSION_NOT_DETERMINISTIC` | Eine nicht-deterministische Funktion, wie `RAND`, wird in der Abfrage verwendet. |
| `INPUT_NOT_IN_DELTA` | Eine oder mehrere Quell-Datasets sind keine Delta-Tabellen. |
| `OPERATOR_NOT_INCREMENTALIZABLE` | Ein Operator, etwa ein komplexer Join, verhindert die Inkrementalisierung. |
| `ROW_TRACKING_NOT_ENABLED` | Quelltabellen, die Row Tracking benötigen, haben Row Tracking nicht aktiviert. |
| `SUBQUERY_EXPRESSION_NOT_INCREMENTALIZABLE` | Eine oder mehrere Subqueries in der Abfrage sind nicht inkrementalisierbar. |
| `UDF_NOT_DETERMINISTIC` | Eine oder mehrere im Ausdruck verwendete UDFs sind nicht als deterministisch markiert. |
| `WINDOW_WITHOUT_PARTITION_BY` | Window-Spezifikationen ohne `PARTITION BY` sind nicht inkrementalisierbar. |

Ob eine SQL-Abfrage inkrementalisierbar ist, lässt sich mit dem `EXPLAIN CREATE MATERIALIZED VIEW`-Statement in Databricks SQL prüfen.

---

## <a id="doku-beispiel">5. Doku-eigenes Beispiel</a>

```sql
-- Create a materialized view with an incremental policy
CREATE OR REFRESH MATERIALIZED VIEW my_mv
REFRESH POLICY INCREMENTAL
AS SELECT a, sum(b) FROM my_catalog.example.my_table GROUP BY a;
```

---

## <a id="quellen">6. Quellen</a>

- REFRESH POLICY clause (pipelines) — SQL-Sprachreferenz (formale Syntax, alle vier Policy-Werte mit Verhaltenstabellen, Fehlerklasse `MATERIALIZED_VIEW_NOT_INCREMENTALIZABLE` mit allen Fehlerdetails, Doku-Beispiel): https://docs.databricks.com/aws/en/ldp/developer/ldp-sql-ref-create-materialized-view-refresh-policy

**Stand:** 2026-08-19.
