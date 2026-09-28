*Verschoben aus `_read_files.md`, Abschnitt 3 (Vollständige Optionsreferenz) — Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).*

### Excel-Optionen (`DataFrameReader`)

| Option | Standardwert | Gültige Werte | Beschreibung |
|---|---|---|---|
| `dataAddress` | keiner | Zellbereich oder Sheet-Name als String | Der in Excel-Syntax angegebene Zellbereich. Ohne Angabe werden alle gültigen Zellen des ersten Sheets gelesen. |
| `headerRows` | `0` | `0`, `1` | Anzahl der ersten Zeilen, die als Spaltennamen-Kopfzeile verwendet werden. |
| `ignoreMissingSheet` | `false` | `true`, `false` | Ob Dateien ohne das in `dataAddress` angegebene Sheet stillschweigend übersprungen werden. |
| `includePhoneticRuns` | `false` | `true`, `false` | Ob phonetische Anmerkungen (z. B. Pinyin oder Furigana) beim Lesen von XLSX-Dateien an Zellwerte angehängt werden. |
| `operation` | `readSheet` | `readSheet`, `listSheets` | Die auf der Excel-Arbeitsmappe auszuführende Operation. |
| `timestampNTZFormat` | `yyyy-MM-dd'T'HH:mm:ss[.SSS]` | Zeitstempel-Formatstring | Format für als String gespeicherte Timestamp-ohne-Zeitzone-Werte in Excel. |
| `dateFormat` | `yyyy-MM-dd` | Datumsformatstring | Format für als `Date` gelesene String-Werte. |

Diese Optionen gelten laut Doku beim Lesen von Excel-Dateien über `DataFrameReader`.
