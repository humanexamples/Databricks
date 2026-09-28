# Dimensionale Modellierung und SCD

## Grundkonzept: Fact- und Dimension-Tabellen

- **Fact-Tabellen:** Ereignisse/Messwerte (Bestellungen, Klicks, Verkäufe).
- **Dimension-Tabellen:** beschreibender Kontext (Kunden, Produkte, Daten).

## Star-Schema-Architektur

Zentrale Fact-Tabelle verbunden über Keys mit mehreren Dimension-Tabellen. Fügt sich in die Medaillon-Architektur ein: Bronze/Silver = Ingestion/Bereinigung, Gold = materialisierte Fact-/Dimension-Tabellen.

## Implementierungsempfehlung je Tabellentyp

```sql
-- Dimension-Tabelle ohne Historienbedarf: Materialized View
CREATE OR REFRESH MATERIALIZED VIEW gold.dim_customer AS
SELECT customer_id, name, segment FROM silver.customers;

-- Dimension-Tabelle MIT Historienbedarf: Streaming Table + AUTO CDC ... STORED AS SCD TYPE 2
CREATE OR REFRESH STREAMING TABLE gold.dim_customer_scd2;

CREATE FLOW dim_customer_scd2_flow AS AUTO CDC INTO gold.dim_customer_scd2
FROM STREAM silver.customer_changes
KEYS (customer_id)
SEQUENCE BY updated_at
STORED AS SCD TYPE 2;

-- Fact-Tabelle: Streaming Table, inkrementell aus Silver gespeist -> Gold-Aggregate nahe Echtzeit
CREATE OR REFRESH STREAMING TABLE gold.fact_orders AS
SELECT * FROM STREAM silver.orders;
```

- Merksatz: Facts als Streaming Tables, Dimensionen als Materialized Views — Ausnahme: bei Historienbedarf `AUTO CDC ... STORED AS SCD TYPE 2`.

## Natürliche vs. Surrogate Keys

- Natürliche Keys bevorzugen, wenn stabil und nutzbar.
- Für Surrogate Keys: **keine Hash-Funktionen** — stattdessen ordnungserhaltend ("order-preserving") deterministisch aus dem stabilen natürlichen Key ableiten, sodass dieselbe fachliche Entität stets denselben Surrogate Key erhält.

## Datumsdimension (`dim_date`)

Als einfache Materialized View, generiert über `sequence()` + `explode()` über einen Datumsbereich — nicht aus einer externen Quelle eingelesen.

```sql
CREATE OR REFRESH MATERIALIZED VIEW gold.dim_date AS
SELECT explode(sequence(DATE'2020-01-01', DATE'2030-12-31', INTERVAL 1 DAY)) AS date_value;
-- Ergebnis: eine Zeile je Kalendertag im angegebenen Bereich
```

- Downstream-BI-Tools sollten Gold-Materialized-Views direkt abfragen.

---

## SCD Type 1 vs. Type 2

Slowly Changing Dimensions (SCD) legen fest, wie Änderungen aus vorgelagerten Systemen in analytischen Tabellen angewendet/modelliert werden.

**SCD Typ 1 — nur aktueller Zustand:** überschreibt alte Daten, keine Historie. Beispiel: Rolle ändert sich "Owner" → "Manager", Tabelle zeigt nur noch "Manager".

- Einsetzen wenn: nur aktueller Zustand nötig; nachgelagerte Materialized Views sollen inkrementell statt vollständig neu berechnet werden; stabile Surrogate Keys für Joins benötigt.

**SCD Typ 2 — vollständige Historie:** mehrere Versionen mit Zeitstempel-Metadaten `__START_AT`/`__END_AT`. Aktive Datensätze: `__END_AT = NULL`. Ermöglicht Rekonstruktion des Zustands zu jedem Zeitpunkt.

- Einsetzen wenn: Auditierbarkeit/Regulatorik; Kundenanalysen über Entitätsentwicklung; Point-in-Time-Reporting; Trendanalyse/Vergleich historischer Zustände.

| Operation | SCD Typ 1 | SCD Typ 2 |
|---|---|---|
| **INSERT** | Neuer Datensatz eingefügt. | Neuer Datensatz als erste aktive Version (`__START_AT` gesetzt, `__END_AT = NULL`). |
| **UPDATE** | Bestehender Datensatz direkt überschrieben — alter Wert nicht mehr abrufbar. | Bisherige aktive Version geschlossen (`__END_AT` = Sequenzwert des Updates), neue Version als aktiv eingefügt (`__END_AT = NULL`); beide Zeilen bleiben erhalten. |
| **DELETE** | Datensatz aus Zieltabelle entfernt (`APPLY AS DELETE WHEN`). | Historie bleibt: aktive Version wird geschlossen, keine neue aktive Version — Datensatz erscheint in keiner aktiven Zeile mehr. |

- Entscheidung: Typ 1 wenn nur aktueller Stand zählt (Zusatzvorteil: inkrementelle statt vollständige Neuberechnung nachgelagerter Materialized Views); Typ 2 wenn vollständige Änderungshistorie für Auditing/Point-in-Time/Trend nötig.

## Bezug zu den AUTO-CDC-APIs

Beide `AUTO CDC`-APIs (`AUTO CDC ... INTO` in SQL, `create_auto_cdc_flow()` / `create_auto_cdc_from_snapshot_flow()` in Python) unterstützen SCD Typ 1 und 2 über `STORED AS SCD TYPE 1`/`STORED AS SCD TYPE 2` (SQL) bzw. `stored_as_scd_type` (Python).

> **Default:** ohne `STORED AS`-Angabe speichert `AUTO CDC` als **SCD Typ 1**.

**Stand:** 2026-09-14.
