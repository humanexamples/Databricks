# `read_files` — tabellenwertige Funktion zum Lesen von Dateien

> Gilt für: Databricks SQL, Databricks Runtime **13.3 LTS und höher**.

Liest Dateien unter einem angegebenen Pfad und gibt die Daten als Tabelle zurück. Unterstützt `JSON`, `CSV`, `XML`, `TEXT`, `BINARYFILE`, `PARQUET`, `AVRO`, `ORC` und kann Format sowie ein einheitliches Schema über alle Dateien hinweg automatisch erkennen. Nutzbar in `SELECT`, CTAS und Streaming Tables; im Streaming-Modus (`STREAM read_files(...)`) intern über **Auto Loader**.

**Beta:** Mit `format => 'file'` liefert `read_files` pro Datei eine `FILE`-Referenz, statt den Inhalt zu lesen.

> **Vertiefung im Projekt:** [_read_files.md](../../../../07%20Data%20Management/01%20Data%20Engineering/02%20Lakeflow%20Connect/02%20Lakeflow%20Connect%20Standard%20Connectors/05%20Working%20with%20Files/_read_files.md) — Schema-Inferenz im Detail, `schemaHints`, alle `schemaEvolutionMode`-Werte, Datei-Tracking, Erkennungsmodi, `cloud_files_state`, Exception-Fälle, Partitionsspalten. Format-spezifische Leseoptionen (z. B. CSV): [12 Query Data/01 Dateiformate/01 CSV lesen und schreiben.md](../../../../12%20Query%20Data/01%20Dateiformate/01%20CSV%20lesen%20und%20schreiben.md).

## Abschnitte

1. [Syntax](01%20Syntax.md)
2. [Arguments](02%20Arguments.md)
3. [Returns](03%20Returns.md)
4. [Die `_metadata`-Spalte](04%20Die%20_metadata-Spalte.md)
5. [File Discovery und Glob-Patterns](05%20File%20Discovery%20und%20Glob-Patterns.md)
6. [Schema-Inferenz](06%20Schema-Inferenz.md)
7. [Authentifizierung für Cloud-Speicher](07%20Authentifizierung%20f%C3%BCr%20Cloud-Speicher.md)
8. [Nutzung in Streaming Tables](08%20Streaming%20Tables.md)
9. [Options](09%20Options.md)
10. [Examples](10%20Examples.md)
11. [Verwandte Funktionen / Artikel](11%20Verwandte%20Funktionen.md)
