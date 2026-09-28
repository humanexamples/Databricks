# Dimensionale Modellierung in Lakeflow Pipelines

Dieses Dokument beschreibt Best Practices für dimensionale Modellierung (Star-Schema, Fact-/Dimension-Tabellen) in der Gold-Schicht von Lakeflow-Pipelines.

## Abschnittsübersicht

1. [Grundkonzept: Fact- und Dimension-Tabellen](#grundkonzept)
2. [Star-Schema-Architektur](#star-schema)
3. [Implementierungsempfehlung je Tabellentyp](#implementierung)
4. [Natürliche vs. Surrogate Keys](#keys)
5. [Datumsdimension (`dim_date`)](#dim-date)
6. [Weitere strukturelle Empfehlungen](#struktur)
7. [Quellen](#quellen)

---

## <a id="grundkonzept">1. Grundkonzept: Fact- und Dimension-Tabellen</a>

Dimensionale Modellierung organisiert Daten der Gold-Schicht in zwei Tabellentypen:

- **Fact-Tabellen** enthalten "the events or measurements you care about, such as orders, clicks, or sales" — also die Ereignisse oder Messwerte, die von Interesse sind.
- **Dimension-Tabellen** enthalten "the descriptive context around those events, such as customers, products, or dates" — den beschreibenden Kontext zu diesen Ereignissen.

## <a id="star-schema">2. Star-Schema-Architektur</a>

Ein Star-Schema platziert "one fact table in the middle and join it out to several dimension tables through their keys" — eine zentrale Fact-Tabelle, die über ihre Keys mit mehreren Dimension-Tabellen verbunden wird. Dieser Ansatz fügt sich natürlich in die Medaillon-Architektur ein: Bronze- und Silber-Schicht übernehmen Ingestion und Bereinigung, während die Gold-Schicht Fact- und Dimension-Tabellen materialisiert.

## <a id="implementierung">3. Implementierungsempfehlung je Tabellentyp</a>

- **Dimension-Tabellen** sollten typischerweise als **Materialized Views** umgesetzt werden — oder als **Streaming Tables mit Slowly Changing Dimension (SCD) Type 2**, wenn Historie benötigt wird.
- **Fact-Tabellen** funktionieren am besten als **Streaming Tables**, inkrementell aus der Silber-Schicht gespeist, damit Gold-Schicht-Aggregate nahe an Echtzeit bleiben.

Zusammengefasst: "Keep facts as streaming tables and dimensions as materialized views" — mit der ausdrücklichen Ausnahme: *unless you specifically need change history, in which case use `AUTO CDC` with `STORED AS SCD TYPE 2`* (siehe Abschnitt 3, erster Punkt).

## <a id="keys">4. Natürliche vs. Surrogate Keys</a>

Natürliche Keys sollten bevorzugt werden, wenn sie stabil und nutzbar sind. Für Surrogate Keys wird empfohlen, **keine Hash-Funktionen** zu verwenden; stattdessen soll ein ordnungserhaltender ("order-preserving") Surrogate Key deterministisch aus dem stabilen natürlichen Key abgeleitet werden, sodass dieselbe fachliche Entität stets auf denselben Surrogate Key abgebildet wird.

## <a id="dim-date">5. Datumsdimension (`dim_date`)</a>

`dim_date` sollte als einfache Materialized View aufgebaut werden, generiert mit `sequence()` und `explode()` über einen Datumsbereich — statt sie aus einer Quelle einzulesen.

## <a id="struktur">6. Weitere strukturelle Empfehlungen</a>

- Fact-Tabellen als Streaming Tables, Dimension-Tabellen als Materialized Views halten.
- Downstream-BI-Tools sollten Gold-Materialized-Views direkt abfragen.

**Ungeklärt (Detailtiefe):** Die per `WebFetch` erfasste Zusammenfassung lieferte keine wörtlich zitierbaren SQL-/Python-Codebeispiele für diese Seite (z. B. für die `sequence()`/`explode()`-basierte `dim_date`-Konstruktion oder für SCD-Type-2-Dimension-Tabellen) — nur die textlichen Empfehlungen wurden extrahiert. Für ein vollständiges Codebeispiel wäre ein gezielter Nachfolge-Abruf nötig.

---

## <a id="quellen">7. Quellen</a>

1. Dimensional modeling in Lakeflow pipelines (AWS): https://docs.databricks.com/aws/en/ldp/best-practices/dimensional-modeling
