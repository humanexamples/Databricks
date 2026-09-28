# `read_files` — Schema-Inferenz

Das Schema lässt sich mit der Option `schema` explizit angeben. Ohne `schema` leitet `read_files` ein **einheitliches Schema über alle gefundenen Dateien** ab.

- Dafür liest es **alle** Dateien, außer die Abfrage hat ein `LIMIT`.
- Auch mit `LIMIT` kann es mehr Dateien lesen als nötig, um ein repräsentativeres Schema zu erhalten.
- In Notebooks und im SQL-Editor ergänzt Databricks bei `SELECT`-Abfragen automatisch ein `LIMIT`, wenn keines angegeben ist.

`schemaHints` legt einzelne Spaltentypen fest, der Rest wird weiter inferiert.

Standardmäßig gibt es eine **Rescued-Data-Spalte**. Sie fängt Daten auf, die nicht zum Schema passen. Mit `schemaEvolutionMode => 'none'` fällt sie weg.

```sql
-- id fest als INT, alle anderen Spalten werden inferiert
SELECT * FROM read_files('s3://bucket/path', format => 'json', schemaHints => 'id int');
```

## Partitionsspalten

Liegen die Dateien in Hive-Style-Verzeichnissen (`/spalte=wert/`), erkennt `read_files` daraus Partitionsspalten.

- **Mit `schema`:** Erkannte Partitionsspalten bekommen den Typ aus dem Schema. Stehen sie nicht im Schema, werden sie ignoriert.
- **Gleicher Name in Pfad und Daten:** Der Wert aus dem Pfad gewinnt. Soll die Datenspalte gelten, die Partitionsspalten mit `partitionColumns` explizit auflisten.
- **`partitionColumns`** bestimmt, welche erkannten Spalten ins Schema kommen. Ein leerer String (`''`) ignoriert alle.
- **`schemaHints`** kann auch den Typ einer Partitionsspalte überschreiben.
- Auch bei `TEXT` und `BINARYFILE` (festes Schema) versucht `read_files`, Partitionen zu erkennen.

```sql
SELECT * FROM read_files('/Volumes/cat/sch/vol/events', format => 'json', partitionColumns => 'event,date');
```
