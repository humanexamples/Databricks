[← Übersicht](00%20Uebersicht.md)

# SCD im Star-Schema

**Kombination:** Faktentabelle · SCD-2-Dimension · Point-in-Time-Join (Range Join) · Surrogate-Key-Lookup · Late-arriving Dimensions · SCD-6-View · Gold-Materialized-Views

In der Gold-Schicht werden Fakten (Bestellungen) mit Dimensionen (Kunden) verbunden. Bei einer SCD-2-Dimension ist die entscheidende Frage: **Welche Version des Kunden gehört zu einer Bestellung?**

---

## Beispieldaten

Anna (Kunde 42) zieht am 10.09. von Hamburg nach Berlin.

**`dim_customer_history`** (AUTO CDC, SCD 2):

| customer_id | city | `__START_AT` | `__END_AT` |
|---|---|---|---|
| 42 | Hamburg | 2026-09-01 | 2026-09-10 |
| 42 | Berlin | 2026-09-10 | NULL |

**`silver_orders`:**

| order_id | customer_id | order_ts | amount |
|---|---|---|---|
| 1 | 42 | 2026-09-05 | 100 |
| 2 | 42 | 2026-09-12 | 50 |

---

## A – Zwei Sichten auf dieselben Daten

```sql
-- 1. Umsatz nach Stadt ZUM ZEITPUNKT der Bestellung (Point-in-Time-Join)
CREATE OR REFRESH MATERIALIZED VIEW gold_revenue_by_city_historical AS
SELECT d.city, sum(f.amount) AS revenue
FROM silver_orders f
JOIN dim_customer_history d
  ON  f.customer_id = d.customer_id
  AND f.order_ts >= d.__START_AT
  AND f.order_ts <  coalesce(d.__END_AT, TIMESTAMP'9999-12-31')
GROUP BY d.city;

-- 2. Umsatz nach AKTUELLER Stadt
CREATE OR REFRESH MATERIALIZED VIEW gold_revenue_by_city_current AS
SELECT d.city, sum(f.amount) AS revenue
FROM silver_orders f
JOIN dim_customer_history d
  ON  f.customer_id = d.customer_id
  AND d.__END_AT IS NULL
GROUP BY d.city;
```

| Sicht | Hamburg | Berlin |
|---|---|---|
| historisch (Point-in-Time) | 100 | 50 |
| aktuell | – | 150 |

Beide Antworten sind richtig, aber auf **unterschiedliche Fragen**. Genau dafür braucht man SCD 2: Mit SCD 1 wäre nur die zweite Sicht möglich.

**Achtung:** Ein in der Quelle gelöschter Kunde hat keine Zeile mit `__END_AT IS NULL` mehr. Seine Bestellungen fallen aus der „aktuellen“ Sicht heraus. Wenn das nicht gewünscht ist, `LEFT JOIN` verwenden und `city` mit `coalesce(d.city, 'gelöscht')` auffüllen.

**Performance:** Die Bedingung `order_ts >= start AND order_ts < end` ist ein **Punkt-in-Intervall-Range-Join**. Databricks SQL optimiert ihn automatisch. Deshalb `coalesce(…, '9999-12-31')` statt `OR __END_AT IS NULL`: So bleibt die Bedingung eine reine `>=`/`<`-Form, die dem dokumentierten Range-Join-Muster entspricht. Eine zusätzliche `OR`-Verzweigung passt nicht in dieses Muster. Details und manueller `RANGE_JOIN`-Hint: [Range-Join-Optimierung](../../Online%20Databricks%20Docs/Platform/Tables/Query-Optimierung/07-range-join.md).

---

## B – Surrogate Key beim Laden der Fakten auflösen

Bei einer manuell gepflegten SCD-2-Tabelle mit Surrogate Key ([03](03%20SCD%20Type%202%20manuell%20mit%20MERGE.md)) speichert die Faktentabelle direkt den Key **der Version**, die zum Bestellzeitpunkt gültig war. Spätere Abfragen brauchen dann nur noch einen einfachen Gleichheits-Join.

```sql
INSERT INTO catalog.gold.fact_orders (order_id, customer_sk, order_ts, amount)
SELECT o.order_id,
       coalesce(d.customer_sk, -1) AS customer_sk,     -- -1 = „Unknown Member“
       o.order_ts,
       o.amount
FROM catalog.silver.orders_new o
LEFT JOIN catalog.schema.dim_customer_history d
  ON  o.customer_id = d.customer_id
  AND o.order_ts >= d.valid_from
  AND o.order_ts <  coalesce(d.valid_to, TIMESTAMP'9999-12-31');
```

```sql
-- Danach: einfacher Join ohne Zeitbedingung
SELECT d.city, sum(f.amount)
FROM catalog.gold.fact_orders f
JOIN catalog.schema.dim_customer_history d ON f.customer_sk = d.customer_sk
GROUP BY d.city;
```

**Late-arriving Dimension:** Kommt eine Bestellung an, bevor der Kunde in der Dimension existiert, findet der Join nichts. Statt die Bestellung zu verlieren, zeigt sie auf die Dummy-Zeile `-1` („Unknown Member“) und wird später per `MERGE` korrigiert.

> Bei AUTO-CDC-Tabellen gibt es keinen eingebauten Surrogate Key. Eine Version ist dort eindeutig über `customer_id` + `__START_AT`. Zu Surrogate Keys allgemein: [Dimensionale Modellierung und SCD](../Data%20Transformation%20and%20Modeling/05%20Datenmodellierung/02%20Dimensionale%20Modellierung%20und%20SCD.md).

---

## C – SCD 6: Historie **und** aktueller Wert in jeder Zeile

Manche Berichte brauchen beides nebeneinander, z. B. „Umsatz nach damaliger Stadt, aber gruppiert nach heutiger Region“. SCD 6 lässt sich als View auf SCD 2 bauen, ohne eine weitere Tabelle zu pflegen:

```sql
CREATE VIEW gold.v_dim_customer_scd6 AS
SELECT h.customer_id,
       h.city            AS city_at_that_time,
       c.city            AS city_current,
       h.__START_AT      AS valid_from,
       h.__END_AT        AS valid_to,
       h.__END_AT IS NULL AS is_current
FROM dim_customer_history h
LEFT JOIN (SELECT customer_id, city
           FROM dim_customer_history
           WHERE __END_AT IS NULL) c
  ON h.customer_id = c.customer_id;
```

---

## Merksätze

- **Fakten** sind Ereignisse und werden per Append oder Streaming Table geladen, nicht als SCD.
- **Dimensionen** sind SCD 1 (nur aktuell) oder SCD 2 (mit Historie).
- Point-in-Time-Join: `fakt.zeit >= dim.start AND fakt.zeit < coalesce(dim.end, '9999-12-31')`.
- Aktueller Stand aus SCD 2: `WHERE __END_AT IS NULL`.

---
[← Vorherige Datei](03%20SCD%20Type%202%20manuell%20mit%20MERGE.md) · [Übersicht](00%20Uebersicht.md) · [Nächste Datei →](05%20SCD%20mit%20Governance%2C%20Data%20Quality%20und%20Performance.md)

## Quellen

- [Range join optimization](https://docs.databricks.com/aws/en/optimizations/range-join)
- [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)
