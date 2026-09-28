# Was ist Change Data Capture (CDC)?

Change Data Capture (CDC) ist ein Datenintegrationsmuster, das Änderungen an Quellsystemen erfasst, statt jedes Mal den gesamten Datensatz zu verarbeiten. Ändert sich z. B. ein einzelner Mitarbeiterdatensatz in einer 50-zeiligen Oracle-Tabelle, enthält der CDC-Feed nur diesen einen UPDATE-Datensatz – das macht die Verarbeitung deutlich effizienter.

## Zwei Ansätze zur Änderungsanwendung

**SCD Typ 1 (<mark style="background:#fff59d;color:#1b1f23;">nur aktueller Stand</mark>):** Überschreibt alte Daten mit neuen Informationen, es bleibt nur die aktuellste Version erhalten. Ideal, <mark style="background:#fff59d;color:#1b1f23;">wenn nur der aktuelle Stand benötigt wird und materialisierte Views inkrementell aktualisiert werden sollen</mark>, ohne vollständige Neuberechnung.

**SCD Typ 2 (<mark style="background:#fff59d;color:#1b1f23;">Historie nachverfolgen</mark>):** Führt vollständige Historien mit Zeitstempel-Metadaten (<mark style="background:#fff59d;color:#1b1f23;">`__START_AT` und `__END_AT`</mark>) mit. Aktive Datensätze haben `__END_AT = NULL`. Geeignet für Szenarien mit Auditierbarkeit, regulatorischen Anforderungen oder Stichtagsberichten.

## <mark style="background:#fff59d;color:#1b1f23;">Verarbeitungsoptionen</mark>

**AUTO CDC** verarbeitet <mark style="background:#fff59d;color:#1b1f23;">Change-Feeds aus Quellen wie relationalen Datenbanken mit aktiviertem CDC</mark> oder <mark style="background:#fff59d;color:#1b1f23;">Delta-Tabellen mit Change Data Feed</mark>. Es behandelt außer der Reihe eintreffende Datensätze automatisch anhand monoton steigender Sequenzierungsspalten.

**AUTO CDC FROM SNAPSHOT** wird eingesetzt, wenn <mark style="background:#fff59d;color:#1b1f23;">CDC im Quellsystem nicht verfügbar ist</mark>. <mark style="background:#fff59d;color:#1b1f23;">Es vergleicht aufeinanderfolgende Snapshots, um Änderungen abzuleiten</mark> und einen synthetischen Change-Feed zu erzeugen, auf den dieselbe SCD-Logik wie bei AUTO CDC angewendet wird.

## Vorteile von CDC

- Reduziert das Verarbeitungsvolumen, da Änderungsdaten meist deutlich kleiner sind als der Gesamtdatensatz.
- Ermöglicht die Rekonstruktion von Datensätzen zu bestimmten Zeitpunkten für Auditierung und Trendanalysen.
- Erhält stabile [Surrogatschlüssel](https://www.databricks.com/de/blog/2022/08/08/identity-columns-to-generate-surrogate-keys-are-now-available-in-a-lakehouse-near-you.html) für **konsistente Joins**.

---
**Quelle:** https://docs.databricks.com/aws/en/data-engineering/what-is-cdc  
**Stand:** 2026-08-07
