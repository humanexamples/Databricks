# Volltextsuche-Indizes auf Unity-Catalog-verwalteten Tabellen

Diese Funktion befindet sich aktuell in der Beta-Phase. Workspace-Administratoren können den Zugriff über die Previews-Einstellungen aktivieren.

Ein Volltextsuche-Index beschleunigt Nachschlagevorgänge auf Textspalten einer von Unity Catalog verwalteten Delta-Lake- oder Iceberg-Tabelle. Diese Seite erklärt Voraussetzungen, Erstellung, Abfrage und Verwaltung solcher Indizes.

## Überblick

Der Index unterstützt Teilstring- und Wort-Matching. Databricks nutzt dafür die Funktionen `search` und `isearch`, um Dateien zu überspringen, die keine passenden Ergebnisse enthalten können. Das reduziert die gescannte Datenmenge bei selektiven Abfragen deutlich.

## Voraussetzungen

### Compute

Volltextsuche-Indizes erfordern Databricks Runtime 18.2 oder höher. Zusätzlich müssen Sie das Beta-Feature in den Workspace-Einstellungen aktivieren.

### Berechtigungen

Um einen Suchindex zu erstellen, benötigen Sie:

- die Berechtigung `MODIFY` auf der referenzierten Tabelle,
- die Berechtigung `CREATE TABLE` im übergeordneten Schema.

### Anforderungen an die Basistabelle

- Der Index wird im selben Katalog und Schema wie die Basistabelle erstellt.
- Die Tabelle ist eine von Unity Catalog verwaltete Delta-Lake- oder Iceberg-Tabelle.
- Row Tracking ist aktiviert (`delta.enableRowTracking = true`).
- Indizierte Spalten sind vom Typ `STRING`, `VARIANT`, `STRUCT` oder `ARRAY`.
- Die Tabelle nutzt kein OpenSharing, keine Shallow Clones, keine attributbasierte Zugriffskontrolle, keine Row-Level-Security-Policies und keine Column Masks.

## Volltextsuche-Indizes erstellen

Die grundlegende Syntax lautet:

```sql
%sql
CREATE SEARCH INDEX [IF NOT EXISTS] index_name
ON table_name ( column_name [, column_name ...] )
[OPTIONS ( option_key = option_value [, ... ] )]
```

Beispiel:

```sql
%sql
CREATE SEARCH INDEX log_idx
ON logs (message, error_detail);
```

### Optionen

| Schlüssel | Werte | Standard | Beschreibung |
| --- | --- | --- | --- |
| `tokenizer` | `ngram`, `split` | `ngram` | Methode zur Text-Tokenisierung beim Indizieren. |
| `ngram_size` | Integer im Bereich [3, 10] | 5 | Länge der erzeugten N-Gramme (nur beim ngram-Tokenizer). |
| `min_token_length` | Integer >= 1 | 3 | Minimale Token-Länge, die erhalten bleibt (nur beim split-Tokenizer). |

### Tokenizer-Optionen

**ngram-Tokenizer** — für Teilstring-Matching:

```sql
%sql
CREATE SEARCH INDEX log_ngram_idx
ON logs (message)
OPTIONS (tokenizer = 'ngram', ngram_size = 4);
```

**split-Tokenizer** — prüft, ob ganze Wörter enthalten sind:

```sql
%sql
CREATE SEARCH INDEX log_word_idx
ON logs (message)
OPTIONS (tokenizer = 'split', min_token_length = 2);
```

## Abfragen mit search() und isearch()

Funktionssignaturen:

```sql
%sql
search( target [, target ... ] , 'pattern' [, mode => 'substring' | 'word' ] )
isearch( target [, target ... ] , 'pattern' [, mode => 'substring' | 'word' ] )
```

- `search`: Groß-/Kleinschreibung wird berücksichtigt.
- `isearch`: Groß-/Kleinschreibung wird ignoriert.

### Rückgabewerte

Die Funktionen liefern:

- `true`, wenn mindestens ein nicht-null Ziel passt,
- `null`, wenn kein nicht-null Ziel passt, aber mindestens eines `null` ist,
- `false`, wenn alle Ziele nicht-null sind und keines passt.

### Beispielabfragen

```sql
%sql
-- Case-insensitive substring search across one column.
SELECT * FROM logs
WHERE isearch(message, 'connection refused');

-- Case-sensitive substring search across multiple columns.
SELECT * FROM logs
WHERE search(message, error_detail, '550e8400-e29b-41d4-a716-446655440000');
```

```sql
%sql
-- Word search: matches rows containing all three words, in any order.
SELECT * FROM audit_logs
WHERE search(message, 'user admin login', mode => 'word');
```

## Indizes verwalten

### Index beschreiben

```sql
%sql
DESCRIBE INDEX log_idx;
```

### Index aktualisieren

Inkrementelle Aktualisierung (fügt nur Einträge für neue Zeilen hinzu):

```sql
%sql
REFRESH INDEX log_idx;
```

Vollständige Aktualisierung (fügt Einträge hinzu und entfernt sie):

```sql
%sql
REFRESH INDEX log_idx FULL;
```

Volltextsuche-Indizes aktualisieren sich nicht automatisch, wenn sich die Basistabelle ändert.

### Index löschen

```sql
%sql
DROP INDEX log_idx;
```

Mit Sicherheitsklausel:

```sql
%sql
DROP INDEX IF EXISTS log_idx;
```

## Wichtige Einschränkungen

- Spalten umbenennen oder den Datentyp ändern wird nicht unterstützt.
- Tabellen mit OpenSharing, Shallow Clones, attributbasierter Zugriffskontrolle, Column Masks oder Row-Level-Security-Policies können keine Suchindizes nutzen.
- Während der Beta-Phase erstellte Indizes sind nicht garantiert mit späteren Releases kompatibel.

---
**Quelle:** https://docs.databricks.com/aws/en/optimizations/full-text-search-indexes  
**Stand:** 2026-08-06
