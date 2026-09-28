[← Übersicht](00%20Uebersicht.md)

# SCD Type 2 mit AUTO CDC

**Kombination:** AUTO CDC · `TRACK HISTORY` · Deletes · Abfragemuster · Snapshots · Change Data Feed des Ziels

---

## A – Grundmuster

```sql
CREATE OR REFRESH STREAMING TABLE dim_customer_history;

CREATE FLOW dim_customer_scd2 AS AUTO CDC INTO dim_customer_history
FROM STREAM customers_cdc_clean
KEYS (customer_id)
APPLY AS DELETE WHEN op = 'd'
SEQUENCE BY change_ts
COLUMNS * EXCEPT (op)
STORED AS SCD TYPE 2;
```

AUTO CDC fügt die Spalten **`__START_AT`** und **`__END_AT`** hinzu. Sie haben den Datentyp der `SEQUENCE BY`-Spalte, hier also `TIMESTAMP`.

**Beispielverlauf für Kundin 42:**

| Event | `op` | `change_ts` | `city` |
|---|---|---|---|
| 1 | `c` | 2026-09-01 | Hamburg |
| 2 | `u` | 2026-09-10 | Berlin |
| 3 | `d` | 2026-09-20 | – |

**Ergebnis in `dim_customer_history`:**

| customer_id | city | `__START_AT` | `__END_AT` |
|---|---|---|---|
| 42 | Hamburg | 2026-09-01 | 2026-09-10 |
| 42 | Berlin | 2026-09-10 | 2026-09-20 |

Nach dem Delete gibt es **keine aktive Zeile** mehr (keine Zeile mit `__END_AT IS NULL`), die Historie bleibt aber erhalten.

---

## B – Nur relevante Spalten versionieren (`TRACK HISTORY`)

Ändert sich nur die E-Mail-Adresse, soll keine neue Version entstehen. Der Wert wird dann in der aktuellen Version überschrieben (SCD-1-Verhalten für diese Spalte).

```sql
CREATE FLOW dim_customer_scd2 AS AUTO CDC INTO dim_customer_history
FROM STREAM customers_cdc_clean
KEYS (customer_id)
APPLY AS DELETE WHEN op = 'd'
SEQUENCE BY change_ts
COLUMNS * EXCEPT (op)
STORED AS SCD TYPE 2
TRACK HISTORY ON * EXCEPT (email, last_login);
```

Python: `track_history_except_column_list = ["email", "last_login"]` bzw. `track_history_column_list = [...]` als Einschlussliste.

**Warum wichtig:** Ohne `TRACK HISTORY` erzeugt jede Kleinigkeit (z. B. ein `last_login`-Zeitstempel) eine neue Version, und die Tabelle wächst unnötig.

---

## C – Abfragemuster auf einer SCD-2-Tabelle

```sql
-- 1. Aktueller Stand (entspricht einer SCD-1-Tabelle)
SELECT * FROM dim_customer_history
WHERE __END_AT IS NULL;

-- 2. Stand zu einem Stichtag (Point-in-Time)
SELECT * FROM dim_customer_history
WHERE __START_AT <= TIMESTAMP'2026-09-15'
  AND (__END_AT > TIMESTAMP'2026-09-15' OR __END_AT IS NULL);

-- 3. Verlauf eines Kunden
SELECT customer_id, city, __START_AT, __END_AT
FROM dim_customer_history
WHERE customer_id = 42
ORDER BY __START_AT;

-- 4. Gelöschte Kunden (Historie vorhanden, aber keine aktive Version)
SELECT customer_id
FROM dim_customer_history
GROUP BY customer_id
HAVING count_if(__END_AT IS NULL) = 0;

-- 5. Wie oft hat jeder Kunde umgezogen?
SELECT customer_id, count(*) - 1 AS moves
FROM dim_customer_history
GROUP BY customer_id;
```

**Sprechende Spaltennamen für BI-Nutzer** per View:

```sql
CREATE VIEW gold.v_dim_customer_history AS
SELECT * EXCEPT (__START_AT, __END_AT),
       __START_AT AS valid_from,
       __END_AT   AS valid_to,
       __END_AT IS NULL AS is_current
FROM dim_customer_history;
```

---

## D – SCD 2 aus Voll-Snapshots

Die Quelle liefert keine Events, sondern täglich den ganzen Bestand. Die Pipeline vergleicht aufeinanderfolgende Snapshots und baut daraus die Historie auf.

```python
from pyspark import pipelines as dp

@dp.temporary_view
def customer_snapshot():
    return spark.read.table("catalog.schema.customer_snapshot_today")

dp.create_streaming_table("dim_customer_history")

dp.create_auto_cdc_from_snapshot_flow(
    target             = "dim_customer_history",
    source             = "customer_snapshot",
    keys               = ["customer_id"],
    stored_as_scd_type = 2,
    track_history_except_column_list = ["email"])
```

Hier gibt es **kein** `sequence_by`: Die Reihenfolge ergibt sich aus der Reihenfolge der Snapshots bzw. Pipeline-Läufe. Das ist das Beispiel für **SCD ohne klassisches CDC**.

---

## E – Änderungen des SCD-2-Ziels weiterreichen (CDF)

Ab DBR 15.2 lässt sich der Change Data Feed eines AUTO-CDC-Ziels lesen, z. B. um nur geänderte Kunden in Gold neu zu berechnen:

```python
changes = (spark.readStream.option("readChangeFeed", "true")
           .table("catalog.schema.dim_customer_history"))
```

- Eine neue Version erscheint typischerweise als `insert`, das Schließen der alten Version als Update (`update_preimage`/`update_postimage`) auf `__END_AT`.
- Der Primärschlüssel einer Zeile ist bei SCD 2: `customer_id` **plus** `coalesce(__START_AT, __END_AT)`.

Mehr zur CDF-Weitergabe: [../CDC/04](../CDC/04%20Change%20Data%20Feed%20-%20Aenderungen%20weiterreichen.md).

---

## Stolperfallen

| Problem | Lösung |
|---|---|
| Zwei Events desselben Keys mit identischer Sequenz | nach mehreren Spalten sequenzieren (`SEQUENCE BY STRUCT(change_ts, lsn)`) |
| `NULL` in der Sequenzspalte | nicht unterstützt → vorher per Expectation filtern |
| `APPLY AS TRUNCATE WHEN` | nur bei SCD 1 erlaubt, **nicht** bei SCD 2 |
| Manuelle DML auf dem Ziel | möglich, aber gültige `__START_AT`/`__END_AT` mitgeben |
| Streaming-Lesen aus dem Ziel ohne CDF | bricht bei Updates ab → CDF nutzen oder `skipChangeCommits` |

---
[← Vorherige Datei](01%20SCD%20Type%201%20-%20Umsetzungswege.md) · [Übersicht](00%20Uebersicht.md) · [Nächste Datei →](03%20SCD%20Type%202%20manuell%20mit%20MERGE.md)

## Quellen

- [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)
- [create_auto_cdc_from_snapshot_flow](https://docs.databricks.com/aws/en/ldp/developer/ldp-python-ref-apply-changes-from-snapshot)
