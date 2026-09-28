# Tutorial: Mehrere Tabellen inkrementell mit For-Each und Watermarks kopieren

Metadatengetriebener Job, der mehrere Quelltabellen inkrementell nach Unity Catalog kopiert. **Watermarks** (die zuletzt verarbeitete Zeile je Tabelle) sorgen dafür, dass bei Folgeläufen nur neue Daten kopiert werden — vollständiges Kopieren bei jedem Lauf wäre langsam und teuer.

## Architektur

| Task | Typ | Aufgabe |
|---|---|---|
| `read_watermarks` | SQL | fragt eine Control-Tabelle mit Quelltabellen-Metadaten ab |
| `copy_tables` | For each | iteriert über die Ergebnisse, verarbeitet Tabellen parallel |
| `copy_incremental` | verschachteltes Notebook | führt den Datentransfer aus und schreibt den Watermark fort |

## Schritte

1. **Control-Tabelle einrichten:** `config.watermarks` mit Quell-/Ziel-Tabellen-Mapping, Watermark-Spalte und letztem verarbeiteten Zeitstempel. Anfangswert `1970-01-01` löst beim ersten Lauf einen vollständigen Load aus.
2. **Notebook-Logik:** filtert Quellzeilen, deren Watermark-Spalte über dem gespeicherten Schwellenwert liegt, hängt neue Daten an die Zieltabelle an, aktualisiert den Watermark auf den maximal kopierten Wert.
3. **Job konfigurieren:** SQL-Task-Ausgabe fließt über `{{tasks.read_watermarks.output.rows}}` in den For-each-Task; einzelne Zeilenfelder werden über `{{input.source_table}}` u. Ä. an das verschachtelte Notebook übergeben.
4. **Ausführen:** Job starten, Iterationen beobachten, Watermark-Fortschritt über die Control-Tabelle prüfen.

## Erweiterungen

- Neue Tabellen durch Einfügen von Control-Tabellen-Zeilen hinzufügen.
- Verarbeitung über eine `active`-Flag-Spalte pausieren.
- Watermarks zurücksetzen, um bestimmte Datumsbereiche erneut zu befüllen (Backfill).

## Quelle

- https://docs.databricks.com/aws/en/jobs/how-to/foreach-watermark-tutorial
