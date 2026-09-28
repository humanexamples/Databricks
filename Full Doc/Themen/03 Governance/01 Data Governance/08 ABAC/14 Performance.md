# Performance-Überlegungen für Row Filter und Column Masks

ABAC-Policies führen UDFs zur Query-Zeit aus — pro Zeile bzw. pro Spaltenwert. Das erfordert gezielte Performance-Optimierung.

## Empfehlungen

- **UDF-Logik einfach halten:** einfache `CASE`-Anweisungen und schlichte Boolean-Ausdrücke statt komplexer Funktionen — diese verschlechtern die Query-Performance direkt.
- **Principal-Targeting statt UDF-Logik:** komplexe Logik lieber über die `TO`/`EXCEPT`-Klauseln der Policy und Identitätsattribute in der `WHEN`-Klausel abbilden. Identitätsfunktionen wie `is_account_group_member()` werden nur einmal während der Analyse aufgelöst, nicht pro Zeile — das minimiert den Overhead.
- **Deterministische Ausdrücke verwenden:** fehlersichere SQL-Alternativen wie `try_divide` statt `/` und `try_cast` statt `CAST`. Nicht-deterministische Funktionen verhindern Optimizer-Caching und Constant Folding.
- **SQL statt Python:** Python-UDFs in ABAC-Policies wenn möglich vermeiden — der Optimizer kann sie nicht inlinen, sie laufen für jede Zeile erneut.
- **Größe von Lookup-Tabellen begrenzen:** externe Referenztabellen klein genug halten für Broadcast-Hash-Joins statt Shuffle-Joins — reduziert den Performance-Einfluss deutlich.

## Herausforderungen bei der Query-Optimierung

- **`SecureView`-Barriere:** Policies führen eine `SecureView`-Barriere ein, die bestimmte Prädikate am Pushdown in die Speicherschicht hindert. Komplexe Prädikate mit Funktionen wie `date_format()` lassen sich nicht pushdownen und erzwingen volle Table Scans. Einfache Gleichheitsvergleiche bleiben dagegen optimierbar.
- **Column-Mask-Wiederverwendung:** Dieselbe Maskierungsfunktion über mehrere Spalten hinweg wiederverwenden reduziert Overhead gegenüber separaten Funktionen pro Spalte.
- **Regex auf Textfeldern:** `regexp_replace` auf serialisierten Dokumenten (XML/JSON) vermeiden — stattdessen sensible Felder in typisierten Spalten separater Tabellen materialisieren.

## Testanforderung

UDF-Performance vor dem Produktivgang mit **mindestens 1 Million Zeilen** und repräsentativen Workload-Queries validieren, um den tatsächlichen Overhead der Policy zu isolieren.

## Quelle

- https://docs.databricks.com/aws/en/data-governance/unity-catalog/abac/performance
