# Slowly Changing Dimensions (SCD) — Übersicht

**SCD** legt fest, **wie Änderungen in einer Dimensionstabelle gespeichert werden**: überschreiben oder versionieren. Woher die Änderungen kommen, beschreibt **CDC** → [../CDC/00 Uebersicht.md](../CDC/00%20Uebersicht.md).

> Kurz: **CDC ist der Input**, **SCD ist die Speicherstrategie**. SCD kann auch ohne Change-Events entstehen, z. B. durch Vergleich von Voll-Snapshots.

---

## Die SCD-Typen

| Typ | Verhalten | In Databricks |
|---|---|---|
| **0** | Wert wird nie geändert (z. B. Geburtsdatum, Erstanlage) | kein eigenes Feature; Spalte beim Update einfach nicht setzen |
| **1** | alter Wert wird **überschrieben**, keine Historie | `STORED AS SCD TYPE 1` (Default von AUTO CDC), `MERGE` |
| **2** | alte Zeile bleibt, neue **Version** mit Gültigkeitszeitraum | `STORED AS SCD TYPE 2` (`__START_AT`, `__END_AT`), `MERGE` |
| **3** | nur der **vorherige** Wert in einer Extra-Spalte (`city`, `previous_city`) | kein eigenes Feature; per `MERGE` |
| **4** | aktueller Stand in einer Tabelle, Historie in separater Tabelle | Kombination: SCD-1- und SCD-2-Ziel aus derselben Quelle → [../CDC/01](../CDC/01%20Debezium-Dateien%20mit%20Auto%20Loader%20und%20AUTO%20CDC.md) |
| **6** | Mischung aus 1 + 2 + 3: Versionen **und** aktueller Wert in jeder Zeile | per View auf SCD 2 → [04](04%20SCD%20im%20Star-Schema.md) |
| *bitemporal* | zwei Zeitachsen: „wann gültig“ und „wann bekannt“ | `STORED AS BITEMPORAL` (Beta) |

**Prüfungsrelevant sind Typ 1 und Typ 2.** Die anderen Typen sind gut zu kennen, weil sie in Gesprächen und in Data-Warehouse-Literatur vorkommen.

---

## Die Dateien in diesem Ordner

| # | Datei | Kombination |
|---|---|---|
| 1 | [SCD Type 1 – Umsetzungswege](01%20SCD%20Type%201%20-%20Umsetzungswege.md) | AUTO CDC · `MERGE` aus Updates · `MERGE` aus Snapshot · AUTO CDC FROM SNAPSHOT · Materialized View downstream |
| 2 | [SCD Type 2 mit AUTO CDC](02%20SCD%20Type%202%20mit%20AUTO%20CDC.md) | AUTO CDC · TRACK HISTORY · Abfragemuster (aktuell, Stichtag, Verlauf) · Snapshots · CDF des Ziels |
| 3 | [SCD Type 2 manuell mit MERGE](03%20SCD%20Type%202%20manuell%20mit%20MERGE.md) | SQL-`MERGE` mit Merge-Key-Trick · `foreachBatch` · Timestamp-CDC |
| 4 | [SCD im Star-Schema](04%20SCD%20im%20Star-Schema.md) | Fakten ↔ SCD-2-Dimension (Point-in-Time-Join) · Surrogate Keys · SCD-6-View · Gold-MVs |
| 5 | [SCD mit Governance, Data Quality und Performance](05%20SCD%20mit%20Governance%2C%20Data%20Quality%20und%20Performance.md) | Expectations · Dynamic View · Column Mask · Row Filter · Liquid Clustering |
| 6 | [SCD Type 2 vs. Delta Time Travel](06%20SCD%20Type%202%20vs.%20Delta%20Time%20Travel.md) | fachliche vs. technische Historie |
| 7 | [SCD in Lakeflow Connect](07%20SCD%20in%20Lakeflow%20Connect.md) | Managed Connectors mit `scd_type` |

---

## Entscheidungshilfe

| Frage | Empfehlung |
|---|---|
| Zählt nur der aktuelle Stand? | **SCD 1** |
| Muss man „Wie war es am Stichtag X?“ beantworten (Reporting, Audit, Regulatorik)? | **SCD 2** |
| Ändern sich nur manche Spalten fachlich relevant? | SCD 2 mit `TRACK HISTORY ON …` → [02](02%20SCD%20Type%202%20mit%20AUTO%20CDC.md) |
| Quelle liefert Change-Events? | AUTO CDC → [02](02%20SCD%20Type%202%20mit%20AUTO%20CDC.md) |
| Quelle liefert nur Voll-Snapshots? | `create_auto_cdc_from_snapshot_flow` → [01](01%20SCD%20Type%201%20-%20Umsetzungswege.md), [02](02%20SCD%20Type%202%20mit%20AUTO%20CDC.md) |
| Kein Pipeline-Kontext? | `MERGE` → [01](01%20SCD%20Type%201%20-%20Umsetzungswege.md), [03](03%20SCD%20Type%202%20manuell%20mit%20MERGE.md) |
| Reicht nicht einfach Delta Time Travel? | Nein, für fachliche Historie nicht → [06](06%20SCD%20Type%202%20vs.%20Delta%20Time%20Travel.md) |

---

## Verwandte Themen

- SCD-Grundlagen und Star-Schema: [../Data Transformation and Modeling/05 Datenmodellierung/02 Dimensionale Modellierung und SCD.md](../Data%20Transformation%20and%20Modeling/05%20Datenmodellierung/02%20Dimensionale%20Modellierung%20und%20SCD.md)
- Vollständige AUTO-CDC-Referenz: [../Data Transformation and Modeling/Vertiefung …/03 Change Data Capture (CDC).md](../Data%20Transformation%20and%20Modeling/Vertiefung%20%28ueber%20Pruefungsumfang%20hinaus%29/Lakeflow%20Declarative%20Pipelines%20-%20Transformation%20und%20CDC/03%20Change%20Data%20Capture%20%28CDC%29.md)
- Gleiche Datei wird überschrieben (SCD 1/2 aus Dateien): [../Ingestion/Datei Ingestion Varianten/03 Gleiche Datei wird ueberschrieben.md](../Ingestion/Datei%20Ingestion%20Varianten/03%20Gleiche%20Datei%20wird%20ueberschrieben.md)

## Quellen

- [The AUTO CDC APIs](https://docs.databricks.com/aws/en/ldp/cdc)
- [Upsert into a Delta Lake table using merge](https://docs.databricks.com/aws/en/delta/merge)
