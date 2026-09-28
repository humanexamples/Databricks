*Verschoben aus `_read_files.md`, Abschnitt 3 (Vollständige Optionsreferenz) — Quelle: [Spark API options reference](https://docs.databricks.com/aws/en/spark/api-options).*

### Text-Optionen (gemeinsam mit `spark.read`)

| Option | Standardwert | Gültige Werte | Beschreibung |
|---|---|---|---|
| `encoding` | `UTF-8` | Name eines `java.nio.charset.Charset` | Name der Zeichenkodierung des Zeilentrenners der TEXT-Datei. |
| `lineSep` | keiner (deckt `\r`, `\r\n` und `\n` ab) | Beliebiger String | String zwischen zwei aufeinanderfolgenden TEXT-Datensätzen. |
| `wholeText` | `false` | `true`, `false` | Ob eine Datei als ein einzelner Datensatz gelesen wird. |
