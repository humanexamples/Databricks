Beim Erstellen einer Tabelle können Sie Metadatenspalten mit Informationen aus den Eingabedateien der Datenquelle anhängen.

Angenommen, Ihr Cloud-Speicherort enthält **eine Reihe von Rohdateien** (CSV, TXT, JSON oder andere Formate), und Sie möchten diese Dateien in eine **Tabelle der Bronze-Ebene** ingestieren.
Im Rahmen dieser Ingestion möchten Sie möglicherweise jeder Zeile der Tabelle bestimmte Metadatenspalten hinzufügen. Diese Spalten können Informationen aus der Ingestion-Quelle enthalten, zum Beispiel:

Um die Spalte `_metadata` in den zurückgegebenen DataFrame aufzunehmen, müssen Sie sie in Ihrer Leseabfrage beim Angeben der Quelle explizit auswählen.
Die Spalte `_metadata` enthält eine Vielzahl nützlicher Felder. Zwei häufig verwendete Felder sind:

1. `_metadata.file_modification_time` – liefert den Zeitstempel der letzten Änderung der Eingabedatei
2. `_metadata.file_name` – gibt für jede Zeile den Namen der Quelldatei zurück
