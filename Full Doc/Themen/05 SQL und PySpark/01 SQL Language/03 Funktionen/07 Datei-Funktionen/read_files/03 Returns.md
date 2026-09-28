# `read_files` — Returns

Eine Tabelle mit den Daten der Dateien unter `path`. Das Schema hängt vom Format ab.

**`BINARYFILE`** — festes Schema:

- `path` (`STRING`): vollständiger Pfad der Datei.
- `modificationTime` (`TIMESTAMP`): letzte Änderung der Datei.
- `length` (`LONG`): Dateigröße in Bytes.
- `content` (`BINARY`): Binärinhalt der Datei. Mit `* EXCEPT (content)` weglassen, wenn nur Metadaten gebraucht werden.

**`TEXT`** — festes Schema mit einer einzigen Spalte `value` (`STRING`).

**Alle anderen Formate** (`JSON`, `CSV`, `XML`, `PARQUET`, `AVRO`, `ORC`) — das Schema wird aus dem Dateiinhalt inferiert oder über die Option `schema` angegeben.
